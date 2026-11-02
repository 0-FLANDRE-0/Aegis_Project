"""Actual NPC owner local RF path, natural measurements, test-only initial ASM placement."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path[:0]=[str(P),str(R/'docs/missile/fuze-zem/A'),str(R/'docs/helicopter/H')]
from instrument import physical_probe
from browser_tools import instrument
from browser import load_fleet,launch
from playwright.sync_api import sync_playwright
s=importlib.util.spec_from_file_location('slots_npc_c',P.with_name('B')/'regression_runner.py');slots=importlib.util.module_from_spec(s);s.loader.exec_module(slots)
FIXTURE=r'''()=>{
 const npc=physicalShipsB()[0],d=window.__NAVAL_SIM_DIAG__;if(!npc)throw Error('NO_NATIVE_NPC');
 d.setEmcon(true);d.observerCommandC(npc.entityId,{emcon:false});d.defenseCommandE(npc.entityId,{mode:'AUTO'});
 const n=npc.navigation.positionWorld;__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_C_AA_INTERNAL__.begin();
 for(let i=0;i<2;i++){const angle=deg(90+3*i),range=kmToWorld(6+i*.2);spawnEnemyMissile({x:n.x+Math.cos(angle)*range,y:n.y+Math.sin(angle)*range,z:12,heading:angle+Math.PI,vx:mpsToWorldSpeed(-280*Math.cos(angle)),vy:mpsToWorldSpeed(-280*Math.sin(angle)),asmType:'Kh-35U',lastKnownShipX:n.x,lastKnownShipY:n.y});}
 const initial=[...enemyMissiles],start=simStepCounter,before=npc.combatSystem.observerC.tickCount;
 for(let i=0;i<3600;i++){simulateFixedTick(SIM_FIXED_DT);__TRACK_C_AA_INTERNAL__.sample(initial);}
 const trace=__TRACK_C_AA_INTERNAL__.finish(),local=trace.records.filter(q=>q.ownerEntityId===npc.entityId&&q.store.startsWith('C55:')&&q.physicalUid),batches=(trace.candidateTrace?.records??[]).filter(q=>q.ownerEntityId===npc.entityId&&q.event==='C55_NATIVE_COVARIANCE_BATCH');
 const contamination=local.filter(q=>q.knownOwnLaunch===false&&q.after?.ownFireEvidence===true),lost=local.filter(q=>q.knownOwnLaunch===true&&q.after?.ownFireEvidence===false);
 return {checks:{npcLocalRfAccepted:local.length>0,npcNativeCovarianceBatchConsumed:batches.length>0,nonOwnProtectionContaminationZero:contamination.length===0,ownLaunchProtectionLossZero:lost.length===0,npcClockOncePerTick:npc.combatSystem.observerC.tickCount-before===simStepCounter-start,core:__CORE_SELFTEST_FAILURES__.length===0,noTraceDrop:trace.dropped===0&&!trace.faults.length&&trace.candidateTrace.dropped===0},ownerEntityId:npc.entityId,profile:npc.profileId,localRecords:local.length,batches:batches.length,ownLaunchMeasurements:local.filter(q=>q.knownOwnLaunch).length,steps:simStepCounter-start,trace,targets:initial.map(q=>({id:q.id,alive:q.alive,cause:q._deathReason??q._wip113Outcome??null}))};
}'''
def main():
 out=P/'evidence/npc-local';out.mkdir(parents=True,exist_ok=True);build=json.loads((P/'BUILD.json').read_text());body=(R/build['html']).read_bytes();assert hashlib.sha256(body).hexdigest()==build['htmlSha256'];hooked,receipt=physical_probe(body);raw=instrument(hooked,(P/'after_action.js').read_text()+'\nwindow.__TRACK_C_NPC_NATIVE__={run:'+FIXTURE+'};');rows=[];errors=[];at=time.monotonic()
 with slots.heavy_browser_slot(),sync_playwright()as pw:
  for profile in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   browser=launch(pw);page=load_fleet(browser,raw,own='DDG_119_LATE_FLIGHT_IIA',ally=profile,enemy=None,errors=errors);page.set_default_timeout(600000);q=page.evaluate('__TRACK_C_NPC_NATIVE__.run()');dest=out/(profile+'.json.gz');dest.write_bytes(gzip.compress(json.dumps(q,separators=(',',':')).encode(),6,mtime=0));rows.append({k:v for k,v in q.items()if k!='trace'});browser.close();print(json.dumps(rows[-1]),flush=True)
 result={'pass':not errors and all(all(q['checks'].values())for q in rows),'rows':rows,'errors':errors,'htmlSha256':build['htmlSha256'],'physicalProbe':receipt,'fixtureSha256':hashlib.sha256(FIXTURE.encode()).hexdigest(),'wallS':time.monotonic()-at};(out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');return 0 if result['pass']else 1
if __name__=='__main__':raise SystemExit(main())
