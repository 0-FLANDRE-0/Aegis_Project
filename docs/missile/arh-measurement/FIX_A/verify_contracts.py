"""Actual-browser RF_V2 contract checks for N/A/U/AU. Zero flight integration."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math,sys,time
from playwright.sync_api import sync_playwright

H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument

BUILD=json.loads((H/'build.json').read_text())
FIXTURE=(R/'docs/missile/termination/A/live-fixture.js').read_text()
HELPER=r'''
window.__ARH_FIX_CONTRACT__=(cases,samples)=>{
 const originalRandom=_arhSeekerRandom,originalNormal=_arhSeekerRandn;
 const tickBefore=simStepCounter,rngBefore=SIM_RNG_STATE,profile=JSON.parse(JSON.stringify(getSamArhProfile(TERM_LIVE_LAST_MISSILE_A)));
 const degOut=x=>x*180/Math.PI;
 const make=(c)=>{
  const m={isSM6:TERM_LIVE_LAST_MISSILE_A.isSM6,isESSM:TERM_LIVE_LAST_MISSILE_A.isESSM,_v1Profile:TERM_LIVE_LAST_MISSILE_A._v1Profile,
    _v1ArhState:c.state??'TRACK',seekerAngle:deg(c.boresightAzDeg??0),seekerEl:deg(c.boresightElDeg??0)};
  const specs=c.echoes??[{azDeg:c.targetAzDeg??0,elDeg:c.targetElDeg??0,power:c.power??1,snr:c.snr??20}];
  const cluster=specs.map((e,i)=>({echoId:i+1,azRad:deg(e.azDeg??0),elRad:deg(e.elDeg??0),rangeM:e.rangeM??26000,dopplerPathRateMps:e.dopplerMps??0,
    baseReceivedPowerNorm:e.power??1,receivedPowerNorm:e.power??1,snr:e.snr??20,rangeExtentM:e.rangeExtentM??0,crossExtentM:e.crossExtentM??0,
    verticalExtentM:e.verticalExtentM??0,dopplerSpreadMps:e.dopplerSpreadMps??0,trackCoherence:1,decoyLikelihood:0,targetEvidence:1,
    eccmFrontend:{pass:1,lowDoppler01:0,clutterMask:0}}));
  return {m,cluster};
 };
 const measure=(c,normal)=>{const q=make(c);_arhSeekerRandn=normal;const raw=_arhMonopulseMeasurement(q.m,q.cluster);const decorated=_arhDecorateMeasurementFromCluster({...raw},q.cluster),R=Array.from(_arhMeasurementCov(decorated));return {raw,decorated,R};};
 const geometry=[],noise=[];
 try{
  _arhSeekerRandom=()=>0;
  for(const c of cases.geometry)geometry.push({input:c,...measure(c,()=>0)});
  for(const c of cases.noise){
   const hi=measure(c,()=>1),lo=measure(c,()=>-1),seed=(c.seed??0x71c42a19)>>>0;
   let s=seed,spare=null;const uniform=()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return((s>>>0)+.5)/4294967296;};
   const gaussian=()=>{if(spare!==null){const q=spare;spare=null;return q;}const r=Math.sqrt(-2*Math.log(uniform())),a=2*Math.PI*uniform();spare=r*Math.sin(a);return r*Math.cos(a);};
   let sumAz=0,sumEl=0,sqAz=0,sqEl=0,last=null;
   for(let i=0;i<samples;i++){last=measure(c,gaussian);const az=degOut(last.raw.azRad),el=degOut(last.raw.elRad);sumAz+=az;sumEl+=el;sqAz+=az*az;sqEl+=el*el;}
   const std=(sum,sq)=>Math.sqrt((sq-sum*sum/samples)/(samples-1));
   noise.push({input:c,samples,
    generatedAzSigmaDeg:degOut((hi.raw.azRad-lo.raw.azRad)/2),generatedElSigmaDeg:degOut((hi.raw.elRad-lo.raw.elRad)/2),
    empiricalAzSigmaDeg:std(sumAz,sqAz),empiricalElSigmaDeg:std(sumEl,sqEl),
    reportedAzSigmaDeg:last.raw.azSigmaDeg,reportedElSigmaDeg:last.raw.elSigmaDeg,
    rAzSigmaDeg:degOut(Math.sqrt(last.R[5])),rElSigmaDeg:degOut(Math.sqrt(last.R[10]))});
  }
 }finally{_arhSeekerRandom=originalRandom;_arhSeekerRandn=originalNormal;}
 return {profile,geometry,noise,tickBefore,tickAfter:simStepCounter,lifeS:TERM_LIVE_LAST_MISSILE_A.life,rngBefore,rngAfter:SIM_RNG_STATE,
  restored:_arhSeekerRandom===originalRandom&&_arhSeekerRandn===originalNormal};
};
'''

CASES={
 "geometry":[
  *[{"kind":"POINT","axis":"AZ","targetAzDeg":v} for v in (-3,-.5,-.1,0,.1,.5,3)],
  *[{"kind":"POINT","axis":"EL","targetElDeg":v} for v in (-3,-.5,-.1,0,.1,.5,3)],
  *[{"kind":"BORESIGHT","axis":"AZ","boresightAzDeg":v} for v in (-.5,-.1,.1,.5)],
  *[{"kind":"BORESIGHT","axis":"EL","boresightElDeg":v} for v in (-.5,-.1,.1,.5)],
  {"kind":"BOUNDARY","axis":"AZ","targetAzDeg":4.2},
  {"kind":"BOUNDARY","axis":"AZ","targetAzDeg":-4.2},
  {"kind":"STATE","axis":"AZ","state":"ACQUIRE","targetAzDeg":.5},
  {"kind":"STATE","axis":"AZ","state":"REACQUIRE","targetAzDeg":.5},
 ],
 "noise":[
  {"name":"CLEAN_TRACK","targetAzDeg":0,"targetElDeg":0,"power":1,"snr":20,"seed":1908685337},
  {"name":"OFF_AXIS_TRACK","targetAzDeg":.7,"targetElDeg":-.45,"boresightAzDeg":.2,"boresightElDeg":-.1,"power":.8,"snr":12,"seed":1908685338},
  {"name":"WEAK_TRACK","targetAzDeg":-.4,"targetElDeg":.25,"power":.12,"snr":5,"seed":1908685339},
  {"name":"EXTENDED_TRACK","seed":1908685340,"echoes":[
    {"azDeg":.25,"elDeg":.07,"power":.55,"snr":8,"rangeExtentM":120,"crossExtentM":25,"verticalExtentM":10,"dopplerSpreadMps":20},
    {"azDeg":.35,"elDeg":.13,"power":.45,"snr":6,"rangeExtentM":120,"crossExtentM":25,"verticalExtentM":10,"dopplerSpreadMps":20}]},
 ]}

def rel(a,b): return abs(a-b)/max(1e-12,abs(b))
def assess(row,expect_fixed):
    geom=row['geometry']; noise=row['noise']; tol=1e-9
    point=[];bore=[];bounds=[]
    for g in geom:
        c=g['input']; axis=c['axis']; value=g['raw']['azRad' if axis=='AZ' else 'elRad']*180/math.pi
        if c['kind'] in ('POINT','STATE'): point.append(abs(value-c.get('targetAzDeg',c.get('targetElDeg',0))))
        elif c['kind']=='BORESIGHT': bore.append(abs(value))
        else: bounds.append((value,c.get('targetAzDeg',c.get('targetElDeg',0))))
    sigma=[]; empirical=[]
    for n in noise:
        sigma += [rel(n['generatedAzSigmaDeg'],n['reportedAzSigmaDeg']),rel(n['generatedElSigmaDeg'],n['reportedElSigmaDeg']),rel(n['reportedAzSigmaDeg'],n['rAzSigmaDeg']),rel(n['reportedElSigmaDeg'],n['rElSigmaDeg'])]
        empirical += [rel(n['empiricalAzSigmaDeg'],n['reportedAzSigmaDeg']),rel(n['empiricalElSigmaDeg'],n['reportedElSigmaDeg'])]
    checks={
      'absoluteAngleContract':max(point)<tol and max(bore)<tol,
      'boundaryContract':all(abs(value-math.copysign(min(abs(target),row['profile']['monopulseAngleGateDeg']),target))<tol for value,target in bounds),
      'sigmaRContract':max(sigma)<1e-10,
      'monteCarloWithin3Pct':max(empirical)<.03,
      'stateAndRngInvariant':row['tickBefore']==row['tickAfter']==0 and row['lifeS']==0 and row['rngBefore']==row['rngAfter'] and row['restored'],
    }
    checks['expectedVariantSemantics']=((checks['absoluteAngleContract'] and checks['boundaryContract'])==expect_fixed[0] and checks['sigmaRContract']==expect_fixed[1] and checks['monteCarloWithin3Pct']==expect_fixed[1])
    return {'checks':checks,'maxPointErrorDeg':max(point),'maxBoresightErrorDeg':max(bore),'boundaryOutputsDeg':[x[0] for x in bounds],'maxSigmaRelativeError':max(sigma),'maxEmpiricalRelativeError':max(empirical)}

def main():
    out=[];errors=[];start=time.perf_counter()
    with sync_playwright() as pw:
      browser=launch(pw)
      try:
       for variant,expect in [('N',(False,False)),('A',(True,False)),('U',(False,True)),('AU',(True,True))]:
        info=BUILD['variants'][variant];raw=Path(info['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==info['htmlSha256']
        page=load_fleet(browser,instrument(raw,FIXTURE+'\n'+HELPER),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
        try:
         for weapon in ('SM6','ESSM') if variant=='AU' else ('SM6',):
          case={'weapon':weapon,'rangeKm':30,'altM':5000,'seed':12001,'enabled':False,'samples':False,'maxTimeS':0}
          page.evaluate('c=>__TERM_LIVE_TEST__.run(c)',case)
          row=page.evaluate('x=>__ARH_FIX_CONTRACT__(x.cases,x.samples)',{'cases':CASES,'samples':20000})
          row.update({'variant':variant,'weapon':weapon,'htmlSha256':info['htmlSha256'],'assessment':assess(row,expect)})
          out.append(row);print(json.dumps({'variant':variant,'weapon':weapon,**row['assessment']},ensure_ascii=False),flush=True)
        finally: page.close()
      finally: browser.close()
    result={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_CONTRACTS_1','samplesPerNoiseCase':20000,'statisticalToleranceRelative':.03,'rows':out,'errors':errors,'elapsedS':time.perf_counter()-start}
    (H/'contract-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    ok=not errors and all(r['assessment']['checks']['stateAndRngInvariant'] and r['assessment']['checks']['expectedVariantSemantics'] for r in out) and all(all(v for k,v in r['assessment']['checks'].items() if k!='expectedVariantSemantics') for r in out if r['variant']=='AU')
    print(json.dumps({'pass':ok,'rows':len(out),'errors':errors,'elapsedS':result['elapsedS']}));raise SystemExit(0 if ok else 1)

if __name__=='__main__':main()
