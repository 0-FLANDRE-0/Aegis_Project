"""Apply the user's CLEAN_B outcome-only approval; exact expectations remain exact."""
from pathlib import Path
import base64,gzip,hashlib,json,re
H=Path(__file__).resolve().parent;R=H.parents[2];A=R/'docs/cleanup/A';H.mkdir(exist_ok=True)
def physical(v):
 if isinstance(v,dict):
  d={k:physical(x)for k,x in v.items()if k not in ['performance','aviation']}
  if v.get('schema')=='AEGIS_OFFBOARD_PORT_C_1':d.pop('helicopterImplemented',None);d['sources']=[s for s in d.get('sources',[])if s.get('sourceId')not in ['H1','H2']]
  if v.get('schema')=='AEGIS_SHIP_OBSERVER_C_1'and'deferred'in d:d['deferred']=[s for s in d['deferred']if s!='helicopterFlightAndSensors']
  return d
 if isinstance(v,list):return[physical(x)for x in v]
 return v
sha=lambda b:hashlib.sha256(b).hexdigest()
identity=lambda v:sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
manifest=json.loads((A/'approved-raid-baselines.json').read_text());proof=json.loads((A/'evidence/part1.json').read_text());metrics=next(c for c in proof['comparisons']if c['ship']=='CG_52_LATE_TICONDEROGA')
b=metrics['before']['KAPPA'];n=metrics['current'];checks={'sameKills':n['samNativeKills']==b['samNativeKills'],'sameEachTargetOutcome':n['allNativeTargetOutcomes']==b['allNativeTargetOutcomes'],'hpNotLower':n['shipHP']>=b['shipHP'],'waterNotHigher':n['waterM3']<=b['waterM3'],'moduleDamageNotHigher':all(n['moduleDamage'].get(k,0)<=b['moduleDamage'].get(k,0)for k in n['moduleDamage'].keys()|b['moduleDamage'].keys()),'survives':n['shipAlive'],'sameHorizon':n['endTimeS']==b['endTimeS']and n['endReason']==b['endReason']}
assert all(checks.values()),checks
history=json.loads((A/'evidence/history/LATEST/baseline-comparison.json').read_text());case=next(c for c in history['cases']if c['ship']=='CG_52_LATE_TICONDEROGA');before=case['pair']['baseline'];after=case['pair']['candidate']
def expectation(x):return{'physical':physical({k:x[k]for k in ['state','dynamics']}),'observer':physical(x['observers']),'loadedVlsCells':sum(c['type']!='EMPTY'for cells in x['state']['inventory']['vls'].values()for c in cells)}
old,new=expectation(before),expectation(after);raw=(R/'Aegis_SIM_v48_WIP_CLEAN_A.html').read_bytes();assert sha(raw)=='ceffbda64f3ffbefce4330b825e36408ea42bcc86abeddc27182843bd0b8ea45'
core=re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1])));assert sha(core)==manifest['gameCoreWithoutEnvelopeSha256']
manifest.update(revision='CLEAN_B',referenceHtmlSha256=sha(raw),evidence='docs/cleanup/B/evidence/cg-approval.json',nonApproved={},approvalPolicy={'source':'CLEAN_B 사용자 결정','outcomeMustBeSameOrBetter':True,'resourceConsumptionDifferencesAreRegressions':False})
manifest['entries']['CG_52_LATE_TICONDEROGA']={'scenario':'raid','classification':'a','assertions':['samePhysicalState','raidInventoryDeltaBounded','sameExistingObserverState'],'old':old,'expected':new,'oldHash':identity(old),'newHash':identity(new),'reason':'사용자 승인: 결과 동일, 자원 소모 차이만 존재'}
assert len(manifest['entries'])==2 and manifest['entries']['DDG_119_LATE_FLIGHT_IIA']==json.loads((A/'approved-raid-baselines.json').read_text())['entries']['DDG_119_LATE_FLIGHT_IIA']
(H/'approved-raid-baselines.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
proof={'schema':'AEGIS_CLEAN_B_CG_APPROVAL_1','checks':checks,'pass':all(checks.values()),'classification':'a','reason':manifest['entries']['CG_52_LATE_TICONDEROGA']['reason'],'before180':b,'current180':n,'old32':{'loadedVlsCells':old['loadedVlsCells'],'hash':identity(old)},'new32':{'loadedVlsCells':new['loadedVlsCells'],'hash':identity(new)},'guardedGameCoreSha256':sha(core),'updatedAssertions':3,'DDGAssertionsUnchanged':3,'sourceEvidence':'docs/cleanup/A/evidence/part1.json'}
(H/'evidence/cg-approval.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':proof['pass'],'approvedCG':3,'preservedDDG':3,'old32':proof['old32'],'new32':proof['new32']}))
