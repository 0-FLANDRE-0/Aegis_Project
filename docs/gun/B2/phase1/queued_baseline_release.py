from pathlib import Path
import os,subprocess,sys,time,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/baseline-4c-release300';E.mkdir(parents=True,exist_ok=True)
while not(P/'evidence/label-preview/results.json').exists():time.sleep(10)
raw=(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes();assert hashlib.sha256(raw).hexdigest()=='4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb'
env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':'OFF','B2_HTML':'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html','B2_OUT':str(E),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'};start=time.perf_counter()
with(E/'run.log').open('w')as f:r=subprocess.run([sys.executable,'-u',str(R/'docs/map/E/c2_browser.py'),str(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html'),'AIR_ORIGIN_A_B2_BASELINE','--suite','release'],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
(E/'execution.json').write_text(json.dumps({'exit':r.returncode,'elapsedS':time.perf_counter()-start,'baselineSha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
raise SystemExit(r.returncode)
