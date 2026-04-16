# 产品封装清单（单下载包）

## 0. 目标

- 用户只下载一个安装包（推荐 `Setup.exe`）。
- 安装后双击图标直接进入应用。
- 不暴露 Python/venv/pip/bat。

## 1. 目录规划（安装后）

- `%ProgramFiles%\DDA3003PROJ\AQDeskShell.exe`
- `%ProgramFiles%\DDA3003PROJ\runtime\`（Python + 后端代码）
- `%ProgramFiles%\DDA3003PROJ\data_bundle\`（内置数据）
- `%LOCALAPPDATA%\DDA3003PROJ\logs\`
- `%APPDATA%\DDA3003PROJ\config.json`

## 2. 数据策略（重点：C 盘 + D 盘 + 内置）

主地图 CSV（`combined_air_quality_data.csv`）读取优先级：
1. `MAIN_DATA_CSV` 环境变量
2. `APP_DATA_BUNDLE_DIR/combined_air_quality_data.csv`（安装包内置）
3. `--data` 参数
4. `repo/data/combined_air_quality_data.csv`
5. `C:\Users\xzh88\Desktop\cleaned\combined_air_quality_data.csv`
6. `D:\xwechat_files\...\data\combined_air_quality_data.csv`

热力图小时 CSV 目录读取优先级：
1. `HEATMAP_DATA_ROOT` 环境变量
2. `APP_DATA_BUNDLE_DIR/data` 或 `APP_DATA_BUNDLE_DIR`
3. `D:\xwechat_files\...\data\data` 或 `D:\xwechat_files\...\data`
4. 主 CSV 同目录推断 `.../data`
5. `repo/data/`

说明：
- 如果 C、D 都存在，优先走环境变量/内置包，避免机器依赖。
- 外部数据只作为兜底，不作为正式发布默认路径。

## 3. 启动流程

1. 壳程序启动（WPF + WebView2）
2. 调用 `bootstrap_env.ps1`（隐藏）准备运行时
3. 启动 `main.py --ai-autostart`（隐藏）
4. 读取 stdout/stderr 映射到 UI 进度条与状态
5. 加载 `interactive_air_quality_map.html` 到内嵌 WebView

## 4. 必做验证

- [ ] 新电脑（无 Python）可启动
- [ ] C 盘无数据，仅内置数据可运行
- [ ] D 盘有小时数据时热力图可读
- [ ] AI 服务正常启动/失败均有 UI 提示
- [ ] 无命令行窗口弹出

## 5. 打包发布（建议）

- `dotnet publish` 产出桌面壳
- 打包器（Inno Setup/WiX）将 `runtime + data_bundle + 壳程序` 一并封装
- 产物：一个 `Setup.exe`

