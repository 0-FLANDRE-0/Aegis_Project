#!/usr/bin/env python3
"""ESM_A Commit-C raw-network and cooperative-estimator gate."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'docs/pip/B'),str(ROOT/'docs/bunkerhill/K')]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
BASE=Path('/tmp/Aegis_SIM_v48_WIP_EMCON_B_ESM_DIAG.html');CAND=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_C_DIAG.html')
def strict(q):return json.dumps(q,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def main():
 started=time.monotonic();errors=[];profiles={}
 with sync_playwright() as pw:
  browser=launch(pw)
  for profile in ('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'):
   base=load(browser,BASE.read_bytes(),ship=profile,errors=errors);baseline=base.evaluate('()=>__ESM_A_B_DIAG__.native(30)');base.close()
   runs=[]
   for _ in range(2):
    page=load(browser,CAND.read_bytes(),ship=profile,errors=errors);native=page.evaluate('()=>__ESM_A_B_DIAG__.native(30)');matrix=page.evaluate('()=>__ESM_A_C_DIAG__.matrix()');page.close();runs.append({'native':native,'matrix':matrix})
   profiles[profile]={'baselineNative':baseline,'runs':runs}
  browser.close()
 checks={'pageErrorsZero':not errors,'allMatricesPass':all(q['matrix']['pass'] for p in profiles.values() for q in p['runs']),'nativeRfAndRngExact':all(q['native']==p['baselineNative'] for p in profiles.values() for q in p['runs']),'repeatDeterministic':all(p['runs'][0]==p['runs'][1] for p in profiles.values()),'truthFieldAudit':all(not q['matrix']['truthAudit']['containsForbidden'] for p in profiles.values() for q in p['runs']),'selfTrackNetworkUnchanged':all(q['matrix']['checks']['selfTrackReportsExact'] for p in profiles.values() for q in p['runs']),'noObserverTrackOrAuthority':all(q['matrix']['checks']['observerTracksUntouched'] and q['matrix']['checks']['noAutomaticAuthority'] for p in profiles.values() for q in p['runs']),'linkDisconnectLocalOnly':all(q['matrix']['checks']['disconnectLeavesLocalPicture'] for p in profiles.values() for q in p['runs']),'geometryFallbacksHonest':all(q['matrix']['checks']['twoReceiverTdoaNotPoint'] and q['matrix']['checks']['clockFrequencyDegradeFallsBackHonestly'] for p in profiles.values() for q in p['runs'])}
 result={'schema':'AEGIS_ESM_A_COMMIT_C_GATE_1','status':'PASS' if all(checks.values()) else 'FAIL','elapsedS':time.monotonic()-started,'checks':checks,'pageErrors':errors,'inputs':{'baselineDiagnosticSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidateDiagnosticSha256':hashlib.sha256(CAND.read_bytes()).hexdigest()},'profiles':profiles}
 (HERE/'C_GATE.json').write_text(strict(result));print(strict({'status':result['status'],'elapsedS':result['elapsedS'],'checks':checks,'pageErrors':errors}));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
