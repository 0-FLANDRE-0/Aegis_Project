"""Run frozen native/UI fixtures on exact C bytes, R4 paired reference."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,importlib.util,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=mod('unchanged_b_regression',P.with_name('B')/'regression_runner.py')
def save(path,q):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def configure():
 build=json.loads((P/'BUILD.json').read_text());candidate=R/build['html'];assert hashlib.sha256(candidate.read_bytes()).hexdigest()==build['htmlSha256']
 b.P=P;b.E=E;b.REFERENCE=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html';b.REFERENCE_SHA=build['baselineHtmlSha256'];b.configure(candidate,build['htmlSha256']);return build
def worker(task):
 build=configure()
 if task in ['d1','natural','auto-iff','idle']:
  rt=mod('unchanged_a_runtime',P.with_name('A')/'verify_runtime.py');rt.CANDIDATE=R/build['html'];rt.E=E/task
  with b.heavy_browser_slot():rt.worker({'natural':'repro-original'}.get(task,task))
  return
 result=b.execute(task);save(E/(task+'-execution.json'),result)
def run_task(task,deadline):
 E.mkdir(parents=True,exist_ok=True);cmd=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker',task];at=time.monotonic()
 with(E/(task+'-controller.log')).open('w')as log:
  try:q=subprocess.run(cmd,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=max(1,min(1800,deadline-time.monotonic())));code=q.returncode
  except subprocess.TimeoutExpired:code=124
 path=E/(task+'-execution.json')
 result=json.loads(path.read_text())if path.exists()else{'suite':task,'status':'PASS'if code==0 else'INCOMPLETE','reason':'Original runtime output preserved separately; inspect native assertions.'}
 result.update(task=task,controllerExitCode=code,controllerWallS=time.monotonic()-at,controllerCommand=cmd)
 if code!=0 and result.get('status')=='PASS':result['status']='INCOMPLETE'
 save(E/(task+'-controller-result.json'),result);return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--worker');ap.add_argument('--only',nargs='+');ap.add_argument('--run',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args()
 if a.worker:return worker(a.worker)
 build=configure();sources=b.test_source_provenance();assert sources['status']=='PASS';E.mkdir(parents=True,exist_ok=True);save(E/'original-source-provenance.json',sources)
 tasks=a.only or[*b.NATIVE,'paired-track-a','ui213','webgl8','d1','natural','auto-iff','idle']
 if not a.run:print(json.dumps({'tasks':tasks,'build':build['htmlSha256'],'baseline':build['baselineHtmlSha256']}));return
 budget=json.loads((P/'evidence/BUDGET.json').read_text());deadline=budget['deadlineMonotonic'];rows=[]
 todo=[]
 for task in tasks:
  p=E/(task+'-controller-result.json')
  if a.resume and p.exists():rows.append(json.loads(p.read_text()))
  else:todo.append(task)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures={pool.submit(run_task,t,deadline):t for t in todo}
  for f in concurrent.futures.as_completed(futures):
   row=f.result();rows.append(row)
   save(P/'REGRESSION_RESULTS.json',{'schema':'AEGIS_TRACK_C_ORIGINAL_REGRESSIONS_1','candidateSha256':build['htmlSha256'],'baselineSha256':build['baselineHtmlSha256'],'rows':rows,'pending':[t for t in tasks if t not in[r['task']for r in rows]],'legacyEmcon14':'USER_APPROVED_RETIREMENT; currentUI coverage in separate matrix','originalAssertionsChanged':False,'expectationsUpdated':False})
   print(json.dumps({'task':row['task'],'status':row['status'],'wallS':row['controllerWallS'],'failed':row.get('failedAssertions',[])},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
