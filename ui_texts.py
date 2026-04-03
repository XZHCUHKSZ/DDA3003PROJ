"""
Centralized UI copy to avoid scattered hard-coded strings and encoding issues.
"""

from __future__ import annotations

import json


TEXTS: dict[str, str] = {
    "app.title": "\u5168\u56fd\u57ce\u5e02\u7a7a\u6c14\u8d28\u91cf\u5b9e\u65f6\u53d1\u5e03\u5e73\u53f0",
    "app.subtitle.normal": "\u65e5\u671f: {date}  \u65f6\u95f4: 00:00  |  \u70b9\u51fb\u57ce\u5e02\u6807\u8bb0\u67e5\u770b\u8be6\u60c5",
    "app.subtitle.compare": "\u65e5\u671f: {date}  \u65f6\u95f4: 00:00  |  \u591a\u57ce\u5e02\u5bf9\u6bd4\u6a21\u5f0f",
    "label.excellent": "\u4f18(0-50)",
    "label.good": "\u826f(51-100)",
    "label.light": "\u8f7b\u5ea6\u6c61\u67d3(101-150)",
    "label.moderate": "\u4e2d\u5ea6\u6c61\u67d3(151-200)",
    "label.heavy": "\u91cd\u5ea6\u6c61\u67d3(201-300)",
    "label.severe": "\u4e25\u91cd\u6c61\u67d3(>300)",
    "loader.status.init": "\u6b63\u5728\u521d\u59cb\u5316\u53ef\u89c6\u5316\u5f15\u64ce...",
    "loader.sub.init": "\u6b63\u5728\u51c6\u5907\u5730\u56fe\u7ec4\u4ef6\u4e0e\u57ce\u5e02\u6570\u636e",
    "loader.hint.default": "\u9996\u6b21\u52a0\u8f7d\u7ea6 8-12 \u79d2\uff0c\u8bf7\u7a0d\u5019",
    "loader.enter.loading": "\u52a0\u8f7d\u4e2d...",
    "loader.retry": "\u5237\u65b0\u91cd\u8bd5",
    "loader.status.framework": "\u6b63\u5728\u88c5\u8f7d\u9875\u9762\u6846\u67b6...",
    "loader.sub.framework": "\u6b63\u5728\u6302\u8f7d\u4ea4\u4e92\u63a7\u4ef6",
    "loader.status.connect_map": "\u6b63\u5728\u8fde\u63a5\u5730\u56fe\u5f15\u64ce...",
    "loader.sub.connect_map": "\u6b63\u5728\u6574\u7406\u4e3b\u89c6\u56fe\u5e03\u5c40",
    "loader.status.bind": "\u6b63\u5728\u7ed1\u5b9a\u5730\u56fe\u4ea4\u4e92...",
    "loader.sub.bind": "\u6b63\u5728\u540c\u6b65\u65f6\u95f4\u8f74\u4e0e\u7f29\u653e\u63a7\u5236",
    "loader.status.render": "\u6b63\u5728\u6e32\u67d3\u4e3b\u5730\u56fe...",
    "loader.sub.render": "\u5373\u5c06\u5b8c\u6210",
    "loader.status.failed": "\u5730\u56fe\u521d\u59cb\u5316\u5931\u8d25",
    "loader.sub.failed": "\u672a\u68c0\u6d4b\u5230\u5730\u56fe\u5b9e\u4f8b\uff0c\u8bf7\u5237\u65b0\u91cd\u8bd5",
    "loader.hint.slow": "\u7f51\u7edc\u8f83\u6162\uff0c\u4ecd\u5728\u52a0\u8f7d\u5730\u56fe\u4e0e\u6570\u636e...",
    "loader.status.ready": "\u52a0\u8f7d\u5b8c\u6210",
    "loader.sub.ready": "\u8bf7\u70b9\u51fb\u4e0b\u65b9\u6309\u94ae\u8fdb\u5165\u9875\u9762",
    "loader.hint.ready": "\u6838\u5fc3\u6570\u636e\u5df2\u5c31\u7eea",
    "loader.enter.ready": "\u8fdb\u5165\u5730\u56fe",
    "control.compare": "\u5bf9\u6bd4\u6a21\u5f0f",
    "control.zoom_in": "\u653e\u5927",
    "control.zoom_out": "\u7f29\u5c0f",
    "control.reset": "\u91cd\u7f6e\u89c6\u56fe",
    "control.goto": "\u8df3\u8f6c\u5230\u8be6\u60c5",
    "control.detail": "\u8be6\u60c5",
    "timeline.prev7": "\u524d 7 \u5929",
    "timeline.prev1": "\u524d 1 \u5929",
    "timeline.next1": "\u540e 1 \u5929",
    "timeline.next7": "\u540e 7 \u5929",
    "scroll.hint": "\u4e0b\u6ed1\u67e5\u770b\u57ce\u5e02\u8be6\u60c5\u4e0e\u5386\u53f2\u8d8b\u52bf",
    "city.placeholder": "\u70b9\u51fb\u5730\u56fe\u4e0a\u7684\u57ce\u5e02\u6807\u8bb0\uff0c\u5728\u8fd9\u91cc\u67e5\u770b\u8be6\u7ec6\u6570\u636e",
    "city.filter": "\u56fe\u8868\u663e\u793a",
    "city.pollutants": "\u6c61\u67d3\u7269\u6d53\u5ea6",
    "city.health": "\u5065\u5eb7\u5efa\u8bae",
    "city.trend7d": "\u8fd17\u65e5\u8d8b\u52bf",
    "city.compare_hint": "\u70b9\u51fb\u5730\u56fe\u57ce\u5e02\u52a0\u5165\u5bf9\u6bd4",
    "city.no_data": "\u65e0\u6570\u636e",
    "city.no_data_day": "\u8be5\u65e5\u671f\u6682\u65f6\u65e0\u6570\u636e",
}


def get(key: str, default: str = "") -> str:
    return TEXTS.get(key, default if default else key)


def build_js() -> str:
    payload = json.dumps(TEXTS, ensure_ascii=True)
    return f"""\
const UI_TEXT = {payload};
function t(key, fallback) {{
    if (Object.prototype.hasOwnProperty.call(UI_TEXT, key)) return UI_TEXT[key];
    return fallback != null ? fallback : key;
}}
"""
