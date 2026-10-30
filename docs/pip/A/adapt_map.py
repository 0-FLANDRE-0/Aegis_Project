"""Share MAP_A's UI state and command functions; introduce only viewport/input adapters."""
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];s=(R/'docs/map/A/map.js').read_text()
def one(a,b):
 global s
 assert s.count(a)==1,a[:100];s=s.replace(a,b,1)
one("const additions=new Map(),counts=", "let inputSurface='MAIN',inputElement=canvas,paintControlled=null,selectionRevision=0,lastSelectionKey='',candidateContext=null;\n const surfaces=new Map([[canvas,'MAIN']]);\n function view(){return inputSurface==='PIP'?window.__PIP_A__.view():{target:'MAIN',rect:AEGIS_VIEWPORT.twoD,km:tacticalViewKm,center:{x:aircraft.x()+camOffset.x,y:aircraft.y()+camOffset.y}};}\n function toScreen(x,y){return worldToScreen(x,y,view());}function fromScreen(x,y){return screenToWorld(x,y,view());}\n function setCenter(c,detach=true){if(inputSurface==='PIP')window.__PIP_A__.setCenter(c,detach);else{camOffset.x=c.x-aircraft.x();camOffset.y=c.y-aircraft.y();}}\n function setDistance(km){if(inputSurface==='PIP')window.__PIP_A__.setDistance(km);else{tacticalViewKm=clamp(km,VP_TACTICAL_DISTANCE_A.minKm,VP_TACTICAL_DISTANCE_A.maxKm);vpUpdateMapZoomA();updateTacticalScaleLabel();}}\n function notifyInput(){if(inputSurface==='PIP')window.__PIP_A__?.invalidate();}\n const additions=new Map(),counts=")
one('worldToScreen(own.x,own.y),worldToScreen(own.x+Math.cos(o.bearingRad)*r,own.y+Math.sin(o.bearingRad)*r)','toScreen(own.x,own.y),toScreen(own.x+Math.cos(o.bearingRad)*r,own.y+Math.sin(o.bearingRad)*r)')
one('Math.min(currentTacticalViewKm(),90));return','Math.min(view().km,90));return')
one('function hits(x,y){const v=AEGIS_VIEWPORT.twoD;', 'function hits(x,y){const v=view().rect;')
one("return {...o,distancePx:segmentDistance(x,y,a,b)};", "return {...o,distancePx:Math.hypot(x-a.x,y-a.y)<=40?Infinity:segmentDistance(x,y,{x:a.x+(b.x-a.x)*Math.min(1,40/Math.max(1e-9,Math.hypot(b.x-a.x,b.y-a.y))),y:a.y+(b.y-a.y)*Math.min(1,40/Math.max(1e-9,Math.hypot(b.x-a.x,b.y-a.y)))},b)};")
one('const p=worldToScreen(o.x,o.y);return {...o,distancePx:', 'const p=toScreen(o.x,o.y);return {...o,distancePx:')
one('function refresh(force=false){const t=', "function refresh(force=false){const selectionKey=JSON.stringify([lookup,controlled,currentTool(),firingTarget]);if(selectionKey!==lastSelectionKey){lastSelectionKey=selectionKey;selectionRevision++;window.__PIP_A__?.invalidate();}const t=")
one('function place(node,x,y){const v=AEGIS_VIEWPORT.twoD,', "function place(node,x,y){const v=inputSurface==='PIP'?AEGIS_VIEWPORT.threeD:AEGIS_VIEWPORT.twoD,")
one("candidates.replaceChildren(el('strong','','겹친 객체 선택'));for(const o of rows)", "candidateContext={rows:rows.map(o=>({...o})),surface:inputSurface,x,y};candidates.replaceChildren(el('strong','','겹친 객체 선택'));const zoomReason=rows.filter(o=>Number.isFinite(o.x)&&Number.isFinite(o.y)).length<2?'위치 있는 후보 2개 필요':'';candidates.append(action('확대',()=>{const saved=inputSurface;inputSurface=candidateContext.surface;const result=window.__PIP_A__.expand(candidateContext.surface,candidateContext.rows);let note=candidates.querySelector('.map-expand-note-a');if(!note){note=el('small','map-expand-note-a');candidates.append(note);}note.textContent=result.message;place(candidates,candidateContext.x,candidateContext.y);inputSurface=saved;return result;},zoomReason,'mapExpandPipA'));for(const o of rows)")
one('const p=screenToWorld(x,y),base=controlObject()', 'const p=fromScreen(x,y),base=controlObject()')
one('camOffset.x=p.x-aircraft.x();camOffset.y=p.y-aircraft.y();','setCenter(p);')
one("function tap(x,y){const rows=hits(x,y);", "function legacyPipTap(x,y){const p=fromScreen(x,y),worldX=p.x,worldY=p.y,ax=aircraft.x(),ay=aircraft.y();if(controlDeckActiveTabWip13C==='AIR')heloMapTapA(worldX,worldY);else if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET')harpoonRouteAddE(worldX,worldY);else if(inputMode==='NAV')addWaypoint(worldX,worldY);else if(inputMode==='AIM'){lockCursor.nx=clamp((worldX-ax)/lockCursor.rx,-1,1);lockCursor.ny=clamp((worldY-ay)/lockCursor.ry,-1,1);lockCursor.x=ax+lockCursor.nx*lockCursor.rx;lockCursor.y=ay+lockCursor.ny*lockCursor.ry;}}\n function tap(x,y){if(!enabled&&inputSurface==='PIP'){legacyPipTap(x,y);return;}const rows=hits(x,y);")
one('const p=screenToWorld(x,y);append(p.x,p.y);','const p=fromScreen(x,y);append(p.x,p.y);')
one('try{canvas.releasePointerCapture(id);}', 'try{inputElement.releasePointerCapture(id);}')
# Each registered surface gets the exact same gesture interpreter; the actual main legacy listener stays untouched.
one("function down(e){if(!enabled)return;stop(e);", "function down(e){const surface=surfaces.get(e.currentTarget)??'MAIN';if(!enabled&&surface==='MAIN')return;if(gesture&&surface!==inputSurface)resetGesture();inputSurface=surface;inputElement=e.currentTarget;notifyInput();stop(e);")
one("canvas.setPointerCapture?.(e.pointerId)","inputElement.setPointerCapture?.(e.pointerId)")
one("pinch={distance:Math.hypot(a.x-b.x,a.y-b.y),km:tacticalViewKm}","pinch={distance:Math.hypot(a.x-b.x,a.y-b.y),km:view().km,anchor:fromScreen((a.x+b.x)/2,(a.y+b.y)/2)}")
one('cam:{...camOffset}', 'center:{...view().center}')
one("function move(e){if(!enabled)return;stop(e);", "function move(e){if(!enabled&&(surfaces.get(e.currentTarget)??'MAIN')==='MAIN')return;if(!pointers.size){inputSurface=surfaces.get(e.currentTarget)??'MAIN';inputElement=e.currentTarget;}notifyInput();stop(e);")
one('tacticalViewKm=clamp(pinch.km*pinch.distance/d,VP_TACTICAL_DISTANCE_A.minKm,VP_TACTICAL_DISTANCE_A.maxKm);vpUpdateMapZoomA();updateTacticalScaleLabel();', 'setDistance(pinch.km*pinch.distance/d);const centerPx={x:(a.x+b.x)/2,y:(a.y+b.y)/2},after=fromScreen(centerPx.x,centerPx.y),c=view().center;setCenter({x:c.x+pinch.anchor.x-after.x,y:c.y+pinch.anchor.y-after.y},false);')
one('const a=screenToWorld(g.x,g.y),b=screenToWorld(e.clientX,e.clientY);camOffset.x=g.cam.x+a.x-b.x;camOffset.y=g.cam.y+a.y-b.y;', 'const a=fromScreen(g.x,g.y),b=fromScreen(e.clientX,e.clientY);setCenter({x:g.center.x+a.x-b.x,y:g.center.y+a.y-b.y});')
one("function up(e){if(!enabled)return;stop(e);", "function up(e){if(!enabled&&(surfaces.get(e.currentTarget)??'MAIN')==='MAIN')return;notifyInput();stop(e);")
one('canvas.releasePointerCapture(e.pointerId)','inputElement.releasePointerCapture(e.pointerId)')
start=s.index(" for(const[n,fn]of [['pointerdown',down]");end=s.index(" document.addEventListener('keydown'",start)
s=s[:start]+''' function attachSurface(element,id){if(surfaces.has(element)&&id!=='MAIN')return;surfaces.set(element,id);
  for(const[n,fn]of [['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',e=>{if(enabled||id==='PIP'){stop(e);notifyInput();suppressUntil=performance.now()+300;resetGesture();}}],['contextmenu',e=>{if(enabled||id==='PIP'){inputSurface=id;inputElement=element;notifyInput();stop(e);if(menu.hidden&&candidates.hidden)contextAt(e.clientX,e.clientY);}}]])element.addEventListener(n,fn,{capture:true,passive:false});
  element.addEventListener('wheel',e=>{if(gesture){gesture.multi=true;killLong();}if(id!=='PIP')return;inputSurface=id;inputElement=element;notifyInput();stop(e);window.__PIP_A__.zoom(e.deltaY<0?'IN':'OUT',{x:e.clientX,y:e.clientY});},{capture:true,passive:false});
  for(const type of ['touchstart','touchmove','touchend','touchcancel'])element.addEventListener(type,e=>{if(!enabled&&id==='MAIN')return;stop(e);notifyInput();if(e.touches.length>1){killLong();if(gesture)gesture.multi=true;suppressUntil=performance.now()+300;}},{capture:true,passive:false});
 }
 attachSurface(canvas,'MAIN');
 document.addEventListener('pointerdown',e=>{if(menu.contains(e.target)||candidates.contains(e.target))return;if(!surfaces.has(e.target))closeTransient();},{capture:true});
''' +s[end:]
one('const rows=records(),o=rows.find(q=>q.key===lookup),c=controlObject();','const rows=picture,o=rows.find(q=>q.key===lookup),c=paintControlled;')
one('return Object.freeze({setMode,showControlInfo,', "return Object.freeze({setMode,showControlInfo,attachSurface,preparePaint(){records(true);paintControlled=controlObject();},revision(){return selectionRevision;},")
one("presentationOnly:true,enabled,controlPlatform:","presentationOnly:true,enabled,inputSurface,controlPlatform:")
one('objects(){return records(true).map(o=>({...o}));},hitTest:hits,',"objects(){return records(true).map(o=>({...o}));},hitTest(x,y,surface='MAIN'){const saved=inputSurface;try{inputSurface=surface;return hits(x,y);}finally{inputSurface=saved;}},")
s=s.replace('picture=mapObservedObjectsA();',"picture=mapObservedObjectsA().map(o=>{const p=pipChartFrameA.tracks.get(o.kind==='TRACK'?o.id:o.associatedTrackId);return p?._chartVisible?{...o,x:p.x,y:p.y,z:p.z}:o;});")
s=s.replace('canvas.classList','inputElement.classList')
s=s.replace("inputSurface='MAIN',inputElement=canvas","pinchSuppressUntil=-Infinity,inputSurface='MAIN',inputElement=canvas")
s=s.replace('moved:false,multi:false,menu:false,blocked:', 'moved:false,multi:false,menu:false,suppressed:now<pinchSuppressUntil,blocked:')
s=s.replace('suppressUntil=now+300','pinchSuppressUntil=suppressUntil=now+300').replace('suppressUntil=performance.now()+300','pinchSuppressUntil=suppressUntil=performance.now()+300')
s=s.replace('longTimer=setTimeout(', 'if(!gesture.suppressed)longTimer=setTimeout(')
s=s.replace('!g.moved&&!g.multi&&!g.menu&&!g.blocked&&elapsed', '!g.moved&&!g.multi&&!g.menu&&!g.blocked&&!g.suppressed&&elapsed')
s=s.replace('if(!g||g.id!==e.pointerId||g.menu||g.blocked)return;', 'if(!g||g.id!==e.pointerId||g.menu||g.blocked||g.multi)return;')
s=s.replace("candidates.append(action('확대',","const zoomAction=action('확대',").replace("zoomReason,'mapExpandPipA'));for(const o of rows)","zoomReason,'mapExpandPipA');for(const o of rows)").replace('candidates.hidden=false;place(candidates,x,y);','candidates.append(zoomAction);candidates.hidden=false;place(candidates,x,y);').replace("candidates.querySelectorAll('button')","candidates.querySelectorAll('button:not(#mapExpandPipA)')")

start=s.index("const zoomAction=action('확대',")
end=s.index(';for(const o of rows)',start)
s=s[:start]+"const zoomAction=action('확대',()=>expandCandidates(false),zoomReason,'mapExpandPipA')"+s[end:]
s=s.replace("function contextFor(o,x,y)","""function updateCandidateNote(result){let note=candidates.querySelector('.map-expand-note-a');if(!note){note=el('small','map-expand-note-a');candidates.append(note);}note.textContent=result.message;let b=candidates.querySelector('#mapCandidateMainA');if(result.minSeparationPx<40&&WIP148_EXTERNAL_3D.active){if(!b)candidates.append(action('주화면에서 보기',()=>expandCandidates(true),'','mapCandidateMainA'));}else b?.parentElement.remove();place(candidates,candidateContext.x,candidateContext.y);}
 async function expandCandidates(main=false){if(!candidateContext)return;const rows=candidateContext.rows.map(o=>resolve(o.key,true)??o);if(main){inputSurface='MAIN';inputElement=canvas;candidateContext.surface='MAIN';const result=await window.__PIP_A__.showMain(rows);updateCandidateNote(result);}else{const saved=inputSurface;inputSurface=candidateContext.surface;const result=window.__PIP_A__.expand(candidateContext.surface,rows);updateCandidateNote(result);inputSurface=saved;}}
 function contextFor(o,x,y)""")
s=s.replace("button:not(#mapExpandPipA)","button:not(#mapExpandPipA):not(#mapCandidateMainA)")
(H/'map.js').write_text(s)
