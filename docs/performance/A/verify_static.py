"""Pinned rebuild, full packing/syntax/scope and three-function change boundary."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import build,decoded,BASE_SHA,OLD,NEW
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bh=a.baseline.read_text();ch=a.html.read_text();b=decoded(bh);c=decoded(ch)
 checks={'pinnedH4A':hashlib.sha256(bh.encode()).hexdigest()==BASE_SHA,'exactRebuild':build(b).replace(OLD,NEW)==c}
 records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['assets0to12Exact']=records(bh)[:13]==records(ch)[:13]
 for i,row in enumerate(records(ch)):
  compressed=base64.b64decode(re.search('data-c55-index="'+str(i)+'">(.*?)</script>',ch,re.S)[1]);raw=gzip.decompress(compressed)
  checks['packedRecord'+str(i)]=len(raw)==row['rawBytes']and len(compressed)==row['gzipBytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
 assets=lambda h:{m[1]:m[2]for m in re.finditer(r'<script id="([^"]+)" type="application/octet-stream">(.*?)</script>',h,re.S)};checks['sourceModelsExact']=assets(bh)==assets(ch)
 module=(HERE/'cache.js').read_text()
 checks['noTargetTruthRngOrClock']=not re.search(r'\b(?:truthRef|enemyMissiles|targetPool|harpoonWorldA|ENGAGEMENT_RUNTIME|SIM_RNG_STATE|simRandom)\b|Math\.random|performance\.now|Date\.now',module)
 checks['noPhysicsOrIdentityWrites']=not re.search(r'\.heading\s*=|\.speed\s*=|positionWorld\.[xy]\s*=|\.identity\s*=|\bupdateMissile\(|\bupdateShipMovement\(',module)
 checks['onlyFrozenModuleNamesCached']="!Object.isFrozen(boxes)||!boxes.every(Object.isFrozen)" in module and 'flooding.readDamage(n)' in c
 checks['noSimulationCacheSerialization']=c.count('systemModuleIndexPerfA')==3 and c.count('kh32PaintViewsPerfA')==3
 checks['idempotentLeaseAndListenerRemoval']='if(released)return;released=true;' in module and "body.geometry.removeEventListener('dispose',releasePaint)" in c
 checks['activeDamageDelegatePreserved']='if(r===ACTIVE_SHIP_RUNTIME)return getShipSystemDamage(system,aggregate);' in c
 checks['allFixedPhasesRetained']=all(c.count(x)==b.count(x)==1 for x in ['stepWeaponsD(dt);','stepElectronicOwnersF(dt);','networkFixedStepG(dt);','teamFixedStepH4();'])
 idx=json.loads((HERE/'patch-index.json').read_text());checks['pinnedFunctionProvenance']=all(hashlib.sha256(b[q['start']:q['end']].encode()).hexdigest()==q['sha256']for q in idx.values())
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  bf=Path(tmp)/'base.js';bf.write_text(b);s=subprocess.run(['node',str(HERE/'verify_scope.cjs'),str(bf),str(f)],capture_output=True,text=True);scope=json.loads(s.stdout);checks['scopeNoNewUnresolved']=scope['pass']
 report={'htmlSha256':hashlib.sha256(ch.encode()).hexdigest(),'mainSha256':hashlib.sha256(c.encode()).hexdigest(),'checks':checks,'scope':scope,'pass':all(checks.values())}
 (a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
