"""Execute unchanged B1 behavioral test assertions on the explicit B2 product.
Historical packaging/readback/old-engine reconstruction scripts are not tests of
this candidate; new native parity/static audits replace that provenance role.
"""
from pathlib import Path
import json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/gun-regression';E.mkdir(parents=True,exist_ok=True)
if len(sys.argv)>2 and sys.argv[1]=='--migration':
 kind=sys.argv[2];f=R/'docs/gun/B1/run_test_migrations.py';sys.argv=[str(f),kind];exec(compile(f.read_text(),str(f)+'::UNCHANGED_B1_MIGRATION','exec'),{'__file__':str(f),'__name__':'__main__'});raise SystemExit()
if len(sys.argv)>2 and sys.argv[1]=='--one':
 name=sys.argv[2];f=R/'docs/gun/B1'/(name+'.py');source=f.read_text();needle="R/'Aegis_SIM_v48_WIP_GUN_B1.html'";assert needle in source;source=source.replace(needle,"R/'Aegis_SIM_v48_WIP_GUN_B2.html'");scope={'__file__':str(f),'__name__':'__main__'};sys.argv=[str(f)];exec(compile(source,str(f)+'::EXPLICIT_B2_PRODUCT','exec'),scope);raise SystemExit()
start=time.perf_counter();rows=[]
for mode in ['OFF','ON']:
 out=E/mode;env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':mode,'B2_ALLOW_AUTO':'1','B2_OUT':str(out),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
 for name in ['verify_native','verify_auto','verify_geometry','verify_mod4','verify_physical_adapter','verify_mass_split','verify_ui','verify_ui_handoff','verify_label']:
  stamp=E/(mode+'-'+name+'.done.json')
  if stamp.exists():rows.append(json.loads(stamp.read_text()));continue
  t=time.perf_counter()
  with(E/(mode+'-'+name+'.log')).open('w')as f:r=subprocess.run([sys.executable,'-u',__file__,'--one',name],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  row={'mode':mode,'test':name,'exit':r.returncode,'elapsedS':time.perf_counter()-t};rows.append(row);stamp.write_text(json.dumps(row)+'\n');print(json.dumps(row),flush=True)
for mode in ['OFF','ON']:
 for kind in ['ui','edges']:
  stamp=E/(mode+'-migration-'+kind+'.done.json')
  if stamp.exists():rows.append(json.loads(stamp.read_text()));continue
  out=E/mode;env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':mode,'B2_ALLOW_AUTO':'0','B2_OUT':str(out),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'};t=time.perf_counter()
  with(E/(mode+'-migration-'+kind+'.log')).open('w')as f:r=subprocess.run([sys.executable,'-u',__file__,'--migration',kind],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT)
  row={'mode':mode,'test':'existing-B1-migration-'+kind,'exit':r.returncode,'elapsedS':time.perf_counter()-t};rows.append(row);stamp.write_text(json.dumps(row)+'\n');print(row,flush=True)
(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'assertionsChanged':0},indent=2)+'\n')
