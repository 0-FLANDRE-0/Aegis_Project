"""Actual Chromium product path: real VLS release, native RF/EKF, fixed ticks.

The fixture controls the ship track and target's linear motion. It does not
replace the missile RF frontend, estimator, guidance, dynamics, fuze or damage.
"""
from pathlib import Path
import gzip,hashlib,json,sys,time
from playwright.sync_api import sync_playwright

H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument,fixture

build=json.loads((H/'build.json').read_text())
seeds=[
 {'rngSeed':1831565813,'navigationSeed':2047861954},
 {'rngSeed':305419896,'navigationSeed':2654435769},
 {'rngSeed':2271560481,'navigationSeed':1013904242},
 {'rngSeed':324508639,'navigationSeed':2779096485},
 {'rngSeed':610839776,'navigationSeed':1515870810},
]
path_hook=r'''
const nvPathPriorAutopilotA=applyAccelCommandToAutopilotV1;
applyAccelCommandToAutopilotV1=function(m,cmd,dt){
 const own=samNavB1OwnState(m),pos=own?.posM,pip=cmd?.pip;
 if(cmd&&Number.isFinite(cmd.gammaFDeg)&&pos&&pip&&simStepCounter%6===0){
  const dx=pip.x-pos.x,dy=pip.y-pos.y,dz=pip.z-pos.z;
  (m._nvPathTraceA??=[]).push({lifeS:m.life,policy:cmd.policy,preShapePipLosGammaDeg:Math.atan2(dz,Math.hypot(dx,dy))/deg(1),usedGammaDeg:cmd.gammaFDeg,waypointB4:!!cmd.waypointB4,vFinal:cmd.vFinal,command:{ax:cmd.ax,ay:cmd.ay,az:cmd.az},owner:m._v1LaunchControlAuthority?'LAUNCH':m._wip79KappaActive?'KAPPA':m._v1TerminalActive?'TERMINAL':'GUIDANCE_OR_FALLBACK',phase:m._v1GuidancePhase,source:m._v1GuidanceAuthority,requestedG:m._v1GCommand??null,limitedG:m._v1GAchieved??null,actualG:m.sam6dofActualNormalG??null,positionM:{...pos},pip:{...pip}});
 }
 return nvPathPriorAutopilotA(m,cmd,dt);
};
const nvPathPriorRunA=window.__TERM_LIVE_TEST__.run;
window.__TERM_LIVE_TEST__.run=c=>{const result=nvPathPriorRunA(c),m=TERM_LIVE_LAST_MISSILE_A;return {...result,pathTrace:m?._nvPathTraceA??[],handoffAtS:m?._pitchoverCompleteAt??null};};
'''

def concise(result):
 p=result.get('pathTrace',[])
 return {'success':result.get('success'),'anyEffect':result.get('anyEffect'),'actualOutcome':result.get('actualOutcome'),'reason':result.get('reason'),'closestM':result.get('closestM'),'fuzeMissM':result.get('fuzeMissM'),'flightTimeS':result.get('flightTimeS'),'handoffAtS':result.get('handoffAtS'),'firstTrackS':result.get('firstTrackS'),'finalRfMode':result.get('final',{}).get('rfMode'),'finalRfValid':result.get('final',{}).get('rfValid'),'pathSamples':len(p),'maxAbsPreShapeGammaDeg':max([abs(x['preShapePipLosGammaDeg'])for x in p]or[0]),'maxAbsUsedGammaDeg':max([abs(x['usedGammaDeg'])for x in p]or[0]),'waypointSamples':sum(bool(x.get('waypointB4'))for x in p)}

def run_variant(pw,variant,errors,seed_indices=range(5)):
 info=build['variants'][variant];raw=Path(info['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==info['htmlSha256']
 body=instrument(raw,fixture()+'\n'+path_hook);rows=[]
 for zero_index in seed_indices:
  i=zero_index+1;seed=seeds[zero_index];browser=launch(pw);page=load_fleet(browser,body,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
  try:
   condition={'weapon':'SM6','targetLabel':'Kh-35U','rangeKm':.1,'altM':20000,'targetSpeedMps':0,'crossSpeedMps':0,'enabled':True,'samples':True,**seed}
   result=page.evaluate('c=>__TERM_LIVE_TEST__.run(c)',condition);row={'variant':variant,'seedIndex':i,'condition':condition,'result':result,'summary':concise(result)};rows.append(row);print(variant,i,result.get('reason'),result.get('closestM'),result.get('firstTrackS'),flush=True)
  finally:page.close();browser.close()
 return rows

def main():
 errors=[];rows=[];start=time.perf_counter()
 with sync_playwright() as pw:
  rows+=run_variant(pw,'BASE',errors);rows+=run_variant(pw,'FINAL',errors)
  # Repeat the final product bytes and condition for determinism.
  repeat=run_variant(pw,'FINAL',errors,[0])[0]
 comparison=[]
 for i in range(1,6):
  b=next(x for x in rows if x['variant']=='BASE'and x['seedIndex']==i);f=next(x for x in rows if x['variant']=='FINAL'and x['seedIndex']==i)
  comparison.append({'seedIndex':i,'base':b['summary'],'final':f['summary']})
 first=next(x for x in rows if x['variant']=='FINAL'and x['seedIndex']==1)
 checks={'pageErrors0':not errors,'allFinite':all(all(isinstance(v,(int,float))and v==v and abs(v)!=float('inf')for p in x['result'].get('pathTrace',[])for v in [p['preShapePipLosGammaDeg'],p['usedGammaDeg'],*p['vFinal'].values()])for x in rows),'finalDeterministic':first['result']==repeat['result'],'nativeRfUsed':all(x['result'].get('firstTrackS')is not None for x in rows)}
 summary={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_PRODUCT_RF_1','scope':'Actual Chromium product VLS/fixed-tick/native RF-EKF flight; ship track and linear ASM motion are controlled by the test fixture.','products':{v:{'htmlSha256':build['variants'][v]['htmlSha256']}for v in ['BASE','FINAL']},'comparison':comparison,'checks':checks,'errors':errors,'elapsedS':time.perf_counter()-start};summary['pass']=all(checks.values())
 (H/'product-rf-results.json.gz').write_bytes(gzip.compress(json.dumps({'summary':summary,'rows':rows,'repeat':repeat},separators=(',',':')).encode(),9,mtime=0));(H/'product-rf-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'pass':summary['pass'],'checks':checks,'outcomes':comparison,'elapsedS':summary['elapsedS']},indent=2));raise SystemExit(0 if summary['pass']else 1)

if __name__=='__main__':
 raise SystemExit('Use run_product_one.py for bounded per-shot execution; then aggregate_product_rf.py.')
