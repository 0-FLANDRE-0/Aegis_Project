"""Actual release, projectile owner/feedback and installed equipment HUD."""
from pathlib import Path
import argparse,hashlib,json
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');p.add_argument('--baseline');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];checks={};details={}
case='''opts=>{const d=window.__NAVAL_SIM_DIAG__,b=d.ciwsB1Closure,e=window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities;
 b.prepare({mount:'BOTH',bearingDeg:opts.bearingDeg,rangeKm:2.4,altM:12,speedMps:280,seed:opts.seed});b.setPaused(true);
 const before=b.snapshot(),owners={},origins={},ramIds=new Set();let maxBullets=0,maxRams=0;
 for(let tick=0;tick<12*60;tick++){d.advanceFrameNoRender(1/60,1);for(const r of e.ramOrdnance)ramIds.add(r.id);maxRams=Math.max(maxRams,e.ramOrdnance.length);maxBullets=Math.max(maxBullets,e.ciwsProjectiles.length);
   for(const p of e.ciwsProjectiles){const key=p.mountId??'UNOWNED';owners[key]=(owners[key]??0)+1;if(!origins[key])origins[key]={installationId:p.installationId??null,x:p.x,y:p.y,z:p.z};}}
 return {before,after:b.snapshot(),local:window.WIP13C5_5.snapshot(),owners,origins,ramLaunched:ramIds.size,maxRams,maxBullets,fault:window.__WIP125_DIAG__.wip150RuntimeFault()};}'''
with sync_playwright()as pw:
 browser=launch(pw)
 if a.baseline:
  old=load(browser,served_bytes(a.baseline),errors=errors);q=old.evaluate(case,{'bearingDeg':-90,'seed':3710911});details['baselinePort']=q
  checks['baselinePortGunFailsToFire']=q['maxBullets']==0 and q['after']['mounts'][1]['spent']==0 and all(m['type']=='GUN'for m in q['after']['mounts']);old.close()
 page=load(browser,served_bytes(a.html,a.main_override),errors=errors)
 for name,bearing,seed in [('starboard',90,3710910),('port',-90,3710911)]:
  q=page.evaluate(case,{'bearingDeg':bearing,'seed':seed});details[name]=q
  expectedIndex=0 if name=='starboard'else 1
  checks[name+'GunActuallyFires']=q['after']['mounts'][expectedIndex]['spent']>0 and q['maxBullets']>0
  checks[name+'NoRAMRelease']=q['ramLaunched']==0 and q['maxRams']==0
  checks[name+'ProjectilesHaveOwner']=bool(q['owners'])and'UNOWNED'not in q['owners']and all(q['origins'][key]['installationId']for key in q['origins'])
  checks[name+'IndependentAmmo']=q['after']['mounts'][1-expectedIndex]['spent']==0
  checks[name+'NoRuntimeFault']=q['fault']is None
 # The real Canvas HUD/panel must show both installed guns and no RAM count.
 ui=page.evaluate('''async()=>{const rows=[],proto=CanvasRenderingContext2D.prototype,original=proto.fillText;proto.fillText=function(text,...a){rows.push(String(text));return original.call(this,text,...a)};
   document.getElementById('armsBtn').click();await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));proto.fillText=original;
   return {rows,hud:document.getElementById('hud')?.textContent??'',closeIn:window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A().ship.inventory.ciws};}''');details['ui']=ui
 checks['BothGunPanelRows']=any('Phalanx 20mm 우현'in row for row in ui['rows'])and any('Phalanx 20mm 좌현'in row for row in ui['rows'])
 checks['NoRAMHudQuota']='PLX STBD:'in ui['hud']and'PORT:'in ui['hud']and'RAM:'not in ui['hud']and not any('SeaRAM /'in row for row in ui['rows'])
 checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
 page.screenshot(path=str(out/'cg52-close-in-panel.png'));page.close();browser.close()
checks['PageErrorsZero']=not errors
r={'schema':'AEGIS_INSTALLED_CLOSE_IN_RELEASE_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']},ensure_ascii=False),flush=True)
if not r['pass']:raise SystemExit(1)
