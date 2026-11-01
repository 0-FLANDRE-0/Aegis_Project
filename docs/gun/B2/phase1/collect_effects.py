"""Count physical ASM outcomes; never promote the inherited ambiguous counters."""
from pathlib import Path
import argparse,collections,csv,json,statistics
P=Path(__file__).resolve().parent;B=P.parent
parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args()
rows=[json.loads(line)for f in(P/'evidence/g7').glob('*.jsonl')for line in f.read_text().splitlines()]
ids=[r['caseId']for r in rows];assert len(set(ids))==len(ids),'DUPLICATED_G7_CASE'
if not args.partial:assert len(rows)==960 and set(ids)==set(range(960)),'G7_INCOMPLETE'
def metrics(row):
 result=row['result'];diag=row['diagnostic'];targets=diag['afterAction']['targets'];assert len(targets)==row['count'];index={r['id']:r for r in targets};credited=set();events=[]
 for burst in diag['bursts']:
  for effect in burst['results']:
   if effect['kind']!='ASM'or effect['id']not in index:continue
   target=index[effect['id']];entry=target['first3kmStep'];death=target.get('deathStep')
   if effect['result']in ['KILL','STRUCT_FAIL']and death is not None and(entry is None or(burst['step']<entry and death<=entry)):
    credited.add(target['id']);events.append({'targetId':target['id'],'effect':effect['result'],'eventStep':burst['step'],'deathStep':death,'first3kmStep':entry})
 return {'caseId':row['caseId'],'ship':row['ship'],'bearing':row['bearing'],'count':row['count'],'seed':row['seed'],'autoAA':row['on'],'physicalAsmKillsBefore3km':len(credited),'mffShots':result['shots'],'ciwsUsed':result['ciwsUsed'],'hpBefore':result['hpBefore'],'hpAfter':result['hpAfter'],'shipDamage':result['hpAfter']<result['hpBefore'],'shipAlive':result['shipAlive'],'simSeconds':result['seconds'],'burstCount':result['burstCount'],'refreshAttempts':diag['b2']['refreshAttempts'],'refreshHostMs':diag['b2']['refreshMs'],'releaseAges':[r['ageS']for r in diag['b2']['releases']],'creditEvidence':events}
flat=[metrics(r)for r in rows];groups=[]
for key in sorted({(r['ship'],r['bearing'],r['count'],r['autoAA'])for r in flat}):
 rr=[r for r in flat if(r['ship'],r['bearing'],r['count'],r['autoAA'])==key];mean=lambda k:statistics.mean(r[k]for r in rr)
 groups.append(dict(zip(['ship','bearing','count','autoAA'],key),n=len(rr),meanPre3kmAsmKills=mean('physicalAsmKillsBefore3km'),totalPre3kmAsmKills=sum(r['physicalAsmKillsBefore3km']for r in rr),meanShots=mean('mffShots'),meanCiwsUsed=mean('ciwsUsed'),shipDamageTrials=sum(r['shipDamage']for r in rr),meanHpAfter=mean('hpAfter'),minHpAfter=min(r['hpAfter']for r in rr),shipSurvivors=sum(r['shipAlive']for r in rr),meanRefreshAttempts=mean('refreshAttempts'),meanRefreshHostMs=mean('refreshHostMs')))
old=[json.loads(line)for f in(B/'post-origin/evidence').glob('worker*.jsonl')for line in f.read_text().splitlines()];pairs=[]
for r in flat:
 if not r['autoAA']or r['count']!=1 or not(419010<=r['seed']<=419024):continue
 ref=next(x['data']['result']for x in old if(x['ship'],x['bearing'],x['seed'])==(r['ship'],r['bearing'],r['seed']))
 pairs.append({'ship':r['ship'],'bearing':r['bearing'],'seed':r['seed'],'beforeShots':ref['shots'],'afterShots':r['mffShots'],'beforeCiwsUsed':ref['ciwsUsed'],'afterCiwsUsed':r['ciwsUsed'],'beforeShipAlive':ref['shipAlive'],'afterShipAlive':r['shipAlive'],'beforeRemainingAsm':sum(t['alive']for t in ref['targets']),'afterRemainingAsm':sum(t['alive']for t in next(x['diagnostic']['afterAction']['targets']for x in rows if x['caseId']==r['caseId'])),'beforeHp':ref['hpAfter'],'afterHp':r['hpAfter'],'worseHp':r['hpAfter']<ref['hpAfter']})
workerReports=[json.loads(p.read_text())for p in(P/'evidence/g7').glob('worker*-complete.json')];frozen=json.loads((P/'measurement-build.json').read_text())
expectedCases=[(ship,bearing,count,419010+seed,on)for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for bearing in [0,90]for count in range(1,5)for seed in range(30)for on in [False,True]]
checks={'caseControlMatrixExact':all(tuple(r[k]for k in ['ship','bearing','count','seed','on'])==expectedCases[r['caseId']]for r in rows),'allFiveB2FlagsOn':all(all(r['diagnostic']['b2']['flags'].values())for r in rows),'autoAAOffNoGunShots':all(r['result']['shots']==0 for r in rows if not r['on']),'allActualReleasesRecorded':all(r['result']['shots']==len(r['diagnostic']['b2']['releases'])for r in rows),'allThreeWorkersComplete':len(workerReports)==3,'pageErrors0':all(not w['errors']for w in workerReports),'sameFrozenPhysicalHtml':all(r['htmlSha256']==frozen['htmlSha256']for r in rows),'unique960':len(rows)==len(set(ids))==960,'allFreshPhysicalTargetsRecorded':all(len(r['diagnostic']['afterAction']['targets'])==r['count']for r in rows),'noStaleRelease':all(age==0 for r in flat for age in r['releaseAges']),'coreErrors0':all(not r['diagnostic']['core']for r in rows),'full32Groups':len(groups)==32 and all(r['n']==30 for r in groups),'matched4cBaseline60':len(pairs)==60}
q={'complete':all(checks.values()),'checks':checks,'cases':len(rows),'groups':groups,'matchedBaseline60':pairs,'worseMatchedHpCases':[r for r in pairs if r['worseHp']],'newExpectedValuesApproved':0,'countsAuthority':'AFTER_ACTION_TRUTH_TEST_ONLY: physical ASM identity, burst effect +death before first3km tick; HP decrease trials (not legacy shipHits)','gameHtmlSha256s':sorted({r['htmlSha256']for r in rows})}
E=P/'evidence';(E/'effects-summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
with(E/'effects-groups.csv').open('w',newline='')as f:
 writer=csv.DictWriter(f,fieldnames=list(groups[0]));writer.writeheader();writer.writerows(groups)
with(E/'effects-trials.csv').open('w',newline='')as f:
 fields=[k for k in flat[0]if k not in ['releaseAges','creditEvidence']];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r[k]for k in fields}for r in flat)
print(json.dumps({'complete':q['complete'],'cases':len(rows),'checks':checks,'worseMatchedHpCases':len(q['worseMatchedHpCases'])}))
if not args.partial:raise SystemExit(not q['complete'])
