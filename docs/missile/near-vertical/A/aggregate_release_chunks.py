from pathlib import Path
import json
H=Path(__file__).resolve().parent;release=H/'release';parts=release/'parts';build=json.loads((H/'build.json').read_text());expected=build['variants']['FINAL']['htmlSha256']
ranges={'normal':[('normal-0-167.json',0,168),('normal-144-191.json',24,24),('normal-192-239.json',0,48)],'dual':[('dual-0-35.json',0,36)],'fault':[('fault-0-11.json',0,12)],'battery':[('battery-0-7.json',0,8)],'request':[('request-0-3.json',0,4)]};records=[]
for kind,sources in ranges.items():
 rows=[];errors=[];elapsed=0
 for name,offset,count in sources:
  q=json.loads((parts/name).read_text());assert q['htmlSha256']==expected and len(q['results'])>=offset+count;rows+=q['results'][offset:offset+count];errors+=q.get('errors',[]);elapsed+=q.get('elapsedS',0)
 out={'htmlSha256':expected,'results':rows,'errors':errors,'elapsedS':elapsed};(release/f'{kind}.json').write_text(json.dumps(out,separators=(',',':')));records.append({'kind':kind,'results':len(rows),'errors':len(errors),'elapsedS':elapsed})
summary={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_RELEASE_EXECUTIONS_1','records':records,'shots':sum(x['results']for x in records),'errors':sum(x['errors']for x in records)};(H/'release-executions.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));raise SystemExit(0 if summary['shots']==300 and summary['errors']==0 else 1)
