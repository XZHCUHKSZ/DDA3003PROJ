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
    '每段结论都要附带来源ID，如[S1]。禁止编造未提供的数据。'
    '输出必须是JSON对象，字段: settlement_text, diffusion_text, cause_text, confidence。'
)


def _fmt_num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return '--'
    return f'{v:.{digits}f}'


def _build_fallback(req: AnalysisRequest, profile: dict) -> tuple[str, str, str, float]:
    s = req.snapshot
    econ = profile.get('economic_level') or '经济体量信息待补充'
    gdp_hint = profile.get('gdp_hint')
    industries = profile.get('industries') or []
    industry_text = '、'.join(industries[:4]) if industries else '主导产业信息待补充'
    econ_text = f'{econ}（约{gdp_hint}）' if gdp_hint else econ
    settlement = (
        f"一句话结论：{s.city} 在 {s.date} 的 {s.metric} 水平最近波动"
        f"{'明显' if (s.delta_day or 0) and abs(s.delta_day or 0) >= 8 else '不大'}。"
        f"当前内圈均值 {_fmt_num(s.in_avg, 1)}，外圈均值 {_fmt_num(s.out_avg, 1)}，"
        f"较昨日 {_fmt_num(s.delta_day, 1)}，7日趋势 {_fmt_num(s.slope_7d, 2)}/天。 [S1]"
    )
    diffusion = (
        f"扩散判断：{s.diffusion_label or '待判定'}。"
        f"{s.diffusion_detail or '从内外圈差值看，短期方向仍需持续观察。'}"
        '建议连续看3-7天变化，不要只看单日。 [S1][S2]'
    )
    cause = (
        f"城市画像补充：{s.city} 的经济画像为“{econ_text}”，"
        f"产业关键词包括：{industry_text}。"
        '当产业活动强度上升且气象扩散条件偏弱时，更容易出现短时抬升。'
        '建议结合风速风向、湿度和降水继续验证。 [S1][S2][S3]'
    )
    return settlement, diffusion, cause, 0.62


def _build_user_prompt(req: AnalysisRequest, sources: list[dict], profile: dict) -> str:
    return json.dumps(
        {
            'task': '对聚落分析做中文解读：必须通俗、短句、可执行建议、附来源ID引用',
            'snapshot': req.snapshot.model_dump(by_alias=True),
            'history': req.history[-14:],
            'city_profile': {
                'economic_level': profile.get('economic_level'),
                'gdp_hint': profile.get('gdp_hint'),
                'industries': profile.get('industries', []),
                'profile_text': profile.get('profile_text', ''),
            },
            'sources': sources,
            'output_requirements': {
                'language': 'zh-CN',
                'max_length': 600,
                'must_cite': True,
                'audience': '普通公众',
                'style': '先结论后解释，避免过度专业术语',
            },
        },
        ensure_ascii=False,
    )


def run_analysis(req: AnalysisRequest) -> AnalysisResponse:
    sources, profile = build_default_sources(req.snapshot.city)
    provider = BailianClient()
    used_fallback = False

    if provider.enabled:
        try:
            model_out = provider.chat_json(SYSTEM_PROMPT, _build_user_prompt(req, sources, profile), timeout=70)
            settlement_text = str(model_out.get('settlement_text', '')).strip()
            diffusion_text = str(model_out.get('diffusion_text', '')).strip()
            cause_text = str(model_out.get('cause_text', '')).strip()
            confidence = float(model_out.get('confidence', 0.7))
            if not settlement_text or not diffusion_text or not cause_text:
                raise RuntimeError('Model output missing required fields')
        except Exception:
            used_fallback = True
            settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)
    else:
        used_fallback = True
        settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req, profile)

    citations = [Citation(**src) for src in sources]
    return AnalysisResponse(
        analysis_id='ana_' + uuid.uuid4().hex[:12],
        provider='bailian' if provider.enabled and not used_fallback else 'fallback',
        model=provider.model if provider.enabled else 'rule-template',
        generated_at=datetime.now(timezone.utc).isoformat(),
        settlement_text=settlement_text,
        diffusion_text=diffusion_text,
        cause_text=cause_text,
        confidence=max(0.0, min(1.0, confidence)),
        citations=citations,
        used_fallback=used_fallback,
    )
