from pathlib import Path
import gzip,hashlib,json
P=Path(__file__).resolve().parent;R=P.parents[3]
def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
baseline=P/'evidence/baseline-4c-release300/map/E/evidence/c2/AIR_ORIGIN_A_B2_BASELINE/release.json.gz';rows=[]
for mode in ['OFF','ON']:
 file=P/f'evidence/regression/{mode}/map/E/evidence/c2/GUN_B2_{mode}/release.json.gz'
 if baseline.exists()and file.exists():
  a,b=read(baseline),read(file);changes=[{'id':x['id'],'beforeSuccess':x['result']['success'],'afterSuccess':y['result']['success'],'beforeReason':x['result']['reason'],'afterReason':y['result']['reason']}for x,y in zip(a['rows'],b['rows'])if x!=y]
  rows.append({'suite':'release300','mode':mode,'baseline':'ACTUAL_AIR_ORIGIN_A_4c519_REPLAY','baselineFile':str(baseline.relative_to(R)),'candidateFile':str(file.relative_to(R)),'baselineSha256':a['htmlSha256'],'candidateSha256':b['htmlSha256'],'cases':len(b['rows']),'sameAllRows':a['rows']==b['rows'],'baselineRowsSha256':digest(a['rows']),'candidateRowsSha256':digest(b['rows']),'changes':changes,'baselineSuccess':sum(r['result']['success']for r in a['rows']),'candidateSuccess':sum(r['result']['success']for r in b['rows']),'errors':a['errors']+b['errors']})
 natural=R/'docs/radar/air-origin/A/evidence/regression/AIR_ORIGIN_A/map/E/evidence/c2/AIR_ORIGIN_A/natural.json.gz';file=P/f'evidence/regression/{mode}/map/E/evidence/c2/GUN_B2_{mode}/natural.json.gz'
 if natural.exists()and file.exists():
  a,b=read(natural),read(file);rows.append({'suite':'natural28','mode':mode,'baseline':'IMMUTABLE_SAME_4c519_EVIDENCE','baselineFile':str(natural.relative_to(R)),'candidateFile':str(file.relative_to(R)),'baselineSha256':a['htmlSha256'],'candidateSha256':b['htmlSha256'],'cases':len(b['rows']),'sameAllRows':a['rows']==b['rows'],'baselineRowsSha256':digest(a['rows']),'candidateRowsSha256':digest(b['rows']),'errors':a['errors']+b['errors']})
q={'pass':bool(rows)and all(r['sameAllRows']and not r['errors']for r in rows),'rows':rows,'comparison':'Every native case/result/event/trajectory value exact; only outer artifact provenance and host elapsedS are separate.'};(P/'evidence/sam-exact-comparison.json').write_text(json.dumps(q,indent=2)+'\n');print([(r['suite'],r['mode'],r['cases'],r['sameAllRows'])for r in rows]);raise SystemExit(not q['pass'])
