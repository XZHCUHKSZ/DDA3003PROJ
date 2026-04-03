"""
Compare mode module.
"""

from __future__ import annotations


def build_css() -> str:
    return """\
#compareBtn {
    position: absolute;
    right: 14px;
    top: 14px;
    z-index: 500;
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    color: #3b1a6e;
    border: 1.5px solid rgba(124,58,237,0.18);
    border-radius: 12px;
    padding: 9px 18px 9px 13px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(124,58,237,0.1), 0 1px 4px rgba(0,0,0,0.08);
    display: inline-flex;
    align-items: center;
    gap: 7px;
    transition: all 0.22s;
    letter-spacing: 0.2px;
}
#compareBtn .btn-icon {
    width: 24px;
    height: 24px;
    border-radius: 7px;
    background: linear-gradient(135deg, #7c3aed, #a78bfa);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
    box-shadow: 0 2px 6px rgba(124,58,237,0.3);
}
#compareBtn:hover {
    background: rgba(255,255,255,0.97);
    border-color: rgba(124,58,237,0.4);
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(124,58,237,0.2);
}
#compareBtn.active {
    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 20px rgba(124,58,237,0.45);
}
#compareBtn.active .btn-icon {
    background: rgba(255,255,255,0.22);
    box-shadow: none;
}

#compareListPanel {
    flex: 0 0 320px;
    padding: 16px 16px 16px 8px;
    display: none;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;
    max-height: 520px;
}
.compare-city-item {
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
    border-radius: 12px;
    border: 1px solid #dde8f5;
    padding: 10px 14px;
    box-shadow: 0 2px 8px rgba(21,101,192,0.05);
}
.compare-city-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 6px currentColor;
}
.compare-city-name {
    font-size: 14px;
    font-weight: 700;
    color: #1a2a4a;
    flex: 1;
}
.compare-city-aqi {
    font-size: 13px;
    font-weight: 700;
}
.compare-city-remove {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #f0f4f8;
    border: 1px solid #dde8f5;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #7a9cc0;
    flex-shrink: 0;
    transition: all 0.15s;
}
.compare-city-remove:hover {
    background: #fee;
    border-color: #f87171;
    color: #dc2626;
}
#compareEmptyHint {
    text-align: center;
    color: #aac4d8;
    font-size: 13px;
    padding: 24px 0;
}
"""


def build_js() -> str:
    return """\
function compareMetricLabel(metric) {
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

function getCompareLabelFontSize(cityCount) {
    if (cityCount <= 4) return 10;
    if (cityCount <= 7) return 9;
    return 8;
}

function getCompareLabelMeta(values) {
    const validIndexes = [];
    values.forEach((value, index) => {
        if (value != null) validIndexes.push(index);
    });

    if (validIndexes.length === 0) {
        return { first: -1, last: -1, max: -1, min: -1, mid: -1, validCount: 0 };
    }

    let maxIdx = validIndexes[0];
    let minIdx = validIndexes[0];
    validIndexes.forEach(index => {
        if (values[index] > values[maxIdx]) maxIdx = index;
        if (values[index] < values[minIdx]) minIdx = index;
    });

    return {
        first: validIndexes[0],
        last: validIndexes[validIndexes.length - 1],
        max: maxIdx,
        min: minIdx,
        mid: validIndexes[Math.floor(validIndexes.length / 2)],
        validCount: validIndexes.length
    };
}

function getCompareLabelPriority(index, meta) {
    if (index === meta.last) return 4;
    if (index === meta.max || index === meta.min) return 3;
    if (index === meta.first) return 2;
    if (index === meta.mid) return 1;
    return 0;
}

function shouldShowCompareLabel(index, value, meta, cityCount) {
    if (value == null) return false;
    const priority = getCompareLabelPriority(index, meta);
    if (cityCount <= 4) return true;
    if (cityCount <= 7) return priority >= 2 || meta.validCount <= 4;
    return priority >= 3;
}

function buildDateLabelLayoutMap(seriesEntries, cityCount) {
    const layoutMap = {};
    const baseGap = cityCount <= 4 ? 6 : cityCount <= 7 ? 8 : 10;
    if (seriesEntries.length === 0) return layoutMap;

    const pointCount = seriesEntries[0].values.length;
    for (let dateIndex = 0; dateIndex < pointCount; dateIndex++) {
        const visibleItems = [];
        seriesEntries.forEach((entry, cityIndex) => {
            const value = entry.values[dateIndex];
            const meta = entry.meta;
            if (!shouldShowCompareLabel(dateIndex, value, meta, cityCount)) return;
            visibleItems.push({
                cityName: entry.name,
                cityIndex: cityIndex,
                value: value,
                priority: getCompareLabelPriority(dateIndex, meta)
            });
        });

        visibleItems.sort((a, b) => {
            if (b.value !== a.value) return b.value - a.value;
            if (b.priority !== a.priority) return b.priority - a.priority;
            return a.cityIndex - b.cityIndex;
        });

        visibleItems.forEach((item, orderIndex) => {
            const tier = Math.floor(orderIndex / 2);
            const placeTop = orderIndex % 2 === 0;
            const offsetY = (tier + 1) * baseGap * (placeTop ? -1 : 1);
            layoutMap[item.cityName + '::' + dateIndex] = {
                position: placeTop ? 'top' : 'bottom',
                offsetY: offsetY
            };
        });
    }
    return layoutMap;
}

function buildCompareSeriesData(entry, cityCount, layoutMap) {
    const fontSize = getCompareLabelFontSize(cityCount);
    return entry.values.map((value, index) => {
        const priority = getCompareLabelPriority(index, entry.meta);
        const showLabel = shouldShowCompareLabel(index, value, entry.meta, cityCount);
        const layout = layoutMap[entry.name + '::' + index] || {
            position: priority >= 3 ? 'top' : 'bottom',
            offsetY: priority >= 3 ? -6 : 6
        };

        return {
            value: value,
            labelPriority: priority,
            itemStyle: {
                color: entry.color,
                borderWidth: 2.5,
                borderColor: 'white'
            },
            label: {
                show: showLabel,
                position: layout.position,
                offset: [0, layout.offsetY],
                color: '#1a2a4a',
                fontSize: Math.max(7, fontSize - (priority === 0 ? 1 : 0)),
                fontWeight: priority >= 3 ? 'bold' : 600,
                formatter: p => p.value != null ? p.value : '',
                backgroundColor: priority >= 3 ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.78)',
                borderRadius: 4,
                padding: cityCount <= 4 ? [2, 5] : [1, 4],
                borderColor: priority >= 3 ? entry.color : '#dde8f5',
                borderWidth: priority >= 3 ? 1.2 : 1
            }
        };
    });
}

function enterCompareMode() {
    compareMode = true;
    mapMode = 'compare';
    const btn = document.getElementById('compareBtn');
    const label = document.getElementById('compareBtnLabel');
    const listPanel = document.getElementById('compareListPanel');
    const detailPanel = document.getElementById('cityDetailPanel');

    btn.classList.add('active');
    label.textContent = '退出对比';
    document.getElementById('infoPlaceholder').style.display = 'none';
    document.getElementById('infoHeaderContent').style.display = 'flex';
    document.getElementById('infoBody').style.display = 'flex';
    document.getElementById('filterBar').style.display = 'flex';
    document.getElementById('selectedCityBadge').textContent = '多城市对比';
    document.getElementById('aqiBadge').textContent = '';
    document.getElementById('aqiBadge').style.background = 'transparent';
    document.getElementById('levelBadge').textContent = '';
    listPanel.style.display = 'flex';
    detailPanel.style.display = 'none';

    if (currentCityName && !compareList.find(c => c.name === currentCityName)) {
        compareList.push({
            name: currentCityName,
            color: COMPARE_PALETTE[compareList.length % COMPARE_PALETTE.length]
        });
    }

    renderCompareList();
    renderCompareChart();
    renderMapByState();
    if (typeof onSettlementModeChange === 'function') onSettlementModeChange();
    setTimeout(() => {
        document.getElementById('infoSection')?.scrollIntoView({ behavior: 'smooth' });
    }, 80);
}

function exitCompareMode(skipRender) {
    compareMode = false;
    mapMode = 'normal';
    compareList = [];

    const btn = document.getElementById('compareBtn');
    const label = document.getElementById('compareBtnLabel');
    const listPanel = document.getElementById('compareListPanel');
    const detailPanel = document.getElementById('cityDetailPanel');

    btn.classList.remove('active');
    label.textContent = '对比模式';
    listPanel.style.display = 'none';
    detailPanel.style.display = 'flex';

    if (currentCityName) {
        document.getElementById('selectedCityBadge').textContent = currentCityName;
        updateCityPanel();
    } else {
        document.getElementById('infoPlaceholder').style.display = 'block';
        document.getElementById('infoHeaderContent').style.display = 'none';
        document.getElementById('infoBody').style.display = 'none';
        document.getElementById('filterBar').style.display = 'none';
    }

    if (!skipRender) {
        renderMapByState();
    }
    if (typeof onSettlementModeChange === 'function') onSettlementModeChange();
}

function toggleCompareMode() {
    if (compareMode) {
        exitCompareMode(false);
    } else {
        enterCompareMode();
    }
}

function renderCompareList() {
    const panel = document.getElementById('compareListPanel');
    const hint = document.getElementById('compareEmptyHint');
    panel.querySelectorAll('.compare-city-item').forEach(el => el.remove());

    if (compareList.length === 0) {
        hint.style.display = 'block';
        return;
    }

    hint.style.display = 'none';
    const dateStr = ALL_DATES[currentDateIndex];
    compareList.forEach((entry, idx) => {
        const aqi = CITY_DATA_BY_DATE[dateStr]?.[entry.name];
        const item = document.createElement('div');
        item.className = 'compare-city-item';
        item.innerHTML = `
            <div class="compare-city-dot" style="background:${entry.color};box-shadow:0 0 8px ${entry.color};"></div>
            <span class="compare-city-name">${entry.name}</span>
            <span class="compare-city-aqi" style="color:${aqi != null ? getAQIColor(aqi) : '#aaa'}">${aqi != null ? 'AQI ' + aqi : '--'}</span>
            <button class="compare-city-remove" onclick="removeCompareCity(${idx})">x</button>
        `;
        panel.appendChild(item);
    });
}

function removeCompareCity(idx) {
    compareList.splice(idx, 1);
    renderCompareList();
    renderCompareChart();
    renderMapByState();
}

function buildCompareMapOption(dateStr) {
    const day = CITY_DATA_BY_DATE[dateStr] || {};
    const mapData = [];
    for (const [city, aqi] of Object.entries(day)) {
        const coords = CITY_COORDS[city];
        if (!coords) continue;
        const index = compareList.findIndex(item => item.name === city);
        const selected = index >= 0;
        mapData.push({
            name: city,
            value: [coords[0], coords[1], aqi],
            itemStyle: {
                color: selected ? compareList[index].color : getAQIColor(aqi),
                opacity: selected ? 1 : 0.42,
                borderColor: selected ? '#ffffff' : 'transparent',
                borderWidth: selected ? 2.5 : 0,
                shadowBlur: selected ? 20 : 0,
                shadowColor: selected ? compareList[index].color : 'transparent'
            },
            symbolSize: selected ? 20 : 9
        });
    }

    return {
        title: buildMapTitle(dateStr),
        geo: buildBaseGeoOption(dateStr),
        tooltip: buildMapTooltip(dateStr),
        visualMap: { show: false },
        series: [{
            type: 'scatter',
            coordinateSystem: 'geo',
            data: mapData,
            zlevel: 2
        }]
    };
}

function renderCompareChart() {
    const chartDom = document.getElementById('metricsChart');
    if (!chartDom) return;
    if (!metricsChart) {
        metricsChart = echarts.init(chartDom, null, { renderer: 'canvas' });
    }

    if (compareList.length === 0) {
        metricsChart.clear();
        document.getElementById('chartPanelTitle').textContent = '对比图表 - 请选择城市';
        return;
    }

    const endIdx = currentDateIndex;
    const startIdx = Math.max(0, endIdx - 6);
    const dates = ALL_DATES.slice(startIdx, endIdx + 1);
    const xLabels = dates.map(d => fmtDate(d).substring(5));
    const name = compareMetricLabel(selectedMetric);
    const cityCount = compareList.length;
    const labelFontSize = getCompareLabelFontSize(cityCount);

    const seriesEntries = compareList.map(entry => {
        const values = dates.map(d => {
            if (selectedMetric === 'AQI') return CITY_DATA_BY_DATE[d]?.[entry.name] ?? null;
            return POLLUTANTS_DATA[d]?.[entry.name]?.[selectedMetric] ?? null;
        });
        return {
            name: entry.name,
            color: entry.color,
            values: values,
            meta: getCompareLabelMeta(values)
        };
    });

    const layoutMap = buildDateLabelLayoutMap(seriesEntries, cityCount);
    const series = seriesEntries.map(entry => ({
        name: entry.name,
        type: 'line',
        data: buildCompareSeriesData(entry, cityCount, layoutMap),
        smooth: true,
        connectNulls: false,
        lineStyle: { color: entry.color, width: 2.5 },
        symbolSize: 10,
        emphasis: { focus: 'series' },
        labelLayout: params => ({
            moveOverlap: 'shiftY',
            hideOverlap: cityCount > 7 && params.data && params.data.labelPriority < 3
        })
    }));

    document.getElementById('chartPanelTitle').textContent = name + ' 多城市对比（近7日）';
    metricsChart.setOption({
        backgroundColor: 'transparent',
        legend: {
            data: compareList.map(c => c.name),
            bottom: 0,
            textStyle: { color: '#6b8cba', fontSize: 11 },
            itemWidth: 14,
            itemHeight: 8
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.96)',
            borderColor: '#c5d8f5',
            borderWidth: 1,
            textStyle: { color: '#1a2a4a' },
            extraCssText: 'box-shadow:0 4px 16px rgba(21,101,192,0.12);border-radius:10px;',
            formatter: params => {
                let output = '<b style="color:#1a2a4a">' + fmtDate(dates[params[0].dataIndex]) + '</b><br/>';
                params.forEach(p => {
                    const color = compareList.find(c => c.name === p.seriesName)?.color || '#888';
                    output += '<span style="color:' + color + '">●</span> ' + p.seriesName
                        + ': <b style="color:' + color + '">' + (p.value != null ? p.value : '--') + '</b><br/>';
                });
                return output;
            }
        },
        grid: { left: 10, right: 16, bottom: 48, top: 20, containLabel: true },
        xAxis: {
            type: 'category',
            data: xLabels,
            axisLabel: { color: '#7a9cc0', fontSize: labelFontSize + 2 },
            axisLine: { lineStyle: { color: '#dde8f5' } },
            axisTick: { lineStyle: { color: '#dde8f5' } }
        },
        yAxis: {
            type: 'value',
            name: name,
            nameTextStyle: { color: '#aac4d8', fontSize: Math.max(10, labelFontSize + 1) },
            axisLabel: { color: '#7a9cc0', fontSize: Math.max(10, labelFontSize + 1) },
            axisLine: { show: true, lineStyle: { color: '#dde8f5' } },
            splitLine: { lineStyle: { color: '#eef3fa', type: 'dashed' } }
        },
        series: series
    }, true);

    setTimeout(() => {
        if (metricsChart) metricsChart.resize();
    }, 50);
}
"""
