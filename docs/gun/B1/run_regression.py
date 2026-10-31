from pathlib import Path
import subprocess,sys,json,time,os,concurrent.futures,base64,gzip,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/regression-driver';E.mkdir(parents=True,exist_ok=True)
env={**os.environ,'PYTHONPATH':str(H/'test_support'),'GUN_B1_REGRESSION':'OFF','TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();main=gzip.decompress(base64.b64decode(__import__('re').search(rb'data-c55-index="13">([^<]+)',raw)[1]));approved=json.loads((R/'docs/map/E/approved-raid-baselines.json').read_text());source_entries=hashlib.sha256(json.dumps(approved['entries'],sort_keys=True).encode()).hexdigest();approved['gameCoreWithoutEnvelopeSha256']=hashlib.sha256(__import__('re').sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',main)).hexdigest();approved['gunB1TestGuard']={'expectedValuesChanged':False,'entriesSha256':source_entries,'reason':'New product core guard only; frozen user-approved expected values preserved; differences are reported, never adopted'};(H/'raid-reference-test-guard.json').write_text(json.dumps(approved,indent=2)+'\n')
sys.path.insert(0,str(R/'docs/viewport/A'));from verify_regressions import SUITES
jobs=[]
for name in SUITES:
 cmd=[sys.executable,str(R/'docs/map/E/verify_emcon_ui.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(E/'domain'/name)]if name=='emcon-ui'else[sys.executable,str(R/'docs/map/E/run_legacy_domain.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(E/'domain'/name),'--only',name]
 jobs.append(('domain-'+name,cmd,name in ['isar-ui','sov-visual']))
jobs+=[('paired-baseline',[sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'archive/v48/WIP_VP_A/Aegis_SIM_v48_WIP_VP_A.html'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(E/'paired-baseline'),'--baseline-only','--approved-raid-baseline',str(H/'raid-reference-test-guard.json')],False),('release300',[sys.executable,str(R/'docs/map/E/c2_browser.py'),'Aegis_SIM_v48_WIP_GUN_B1.html','GUN_B1','--suite','release'],False),('world120',[sys.executable,str(R/'docs/map/E/verify_delivery_world.py')],False),('webgl8',[sys.executable,str(R/'docs/envelope/D/run_observed_webgl.py'),'Aegis_SIM_v48_WIP_GUN_B1.html',str(E/'webgl8')],True)]
for n in ['run_final_ui','verify_d_native','verify_d_ui','verify_d_edges','verify_ew_h3','verify_e','verify_e_policy']:jobs.append((n,[sys.executable,str(R/'docs/map/E'/f'{n}.py')],n not in ['verify_d_native','verify_ew_h3']))
if len(sys.argv)>1:jobs=[j for j in jobs if any(s in j[0]for s in sys.argv[1:])]
start=time.perf_counter();rows=[]
def run(job):
 name,cmd,gpu=job
 if gpu:cmd=['flock','/tmp/aegis-gun-b1/gpu.lock',*cmd]
 t=time.perf_counter()
 with(E/(name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 return {'name':name,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for f in concurrent.futures.as_completed([pool.submit(run,j)for j in jobs]):
  r=f.result();rows.append(r);print(json.dumps(r),flush=True);(E/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'htmlSha256':hashlib.sha256(raw).hexdigest(),'autoAA':'OFF','expectedRaidEntriesSha256':source_entries,'referenceValuesChanged':False},indent=2)+'\n')
