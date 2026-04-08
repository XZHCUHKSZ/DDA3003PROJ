"""
City detail panel module.
"""

from __future__ import annotations

import ui_texts
from utils import fmt_date


def build_css() -> str:
    return """\
#infoSection {
    background: linear-gradient(160deg, #f7f9fc 0%, #eef2f8 50%, #e8eef6 100%);
    min-height: 520px;
    padding: 0;
    border-top: 2px solid #d0dff0;
}

#infoHeader {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px 14px;
    border-bottom: 1px solid rgba(21,101,192,0.1);
    flex-wrap: wrap;
    gap: 10px;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(8px);
}
#infoHeaderLeft {
    display: flex;
    align-items: center;
    gap: 14px;
}
#selectedCityBadge {
    font-size: 22px;
    font-weight: 800;
    color: #1a2a4a;
    letter-spacing: 1px;
}
#aqiBadge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 15px;
    font-weight: 700;
    color: #111;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
#levelBadge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    background: rgba(21,101,192,0.1);
    color: #1565c0;
    border: 1px solid rgba(21,101,192,0.2);
}
#infoPlaceholder {
    width: 100%;
    padding: 60px 0;
    text-align: center;
    color: rgba(21,101,192,0.35);
    font-size: 16px;
    letter-spacing: 1px;
}

#filterBar {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    padding: 12px 32px;
    background: rgba(255,255,255,0.6);
    border-bottom: 1px solid rgba(21,101,192,0.08);
}
#filterBar .filter-label {
    font-size: 12px;
    color: #6b8cba;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-right: 4px;
}
.filter-btn {
    padding: 5px 14px;
    border-radius: 20px;
    border: 1.5px solid #c5d8f5;
    background: white;
    color: #3a5f8a;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.filter-btn:hover {
    background: #e8f0fb;
    border-color: #6ea8e0;
    color: #1565c0;
}
.filter-btn.active {
    background: #1565c0;
    border-color: #1565c0;
    color: white;
    box-shadow: 0 2px 8px rgba(21,101,192,0.3);
}

#infoBody {
    display: flex;
    gap: 0;
    padding: 0 24px 28px;
    min-height: 420px;
}

#cityDetailPanel {
    flex: 0 0 320px;
    padding: 20px 20px 20px 8px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}
.detail-card {
    background: white;
    border: 1px solid #dde8f5;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 2px 12px rgba(21,101,192,0.06);
}
.detail-card h3 {
    margin: 0 0 12px 0;
    font-size: 13px;
    color: #7a9cc0;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #eef3fa;
    padding-bottom: 8px;
    font-weight: 700;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 9px;
    padding: 4px 0;
    border-radius: 6px;
    transition: background 0.15s;
}
.detail-row:last-child {
    margin-bottom: 0;
}
.detail-row:hover {
    background: #f5f8fd;
}
.detail-row.highlight-row {
    background: #edf4ff;
    border-left: 3px solid #1565c0;
    padding-left: 8px;
}
.detail-label {
    font-size: 13px;
    color: #6b8cba;
}
.detail-value {
    font-size: 14px;
    font-weight: 700;
    color: #1a2a4a;
}
.pollutant-bar-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.pollutant-item {
    border: 1px solid #e7eef8;
    background: #fbfdff;
    border-radius: 10px;
    padding: 7px 9px;
}
.pollutant-item.active {
    border-color: #1565c0;
    box-shadow: 0 0 0 1px rgba(21,101,192,0.16) inset;
}
.pollutant-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 12px;
}
.pollutant-name {
    color: #587ba2;
    font-weight: 700;
}
.pollutant-value {
    color: #1a2a4a;
    font-weight: 800;
}
.pollutant-track {
    height: 8px;
    border-radius: 999px;
    background: #e8f0fb;
    overflow: hidden;
}
.pollutant-fill {
    height: 100%;
    border-radius: inherit;
    transition: width 0.22s ease;
}
.pollutant-meta {
    margin-bottom: 10px;
}
#pollutantSortHint {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 800;
    color: #2f5f93;
    margin-bottom: 8px;
}
.pollutant-sort-arrow {
    font-size: 18px;
    line-height: 1;
    color: #1565c0;
}
#healthAdvice {
    font-size: 13px;
    color: #4a6a8a;
    line-height: 1.7;
    margin: 0;
}

#chartPanel {
    flex: 1;
    padding: 20px 8px 20px 16px;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #dde8f5;
    min-width: 0;
}
#chartPanelTitle {
    font-size: 14px;
    color: #6b8cba;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    border-bottom: 1px solid #eef3fa;
    padding-bottom: 8px;
    flex-shrink: 0;
    font-weight: 700;
}
#analysisTwinGrid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
    align-items: stretch;
    min-height: 0;
    flex: 1;
}
#metricsCard {
    background: #ffffff;
    border: 1px solid #dde8f5;
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(21,101,192,0.06);
    box-sizing: border-box;
    padding: 12px 14px 14px;
    display: flex;
    flex-direction: column;
    min-height: 100%;
}
#metricsCard #chartPanelTitle {
    margin-bottom: 8px;
}
#analysisTwinGrid #metricsChart {
    min-height: 360px;
    flex: 1;
}
#settlementPanelHost {
    display: none;
    min-width: 0;
}
#analysisTwinGrid.settlement-visible {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}
#analysisTwinGrid.settlement-visible #settlementPanelHost {
    display: block;
}
#analysisTwinGrid.settlement-visible #metricsCard {
    min-height: 100%;
}
#analysisTwinGrid.settlement-visible #settlementPanel {
    margin-top: 0;
}
@media (max-width: 1199px) {
    #analysisTwinGrid,
    #analysisTwinGrid.settlement-visible {
        grid-template-columns: minmax(0, 1fr);
    }
    #metricsCard {
        min-height: auto;
    }
    #analysisTwinGrid.settlement-visible #settlementPanel {
        margin-top: 12px;
    }
}

#dateNavBar {
    position: sticky;
    top: 0;
    z-index: 40;
    background: white;
    border-top: 1px solid #eef3fa;
    border-bottom: 1px solid #dde8f5;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    box-shadow: 0 2px 12px rgba(21,101,192,0.08);
}
#analysisModeBar {
    display: none;
    align-items: center;
    gap: 8px;
    padding: 10px 28px 0;
}
.analysis-mode-btn {
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid #c5d8f5;
    background: #f4f8ff;
    color: #3a5f8a;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
}
.analysis-mode-btn.active {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
}
#dateNavBar button {
    padding: 6px 13px;
    background: #eef3fa;
    color: #1565c0;
    border: 1px solid #c5d8f5;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 700;
    font-size: 15px;
    transition: all 0.2s;
    flex-shrink: 0;
}
#dateNavBar button:hover {
    background: #1565c0;
    color: white;
    border-color: #1565c0;
}
.nav-date-label {
    font-size: 11px;
    color: #aac4d8;
    white-space: nowrap;
    flex-shrink: 0;
}
#bottomSlider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 6px;
    border-radius: 3px;
    background: #c5d8f5;
    outline: none;
    cursor: pointer;
    min-width: 80px;
}
#bottomSlider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #1565c0;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(21,101,192,0.35);
    transition: transform 0.2s;
}
#bottomSlider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}
#bottomCurrentDate {
    min-width: 108px;
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    color: #1565c0;
    background: #eef3fa;
    border: 1px solid #c5d8f5;
    border-radius: 8px;
    padding: 5px 12px;
    flex-shrink: 0;
}

#aiInsightSection {
    margin: 0 24px 30px;
    background: #ffffff;
    border: 1px solid #dde8f5;
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(21,101,192,0.06);
    padding: 14px 16px;
}
#aiInsightHeader {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
#aiInsightTitle {
    font-size: 15px;
    color: #1a2a4a;
    font-weight: 800;
}
#aiInsightSub {
    margin-top: 4px;
    font-size: 12px;
    color: #7a9cc0;
}
#aiGenerateBtn {
    border: 1px solid #8db6e4;
    background: #1565c0;
    color: #fff;
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}
#aiGenerateBtn[disabled] {
    opacity: 0.65;
    cursor: not-allowed;
}
#aiConfigBtn {
    border: 1px solid #b8cfea;
    background: #f3f8ff;
    color: #2f5f93;
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}
#aiConfigBtn:hover {
    background: #e7f0fc;
}
#aiStatus {
    margin-top: 10px;
    font-size: 12px;
    color: #6b8cba;
    white-space: pre-line;
}
.ai-config-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(10,30,60,0.3);
    z-index: 4200;
    display: none;
}
.ai-config-backdrop.show {
    display: block;
}
#aiConfigDrawer {
    position: fixed;
    right: 0;
    top: 0;
    height: 100%;
    width: min(420px, 92vw);
    background: #ffffff;
    border-left: 1px solid #d8e7f8;
    box-shadow: -8px 0 24px rgba(20,71,132,0.16);
    z-index: 4300;
    transform: translateX(104%);
    transition: transform 0.24s ease;
    padding: 14px 14px 16px;
}
#aiConfigDrawer.show {
    transform: translateX(0);
}
.ai-config-title {
    font-size: 16px;
    font-weight: 800;
    color: #1a2a4a;
    margin-bottom: 10px;
}
.ai-config-group {
    margin-bottom: 10px;
}
.ai-config-label {
    font-size: 12px;
    color: #5d7fa7;
    margin-bottom: 4px;
    display: block;
    font-weight: 700;
}
.ai-config-input, .ai-config-select {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #c7daf1;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
    color: #24476f;
    background: #fbfdff;
}
.ai-config-row {
    display: flex;
    gap: 8px;
}
.ai-config-btn {
    border: 1px solid #8db6e4;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}
.ai-config-btn.primary {
    background: #1565c0;
    color: #fff;
    border-color: #1565c0;
}
.ai-config-btn.ghost {
    background: #f3f8ff;
    color: #2f5f93;
}
#aiConfigStatus {
    margin-top: 8px;
    font-size: 12px;
    color: #5d7fa7;
    white-space: pre-line;
}
#aiProgressWrap {
    margin-top: 8px;
    width: 100%;
    height: 7px;
    background: #e8f0fb;
    border-radius: 999px;
    overflow: hidden;
    display: none;
}
#aiProgressBar {
    width: 0%;
    height: 100%;
    background: linear-gradient(90deg, #4c8ed6 0%, #1565c0 100%);
    transition: width 0.25s ease;
}
#aiBlocks {
    margin-top: 12px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 12px;
}
.ai-block {
    background: linear-gradient(180deg, #fbfdff 0%, #f4f8ff 100%);
    border: 1px solid #dce9f8;
    border-radius: 12px;
    padding: 12px 13px;
    box-shadow: 0 4px 14px rgba(21,101,192,0.08);
}
.ai-block h4 {
    margin: 0 0 8px 0;
    color: #3e6a98;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.5px;
}
.ai-block p {
    margin: 0;
    color: #1f3f62;
    font-size: 14px;
    line-height: 1.75;
    white-space: pre-wrap;
}
.ai-cause-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
}
.ai-cause-item {
    display: grid;
    grid-template-columns: 22px 1fr;
    gap: 8px;
    align-items: start;
    border: 1px solid #d8e6f8;
    border-radius: 9px;
    background: #fafdff;
    padding: 8px 10px;
}
.ai-cause-no {
    width: 22px;
    height: 22px;
    border-radius: 7px;
    background: #e5f0ff;
    color: #1b5fb7;
    font-size: 12px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
}
.ai-cause-text {
    color: #24476f;
    font-size: 13px;
    line-height: 1.72;
}
#aiSources {
    margin-top: 10px;
    border-top: 1px dashed #dbe8f6;
    padding-top: 10px;
}
#aiSources ul {
    margin: 0;
    padding-left: 18px;
}
#aiSources li {
    color: #4a6a8a;
    font-size: 12px;
    margin-bottom: 8px;
}
.ai-source-time {
    color: #7a9cc0;
    margin-left: 4px;
}
.ai-source-snippet {
    margin-top: 2px;
    color: #597a9d;
    line-height: 1.55;
}
#aiSources a {
    color: #1565c0;
    text-decoration: none;
}
#aiSources a:hover {
    text-decoration: underline;
}
#monthHeatmapSection {
    display: none;
    margin: 10px 24px 28px;
    background: #ffffff;
    border: 1px solid #dde8f5;
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(21,101,192,0.06);
    padding: 14px 16px 16px;
}
#monthHeatmapToolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 10px;
}
#monthHeatmapTitle {
    font-size: 15px;
    color: #1a2a4a;
    font-weight: 800;
}
#monthHeatmapCtrl {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
#monthHeatmapCtrl label {
    font-size: 12px;
    color: #6b8cba;
    font-weight: 700;
}
#monthPicker {
    border: 1px solid #c5d8f5;
    background: #f8fbff;
    color: #2f5f93;
    border-radius: 8px;
    padding: 5px 8px;
    font-size: 12px;
    font-weight: 700;
}
#monthHeatmapChart {
    width: 100%;
    height: 700px;
    border: 1px solid #eef3fa;
    border-radius: 10px;
    background: #fbfdff;
}
#monthHeatmapHint {
    margin-top: 8px;
    font-size: 12px;
    color: #6b8cba;
}
"""


def build_dom(all_dates: list[str], current_index: int) -> str:
    first_label = fmt_date(all_dates[0])
    last_label = fmt_date(all_dates[-1])
    cur_label = fmt_date(all_dates[current_index])
    placeholder = ui_texts.get("city.placeholder")
    filter_label = ui_texts.get("city.filter")
    pollutants_title = ui_texts.get("city.pollutants")
    health_title = ui_texts.get("city.health")
    trend_title = ui_texts.get("city.trend7d")
    compare_hint = ui_texts.get("city.compare_hint")

    return f"""\
<div id="infoSection">
    <div id="infoHeader">
        <div id="infoPlaceholder">{placeholder}</div>
        <div id="infoHeaderContent" style="display:none; width:100%;">
            <div id="infoHeaderLeft">
                <span id="selectedCityBadge">--</span>
                <span id="aqiBadge">AQI --</span>
                <span id="levelBadge">--</span>
            </div>
        </div>
    </div>

    <div id="filterBar" style="display:none;">
        <span class="filter-label">{filter_label}</span>
        <button class="filter-btn active" data-metric="AQI">AQI</button>
        <button class="filter-btn" data-metric="PM2.5_24h">PM2.5</button>
        <button class="filter-btn" data-metric="PM10_24h">PM10</button>
        <button class="filter-btn" data-metric="SO2_24h">SO2</button>
        <button class="filter-btn" data-metric="NO2_24h">NO2</button>
        <button class="filter-btn" data-metric="O3_8h">O3</button>
    </div>

    <div id="dateNavBar">
        <button id="btn-prev-7">&laquo;</button>
        <button id="btn-prev-1">&lsaquo;</button>
        <span class="nav-date-label">{first_label}</span>
        <input type="range" id="bottomSlider" min="0" max="{len(all_dates)-1}" value="{current_index}" step="1">
        <span class="nav-date-label">{last_label}</span>
        <button id="btn-next-1">&rsaquo;</button>
        <button id="btn-next-7">&raquo;</button>
        <span id="bottomCurrentDate">{cur_label}</span>
    </div>

    <div id="analysisModeBar">
        <button id="modeCityBtn" class="analysis-mode-btn active" data-mode="city">城市分析模式</button>
        <button id="modeHeatmapBtn" class="analysis-mode-btn" data-mode="heatmap">月历热力模式</button>
    </div>

    <div id="infoBody" style="display:none;">
        <div id="compareListPanel">
            <div id="compareEmptyHint">{compare_hint}</div>
        </div>

        <div id="cityDetailPanel">
            <div class="detail-card">
                <h3>{pollutants_title} (ug/m3)</h3>
                <div class="pollutant-meta">
                    <div id="pollutantSortHint"><span class="pollutant-sort-arrow">↓</span>严重程度降序</div>
                </div>
                <div class="pollutant-bar-list" id="pollutantBarList"></div>
            </div>

            <div class="detail-card">
                <h3>{health_title}</h3>
                <p id="healthAdvice">--</p>
            </div>
        </div>

        <div id="chartPanel">
            <div id="analysisTwinGrid">
                <div id="metricsCard">
                    <div id="chartPanelTitle">{trend_title}</div>
                    <div id="metricsChart"></div>
                </div>
                <div id="settlementPanelHost"></div>
            </div>
        </div>
    </div>

    <div id="aiInsightSection" style="display:none;">
        <div id="aiInsightHeader">
            <div>
                <div id="aiInsightTitle">{ui_texts.get("ai.title")}</div>
                <div id="aiInsightSub">{ui_texts.get("ai.subtitle")}</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                <button id="aiConfigBtn" type="button">AI服务设置</button>
                <button id="aiGenerateBtn" type="button">{ui_texts.get("ai.btn")}</button>
            </div>
        </div>
        <div id="aiStatus">{ui_texts.get("ai.empty")}</div>
        <div id="aiProgressWrap"><div id="aiProgressBar"></div></div>
        <div id="aiBlocks" style="display:none;">
            <div class="ai-block">
                <h4>{ui_texts.get("ai.section.settlement")}</h4>
                <p id="aiSettlementText">--</p>
            </div>
            <div class="ai-block">
                <h4>{ui_texts.get("ai.section.diffusion")}</h4>
                <p id="aiDiffusionText">--</p>
            </div>
            <div class="ai-block">
                <h4>{ui_texts.get("ai.section.causes")}</h4>
                <div id="aiCauseText">--</div>
            </div>
        </div>
    </div>

    <div id="monthHeatmapSection">
        <div id="monthHeatmapToolbar">
            <div id="monthHeatmapTitle">月历热力图</div>
            <div id="monthHeatmapCtrl">
                <label for="monthPicker">月份</label>
                <select id="monthPicker"></select>
            </div>
        </div>
        <div id="monthHeatmapChart"></div>
        <div id="monthHeatmapHint">显示当前城市在选定月份内按日强度分布；颜色标准随当前污染物切换。</div>
    </div>

    <div class="ai-config-backdrop" id="aiConfigBackdrop"></div>
    <div id="aiConfigDrawer">
        <div class="ai-config-title">AI服务设置</div>
        <div class="ai-config-group">
            <label class="ai-config-label">运行模式</label>
            <div id="aiModeState" style="font-size:12px;color:#2f5f93;">--</div>
        </div>
        <div class="ai-config-group">
            <label class="ai-config-label">服务地址</label>
            <input id="aiApiBaseInput" class="ai-config-input" placeholder="http://127.0.0.1:8787" />
        </div>
        <div class="ai-config-group">
            <label class="ai-config-label">Provider</label>
            <select id="aiProviderSelect" class="ai-config-select">
                <option value="bailian">bailian</option>
                <option value="openai">openai</option>
                <option value="custom">custom</option>
            </select>
        </div>
        <div class="ai-config-group">
            <label class="ai-config-label">模型名（可选）</label>
            <input id="aiModelInput" class="ai-config-input" placeholder="qwen-plus" />
        </div>
        <div class="ai-config-group">
            <label class="ai-config-label">API Key（可选）</label>
            <input id="aiApiKeyInput" type="password" class="ai-config-input" placeholder="不填写则使用服务端默认配置" />
            <label style="margin-top:6px;display:flex;gap:6px;align-items:center;font-size:12px;color:#6b8cba;">
                <input id="aiRememberKey" type="checkbox" />
                在本机记住 Key（有安全风险）
            </label>
        </div>
        <div class="ai-config-row">
            <button id="aiTestConnBtn" class="ai-config-btn ghost" type="button">测试连接</button>
            <button id="aiSaveConfigBtn" class="ai-config-btn primary" type="button">保存并应用</button>
            <button id="aiCloseConfigBtn" class="ai-config-btn ghost" type="button">关闭</button>
        </div>
        <div id="aiConfigStatus">--</div>
    </div>

</div>
"""


def build_js() -> str:
    return """\
function metricLabel(metric) {
    return {
        AQI: 'AQI',
        'PM2.5_24h': 'PM2.5 (ug/m3)',
        'PM10_24h': 'PM10 (ug/m3)',
        'SO2_24h': 'SO2 (ug/m3)',
        'NO2_24h': 'NO2 (ug/m3)',
        'O3_8h': 'O3 (ug/m3)',
        'O3_8h_24h': 'O3_8h_24h (ug/m3)'
    }[metric] || metric;
}

function pollutantDisplayName(metric) {
    return {
        'PM2.5_24h': 'PM2.5',
        'PM10_24h': 'PM10',
        'SO2_24h': 'SO2',
        'NO2_24h': 'NO2',
        'O3_8h': 'O3',
        'O3_8h_24h': 'O3_8h_24h'
    }[metric] || metric;
}

const POLLUTANT_COLOR_LEVELS = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#99004c', '#7e0023'];
const POLLUTANT_THRESHOLDS = {
    'PM2.5_24h': [35, 75, 115, 150, 250],
    'PM10_24h': [50, 150, 250, 350, 420],
    'SO2_24h': [50, 150, 475, 800, 1600],
    'NO2_24h': [40, 80, 180, 280, 565],
    'O3_8h': [100, 160, 215, 265, 800],
    'O3_8h_24h': [100, 160, 215, 265, 800]
};
let detailViewMode = 'city';
let monthHeatmapChart = null;
let selectedHeatmapMonth = '';
const HEATMAP_SERVICE_BASE = 'http://127.0.0.1:8791';

function pollutantLevel(metric, value) {
    if (value == null || Number.isNaN(Number(value))) return -1;
    const v = Number(value);
    const th = POLLUTANT_THRESHOLDS[metric];
    if (!th) return -1;
    if (v <= th[0]) return 0;
    if (v <= th[1]) return 1;
    if (v <= th[2]) return 2;
    if (v <= th[3]) return 3;
    if (v <= th[4]) return 4;
    return 5;
}

function pollutantLevelText(level) {
    return ['优', '良', '轻度污染', '中度污染', '重度污染', '严重污染'][level] || '无数据';
}

function getMetricLegendPieces(metric) {
    const colors = POLLUTANT_COLOR_LEVELS.slice();
    if (metric === 'AQI') {
        return [
            { label: '优', min: 0, max: 50, range: '0-50', color: colors[0] },
            { label: '良', min: 51, max: 100, range: '51-100', color: colors[1] },
            { label: '轻度污染', min: 101, max: 150, range: '101-150', color: colors[2] },
            { label: '中度污染', min: 151, max: 200, range: '151-200', color: colors[3] },
            { label: '重度污染', min: 201, max: 300, range: '201-300', color: colors[4] },
            { label: '严重污染', min: 301, max: 9999, range: '>300', color: colors[5] }
        ];
    }
    const th = POLLUTANT_THRESHOLDS[metric];
    if (!th || th.length < 5) return [];
    return [
        { label: '优', min: 0, max: th[0], range: `0-${th[0]}`, color: colors[0] },
        { label: '良', min: th[0] + 1, max: th[1], range: `${th[0] + 1}-${th[1]}`, color: colors[1] },
        { label: '轻度污染', min: th[1] + 1, max: th[2], range: `${th[1] + 1}-${th[2]}`, color: colors[2] },
        { label: '中度污染', min: th[2] + 1, max: th[3], range: `${th[2] + 1}-${th[3]}`, color: colors[3] },
        { label: '重度污染', min: th[3] + 1, max: th[4], range: `${th[3] + 1}-${th[4]}`, color: colors[4] },
        { label: '严重污染', min: th[4] + 1, max: 9999, range: `>${th[4]}`, color: colors[5] }
    ];
}

function fmtYm(dateStr) {
    const s = String(dateStr || '');
    if (s.length !== 8) return s;
    return s.slice(0, 4) + '-' + s.slice(4, 6);
}

function getAvailableMonths() {
    const set = new Set();
    (ALL_DATES || []).forEach(d => {
        const ym = fmtYm(d);
        if (ym) set.add(ym);
    });
    return Array.from(set).sort();
}

function ensureHeatmapMonthPicker() {
    const sel = document.getElementById('monthPicker');
    if (!sel) return;
    const months = getAvailableMonths();
    if (!selectedHeatmapMonth || !months.includes(selectedHeatmapMonth)) {
        selectedHeatmapMonth = months.length ? months[months.length - 1] : '';
    }
    sel.innerHTML = months.map(m => `<option value="${m}">${m}</option>`).join('');
    sel.value = selectedHeatmapMonth;
}

function metricToHourlyType(metric) {
    return {
        AQI: 'AQI',
        'PM2.5_24h': 'PM2.5',
        'PM10_24h': 'PM10',
        'SO2_24h': 'SO2',
        'NO2_24h': 'NO2',
        'O3_8h': 'O3',
        'O3_8h_24h': 'O3'
    }[metric] || metric;
}

function getDaysInMonth(monthYm) {
    const [y, m] = monthYm.split('-').map(x => Number(x));
    if (!y || !m) return [];
    const days = new Date(y, m, 0).getDate();
    return Array.from({ length: days }, (_, i) => i + 1);
}

function buildHourAxis() {
    return Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'));
}

async function fetchMonthlyHourlyHeatmap(cityName, monthYm, metric) {
    const hourlyMetric = metricToHourlyType(metric);
    const url = `${HEATMAP_SERVICE_BASE}/api/heatmap/monthly?city=${encodeURIComponent(cityName)}&metric=${encodeURIComponent(hourlyMetric)}&month=${encodeURIComponent(monthYm)}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    if (!data.ok) throw new Error(data.message || 'heatmap service error');
    return data;
}

async function renderMonthHeatmap() {
    const chartDom = document.getElementById('monthHeatmapChart');
    const titleEl = document.getElementById('monthHeatmapTitle');
    const hintEl = document.getElementById('monthHeatmapHint');
    if (!chartDom) return;
    if (!monthHeatmapChart) {
        monthHeatmapChart = echarts.init(chartDom, null, { renderer: 'canvas' });
    }
    if (!currentCityName) {
        monthHeatmapChart.clear();
        if (titleEl) titleEl.textContent = '月历热力图（请先在地图上选择城市）';
        return;
    }
    ensureHeatmapMonthPicker();
    const monthYm = selectedHeatmapMonth;
    const metric = selectedMetric || 'AQI';
    const hourlyMetric = metricToHourlyType(metric);
    const pieces = getMetricLegendPieces(metric);
    const metricName = metric === 'AQI' ? 'AQI' : pollutantDisplayName(metric) + ' (ug/m3)';
    if (titleEl) titleEl.textContent = `${currentCityName} · ${monthYm} · ${metricName} 小时热力图`;
    if (hintEl) hintEl.textContent = '正在加载小时数据...';
    let serviceData;
    try {
        serviceData = await fetchMonthlyHourlyHeatmap(currentCityName, monthYm, metric);
    } catch (err) {
        monthHeatmapChart.clear();
        if (hintEl) hintEl.textContent = `热力图服务不可用：${err?.message || err}。请先运行主程序。`;
        return;
    }

    const days = getDaysInMonth(monthYm);
    const hours = buildHourAxis();
    const heatRows = [];
    const byDayHour = {};
    (serviceData.data || []).forEach(item => {
        const ds = String(item[0] || '');
        const day = Number(ds.slice(-2));
        const hour = Number(item[1]);
        const val = Number(item[2]);
        if (!Number.isFinite(day) || !Number.isFinite(hour) || !Number.isFinite(val)) return;
        byDayHour[`${day}-${hour}`] = val;
    });
    days.forEach((d, di) => {
        for (let h = 0; h < 24; h++) {
            const key = `${d}-${h}`;
            const v = byDayHour[key];
            if (v == null || Number.isNaN(v)) continue;
            heatRows.push([h, di, v]);
        }
    });

    const coverage = serviceData.coverage || {};
    if (hintEl) {
        const ratio = Number.isFinite(coverage.ratio) ? (coverage.ratio * 100).toFixed(1) : '--';
        if (metric !== hourlyMetric) {
            hintEl.textContent = `数据源：${hourlyMetric} 小时值（当前筛选 ${metricName}）；覆盖率 ${ratio}%（缺失自动跳过）`;
        } else {
            hintEl.textContent = `覆盖率 ${ratio}%（缺失自动跳过）`;
        }
    }

    monthHeatmapChart.setOption({
        animation: false,
        tooltip: {
            position: 'top',
            backgroundColor: 'rgba(255,255,255,0.96)',
            borderColor: '#c5d8f5',
            borderWidth: 1,
            textStyle: { color: '#1a2a4a' },
            formatter: p => {
                const xh = p.data?.[0];
                const yd = p.data?.[1];
                const vv = p.data?.[2];
                const hourLabel = String(xh).padStart(2, '0') + ':00';
                const dayLabel = String(days[yd] || '--').padStart(2, '0');
                return `${monthYm}-${dayLabel} ${hourLabel}<br/>${metricName}: <b>${vv ?? '--'}</b>`;
            }
        },
        visualMap: {
            type: 'piecewise',
            orient: 'horizontal',
            left: 'center',
            top: 36,
            itemWidth: 18,
            itemHeight: 10,
            textStyle: { color: '#6b8cba', fontSize: 11 },
            pieces: pieces.map(x => ({ min: x.min, max: x.max, label: x.label, color: x.color }))
        },
        grid: { left: 60, right: 20, top: 86, bottom: 26, containLabel: true },
        xAxis: {
            type: 'category',
            data: hours,
            splitArea: { show: true },
            axisLabel: { color: '#6b8cba', fontSize: 11 },
            axisLine: { lineStyle: { color: '#dde8f5' } }
        },
        yAxis: {
            type: 'category',
            data: days.map(d => String(d).padStart(2, '0')),
            splitArea: { show: true },
            axisLabel: { color: '#6b8cba', fontSize: 11 },
            axisLine: { lineStyle: { color: '#dde8f5' } }
        },
        series: [{
            type: 'heatmap',
            data: heatRows,
            emphasis: {
                itemStyle: {
                    shadowBlur: 8,
                    shadowColor: 'rgba(21,101,192,0.25)'
                }
            }
        }]
    }, true);
    setTimeout(() => monthHeatmapChart && monthHeatmapChart.resize(), 30);
}

function applyDetailViewMode(mode) {
    detailViewMode = mode === 'heatmap' ? 'heatmap' : 'city';
    const modeBar = document.getElementById('analysisModeBar');
    const infoBody = document.getElementById('infoBody');
    const aiSection = document.getElementById('aiInsightSection');
    const hmSection = document.getElementById('monthHeatmapSection');
    if (modeBar) modeBar.style.display = currentCityName ? 'flex' : 'none';
    document.querySelectorAll('.analysis-mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === detailViewMode);
    });
    if (detailViewMode === 'heatmap') {
        if (infoBody) infoBody.style.display = 'none';
        if (aiSection) aiSection.style.display = 'none';
        if (hmSection) hmSection.style.display = currentCityName ? 'block' : 'none';
        renderMonthHeatmap();
    } else {
        if (hmSection) hmSection.style.display = 'none';
        if (infoBody) infoBody.style.display = currentCityName ? 'flex' : 'none';
        if (aiSection) aiSection.style.display = currentCityName ? 'block' : 'none';
    }
}

function renderPollutantLegend() {
    const sortHint = document.getElementById('pollutantSortHint');
    if (!sortHint) return;
    sortHint.innerHTML = '<span class="pollutant-sort-arrow">↓</span>严重程度降序';
}

function renderPollutantBars(pollutants) {
    const wrap = document.getElementById('pollutantBarList');
    if (!wrap) return;
    renderPollutantLegend();

    const rows = [
        { key: 'PM2.5_24h', val: pollutants['PM2.5_24h'] },
        { key: 'PM10_24h', val: pollutants['PM10_24h'] },
        { key: 'SO2_24h', val: pollutants['SO2_24h'] },
        { key: 'NO2_24h', val: pollutants['NO2_24h'] },
        { key: 'O3_8h', val: pollutants['O3_8h'] },
        { key: 'O3_8h_24h', val: pollutants['O3_8h_24h'] }
    ].map(item => {
        const n = (item.val == null || Number.isNaN(Number(item.val))) ? null : Number(item.val);
        const lvl = pollutantLevel(item.key, n);
        return { ...item, n, lvl };
    });

    rows.sort((a, b) => {
        const la = a.lvl < 0 ? -1 : a.lvl;
        const lb = b.lvl < 0 ? -1 : b.lvl;
        if (lb !== la) return lb - la;
        return (b.n ?? -1) - (a.n ?? -1);
    });

    const maxVal = rows.reduce((m, r) => Math.max(m, r.n ?? 0), 1);
    wrap.innerHTML = rows.map(r => {
        const active = selectedMetric === r.key ? ' active' : '';
        const valText = r.n == null ? '--' : String(r.n);
        const levelText = pollutantLevelText(r.lvl);
        const color = r.lvl >= 0 ? POLLUTANT_COLOR_LEVELS[r.lvl] : '#9fb3c8';
        const width = r.n == null ? 0 : Math.max(12, Math.round((r.n / maxVal) * 100));
        const title = `${pollutantDisplayName(r.key)} ${valText} ug/m3 | ${levelText}`;
        return `<div class="pollutant-item${active}" title="${title}">`
            + `<div class="pollutant-head"><span class="pollutant-name">${pollutantDisplayName(r.key)}</span>`
            + `<span class="pollutant-value">${valText}</span></div>`
            + `<div class="pollutant-track"><div class="pollutant-fill" style="width:${width}%;background:${color};"></div></div>`
            + `</div>`;
    }).join('');
}

const CITY_TREND_CACHE = new Map();
function getCityTrendValues(cityName, metric, startIdx, endIdx) {
    const key = cityName + '::' + metric + '::' + startIdx + '::' + endIdx;
    if (CITY_TREND_CACHE.has(key)) {
        return CITY_TREND_CACHE.get(key);
    }
    const out = [];
    for (let i = startIdx; i <= endIdx; i++) {
        const date = ALL_DATES[i];
        if (metric === 'AQI') {
            out.push(CITY_DATA_BY_DATE[date]?.[cityName] ?? null);
        } else {
            out.push(POLLUTANTS_DATA[date]?.[cityName]?.[metric] ?? null);
        }
    }
    CITY_TREND_CACHE.set(key, out);
    return out;
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function withAIDisclaimer(text) {
    const base = text || '';
    return base ? (base + '\\n仅供参考') : '仅供参考';
}

function stripSourceMarks(text) {
    return String(text || '')
        .replace(/\\[S\\d+\\]/gi, '')
        .replace(/\\s{2,}/g, ' ')
        .replace(/\\s+([，。！？；：])/g, '$1')
        .trim();
}

function escapeHtml(text) {
    return String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatCauseBulletList(text) {
    const cleaned = stripSourceMarks(text || '');
    if (!cleaned) {
        return '<div class="ai-cause-grid"><div class="ai-cause-item"><div class="ai-cause-no">1</div><div class="ai-cause-text">--</div></div></div>';
    }

    const normalized = cleaned
        .replace(/\\r/g, '\\n')
        .replace(/(^|\\n)\\s*(\\d{1,2})\\s*(?=\\n)/g, '$1$2）')
        .trim();
    const ordered = [];

    const markerRe = /(\\d{1,2})\\s*(?:[、\\)）]|\\.(?!\\d))\\s*/g;
    const marks = [];
    let mk;
    while ((mk = markerRe.exec(normalized)) !== null) {
        marks.push({ start: mk.index, end: markerRe.lastIndex });
    }
    if (marks.length >= 2 || (marks.length === 1 && marks[0].start <= 2)) {
        for (let i = 0; i < marks.length; i++) {
            const segStart = marks[i].end;
            const segEnd = i + 1 < marks.length ? marks[i + 1].start : normalized.length;
            const piece = normalized
                .slice(segStart, segEnd)
                .replace(/^[\\s；;，,]+/, '')
                .replace(/[\\s；;]+$/, '')
                .trim();
            if (piece && !/^\\d+$/.test(piece)) ordered.push(piece);
        }
    }

    if (!ordered.length) {
        const lines = normalized
            .split('\\n')
            .map(s => s.trim())
            .filter(Boolean)
            .map(s => s.replace(/^\\d+\\s*[\\.、\\)）]\\s*/, '').trim())
            .filter(s => s && !/^\\d+$/.test(s));
        if (lines.length >= 2) ordered.push(...lines);
    }
    if (!ordered.length) {
        const semi = normalized
            .split(/[；;]/)
            .map(s => s.trim())
            .filter(Boolean)
            .map(s => s.replace(/^\\d+\\s*[\\.、\\)）]\\s*/, '').trim())
            .filter(s => s && !/^\\d+$/.test(s));
        if (semi.length >= 2) ordered.push(...semi);
    }
    if (!ordered.length) {
        ordered.push(normalized);
    }
    const econItems = ordered.filter(s => /经济|GDP|产业结构|经济体量|经济总量/.test(s));
    const nonEconItems = ordered.filter(s => !/经济|GDP|产业结构|经济体量|经济总量/.test(s));
    const reordered = [...nonEconItems, ...econItems];
    const trimmed = reordered.slice(0, 6);
    return '<div class="ai-cause-grid">'
        + trimmed.map((item, idx) =>
            `<div class="ai-cause-item"><div class="ai-cause-no">${idx + 1}</div><div class="ai-cause-text">${escapeHtml(item)}</div></div>`
        ).join('')
        + '</div>';
}

const AI_CONFIG_STORAGE_KEY = 'APP_AI_SETTINGS';
const AI_ONLINE_READY_KEY = 'APP_AI_ONLINE_READY';
const AI_CONTROL_SERVICE_BASE = 'http://127.0.0.1:8790';
let aiRunMode = window.APP_RUN_MODE || 'offline';
let aiRuntimeConfig = {
    baseUrl: AI_ANALYSIS_API_BASE || 'http://127.0.0.1:8787',
    provider: 'bailian',
    model: '',
    apiKey: '',
    rememberKey: false
};

function loadAIRuntimeConfig() {
    try {
        const raw = localStorage.getItem(AI_CONFIG_STORAGE_KEY);
        if (!raw) return;
        const cfg = JSON.parse(raw);
        aiRuntimeConfig.baseUrl = (cfg.baseUrl || aiRuntimeConfig.baseUrl || '').trim();
        aiRuntimeConfig.provider = (cfg.provider || 'bailian').trim();
        aiRuntimeConfig.model = (cfg.model || '').trim();
        aiRuntimeConfig.rememberKey = !!cfg.rememberKey;
        aiRuntimeConfig.apiKey = aiRuntimeConfig.rememberKey ? ((cfg.apiKey || '').trim()) : '';
    } catch (err) {}
}

function persistAIRuntimeConfig() {
    const cfg = {
        baseUrl: aiRuntimeConfig.baseUrl,
        provider: aiRuntimeConfig.provider,
        model: aiRuntimeConfig.model,
        rememberKey: !!aiRuntimeConfig.rememberKey,
        apiKey: aiRuntimeConfig.rememberKey ? (aiRuntimeConfig.apiKey || '') : ''
    };
    localStorage.setItem(AI_CONFIG_STORAGE_KEY, JSON.stringify(cfg));
}

function markAIOnlineReady(ready) {
    localStorage.setItem(AI_ONLINE_READY_KEY, ready ? '1' : '0');
}

function isAIOnlineReady() {
    return localStorage.getItem(AI_ONLINE_READY_KEY) === '1';
}

function hasValidOnlineConfig() {
    const baseOk = !!(aiRuntimeConfig.baseUrl || '').trim();
    const keyOk = !!(aiRuntimeConfig.apiKey || '').trim();
    return baseOk && keyOk;
}

function parseBaseHostPort(baseUrl) {
    try {
        const u = new URL(baseUrl || '');
        const host = (u.hostname || '').trim();
        const port = Number(u.port || (u.protocol === 'https:' ? 443 : 80));
        return { host, port, protocol: u.protocol };
    } catch (err) {
        return null;
    }
}

function isLocalAIBase(baseUrl) {
    const info = parseBaseHostPort(baseUrl);
    if (!info) return false;
    return info.host === '127.0.0.1' || info.host === 'localhost';
}

async function fetchWithTimeout(url, options, timeoutMs) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), Math.max(1000, timeoutMs || 5000));
    try {
        return await fetch(url, { ...(options || {}), signal: ctrl.signal });
    } finally {
        clearTimeout(timer);
    }
}

async function checkAIHealth(baseUrl, apiKey) {
    const headers = {};
    if (apiKey) headers['X-API-Key'] = apiKey;
    const resp = await fetchWithTimeout((baseUrl || '').replace(/\\/$/, '') + '/health', {
        method: 'GET',
        headers: headers
    }, 2500);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    return true;
}

async function checkAIProvider(baseUrl, apiKey, provider, model) {
    const headers = { 'Content-Type': 'application/json' };
    if (apiKey) headers['X-API-Key'] = apiKey;
    const resp = await fetchWithTimeout((baseUrl || '').replace(/\\/$/, '') + '/api/provider/check', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            provider: provider || 'bailian',
            model: model || ''
        })
    }, 12000);
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok || !data.ok) {
        throw new Error(data.message || ('HTTP ' + resp.status));
    }
    return data;
}

async function waitAIHealthReady(baseUrl, apiKey, attempts, delayMs, onTry) {
    let lastErr = null;
    const total = Math.max(1, attempts || 1);
    for (let i = 0; i < total; i++) {
        if (typeof onTry === 'function') onTry(i + 1, total);
        try {
            await checkAIHealth(baseUrl, apiKey);
            return true;
        } catch (err) {
            lastErr = err;
            if (i < total - 1) {
                await new Promise(resolve => setTimeout(resolve, Math.max(200, delayMs || 500)));
            }
        }
    }
    throw lastErr || new Error('AI service not ready');
}

async function startLocalAIService(baseUrl) {
    const info = parseBaseHostPort(baseUrl);
    if (!info) throw new Error('服务地址格式不正确');
    const resp = await fetchWithTimeout(AI_CONTROL_SERVICE_BASE + '/api/ai/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            host: info.host,
            port: info.port,
            wait_seconds: 1.5
        })
    }, 30000);
    const data = await resp.json().catch(() => ({}));
    const msg = String(data.message || '');
    if (!resp.ok || !data.ok) {
        // 兼容旧控制器：可能返回500但进程已拉起（health尚在预热）
        if (msg.includes('started') || msg.includes('timed out') || msg.includes('warming')) {
            return data;
        }
        throw new Error(msg || ('HTTP ' + resp.status));
    }
    return data;
}

function applyAIBaseUrl() {
    const base = (aiRuntimeConfig.baseUrl || '').trim();
    if (base) {
        AI_ANALYSIS_API_BASE = base;
        localStorage.setItem('APP_AI_BASE_URL', base);
    }
}

function setAIModeStateText() {
    const modeEl = document.getElementById('aiModeState');
    if (!modeEl) return;
    const readyText = isAIOnlineReady() ? '已完成在线配置' : '未完成在线配置';
    modeEl.textContent = aiRunMode === 'online'
        ? ('在线模式（可使用AI分析） | ' + readyText)
        : ('离线模式（仅本地数据，不请求AI服务） | ' + readyText);
}

function syncAIConfigFormFromState() {
    const baseInput = document.getElementById('aiApiBaseInput');
    const providerSel = document.getElementById('aiProviderSelect');
    const modelInput = document.getElementById('aiModelInput');
    const keyInput = document.getElementById('aiApiKeyInput');
    const remember = document.getElementById('aiRememberKey');
    if (baseInput) baseInput.value = aiRuntimeConfig.baseUrl || '';
    if (providerSel) providerSel.value = aiRuntimeConfig.provider || 'bailian';
    if (modelInput) modelInput.value = aiRuntimeConfig.model || '';
    if (keyInput) keyInput.value = aiRuntimeConfig.apiKey || '';
    if (remember) remember.checked = !!aiRuntimeConfig.rememberKey;
    setAIModeStateText();
}

function readAIConfigFormToState() {
    const baseInput = document.getElementById('aiApiBaseInput');
    const providerSel = document.getElementById('aiProviderSelect');
    const modelInput = document.getElementById('aiModelInput');
    const keyInput = document.getElementById('aiApiKeyInput');
    const remember = document.getElementById('aiRememberKey');
    aiRuntimeConfig.baseUrl = (baseInput?.value || '').trim() || 'http://127.0.0.1:8787';
    aiRuntimeConfig.provider = (providerSel?.value || 'bailian').trim();
    aiRuntimeConfig.model = (modelInput?.value || '').trim();
    aiRuntimeConfig.rememberKey = !!remember?.checked;
    aiRuntimeConfig.apiKey = (keyInput?.value || '').trim();
}

function setAIConfigStatus(text) {
    const el = document.getElementById('aiConfigStatus');
    if (el) el.textContent = text || '--';
}

function openAIConfigDrawer() {
    syncAIConfigFormFromState();
    document.getElementById('aiConfigBackdrop')?.classList.add('show');
    document.getElementById('aiConfigDrawer')?.classList.add('show');
    localStorage.removeItem('APP_AI_NEED_SETUP');
}

function closeAIConfigDrawer() {
    document.getElementById('aiConfigBackdrop')?.classList.remove('show');
    document.getElementById('aiConfigDrawer')?.classList.remove('show');
}

async function testAIConnection() {
    readAIConfigFormToState();
    applyAIBaseUrl();
    setAIConfigStatus('正在测试连接...');
    if (!hasValidOnlineConfig()) {
        markAIOnlineReady(false);
        setAIConfigStatus('请先填写服务地址和API Key');
        setAIModeStateText();
        return;
    }
    try {
        await checkAIHealth(AI_ANALYSIS_API_BASE || '', aiRuntimeConfig.apiKey);
        setAIConfigStatus('服务可达，正在校验模型...');
        await checkAIProvider(
            AI_ANALYSIS_API_BASE || '',
            aiRuntimeConfig.apiKey,
            aiRuntimeConfig.provider,
            aiRuntimeConfig.model
        );
        markAIOnlineReady(true);
        setAIConfigStatus('连接成功：服务与模型均可用');
    } catch (err) {
        try {
            if (isLocalAIBase(AI_ANALYSIS_API_BASE || '')) {
                setAIConfigStatus('AI服务未启动，正在自动启动...');
                await startLocalAIService(AI_ANALYSIS_API_BASE || '');
                await waitAIHealthReady(
                    AI_ANALYSIS_API_BASE || '',
                    aiRuntimeConfig.apiKey,
                    15,
                    1000,
                    (cur, total) => setAIConfigStatus(`AI服务已启动，正在等待就绪... (${cur}/${total})`)
                );
                setAIConfigStatus('服务已就绪，正在校验模型...');
                await checkAIProvider(
                    AI_ANALYSIS_API_BASE || '',
                    aiRuntimeConfig.apiKey,
                    aiRuntimeConfig.provider,
                    aiRuntimeConfig.model
                );
                markAIOnlineReady(true);
                setAIConfigStatus('AI服务已启动，模型鉴权成功');
            } else {
                markAIOnlineReady(false);
                setAIConfigStatus('连接失败：' + (err?.message || 'unknown error'));
            }
        } catch (startErr) {
            markAIOnlineReady(false);
            const raw = String(startErr?.message || err?.message || 'unknown error');
            if (raw.includes('Failed to fetch')) {
                setAIConfigStatus('启动失败：本地AI控制服务不可达。请重新运行主程序后重试。');
            } else if (raw.includes('AbortError') || raw.includes('timed out')) {
                setAIConfigStatus('启动超时：服务仍未就绪。请稍后重试，或查看 logs/ai_service.err.log');
            } else {
                setAIConfigStatus('启动/连接失败：' + raw);
            }
        }
    }
    setAIModeStateText();
}

function onAppRunModeChanged(mode) {
    aiRunMode = mode || 'offline';
    setAIModeStateText();
    const btn = document.getElementById('aiGenerateBtn');
    if (btn) btn.disabled = (aiRunMode !== 'online' || !isAIOnlineReady());
    if (aiRunMode !== 'online') {
        resetAIInsightDisplay('当前为离线模式，AI分析已关闭');
    } else if (!isAIOnlineReady()) {
        resetAIInsightDisplay('在线模式未完成配置，请先在“AI服务设置”中填写地址和API Key并测试连接');
        openAIConfigDrawer();
    }
}

window.onAppRunModeChanged = onAppRunModeChanged;
window.isAIOnlineConfigured = () => isAIOnlineReady();
window.openAIConfigFromBoot = () => openAIConfigDrawer();

let aiProgressTimer = null;

function setAIProgress(value) {
    const wrap = document.getElementById('aiProgressWrap');
    const bar = document.getElementById('aiProgressBar');
    if (!wrap || !bar) return;
    wrap.style.display = 'block';
    const v = Math.max(0, Math.min(100, Number(value) || 0));
    bar.style.width = v + '%';
}

function startAIProgress() {
    const stages = [
        { p: 16, text: '\\u6b63\\u5728\\u8054\\u7f51\\u68c0\\u7d22\\u76f8\\u5173\\u4fe1\\u6e90...' },
        { p: 44, text: '\\u6b63\\u5728\\u62c9\\u53d6\\u5e76\\u63d0\\u53d6\\u7f51\\u9875\\u8bc1\\u636e...' },
        { p: 72, text: '\\u6b63\\u5728\\u751f\\u6210\\u805a\\u843d\\u4e0e\\u6269\\u6563\\u5206\\u6790...' },
        { p: 88, text: '\\u6b63\\u5728\\u6574\\u7406\\u6765\\u6e90\\u4e0e\\u53ef\\u89c6\\u5316\\u5c55\\u793a...' }
    ];
    let idx = 0;
    setAIProgress(5);
    setText('aiStatus', stages[0].text);
    if (aiProgressTimer) clearInterval(aiProgressTimer);
    aiProgressTimer = setInterval(() => {
        if (idx >= stages.length) return;
        setAIProgress(stages[idx].p);
        setText('aiStatus', stages[idx].text);
        idx += 1;
    }, 1200);
}

function finishAIProgress(statusText) {
    if (aiProgressTimer) {
        clearInterval(aiProgressTimer);
        aiProgressTimer = null;
    }
    setAIProgress(100);
    if (statusText) setText('aiStatus', statusText);
    setTimeout(() => {
        const wrap = document.getElementById('aiProgressWrap');
        if (wrap) wrap.style.display = 'none';
    }, 450);
}

function resetAIInsightDisplay(statusText) {
    const blocks = document.getElementById('aiBlocks');
    const sources = document.getElementById('aiSources');
    const list = document.getElementById('aiSourcesList');
    if (aiProgressTimer) {
        clearInterval(aiProgressTimer);
        aiProgressTimer = null;
    }
    const wrap = document.getElementById('aiProgressWrap');
    const bar = document.getElementById('aiProgressBar');
    if (wrap) wrap.style.display = 'none';
    if (bar) bar.style.width = '0%';
    setText('aiStatus', statusText || t('ai.empty'));
    setText('aiSettlementText', '--');
    setText('aiDiffusionText', '--');
    const causeEl = document.getElementById('aiCauseText');
    if (causeEl) causeEl.innerHTML = '--';
    if (blocks) blocks.style.display = 'none';
    if (sources) sources.style.display = 'none';
    if (list) list.innerHTML = '';
}

const AI_INSIGHT_CACHE = new Map();

function getCurrentAIContextKey(payload) {
    const snap = payload?.snapshot || {};
    const city = snap.city || currentCityName || '';
    const date = snap.date || ALL_DATES[currentDateIndex] || '';
    const metric = snap.metric || selectedMetric || 'AQI';
    const radius = snap.radiusKm != null
        ? Number(snap.radiusKm)
        : (typeof settlementRadiusKm === 'number' ? settlementRadiusKm : 120);
    return [city, date, metric, radius].join('::');
}

function storeAIInsightInCache(cacheKey, insightData) {
    if (!cacheKey || !insightData) return;
    AI_INSIGHT_CACHE.set(cacheKey, {
        settlement_text: insightData.settlement_text || '--',
        diffusion_text: insightData.diffusion_text || '--',
        cause_text: insightData.cause_text || '--',
        citations: Array.isArray(insightData.citations) ? insightData.citations : [],
        status_text: insightData.status_text || t('ai.empty')
    });
}

function renderAICitations(citations) {
    const wrap = document.getElementById('aiSources');
    const list = document.getElementById('aiSourcesList');
    if (!wrap || !list) return;
    if (!citations || !citations.length) {
        wrap.style.display = 'none';
        list.innerHTML = '';
        return;
    }
    list.innerHTML = citations.map(c => {
        const title = c.title || c.id || '\\u6765\\u6e90';
        const href = c.url || '#';
        const publish = c.published_at ? ('<span class=\"ai-source-time\">\\u53d1\\u5e03: ' + c.published_at + '</span>') : '';
        const access = c.accessed_at ? ('<span class=\"ai-source-time\">\\u68c0\\u7d22: ' + c.accessed_at + '</span>') : '';
        const fieldText = c.used_fields && c.used_fields.length
            ? ('<div class=\"ai-source-snippet\">\\u4f7f\\u7528\\u5b57\\u6bb5: ' + c.used_fields.join(', ') + '</div>')
            : '';
        const snippet = c.snippet
            ? ('<div class=\"ai-source-snippet\">\\u8bc1\\u636e\\u6458\\u8981: ' + c.snippet + '</div>')
            : '';
        return '<li><a href=\"' + href + '\" target=\"_blank\" rel=\"noopener noreferrer\">'
            + title + '</a> ' + publish + access + fieldText + snippet + '</li>';
    }).join('');
    wrap.style.display = 'block';
}

function renderAIInsight(insightData, statusText) {
    const blocks = document.getElementById('aiBlocks');
    setText('aiSettlementText', stripSourceMarks(insightData?.settlement_text || '--'));
    setText('aiDiffusionText', stripSourceMarks(insightData?.diffusion_text || '--'));
    const causeEl = document.getElementById('aiCauseText');
    if (causeEl) causeEl.innerHTML = formatCauseBulletList(insightData?.cause_text || '--');
    setText('aiStatus', withAIDisclaimer(statusText || insightData?.status_text || t('ai.empty')));
    if (blocks) blocks.style.display = 'grid';
}

function restoreAIInsightFromCache(payload) {
    const contextPayload = payload || buildAIAnalysisPayload();
    const key = getCurrentAIContextKey(contextPayload);
    if (!AI_INSIGHT_CACHE.has(key)) return false;
    const cached = AI_INSIGHT_CACHE.get(key);
    renderAIInsight(cached, cached.status_text || t('ai.empty'));
    return true;
}

function refreshAIInsightPanel() {
    if (!currentCityName) {
        resetAIInsightDisplay(t('ai.empty'));
        return;
    }
    if (aiRunMode !== 'online') {
        resetAIInsightDisplay('当前为离线模式，AI分析已关闭');
        return;
    }
    if (!isAIOnlineReady()) {
        resetAIInsightDisplay('在线模式未完成配置，请先在“AI服务设置”中填写地址和API Key并测试连接');
        return;
    }
    if (!restoreAIInsightFromCache()) {
        resetAIInsightDisplay(t('ai.empty'));
    }
}

window.refreshAIInsightPanel = refreshAIInsightPanel;

function buildAIAnalysisPayload() {
    const snapshotBase = (typeof getCurrentSettlementSnapshot === 'function')
        ? getCurrentSettlementSnapshot()
        : null;
    const dateStr = ALL_DATES[currentDateIndex];
    const fallbackAQI = CITY_DATA_BY_DATE[dateStr]?.[currentCityName] ?? null;
    return {
        snapshot: {
            city: currentCityName,
            date: dateStr,
            metric: selectedMetric,
            radiusKm: typeof settlementRadiusKm === 'number' ? settlementRadiusKm : 120,
            in_count: snapshotBase?.in_count ?? null,
            in_avg: snapshotBase?.in_avg ?? fallbackAQI,
            out_avg: snapshotBase?.out_avg ?? null,
            delta_day: snapshotBase?.delta_day ?? null,
            slope_7d: snapshotBase?.slope_7d ?? null,
            diffusion_label: snapshotBase?.diffusion_label ?? null,
            diffusion_detail: snapshotBase?.diffusion_detail ?? null
        },
        history: snapshotBase?.history || []
    };
}

function renderLocalFallbackInsight(payload, reasonText) {
    const snap = payload.snapshot || {};
    const metric = snap.metric || 'AQI';
    const inAvg = snap.in_avg != null ? Number(snap.in_avg).toFixed(1) : '--';
    const outAvg = snap.out_avg != null ? Number(snap.out_avg).toFixed(1) : '--';
    const delta = snap.delta_day != null ? ((snap.delta_day >= 0 ? '+' : '') + Number(snap.delta_day).toFixed(1)) : '--';
    const slope = snap.slope_7d != null ? ((snap.slope_7d >= 0 ? '+' : '') + Number(snap.slope_7d).toFixed(2)) : '--';

    const insightData = {
        settlement_text:
            `${snap.city || currentCityName} 在 ${snap.date || ALL_DATES[currentDateIndex]} 的 ${metric} 聚落结构：`
            + `内圈均值 ${inAvg}，外圈均值 ${outAvg}，较昨日 ${delta}，7日斜率 ${slope}/天。[S1]`,
        diffusion_text:
            `扩散判断：${snap.diffusion_label || '待判定'}。${snap.diffusion_detail || '当前样本有限，建议结合风场数据继续验证。'} [S1][S2]`,
        cause_text:
            '可能受区域传输、局地排放变化和不利气象条件共同影响。建议联动风速风向、湿度和降水数据进行复核。[S1][S2]',
        citations: [
            {
                id: 'S1',
                title: '项目本地城市空气质量时序数据',
                url: 'local://air_quality_dataset/current',
                accessed_at: new Date().toISOString(),
                used_fields: ['city', 'date', 'metric', 'inner_avg', 'outer_avg', 'delta_day', 'slope_7d']
            },
            {
                id: 'S2',
                title: '生态环境部-城市空气质量状况月报',
                url: 'https://www.mee.gov.cn/hjzl/dqhj/cskqzlzkyb/index.shtml',
                accessed_at: new Date().toISOString(),
                used_fields: ['national_background']
            }
        ],
        status_text: reasonText || t('ai.err')
    };

    renderAIInsight(insightData, insightData.status_text);
    storeAIInsightInCache(getCurrentAIContextKey(payload), insightData);
}

async function generateAIInsight() {
    if (aiRunMode !== 'online') {
        setText('aiStatus', withAIDisclaimer('当前为离线模式，无法发起AI分析'));
        return;
    }
    if (!isAIOnlineReady()) {
        setText('aiStatus', withAIDisclaimer('在线模式未完成配置，请先配置并测试连接'));
        openAIConfigDrawer();
        return;
    }
    if (!currentCityName) {
        resetAIInsightDisplay(t('ai.empty'));
        return;
    }
    const btn = document.getElementById('aiGenerateBtn');
    const blocks = document.getElementById('aiBlocks');
    const sourcesWrap = document.getElementById('aiSources');
    const sourcesList = document.getElementById('aiSourcesList');
    if (btn) btn.disabled = true;
    startAIProgress();
    if (blocks) blocks.style.display = 'none';
    if (sourcesWrap) sourcesWrap.style.display = 'none';
    if (sourcesList) sourcesList.innerHTML = '';

    const payload = buildAIAnalysisPayload();
    payload.client_config = {
        provider: aiRuntimeConfig.provider,
        model: aiRuntimeConfig.model
    };
    const cacheKey = getCurrentAIContextKey(payload);

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (aiRuntimeConfig.apiKey) headers['X-API-Key'] = aiRuntimeConfig.apiKey;
        const base = (AI_ANALYSIS_API_BASE || 'http://127.0.0.1:8787').replace(/\\/$/, '');
        const resp = await fetchWithTimeout(base + '/api/analysis/settlement', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        }, 90000);
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();

        const statusText = data.used_fallback
            ? ('AI生成失败，已切换回退模式：' + (data.fallback_reason || '未返回具体原因'))
            : '分析已生成';

        const insightData = {
            settlement_text: data.settlement_text || '--',
            diffusion_text: data.diffusion_text || '--',
            cause_text: data.cause_text || '--',
            citations: data.citations || [],
            status_text: statusText
        };

        renderAIInsight(insightData, statusText);
        finishAIProgress(statusText);
        storeAIInsightInCache(cacheKey, insightData);
    } catch (err) {
        finishAIProgress(t('ai.err'));
        renderLocalFallbackInsight(payload, t('ai.err') + '（未连接分析服务）');
    } finally {
        if (btn) btn.disabled = false;
    }
}

function openCityDetail(cityName) {
    currentCityName = cityName;
    document.getElementById('infoPlaceholder').style.display = 'none';
    document.getElementById('infoHeaderContent').style.display = 'flex';
    document.getElementById('infoBody').style.display = 'flex';
    document.getElementById('filterBar').style.display = 'flex';
    document.getElementById('analysisModeBar').style.display = 'flex';
    document.getElementById('aiInsightSection').style.display = detailViewMode === 'city' ? 'block' : 'none';
    document.getElementById('compareBtn').style.display = 'inline-flex';
    setText('selectedCityBadge', cityName);
    setText('chartPanelTitle', cityName + ' - ' + t('city.trend7d'));
    ensureHeatmapMonthPicker();
    refreshAIInsightPanel();
    if (typeof renderSettlementAnalysis === 'function') {
        renderSettlementAnalysis();
    }
    applyDetailViewMode(detailViewMode);
}

function showCityInfo(cityName, aqiValue) {
    if (compareMode) {
        const idx = compareList.findIndex(c => c.name === cityName);
        if (idx >= 0) {
            compareList.splice(idx, 1);
        } else if (compareList.length < 10) {
            compareList.push({
                name: cityName,
                color: COMPARE_PALETTE[compareList.length % COMPARE_PALETTE.length]
            });
        }
        renderCompareList();
        renderCompareChart();
        renderMapByState();
        document.getElementById('infoSection')?.scrollIntoView({ behavior: 'smooth' });
        return;
    }

    openCityDetail(cityName);
    updateCityPanel();
    renderMapByState();
    document.getElementById('infoSection')?.scrollIntoView({ behavior: 'smooth' });
}

function updateCityPanel() {
    if (compareMode) {
        renderCompareList();
        renderCompareChart();
        if (typeof hideSettlementPanel === 'function') {
            hideSettlementPanel();
        }
        document.getElementById('aiInsightSection').style.display = 'none';
        return;
    }
    document.getElementById('analysisModeBar').style.display = currentCityName ? 'flex' : 'none';
    document.getElementById('aiInsightSection').style.display = (currentCityName && detailViewMode === 'city') ? 'block' : 'none';
    if (!currentCityName) return;

    const dateStr = ALL_DATES[currentDateIndex];
    const aqi = CITY_DATA_BY_DATE[dateStr]?.[currentCityName];
    const info = aqi != null ? getAQIInfo(aqi) : null;
    const pollutants = POLLUTANTS_DATA[dateStr]?.[currentCityName] || {};

    const aqiBadge = document.getElementById('aqiBadge');
    if (aqi != null) {
        aqiBadge.textContent = 'AQI ' + aqi;
        aqiBadge.style.background = getAQIColor(aqi);
        aqiBadge.style.color = '#111';
        setText('levelBadge', info.level);
    } else {
        aqiBadge.textContent = 'AQI --';
        aqiBadge.style.background = 'rgba(21,101,192,0.1)';
        aqiBadge.style.color = '#1a2a4a';
        setText('levelBadge', t('city.no_data'));
    }

    renderPollutantBars(pollutants);
    setText('healthAdvice', info ? info.advice : t('city.no_data_day'));

    if (detailViewMode === 'city') {
        renderLineChart();
        if (typeof renderSettlementAnalysis === 'function') {
            renderSettlementAnalysis();
        }
    } else {
        renderMonthHeatmap();
    }
    refreshAIInsightPanel();
    applyDetailViewMode(detailViewMode);
}

function renderLineChart() {
    const chartDom = document.getElementById('metricsChart');
    if (!chartDom || !currentCityName) return;
    if (!metricsChart) {
        metricsChart = echarts.init(chartDom, null, { renderer: 'canvas' });
    }

    if (typeof settlementCompareMode !== 'undefined'
        && settlementCompareMode
        && typeof renderSettlementCompareInMainChart === 'function') {
        renderSettlementCompareInMainChart();
        return;
    }

    const endIdx = currentDateIndex;
    const startIdx = Math.max(0, endIdx - 6);
    const dates = ALL_DATES.slice(startIdx, endIdx + 1);
    const xLabels = dates.map(d => fmtDate(d).substring(5));

    let values;
    let seriesColor;
    let areaColor0;
    let areaColor1;

    if (selectedMetric === 'AQI') {
        values = getCityTrendValues(currentCityName, selectedMetric, startIdx, endIdx);
        seriesColor = '#1565c0';
        areaColor0 = 'rgba(21,101,192,0.18)';
        areaColor1 = 'rgba(21,101,192,0.01)';
    } else {
        const colors = {
            'PM2.5_24h': '#e74c3c',
            'PM10_24h': '#e67e22',
            'SO2_24h': '#9b59b6',
            'NO2_24h': '#2ecc71',
            'O3_8h': '#3498db',
            'O3_8h_24h': '#16a34a'
        };
        seriesColor = colors[selectedMetric] || '#1565c0';
        areaColor0 = 'rgba(21,101,192,0.15)';
        areaColor1 = 'rgba(21,101,192,0.01)';
        values = getCityTrendValues(currentCityName, selectedMetric, startIdx, endIdx);
    }

    const pointData = values.map(v => ({
        value: v,
        itemStyle: { color: selectedMetric === 'AQI' && v != null ? getAQIColor(v) : seriesColor }
    }));
    const name = metricLabel(selectedMetric);

    metricsChart.setOption({
        backgroundColor: 'transparent',
        legend: { show: false },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.96)',
            borderColor: '#c5d8f5',
            borderWidth: 1,
            textStyle: { color: '#1a2a4a' },
            extraCssText: 'box-shadow:0 4px 16px rgba(21,101,192,0.12);border-radius:10px;',
            formatter: function(params) {
                const p = params[0];
                if (p.value == null) return p.axisValue + '<br/>' + t('city.no_data');
                const color = selectedMetric === 'AQI' ? getAQIColor(p.value) : seriesColor;
                return '<b style="color:#1a2a4a">' + fmtDate(dates[p.dataIndex]) + '</b><br/>'
                    + '<span style="color:' + color + '">●</span> ' + name
                    + ': <b style="color:' + color + ';font-size:16px">' + p.value + '</b>';
            }
        },
        grid: { left: 10, right: 16, bottom: 32, top: 20, containLabel: true },
        xAxis: {
            type: 'category',
            data: xLabels,
            axisLabel: { color: '#7a9cc0', fontSize: 12 },
            axisLine: { lineStyle: { color: '#dde8f5' } },
            axisTick: { lineStyle: { color: '#dde8f5' } }
        },
        yAxis: {
            type: 'value',
            name: name,
            nameTextStyle: { color: '#aac4d8', fontSize: 11 },
            axisLabel: { color: '#7a9cc0', fontSize: 11 },
            axisLine: { show: true, lineStyle: { color: '#dde8f5' } },
            splitLine: { lineStyle: { color: '#eef3fa', type: 'dashed' } }
        },
        series: [{
            type: 'line',
            data: pointData,
            smooth: true,
            connectNulls: false,
            lineStyle: { color: seriesColor, width: 2.5 },
            itemStyle: { borderWidth: 2.5, borderColor: 'white' },
            symbolSize: 11,
            label: {
                show: true,
                color: '#1a2a4a',
                fontSize: 11,
                fontWeight: 'bold',
                formatter: p => p.value != null ? p.value : ''
            },
            areaStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [
                        { offset: 0, color: areaColor0 },
                        { offset: 1, color: areaColor1 }
                    ]
                }
            }
        }]
    }, true);

    setTimeout(() => {
        if (metricsChart) metricsChart.resize();
    }, 50);
}

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedMetric = this.dataset.metric;
        if (compareMode) {
            renderCompareChart();
        } else {
            updateCityPanel();
            refreshAIInsightPanel();
            if (detailViewMode === 'heatmap') renderMonthHeatmap();
        }
    });
});

document.querySelectorAll('.analysis-mode-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        applyDetailViewMode(this.dataset.mode);
        if (detailViewMode === 'city') {
            updateCityPanel();
        } else {
            renderMonthHeatmap();
        }
    });
});

document.getElementById('monthPicker')?.addEventListener('change', function() {
    selectedHeatmapMonth = this.value;
    if (detailViewMode === 'heatmap') renderMonthHeatmap();
});

document.getElementById('aiGenerateBtn')?.addEventListener('click', () => {
    generateAIInsight();
});

document.getElementById('aiConfigBtn')?.addEventListener('click', () => {
    openAIConfigDrawer();
});
document.getElementById('aiCloseConfigBtn')?.addEventListener('click', () => {
    closeAIConfigDrawer();
});
document.getElementById('aiConfigBackdrop')?.addEventListener('click', () => {
    closeAIConfigDrawer();
});
document.getElementById('aiTestConnBtn')?.addEventListener('click', async () => {
    await testAIConnection();
});
document.getElementById('aiSaveConfigBtn')?.addEventListener('click', async () => {
    readAIConfigFormToState();
    applyAIBaseUrl();
    persistAIRuntimeConfig();
    await testAIConnection();
    if (isAIOnlineReady()) {
        setAIConfigStatus('配置已保存并应用');
    }
    closeAIConfigDrawer();
    onAppRunModeChanged(aiRunMode);
});

loadAIRuntimeConfig();
applyAIBaseUrl();
syncAIConfigFormFromState();
onAppRunModeChanged(aiRunMode);
if (localStorage.getItem('APP_AI_NEED_SETUP') === '1') {
    setTimeout(() => openAIConfigDrawer(), 80);
}
"""



