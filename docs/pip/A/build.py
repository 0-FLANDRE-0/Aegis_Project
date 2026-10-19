"""PIP_A from pinned MAP_A. No sensor/physics/save code patches."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
H=Path(__file__).resolve().parent
BASE_SHA='68c13d352c3e80ab8bae1e08138ee42284c426f7fb7cce24e9d64941b34362b5'
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def patch(s):
 def one(a,b):
  nonlocal s
  assert s.count(a)==1,a[:120];s=s.replace(a,b,1)
 def function(name,new):
  # Source boundaries exported by the Acorn audit, preserved with this builder.
  old=(H/'legacy-drawing'/f'{name}.js').read_text();one(old,new)
 one("const ctx = canvas.getContext('2d', { alpha: false });","let ctx = canvas.getContext('2d', { alpha: false });\nlet pipRenderContextA=null; // Synchronous presentation context; always restored in finally.")
 one('minKm:390*.42/(6*3.8)','minKm:.1')
 one("reference:'Legacy pixel-zoom distance union over the seven VP_A review sizes; presentation only'","reference:'PIP_A: user minimum 0.1 km; previous maximum preserved; presentation only'")
 one('function vpUpdateMapZoomA(){mapZoom=AEGIS_VIEWPORT.twoD.shortSide*.42/(tacticalViewKm*WORLD_UNITS_PER_KM);return mapZoom;}','function vpUpdateMapZoomA(){const v=pipRenderContextA?.rect??AEGIS_VIEWPORT.twoD;mapZoom=v.shortSide*.42/(tacticalViewKm*WORLD_UNITS_PER_KM);return mapZoom;}')
 function('worldToScreen',"function worldToScreen(x,y,view=pipRenderContextA){const v=view?.rect??AEGIS_VIEWPORT.twoD,z=view?v.shortSide*.42/(view.km*WORLD_UNITS_PER_KM):vpUpdateMapZoomA(),c=view?.center??{x:aircraft.x()+camOffset.x,y:aircraft.y()+camOffset.y};return {x:v.cx+(x-c.x)*z,y:v.cy+(y-c.y)*z};}")
 function('screenToWorld',"function screenToWorld(x,y,view=pipRenderContextA){const v=view?.rect??AEGIS_VIEWPORT.twoD,z=view?v.shortSide*.42/(view.km*WORLD_UNITS_PER_KM):vpUpdateMapZoomA(),c=view?.center??{x:aircraft.x()+camOffset.x,y:aircraft.y()+camOffset.y};return {x:c.x+(x-v.cx)/z,y:c.y+(y-v.cy)/z};}")
 one('const TACTICAL_ZOOM_KM = [300, 120, 40, 15];','const TACTICAL_ZOOM_KM = [300, 120, 40, 15, 5, 2, 1, .5];')
 one("if(e.deltaY > 0){\n    // Zoom out: next larger view\n    if(tacticalZoomIdx > 0) setTacticalZoom(tacticalZoomIdx - 1);\n  } else {\n    // Zoom in: next smaller view\n    if(tacticalZoomIdx < TACTICAL_ZOOM_KM.length - 1) setTacticalZoom(tacticalZoomIdx + 1);\n  }", "const next=window.__PIP_A__?.nextDistance(tacticalViewKm,e.deltaY>0?'OUT':'IN')??tacticalViewKm;if(next!==tacticalViewKm)setTacticalZoom(TACTICAL_ZOOM_KM.indexOf(next));")
 function('tacticalViewportWorldBounds',"function tacticalViewportWorldBounds(rw,rh){const v=pipRenderContextA?.rect??AEGIS_VIEWPORT.twoD,a=screenToWorld(v.x,v.y),b=screenToWorld(v.x+v.w,v.y+v.h);return {minX:a.x,maxX:b.x,minY:a.y,maxY:b.y};}")
 one("const txt = viewKm >= 10 ? Math.round(viewKm) + 'km' : viewKm.toFixed(1) + 'km';","const txt = viewKm<1?Math.round(viewKm*1000)+' m':viewKm >= 10 ? Math.round(viewKm) + 'km' : viewKm.toFixed(1) + 'km';")
 one('const v=AEGIS_VIEWPORT.twoD,niceKm=pickNiceScaleBarKm(tacticalViewKm*.2);','const v=pipRenderContextA?.rect??AEGIS_VIEWPORT.twoD,niceKm=pickNiceScaleBarKm(tacticalViewKm*.2);')
 old=(H/'legacy-drawing/drawRadar.js').read_text()
 body=old.replace('function drawRadar(){','function pipDrawRadarPixelsA(){\n'+(H/'render-bindings.js').read_text(),1)
 body=body.replace('vpUpdateMapZoomA();const raw=AEGIS_VIEWPORT.raw,vp=AEGIS_VIEWPORT.twoD,rw=raw.w,rh=raw.h;','vpUpdateMapZoomA();const raw=pipRenderContextA.rect,vp=raw,rw=raw.w,rh=raw.h;')
 body=body.replace('    updateTacticalScaleLabel();','    // DOM scale label is updated once by the frame preparation, never here.')
 body=body.replace("const ringStep = (viewKm <= 20) ? 5 : (viewKm <= 50) ? 10 : (viewKm <= 150) ? 20 : 50;","const ringStep = viewKm<5?pickNiceScaleBarKm(viewKm/4):(viewKm <= 20) ? 5 : (viewKm <= 50) ? 10 : (viewKm <= 150) ? 20 : 50;")
 body=body.replace("ctx.fillText(r+'', 0, -rr - 3);","ctx.fillText(r<1?Math.round(r*1000)+' m':r+' km', 0, -rr-screenPxToWorld(3));")
 body=body.replace("trackTruthDomainV27(beam.trackId)??'TRACK'","tracks.get(beam.trackId)?.classification??'TRACK'")
 # Unknown enemy decoy truth endpoints were a legacy drawing leak. Keep measured RF estimates only.
 a=body.index("          } else if(m.seekerLockType==='CHAFF'){");b=body.index('\n        }\n        if(tx==null',a);body=body[:a]+'          }'+body[b:]
 body=body.replace('drawTerrainChartLayer(ctx);','pipDrawTerrainA(ctx);').replace('drawRescueRaftsCicK();drawNetworkPictureG();heloDrawMapA();','pipDrawRaftsA();pipDrawNetworkA();pipDrawHelosA();')
 body=body.replace('drawLockedTrackInfoCard(ctx,','pipDrawLockedCardA(ctx,').replace('harpoonDrawCicA(ctx,sym);','pipDrawHarpoonA(ctx,sym);').replace('ciwsWorldArcSegmentsV1(cw)','cw.chartArcs')
 body=body.replace('    drawSpySchedulerScreenOverlay(ctx,rw,rh);','    if(pipRenderContextA.target===\'MAIN\')drawSpySchedulerScreenOverlay(ctx,rw,rh);')
 # Correct legacy world-sized annotations at the newly requested close scales.
 body=body.replace("ctx.font='5px monospace';","ctx.font=`${tacticalFontWorldSize(5,4)}px monospace`;").replace("ctx.font='6px monospace';","ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;")
 body=body.replace('const hlLen = 20;','const hlLen = 20*sym;').replace('Math.max(2,majorW),Math.max(1.5,minorW)','Math.max(screenPxToWorld(2),majorW),Math.max(screenPxToWorld(1.5),minorW)').replace('Math.max(6, sigAlong), Math.max(4, sigCross)','Math.max(screenPxToWorld(6), sigAlong), Math.max(screenPxToWorld(4), sigCross)')
 body=body.replace('const s = lerp(22, 14, tq);','const s = tacticalWorldPx(lerp(22,14,tq),lerp(22,14,tq));')
 body=body.replace('drawX + 8, drawY - 6','drawX + 8*sym, drawY - 6*sym')
 one(old,body+'\n'+(H/'render.js').read_text())
 one('    drawRadar();\n    updateHud();',"    pipPrepareChartFrameA();\n    if(!WIP148_EXTERNAL_3D.isActive())drawRadar();\n    updateHud();")
 one('    requestAnimationFrame(step);\n  }',"    window.__PIP_A__?.frame(now);\n    requestAnimationFrame(step);\n  }")
 one("    drawAuxCic(st){\n      const cv=", "    drawAuxCic(st){\n      if(window.__PIP_A__)return; // DEAD_LEGACY: preserved original simplified map for comparison/recovery.\n      const cv=")
 one("if(!WIP148_EXTERNAL_3D.active&&WIP148_EXTERNAL_3D.ready&&windows.get('CIC')?.open)","if(!window.__PIP_A__&&!WIP148_EXTERNAL_3D.active&&WIP148_EXTERNAL_3D.ready&&windows.get('CIC')?.open)")
 one("createWindow('CIC','소형 전술도',mini,220,160)","createWindow('CIC','2D 전술 지도',mini,200,160)")
 one("miniWas3D=active;if(active)open('CIC',{expand:false});", "miniWas3D=active;if(active)open('CIC',{expand:false});else close(windows.get('CIC'));")
 one("q.id==='AIR'?280:q.id==='ARM'?220:180","q.id==='CIC'?200:q.id==='AIR'?280:q.id==='ARM'?220:180")
 one('c.x=b.x+8;c.y=b.y+b.h-c.h-8;',"c.x=b.x+8;c.y=b.y+b.h-c.h-8;if(c.x+c.w>b.x+b.w-Math.min(windowSize(widget)[0]*s,b.w)-8)c.y=Math.max(b.y,c.y-windowSize(widget)[1]*s-8);")
 one("(compact()?Math.min(q.minH,q.id==='AIR'?160:120):q.minH)","(q.id==='CIC'?160:compact()?Math.min(q.minH,q.id==='AIR'?160:120):q.minH)")
 # MAP_A state remains owned by its original UI IIFE; only adapters/inputs are generalized.
 a=s.index('// MAP_A_UI: independent transient operator state.')if'// MAP_A_UI: independent transient operator state.'in s else s.index('// MAP_A_UI: independent transient') if '// MAP_A_UI: independent transient'in s else s.index('// MAP_A_UI: independent')
 b=s.index('\n  completeShipStartup();',a)
 s=s[:a]+(H/'map.js').read_text()+'\n'+(H/'pip.js').read_text()+s[b:]
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=patch(decoded(h)).replace('v48_WIP_MAP_A','v48_WIP_PIP_A');z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):];i=h.index('</style>',h.index('<style id="uiStyleA">'));h=h[:i]+'\n'+(H/'pip.css').read_text()+h[i:];return h.replace('v48_WIP_MAP_A','v48_WIP_PIP_A').replace('V48_WIP_MAP_A','V48_WIP_PIP_A'),s
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();h,s=build(a.base.read_bytes());a.out.write_text(h);Path('/tmp/pip-main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))
