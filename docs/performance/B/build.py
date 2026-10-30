"""Pinned PERF_A → PERF_B. Exact pose frames and build-local planner forecasts."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='13a9de64d918efd053ead648cb312a691688691ccbfa72fe50fefd72054ae6ad'
OLD='v48_WIP_PERF_A';NEW='v48_WIP_PERF_B';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key,index=0):
 q=json.loads((HERE/'patch-index.json').read_text())[key][index];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 original=s
 replacements=[]
 def replace_function(key,index,new,label):
  extract(original,key,index);q=json.loads((HERE/'patch-index.json').read_text())[key][index]
  replacements.append((q['start'],q['end'],new));PATCHES.append(label)
 f=extract(original,'shipBodyFrameB')
 f=once(f,'createShipBodyFrameV1(r.survival.snapshot(),','shipFrameForInputsPerfB(r,r.survival.snapshot(),','foreign current-pose frame reuse')
 replace_function('shipBodyFrameB',0,(HERE/'frame-cache.js').read_text()+'\n'+f,'owner-separated immutable frame cache')
 f=extract(original,'shipGameFrameV1',2)
 f=once(f,'createShipBodyFrameV1(floodAttitudePreviewV1.snapshot(),','shipFrameForInputsPerfB(ACTIVE_SHIP_RUNTIME,floodAttitudePreviewV1.snapshot(),','active current-pose frame reuse')
 replace_function('shipGameFrameV1',2,f,'active frame wrapper; live reads retained')
 # Two canonical planners live in distinct lexical scopes; provenance pins each.
 for index in [0,1]:
  f=extract(original,'wip118FutureThreat',index)
  f=once(f,'(th,delayS,accel){','(th,delayS,accel,leanPerfB=false){','private lean forecast option')
  f=once(f,'const ft={...tr,x:wx,y:wy,z,vx:wvx,vy:wvy,vz};','const ft=leanPerfB?{x:wx,y:wy,z,vx:wvx,vy:wvy,vz}:{...tr,x:wx,y:wy,z,vx:wvx,vy:wvy,vz};','skip unused track metadata copy in NEZ scans')
  replace_function('wip118FutureThreat',index,f,'forecast arithmetic retained scope '+str(index))
  f=extract(original,'wip118NezPoint',index)
  f=once(f,'(th,weapon,launchDelayS,accel){','(th,weapon,launchDelayS,accel,ctxPerfB=null){','planner-only context')
  f=once(f,'future=wip118FutureThreat(th,launchDelayS,accel);','future=ctxPerfB?wip118NezForecastPerfB(th,launchDelayS,accel,ctxPerfB):wip118FutureThreat(th,launchDelayS,accel);','same threat/delay forecast reuse within build')
  replace_function('wip118NezPoint',index,(HERE/'planner-cache.js').read_text()+'\n'+f,'private derived forecast/candidate maps scope '+str(index))
  f=extract(original,'wip118ReservationAtNezPoint',index)
  f=once(f,'spg62ReservationCandidateIlluminators(pt.futureThreat.tr)','wip118NezCandidatesPerfB(pt.futureThreat.tr,ctx)','SPG scores reuse; current window checks retained')
  replace_function('wip118ReservationAtNezPoint',index,f,'same-build geometric opportunities scope '+str(index))
  f=extract(original,'wip118FindNezPlan',index)
  f=once(f,'wip118NezPoint(th,weapon,d,accel)','wip118NezPoint(th,weapon,d,accel,ctx)','shared only by this synchronous build')
  replace_function('wip118FindNezPlan',index,f,'native full NEZ scan retained scope '+str(index))
 for start,end,new in sorted(replacements,reverse=True):s=s[:start]+new+s[end:]
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const perfB=performanceBSelfTest();if(!perfB.pass)failures.push('PERF_B '+JSON.stringify(perfB.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'isolated frame-cache selftest')
 s=once(s,'performanceASelfTest:performanceASelfTest,','performanceBSelfTest:performanceBSelfTest,performanceASelfTest:performanceASelfTest,','detached selftest export')
 return s
def decoded(html):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();candidate=build(decoded(html)).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
 row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):]
 html=html.replace(OLD,NEW).replace('V48_WIP_PERF_A','V48_WIP_PERF_B')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate)
 manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES}
 a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()
