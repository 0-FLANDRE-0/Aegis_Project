"""Fail closed if any primary evidence is missing, failed or from another HTML."""
import argparse,hashlib,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('evidence',type=Path);a=ap.parse_args();sha=hashlib.sha256(a.html.read_bytes()).hexdigest()
paths=['static/static','input/input','additional/additional','preferences/preferences','legacy/legacy','invariance/invariance','3d/3d','examples/examples','bounds/bounds','ui-a1/compact','ui-a1-events/events','ui-a1-hash/hash']
paths+=['regressions/'+p for p in ['helicopter-flight/native','aps153/native','isar-native/native','isar-classes/classes','isar-clock/clock','isar-ui/ui','emcon-native/native','emcon-ui/ui','harpoon-f1/native','harpoon-clock/ui-clock','sov-native/native','sov-casualty/casualty','sov-deployment/deployment','sov-visual/visual','paired-baseline/baseline-comparison']]
rows=[]
for path in paths:
 p=a.evidence/(path+'.json');d=json.loads(p.read_text());assert d['pass']and not d.get('errors'),path;assert d.get('htmlSha256',d.get('candidateSha256'))==sha,path
 checks=d.get('checks')
 if checks is None:checks={str(i)+':'+k:v for i,c in enumerate(d['cases'])for k,v in c['checks'].items()}
 assert checks and all(checks.values()),path
 rows.append({'suite':path,'checks':len(checks),'pass':True,'path':str(p)})
out={'schema':'AEGIS_MAP_A_VERIFICATION_1','pass':True,'htmlSha256':sha,'bytes':a.html.stat().st_size,'assertions':sum(r['checks']for r in rows),'suites':rows,'pageErrors':0,'historicalUiA1144NotClaimedRerun':True,'uiA1StaticSupersededBy48Checks':True,'backend':'Headless Chromium / software WebGL, DPR 2.8125; not physical phone FPS'}
(a.evidence/'verification-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'suites':len(rows),'assertions':out['assertions'],'sha256':sha}))
