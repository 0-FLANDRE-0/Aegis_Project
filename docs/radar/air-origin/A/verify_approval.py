"""Approval guard checks and exact source/measurement audits; no game mutation."""
from pathlib import Path
import copy,hashlib,json,subprocess,tempfile
from approved_expectations import IDS,apply_pair,load_approval,physical,world_expectations
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence';O=E/'approval';O.mkdir(exist_ok=True)
PREVIOUS='891fa17a836313fdb134e26dbb6cb711fbbe44da';p=B/'approved-expectations.json';raw=(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes();q=load_approval(p,raw);checks={};sha=lambda b:hashlib.sha256(b).hexdigest()
old=lambda path:subprocess.check_output(['git','show',PREVIOUS+':'+path],cwd=R)
checks['exactlyFiveIds']=len(q['entries'])==5 and {r['id']for r in q['entries']}==IDS
checks['htmlByteIdentical']=raw==old('Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html')
checks['zeroOtherExpectedOrToleranceChanges']=q['otherExpectationsChanged']==q['tolerancesChanged']==0
def rejects(change,body=raw):
 v=copy.deepcopy(q);change(v)
 with tempfile.TemporaryDirectory(prefix='air-origin-approval-')as tmp:
  t=Path(tmp)/'approval.json';t.write_text(json.dumps(v))
  try:load_approval(t,body)
  except AssertionError:return True
 return False
checks['wrongHtmlRejected']=rejects(lambda v:None,raw+b' ')
checks['wrongCoreRejected']=rejects(lambda v:v.update(reviewedMainSha256='0'*64))
checks['missingApprovalRejected']=rejects(lambda v:v['entries'].pop())
checks['extraApprovalRejected']=rejects(lambda v:v['entries'].append(copy.deepcopy(v['entries'][0])))
checks['unapprovedCheckRejected']=rejects(lambda v:v['entries'][0].update(id='DDG_119_LATE_FLIGHT_IIA:raid:sameCombatRng'))
checks['changedValueWithoutHashRejected']=rejects(lambda v:v['entries'][0].update(newExpected={}))
paired=json.loads((E/'regression/AIR_ORIGIN_A/paired42/baseline-comparison.json').read_text())
case=next(r for r in paired['cases']if r['scenario']=='raid');base=copy.deepcopy(case['checks']);observations={};apply_pair(q,case['ship'],'raid',case['pair'],base,observations,physical)
checks['twoApprovedPairChecksPass']=base['samePhysicalState']and base['sameExistingObserverState']
checks['otherPairChecksUnchanged']=all(base[k]==v for k,v in case['checks'].items()if k not in ['samePhysicalState','sameExistingObserverState'])
bad=copy.deepcopy(case['pair']);bad['candidate']['state']['shipHP']-=1;values=copy.deepcopy(case['checks']);apply_pair(q,case['ship'],'raid',bad,values,{},physical);checks['futurePhysicalDriftStillFails']=values['samePhysicalState']is False
bad=copy.deepcopy(case['pair']);bad['candidate']['observers']['worldTimeS']+=1;values=copy.deepcopy(case['checks']);apply_pair(q,case['ship'],'raid',bad,values,{},physical);checks['futureObserverDriftStillFails']=values['sameExistingObserverState']is False
bad=copy.deepcopy(case['pair']);bad['baseline']['state']['shipHP']-=1
try:apply_pair(q,case['ship'],'raid',bad,dict(case['checks']),{},physical);checks['oldBaselineDriftRejected']=False
except AssertionError:checks['oldBaselineDriftRejected']=True
values=dict(case['checks']);values['sameCombatRng']=False;apply_pair(q,case['ship'],'raid',case['pair'],values,{},physical);checks['unapprovedFailureNotMasked']=values['sameCombatRng']is False
values=dict(case['checks']);before=dict(values);obs={};apply_pair(q,case['ship'],'idle',case['pair'],values,obs,physical);checks['nonRaidUntouched']=values==before and not obs
old_world={'idle':'fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc','combat':'b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1'};new_world=world_expectations(q,old_world);checks['onlyCombatHashUpdated']=new_world['idle']==old_world['idle']and new_world['combat']=='f546c836e56feac2e8823e2bfd9e27e32bf392d71c6aeeb36640f549e7fff078'
# Remove only the explicit approval plumbing. Everything else in these two
# shared test files must equal its pre-approval bytes, including all assertions.
path='docs/helicopter/F/verify_regression.py';s=(R/path).read_text()
blocks=['''    air_approved = None
    if getattr(a, 'approved_air_origin_baselines', None):
        assert not getattr(a, 'approved_raid_baseline', None), 'Choose one explicit baseline approval'
        sys.path.insert(0, str(ROOT / 'docs/radar/air-origin/A'))
        from approved_expectations import load_approval, apply_pair
        air_approved = load_approval(a.approved_air_origin_baselines, a.html.read_bytes())
''','''    if air_approved:
        needle = "                rows.append({'ship':ship"
        assert source.count(needle) == 1
        source = source.replace(needle, "                apply_air_origin_pair(AIR_ORIGIN_APPROVED,ship,scenario,pair,checks,observations,physical)\\n" + needle, 1)
''',"    p.add_argument('--approved-air-origin-baselines', type=Path, help='Only five explicitly approved AIR_ORIGIN_A expectations, guarded by exact HTML/core hashes')\n"]
for text in blocks:assert s.count(text)==1;s=s.replace(text,'',1)
scope_new="    scope = {'__file__': str(source_path), '__name__': '_helo_d_baseline', 'CLEAN_A_APPROVED': approved,\n             'AIR_ORIGIN_APPROVED': air_approved, 'apply_air_origin_pair': apply_pair if air_approved else None}\n";scope_old="    scope = {'__file__': str(source_path), '__name__': '_helo_d_baseline', 'CLEAN_A_APPROVED': approved}\n";assert s.count(scope_new)==1;s=s.replace(scope_new,scope_old,1);checks['pairedVerifierOtherwiseByteIdentical']=s.encode()==old(path)
path='docs/map/E/verify_delivery_world.py';s=(R/path).read_text();block="""import argparse
parser=argparse.ArgumentParser();parser.add_argument('--approved-air-origin-baselines',type=Path);args=parser.parse_args()
if args.approved_air_origin_baselines:
 sys.path.insert(0,str(R/'docs/radar/air-origin/A'));from approved_expectations import load_approval,world_expectations
 expected=world_expectations(load_approval(args.approved_air_origin_baselines,raw),expected)
""";assert s.count(block)==1;s=s.replace(block,'',1);checks['worldVerifierOtherwiseByteIdentical']=s.encode()==old(path)
source_records=[]
for r in q['sourceEvidence']:
 path=R/r['path'];checks['evidencePreserved:'+r['path']]=sha(path.read_bytes())==r['sha256']and path.read_bytes()==old(r['path']);source_records.append(r)
# The fourteen untouched suites (378 checks) have the same product, fixtures,
# assertions, adapters and dependency files. Retain their original evidence.
paths=subprocess.check_output(['git','diff','--name-only',PREVIOUS],cwd=R,text=True).splitlines();allowed={'docs/helicopter/F/verify_regression.py','docs/map/E/verify_delivery_world.py'};checks['noOtherSharedTestEdits']=all(x in allowed or x.startswith('docs/radar/air-origin/A/')or x.startswith('downloads/Aegis_SIM_v48_WIP_AIR_ORIGIN_A_')or x=='downloads/AIR_ORIGIN_A_SHA256SUMS.txt'for x in paths)
report={'pass':all(checks.values()),'checks':checks,'approvedExpectationCount':5,'otherExpectationsChanged':0,'tolerancesChanged':0,'gameHtmlChanged':False,'htmlSha256':sha(raw),'approvalSha256':sha(p.read_bytes()),'beforeAfterSources':source_records,'previousBranchHead':PREVIOUS,'domain378Policy':'Reuse the preserved prior 378 checks: exact product and unchanged suite/assertion/dependency bytes; rerun all affected paired42/world120 assertions separately.'}
(O/'guard-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(not report['pass'])
