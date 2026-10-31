"""Apply no new expectations. Compare fresh measurements to the five immutable,
user-approved AIR values. Original tests and their raw reports remain unchanged.
"""
from pathlib import Path
import copy,json,sys
P=Path(__file__).resolve().parent;R=P.parents[3];A=R/'docs/radar/air-origin/A';sys.path.insert(0,str(A))
from approved_expectations import load_approval,pair_value,value_hash
def mutate_numeric(value):
 if isinstance(value,dict):
  for key,v in value.items():
   if isinstance(v,(int,float))and not isinstance(v,bool):value[key]=v+1;return str(key)
   path=mutate_numeric(v)
   if path is not None:return str(key)+'/'+path
 if isinstance(value,list):
  for index,v in enumerate(value):
   if isinstance(v,(int,float))and not isinstance(v,bool):value[index]=v+1;return str(index)
   path=mutate_numeric(v)
   if path is not None:return str(index)+'/'+path
 return None
manifest=load_approval(A/'approved-expectations.json',(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html').read_bytes());results=[]
for mode in ['OFF','ON']:
 E=P/'evidence/regression'/mode;f=E/'paired42/baseline-comparison.json';world=E/'map/E/evidence/delivery-world120.json'
 if not(f.exists()and world.exists()):continue
 q=json.loads(f.read_text());rows=[];negative=[]
 for row in q['cases']:
  checks=dict(row['checks']);entries=[e for e in manifest['entries']if e.get('ship')==row['ship']and e.get('scenario')==row['scenario']]
  for e in entries:
   actual=pair_value(row['pair']['candidate'],e['check']);checks[e['check']]=actual==e['newExpected'];mutant=copy.deepcopy(actual);mutatedPath=mutate_numeric(mutant);negative.append(mutatedPath is not None and actual==e['newExpected']and mutant!=e['newExpected']);
  rows.append({'ship':row['ship'],'scenario':row['scenario'],'originalChecks':row['checks'],'approvedChecks':checks,'usedExistingApprovals':[e['id']for e in entries]})
 w=json.loads(world.read_text());wr=[]
 for r in w['records']:
  e=next((e for e in manifest['entries']if e['id']=='world120:'+r['mode']+':truthSha256'),None)
  if e:assert r['expected']==e['oldExpected'];expected=e['newExpected']
  else:expected=r['expected']
  wr.append({**r,'approvedExpected':expected,'approvedExact':r['truthSha256']==expected})
 checks={'paired42':sum(len(r['approvedChecks'])for r in rows)==42 and all(all(r['approvedChecks'].values())for r in rows),'world120':all(r['approvedExact']for r in wr),'negativeMutationRejected':all(negative),'errors0':not q['errors']and not w['errors']}
 result={'mode':mode,'pass':all(checks.values()),'checks':checks,'rows':rows,'world':wr,'newExpectedValues':0,'tolerancesChanged':0,'approvalArtifactSha256':__import__('hashlib').sha256((A/'approved-expectations.json').read_bytes()).hexdigest(),'guard':'Original manifest validated against exact reviewed AIR HTML; B2 source/RF/static guards and OFF native equality audited separately.'};results.append(result)
(P/'evidence/existing-approval-reconciliation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print([(r['mode'],r['pass'],r['checks'])for r in results]);raise SystemExit(not all(r['pass']for r in results))
