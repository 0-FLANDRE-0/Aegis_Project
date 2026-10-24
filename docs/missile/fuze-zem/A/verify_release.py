"""Compare unchanged original release cases across BASE and DZT."""
from pathlib import Path
import json,csv,io
H=Path(__file__).resolve().parent;E=H/'evidence';checks={};groups=[];regressions=[];rows=[]
expected={'normals':240,'dual':36,'faults':12,'battery':8,'request':4}
for kind,count in expected.items():
 b=json.loads((E/'release-BASE'/(kind+'.json')).read_text());d=json.loads((E/'release-DZT'/(kind+'.json')).read_text());assert len(b['results'])==len(d['results'])==count
 losses=[]
 for i,(a,c)in enumerate(zip(b['results'],d['results'])):
  for field in ['weapon','scenario','enabled','rangeKm','altM','seed']:assert a[field]==c[field],(kind,i,field)
  q={'kind':kind,'index':i,'weapon':a['weapon'],'rangeKm':a['rangeKm'],'altM':a['altM'],'seed':a['seed'],'scenario':a['scenario'],'enabled':a['enabled'],'beforeSuccess':a['success'],'afterSuccess':c['success'],'beforeReason':a['reason'],'afterReason':c['reason'],'beforeClosestM':a['closestM'],'afterClosestM':c['closestM'],'beforeFuzeMissM':a['fuzeMissM'],'afterFuzeMissM':c['fuzeMissM'],'beforeFlightTimeS':a['flightTimeS'],'afterFlightTimeS':c['flightTimeS']};rows.append(q)
  if a['success']and not c['success']:losses.append(q);regressions.append(q)
 checks[kind+'.pageErrors0']=not b['errors']and not d['errors'];checks[kind+'.noNewFailure']=not losses
 groups.append({'kind':kind,'count':count,'baseSuccess':sum(x['success']for x in b['results']),'candidateSuccess':sum(x['success']for x in d['results']),'regressions':losses})
 if kind in ['normals','dual']:
  pairs=list(zip(d['results'][::2],d['results'][1::2]));checks[kind+'.noPrematureComparedToTermOff']=all(not x['success']or y['success']for x,y in pairs)
 if kind=='battery':
  life={'SM2':380,'SM2ER':430,'SM6':480,'ESSM':185};checks['battery.exactPreservedLife']=all(x['reason']=='BATTERY_EXHAUSTED'and life[x['weapon']]<=x['flightTimeS']<=life[x['weapon']]+1/60+1e-6 for x in d['results']);checks['battery.zeroRemaining']=all(x['final']['batteryRemainingS']==0 for x in d['results'])
 if kind=='faults':
  a=d['results'];checks['rf.reacquire4NativeIntercepts']=sum(x['scenario']=='REACQUIRE'and x['reacquired']and x['success']for x in a)==4;checks['rf.loss4Retired']=sum(x['scenario']=='LOSS'and x['final']['dead']for x in a)==4
 if kind=='request':checks['request.nativeVlsRecord4']=all(x['releaseRequest']and x['releaseRecord']for x in d['results'])
s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);(H/'RELEASE_AB.csv').write_bytes(s.getvalue().encode('utf-8-sig'))
result={'pass':all(checks.values()),'checks':checks,'shotsPerVersion':sum(expected.values()),'groups':groups,'regressions':regressions,'failureChanges':[q for q in rows if q['beforeReason']!=q['afterReason']],'method':'Same original release cases. Native RF, constant point target, native fuze/flight; not a full ENV_D sweep. Battery tests preserve the original test-only life checkpoint.'};(E/'release-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'shots':2*result['shotsPerVersion'],'regressions':regressions,'failed':[k for k,v in checks.items()if not v],'groups':groups}));raise SystemExit(0 if result['pass']else 1)
