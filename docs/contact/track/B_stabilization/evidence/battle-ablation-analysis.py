"""Independent feature comparison; immutable raw input, no game calls."""
from pathlib import Path
import collections,gzip,hashlib,importlib.util,json

P=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('battle_codec',P/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
TAG='candidate-active-NATURAL_SATURATION_13'
def load(folder,tag=TAG):
 path=folder/(tag+'.json.gz')
 if not path.exists():return None
 summary=folder/(tag+'-SUMMARY.json');return json.loads(summary.read_text()),b.decode_capture(json.loads(gzip.decompress(path.read_bytes())))
def first_difference(a,z):
 for i,(x,y)in enumerate(zip(a['associationReturns'],z['associationReturns'])):
  same_context=all(x[k]==y[k]for k in ['step','route','observerShip'])
  pair=lambda q:([(p['i'],p['id'])for p in q['actualSelectedPairs']],q['actualHeldPlots'],q['actualHeldTracks'])
  if not same_context or pair(x)!=pair(y):return {'index':i,'sameNativeCallContext':same_context,'old':x,'new':y}
 return None
def main():
 frozen=P/'evidence/battle-final';inputs={'old-active':load(frozen,'old-active-NATURAL_SATURATION_13'),'combined':load(frozen),'s-only':load(P/'evidence/battle-ablation/s-only'),'large-only':load(P/'evidence/battle-ablation/large-only')};pending=[k for k,v in inputs.items()if v is None];a=inputs['old-active'][1];rows=[]
 for label,value in inputs.items():
  if value is None:continue
  summary,r=value;events=r['events'];hit=[e for e in events if e['kind']=='NATIVE_SHIP_HIT_RECORD'];damaging=[h for h in hit if(h['hit'].get('dmg')or 0)>0 and not h['hit'].get('miss')];miss=[h for h in hit if h['hit'].get('miss')];kinds=collections.Counter(t['retirement'].get('cause')or t.get('_deathReason')or t.get('_wip113Outcome')or('ALIVE'if t.get('alive')else'UNKNOWN')for t in r['targets']);initialids={t['id']for t in r['targets']};unique_kills=sorted({e['target']['id']for e in events if e['kind']=='NATIVE_INTERCEPT_RESULT'and e['result']in ['KILL','STRUCT_FAIL']and e['target']['id']in initialids});reasons=collections.Counter(c.get('reason')or'NONE'for q in r['associationReturns']for c in q['components']);worse=[]
  if r['final']['ship']['shipHP']<a['final']['ship']['shipHP']:worse.append('LOWER_HP')
  before_mod=a['final']['ship']['damage']['moduleDamage'];after_mod=r['final']['ship']['damage']['moduleDamage'];module_higher={k:{'before':before_mod.get(k,0),'after':v}for k,v in after_mod.items()if v>before_mod.get(k,0)}
  if module_higher:worse.append('SOME_MODULE_DAMAGE_HIGHER')
  if r['end']['remainingInitialThreats']>a['end']['remainingInitialThreats']:worse.append('MORE_LIFECYCLE_UNRESOLVED_INITIAL_ASMS')
  rows.append({'variant':label,'status':summary['status'],'productSha256':summary['productSha256'],'setupSha256':summary['setupSha256'],'fixtureSha256':summary['fixtureSha256'],'postValidation':summary['postValidation'],'end':r['end'],'hp':r['final']['ship']['shipHP'],'counts':r['counts'],'initialNativeTerminalKinds':dict(kinds),'uniqueInitialInterceptKilledOrStructuralFailIds':unique_kills,'shotEffectsSeparateFromUniquePhysicalTargets':True,'damagingHitHistoryRecords':len(damaging),'missHistoryRecords':len(miss),'damagingHitHistoryTimeline':damaging,'missHistoryTimeline':miss,'actualReasonCounts':dict(reasons),'actualHoldEpisodes':len(r['holdDurations']),'maxHoldToNextAcceptedUpdateS':max((h['durationS']for h in r['holdDurations']),default=0),'firstAppliedDifferenceVsOldActive':None if label=='old-active'else first_difference(a,r),'launchTimeline':[e for e in events if e['kind']=='NATIVE_WEAPON_LAUNCH'],'effectTimeline':[e for e in events if e['kind']=='NATIVE_INTERCEPT_RESULT'],'nativeInitialTargetStates':r['targets'],'nativeModuleDamage':after_mod,'moduleDamageHigherVsOldActive':module_higher,'worseningIndicatorsVsOldActive':worse,'nativeSources':summary['nativeSourceHashes'],'releaseApproved':False})
 value={'schema':'AEGIS_TRACK_B_INDEPENDENT_FEATURE_ABLATION_RESULTS_1','status':'PENDING'if pending else'CAUSE_REVIEW_REQUIRED','pending':pending,'rows':rows,'frozen19RecordsChanged':False,'physicalCoefficientsOrExpectationsChanged':False,'interpretation':'Diagnostic variants isolate algorithm features, not shipping products or tuned performance. Native defeat/lifecycle/PK outcomes are retained. No automatic approval.','releaseApproved':False};out=P/'evidence/battle-ablation';out.mkdir(parents=True,exist_ok=True);(out/'RESULTS.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 lines=['# Independent natural13 feature ablation — '+value['status'],'','All variants use seed419027 and the same unchanged native battle helper, inventory, settings and90s maximum. The frozen19-page evidence is unchanged.','', '| Variant | Native result | End s | HP | Initial native terminal kinds | Actual HOLD plots/tracks | Damaging/miss history records |','|---|---|---:|---:|---|---:|---:|']
 for r in rows:lines.append(f"| {r['variant']} | {r['status']} | {r['end']['timeS']:.3f} | {r['hp']} | {json.dumps(r['initialNativeTerminalKinds'])} | {r['counts']['actualHeldPlotAppearances']}/{r['counts']['holds']} | {r['damagingHitHistoryRecords']}/{r['missHistoryRecords']} |")
 lines+=['','Hit-history records are callbacks, not unique physical-leaker counts. Unique initial-target kill/structural retirement IDs and all native damage/behavior fields are retained separately. Present system damage0 means native zero damage; missing remains absent. Alive at horizon is lifecycle-unresolved and is not silently counted as a kill.','', 'All source receipts, first applied return differences, native timelines and module values are in RESULTS.json. Some modules may worsen while other outcomes improve; HP0 does not waive those differences. Diagnostic results do not approve a product.'];(out/'RESULTS.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'status':value['status'],'pending':pending,'rows':[{'variant':r['variant'],'end':r['end'],'physicalKinds':r['initialNativeTerminalKinds'],'damagingRecords':r['damagingHitHistoryRecords'],'worse':r['worseningIndicatorsVsOldActive']}for r in rows]}))

if __name__=='__main__':main()
