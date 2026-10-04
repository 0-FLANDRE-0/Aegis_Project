from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess,sys,tempfile
result,baseline=map(Path,sys.argv[1:]);checks={}
def read(p):
 h=p.read_text(encoding='utf-8');blobs={int(i):base64.b64decode(s) for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
 records=json.loads(re.search(r'const records=(\[.*?\]);',h,re.S).group(1));return h,blobs,records
h,blobs,records=read(result);b,old,_=read(baseline)
checks['baselineHash']=hashlib.sha256(baseline.read_bytes()).hexdigest()=='6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24'
checks['allRecords']=set(blobs)==set(range(14)) and len(records)==14
checks['embeddedAssetsUnchanged']=all(blobs[i]==old[i] for i in range(13))
main=gzip.decompress(blobs[13]).decode();prev=gzip.decompress(old[13]).decode();marker='  const WIP148_THREE_VERSION='
checks['simulationPrefixUnchanged']=main[:main.index(marker)]==prev[:prev.index(marker)]
for i,row in enumerate(records):checks[f'recordHash{i}']=hashlib.sha256(gzip.decompress(blobs[i])).hexdigest()==row['sha256']
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);scripts=[gzip.decompress(blobs[i]).decode() for i,r in enumerate(records) if r['type'] in ('text/javascript','application/javascript','module')]
 scripts += [source for attrs,source in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I) if not any(t in attrs for t in ('application/octet-stream','application/json','text/plain'))]
 for i,s in enumerate(scripts):
  p=tmp/f'{i}.js';p.write_text(s);checks[f'syntax{i}']=subprocess.run(['node','--check',str(p)],capture_output=True).returncode==0
 rebuilt=tmp/'rebuilt.html';r=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'build_wip16b.py'),str(baseline.resolve()),str(rebuilt)],capture_output=True)
 checks['exactRebuild']=r.returncode==0 and rebuilt.read_bytes()==result.read_bytes()
out={'schema':'AEGIS_WIP16B_PACKAGE','bytes':result.stat().st_size,'sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values())}
print(json.dumps(out,indent=2));raise SystemExit(0 if out['pass'] else 1)
