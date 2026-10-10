"""Pinned rebuild, syntax/scope deltas, preserved kernels and knowledge boundaries."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import BASE_SHA,build,OLD,NEW
HERE=Path(__file__).resolve().parent
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.candidate.read_text();b=decoded(bh);c=decoded(ch);checks={}
 checks['pinnedBaseline']=hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA
 checks['exactDeclaredMain']=build(b).replace(OLD,NEW)==c
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
 checks['unchangedAssetRecords']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  raw=gzip.decompress(base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]));checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)}
 checks['sourceModelsExact']=assets(bh)==assets(ch)
 modules='\n'.join((HERE/name).read_text()for name in ['network.js','cooperation.js','fleet.js','ui.js','launch-protection.js'])
 checks['noTargetTruthInNetworkOrKnowledge']=not re.search(r'\b(?:truthRef|_truthObject|enemyMissiles|targetPool|harpoonWorldA|truthObjectForTrackV27)\b',modules)
 checks['noRuntimeEvalOrProfileSwap']=not re.search(r'\beval\s*\(|new Function|(?:^|[;}])\s*(?:ACTIVE_SHIP_PROFILE|ACTIVE_SHIP_RUNTIME|IS_BUNKER)\s*=',modules)
 checks['fixedTransportOnce']=c.count('networkFixedStepG(dt);')==1
 checks['originalWorldAndWeaponTicks']=c.count('stepWeaponsD(dt);')==1 and c.count('stepElectronicOwnersF(dt);')==1
 checks['conservativeCorrelatedFusion']='networkIntersectionG' in c and 'file.fused=networkIntersectionG(p.e,p.estimate)'in c
 checks['presentationDoesNotChangeCanonicalFcs']='const tr=networkPresentationTrackG(localTr)'in c and 'fcsSource:\'LOCAL_ONLY\''in c
 checks['delayedRadioAndAge']='availableStep:simStepCounter+NETWORK_POLICY_G.latencyTicks'in c and 'now-q.measuredAtS>NETWORK_POLICY_G.coastS'in c
 checks['twoOwnerSchedulerConsent']=c.count('const net=networkVlsGateG(ACTIVE_SHIP_RUNTIME,pending.trackId')==2
 checks['twoOwnerActualVlsRecheck']=c.count('const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);')==6
 checks['networkSettingsPreflightAndDeferred']='validateNetworkSettingsG(src.ship?.network,errors)'in c and 'networkReportsLeasesAndGroupRuntime'in c
 checks['ownHarpoonNoPrivateFlightPosition']='lastRadarSampleG'in c and 'OWN_LAUNCH_COAST_UNCERTAIN'in c and 'noDataLink:true'not in modules
 checks['observedHarpoonCanBeShared']='!tr._harpoonOwnC'not in (HERE/'network.js').read_text()
 checks['boundedPictureQueuesAndLogs']='maxFiles:96' in c and 'maxQueue:16'in c and 'maxLogs:128'in c
 for name in ['updateMissileBodyB3','updateRamSixDof','harpoonFlightStepA','harpoonSeekerA','harpoonImuSampleC','harpoonRouteStepE','phalanxIntegratePointMass','wip12aTraceTerminalProjectile','wip118PredictTrackCPA','syncOceanEffectsOwnerF']:
  lo=b.index('function '+name+'(');match=re.search(r'\n {0,2}function \w+\(',b[lo+20:]);hi=lo+20+match.start();checks['retainedKernel.'+name]=b[lo:hi]in c
 checks['oceanOwnerLifecycle']='disposeShipOceanEffectsF(v);'in c and 'syncShipOceanEffectsF(this,v,st);'in c
 index=json.loads((HERE/'patch-index.json').read_text());checks['patchProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in index.values())
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=Path(tmp)/'baseline.js';bf.write_text(b);scope=subprocess.run(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)],capture_output=True,text=True);scope_report=json.loads(scope.stdout);checks['scopeNoNewUnresolved']=scope_report['pass'];(a.out/'scope.json').write_text(json.dumps(scope_report,indent=2)+'\n')
  out=Path(tmp)/'rebuilt.html';subprocess.run(['python',str(HERE/'build.py'),str(a.baseline),str(out)],capture_output=True,check=True);checks['exactHtmlRebuild']=out.read_bytes()==a.candidate.read_bytes()
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'checks':checks,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
