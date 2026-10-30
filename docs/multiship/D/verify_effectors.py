"""Both owner guns; measured local CIWS consent, no CMS-only/automatic release."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[2]/'docs/bunkerhill/K'));from browser_i import launch,load
from verify_weapons import SETUP
GUN=r'''()=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',checks={},n=d.physicalFleetSnapshotB().ships[0].navigation,pos={x:n.positionWorld.x/.0038+4000,y:n.positionWorld.y/.0038,z:2},fresh=()=>{d.weaponFixtureD(id,{action:'track',trackId:44,domain:'SURFACE',positionM:pos});d.weaponFixtureD(id,{action:'identity',trackId:44,identity:'HOSTILE'});};fresh();const before=d.exportOperationalStateV48Wip11A(),release=d.weaponCommandD(id,{observerShipId:id,trackId:44,weapon:'GUN'});let last;
 for(let i=0;i<18;i++){fresh();d.runFramesToTicks(60,1,20);last=d.weaponsSnapshotD().ships[0].guns[0];if(last.shotsFired)break;}
 const after=d.exportOperationalStateV48Wip11A();checks.consentHeld=release.ok&&release.queued;checks.originalGunFiresOnce=last.shotsFired===1&&last.lastFire.projectileId.startsWith(id+':');checks.ownerAmmo=last.magazine.HE_127_SIM===before.fleet.ships[0].ship.inventory.guns[0].magazine.HE_127_SIM-1;checks.playerAmmoUnchanged=JSON.stringify(after.ship.inventory.gunMounts)===JSON.stringify(before.ship.inventory.gunMounts);checks.measuredFCQ=last.lastFire.fireControlTrackQuality.truthUsed===false&&last.lastFire.fireControlTrackQuality.firePermitted;
 return {checks,release,last};}'''
CIWS=r'''enemy=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',checks={},s=d.exportOperationalStateV48Wip11A(),n=s.fleet.ships[0].ship.navigation,weapon=enemy.startsWith('DDG')?'RAM':'PHALANX';
 Object.assign(s.ship.navigation,{positionWorld:{x:0,y:0},previousPositionWorld:{x:0,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});Object.assign(n,{positionWorld:{x:8000*.0038,y:0},previousPositionWorld:{x:8000*.0038,y:0},heading:Math.PI/2,previousHeadingWorld:Math.PI/2,speed:0,targetSpeedKt:0,vx:0,vy:0});d.importOperationalStateV48Wip11A(s);d.setEmcon(true);d.observerCommandC(id,{emcon:false});
 const original=d.weaponsSnapshotD().ships[0].closeIn;d.weaponFixtureD(id,{action:'track',trackId:71,positionM:{x:10000,y:0,z:20},velocityMps:{x:-300,y:0,z:0}});d.weaponFixtureD(id,{action:'identity',trackId:71,identity:'HOSTILE'});const cms=d.weaponCommandD(id,{observerShipId:id,trackId:71,weapon});d.runFramesToTicks(60,1,60);checks.cmsAloneNoRelease=cms.queued&&d.weaponsSnapshotD().ships[0].closeIn.every((m,i)=>m.ammo===original[i].ammo);
 d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:13,altM:20,speedMps:300});d.setEmcon(true);d.observerCommandC(id,{emcon:false});const rows=[];let released=false;
 // The world fixture supplies the physical target. The controller receives only
 // naturally observed tracks/local files; it never gets the fixture target ID.
 for(let i=0;i<30;i++){d.runFramesToTicks(60,1,30);const w=d.weaponsSnapshotD().ships[0],obs=d.observerSnapshotC().ships[1].tracks.filter(t=>t.confirmed&&t.classification==='ASM'),ammo=w.closeIn.reduce((n,m)=>n+m.ammo,0);
  rows.push({timeS:(i+1)/2,tracks:obs.map(t=>({id:t.trackId,identity:t.identity,ageS:t.sensorAgeS})),banks:w.nativeCiws,ammo,ram:w.ram});
  if(ammo<original.reduce((n,m)=>n+m.ammo,0)){released=true;break;}
  if(i<4){checks.noAutomaticRelease=ammo===original.reduce((n,m)=>n+m.ammo,0);continue;}
  for(const t of obs)d.weaponFixtureD(id,{action:'identity',trackId:t.trackId,identity:'HOSTILE'});
  const bank=w.nativeCiws.find(m=>m.type===(weapon==='RAM'?'RAM':'GUN')&&m.measured.some(r=>r.confirmed&&r.audit?.accepted&&r.cmsTrackId!=null));
  const tid=bank?.measured.find(r=>r.confirmed&&r.audit?.accepted&&r.cmsTrackId!=null)?.cmsTrackId;
  if(tid!=null)d.weaponCommandD(id,{observerShipId:id,trackId:tid,weapon,mountId:bank.id});
 }
 checks.naturalLocalConfirmation=rows.some(r=>r.banks.some(m=>m.measured.some(f=>f.confirmed&&f.hits>=5)));checks.manualActualRelease=released;checks.nativeEffector=weapon!=='RAM'||rows.at(-1).ram.some(m=>m.ownerEntityId===id&&m.alive&&m.lifeS>0);checks.installedOnly=enemy.startsWith('CG')?d.weaponsSnapshotD().ships[0].closeIn.every(m=>m.type==='GUN')&&d.weaponCommandD(id,{observerShipId:id,trackId:71,weapon:'RAM'}).ok===false:true;checks.shadowNoExecution=d.weaponsSnapshotD().activeAI===false&&d.weaponsSnapshotD().ships[0].shadow.every(f=>(f.rows??[]).every(r=>!r.executed&&!r.truthUsed));checks.coreFaultZero=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault();return {checks,weapon,rows};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=load(b,a.html.read_bytes(),own,errors=errors);page.evaluate(SETUP,enemy);gun=page.evaluate(GUN);page.close();page=load(b,a.html.read_bytes(),own,errors=errors);page.evaluate(SETUP,enemy);ciws=page.evaluate(CIWS,enemy);page.close();checks={**{'gun.'+k:v for k,v in gun['checks'].items()},**{'ciws.'+k:v for k,v in ciws['checks'].items()}};rows.append({'own':own,'enemy':enemy,'checks':checks,'gun':gun,'ciws':ciws});print(json.dumps({'own':own,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(r['checks'].values())for r in rows)};(a.out/'effectors.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
