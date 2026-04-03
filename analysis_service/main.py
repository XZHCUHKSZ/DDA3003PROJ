from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analysis_service.models import AnalysisRequest, AnalysisResponse
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
def analyze_settlement(req: AnalysisRequest) -> AnalysisResponse:
    return run_analysis(req)
