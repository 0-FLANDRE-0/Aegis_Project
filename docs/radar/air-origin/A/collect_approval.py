"""Current approved results, with explicit fresh/cached provenance."""
from pathlib import Path
import csv,json
from approved_expectations import load_approval,pair_value,physical,value_hash
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence';O=E/'approval';load=lambda p:json.loads(p.read_text())
manifest=load_approval(B/'approved-expectations.json',(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes());old=load(E/'regression/AIR_ORIGIN_A/paired42/baseline-comparison.json');new=load(O/'fresh/paired42/baseline-comparison.json');world=load(O/'fresh/map/E/evidence/delivery-world120.json');summary=load(E/'summary.json');guards=load(O/'guard-checks.json');execution=load(O/'execution.json')
assert execution['pass']and guards['pass']and new['pass']and world['pass']
changes=[]
for a,b in zip(old['cases'],new['cases']):
 assert(a['ship'],a['scenario'])==(b['ship'],b['scenario'])
 for side in ['baseline','candidate']:
  for key in ['samePhysicalState','sameExistingObserverState']:
   assert pair_value(a['pair'][side],key)==pair_value(b['pair'][side],key),'FRESH_RUN_CHANGED_PHYSICAL_OR_OBSERVER_RESULT'
  assert a['pair'][side]['rng']==b['pair'][side]['rng']
 for check,before in a['checks'].items():
  after=b['checks'][check]
  if before!=after:changes.append({'id':f"{a['ship']}:{a['scenario']}:{check}",'beforePass':before,'afterPass':after})
 assert all(b['checks'].values())
 if a['scenario']=='raid':
  approval=b['observations']['airOriginApproval'];assert approval['originalChecks']==a['checks']and len(approval['applied'])==2
assert len(changes)==4
for a in world['records']:
 before=next(x for x in summary['world']if x['mode']==a['mode']);assert a['truthSha256']==before['afterHash']
 if a['mode']=='combat':changes.append({'id':'world120:combat:truthSha256','beforePass':False,'afterPass':a['same'],'oldExpected':before['beforeHash'],'newExpected':a['expected']})
assert {r['id']for r in changes}=={r['id']for r in manifest['entries']}and len(changes)==5
reused=[r for r in summary['domain']['AIR_ORIGIN_A']['suites']if r['suite']!='paired42'];assert sum(r['total']for r in reused)==sum(r['passed']for r in reused)==378
fresh=sum(len(r['checks'])for r in new['cases']);assert fresh==42 and not new['errors']and not world['errors']
q={'pass':True,'approvedExpectationCount':5,'otherExpectationsChanged':0,'tolerancesChanged':0,'gameHtmlChanged':False,'htmlSha256':world['htmlSha256'],'domain':{'passed':420,'total':420,'freshPaired':42,'cachedUnchangedSuites':378,'reusePolicy':'Same HTML SHA and unchanged 14 suite/assertion/fixture/dependency files. All prior evidence is preserved verbatim; no new execution claim for the cached 378.'},'world120':world['records'],'checksChanged':changes,'guards':{'passed':sum(guards['checks'].values()),'total':len(guards['checks'])},'freshMeasurementsIdenticalToReviewedEvidence':True,'freshElapsedS':execution['elapsedS'],'oldSummaryPath':'docs/radar/air-origin/A/evidence/summary.json','expectedValuesUpdatedWithUserApproval':True,'mainMerged':False,'gunB2Rebased':False,'gunB2Phase1Started':False}
(O/'summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
with(O/'expectation-changes.tsv').open('w',newline='')as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['id','old_value_sha256','new_value_sha256','old_expected_literal_if_scalar','new_expected_literal_if_scalar','cause_path'])
 for r in manifest['entries']:w.writerow([r['id'],r['oldValueSha256'],r['newValueSha256'],r['oldExpected']if isinstance(r['oldExpected'],str)else'Full value in approved-expectations.json',r['newExpected']if isinstance(r['newExpected'],str)else'Full value in approved-expectations.json',json.dumps(r['causePath'],ensure_ascii=False,separators=(',',':'))])
print(json.dumps({'pass':True,'domain':'420/420 (42 fresh + 378 cached)','world120':'2/2 fresh','approved':len(changes),'otherChanges':0,'elapsedS':execution['elapsedS']}))
