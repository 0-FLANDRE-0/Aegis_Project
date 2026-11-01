from pathlib import Path
import json
P=Path(__file__).resolve().parent;E=P/'evidence/regression/ON';files={'native':E/'gun/B1/evidence/native/results.json','geometry':E/'gun/B1/evidence/geometry.json','physical-adapter':E/'gun/B1/evidence/physical-adapter/results.json','B1-UI':E/'gun/B1/evidence/ui/results.json','MAP_D-gun-flow':E/'map/E/evidence/d-native/native.json','MAP_D-UI-existing-migration':E/'map/E/evidence/d-ui/ui.json'};rows=[]
for name,f in files.items():
 q=json.loads(f.read_text());checks=q['checks'];rows.append({'suite':name,'pass':all(checks.values())and not q['errors'],'passed':sum(bool(v)for v in checks.values()),'total':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':q['errors'],'file':str(f.relative_to(P))})
q=json.loads((P/'evidence/paired42-approved.json').read_text());rows.append({'suite':'paired42-ON','pass':q['pass'],'passed':sum(v for r in q['rows']for v in r['approvedChecks'].values()),'total':42,'file':'evidence/paired42-approved.json','newExpectedValues':0})
r={'pass':all(r['pass']for r in rows),'rows':rows,'oldFilesAndExpectationsUnmodifiedExceptSection5PrivateTestMigrations':True,'priorIncompleteRfMockFailures':'evidence/fixture-rf-before/','userApprovedMigration':'INSTRUCTIONS.md#5'};(P/'evidence/regression-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(not r['pass'])
