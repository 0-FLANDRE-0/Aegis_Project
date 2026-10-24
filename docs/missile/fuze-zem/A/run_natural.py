"""Native onboard RF/EKF, with a controlled ship cue and constant ASM motion.

No ideal seeker state, track validity or detection flags are injected. Observer
wrappers record the unmodified native return values. Flight AI is excluded only
from the ASM target; the native damage prefix remains active.
"""
from pathlib import Path
import argparse,json,gzip,time,sys
from playwright.sync_api import sync_playwright
from browser_tools import H,R,launch,load_fleet,instrument,fixture
ap=argparse.ArgumentParser();ap.add_argument('--variants',nargs='*',default=['BASE','F','D','Z','T','ZT','DZT']);a=ap.parse_args();rows=[];errors=[];start=time.perf_counter();build=Path('/tmp/aegis-fuze-zem/builds');seed1={'rngSeed':1831565813,'navigationSeed':2047861954};seed2={'rngSeed':305419896,'navigationSeed':2654435769}
cases=[]
for w in ['SM2','SM2ER','SM6','ESSM']:
 for name,km,alt,v,cross,seed in [('MID_INBOUND',15 if w=='ESSM'else 30,5000,250,0,seed1),('CROSSING',10 if w=='ESSM'else 20,5000,0,250,seed1),('HIGH_NEAR_5_20',5,20000,0,0,seed1),('SEED2_INBOUND',15 if w=='ESSM'else 30,5000,250,0,seed2)]:cases.append({'caseId':w+'_'+name,'weapon':w,'rangeKm':km,'altM':alt,'targetSpeedMps':v,'crossSpeedMps':cross,**seed,'samples':False,'scenario':'NORMAL'})
for w in ['SM2','SM2ER','SM6','ESSM']:
 for scenario in ['LOSS','REACQUIRE','NO_ACQUISITION']:cases.append({'caseId':w+'_'+scenario,'weapon':w,'rangeKm':15 if w=='ESSM'else 60,'altM':5000,'targetSpeedMps':250,'scenario':scenario,'removeTarget':scenario=='LOSS','gapS':.65,**seed1,'samples':False})
(H/'natural-cases.json').write_text(json.dumps(cases,indent=2)+'\n')
with sync_playwright()as pw:
 b=launch(pw)
 for variant in a.variants:
  raw=(build/('Aegis_SIM_v48_WIP_FUZE_ZEM_A_'+variant+'.html')).read_bytes();p=load_fleet(b,instrument(raw,fixture()),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000);core=p.evaluate('__CORE_SELFTEST_FAILURES__');assert not core,core
  for case in cases:
   if case['scenario']!='NORMAL'and variant not in ['BASE','T','DZT','ZT']:continue
   q=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',case);rows.append({'variant':variant,'condition':case,'result':q});print(variant,case['caseId'],q.get('reason'),q.get('success'),q.get('closestM'),flush=True)
   (H/'results/natural.json.gz').write_bytes(gzip.compress(json.dumps({'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'method':__doc__},separators=(',',':')).encode(),9,mtime=0))
  p.close()
 b.close()
print(json.dumps({'flights':len(rows),'errors':errors,'elapsedS':time.perf_counter()-start}));sys.exit(0 if not errors else 1)
