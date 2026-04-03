# AI Analysis Service (Bailian)

## 1. Install

```bash
pip install fastapi uvicorn pydantic
```

## 2. Configure

Set environment variable:

```bash
set DASHSCOPE_API_KEY=your_key_here
set BAILIAN_MODEL=qwen-plus
```

If no `DASHSCOPE_API_KEY` is set, service will return rule-based fallback analysis.

## 3. Run

```bash
uvicorn analysis_service.main:app --host 127.0.0.1 --port 8787 --reload
```

Windows quick start:

```bash
start_ai_service.bat
```

## 4. API

- `GET /health`
- `POST /api/analysis/settlement`

Request example:

```json
{
  "snapshot": {
    "city": "常州",
    "date": "20250110",
    "metric": "AQI",
    "radiusKm": 120,
    "in_count": 29,
    "in_avg": 43.6,
    "out_avg": 57.8,
    "delta_day": -2.3,
    "slope_7d": -1.1,
    "diffusion_label": "回落收敛",
    "diffusion_detail": "外圈相对内圈回落，污染影响向中心附近收敛。"
  },
  "history": []
}
```
