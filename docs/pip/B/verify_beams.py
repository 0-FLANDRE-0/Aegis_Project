"""Toggle ON reproduces PIP_A paint, excluding the documented trail-width correction."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for path in [a.base,a.html]:
  p=load_fleet(b,path.read_bytes(),width=1400,height=900,errors=errors);p.evaluate('__NAVAL_SIM_DIAG__.setEmcon(false);__NAVAL_SIM_DIAG__.stepTicks(120)');p.wait_for_timeout(120)
  if path==a.html:p.evaluate('()=>{const e=document.getElementById("sensorBeams2DB");e.checked=true;e.dispatchEvent(new Event("change"))}')
  cmds=p.evaluate('''()=>{__PIP_A__.prepare();const c=new OffscreenCanvas(400,300).getContext('2d'),log=[],norm=x=>typeof x==='object'?Object.prototype.toString.call(x):x,proxy=new Proxy(c,{get(t,k){const v=Reflect.get(t,k,t);return typeof v==='function'?function(...args){log.push([k,...args.map(norm)]);return v.apply(t,args)}:v;},set(t,k,v){log.push(['SET',k,k==='lineWidth'&&t.strokeStyle==='rgba(56, 180, 140, 0.22)'?'NAV_TRAIL_PIXEL_WIDTH_FIX':norm(v)]);Reflect.set(t,k,v,t);return true;}}),rect={x:0,y:0,w:400,h:300,cx:200,cy:150,shortSide:300,dpr:1};__PIP_A__.renderView({target:'AUDIT',context:proxy,rect,km:40,center:{x:0,y:0}});return log;}''');data=json.dumps(cmds,separators=(',',':'));rows.append({'build':path.name,'htmlSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'paintCommands':len(cmds),'commandHash':hashlib.sha256(data.encode()).hexdigest()});(a.out/(path.stem+'-commands.json')).write_text(data);p.close()
 b.close()
checks={'P4.onSamePaintCommands':rows[0]['commandHash']==rows[1]['commandHash'],'pageErrors':not errors};out={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors};(a.out/'beams.json').write_text(json.dumps(out,indent=2));print(json.dumps(out));raise SystemExit(0 if out['pass']else 1)
