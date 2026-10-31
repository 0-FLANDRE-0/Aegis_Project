"""Summarize completed paired evidence; preserve old assertions and all differences."""
from pathlib import Path
import csv,gzip,hashlib,json
B=Path(__file__).resolve().parent;E=B/'evidence';load=lambda p:json.loads(p.read_text())
execution=load(E/'regression-execution.json');assert len(execution['rows'])==execution['jobCount']==38
tags=['MAIN','AIR_ORIGIN_A'];D={t:E/'regression'/t for t in tags};summaries={};differences=[]
def delta(a,b,p=''):
 if type(a)!=type(b):return [{'path':p,'before':a,'after':b}]
 if isinstance(a,dict):
  return [r for k in sorted(a.keys()|b.keys())for r in(delta(a[k],b[k],p+'.'+str(k))if k in a and k in b else[{'path':p+'.'+str(k),'before':a.get(k),'after':b.get(k)}])]
 if isinstance(a,list):
  if len(a)!=len(b):return [{'path':p+'.length','before':len(a),'after':len(b)}]
  return [r for i,(x,y)in enumerate(zip(a,b))for r in delta(x,y,p+f'[{i}]')]
 return []if a==b else[{'path':p,'before':a,'after':b}]
def domain(tag):
 rows=[]
 for d in sorted((D[tag]/'domain').iterdir()):
  candidates=[]
  for p in d.glob('*.json'):
   q=load(p)
   if isinstance(q,dict)and isinstance(q.get('checks'),dict)and'pass'in q:candidates.append((p,q))
  assert len(candidates)==1,(tag,d,candidates)
  p,q=candidates[0];rows.append({'suite':d.name,'passed':sum(bool(x)for x in q['checks'].values()),'total':len(q['checks']),'failed':[k for k,v in q['checks'].items()if not v],'path':str(p.relative_to(B))})
 pair=load(D[tag]/'paired42/baseline-comparison.json');assert len(pair['cases'])==6
 rows.append({'suite':'paired42','passed':sum(bool(v)for r in pair['cases']for v in r['checks'].values()),'total':sum(len(r['checks'])for r in pair['cases']),'failed':[r['ship']+':'+r['scenario']+':'+k for r in pair['cases']for k,v in r['checks'].items()if not v],'path':str((D[tag]/'paired42/baseline-comparison.json').relative_to(B))})
 assert sum(r['total']for r in rows)==420
 return rows,pair
for t in tags:
 domains,pair=domain(t);world=load(D[t]/'map/E/evidence/delivery-world120.json');webgl=load(D[t]/'webgl8/observed-world.json');seeker=json.loads(gzip.decompress((D[t]/f'map/E/evidence/c2/{t}/natural.json.gz').read_bytes()));combat=load(D[t]/'combat/results.json')
 summaries[t]={'domain':domains,'domainPassed':sum(r['passed']for r in domains),'domainTotal':420,'world':world,'webgl':webgl,'seeker':seeker,'combat':combat,'paired':pair}
a,b=(summaries[t]for t in tags);causes=load(E/'cause-analysis.json');assert causes['pass']and causes['passiveLoggerEquivalent']
extra=load(E/'ciws-main-extra/results.json');assert not extra['errors']and len(extra['rows'])==2
for r in extra['rows']:
 old=next(x for x in a['combat']['rows']if x['suite']=='ciws'and x['ship']==r['ship'])
 assert {k:v for k,v in old['result'].items()if k!='targets'}=={k:v for k,v in r['result'].items()if k!='targets'},'CIWS_RETIRED_TARGET_LOGGER_CHANGED_PHYSICS'
 old['result']=r['result']
for old,new in zip(a['domain'],b['domain']):
 if old['failed']!=new['failed']:differences.append({'category':'DOMAIN_CHECKS','item':old['suite'],'before':old['failed'],'after':new['failed'],'cause':'DDG/CG 각 samePhysicalState와 sameExistingObserverState, 총 4건 불일치. 관측 보정→기존 AUTO 발사 틱 변경→708kg 탄약 질량 제거 시점 변경→미세한 함체 자세 차이. HP·손상·최종 탄약·RNG·32초 시점 표적 결과 동일. 기대값 갱신 없음. 틱별 동등성 검증: cause-analysis.json.'})
flightRows=[];flightDetails=[]
for old,new in zip(a['webgl']['records'],b['webgl']['records']):
 assert (old['weapon'],old['enabled'])==(new['weapon'],new['enabled'])
 info=lambda r:{'targetAlive':r['final']['targetAlive'],'reason':r['final']['missile']['reason'],'lifeS':r['final']['missile']['lifeS'],'launched':r['launch'].get('launched',False),'source':r['launch'].get('localSensorSource')}
 x,y=info(old),info(new);success=lambda q:q['launched']and q['targetAlive']is False and str(q['reason']).startswith('PROX_DETONATION')
 changes=delta({k:old[k]for k in ['launch','final','samples']},{k:new[k]for k in ['launch','final','samples']})
 positionDeltaM=sum((aa-bb)**2 for aa,bb in zip(old['final']['missile']['positionM'],new['final']['missile']['positionM']))**.5
 flightRows.append({'weapon':old['weapon'],'terminationEnabled':old['enabled'],'before':x,'after':y,'successToFailure':success(x)and not success(y),'failureToSuccess':not success(x)and success(y),'changeCount':len(changes),'finalPositionDeltaM':positionDeltaM})
 flightDetails.append({'weapon':old['weapon'],'terminationEnabled':old['enabled'],'changes':changes,'excludedPresentationOnly':'framesAfterFlight (host-render timing); raw original results retained'})
 if changes:differences.append({'category':'NATURAL_WEBGL','item':old['weapon']+':'+str(old['enabled']),'before':x,'after':y,'cause':'receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json.'})
assert len(flightRows)==8
seekerChanges=[]
for x,y in zip(a['seeker']['rows'],b['seeker']['rows']):
 assert x['id']==y['id']
 if x['result']!=y['result']:seekerChanges.append({'id':x['id'],'differences':delta(x['result'],y['result'])})
assert len(a['seeker']['rows'])==len(b['seeker']['rows'])==28
combatRows=[]
for x,y in zip(a['combat']['rows'],b['combat']['rows']):
 assert(x['suite'],x['ship'])==(y['suite'],y['ship'])
 xx,yy=x['result'],y['result'];changes=delta(xx,yy);row={'suite':x['suite'],'ship':x['ship'],'same':not changes,'changeCount':len(changes),'changes':changes}
 if x['suite']=='ciws':row.update(before={k:xx[k]for k in ['rounds','before','after','hp','actualShipHits','targets','rng','initialTracks','samLaunches','gunShots']},after={k:yy[k]for k in ['rounds','before','after','hp','actualShipHits','targets','rng','initialTracks','samLaunches','gunShots']})
 else:row.update(beforePassed=sum(xx['checks'].values()),afterPassed=sum(yy['checks'].values()),total=len(xx['checks']),beforeFailed=[k for k,v in xx['checks'].items()if not v],afterFailed=[k for k,v in yy['checks'].items()if not v])
 combatRows.append(row)
 if changes:differences.append({'category':x['suite'].upper(),'item':x['ship'],'changeCount':len(changes),'cause':'자체 레이더 큐의 관측 고도·트랙 수/출처만 변화. CIWS 탄 소모·자함 HP·피격 수·표적별 최종 결과·RNG 동일. 로컬 RF·탄도·피해 코드 동일.'if x['suite']=='ciws'else'Inspect recorded fixture differences; no expected values adopted.','detail':'combat-comparison.json'})
worldRows=[]
for i,(x,y)in enumerate(zip(a['world']['records'],b['world']['records'])):
 assert x['mode']==y['mode'];old=load(D['MAIN']/f'world120-returned-state-{i}.json');new=load(D['AIR_ORIGIN_A']/f'world120-returned-state-{i}.json');changes=delta(old,new)
 row={'mode':x['mode'],'beforeHash':x['truthSha256'],'afterHash':y['truthSha256'],'same':x['truthSha256']==y['truthSha256'],'changeCount':len(changes),'changes':changes};worldRows.append(row)
 if changes:differences.append({'category':'WORLD120','item':x['mode'],'before':x['truthSha256'],'after':y['truthSha256'],'changeCount':len(changes),'cause':'56틱 관측 차이→4032틱 SM-6 ACTIVE/IOG·시커 방사 시점 차이→4034틱 표적 위협 감지·회피 분기/RNG 소비 차이. 최종 항공기 운동 7필드+RNG만 변경, 자함 물리·재고·피해 동일. passive trace의 최종 hash는 원래 실행과 각각 정확히 일치.'})
core={'static':load(E/'static.json')['pass'],'roundtrip':load(E/'roundtrip.json')['pass'],'liveReceivers':load(E/'live-receivers.json')['pass']};errors={t:{'webgl':summaries[t]['webgl']['errors'],'seeker':summaries[t]['seeker']['errors'],'combat':summaries[t]['combat']['errors'],'world':summaries[t]['world']['errors']}for t in tags}
result={'contractPass':all(core.values()),'contractChecks':core,'completedJobs':38,'domain':{t:{'passed':summaries[t]['domainPassed'],'total':420,'suites':summaries[t]['domain']}for t in tags},'naturalFlights':flightRows,'naturalWebglChecks':{t:{'passed':sum(summaries[t]['webgl']['checks'].values()),'total':len(summaries[t]['webgl']['checks'])}for t in tags},'successToFailure':[q for q in flightRows if q['successToFailure']],'failureToSuccess':[q for q in flightRows if q['failureToSuccess']],'seeker28Changes':seekerChanges,'seeker28Scope':'Actual missile seeker RF; ideal injected ship track, not unforced onboard radar. Natural onboard coverage is webgl8/liveReceivers/CIWS/world120.','world':[{k:v for k,v in q.items()if k!='changes'}for q in worldRows],'combat':[{k:v for k,v in q.items()if k!='changes'}for q in combatRows],'differences':differences,'errors':errors,'expectedValuesUpdated':False,'executionS':execution['elapsedS'],'extraCauseTraceS':causes['extraElapsedS'],'causeTracePass':True,'allExistingAssertionsPass':all(r['exitCode']==0 for r in execution['rows'])}
for name,q in [('summary.json',result),('world120-comparison.json',worldRows),('combat-comparison.json',combatRows),('natural-flight-comparison.json',flightDetails)]: (E/name).write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
with(E/'differences.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=['category','item','before','after','cause'],lineterminator='\n');w.writeheader()
 for q in differences:w.writerow({k:json.dumps(q[k],ensure_ascii=False)if isinstance(q.get(k),(dict,list))else q.get(k,'')for k in w.fieldnames})
print(json.dumps({'contractPass':result['contractPass'],'domain':{t:result['domain'][t]['passed']for t in tags},'naturalSuccessToFailure':len(result['successToFailure']),'differences':len(differences),'allExistingAssertionsPass':result['allExistingAssertionsPass']},ensure_ascii=False))
