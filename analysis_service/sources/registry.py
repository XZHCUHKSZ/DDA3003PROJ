from __future__ import annotations

from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_default_sources() -> list[dict]:
    now = _now_iso()
    return [
        {
            'id': 'S1',
            'title': '项目本地城市空气质量时序数据',
            'url': 'local://air_quality_dataset/current',
            'accessed_at': now,
            'used_fields': ['city', 'date', 'metric', 'radius', 'inner_avg', 'outer_avg', 'delta_day', 'slope_7d'],
        },
        {
            'id': 'S2',
            'title': '生态环境部-城市空气质量状况月报',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/cskqzlzkyb/index.shtml',
            'accessed_at': now,
            'used_fields': ['national_background', 'policy_context'],
        },
    ]
