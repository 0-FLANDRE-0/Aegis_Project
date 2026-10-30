// VP_A: presentation-only CSS/client-pixel geometry. No simulation state/RNG.
// Only full-span edge panels reduce the visible rectangle. Explicit membership
// prevents a floating HUD, drawer, mini CIC or missile-status box moving a map.
const AEGIS_VIEWPORT=(()=>{
 const EDGE_PANELS=Object.freeze([{id:'controlDeckPanel',screen:'twoD',edge:'bottom',minSpan:.9,maxEdgeGapPx:32}]);
 const listeners=new Set(),pending=new Set(),observed=new Set();let state=null,raf=0,settle=0,version=0;
 const rect=(x,y,w,h)=>({x,y,w:Math.max(1,w),h:Math.max(1,h),cx:x+Math.max(1,w)/2,cy:y+Math.max(1,h)/2,shortSide:Math.max(1,Math.min(w,h))});
 const box=e=>{const r=e.getBoundingClientRect();return rect(r.x,r.y,r.width,r.height);};
 const intersection=(a,b)=>rect(Math.max(a.x,b.x),Math.max(a.y,b.y),Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
 const probe=document.createElement('div');probe.id='aegisSafeAreaProbeVpA';probe.setAttribute('aria-hidden','true');probe.style.cssText='position:fixed;visibility:hidden;pointer-events:none;width:0;height:0;padding:env(safe-area-inset-top,0px) env(safe-area-inset-right,0px) env(safe-area-inset-bottom,0px) env(safe-area-inset-left,0px)';document.body.append(probe);
 function measure(){
  const vv=window.visualViewport,raw=rect(vv?.offsetLeft??0,vv?.offsetTop??0,vv?.width??window.innerWidth,vv?.height??window.innerHeight),s=window.getComputedStyle(probe),safe={top:Number.parseFloat(s.paddingTop)||0,right:Number.parseFloat(s.paddingRight)||0,bottom:Number.parseFloat(s.paddingBottom)||0,left:Number.parseFloat(s.paddingLeft)||0},layout=rect(raw.x+safe.left,raw.y+safe.top,raw.w-safe.left-safe.right,raw.h-safe.top-safe.bottom),dpr=Math.max(1,window.devicePixelRatio||1),orientation=layout.w>=layout.h?'landscape':'portrait';
  let twoD={...layout};const panels=[];
  for(const p of EDGE_PANELS){const el=document.getElementById(p.id);if(!el)continue;const r=box(el),css=window.getComputedStyle(el),visible=css.display!=='none'&&css.visibility!=='hidden'&&el.getBoundingClientRect().height>0,span=Math.max(0,Math.min(r.x+r.w,layout.x+layout.w)-Math.max(r.x,layout.x))/layout.w,attached=r.y<layout.y+layout.h&&r.y+r.h>=layout.y+layout.h-p.maxEdgeGapPx;
   const reduces=visible&&span>=p.minSpan&&attached;panels.push({...p,...r,reduces});if(reduces)twoD=rect(twoD.x,twoD.y,twoD.w,Math.max(1,Math.min(twoD.y+twoD.h,r.y)-twoD.y));
  }
  const root=document.getElementById('external3DView'),rootBox=root&&root.getBoundingClientRect().width>0?box(root):raw,threeD=intersection(layout,rootBox),extras=[...observed].filter(e=>e.isConnected).map(e=>({id:e.id,...box(e)}));
  const add=r=>({...r,dpr,orientation,version:0});return {raw:add(raw),layout:add(layout),twoD:add(twoD),threeD:add(threeD),threeDCanvas:add(rootBox),safe,panels,extras,dpr,orientation,version:0};
 }
 function publish(){raf=0;const next=measure(),changed=!state||JSON.stringify({...next,version:0})!==JSON.stringify({...state,version:0,raw:{...state.raw,version:0},layout:{...state.layout,version:0},twoD:{...state.twoD,version:0},threeD:{...state.threeD,version:0},threeDCanvas:{...state.threeDCanvas,version:0}});
  if(changed){next.version=++version;for(const k of ['raw','layout','twoD','threeD','threeDCanvas'])next[k].version=version;state=next;}const deliver=changed?[...listeners]:[...pending];pending.clear();for(const fn of deliver)fn(snapshot());
 }
 function schedule(){if(!raf)raf=requestAnimationFrame(publish);window.clearTimeout(settle);settle=setTimeout(()=>{settle=0;if(!raf)raf=requestAnimationFrame(publish);},150);}
 function snapshot(){return JSON.parse(JSON.stringify(state??measure()));}
 const ro=typeof ResizeObserver==='function'?new ResizeObserver(schedule):null;
 function observe(el){if(el&&!observed.has(el)){observed.add(el);ro?.observe(el);schedule();}}
 for(const event of ['resize','orientationchange'])window.addEventListener(event,schedule,{passive:true});
 for(const event of ['fullscreenchange','webkitfullscreenchange'])document.addEventListener(event,schedule,{passive:true});
 for(const event of ['resize','scroll'])window.visualViewport?.addEventListener(event,schedule,{passive:true});
 for(const id of ['controlDeckPanel','external3DView'])observe(document.getElementById(id));observe(document.documentElement);
 // Class/hidden changes can reveal an equally sized panel without a RO size event.
 const mo=new MutationObserver(schedule);for(const id of ['controlDeckPanel','external3DView']){const e=document.getElementById(id);if(e)mo.observe(e,{attributes:true,attributeFilter:['class','style','hidden']});}
 state=measure();schedule();
 return Object.freeze({get twoD(){return {...state.twoD};},get threeD(){return {...state.threeD};},get raw(){return {...state.raw};},get layout(){return {...state.layout};},get version(){return version;},snapshot,subscribe(fn){listeners.add(fn);pending.add(fn);schedule();return()=>{listeners.delete(fn);pending.delete(fn);};},observe,schedule,intersection,edgePanels:EDGE_PANELS});
})();
window.AEGIS_VIEWPORT=AEGIS_VIEWPORT;

// FOV is measured along the unobscured short side, not the canvas vertical axis.
// setViewOffset extends this visible frustum over the complete backing canvas.
function vpCameraProjectionA(camera,canvasRect,visible,shortFovDeg=52){
 const w=Math.max(1,visible.w),h=Math.max(1,visible.h),fov=w>=h?shortFovDeg:Math.min(100,2*Math.atan(Math.tan(shortFovDeg*Math.PI/360)*h/w)*180/Math.PI);
 camera.fov=fov;camera.aspect=w/h;
 const full=Math.abs(canvasRect.x-visible.x)<.1&&Math.abs(canvasRect.y-visible.y)<.1&&Math.abs(canvasRect.w-w)<.1&&Math.abs(canvasRect.h-h)<.1;
 if(full)camera.clearViewOffset();else camera.setViewOffset(w,h,canvasRect.x-visible.x,canvasRect.y-visible.y,canvasRect.w,canvasRect.h);
 camera.updateProjectionMatrix();
 return w>=h?fov:2*Math.atan(Math.tan(fov*Math.PI/360)*w/h)*180/Math.PI;
}

const VP_TACTICAL_DISTANCE_A=Object.freeze({minKm:390*.42/(6*3.8),maxKm:1080*.42/(.08*3.8),reference:'Legacy pixel-zoom distance union over the seven VP_A review sizes; presentation only'});
function vpUpdateMapZoomA(){mapZoom=AEGIS_VIEWPORT.twoD.shortSide*.42/(tacticalViewKm*WORLD_UNITS_PER_KM);return mapZoom;}
function worldToScreen(x,y){const v=AEGIS_VIEWPORT.twoD,z=vpUpdateMapZoomA();return {x:v.cx+(x-aircraft.x()-camOffset.x)*z,y:v.cy+(y-aircraft.y()-camOffset.y)*z};}
function screenToWorld(x,y){const v=AEGIS_VIEWPORT.twoD,z=vpUpdateMapZoomA();return {x:aircraft.x()+camOffset.x+(x-v.cx)/z,y:aircraft.y()+camOffset.y+(y-v.cy)/z};}
function vpCancelMapGestureA(){if(_ptrId!==null){try{if(canvas.hasPointerCapture(_ptrId))canvas.releasePointerCapture(_ptrId);}catch(_){} }_ptrId=null;_ptrMoved=false;_pinchDist0=0;canvas.classList.remove('dragging');}
