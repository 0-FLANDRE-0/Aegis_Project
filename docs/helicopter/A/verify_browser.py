"""Offline native Three/WebGL: exact-vs-packed poses, sharing and disposal."""
import hashlib,json
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
from browser_support import launch
r=[];errors=[];pixels={};checks={}
with sync_playwright()as pw:
 b=launch(pw,True)
 for version,file in [('original','AEGIS_HELICOPTER_MODEL_SOURCE_VIEWER_v01.html'),('packed','AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html')]:
  p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://heli.test/**',lambda route,request=None,src=(ROOT/file).read_bytes():route.fulfill(body=src,content_type='text/html'));p.goto('https://heli.test/');p.wait_for_function('window.__HELI_VIEW__?.ready||window.__HELI_ERROR__',timeout=60000);assert p.evaluate('!window.__HELI_ERROR__')
  for pose in ['folded','deployed','flight']:
   p.evaluate('m=>__HELI_VIEW__.select(m)',pose);out=p.evaluate('''()=>{const v=__HELI_VIEW__,gl=v.renderer.getContext(),w=gl.drawingBufferWidth,h=gl.drawingBufferHeight,rgba=new Uint8Array(w*h*4);v.draw();gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,rgba);const parts=[...v.groups].filter(([id,o])=>o.visible).map(([id])=>id);return{pixels:Array.from(rgba),width:w,height:h,parts,triangles:v.renderer.info.render.triangles,calls:v.renderer.info.render.calls,error:gl.getError(),memory:{...v.renderer.info.memory}}}''');pix=np.asarray(out.pop('pixels'),dtype=np.uint8).reshape((out['height'],out['width'],4));pixels[(version,pose)]=pix;p.locator('canvas').screenshot(path=str(ROOT/(pose+'-'+version+'.png')));r.append({'version':version,'pose':pose,**out});print(json.dumps(r[-1]),flush=True)
  if version=='packed':
   life=p.evaluate('''()=>{const v=__HELI_VIEW__,lease=v.lease,a=lease.build('deployed'),b=lease.build('flight'),ga=a.parts.values().next().value.children[0].geometry,gb=b.parts.values().next().value.children[0].geometry;v.scene.add(a.root,b.root);const mats=new Set(lease.materials),geos=new Set(lease.geometries.flat()),freed=new Set(),freedMat=new Set();for(const g of geos)g.addEventListener('dispose',()=>freed.add(g));for(const m of mats)m.addEventListener('dispose',()=>freedMat.add(m));a.dispose();const oneKeepsBuffers=freed.size===0&&freedMat.size===0&&b.root.parent===v.scene;b.dispose();lease.dispose();const first={geometry:freed.size,material:freedMat.size};lease.dispose();let blocks=false;try{lease.build()}catch(e){blocks=e.message==='HELI_ASSET_RETIRED'}return{geometryShared:ga===gb,oneKeepsBuffers,allDisposed:first.geometry===geos.size&&first.material===mats.size,repeatSafe:first.geometry===freed.size&&first.material===freedMat.size,retiredBlocksBuild:blocks,geoCount:geos.size,matCount:mats.size};}''');checks.update({k:v for k,v in life.items()if isinstance(v,bool)})
  p.close()
 b.close()
differences=[]
for pose in ['folded','deployed','flight']:
 old,p=pixels[('original',pose)],pixels[('packed',pose)];delta=np.abs(old.astype(np.int16)-p.astype(np.int16));fraction=float((delta[:,:,:3].max(axis=2)>3).mean());o,c=[a for a in r if a['pose']==pose];checks[pose+'.samePartsAndTriangles']=o['parts']==c['parts']and o['triangles']==c['triangles'];checks[pose+'.pixelDifferenceBounded']=fraction<.005;differences.append({'pose':pose,'pixelsRgbDifferenceOver3Fraction':fraction,'meanRgbDifference':float(delta[:,:,:3].mean()),'maxChannelDifference':int(delta.max())})
checks['allGlErrorsZero']=all(x['error']==0 for x in r);checks['allPageErrorsZero']=not errors
q={'checks':checks,'pass':all(checks.values()),'rows':r,'differences':differences,'errors':errors,'assetSha256':hashlib.sha256((ROOT/'seahawk-render-a1.bin.gz').read_bytes()).hexdigest(),'limits':'Controlled offline native Three r140/Chromium SwiftShader. Pixel thresholds allow quantization edge antialias differences; not hardware/mobile FPS. Source values, topology and material factors are tested separately.'};(ROOT/'verification-browser.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'differences':differences,'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if q['pass']else 1)
