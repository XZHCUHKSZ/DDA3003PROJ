from __future__ import annotations

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

from analysis_service.models import (
    AnalysisRequest,
    AnalysisResponse,
    ProviderCheckRequest,
    ProviderCheckResponse,
)
from analysis_service.providers.bailian_client import BailianClient
from analysis_service.pipelines.city_analysis import run_city_analysis
from analysis_service.pipelines.heatmap_month_analysis import run_heatmap_month_analysis
from analysis_service.pipelines.settlement_analysis import run_analysis

app = FastAPI(title='Air Quality AI Analysis Service', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/api/analysis/settlement', response_model=AnalysisResponse)
def analyze_settlement(
    req: AnalysisRequest,
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
) -> AnalysisResponse:
    return run_analysis(req, api_key=(x_api_key or '').strip())


@app.post('/api/analysis/city', response_model=AnalysisResponse)
def analyze_city(
    req: AnalysisRequest,
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
) -> AnalysisResponse:
    return run_city_analysis(req, api_key=(x_api_key or '').strip())


@app.post('/api/analysis/heatmap-month', response_model=AnalysisResponse)
def analyze_heatmap_month(
    req: AnalysisRequest,
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
) -> AnalysisResponse:
    return run_heatmap_month_analysis(req, api_key=(x_api_key or '').strip())


@app.post('/api/provider/check', response_model=ProviderCheckResponse)
def provider_check(
    req: ProviderCheckRequest,
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
) -> ProviderCheckResponse:
    provider = (req.provider or 'bailian').strip().lower()
    model = (req.model or '').strip()
    if provider not in ('bailian', 'openai', 'custom'):
        return ProviderCheckResponse(ok=False, message=f'暂不支持的provider: {provider}')

    client = BailianClient(api_key=(x_api_key or '').strip(), model=model)
    if not client.enabled:
        return ProviderCheckResponse(ok=False, message='API Key 未设置或为空')
    try:
        out = client.chat_json(
            '你是连通性探针。请输出 JSON。',
            '{"task":"connectivity_check","output":"{\"pong\":true}"}',
            timeout=25,
        )
        if isinstance(out, dict):
            return ProviderCheckResponse(ok=True, message='模型鉴权成功，可用于AI分析')
        return ProviderCheckResponse(ok=False, message='模型返回格式异常')
    except Exception as err:
        return ProviderCheckResponse(ok=False, message=f'模型连通失败: {err}')
