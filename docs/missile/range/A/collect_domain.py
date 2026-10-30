"""Count the unchanged existing domain assertions, never alter their outcomes."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
paths=['helicopter-flight/native.json','aps153/native.json','isar-native/native.json','isar-classes/classes.json','isar-clock/clock.json','isar-ui/ui.json','emcon-native/native.json','emcon-ui/ui.json','harpoon-f1/native.json','harpoon-clock/ui-clock.json','sov-native/native.json','sov-casualty/casualty.json','sov-deployment/deployment.json','sov-visual/visual.json','paired-baseline/baseline-comparison.json']
rows=[]
for name in paths:
 f=a.directory/name;j=json.loads(f.read_text());checks=j.get('checks')
 count=len(checks) if isinstance(checks,dict) else sum(len(q['checks'])for q in j['cases'])
 rows.append({'path':name,'count':count,'pass':j['pass'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
progress=json.loads((a.directory/'progress.json').read_text());r={'schema':'AEGIS_RANGE_A_EXISTING_DOMAIN_ACCEPTANCE_1','pass':all(q['pass']for q in rows)and len(progress)==15 and all(q['exitCode']==0 for q in progress),'checks':sum(q['count']for q in rows),'suites':len(rows),'records':rows,'actionsUsed':False};r['pass']=r['pass']and r['checks']==420;a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2));print(json.dumps({'pass':r['pass'],'checks':r['checks'],'suites':r['suites']}));raise SystemExit(0 if r['pass']else 1)
