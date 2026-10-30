"""Pinned HELI_E -> HELI_E1; model/background only, packed13 only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OLD=ROOT/'docs/helicopter/F'
BASE_SHA='e34cb884f375600a1c5bb3b0441bb89a385075f4167cfad04242594e26df9bcb'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 for f in ['model.js','radar.js','probes.js']:
  old=(OLD/f).read_text();assert s.count(old)==1,f;s=s.replace(old,(HERE/f).read_text())
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_E','v48_WIP_HELI_E1');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_E','v48_WIP_HELI_E1').replace('V48_WIP_HELI_E','V48_WIP_HELI_E1'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);r={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-a.baseline.stat().st_size};a.output.with_suffix('.manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
