"""Full packing/syntax/scope, unchanged authority and reproducible final bytes."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,envelope,decoded,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch)
 checks={'baselinePinned':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'mainRebuildExact':build(b).replace(OLD,NEW)==c,'DDGEnvelopeRebuildExact':envelope(decoded(bh,2))==decoded(ch,2)}
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['allOtherPackedAssetsExact']=all(x==y for i,(x,y)in enumerate(zip(records(bh),records(ch)))if i not in [2,13])
 with tempfile.TemporaryDirectory()as tmp:
  for i,row in enumerate(records(ch)):
   z=base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]);raw=gzip.decompress(z);checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and len(z)==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256'];f=Path(tmp)/f'asset{i}.mjs';f.write_bytes(raw);checks['packedSyntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['loaderSyntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=Path(tmp)/'base.js';bf.write_text(b);cf=Path(tmp)/'main.mjs';cf.write_text(c);scope=json.loads(subprocess.check_output(['node',str(HERE/'verify_scope.cjs'),str(bf),str(cf)]));checks['scopeNoNewUnresolved']=scope['pass']
  names=['vlsReleaseB2SupportPreflight','vlsReleaseB2Request','vlsReleaseStandardB1','vlsReleaseEssmB1','wip119EvaluateRow','wip119FireOne','defenseLocalReleaseH4A','surfaceMissileReleaseGateWip13C4','surfaceEssmLiveReleaseGateWip13C6','surfaceSm2LiveReleaseGateWip13C5','trackEkfUpdateRadar','trackRadarAssociationNisV31','trackRadarAssociationKernelPerfC','spyGlobalAssignmentsV36','observerAcceptPlotsC','shipFrameForInputsPerfB','wip118NezForecastPerfB','wip118NezCandidatesPerfB','wip12eSolveCompartmentBlast','damageFloodImpactV1','physicalDamageImpactB','simulateFixedTick']
  sources=[json.loads(subprocess.check_output(['node',str(HERE/'function_sources.cjs'),str(f),*names]))for f in [bf,cf]]
  for n in names:checks['unchanged_'+n]=bool(sources[0].get(n))and sources[0][n]==sources[1].get(n)
  for i in [2,13]:
   bf.write_text(decoded(bh,i));cf.write_text(decoded(ch,i));q=json.loads(subprocess.check_output(['node',str(HERE/'verify_scope.cjs'),str(bf),str(cf)]));checks['assetScope'+str(i)]=q['pass']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['modelAndEnvelopeSourceBytesExact']=assets(bh)==assets(ch)
 checks['fixedPhasesRetained']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);','teamFixedStepH4();'])
 report={'htmlSha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
