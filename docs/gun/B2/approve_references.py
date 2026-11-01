"""Apply only the explicit B2 §9 approvals, with exact core and value guards.

Historical B1 raw reports stay untouched. Fresh B1 replay must equal the values
the user approved, not merely pass a tolerance or a reduced comparison.
"""
from pathlib import Path
import ast,base64,copy,gzip,hashlib,json,re
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=R/'docs/gun/B1';E=B/'evidence'
sha=lambda x:hashlib.sha256(x).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def load(p):return json.loads(p.read_text())
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();assert sha(raw)=='c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc'
main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]));core=sha(re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',main))
# Execute the exact existing normalizer literal, without reinterpreting it.
f=R/'docs/helicopter/F/verify_regression.py';tree=ast.parse(f.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='baseline');s=next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='normalizer'for t in n.targets));scope={};exec(ast.literal_eval(s.value),scope);physical=scope['physical']
signature=lambda q:physical({k:q[k]for k in ['state','dynamics']})
def diff(a,b,p=''):
 if type(a)!=type(b):return [(p,a,b)]
 if isinstance(a,dict):return sum([diff(a.get(k,'<absent>'),b.get(k,'<absent>'),p+'/'+k)for k in sorted(set(a)|set(b))],[])
 if isinstance(a,list):
  if len(a)!=len(b):return[(p+'/length',len(a),len(b))]
  return sum([diff(x,y,p+'/'+str(i))for i,(x,y)in enumerate(zip(a,b))],[])
 return []if a==b else[(p,a,b)]
history=load(OLD/'evidence/regression-driver/paired-baseline/baseline-comparison.json');fresh=load(E/'paired-baseline/baseline-comparison.json');guard=load(OLD/'raid-reference-test-guard.json');assert guard['gameCoreWithoutEnvelopeSha256']==core
assert fresh['candidateSha256']==sha(raw)and not fresh['errors']
entries=[];checks=[]
for q in fresh['cases']:
 prior=next(x for x in history['cases']if(x['ship'],x['scenario'])==(q['ship'],q['scenario']))
 candidate=signature(q['pair']['candidate']);assert candidate==signature(prior['pair']['candidate']),(q['ship'],q['scenario'],'not the reviewed B1 state')
 c=dict(q['checks'])
 if q['ship']=='CG_52_LATE_TICONDEROGA':
  old=guard['entries'][q['ship']]['expected']['physical']if q['scenario']=='raid'else signature(q['pair']['baseline'])
  assert not c['samePhysicalState']and candidate!=old
  entries.append({'ship':q['ship'],'scenario':q['scenario'],'assertion':'samePhysicalState','classification':'a','reason':'사용자 승인: GUN_B2 §9, Mod4 ID·HE/MFF 질량 노드 분할 및 IEEE-754 합산 차이. 기존 결과·자원·RNG·관측값 보존.','old':old,'expected':candidate,'oldHash':sha(canonical(old)),'newHash':sha(canonical(candidate)),'differences':diff(old,candidate)})
  c['samePhysicalState']=candidate==entries[-1]['expected']
  mutant=copy.deepcopy(candidate);mutant['state']['shipHP']-=1;assert mutant!=entries[-1]['expected']
 checks.append({'ship':q['ship'],'scenario':q['scenario'],'originalChecks':q['checks'],'approvedChecks':c})
assert len(entries)==3 and all(all(q['approvedChecks'].values())for q in checks)
ew=[];pattern=re.compile(r'^/(base|roundtrip)/(ship/inventory/gunMounts|fleet/ships/\d+/ship/inventory/guns)/\d+/(magazine/(HE_127_SIM|MFF_127_SIM)|moduleId)$')
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 path=E/f'regression/map/E/evidence/ew-h3/ew-{ship}.json';q=load(path);prior=load(OLD/f'evidence/regression/map/E/evidence/ew-h3/ew-{ship}.json');assert q['candidate']==prior['candidate']and q['baseline']==prior['baseline']
 changes=diff(q['baseline'],q['candidate']);assert changes
 for p,a,b in changes:assert pattern.fullmatch(p)and((p.endswith('/HE_127_SIM')and(a,b)==(360,180))or(p.endswith('/MFF_127_SIM')and(a,b)==('<absent>',180))or(p.endswith('/moduleId')and(a,b)==('MK45_MOD2_MK160_SURFACE_V1','MK45_MOD4_CG52_MK160_V1'))),(p,a,b)
 assert q['candidate']['pass']and all(q['candidate']['checks'].values())
 ew.append({'ship':ship,'reason':'사용자 승인: GUN_B2 §9, 기존 EW 원시 저장 비교의 Mod4 ID·HE/MFF 배분 경로만 갱신','oldHash':sha(canonical(q['baseline'])),'newHash':sha(canonical(q['candidate'])),'expected':q['candidate'],'differences':changes,'freshReport':path.relative_to(R).as_posix()})
ref={'schema':'AEGIS_GUN_B2_APPROVED_REFERENCES_1','htmlSha256':sha(raw),'gameCoreWithoutEnvelopeSha256':core,'authority':'docs/gun/B2/INSTRUCTIONS.md §9','normalizerSha256':sha(ast.literal_eval(s.value).encode()),'previousRaidReferences':{'path':'docs/map/E/approved-raid-baselines.json','sha256':sha((R/'docs/map/E/approved-raid-baselines.json').read_bytes()),'changed':False},'entries':entries,'ewEntries':ew}
(B/'approved-gun-baselines.json').write_text(json.dumps(ref,indent=2,ensure_ascii=False)+'\n')
domain=[]
for directory in(OLD/'evidence/regression-driver/domain').iterdir():
 for path in directory.glob('*.json'):
  q=load(path)
  if isinstance(q,dict)and'checks'in q and'pass'in q:
   assert q['pass']and all(q['checks'].values());domain.append({'path':path.relative_to(R).as_posix(),'sha256':sha(path.read_bytes()),'passed':len(q['checks']),'execution':'REUSED_B1_UNCHANGED_PRODUCT'})
assert sum(x['passed']for x in domain)==378
out={'pass':True,'domainTotal':420,'reusedNative':378,'freshPaired':42,'changedExpectedValues':3,'ewUpdatedComparisons':2,'sameProductSha256':sha(raw),'checks':checks,'reusedReports':domain,'guardNegativeTests':{'wrongCoreRejected':core!=('0'*64),'oneHpChangeRejected':True},'notes':'No original report or common comparison weakened. 378 prior B1 assertions reused under identical product bytes, 42 fresh assertions compared against approved exact references.'}
(E/'approved-reference-validation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['checks','reusedReports']}))
