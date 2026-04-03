"""
纯工具函数：日期格式化、AQI 颜色/等级查询、列名筛选。

无副作用，无外部 IO，可在任意模块中直接 import 使用。
"""

from __future__ import annotations

import pandas as pd

from constants import AQI_LEVELS, NON_CITY_COLUMNS


def fmt_date(date_str: str) -> str:
    """将 'YYYYMMDD' 格式日期字符串转换为 'YYYY-MM-DD' 格式。

    若输入长度不为 8，则原样返回。

    Args:
        date_str: 待转换的日期字符串，如 '20240101'。

    Returns:
        格式化后的日期字符串，如 '2024-01-01'。
    """
    d = str(date_str)
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d


def get_aqi_color(aqi_value: float) -> str:
    """根据 AQI 数值返回对应的十六进制颜色码。

    Args:
        aqi_value: AQI 数值。若为 NaN，返回灰色 '#cccccc'。

    Returns:
        颜色十六进制字符串，如 '#00e400'。
    """
    if pd.isna(aqi_value):
        return '#cccccc'
    for info in AQI_LEVELS.values():
        lo, hi = info['range']
        if lo <= aqi_value <= hi:
            return info['color']
    return '#7e0023' if aqi_value > 500 else '#cccccc'


def get_aqi_level_label(aqi_value: float) -> str:
    """根据 AQI 数值返回等级标签（如 '优'、'良'、'重度污染'）。

    Args:
        aqi_value: AQI 数值。若为 NaN，返回 '无数据'。

    Returns:
        等级标签字符串。
    """
    if pd.isna(aqi_value):
        return '无数据'
    for info in AQI_LEVELS.values():
        lo, hi = info['range']
        if lo <= aqi_value <= hi:
            return info['label']
    return '严重污染' if aqi_value > 500 else '无数据'


def get_city_columns(df: pd.DataFrame) -> list[str]:
    """从 DataFrame 中提取城市列名（排除 date/hour/type 列）。

    Args:
        df: 原始数据 DataFrame。

    Returns:
        城市列名列表。
    """
    return [col for col in df.columns if col not in NON_CITY_COLUMNS]
