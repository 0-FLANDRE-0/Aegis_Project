"""Serial five-inch regression lane; surface first-hit and unrelated suites are source-guarded."""
from pathlib import Path
import json, os, signal, subprocess, sys, time
from deadline import check, remaining

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression';E.mkdir(parents=True,exist_ok=True)
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-f/docs/performance/F/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_ALLOW_AUTO':'1','B2_OUT':str(E/'ON'),'PYTHONPATH':str(P/'test_support')}
jobs=[]
for name in ['verify_native','verify_geometry','verify_physical_adapter','verify_ui','map_d_gun_flow']:
    jobs.append((name,[sys.executable,'-u',str(P/'adapted'/(name+'.py'))],{**env,'B2_ALLOW_AUTO':'1' if name!='map_d_gun_flow' else '0'}))
jobs.append(('map_d_ui_existing_B1_migration',[sys.executable,str(R/'docs/gun/B1/run_test_migrations.py'),'ui'],{**env,'B2_ALLOW_AUTO':'0'}))
jobs.append(('paired42_ON',[sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(E/'ON/paired42'),'--baseline-only'],{**env,'B2_ALLOW_AUTO':'0'}))
rows=[];started=time.perf_counter()
for name,cmd,cfg in jobs:
    check();at=time.perf_counter();log=E/(name+'.log')
    with log.open('w') as stream:
        process=subprocess.Popen(cmd,cwd=R,env=cfg,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        try: exit_code=process.wait(timeout=remaining())
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL);process.wait()
            exit_code=124
    row={'name':name,'exit':exit_code,'elapsedS':time.perf_counter()-at,'log':str(log.relative_to(P))};rows.append(row)
    (E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-started,'deadlineRemainingS':remaining()},indent=2)+'\n')
    print(json.dumps(row),flush=True)
    if exit_code: break
raise SystemExit(0 if rows and len(rows)==len(jobs) and all(not x['exit'] for x in rows) else 1)
