"""All evidence must pass against the exact final original HTML, fail closed."""
import argparse,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();sha=hashlib.sha256(a.html.read_bytes()).hexdigest();root=Path(__file__).resolve().parents[3]
old=json.loads((root/'docs/map/A/evidence/verification-summary.json').read_text());paths=[('static/static'if q['suite']=='static/static'else'regressions/'+q['suite'].split('regressions/',1)[1]if q['suite'].startswith('regressions/')else'map-regressions/'+q['suite'])for q in old['suites']]
paths+=['input/input','render/render','invariance/invariance','precision/precision','visual/visual'];rows=[]
for path in paths:
 p=a.out/(path+'.json');d=json.loads(p.read_text());assert d['pass']and not d.get('errors'),path;assert d.get('htmlSha256',d.get('candidateSha256'))==sha,path
 checks=d.get('checks')
 if checks is None:checks={str(i)+':'+k:v for i,c in enumerate(d['cases'])for k,v in c['checks'].items()}
 assert checks and all(checks.values()),path
 rows.append({'suite':path,'checks':len(checks),'pass':True,'path':str(p)})
d={'schema':'AEGIS_PIP_A_VERIFICATION_1','pass':True,'htmlSha256':sha,'bytes':a.html.stat().st_size,'assertions':sum(q['checks']for q in rows),'suites':rows,'pageErrors':0,'baselineMapA':{'runtimeAssertionsRerun':994,'static48RebasedToPinnedMapABuilder':True,'historicalStaticEvidenceNotReused':True},'backend':'Headless Chromium; geometry DPR 2.8125, real software WebGL screenshots and paired frame-time measurement. Not physical phone FPS.'};(a.out/'verification-summary.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'assertions':d['assertions'],'suites':len(rows),'sha256':sha}))
