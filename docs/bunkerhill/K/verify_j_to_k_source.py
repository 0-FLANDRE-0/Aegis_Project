"""Exact refinement and unchanged profiles, mesh records and installations."""
from pathlib import Path
import sys,re,gzip,base64,json,hashlib
from refine_bunker_k import refine_k
j,k,out=map(Path,sys.argv[1:]);checks={}
def read(p):
 h=p.read_text();data={int(i):v for i,v in re.findall(r'<script type="application/octet-stream" data-c55-index="(\d+)">(.*?)</script>',h,re.S)}
 return h,data,gzip.decompress(base64.b64decode(data[13])).decode()
jh,jr,js=read(j);kh,kr,ks=read(k)
checks['exactJBaseline']=hashlib.sha256(j.read_bytes()).hexdigest()=='05306084448d4b68e25f696276346d3b9b2d4899d01a6b6d5b7ae2be9e2323b6'
checks['onlyDeclaredKRefinement']=refine_k(js)==ks
checks['original13RecordsExact']=all(jr[i]==kr[i]for i in range(13))
checks['allSixCGAssetsExact']=all(re.search(r'<script id="cg52-'+s+r'" type="application/octet-stream">(.*?)</script>',jh,re.S)[1]==re.search(r'<script id="cg52-'+s+r'" type="application/octet-stream">(.*?)</script>',kh,re.S)[1]for s in ['registration','envelope','meta','components','geo','projection'])
def profile(s,name):
 start=s.index('const '+name+'=');return s[start:s.index('\n}));',start)+len('\n}));')]
checks['DDGProfileExact']=profile(js,'DDG_119_LATE_FLIGHT_IIA_PROFILE')==profile(ks,'DDG_119_LATE_FLIGHT_IIA_PROFILE')
start='function makeBunkerShipProfile(';end='const CG_52_LATE_TICONDEROGA_PROFILE=makeBunkerShipProfile();'
checks['CGProfileExact']=js[js.index(start):js.index(end)+len(end)]==ks[ks.index(start):ks.index(end)+len(end)]
checks['physicalSpyLayoutExact']=js[js.index('const WIP199_SPY_LAYOUT'):js.index('const WIP199_SPY_HITBOXES')]==ks[ks.index('const WIP199_SPY_LAYOUT'):ks.index('const WIP199_SPY_HITBOXES')]
r={'schema':'AEGIS_J_TO_K_SOURCE_AUDIT_1','baseline':j.name,'candidate':k.name,'sha256':hashlib.sha256(k.read_bytes()).hexdigest(),'checks':checks,'passed':sum(checks.values()),'total':len(checks),'pass':all(checks.values())}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(0 if r['pass']else 1)
