"""Packing, syntax, scope, existing combat authority and sensor isolation."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import patch,decoded,BASE_SHA
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);b=a.baseline.read_text();c=a.html.read_text();bm=decoded(b);cm=decoded(c);checks={'baselinePinned':hashlib.sha256(b.encode()).hexdigest()==BASE_SHA,'mainRebuildExact':patch(bm).replace('v48_WIP_PERF_F','v48_WIP_HELI_A')==cm}
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['other13PackedAssetsExact']=records(b)[:13]==records(c)[:13]
 with tempfile.TemporaryDirectory()as tmp:
  for i,row in enumerate(records(c)):
   z=base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',c,re.S)[1]);raw=gzip.decompress(z);checks['record'+str(i)]=len(raw)==row['rawBytes']and len(z)==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];f=Path(tmp)/f'{i}.js';f.write_bytes(raw);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',c,re.S)):
   if'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'loader{i}.js';f.write_text(m[2]);checks['loader'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=Path(tmp)/'base.js';cf=Path(tmp)/'candidate.js';bf.write_text(bm);cf.write_text(cm)
  q=subprocess.run(['node',str(ROOT/'docs/performance/F/verify_scope.cjs'),str(bf),str(cf)],capture_output=True,text=True);scope=json.loads(q.stdout);scope['declaredNewBrowserGlobals']=['DataView','Int16Array'];checks['scopeNoNewUnresolved']=all(name in scope['declaredNewBrowserGlobals']for name in scope['added'])
  names=['vlsReleaseB2Request','vlsReleaseStandardB1','vlsReleaseEssmB1','wip119EvaluateRow','wip119FireOne','defenseLocalReleaseH4A','trackEkfUpdateRadar','trackRadarAssociationNisV31','spyGlobalAssignmentsV36','observerAcceptPlotsC','navalReflectorsC','configureOffboardSourceC','shipFrameForInputsPerfB','wip118NezForecastPerfB','wip12eSolveCompartmentBlast','damageFloodImpactV1','physicalDamageImpactB']
  src=[json.loads(subprocess.check_output(['node',str(ROOT/'docs/performance/F/function_sources.cjs'),str(f),*names]))for f in [bf,cf]]
  for n in names:checks['unchanged_'+n]=bool(src[0].get(n))and src[0][n]==src[1].get(n)
  checks['existingTickPreserved']=src[0].get('simulateFixedTick')==src[1].get('simulateFixedTick')if'simulateFixedTick'in src[0]else cm[cm.index('  function simulateFixedTick'):cm.index('  // ===== WIP150')]==bm[bm.index('  function simulateFixedTick'):bm.index('  // ===== WIP150')]
 modules='\n'.join((HERE/f).read_text()for f in ['motion.js','runtime.js','ui.js']);code=re.sub(r'//[^\n]*','',modules);checks['noSensorOrWeaponRegistration']=not re.search(r'\b(?:targetPool|configureOffboardSourceC|ingestOffboardReportC|navalReflectorsC|weaponCommandD|fireSM2|simRandom)\b',code)
 render=(HERE/'render.js').read_text();checks['renderNoCommandOrFixedIntegration']=not any(x in render for x in ['heloCommandA(','heloFixedStepA(','heloMoveA(']);checks['singleHeloPayload']=c.count('id="helo-render-a1"')==1
 oldassets={m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',b,re.S)};newassets={m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',c,re.S)};checks['existingEmbeddedModelsExact']=all(newassets.get(k)==v for k,v in oldassets.items())
 out={'pass':all(checks.values()),'checks':checks,'scope':scope,'htmlSha256':hashlib.sha256(c.encode()).hexdigest(),'mainSha256':hashlib.sha256(cm.encode()).hexdigest()};(a.out/'static.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
