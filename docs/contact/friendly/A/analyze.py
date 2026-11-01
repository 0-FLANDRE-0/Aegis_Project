from pathlib import Path
import json,gzip,csv
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';A=P/'analysis';A.mkdir(exist_ok=True)
def lines(p):
 if not p.exists():p=Path(str(p)+'.gz')
 return [json.loads(s)for s in (gzip.open(p,'rt')if p.suffix=='.gz'else p.open())]
old=lines(R/'docs/ciws/dmg/A/evidence/d1.jsonl');new=lines(E/'ciws-d1.jsonl');assert len(old)==len(new)==30
rows=[]
for a,b in zip(old,new):
 assert a['case']['seed']==b['case']['seed']
 row={'seed':b['case']['seed']}
 for tag,q in [('before',a),('after',b)]:
  row.update({tag+'Hits':q['result']['shipHits'],tag+'Hp':q['result']['hpAfter'],tag+'GunRounds':sum(x['rounds']for x in q['events']if x['kind']=='CIWS_FIRE'),tag+'Ram':sum(x['rounds']for x in q['events']if x['kind']=='RAM_AMMO')})
 row['outcome']='WORSE_NEW_HIT'if row['beforeHits']==0 and row['afterHits']else'IMPROVED_AVOIDED_HIT'if row['beforeHits']and row['afterHits']==0 else'SAME_HIT_CATEGORY'
 rows.append(row)
with(A/'ciws30.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'caseCount':30,'beforeHits':sum(x['beforeHits']for x in rows),'afterHits':sum(x['afterHits']for x in rows),'beforeHpZero':sum(x['beforeHp']==0 for x in rows),'afterHpZero':sum(x['afterHp']==0 for x in rows),'worseNewHit':[x['seed']for x in rows if x['outcome']=='WORSE_NEW_HIT'],'improvedAvoidedHit':[x['seed']for x in rows if x['outcome']=='IMPROVED_AVOIDED_HIT'],'rows':rows}
(A/'ciws30.json').write_text(json.dumps(summary,indent=2)+'\n')
repro=[]
for i in range(3):
 row={'case':['HELO_HOVER_60S','HELO_ROUTE_120S','HARPOON_ROUTE_75S'][i]}
 for tag in ['before','after']:
  d=json.loads((E/f'{tag}-{i}.json').read_text());row[tag]={'initiations':sum(x['requested']is None and x['id']is not None for x in d['births']),'maxFiles':max(len(x['tracks'])for x in d['samples']),'finalFiles':len(d['final']),'final':d['final'],'core':d['core'],'faults':d['faults']}
 repro.append(row)
(A/'track-reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
if(E/'ciws-protection.jsonl').exists()or(E/'ciws-protection.jsonl.gz').exists():
 records=[]
 for d in lines(E/'ciws-protection.jsonl'):
  seed=d['case']['seed'];plain=next(x for x in new if x['case']['seed']==seed);events=[e for e in d['events']if e['kind']=='PROTECTION_ASSOCIATION'];records.append({'seed':seed,'observerSignatureMatches':d['signatureSha256']==plain['signatureSha256'],'associations':len(events),'ownFiles':len({(e['mount'],e['localId'])for e in events if e['ownFireEvidence']}),'nonOwnSourceInOwnFile':[e for e in events if e['ownFireEvidence']and not e['sourceOwn']],'ownSourceInNonOwnFile':[e for e in events if e['sourceOwn']and not e['ownFireEvidence']],'result':d['result']})
 (A/'protection.json').write_text(json.dumps({'records':records,'pass':all(x['observerSignatureMatches']and not x['nonOwnSourceInOwnFile']and not x['ownSourceInNonOwnFile']for x in records)},indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items()if k!='rows'}));print(json.dumps([{k:({z:v[z]for z in ['initiations','maxFiles','finalFiles']}if k in ['before','after']else v)for k,v in x.items()}for x in repro]))
