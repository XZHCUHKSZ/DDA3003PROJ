from __future__ import annotations

from datetime import datetime, timezone

from analysis_service.sources.web_context import fetch_city_profile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_default_sources(city: str) -> tuple[list[dict], dict]:
    now = _now_iso()
    sources = [
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

    profile = fetch_city_profile(city)
    if profile.get('source'):
        sources.append(profile['source'])
    if profile.get('extra_source'):
        sources.append(profile['extra_source'])
    else:
        sources.append(
            {
                'id': 'S4',
                'title': '国家统计局',
                'url': 'https://www.stats.gov.cn/',
                'accessed_at': now,
                'used_fields': ['regional_economy', 'industry_structure'],
            }
        )

    return sources, profile
