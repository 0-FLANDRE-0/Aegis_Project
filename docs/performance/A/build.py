"""Pinned H4A → PERF_A. Only immutable lookup, EW ordering and paint lifetime."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a'
OLD='v48_WIP_MULTI_SHIP_H4A';NEW='v48_WIP_PERF_A';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 original=s
 f=extract(original,'shipSystemDamageB')
 f=once(f,"[...new Set(r.geometry.boxes.filter(b=>b.system===system).map(b=>b.name))]","systemModuleNamesPerfA(r.geometry.boxes,system)",'static module name index; live damage reads')
 s=once(s,extract(original,'shipSystemDamageB'),(HERE/'cache.js').read_text()+'\n'+f,'transient caches and isolated selftest')
 f=extract(original,'electronicJammerSampleF')
 old="  const pod=electronicPodF(r,rx);if(!pod)return null;\n  const band=electronicBandF(p.rfBandTag),match=band==='IJ'?1:0;if(!match)return null;"
 new="  const band=electronicBandF(p.rfBandTag),match=band==='IJ'?1:0;if(!match)return null;\n  const pod=electronicPodF(r,rx);if(!pod)return null;"
 f=once(f,old,new,'unsupported EW band before pod geometry')
 s=once(s,extract(original,'electronicJammerSampleF'),f,'EW result and supported-band calculation retained')
 f=extract(original,'buildKh32VisualMesh')
 start=f.index("      const canvas=document.createElement('canvas');")
 end=f.index('\n      const bodyMat=paint.clone();',start)
 paint=f[start:end]
 f=once(f,paint,"      const paintLease=acquireKh32PaintPerfA(this,L,p,()=>{\n"+paint+"\n      return tex;});\n      const tex=paintLease.texture;",'identical canvas paint shared per view/input')
 f=once(f,"body.geometry.addEventListener('dispose',()=>tex.dispose());","const releasePaint=()=>{body.geometry.removeEventListener('dispose',releasePaint);paintLease.release();};body.geometry.addEventListener('dispose',releasePaint);",'idempotent geometry lease release; last texture disposal')
 s=once(s,extract(original,'buildKh32VisualMesh'),f,'Kh32 geometry and per-missile materials retained')
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const perfA=performanceASelfTest();if(!perfA.pass)failures.push('PERF_A '+JSON.stringify(perfA.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'startup cache transition selftest')
 s=once(s,'localDefenseSelfTestH4A:localDefenseSelfTestH4A,','performanceASelfTest:performanceASelfTest,localDefenseSelfTestH4A:localDefenseSelfTestH4A,','detached diagnostic selftest')
 return s
def decoded(html):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();candidate=build(decoded(html)).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):]
 html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_H4A','V48_WIP_PERF_A')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate)
 manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES}
 a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()
