"""Verify limited diagnostic evidence; do not imply product regression approval."""
from pathlib import Path
import json,gzip,hashlib,ast,datetime,subprocess
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3]
checks={};kit=json.loads((H/'kit/MANIFEST.json').read_text())
for n,q in kit.items():
 b=(H/'kit'/n).read_bytes();checks['kit.'+n]=len(b)==q['bytes']and hashlib.sha256(b).hexdigest()==q['sha256']
for f in H.glob('*.py'):ast.parse(f.read_text())
ast.parse((H/'kit/probe_sm6_240km_rf.py').read_text());checks['pythonSyntax']=True
subprocess.run(['node','--check',str(H/'kit/observer.js')],check=True)
stub=json.loads(subprocess.check_output(['node',str(H/'kit/test_observer.cjs')]).decode());checks['stubContract']=stub['pass']
summary=json.loads((H/'all-modes/summary.json').read_text());first=json.loads((H/'native-first/summary.json').read_text());checks['browserErrors0']=not summary['errors']and not first['errors'];checks['allSixModes']=len(summary['summary'])==6;checks['nativeFirst2']=len(first['summary'])==2 and all(q['nativeObserverExact']for q in first['summary']);checks['nativeRepeated2']=all(q['nativeObserverExact']for q in summary['summary']if q['mode']=='NATIVE')
checks['nativeStageCompletedBeforeFullStage']=((H/'native-first/summary.json').stat().st_mtime<min(p.stat().st_mtime for p in(H/'all-modes').glob('*.json.gz')))
for v in ['DZT','HANDOFF']:
 a=(H/'native-first'/(v+'-NATIVE.json.gz')).read_bytes();b=(H/'all-modes'/(v+'-NATIVE.json.gz')).read_bytes();checks[v+'.nativeRawBitIdentical']=a==b
 reference=R/('docs/missile/fuze-zem/A/evidence/release-DZT/normals.json'if v=='DZT'else'docs/missile/launch-handoff/A/final-evidence/release-HANDOFF/normals.json')
 expected=json.loads(reference.read_text())['results'][152]
 checks[v+'.independentEntireReturnComparison']=all(json.loads(gzip.decompress(data))['result']==expected for data in [a,b])
sources=json.loads((H/'analysis/source-equivalence.json').read_text());checks['sourceProvenance']=sources['pass']and all(q['functionCount']==14 and all(f['presentInActualSelectedMain']for f in q['functions'])for q in sources['records'])
for q in json.loads((H/'input-provenance.json').read_text())['protectedFiles']:checks['unchanged.'+q['path']]=hashlib.sha256((R/q['path']).read_bytes()).hexdigest()==q['sha256']
calls=[]
for v in ['DZT','HANDOFF']:
 d=json.load(gzip.open(H/'all-modes'/(v+'-NATIVE.json.gz')));rr=[r for r in d['rows']if 147<=r['timeS']<=163];counts={n:sum((r['before']['calls'].get(n)or{}).get('count',0)for r in rr if(r['before']['calls'].get(n)or{}).get('calledThisTick'))for n in ['kappa','pn','apn','zem']};calls.append({'variant':v,'ticks':len(rr),'calls':counts,'phases':sorted({r['before']['phase']for r in rr})});checks[v+'.windowControlOwnership']=len(rr)==960 and counts=={'kappa':960,'pn':0,'apn':0,'zem':0}and all(r['before']['owner']=='KAPPA'and not r['before']['pitchover']for r in rr)
 del d
d=json.loads((H/'analysis/analysis.json').read_text());o=d['onsets']['HANDOFF/NATIVE'];checks['reportedOrder']=o['arhVelocityErrorRawMps>=10']['timeS']<o['firstARHSource']['timeS']<o['dragManeuverN>=100']['timeS']<o['firstCoast']['timeS'];checks['handoffBothCounterfactualsHit']=all(q['success']for q in summary['summary']if q['variant']=='HANDOFF'and q['mode']!='NATIVE');checks['handoffNativeRemainsMiss']=not next(q for q in summary['summary']if q['variant']=='HANDOFF'and q['mode']=='NATIVE')['success']
q={'schema':'AEGIS_SM6_240KM_RF_DIAGNOSTIC_A_VERIFICATION_1','diagnosticPass':all(checks.values()),'checks':checks,'windowCalls':calls,'newFlightCount':8,'nativeFlights':4,'counterfactualFlights':4,'productCodeChanges':0,'coefficientChanges':0,'shippingFixApproved':False,'fullEnvelopeSweep':False,'fullDomainRegressionRerun':False,'reviewedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat()}
(H/'verification.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'diagnosticPass':q['diagnosticPass'],'failed':[k for k,v in checks.items()if not v],'windowCalls':calls}));raise SystemExit(0 if q['diagnosticPass']else 1)
