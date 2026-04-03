"""
独立深色热力图页（heatmap.html）生成模块。

与主地图页面无依赖，输出一个完全自包含的 HTML 文件：
深色背景 + effectScatter 动态涟漪效果 + 时间轴滑块 + 统计卡片。
"""

from __future__ import annotations

import json
from typing import Any

from constants import CITY_COORDINATES
from utils import fmt_date


def build_heatmap_html(
    aqi_by_date: dict[str, dict[str, float]],
    all_dates: list[str],
) -> str:
    """构建完整的独立热力图 HTML 字符串。

    Args:
        aqi_by_date: {date_str: {city: aqi}} 字典。
        all_dates:   升序日期字符串列表。

    Returns:
        完整 HTML 文本，可直接写入文件。
    """
    cur_idx    = len(all_dates) - 1
    cur_date   = fmt_date(all_dates[-1])
    coords_json = json.dumps({c: v for c, v in CITY_COORDINATES.items()})
    dates_json  = json.dumps(all_dates)
    data_json   = json.dumps(aqi_by_date)
    first_label = fmt_date(all_dates[0])
    last_label  = fmt_date(all_dates[-1])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全国城市AQI热力图</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html,body{{width:100%;height:100%;background:#0d1117;color:#e6edf3;font-family:'Segoe UI',sans-serif;overflow:hidden;}}
  #topBar{{position:fixed;top:0;left:0;right:0;height:56px;background:rgba(13,17,23,0.92);backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;padding:0 20px;gap:16px;z-index:1000;}}
  #backBtn{{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);color:#e6edf3;border-radius:8px;padding:6px 14px;font-size:13px;cursor:pointer;transition:all 0.2s;text-decoration:none;display:flex;align-items:center;gap:6px;}}
  #backBtn:hover{{background:rgba(255,255,255,0.15);}}
  #pageTitle{{font-size:18px;font-weight:700;color:#ff6b35;text-shadow:0 0 20px rgba(255,107,53,0.5);flex:1;}}
  #dateDisplay{{font-size:14px;color:rgba(255,255,255,0.6);background:rgba(255,107,53,0.15);border:1px solid rgba(255,107,53,0.3);border-radius:8px;padding:5px 14px;font-weight:600;}}
  #mapContainer{{position:fixed;top:56px;left:0;right:0;bottom:76px;}}
  #heatChart{{width:100%;height:100%;}}
  #controlBar{{position:fixed;bottom:0;left:0;right:0;height:76px;background:rgba(13,17,23,0.95);backdrop-filter:blur(12px);border-top:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;padding:0 20px;gap:12px;}}
  .nav-btn{{background:rgba(255,107,53,0.15);border:1px solid rgba(255,107,53,0.4);color:#ff9a76;border-radius:8px;padding:8px 14px;font-size:16px;font-weight:bold;cursor:pointer;transition:all 0.2s;flex-shrink:0;}}
  .nav-btn:hover{{background:rgba(255,107,53,0.3);}}
  .date-label{{font-size:12px;color:rgba(255,255,255,0.5);white-space:nowrap;flex-shrink:0;}}
  #heatSlider{{flex:1;height:6px;cursor:pointer;-webkit-appearance:none;appearance:none;background:rgba(255,107,53,0.25);border-radius:3px;outline:none;}}
  #heatSlider::-webkit-slider-thumb{{-webkit-appearance:none;width:18px;height:18px;background:#ff6b35;border-radius:50%;cursor:pointer;box-shadow:0 0 8px rgba(255,107,53,0.6);}}
  #currentDateLabel{{min-width:110px;text-align:center;font-size:14px;font-weight:700;color:#ff9a76;background:rgba(255,107,53,0.15);border:1px solid rgba(255,107,53,0.35);border-radius:8px;padding:6px 12px;flex-shrink:0;}}
  #legend{{position:fixed;right:20px;top:70px;background:rgba(13,17,23,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:14px 16px;z-index:500;}}
  #legend h4{{font-size:12px;color:rgba(255,255,255,0.5);margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;}}
  .legend-item{{display:flex;align-items:center;gap:8px;margin-bottom:7px;font-size:12px;}}
  .legend-dot{{width:12px;height:12px;border-radius:50%;flex-shrink:0;}}
  #statsBar{{position:fixed;left:20px;top:70px;display:flex;flex-direction:column;gap:8px;z-index:500;}}
  .stat-card{{background:rgba(13,17,23,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:10px 14px;min-width:130px;}}
  .stat-label{{font-size:11px;color:rgba(255,255,255,0.45);margin-bottom:4px;}}
  .stat-value{{font-size:22px;font-weight:700;}}
</style>
</head>
<body>
<div id="topBar">
  <a id="backBtn" href="interactive_air_quality_map.html">← 返回地图</a>
  <div id="pageTitle">🔥 全国城市AQI热力图</div>
  <div id="dateDisplay">{cur_date}</div>
</div>
<div id="mapContainer"><div id="heatChart"></div></div>
<div id="statsBar">
  <div class="stat-card"><div class="stat-label">当日城市数</div><div class="stat-value" id="statCities" style="color:#60a5fa;">--</div></div>
  <div class="stat-card"><div class="stat-label">平均AQI</div><div class="stat-value" id="statAvg" style="color:#34d399;">--</div></div>
  <div class="stat-card"><div class="stat-label">最高AQI</div><div class="stat-value" id="statMax" style="color:#f87171;">--</div></div>
  <div class="stat-card"><div class="stat-label">优良城市占比</div><div class="stat-value" id="statGood" style="color:#a78bfa;">--%</div></div>
</div>
<div id="legend">
  <h4>AQI 等级</h4>
  <div class="legend-item"><div class="legend-dot" style="background:#00e400"></div>优 (0-50)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ffff00"></div>良 (51-100)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ff7e00"></div>轻度 (101-150)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#ff0000"></div>中度 (151-200)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#99004c"></div>重度 (201-300)</div>
  <div class="legend-item"><div class="legend-dot" style="background:#7e0023"></div>严重 (>300)</div>
</div>
<div id="controlBar">
  <button class="nav-btn" id="hBtn-prev-7">&lt;&lt;</button>
  <button class="nav-btn" id="hBtn-prev-1">&lt;</button>
  <span class="date-label">{first_label}</span>
  <input type="range" id="heatSlider" min="0" max="{len(all_dates)-1}" value="{cur_idx}" step="1">
  <span class="date-label">{last_label}</span>
  <button class="nav-btn" id="hBtn-next-1">&gt;</button>
  <button class="nav-btn" id="hBtn-next-7">&gt;&gt;</button>
  <div id="currentDateLabel">{cur_date}</div>
</div>
<script>
  const ALL_DATES={dates_json},CITY_DATA={data_json},CITY_COORDS={coords_json};
  const AQI_COLORS=[{{max:50,color:'#00e400'}},{{max:100,color:'#ffff00'}},{{max:150,color:'#ff7e00'}},{{max:200,color:'#ff0000'}},{{max:300,color:'#99004c'}},{{max:9999,color:'#7e0023'}}];
  let currentIdx={cur_idx},sliderTimer=null;
  function fmtDate(d){{return d&&d.length===8?d.substring(0,4)+'-'+d.substring(4,6)+'-'+d.substring(6,8):d;}}
  function getColor(v){{for(const t of AQI_COLORS)if(v<=t.max)return t.color;return'#7e0023';}}
  const chart=echarts.init(document.getElementById('heatChart'),'dark');
  function buildData(ds){{const day=CITY_DATA[ds]||{{}};return Object.entries(day).filter(([c])=>CITY_COORDS[c]).map(([c,a])=>({{name:c,value:[CITY_COORDS[c][0],CITY_COORDS[c][1],a],itemStyle:{{color:getColor(a),opacity:0.85}}}}));}}
  function updateStats(ds){{const vals=Object.values(CITY_DATA[ds]||{{}}).filter(v=>v>0);if(!vals.length){{['statCities','statAvg','statMax','statGood'].forEach(id=>document.getElementById(id).textContent='--');return;}}document.getElementById('statCities').textContent=vals.length;document.getElementById('statAvg').textContent=(vals.reduce((a,b)=>a+b,0)/vals.length).toFixed(1);document.getElementById('statMax').textContent=Math.max(...vals);document.getElementById('statGood').textContent=((vals.filter(v=>v<=100).length/vals.length)*100).toFixed(0)+'%';}}
  function render(instant){{
    const ds = ALL_DATES[currentIdx], label = fmtDate(ds);
    document.getElementById('currentDateLabel').textContent = label;
    document.getElementById('dateDisplay').textContent = label;
    chart.setOption({{
      backgroundColor:'#0d1117',
      geo:{{
        map:'china',
        roam:true,
        zoom:1.03,
        center:[105,36],
        layoutCenter:['50%','52%'],
        layoutSize:'112%',
        aspectScale:0.9,
        scaleLimit:{{min:0.95,max:2.2}},
        itemStyle:{{areaColor:'#161b22',borderColor:'#30363d',borderWidth:0.8}},
        emphasis:{{itemStyle:{{areaColor:'#21262d'}},label:{{show:false}}}},
        label:{{show:false}}
      }},
      tooltip:{{
        trigger:'item',
        backgroundColor:'rgba(13,17,23,0.92)',
        borderColor:'rgba(255,107,53,0.4)',
        borderWidth:1,
        textStyle:{{color:'#e6edf3'}},
        formatter:function(p){{
          if(!p.name)return'';
          const a=p.value&&p.value[2]?p.value[2]:'--',col=typeof a==='number'?getColor(a):'#aaa';
          return'<b style="font-size:15px">'+p.name+'</b><br/><span style="color:'+col+'">●</span> AQI: <b style="color:'+col+';font-size:16px">'+a+'</b>';
        }}
      }},
      series:[{{
        type:'effectScatter',
        coordinateSystem:'geo',
        data:buildData(ds),
        symbolSize:function(v){{return Math.max(4,Math.min(12,4+(v[2]/300)*8));}},
        rippleEffect:{{period:4,scale:2,brushType:'fill'}},
        showEffectOn:'render',
        label:{{show:false}},
        zlevel:2
      }}]
    }},instant?true:false);
    updateStats(ds);
  }}
  fetch('https://cdn.jsdelivr.net/npm/echarts@5/map/json/china.json').then(r=>r.json()).then(g=>{{echarts.registerMap('china',g);render(true);}}).catch(()=>{{echarts.registerMap('china',{{}});render(true);}});
  document.getElementById('heatSlider').addEventListener('input',function(){{currentIdx=parseInt(this.value);document.getElementById('currentDateLabel').textContent=fmtDate(ALL_DATES[currentIdx]);document.getElementById('dateDisplay').textContent=fmtDate(ALL_DATES[currentIdx]);clearTimeout(sliderTimer);sliderTimer=setTimeout(()=>render(false),200);}});
  document.getElementById('hBtn-prev-7').addEventListener('click',()=>{{currentIdx=Math.max(0,currentIdx-7);document.getElementById('heatSlider').value=currentIdx;render(true);}});
  document.getElementById('hBtn-prev-1').addEventListener('click',()=>{{currentIdx=Math.max(0,currentIdx-1);document.getElementById('heatSlider').value=currentIdx;render(true);}});
  document.getElementById('hBtn-next-1').addEventListener('click',()=>{{currentIdx=Math.min(ALL_DATES.length-1,currentIdx+1);document.getElementById('heatSlider').value=currentIdx;render(true);}});
  document.getElementById('hBtn-next-7').addEventListener('click',()=>{{currentIdx=Math.min(ALL_DATES.length-1,currentIdx+7);document.getElementById('heatSlider').value=currentIdx;render(true);}});
  window.addEventListener('resize',()=>chart.resize());
</script>
</body>
</html>"""
