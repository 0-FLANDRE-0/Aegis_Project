"""Isolated native forecast/planning equivalence, then real-profile browser selftests.
Dependency controls below are not sensor acquisition or natural combat evidence.
"""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from build import decoded,BASE_SHA
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
NAMES=['createShipBodyFrameV1','shipFrameForInputsPerfB','performanceBSelfTest','wip118FutureThreat','wip118NezForecastPerfB','wip118NezCandidatesPerfB','wip118NezPoint','wip118FindNezPlan','wip118ReservationAtNezPoint','hardKillKinematicInterceptEstimate','wip118TrackStateSI']
JS=r'''
const vm=require('node:vm'),fs=require('node:fs');const f=JSON.parse(fs.readFileSync(process.argv[2]));
function make(src,index){const p={heading:.3,vx:.003,vy:-.001};
 const s={Math,Map,WeakMap,Object,Number,TypeError,Float64Array,shipNav:p,OWN_ALT_M:0,navX:7,navY:-4,health:1,scores:0,windows:0,
 aircraft:{x:()=>s.navX,y:()=>s.navY},worldToMeters:v=>v/.0038,metersToWorld:v=>v*.0038,mpsToWorldSpeed:v=>v*.0038,worldSpeedToMps:v=>v/.0038,worldToKm:v=>v/3.8,dist:(a,b,c,d)=>Math.hypot(c-a,d-b),
 closingSpeedKmh3:(ax,ay,svx,svy,sz,svz,x,y,vx,vy,z,vz)=>-( (x-ax)*(vx-svx)+(y-ay)*(vy-svy)+(z-sz)*.0038*(vz-svz)*.0038)/Math.max(1e-9,Math.hypot(x-ax,y-ay,(z-sz)*.0038))*3.6/.0038,
 clamp:(v,a,b)=>Math.max(a,Math.min(b,v)),wip118TrackAcceleration:()=>({x:0,y:0,z:0}),
 wip14a14WeaponProfile:w=>w==='INVALID'?null:{effectiveRangeKmGameplay:w==='SM2'?180:40,planningSpeedMps:w==='SM2'?1100:900,publicTargetEngagementAltitudeReferenceM:25000},
 wip119WeaponDescriptor:w=>({requiresIlluminator:w!=='ESSM'}),wip118SamAuthorityAt:(w,h)=>({availableG:h>18000?1:25}),wip118TargetEvasiveG:th=>th.tag==='ASM-SS'?8:4,
 WIP118_KILL_ASSESSMENT_POLICY:{reengageSafetyS:2,nezMaxLookaheadS:80,nezScanStepS:1,interceptorGAdvantage:1.2},
 SPG62_RESERVATION_POLICY:{stabilizationLeadS:.5,minWindowS:1,cpaReleaseMarginS:.5},SPG62_RESERVATION_STATE:new Map(),spg62ReservationNowS:()=>1,
 spg62ReservationCandidateIlluminators:tr=>{s.scores++;return s.health?[{ill:{id:0},score:.8},{ill:{id:1},score:.6}]:[];},
 spg62ReservationWindowFree:(id,w,target,rows)=>{s.windows++;return !rows.some(r=>r.illId===id&&r.targetId!==target&&w.startT<r.endT&&r.startT<w.endT);}};
 vm.createContext(s);let code='';for(const n of ['wip118TrackStateSI','hardKillKinematicInterceptEstimate','wip118FutureThreat','wip118NezForecastPerfB','wip118NezCandidatesPerfB','wip118NezPoint','wip118ReservationAtNezPoint','wip118FindNezPlan'])if(src[n])code+='\n'+src[n][Math.min(index,src[n].length-1)];
 vm.runInContext(code+';this.plan=wip118FindNezPlan;this.future=wip118FutureThreat;'+(src.wip118NezForecastPerfB?'this.forecast=wip118NezForecastPerfB;this.candidates=wip118NezCandidatesPerfB;this.reserve=wip118ReservationAtNezPoint;':''),s);return s;}
const rows=[],checks={};
for(let scope=0;scope<2;scope++){
 const a=make(f.baseline,scope),b=make(f.candidate,scope);
 for(let i=0;i<48;i++){
  const tr={_kfX:new Float64Array([12000+i*180,900-i*30,300+i*410,-270,3,-1]),identity:'HOSTILE',classification:'ASM',metadata:{retained:true}},th={id:i+1,tag:i%2?'ASM-SK':'ASM-SS',tr},assessment={closureTgoS:18+i,accel:{x:i%3*.05,y:-.03,z:i%4*.08}},ca={provisionalReservations:[]},cb={provisionalReservations:[]};
  a.health=b.health=i%4?1:0;
  if(i%3===0){const r={illId:0,targetId:999,startT:0,endT:200};ca.provisionalReservations.push(r);cb.provisionalReservations.push({...r});}
  const old=[],next=[];for(const w of ['SM2','ESSM','SM2','INVALID','RAM','PHALANX']){old.push(a.plan(th,w,assessment,ca));next.push(b.plan(th,w,assessment,cb));}
  rows.push({scope,case:i,exact:JSON.stringify(old)===JSON.stringify(next),reservationsExact:JSON.stringify(ca.provisionalReservations)===JSON.stringify(cb.provisionalReservations),results:next});
 }
 checks['plansExactScope'+scope]=rows.filter(r=>r.scope===scope).every(r=>r.exact&&r.reservationsExact);
 const th={id:500,tag:'ASM-SS',tr:{_kfX:new Float64Array([14000,2000,6000,-250,0,0]),identity:'FRIEND',extra:'preserved'}},acc={x:0,y:0,z:0},ctx={provisionalReservations:[]};b.health=1;
 const full=b.future(th,3,acc),old=a.future(th,3,acc);checks['defaultFutureContractScope'+scope]=JSON.stringify(full)===JSON.stringify(old)&&full.tr.extra==='preserved';
 const first=b.forecast(th,3,acc,ctx),same=b.forecast(th,3,acc,ctx),other=b.forecast(th,4,acc,ctx);
 checks['forecastReuseScope'+scope]=first===same&&first!==other;
 const scores=b.scores,one=b.candidates(first.tr,ctx),two=b.candidates(same.tr,ctx);checks['sameGeometryReuseScope'+scope]=one===two&&b.scores===scores+1;
 const beforeWindows=b.windows,pt={launchDelayS:3,interceptS:8,futureThreat:first};b.reserve(th,'SM2',pt,ctx);ctx.provisionalReservations.push({illId:0,targetId:999,startT:0,endT:999},{illId:1,targetId:999,startT:0,endT:999});
 const blocked=b.reserve(th,'SM2',pt,ctx);checks['availabilityStillCurrentScope'+scope]=!blocked.ok&&b.windows>beforeWindows;
 b.health=0;b.navX+=.1;const fresh={provisionalReservations:[]},moved=b.forecast(th,3,acc,fresh);
 checks['newBuildReadsPoseAndDamageScope'+scope]=moved!==first&&moved.dKm!==first.dKm&&b.candidates(moved.tr,fresh).length===0;
 th.tr._kfX[0]+=100;const observed=b.forecast(th,3,acc,{provisionalReservations:[]});checks['newMeasurementScope'+scope]=observed.tr.x!==moved.tr.x;
}
const frame={};vm.createContext(frame);vm.runInContext('const shipFrameCachePerfB=new WeakMap();'+f.candidate.createShipBodyFrameV1[0]+f.candidate.shipFrameForInputsPerfB[0]+f.candidate.performanceBSelfTest[0]+';this.result=performanceBSelfTest();',frame);
Object.assign(checks,frame.result.checks);process.stdout.write(JSON.stringify({checks,rows,pass:Object.values(checks).every(Boolean)}));
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()==BASE_SHA
 with tempfile.TemporaryDirectory()as tmp:
  t=Path(tmp);sources={}
  for name,path in [('baseline',a.baseline),('candidate',a.candidate)]:
   f=t/(name+'.js');f.write_text(decoded(path.read_text()));sources[name]=json.loads(subprocess.check_output(['node',str(HERE/'function_sources.cjs'),str(f),*NAMES]))
  (t/'functions.json').write_text(json.dumps(sources));(t/'verify.cjs').write_text(JS);isolated=json.loads(subprocess.check_output(['node',str(t/'verify.cjs'),str(t/'functions.json')]))
 errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   page=load(browser,a.candidate.read_bytes(),ship=ship,errors=errors);v=page.evaluate('({test:__NAVAL_SIM_DIAG__.performanceBSelfTest(),prior:__NAVAL_SIM_DIAG__.performanceASelfTest(),core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()})')
   checks={**v['test']['checks'],'priorCacheSelftest':v['prior']['pass'],'coreZero':v['core']==[],'faultsZero':v['runtime']is None and v['presentation']is None};cases.append({'ship':ship,'checks':checks,'pass':all(checks.values())});page.close()
  browser.close()
 checks={**isolated['checks'],'profilesSelftestsPass':all(q['pass']for q in cases),'pageErrorsZero':not errors};report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'checks':checks,'isolated':isolated,'cases':cases,'errors':errors,'pass':all(checks.values())}
 (a.out/'semantics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
