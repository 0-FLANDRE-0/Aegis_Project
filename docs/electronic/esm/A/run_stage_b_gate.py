#!/usr/bin/env python3
"""ESM_A Commit-B deterministic boundary/localizer gate."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'docs/pip/B'),str(ROOT/'docs/bunkerhill/K')]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
BASE=Path('/tmp/Aegis_SIM_v48_WIP_EMCON_B_ESM_DIAG.html');CAND=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_B_DIAG.html')
def strict(q):return json.dumps(q,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def main():
 started=time.monotonic();errors=[];profiles={};localizer=None;end_to_end=None
 with sync_playwright() as pw:
  browser=launch(pw)
  for profile in ('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'):
   rows={}
   for name,body in [('baseline',BASE.read_bytes()),('candidate',CAND.read_bytes())]:
    page=load(browser,body,ship=profile,errors=errors);rows[name]=page.evaluate('()=>__ESM_A_B_DIAG__.native(30)')
    if name=='candidate' and localizer is None:
     localizer=page.evaluate('()=>__ESM_A_B_DIAG__.localizer()');end_to_end=page.evaluate('()=>__ESM_A_B_DIAG__.endToEnd()')
    page.close()
   profiles[profile]=rows
  browser.close()
 same={p:profiles[p]['baseline']==profiles[p]['candidate'] for p in profiles}
 checks={'pageErrorsZero':not errors,'ddgNativeDetectionBearingAndRngExact':same['DDG_119_LATE_FLIGHT_IIA'],'cgNativeDetectionBearingAndRngExact':same['CG_52_LATE_TICONDEROGA'],'localizerMatrixPass':localizer['pass'],'singleBearingNoPoint':localizer['checks']['singleBearingNoPoint'],'historicalOriginFixed':localizer['checks']['historicalOriginFixed'],'parallelGeometryNotPromoted':localizer['checks']['parallelNotPoint'],'coastAndLostHonest':localizer['checks']['coastGrows'] and localizer['checks']['lostAtHold'],'strictDtoFailClosed':all(localizer['checks'][k] for k in ('unknownRejected','nanRejected','futureRejected','badCovarianceRejected')),'deterministic':localizer['checks']['deterministic'],'truthBoundary':localizer['checks']['noTruthFields'] and not end_to_end['truthLeak'],'endToEndCommonPath':end_to_end['rawCount']>0 and end_to_end['accepted']['ok'] and end_to_end['contactCount']>0,'noObserverTrackOrAuthority':end_to_end['tracksBefore']==end_to_end['tracksAfter'] and end_to_end['snapshot']['observerTracksCreated']==0 and end_to_end['snapshot']['automaticEngagementAuthority'] is False}
 result={'schema':'AEGIS_ESM_A_COMMIT_B_GATE_1','status':'PASS' if all(checks.values()) else 'FAIL','elapsedS':time.monotonic()-started,'checks':checks,'pageErrors':errors,'inputs':{'baselineDiagnosticSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidateDiagnosticSha256':hashlib.sha256(CAND.read_bytes()).hexdigest()},'profiles':profiles,'localizer':localizer,'endToEnd':end_to_end}
 (HERE/'B_GATE.json').write_text(strict(result));print(strict({'status':result['status'],'elapsedS':result['elapsedS'],'checks':checks,'pageErrors':errors}));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
