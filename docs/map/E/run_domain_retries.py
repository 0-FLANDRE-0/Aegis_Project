from pathlib import Path
import json,sys,subprocess,time
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/domain-final';rows=[];start=time.perf_counter()
for name in ['isar-native','emcon-native']:
 with(E/(name+'-rerun.log')).open('w')as f:q=subprocess.run([sys.executable,'-u',str(H/'run_legacy_domain.py'),str(R/'Aegis_SIM_v48_WIP_MAP_E.html'),str(E/name),'--only',name],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'suite':name,'exitCode':q.returncode,'reason':'Preparation migrated from retired ARM tab/node; all original assertions retained'});print(rows[-1],flush=True);(E/'reruns.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
 if q.returncode:raise SystemExit(q.returncode)
