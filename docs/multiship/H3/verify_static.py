"""Final H3 packing, rebuild, scope, preserved kernels and observation boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch);checks={'pinnedH2':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'exactRebuild':build(b).replace(OLD,NEW)==c};records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['assets0to12Exact']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  raw=gzip.decompress(base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]));checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['sourceModelsExact']=assets(bh)==assets(ch)
 modules='\n'.join((HERE/name).read_text()for name in ['attack.js','ui.js'])
 checks['noTargetTruthOrPeerPrivateFcs']=not re.search(r'\b(?:truthRef|_truthObject|enemyMissiles|targetPool|harpoonWorldA|truthObjectForTrackV27|physicalFleetSnapshotB|navalFlightObjectsD)\b',modules)
 checks['noRngWallClockOrProfileSwap']=not re.search(r'\bsimRandom|Math\.random|performance\.now|Date\.now|\beval\s*\(|new Function|(?:^|[;}])\s*(?:ACTIVE_SHIP_PROFILE|ACTIVE_SHIP_RUNTIME|IS_BUNKER)\s*=',modules)
 checks['nativeUtilityBothOwnersRetained']=c.count('tacticalEvaluateH1(ACTIVE_SHIP_RUNTIME,wip118ControlState,inventory,getShipDamageEffects());')==2
 checks['oneFixedAttackPhase']=c.count('stepAttackFleetH3();')==1 and 'stepManeuverFleetH2();\n    stepAttackFleetH3();' in c
 checks['strictBothOwnerSettings']='validateAttackSettingsH3(src.ship?.attack,errors)' in c and 'validateAttackSettingsH3(q.attack,errors)' in c
 checks['settingsOnlyAndAuthorityDeferred']='surfaceAttackConsentPlansAndReleaseCapabilities' in c and 'attack:attackSettingsH3(r)' in c and 'attack:attackSettingsH3(ACTIVE_SHIP_RUNTIME)' in c
 checks['typedAuthorityBothOwners']=c.count('options.attackH3?attackAuthorityH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3)')==2 and c.count('attackFinalGuardH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3,result)')==2
 checks['genericAutomaticDenialRetained']=c.count("if(!options.attackH3&&(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO'))return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');")==2
 checks['coordinateSearchRemainsManual']=c.count("if(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');")>=2
 checks['distinctOwnerPorts']='attackRequestH3:(id,token)=>{sync();return harpoonRequestFireA(id,null,{attackH3:token});}' in c
 checks['boundedNoNewPhysics']='periodTicks:12' in c and 'maxTracks:16,maxProtected:64,maxLog:64' in c and not re.search(r'\.heading\s*=|\.speed\s*=|positionWorld\.[xy]\s*=|\bupdateShipMovement\(|\bupdateMissile\(',modules)
 checks['noOpponentPrivateState']=not re.search(r'ENGAGEMENT_RUNTIME\.ships\.get|physicalFleetSnapshotB|shipSurvivalB|ownerTrackKeyD',modules)
 checks['fixedWorldOwnerTicksUnchanged']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);'])
 checks['noFlightTruthOrTelemetry']=not re.search(r'harpoonWorldA|navalFlightObjectsD|harpoonRenderStatesA|seeker\.mode|\.outcome|\.alive',modules)
 checks['exactObjectCapability']='token!==s.releaseToken' in c and 'token.track!==tr' in c and "Object.defineProperty(token,'track',{value:q.tr})" in c
 checks['sameNativeDoorAndInventory']=c.count('if(pending.attackH3)attackCommitH3(ACTIVE_SHIP_RUNTIME,pending.attackH3,gate,serial);')==2
 checks['chartAndProtectedMeasurements']='CHART_ROUTE_BLOCKED' in c and 'PROTECTED_ATTACK_CORRIDOR_OR_SEARCH' in c and 'RECEIVED_PROTECTED' in c
 idx=json.loads((HERE/'patch-index.json').read_text());checks['pinnedFunctionProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in idx.values())
 for name in ['updateMissileBodyB3','updateRamSixDof','harpoonFlightStepA','harpoonSeekerA','harpoonImuSampleC','harpoonRouteStepE','phalanxIntegratePointMass','wip12aTraceTerminalProjectile','wip118PredictTrackCPA','syncOceanEffectsOwnerF','networkVlsGateG','maneuverEvaluateH2','tacticalEvaluateH1','surfaceMissileIdentityPolicyWip13C4']:
  lo=b.index('function '+name+'(');m=re.search(r'\n {0,2}function \w+\(',b[lo+20:]);hi=lo+20+m.start();checks['retainedKernel.'+name]=b[lo:hi]in c
 checks['nativeSalvoLogicExact']=c.count("return tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,wip118SalvoPolicyNativeH1(th,weapon,assessment,plan));")==2
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0;bf=Path(tmp)/'base.js';bf.write_text(b);s=subprocess.run(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)],capture_output=True,text=True);scope=json.loads(s.stdout);checks['scopeNoNewUnresolved']=scope['pass']
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
