"""Pinned HELI_A → HELI_B; replace aviation modules and its read-only renderer."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='35dbbb64f3067768494c9c6b08d3dc7f02d53cc223f80f4fc7f4970dcb871477'
OLD='v48_WIP_HELI_A';NEW='v48_WIP_HELI_B'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 old='\n'.join((ROOT/'docs/helicopter/B'/f).read_text()for f in ['motion.js','runtime.js','ui.js']);new='\n'.join((HERE/f).read_text()for f in ['motion.js','runtime.js','ui.js']);assert s.count(old)==1;s=s.replace(old,new,1)
 def render(folder):return (folder/'render.js').read_text().replace('__HELO_RIG_JSON__',json.dumps(json.loads((folder/'rig.json').read_text()),separators=(',',':')))
 old=render(ROOT/'docs/helicopter/B');assert s.count(old)==1;s=s.replace(old,render(HERE),1)
 return s

def build_html(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace(OLD,NEW);z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
 html=html.replace(OLD,NEW).replace('V48_WIP_HELI_A','V48_WIP_HELI_B')
 return html,main

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build_html(a.baseline.read_bytes());a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);report={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'changedPackedAssets':[13],'bytes':len(html.encode()),'addedBytes':len(html.encode())-a.baseline.stat().st_size,'assetSha256':hashlib.sha256((ROOT/'docs/helicopter/A/seahawk-render-a1.bin.gz').read_bytes()).hexdigest()};a.output.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
