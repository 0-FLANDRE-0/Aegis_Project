"""Collect actual receipts; never manufacture pass values or count old pinned checks."""
import gzip,hashlib,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
SOURCES={
 'static':'/tmp/pip-b-final3-static','pip-ui':'/tmp/pip-b-final3-ui','pip-input':'/tmp/pip-b-final3-input','pip-render':'/tmp/pip-b-final3-render','pip-invariance':'/tmp/pip-b-final3-invariance','precision':'/tmp/pip-b-precision','beams':'/tmp/pip-b-final3-beams','circle':'/tmp/pip-b-circle-final2','visual':'/tmp/pip-b-final3-visual-retry',
 'map-input':'/tmp/pip-b-map/input','map-additional':'/tmp/pip-b-map/additional','map-preferences':'/tmp/pip-b-map/preferences','map-legacy':'/tmp/pip-b-map/legacy','map-invariance':'/tmp/pip-b-map/invariance','map-3d':'/tmp/pip-b-gpu-fast/3d','map-examples':'/tmp/pip-b-map/examples','map-bounds':'/tmp/pip-b-map/bounds','ui-a1':'/tmp/pip-b-ui-a1-fast/ui-a1','ui-a1-events':'/tmp/pip-b-map/ui-a1-events','ui-a1-hash':'/tmp/pip-b-final3-hash/ui-a1-hash','domain':'/tmp/pip-b-final-domain'
}
receipts=[]
def copy(src,dst):
 data=src.read_bytes()
 if len(data)>524288 and src.suffix=='.json':dst=dst.with_name(dst.name+'.gz');data=gzip.compress(data,6,mtime=0)
 dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists()or dst.read_bytes()!=data:dst.write_bytes(data)
 return dst
for name,path in SOURCES.items():
 root=Path(path)
 for src in root.rglob('*'):
  if not src.is_file()or src.suffix not in ['.json','.png','.log']:continue
  dst=copy(src,H/'evidence'/name/src.relative_to(root))
  if src.suffix=='.json':
   try:q=json.loads(src.read_text())
   except ValueError:continue
   if isinstance(q,dict)and src.name=='baseline-comparison.json':q={**q,'checks':{f"{r['ship']}.{r['scenario']}.{k}":v for r in q['cases']for k,v in r['checks'].items()},'htmlSha256':q.get('candidateSha256')}
   if isinstance(q,dict)and isinstance(q.get('checks'),dict)and 'pass'in q:
    receipts.append({'suite':name+'/'+str(src.relative_to(root).with_suffix('')),'checks':len(q['checks']),'pass':q['pass'],'path':str(dst.relative_to(R)),'testedHtmlSha256':q.get('htmlSha256'),'failed':[k for k,v in q['checks'].items()if not v]})
summary={'schema':'AEGIS_PIP_B_VERIFICATION_1','pass':len(receipts)==35 and all(q['pass']for q in receipts),'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_PIP_B.html').read_bytes()).hexdigest(),'assertions':sum(q['checks']for q in receipts),'suiteCount':len(receipts),'suites':receipts,'scope':'Runtime regressions plus final UI acceptance; per-receipt tested SHA retained. Earlier component runs are paired with final source/function preservation audit.'}
(H/'evidence/verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
for src in Path('/tmp/pip-b-dom-screens').glob('*.png'):copy(src,H/'screenshots'/src.name)
copy(Path('/tmp/pip-b-screens/screenshots.json'),H/'evidence/density-and-webgl.json')
print(json.dumps({'pass':summary['pass'],'assertions':summary['assertions'],'suites':len(receipts),'failures':[q['suite']for q in receipts if not q['pass']]}))
