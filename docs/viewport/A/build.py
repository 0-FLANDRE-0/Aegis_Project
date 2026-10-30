"""Pinned presentation-only patch of SOV_A; other packed/assets bytes preserved."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
BASE_SHA='1e2125e49ae0720d45f2457474753ed948324241aecf69120f5c7694ea733b28'
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def patch(s):
 def edit(a,b,n=1):
  nonlocal s
  assert s.count(a)==n,(a[:160],s.count(a),n)
  s=s.replace(a,b)
 edit('// ===== FULL SCREEN RADAR =====\nfunction radarW(){ return innerWidth; }\nfunction radarH(){ return innerHeight; }',(HERE/'viewport.js').read_text())
 edit('let mapZoom = 1.0;  // drawing-only zoom (pinch)','let tacticalViewKm=120; // authoritative presentation distance, invariant under resize\nlet mapZoom=1; // derived CSS px/world; never saved or directly manipulated')
 edit('const centerX = r.width * 0.5, centerY = r.height * 0.5;\n    const worldX = aircraft.x()+camOffset.x+(screenX-centerX)/mapZoom;\n    const worldY = aircraft.y()+camOffset.y+(screenY-centerY)/mapZoom;', 'const world=screenToWorld(e.clientX,e.clientY),worldX=world.x,worldY=world.y;')
 edit('  _ptrId = e.pointerId;\n  const r', '  vpUpdateMapZoomA();\n  _ptrId = e.pointerId;\n  const r')
 edit('    camOffset.x = _camStartX - dx / mapZoom;\n    camOffset.y = _camStartY - dy / mapZoom;', '    const a=screenToWorld(_ptrStartX+r.left,_ptrStartY+r.top),b=screenToWorld(e.clientX,e.clientY);camOffset.x=_camStartX+a.x-b.x;camOffset.y=_camStartY+a.y-b.y;')
 edit('_pinchZoom0 = mapZoom;', '_pinchZoom0 = tacticalViewKm;')
 edit('mapZoom = Math.max(0.08, Math.min(6.0, _pinchZoom0 * (d / _pinchDist0)));', 'tacticalViewKm=clamp(_pinchZoom0*(_pinchDist0/d),VP_TACTICAL_DISTANCE_A.minKm,VP_TACTICAL_DISTANCE_A.maxKm);vpUpdateMapZoomA();')
 a=s.index('function resize() {');b=s.index('  const TAU =',a)
 s=s[:a]+'''function resize(){
  const v=AEGIS_VIEWPORT.raw,dpr=Math.min(2,v.dpr);
  canvas.width=Math.max(1,Math.floor(v.w*dpr));canvas.height=Math.max(1,Math.floor(v.h*dpr));
  canvas.style.width=v.w+'px';canvas.style.height=v.h+'px';canvas.style.left=v.x+'px';canvas.style.top=v.y+'px';
  // All map transforms and input use client CSS coordinates, including VV offset.
  ctx.setTransform(dpr,0,0,dpr,-v.x*dpr,-v.y*dpr);
  const ap=altCanvas.parentElement;if(ap){altCanvas.width=Math.floor(ap.clientWidth*dpr);altCanvas.height=Math.floor(ap.clientHeight*dpr);altCtx.setTransform(dpr,0,0,dpr,0,0);}
  vpCancelMapGestureA();vpUpdateMapZoomA();
}
AEGIS_VIEWPORT.subscribe(resize);

'''+s[b:]
 edit('const screen = () => ({ w: radarW(), h: radarH() });', 'const screen=()=>({w:AEGIS_VIEWPORT.twoD.w,h:AEGIS_VIEWPORT.twoD.h});')
 edit('    const screenR = Math.min(radarW(), radarH()) * 0.42;\n    return screenR / Math.max(1e-9, mapZoom * WORLD_UNITS_PER_KM);', '    return tacticalViewKm;')
 edit('    const cx=rw*0.5,cy=rh*0.5,z=Math.max(1e-9,mapZoom);\n    return {\n      minX:aircraft.x()+camOffset.x-cx/z,\n      maxX:aircraft.x()+camOffset.x+(rw-cx)/z,\n      minY:aircraft.y()+camOffset.y-cy/z,\n      maxY:aircraft.y()+camOffset.y+(rh-cy)/z\n    };', '    const v=AEGIS_VIEWPORT.twoD,a=screenToWorld(v.x,v.y),b=screenToWorld(v.x+v.w,v.y+v.h);return {minX:a.x,maxX:b.x,minY:a.y,maxY:b.y};')
 edit('    const viewKm = TACTICAL_ZOOM_KM[tacticalZoomIdx];\n    const screenR = Math.min(radarW(), radarH()) * 0.42;\n    mapZoom = screenR / (viewKm * WORLD_UNITS_PER_KM);\n    mapZoom = Math.max(0.08, Math.min(6.0, mapZoom));', '    tacticalViewKm=TACTICAL_ZOOM_KM[tacticalZoomIdx];vpUpdateMapZoomA();')
 edit('    const targetPx = Math.min(120, Math.max(72, radarW()*0.18));\n    const niceKm = pickNiceScaleBarKm(targetPx * kmPerPx);', '    const v=AEGIS_VIEWPORT.twoD,niceKm=pickNiceScaleBarKm(tacticalViewKm*.2);')
 edit('    const x = 16;\n    const y = radarH() - 22;', '    const x=v.x+16,y=v.y+v.h-22;')
 edit('    const rw = radarW(), rh = radarH();\n    ctx.fillStyle', '    vpUpdateMapZoomA();const raw=AEGIS_VIEWPORT.raw,vp=AEGIS_VIEWPORT.twoD,rw=raw.w,rh=raw.h;\n    ctx.fillStyle')
 edit('ctx.fillRect(0,0,rw,rh);', 'ctx.fillRect(raw.x,raw.y,rw,rh);')
 edit('const W=Math.min(360,Math.max(300,rw*0.30)),H=151,x=(rw-W)*0.5,y=6;', 'const vp=AEGIS_VIEWPORT.layout,W=Math.min(360,Math.max(300,vp.w*.30)),H=151,x=vp.cx-W*.5,y=vp.y+6;')
 edit('    const cx = rw * 0.5, cy = rh * 0.5;\n    ctx.translate(cx, cy);\n    ctx.scale(mapZoom, mapZoom);\n    ctx.translate(-aircraft.x()-camOffset.x,-aircraft.y()-camOffset.y);', '    ctx.beginPath();ctx.rect(vp.x,vp.y,vp.w,vp.h);ctx.clip();\n    const origin=worldToScreen(0,0);ctx.translate(origin.x,origin.y);ctx.scale(mapZoom,mapZoom);')
 edit('  setTimeout(() => { setTacticalZoom(1); updateTacticalScaleLabel(); }, 100);', '  setTacticalZoom(1);updateTacticalScaleLabel();')
 edit("function c52UpdateDockClearance(){const el=document.getElementById('controlDeckPanel');if(el)document.documentElement.style.setProperty('--c52-control-height',Math.ceil(el.getBoundingClientRect().height+6)+'px');}", "function c52UpdateDockClearance(){const p=AEGIS_VIEWPORT.snapshot().panels.find(p=>p.id==='controlDeckPanel'),height=Math.ceil((p?.h??0)+6),root=document.documentElement;if(root.style.getPropertyValue('--c52-control-height')!==height+'px')root.style.setProperty('--c52-control-height',height+'px');}")
 edit("  if(typeof ResizeObserver!=='undefined'){new ResizeObserver(c52UpdateDockClearance).observe(document.getElementById('controlDeckPanel'));}\n  window.addEventListener('resize',c52UpdateDockClearance,{passive:true});c52UpdateDockClearance();", '  AEGIS_VIEWPORT.subscribe(c52UpdateDockClearance);')
 edit('    c52UpdateDockClearance();\n    const panel', '    const panel')
 edit('resize(){if(!this.renderer||!this.camera||!this.canvas)return;const w=Math.max(2,this.root?.clientWidth||innerWidth),h=Math.max(2,this.root?.clientHeight||innerHeight);this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this._resizeNeeded=false;},', '''resize(){if(!this.renderer||!this.camera||!this.canvas)return;const r=this.root.getBoundingClientRect(),c={x:r.x,y:r.y,w:Math.max(2,r.width),h:Math.max(2,r.height)};this.renderer.setSize(c.w,c.h,false);this.vpShortFovDegA=vpCameraProjectionA(this.camera,c,AEGIS_VIEWPORT.threeD,52);this._viewportVersionA=AEGIS_VIEWPORT.version;this._resizeNeeded=false;},''')
 edit('if(this._resizeNeeded)this.resize();const st=get3DRenderState();', 'if(this._resizeNeeded||this._viewportVersionA!==AEGIS_VIEWPORT.version)this.resize();const st=get3DRenderState();')
 edit('    const camera=view.camera,h=Math.max(1,c.getBoundingClientRect().height),scale=2*distance*Math.tan((camera?.fov??52)*Math.PI/360)/(h*(camera?.zoom||1));\n    if(!Number.isFinite(scale))return;\n    view.c14CameraPan.x-=dx*scale;view.c14CameraPan.y+=dy*scale;', '    const scale=1/(AEGIS_VIEWPORT.threeD.shortSide*(view.camera?.zoom||1));\n    if(!Number.isFinite(scale))return;\n    view.c14CameraPan.x-=dx*scale;view.c14CameraPan.y+=dy*scale;')
 edit("window.addEventListener('resize',()=>{view.c14CancelGesture();view._resizeNeeded=true;},{passive:true});", 'AEGIS_VIEWPORT.subscribe(()=>{view.c14CancelGesture();view._resizeNeeded=true;});')
 edit('q.set(p.x,p.y,0).applyQuaternion(this.camera.quaternion);', 'const span=2*this.orbit.distance*Math.tan((this.vpShortFovDegA??52)*Math.PI/360);q.set(p.x*span,p.y*span,0).applyQuaternion(this.camera.quaternion);')
 edit("const max=Math.max(92,innerHeight-r.top-reserved);", "const max=Math.max(92,AEGIS_VIEWPORT.layout.y+AEGIS_VIEWPORT.layout.h-r.top-reserved);")
 edit('reserved=innerHeight>620?166:10;', 'reserved=AEGIS_VIEWPORT.layout.h>620?166:10;')
 edit("window.addEventListener('resize',place,{passive:true});", 'AEGIS_VIEWPORT.subscribe(place);')
 # Variable-size catalog: retain its intentional 38-degree short-side FOV.
 edit("document.body.appendChild(root);this.root=root;this.canvas=root.querySelector('#wip200MissileCatalogCanvas');", "document.body.appendChild(root);this.root=root;this.canvas=root.querySelector('#wip200MissileCatalogCanvas');AEGIS_VIEWPORT.observe(root);AEGIS_VIEWPORT.observe(this.canvas);")
 edit('resize(){if(!this.renderer||!this.canvas)return;const w=Math.max(2,this.canvas.clientWidth|0),h=Math.max(2,this.canvas.clientHeight|0),pr=Math.min(2,window.devicePixelRatio||1);if(this.canvas.width!==Math.floor(w*pr)||this.canvas.height!==Math.floor(h*pr)){this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();}},', '''resize(){if(!this.renderer||!this.canvas)return;const r=this.canvas.getBoundingClientRect(),w=Math.max(2,r.width),h=Math.max(2,r.height),pr=Math.min(2,AEGIS_VIEWPORT.raw.dpr);if(this._viewportVersionA!==AEGIS_VIEWPORT.version||this.canvas.width!==Math.floor(w*pr)||this.canvas.height!==Math.floor(h*pr)){this.renderer.setSize(w,h,false);this.vpShortFovDegA=vpCameraProjectionA(this.camera,{x:r.x,y:r.y,w,h},AEGIS_VIEWPORT.intersection({x:r.x,y:r.y,w,h},AEGIS_VIEWPORT.layout),38);this._viewportVersionA=AEGIS_VIEWPORT.version;}},''')
 edit('  completeShipStartup();', (HERE/'diagnostic.js').read_text()+'\n  completeShipStartup();')
 return s
def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=patch(decoded(h));s=s.replace('v48_WIP_SOV_A','v48_WIP_VP_A');z=gzip.compress(s.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):]
 h=h.replace('v48_WIP_SOV_A','v48_WIP_VP_A').replace('V48_WIP_SOV_A','V48_WIP_VP_A').replace('user-scalable=no','user-scalable=no,viewport-fit=cover')
 return h,s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();h,s=build(a.baseline.read_bytes());a.output.write_text(h);a.output.with_suffix('.main.js').write_text(s);print(json.dumps({'bytes':len(h.encode()),'sha256':hashlib.sha256(h.encode()).hexdigest()}))
