from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from analysis_service.models import AnalysisRequest, AnalysisResponse, Citation
from analysis_service.providers.bailian_client import BailianClient
from analysis_service.sources.registry import build_default_sources


SYSTEM_PROMPT = (
    '你是城市空气质量分析助手。请用普通人看得懂的中文表达，避免术语堆砌。'
    '请先给结论，再讲风险，再讲成因。成因用 1) 2) 3) 4) 四条，经济相关放最后。'
    '输出必须是JSON对象，字段: settlement_text, diffusion_text, cause_text, confidence。'
)


def _fmt(v: float | None, digits: int = 1) -> str:
    if v is None:
        return '--'
    return f'{v:.{digits}f}'


def _build_user_prompt(req: AnalysisRequest, sources: list[dict], profile: dict) -> str:
    return json.dumps(
        {
            'task': '基于城市近7日序列与当日分位，给出城市分析。必须通俗、可读、结论明确。',
            'snapshot': req.snapshot.model_dump(by_alias=True),
            'history': req.history[-14:],
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
                'style': '短句、少术语、先结论',
                'cause_format': 'strict_numbered_1_to_4',
                'cause_economic_last': True,
            },
        },
        ensure_ascii=False,
    )


def _build_fallback(req: AnalysisRequest, profile: dict) -> tuple[str, str, str, float]:
    s = req.snapshot
    c = req.city_context or {}
    current = c.get('current')
    delta = c.get('delta_day')
    slope = c.get('slope_7d')
    pct = c.get('national_percentile')
    risk = c.get('risk_level') or '中等'
    industries = profile.get('industries') or []
    geo = profile.get('geo_factors') or []

    settlement = (
        f"一句话结论：{s.city}{s.date}的{s.metric}为{_fmt(current)}，"
        f"较昨日{_fmt(delta)}，近7日斜率{_fmt(slope,2)}/天；"
        f"全国相对分位约{_fmt(pct)}%。整体处于{risk}风险水平。"
    )
    diffusion = (
        f"短期风险：若未来2-3天仍处于静稳天气，{s.metric}可能维持高位波动。"
        "建议同时观察风速、湿度与降水，判断是本地累积还是区域传输主导。"
    )

    ind_text = '、'.join(industries[:4]) if industries else '本地工业与交通排放'
    geo_text = '、'.join(geo[:3]) if geo else '地形与边界层条件'
    cause = (
        "1) 当前污染变化首先受短期气象条件影响，弱风与高湿会降低扩散效率。\n"
        f"2) 本地排放端可重点关注{ind_text}，活动强度变化会传导到指标。\n"
        f"3) 地理条件方面，{s.city}的{geo_text}特征会影响污染物滞留与输送路径。\n"
        "4) 经济与产业层面，城市运行强度变化会影响排放总量与时段分布（该因素放在长期视角评估更稳妥）。"
    )
    return settlement, diffusion, cause, 0.63


def run_city_analysis(req: AnalysisRequest, *, api_key: str = '') -> AnalysisResponse:
    sources, profile = build_default_sources(req.snapshot.city, req.snapshot.metric, req.snapshot.date)
    client_cfg = req.client_config or {}
    provider_name = str(client_cfg.get('provider') or 'bailian').strip().lower()
    model_name = str(client_cfg.get('model') or '').strip()

    provider = BailianClient(api_key=api_key, model=model_name)
    used_fallback = False
    fallback_reason: str | None = None

    if provider.enabled and provider_name in ('bailian', 'openai', 'custom'):
        try:
            model_out = provider.chat_json(SYSTEM_PROMPT, _build_user_prompt(req, sources, profile), timeout=70)
            settlement_text = str(model_out.get('settlement_text', '')).strip()
            diffusion_text = str(model_out.get('diffusion_text', '')).strip()
            cause_text = str(model_out.get('cause_text', '')).strip()
            confidence = float(model_out.get('confidence', 0.72))
            if not settlement_text or not diffusion_text or not cause_text:
                raise RuntimeError('Model output missing required fields')
        except Exception as err:
            used_fallback = True
            fallback_reason = str(err)
            settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)
    else:
        used_fallback = True
        fallback_reason = 'API Key missing' if not provider.enabled else f'Unsupported provider: {provider_name}'
        settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)

    selected_sources = [s for s in sources if str(s.get('url', '')).startswith('local://')][:1]
    selected_sources += [s for s in sources if s.get('snippet')][:6]
    if not selected_sources:
        selected_sources = sources[:6]

    citations = [Citation(**src) for src in selected_sources]
    return AnalysisResponse(
        analysis_id='city_' + uuid.uuid4().hex[:12],
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
