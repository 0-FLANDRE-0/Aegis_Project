"""Original vs optimized EW evaluation with controlled dependency outputs.
This is an isolated equivalence/call-count check, not a natural sensor fixture.
Startup selftests are then run in actual browsers on both selected profiles.
"""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from build import decoded,extract,build
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
JS=r'''
const vm=require('node:vm'),fs=require('node:fs');const f=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
function make(src){const s={calls:0,NOISE_JAM:{txPathEfficiency:.8,polarizationCoupling:.9,erpW:1e5},DECEPTION_JAM:{txPathEfficiency:.7,polarizationCoupling:.8,replayErpW:2e5},SLQ32_EA_ALLOC:{minEffectiveShare:.01},Math,
 electronicSettingsF:r=>r.settings,electronicAllocatorF:r=>r.allocation,electronicBandF:tag=>{const t=String(tag??'').toUpperCase();return t.includes('X')||t.includes('I')||t.includes('J')?'IJ':t.includes('S')?'S':t;},
 electronicPodF:r=>{s.calls++;return r.pod;},worldToMeters:v=>v/.0038,terrainAwareRadarLOS:()=>s.los,electronicBeamF:()=>.6,clamp:(x,a,b)=>Math.max(a,Math.min(b,x)),maritimeRfWeatherPathFactorWip13A3:()=>.91};vm.createContext(s);vm.runInContext(src+';this.sample=electronicJammerSampleF',s);return s;}
const a=make(f.baseline),b=make(f.candidate),rows=[];
for(const band of ['S','C','L','X','I/J',undefined])for(const kind of ['NOISE','DECEPTION'])for(const variant of ['on','off','shareBoundary','noPod','losBlocked','damaged']){
 const r={settings:{noiseRequested:variant!=='off',deceptionRequested:variant!=='off'},allocation:{noiseShare:variant==='shareBoundary'?.01:.4,deceptionShare:variant==='shareBoundary'?.01:.6},pod:variant==='noPod'?null:{health:variant==='damaged'?.2:1,point:{x:2,y:3,z:15}}};
 const p={rfBandTag:band,receiveApertureM2:.008,noiseJamBandCoupling:.8,deceptionJamBandCoupling:.7,noiseJamRejectionDb:3,deceptionJamRejectionDb:4},rx={x:1,y:1,z:20};a.los=b.los=variant==='losBlocked'?0:1;
 const before=[a.calls,b.calls],old=a.sample(r,rx,p,kind),next=b.sample(r,rx,p,kind),calls=[a.calls-before[0],b.calls-before[1]];
 rows.push({band:band??null,kind,variant,result:next,calls,exact:JSON.stringify(old)===JSON.stringify(next)});
}
const checks={allOutputsExact:rows.every(q=>q.exact),supportedPodCallsRetained:rows.filter(q=>['X','I/J'].includes(q.band)).every(q=>q.calls[0]===q.calls[1]),unsupportedPodCallsZero:rows.filter(q=>!['X','I/J'].includes(q.band)).every(q=>q.calls[1]===0),baselineAvoidableWorkProven:rows.some(q=>q.calls[0]===1&&q.calls[1]===0)};
process.stdout.write(JSON.stringify({checks,rows,pass:Object.values(checks).every(Boolean)}));
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 b=decoded(a.baseline.read_text());c=decoded(a.candidate.read_text());old=extract(b,'electronicJammerSampleF');candidate=build(b)
 lo=c.index('function electronicJammerSampleF(');hi=c.index('\nfunction electronicJammerAtReceiverF(',lo);new=c[lo:hi]
 assert candidate.replace('v48_WIP_MULTI_SHIP_H4A','v48_WIP_PERF_A')==c
 with tempfile.TemporaryDirectory()as tmp:
  t=Path(tmp);(t/'ew.json').write_text(json.dumps({'baseline':old,'candidate':new}));(t/'verify.cjs').write_text(JS);ew=json.loads(subprocess.check_output(['node',str(t/'verify.cjs'),str(t/'ew.json')]))
 errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   page=load(browser,a.candidate.read_bytes(),ship=ship,errors=errors);v=page.evaluate('({test:__NAVAL_SIM_DIAG__.performanceASelfTest(),core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()})')
   checks={**v['test']['checks'],'coreZero':v['core']==[],'faultsZero':v['runtime']is None and v['presentation']is None};cases.append({'ship':ship,'checks':checks,'pass':all(checks.values())});page.close()
  browser.close()
 checks={**ew['checks'],'profilesSelftestsPass':all(q['pass']for q in cases),'pageErrorsZero':not errors};report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'checks':checks,'ew':ew,'cases':cases,'errors':errors,'pass':all(checks.values())}
 (a.out/'semantics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
