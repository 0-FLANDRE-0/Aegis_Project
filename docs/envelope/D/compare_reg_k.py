"""Compare every shot outcome to RANGE_RECOVERY_A, retaining numeric changes."""
from pathlib import Path
import csv,json
H=Path(__file__).resolve().parent;E=H/'evidence/reg-k'
files=[('normals-release','docs/missile/termination/A/cases/normal.json'),('dual-release','docs/missile/termination/A/cases/dual.json'),('faults-release','docs/missile/termination/A/cases/fault.json'),('battery-release','docs/missile/termination/A/cases/battery.json'),('release-request-final','docs/missile/termination/A/cases/release-request.json'),('validation-release','docs/missile/range/A/cases/validation.json')]
R=H.parents[2];rows=[];changes=[];losses=[];gains=[]
def comparison(suite,index,condition,a,b):
 keys=['success','reason','closestM','fuzeMissM','flightTimeS','reacquired']
 changed=[k for k in keys if a.get(k)!=b.get(k)]
 row={'suite':suite,'index':index,'condition':condition,'changed':changed,'before':{k:a.get(k)for k in keys},'after':{k:b.get(k)for k in keys}}
 rows.append(row)
 if changed:changes.append(row)
 if a.get('success')and not b.get('success'):losses.append(row)
 if not a.get('success')and b.get('success'):gains.append(row)
for name,case in files:
 a=json.loads((E/'recovery'/(name+'.json')).read_text())['results'];b=json.loads((E/'current'/(name+'.json')).read_text())['results'];conditions=json.loads((R/case).read_text());assert len(a)==len(b)==len(conditions)
 for i,(c,x,y)in enumerate(zip(conditions,a,b)):comparison(name,i,c,x,y)
for source in ['observed-world','observed-webgl']:
 for tag in ['current','recovery']:
  assert (E/tag/source/'observed-world.json').exists()
 a=json.loads((E/'recovery'/source/'observed-world.json').read_text())['records'];b=json.loads((E/'current'/source/'observed-world.json').read_text())['records'];assert len(a)==len(b)==8
 for i,(x,y)in enumerate(zip(a,b)):
  def value(r):
   f=r['final'];m=f['missile'];return {'success':not f['targetAlive']and bool(m['prox']),'reason':m['reason'],'closestM':f.get('closestM'),'flightTimeS':m['lifeS']}
  comparison(source,i,{'weapon':x['weapon'],'enabled':x['enabled'],'naturalSensor':True,'actualWebgl':source=='observed-webgl'},value(x),value(y))
acceptance={}
for tag in ['current','recovery']:
 acceptance[tag]={}
 for name,path in [('domain','domain-acceptance.json'),('ui','ui/ui.json'),('termination','live-acceptance.json'),('observed','observed-webgl/observed-world.json')]:
  j=json.loads((E/tag/path).read_text());acceptance[tag][name]={'pass':j['pass'],'count':j['checks']if isinstance(j['checks'],int)else len(j['checks']),'failed':[k for k,v in j.get('checks',{}).items()if not v]if isinstance(j['checks'],dict)else[]}
world=json.loads((E/'world120.json').read_text());combat=json.loads((E/'combat-followup.json').read_text())
out={'schema':'AEGIS_REG_K_COMPARISON_1','acceptance':acceptance,'comparedShots':len(rows),'allOutcomeAndGeometryChanges':changes,'successToFailure':losses,'failureToSuccess':gains,'successToFailureCount':len(losses),'failureToSuccessCount':len(gains),'idleTruthHashIdentical':world['checks']['idleSameTruthHash'],'combatHashChanged':world['combatHashChanged'],'combatFollowup':combat,'rows':rows,'pass':all(v['pass']for x in acceptance.values()for v in x.values())and world['pass']and combat['pass']}
(H/'REG_K_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
with(H/'REG_K_ALL_CHANGES.csv').open('w',newline='')as f:
 fields=['suite','index','condition','changed','beforeSuccess','afterSuccess','beforeReason','afterReason','beforeClosestM','afterClosestM','beforeFuzeMissM','afterFuzeMissM','beforeTimeS','afterTimeS'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for row in rows:
  a,b=row['before'],row['after'];w.writerow({'suite':row['suite'],'index':row['index'],'condition':json.dumps(row['condition'],ensure_ascii=False,separators=(',',':')),'changed':','.join(row['changed']),'beforeSuccess':a.get('success'),'afterSuccess':b.get('success'),'beforeReason':a.get('reason'),'afterReason':b.get('reason'),'beforeClosestM':a.get('closestM'),'afterClosestM':b.get('closestM'),'beforeFuzeMissM':a.get('fuzeMissM'),'afterFuzeMissM':b.get('fuzeMissM'),'beforeTimeS':a.get('flightTimeS'),'afterTimeS':b.get('flightTimeS')})
print(json.dumps({'pass':out['pass'],'successToFailure':len(losses),'failureToSuccess':len(gains),'changed':len(changes),'compared':len(rows)}))
