#!/usr/bin/env python3
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess,sys,tempfile
result,baseline=map(Path,sys.argv[1:]);checks={}
def read(p):
    h=p.read_text();blobs={int(i):base64.b64decode(s)for i,s in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
    return h,blobs,json.loads(re.search(r'const records=(\[.*?\]);',h,re.S)[1])
h,blobs,records=read(result);b,old,_=read(baseline)
checks['baselineHash']=hashlib.sha256(baseline.read_bytes()).hexdigest()=='7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d'
checks['allRecords']=set(blobs)==set(range(14))and len(records)==14
checks['embeddedAssetsUnchanged']=all(blobs[i]==old[i]for i in range(13))
main=gzip.decompress(blobs[13]).decode();prev=gzip.decompress(old[13]).decode()
def profile(s):return s[s.index('const DDG_119_LATE_FLIGHT_IIA_PROFILE='):s.index('const SHIP_PROFILE_REGISTRY_V48_WIP09=')]
checks['immutableDdgProfileUnchanged']=profile(main)==profile(prev)
for i,row in enumerate(records):
    raw=gzip.decompress(blobs[i]);checks[f'recordIntegrity{i}']=hashlib.sha256(raw).hexdigest()==row['sha256']and len(raw)==row['rawBytes']and len(blobs[i])==row['gzipBytes']
with tempfile.TemporaryDirectory()as tmp:
    tmp=Path(tmp);scripts=[gzip.decompress(blobs[i]).decode()for i,r in enumerate(records)if r['type']in('text/javascript','application/javascript','module')]
    scripts+=[source for attrs,source in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',h,re.S|re.I)if not any(t in attrs for t in('application/octet-stream','application/json','text/plain'))]
    for i,s in enumerate(scripts):
        p=tmp/f'{i}.js';p.write_text(s);checks[f'syntax{i}']=subprocess.run(['node','--check',str(p)],capture_output=True).returncode==0
    rebuilt=tmp/'rebuilt.html';r=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'build_startup.py'),str(baseline.resolve()),str(rebuilt)],capture_output=True)
    checks['exactRebuild']=r.returncode==0 and rebuilt.read_bytes()==result.read_bytes()
out={'schema':'AEGIS_SHIP_STARTUP_PACKAGE_V1','bytes':result.stat().st_size,'sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'checks':checks,'passed':sum(checks.values()),'total':len(checks),'pass':all(checks.values())}
print(json.dumps(out,indent=2));raise SystemExit(0 if out['pass']else 1)
