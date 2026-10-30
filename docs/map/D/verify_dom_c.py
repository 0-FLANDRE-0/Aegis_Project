"""Independent CSS attachment check. Same geometry fixture as inherited UI88.
Actual WebGL and actual plot arcs are verified by C135/C73, not claimed here.
"""
from pathlib import Path
import json,sys,hashlib,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();errors=[];rows=[];checks={}
with sync_playwright()as pw:
 b=launch(pw)
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()),width=w,height=h,errors=errors);reset(p);select(p,'SM6');tid=p.evaluate('__MB_TEST__.add()')
  for surface in ['MAIN','PIP']:
   if surface=='PIP':p.evaluate('__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC");__PIP_A__.setDistance(40)')
   p.wait_for_timeout(200);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);p.evaluate('a=>__MAP_B__.pickObject(a.o,a.s)',{'o':o,'s':surface});p.evaluate('__MAP_B__.refresh(true)')
   for scale in [85,100,130]:
    p.evaluate('s=>__UI_A__.setScale(s)',scale);p.wait_for_timeout(250);p.evaluate('__PIP_A__.prepare();__VIEWPORT_A__.draw();__PIP_A__.paint();__MAP_B__.refresh(true)');p.wait_for_timeout(100)
    q=p.evaluate('''()=>{const c=__MAP_C__.snapshot(),t=c.tag,b=document.getElementById('mapEngagementB').getBoundingClientRect(),r=t.sourceRect,a=t.anchor;const x=Math.max(r.x+4,Math.min(r.x+r.w-b.width-4,t.side==='right'?a.x+14:a.x-14-b.width)),y=Math.max(r.y+4,Math.min(r.y+r.h-b.height-4,t.vertical==='below'?a.y+10:a.y-10-b.height));return{anchor:a,source:r,side:t.side,vertical:t.vertical,actual:{x:b.x,y:b.y,w:b.width,h:b.height},expected:{x,y},error:Math.hypot(x-b.x,y-b.y),visible:getComputedStyle(document.getElementById('mapEngagementB')).visibility,hidden:document.getElementById('mapEngagementB').hidden}}''');tag=f'{w}.{surface}.{scale}';checks[tag]=q['error']<=1 and q['visible']=='visible'and not q['hidden'];rows.append({'size':[w,h],'surface':surface,'uiScale':scale,**q});print(tag,checks[tag],q['error'],flush=True)
   p.evaluate('__UI_A__.setScale(100)')
  p.close()
 b.close()
checks['pageErrors0']=not errors;q={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'scope':'CSS attachment / inherited UI88 geometry fixture; no separate GPU claim'};(H/'evidence/dom-attachment.json').write_text(json.dumps(q,indent=2)+'\n');assert q['pass']
