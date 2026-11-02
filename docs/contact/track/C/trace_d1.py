"""Four AFTER_ACTION causal replays. Original D1 signature must remain exact."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path[:0]=[str(P),str(R/'docs/missile/fuze-zem/A')]
from instrument import physical_probe
from playwright.sync_api import sync_playwright
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
EXTRA=r'''
const trackCCauseBatches=[],trackCCauseCandidates=[];
if(typeof trackCC55AssignmentsC==='function'){
 const original=trackCC55AssignmentsC;
 trackCC55AssignmentsC=function(plots,files,cfg){
  const before={step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,plots:plots.map(p=>({knownOwnLaunch:p.knownOwnLaunch,measurement:{rxM:p.measurement.rxM,ryM:p.measurement.ryM,rzM:p.measurement.rzM,rangeM:p.measurement.rangeM,azRad:p.measurement.azRad,elRad:p.measurement.elRad,positionVarianceM2:p.measurement.positionVarianceM2?.slice()}})),files:[...files.values()].map(r=>({id:r.id,ownFireEvidence:!!r.ownFireEvidence,confirmed:r.confirmed,st:{rxM:r.st.rxM,ryM:r.st.ryM,rzM:r.st.rzM,localAgeS:r.st.localAgeS,localHits:r.st.localHits,P:r.st._c55P?.map(q=>q.slice())}}))};
  const result=original.apply(this,arguments);before.result={pairs:result.pairs.map(q=>({i:q.i,id:q.id,nis:q.nis})),heldPlots:[...result.heldPlots],heldTracks:[...result.heldTracks],components:result.components,reason:result.reason??null};if(plots.length)trackCCauseBatches.push(before);return result;
 };
}
const trackCCauseNativeTrace=trackATraceEventA;
trackATraceEventA=function(type,payload,context={}){
 const result=trackCCauseNativeTrace.apply(this,arguments);
 if(type==='CANDIDATE'&&context.kind==='CIWS_LOCAL_RF')trackCCauseCandidates.push({step:simStepCounter,mountId:context.mountId,trackId:context.trackId,knownOwnLaunch:context.knownOwnLaunch,decision:context.decision,reason:context.reason,distanceM:context.distanceM,gate:context.gate,measurement:{rangeM:payload?.rangeM,azRad:payload?.azRad,elRad:payload?.elRad,rxM:payload?.rxM,ryM:payload?.ryM,rzM:payload?.rzM}});
 return result;
};
window.__TRACK_C_D1_CAUSE__={run(c){
 __TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_C_AA_INTERNAL__.begin();
 const original=simulateFixedTick;simulateFixedTick=function(){const r=original.apply(this,arguments);__TRACK_C_AA_INTERNAL__.sample(CD_A.targets);return r;};
 const result=__CIWS_DMG_A__.run(c,true),lineage=__TRACK_C_AA_INTERNAL__.finish();return {result,lineage,costBatches:trackCCauseBatches,legacyCandidates:trackCCauseCandidates};
}};
'''
def enhanced_helper():
 s=(P/'after_action.js').read_text();needle='state.measurements.set(echo,link);';assert s.count(needle)==1;s=s.replace(needle,needle+"emit({...link,store:'RF_FRONTEND',type:'RF_ECHO',decision:'SYNTHESIZED_MEASUREMENT',trackId:null,fields:scalar(echo,['rangeM','azRad','elRad','radialMps'])});",1)
 needle="state.measurements.set(meas,{measurementUid:'LOCAL'+(++state.rfSerial),physicalUid:uid,ownerEntityId:owner,mountId:mount,...stamp()});";assert s.count(needle)==1;s=s.replace(needle,"const link={measurementUid:'LOCAL'+(++state.rfSerial),physicalUid:uid,ownerEntityId:owner,mountId:mount,...stamp()};state.measurements.set(meas,link);emit({...link,store:'C55:'+mount,type:'LOCAL_MEASURED',decision:'RF_DETECTED_BEFORE_ASSOCIATION',trackId:null,fields:scalar(meas,['rangeM','azRad','elRad','rxM','ryM','rzM','positionVarianceM2'])});",1)
 # Keep rejected/HOLD measurements visible independently of an eventual KF update.
 needle="(type==='UPDATE'||type==='ASSIGNMENT')&&context.trackId!=null";assert s.count(needle)==1;s=s.replace(needle,"(type==='UPDATE'||type==='ASSIGNMENT'||(type==='RECEIVED'&&context.kind==='CIWS_LOCAL_RF'))",1)
 s=s.replace('state.records.length<160000','state.records.length<1000000');return s
def main():
 out=P/'evidence/d1-cause';out.mkdir(parents=True,exist_ok=True);helper=enhanced_helper();(out/'enhanced_after_action.js').write_text(helper);(out/'EXTRA.js').write_text(EXTRA);build=json.loads((P/'BUILD.json').read_text());h=module('original_d1_cause_harness',R/'docs/contact/friendly/A/harness.py');slots=module('slots_d1_cause',P.with_name('B')/'regression_runner.py');summary=[];errors=[];at=time.monotonic()
 refs={name:{q['case']['seed']:q for q in[json.loads(l)for l in path.read_text().splitlines()]}for name,path in {'R4':P/'evidence/extra-r4-d1/friendly/ciws-d1.jsonl','C':P/'evidence/regression/d1/friendly/ciws-d1.jsonl'}.items()}
 with slots.heavy_browser_slot(),sync_playwright()as pw:
  for name in ['R4','C']:
   product=R/('Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html'if name=='R4'else build['html']);hooked,receipt=physical_probe(product.read_bytes());temp=out/('_TEST_ONLY_'+name+'.html');temp.write_bytes(hooked)
   raw=h.base.build(file=str(temp),record=False,extra=helper+'\n'+(R/'docs/ciws/dmg/A/diagnostic.js').read_text()+'\n'+EXTRA);server,url=h.serve(raw)
   try:
    for seed in [419015,419026]:
     browser=h.launch(pw);page=h.load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(600000);q=page.evaluate('c=>__TRACK_C_D1_CAUSE__.run(c)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':seed});sig=q['result'].pop('equivalenceSignature');actual=hashlib.sha256(sig.encode()).hexdigest();expected=refs[name][seed]['signatureSha256'];row={'product':name,'seed':seed,'signatureExactToOriginalD1':actual==expected,'expected':expected,'actual':actual,'physicalProbe':receipt,'lineageFaults':q['lineage']['faults'],'lineageDropped':q['lineage']['dropped'],'costBatches':len(q['costBatches']),'legacyCandidates':len(q['legacyCandidates']),'actualProductSha256':hashlib.sha256(product.read_bytes()).hexdigest()};summary.append(row);q['receipt']=row;dest=out/(name+'-'+str(seed)+'.json.gz');assert not dest.exists();dest.write_bytes(gzip.compress(json.dumps(q,separators=(',',':')).encode(),6,mtime=0));browser.close();print(json.dumps(row),flush=True)
   finally:server.shutdown();temp.unlink(missing_ok=True)
 result={'status':'PASS'if not errors and all(q['signatureExactToOriginalD1']and not q['lineageFaults']and not q['lineageDropped']for q in summary)and len(summary)==4 else'FAIL','rows':summary,'errors':errors,'wallS':time.monotonic()-at,'fullStatisticsHelperChanged':False,'originalD1AssertionsAndProductChanged':False};(out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');return 0 if result['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
