"""
Unified client-side map renderer helpers.
"""

from __future__ import annotations


def build_js() -> str:
    return """\
function getAQIPieces() {
    return [
        { min: 0, max: 50, label: t('label.excellent'), color: '#00e400' },
        { min: 51, max: 100, label: t('label.good'), color: '#ffff00' },
        { min: 101, max: 150, label: t('label.light'), color: '#ff7e00' },
        { min: 151, max: 200, label: t('label.moderate'), color: '#ff0000' },
        { min: 201, max: 300, label: t('label.heavy'), color: '#99004c' },
        { min: 301, label: t('label.severe'), color: '#7e0023' }
    ];
}

function buildMapSubtitle(dateStr) {
    const label = fmtDate(dateStr);
    if (compareMode) {
        return t('app.subtitle.compare').replace('{date}', label);
    }
    return t('app.subtitle.normal').replace('{date}', label);
}

function buildMapTitle(dateStr) {
    return {
        text: t('app.title'),
        subtext: buildMapSubtitle(dateStr),
        left: 'center',
        top: '12px',
        textStyle: {
            fontSize: 24,
            fontWeight: 'bold',
            color: '#1565c0'
        },
        subtextStyle: {
            fontSize: 13,
            color: '#555'
        }
    };
}

function buildBaseGeoOption(dateStr) {
    return {
        map: 'china',
        roam: true,
        zoom: currentZoom,
        center: currentCenter,
        layoutCenter: ['50%', '53%'],
        layoutSize: '116%',
        aspectScale: 0.92,
        scaleLimit: {
            min: 0.8,
            max: 8
        },
        itemStyle: {
            areaColor: '#dde8f0',
            borderColor: '#aac4d8',
            borderWidth: 0.8
        },
        emphasis: {
            itemStyle: { areaColor: '#cfe0ef' },
            label: { show: false }
        },
        label: { show: false },
        regions: []
    };
}

function buildNormalMapSeries(dateStr) {
    const day = CITY_DATA_BY_DATE[dateStr] || {};
    const data = [];

    for (const [city, aqi] of Object.entries(day)) {
        const coords = CITY_COORDS[city];
        if (!coords) continue;
        const isSelected = city === currentCityName;
        data.push({
            name: city,
            value: [coords[0], coords[1], aqi],
            itemStyle: {
                color: getAQIColor(aqi),
                opacity: isSelected ? 1 : 0.86,
                borderColor: isSelected ? '#ffffff' : 'transparent',
                borderWidth: isSelected ? 2.5 : 0,
                shadowBlur: isSelected ? 18 : 0,
                shadowColor: isSelected ? 'rgba(255,255,255,0.7)' : 'transparent'
            },
            symbolSize: isSelected ? 18 : 10
        });
    }

    return [{
        type: 'scatter',
        coordinateSystem: 'geo',
        data: data,
        zlevel: 2
    }];
}

function buildMapVisualMap(dateStr) {
    if (compareMode) {
        return {
            show: false
        };
    }

    return {
        show: true,
        type: 'piecewise',
        pieces: getAQIPieces(),
        orient: 'vertical',
        pos_right: '1%',
        pos_top: '18%',
        itemWidth: 26,
        itemHeight: 18,
        textStyle: { color: '#4b6584', fontSize: 11 },
        seriesIndex: 0
    };
}

function buildMapTooltip(dateStr) {
    return {
        trigger: 'item',
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#c5d8f5',
        borderWidth: 1,
        textStyle: { color: '#1a2a4a' },
        extraCssText: 'box-shadow:0 4px 16px rgba(21,101,192,0.12);border-radius:10px;',
        formatter: function(params) {
            let cityName = params.name;
            let aqi = '--';
            if (Array.isArray(params.value) && params.value.length > 2) {
                aqi = params.value[2];
            } else if (typeof params.value === 'number') {
                aqi = params.value;
            }

            const info = typeof aqi === 'number' ? getAQIInfo(aqi) : null;
            const color = typeof aqi === 'number' ? getAQIColor(aqi) : '#94a3b8';
            return '<b style="font-size:14px;color:#1a2a4a">' + cityName + '</b><br/>'
                + '<span style="color:' + color + '">●</span> AQI: <b style="color:' + color + ';font-size:15px">' + aqi + '</b>'
                + (info ? '<br/>等级: <b>' + info.level + '</b>' : '')
                + '<br/><span style="font-size:11px;color:#7a9cc0">' + fmtDate(dateStr) + '</span>';
        }
    };
}

let mapRenderPending = false;
function renderMapByStateNow() {
    if (!mapChartInstance) return;
    const dateStr = ALL_DATES[currentDateIndex];
    let option;

    if (compareMode && typeof buildCompareMapOption === 'function') {
        option = buildCompareMapOption(dateStr);
    } else {
        option = {
            title: buildMapTitle(dateStr),
            geo: buildBaseGeoOption(dateStr),
            tooltip: buildMapTooltip(dateStr),
            visualMap: buildMapVisualMap(dateStr),
            series: buildNormalMapSeries(dateStr)
        };
    }

    mapChartInstance.setOption(option, true);
}

function renderMapByState(forceNow) {
    if (forceNow) {
        mapRenderPending = false;
        renderMapByStateNow();
        return;
    }
    if (mapRenderPending) return;
    mapRenderPending = true;
    requestAnimationFrame(() => {
        mapRenderPending = false;
        renderMapByStateNow();
    });
}
"""
