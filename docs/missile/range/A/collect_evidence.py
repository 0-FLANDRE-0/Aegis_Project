"""Preserve raw receipts without rewriting their candidate HTML hashes."""
from pathlib import Path
import gzip,json,shutil
H=Path(__file__).resolve().parent;R=H.parents[3];src=Path('/tmp/range-a');C=R/'docs/envelope/C';E=H/'evidence';E.mkdir(exist_ok=True);(C/'evidence').mkdir(exist_ok=True)
def copy(a,b):
 b.parent.mkdir(parents=True,exist_ok=True)
 if a.suffix=='.json' and a.stat().st_size>500000:b=b.with_suffix(b.suffix+'.gz');b.write_bytes(gzip.compress(a.read_bytes(),9,mtime=0))
 else:shutil.copyfile(a,b)
for p in src.rglob('*'):
 if not p.is_file()or'__pycache__'in p.parts:continue
 rel=p.relative_to(src)
 if rel.parts[0]=='path':copy(p,C/'evidence/path-candidate'/Path(*rel.parts[1:]))
 elif p.name=='path.log':copy(p,C/'evidence/path-candidate.log')
 elif p.name=='goal-shots.json':copy(p,C/'results/goal-shots.json')
 elif p.name=='goal-shots.log':copy(p,C/'evidence/goal-shots.log')
 elif p.name=='live.js':continue
 elif p.name=='static.json':copy(p,E/'static-candidate.json')
 else:copy(p,E/rel)
# Correctly pair only identical scenarios: validation also contains individual faults.
cs=json.loads((H/'cases/validation.json').read_text());out=json.loads((src/'validation-release.json').read_text());rs=out['results'];pairs=[]
for i in range(len(cs)-1):
 a,b=cs[i:i+2]
 if a.get('enabled',True)is False and b.get('enabled',True)is True and {k:v for k,v in a.items()if k!='enabled'}=={k:v for k,v in b.items()if k!='enabled'}:pairs.append({'indices':[i,i+1],'case':a,'offHit':rs[i]['success'],'onHit':rs[i+1]['success']})
r={'pass':len(rs)==60 and len(pairs)==22 and all(not q['offHit']or q['onHit']for q in pairs)and not out['errors'],'cases':60,'abPairs':len(pairs),'premature':sum(q['offHit']and not q['onHit']for q in pairs),'records':pairs};(E/'validation60-acceptance.json').write_text(json.dumps(r,indent=2))
assert r['pass'];print('Evidence copied; validation60 paired by full case identity:',r['abPairs'])
