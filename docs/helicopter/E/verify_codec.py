"""Real HELI_C save migration, strict operator settings and transient reset."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'docs/multiship/G'))
from browser_g import launch, load_fleet

LEGACY_FIXTURE = r'''()=>{
 const api=__HELO__,d=__NAVAL_SIM_DIAG__,h=api.snapshot().aircraft[0],h2=api.snapshot().aircraft[1];
 api.command(h.id,'SET_ALTITUDE',{altitudeM:300});api.command(h2.id,'SET_ALTITUDE',{altitudeM:1200});
 api.command(h.id,'WAYPOINT',{x:h.positionM.x+6000,y:h.positionM.y+2000});
 api.command(h.id,'ROUTE_APPEND',{x:h.positionM.x+8000,y:h.positionM.y-2000});
 api.command(h.id,'LAUNCH');d.stepTicks(10000);
 const save=d.exportOperationalStateV48Wip11A();
 return {save,aircraft:api.snapshot().aircraft,valid:d.validateOperationalStateV48Wip11B(save).ok};
}'''

FIXTURE = r'''({legacy,phase})=>{
 const d=__NAVAL_SIM_DIAG__,api=__HELO__,checks={},snap=()=>api.snapshot(),save=()=>d.exportOperationalStateV48Wip11A();
 const fingerprint=()=>JSON.stringify({operational:d.operationalImportMutationFingerprintV48Wip11B(),helicopters:snap(),iff:__HELO_SENSOR_STAGE_A_E__.snapshot()});
 checks.actualCFlightFixture=legacy.valid&&legacy.save.ship.aviation.schema==='AEGIS_HELO_SAVE_C1'&&!legacy.aircraft[0].onboard&&legacy.aircraft[0].altitudeM>50&&legacy.aircraft[0].altitudeM<300;
 const input=JSON.stringify(legacy.save),validation=d.validateOperationalStateV48Wip11B(legacy.save);
 checks.CMigrationValid=validation.ok;checks.validationDoesNotMutateInput=input===JSON.stringify(legacy.save);
 d.importOperationalStateV48Wip11A(legacy.save);const migrated=save().ship.aviation;
 checks.D1Schema=migrated.schema==='AEGIS_HELO_SAVE_D1'&&migrated.launch.schema==='AEGIS_HELO_OPERATIONS_D1';
 checks.defaultIffOnRadarOff=migrated.aircraft.every(h=>h.iffOn===true&&h.radarOn===false);
 checks.allExistingAircraftFieldsPreserved=legacy.save.ship.aviation.aircraft.every((h,i)=>Object.keys(h).every(k=>JSON.stringify(h[k])===JSON.stringify(migrated.aircraft[i][k])));
 checks.inventoryPreserved=JSON.stringify(migrated.inventory)===JSON.stringify(legacy.save.ship.aviation.inventory);
 checks.queueAndDoorsPreserved=Object.keys(legacy.save.ship.aviation.launch).filter(k=>k!=='schema').every(k=>JSON.stringify(migrated.launch[k])===JSON.stringify(legacy.save.ship.aviation.launch[k]));
 const id=snap().aircraft[0].id,id2=snap().aircraft[1].id;
 const pose=()=>JSON.stringify(snap().aircraft.map(h=>({p:h.positionM,v:h.airVelocityMps,g:h.groundVelocityMps,hdg:h.headingRad,route:h.route,state:h.state})));
 let before=pose();
 checks.independentIffToggle=api.command(id,'SET_IFF',{enabled:false}).ok&&snap().aircraft[0].iffOn===false&&snap().aircraft[1].iffOn===true;
 checks.independentRadarToggle=api.command(id,'SET_RADAR',{enabled:true}).ok&&snap().aircraft[0].radarOn===true&&snap().aircraft[1].radarOn===false;
 checks.sensorCommandsDoNotMoveAircraft=before===pose();
 checks.invalidCommandZeroWrites=true;
 for(const action of ['SET_IFF','SET_RADAR'])for(const enabled of [undefined,null,0,1,'ON','false',{},[]]){
  before=fingerprint();if(api.command(id,action,{enabled}).ok||before!==fingerprint())checks.invalidCommandZeroWrites=false;
 }
 checks.invalidCommandExtraKeysZeroWrites=true;for(const action of ['SET_IFF','SET_RADAR']){before=fingerprint();const result=api.command(id,action,{enabled:true,targetId:'TRUTH'});if(result.ok||before!==fingerprint())checks.invalidCommandExtraKeysZeroWrites=false;}
 const active=save();checks.D1SettingsExported=active.ship.aviation.aircraft[0].iffOn===false&&active.ship.aviation.aircraft[0].radarOn===true;
 checks.D1Valid=d.validateOperationalStateV48Wip11B(active).ok;
 d.importOperationalStateV48Wip11A(active);checks.D1RoundTripExact=JSON.stringify(active.ship.aviation)===JSON.stringify(save().ship.aviation);
 checks.invalidSaveRejected=true;checks.invalidSaveZeroWrites=true;const rejected=[];
 const corruptions=[
  ['iffString',a=>a.iffOn='ON'],['iffNull',a=>a.iffOn=null],['iffNumeric',a=>a.iffOn=1],['iffMissing',a=>delete a.iffOn],
  ['radarString',a=>a.radarOn='OFF'],['radarNull',a=>a.radarOn=null],['radarNumeric',a=>a.radarOn=0],['radarMissing',a=>delete a.radarOn],
  ['snapshotTransient',a=>a.sensorsE={iffRepliesReceived:99}],['linkTransient',a=>a.hawklink={connected:true}],
  ['plotTransient',a=>a.lastPlot={targetId:'TRUTH'}],['receiverTransient',a=>a.sensorRng={state:1234}],
  ['nonFiniteFlight',a=>a.positionM.z=NaN],['badRouteAltitude',a=>a.route[0].z=50],
 ];
 for(const [name,mutate]of corruptions){const bad=structuredClone(active);mutate(bad.ship.aviation.aircraft[0]);const valid=d.validateOperationalStateV48Wip11B(bad);before=fingerprint();let threw=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){threw=true;}const zero=before===fingerprint();if(valid.ok||!threw)checks.invalidSaveRejected=false;if(!zero)checks.invalidSaveZeroWrites=false;rejected.push({name,rejected:!valid.ok,threw,zeroWrites:zero});}
 checks.injectedCSettingsRejected=true;
 for(const key of ['iffOn','radarOn']){const bad=structuredClone(legacy.save);bad.ship.aviation.aircraft[0][key]=true;before=fingerprint();let threw=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){threw=true;}if(!threw||before!==fingerprint())checks.injectedCSettingsRejected=false;}
 // Exercise the actual receiver before proving that imports discard its history.
 api.command(id,'SET_IFF',{enabled:true});d.setEmcon(false);d.stepTicks(180);
 const live=snap(),toRestore=save(),transients=__AEGIS_ACTIVE_SHIP_RUNTIME__.aviation.heloSensorsE;
 checks.receiverActuallyRan=live.aircraft[0].sensorsE.iffRepliesReceived>0&&transients instanceof Map&&transients.size>0;
 if(phase==='C'){
  const link=d.offboardSnapshotC().sources.find(s=>s.sourceId==='H1'),now=d.observerFacadeC(__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId).timeS;
  const configured=d.offboardDiagnosticC(__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId,{link:{sourceId:'H1',connected:true,latencyS:10}});
  const queued=d.offboardDiagnosticC(__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:(link?.lastSequence??-1)+1,measuredAtS:now,positionM:{x:130000,y:50000,z:8},covarianceM2:[40000,0,0,0,40000,0,0,0,400],domainEvidence:{surface:.9,air:.02,missile:.01,background:.07}}});
  checks.pendingPortActuallySeeded=configured.ok&&queued.ok&&d.offboardSnapshotC().queued>0;
 }
 const aviationJson=JSON.stringify(toRestore.ship.aviation);
 checks.transientsNotSerialized=!['sensorsE','iffRepliesReceived','lastIffReplyAtS','_truthObject','lastPlot','heloSensorsE'].some(k=>aviationJson.includes('"'+k+'"'));
 d.importOperationalStateV48Wip11A(toRestore);
 checks.receiverTransientReset=__AEGIS_ACTIVE_SHIP_RUNTIME__.aviation.heloSensorsE.size===0&&snap().aircraft.every(h=>h.sensorsE.iffRepliesReceived===0&&h.sensorsE.lastIffReplyAtS===null);
 checks.observerIffHistoryReset=__HELO_SENSOR_STAGE_A_E__.snapshot().ships.every(s=>s.iff===null);
 checks.sensorSettingsSurviveReset=snap().aircraft[0].iffOn===true&&snap().aircraft[0].radarOn===true&&snap().aircraft[1].radarOn===false;
 const postImport=save();checks.noPortHistoryInRoundTrip=JSON.stringify(toRestore.ship.aviation)===JSON.stringify(postImport.ship.aviation);
 if(phase==='C'){
  const port=d.offboardSnapshotC();checks.pendingPortCleared=port.queued===0&&port.sources.filter(s=>['H1','H2'].includes(s.sourceId)).every(s=>s.lastSequence===-1&&s.lastReportS===null);
  d.setEmcon(true);d.stepTicks(60);const resumed=d.offboardSnapshotC().sources.find(s=>s.sourceId==='H1');checks.radarEmconDoesNotBlockHawklink=resumed?.connected===true;
 }
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;
 return {checks,validation,rejected,live,after:snap(),phase};
}'''


def main():
    p = argparse.ArgumentParser()
    p.add_argument('html', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('--baseline', type=Path, default=ROOT / 'archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html')
    p.add_argument('--phase', choices=['A', 'B', 'C'], default='C')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load_fleet(browser, a.baseline.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None, errors=errors)
        legacy = page.evaluate(LEGACY_FIXTURE)
        page.close()
        page = load_fleet(browser, a.html.read_bytes(), own='DDG_119_LATE_FLIGHT_IIA', ally=None, enemy=None, errors=errors)
        result = page.evaluate(FIXTURE, {'legacy': legacy, 'phase': a.phase})
        browser.close()
    report = {'pass': all(result['checks'].values()) and not errors, 'checks': result['checks'], 'phase': a.phase,
              'runtime': result, 'errors': errors, 'htmlSha256': hashlib.sha256(a.html.read_bytes()).hexdigest(),
              'baselineSha256': hashlib.sha256(a.baseline.read_bytes()).hexdigest()}
    (a.out / 'codec.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'pass': report['pass'], 'phase': a.phase, 'checks': len(report['checks']), 'failed': [k for k, v in report['checks'].items() if not v], 'errors': errors}))
    raise SystemExit(0 if report['pass'] else 1)


if __name__ == '__main__':
    main()
