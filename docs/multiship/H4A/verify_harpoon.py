"""Fresh departure, real manual Harpoon, natural local sensors and native defense.
Positive cases never inject incoming files, grant defender identity or force hits.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP=r'''enemy=>{
const d=__NAVAL_SIM_DIAG__,w=__AEGIS_ENGAGEMENT_RUNTIME__,h=__HARPOON_DIAG_A__,id='SHIP_SCENARIO_ENEMY_A';
__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;
Object.assign(cfg,{enemyProfileId:enemy,allyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});
__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();
const before={deployment:d.exportOperationalStateV48Wip11A().deployment,defense:d.defenseSnapshotE(),ew:d.electronicSnapshotF()};
const saved=d.exportOperationalStateV48Wip11A(),n=saved.fleet.ships.find(q=>q.entityId===id).ship.navigation;
const nav=(n,x,heading)=>Object.assign(n,{positionWorld:{x:x*.0038,y:0},previousPositionWorld:{x:x*.0038,y:0},heading,previousHeadingWorld:heading,speed:0,targetSpeedKt:0,vx:0,vy:0,rudder:0,targetRudder:0});
nav(saved.ship.navigation,0,0);nav(n,8000,Math.PI/2);d.importOperationalStateV48Wip11A(saved);
d.setTerrainDiagBypass(true);d.setEmcon(false);d.runFramesToTicks(60,1,600);
const t=d.observerSnapshotC().ships[0].tracks.find(q=>q.confirmed&&q.classification==='SURFACE'&&Math.hypot(q.positionM.x-8000,q.positionM.y)<500);
if(!t)throw Error('NO_NATURAL_NAVAL_CONTACT');d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);
const release=h.fire(t.trackId);if(!release.ok)throw Error('HARPOON_RELEASE '+JSON.stringify(release));d.setEmcon(true);
return {before,release,enemy,localTargetId:t.trackId};
}'''
SAMPLE=r'''()=>{
const d=__NAVAL_SIM_DIAG__,h=__HARPOON_DIAG_A__,w=__AEGIS_ENGAGEMENT_RUNTIME__,id='SHIP_SCENARIO_ENEMY_A';
d.runFramesToTicks(60,1,30);
const r=w.ships.get(id),observer=d.observerSnapshotC().ships.find(q=>q.ownerEntityId===id),defense=d.defenseSnapshotE().ships.find(q=>q.entityId===id),weapons=d.weaponsSnapshotD().ships.find(q=>q.entityId===id),ew=d.electronicSnapshotF().ships.find(q=>q.entityId===id);
const m=h.snapshot().missiles.at(-1),own=r.navigation;
return {timeS:d.observerSnapshotC().worldTimeS,observer,defense,weapons,ew,localCues:r.weapons.executionD.context.localDefenseCuesH4A(),ewAudit:r.ew.executionF.context.snapshot(),wrecks:w.world.entities.asmWreckage.map(q=>({id:q.id,sourceAsmId:q.sourceAsmId})),
 diagnosticOnlyFlight:m?{id:m.id,alive:m.alive,phase:m.phase,outcome:m.outcome,positionM:m.positionM,seekerMode:m.seeker?.mode,rangeToDefenderM:Math.hypot(m.positionM.x-own.positionWorld.x/.0038,m.positionM.y-own.positionWorld.y/.0038)}:null,
 diagnosticOnlyTracks:[...r.combatSystem.trackManager.tracks.values()].map(t=>({id:t.trackId,domain:t.domain,classification:t.classification,confidence:t.classificationConfidence,identity:t.identity,authority:t.engagementAuthority,reason:t._a3AuthorityReason,confirmed:t.confirmed,hits:t.sensorHits,age:t.sensorAge,evidence:t.domainEvidenceC,source:t.sensorSource})),
 faults:{core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()}};
}'''

def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for enemy,mode in [('CG_52_LATE_TICONDEROGA','AUTO'),('CG_52_LATE_TICONDEROGA','HOLD'),('DDG_119_LATE_FLIGHT_IIA','AUTO')]:
   page=load(b,a.html.read_bytes(),ship='CG_52_LATE_TICONDEROGA',errors=errors);setup=page.evaluate(SETUP,enemy)
   if mode=='HOLD':page.evaluate("__NAVAL_SIM_DIAG__.defenseCommandE('SHIP_SCENARIO_ENEMY_A',{mode:'HOLD'})")
   rows=[];probes=None
   for i in range(180):
    row=page.evaluate(SAMPLE);rows.append(row)
    if enemy.startswith('CG')and mode=='AUTO'and row['defense']['closeIn']and not probes:
     probes=page.evaluate("()=>{const w=__AEGIS_ENGAGEMENT_RUNTIME__,r=w.ships.get('SHIP_SCENARIO_ENEMY_A');return ['PROTECTED','STALE','UNCONFIRMED','FILE_REPLACED','CAPABILITY_CLONED','EXPIRED','HOLD','EMCON'].map(action=>r.weapons.executionD.context.localDefenseGuardProbeH4A(action));}")
    if not row['diagnosticOnlyFlight']['alive']:break
   last=rows[-1];log=last['defense']['closeInLog'];effects=last['defense']['control']['recentInterceptEvents'];checks={}
   checks['freshDefaultsAutoAndRadarOn']=setup['before']['defense']['ships'][0]['mode']=='AUTO'and setup['before']['ew']['ships'][-1]['settings']['emcon']is False
   checks['realOwnRelease']=setup['release']['ok'];checks['measuredLocalConfirmation']=any(any(m['measured']and any(f['confirmed']for f in m['measured'])for m in row['weapons']['nativeCiws'])for row in rows)
   checks['actualModePolicy']=bool(log)if mode=='AUTO'else not log and sum(last['defense']['autonomy']['totalAutoRounds'].values())==0
   checks['installedWeaponsOnly']=all(q['weapon']=='PHALANX'for q in log)if enemy.startswith('CG')else any(m['type']=='RAM'for m in last['weapons']['closeIn'])
   checks['naturalResolution']=not last['diagnosticOnlyFlight']['alive'];checks['faultsZero']=all(row['faults']['core']==[]and row['faults']['runtime']is None and row['faults']['presentation']is None for row in rows)
   checks['builtInBoundaryTests']=page.evaluate('__NAVAL_SIM_DIAG__.localDefenseSelfTestH4A().pass')
   if enemy.startswith('CG'):
    checks['noArtificialCmsAcquisition']=all(not any(t['confirmed']and t['classification']=='ASM'for t in row['diagnosticOnlyTracks'])for row in rows)
    checks['measuredLocalEsmTiming']=any(any(t['source']=='LOCAL_RF_ESM_FUSED_H4A'and t['rangeKm']is not None and t['ttcS']is not None and t['trackId']is None for t in row['ewAudit']['threats'])for row in rows)
    checks['actualChaffRelease']=last['ew']['logistics']['srboc']['expendedRounds']>0
    checks['noTruthInLocalRelease']=all(q['truthUsed']is False and q['authority']=='LOCAL_SELF_DEFENCE_H4A'and q['trackId']<0 for q in log)
    if mode=='AUTO':
     checks['actualPhalanxBreakup']=any(q['weapon']=='PHALANX'and q['evidence']=='DIRECT_BREAKUP'for q in effects)
     checks['physicalWreck']=any(q['sourceAsmId']==last['diagnosticOnlyFlight']['id']for q in last['wrecks'])
     checks['turretActuallyMoved']=any(abs(q['azRad']-(1 if q['id']==1 else -1)*3.141592653589793/2)>.05 for q in last['weapons']['closeIn'])
     reasons={'PROTECTED':'PROTECTED_LOCAL_CONTACT','STALE':'LOCAL_MEASUREMENT_REQUIRED','UNCONFIRMED':'LOCAL_MEASUREMENT_REQUIRED','FILE_REPLACED':'LOCAL_FILE_CHANGED','CAPABILITY_CLONED':'LOCAL_CAPABILITY_REQUIRED','EXPIRED':'LOCAL_CAPABILITY_REQUIRED','HOLD':'AUTO_OFF','EMCON':'EMCON_BLOCK'}
     checks['lateGuardsAtActualRelease']=bool(probes)and all(q.get('ok')and q['baselineAdmitted']and q['gate']['ok']is False and q['gate']['reason']==reasons[q['action']]and q['actualAmmoDelta']==0 and q['actualProjectileDelta']==0 and q['actualLogDelta']==0 and q['rngUnchanged']for q in probes)
   cases.append({'enemy':enemy,'mode':mode,'setup':setup,'checks':checks,'samples':rows,'guardProbes':probes,'pass':all(checks.values())});print(json.dumps({'enemy':enemy,'mode':mode,'failed':[k for k,v in checks.items()if not v],'chaff':last['ew']['logistics']['srboc']['expendedRounds'],'closeinRounds':sum(q['rounds']for q in log),'effects':[q['evidence']for q in effects]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':cases,'errors':errors,'pass':not errors and all(q['pass']for q in cases)};(a.out/'harpoon-defense.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
