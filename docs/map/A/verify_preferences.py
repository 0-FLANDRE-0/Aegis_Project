"""New-mode default/persistence/failure handling and unchanged operational-save policy."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import load_fleet,launch
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};errors=[]
with sync_playwright()as pw:
 b=launch(pw);native=b.new_page
 def page(**kw):
  p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('fixture'))");return p
 b.new_page=page
 for kind in ['normal','blocked','corrupt']:
  init="Object.defineProperty(window,'localStorage',{get(){throw Error('storage blocked')}})"if kind=='blocked'else"localStorage.setItem('aegis.map.a.input.1','{invalid')"if kind=='corrupt'else''
  old=b.new_page
  def newpage(**kw):
   p=old(**kw)
   if init:p.add_init_script(init)
   return p
  b.new_page=newpage;p=load_fleet(b,raw,width=832,height=384,errors=errors);checks[kind+'.defaultsNew']=p.evaluate('__MAP_A__.snapshot().enabled');checks[kind+'.startsUncontrolled']=p.evaluate('__MAP_A__.snapshot().controlPlatform===null&&__MAP_A__.snapshot().firingDesignatedTarget===null')
  saved=p.evaluate("()=>{const d=__NAVAL_SIM_DIAG__,id=d.wip114DiagAddTrack({rangeKm:15,bearingDeg:0,speedMps:0});d.a3SetOperatorIdentity(id,'HOSTILE');const s=d.exportOperationalStateV48Wip11A(),json=JSON.stringify(s);return {s,hasUI:/lookupTarget|controlPlatform|firingDesignatedTarget|AEGIS_MAP_A_UI/.test(json)}}");checks[kind+'.noUIInGameSave']=not saved['hasUI'];result=p.evaluate('s=>{__NAVAL_SIM_DIAG__.importOperationalStateV48Wip11A(s);return __AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks.size}',saved['s']);checks[kind+'.retainedTrackResetPolicy']=result==0
  if kind=='normal':
   p.evaluate('__MAP_A__.setMode(false)');p.reload();p.wait_for_selector('#aegisShipConfirmBtn');p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.__MAP_A__&&C55Packaging.ready');checks['normal.legacyRestored']=p.evaluate('__MAP_A__.snapshot().enabled===false');p.evaluate('__MAP_A__.setMode(true)');checks['normal.toggleSaved']=p.evaluate('JSON.parse(localStorage.getItem("aegis.map.a.input.1")).enabled===true')
  p.close();b.new_page=old
 b.close()
checks['pageErrors']=not errors;out={'pass':all(checks.values()),'checks':checks,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'policy':'저장 시 트랙·식별 초기화(기존 정책); export is read-only, combat transient resets on import.'};(a.out/'preferences.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
