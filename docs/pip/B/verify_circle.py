"""P5 visual diagnosis: stationary native navigation trail had a world-unit pen."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from browser_backend import install
install()
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];checks={};records=[]
with sync_playwright()as pw:
 b=launch(pw)
 for path in [a.base,a.html]:
  p=load_fleet(b,path.read_bytes(),width=832,height=384,errors=errors,own='DDG_119_LATE_FLIGHT_IIA');p.evaluate('()=>{__NAVAL_SIM_DIAG__.stepTicks(120);for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC")}');p.wait_for_timeout(250)
  for km in [40,.5,.1]:
   p.evaluate('km=>__PIP_A__.setDistance(km)',km);q=p.evaluate('''()=>{__PIP_A__.prepare();const c=document.getElementById('external3DMiniCicCanvas').getContext('2d'),proto=CanvasRenderingContext2D.prototype,old=proto.stroke,rows=[];proto.stroke=function(...a){if(this===c&&this.strokeStyle==='rgba(56, 180, 140, 0.22)'){const t=this.getTransform();rows.push({worldWidth:this.lineWidth,cssWidth:this.lineWidth*Math.hypot(t.a,t.b)/devicePixelRatio,lineCap:this.lineCap});}return old.apply(this,a)};try{__PIP_A__.renderView(__PIP_A__.view());return {rows,png:c.canvas.toDataURL(),view:__PIP_A__.snapshot()}}finally{proto.stroke=old}}''');(a.out/f'{path.stem}-{km}km.png').write_bytes(base64.b64decode(q.pop('png').split(',')[1]));records.append({'build':path.name,'km':km,**q})
   checks[f'{path.stem}.{km}.trailExists']=len(q['rows'])==1
   if path==a.html:checks[f'{km}.widthIs1_5px']=abs(q['rows'][0]['cssWidth']-1.5)<.01
  p.close()
 b.close()
checks['pageErrors']=not errors;d={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'circle.json').write_text(json.dumps(d,indent=2));print(json.dumps({'pass':d['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if d['pass']else 1)
