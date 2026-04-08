"""
Settlement analysis panel (radius cluster + diffusion trend).
"""

from __future__ import annotations


def build_css() -> str:
    return """\
#settlementPanel {
    margin-top: 12px;
    background: #ffffff;
    border: 1px solid #dde8f5;
    border-radius: 14px;
    box-shadow: 0 2px 12px rgba(21,101,192,0.06);
    padding: 12px 14px 14px;
}
#settlementHeader {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
#settlementTitle {
    font-size: 13px;
    color: #6b8cba;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 700;
}
#settlementRadiusGroup {
    display: inline-flex;
    gap: 6px;
}
.settlement-radius-btn {
    padding: 4px 10px;
    border: 1px solid #c5d8f5;
    border-radius: 999px;
    background: #f7fbff;
    color: #3a5f8a;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
}
.settlement-radius-btn.active {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
}
#settlementMapWrap {
    position: relative;
}
#settlementMap {
    width: 100%;
    height: 360px;
    border: 1px solid #eef3fa;
    border-radius: 10px;
    overflow: hidden;
    background: #f8fbff;
}
#settlementMapLegend {
    margin-top: 6px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12px;
    color: #6b8cba;
}
#settlementLegendText {
    color: #6b8cba;
}
#settlementLegendScale {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.settlement-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 7px;
    border-radius: 999px;
    border: 1px solid #e2ebf7;
    background: #f8fbff;
    color: #56789e;
    font-size: 11px;
    white-space: nowrap;
}
.settlement-legend-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.9);
    box-shadow: 0 0 0 1px rgba(21,101,192,0.08);
    flex-shrink: 0;
}
#settlementMapControls {
    position: absolute;
    right: 10px;
    top: 10px;
    z-index: 8;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
#settlementCompareBtn {
    position: absolute;
    right: 10px;
    bottom: 10px;
    z-index: 9;
    padding: 5px 10px;
    border-radius: 999px;
    border: 1px solid #c5d8f5;
    background: rgba(255,255,255,0.95);
    color: #1565c0;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 1px 8px rgba(21,101,192,0.12);
}
#settlementCompareBtn.active {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
}
.settlement-map-btn {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    border: 1px solid #c5d8f5;
    background: rgba(255,255,255,0.94);
    color: #1565c0;
    font-size: 14px;
    font-weight: 800;
    cursor: pointer;
    box-shadow: 0 1px 8px rgba(21,101,192,0.12);
}
.settlement-map-btn:hover {
    background: #1565c0;
    border-color: #1565c0;
    color: #fff;
}
#settlementSummary {
    margin-top: 10px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 8px;
}
.settlement-kpi {
    background: #f8fbff;
    border: 1px solid #e6effa;
    border-radius: 10px;
    padding: 8px 10px;
}
.settlement-kpi .k {
    font-size: 11px;
    color: #7a9cc0;
}
.settlement-kpi .v {
    margin-top: 4px;
    font-size: 15px;
    color: #1a2a4a;
    font-weight: 800;
}
#settlementNarrative {
    margin-top: 10px;
    background: #f7fafc;
    border: 1px solid #e6eef7;
    border-radius: 10px;
    padding: 9px 10px;
    color: #4a6a8a;
    font-size: 13px;
    line-height: 1.6;
}
"""


def build_dom() -> str:
    return ""


def build_js() -> str:
    return """\
const SETTLEMENT_GEO_BASE_URL = 'https://geo.datav.aliyun.com/areas_v3/bound';
let settlementUIReady = false;
let settlementRenderToken = 0;
let settlementProvinceByCity = {};
let settlementProvinceGeoCache = {};
let settlementViewZoom = null;
let settlementViewCenter = null;
let settlementCompareMode = false;
let settlementLastCenterCity = '';
const settlementRadiusRowsCache = new Map();
const settlementDiffusionCache = new Map();
const settlementTrendCache = new Map();
const settlementBandSeriesCache = new Map();
const settlementCircleAvgCache = new Map();

function normalizeCnCityName(name) {
    if (!name) return '';
    return String(name)
        .replace(/(特别行政区|自治区|自治州|地区|盟|林区|新区|矿区)$/g, '')
        .replace(/(省|市|县|区)$/g, '')
        .trim();
}

function getChinaProvinceFeatures() {
    const mapObj = echarts.getMap && echarts.getMap('china');
    if (!mapObj) return [];
    const geoJson = mapObj.geoJson || mapObj.geoJSON || {};
    return geoJson.features || [];
}

function pointInRing(point, ring) {
    const x = point[0];
    const y = point[1];
    let inside = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        const xi = ring[i][0];
        const yi = ring[i][1];
        const xj = ring[j][0];
        const yj = ring[j][1];
        const intersect = ((yi > y) !== (yj > y))
            && (x < (xj - xi) * (y - yi) / ((yj - yi) || 1e-9) + xi);
        if (intersect) inside = !inside;
    }
    return inside;
}

function pointInPolygon(point, polygon) {
    if (!polygon || !polygon.length) return false;
    if (!pointInRing(point, polygon[0])) return false;
    for (let i = 1; i < polygon.length; i++) {
        if (pointInRing(point, polygon[i])) return false;
    }
    return true;
}

function geometryContainsPoint(geometry, point) {
    if (!geometry) return false;
    if (geometry.type === 'Polygon') return pointInPolygon(point, geometry.coordinates);
    if (geometry.type === 'MultiPolygon') {
        return geometry.coordinates.some(poly => pointInPolygon(point, poly));
    }
    return false;
}

function getCityProvince(cityName) {
    if (settlementProvinceByCity[cityName]) return settlementProvinceByCity[cityName];
    const coords = CITY_COORDS[cityName];
    if (!coords) return null;
    const features = getChinaProvinceFeatures();
    for (const feature of features) {
        if (!geometryContainsPoint(feature.geometry, coords)) continue;
        const p = feature.properties || {};
        const adcode = p.adcode || (p.parent && p.parent.adcode);
        const matched = { adcode: adcode, name: p.name || '' };
        settlementProvinceByCity[cityName] = matched;
        return matched;
    }
    return null;
}

function haversineKm(lng1, lat1, lng2, lat2) {
    const toRad = x => x * Math.PI / 180;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) ** 2
        + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
    return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function getRadiusRows(centerCity, dateStr, radiusKm) {
    const cacheKey = centerCity + '::' + dateStr + '::' + radiusKm;
    if (settlementRadiusRowsCache.has(cacheKey)) {
        return settlementRadiusRowsCache.get(cacheKey);
    }
    const center = CITY_COORDS[centerCity];
    const day = CITY_DATA_BY_DATE[dateStr] || {};
    if (!center) return [];
    const rows = [];
    for (const [city, aqiRaw] of Object.entries(day)) {
        const coords = CITY_COORDS[city];
        if (!coords || aqiRaw == null || Number.isNaN(aqiRaw)) continue;
        const distance = haversineKm(center[0], center[1], coords[0], coords[1]);
        if (distance > radiusKm) continue;
        rows.push({
            name: city,
            norm: normalizeCnCityName(city),
            lng: coords[0],
            lat: coords[1],
            aqi: Number(aqiRaw),
            distanceKm: distance,
            isCenter: city === centerCity
        });
    }
    rows.sort((a, b) => a.distanceKm - b.distanceKm);
    settlementRadiusRowsCache.set(cacheKey, rows);
    return rows;
}

function mean(values) {
    const valid = values.filter(v => v != null && !Number.isNaN(v));
    if (!valid.length) return null;
    return valid.reduce((s, v) => s + v, 0) / valid.length;
}

function describeDiffusion(centerCity, radiusKm, endIdx) {
    const cacheKey = centerCity + '::' + radiusKm + '::' + endIdx;
    if (settlementDiffusionCache.has(cacheKey)) {
        return settlementDiffusionCache.get(cacheKey);
    }
    const startIdx = Math.max(0, endIdx - 6);
    const near = [];
    const outer = [];
    for (let i = startIdx; i <= endIdx; i++) {
        const dateStr = ALL_DATES[i];
        const rows = getRadiusRows(centerCity, dateStr, radiusKm);
        if (!rows.length) {
            near.push(null);
            outer.push(null);
            continue;
        }
        const split = radiusKm / 2;
        near.push(mean(rows.filter(r => r.distanceKm <= split).map(r => r.aqi)));
        outer.push(mean(rows.filter(r => r.distanceKm > split).map(r => r.aqi)));
    }

    const nearValid = near.filter(v => v != null);
    const outerValid = outer.filter(v => v != null);
    if (!nearValid.length || !outerValid.length) {
        const result = { label: '数据不足', detail: '最近 7 天有效样本不足，暂无法判断扩散趋势。' };
        settlementDiffusionCache.set(cacheKey, result);
        return result;
    }

    const firstGap = outer[0] != null && near[0] != null ? outer[0] - near[0] : 0;
    const lastGap = outer[outer.length - 1] != null && near[near.length - 1] != null
        ? outer[outer.length - 1] - near[near.length - 1] : 0;
    const delta = lastGap - firstGap;
    if (delta > 8) {
        const result = { label: '外扩增强', detail: '外圈相对内圈上升更快，存在向外扩散迹象。' };
        settlementDiffusionCache.set(cacheKey, result);
        return result;
    }
    if (delta < -8) {
        const result = { label: '回落收敛', detail: '外圈相对内圈回落，污染影响向中心附近收敛。' };
        settlementDiffusionCache.set(cacheKey, result);
        return result;
    }
    const result = { label: '基本稳定', detail: '内外圈差值变化较小，暂无明显扩散方向。' };
    settlementDiffusionCache.set(cacheKey, result);
    return result;
}

function getSettlementTrendValues(cityName, metric, startIdx, endIdx) {
    const key = cityName + '::' + metric + '::' + startIdx + '::' + endIdx;
    if (settlementTrendCache.has(key)) {
        return settlementTrendCache.get(key);
    }
    const out = [];
    for (let i = startIdx; i <= endIdx; i++) {
        out.push(getSettlementMetricValue(ALL_DATES[i], cityName));
    }
    settlementTrendCache.set(key, out);
    return out;
}

function getSettlementBandSeries(centerCity, radiusKm, startIdx, endIdx, metric) {
    const key = centerCity + '::' + radiusKm + '::' + metric + '::' + startIdx + '::' + endIdx;
    if (settlementBandSeriesCache.has(key)) {
        return settlementBandSeriesCache.get(key);
    }
    const split = radiusKm / 2;
    const near = [];
    const outer = [];
    for (let i = startIdx; i <= endIdx; i++) {
        const rows = getRadiusRows(centerCity, ALL_DATES[i], radiusKm);
        if (!rows.length) {
            near.push(null);
            outer.push(null);
            continue;
        }
        const dateStr = ALL_DATES[i];
        const nearValues = rows
            .filter(r => r.distanceKm <= split)
            .map(r => getSettlementMetricValue(dateStr, r.name))
            .filter(v => v != null && !Number.isNaN(v));
        const outerValues = rows
            .filter(r => r.distanceKm > split)
            .map(r => getSettlementMetricValue(dateStr, r.name))
            .filter(v => v != null && !Number.isNaN(v));
        near.push(mean(nearValues));
        outer.push(mean(outerValues));
    }
    const result = { near, outer };
    settlementBandSeriesCache.set(key, result);
    return result;
}

function getSettlementCircleAvgSeries(centerCity, radiusKm, startIdx, endIdx, metric) {
    const key = centerCity + '::' + radiusKm + '::avg::' + metric + '::' + startIdx + '::' + endIdx;
    if (settlementCircleAvgCache.has(key)) {
        return settlementCircleAvgCache.get(key);
    }
    const out = [];
    for (let i = startIdx; i <= endIdx; i++) {
        const dateStr = ALL_DATES[i];
        const rows = getRadiusRows(centerCity, dateStr, radiusKm);
        const values = rows
            .map(r => getSettlementMetricValue(dateStr, r.name))
            .filter(v => v != null && !Number.isNaN(v));
        out.push(values.length ? mean(values) : null);
    }
    settlementCircleAvgCache.set(key, out);
    return out;
}

function getDefaultSettlementZoom(radiusKm) {
    return 2.6;
}

function buildCircleCoords(center, radiusKm, steps = 84) {
    if (!center) return [];
    const lng = center[0];
    const lat = center[1];
    const latScale = 1 / 111;
    const lngScale = 1 / (111 * Math.max(0.2, Math.cos(lat * Math.PI / 180)));
    const out = [];
    for (let i = 0; i <= steps; i++) {
        const t = (i / steps) * Math.PI * 2;
        const dLat = Math.sin(t) * radiusKm * latScale;
        const dLng = Math.cos(t) * radiusKm * lngScale;
        out.push([lng + dLng, lat + dLat]);
    }
    return out;
}

async function fetchProvinceCityBoundaries(provinceAdcode) {
    if (!provinceAdcode) return [];
    if (settlementProvinceGeoCache[provinceAdcode]) {
        return settlementProvinceGeoCache[provinceAdcode];
    }

    const urls = [
        `${SETTLEMENT_GEO_BASE_URL}/${provinceAdcode}_full.json`,
        `${SETTLEMENT_GEO_BASE_URL}/${provinceAdcode}.json`
    ];
    for (const url of urls) {
        try {
            const resp = await fetch(url);
            if (!resp.ok) continue;
            const geo = await resp.json();
            const features = (geo.features || []).filter(f => {
                const lv = (f.properties || {}).level;
                return lv === 'city' || lv === 'province';
            });
            if (features.length) {
                settlementProvinceGeoCache[provinceAdcode] = features;
                return features;
            }
        } catch (err) {}
    }

    settlementProvinceGeoCache[provinceAdcode] = [];
    return [];
}

function ensureSettlementUI() {
    if (settlementUIReady) return;
    const panel = document.getElementById('settlementPanelHost') || document.getElementById('chartPanel');
    if (!panel) return;

    const host = document.createElement('div');
    host.id = 'settlementPanel';
    host.style.display = 'none';
    host.innerHTML = `
        <div id="settlementHeader">
            <div id="settlementTitle">聚落分析（半径圈）</div>
            <div id="settlementRadiusGroup">
                <button class="settlement-radius-btn" data-r="80">80km</button>
                <button class="settlement-radius-btn active" data-r="120">120km</button>
                <button class="settlement-radius-btn" data-r="180">180km</button>
            </div>
        </div>
        <div id="settlementMapWrap">
            <div id="settlementMapControls">
                <button class="settlement-map-btn" id="settlementZoomIn" title="放大">+</button>
                <button class="settlement-map-btn" id="settlementZoomOut" title="缩小">-</button>
                <button class="settlement-map-btn" id="settlementZoomReset" title="重置视图">R</button>
            </div>
            <button id="settlementCompareBtn" title="切换聚落对比折线">对比</button>
            <div id="settlementMap"></div>
        </div>
        <div id="settlementMapLegend">
            <div id="settlementLegendText">颜色按当前指标分级；蓝色虚线圈为分析半径。</div>
            <div id="settlementLegendScale"></div>
        </div>
        <div id="settlementSummary"></div>
        <div id="settlementNarrative">--</div>
    `;
    panel.appendChild(host);

    host.querySelectorAll('.settlement-radius-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            host.querySelectorAll('.settlement-radius-btn').forEach(x => x.classList.remove('active'));
            btn.classList.add('active');
            settlementRadiusKm = parseInt(btn.dataset.r, 10);
            settlementViewZoom = null;
            settlementViewCenter = null;
            if (settlementCompareMode && typeof updateCityPanel === 'function') {
                updateCityPanel();
            } else {
                renderSettlementAnalysis();
            }
            if (typeof refreshAIInsightPanel === 'function') {
                refreshAIInsightPanel();
            }
        });
    });

    host.querySelector('#settlementZoomIn')?.addEventListener('click', () => {
        if (!settlementMapChart) return;
        settlementViewZoom = (settlementViewZoom || getDefaultSettlementZoom(settlementRadiusKm)) * 1.25;
        applySettlementView();
    });
    host.querySelector('#settlementZoomOut')?.addEventListener('click', () => {
        if (!settlementMapChart) return;
        settlementViewZoom = (settlementViewZoom || getDefaultSettlementZoom(settlementRadiusKm)) / 1.25;
        applySettlementView();
    });
    host.querySelector('#settlementZoomReset')?.addEventListener('click', () => {
        settlementViewZoom = null;
        settlementViewCenter = null;
        renderSettlementAnalysis();
    });
    host.querySelector('#settlementCompareBtn')?.addEventListener('click', () => {
        settlementCompareMode = !settlementCompareMode;
        if (typeof updateCityPanel === 'function') {
            updateCityPanel();
        } else {
            renderSettlementAnalysis();
        }
    });

    window.addEventListener('resize', () => {
        syncTwinPanelHeights();
        if (metricsChart) metricsChart.resize();
        if (settlementMapChart) settlementMapChart.resize();
    });

    settlementUIReady = true;
    renderSettlementLegendScale();
}

function setSettlementLayoutVisible(visible) {
    const grid = document.getElementById('analysisTwinGrid');
    const host = document.getElementById('settlementPanelHost');
    if (grid) {
        grid.classList.toggle('settlement-visible', !!visible);
    }
    if (host) {
        host.style.display = visible ? 'block' : 'none';
    }
    setTimeout(() => {
        syncTwinPanelHeights();
        if (metricsChart) metricsChart.resize();
        if (settlementMapChart) settlementMapChart.resize();
    }, 40);
}

function syncTwinPanelHeights() {
    const grid = document.getElementById('analysisTwinGrid');
    const metricsCard = document.getElementById('metricsCard');
    const metricsDom = document.getElementById('metricsChart');
    const titleEl = document.getElementById('chartPanelTitle');
    const settlementPanel = document.getElementById('settlementPanel');
    if (!grid || !metricsCard || !metricsDom) return;
    const isSideBySide = grid.classList.contains('settlement-visible') && window.innerWidth > 1199;
    if (!isSideBySide || !settlementPanel) {
        metricsCard.style.height = '';
        metricsDom.style.height = '';
        return;
    }
    const rightHeight = settlementPanel.offsetHeight || 0;
    if (!rightHeight) return;
    const titleHeight = titleEl ? titleEl.offsetHeight : 0;
    const verticalPadding = 34;
    const chartHeight = Math.max(300, rightHeight - titleHeight - verticalPadding);
    metricsCard.style.height = rightHeight + 'px';
    metricsDom.style.height = chartHeight + 'px';
}

function applySettlementView() {
    if (!settlementMapChart) return;
    if (settlementViewZoom == null || !settlementViewCenter) return;
    settlementMapChart.setOption({
        geo: {
            zoom: Math.max(2.6, Math.min(11.5, settlementViewZoom)),
            center: settlementViewCenter
        }
    }, false);
}

function getSettlementMetricValue(dateStr, cityName) {
    if (selectedMetric === 'AQI') {
        return CITY_DATA_BY_DATE[dateStr]?.[cityName] ?? null;
    }
    return POLLUTANTS_DATA[dateStr]?.[cityName]?.[selectedMetric] ?? null;
}

function renderSettlementCompareInMainChart() {
    if (!currentCityName || !metricsChart) return;
    const dateStr = ALL_DATES[currentDateIndex];
    const rows = getRadiusRows(currentCityName, dateStr, settlementRadiusKm);
    if (!rows.length) {
        metricsChart.clear();
        document.getElementById('chartPanelTitle').textContent = '聚落对比图 - 当前半径无可用城市';
        return;
    }

    const selectedRows = rows;

    const endIdx = currentDateIndex;
    const startIdx = Math.max(0, endIdx - 6);
    const dates = ALL_DATES.slice(startIdx, endIdx + 1);
    const xLabels = dates.map(d => fmtDate(d).substring(5));
    const metricName = typeof compareMetricLabel === 'function'
        ? compareMetricLabel(selectedMetric)
        : (typeof metricLabel === 'function' ? metricLabel(selectedMetric) : selectedMetric);
    document.getElementById('chartPanelTitle').textContent =
        `聚落内城市对比（${selectedRows.length}城，近7日 ${metricName}）`;

    const cityCount = selectedRows.length;
    const labelFontSize = typeof getCompareLabelFontSize === 'function'
        ? getCompareLabelFontSize(cityCount)
        : 10;
    const seriesEntries = selectedRows.map((row, idx) => {
        const color = row.isCenter ? '#111827' : COMPARE_PALETTE[idx % COMPARE_PALETTE.length];
        const values = getSettlementTrendValues(row.name, selectedMetric, startIdx, endIdx);
        return {
            name: row.name,
            color: color,
            values: values,
            meta: typeof getCompareLabelMeta === 'function'
                ? getCompareLabelMeta(values)
                : { first: 0, last: values.length - 1, max: -1, min: -1, mid: 0, validCount: values.length }
        };
    });
    const layoutMap = typeof buildDateLabelLayoutMap === 'function'
        ? buildDateLabelLayoutMap(seriesEntries, cityCount)
        : {};
    const series = seriesEntries.map(entry => ({
        name: entry.name,
        type: 'line',
        data: typeof buildCompareSeriesData === 'function'
            ? buildCompareSeriesData(entry, cityCount, layoutMap)
            : entry.values,
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
    const bandSeries = getSettlementBandSeries(currentCityName, settlementRadiusKm, startIdx, endIdx, selectedMetric);
    series.push({
        name: '中心圈均值',
        type: 'line',
        data: bandSeries.near,
        smooth: true,
        connectNulls: false,
        symbolSize: 6,
        lineStyle: { color: '#1f2937', width: 2, type: 'dashed' },
        itemStyle: { color: '#1f2937' },
        label: { show: false }
    });
    series.push({
        name: '外圈均值',
        type: 'line',
        data: bandSeries.outer,
        smooth: true,
        connectNulls: false,
        symbolSize: 6,
        lineStyle: { color: '#64748b', width: 2, type: 'dashed' },
        itemStyle: { color: '#64748b' },
        label: { show: false }
    });

    metricsChart.setOption({
        backgroundColor: 'transparent',
        legend: {
            type: 'scroll',
            data: selectedRows.map(r => r.name).concat(['中心圈均值', '外圈均值']),
            bottom: 0,
            textStyle: { color: '#6b8cba', fontSize: Math.max(10, labelFontSize + 1) },
            itemWidth: 14,
            itemHeight: 8
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255,255,255,0.96)',
            borderColor: '#c5d8f5',
            borderWidth: 1,
            textStyle: { color: '#1a2a4a' },
            formatter: params => {
                let out = '<b>' + fmtDate(dates[params[0].dataIndex]) + '</b><br/>';
                params.forEach(p => {
                    out += '<span style="color:' + p.color + '">●</span> ' + p.seriesName
                        + ': <b>' + (p.value != null ? p.value : '--') + '</b><br/>';
                });
                return out;
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
            name: metricName,
            nameTextStyle: { color: '#aac4d8', fontSize: Math.max(10, labelFontSize + 1) },
            axisLabel: { color: '#7a9cc0', fontSize: Math.max(10, labelFontSize + 1) },
            axisLine: { show: true, lineStyle: { color: '#dde8f5' } },
            splitLine: { lineStyle: { color: '#eef3fa', type: 'dashed' } }
        },
        series: series
    }, true);

    setTimeout(() => {
        if (metricsChart) metricsChart.resize();
    }, 40);
}

function getSettlementMetricColor(metric, value) {
    if (value == null || Number.isNaN(value)) return '#dbe7f3';
    const levels = getSettlementPollutantThresholds()[metric];
    if (!levels) return getAQIColor(value);
    const colors = getSettlementLevelColors();
    for (let i = 0; i < levels.length; i++) {
        if (value <= levels[i]) return colors[i];
    }
    return colors[colors.length - 1];
}

function getSettlementPollutantThresholds() {
    return {
        'PM2.5_24h': [35, 75, 115, 150, 250],
        'PM10_24h': [50, 150, 250, 350, 420],
        'SO2_24h': [50, 150, 475, 800, 1600],
        'NO2_24h': [40, 80, 180, 280, 565],
        'O3_8h': [100, 160, 215, 265, 800],
        'O3_8h_24h': [100, 160, 215, 265, 800]
    };
}

function getSettlementLevelColors() {
    if (typeof POLLUTANT_COLOR_LEVELS !== 'undefined' && Array.isArray(POLLUTANT_COLOR_LEVELS) && POLLUTANT_COLOR_LEVELS.length >= 6) {
        return POLLUTANT_COLOR_LEVELS.slice(0, 6);
    }
    return ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#99004c', '#7e0023'];
}

function getSettlementLegendPieces(metric) {
    const colors = getSettlementLevelColors();
    if (metric === 'AQI') {
        return [
            { label: '优', range: '0-50', color: colors[0] },
            { label: '良', range: '51-100', color: colors[1] },
            { label: '轻度', range: '101-150', color: colors[2] },
            { label: '中度', range: '151-200', color: colors[3] },
            { label: '重度', range: '201-300', color: colors[4] },
            { label: '严重', range: '>300', color: colors[5] }
        ];
    }
    const th = getSettlementPollutantThresholds()[metric];
    if (!th || th.length < 5) return [];
    return [
        { label: '优', range: `0-${th[0]}`, color: colors[0] },
        { label: '良', range: `${th[0] + 1}-${th[1]}`, color: colors[1] },
        { label: '轻度', range: `${th[1] + 1}-${th[2]}`, color: colors[2] },
        { label: '中度', range: `${th[2] + 1}-${th[3]}`, color: colors[3] },
        { label: '重度', range: `${th[3] + 1}-${th[4]}`, color: colors[4] },
        { label: '严重', range: `>${th[4]}`, color: colors[5] }
    ];
}

function renderSettlementLegendScale() {
    const textEl = document.getElementById('settlementLegendText');
    const scaleEl = document.getElementById('settlementLegendScale');
    if (!textEl || !scaleEl) return;
    const metric = selectedMetric === 'AQI' ? 'AQI' : selectedMetric;
    const metricName = (typeof compareMetricLabel === 'function')
        ? compareMetricLabel(metric)
        : ((typeof metricLabel === 'function') ? metricLabel(metric) : metric);
    textEl.textContent = `颜色按当前指标分级（${metricName}）；蓝色虚线圈为分析半径。`;
    const pieces = getSettlementLegendPieces(metric);
    scaleEl.innerHTML = pieces.map(p =>
        `<span class="settlement-legend-item" title="${metricName} ${p.label} ${p.range}">`
        + `<span class="settlement-legend-dot" style="background:${p.color};"></span>`
        + `<span>${p.label} ${p.range}</span></span>`
    ).join('');
}

function updateSettlementSummary(rows, diffusion, centerCity, radiusKm, endIdx) {
    const el = document.getElementById('settlementSummary');
    const narrative = document.getElementById('settlementNarrative');
    if (!el || !narrative) return;

    const dateStr = ALL_DATES[endIdx];
    const metricName = typeof compareMetricLabel === 'function'
        ? compareMetricLabel(selectedMetric)
        : (typeof metricLabel === 'function' ? metricLabel(selectedMetric) : selectedMetric);
    const metricRows = rows
        .map(r => ({ name: r.name, value: getSettlementMetricValue(dateStr, r.name) }))
        .filter(r => r.value != null && !Number.isNaN(r.value));
    const avg = mean(metricRows.map(r => r.value));
    const count = rows.length;
    const startIdx = Math.max(0, endIdx - 6);
    const avg7d = getSettlementCircleAvgSeries(centerCity, radiusKm, startIdx, endIdx, selectedMetric);
    const todayAvg = avg7d[avg7d.length - 1];
    const prevAvg = avg7d.length > 1 ? avg7d[avg7d.length - 2] : null;
    const circleDelta = (todayAvg != null && prevAvg != null) ? (todayAvg - prevAvg) : null;
    const centerToday = getSettlementMetricValue(ALL_DATES[endIdx], centerCity);
    const centerPrev = endIdx > 0 ? getSettlementMetricValue(ALL_DATES[endIdx - 1], centerCity) : null;
    const centerDelta = (centerToday != null && centerPrev != null) ? (centerToday - centerPrev) : null;
    let slope = null;
    const valid = avg7d
        .map((v, i) => ({ v, i }))
        .filter(p => p.v != null && !Number.isNaN(p.v));
    if (valid.length >= 2) {
        const first = valid[0];
        const last = valid[valid.length - 1];
        slope = (last.v - first.v) / Math.max(1, last.i - first.i);
    }
    const circleDeltaText = circleDelta == null ? '--' : `${circleDelta >= 0 ? '+' : ''}${circleDelta.toFixed(1)}`;
    const centerDeltaText = centerDelta == null ? '--' : `${centerDelta >= 0 ? '+' : ''}${centerDelta.toFixed(1)}`;
    const slopeText = slope == null ? '--' : `${slope >= 0 ? '+' : ''}${slope.toFixed(2)} /天`;
    const peakMetric = metricRows.length
        ? metricRows.reduce((m, r) => r.value > m.value ? r : m, metricRows[0])
        : null;

    el.innerHTML = `
        <div class="settlement-kpi"><div class="k">圈内城市数</div><div class="v">${count}</div></div>
        <div class="settlement-kpi"><div class="k">圈内平均 ${metricName}</div><div class="v">${avg != null ? avg.toFixed(1) : '--'}</div></div>
        <div class="settlement-kpi"><div class="k">峰值城市</div><div class="v">${peakMetric ? peakMetric.name + ' ' + peakMetric.value : '--'}</div></div>
        <div class="settlement-kpi"><div class="k">中心城较昨日</div><div class="v">${centerDeltaText}</div></div>
        <div class="settlement-kpi"><div class="k">圈均较昨日</div><div class="v">${circleDeltaText}</div></div>
        <div class="settlement-kpi"><div class="k">圈均7日斜率</div><div class="v">${slopeText}</div></div>
    `;

    narrative.innerHTML = `<b>${diffusion.label}</b>：${diffusion.detail}`;
}

function buildSettlementGeoRegions(features, rows, dateStr) {
    const rowByNorm = {};
    rows.forEach(row => { rowByNorm[row.norm] = row; });
    return features.map(feature => {
        const name = (feature.properties || {}).name || '';
        const norm = normalizeCnCityName(name);
        const row = rowByNorm[norm];
        if (!row) {
            return {
                name: name,
                itemStyle: {
                    areaColor: '#eef4fa',
                    borderColor: '#bfd1e3',
                    borderWidth: 0.8
                },
                emphasis: {
                    itemStyle: {
                        areaColor: '#e5eef7',
                        borderColor: '#9eb7d1',
                        borderWidth: 1.0
                    }
                }
            };
        }
        const metricValue = getSettlementMetricValue(dateStr, row.name);
        const fillColor = getSettlementMetricColor(selectedMetric, metricValue);
        return {
            name: name,
            itemStyle: {
                areaColor: fillColor,
                borderColor: '#bfd1e3',
                borderWidth: 0.9
            },
            emphasis: {
                itemStyle: {
                    areaColor: fillColor,
                    borderColor: '#9eb7d1',
                    borderWidth: 1.1
                }
            }
        };
    });
}

async function renderSettlementMiniMap(centerCity, dateStr, rows) {
    const mapDom = document.getElementById('settlementMap');
    if (!mapDom || !rows.length) return;
    if (!settlementMapChart) {
        settlementMapChart = echarts.init(mapDom, null, { renderer: 'canvas' });
        settlementMapChart.on('georoam', () => {
            try {
                const opt = settlementMapChart.getOption();
                const geo = opt.geo && opt.geo[0];
                if (!geo) return;
                if (geo.zoom != null) settlementViewZoom = geo.zoom;
                if (geo.center) settlementViewCenter = geo.center;
            } catch (err) {}
        });
    }

    const token = ++settlementRenderToken;
    const provinces = new Map();
    rows.forEach(row => {
        const p = getCityProvince(row.name);
        if (p && p.adcode) provinces.set(p.adcode, p);
    });

    const provinceFeatures = (await Promise.all(
        Array.from(provinces.keys()).map(code => fetchProvinceCityBoundaries(code))
    )).flat();
    if (token !== settlementRenderToken) return;

    const center = CITY_COORDS[centerCity];
    if (!center) return;

    let mapName = 'china';
    let regions = [];
    if (provinceFeatures.length) {
        mapName = 'settlement_city_map';
        echarts.registerMap(mapName, { type: 'FeatureCollection', features: provinceFeatures });
        regions = buildSettlementGeoRegions(provinceFeatures, rows, dateStr);
    }

    if (settlementViewCenter == null) {
        settlementViewCenter = center;
    }
    if (settlementViewZoom == null) {
        settlementViewZoom = getDefaultSettlementZoom(settlementRadiusKm);
    }

    const circleCoords = buildCircleCoords(center, settlementRadiusKm);
    const rowByName = {};
    rows.forEach(row => { rowByName[row.name] = row; });

    settlementMapChart.setOption({
        animation: false,
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255,255,255,0.97)',
            borderColor: '#c5d8f5',
            borderWidth: 1,
            textStyle: { color: '#1a2a4a' },
            formatter: params => {
                const n = params.name || '';
                const row = rowByName[n];
                if (row) {
                    const metricName = typeof compareMetricLabel === 'function'
                        ? compareMetricLabel(selectedMetric)
                        : selectedMetric;
                    const metricValue = getSettlementMetricValue(dateStr, row.name);
                    return `<b>${n}</b><br/>${metricName}: <b>${metricValue ?? '--'}</b><br/>距中心: <b>${row.distanceKm.toFixed(1)} km</b>`;
                }
                if (params.seriesType === 'lines') {
                    return `半径圈：${settlementRadiusKm} km`;
                }
                if (params.seriesType === 'scatter' && n === centerCity) {
                    return `<b>${centerCity}</b><br/>分析中心城市`;
                }
                return `<b>${n}</b>`;
            }
        },
        geo: {
            map: mapName,
            roam: true,
            zoom: Math.max(2.6, Math.min(11.5, settlementViewZoom)),
            center: settlementViewCenter,
            layoutCenter: ['50%', '50%'],
            layoutSize: '96%',
            aspectScale: 0.92,
            scaleLimit: { min: 2.4, max: 12 },
            itemStyle: {
                areaColor: '#eef4fa',
                borderColor: '#bfd1e3',
                borderWidth: 0.9
            },
            emphasis: {
                itemStyle: {
                    areaColor: '#e5eef7',
                    borderColor: '#8fa7c0',
                    borderWidth: 1.1
                },
                label: { show: false }
            },
            label: { show: false },
            regions: regions
        },
        series: [
            {
                type: 'lines',
                coordinateSystem: 'geo',
                polyline: true,
                data: [{ coords: circleCoords }],
                lineStyle: {
                    color: 'rgba(37,99,235,0.45)',
                    width: 1.4,
                    type: 'dashed'
                },
                silent: true,
                zlevel: 2
            },
            {
                type: 'scatter',
                coordinateSystem: 'geo',
                data: rows.map(r => ({
                    name: r.name,
                    value: [r.lng, r.lat, r.aqi],
                    itemStyle: {
                        color: r.isCenter ? '#0f172a' : '#0ea5e9',
                        borderColor: '#ffffff',
                        borderWidth: 1.4
                    },
                    symbolSize: r.isCenter ? 12 : 8
                })),
                emphasis: { scale: false },
                zlevel: 3
            },
            {
                type: 'scatter',
                coordinateSystem: 'geo',
                data: [{
                    name: centerCity,
                    value: [center[0], center[1], 0]
                }],
                label: {
                    show: true,
                    formatter: '{b}',
                    position: 'right',
                    color: '#0f172a',
                    fontSize: 12,
                    fontWeight: 700,
                    backgroundColor: 'rgba(255,255,255,0.85)',
                    borderColor: '#dbe7f5',
                    borderWidth: 1,
                    borderRadius: 6,
                    padding: [2, 6]
                },
                itemStyle: {
                    color: '#0f172a',
                    borderColor: '#ffffff',
                    borderWidth: 1.8
                },
                symbolSize: 13,
                emphasis: { scale: false },
                zlevel: 4
            }
        ]
    }, true);
    syncTwinPanelHeights();
}

function hideSettlementPanel() {
    ensureSettlementUI();
    const panel = document.getElementById('settlementPanel');
    if (panel) panel.style.display = 'none';
    setSettlementLayoutVisible(false);
}

function onSettlementModeChange() {
    renderSettlementAnalysis();
}

function getCurrentSettlementSnapshot() {
    if (!currentCityName) return null;
    const endIdx = currentDateIndex;
    const startIdx = Math.max(0, endIdx - 6);
    const dateStr = ALL_DATES[endIdx];
    const rows = getRadiusRows(currentCityName, dateStr, settlementRadiusKm);
    if (!rows.length) return null;

    const split = settlementRadiusKm / 2;
    const inValues = rows
        .filter(r => r.distanceKm <= split)
        .map(r => getSettlementMetricValue(dateStr, r.name))
        .filter(v => v != null && !Number.isNaN(v));
    const outValues = rows
        .filter(r => r.distanceKm > split)
        .map(r => getSettlementMetricValue(dateStr, r.name))
        .filter(v => v != null && !Number.isNaN(v));

    const avg7d = getSettlementCircleAvgSeries(currentCityName, settlementRadiusKm, startIdx, endIdx, selectedMetric);
    const todayAvg = avg7d[avg7d.length - 1];
    const prevAvg = avg7d.length > 1 ? avg7d[avg7d.length - 2] : null;
    const delta = (todayAvg != null && prevAvg != null) ? (todayAvg - prevAvg) : null;

    let slope = null;
    const valid = avg7d.map((v, i) => ({ v, i })).filter(p => p.v != null && !Number.isNaN(p.v));
    if (valid.length >= 2) {
        slope = (valid[valid.length - 1].v - valid[0].v) / Math.max(1, valid[valid.length - 1].i - valid[0].i);
    }

    const band = getSettlementBandSeries(currentCityName, settlementRadiusKm, startIdx, endIdx, selectedMetric);
    const history = [];
    for (let i = startIdx; i <= endIdx; i++) {
        history.push({
            date: ALL_DATES[i],
            in_avg: band.near[i - startIdx],
            out_avg: band.outer[i - startIdx],
            circle_avg: avg7d[i - startIdx]
        });
    }

    const diffusion = describeDiffusion(currentCityName, settlementRadiusKm, endIdx);
    return {
        in_count: rows.length,
        in_avg: mean(inValues),
        out_avg: mean(outValues),
        delta_day: delta,
        slope_7d: slope,
        diffusion_label: diffusion.label,
        diffusion_detail: diffusion.detail,
        history: history
    };
}

async function renderSettlementAnalysis() {
    ensureSettlementUI();
    const panel = document.getElementById('settlementPanel');
    if (!panel) return;

    if (compareMode || !currentCityName) {
        panel.style.display = 'none';
        settlementCompareMode = false;
        setSettlementLayoutVisible(false);
        return;
    }
    panel.style.display = 'block';
    setSettlementLayoutVisible(true);
    renderSettlementLegendScale();
    if (settlementLastCenterCity !== currentCityName) {
        settlementLastCenterCity = currentCityName;
        settlementViewZoom = null;
        settlementViewCenter = null;
    }
    const compareBtn = document.getElementById('settlementCompareBtn');
    compareBtn?.classList.toggle('active', settlementCompareMode);

    const dateStr = ALL_DATES[currentDateIndex];
    const rows = getRadiusRows(currentCityName, dateStr, settlementRadiusKm);
    const diffusion = describeDiffusion(currentCityName, settlementRadiusKm, currentDateIndex);
    updateSettlementSummary(rows, diffusion, currentCityName, settlementRadiusKm, currentDateIndex);

    if (!rows.length) {
        const narrative = document.getElementById('settlementNarrative');
        if (narrative) narrative.textContent = '当前半径内暂无可用城市样本。';
        if (settlementMapChart) settlementMapChart.clear();
        settlementCompareMode = false;
        return;
    }
    await renderSettlementMiniMap(currentCityName, dateStr, rows);
}
"""


