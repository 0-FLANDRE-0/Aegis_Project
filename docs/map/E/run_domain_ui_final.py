from pathlib import Path
import subprocess,json,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/domain-final';p=E/'reruns.json';result=json.loads(p.read_text());start=time.perf_counter()
for name in ['isar-ui','emcon-ui']:
 cmd=[sys.executable,'-u',str(H/'verify_emcon_ui.py'),str(R/'Aegis_SIM_v48_WIP_MAP_E.html'),str(E/name)]if name=='emcon-ui'else[sys.executable,'-u',str(H/'run_legacy_domain.py'),str(R/'Aegis_SIM_v48_WIP_MAP_E.html'),str(E/name),'--only',name]
 if name=='isar-ui':cmd=['flock','/tmp/aegis-map-e/gpu.lock',*cmd]
 with(E/(name+'-final.log')).open('w')as log:q=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 row={'suite':name,'exitCode':q.returncode,'reason':'Final UI rerun after presentation-only inventory/scaled-layout fix'};result['rows']=[r for r in result['rows']if r['suite']!=name]+[row];result['finalUiElapsedS']=time.perf_counter()-start;p.write_text(json.dumps(result,indent=2)+'\n');print(row,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
