# DDA3003PROJ

中国城市空气质量可视化项目（课程项目版）。  
项目基于 Python + Pyecharts 生成交互式 HTML 页面，支持全国地图浏览、城市详情、时间轴回放、对比模式与聚落分析。

## 1. 项目功能

- 全国城市 AQI 地图展示（可缩放、可平移）
- 时间轴联动（按日期浏览数据）
- 城市详情面板（AQI 与污染物指标）
- 近 7 日折线趋势
- 多城市对比模式
- 聚落分析（半径圈）与聚落内城市折线对比
- 加载启动层（慢网提示、就绪后手动进入）

## 2. 环境要求

- Python 3.10+（建议 3.11/3.12）
- Windows / macOS / Linux

## 3. 安装依赖

在项目根目录执行：

```bash
pip install pandas pyecharts
```

如你使用虚拟环境，建议先创建并激活 venv。

## 4. 运行方式

### 4.1 直接运行（使用默认路径）

```bash
python main.py
```

### 4.2 指定数据与输出目录

```bash
python main.py --data <your_csv_path> --out <output_dir>
```

示例：

```bash
python main.py --data C:\\data\\combined_air_quality_data.csv --out C:\\data\\visualizations
```

运行后会在输出目录生成交互页面（如 `interactive_air_quality_map.html`）。

## 5. 数据格式说明（最小要求）

CSV 至少应包含：

- `date`（日期）
- `hour`（小时）
- `type`（指标类型，含 `AQI`）
- 城市列（如 `北京`、`上海` 等）

项目会按 `type == AQI` 构建主地图，并从污染物数据构建详情和趋势。

## 6. 目录结构（核心文件）

- `main.py`：命令行入口
- `visualizer.py`：页面装配与输出
- `map_base.py`：地图壳层、控件、时间轴、加载层
- `map_renderer.py`：地图渲染逻辑
- `city_panel.py`：城市详情与主折线图
- `compare_mode.py`：多城市对比逻辑
- `settlement_mode.py`：聚落分析逻辑
- `data_loader.py`：数据加载与预处理
- `constants.py`：坐标与常量

## 7. 常见问题

### Q1: 页面打开慢或先空白

属于正常现象（地图资源与数据初始化）。项目已内置加载层和慢网提示。

### Q2: 中文显示异常或乱码

请确认：

- 源码文件使用 UTF-8 编码保存
- 浏览器页面编码为 UTF-8
- 数据文件本身未损坏

### Q3: 运行报依赖缺失

重新安装：

```bash
pip install -U pandas pyecharts
```

## 8. 开发分支说明

- `main`：稳定主分支
- `codex/test-improvements`：测试改进分支

如需合并测试分支改动，请发起 PR：  
`codex/test-improvements -> main`
