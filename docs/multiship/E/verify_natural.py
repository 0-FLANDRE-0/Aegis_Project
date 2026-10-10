"""Real Harpoon launch and natural defender radar/AUTO; no synthetic incoming tracks or forced hit."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
from verify_defense import SETUP
FIXTURE=r'''({enemy,mode})=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,id='SHIP_SCENARIO_ENEMY_A',checks={},samples=[],saved=d.exportOperationalStateV48Wip11A();
 const own=saved.ship.navigation,n=saved.fleet.ships[0].ship.navigation;Object.assign(own,{positionWorld:{x:0,y:0},previousPositionWorld:{x:0,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});Object.assign(n,{positionWorld:{x:8000*.0038,y:0},previousPositionWorld:{x:8000*.0038,y:0},heading:Math.PI/2,previousHeadingWorld:Math.PI/2,speed:0,targetSpeedKt:0,vx:0,vy:0});d.importOperationalStateV48Wip11A(saved);d.defenseCommandE(id,{mode});d.setTerrainDiagBypass(true);d.setEmcon(false);d.observerCommandC(id,{emcon:false});d.runFramesToTicks(60,8,600);
 const t=d.observerSnapshotC().ships[0].tracks.find(q=>q.confirmed&&q.classification==='SURFACE'&&Math.hypot(q.positionM.x-8000,q.positionM.y)<500);if(!t)throw Error('NO_NATURAL_NAVAL_CONTACT');d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);const release=h.fire(t.trackId);d.setEmcon(true);const ownBda=JSON.stringify(d.wip118ControlSnapshot().recentInterceptEvents);
 for(let i=0;i<52;i++){d.runFramesToTicks(60,8,60);const m=h.snapshot().missiles.at(-1),w=d.weaponsSnapshotD().ships[0],a=d.defenseSnapshotE().ships[0];samples.push({timeS:(i+1),harpoon:m?{id:m.id,alive:m.alive,outcome:m.outcome,impact:m.impact}:null,observer:d.observerSnapshotC().ships[1].tracks,autonomy:a.autonomy,assessments:a.control.assessments,effects:a.control.recentInterceptEvents,closeInLog:a.closeInLog,sam:w.sam,ram:w.ram});if(m&&!m.alive)break;}
 d.runFramesToTicks(60,8,120);const a=d.defenseSnapshotE().ships[0],m=h.snapshot().missiles.at(-1),rounds=Object.values(a.autonomy.totalAutoRounds).reduce((x,y)=>x+y,0),w=d.weaponsSnapshotD().ships[0];
 checks.realLaunch=release.ok;const detected=samples.some(q=>q.observer.some(t=>t.confirmed&&t.classification==='ASM'));
 if(enemy.startsWith('CG')){checks.sensorLimitedApproach=detected===false;checks.noBlindAutoFire=rounds===0&&a.closeInLog.length===0;}
 else {checks.naturalReceiverDetection=detected;checks.modePolicy=mode==='HOLD'?rounds===0:rounds>0||a.closeInLog.some(q=>q.mode==='AUTO');if(mode==='AUTO')checks.nativeFlight=samples.some(q=>q.sam.some(m=>m.ownerEntityId===id&&m.lifeS>0&&Number.isFinite(m.x))||q.ram.some(m=>m.ownerEntityId===id&&m.lifeS>0));}
 checks.physicalResolution=mode==='HOLD'?m?.outcome==='NAVAL_CONTACT'&&m.impact?.accepted:!m?.alive;checks.noTruthInAutonomy=a.truthUsed===false;checks.noHarpoonTelemetry=h.operatorPicture().telemetryAvailable===false&&h.profile().dataLink===false;checks.foreignEffectNotPlayerBda=JSON.stringify(d.wip118ControlSnapshot().recentInterceptEvents)===ownBda;checks.realWreckIfIntercepted=mode==='HOLD'||m.outcome==='NAVAL_CONTACT'||window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.asmWreckage.some(q=>q.sourceAsmId===m.id);
 checks.nativeInstallation=enemy.startsWith('CG')?w.closeIn.every(m=>m.type==='GUN'):w.closeIn.some(m=>m.type==='RAM');checks.coreFaultZero=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault();return {checks,mode,enemy,release,samples,final:{missile:m,defense:a},pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for enemy in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   for mode in ['HOLD','AUTO']:
    page=load(b,a.html.read_bytes(),ship='CG_52_LATE_TICONDEROGA',errors=errors);page.evaluate(SETUP,enemy);q=page.evaluate(FIXTURE,{'enemy':enemy,'mode':mode});rows.append(q);page.close();print(json.dumps({'enemy':enemy,'mode':mode,'failed':[k for k,v in q['checks'].items()if not v],'rounds':q['final']['defense']['autonomy']['totalAutoRounds'],'outcome':q['final']['missile']['outcome']}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'natural.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
