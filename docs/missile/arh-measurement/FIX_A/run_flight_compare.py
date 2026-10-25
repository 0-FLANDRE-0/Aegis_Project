"""Run the frozen 240 km AIR fixture through N/A/U/AU actual product paths."""
from __future__ import annotations
from pathlib import Path
import gzip,hashlib,json,sys,time
from playwright.sync_api import sync_playwright

H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument

BUILD=json.loads((H/'build.json').read_text())
CASE=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text())[152]
EXPECTED={'weapon':'SM6','rangeKm':240,'altM':5000,'seed':12001,'enabled':False,'samples':False}
if CASE != EXPECTED: raise SystemExit(f'case 152 changed: {CASE!r}')
FIXTURE=(R/'docs/missile/termination/A/live-fixture.js').read_text()
OBSERVER=(R/'docs/missile/sm6-rf/A/kit/observer.js').read_text()
EXTRA=r'''
const arhFixOriginalMonopulse=_arhMonopulseMeasurement;
_arhMonopulseMeasurement=function(m,cluster){
 const out=arhFixOriginalMonopulse(m,cluster);
 if(m===TERM_LIVE_LAST_MISSILE_A&&out)sm6DiagMark(m,'monopulse',{measurement:{rangeM:out.rangeM,azRad:out.azRad,elRad:out.elRad,dopplerPathRateMps:out.dopplerPathRateMps,rangeSigmaM:out.rangeSigmaM,azSigmaDeg:out.azSigmaDeg,elSigmaDeg:out.elSigmaDeg,dopplerSigmaMps:out.dopplerSigmaMps,snr:out.snr,pd:out.pd},seeker:{az:m.seekerAngle,el:m.seekerEl,heading:m.heading,pitch:m.pitch},clusterSize:cluster?.length??0});
 return out;
};
const arhFixOriginalCov=_arhMeasurementCov;
_arhMeasurementCov=function(meas){
 const out=arhFixOriginalCov(meas),m=TERM_LIVE_LAST_MISSILE_A;
 if(m&&meas)sm6DiagMark(m,'measurementCov',{R:Array.from(out),azSigmaDeg:meas.azSigmaDeg,elSigmaDeg:meas.elSigmaDeg,eccmCovInflation:meas.eccmCovInflation??1});
 return out;
};
'''

def clean(v):
    if isinstance(v,float):
        if v != v or v in (float('inf'),float('-inf')): return None
        return v
    if isinstance(v,list): return [clean(x) for x in v]
    if isinstance(v,dict): return {k:clean(x) for k,x in v.items()}
    return v

def run_one(browser,variant,run_id,errors):
    info=BUILD['variants'][variant];path=Path(info['file']);raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=info['htmlSha256']: raise RuntimeError('HTML hash mismatch '+variant)
    helper=FIXTURE+'\n'+OBSERVER+'\n'+EXTRA
    page=load_fleet(browser,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
    try:
        page.evaluate("__SM6_RF_CAUSAL_DIAG__.configure('NATIVE')")
        result=page.evaluate('c=>__TERM_LIVE_TEST__.run(c)',CASE)
        rows=page.evaluate('__SM6_RF_CAUSAL_DIAG__.read()')
        metadata=page.evaluate('__SM6_RF_CAUSAL_DIAG__.metadata()')
    finally: page.close()
    deterministic=clean({'condition':CASE,'htmlSha256':info['htmlSha256'],'metadata':metadata,'result':result,'rows':rows})
    deterministic_bytes=json.dumps(deterministic,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
    payload=clean({'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_FLIGHT_TRACE_1','variant':variant,'runId':run_id,'condition':CASE,
      'htmlSha256':info['htmlSha256'],'observerSha256':hashlib.sha256((OBSERVER+'\n'+EXTRA).encode()).hexdigest(),
      'metadata':metadata,'result':result,'rows':rows})
    out=H/'flight-traces';out.mkdir(exist_ok=True)
    target=out/f'{variant}-{run_id}.json.gz';target.write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode(),9,mtime=0))
    return {'variant':variant,'runId':run_id,'htmlSha256':info['htmlSha256'],'success':result.get('success'),'reason':result.get('reason'),
      'closestM':result.get('closestM'),'flightTimeS':result.get('flightTimeS'),'finalSpeedMps':result.get('final',{}).get('speedMps'),
      'proxDetonated':result.get('proxDetonated'),'rows':len(rows),'trace':str(target.relative_to(H)),'traceSha256':hashlib.sha256(target.read_bytes()).hexdigest(),
      'deterministicContentSha256':hashlib.sha256(deterministic_bytes).hexdigest(),'entireResult':result}

def main():
    out=[];errors=[];start=time.perf_counter()
    with sync_playwright() as pw:
      browser=launch(pw)
      try:
       for variant,run_id in [('N','primary'),('A','primary'),('U','primary'),('AU','primary'),('AU','repeat')]:
        q=run_one(browser,variant,run_id,errors);out.append(q);print(json.dumps({k:q[k] for k in ('variant','runId','success','reason','closestM','flightTimeS','finalSpeedMps','rows')},ensure_ascii=False),flush=True)
      finally: browser.close()
    ref=json.loads((R/'docs/missile/launch-handoff/A/final-evidence/release-HANDOFF/normals.json').read_text())['results'][152]
    n=next(x for x in out if x['variant']=='N');a=[x for x in out if x['variant']=='AU']
    checks={'nEntireResultMatchesFrozenHandoff':n['entireResult']==ref,'auRepeatEntireResultExact':a[0]['entireResult']==a[1]['entireResult'],
      'auRepeatTraceContentExact':a[0]['deterministicContentSha256']==a[1]['deterministicContentSha256'],'browserErrorsZero':not errors}
    result={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_FLIGHT_COMPARE_1','condition':CASE,'rows':out,'checks':checks,'errors':errors,'elapsedS':time.perf_counter()-start}
    (H/'flight-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'checks':checks,'elapsedS':result['elapsedS'],'errors':errors}));raise SystemExit(0 if all(checks.values()) else 1)

if __name__=='__main__':main()
