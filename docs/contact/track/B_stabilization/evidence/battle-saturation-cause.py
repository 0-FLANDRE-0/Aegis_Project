"""Read-only AFTER_ACTION comparison of the frozen natural13 captures."""
from pathlib import Path
import collections,gzip,hashlib,importlib.util,json

P=Path(__file__).resolve().parents[1];E=P/'evidence/battle-final'
spec=importlib.util.spec_from_file_location('battle_codec',P/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
sha=lambda x:hashlib.sha256(x).hexdigest()
def load(v):
 path=E/(v+'-NATURAL_SATURATION_13.json.gz');return b.decode_capture(json.loads(gzip.decompress(path.read_bytes())))
def main():
 data={v:load(v)for v in ['track-a','old-active','candidate-shadow','candidate-active']};a=data['old-active'];z=data['candidate-active']
 applied=lambda r:([(p['i'],p['id'])for p in r['actualSelectedPairs']],r['actualHeldPlots'],r['actualHeldTracks'])
 first=None;equal=0
 for i,(x,y)in enumerate(zip(a['associationReturns'],z['associationReturns'])):
  same_context=all(x[k]==y[k]for k in ['step','route','observerShip'])
  if not same_context or applied(x)!=applied(y):first={'index':i,'sameNativeCallContext':same_context,'old':x,'new':y};break
  equal+=1
 rows=[]
 for v,r in data.items():
  events=r['events'];bykind=lambda kind:[q for q in events if q['kind']==kind]
  hits=bykind('NATIVE_SHIP_HIT_RECORD');damaging=[q for q in hits if(q['hit'].get('dmg')or 0)>0 and not q['hit'].get('miss')];misses=[q for q in hits if q['hit'].get('miss')]
  large=[{'step':q['step'],'timeS':q['timeS'],'route':q['route'],'observerShip':q['observerShip'],'actualSelectedPairs':q['actualSelectedPairs'],'actualHeldPlots':q['actualHeldPlots'],'actualHeldTracks':q['actualHeldTracks'],'components':q['components']}for q in r['associationReturns']if any(max(c['plots'],c['tracks'])>12 for c in q['components'])]
  reasons=collections.Counter(c.get('reason')for q in large for c in q['components']if max(c['plots'],c['tracks'])>12)
  rows.append({'version':v,'nativeFaultFree':all(r['postValidation'].values()),'end':r['end'],'hp':r['final']['ship']['shipHP'],'globalRng':r['final']['globalRng'],'counts':r['counts'],'shotEffectCountsAreNotUniquePhysicalTargetKills':True,'nativeInitialTargetRetirements':r['targets'],'remainingAliveNativeStates':[t for t in r['targets']if t.get('alive')],'shipHitHistoryRecords':len(hits),'damagingShipHitRecords':len(damaging),'nativeShipMissRecords':len(misses),'damagingHitTimeline':damaging,'nativeShipMissTimeline':misses,'largeReasonCounts':dict(reasons),'largeNativeReturns':large,'maxHoldToNextAcceptedUpdateS':max((q['durationS']for q in r['holdDurations']),default=0),'holdEpisodes':r['holdDurations'],'launchTimeline':bykind('NATIVE_WEAPON_LAUNCH'),'nativeEffectTimeline':bykind('NATIVE_INTERCEPT_RESULT'),'sensorRecordSamples':bykind('OBSERVED_SENSOR_RECORD')})
 divergences=[]
 for kind in ['NATIVE_WEAPON_LAUNCH','NATIVE_INTERCEPT_RESULT','NATIVE_SHIP_HIT_RECORD']:
  x=[e for e in a['events']if e['kind']==kind];y=[e for e in z['events']if e['kind']==kind]
  divergences.append({'kind':kind,'firstDifferent':next(({'index':i,'old':u,'new':v}for i,(u,v)in enumerate(zip(x,y))if u!=v),None),'oldCount':len(x),'newCount':len(y)})
 # This is accepted-update evidence, not a complete independent RF producer log.
 line_a=a['observedPlotLineage'];line_z=z['observedPlotLineage'];line_diff=next(({'index':i,'old':x,'new':y}for i,(x,y)in enumerate(zip(line_a,line_z))if x!=y),None)
 result={'schema':'AEGIS_TRACK_B_NATURAL13_PASSIVE_CAUSE_1','frozenProductChanged':False,'sourceHashes':{v:{'captureGzipSha256':sha((E/(v+'-NATURAL_SATURATION_13.json.gz')).read_bytes())}for v in data},'firstAppliedDifference':first,'precedingAppliedReturnsExactlyEqual':equal,'firstCapturedAcceptedUpdateDifference':line_diff,'laterEventDifferences':divergences,'rows':rows,'known':'First applied difference is proven from actual returned pairs/held sets; native effects and damage histories are original records.','unknown':['Accepted-update lineage is not a complete pre-association RF stream.','No per-tick P36/global RNG or actual Pk draw was captured by the original frozen battle helper.','Mathematically safe graph assignment is not a certificate of physical target identity.','Alive count at horizon is lifecycle incompleteness; remaining native damage/behavior flags are retained, and alive is not equated to a fully effective threat.'],'approval':'UNAPPROVED_WORSENING_INDICATORS; no coefficient or expectation adjustment','releaseApproved':False}
 out=P/'evidence/battle-analysis/NATURAL13_CAUSE.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'firstAppliedDifferenceS':first['old']['timeS']if first else None,'precedingEqual':equal,'rows':[{'version':q['version'],'largeReasons':q['largeReasonCounts'],'damagingHits':q['damagingShipHitRecords'],'missRecords':q['nativeShipMissRecords'],'remainingAlive':len(q['remainingAliveNativeStates'])}for q in rows]}))

if __name__=='__main__':main()
