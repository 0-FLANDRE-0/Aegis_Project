"""Pinned HELI_C → HELI_D. A/B/C gateable sensor integration; packed13 only."""
import argparse,base64,gzip,hashlib,importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='65c1f2ec7deb4bc4740a0477754edd210a6c09bacbefad41e93a3ae9675e6ff6'
OLD='v48_WIP_HELI_C';NEW='v48_WIP_HELI_D'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s,phase='C'):
 old='\n'.join((ROOT/'docs/helicopter/D'/f).read_text()for f in ['motion.js','runtime.js','ui.js']);new='\n'.join((HERE/f).read_text()for f in ['motion.js','runtime.js','ui.js']);assert s.count(old)==1;s=s.replace(old,new,1)
 def render(folder):return (folder/'render.js').read_text().replace('__HELO_RIG_JSON__',json.dumps(json.loads((folder/'rig.json').read_text()),separators=(',',':')))
 old=render(ROOT/'docs/helicopter/D');assert s.count(old)==1;s=s.replace(old,render(HERE),1)
 for stage in ['a','b','c'][:ord(phase)-ord('A')+1]:
  spec=importlib.util.spec_from_file_location('helo_patch_'+stage,HERE/('patch_'+stage+'.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);s=mod.patch(s)
 return s

def build_html(raw,phase='C'):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html),phase).replace(OLD,NEW);z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
 return html.replace(OLD,NEW).replace('V48_WIP_HELI_C','V48_WIP_HELI_D'),main

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);p.add_argument('--phase',choices=['A','B','C'],default='C');a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True);html,main=build_html(a.baseline.read_bytes(),a.phase);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);report={'phase':a.phase,'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'changedPackedAssets':[13],'bytes':len(html.encode()),'addedBytes':len(html.encode())-a.baseline.stat().st_size};a.output.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
