from pathlib import Path
import csv,hashlib,json,statistics,re,collections
P=Path(__file__).resolve().parent;E=P/'evidence/range-intercept';R=P.parents[3];rows=[json.loads(l)for p in E.glob('*.jsonl')for l in p.read_text().splitlines()];assert len(rows)==1440 and len({(r['ship'],r['bearing'],r['rangeKm'],r['seed'])for r in rows})==1440
profiles={};bins=[]
def avg(values):
 v=list(values);return statistics.mean(v)if v else None
for ship in sorted({r['ship']for r in rows}):
 curves={}
 for bearing in [0,90]:
  curve=[]
  for km in range(1,10):
   rr=[r for r in rows if(r['ship'],r['bearing'],r['rangeKm'])==(ship,bearing,km)];assert len(rr)==40;v=sorted(r['pk']for r in rr if 'release'in r);quant=lambda p:v[int((len(v)-1)*p)]if v else None;data={'ship':ship,'bearing':bearing,'interceptRangeKm':km,'n':len(rr),'meanPk':avg(v),'p10Pk':quant(.1),'p90Pk':quant(.9),'nativeReleases':sum('release'in r for r in rr),'withheldReasons':dict(collections.Counter(r['reason']for r in rr if 'release'not in r)),'meanLaunchRangeKm':avg(r['firingRangeKm']for r in rr if 'firingRangeKm'in r),'meanBurstRangeKm':avg(r['burstRangeKm']for r in rr if r.get('burstRangeKm')is not None),'patternBandRejects':sum(r.get('fragment',{}).get('gunB2FragmentField',{}).get('reason')=='OUTSIDE_FRAGMENT_BAND'for r in rr if r.get('fragment'))};curve.append(data);bins.append(data)
  curves[str(bearing)]=curve
 front=curves['0'];seen=False;drop=None
 for r in front:
  if r['meanPk']is None:continue
  if r['meanPk']>=.05:seen=True
  elif seen:drop=r['interceptRangeKm'];break
 proposal={'rangeKm':drop if drop is not None else 9 if seen else None,'rightCensored':seen and drop is None,'thresholdMeanPk':.05,'resolutionKm':1,'method':'FIRST_MEASURED_DOWNWARD_CROSSING_AFTER_MEAN_PK_0_05; >=9 IF RIGHT_CENSORED; NO EXTRAPOLATION','nearRangeBelowThresholdKm':[r['interceptRangeKm']for r in front if r['meanPk']is not None and r['meanPk']<.05],'status':'PROPOSED_FOR_PR_REVIEW_ONLY','authority':'USER_APPROVED_PHASE1_NATIVE_MEASUREMENT'};profiles[ship]={'curves':curves,'proposal':proposal}
q={'schema':'AEGIS_GUN_B2_MEASURED_RANGE_1','provenance':'GAME_ENGINE_COMPUTED_SIM_TUNED','target':'Kh-35U','targetAltitudeM':10,'targetSpeedMps':280,'bearingsDeg':[0,90],'observation':'IDEAL_CURRENT_TRACK; NO SENSOR_NOISE IN THIS CURVE; NATURAL_RF_TESTED_SEPARATELY','distanceDefinition':'PLANNED_INTERCEPT_FROM_NATIVE_CONTINUATION_SOLVE; ACTUAL_BURST_DISTANCE_ALSO_RECORDED','seeds':list(range(592001,592041)),'measuredHtmlSha256':json.loads((E/'execution.json').read_text())['htmlSha256'],'profiles':profiles,'usedByReleaseGate':False,'autoRangeMChanged':False};fp=json.loads((E/'execution.json').read_text())['modelFingerprints'];q.update({k:fp[k]for k in ['runtimeTemplateSha256','dispersionConstantsSha256','compiledGunSpecSha256']});q['nativeSourceHashes']={k:v for k,v in fp['nativeSourceHashes'].items()if k!='createProfileGunModuleWip13B3'};q['nativeFactorySourceSha256']=fp['nativeSourceHashes']['createProfileGunModuleWip13B3'];q['sampleFileHashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in E.glob('*.jsonl')};(P/'range-table.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
with(E/'curve.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(bins[0]));w.writeheader();w.writerows(bins)
print(json.dumps({ship:q['proposal']for ship,q in profiles.items()},ensure_ascii=False))
