"""Chromium: owner release gates, real kernels, inventory and actual damage dispatch."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[2]/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP=r'''enemy=>{const d=window.__NAVAL_SIM_DIAG__;window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:enemy,targetShip:'NONE'});window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();d.setTerrainDiagBypass(true);d.setEmcon(false);d.observerCommandC('SHIP_SCENARIO_ENEMY_A',{emcon:false});}'''
FIXTURE=r'''()=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',checks={},results=[],ownId=d.exportOperationalStateV48Wip11A().shipId;
 const save=d.exportOperationalStateV48Wip11A(),inv=save.fleet.ships[0].ship.inventory;
 ['SM2','SM2ER','SM6','ESSM4'].forEach((w,i)=>Object.assign(inv.vls.fwd[i],{type:w,essmCount:w==='ESSM4'?4:0}));d.importOperationalStateV48Wip11A(save);d.setEmcon(false);d.observerCommandC(id,{emcon:false});
 const n=d.physicalFleetSnapshotB().ships[0].navigation,pos={x:n.positionWorld.x/.0038+8000,y:n.positionWorld.y/.0038+1000,z:600},fresh=()=>{d.weaponFixtureD(id,{action:'track',trackId:11,positionM:pos,velocityMps:{x:-200,y:0,z:0}});},mark=()=>d.weaponFixtureD(id,{action:'identity',trackId:11,identity:'HOSTILE'}),command=(weapon,more={})=>d.weaponCommandD(id,{observerShipId:id,trackId:11,weapon,...more});fresh();
 const pristine=JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.inventory);
 checks.unknownNoRelease=command('SM2').reason==='IDENTITY_WITHHELD'&&JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.inventory)===pristine;
 checks.wrongOwnerRejected=d.weaponCommandD(id,{observerShipId:ownId,trackId:11,weapon:'SM2'}).reason==='OWNER_TRACK_ADDRESS_REQUIRED';
 checks.noTruthCommand=command('SM2',{truthRef:99}).reason==='OWNER_TRACK_ADDRESS_REQUIRED';mark();
 checks.autoReleaseWithheld=command('SM2',{mode:'AUTO'}).reason==='SHADOW_AI_ONLY';checks.semiAutoReleaseWithheld=command('SM2',{mode:'SEMIAUTO'}).reason==='SHADOW_AI_ONLY';
 const finite=q=>JSON.stringify({vls:Object.fromEntries(Object.entries(q.vls).map(([k,v])=>[k,v.map(c=>[c.type,c.essmCount,c.row,c.col,c.destroyed])])),closeIn:q.closeIn.map(m=>[m.id,m.ammo]),harpoon:q.harpoon,gunMounts:q.gunMounts}),ownInventory=finite(d.exportOperationalStateV48Wip11A().ship.inventory);
 for(const weapon of ['SM2','SM2ER','SM6','ESSM']){fresh();mark();const before=d.weaponsSnapshotD().ships[0].sam.length,q=command(weapon);results.push({weapon,q});checks['release.'+weapon]=q.ok&&d.weaponsSnapshotD().ships[0].sam.length===before+1;
  checks['cadence.'+weapon]=!command(weapon).ok;d.runFramesToTicks(60,1,60);}
 const live=d.weaponsSnapshotD().ships[0];checks.correctProfiles=live.sam.map(m=>m.profileId).join(',')==='SM2MR_BLKIIIA_SIM,SM2ER_BLKIV_SIM,SM6_BLKIA_SIM,ESSM_BLK2_SIM';
 checks.finiteRealFlight=live.sam.every(m=>m.lifeS>0&&[m.x,m.y,m.z].every(Number.isFinite));checks.globallyUniqueProjectileIds=new Set(live.sam.map(m=>m.id)).size===4&&live.sam.every(m=>m.id>=1000000&&m.ownerEntityId===id&&m.trackKey==='["SHIP_SCENARIO_ENEMY_A",11]');
 checks.playerInventoryUnchanged=finite(d.exportOperationalStateV48Wip11A().ship.inventory)===ownInventory;
 checks.independentSpg=live.reservations.live.every(row=>row[0]===11);checks.noActiveAI=live.shadow.every(frame=>(frame.rows??[]).every(row=>!row.executed&&!row.truthUsed))&&d.weaponsSnapshotD().activeAI===false;
 const saved=d.exportOperationalStateV48Wip11A();checks.validInventorySave=d.validateOperationalStateV48Wip11A(saved).ok;
 const bads=[q=>q.vls.fwd[0].row=99,q=>q.vls.fwd[0].type='FAKE',q=>q.vls.fwd[0].essmCount=99,q=>q.guns[0].magazine[Object.keys(q.guns[0].magazine)[0]]=-1,q=>q.closeIn[0].ammo=99999,q=>q.harpoon.tubes.push({id:'FAKE',loaded:true})];
 for(let i=0;i<bads.length;i++){const bad=structuredClone(saved);bads[i](bad.fleet.ships[0].ship.inventory);const before=JSON.stringify(d.weaponsSnapshotD());let rejected=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){rejected=true;}checks['invalidInventoryAtomic.'+i]=rejected&&JSON.stringify(d.weaponsSnapshotD())===before;}
 d.importOperationalStateV48Wip11A(saved);checks.inventoryRestoresExactly=JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.inventory)===JSON.stringify(saved.fleet.ships[0].ship.inventory);checks.transientsCleared=d.weaponsSnapshotD().ships[0].sam.length===0&&d.observerSnapshotC().ships[1].tracks.length===0;
 const legacy=structuredClone(saved);delete legacy.fleet.ships[0].ship.inventory;delete legacy.fleet.weaponInventorySchema;checks.explicitLegacyInventoryMigration=d.validateOperationalStateV48Wip11A(legacy).ok;
 const detached=d.weaponsSnapshotD();detached.ships[0].vls.fwd[0].type='FAKE';checks.detachedSnapshot=d.weaponsSnapshotD().ships[0].vls.fwd[0].type!=='FAKE';
 const ownBefore=JSON.stringify(d.exportOperationalStateV48Wip11A().ship),contact=d.weaponFixtureD(id,{action:'contact',weapon:'HARPOON',xM:12,zM:2});checks.physicalContactOnce=contact.ok&&contact.duplicateRejected;checks.receiverDamageIsolated=JSON.stringify(d.exportOperationalStateV48Wip11A().ship)===ownBefore;checks.realFloodOpenings=d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.damage.flooding.openings.some(q=>q.areaM2>0);
 d.runFramesToTicks(60,1,120);checks.hydraulicFeedback=d.physicalFleetSnapshotB().ships[0].clock.tick===saved.fleet.ships[0].clock.tick+120;
 checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultsZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
 return {checks,results,live,contact:{eventId:contact.eventId,terminationReason:contact.terminationReason,duplicateRejected:contact.duplicateRejected},pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright() as pw:
  b=launch(pw)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=load(b,a.html.read_bytes(),ship=own,errors=errors);page.evaluate(SETUP,enemy);q=page.evaluate(FIXTURE);q.update(own=own,enemy=enemy);rows.append(q);page.close();print(json.dumps({'own':own,'enemy':enemy,'failed':[k for k,v in q['checks'].items() if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass'] for q in rows)};(a.out/'weapons.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
