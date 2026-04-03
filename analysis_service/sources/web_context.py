from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

INDUSTRY_KEYWORDS = [
    '工程机械', '汽车', '电子信息', '钢铁', '石化', '有色金属',
    '装备制造', '生物医药', '新能源', '纺织', '食品加工', '新材料',
    '软件', '集成电路', '港口物流', '文旅', '金融服务'
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_json(url: str, timeout: int = 8) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None


def _extract_gdp_level(text: str) -> tuple[str, str | None]:
    t = text.replace(',', '')
    # Match "GDP...x万亿元" or simple "x万亿元"
    m = re.search(r'GDP[^。；\n]{0,40}?(\d+(?:\.\d+)?)\s*万亿元', t, flags=re.IGNORECASE)
    if not m:
        m = re.search(r'(\d+(?:\.\d+)?)\s*万亿元', t)
    if not m:
        return '经济体量信息待补充', None

    val = float(m.group(1))
    if val >= 2.0:
        return '经济体量很大', f'{val:.2f}万亿元'
    if val >= 1.0:
        return '经济体量较大', f'{val:.2f}万亿元'
    if val >= 0.5:
        return '经济体量中等', f'{val:.2f}万亿元'
    return '经济体量相对较小', f'{val:.2f}万亿元'


def _extract_industries(text: str) -> list[str]:
    found: list[str] = []
    for kw in INDUSTRY_KEYWORDS:
        if kw in text and kw not in found:
            found.append(kw)
    return found[:6]


def fetch_city_profile(city: str) -> dict:
    query_city = city.replace('市', '').strip()
    encoded = urllib.parse.quote(query_city)
    summary_url = f'https://zh.wikipedia.org/api/rest_v1/page/summary/{encoded}'
    data = _http_json(summary_url)

    if not data:
        return {
            'economic_level': '经济体量信息待补充',
            'gdp_hint': None,
            'industries': [],
            'profile_text': '',
            'source': {
                'id': 'S3',
                'title': f'{query_city}（在线公开资料）',
                'url': f'https://zh.wikipedia.org/wiki/{encoded}',
                'accessed_at': _now_iso(),
                'used_fields': ['city_profile'],
            },
        }

    extract = str(data.get('extract', '') or '')
    econ_level, gdp_hint = _extract_gdp_level(extract)
    industries = _extract_industries(extract)

    return {
        'economic_level': econ_level,
        'gdp_hint': gdp_hint,
        'industries': industries,
        'profile_text': extract[:500],
        'source': {
            'id': 'S3',
            'title': data.get('title') or f'{query_city}（在线公开资料）',
            'url': data.get('content_urls', {}).get('desktop', {}).get('page')
                or f'https://zh.wikipedia.org/wiki/{encoded}',
            'accessed_at': _now_iso(),
            'used_fields': ['economic_level', 'industry_keywords', 'city_profile_text'],
        },
    }
