"""Pinned rebuild, every packed JS, scope, source counts and offline hydro/ISAR."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re,subprocess,os,tempfile
from build import build,BASE_SHA,decoded
HERE=Path(__file__).resolve().parent;R=HERE.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();html=raw.decode();baseline=a.baseline.read_bytes();checks={'baselinePinned':hashlib.sha256(baseline).hexdigest()==BASE_SHA,'exactRebuild':build(baseline)[0].encode()==raw};records=lambda h:json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1]);checks['other13AssetsExact']=records(html)[:13]==records(baseline.decode())[:13]
 env=os.environ.copy();env['NODE_PATH']='/workspace/aegis-performance-f/docs/performance/F/node_modules'if Path('/workspace/aegis-performance-f/docs/performance/F/node_modules').exists()else str(R/'docs/performance/F/node_modules')
 with tempfile.TemporaryDirectory()as tmp:
  tmp=Path(tmp)
  for i,row in enumerate(records(html)):
   z=base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',html,re.S)[1]);b=gzip.decompress(z);checks['packed'+str(i)]=len(z)==row['gzipBytes']and len(b)==row['rawBytes']and hashlib.sha256(b).hexdigest()==row['sha256'];f=tmp/(str(i)+'.js');f.write_bytes(b);checks['syntax'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  for i,m in enumerate(re.finditer(r'<script\b([^>]*)>(.*?)</script>',html,re.S)):
   if 'application/octet-stream'in m[1]or not m[2].strip():continue
   f=tmp/f'loader{i}.js';f.write_text(m[2]);checks['loader'+str(i)]=subprocess.run(['node','--check',str(f)],capture_output=True).returncode==0
  b=tmp/'b.js';c=tmp/'c.js';b.write_text(decoded(baseline.decode()));c.write_text(decoded(html));run=subprocess.run(['node',str(R/'docs/performance/F/verify_scope.cjs'),str(b),str(c)],env=env,capture_output=True,text=True);scope=json.loads(run.stdout);checks['noNewUnresolved']=scope['pass']
 r=json.loads((HERE/'registration.json').read_text());meta=json.loads(gzip.decompress((HERE/'meta.json.gz').read_bytes()));meshes=[]
 def walk(n):
  meshes.extend(n['meshes'])
  for c in n['children']:walk(c)
 for s in meta['statics']:meshes.extend(s['meshes'])
 for a0 in meta['assemblies']:walk(a0['root'])
 checks['source48925']=sum(m['idx'][1]//3 for m in meshes)==r['sourceTriangles']==48925;checks['parkedCollisionRegistered']=sum(g['name'].startswith('HARDWARE_')for g in r['groups'])>20;checks['source81Batches']=len(meshes)==r['meshBatches']==81;checks['attributionAndChanges']=all(r['attribution'].get(k)for k in ['title','author','sourceUrl','license','licenseUrl','changes']);checks['sourcePin']=r['sourceSha256']=='c46694e18a68aa11e4741312a904f195afcd9773a12eb5007a55b6a8645afc7f';checks['explicitWaterlineDatum']=r['verticalDatum']=='AUTHORED_WATERLINE_Z0__NO_VERTICAL_OFFSET'and r['mastHeightM']==29.84874
 vol=sum(max(0,min(0,c['top'])-c['bottom'])*c['area']for c in r['hydroColumns']);kg=vol*1025*r['hydroCalibration']['effectiveBuoyancyScale'];checks['7940tAtZeroDatum']=abs(kg-7940000)<.1;checks['inactiveAll']=all(not h['active']and not h['emitter']and not h['installed']for h in r['inactiveHardpoints'])and all(not q['emitter']and not q['active']for q in r['sensorRegistration']['sensors']);checks['RcsStaticEnvelopeLut']=len(r['projectedAreaLut'])==24 and r['projectedAreaLut'][6][1]>r['projectedAreaLut'][0][1]
 lib=json.loads((HERE/'library.json').read_text())['entries'];old=json.loads((R/'docs/helicopter/L/library.json').read_text())['entries'];checks['existingIsarInformationExact']=lib[:3]==old;checks['SovInformation156p5']=lib[-1]['classId']=='SOVREMENNY_956'and lib[-1]['lengthM']==156.5;checks['rendererNoSimulationWrites']=not re.search(r'\.navigation\.|ENGAGEMENT_RUNTIME|simulateFixedTick|SIM_RNG|configureOffboardSource|ingestOffboard', (HERE/'render.js').read_text());checks['classifierAndTransportExact']=all((R/'docs/helicopter/L'/f).read_text()in decoded(html)for f in ['physical.js','sensor.js','transport.js'])
 report={'pass':all(checks.values()),'checks':checks,'scope':scope,'hydroMassAtZeroKg':kg,'htmlSha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'addedBytes':len(raw)-len(baseline)};(a.out/'static.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
