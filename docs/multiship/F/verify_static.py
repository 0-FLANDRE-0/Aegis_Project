"""Pinned rebuild, all inline syntax, retained physical/weapon spans and truth boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import BASE_SHA,build,OLD,NEW
def decoded(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.candidate.read_text();b=decoded(bh);c=decoded(ch);checks={}
 checks['pinnedBaseline']=hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA
 checks['exactDeclaredMain']=build(b).replace(OLD,NEW)==c
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
 checks['unchangedAssetRecords']=records(bh)[:13]==records(ch)[:13]
 for i,r in enumerate(records(ch)):
  raw=gzip.decompress(base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]));checks['packedRecord'+str(i)]=len(raw)==r['rawBytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)}
 checks['sourceModelsExact']=assets(bh)==assets(ch)
 owner=Path(__file__).with_name('owner.js').read_text()
 checks['freshAndReleaseRecheck']='defenseGateE' in c and 'const releaseGate=trackEngagementGateA3(pending.trackId' in c
 checks['threeOwnerScenario']='allyProfileId' in c and 'enemyMinM:10000' in c and 'enemyMaxM:30000' in c
 checks['strictEWSettings']='validateElectronicSettingsF(src.ship?.ew,errors)' in c
 checks['noRuntimeEvalOrProfileSwap']=not re.search(r'\beval\s*\(|new Function|(?:^|[;}])\s*(?:ACTIVE_SHIP_PROFILE|ACTIVE_SHIP_RUNTIME|IS_BUNKER)\s*=',owner)
 checks['passiveContactHasNoTruth']='source:source.owner' not in c and "rangeKm:null,identity:'UNKNOWN'" in c
 checks['nativeWeaponTick']=c.count('stepWeaponsD(dt);')==1
 checks['receiverTick']=c.count('stepElectronicReceiversF(dt);')==1
 checks['ownerEwTick']=c.count('stepElectronicOwnersF(dt);')==1
 checks['registeredSoftKillReuse']='@ORIGINAL_EW_FUNCTIONS_F@' not in c
 index=json.loads(Path(__file__).with_name('function-index.json').read_text())
 checks['ownerKernelProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256'] for q in index.values())
 ocean_index=json.loads(Path(__file__).with_name('ocean-index.json').read_text())
 checks['ownOceanKernelUnchanged']=all(b[q['start']:q['end']]in c for q in ocean_index.values())
 checks['oceanKernelProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in ocean_index.values())
 ocean=Path(__file__).with_name('ocean.js').read_text()
 checks['oceanPresentationOnly']='@ORIGINAL_OWNER_OCEAN_KERNEL_F@'not in c and not re.search(r'simRandom|Math.random|stepSimulation|runFramesToTicks',ocean)
 checks['oceanOwnerLifecycle']='disposeShipOceanEffectsF(v);'in c and 'syncShipOceanEffectsF(this,v,st);'in c
 for name in ['updateMissileBodyB3','updateRamSixDof','harpoonFlightStepA','harpoonSeekerA','harpoonImuSampleC','phalanxIntegratePointMass','wip12aTraceTerminalProjectile','wip118PredictTrackCPA']:
  lo=b.index('function '+name+'(');hi=lo+20+re.search(r'\n {0,2}function \w+\(',b[lo+20:]).start();span=b[lo:hi]
  checks['retainedKernel.'+name]=span in c
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream' in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  out=Path(tmp)/'rebuilt.html';subprocess.run(['python',str(Path(__file__).with_name('build.py')),str(a.baseline),str(out)],capture_output=True,check=True);checks['exactHtmlRebuild']=out.read_bytes()==a.candidate.read_bytes()
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'checks':checks,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
