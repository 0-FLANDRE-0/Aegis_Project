"""Offline R3/R4 moderate battle difference review. No new native calls."""
from pathlib import Path
import gzip,hashlib,importlib.util,itertools,json
P=Path(__file__).resolve().parents[1];R3=P.with_name('B_stabilization_r3');R1=P.with_name('B_stabilization')
s=importlib.util.spec_from_file_location('codec',R1/'battle.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
def load(folder):
 p=folder/'candidate-active-NATURAL_SATURATION_6.json.gz'
 return b.decode_capture(json.loads(gzip.decompress(p.read_bytes()))),{'path':str(p.relative_to(P.parent)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def first(a,z,project=lambda v:v):
 for i,(x,y)in enumerate(itertools.zip_longest(a,z)):
  px=project(x)if x is not None else None;py=project(y)if y is not None else None
  if px!=py:return {'index':i,'R3':px,'R4':py}
 return None
def sig(q,nis=True):
 return {k:q[k]for k in ['step','timeS','route','observerShip','actualHeldPlots','actualHeldTracks']}|{'actualSelectedPairs':q['actualSelectedPairs']if nis else[{k:x[k]for k in ['i','id']}for x in q['actualSelectedPairs']]}
def main():
 a,ap=load(R3/'evidence/battle-active-six');z,zp=load(P/'evidence/battle-final-matrix')
 event=lambda r,k:[x for x in r['events']if x['kind']==k]
 launch=first(event(a,'NATIVE_WEAPON_LAUNCH'),event(z,'NATIVE_WEAPON_LAUNCH'))
 snapshot=first(a['samples'],z['samples'],lambda q:{'step':q['step'],'timeS':q['timeS'],'shipHP':q['shipHP'],'inventory':q['inventory'],'ownPositionM':q['ownPositionM'],'tracks':q['tracks'],'truthAfterAction':q['truthAfterAction']})
 if snapshot:
  snapshot={'index':snapshot['index'],'R3Step':snapshot['R3']['step'],'R4Step':snapshot['R4']['step'],'R3TimeS':snapshot['R3']['timeS'],'R4TimeS':snapshot['R4']['timeS'],'differentTopLevelFields':[k for k in snapshot['R3']if snapshot['R3'][k]!=snapshot['R4'][k]]}
 result={'schema':'AEGIS_R4_SIX_PHYSICAL_REGRESSION_REVIEW_1','status':'FAIL_PHYSICAL_OUTCOME_WORSENED_CAUSE_NOT_FULLY_OBSERVED','inputs':{'R3':ap,'R4':zp},'firstCapturedAssociationReturnDifferenceIncludingNis':first(a['associationReturns'],z['associationReturns'],sig),'firstCapturedAssociationChoiceOrHoldDifference':first(a['associationReturns'],z['associationReturns'],lambda q:sig(q,False)),'firstSampledStateDifference':snapshot,'firstFiveSecondAcceptedAirLineageExact':a['observedPlotLineage']==z['observedPlotLineage'],'firstNativeLaunchDifference':launch,'firstNativeEffectDifference':first(event(a,'NATIVE_INTERCEPT_RESULT'),event(z,'NATIVE_INTERCEPT_RESULT')),'nativeHitRecords':{'R3':event(a,'NATIVE_SHIP_HIT_RECORD'),'R4':event(z,'NATIVE_SHIP_HIT_RECORD')},'ends':{'R3':a['end'],'R4':z['end']},'hp':{'R3':a['final']['ship']['shipHP'],'R4':z['final']['ship']['shipHP']},'waterM3':{name:sum(c['waterM3']for c in r['final']['ship']['damage']['flooding']['cells'])for name,r in [('R3',a),('R4',z)]},'lifecycleObserver':{'R3':a['reacqExtra']['counts'],'R4':z['reacqExtra']['counts'],'scope':z['reacqExtra']['scope']},'interpretation':['The first logged native return differs at NIS before a subsequent different selection/launch/hit geometry. A changed scalar does not identify the earliest causative hidden lifecycle metadata write.','Observed focused foreign finalizer denominator is zero in both six-target runs;12–26s on003/004 does not cover the later recipient/time that may be affected. Do not use zero here to prove the guard never executed anywhere.','R4 has one initial NORMAL_HIT plus three later native wreck hit callbacks; these are not four unique initial surviving missiles.','The all-initial-terminal+5s criterion is unchanged; R4 still has one native SAM alive at that checkpoint.','No global RNG trace at first divergence is available here. Protected source equality does not prove identical consumed RNG branches; do not attribute this damage change solely to RNG.','No automatic coefficient adjustment or baseline approval is performed.'],'extraBrowserRuns':0,'extraNativeQueries':0,'productChanged':False,'expectationsChanged':False,'releaseApproved':False}
 (P/'evidence/SIX_PHYSICAL_REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# R4 moderate-six physical regression — not approved','',f"R3 HP {result['hp']['R3']}; R4 HP {result['hp']['R4']}. R4 flooding is {result['waterM3']['R4']} m³ at the original checkpoint. Native initial terminal kinds match5KILL+1NORMAL_HIT; material result worsens.",'']
 for key in ['firstCapturedAssociationReturnDifferenceIncludingNis','firstCapturedAssociationChoiceOrHoldDifference','firstSampledStateDifference','firstNativeLaunchDifference','firstNativeEffectDifference']:
  lines += [key+':','```json',json.dumps(result[key],indent=2),'```','']
 lines+=result['interpretation'];(P/'evidence/SIX_PHYSICAL_REGRESSION.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'status':result['status'],'firstNativeReturnTime':result['firstCapturedAssociationReturnDifferenceIncludingNis']['R3']['timeS'],'hp':result['hp'],'firstLaunch':launch}))
if __name__=='__main__':main()
