"""
Client-side heat data helpers for unified map rendering.
"""

from __future__ import annotations


def build_js() -> str:
    return """\
const HEAT_GRADIENT = ['#2dd4bf', '#84cc16', '#facc15', '#fb923c', '#ef4444', '#7f1d1d'];
let cityProvinceLookup = null;
let provinceHeatCache = {};

function getDayCityEntries(dateStr) {
    const day = CITY_DATA_BY_DATE[dateStr] || {};
    const rows = [];
    for (const [city, aqi] of Object.entries(day)) {
        const coords = CITY_COORDS[city];
        if (!coords || aqi == null || Number.isNaN(aqi)) continue;
        rows.push({
            name: city,
            lng: coords[0],
            lat: coords[1],
            aqi: Number(aqi)
        });
    }
    return rows;
}

function getHeatRange(dateStr) {
    const values = getDayCityEntries(dateStr).map(row => row.aqi);
    if (!values.length) return { min: 0, max: 300 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    return {
        min: Math.max(0, Math.floor(min)),
        max: Math.max(100, Math.ceil(max))
    };
}

function buildCityHeatScatterData(dateStr, options = {}) {
    const opacity = options.opacity == null ? 0.92 : options.opacity;
    const selectedCity = options.selectedCity || currentCityName;
    return getDayCityEntries(dateStr).map(row => {
        const isSelected = row.name === selectedCity;
        return {
            name: row.name,
            value: [row.lng, row.lat, row.aqi],
            itemStyle: {
                opacity: isSelected ? 1 : opacity,
                borderColor: isSelected ? '#ffffff' : 'rgba(255,255,255,0.45)',
                borderWidth: isSelected ? 2.4 : 1.1,
                shadowBlur: isSelected ? 18 : 0,
                shadowColor: isSelected ? 'rgba(255,255,255,0.75)' : 'transparent'
            }
        };
    });
}

function buildCityHeatEffectData(dateStr) {
    return getDayCityEntries(dateStr)
        .filter(row => row.aqi >= 150)
        .map(row => ({
            name: row.name,
            value: [row.lng, row.lat, row.aqi]
        }));
}

function getChinaMapFeatures() {
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
    if (geometry.type === 'Polygon') {
        return pointInPolygon(point, geometry.coordinates);
    }
    if (geometry.type === 'MultiPolygon') {
        return geometry.coordinates.some(polygon => pointInPolygon(point, polygon));
    }
    return false;
}

function buildCityProvinceLookup() {
    if (cityProvinceLookup) return cityProvinceLookup;

    const lookup = {};
    const features = getChinaMapFeatures();
    const cityNames = Object.keys(CITY_COORDS);

    cityNames.forEach(city => {
        const coords = CITY_COORDS[city];
        if (!coords) return;
        for (const feature of features) {
            if (geometryContainsPoint(feature.geometry, coords)) {
                const rawName = feature.properties && feature.properties.name ? feature.properties.name : '';
                lookup[city] = normalizeProvinceName(rawName);
                break;
            }
        }
    });

    cityProvinceLookup = lookup;
    return lookup;
}

function getProvinceHeatRows(dateStr) {
    if (provinceHeatCache[dateStr]) return provinceHeatCache[dateStr];

    const lookup = buildCityProvinceLookup();
    const rows = getDayCityEntries(dateStr);
    const grouped = {};

    rows.forEach(row => {
        const province = lookup[row.name];
        if (!province) return;
        if (!grouped[province]) {
            grouped[province] = {
                name: province,
                sum: 0,
                count: 0,
                max: 0
            };
        }
        grouped[province].sum += row.aqi;
        grouped[province].count += 1;
        grouped[province].max = Math.max(grouped[province].max, row.aqi);
    });

    const result = Object.values(grouped).map(group => ({
        name: group.name,
        avg: +(group.sum / group.count).toFixed(1),
        count: group.count,
        max: group.max
    }));

    provinceHeatCache[dateStr] = result;
    return result;
}

function interpolateHeatColor(start, end, ratio) {
    const a = parseInt(start.slice(1), 16);
    const b = parseInt(end.slice(1), 16);
    const ar = (a >> 16) & 255;
    const ag = (a >> 8) & 255;
    const ab = a & 255;
    const br = (b >> 16) & 255;
    const bg = (b >> 8) & 255;
    const bb = b & 255;
    const rr = Math.round(ar + (br - ar) * ratio);
    const rg = Math.round(ag + (bg - ag) * ratio);
    const rb = Math.round(ab + (bb - ab) * ratio);
    return '#' + [rr, rg, rb].map(v => v.toString(16).padStart(2, '0')).join('');
}

function getContinuousHeatColor(value, min, max) {
    if (max <= min) return HEAT_GRADIENT[HEAT_GRADIENT.length - 1];
    const ratio = Math.max(0, Math.min(1, (value - min) / (max - min)));
    const scaled = ratio * (HEAT_GRADIENT.length - 1);
    const leftIndex = Math.floor(scaled);
    const rightIndex = Math.min(HEAT_GRADIENT.length - 1, leftIndex + 1);
    const innerRatio = scaled - leftIndex;
    return interpolateHeatColor(HEAT_GRADIENT[leftIndex], HEAT_GRADIENT[rightIndex], innerRatio);
}

function buildProvinceRegions(dateStr) {
    const rows = getProvinceHeatRows(dateStr);
    if (!rows.length) return [];
    const values = rows.map(row => row.avg);
    const min = Math.min(...values);
    const max = Math.max(...values);
    return rows.map(row => ({
        name: row.name,
        itemStyle: {
            areaColor: getContinuousHeatColor(row.avg, min, max),
            borderColor: '#9eb7d3',
            borderWidth: 1
        },
        emphasis: {
            itemStyle: {
                areaColor: getContinuousHeatColor(row.avg, min, max),
                borderColor: '#4f78a7',
                borderWidth: 1.3
            }
        }
    }));
}
"""
