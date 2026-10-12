"""Actual registered static envelopes plus convex edge cases, without physics authority changes."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build import decoded
HERE=Path(__file__).resolve().parent
JS=r'''const fs=require('node:fs'),vm=require('node:vm');const o=JSON.parse(fs.readFileSync(process.argv[2])),checks={};
function env(s,kind){const c={};c.window=c;c.globalThis=c;if(kind==='CG'){c.BunkerEnvelopeSource=o.cg.source;c.BunkerEnvelopeStats=o.cg.stats}vm.createContext(c);vm.runInContext(s,c);return {c,L:kind==='CG'?c.BunkerLayout:c.BurkeC52Layout};}
function same(a,b){if(typeof a==='number'||typeof b==='number')return Object.is(a,b);if(a===null||b===null)return a===b;if(typeof a!=='object'||typeof b!=='object')return a===b;const ak=Object.keys(a),bk=Object.keys(b);return JSON.stringify(ak)===JSON.stringify(bk)&&ak.every(k=>same(a[k],b[k]));}
const cases=[];let seed=1831565813;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
for(const kind of ['CG','DDG']){
 const a=env(o[kind].baseline,kind),b=env(o[kind].candidate,kind),bounds=a.L.stats.bounds;
 let exact=true;const rows=[];
 for(let i=0;i<256;i++){const x=i<4?[bounds.stern,bounds.bow,bounds.stern-1e-5,bounds.bow+1e-5][i]:bounds.stern+random()*(bounds.bow-bounds.stern),z=-7+random()*42,y=-12+random()*24,mode=['all','HULL','SUPERSTRUCTURE'][i%3];
  for(const [method,args]of [['sections',[x,mode]],['intervals',[x,z,mode,.16]],['vertical',[x,y,mode,.16]],['contains',[x,y,z,mode,.03]],['halfBeam',[x,z]],['normal',[{x,y,z}]]]){const old=a.L[method](...args),next=b.L[method](...args),ok=same(old,next);rows.push({i,method,exact:ok});exact=exact&&ok}
 }checks[kind+'RegisteredQueriesExact']=exact;cases.push({kind,rows});
}
const hulls=[];
for(const kind of ['CG','DDG']){const a={},b={};vm.createContext(a);vm.createContext(b);vm.runInContext(o[kind].oldConvex+';this.fn=convex;',a);vm.runInContext(o[kind].newConvex+';this.fn=convex;',b);let exact=true;
 for(let i=0;i<192;i++){const p=[];for(let j=0;j<48;j++){const q=[(random()-.5)*80,(random()-.5)*80];p.push(q);if(j%3===0)p.push(q.slice());if(j%7===0)p.push([q[0]+1e-8,q[1]-1e-8])}if(i<5)p.splice(0,p.length,...[[],[[0,0]],[[0,0],[1,1]],[[0,0],[-0,-0],[1,0],[0,1]],[[0,0],[1,1],[2,2]]][i]);const ok=same(a.fn(p),b.fn(p));hulls.push({kind,i,exact:ok});exact=exact&&ok}checks[kind+'ConvexDuplicatesDegenerateAndSignedZeroExact']=exact;
}process.stdout.write(JSON.stringify({checks,cases,hulls,pass:Object.values(checks).every(Boolean)}));'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);bh=a.baseline.read_text();ch=a.html.read_text()
 cg=json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="cg52-envelope" type="application/octet-stream">(.*?)</script>',bh,re.S)[1])))
 data={'cg':cg,'CG':{},'DDG':{}}
 with tempfile.TemporaryDirectory()as tmp:
  t=Path(tmp)
  for name,h in [('baseline',bh),('candidate',ch)]:
   for kind,index in [('CG',13),('DDG',2)]:
    s=decoded(h,index);f=t/(kind+name+'.js');f.write_text(s);functions=json.loads(subprocess.check_output(['node',str(HERE/'function_sources.cjs'),str(f),'convex']));data[kind][('old'if name=='baseline'else 'new')+'Convex']=functions['convex'][0]
    if kind=='CG':s=s[s.index("(function(G){'use strict';\nconst source=G.BunkerEnvelopeSource"):s.index('})(globalThis);')+len('})(globalThis);')]
    data[kind][name]=s
  (t/'data.json').write_text(json.dumps(data));(t/'test.cjs').write_text(JS);q=json.loads(subprocess.check_output(['node',str(t/'test.cjs'),str(t/'data.json')]))
 q.update(sha256=hashlib.sha256(a.html.read_bytes()).hexdigest(),baselineSha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest());(a.out/'envelope.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'registeredQueries':sum(len(c['rows'])for c in q['cases']),'hullCases':len(q['hulls']),'checks':q['checks']}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
