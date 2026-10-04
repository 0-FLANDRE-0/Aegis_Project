"""Keep the DDG's genuine launcher capable of physical RAM release."""
from pathlib import Path
import argparse,hashlib,json
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[]
with sync_playwright()as pw:
 b=launch(pw);page=load(b,served_bytes(a.html),ship='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 q=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,b=d.ciwsB1Closure,e=window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities;
 b.prepare({mount:'RAM',bearingDeg:90,rangeKm:6,altM:12,speedMps:280,seed:3710811});b.setPaused(true);d.wip119SetMode('MANUAL');const before=b.snapshot(),released=new Map();
 for(let tick=0;tick<20*60;tick++){d.advanceFrameNoRender(1/60,1);for(const r of e.ramOrdnance)if(!released.has(r.id))released.set(r.id,{id:r.id,isRAM:r.isRAM,platform:r._launchPlatform,massKg:r.massKg,life:r.life,x:r.x,y:r.y,z:r.z});}
 return {before,after:b.snapshot(),released:[...released.values()],fault:window.__WIP125_DIAG__.wip150RuntimeFault(),core:window.__CORE_SELFTEST_FAILURES__};}''');page.close();b.close()
checks={'GenuineRamInstallation':q['before']['mounts'][1]['type']=='RAM','RealRAMReleased':len(q['released'])>0 and all(r['isRAM']and r['platform']=='SEARAM_TRAIN_ELEVATION_MOUNT'and r['massKg']>60 for r in q['released']),'LauncherAmmoConsumed':q['after']['mounts'][1]['spent']>0,'GunDisabledInFixture':q['after']['mounts'][0]['spent']==0,'CoreZero':q['core']==[],'NoRuntimeFault':q['fault']is None,'PageErrorsZero':not errors}
r={'schema':'AEGIS_DDG119_GENUINE_RAM_RELEASE_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'checks':checks,'details':q,'errors':errors,'pass':all(checks.values())};(out/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']}),flush=True)
if not r['pass']:raise SystemExit(1)
