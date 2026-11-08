#!/usr/bin/env python3
"""ESM_A Commit-D state presentation and manual cue gate."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'docs/pip/B'),str(ROOT/'docs/bunkerhill/K')]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
CAND=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_D_DIAG.html')
def strict(q):return json.dumps(q,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def main():
 started=time.monotonic();errors=[];profiles={};screens={};layout={}
 with sync_playwright() as pw:
  browser=launch(pw)
  for profile in ('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'):
   runs=[]
   for _ in range(2):
    page=load(browser,CAND.read_bytes(),ship=profile,errors=errors);runs.append(page.evaluate('()=>__ESM_A_D_DIAG__.matrix()'));page.close()
   profiles[profile]=runs
  for label,size in [('desktop',{'width':1400,'height':900}),('mobile',{'width':832,'height':384})]:
   page=load(browser,CAND.read_bytes(),ship='CG_52_LATE_TICONDEROGA',errors=errors);page.set_viewport_size(size);page.wait_for_timeout(250);layout[label]=page.evaluate('()=>__ESM_A_D_DIAG__.scene()');path=HERE/f'D_{label.upper()}.png';page.screenshot(path=str(path),full_page=False);screens[label]={'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size};page.close()
  browser.close()
 matrices=[q for rows in profiles.values() for q in rows];checks={'pageErrorsZero':not errors,'allMatricesPass':all(q['pass'] for q in matrices),'repeatDeterministic':all(rows[0]==rows[1] for rows in profiles.values()),'ddgUnsupportedWeaponFailClosed':profiles['DDG_119_LATE_FLIGHT_IIA'][0]['checks']['unsupportedShipFailClosed'],'cgManualCueAllowed':profiles['CG_52_LATE_TICONDEROGA'][0]['checks']['supportedCueUsesExistingRoute'],'uncertainMultimodalStaleRejected':all(q['checks']['staleRejected'] and q['checks']['ambiguousRejected'] and q['checks']['wideAreaRejected'] for q in matrices),'noTrackIdentityOrAutomaticAuthority':all(q['checks']['observerTracksUntouched'] and q['checks']['identityRemainsUnknown'] and q['checks']['noAutomaticAuthority'] for q in matrices),'historicalOriginsAndPipExact':all(q['checks']['historicalOriginsPreserved'] and q['checks']['mapUsesHistoricalOrigin'] and q['checks']['mainAndPipPresentationExact'] for q in matrices),'hiddenTruthTextZero':all(q['checks']['noHiddenTruthText'] and q['checks']['frameHasNoTruth'] for q in matrices),'desktopMobileOverflowZero':all(q['body']['scrollWidth']<=q['body']['innerWidth'] for q in layout.values()),'screenshotsCaptured':len(screens)==2 and all(q['bytes']>0 for q in screens.values())}
 result={'schema':'AEGIS_ESM_A_COMMIT_D_GATE_1','status':'PASS' if all(checks.values()) else 'FAIL','elapsedS':time.monotonic()-started,'checks':checks,'pageErrors':errors,'candidateDiagnosticSha256':hashlib.sha256(CAND.read_bytes()).hexdigest(),'profiles':profiles,'layout':layout,'screenshots':screens}
 (HERE/'D_GATE.json').write_text(strict(result));print(strict({'status':result['status'],'elapsedS':result['elapsedS'],'checks':checks,'pageErrors':errors,'screenshots':screens}));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
