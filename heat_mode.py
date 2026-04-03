"""
Heat mode controls for the unified map renderer.
"""

from __future__ import annotations


def build_css() -> str:
    return """\
#heatToolbar {
    position: absolute;
    left: 14px;
    top: 198px;
    z-index: 500;
    display: none;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    border-radius: 14px;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(21,101,192,0.12);
    box-shadow: 0 4px 18px rgba(21,101,192,0.12);
}
#heatToolbar.open {
    display: flex;
}
#heatToolbarTitle {
    font-size: 11px;
    color: #7a9cc0;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.heat-view-btn {
    min-width: 112px;
    padding: 7px 12px;
    border-radius: 10px;
    border: 1px solid #c5d8f5;
    background: #f8fbff;
    color: #45678f;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
}
.heat-view-btn:hover {
    background: #e9f2fd;
    border-color: #8bb7e4;
    color: #1565c0;
}
.heat-view-btn.active {
    background: linear-gradient(135deg, #1565c0, #1e88e5);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 14px rgba(21,101,192,0.24);
}
"""


def build_dom() -> str:
    return """\
<div id="heatToolbar">
    <div id="heatToolbarTitle">热力视图</div>
    <button class="heat-view-btn active" data-heat-view="city_heat" onclick="setHeatView('city_heat')">城市热力</button>
    <button class="heat-view-btn" data-heat-view="province_fill" onclick="setHeatView('province_fill')">省域填色</button>
</div>
"""


def build_js() -> str:
    return """\
function syncHeatToolbar() {
    const toolbar = document.getElementById('heatToolbar');
    const btn = document.getElementById('heatmapBtn');
    const label = document.getElementById('heatBtnLabel');
    const isHeat = mapMode === 'heat';

    toolbar?.classList.toggle('open', isHeat);
    btn?.classList.toggle('active', isHeat);
    if (label) {
        label.textContent = isHeat ? '退出热力模式' : '热力模式';
    }

    document.querySelectorAll('.heat-view-btn').forEach(item => {
        item.classList.toggle('active', item.dataset.heatView === heatView);
    });
}

function exitHeatMode(skipRender) {
    if (mapMode !== 'heat') return;
    mapMode = 'normal';
    heatView = 'city_heat';
    syncHeatToolbar();
    if (!skipRender) renderMapByState();
}

function toggleHeatMode() {
    if (mapMode === 'heat') {
        exitHeatMode(false);
        return;
    }

    if (compareMode && typeof exitCompareMode === 'function') {
        exitCompareMode(true);
    }
    compareMode = false;
    mapMode = 'heat';
    syncHeatToolbar();
    renderMapByState();
}

function setHeatView(view) {
    heatView = view;
    mapMode = 'heat';
    syncHeatToolbar();
    renderMapByState();
}
"""
