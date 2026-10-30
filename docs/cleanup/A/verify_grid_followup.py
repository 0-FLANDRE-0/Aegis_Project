"""Audit approved extra flights and exact preservation of all prior shots."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
before=load(H/'evidence/interval-followup-before.json');m=load(H/'results/intervals.json');approval=load(H/'scope-approval.json')
by={r['cellId']:r for r in before['rows']};checks={};changes=[]
sha=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for r in m['rows']:
 old=by[r['cellId']];new={str(q['rangeKm']):q for q in r['newDistances']}
 checks[r['cellId']+'.oldShotsPreserved']=all(k in new and sha(new[k])==v for k,v in old['newDistancesHashes'].items())
 checks[r['cellId']+'.minimumUnchanged']=r['effectiveMinKm']==old['effectiveMinKm']
 added=[q for k,q in new.items()if k not in old['newDistancesHashes']]
 if added:
  assert r['cellId']in approval['cells'];assert all(q['purpose']=='GRID'and q['rangeKm']%5==0 for q in added)
  changes.append({'cellId':r['cellId'],'altM':r['altM'],'motion':r['motion'],'effectiveMinKm':r['effectiveMinKm'],'effectiveMaxKm':r['effectiveMaxKm'],'addedPoints':[{k:q[k]for k in ['rangeKm','lethalCount','effectCount']}for q in added],'addedShots':len(added)*5,'breakRangeKm':r['breakPoint']['rangeKm'],'breakLethalCount':r['breakPoint']['lethalCount'],'breakResults':[{'rngSeed':s['rngSeed'],'navigationSeed':s['navigationSeed'],'outcome':s['outcome'],'reason':s['reason']}for s in r['breakPoint']['shots']]})
 if r['cellId']not in approval['cells']:checks[r['cellId']+'.completedIntervalUnchanged']=r['effectiveMaxKm']==old['effectiveMaxKm']and not added
checks['onlyApprovedFive']=set(r['cellId']for r in changes)==set(approval['cells'])
checks['shotCapRespected']=sum(r['addedShots']for r in changes)<=approval['maximumAdditionalShots']
checks['noExtraMinimumFlights']=m['newShotsTotal']-before['minimumShots']==sum(r['addedShots']for r in changes)
checks['freshCallsWithinRecordedAdditions']=0<=m['freshCalls']<=sum(r['addedShots']for r in changes)
checks['all120Complete']=m['complete']and all(r['status']=='MEASURED'and r['effectiveMaxKm']is not None for r in m['rows'])
result={'schema':'AEGIS_CLEAN_A_GRID_FOLLOWUP_VERIFICATION_1','pass':all(checks.values()),'checks':checks,'changes':changes,'additionalGridShots':sum(r['addedShots']for r in changes),'minimumShots':before['minimumShots'],'totalAdditionalShots':m['newShotsTotal'],'minimumElapsedS':before['minimumElapsedS'],'gridElapsedS':m['elapsedS'],'approval':'scope-approval.json','priorDeliveryCommit':before['deliveryCommit']}
(H/'evidence/grid-followup.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['pass'];print(json.dumps({k:v for k,v in result.items()if k not in ['checks','changes']}))
