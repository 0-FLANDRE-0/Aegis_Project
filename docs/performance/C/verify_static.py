"""Full-original syntax, packed bytes, exact rebuild and unchanged authority/update paths."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,decoded,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch);modules=(HERE/'radar-cache.js').read_text()
 checks={'pinnedPERFB':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'exactRebuild':build(b).replace(OLD,NEW)==c}
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['assets0to12Exact']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  compressed=base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]);raw=gzip.decompress(compressed)
  checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and len(compressed)==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['sourceModelsExact']=assets(bh)==assets(ch)
 checks['noTruthRngOrClock']=not re.search(r'\b(?:truthRef|enemyMissiles|targetPool|harpoonWorldA|ENGAGEMENT_RUNTIME|SIM_RNG_STATE|simRandom)\b|Math\.random|performance\.now|Date\.now',modules)
 checks['noAuthorityOrPhysicsWrites']=not re.search(r'\.heading\s*=|\.speed\s*=|positionWorld\.[xy]\s*=|\.identity\s*=|\.engagementAuthority\s*=',modules)
 checks['noPersistentCacheSerialization']=c.count('trackRadarAssociationCachePerfC')==2
 checks['exactFullStateAndCovarianceInputs']='i<6' in modules and 'i<36' in modules and 'Object.is(old.x[i],x[i])'in modules and 'Object.is(old.P[i],P[i])'in modules
 checks['sensorAndNoiseInputsExact']=all('Object.is(old.'+k in modules for k in ['ox','oy','oz','ovx','ovy','ovz'])and all('Object.is(noise['+str(i)+']'in modules for i in range(4))
 checks['oneBoundedKernelPerTrack']='new WeakMap()'in modules and 'cache.set(tr,entry)'in modules and 'new Map()'not in modules
 checks['allFixedPhasesRetained']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);','teamFixedStepH4();'])
 idx=json.loads((HERE/'patch-index.json').read_text());checks['allNativeSourceSlicesPinned']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for rows in idx.values()for q in rows)
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=Path(tmp)/'base.js';bf.write_text(b);f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  scope=json.loads(subprocess.check_output(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)]));checks['scopeNoNewUnresolved']=scope['pass']
  guards=['vlsReleaseB2SupportPreflight','vlsReleaseB2Request','vlsReleaseStandardB1','vlsReleaseEssmB1','wip119EvaluateRow','wip119FireOne','defenseLocalReleaseH4A','surfaceMissileReleaseGateWip13C4','surfaceEssmLiveReleaseGateWip13C6','surfaceSm2LiveReleaseGateWip13C5']
  updates=['trackEkfInit','trackEkfPredict','trackEkfUpdateRadar','trackEkfUpdateSurfaceRadar2D','trackRadarPrediction','trackEkfRadarJacobian','trackSurfaceRadarAssociationNisV35','trackSurfacePositionAssociationNisWip13B9','observerAcceptPlotsC','spyGlobalAssignmentsV36','spyBestPlotForTrackV31','executeSpyTask','spyExecuteSurfacePlotsWip13B9','spq9bAcceptAnonymousPlotsV34','updateSensorTrackMeasurement','wip118BuildEngagementControl','shipFrameForInputsPerfB','wip118NezForecastPerfB','wip118NezCandidatesPerfB']
  sources=[json.loads(subprocess.check_output(['node',str(HERE/'function_sources.cjs'),str(src),*(guards+updates)]))for src in [bf,f]]
  checks['actualReleaseFunctionsByteIdentical']=all(sources[0].get(n)and sources[0][n]==sources[1].get(n)for n in guards)
  checks['nativeUpdateAndAssignmentAndPriorCachesByteIdentical']=all(sources[0].get(n)and sources[0][n]==sources[1].get(n)for n in updates)
 report={'htmlSha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
