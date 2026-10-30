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
 processing='\n'.join(Path(__file__).with_name(n).read_text()for n in ['observer.js','offboard.js'])
 checks['noTrackTruthAccess']=not re.search(r'_truthObject|truthRef|targetPool|enemyMissiles|surfaceContacts|\.physicalWorld|\.world\.entities',re.sub(r'function (?:observerFixtureC|offboardFixtureC)\(\)\{.*?\n\}', '', processing,flags=re.S))
 checks['noProfileOrGlobalSwap']=not re.search(r'ACTIVE_SHIP_PROFILE\s*=|ACTIVE_SHIP_RUNTIME\s*=|IS_BUNKER\s*=',processing)
 checks['singleObserverTick']=c.count('stepObserversC(dt);')==1
 checks['singleWeatherTick']=c.count('updateMaritimeEnvironmentWip13A3(dt);')==b.count('updateMaritimeEnvironmentWip13A3(dt);')
 for start,end in [('function damageFloodTickV1(', 'function damageFloodImpactV1('),('function harpoonStepA(', 'function '),('function applyInterceptResult(', 'function '),('function updateMissileBodyB3(', 'function ')]:
  if start not in b:continue
  lo=b.index(start);hi=b.index(end,lo+len(start));checks['unchanged.'+start]=b[lo:hi] in c
 with tempfile.TemporaryDirectory()as tmp:
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',ch,re.S)):
   if 'application/octet-stream' in m[1]or not m[2].strip():continue
   f=Path(tmp)/f'script{i}.mjs';f.write_text(m[2]);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  f=Path(tmp)/'main.mjs';f.write_text(c);checks['mainSyntax']=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  out=Path(tmp)/'rebuilt.html';subprocess.run(['python',str(Path(__file__).with_name('build.py')),str(a.baseline),str(out)],capture_output=True,check=True);checks['exactHtmlRebuild']=out.read_bytes()==a.candidate.read_bytes()
 report={'sha256':hashlib.sha256(ch.encode()).hexdigest(),'checks':checks,'pass':all(checks.values())};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
