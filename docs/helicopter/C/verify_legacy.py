"""Import actual HELI_A airborne state into HELI_B without resetting its motion."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);old=load_fleet(b,a.baseline.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);save=old.evaluate('''()=>{const d=__NAVAL_SIM_DIAG__,a=__HELO__.snapshot().aircraft[0];__HELO__.command(a.id,'WAYPOINT',{x:3000,y:1000});__HELO__.command(a.id,'LAUNCH');d.stepTicks(9000);return d.exportOperationalStateV48Wip11A();}''');old.close()
  page=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors)
  result=page.evaluate('''save=>{const d=__NAVAL_SIM_DIAG__,checks={},old=save.ship.aviation.aircraft[0];checks.actualAFlight=save.ship.aviation.schema==='AEGIS_HELO_SAVE_A1'&&!old.onboard&&old.positionM.z===50;const valid=d.validateOperationalStateV48Wip11B(save);checks.validMigration=valid.ok;const invalid=structuredClone(save);invalid.ship.aviation.aircraft[0].localM.x=false;const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());checks.invalidLegacyRejected=!d.validateOperationalStateV48Wip11B(invalid).ok;let threw=false;try{d.importOperationalStateV48Wip11A(invalid);}catch(e){threw=true;}checks.invalidLegacyZeroWrites=threw&&before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());d.importOperationalStateV48Wip11A(save);const h=__HELO__.snapshot().aircraft[0];checks.preservedPose=JSON.stringify(old.positionM)===JSON.stringify(h.positionM);checks.preservedVelocity=JSON.stringify(old.airVelocityMps)===JSON.stringify(h.airVelocityMps);checks.preservedHeading=old.headingRad===h.headingRad;checks.routeFromLegacyTarget=h.route.length===1&&JSON.stringify(h.route[0])===JSON.stringify(old.waypointM);checks.newSaveSchema=d.exportOperationalStateV48Wip11A().ship.aviation.schema==='AEGIS_HELO_SAVE_B1';checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,valid,old,h};}''',save);b.close()
 out={'pass':all(result['checks'].values())and not errors,'checks':result['checks'],'result':result,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest()};(a.out/'legacy.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(out['checks']),'failed':[k for k,v in out['checks'].items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
