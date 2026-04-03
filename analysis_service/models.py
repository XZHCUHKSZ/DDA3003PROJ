from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class SettlementSnapshot(BaseModel):
    city: str
    date: str
    metric: str
    radius_km: int = Field(..., alias='radiusKm')
    in_count: int | None = None
    in_avg: float | None = None
    out_avg: float | None = None
    delta_day: float | None = None
    slope_7d: float | None = None
    diffusion_label: str | None = None
    diffusion_detail: str | None = None


class AnalysisRequest(BaseModel):
    snapshot: SettlementSnapshot
    history: list[dict[str, Any]] = Field(default_factory=list)
    client_config: dict[str, Any] = Field(default_factory=dict)


class ProviderCheckRequest(BaseModel):
    provider: str = "bailian"
    model: str = ""


class ProviderCheckResponse(BaseModel):
    ok: bool
    message: str


class Citation(BaseModel):
    id: str
    title: str
    url: str
    accessed_at: str
    used_fields: list[str] = Field(default_factory=list)
    published_at: str | None = None
    snippet: str | None = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    provider: str
    model: str
    generated_at: str
    settlement_text: str
    diffusion_text: str
    cause_text: str
    confidence: float
    citations: list[Citation]
    used_fallback: bool = False
    fallback_reason: str | None = None
