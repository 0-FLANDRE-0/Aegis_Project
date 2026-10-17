"""Pinned HELI_CG_A -> HELI_CG_B; restore facade and move original port leaf."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 for name in ['runtime.js','hangar-render.js']:
  before=(ROOT/'docs/helicopter/I'/name).read_text();assert s.count(before)==1;s=s.replace(before,(HERE/name).read_text()+('\n' if name=='runtime.js' else ''))
 a="if(d.facility.doorStyle==='CG_SHARED_OVERHEAD_FOLD'){heloSyncFoldingDoorI(view,values);return;}";assert s.count(a)==1;s=s.replace(a,"if(d.facility.doorStyle==='CG_PORT_SOURCE_SLIDE'){heloSyncSourceDoorJ(view,values);return;}")
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_CG_A','v48_WIP_HELI_CG_B');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_CG_A','v48_WIP_HELI_CG_B').replace('V48_WIP_HELI_CG_A','V48_WIP_HELI_CG_B'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);d={'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode()),'addedBytes':len(html.encode())-len(a.baseline.read_bytes())};a.output.with_suffix('.manifest.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
