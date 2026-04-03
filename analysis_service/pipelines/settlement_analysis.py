from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from analysis_service.models import AnalysisRequest, AnalysisResponse, Citation
from analysis_service.providers.bailian_client import BailianClient
from analysis_service.sources.registry import build_default_sources


SYSTEM_PROMPT = (
    '你是空气质量聚落分析助手。请严格基于给定数据生成结论，'
    '每段结论都要附带来源ID，如[S1]。禁止编造未提供的数据。'
    '输出必须是JSON对象，字段: settlement_text, diffusion_text, cause_text, confidence。'
)


def _fmt_num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return '--'
    return f'{v:.{digits}f}'


def _build_fallback(req: AnalysisRequest) -> tuple[str, str, str, float]:
    s = req.snapshot
    settlement = (
        f"{s.city} 在 {s.date} 的 {s.metric} 聚落分析显示："
        f"内圈均值 {_fmt_num(s.in_avg, 1)}，外圈均值 {_fmt_num(s.out_avg, 1)}，"
        f"较昨日变化 {_fmt_num(s.delta_day, 1)}，7日斜率 {_fmt_num(s.slope_7d, 2)}。 [S1]"
    )
    diffusion = (
        f"扩散判断：{s.diffusion_label or '待判定'}。"
        f"{s.diffusion_detail or '当前数据用于趋势提示，建议结合气象风场做复核。'} [S1][S2]"
    )
    cause = (
        '可能成因包括区域传输、局地排放强度变化和不利气象条件叠加。'
        '建议联动风速风向、湿度和降水数据进行进一步验证。 [S1][S2]'
    )
    return settlement, diffusion, cause, 0.62


def _build_user_prompt(req: AnalysisRequest, sources: list[dict]) -> str:
    return json.dumps(
        {
            'task': '对聚落分析做中文深度解读，强调扩散及成因，并附来源ID引用',
            'snapshot': req.snapshot.model_dump(by_alias=True),
            'history': req.history[-14:],
            'sources': sources,
            'output_requirements': {
                'language': 'zh-CN',
                'max_length': 600,
                'must_cite': True,
            },
        },
        ensure_ascii=False,
    )


def run_analysis(req: AnalysisRequest) -> AnalysisResponse:
    sources = build_default_sources()
    provider = BailianClient()
    used_fallback = False

    if provider.enabled:
        try:
            model_out = provider.chat_json(SYSTEM_PROMPT, _build_user_prompt(req, sources), timeout=70)
            settlement_text = str(model_out.get('settlement_text', '')).strip()
            diffusion_text = str(model_out.get('diffusion_text', '')).strip()
            cause_text = str(model_out.get('cause_text', '')).strip()
            confidence = float(model_out.get('confidence', 0.7))
            if not settlement_text or not diffusion_text or not cause_text:
                raise RuntimeError('Model output missing required fields')
        except Exception:
            used_fallback = True
            settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req)
    else:
        used_fallback = True
        settlement_text, diffusion_text, cause_text, confidence = _build_fallback(req)

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
