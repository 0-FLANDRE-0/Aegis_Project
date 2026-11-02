"""R2 shadow control: frozen R1 natural13 sampler plus passive trace scalars.

No product edit or new RF/NIS/KF/solver call. All new files stay in this folder.
Uses the existing battle.py CLI and one shared heavy-browser lease.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys

D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization')
spec=importlib.util.spec_from_file_location('r1_frozen_battle',R1/'battle.py');battle=importlib.util.module_from_spec(spec);spec.loader.exec_module(battle)
EXTENSION=r'''// R2 TEST ONLY: copy already-produced native proposal trace scalars.
(()=>{const records=[],faults=[];let installed=false,dropped=0,source=null;
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 function fields(o,keys){const q={};for(const k of keys){const v=own(o,k);if(v!==undefined&&(v===null||['number','string','boolean'].includes(typeof v)))q[k]=v;}return q;}
 window.__R2_BATTLE_TRACE__=Object.freeze({install(){if(installed)return;installed=true;const prior=trackBTraceB;source=String(prior);trackBTraceB=function(...args){const result=prior.apply(this,args);try{const e=args[0];if((e?.decision==='COMPONENT'&&e.plotCount>12)||(simStepCounter>=157&&simStepCounter<=160&&['COMPONENT','BATCH'].includes(e?.decision))){if(records.length<1000)records.push({insideNativeTickCounter:simStepCounter,...fields(e,['decision','reason','route','observerShip','tick','timeS','active','mode','stabilizationMode','plotCount','trackCount','certifiedCount','evidenceResolved','lowerBoundCertifiedCount','exactResidualCertifiedCount','residualComponentsSolved','residualRefinementRejected','legacyCount','proposedCount','heldCount'])});else dropped++;}}catch(error){faults.push(String(error?.stack??error));}return result;};},snapshot(){return {schema:'AEGIS_R2_NATIVE_COMPONENT_TRACE_1',records,faults,dropped,source,scope:'Proposal component/BATCH arguments copied after original trace function once; no producer/filter/solver recomputation.'};}});
})();'''
def main():
 original=(R1/'battle.js').read_text();original_hash=hashlib.sha256(original.encode()).hexdigest();assert original_hash=='bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b'
 assert original.count('install();active=false;')==1
 derived=EXTENSION+'\n'+original.replace('install();active=false;','install();window.__R2_BATTLE_TRACE__.install();active=false;')
 assert derived.count('faults,nativeSources:sourceReceipt};')==1
 derived=derived.replace('faults,nativeSources:sourceReceipt};','faults,nativeSources:sourceReceipt,r2Trace:window.__R2_BATTLE_TRACE__.snapshot()};')
 target=D/'sampler.js';target.write_text(derived);battle.HELPER=target;battle.P=P
 receipt={'schema':'AEGIS_R2_BATTLE_SOURCE_1','originalHelper':str(R1/'battle.js'),'originalHelperSha256':original_hash,'extensionSha256':hashlib.sha256(EXTENSION.encode()).hexdigest(),'derivedHelperSha256':hashlib.sha256(derived.encode()).hexdigest(),'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sharedRunnerSha256':hashlib.sha256((R1/'battle.py').read_bytes()).hexdigest(),'noNewNativeCalls':True,'productChanged':False,'expectedValuesChanged':False,'releaseApproved':False};(D/'SAMPLER_SOURCE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
 return battle.main()

if __name__=='__main__':raise SystemExit(main())
