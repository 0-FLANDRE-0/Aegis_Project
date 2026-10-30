"""RANGE_A: eight SIM_TUNED design-range values on pinned ALL4_TERM; no flight math edits."""
from pathlib import Path
import base64,gzip,hashlib,json,re
H=Path(__file__).resolve().parent;R=H.parents[3];C=R/'docs/envelope/C'
BASE_SHA='c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800'
NAME='Aegis_SIM_v48_WIP_RANGE_A.html'
EDITS=[('nominalRmaxKm:200,minRmaxKm:45,maxRmaxKm:250','nominalRmaxKm:450,minRmaxKm:45,maxRmaxKm:450'),('nominalRmaxKm:180,minRmaxKm:40,maxRmaxKm:220','nominalRmaxKm:360,minRmaxKm:40,maxRmaxKm:360'),("id:'SM2ER_B4',mode:'LOFT',rangeGoalKm:240,fullLoftKm:240","id:'SM2ER_B4',mode:'LOFT',rangeGoalKm:360,fullLoftKm:360"),("id:'SM6_B4',mode:'LOFT',rangeGoalKm:240,fullLoftKm:260","id:'SM6_B4',mode:'LOFT',rangeGoalKm:450,fullLoftKm:450")]
def unpack(h):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)[1])).decode()
def live(s):
 a=s.index('// ENV_B: cumulative ALL4_TERM diagnostic-only source capsule.');b=s.index('\n  completeShipStartup();',a)
 return s[:a]+s[b:]
def source():
 proof=json.loads((C/'stage0/verification.json').read_text());assert proof['pass'] and proof['bitIdentical'] and proof['rangeCapKm']==500
 p=R/'Aegis_SIM_v48_WIP_ALL4_TERM.html'
 if not p.exists():p=R/'archive/v48/WIP_ALL4_TERM'/p.name
 raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 h=raw.decode();s=live(unpack(h))
 for old,new in EDITS:assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
 return h,s

def main():
 h,s=source();Path('/tmp/range-a').mkdir(exist_ok=True);Path('/tmp/range-a/live.js').write_text(s)
 adapter=C/'adapter.js'
 if not adapter.exists():print('prepared live source only; ENV_C not generated');return
 s=s.replace('\n  completeShipStartup();','\n'+adapter.read_text()+'\n  completeShipStartup();',1)
 z=gzip.compress(s.encode(),9,mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S)
 h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest())
 h=h[:m.start(1)]+json.dumps(records,separators=(',',':'))+h[m.end(1):]
 # Version labels outside the packed live script are presentation metadata only.
 h=h.replace('v48_WIP_ALL4_TERM','v48_WIP_RANGE_A').replace('V48_WIP_ALL4_TERM','V48_WIP_RANGE_A')
 p=R/NAME;p.write_text(h);print(json.dumps({'html':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
