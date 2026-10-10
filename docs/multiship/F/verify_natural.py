"""A real Kh-35U RF emitter and independent foreign radar drive soft-kill AUTO."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'));sys.path.insert(0,str(HERE.parent/'E'))
from browser_i import launch,load
from verify_defense import SETUP
FIXTURE=r'''()=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',s=d.exportOperationalStateV48Wip11A(),n=s.fleet.ships[0].ship.navigation;
 Object.assign(s.ship.navigation,{positionWorld:{x:0,y:0},previousPositionWorld:{x:0,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});Object.assign(n,{positionWorld:{x:8000*.0038,y:0},previousPositionWorld:{x:8000*.0038,y:0},heading:Math.PI/2,previousHeadingWorld:Math.PI/2,speed:0,targetSpeedKt:0,vx:0,vy:0});d.importOperationalStateV48Wip11A(s);d.setTerrainDiagBypass(true);d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:13,altM:20,speedMps:300});d.setEmcon(true);d.defenseCommandE(id,{mode:'HOLD'});d.electronicCommandF(id,{emcon:false,auto:true,noiseRequested:true,deceptionRequested:true});
 const rows=[],checks={};for(let i=0;i<48;i++){d.runFramesToTicks(60,1,30);const e=d.electronicSnapshotF().ships.find(q=>q.entityId===id);rows.push({timeS:(i+1)/2,seeker:d.asmSeekerAudit(),contacts:e.contacts,allocator:e.allocator,logistics:e.logistics,responses:e.responses,observer:d.observerSnapshotC().ships.find(q=>q.ownerEntityId===id||q.entityId===id)});}
 const last=rows.at(-1);checks.realSeekerReceived=rows.some(q=>q.contacts.some(c=>c.emitterClass==='ACTIVE_SEEKER'&&c.source==='PASSIVE_RF_F'));checks.realRadarTrack=rows.some(q=>q.responses.threats.some(t=>t.trackId!=null&&t.source==='TRACK_ESM_FUSED'));checks.actualAutoNulka=last.logistics.nulka.expendedRounds>0;checks.actualAutoSrboc=last.logistics.srboc.expendedRounds>0;checks.actualSharedEa=rows.some(q=>q.allocator.noiseShare>0&&q.allocator.deceptionShare>0&&q.allocator.resourceUsed<=1.00000001);checks.realSeekerNoiseCoupling=rows.some(q=>q.seeker.some(m=>m.seeker?.jOverN>0));checks.realCoherentCapture=rows.some(q=>q.seeker.some(m=>m.seeker?.deceptionReplaySnr>0&&m.seeker?.deceptionPhase!=='OFF'));checks.conservation=last.logistics.nulka.conserved&&last.logistics.srboc.conserved;checks.noTruthInContacts=rows.every(q=>q.contacts.every(c=>!('truthRef'in c)&&!('objectId'in c)&&c.rangeKm===null));checks.ownNoDecoySpend=d.electronicSnapshotF().ships[0].logistics.nulka.expendedRounds===0&&d.electronicSnapshotF().ships[0].logistics.srboc.expendedRounds===0;checks.noFault=!window.__WIP125_DIAG__.wip150RuntimeFault()&&window.__CORE_SELFTEST_FAILURES__.length===0;return {checks,rows,pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=load(b,a.html.read_bytes(),ship=own,errors=errors);page.evaluate(SETUP,enemy);q=page.evaluate(FIXTURE);q.update(own=own,enemy=enemy);rows.append(q);print(json.dumps({'enemy':enemy,'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'natural.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
