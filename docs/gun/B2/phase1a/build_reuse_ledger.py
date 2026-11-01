from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent;R=P.parents[3];OLD=P.parent/'phase1';sha=lambda b:hashlib.sha256(b).hexdigest();scope=json.loads((P/'evidence/scope.json').read_text());assert scope['pass'];files=['evidence/sam-exact-comparison.json','evidence/ew-reconciliation.json','evidence/existing-approval-reconciliation.json','evidence/canonical-on-ui-execution.json','evidence/unchanged-ui-reuse.json','evidence/regression/ON/webgl8/observed-world.json','evidence/label-final/results.json','evidence/physics/results.json'];items=[]
for f in files:
 p=OLD/f;assert p.exists();items.append({'report':p.relative_to(R).as_posix(),'sha256':sha(p.read_bytes()),'basis':'User section6 authorizes reuse. Whole main inverse proof limits game changes to3 approved symbols/data; corresponding SAM/RF/EKF/weapon permissions/UI/save functions remain exact. AutoAA OFF/no5inch requests in the reused SAM/common UI scenarios.','freshB2AExecution':False,'caveat':'Center-dependent detector geometry is fresh in geometry5/axis/positive RF mocks and1440 native shots. Historical physics tests certify unchanged algorithms, not a newly measured center.'if'physics'in f else None})
# The remaining378 original domain assertions retain their actual Phase1 records.
for p in sorted((OLD/'evidence/regression').glob('ON-domain-*.done.json')):items.append({'report':p.relative_to(R).as_posix(),'sha256':sha(p.read_bytes()),'basis':'Unchanged protected domain code, explicit section6 source-guard reuse','freshB2AExecution':False})
refs=P/'evidence/b2-reference';refs.mkdir(exist_ok=True);oldRows=[];sourceHashes={}
for f in sorted((OLD/'evidence/g7').glob('worker*.jsonl')):
 sourceHashes[f.relative_to(R).as_posix()]=sha(f.read_bytes())
 for line in f.open():
  r=json.loads(line)
  if r['count']in[1,4]and 419010<=r['seed']<=419024:oldRows.append((r,line))
for on in[False,True]:
 rr=[(r,l)for r,l in oldRows if r['on']==on];assert len(rr)==120
 if not on:assert all(r['result']['shots']==0 and not r['diagnostic']['bursts']and not r['diagnostic']['b2']['releases']for r,l in rr)
 p=refs/('g7-'+('on'if on else'off')+'120.jsonl');p.write_text(''.join(l for r,l in rr));items.append({'report':p.relative_to(R).as_posix(),'sha256':sha(p.read_bytes()),'freshB2AExecution':False,'basis':'Exact raw row subset of immutable Phase1; comparison reference ON or unchanged inactive-5inch path OFF.','rows':120})
q={'authorizedBy':'INSTRUCTIONS.md section6','sourceGuard':'evidence/scope.json','sourceGuardSha256':sha((P/'evidence/scope.json').read_bytes()),'oldSourceCommit':'c1d17cee4eb5d2a7ce00d0fa17b3c46a0908bff9','noRelabelingAsFresh':True,'sourceG7FileHashes':sourceHashes,'items':items,'phase1TrackedDiff':subprocess.check_output(['git','diff','--name-only','c1d17cee','--','docs/gun/B2/phase1'],cwd=R,text=True).strip()};assert not q['phase1TrackedDiff'];(P/'TEST_REUSE.json').write_text(json.dumps(q,indent=2)+'\n');print('Reuse ledger',len(items))
