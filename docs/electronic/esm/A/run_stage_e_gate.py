#!/usr/bin/env python3
"""ESM_A Commit-E profile, lifecycle, persistence and inactive-SOV gate."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'docs/pip/B'),str(ROOT/'docs/bunkerhill/K')]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
BASE=Path('/tmp/Aegis_SIM_v48_WIP_EMCON_B_E_BASELINE_DIAG.html');CAND=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_E_DIAG.html');PRODUCT=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_E.html')
def strict(q):return json.dumps(q,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def main():
 started=time.monotonic();errors=[];profiles={}
 with sync_playwright() as pw:
  browser=launch(pw)
  page=load(browser,BASE.read_bytes(),ship='DDG_119_LATE_FLIGHT_IIA',errors=errors);sov_baseline=page.evaluate('()=>__ESM_A_E_BASELINE__.sov()');page.close()
  for profile in ('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'):
   runs=[]
   for _ in range(2):
    page=load(browser,CAND.read_bytes(),ship=profile,errors=errors);runs.append(page.evaluate('()=>__ESM_A_E_DIAG__.matrix()'));page.close()
   profiles[profile]=runs
  page=load(browser,CAND.read_bytes(),ship='DDG_119_LATE_FLIGHT_IIA',errors=errors);sov_candidate=page.evaluate('()=>__ESM_A_E_DIAG__.sov()');performance=page.evaluate('()=>__ESM_A_E_DIAG__.performance(40)');page.close();browser.close()
 matrices=[q for rows in profiles.values() for q in rows];product_text=PRODUCT.read_text(errors='ignore')
 checks={'pageErrorsZero':not errors,'allMatricesPass':all(q['pass'] for q in matrices),'repeatDeterministic':all(rows[0]==rows[1] for rows in profiles.values()),'actualProfilesDistinct':profiles['DDG_119_LATE_FLIGHT_IIA'][0]['path']['profile']['receiverId']!=profiles['CG_52_LATE_TICONDEROGA'][0]['path']['profile']['receiverId'],'ddgCgActualEndToEnd':all(q['path']['pass'] and q['network']['pass'] for q in matrices),'receiveEaIndependence':all(q['path']['checks']['receiverDisableDoesNotChangeEa'] for q in matrices),'silentReceiveTransmitZero':all(q['path']['checks']['silentPassiveReceiveContinues'] and q['path']['checks']['silentShipEmissionZero'] for q in matrices),'damageOfflineDisableFailClosed':all(q['path']['checks']['receiverDisableStopsReceive'] and q['path']['checks']['damageStopsReceive'] and q['network']['checks']['offlineStopsReceive'] for q in matrices),'syntheticCommonContract':all(q['synthetic']['pass'] for q in matrices),'saveLifecyclePass':all(q['save']['pass'] for q in matrices),'sovCandidatePass':all(sov_candidate['checks'].values()),'sovBaselineExact':sov_candidate['baseline']==sov_baseline,'performanceBudget':performance['pass'],'productDiagnosticAdapterAbsent':'__ESM_A_E_DIAG__' not in product_text and '__ESM_A_E_BASELINE__' not in product_text,'truthAndAuthorityZero':all(q['path']['checks']['observerTracksUntouched'] and q['path']['checks']['identityUnknown'] and q['network']['checks']['noAutomaticAuthority'] for q in matrices)}
 result={'schema':'AEGIS_ESM_A_COMMIT_E_GATE_1','status':'PASS' if all(checks.values()) else 'FAIL','elapsedS':time.monotonic()-started,'checks':checks,'pageErrors':errors,'inputs':{'baselineDiagnosticSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidateDiagnosticSha256':hashlib.sha256(CAND.read_bytes()).hexdigest(),'productSha256':hashlib.sha256(PRODUCT.read_bytes()).hexdigest()},'performance':performance,'sov':{'baseline':sov_baseline,'candidate':sov_candidate},'profiles':profiles}
 (HERE/'E_GATE.json').write_text(strict(result));print(strict({'status':result['status'],'elapsedS':result['elapsedS'],'checks':checks,'pageErrors':errors}));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
