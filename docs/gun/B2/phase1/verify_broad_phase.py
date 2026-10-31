from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
from harness import P,build,serve,launch
from fast_http import load_fast_http
old=(P/'development/density-frame-v1/runtime.js').read_text();fn=re.search(r'^function gunB2FuzeIntervals\([\s\S]*?\n}',old,re.M)[0].replace('function gunB2FuzeIntervals(','function gunB2FuzeIntervalsV1(',1)
extra=fn+r'''
window.__B2_BROAD_PHASE_EQ__=()=>{const random=gunB2PrivateStream(0xb20e71),rng=SIM_RNG_STATE,rows=[];let failed=0,inside=0;for(let i=0;i<12000;i++){const near=i<2000,r={x:(random.uniform()-.5)*(near?60:20000),y:(random.uniform()-.5)*(near?60:20000),z:(random.uniform()-.5)*(near?60:20000)},d={x:(random.uniform()-.5)*80,y:(random.uniform()-.5)*80,z:(random.uniform()-.5)*80},a={x:1,y:0,z:0},armed=random.uniform();const before=gunB2FuzeIntervalsV1(r,d,a,armed,25),after=gunB2FuzeIntervals(r,d,a,armed,25),same=before.inSphere===after.inSphere&&before.endInside===after.endInside&&(!before.inSphere||JSON.stringify(before.intervals)===JSON.stringify(after.intervals));if(before.inSphere)inside++;if(!same){failed++;rows.push({r,d,armed,before,after});}}
return{cases:12000,inside,failed,mismatches:rows.slice(0,20),globalRngUnchanged:rng===SIM_RNG_STATE};};
'''
raw=build(record=False,extra=extra);server,url=serve(raw);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fast_http(b,url,errors=errors);q=p.evaluate('__B2_BROAD_PHASE_EQ__()');p.close();b.close()
server.shutdown();q.update(pass_=q['failed']==0 and q['globalRngUnchanged']and not errors,errors=errors,contract='Exact inSphere/endInside; intervals exact when consumed. Caller discards intervals if inSphere=false.');q['pass']=q.pop('pass_');(P/'evidence/broad-phase.json').write_text(json.dumps(q,indent=2)+'\n');print(q);raise SystemExit(not q['pass'])
