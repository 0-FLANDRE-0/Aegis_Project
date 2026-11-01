"""Unchanged Phase1 .05 outer-decline rule; measurements never tune the model."""
from pathlib import Path
import collections,csv,hashlib,json,statistics
P=Path(__file__).resolve().parent;E=P/'evidence/range-intercept';sha=lambda b:hashlib.sha256(b).hexdigest();rows=[json.loads(l)for f in E.glob('*.jsonl')for l in f.open()];assert len(rows)==1440 and len({(r['ship'],r['bearing'],r['rangeKm'],r['seed'])for r in rows})==1440
execution=json.loads((E/'execution.json').read_text());model=json.loads((P/'measurement-build.json').read_text());assert execution['htmlSha256']==model['htmlSha256']and not execution['errors'];assert execution['actualSourceChecks']and all(q==model['modelFingerprints']['nativeSourceHashes']for q in execution['actualSourceChecks']);assert all(not r.get('core')for r in rows)
profiles={};bins=[];comparison=[];old=json.loads((P.parent/'phase1/range-table.json').read_text());mean=lambda v:statistics.mean(a)if(a:=list(v))else None
for ship in sorted({r['ship']for r in rows}):
 curves={}
 for bearing in[0,90]:
  curve=[]
  for km in range(1,10):
   rr=[r for r in rows if(r['ship'],r['bearing'],r['rangeKm'])==(ship,bearing,km)];assert len(rr)==40;v=sorted(r['pk']for r in rr if'release'in r);q=lambda p:v[int((len(v)-1)*p)]if v else None
   d={'ship':ship,'bearing':bearing,'interceptRangeKm':km,'n':40,'meanPk':mean(v),'p10Pk':q(.1),'p90Pk':q(.9),'nativeReleases':len(v),'withheldReasons':dict(collections.Counter(r['reason']for r in rr if'release'not in r)),'meanLaunchRangeKm':mean(r['firingRangeKm']for r in rr if'firingRangeKm'in r),'meanBurstRangeKm':mean(r['burstRangeKm']for r in rr if r.get('burstRangeKm')is not None),'patternBandRejects':sum(r.get('fragment',{}).get('gunB2FragmentField',{}).get('reason')=='OUTSIDE_FRAGMENT_BAND'for r in rr if r.get('fragment')),'nativeOutcomes':dict(collections.Counter(r.get('outcome')or('WITHHELD'if'release'not in r else'NO_NATIVE_EFFECT')for r in rr))};curve.append(d);bins.append(d)
   previous=old['profiles'][ship]['curves'][str(bearing)][km-1];comparison.append({'ship':ship,'bearing':bearing,'rangeKm':km,'beforeMeanPk':previous['meanPk'],'afterMeanPk':d['meanPk'],'beforeNativeReleases':previous['nativeReleases'],'afterNativeReleases':d['nativeReleases']})
  curves[str(bearing)]=curve
 front=curves['0'];seen=False;drop=None;inner=[]
 for r in front:
  if r['meanPk']is None:continue
  if r['meanPk']>=.05:seen=True
  elif not seen:inner.append(r['interceptRangeKm'])
  elif drop is None:drop=r['interceptRangeKm']
 proposal={'rangeKm':drop if drop is not None else 9 if seen else None,'rightCensored':seen and drop is None,'thresholdMeanPk':.05,'resolutionKm':1,'method':old['profiles'][ship]['proposal']['method'],'nearRangeBelowThresholdKm':[r['interceptRangeKm']for r in front if r['meanPk']is not None and r['meanPk']<.05],'innerBelowThresholdKm':inner,'status':'PROPOSED_FOR_PR_REVIEW_ONLY','authority':'USER_APPROVED_B2A_NATIVE_MEASUREMENT'};profiles[ship]={'curves':curves,'proposal':proposal}
q={**{k:old[k]for k in ['target','targetAltitudeM','targetSpeedMps','bearingsDeg','observation','distanceDefinition','seeds']},'schema':'AEGIS_GUN_B2_MEASURED_RANGE_2','provenance':'GAME_ENGINE_COMPUTED_SIM_TUNED','measuredHtmlSha256':execution['htmlSha256'],'measurementModelFingerprints':model['modelFingerprints'],'profiles':profiles,'usedByReleaseGate':False,'autoRangeMChanged':False,'sampleFileHashes':{f.name:sha(f.read_bytes())for f in E.glob('*.jsonl')},'previous':old};(P/'range-table.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
for name,data in [('curve.csv',bins),('before-after.csv',comparison)]:
 with(E/name).open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
(P/'evidence/range-comparison.json').write_text(json.dumps({'attempts':len(rows),'actualReleases':sum('release'in r for r in rows),'profiles':profiles,'comparison':comparison,'actualSourceChecks':True},indent=2)+'\n')
print(json.dumps({s:q['proposal']for s,q in profiles.items()}))
