"""Final H1 packing, rebuild, scope, preserved kernels and observation boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch);checks={'pinnedG':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'exactRebuild':build(b).replace(OLD,NEW)==c};records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['assets0to12Exact']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  raw=gzip.decompress(base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]));checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['sourceModelsExact']=assets(bh)==assets(ch)
 modules='\n'.join((HERE/name).read_text()for name in ['tactical.js','ui.js'])
 checks['noTargetTruthOrPeerPrivateFcs']=not re.search(r'\b(?:truthRef|_truthObject|enemyMissiles|targetPool|harpoonWorldA|truthObjectForTrackV27|physicalFleetSnapshotB|navalFlightObjectsD)\b',modules)
 checks['noRngWallClockOrProfileSwap']=not re.search(r'\bsimRandom|Math\.random|performance\.now|Date\.now|\beval\s*\(|new Function|(?:^|[;}])\s*(?:ACTIVE_SHIP_PROFILE|ACTIVE_SHIP_RUNTIME|IS_BUNKER)\s*=',modules)
 checks['nativeUtilityBothOwners']=c.count('tacticalEvaluateH1(ACTIVE_SHIP_RUNTIME,wip118ControlState,inventory,getShipDamageEffects());')==2
 checks['priorityBeforeAndAfterAllocation']=c.count('tacticalOrderH1(ACTIVE_SHIP_RUNTIME,wip118ThreatRows())')==2 and c.count('tacticalRecommendationOrderH1(ACTIVE_SHIP_RUNTIME,a,b)')==2
 checks['salvoBothNativeOwners']=c.count('function wip118SalvoPolicyNativeH1(')==2 and c.count('return tacticalSalvoH1(ACTIVE_SHIP_RUNTIME,th,weapon,')==2
 checks['fixedWorldOwnerTicksUnchanged']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);'])
 checks['manualRadarAndEwHooked']='tacticalNoteOperatorH1(ACTIVE_SHIP_RUNTIME' in c and "if(origin==='OPERATOR')tacticalNoteOperatorH1"in c
 checks['strictSettingsAndDeferred']='validateTacticalSettingsH1(q.tactical,errors)'in c and 'utilityDecisionsPrioritiesAndEffectOwnership'in c
 checks['groupYieldAndBoundedMemory']='received group consent supersedes'not in c and 'tacticalYieldRadarH1(r);if(n.groupBase===null)'in c and 'maxTracks:96,maxLog:64'in c
 checks['noNavigationCommand']=not re.search(r'physicalShipCommandB|targetSpeedKt\s*=|targetRudder\s*=',modules)
 idx=json.loads((HERE/'patch-index.json').read_text());checks['pinnedFunctionProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in idx.values())
 for name in ['updateMissileBodyB3','updateRamSixDof','harpoonFlightStepA','harpoonSeekerA','harpoonImuSampleC','harpoonRouteStepE','phalanxIntegratePointMass','wip12aTraceTerminalProjectile','wip118PredictTrackCPA','syncOceanEffectsOwnerF','networkVlsGateG']:
  lo=b.index('function '+name+'(');m=re.search(r'\n {0,2}function \w+\(',b[lo+20:]);hi=lo+20+m.start();checks['retainedKernel.'+name]=b[lo:hi]in c
 q=idx['wip118SalvoPolicy'];checks['nativeSalvoLogicExact']=b[q['start']:q['end']].replace('function wip118SalvoPolicy(','function wip118SalvoPolicyNativeH1(',1)in c
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0;bf=Path(tmp)/'base.js';bf.write_text(b);s=subprocess.run(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)],capture_output=True,text=True);scope=json.loads(s.stdout);checks['scopeNoNewUnresolved']=scope['pass']
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
