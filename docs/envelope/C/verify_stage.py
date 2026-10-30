"""Verify two independent six-condition sweeps, then persist canonical raw+receipts."""
import argparse,gzip,hashlib,itertools,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
x=a.first.read_bytes();y=a.second.read_bytes();j=json.loads(x);expected=set(itertools.product(['SM2ER','SM6'],[1000,10000,20000]));actual={(q['weapon'],q['altM'])for q in j['table']}
checks={'bitIdentical':x==y,'sixUniqueRows':actual==expected and len(j['table'])==6,'cap500':j['rangeCapKm']==500,'stationaryOnly':all(q['targetSpeedMps']==0 for q in j['table']),'allNativeReasons':all(q['lastSuccess']and q['lastSuccess']['result']['success']and(q['upperCapReached']or q['firstFailure']and not q['firstFailure']['result']['success']and q['firstFailure']['rangeKm']==q['maxRangeKm']+1)for q in j['table'])}
r={'pass':all(checks.values()),**checks,'rangeCapKm':500,'sha256':hashlib.sha256(x).hexdigest(),'bytes':len(x),'profileHash':j['profileHash'],'receipts':[],'rows':[]}
for name,src in [('first',a.first),('second',a.second)]:
 receipt=json.loads(Path(str(src)+'.receipt.json').read_text());r['receipts'].append({'name':name,**receipt});(a.out/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2))
(a.out/'results.json.gz').write_bytes(gzip.compress(x,9,mtime=0))
for q in j['table']:
 row={'weapon':q['weapon'],'altM':q['altM'],'maxRangeKm':q['maxRangeKm'],'interceptPointKm':q['lastSuccess']['result'].get('interceptPointKm',q['lastSuccess']['result']['terminal']['distanceKm']),'lastSuccess':q['lastSuccess'],'firstFailure':q['firstFailure']};r['rows'].append(row)
(a.out/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps({'pass':r['pass'],'hash':r['sha256'],'receipts':r['receipts'],'rows':[{k:q[k]for k in ['weapon','altM','maxRangeKm','interceptPointKm']}|{'failure':q['firstFailure']['result']['reason']if q['firstFailure']else'CAP'}for q in r['rows']]}));raise SystemExit(0 if r['pass']else 1)
