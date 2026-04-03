"""
Map shell module.
"""

from __future__ import annotations

import ui_texts
from utils import fmt_date


def build_css() -> str:
    return """\
html {
    overflow-y: auto !important;
    height: auto !important;
    scroll-behavior: smooth;
}
body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: auto !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    background: #f0f4f8;
    font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

#bootOverlay {
    position: fixed;
    inset: 0;
    z-index: 4000;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(1200px 620px at 50% 28%, rgba(255,255,255,0.92) 0%, rgba(240,246,253,0.95) 46%, rgba(228,238,250,0.97) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 1;
    pointer-events: all;
    transition: opacity 0.26s ease, transform 0.26s ease;
}
#bootOverlay.hidden {
    opacity: 0;
    transform: scale(0.985);
    pointer-events: none;
}
.boot-card {
    width: min(540px, 86vw);
    padding: 28px 28px 22px;
    border-radius: 18px;
    border: 1px solid rgba(21,101,192,0.18);
    box-shadow: 0 20px 60px rgba(20,71,132,0.14), 0 4px 16px rgba(20,71,132,0.08);
    background: rgba(255,255,255,0.78);
}
.boot-ring {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    margin: 0 auto 14px;
    border: 2px solid rgba(21,101,192,0.24);
    border-top-color: rgba(21,101,192,0.9);
    animation: boot-spin 1.1s linear infinite;
}
.boot-title {
    margin: 0;
    text-align: center;
    font-size: 28px;
    letter-spacing: 0.6px;
    color: #16406f;
    font-weight: 800;
}
.boot-progress {
    margin-top: 20px;
    height: 4px;
    border-radius: 999px;
    background: rgba(147,183,220,0.32);
    overflow: hidden;
}
.boot-progress::after {
    content: "";
    display: block;
    height: 100%;
    width: 42%;
    border-radius: inherit;
    background: linear-gradient(90deg, rgba(22,87,160,0.26), rgba(21,101,192,0.95), rgba(22,87,160,0.26));
    animation: boot-flow 1.25s ease-in-out infinite;
}
#bootOverlay.ready .boot-ring {
    animation: none;
    border-top-color: rgba(21,101,192,0.45);
}
#bootOverlay.ready .boot-progress::after {
    width: 100%;
    transform: none;
    animation: none;
    background: linear-gradient(90deg, rgba(21,101,192,0.82), rgba(21,101,192,0.92));
}
.boot-status {
    margin-top: 14px;
    text-align: center;
    font-size: 15px;
    color: #1f4f82;
    font-weight: 700;
}
.boot-sub {
    margin-top: 6px;
    text-align: center;
    font-size: 12px;
    color: #7393b8;
}
.boot-hint {
    margin-top: 16px;
    text-align: center;
    font-size: 12px;
    color: #6f8fb3;
}
.boot-mode-row {
    margin-top: 14px;
    display: flex;
    gap: 10px;
    justify-content: center;
}
.boot-mode-btn {
    border: 1px solid #b8cfea;
    background: #f2f7fe;
    color: #355f8f;
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}
.boot-mode-btn.active {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
    box-shadow: 0 5px 14px rgba(21,101,192,0.25);
}
.boot-mode-tip {
    margin-top: 8px;
    text-align: center;
    font-size: 12px;
    color: #5a7fa8;
}
.boot-retry {
    margin: 14px auto 0;
    display: none;
    border: 1px solid #8db6e4;
    background: #f4f9ff;
    color: #1565c0;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}
.boot-retry.show {
    display: block;
}
.boot-enter {
    margin: 12px auto 0;
    display: block;
    min-width: 132px;
    border: 1px solid #8db6e4;
    background: #eaf2fd;
    color: #7a9cc0;
    border-radius: 999px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 800;
    cursor: not-allowed;
    transition: all 0.2s;
}
.boot-enter.ready {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
    box-shadow: 0 6px 18px rgba(21,101,192,0.26);
    cursor: pointer;
}
.boot-enter.ready:hover {
    transform: translateY(-1px);
    background: #1157a6;
}
@keyframes boot-spin {
    to { transform: rotate(360deg); }
}
@keyframes boot-flow {
    0% { transform: translateX(-55%); }
    100% { transform: translateX(220%); }
}

#mapWrapper > .chart-container,
#mapWrapper > div[_echarts_instance_] {
    position: relative !important;
    top: auto !important;
    left: auto !important;
    width: 100% !important;
    height: 100vh !important;
    display: block !important;
}

#mapWrapper {
    position: relative;
    width: 100%;
    background: #f0f4f8;
}

#mapControls {
    position: absolute;
    left: 14px;
    top: 14px;
    z-index: 500;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.map-ctrl-btn {
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.95);
    border: 1px solid #c5d8f5;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    font-weight: 700;
    color: #1565c0;
    box-shadow: 0 2px 10px rgba(21,101,192,0.13);
    transition: all 0.18s;
    user-select: none;
    text-decoration: none;
    line-height: 1;
}
.map-ctrl-btn:hover {
    background: #1565c0;
    color: white;
    border-color: #1565c0;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(21,101,192,0.3);
}
.map-ctrl-btn:active {
    transform: scale(0.94);
}
.map-ctrl-sep {
    height: 1px;
    background: #dde8f5;
    margin: 2px 4px;
}

#topTimelineBar {
    position: absolute;
    top: 82px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 400;
    background: rgba(255,255,255,0.93);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    box-shadow: 0 4px 18px rgba(21,101,192,0.13);
    border: 1px solid rgba(21,101,192,0.12);
    padding: 7px 18px 9px;
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 500px;
    max-width: 75vw;
    pointer-events: all;
}
#topTimelineBar button {
    padding: 4px 10px;
    background: #e3eaf6;
    color: #1565c0;
    border: none;
    border-radius: 7px;
    cursor: pointer;
    font-weight: 700;
    font-size: 14px;
    transition: all 0.2s;
    flex-shrink: 0;
}
#topTimelineBar button:hover {
    background: #1565c0;
    color: white;
}
.tl-date-label {
    font-size: 11px;
    color: #9fb3c8;
    white-space: nowrap;
    flex-shrink: 0;
}
#topCurrentDate {
    min-width: 108px;
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    color: #1565c0;
    background: #e3eaf6;
    border-radius: 7px;
    padding: 4px 11px;
    flex-shrink: 0;
}
#topSlider {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 5px;
    border-radius: 3px;
    background: #c5d8f5;
    outline: none;
    cursor: pointer;
}
#topSlider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    background: #1565c0;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(21,101,192,0.4);
    transition: transform 0.2s;
}
#topSlider::-webkit-slider-thumb:hover {
    transform: scale(1.25);
}

#scrollHint {
    text-align: center;
    padding: 10px 0 6px;
    background: linear-gradient(to bottom, #f0f4f8, #e8eef6);
    color: #7a9cc0;
    font-size: 13px;
    letter-spacing: 1px;
    user-select: none;
    cursor: pointer;
    border-top: 1px solid #d5e3ef;
    border-bottom: 1px solid #d0dff0;
}
#scrollHint:hover {
    color: #1565c0;
}
#scrollHint .arrow {
    display: block;
    font-size: 20px;
    animation: bounce 1.6s infinite;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}
"""


def build_dom(all_dates: list[str], current_index: int) -> str:
    first_label = fmt_date(all_dates[0])
    last_label = fmt_date(all_dates[-1])
    cur_label = fmt_date(all_dates[current_index])
    app_title = ui_texts.get("app.title")
    compare_label = ui_texts.get("control.compare")
    zoom_in = ui_texts.get("control.zoom_in")
    zoom_out = ui_texts.get("control.zoom_out")
    reset_view = ui_texts.get("control.reset")
    goto_detail = ui_texts.get("control.goto")
    detail_label = ui_texts.get("control.detail")
    prev7 = ui_texts.get("timeline.prev7")
    prev1 = ui_texts.get("timeline.prev1")
    next1 = ui_texts.get("timeline.next1")
    next7 = ui_texts.get("timeline.next7")
    scroll_hint = ui_texts.get("scroll.hint")
    loader_status_init = ui_texts.get("loader.status.init")
    loader_sub_init = ui_texts.get("loader.sub.init")
    loader_hint_default = ui_texts.get("loader.hint.default")
    loader_enter_loading = ui_texts.get("loader.enter.loading")
    loader_retry = ui_texts.get("loader.retry")

    return f"""\
<div id="bootOverlay">
    <div class="boot-card">
        <div class="boot-ring"></div>
        <h1 class="boot-title">{app_title}</h1>
        <div class="boot-progress"></div>
        <div class="boot-status" id="bootStatus">{loader_status_init}</div>
        <div class="boot-sub" id="bootSub">{loader_sub_init}</div>
        <div class="boot-mode-row">
            <button class="boot-mode-btn" id="bootModeOffline" type="button">离线模式</button>
            <button class="boot-mode-btn" id="bootModeOnline" type="button">在线模式（启用AI）</button>
        </div>
        <div class="boot-mode-tip" id="bootModeTip">请先选择模式，再进入页面</div>
        <div class="boot-hint" id="bootHint">{loader_hint_default}</div>
        <button class="boot-enter" id="bootEnter" type="button">{loader_enter_loading}</button>
        <button class="boot-retry" id="bootRetry" type="button">{loader_retry}</button>
    </div>
</div>

<div id="mapWrapper">
    <button id="compareBtn" onclick="toggleCompareMode()">
        <span class="btn-icon" style="background:linear-gradient(135deg,#7c3aed,#a78bfa);">+</span>
        <span id="compareBtnLabel">{compare_label}</span>
    </button>

    <div id="mapControls">
        <button class="map-ctrl-btn" id="ctrlZoomIn" title="{zoom_in}">+</button>
        <button class="map-ctrl-btn" id="ctrlZoomOut" title="{zoom_out}">-</button>
        <button class="map-ctrl-btn" id="ctrlReset" title="{reset_view}" style="font-size:14px;">R</button>
        <button class="map-ctrl-btn" id="ctrlAISetup" title="AI服务设置" style="font-size:12px;">AI</button>
        <div class="map-ctrl-sep"></div>
        <button class="map-ctrl-btn" id="ctrlGoDetail" title="{goto_detail}" style="font-size:13px;">
            v<br><span style="font-size:9px;line-height:1;display:block;">{detail_label}</span>
        </button>
    </div>

    <div id="topTimelineBar">
        <button id="tl-prev-7" title="{prev7}">&laquo;</button>
        <button id="tl-prev-1" title="{prev1}">&lsaquo;</button>
        <span class="tl-date-label">{first_label}</span>
        <input type="range" id="topSlider" min="0" max="{len(all_dates)-1}" value="{current_index}" step="1">
        <span class="tl-date-label">{last_label}</span>
        <button id="tl-next-1" title="{next1}">&rsaquo;</button>
        <button id="tl-next-7" title="{next7}">&raquo;</button>
        <span id="topCurrentDate">{cur_label}</span>
    </div>
</div>

<div id="scrollHint" onclick="document.getElementById('infoSection').scrollIntoView({{behavior:'smooth'}})">
    <span class="arrow">v</span>
    {scroll_hint}
</div>
"""


def build_js() -> str:
    return """\
function byId(id) {
    return document.getElementById(id);
}

function fmtDate(d) {
    return (d && d.length === 8)
        ? d.substring(0, 4) + '-' + d.substring(4, 6) + '-' + d.substring(6, 8)
        : d;
}

function getAQIColor(v) {
    for (const t of AQI_COLORS) {
        if (v <= t.max) return t.color;
    }
    return '#7e0023';
}

function getAQIInfo(v) {
    if (v <= 50) return { level: '\u4f18', advice: '\u7a7a\u6c14\u8d28\u91cf\u4ee4\u4eba\u6ee1\u610f\uff0c\u5404\u7c7b\u4eba\u7fa4\u53ef\u6b63\u5e38\u6d3b\u52a8\u3002' };
    if (v <= 100) return { level: '\u826f', advice: '\u7a7a\u6c14\u8d28\u91cf\u53ef\u63a5\u53d7\uff0c\u654f\u611f\u4eba\u7fa4\u5efa\u8bae\u9002\u5ea6\u9632\u62a4\u3002' };
    if (v <= 150) return { level: '\u8f7b\u5ea6\u6c61\u67d3', advice: '\u654f\u611f\u4eba\u7fa4\u5e94\u51cf\u5c11\u957f\u65f6\u95f4\u6237\u5916\u6d3b\u52a8\u3002' };
    if (v <= 200) return { level: '\u4e2d\u5ea6\u6c61\u67d3', advice: '\u5efa\u8bae\u51cf\u5c11\u5916\u51fa\uff0c\u5fc5\u8981\u65f6\u4f69\u6234\u9632\u62a4\u88c5\u5907\u3002' };
    if (v <= 300) return { level: '\u91cd\u5ea6\u6c61\u67d3', advice: '\u5efa\u8bae\u5c3d\u91cf\u51cf\u5c11\u6237\u5916\u6d3b\u52a8\u5e76\u505a\u597d\u9632\u62a4\u3002' };
    return { level: '\u4e25\u91cd\u6c61\u67d3', advice: '\u5efa\u8bae\u907f\u514d\u6237\u5916\u6d3b\u52a8\uff0c\u5fc5\u987b\u5916\u51fa\u65f6\u52a0\u5f3a\u9632\u62a4\u3002' };
}

function syncMapSubtitle() {
    if (!mapChartInstance) return;
    mapChartInstance.setOption({
        title: buildMapTitle(ALL_DATES[currentDateIndex])
    }, false);
}

let bootOverlayDone = false;
let bootReadyToEnter = false;
let appRunMode = '';

function syncBootModeUI() {
    const offlineBtn = byId('bootModeOffline');
    const onlineBtn = byId('bootModeOnline');
    offlineBtn?.classList.toggle('active', appRunMode === 'offline');
    onlineBtn?.classList.toggle('active', appRunMode === 'online');
    const tip = byId('bootModeTip');
    if (!tip) return;
    if (appRunMode === 'offline') {
        tip.textContent = '离线模式：禁用AI分析，仅使用本地数据解读';
    } else if (appRunMode === 'online') {
        tip.textContent = '在线模式：可使用AI分析与服务设置';
    } else {
        tip.textContent = '请先选择模式，再进入页面';
    }
}

function canEnterBoot() {
    return appRunMode === 'offline' || appRunMode === 'online';
}

function refreshBootEnterByMode() {
    const enterBtn = byId('bootEnter');
    if (!enterBtn) return;
    if (canEnterBoot()) {
        enterBtn.textContent = t('loader.enter.ready');
        enterBtn.classList.add('ready');
    } else {
        enterBtn.textContent = '请选择模式';
        enterBtn.classList.remove('ready');
    }
}

function notifyRunModeChanged() {
    window.APP_RUN_MODE = appRunMode || 'offline';
    if (typeof window.onAppRunModeChanged === 'function') {
        window.onAppRunModeChanged(window.APP_RUN_MODE);
    }
}

function setAppRunMode(mode) {
    if (mode !== 'offline' && mode !== 'online') return;
    appRunMode = mode;
    localStorage.setItem('APP_RUN_MODE', mode);
    if (mode === 'online' && localStorage.getItem('APP_AI_ONLINE_READY') !== '1') {
        localStorage.setItem('APP_AI_NEED_SETUP', '1');
    } else {
        localStorage.removeItem('APP_AI_NEED_SETUP');
    }
    syncBootModeUI();
    refreshBootEnterByMode();
    notifyRunModeChanged();
}

function setBootStatus(mainText, subText) {
    const main = byId('bootStatus');
    const sub = byId('bootSub');
    if (main && mainText) main.textContent = mainText;
    if (sub && subText != null) sub.textContent = subText;
}

function showBootSlowHint() {
    const hint = byId('bootHint');
    const retry = byId('bootRetry');
    if (hint) hint.textContent = t('loader.hint.slow');
    if (retry) retry.classList.add('show');
}

function markBootReady() {
    if (bootReadyToEnter) return;
    bootReadyToEnter = true;
    const enterBtn = byId('bootEnter');
    const hint = byId('bootHint');
    byId('bootOverlay')?.classList.add('ready');
    setBootStatus(t('loader.status.ready'), t('loader.sub.ready'));
    if (hint) hint.textContent = t('loader.hint.ready');
    if (enterBtn) refreshBootEnterByMode();
}

function hideBootOverlay() {
    if (bootOverlayDone) return;
    bootOverlayDone = true;
    document.documentElement.classList.remove('preboot-hide');
    const overlay = byId('bootOverlay');
    overlay?.classList.add('hidden');
}

function syncAllTimelines() {
    const label = fmtDate(ALL_DATES[currentDateIndex]);
    if (byId('topSlider')) byId('topSlider').value = currentDateIndex;
    if (byId('topCurrentDate')) byId('topCurrentDate').textContent = label;
    if (byId('bottomSlider')) byId('bottomSlider').value = currentDateIndex;
    if (byId('bottomCurrentDate')) byId('bottomCurrentDate').textContent = label;
}

function onDateChange(instant) {
    syncAllTimelines();
    renderMapByState();
    if (instant) {
        if (typeof updateCityPanel === 'function') updateCityPanel();
    } else {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (typeof updateCityPanel === 'function') updateCityPanel();
        }, 250);
    }
}

function bindTimelineEvents() {
    byId('tl-prev-7')?.addEventListener('click', () => {
        currentDateIndex = Math.max(0, currentDateIndex - 7);
        onDateChange(true);
    });
    byId('tl-prev-1')?.addEventListener('click', () => {
        currentDateIndex = Math.max(0, currentDateIndex - 1);
        onDateChange(true);
    });
    byId('tl-next-1')?.addEventListener('click', () => {
        currentDateIndex = Math.min(ALL_DATES.length - 1, currentDateIndex + 1);
        onDateChange(true);
    });
    byId('tl-next-7')?.addEventListener('click', () => {
        currentDateIndex = Math.min(ALL_DATES.length - 1, currentDateIndex + 7);
        onDateChange(true);
    });
    byId('topSlider')?.addEventListener('input', function() {
        currentDateIndex = parseInt(this.value, 10);
        onDateChange(false);
    });
    byId('btn-prev-7')?.addEventListener('click', () => {
        currentDateIndex = Math.max(0, currentDateIndex - 7);
        onDateChange(true);
    });
    byId('btn-prev-1')?.addEventListener('click', () => {
        currentDateIndex = Math.max(0, currentDateIndex - 1);
        onDateChange(true);
    });
    byId('btn-next-1')?.addEventListener('click', () => {
        currentDateIndex = Math.min(ALL_DATES.length - 1, currentDateIndex + 1);
        onDateChange(true);
    });
    byId('btn-next-7')?.addEventListener('click', () => {
        currentDateIndex = Math.min(ALL_DATES.length - 1, currentDateIndex + 7);
        onDateChange(true);
    });
    byId('bottomSlider')?.addEventListener('input', function() {
        currentDateIndex = parseInt(this.value, 10);
        onDateChange(false);
    });
}

bindTimelineEvents();
setBootStatus(t('loader.status.framework'), t('loader.sub.framework'));
const bootHint = byId('bootHint');
const bootEnter = byId('bootEnter');
const bootRetry = byId('bootRetry');
if (bootHint) bootHint.textContent = t('loader.hint.default');
if (bootEnter) bootEnter.textContent = '请选择模式';
if (bootRetry) bootRetry.textContent = t('loader.retry');
syncBootModeUI();
refreshBootEnterByMode();
if (appRunMode === 'offline' || appRunMode === 'online') {
    notifyRunModeChanged();
}
byId('bootModeOffline')?.addEventListener('click', () => setAppRunMode('offline'));
byId('bootModeOnline')?.addEventListener('click', () => setAppRunMode('online'));

byId('bootRetry')?.addEventListener('click', () => window.location.reload());
byId('bootEnter')?.addEventListener('click', () => {
    if (!canEnterBoot()) {
        const tip = byId('bootModeTip');
        if (tip && !appRunMode) tip.textContent = '请先选择离线或在线模式';
        return;
    }
    hideBootOverlay();
    if (appRunMode === 'online' && localStorage.getItem('APP_AI_ONLINE_READY') !== '1') {
        setTimeout(() => {
            if (typeof window.openAIConfigFromBoot === 'function') {
                window.openAIConfigFromBoot();
            }
        }, 120);
    }
});
document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && canEnterBoot() && !bootOverlayDone) {
        hideBootOverlay();
    }
});

const bootSlowTimer = setTimeout(() => {
    if (!bootOverlayDone) showBootSlowHint();
}, 10000);
const bootForceReadyTimer = setTimeout(() => {
    if (!bootReadyToEnter) {
        setBootStatus(t('loader.status.ready'), '初始化较慢，已允许先进入页面');
        markBootReady();
    }
}, 15000);

setTimeout(function() {
    setBootStatus(t('loader.status.connect_map'), t('loader.sub.connect_map'));
    const mapWrapper = byId('mapWrapper');
    const chartDivs = document.querySelectorAll('[_echarts_instance_]');

    chartDivs.forEach(function(dom) {
        if (dom.id !== 'metricsChart') {
            mapWrapper.insertBefore(dom, mapWrapper.firstChild);
            mapChartInstance = echarts.getInstanceByDom(dom);
        }
    });

    if (!mapChartInstance) {
        setBootStatus(t('loader.status.failed'), t('loader.sub.failed'));
        showBootSlowHint();
        clearTimeout(bootSlowTimer);
        clearTimeout(bootForceReadyTimer);
        markBootReady();
        return;
    }

    setBootStatus(t('loader.status.bind'), t('loader.sub.bind'));
    currentZoom = 1.2;
    currentCenter = [105, 36];

    let isSettingView = false;
    const ZOOM_STEP = 1.5;
    const ZOOM_MIN = 0.8;
    const ZOOM_MAX = 8.0;

    function applyGeoView(targetZoom, targetCenter) {
        currentZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, targetZoom));
        currentCenter = targetCenter || currentCenter;
        isSettingView = true;
        mapChartInstance.setOption({
            geo: [{
                zoom: currentZoom,
                center: currentCenter,
                scaleLimit: {
                    min: ZOOM_MIN,
                    max: ZOOM_MAX
                }
            }]
        }, false);
        isSettingView = false;
        renderMapByState();
    }

    mapChartInstance.on('georoam', function() {
        if (isSettingView) return;
        try {
            const opt = mapChartInstance.getOption();
            const geoOpt = opt.geo && opt.geo[0];
            if (!geoOpt) return;
            if (geoOpt.zoom != null) {
                const clampedZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, geoOpt.zoom));
                if (Math.abs(clampedZoom - geoOpt.zoom) > 0.001) {
                    applyGeoView(clampedZoom, geoOpt.center || currentCenter);
                    return;
                }
                currentZoom = clampedZoom;
            }
            if (geoOpt.center) currentCenter = geoOpt.center;
        } catch (err) {}
    });

    byId('ctrlZoomIn')?.addEventListener('click', () => applyGeoView(currentZoom * ZOOM_STEP));
    byId('ctrlZoomOut')?.addEventListener('click', () => applyGeoView(currentZoom / ZOOM_STEP));
    byId('ctrlReset')?.addEventListener('click', () => applyGeoView(1.2, [105, 36]));
    byId('ctrlAISetup')?.addEventListener('click', () => {
        if (typeof window.openAIConfigFromBoot === 'function') {
            window.openAIConfigFromBoot();
        }
    });
    byId('ctrlGoDetail')?.addEventListener('click', () => {
        byId('infoSection')?.scrollIntoView({ behavior: 'smooth' });
    });

    mapChartInstance.on('click', function(params) {
        if (params.componentType !== 'series' || !params.name || typeof showCityInfo !== 'function') return;

        let aqi = 0;
        if (Array.isArray(params.value) && params.value.length > 2) {
            aqi = params.value[2];
        } else if (params.data && Array.isArray(params.data.value) && params.data.value.length > 2) {
            aqi = params.data.value[2];
        } else if (typeof params.value === 'number') {
            aqi = params.value;
        }
        showCityInfo(params.name, aqi);
    });

    let finishHooked = false;
    const onBootRenderFinished = function() {
        if (bootOverlayDone) return;
        clearTimeout(bootSlowTimer);
        clearTimeout(bootForceReadyTimer);
        markBootReady();
        if (finishHooked) {
            mapChartInstance.off('finished', onBootRenderFinished);
            finishHooked = false;
        }
    };
    mapChartInstance.on('finished', onBootRenderFinished);
    finishHooked = true;

    setBootStatus(t('loader.status.render'), t('loader.sub.render'));
    renderMapByState(true);
    setTimeout(() => {
        if (!bootReadyToEnter) onBootRenderFinished();
    }, 1000);

    window.addEventListener('resize', () => {
        if (mapChartInstance) mapChartInstance.resize();
        if (metricsChart) metricsChart.resize();
        if (settlementMapChart) settlementMapChart.resize();
    });
}, 120);
"""


