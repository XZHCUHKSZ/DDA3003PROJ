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
    font-size: 12px;
    color: #6b8cba;
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
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
    return rows;
}

function mean(values) {
    const valid = values.filter(v => v != null && !Number.isNaN(v));
    if (!valid.length) return null;
    return valid.reduce((s, v) => s + v, 0) / valid.length;
}

function describeDiffusion(centerCity, radiusKm, endIdx) {
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
        return { label: '数据不足', detail: '最近 7 天有效样本不足，暂无法判断扩散趋势。' };
    }

    const firstGap = outer[0] != null && near[0] != null ? outer[0] - near[0] : 0;
    const lastGap = outer[outer.length - 1] != null && near[near.length - 1] != null
        ? outer[outer.length - 1] - near[near.length - 1] : 0;
    const delta = lastGap - firstGap;
    if (delta > 8) {
        return { label: '外扩增强', detail: '外圈相对内圈上升更快，存在向外扩散迹象。' };
    }
    if (delta < -8) {
        return { label: '回落收敛', detail: '外圈相对内圈回落，污染影响向中心附近收敛。' };
    }
    return { label: '基本稳定', detail: '内外圈差值变化较小，暂无明显扩散方向。' };
}

function getDefaultSettlementZoom(radiusKm) {
    if (radiusKm <= 80) return 7.0;
    if (radiusKm <= 120) return 6.4;
    if (radiusKm <= 180) return 5.8;
    return 5.2;
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
    const panel = document.getElementById('chartPanel');
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
        <div id="settlementMapLegend">颜色沿用主图 AQI 分级；粗边框表示半径圈内地级市；蓝色虚线圈为分析半径。</div>
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

    settlementUIReady = true;
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
        const values = dates.map(d => getSettlementMetricValue(d, row.name));
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

    metricsChart.setOption({
        backgroundColor: 'transparent',
        legend: {
            type: 'scroll',
            data: selectedRows.map(r => r.name),
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

function updateSettlementSummary(rows, diffusion) {
    const el = document.getElementById('settlementSummary');
    const narrative = document.getElementById('settlementNarrative');
    if (!el || !narrative) return;

    const avg = mean(rows.map(r => r.aqi));
    const peak = rows.length ? rows.reduce((m, r) => r.aqi > m.aqi ? r : m, rows[0]) : null;
    const count = rows.length;

    el.innerHTML = `
        <div class="settlement-kpi"><div class="k">圈内城市数</div><div class="v">${count}</div></div>
        <div class="settlement-kpi"><div class="k">圈内平均 AQI</div><div class="v">${avg != null ? avg.toFixed(1) : '--'}</div></div>
        <div class="settlement-kpi"><div class="k">峰值城市</div><div class="v">${peak ? peak.name + ' ' + peak.aqi : '--'}</div></div>
    `;

    narrative.innerHTML = `<b>${diffusion.label}</b>：${diffusion.detail}`;
}

function buildSettlementGeoRegions(features, rows) {
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
        return {
            name: name,
            itemStyle: {
                areaColor: getAQIColor(row.aqi),
                borderColor: '#213a57',
                borderWidth: 2.0
            },
            emphasis: {
                itemStyle: {
                    areaColor: getAQIColor(row.aqi),
                    borderColor: '#0f2238',
                    borderWidth: 2.4
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
        regions = buildSettlementGeoRegions(provinceFeatures, rows);
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
                    return `<b>${n}</b><br/>AQI: <b>${row.aqi}</b><br/>距中心: <b>${row.distanceKm.toFixed(1)} km</b>`;
                }
                if (params.seriesType === 'lines') {
                    return `半径圈：${settlementRadiusKm} km`;
                }
                if (params.seriesType === 'scatter' && n === centerCity) {
                    return `<b>${centerCity}</b><br/>鍒嗘瀽涓績鍩庡競`;
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
                    color: '#2563eb',
                    width: 2,
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
}

function hideSettlementPanel() {
    ensureSettlementUI();
    const panel = document.getElementById('settlementPanel');
    if (panel) panel.style.display = 'none';
}

function onSettlementModeChange() {
    renderSettlementAnalysis();
}

async function renderSettlementAnalysis() {
    ensureSettlementUI();
    const panel = document.getElementById('settlementPanel');
    if (!panel) return;

    if (compareMode || !currentCityName) {
        panel.style.display = 'none';
        settlementCompareMode = false;
        return;
    }
    panel.style.display = 'block';
    const compareBtn = document.getElementById('settlementCompareBtn');
    compareBtn?.classList.toggle('active', settlementCompareMode);

    const dateStr = ALL_DATES[currentDateIndex];
    const rows = getRadiusRows(currentCityName, dateStr, settlementRadiusKm);
    const diffusion = describeDiffusion(currentCityName, settlementRadiusKm, currentDateIndex);
    updateSettlementSummary(rows, diffusion);

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


