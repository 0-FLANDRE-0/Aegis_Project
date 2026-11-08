#!/usr/bin/env python3
"""Recheck Commit-B/C gates after the Commit-D mobile-AOA association fix."""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'docs/pip/B'),str(ROOT/'docs/bunkerhill/K')]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
BASE=Path('/tmp/Aegis_SIM_v48_WIP_EMCON_B_ESM_DIAG.html');CAND=Path('/tmp/Aegis_SIM_v48_WIP_ESM_A_D_RECHECK_DIAG.html')
def strict(q):return json.dumps(q,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
def main():
 started=time.monotonic();errors=[];profiles={}
 with sync_playwright() as pw:
  browser=launch(pw)
  for profile in ('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'):
   p=load(browser,BASE.read_bytes(),ship=profile,errors=errors);native_base=p.evaluate('()=>__ESM_A_B_DIAG__.native(30)');p.close();runs=[]
   for _ in range(2):
    p=load(browser,CAND.read_bytes(),ship=profile,errors=errors);runs.append({'native':p.evaluate('()=>__ESM_A_B_DIAG__.native(30)'),'localizer':p.evaluate('()=>__ESM_A_B_DIAG__.localizer()'),'endToEnd':p.evaluate('()=>__ESM_A_B_DIAG__.endToEnd()'),'network':p.evaluate('()=>__ESM_A_C_DIAG__.matrix()')});p.close()
   profiles[profile]={'baselineNative':native_base,'runs':runs}
  browser.close()
 rows=[q for p in profiles.values() for q in p['runs']];checks={'pageErrorsZero':not errors,'nativeRfBearingRngExact':all(q['native']==p['baselineNative'] for p in profiles.values() for q in p['runs']),'bLocalizerPass':all(q['localizer']['pass'] for q in rows),'bNoTrackAuthority':all(q['endToEnd']['tracksBefore']==q['endToEnd']['tracksAfter'] and not q['endToEnd']['snapshot']['automaticEngagementAuthority'] for q in rows),'cNetworkMatrixPass':all(q['network']['pass'] for q in rows),'repeatDeterministic':all(p['runs'][0]==p['runs'][1] for p in profiles.values())}
 result={'schema':'AEGIS_ESM_A_D_PREDECESSOR_RECHECK_1','status':'PASS' if all(checks.values()) else 'FAIL','elapsedS':time.monotonic()-started,'checks':checks,'pageErrors':errors,'inputs':{'baselineSha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'candidateSha256':hashlib.sha256(CAND.read_bytes()).hexdigest()},'profiles':profiles}
 (HERE/'D_PREDECESSOR_RECHECK.json').write_text(strict(result));print(strict({'status':result['status'],'elapsedS':result['elapsedS'],'checks':checks,'pageErrors':errors}));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
