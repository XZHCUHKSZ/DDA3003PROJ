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

GEO_KEYWORDS = [
    '沿海', '海岸', '港口', '平原', '盆地', '山地', '丘陵', '河谷', '河网', '季风', '台风'
]

CITY_PROFILE_HINTS: dict[str, dict] = {
    '淮北': {
        'province': '安徽',
        'economic_level': '资源型城市，经济体量中等偏小',
        'gdp_hint': '约0.14万亿元（近年量级）',
        'industries': ['煤化工', '电力', '新材料', '装备制造', '食品加工'],
        'geo_factors': ['华北平原南缘', '冬季静稳天气易出现', '秋冬颗粒物扩散条件偏弱'],
        'source': {
            'id': 'S4',
            'title': '安徽省统计局',
            'url': 'https://tjj.ah.gov.cn/',
        },
        'supplementary_sources': [
            {'title': '安徽省生态环境厅', 'url': 'https://sthjt.ah.gov.cn/'},
            {'title': '淮北市人民政府-统计公报', 'url': 'https://www.huaibei.gov.cn/'},
        ],
    },
    '长沙': {
        'province': '湖南',
        'economic_level': '省会城市，经济体量较大',
        'gdp_hint': '约1.4万亿元（近年量级）',
        'industries': ['工程机械', '汽车及零部件', '电子信息', '新材料', '食品制造'],
        'geo_factors': ['内陆河网城市', '夏季高温高湿', '静稳天气时扩散效率下降'],
        'source': {
            'id': 'S4',
            'title': '湖南省统计局',
            'url': 'http://tjj.hunan.gov.cn/',
        },
        'supplementary_sources': [
            {'title': '湖南省生态环境厅', 'url': 'https://sthjt.hunan.gov.cn/'},
            {'title': '长沙市人民政府-统计公报', 'url': 'https://www.changsha.gov.cn/'},
        ],
    },
    '泉州': {
        'province': '福建',
        'economic_level': '沿海制造业与民营经济活跃城市',
        'gdp_hint': '约1.2万亿元（近年量级）',
        'industries': ['纺织鞋服', '石化', '机械装备', '建材', '电子信息'],
        'geo_factors': ['沿海港口城市', '受海陆风与季风影响明显', '近海湿润空气对二次颗粒物形成有促进作用'],
        'source': {
            'id': 'S4',
            'title': '福建省统计局',
            'url': 'https://tjj.fujian.gov.cn/',
        },
        'supplementary_sources': [
            {'title': '福建省生态环境厅', 'url': 'https://sthjt.fujian.gov.cn/'},
            {'title': '泉州市人民政府-统计公报', 'url': 'https://www.quanzhou.gov.cn/'},
        ],
    },
}


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
        return '', None

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


def _extract_geo_factors(text: str) -> list[str]:
    found: list[str] = []
    for kw in GEO_KEYWORDS:
        if kw in text and kw not in found:
            found.append(kw)
    return found[:5]


def fetch_city_profile(city: str) -> dict:
    query_city = city.replace('市', '').strip()
    encoded = urllib.parse.quote(query_city)
    summary_url = f'https://zh.wikipedia.org/api/rest_v1/page/summary/{encoded}'
    data = _http_json(summary_url)

    hint = CITY_PROFILE_HINTS.get(query_city)

    if not data:
        out = {
            'economic_level': '',
            'gdp_hint': None,
            'industries': [],
            'geo_factors': [],
            'profile_text': '',
            'source': {
                'id': 'S3',
                'title': f'{query_city}（在线公开资料）',
                'url': f'https://zh.wikipedia.org/wiki/{encoded}',
                'accessed_at': _now_iso(),
                'used_fields': ['city_profile'],
            },
        }
        if hint:
            out['economic_level'] = hint.get('economic_level') or out['economic_level']
            out['gdp_hint'] = hint.get('gdp_hint') or out['gdp_hint']
            out['industries'] = hint.get('industries') or out['industries']
            out['geo_factors'] = hint.get('geo_factors') or out['geo_factors']
            out['province'] = hint.get('province')
            out['extra_source'] = {
                'id': hint.get('source', {}).get('id', 'S4'),
                'title': hint.get('source', {}).get('title', f'{hint.get("province","")}统计局'),
                'url': hint.get('source', {}).get('url', ''),
                'accessed_at': _now_iso(),
                'used_fields': ['regional_economy', 'industry_structure'],
            }
            out['supplementary_sources'] = [
                {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'accessed_at': _now_iso(),
                    'used_fields': ['regional_policy', 'industry_background', 'city_context'],
                }
                for item in hint.get('supplementary_sources', [])
            ]
        return out

    extract = str(data.get('extract', '') or '')
    econ_level, gdp_hint = _extract_gdp_level(extract)
    industries = _extract_industries(extract)
    geo_factors = _extract_geo_factors(extract)
    if hint:
        if not econ_level and hint.get('economic_level'):
            econ_level = hint['economic_level']
        if not gdp_hint and hint.get('gdp_hint'):
            gdp_hint = hint['gdp_hint']
        if not industries:
            industries = hint.get('industries', [])
        if not geo_factors:
            geo_factors = hint.get('geo_factors', [])

    out = {
        'economic_level': econ_level,
        'gdp_hint': gdp_hint,
        'industries': industries,
        'geo_factors': geo_factors,
        'profile_text': extract[:500],
        'province': hint.get('province') if hint else None,
        'source': {
            'id': 'S3',
            'title': data.get('title') or f'{query_city}（在线公开资料）',
            'url': data.get('content_urls', {}).get('desktop', {}).get('page')
                or f'https://zh.wikipedia.org/wiki/{encoded}',
            'accessed_at': _now_iso(),
            'used_fields': ['economic_level', 'industry_keywords', 'city_profile_text'],
        },
    }
    if hint:
        out['extra_source'] = {
            'id': hint.get('source', {}).get('id', 'S4'),
            'title': hint.get('source', {}).get('title', f'{hint.get("province","")}统计局'),
            'url': hint.get('source', {}).get('url', ''),
            'accessed_at': _now_iso(),
            'used_fields': ['regional_economy', 'industry_structure'],
        }
        out['supplementary_sources'] = [
            {
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'accessed_at': _now_iso(),
                'used_fields': ['regional_policy', 'industry_background', 'city_context'],
            }
            for item in hint.get('supplementary_sources', [])
        ]
    return out
