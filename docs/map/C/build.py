"""MAP_C: fixed MAP_B source, UI replacements only, packed-main regeneration."""
from pathlib import Path
import base64,gzip,re,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'Aegis_SIM_v48_WIP_MAP_B.html').read_bytes();assert sha(raw)=='6dfac8a6e846bc6476619d721d5113fdc638f309ef5ba0b568e0526010ed8c42';html=raw.decode();p=re.search(r'data-c55-index="13">([^<]+)</script>',html);base=gzip.decompress(base64.b64decode(p[1])).decode();main=base;changes=[]
def change(a,b):
 global main
 assert main.count(a)==1,(main.count(a),a[:160]);main=main.replace(a,b);changes.append({'anchor':a[:140],'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
# A detached presentation frame feeds shared selected-symbol/tag coordinates.
change('pipChartFrameA=frame;window.__MAP_A__?.preparePaint();','pipChartFrameA=frame;window.__MAP_C__?.prepareFrame(frame);window.__MAP_A__?.preparePaint();')
change('      const drawX = tr.x;\n      const drawY = tr.y;',"      const mapCPoint=window.__MAP_C__?.trackPoint(id,tr,pipRenderContextA);\n      const drawX = mapCPoint?.x??tr.x;\n      const drawY = mapCPoint?.y??tr.y;")
networkStart=main.index('function pipDrawNetworkA(){');networkEnd=main.index('\nfunction pipDrawRaftsA()',networkStart);networkOld=main[networkStart:networkEnd]
change(networkOld,networkOld.replace("const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y),friend=q.identity==='FRIEND'", "const mapCPoint=window.__MAP_C__?.networkPoint(q,pipRenderContextA),x=mapCPoint?.x??metersToWorld(q.positionM.x),y=mapCPoint?.y??metersToWorld(q.positionM.y),friend=q.identity==='FRIEND'"))
change("if(visible()&&(dirty||now<activeUntil||now-lastPaint>=1000/hz))paint(now);", "if(visible()&&(dirty||window.__MAP_C__?.forcePipFrames()||now<activeUntil||now-lastPaint>=1000/hz))paint(now);")
# Hit geometry follows the rendered presentation point; command records retain raw observations.
change('const p=toScreen(o.x,o.y);return {...o,distancePx:Math.hypot(x-p.x,y-p.y)};', 'const shown=window.__MAP_C__?.pointFor(o)??o,p=toScreen(shown.x,shown.y);return {...o,distancePx:Math.hypot(x-p.x,y-p.y)};')
change("const rows=picture,o=rows.find(q=>q.key===lookup),c=paintControlled;context.save();", "const rows=picture,raw=rows.find(q=>q.key===lookup),o=raw?{...raw,...(window.__MAP_C__?.pointFor(raw)??{})}:null,c=paintControlled;context.save();")
# Keep an automatically opened floating INFO window from swallowing the next cycle tap.
change('return Object.freeze({open,register(',"""return Object.freeze({open,avoidPoint(id,x,y,source=null){const q=windows.get(id);if(!q?.open||q.dock||q.maximized)return;const r=q.el.getBoundingClientRect();if(x<r.left-12||x>r.right+12||y<r.top-12||y>r.bottom+12)return;const b=bounds(),a=source??{x:x-20,y:y-20,w:40,h:40},xs=[b.x+8,b.x+b.w-q.w-8,a.x+a.w+8,a.x-q.w-8],ys=[b.y+8,b.y+b.h-q.h-8,a.y+a.h+8,a.y-q.h-8],options=[];for(const xx of xs)for(const yy of ys){const px=Math.max(b.x,Math.min(b.x+b.w-q.w,xx)),py=Math.max(b.y,Math.min(b.y+b.h-q.h,yy)),overlap=Math.max(0,Math.min(px+q.w,a.x+a.w)-Math.max(px,a.x))*Math.max(0,Math.min(py+q.h,a.y+a.h)-Math.max(py,a.y));options.push({x:px,y:py,overlap,d:(px-q.x)**2+(py-q.y)**2});}options.sort((a,b)=>a.overlap-b.overlap||a.d-b.d);q.x=options[0].x;q.y=options[0].y;clampWindow(q);persist();},register(""")
# Only an already confirmed own-launch correlation becomes a presentation boolean.
change("classification:tr.classification??tr.domain??'UNKNOWN',identity:tr.identity??'UNKNOWN',operatorIdentity:", "classification:tr.classification??tr.domain??'UNKNOWN',ownLaunchObserved:tr._harpoonOwnC?.confirmed===true,identity:tr.identity??'UNKNOWN',operatorIdentity:")
anchor=" function tap(x,y){if(!enabled&&inputSurface==='PIP'){legacyPipTap(x,y);return;}const rows=hits(x,y);if(rows.length){choose(rows,x,y);return;}"
new=""" const tapCycleC={keys:[],signature:'',at:-Infinity,x:0,y:0,surface:null,armed:false,index:-1};
 function chooseTapC(rows,x,y){const now=performance.now(),signature=pointSig(rows),armed=!!window.__MAP_B__?.snapshot().selection,same=tapCycleC.signature===signature&&tapCycleC.surface===inputSurface&&tapCycleC.armed===armed&&now-tapCycleC.at<=1500&&Math.hypot(x-tapCycleC.x,y-tapCycleC.y)<=12;
  let ordered;if(same){ordered=tapCycleC.keys.map(k=>rows.find(o=>o.key===k));tapCycleC.index=(tapCycleC.index+1)%ordered.length;}else{ordered=window.__MAP_C__?.rankCandidates(rows,armed)??rows;tapCycleC.keys=ordered.map(o=>o.key);tapCycleC.index=0;}
  Object.assign(tapCycleC,{signature,at:now,x,y,surface:inputSurface,armed});closeTransient();const chosen=ordered[tapCycleC.index];window.__MAP_C__?.cycleFeedback(tapCycleC.index+1,ordered.length,chosen.label,x,y,view().rect);show(chosen);window.__UI_A__?.avoidPoint('INFO',x,y,inputSurface==='PIP'?view().rect:null);
 }
 function tap(x,y){if(!enabled&&inputSurface==='PIP'){legacyPipTap(x,y);return;}const rows=hits(x,y);if(rows.length){chooseTapC(rows,x,y);return;}"""
change(anchor,new)
# The existing permission/queue bodies remain verbatim in the MAP_B module.
old=(R/'docs/map/B/map_b.js').read_text().replace('/* NATIVE_PREFLIGHT_COPIES */',(R/'docs/map/B/native_preview.inc.js').read_text());ui=(R/'docs/map/B/map_b.js').read_text()
ui=ui.replace("const title=el('header'),summary=el('pre')", "const title=el('header'),titleText=el('span','map-title-text-c'),tagDot=el('span','map-status-dot-c'),summary=el('pre')")
ui=ui.replace("cancel=el('button','','취소')", "cancel=el('button','','✕')")
ui=ui.replace("buttons.append(fire,cancel);pane.append(title,summary,verdict,reason,buttons);host.append(chooser,pane);", "title.append(tagDot,titleText);cancel.setAttribute('aria-label','표적 해제');cancel.title='표적 해제';reason.hidden=true;buttons.append(fire);pane.append(title,summary,verdict,reason,cancel);host.append(chooser,pane,buttons);")
ui=ui.replace("e.disabled=ready(w)<=0;}if(pending)", "e.disabled=ready(w)<=0;}window.__MAP_C__?.stabilizeInventory();if(pending)")
a=ui.index(' function refresh(force=false){');z=ui.index(' function stepCommands(){',a)
refresh=""" function refresh(force=false){const now=performance.now();if(refreshing||(!force&&now-lastAt<125))return;refreshing=true;try{lastAt=now;model=calculate();highlight();if(target&&selection){if(pane.hidden)pane.hidden=false;const d=model.d,o=d.o??target.last,tone=!model.allowed?'blocked':model.verdict==='유효'?'effective':'warning';titleText.textContent=o.label+' · '+(o.identity??'UNKNOWN');tagDot.dataset.tone=tone;
   const distance=Number.isFinite(d.rangeKm)?(d.rangeKm<1?Math.round(d.rangeKm*1000)+'m':d.rangeKm.toFixed(d.rangeKm<10?1:0)+'km'):'—';summary.textContent=labels[selection.weapon]+'×'+selection.count+' · '+model.verdict+' · '+distance;
   const displayed=({'사각지대':'사각지대 · 명중 확률 낮음','최대 사거리 구간':'최대 사거리 · 명중 확률 낮음','최소 사거리 안쪽':'최소 유효거리 안쪽 · 명중 확률 낮음'})[model.verdict]??model.verdict;verdict.textContent=tone==='blocked'?model.reason:displayed;verdict.dataset.tone=tone;verdict.hidden=tone==='effective';reason.textContent=queue?'연속 발사 중 · 남은 '+queue.remaining+'발':model.reason;fire.title=!model.allowed||queue?reason.textContent:'';
  }window.__MAP_C__?.setFireState(selection,model,queue);positionPane();
 }finally{refreshing=false;}}
 function positionPane(){window.__MAP_C__?.positionTag(target,model);}
"""
ui=ui[:a]+refresh+ui[z:]
ui=ui.replace('context.font=`${11/z}px monospace`;', 'context.font=`${9/z}px monospace`;')
ui=ui.replace('if(model.prediction&&model.d?.o){const p=', 'if(model.prediction&&model.d?.o){context.font=`${11/z}px monospace`;const p=')
ui=ui.replace("const y=r.y+16+(s.name==='고고도'?42:0)", "const y=(window.__MAP_C__?.labelBase(view)??r.y+16)+(s.name==='고고도'?42:0)")
# Check exact authority/flight dispatch preservation before assembly.
for marker,end in [(' function nativeReason(d){',' function classify('),(' function lookup(d,w){',' function nativeReason('),(' function calculate(){',' function refresh('),(' function stepCommands(){'," fire.addEventListener('click'"),(" fire.addEventListener('click'",' function draw(')]:
 a0=old.index(marker);a1=old.index(end,a0);b0=ui.index(marker);b1=ui.index(end,b0);assert old[a0:a1]==ui[b0:b1],marker
ui=ui.replace('/* NATIVE_PREFLIGHT_COPIES */',(R/'docs/map/B/native_preview.inc.js').read_text())
change(old,ui)
change('// MAP_B_UI_BEGIN', '// MAP_C_PRESENTATION_BEGIN\n'+(H/'presentation.js').read_text()+'\n// MAP_C_PRESENTATION_END\n// MAP_B_UI_BEGIN')
change('// MAP_B_UI_END\n  completeShipStartup();','// MAP_B_UI_END\nwindow.__MAP_C__.mount();\n  completeShipStartup();')
assert re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',base)[0]==re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',main)[0]
z=gzip.compress(main.encode(),9,mtime=0);html=html[:p.start(1)]+base64.b64encode(z).decode()+html[p.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
out=R/'Aegis_SIM_v48_WIP_MAP_C.html';out.write_text(html);Path('/tmp/aegis-map-c/current.js').write_text(main);(H/'engagement_ui.generated.js').write_text(ui)
q={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseCommit':'06d668abf457a8dd3a98659e3b4535ee69612612','baseHtmlSha256':sha(raw),'mainSha256':sha(main.encode()),'gameCoreWithoutEnvelopeSha256':sha(re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','',main).encode()),'envelopeBlockByteExact':True,'releaseAndGateBodiesByteExact':True,'changes':changes};(H/'build.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='changes'}))
