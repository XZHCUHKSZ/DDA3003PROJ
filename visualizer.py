"""
Main HTML assembler for the interactive air quality map.
"""

from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, ThemeType

import city_panel
import compare_mode
import map_base
import map_renderer
import region_mapping
import settlement_mode
import ui_texts
from constants import CITY_COORDINATES
from data_loader import AirQualityDataLoader, CityMatcher
from utils import get_city_columns


class InteractiveAirQualityMap:
    def __init__(self, data_file: str) -> None:
        self.loader = AirQualityDataLoader(data_file)
        self.matcher = CityMatcher()

    def load_data(self) -> "InteractiveAirQualityMap":
        self.loader.load()
        return self

    def prepare_city_data(
        self,
        date: Any = None,
        hour: int = 0,
    ) -> tuple[list[dict], Any, int] | None:
        print("\n📊 准备城市数据...")
        data = self.loader.data
        aqi_data = data[data["type"] == "AQI"].copy()

        if date is None:
            date = aqi_data["date"].max()

        filtered = aqi_data[(aqi_data["date"] == date) & (aqi_data["hour"] == hour)]
        if filtered.empty:
            print(f"❌ 未找到日期 {date} 小时 {hour} 的数据")
            return None

        print(f"✓ 选择日期: {date}, 小时: {hour}h")
        city_cols = get_city_columns(data)
        row = filtered.iloc[0]
        city_row = {city: row[city] for city in city_cols if pd.notna(row[city])}

        matched, unmatched = self.matcher.match(city_row, date, hour)
        self.matcher.log_match_result(matched, unmatched)
        return matched, date, hour

    def run(self, output_dir: str = "visualizations") -> None:
        print("\n" + "🗺️  " * 35)
        print("交互式空气质量地图可视化程序（滚动布局版）")
        print("🗺️  " * 35)

        os.makedirs(output_dir, exist_ok=True)

        result = self.prepare_city_data()
        if result is None:
            print("\n❌ 数据准备失败")
            return

        city_data, date, hour = result
        map_file = os.path.join(output_dir, "interactive_air_quality_map.html")

        self.create_interactive_map(city_data, date, hour, map_file)

        print("\n" + "=" * 70)
        print("✅ 可视化生成完成！")
        print("=" * 70)
        print(f"\n📂 主地图: {map_file}")

    def create_interactive_map(
        self,
        city_data: list[dict],
        date: Any,
        hour: int,
        output_file: str = "interactive_map.html",
    ) -> Geo:
        print("\n🗺️  创建交互式地图（滚动布局版）...")

        all_dates = self.loader.get_sorted_dates(hour)
        date_str = str(date)
        current_index = all_dates.index(date_str) if date_str in all_dates else len(all_dates) - 1
        print(f"✓ 日期范围: {all_dates[0]} 至 {all_dates[-1]}, 共 {len(all_dates)} 天")

        city_data_by_date = self.loader.build_aqi_by_date(hour)
        all_pollutants_data = self.loader.build_pollutants_by_date(hour)
        print(f"✓ 已准备 {len(city_data_by_date)} 天的数据")

        geo = self._build_geo_chart(city_data, date, hour)
        geo.render(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        injected = self._assemble_injection(
            all_dates=all_dates,
            current_index=current_index,
            city_data_by_date=city_data_by_date,
            all_pollutants_data=all_pollutants_data,
        )
        html_content = html_content.replace("</body>", injected + "</body>")

        head_fix = (
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "    <script>document.documentElement.classList.add('preboot-hide');</script>\n"
            "    <style>\n"
            "        html { overflow-y: auto !important; }\n"
            "        body { overflow-y: auto !important; height: auto !important; }\n"
            "        .preboot-hide div[_echarts_instance_],\n"
            "        .preboot-hide .chart-container { visibility: hidden !important; }\n"
            "    </style>"
        )
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", "<head>\n    " + head_fix)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✓ 交互式地图已保存: {output_file}")
        print("\n💡 使用方式:")
        print("  - 上半部分：地图 + 标题下方时间轴")
        print("  - 点击城市 → 自动滚动到下方，显示详情+折线图")
        print("  - 热力模式：在同一张地图上切换城市热力/省域填色")
        print("  - 对比模式：点击多个城市加入折线对比")
        print("  - 底部日期导航条与顶部时间轴联动")
        return geo

    def _assemble_injection(
        self,
        all_dates: list[str],
        current_index: int,
        city_data_by_date: dict,
        all_pollutants_data: dict,
    ) -> str:
        coords_json = json.dumps({city: value for city, value in CITY_COORDINATES.items()})
        dates_json = json.dumps(all_dates)
        city_data_json = json.dumps(city_data_by_date)
        pollutants_json = json.dumps(all_pollutants_data)

        css_block = (
            map_base.build_css()
            + city_panel.build_css()
            + compare_mode.build_css()
            + settlement_mode.build_css()
        )

        dom_block = (
            map_base.build_dom(all_dates, current_index)
            + city_panel.build_dom(all_dates, current_index)
            + settlement_mode.build_dom()
        )

        js_globals = f"""\
const ALL_DATES = {dates_json};
const CURRENT_DATE_IDX = {current_index};
const CITY_DATA_BY_DATE = {city_data_json};
const POLLUTANTS_DATA = {pollutants_json};
const CITY_COORDS = {coords_json};
const AQI_COLORS = [
    {{ max: 50, color: '#00e400' }},
    {{ max: 100, color: '#ffff00' }},
    {{ max: 150, color: '#ff7e00' }},
    {{ max: 200, color: '#ff0000' }},
    {{ max: 300, color: '#99004c' }},
    {{ max: 9999, color: '#7e0023' }}
];
const COMPARE_PALETTE = [
    '#3b82f6', '#ef4444', '#10b981', '#f59e0b',
    '#8b5cf6', '#ec4899', '#06b6d4', '#f97316',
    '#84cc16', '#6366f1'
];

let currentDateIndex = CURRENT_DATE_IDX;
let currentCityName = '';
let selectedMetric = 'AQI';
let metricsChart = null;
let mapChartInstance = null;
let debounceTimer = null;
let compareMode = false;
let compareList = [];
let mapMode = 'normal';
let currentZoom = 1.2;
let currentCenter = [105, 36];
let settlementRadiusKm = 120;
let settlementMapChart = null;
"""

        js_block = (
            js_globals
            + ui_texts.build_js()
            + region_mapping.build_js()
            + map_renderer.build_js()
            + map_base.build_js()
            + compare_mode.build_js()
            + city_panel.build_js()
            + settlement_mode.build_js()
        )

        return f"""
<style>
{css_block}
</style>

{dom_block}

<script>
{js_block}
</script>
"""

    def _build_geo_chart(
        self,
        city_data: list[dict],
        date: Any,
        hour: int,
    ) -> Geo:
        geo = Geo(
            init_opts=opts.InitOpts(
                width="100%",
                height="100vh",
                theme=ThemeType.LIGHT,
                bg_color="#f0f4f8",
            )
        )

        for city, coords in CITY_COORDINATES.items():
            geo.add_coordinate(city, coords[0], coords[1])

        data_pairs = [(item["name"], item["value"]) for item in city_data]
        geo.add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="#dde8f0",
                border_color="#aac4d8",
                border_width=0.8,
            ),
            emphasis_itemstyle_opts=opts.ItemStyleOpts(color="#bdd6e6"),
            label_opts=opts.LabelOpts(is_show=False),
            zoom=1.2,
            center=[105, 36],
        )
        geo.add(
            series_name="AQI指数",
            data_pair=data_pairs,
            type_=ChartType.SCATTER,
            symbol_size=10,
            label_opts=opts.LabelOpts(is_show=False),
        )
        geo.set_global_opts(
            title_opts=opts.TitleOpts(
                title="全国城市空气质量实时发布平台",
                subtitle=f"日期: {date}  时间: {hour:02d}:00  |  点击城市标记查看详情",
                pos_left="center",
                pos_top="12px",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=24,
                    font_weight="bold",
                    color="#1565c0",
                ),
                subtitle_textstyle_opts=opts.TextStyleOpts(font_size=13, color="#555"),
            ),
            visualmap_opts=opts.VisualMapOpts(
                min_=0,
                max_=300,
                is_piecewise=True,
                pieces=[
                    {"min": 0, "max": 50, "label": "优 (0-50)", "color": "#00e400"},
                    {"min": 51, "max": 100, "label": "良 (51-100)", "color": "#ffff00"},
                    {"min": 101, "max": 150, "label": "轻度污染 (101-150)", "color": "#ff7e00"},
                    {"min": 151, "max": 200, "label": "中度污染 (151-200)", "color": "#ff0000"},
                    {"min": 201, "max": 300, "label": "重度污染 (201-300)", "color": "#99004c"},
                    {"min": 301, "label": "严重污染 (>300)", "color": "#7e0023"},
                ],
                pos_right="1%",
                pos_top="18%",
                orient="vertical",
                item_width=26,
                item_height=18,
                textstyle_opts=opts.TextStyleOpts(font_size=11),
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="item",
                formatter=(
                    "<div style='padding:10px;background:#fff;border-radius:8px;"
                    "box-shadow:0 4px 12px rgba(0,0,0,0.15);'>"
                    "<div style='font-size:16px;font-weight:bold;color:#1565c0;margin-bottom:8px;'>{b}</div>"
                    "<div style='font-size:14px;color:#333;'>AQI: "
                    "<b style='color:#c62828;font-size:18px;'>{c}</b></div>"
                    "<div style='font-size:11px;color:#999;margin-top:6px;'>点击查看详细数据</div>"
                    "</div>"
                ),
                background_color="rgba(255,255,255,0.95)",
                border_color="#1565c0",
                border_width=1,
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="1%",
                pos_top="30%",
                feature={
                    "restore": {"title": "还原"},
                    "saveAsImage": {"title": "保存图片"},
                },
            ),
        )
        geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        return geo
