"""Final H4A packing, rebuild, scope, preserved kernels and observation boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch);checks={'pinnedH4':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'exactRebuild':build(b).replace(OLD,NEW)==c};records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['assets0to12Exact']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  raw=gzip.decompress(base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]));checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['sourceModelsExact']=assets(bh)==assets(ch)
 modules='\n'.join((HERE/name).read_text()for name in ['local-defense.js','local-ew.js'])
 checks['noTargetTruthOrWorldLookup']=not re.search(r'\b(?:truthRef|_truthObject|enemyMissiles|targetPool|harpoonWorldA|truthObjectForTrackV27|physicalFleetSnapshotB|navalFlightObjectsD|ENGAGEMENT_RUNTIME)\b',modules)
 checks['noRngOrPhysicsWrites']=not re.search(r'\bsimRandom|Math\.random|performance\.now|Date\.now|\.heading\s*=|\.speed\s*=|positionWorld\.[xy]\s*=|\bupdateShipMovement\(|\bupdateMissile\(',modules)
 checks['noIdentityMutation']=not re.search(r'\._operatorIdentity\s*=|\.identity\s*=',modules)
 checks['nativeActualReleaseRechecks']="gate=c.authorityH4A?h.defenseLocalReleaseH4A(mount,p):ownerTrackGateD(r,c.trackId,c)" in c and "defenseE.closeIn.get(mount?.id)!==p" in c and "q.file!==p.localFileH4A" in c
 checks['localOnlyTypedAuthority']="authorityH4A:'LOCAL_SELF_DEFENCE_H4A'" in c and "audit.reason!=='LOCAL_SELF_DEFENCE'" in c
 checks['noFakeCmsOrSamAuthority']="trackId:null,emitterContactId:es.id" in c and "localDefenseCuesH4A:defenseLocalCuesH4A" in c
 checks['measurementsThenUniqueEsm']="rows.length===1" in c and "candidates.filter(t=>t.q===p.q).length!==1" in c
 checks['holdReleasesMount']="wip119CancelPending('AUTO_OFF');for(const mount of ciws)defenseDropMountH4A(mount);" in c
 checks['allFixedPhasesRetained']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);','teamFixedStepH4();'])
 checks['builtInBoundarySelftest']="const defenseH4A=localDefenseSelfTestH4A();" in c
 idx=json.loads((HERE/'patch-index.json').read_text());checks['pinnedFunctionProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in idx.values())
 for name in ['updateMissileBodyB3','updateRamSixDof','harpoonFlightStepA','harpoonSeekerA','harpoonImuSampleC','harpoonRouteStepE','phalanxIntegratePointMass','wip12aTraceTerminalProjectile','wip118PredictTrackCPA','syncOceanEffectsOwnerF','networkVlsGateG','tacticalEvaluateH1','surfaceMissileIdentityPolicyWip13C4','observerAuxStepC','observerExtractC','c55SensorSweep','c55ContactAudit','c55AssociateCms','defenseGateE','wip119FireOne','softKillDoctrineChaffCandidate','deployOwnChaffForThreat','teamFixedStepH4']:
  lo=b.index('function '+name+'(');m=re.search(r'\n {0,2}function \w+\(',b[lo+20:]);hi=lo+20+m.start();checks['retainedKernel.'+name]=b[lo:hi].replace(OLD,NEW)in c
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0;bf=Path(tmp)/'base.js';bf.write_text(b);s=subprocess.run(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)],capture_output=True,text=True);scope=json.loads(s.stdout);checks['scopeNoNewUnresolved']=scope['pass']
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
