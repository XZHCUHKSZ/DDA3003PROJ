from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


SEARCH_ENDPOINT = 'https://www.bing.com/search?q='

PREFERRED_DOMAIN_HINTS = (
    '.gov.cn',
    'gov.cn',
    'mee.gov.cn',
    'cma.gov.cn',
    'stats.gov.cn',
    'cnemc.cn',
    '.edu.cn',
    'wikipedia.org',
)
NATIONAL_CONTEXT_DOMAINS = (
    'mee.gov.cn',
    'cma.gov.cn',
    'stats.gov.cn',
    'cnemc.cn',
)
BLOCKED_DOMAIN_HINTS = (
    'bing.com',
    'duckduckgo.com',
    'baidu.com',
    'so.com',
)

METRIC_WORDS = {
    'AQI': ['AQI', '空气质量'],
    'PM2.5_24h': ['PM2.5', '颗粒物', '细颗粒物'],
    'PM10_24h': ['PM10', '可吸入颗粒物', '扬尘'],
    'SO2_24h': ['SO2', '二氧化硫', '燃煤'],
    'NO2_24h': ['NO2', '二氧化氮', '交通排放'],
    'O3_8h': ['臭氧', 'O3', '光化学'],
    'O3_8h_24h': ['臭氧', 'O3', '光化学'],
}

TOPIC_KEYWORDS = ['空气', '污染', '生态环境', '统计', '经济', '产业', '地理', '气象', '扩散', '排放']
NOISE_KEYWORDS = ['旅游', '攻略', '酒店', '美食', '电视剧', '动漫', '小说', '游戏', '短视频', '八卦']


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_text(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(
        url=url,
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def _strip_tags(s: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def _extract_bing_results(html_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r'<li class="b_algo"[\s\S]*?<h2[^>]*><a[^>]*href="(?P<href>https?://[^"]+)"[^>]*>(?P<title>[\s\S]*?)</a></h2>'
        r'[\s\S]*?(?:<p class="b_lineclamp\d*">(?P<cap>[\s\S]*?)</p>)?',
        re.IGNORECASE,
    )
    results: list[dict[str, str]] = []
    for m in pattern.finditer(html_text):
        href = html.unescape(m.group('href')).strip()
        title = _strip_tags(m.group('title'))
        cap = _strip_tags(m.group('cap') or '')
        if not href.startswith('http'):
            continue
        if not title:
            continue
        results.append({'title': title, 'url': href, 'caption': cap})
    return results


def _domain(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ''


def _is_national_context_domain(url: str) -> bool:
    d = _domain(url)
    return any(x in d for x in NATIONAL_CONTEXT_DOMAINS)


def _is_domain_allowed(url: str) -> bool:
    d = _domain(url)
    if not d:
        return False
    if any(hint in d for hint in BLOCKED_DOMAIN_HINTS):
        return False
    return True


def _extract_date(text: str) -> str | None:
    m = re.search(r'(20\d{2})[年\-/\.](\d{1,2})[月\-/\.](\d{1,2})', text)
    if not m:
        return None
    y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
    return f'{y}-{mo:02d}-{d:02d}'


def _clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\u3000', ' ')
    return text.strip()


def _html_to_text(raw_html: str) -> str:
    # remove script/style
    text = re.sub(r'<script[\s\S]*?</script>', ' ', raw_html, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    return _clean_text(html.unescape(text))


def _pick_snippet(text: str, keywords: list[str], max_len: int = 180) -> str:
    if not text:
        return ''
    compact = _clean_text(text)
    for kw in keywords:
        idx = compact.find(kw)
        if idx >= 0:
            start = max(0, idx - 40)
            end = min(len(compact), idx + max_len)
            return compact[start:end]
    return compact[:max_len]


def _score_doc(title: str, snippet: str, url: str, city: str, keywords: list[str], year: str) -> float:
    full = f'{title} {snippet}'
    score = 0.0
    if city and city in full:
        score += 2.0
    else:
        score -= 2.2
    for kw in keywords:
        if kw and kw in full:
            score += 1.0
    if year and year in full:
        score += 0.8
    d = _domain(url)
    if any(hint in d for hint in PREFERRED_DOMAIN_HINTS):
        score += 1.2
    elif d.endswith('.news') or 'news.' in d:
        score += 0.6
    return score


def _build_queries(city: str, metric: str, date_str: str) -> list[str]:
    y = (date_str or '')[:4]
    words = METRIC_WORDS.get(metric, [metric, '空气质量'])
    metric_q = ' '.join(words[:2])
    return [
        f'{city} {metric_q} 空气质量 {y} site:gov.cn',
        f'{city} 统计公报 GDP 产业结构 {y} site:gov.cn',
        f'{city} 地形 气候 污染扩散 site:gov.cn',
        f'{city} 生态环境 空气质量 通报 {y}',
    ]


def build_live_web_sources(city: str, metric: str, date_str: str, max_sources: int = 6) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    now = _now_iso()
    city_name = city.replace('市', '').strip()
    year = (date_str or '')[:4]
    queries = _build_queries(city_name, metric, date_str)
    metric_words = METRIC_WORDS.get(metric, [])
    keywords = [city_name, metric] + metric_words + ['产业', '经济', '地形', '气象']

    candidates: dict[str, dict[str, str]] = {}
    for q in queries:
        try:
            url = SEARCH_ENDPOINT + urllib.parse.quote(q) + '&setlang=zh-cn'
            search_html = _http_text(url, timeout=10)
        except Exception:
            continue
        for item in _extract_bing_results(search_html):
            url = item['url']
            if not _is_domain_allowed(url):
                continue
            if url not in candidates:
                candidates[url] = item
            if len(candidates) >= 20:
                break
        if len(candidates) >= 20:
            break

    ranked: list[dict[str, Any]] = []
    for item in candidates.values():
        url = item['url']
        title = item['title']
        cap = item.get('caption', '')
        try:
            text = _html_to_text(_http_text(url, timeout=10))
        except Exception:
            continue
        snippet = _pick_snippet(text or cap, keywords, max_len=200)
        if not snippet:
            continue
        full_text = f'{title} {snippet}'
        if any(noise in full_text for noise in NOISE_KEYWORDS):
            continue
        city_hit = city_name in full_text
        metric_hit = any(w in full_text for w in metric_words)
        cause_hit = any(w in full_text for w in ['产业', '经济', '地理', '地形', '气象', '扩散', '排放', '通报', '公报'])
        # 强相关门槛：必须涉及当前污染物或成因主题；且城市未命中时只允许国家级背景域名通过
        if not (metric_hit or cause_hit):
            continue
        if (not city_hit) and (not _is_national_context_domain(url)):
            continue
        # 过滤泛城市百科类页面，避免“只搜城市名”
        d = _domain(url)
        if ('wikipedia.org' in d) and (not metric_hit) and (not cause_hit):
            continue
        topic_hits = sum(1 for kw in (TOPIC_KEYWORDS + metric_words) if kw and kw in full_text)
        if topic_hits < 2:
            continue
        pub = _extract_date(text) or _extract_date(cap) or _extract_date(title)
        score = _score_doc(title, snippet, url, city_name, keywords, year)
        if score < 2.0:
            continue
        ranked.append(
            {
                'title': title,
                'url': url,
                'accessed_at': now,
                'published_at': pub,
                'snippet': snippet,
                'score': score,
                'used_fields': ['web_evidence', 'city_metric_context', 'economy_industry_geography'],
            }
        )

    ranked.sort(key=lambda x: x['score'], reverse=True)
    ranked = ranked[:max_sources]

    for idx, src in enumerate(ranked, start=1):
        src['id'] = f'W{idx}'

    evidence = [
        {
            'id': src['id'],
            'title': src['title'],
            'url': src['url'],
            'published_at': src.get('published_at'),
            'snippet': src.get('snippet', ''),
            'score': src.get('score', 0.0),
        }
        for src in ranked
    ]
    return ranked, evidence
