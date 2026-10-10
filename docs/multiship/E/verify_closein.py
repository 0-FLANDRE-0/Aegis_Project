"""Native local radar plus naturally measured CMS intent → independent automatic RAM/Phalanx."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
from verify_defense import SETUP
FIXTURE=r'''enemy=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',s=d.exportOperationalStateV48Wip11A(),n=s.fleet.ships[0].ship.navigation,checks={},rows=[];
 Object.assign(s.ship.navigation,{positionWorld:{x:0,y:0},previousPositionWorld:{x:0,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});Object.assign(n,{positionWorld:{x:8000*.0038,y:0},previousPositionWorld:{x:8000*.0038,y:0},heading:Math.PI/2,previousHeadingWorld:Math.PI/2,speed:0,targetSpeedKt:0,vx:0,vy:0});for(const section of Object.values(s.fleet.ships[0].ship.inventory.vls))for(const c of section){c.type='EMPTY';c.essmCount=0;}d.importOperationalStateV48Wip11A(s);d.setTerrainDiagBypass(true);d.setEmcon(true);d.observerCommandC(id,{emcon:false});
 const start=d.weaponsSnapshotD().ships[0].closeIn,initial=start.reduce((a,m)=>a+m.ammo,0);d.weaponFixtureD(id,{action:'track',trackId:71,positionM:{x:10000,y:0,z:20},velocityMps:{x:-300,y:0,z:0}});d.weaponFixtureD(id,{action:'identity',trackId:71,identity:'HOSTILE'});d.runFramesToTicks(60,1,60);checks.cmsAloneCannotFire=d.weaponsSnapshotD().ships[0].closeIn.reduce((a,m)=>a+m.ammo,0)===initial;
 d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:13,altM:20,speedMps:300});d.setEmcon(true);d.observerCommandC(id,{emcon:false});
 for(let i=0;i<34;i++){d.runFramesToTicks(60,1,30);const a=d.defenseSnapshotE().ships[0],w=d.weaponsSnapshotD().ships[0];rows.push({timeS:(i+1)/2,observer:d.observerSnapshotC().ships[1].tracks,banks:w.nativeCiws,closeIn:w.closeIn,ram:w.ram,autoLog:a.closeInLog});}
 const last=rows.at(-1),log=last.autoLog;checks.naturalLocalConfirmation=rows.some(q=>q.banks.some(m=>m.measured.some(f=>f.confirmed&&f.hits>=5)));checks.naturalIntent=rows.some(q=>q.observer.some(t=>t.classification==='ASM'&&t.identity==='ASSUMED_HOSTILE'));checks.actualAutoRelease=log.some(q=>q.mode==='AUTO'&&q.rounds>0);checks.continuousPhalanxBurst=enemy.startsWith('DDG')||log.filter(q=>q.weapon==='PHALANX').length>1;checks.installedOnly=enemy.startsWith('CG')?last.closeIn.every(m=>m.type==='GUN')&&log.every(q=>q.weapon==='PHALANX'):last.closeIn.some(m=>m.type==='RAM');checks.ramReserve=last.closeIn.filter(m=>m.type==='RAM').every(m=>m.ammo>=1);checks.realAmmoConsumed=last.closeIn.reduce((a,m)=>a+m.ammo,0)<initial;checks.effectHasMeasuredTrack=log.every(q=>Number.isInteger(q.trackId)&&q.truthUsed===false);checks.coreFaultZero=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault();return {checks,enemy,rows,pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=load(b,a.html.read_bytes(),ship=own,errors=errors);page.evaluate(SETUP,enemy);q=page.evaluate(FIXTURE,enemy);rows.append(q);page.close();print(json.dumps({'enemy':enemy,'failed':[k for k,v in q['checks'].items()if not v],'autoLog':q['rows'][-1]['autoLog'][-4:]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'closein.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
