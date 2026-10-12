"""Pinned PERF_E to PERF_F; presentation-only bounded damage job preemption."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
BASE_SHA='0b59340c2db16d33a6fefe810d8bbf27f96ff189ad8a8166139578b50f2051b5'
OLD='v48_WIP_PERF_E';NEW='v48_WIP_PERF_F';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def decoded(html,index=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(index)+r'">(.*?)</script>',html,re.S)[1])).decode()
def build(s):
 s=once(s,'this._damageRefineV11=null;this._damageQuickV11=false;if(this._damageSurfaceSignatureV2!==signature)', 'this._damageRefineV11=null;this._damageQuickV11=false;this._damageOpeningReadyPerfF=false;if(this._damageSurfaceSignatureV2!==signature)','clear presentation publication marker on reset')
 s=once(s,'''      // Finish the visible opening snapshot even while damage grows. Restarting it on
      // every update can starve presentation indefinitely. Only optional detail is preempted.
      if(this._damageJobV3&&!this._damageQuickV11&&this._damageJobSignatureV3!==signature){this._damageJobV3.return();this._damageJobV3=null;}''', '''      // PERF_F: never interrupt an unpublished opening snapshot. Once all of its
      // anchor meshes are live, a newer hit may preempt remaining adjacent/decorative
      // work. Cancellation retains live cuts; each replacement must publish before
      // it can be preempted, so continuous hits cannot starve the opening queue.
      if(this._damageJobV3&&(!this._damageQuickV11||this._damageOpeningReadyPerfF)&&this._damageJobSignatureV3!==signature){this._damageJobV3.return();this._damageJobV3=null;}''','accept latest hits after complete anchor publication; prevent starvation')
 s=once(s,'this._damageQuickV11=quick;this._damageJobSignatureV3=', 'this._damageQuickV11=quick;this._damageOpeningReadyPerfF=false;this._damageJobSignatureV3=','each new job must publish before preemption')
 s=once(s,'if(quick)this._damageOpeningRevisionPerfD=(this._damageOpeningRevisionPerfD||0)+1;', 'if(quick){this._damageOpeningRevisionPerfD=(this._damageOpeningRevisionPerfD||0)+1;this._damageOpeningReadyPerfF=true;}','mark completed anchor publication, not a half-cut mesh')
 s=once(s,"this._bunkerAsset={root,parts,nodes,sourceTriangles,declaredSourceTriangles:R.sourceTriangles};", "this._bunkerAsset={root,parts,nodes,sourceTriangles,declaredSourceTriangles:R.sourceTriangles,ownedTextures:new Set(materials.chain.map?[materials.chain.map]:[])};",'record the new per-presenter CG chain texture ownership')
 s=once(s,"for(const g of geos)g.dispose();for(const m of mats)m.dispose();const owner=v._c12BudgetOwner", "for(const g of geos)g.dispose();for(const t of v._bunkerAsset?.ownedTextures??[])t.dispose();for(const m of mats)m.dispose();const owner=v._c12BudgetOwner",'retiring CG frees its owned texture; DDG shared factory textures remain live')
 return s

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();candidate=build(decoded(html)).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0);m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_PERF_E','V48_WIP_PERF_F');a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate)
 a.output.with_suffix('.manifest.json').write_text(json.dumps({'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedAssets':[13],'patches':PATCHES},indent=2)+'\n');print(json.dumps({'bytes':len(html.encode()),'sha256':hashlib.sha256(html.encode()).hexdigest(),'patches':PATCHES}))
if __name__=='__main__':main()
