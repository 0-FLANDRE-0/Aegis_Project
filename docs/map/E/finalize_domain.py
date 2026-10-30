"""Aggregate actual completed suite files; preserve failed preparation attempts."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/domain-final';initial=json.loads((E/'progress.json').read_text());reruns=json.loads((E/'reruns.json').read_text());rows=[];total=0
for name in ['helicopter-flight','aps153','isar-native','isar-classes','isar-clock','isar-ui','emcon-native','emcon-ui','harpoon-f1','harpoon-clock','sov-native','sov-casualty','sov-deployment','sov-visual']:
 qs=[]
 for p in(E/name).glob('*.json'):
  q=json.loads(p.read_text())
  if isinstance(q,dict)and isinstance(q.get('checks'),dict)and'pass'in q:qs.append((p,q))
 assert len(qs)==1,(name,len(qs));p,q=qs[0];count=len(q['checks']);total+=count;row={'suite':name,'exitCode':0 if q['pass']and all(q['checks'].values())else 1,'assertions':count,'evidence':p.relative_to(E).as_posix(),'htmlSha256':q.get('htmlSha256',q.get('sha256'))};old=next((x for x in initial if x['suite']==name),None);retry=next((x for x in reruns['rows']if x['suite']==name),None)
 if old:row['initialExitCode']=old['exitCode']
 if retry:row['rerun']=retry
 rows.append(row)
assert total==378
pair=json.loads((E/'paired-baseline/baseline-comparison.json').read_text());checks=[v for q in pair['cases']for v in q['checks'].values()];assert len(checks)==42;rows.append({'suite':'paired-baseline','exitCode':0 if all(checks)else 1,'assertions':42,'htmlSha256':pair['candidateSha256']});out={'pass':all(r['exitCode']==0 for r in rows),'rows':rows,'domainAssertions':total+len(checks),'initialAttempts':initial,'reruns':reruns,'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes()).hexdigest(),'executionNotes':['Two old ARM preparations timed out, then passed with unchanged assertions through test-only native listener adapter','Long tool session expired before sov-visual/paired-baseline; these jobs reran in a detached durable runner','Native domain evidence from prior display-only build retains its actual SHA and byte-equivalence proof']};(E/'execution.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':out['domainAssertions'],'failed':[r['suite']for r in rows if r['exitCode']]}));assert out['pass']
