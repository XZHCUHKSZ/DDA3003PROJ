"""
数据加载与城市匹配层。

- AirQualityDataLoader: 读取 CSV，构建按日期/污染物组织的数据字典。
- CityMatcher:          城市名称标准化，与坐标库匹配。
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from constants import (
    CITY_COORDINATES,
    CITY_NAME_MAPPING,
    POLLUTANT_TYPES,
)
from utils import get_aqi_color, get_aqi_level_label, get_city_columns


class AirQualityDataLoader:
    """负责加载与预处理空气质量 CSV 数据。

    Attributes:
        data_file: CSV 文件路径。
        data:      加载后的完整 DataFrame，初始为 None。
    """

    def __init__(self, data_file: str) -> None:
        self.data_file = data_file
        self.data: pd.DataFrame | None = None

    def load(self) -> 'AirQualityDataLoader':
        """读取 CSV 文件并存入 self.data。

        Returns:
            self，支持链式调用。

        Raises:
            FileNotFoundError: 若 data_file 不存在。
        """
        print(f"📂 加载数据: {self.data_file}")
        self.data = pd.read_csv(self.data_file, encoding='utf-8')
        print(f"✓ 数据加载完成: {self.data.shape[0]} 行 × {self.data.shape[1]} 列")
        return self

    def build_aqi_by_date(self, hour: int = 0) -> dict[str, dict[str, float]]:
        """按日期聚合 AQI 数据，用于前端地图渲染。

        Args:
            hour: 取哪个小时的数据，默认 0。

        Returns:
            {date_str: {city: aqi_value}} 的嵌套字典。
        """
        assert self.data is not None, "请先调用 load() 方法"
        city_cols = get_city_columns(self.data)
        aqi_df = self.data[
            (self.data['type'] == 'AQI') & (self.data['hour'] == hour)
        ].copy()
        aqi_df['date'] = aqi_df['date'].astype(str)

        result: dict[str, dict[str, float]] = {}
        for date_val, grp in aqi_df.groupby('date'):
            row = grp.iloc[0]
            result[date_val] = {
                city: float(row[city])
                for city in city_cols
                if pd.notna(row[city])
            }
        return result

    def build_pollutants_by_date(
        self, hour: int = 0
    ) -> dict[str, dict[str, dict[str, float]]]:
        """按日期、城市、污染物类型聚合浓度数据。

        Args:
            hour: 取哪个小时的数据，默认 0。

        Returns:
            {date_str: {city: {pollutant_type: value}}} 的三层嵌套字典。
        """
        assert self.data is not None, "请先调用 load() 方法"
        city_cols = get_city_columns(self.data)
        poll_df = self.data[
            (self.data['type'].isin(POLLUTANT_TYPES)) & (self.data['hour'] == hour)
        ].copy()
        poll_df['date'] = poll_df['date'].astype(str)

        result: dict[str, dict[str, dict[str, float]]] = {}
        for (date_val, ptype), grp in poll_df.groupby(['date', 'type']):
            result.setdefault(date_val, {})
            row = grp.iloc[0]
            for city in city_cols:
                if pd.notna(row[city]):
                    result[date_val].setdefault(city, {})[ptype] = float(row[city])
        return result

    def get_sorted_dates(self, hour: int = 0) -> list[str]:
        """获取 AQI 数据中所有日期的有序列表（字符串格式）。

        Args:
            hour: 过滤条件，默认 0。

        Returns:
            升序排列的日期字符串列表，如 ['20240101', '20240102', ...]。
        """
        assert self.data is not None, "请先调用 load() 方法"
        aqi_df = self.data[self.data['type'] == 'AQI']
        return sorted(str(d) for d in aqi_df['date'].unique())


class CityMatcher:
    """将 CSV 中的城市名与坐标库匹配，生成带坐标的城市数据列表。

    Attributes:
        coordinates:  城市坐标字典，键为标准城市名。
        name_mapping: 城市简称到标准全称的映射表。
    """

    def __init__(
        self,
        coordinates: dict[str, list[float]] = CITY_COORDINATES,
        name_mapping: dict[str, str] = CITY_NAME_MAPPING,
    ) -> None:
        self.coordinates = coordinates
        self.name_mapping = name_mapping

    def standardize(self, city: str) -> str:
        """将城市简称映射到标准全称，无映射则原样返回。"""
        return self.name_mapping.get(city, city)

    def match(
        self,
        city_row: dict[str, float],
        date: Any,
        hour: int,
    ) -> tuple[list[dict], list[str]]:
        """将一行 AQI 数据与坐标库匹配，返回匹配结果与未匹配城市列表。

        Args:
            city_row: {城市名: aqi值} 的字典（已过滤 NaN）。
            date:     该行对应的日期，仅用于日志输出。
            hour:     该行对应的小时，仅用于日志输出。

        Returns:
            (matched_list, unmatched_list)
        """
        matched: list[dict] = []
        unmatched: list[str] = []

        for city, aqi_value in city_row.items():
            standard = self.standardize(city)
            if standard in self.coordinates:
                lng, lat = self.coordinates[standard]
                matched.append({
                    'name':          standard,
                    'original_name': city,
                    'value':         float(aqi_value),
                    'lng':           lng,
                    'lat':           lat,
                    'level':         get_aqi_level_label(aqi_value),
                    'color':         get_aqi_color(aqi_value),
                })
            else:
                unmatched.append(f"{city} ({standard})")

        return matched, unmatched

    def log_match_result(self, matched: list[dict], unmatched: list[str]) -> None:
        """将匹配结果打印到控制台。"""
        print(f"✓ 成功匹配 {len(matched)} 个城市")
        if unmatched:
            print(f"⚠️  未匹配坐标的城市 ({len(unmatched)}个)")
            for c in unmatched[:10]:
                print(f"   - {c}")
            if len(unmatched) > 10:
                print(f"   ... 及其他 {len(unmatched) - 10} 个")
