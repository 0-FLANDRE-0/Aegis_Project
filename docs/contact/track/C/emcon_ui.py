"""Current DOM UI, no resurrected/detached LOCK/FIRE control adapters."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path[:0]=[str(R/'docs/missile/fuze-zem/A'),str(R/'docs/gun/B2/phase1b'),str(R/'docs/gun/B2/diagnostic')]
from browser_tools import instrument,launch
from fast_http import load_fast_http
from http_browser import serve
from playwright.sync_api import sync_playwright
sp=importlib.util.spec_from_file_location('ui_shared_slots_c',P.with_name('B')/'regression_runner.py');slots=importlib.util.module_from_spec(sp);sp.loader.exec_module(slots)

def main():
 out=P/'evidence/current-emcon-ui';out.mkdir(parents=True,exist_ok=True);build=json.loads((P/'BUILD.json').read_text());raw=(R/build['html']).read_bytes();assert hashlib.sha256(raw).hexdigest()==build['htmlSha256']
 helper='\n'.join((R/f).read_text()for f in ['docs/map/E/test-helper.js','docs/map/D/extension-fixture.js','docs/map/E/test_e_fixture.js'])
 server,url=serve(instrument(raw,helper));checks={};records=[];errors=[];at=time.monotonic()
 try:
  with slots.heavy_browser_slot(),sync_playwright()as pw:
   for w,h in [(390,1000),(1100,800)]:
    for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
     browser=launch(pw);page=load_fast_http(browser,url,own=own,width=w,height=h,errors=errors);page.set_default_timeout(60000);tag=f'{w}.{own[:2]}'
     page.evaluate('__ME_TEST__.reset()');checks[tag+'.retiredControlsAbsent']=page.locator('#lockBtn,#external3DAutoLockBtn,#external3DFireBtn').count()==0
     page.locator('#uiEmconChipA').click();rect=page.locator('#mapEmconMenuE').bounding_box();checks[tag+'.currentMenuInside']=rect['x']>=0 and rect['x']+rect['width']<=w+1
     page.locator('#mapRadarE').click();page.mouse.click(w/2,8);checks[tag+'.radarQuiet']=not page.evaluate('__MAP_E__.snapshot().radarOn')
     page.locator('#uiModeChipA').click();page.locator('[data-engagement-mode-a1="AUTO"]').click();page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(1)');quiet=page.evaluate('__EMCON_DESIGNATION_F2__.snapshot()');checks[tag+'.autoDoesNotRadiate']=not quiet['pdTracking']and quiet['physicalSpyEmitters']==0
     page.locator('[data-weapon-b="SM2"]').click();page.locator('[data-salvo-b="1"]').click();tid=page.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');page.evaluate('id=>{__MAP_B__.pickObject(__MAP_A__.objects().find(o=>o.key==="TRACK:"+id),"MAIN");__MAP_B__.refresh(true)}',tid)
     model=page.evaluate('__MAP_B__.snapshot()');checks[tag+'.currentSamReleaseBlocked']=page.locator('#mapFireB').is_disabled()and not model['model']['allowed']
     before=page.evaluate('__NAVAL_SIM_DIAG__.snapshot().liveInterceptors');page.locator('#mapFireB').evaluate('e=>e.click()');checks[tag+'.blockedClickNoRelease']=before==page.evaluate('__NAVAL_SIM_DIAG__.snapshot().liveInterceptors')
     if own.startswith('CG'):
      page.locator('[data-weapon-b="HARPOON"]').click();page.locator('[data-salvo-b="1"]').click();tid=page.evaluate('__MD_TEST__.surface({rangeKm:10,bearingDeg:90})');page.evaluate('id=>{__MAP_B__.pickObject(__MAP_A__.objects().find(o=>o.key==="TRACK:"+id),"MAIN");__MAP_B__.refresh(true)}',tid)
      ready=page.evaluate('__MAP_B__.snapshot()');checks[tag+'.harpoonOriginalEmconPolicy']=ready['model']['allowed']
      if ready['model']['allowed']:page.locator('#mapFireB').click()
      page.locator('#uiEmconChipA').click();page.locator('#mapRadarE').click();page.mouse.click(w/2,8);page.evaluate('__MD_TEST__.tick(120)');journal=page.evaluate('__HARPOON_JOURNAL_F1__.snapshot()');checks[tag+'.journalUsesReleaseTime']=bool(journal['records'])and journal['records'][-1]['launchEmcon']is False
     else:
      page.locator('#uiEmconChipA').click();page.locator('#mapRadarE').click();page.mouse.click(w/2,8)
     checks[tag+'.radarRestored']=page.evaluate('__MAP_E__.snapshot().radarOn');checks[tag+'.core']=page.evaluate('__CORE_SELFTEST_FAILURES__.length===0')
     records.append({'tag':tag,'quiet':quiet,'samModel':model['model']});page.screenshot(path=str(out/(tag+'.png')));browser.close()
 finally:server.shutdown()
 result={'schema':'AEGIS_TRACK_C_CURRENT_EMCON_UI_1','pass':all(checks.values())and not errors,'checks':checks,'records':records,'errors':errors,'htmlSha256':build['htmlSha256'],'legacy14RetiredNotCountedAsPass':True,'restoredRetiredControlNodes':0,'wallS':time.monotonic()-at}
 (out/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}))
 return 0 if result['pass']else 1
if __name__=='__main__':raise SystemExit(main())
