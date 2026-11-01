"""Independent control lane: undo only the two CG installation origin values."""
from pathlib import Path
import json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression';at=time.perf_counter()
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':'Aegis_SIM_v48_WIP_CG_TURRET_A.html','B2_OUT':str(E/'origin-control'),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'1','CG_ORIGIN_CONTROL':'1'}
with(E/'native-origin-control.log').open('w')as f:q=subprocess.run([sys.executable,'-u',str(P/'run_regression.py'),'native'],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
(E/'native-origin-control-execution.json').write_text(json.dumps({'suite':'native-origin-control','exit':q.returncode,'elapsedS':time.perf_counter()-at},indent=2)+'\n');print(q.returncode);raise SystemExit(q.returncode)
