from pathlib import Path
import os,sys,subprocess,time,json
from harness import P,R,OUT
E=P/'evidence/regression';env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':OUT,'B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'};start=time.perf_counter()
with(E/'ui213-cpu2d.log').open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/'cpu2d_ui.py')],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
(E/'ui213-cpu2d-execution.json').write_text(json.dumps({'exit':r.returncode,'elapsedS':time.perf_counter()-start,'assertionChanges':0,'backend':'existing docs/pip/B/browser_backend.py CPU Canvas2D + actual WebGL'},indent=2)+'\n');print(r.returncode,time.perf_counter()-start);raise SystemExit(r.returncode)
