"""Non-game pass-through observer guard; native game methods are not executed."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r2_shadow_observer_source',D/'run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
JS=r'''const vm=require('vm'),fs=require('fs'),ext=fs.readFileSync(0,'utf8');
const receiver={},marker={},event={decision:'COMPONENT',reason:'LARGE_COMPONENT_REFINED_EXACT',route:'OWN_SPY_GLOBAL',tick:158,timeS:158/60,plotCount:13,trackCount:13,certifiedCount:13,lowerBoundCertifiedCount:3,exactResidualCertifiedCount:10,residualComponentsSolved:1,residualRefinementRejected:0,evidenceResolved:false,privateTruthCanary:'MUST_NOT_COPY'};
let calls=0,observedThis=null,observedArgs=null;const ctx={window:{},simStepCounter:158,trackBTraceB:function(...args){calls++;observedThis=this;observedArgs=args;return marker;}};
vm.runInNewContext(ext,ctx);ctx.window.__R2_BATTLE_TRACE__.install();const returned=ctx.trackBTraceB.call(receiver,event,'SENTINEL');const snapshot=ctx.window.__R2_BATTLE_TRACE__.snapshot();
const checks={callsExactlyOnce:calls===1,originalThis:observedThis===receiver,originalArguments:observedArgs[0]===event&&observedArgs[1]==='SENTINEL',originalReturn:returned===marker,oneCopiedRecord:snapshot.records.length===1,componentScalars:snapshot.records[0].certifiedCount===13&&snapshot.records[0].lowerBoundCertifiedCount===3&&snapshot.records[0].exactResidualCertifiedCount===10,unrecognizedTruthNotCopied:!JSON.stringify(snapshot.records).includes('MUST_NOT_COPY'),noFault:snapshot.faults.length===0,noDrop:snapshot.dropped===0};
const error=new Error('NATIVE_SENTINEL');let throwCalls=0;const thrown={window:{},simStepCounter:158,trackBTraceB(){throwCalls++;throw error;}};vm.runInNewContext(ext,thrown);thrown.window.__R2_BATTLE_TRACE__.install();let same=false;try{thrown.trackBTraceB(event);}catch(e){same=e===error;}checks.nativeExceptionPreserved=throwCalls===1&&same;process.stdout.write(JSON.stringify({checks,status:Object.values(checks).every(Boolean)?'PASS':'FAIL',gameNativeCalls:0}));'''
def main():
 result=json.loads(subprocess.check_output(['node','-e',JS],input=runner.EXTENSION.encode()));result['extensionSha256']=hashlib.sha256(runner.EXTENSION.encode()).hexdigest();result['schema']='AEGIS_R2_COMPONENT_OBSERVER_PURE_GUARD_1';(D/'PURE_GUARD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['status']=='PASS'
if __name__=='__main__':main()
