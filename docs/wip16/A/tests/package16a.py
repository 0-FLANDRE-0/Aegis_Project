#!/usr/bin/env python3
from pathlib import Path
import sys,re,base64,gzip,json,hashlib,subprocess,tempfile
def sha(b): return hashlib.sha256(b).hexdigest()
if len(sys.argv)!=3: raise SystemExit("usage: package16a.py RESULT.html BASELINE.html")
res=Path(sys.argv[1]); base=Path(sys.argv[2])
def unpack(p):
    h=p.read_text()
    mm=re.search(r'const records=(\[.*?\]);',h,re.S); rec=json.loads(mm.group(1))
    blobs={}
    for m in re.finditer(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S):
        i=int(m.group(1)); gz=base64.b64decode(m.group(2)); raw=gzip.decompress(gz); blobs[i]=(gz,raw)
    return h,rec,blobs
h,r,b=unpack(res); hb,rb,bb=unpack(base); rows=[]
def check(name,v,detail=None):
    rows.append({"name":name,"pass":bool(v),"detail":detail})
for i in range(14):
    gz,raw=b[i]; q=r[i]
    check(f"record {i} raw sha",sha(raw)==q["sha256"])
    check(f"record {i} raw bytes",len(raw)==q["rawBytes"])
    check(f"record {i} gzip bytes",len(gz)==q["gzipBytes"])
for i in range(13):
    check(f"record {i} byte preserved",b[i][0]==bb[i][0])
main=b[13][1].decode()
check("WIP16 fire-control profile", "PHALANX_FIRE_CONTROL_STABILIZATION_V48_1_WIP16A" in main)
check("3.0 mil fixed dispersion preserved","dispersion80DiameterMil:3.0" in main)
check("range-scaled fire gate wired","phalanxFireControlGate(phalanx,st,sol,turretErr" in main)
check("control-surface region wired","region:'CONTROL_SURFACE'" in main)
check("WIP112 fins geometry reused","wip112BuildSystemBoxes(em).find(q=>q.system==='fins')" in main)
check("control surface immediate crit disabled","controlSurface?0:clamp" in main)
check("diagnostic hit region","hitRegion:hitMeta?.region" in main)
check("diagnostic CIWS local RNG reset","trackingTrackId=null" in main and "delete p._gunAimRngState" in main and "delete p._gunShotRngState" in main)
with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False) as f:
    f.write(main); js=f.name
p=subprocess.run(["node","--check",js],capture_output=True,text=True)
check("main JS syntax",p.returncode==0,p.stderr[-1000:])
out={"schema":"AEGIS_WIP16A_PACKAGE_CHECK","passed":sum(x["pass"] for x in rows),"total":len(rows),"pass":all(x["pass"] for x in rows),"rows":rows}
print(json.dumps(out,ensure_ascii=False,indent=2))
if not out["pass"]: raise SystemExit(1)
