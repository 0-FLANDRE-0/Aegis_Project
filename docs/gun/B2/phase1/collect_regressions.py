"""Raw and reconciled results stay separate; never update an expectation."""
from pathlib import Path
import csv,gzip,json
P=Path(__file__).resolve().parent;E=P/'evidence';rows=[];failed=[]
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_text())
def audit(mode,label,path):
 q=read(path);checks=q.get('checks',{});assert isinstance(checks,dict)
 rr={'mode':mode,'suite':label,'file':path.relative_to(P).as_posix(),'pass':q.get('pass',all(checks.values())),'checks':len(checks),'passed':sum(v is True for v in checks.values()),'failed':[k for k,v in checks.items()if v is False]};rows.append(rr)
 for key in rr['failed']:failed.append({'mode':mode,'suite':label,'check':key,'file':rr['file']})
 return q
for mode in ['OFF','ON']:
 b=E/'regression'/mode;domain=[]
 if(b/'domain').exists():
  for folder in sorted(p for p in(b/'domain').iterdir()if p.is_dir()):
   for file in folder.glob('*.json'):
    q=read(file)
    if isinstance(q,dict)and isinstance(q.get('checks'),dict)and all(isinstance(v,bool)for v in q['checks'].values()):audit(mode,'domain:'+folder.name,file);domain.extend(q['checks'].values())
  rows.append({'mode':mode,'suite':'domain14 subtotal','checks':len(domain),'passed':sum(domain),'pass':len(domain)==378 and all(domain),'failed':[]})
 for label,rel in [('canonical UI88','map/E/evidence/ui88/ui.json'),('raw obsolete UI88','map/E/evidence/c2/GUN_B2_'+mode+'/ui/ui.json'),('MAP_D native','map/E/evidence/d-native/native.json'),('raw MAP_D UI','map/E/evidence/d-ui/ui.json'),('raw MAP_D edges','map/E/evidence/d-edges/edges.json')]:
  file=b/rel
  if file.exists():audit(mode,label,file)
 gb=E/'gun-regression'/mode
 for file in gb.rglob('*.json')if gb.exists()else[]:
  q=read(file)
  if isinstance(q,dict)and isinstance(q.get('checks'),dict)and all(isinstance(v,bool)for v in q['checks'].values()):audit(mode,'B1:'+str(file.relative_to(gb)),file)
for file in [E/'regression/execution.json',E/'gun-regression/execution.json']:
 if file.exists():rows.append({'suite':file.relative_to(P).as_posix(),'jobs':read(file)['rows']})
out={'rows':rows,'failedChecks':failed,'expectationsChanged':0,'note':'Raw failures are not normalized away. Existing AIR and B1 migrations are separate exact audits; new B2 ON differences need reviewer classification.'};(E/'regression-summary.json').write_text(json.dumps(out,indent=2)+'\n')
with(E/'regression-failures.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['mode','suite','check','file']);w.writeheader();w.writerows(failed)
print({'reports':len(rows),'rawFailedChecks':len(failed)})
