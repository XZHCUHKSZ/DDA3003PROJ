from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from analysis_service.models import AnalysisRequest, AnalysisResponse, Citation
from analysis_service.providers.bailian_client import BailianClient
from analysis_service.sources.registry import build_default_sources


SYSTEM_PROMPT = (
    '你是空气质量聚落分析助手。请用普通人能看懂的中文表达，不要堆术语。'
    '先讲结论，再解释原因，再给行动建议。请严格基于给定数据生成结论，'
    '每段结论都要附带来源ID，如[S1]。优先引用联网检索到的具体页面证据。'
    '禁止编造未提供的数据。'
    '输出必须是JSON对象，字段: settlement_text, diffusion_text, cause_text, confidence。'
)


def _fmt_num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return '--'
    return f'{v:.{digits}f}'


def _build_fallback(req: AnalysisRequest, profile: dict) -> tuple[str, str, str, float]:
    s = req.snapshot
    econ = profile.get('economic_level') or ''
    gdp_hint = profile.get('gdp_hint')
    industries = profile.get('industries') or []
    geo_factors = profile.get('geo_factors') or []
    industry_text = '、'.join(industries[:4]) if industries else ''
    econ_text = f'{econ}（约{gdp_hint}）' if (econ and gdp_hint) else econ
    metric_hint = {
        'AQI': 'AQI代表综合空气质量水平',
        'PM2.5_24h': 'PM2.5更容易受燃烧源和二次转化影响',
        'PM10_24h': 'PM10常受扬尘、施工和道路再悬浮影响',
        'SO2_24h': 'SO2与燃煤及部分工业燃烧过程相关',
        'NO2_24h': 'NO2常与交通排放和燃烧过程相关',
        'O3_8h': 'O3受光照、温度和前体物浓度共同驱动',
        'O3_8h_24h': 'O3受光照、温度和前体物浓度共同驱动',
    }.get(s.metric, '该指标反映空气污染过程变化')
    settlement = (
        f"一句话结论：{s.city} 在 {s.date} 的 {s.metric} 水平最近波动"
        f"{'明显' if (s.delta_day or 0) and abs(s.delta_day or 0) >= 8 else '不大'}。"
        f"当前内圈均值 {_fmt_num(s.in_avg, 1)}，外圈均值 {_fmt_num(s.out_avg, 1)}，"
        f"较昨日 {_fmt_num(s.delta_day, 1)}，7日趋势 {_fmt_num(s.slope_7d, 2)}/天。"
        f"从指标含义看，{metric_hint}，因此建议把“单日值”与“近7日斜率”一起看，避免误判。 [S1][S5]"
    )
    diffusion = (
        f"扩散判断：{s.diffusion_label or '待判定'}。"
        f"{s.diffusion_detail or '从内外圈差值看，短期方向仍需持续观察。'}"
        '结合气象条件（风速风向、边界层高度、湿度与降水）同看，能更好区分“本地累积”还是“外来输送”。 [S1][S2][S6]'
    )
    cause_parts = []
    if econ_text:
        cause_parts.append(f"{s.city} 的经济画像可概括为“{econ_text}”。 [S3][S4]")
    if industry_text:
        cause_parts.append(f"本地/周边产业结构可关注：{industry_text}，其活动强度变化会影响污染排放强弱。 [S3][S4]")
    if geo_factors:
        cause_parts.append(f"地理条件因素：{s.city} 具有“{'、'.join(geo_factors[:3])}”等特征，会影响污染物扩散与滞留。 [S3]")
    cause_parts.append('建议结合风速风向、湿度和降水继续验证，并关注连续3天以上同向变化。 [S1][S2]')
    cause = ''.join(cause_parts)
    return settlement, diffusion, cause, 0.62


def _build_user_prompt(req: AnalysisRequest, sources: list[dict], profile: dict) -> str:
    return json.dumps(
        {
            'task': (
                '对聚落分析做中文解读：必须通俗、完整、可执行建议、附来源ID引用。'
                '成因段必须明确写出：1)当地经济体量判断；2)本地或所在省重点产业类型；'
                '3)这些产业和污染物变化的关系；4)地理条件如何影响扩散。'
            ),
            'snapshot': req.snapshot.model_dump(by_alias=True),
            'history': req.history[-14:],
            'city_profile': {
                'city': req.snapshot.city,
                'province': profile.get('province'),
                'economic_level': profile.get('economic_level'),
                'gdp_hint': profile.get('gdp_hint'),
                'industries': profile.get('industries', []),
                'geo_factors': profile.get('geo_factors', []),
                'profile_text': profile.get('profile_text', ''),
            },
            'web_evidence': profile.get('web_evidence', []),
            'sources': sources,
            'output_requirements': {
                'language': 'zh-CN',
                'max_length': 1200,
                'must_cite': True,
                'audience': '普通公众',
                'style': '先结论后解释，避免过度专业术语，每段3-5句，解释清楚因果链条',
                'must_include_city_profile': True,
                'must_include_geography_factor': True,
                'prefer_detail': True,
                'prefer_live_web_sources': True,
            },
        },
        ensure_ascii=False,
    )


def _ensure_specific_cause(cause_text: str, req: AnalysisRequest, profile: dict) -> str:
    city = req.snapshot.city
    econ = profile.get('economic_level') or ''
    gdp_hint = profile.get('gdp_hint')
    industries = profile.get('industries') or []
    geo_factors = profile.get('geo_factors') or []
    province = profile.get('province')

    has_city = city in cause_text
    has_econ = ('经济' in cause_text) or ('GDP' in cause_text) or ('体量' in cause_text)
    has_industry = any(ind in cause_text for ind in industries) if industries else False
    has_geo = ('地理' in cause_text) or ('沿海' in cause_text) or ('盆地' in cause_text) or ('山地' in cause_text) or ('平原' in cause_text)

    if has_city and ((not industries and not econ) or (has_econ and (has_industry or not industries))) and (has_geo or not geo_factors):
        return cause_text

    industry_text = '、'.join(industries[:5]) if industries else ''
    region_text = f'{province}{city}' if province else city
    econ_text = f'{econ}（约{gdp_hint}）' if (econ and gdp_hint) else econ
    supplements: list[str] = []
    if econ_text or industry_text:
        line = f"\n补充说明：{region_text}"
        if econ_text:
            line += f"的经济画像为“{econ_text}”"
        if industry_text:
            line += ('' if not econ_text else '，') + f"产业结构可关注：{industry_text}"
        line += "。 [S3][S4]"
        supplements.append(line)
    if geo_factors and not has_geo:
        supplements.append(f"\n地理条件因素：{city}具备“{'、'.join(geo_factors[:3])}”等特征，可能改变污染物的扩散效率与累积位置。 [S3]")
    if not supplements:
        return cause_text
    return (cause_text.rstrip() + ''.join(supplements)).strip()


def run_analysis(req: AnalysisRequest, *, api_key: str = '') -> AnalysisResponse:
    sources, profile = build_default_sources(req.snapshot.city, req.snapshot.metric, req.snapshot.date)
    client_cfg = req.client_config or {}
    provider_name = str(client_cfg.get('provider') or 'bailian').strip().lower()
    model_name = str(client_cfg.get('model') or '').strip()

    provider = BailianClient(
        api_key=api_key,
        model=model_name,
    )
    used_fallback = False
    fallback_reason: str | None = None

    if provider.enabled and provider_name in ('bailian', 'openai', 'custom'):
        try:
            model_out = provider.chat_json(SYSTEM_PROMPT, _build_user_prompt(req, sources, profile), timeout=70)
            settlement_text = str(model_out.get('settlement_text', '')).strip()
            diffusion_text = str(model_out.get('diffusion_text', '')).strip()
            cause_text = str(model_out.get('cause_text', '')).strip()
            confidence = float(model_out.get('confidence', 0.7))
            if not settlement_text or not diffusion_text or not cause_text:
                raise RuntimeError('Model output missing required fields')
            cause_text = _ensure_specific_cause(cause_text, req, profile)
        except Exception as err:
            used_fallback = True
            fallback_reason = str(err)
            settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)
    else:
        used_fallback = True
        if not provider.enabled:
            fallback_reason = 'API Key missing'
        elif provider_name not in ('bailian', 'openai', 'custom'):
            fallback_reason = f'Unsupported provider: {provider_name}'
        settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)

    # 来源输出收口：优先展示有正文证据片段的联网来源；保留本地数据来源用于数值可追溯
    live_with_snippet = [s for s in sources if s.get('snippet')]
    local_core = [s for s in sources if str(s.get('url', '')).startswith('local://')]
    ministry_core = [s for s in sources if 'mee.gov.cn' in str(s.get('url', '')) and not s.get('snippet')]
    selected_sources = (local_core[:1] + live_with_snippet[:6] + ministry_core[:1]) or sources[:6]
    citations = [Citation(**src) for src in selected_sources]
    return AnalysisResponse(
        analysis_id='ana_' + uuid.uuid4().hex[:12],
        provider=provider_name if provider.enabled and not used_fallback else 'fallback',
        model=provider.model if provider.enabled else 'rule-template',
        generated_at=datetime.now(timezone.utc).isoformat(),
        settlement_text=settlement_text,
        diffusion_text=diffusion_text,
        cause_text=cause_text,
        confidence=max(0.0, min(1.0, confidence)),
        citations=citations,
        used_fallback=used_fallback,
        fallback_reason=fallback_reason,
    )
