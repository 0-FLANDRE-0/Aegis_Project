"""Actual browser function spot checks; zero physical integration steps."""
from pathlib import Path
import json,hashlib,sys
from playwright.sync_api import sync_playwright
T=Path(__file__).resolve().parent;R=T.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
cap=json.loads((T/'active/HANDOFF-capture.json').read_text());kit=json.loads((T/'active/active-contract-results.json').read_text());vm=next(v for v in kit['variants']if v['variant']=='HANDOFF')
helper=(R/'docs/missile/termination/A/live-fixture.js').read_text()+r'''
window.__MEAS_NATIVE_SPOTS__=cases=>{
 const originalRandom=_arhSeekerRandom,originalNormal=_arhSeekerRandn;
 const tickBefore=simStepCounter,rngBefore=SIM_RNG_STATE,profileBefore=JSON.stringify(getSamArhProfile(TERM_LIVE_LAST_MISSILE_A)),rows=[];
 try{
  _arhSeekerRandom=()=>0;_arhSeekerRandn=()=>0;
  for(const c of cases){
   const original=TERM_LIVE_LAST_MISSILE_A,m={isSM6:original.isSM6,isESSM:original.isESSM,_v1Profile:original._v1Profile,_v1ArhState:c.state??'TRACK',seekerAngle:deg(c.boresightAzDeg??0),seekerEl:deg(c.boresightElDeg??0)};
   const cluster=[{azRad:deg(c.targetAzDeg??0),elRad:deg(c.targetElDeg??0),rangeM:26000,dopplerPathRateMps:0,baseReceivedPowerNorm:1,receivedPowerNorm:1,snr:20,trackCoherence:1,decoyLikelihood:0,targetEvidence:1,eccmFrontend:{pass:1,lowDoppler01:0,clutterMask:0}}];
   const raw=JSON.parse(JSON.stringify(_arhMonopulseMeasurement(m,cluster))),decorated=_arhDecorateMeasurementFromCluster({...raw},cluster),R=Array.from(_arhMeasurementCov(decorated));
   rows.push({input:c,raw,decorated,R,TAU});
  }
 }finally{_arhSeekerRandom=originalRandom;_arhSeekerRandn=originalNormal;}
 return {rows,tickBefore,tickAfter:simStepCounter,lifeS:TERM_LIVE_LAST_MISSILE_A.life,rngBefore,rngAfter:SIM_RNG_STATE,profileUnchanged:profileBefore===JSON.stringify(getSamArhProfile(TERM_LIVE_LAST_MISSILE_A)),randomFunctionsRestored:_arhSeekerRandom===originalRandom&&_arhSeekerRandn===originalNormal};
};
'''
errors=[];raw=(R/'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html').read_bytes();assert hashlib.sha256(raw).hexdigest()==cap['htmlSha256']
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 c=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text())[152];c={**c,'maxTimeS':0};p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c)
 result=p.evaluate('cs=>__MEAS_NATIVE_SPOTS__(cs)',[g['input']for g in vm['geometry']]);p.close();b.close()
keys=['azRad','elRad','rangeM','dopplerPathRateMps','azSigmaDeg','elSigmaDeg'];delta=0
for n,v in zip(result['rows'],vm['geometry']):
 assert n['input']==v['input'];assert n['TAU']==2*__import__('math').pi
 for where in ['raw','decorated']:
  for k in keys:delta=max(delta,abs(n[where][k]-v[where][k]))
 for a,b in zip(n['R'],v['covarianceR']):delta=max(delta,abs(a-b))
assert delta<=1e-12 and not errors and result['rngBefore']==result['rngAfter']and result['randomFunctionsRestored']and result['profileUnchanged']and result['tickAfter']==0 and result['lifeS']==0
out={'pass':True,'points':len(result['rows']),'maxNativeVsVmDifference':delta,'errors':errors,**result};(T/'active/live-point-equivalence.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['pass','points','maxNativeVsVmDifference','errors','profileUnchanged','randomFunctionsRestored','tickAfter','lifeS']}))
