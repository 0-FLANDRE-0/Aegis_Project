"""AFTER_ACTION sampled geometry only; no simulation/prediction consumer."""
from pathlib import Path
import gzip,importlib.util,json,math
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');spec=importlib.util.spec_from_file_location('battle_codec',R1/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def main():
 paths={'oldB':R1/'evidence/battle-final/old-active-NATURAL_SATURATION_13.json.gz','R2':P/'evidence/battle-active-pilot/candidate-active-NATURAL_SATURATION_13.json.gz'};rows=[]
 for label,path in paths.items():
  r=b.decode_capture(json.loads(gzip.decompress(path.read_bytes())));last=r['samples'][-1];before=r['samples'][-2];dt=last['timeS']-before['timeS'];ownv={k:(last['ownPositionM'][k]-before['ownPositionM'][k])/dt for k in ['x','y']};alive={t['id']for t in r['targets']if t.get('alive')}
  for ident in sorted(alive):
   history=[]
   for sample in r['samples']:
    target=next((t for t in sample['truthAfterAction']if t['id']==ident),None)
    if target is None:continue
    rel={k:target['positionM'][k]-sample['ownPositionM'][k]for k in ['x','y']};history.append({'timeS':sample['timeS'],'rangeM':math.hypot(rel['x'],rel['y']),'relativePositionM':rel,'nativePose':target})
   end=history[-1];velocity=end['nativePose']['velocityMps'];relv={k:velocity[k]-ownv[k]for k in ['x','y']};dot=sum(end['relativePositionM'][k]*relv[k]for k in ['x','y']);radial=dot/end['rangeM'];closest=min(history,key=lambda q:q['rangeM']);tail=[q for q in history if q['timeS']>=last['timeS']-10];increasing=all(x['rangeM']<y['rangeM']for x,y in zip(tail,tail[1:]));classification='CURRENTLY_RECEDING_AFTER_SAMPLED_PASSAGE'if radial>0 and closest['timeS']<last['timeS']and increasing else'UNRESOLVED_GEOMETRY'
   rows.append({'variant':label,'tag':'AFTER_ACTION_TRUTH_TEST_ONLY','initialPhysicalId':ident,'atS':last['timeS'],'nativePositionM':end['nativePose']['positionM'],'nativeVelocityMps':velocity,'ownPositionM':last['ownPositionM'],'ownVelocityMpsFromLastTwoSamples':ownv,'horizontalRangeM':end['rangeM'],'horizontalRangeRateMpsPositiveReceding':radial,'last10sSampledRangesStrictlyIncreasing':increasing,'sampledClosestApproach':closest,'classification':classification,'nativeFinalTargetState':next(t for t in r['targets']if t['id']==ident),'finalNativeEwSettings':r['final']['ship']['ew'],'history':history,'limitations':['Closest range is a1Hz sample minimum, not native swept CPA.','Final EW command settings do not establish decoy/ECM history or cause of the miss.','Receding after passage is not permanent harmlessness or a change to native lifecycle outcome.','No new tactical target state, identity or firing authority is produced.']})
 result={'schema':'AEGIS_NATURAL13_LEFTOVER_SAMPLED_GEOMETRY_1','status':'PRELIMINARY_WAITING_GUARDED_EW_SEEKER_HISTORY','rows':rows,'noGameFunctionCalls':True,'nativeLifecycleCriterionChanged':False,'releaseApproved':False};(D/'LEFTOVER_PRELIMINARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'variant':q['variant'],'id':q['initialPhysicalId'],'rangeM':q['horizontalRangeM'],'radialMps':q['horizontalRangeRateMpsPositiveReceding'],'sampledClosestS':q['sampledClosestApproach']['timeS'],'sampledClosestM':q['sampledClosestApproach']['rangeM'],'classification':q['classification']}for q in rows]))
if __name__=='__main__':main()
