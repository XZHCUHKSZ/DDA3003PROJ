from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from analysis_service.models import AnalysisRequest, AnalysisResponse, Citation
from analysis_service.providers.bailian_client import BailianClient
from analysis_service.sources.registry import build_default_sources


SYSTEM_PROMPT = (
    '你是空气质量月历热力分析助手。请使用专业但清晰的中文，避免碎片化短句。'
    '先讲本月总体结论，再讲高风险时段，再讲成因。'
    '必须围绕 snapshot.metric 分析，不得默认按AQI泛化；若metric不是AQI，正文中不要把核心结论写成AQI。'
    '禁止使用“内圈/外圈/聚落/半径扩散”这类聚落分析术语。'
    'settlement_text 与 diffusion_text 各不少于120字。'
    'cause_text 按 1）2）3）4） 输出，每条2-3句，经济与产业放最后。'
    '输出必须是JSON对象，字段: settlement_text, diffusion_text, cause_text, confidence。'
)


def _safe_num(v):
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _build_user_prompt(req: AnalysisRequest, sources: list[dict], profile: dict) -> str:
    s = req.snapshot
    return json.dumps(
        {
            'task': '基于月历热力图数据做月度解读。重点说明覆盖率、峰值时段、可能成因。',
            'snapshot': {
                'city': s.city,
                'date': s.date,
                'metric': s.metric,
            },
            'city_context': req.city_context,
            'city_profile': {
                'city': req.snapshot.city,
                'province': profile.get('province'),
                'economic_level': profile.get('economic_level'),
                'gdp_hint': profile.get('gdp_hint'),
                'industries': profile.get('industries', []),
                'geo_factors': profile.get('geo_factors', []),
            },
            'sources': sources,
            'output_requirements': {
                'language': 'zh-CN',
                'audience': '普通公众',
                'style': '先结论后解释，段落连贯，解释因果链条',
                'cause_format': 'strict_numbered_1p_to_4p',
                'cause_economic_last': True,
                'forbidden_terms': ['内圈', '外圈', '聚落', '半径扩散'],
                'min_length_settlement': 120,
                'min_length_diffusion': 120,
            },
        },
        ensure_ascii=False,
    )


def _fallback(req: AnalysisRequest, profile: dict) -> tuple[str, str, str, float]:
    s = req.snapshot
    c = req.city_context or {}
    month = c.get('heatmap_month') or '--'
    cov = c.get('heatmap_coverage') or {}
    ratio = _safe_num(cov.get('ratio'))
    pct = '--' if ratio is None else f"{ratio * 100:.1f}%"
    top_hours = c.get('heatmap_top_hours') or []
    hour_text = '、'.join([f'{int(h):02d}:00' for h in top_hours if isinstance(h, (int, float))]) or '暂无明显集中时段'
    industries = profile.get('industries') or []
    geo = profile.get('geo_factors') or []

    settlement = (
        f"月度结论：{s.city}{month}的{s.metric}小时热力图覆盖率为{pct}，"
        f"高值主要出现在{hour_text}。从月内分布看，高值并非均匀铺开，而是集中在特定时段反复出现，"
        "说明污染过程具有明显的时间结构特征。解读时应同时观察高值持续时长与高值出现频次，"
        "避免仅凭单个峰值判断整月风险。"
    )
    diffusion = (
        '时段风险：当高值时段与夜间弱风、高湿、边界层压低等条件重叠时，污染物更容易在近地面累积，'
        '短时风险会明显上升。若连续多日出现同类峰值时段，通常意味着本地排放节奏与气象条件形成耦合。'
        + ('本月缺失偏多，建议谨慎解读并优先关注方向性结论。' if ratio is not None and ratio < 0.8 else '本月数据完整度可用于时段判断与风险排序。')
    )
    ind_txt = '、'.join(industries[:4]) if industries else '本地工业与交通活动'
    geo_txt = '、'.join(geo[:3]) if geo else '地形与边界层条件'
    cause = (
        '1）高值时段通常与不利扩散气象同时出现。若风速偏低、湿度偏高且边界层较低，污染物更难被快速稀释，容易形成“小时级抬升”。\n'
        f'2）本地排放端可重点关注{ind_txt}在高峰时段的活动强度。这些活动在时间上若与热力高值重叠，会放大短时浓度波动。\n'
        f'3）地理条件方面，{geo_txt}会影响污染物滞留时间与输送路径。地形与下垫面差异会改变局地环流，进而影响高值出现的稳定性。\n'
        '4）经济与产业运行节奏决定了月内排放背景强度。生产旺季、物流活跃期与能源消费变化会共同抬升排放底噪，因此应放在长期框架下综合判断。'
    )
    return settlement, diffusion, cause, 0.66


def run_heatmap_month_analysis(req: AnalysisRequest, *, api_key: str = '') -> AnalysisResponse:
    sources, profile = build_default_sources(req.snapshot.city, req.snapshot.metric, req.snapshot.date)
    cfg = req.client_config or {}
    provider_name = str(cfg.get('provider') or 'bailian').strip().lower()
    model_name = str(cfg.get('model') or '').strip()
    provider = BailianClient(api_key=api_key, model=model_name)

    used_fallback = False
    fallback_reason = None

    if provider.enabled and provider_name in ('bailian', 'openai', 'custom'):
        try:
            out = provider.chat_json(SYSTEM_PROMPT, _build_user_prompt(req, sources, profile), timeout=70)
            settlement_text = str(out.get('settlement_text', '')).strip()
            diffusion_text = str(out.get('diffusion_text', '')).strip()
            cause_text = str(out.get('cause_text', '')).strip()
            confidence = float(out.get('confidence', 0.72))
            if not settlement_text or not diffusion_text or not cause_text:
                raise RuntimeError('Model output missing required fields')
        except Exception as err:
            used_fallback = True
            fallback_reason = str(err)
            settlement_text, diffusion_text, cause_text, confidence = _fallback(req, profile)
    else:
        used_fallback = True
        fallback_reason = 'API Key missing' if not provider.enabled else f'Unsupported provider: {provider_name}'
        settlement_text, diffusion_text, cause_text, confidence = _fallback(req, profile)

    selected_sources = [s for s in sources if str(s.get('url', '')).startswith('local://')][:1]
    selected_sources += [s for s in sources if s.get('snippet')][:6]
    if not selected_sources:
        selected_sources = sources[:6]
    citations = [Citation(**src) for src in selected_sources]

    return AnalysisResponse(
        analysis_id='hm_' + uuid.uuid4().hex[:12],
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
