"""Native neutral placement/FLEET NAV-only UI, intact waves and 1/8/16/64x."""
from pathlib import Path
import argparse,json,hashlib,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import load_fleet,launch

def main():
 a=argparse.ArgumentParser();a.add_argument('html',type=Path);a.add_argument('out',type=Path);a=a.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];checks={};records={}
 with sync_playwright()as pw:
  b=launch(pw,False)
  p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');p.route('https://aegis.test/**',lambda r:r.fulfill(body=raw,content_type='text/html'));p.goto('https://aegis.test/sov?view3d=0',timeout=90000);p.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);c=p.locator('[data-deployment-a]:visible')
  checks['playerPickerExcluded']=not p.locator('#aegisShipSelect option[value=SOVREMENNY_956]').count();checks['allyPickerExcluded']=not c.locator('[data-ally-choice] option[value=SOVREMENNY_956]').count()
  c.locator('[data-ally-choice]').select_option('CG_52_LATE_TICONDEROGA');c.locator('[data-ally-emcon]').select_option('SILENT');c.locator('[data-enemy-choice]').select_option('SOVREMENNY_956');c.locator('[data-neutral-choice]').select_option('SOVREMENNY_956');c.locator('[data-target-choice]').select_option('NONE');c.locator('[data-enemy-aircraft-choice]').select_option('OFF');p.locator('#aegisShipSelect').select_option('DDG_119_LATE_FLIGHT_IIA');p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000);p.evaluate("()=>{document.getElementById('wip125DepartBtn').click();__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}")
  q=p.evaluate('({sov:__SOV_A__.snapshot(),fleet:__NAVAL_SIM_DIAG__.fleetSnapshotG(),save:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()})');records['initial']=q;checks['allThreeNPCs']=len(q['save']['fleet']['ships'])==3;checks['neutralFaction']=any(q['role']=='NEUTRAL'and q['faction']=='NEUTRAL'for q in q['sov']['ships']);own=q['save']['ship']['navigation']['positionWorld'];checks['enemyAndNeutralMin10km']=all(10000<=((q['navigation']['positionWorld']['x']-own['x'])**2+(q['navigation']['positionWorld']['y']-own['y'])**2)**.5/.0038<=30000 for q in q['sov']['ships']);checks['neutralSaveValid']=p.evaluate('s=>__NAVAL_SIM_DIAG__.validateOperationalStateV48Wip11A(s).ok',q['save'])
  p.locator('#modeFleetBtn').click();p.locator('#fleetChangeG').click();p.wait_for_timeout(300);p.locator('#fleetChangeG').click();p.wait_for_timeout(300);checks['selectedSOV']='소브레멘니'in p.locator('#fleetSelectedG').inner_text();checks['controlsDisabled']=all(p.locator('#'+id).is_disabled()for id in ['fleetModeG','fleetFireG','fleetEmconG','networkRadioG']);p.locator('#fleetSpeedG').fill('32');p.locator('#fleetRudderG').fill('12');p.locator('#fleetNavG').click();checks['nativeNAV32Accepted']=p.evaluate("__AEGIS_ENGAGEMENT_RUNTIME__.ships.get('SHIP_SCENARIO_ENEMY_A').navigation.targetSpeedKt===32");checks['creditVisible']=p.locator('#sovCreditA').is_visible()and'SB-129'in p.locator('#sovCreditA').inner_text();checks['mobileNoOverflow']=p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(a.out/'fleet-mobile.png'))
  q=p.evaluate('''()=>{const d=__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A(),v=d.validateOperationalStateV48Wip11A(s);d.importOperationalStateV48Wip11A(s);return {valid:v.ok,count:__SOV_A__.snapshot().ships.length,core:__CORE_SELFTEST_FAILURES__};}''');records['restore']=q;print('restore',flush=True);checks['neutralRestore']=q['valid']and q['count']==2 and not q['core'];p.close()
  # Intact ship driven by the same fixed-step heave/roll/pitch integrator.
  p=load_fleet(b,raw,enemy='SOVREMENNY_956',errors=errors);p.evaluate('window.requestAnimationFrame=()=>0');p.evaluate("()=>{const d=__NAVAL_SIM_DIAG__,r=__AEGIS_ENGAGEMENT_RUNTIME__.ships.get('SHIP_SCENARIO_ENEMY_A');d.setTerrainDiagBypass(true);d.setEmcon(true);r.dynamics.haltHorizontalContact();r.navigation.speed=r.navigation.targetSpeedKt=0;}")
  waves=[]
  for hs in [0,.9,3]:
   p.evaluate('hs=>__NAVAL_SIM_DIAG__.wip13a3SetManualWeather({hsM:hs,windSpeedMps:0,precipitation01:0})',hs);samples=[]
   for i in range(20):samples.append(p.evaluate("()=>{__NAVAL_SIM_DIAG__.stepTicks(60);return __SOV_A__.snapshot().ships[0].survival;}"))
   waves.append({'hsM':hs,'samples':samples,'rollRange':max(q['heelRad']for q in samples)-min(q['heelRad']for q in samples),'trimRange':max(q['trimRad']for q in samples)-min(q['trimRad']for q in samples),'heaveRange':max(q['draftM']for q in samples)-min(q['draftM']for q in samples)})
  records['waves']=waves;print('waves',flush=True);checks['seaStateMotion']=waves[2]['heaveRange']>waves[1]['heaveRange']>waves[0]['heaveRange']and waves[2]['rollRange']>waves[0]['rollRange']and waves[2]['trimRange']>waves[0]['trimRange'];p.close()
  rows=[]
  class Controlled:
   def new_page(self,**opts):
    x=b.new_page(**opts);x.add_init_script('window.requestAnimationFrame=()=>0;');return x
  for scale in [1,8,16,64]:
   p=load_fleet(b,raw,enemy='SOVREMENNY_956',errors=errors);p.evaluate('window.requestAnimationFrame=()=>0');q=p.evaluate('''scale=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);d.setEmcon(true);d.ciwsB1Closure.setPaused(false);d.wip13a3SetManualWeather({hsM:.9,windSpeedMps:0,precipitation01:0});d.fleetCommandG('SHIP_SCENARIO_ENEMY_A',{action:'NAV',speedKt:32,rudderDeg:12});const run=d.runFramesToTicks(60,scale,640);const q=__SOV_A__.snapshot().ships[0];delete q.mass.performance;return {scale,run,ship:q,rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};}''',scale);rows.append(q);print('scale',scale,flush=True);p.close()
  records['clock']=rows;checks['clockActually640FixedTicks']=all(r['run']['steps']==640 for r in rows);checks['allScalesExact']=all(r['ship']==rows[0]['ship']and r['rng']==rows[0]['rng']and not r['core']for r in rows);b.close()
 report={'pass':all(checks.values())and not errors,'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'deployment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
