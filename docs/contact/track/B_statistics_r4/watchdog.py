"""Independent hard wall deadline for this test controller and its children."""
from pathlib import Path
import argparse,json,os,signal,time
import psutil

P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--pid',type=int,required=True);a=ap.parse_args()
budget=json.loads((P/'evidence/BUDGET.json').read_text());proc=psutil.Process(a.pid)
birth=proc.create_time();record={'controllerPid':a.pid,'controllerCreateTime':birth,
    'deadlineMonotonic':budget['deadlineMonotonic'],'scope':'ONLY_THIS_CONTROLLER_AND_DESCENDANTS',
    'gameCodeChanged':False,'statisticsRuleChanged':False}
(P/'evidence/WATCHDOG.json').write_text(json.dumps(record,indent=2)+'\n')
while True:
    if not psutil.pid_exists(a.pid) or proc.create_time()!=birth or proc.status()==psutil.STATUS_ZOMBIE:
        record['result']='CONTROLLER_CLOSED_BEFORE_HARD_DEADLINE';break
    if time.monotonic()>=budget['deadlineMonotonic']:
        children=proc.children(recursive=True)
        for child in reversed(children):
            try:child.terminate()
            except psutil.Error:pass
        try:proc.terminate()
        except psutil.Error:pass
        _,alive=psutil.wait_procs(children+[proc],timeout=5)
        for child in alive:
            try:child.kill()
            except psutil.Error:pass
        record['result']='HARD_3H_CAP_STOPPED_INCOMPLETE';break
    time.sleep(1)
record['endedMonotonic']=time.monotonic()
(P/'evidence/WATCHDOG.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
