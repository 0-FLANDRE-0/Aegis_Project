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
 owner=Path(__file__).with_name('owner.js').read_text();runtime=Path(__file__).with_name('runtime.js').read_text().split('// DIAGNOSTIC_ONLY:')[0]
 checks['controllerNoTruthAccess']=not re.search(r'_truthObject|truthRef|targetPool|enemyMissiles|surfaceContacts|\.world\.entities|alive\b',owner+runtime)
 checks['freshAndReleaseRecheck']='defenseGateE' in c and 'const releaseGate=trackEngagementGateA3(pending.trackId,{automatic:true,mode:' in c
 checks['independentCloseInMeasurement']='q.confirmed&&q.audit?.accepted&&!q.protectedIdentity' in owner and 'q.st.localAgeS<CIWS_C55_POLICY.releaseFreshS' in owner
 checks['perMountCloseIn']='for(const p of [...e.defenseE.closeIn.values()])' in c
 checks['spawnOffConstructors']=c.count('if(!enemyAircraftSpawnsEnabledE())return null;')==2 and 'if(!enemyAircraftSpawnsEnabledE())return;' in c
 checks['versionedStrictScenario']="AEGIS_DEPLOYMENT_MULTI_SHIP_E_1" in c and "DEPLOYMENT_ENEMY_AIRCRAFT" in c
 checks['singleOwnerWeaponTick']=c.count('stepWeaponsD(dt);')==1
 checks['singleWorldHarpoonTick']=c.count('updateHarpoonA(dt);')==b.count('updateHarpoonA(dt);')
 modules='\n'.join(Path(__file__).with_name(n).read_text() for n in ['runtime.js','owner.js','deployment.js'])
 checks['noRuntimeEvalOrProfileSwap']=not re.search(r'\beval\s*\(|new Function|(?:^|[;}])\s*(?:ACTIVE_SHIP_PROFILE|ACTIVE_SHIP_RUNTIME|IS_BUNKER)\s*=',modules)
 checks['nativeVlsIncidentCadence']='context.vlsIncidents(.1,power01,control,p)' in c
 checks['foreignExcludedFromOperatorTelemetry']='navalMissilesD:physicalShipsB()' in c and 'missiles:[...st.missiles,...(st.navalMissilesD??[])]' in c
 index=json.loads(Path(__file__).with_name('function-index.json').read_text())
 checks['ownerKernelProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256'] for q in index.values())
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
