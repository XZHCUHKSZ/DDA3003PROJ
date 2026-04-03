from __future__ import annotations

from datetime import datetime, timezone

from analysis_service.sources.live_search import build_live_web_sources
from analysis_service.sources.web_context import fetch_city_profile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _metric_reference_source(metric: str, now: str) -> dict:
    metric_map = {
        'PM2.5_24h': {
            'title': '生态环境部-颗粒物（PM2.5/PM10）污染防治与监测解读',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/',
            'used_fields': ['pm25', 'pm10', 'primary_secondary_particle_context'],
        },
        'PM10_24h': {
            'title': '生态环境部-颗粒物（PM2.5/PM10）污染防治与监测解读',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/',
            'used_fields': ['pm25', 'pm10', 'dust_resuspension_context'],
        },
        'SO2_24h': {
            'title': '生态环境部-SO2污染与固定源治理资料',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/',
            'used_fields': ['so2', 'coal_combustion', 'desulfurization_context'],
        },
        'NO2_24h': {
            'title': '生态环境部-NOx/NO2污染与交通工业排放资料',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/',
            'used_fields': ['no2', 'mobile_source', 'industrial_combustion'],
        },
        'O3_8h': {
            'title': '中国气象局/生态环境部门-臭氧与光化学污染科普与预报资料',
            'url': 'https://www.cma.gov.cn/',
            'used_fields': ['o3', 'photochemical_reaction', 'temperature_radiation'],
        },
        'O3_8h_24h': {
            'title': '中国气象局/生态环境部门-臭氧与光化学污染科普与预报资料',
            'url': 'https://www.cma.gov.cn/',
            'used_fields': ['o3', 'photochemical_reaction', 'temperature_radiation'],
        },
    }
    fallback = {
        'title': '中国环境监测总站-空气质量监测与解读',
        'url': 'https://www.cnemc.cn/',
        'used_fields': ['pollutant_metric_context'],
    }
    picked = metric_map.get(metric, fallback)
    return {
        'title': picked['title'],
        'url': picked['url'],
        'accessed_at': now,
        'used_fields': picked['used_fields'],
    }


def _normalize_sources(raw_sources: list[dict], now: str) -> list[dict]:
    out: list[dict] = []
    seen_urls: set[str] = set()
    for src in raw_sources:
        if not src:
            continue
        url = str(src.get('url') or '').strip()
        title = str(src.get('title') or '').strip()
        if not url or not title:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        out.append(
            {
                'title': title,
                'url': url,
                'accessed_at': src.get('accessed_at') or now,
                'used_fields': src.get('used_fields') or [],
                'published_at': src.get('published_at'),
                'snippet': src.get('snippet'),
            }
        )

    for idx, src in enumerate(out, start=1):
        src['id'] = f'S{idx}'
    return out


def _looks_like_weak_city_page(src: dict) -> bool:
    title = str(src.get('title') or '')
    url = str(src.get('url') or '')
    if ('在线公开资料' in title) or ('wikipedia.org' in url):
        return True
    return False


def build_default_sources(city: str, metric: str, date_str: str | None = None) -> tuple[list[dict], dict]:
    now = _now_iso()
    sources_pool = [
        {
            'title': '项目本地城市空气质量时序数据',
            'url': 'local://air_quality_dataset/current',
            'accessed_at': now,
            'used_fields': ['city', 'date', 'metric', 'radius', 'inner_avg', 'outer_avg', 'delta_day', 'slope_7d'],
        },
        {
            'title': '生态环境部-城市空气质量状况月报',
            'url': 'https://www.mee.gov.cn/hjzl/dqhj/cskqzlzkyb/index.shtml',
            'accessed_at': now,
            'used_fields': ['national_background', 'policy_context'],
        },
    ]

    profile = fetch_city_profile(city)
    live_sources, evidence = build_live_web_sources(city, metric, date_str or '')
    profile['web_evidence'] = evidence
    for src in live_sources:
        sources_pool.append(src)

    # 仅在实时证据不足时追加静态背景来源，且过滤弱相关城市资料页
    if len(live_sources) < 2:
        if profile.get('source') and not _looks_like_weak_city_page(profile['source']):
            sources_pool.append(profile['source'])
        if profile.get('extra_source'):
            sources_pool.append(profile['extra_source'])
        for extra in profile.get('supplementary_sources', []):
            sources_pool.append(extra)

    if len(live_sources) < 2:
        sources_pool.append(
            {
                'title': '中国气象局-气象条件与污染扩散背景资料',
                'url': 'https://www.cma.gov.cn/',
                'accessed_at': now,
                'used_fields': ['wind', 'boundary_layer', 'humidity', 'precipitation'],
            }
        )
        sources_pool.append(
            {
                'title': '国家统计局-区域经济与产业结构年度数据',
                'url': 'https://www.stats.gov.cn/',
                'accessed_at': now,
                'used_fields': ['regional_economy', 'industry_structure'],
            }
        )
        sources_pool.append(_metric_reference_source(metric, now))

    if (len(live_sources) < 2) and (not profile.get('extra_source')):
        sources_pool.append(
            {
                'title': '国家统计局',
                'url': 'https://www.stats.gov.cn/',
                'accessed_at': now,
                'used_fields': ['regional_economy', 'industry_structure'],
            }
        )

    sources = _normalize_sources(sources_pool, now)
    return sources, profile
