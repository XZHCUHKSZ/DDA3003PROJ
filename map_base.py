"""
Map shell module.
"""

from __future__ import annotations

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

    return f"""\
<div id="bootOverlay">
    <div class="boot-card">
        <div class="boot-ring"></div>
        <h1 class="boot-title">空气质量可视化平台</h1>
        <div class="boot-progress"></div>
        <div class="boot-status" id="bootStatus">正在初始化可视化引擎...</div>
        <div class="boot-sub" id="bootSub">正在准备地图组件与城市数据</div>
        <div class="boot-hint" id="bootHint">首次加载约 5-10 秒，请稍候</div>
        <button class="boot-enter" id="bootEnter" type="button">加载中...</button>
        <button class="boot-retry" id="bootRetry" type="button">刷新重试</button>
    </div>
</div>

<div id="mapWrapper">
    <button id="compareBtn" onclick="toggleCompareMode()">
        <span class="btn-icon" style="background:linear-gradient(135deg,#7c3aed,#a78bfa);">+</span>
        <span id="compareBtnLabel">对比模式</span>
    </button>

    <div id="mapControls">
        <button class="map-ctrl-btn" id="ctrlZoomIn" title="放大">+</button>
        <button class="map-ctrl-btn" id="ctrlZoomOut" title="缩小">-</button>
        <button class="map-ctrl-btn" id="ctrlReset" title="重置视图" style="font-size:14px;">R</button>
        <div class="map-ctrl-sep"></div>
        <button class="map-ctrl-btn" id="ctrlGoDetail" title="跳转到详情" style="font-size:13px;">
            v<br><span style="font-size:9px;line-height:1;display:block;">详情</span>
        </button>
    </div>

    <div id="topTimelineBar">
        <button id="tl-prev-7" title="前 7 天">&laquo;</button>
        <button id="tl-prev-1" title="前 1 天">&lsaquo;</button>
        <span class="tl-date-label">{first_label}</span>
        <input type="range" id="topSlider" min="0" max="{len(all_dates)-1}" value="{current_index}" step="1">
        <span class="tl-date-label">{last_label}</span>
        <button id="tl-next-1" title="后 1 天">&rsaquo;</button>
        <button id="tl-next-7" title="后 7 天">&raquo;</button>
        <span id="topCurrentDate">{cur_label}</span>
    </div>
</div>

<div id="scrollHint" onclick="document.getElementById('infoSection').scrollIntoView({{behavior:'smooth'}})">
    <span class="arrow">v</span>
    下滑查看城市详情与历史趋势
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
    if (v <= 50) return { level: '?', advice: '???????????????????' };
    if (v <= 100) return { level: '?', advice: '???????????????????' };
    if (v <= 150) return { level: '????', advice: '???????????????' };
    if (v <= 200) return { level: '????', advice: '?????????????????' };
    if (v <= 300) return { level: '????', advice: '????????????????' };
    return { level: '????', advice: '???????????????????' };
}

function syncMapSubtitle() {
    if (!mapChartInstance) return;
    mapChartInstance.setOption({
        title: buildMapTitle(ALL_DATES[currentDateIndex])
    }, false);
}

let bootOverlayDone = false;
let bootReadyToEnter = false;
function setBootStatus(mainText, subText) {
    const main = byId('bootStatus');
    const sub = byId('bootSub');
    if (main && mainText) main.textContent = mainText;
    if (sub && subText != null) sub.textContent = subText;
}

function showBootSlowHint() {
    const hint = byId('bootHint');
    const retry = byId('bootRetry');
    if (hint) hint.textContent = '网络较慢，仍在加载地图与数据...';
    if (retry) retry.classList.add('show');
}

function markBootReady() {
    if (bootReadyToEnter) return;
    bootReadyToEnter = true;
    const enterBtn = byId('bootEnter');
    const hint = byId('bootHint');
    byId('bootOverlay')?.classList.add('ready');
    setBootStatus('加载完成', '请点击下方按钮进入页面');
    if (hint) hint.textContent = '核心数据已就绪';
    if (enterBtn) {
        enterBtn.textContent = '进入地图';
        enterBtn.classList.add('ready');
    }
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
setBootStatus('正在装载页面框架...', '正在挂载交互控件');
byId('bootRetry')?.addEventListener('click', () => window.location.reload());
byId('bootEnter')?.addEventListener('click', () => {
    if (!bootReadyToEnter) return;
    hideBootOverlay();
});
document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && bootReadyToEnter && !bootOverlayDone) hideBootOverlay();
});

const bootSlowTimer = setTimeout(() => {
    if (!bootOverlayDone) showBootSlowHint();
}, 10000);

setTimeout(function() {
    setBootStatus('正在连接地图引擎...', '正在整理主视图布局');
    const mapWrapper = byId('mapWrapper');
    const chartDivs = document.querySelectorAll('[_echarts_instance_]');

    chartDivs.forEach(function(dom) {
        if (dom.id !== 'metricsChart') {
            mapWrapper.insertBefore(dom, mapWrapper.firstChild);
            mapChartInstance = echarts.getInstanceByDom(dom);
        }
    });

    if (!mapChartInstance) {
        setBootStatus('地图初始化失败', '未检测到地图实例，请刷新重试');
        showBootSlowHint();
        return;
    }

    setBootStatus('正在绑定地图交互...', '正在同步时间轴与缩放控制');
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
        markBootReady();
        if (finishHooked) {
            mapChartInstance.off('finished', onBootRenderFinished);
            finishHooked = false;
        }
    };
    mapChartInstance.on('finished', onBootRenderFinished);
    finishHooked = true;

    setBootStatus('正在渲染主地图...', '即将完成');
    renderMapByState();
    setTimeout(() => {
        if (!bootReadyToEnter) onBootRenderFinished();
    }, 1600);

    window.addEventListener('resize', () => {
        if (mapChartInstance) mapChartInstance.resize();
        if (metricsChart) metricsChart.resize();
        if (settlementMapChart) settlementMapChart.resize();
    });
}, 900);
"""
