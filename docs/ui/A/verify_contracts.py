"""Paired native handler behavior, fullscreen/storage failure paths, clock/hash."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
spec=importlib.util.spec_from_file_location('vp_inv',R/'docs/viewport/A/verify_invariance.py');inv=importlib.util.module_from_spec(spec);spec.loader.exec_module(inv)
F_SETUP='''()=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);d.setEmcon(false);const result=__AEGIS_WIP14A14_ENGAGEMENT_UI__.selectionProbe(35);d.ciwsB1Closure.setPaused(true);return result;}'''
E_STATE='''()=>({deck:__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot(),emcon:__EMCON_DESIGNATION_F2__.snapshot(),helicopters:__HELO__.snapshot(),harpoon:__HARPOON_DIAG_A__.snapshot(),journal:__HARPOON_JOURNAL_F1__.snapshot(),inventory:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()})'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['events','quick','storage','hash'],required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[]
 def ck(k,v):checks[k]=bool(v)
 with sync_playwright()as pw:
  b=launch(pw,a.part in ['events','quick'])
  if a.part in ['events','quick']:
   # Controls execute natively; UI visibility is not part of the tactical result.
   groups={'NAV':['rudL','rudR','spdU','spdD','undoWpBtn','clearRouteBtn','rangeBtn','centerViewBtn','shipDetailBtn','damageControlToggleV1','damageFloodToggleV1'],
    'ARM':['lockBtn','autoEngBtn','engCtrlBtn','trackIdentityBtn','fireBtn','harpoonFireA','harpoonRouteE','mainGunCueBtn','mainGunFireBtn','mainGunContinuousBtn','mainGunAmmoBtn','emconBtn','chaffBtn','nulka15bBtn','softKillAutoBtn','noiseJamBtn','deceptJamBtn','missileSelectSm2Btn','missileSelectSm2ErBtn','missileSelectSm6Btn','missileSelectEssmBtn','external3DAutoLockBtn','external3DUnlockBtn','external3DFireBtn'],
    'FLEET':['fleetChangeG','fleetModeG','fleetFireG','fleetEmconG','networkRadioG','fleetSpeedApplyG','fleetRudderApplyG','fleetFormationG','fleetManeuverG','fleetAttackH3'],
    'AIR':['airHeloA0','airHeloA1','airLaunchA','airUndoB','airClearB','airFollowB','airIffE','airRadarModeFSTBY','airRadarModeFLONG','airRadarModeFSHORT','airRadarModeFPERI','airRadarModeFISAR','airIsarCancelF2'],
    'DEBUG':['debugToggle','fullscreenBtn','modeBtn','searchModeBtn','sectorBtn','rippleBtn','salvoBtn','apsPerformanceF','isarPerformanceF2','harpoonJournalF1','b4LoftBtn']}
   if a.part=='quick':groups={}
   # Include every actual button in a tab up to 10 minimum if names changed.
   counts={};paired={}
   for tab,ids in groups.items():
    runs=[]
    for idx,path in enumerate([a.base,a.html]):
     p=load_fleet(b,path.read_bytes(),width=1400,height=900,errors=errors);p.on('dialog',lambda d:d.accept());p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');p.evaluate('t=>__NAVAL_SIM_DIAG__.wip13cSetControlDeckTab(t)',tab)
     selector='.control-deck-page[data-page="'+tab+'"]';available=p.locator(selector+' button[id]').evaluate_all('es=>es.map(e=>e.id)');wanted=[i for i in ids if p.locator('#'+i).count()];wanted+= [i for i in available if i not in wanted][:max(0,10-len(wanted))]
     if tab=='ARM':wanted+=p.locator('.wep-btn.fire,.wep-btn.lock,#wip14a14QuickEngage3D button').evaluate_all('es=>es.map(e=>e.id).filter(Boolean)')
     wanted=list(dict.fromkeys(wanted));states=[]
     for id in wanted:
      p.evaluate('id=>document.getElementById(id).click()',id);p.evaluate("document.querySelectorAll('dialog[open]').forEach(d=>d.close())");state=p.evaluate(E_STATE);encoded=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();states.append({'id':id,'stateSha256':hashlib.sha256(encoded).hexdigest(),'stateBytes':len(encoded)})
     counts[tab]=len(wanted);runs.append(states);p.close()
    ck('E.'+tab+'.minimum10',counts[tab]>=10);ck('E.'+tab+'.nativeResultsSame',runs[0]==runs[1]);paired[tab]=runs
   records['controlCounts']=counts;records['pairedControls']=paired
   f=[]
   for dimension in ['2D','3D']:
    results=[]
    for path in [a.base,a.html]:
     p=load_fleet(b,path.read_bytes(),errors=errors)
     if dimension=='3D':p.evaluate('async()=>{await __WIP148_3D_VIEW__.open();__WIP148_3D_VIEW__.active=false;}')
     fx=p.evaluate(F_SETUP);result=p.evaluate("()=>{document.getElementById('external3DAutoLockBtn').click();const lock=__EMCON_DESIGNATION_F2__.snapshot();const before=__NAVAL_SIM_DIAG__.snapshot().liveInterceptors;document.getElementById('external3DFireBtn').click();__NAVAL_SIM_DIAG__.stepTicks(60);return {lock,delta:__NAVAL_SIM_DIAG__.snapshot().liveInterceptors-before,selection:__AEGIS_WIP14A14_ENGAGEMENT_UI__.uiSnapshot().selection};}");results.append(result);p.close()
    ck('F.'+dimension+'.equal',results[0]==results[1]);ck('F.'+dimension+'.nativeLaunch',results[1]['delta']>=1);f.append({'view':dimension,'results':results})
   records['quickWidget']=f
  elif a.part=='storage':
   for mode in ['normal','reject','blocked','corrupt','oldSchema','noLandscape']:
    p=b.new_page(viewport={'width':1400,'height':900});p.on('pageerror',lambda e:errors.append(str(e)));script="""window.__NAVAL_SIM_SEED__=1831565813;window.__fsSpy={requests:0,locks:0,alerts:0};window.alert=()=>__fsSpy.alerts++;let active=null;Object.defineProperty(document,'fullscreenElement',{get:()=>active,configurable:true});Element.prototype.requestFullscreen=function(){__fsSpy.requests++;REJECT active=this;document.dispatchEvent(new Event('fullscreenchange'));return Promise.resolve();};document.exitFullscreen=()=>{active=null;document.dispatchEvent(new Event('fullscreenchange'));return Promise.resolve();};screen.orientation.lock=()=>{__fsSpy.locks++;return Promise.resolve();};""".replace('REJECT',"return Promise.reject(Error('test rejection'));"if mode=='reject'else'')
    if mode=='blocked':script+="Object.defineProperty(window,'localStorage',{get(){throw Error('storage blocked')}});"
    if mode=='corrupt':script+="localStorage.setItem('aegis.ui.a.layout.1','{bad');localStorage.setItem('aegis.ui.a.preferences.1','{bad');"
    if mode=='oldSchema':script+="localStorage.setItem('aegis.ui.a.layout.1',JSON.stringify({schema:99,layouts:{}}));"
    if mode=='noLandscape':script+="localStorage.setItem('aegis.ui.a.preferences.1',JSON.stringify({schema:1,scale:100,landscape:false}));"
    p.add_init_script(script);p.route('https://aegis.test/**',lambda r:r.fulfill(body=a.html.read_bytes(),content_type='text/html'));p.goto('https://aegis.test/ui?view3d=0',timeout=90000);p.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);ck('I.'+mode+'.load0',p.evaluate('__fsSpy.requests')==0);p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.__UI_A__&&C55Packaging?.ready',timeout=120000);p.evaluate('__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');p.wait_for_timeout(300);spy=p.evaluate('__fsSpy');ck('I.'+mode+'.first1',spy['requests']==1);ck('I.'+mode+'.silent',spy['alerts']==0);ck('I.'+mode+'.orientation',spy['locks']==(0 if mode in ['reject','noLandscape']else 1));p.evaluate("async()=>{await document.exitFullscreen();__UI_A_SETTINGS__.firstButton({target:document.createElement('button')});}");ck('I.'+mode+'.exitNoRetry',p.evaluate('__fsSpy.requests')==1);s=p.evaluate('__UI_A__.snapshot()');ck('H.'+mode+'.default',s['preset']=='PC 가로' and s['scale']==1 and s['duplicateIds']==[]);ck('E.'+mode+'.reuseFullscreen',p.locator('#uiSettingsA-system #fullscreenBtn').count()==1 and p.locator('#uiSettingsA-system button').count()==1);records[mode]={'spy':spy,'snapshot':s};p.close()
  else:
   values=[]
   for path,pause in [(a.base,False),(a.html,False),(a.html,True)]:
    p=load_fleet(b,path.read_bytes(),own='CG_52_LATE_TICONDEROGA',ally='DDG_119_LATE_FLIGHT_IIA',enemy='SOVREMENNY_956',width=1400,height=900,errors=errors);p.evaluate(inv.SETUP)
    sp=importlib.util.spec_from_file_location('emcon_ui',R/'docs/helicopter/K/verify_ui.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);tid=p.evaluate(m.SETUP);release=p.evaluate('id=>__HARPOON_DIAG_A__.fire(id)',tid);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(30)')
    for i in range(24):
     result=p.evaluate('''pause=>{const d=__NAVAL_SIM_DIAG__;if(pause){document.getElementById('uiPauseA').click();const s=__UI_A__.snapshot().time.step;d.advanceFrameNoRender(.25);if(__UI_A__.snapshot().time.step!==s)throw Error('PAUSE_TICK');document.querySelector('.time-btn[data-tw="1"]').click();}d.stepTicks(300);d.ciwsB1Closure.setPaused(true);return true;}''',pause)
    state=p.evaluate(inv.STATE);encoded=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();values.append({'file':path.name,'paused':pause,'hash':hashlib.sha256(encoded).hexdigest(),'stateBytes':len(encoded),'release':release,'ticks':7200});(a.out/('state-'+str(len(values))+'.json')).write_bytes(encoded);p.close()
   records['hashes']=values;ck('K.VP_A_120s',values[0]['hash']==values[1]['hash']);ck('G.pauseResume120s',values[1]['hash']==values[2]['hash']);ck('K.release',all(r['release']['ok']for r in values))
  b.close()
 ck('pageErrors',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors};(a.out/(a.part+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
