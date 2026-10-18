"""H: paired 120s native fixed-tick state, with/without resize/reflow/render reads."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
SETUP=r'''()=>{const d=__NAVAL_SIM_DIAG__,a=__HELO__;d.setTerrainDiagBypass(true);d.setEmcon(true);d.wip13a3SetManualWeather({hsM:.9,windSpeedMps:5,precipitation01:0});for(const h of a.snapshot().aircraft){a.command(h.id,'LAUNCH');a.command(h.id,'SET_RADAR_MODE',{mode:'PERI'});a.command(h.id,'SET_ALTITUDE',{altitudeM:h.slot?150:300});}d.setShipRudderTest(6);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});return {core:__CORE_SELFTEST_FAILURES__,seed:__NAVAL_SIM_SEED__};}'''
STATE=r'''()=>{const d=__NAVAL_SIM_DIAG__,r=__AEGIS_ACTIVE_SHIP_RUNTIME__,w=__AEGIS_ENGAGEMENT_RUNTIME__;return {operational:d.exportOperationalStateV48Wip11A(),dynamics:d.shipDynamics(),helicopters:__HELO__.snapshot(),aps:__APS153__.snapshot(),isar:__ISAR_F2__.snapshot(),offboard:d.offboardSnapshotC(),observers:d.observerSnapshotC(),weapons:__HARPOON_DIAG_A__.snapshot(),journal:__HARPOON_JOURNAL_F1__.snapshot(),physicalShips:[...w.ships.values()].map(s=>({id:s.entityId,nav:s.navigation,survival:s.survival?.snapshot(),damage:s.flooding?.snapshot(),observerRng:s.combatSystem.observerC?.rf?.rng??null})),mutation:d.operationalImportMutationFingerprintV48Wip11B(),core:__CORE_SELFTEST_FAILURES__};}'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for resize in [False,True]:
   p=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally='DDG_119_LATE_FLIGHT_IIA',enemy='SOVREMENNY_956',width=1400,height=900,errors=errors);setup=p.evaluate(SETUP)
   sp=importlib.util.spec_from_file_location('ui',R/'docs/helicopter/K/verify_ui.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);tid=p.evaluate(m.SETUP);release=p.evaluate('id=>__HARPOON_DIAG_A__.fire(id)',tid);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(30)')
   for i in range(24):
    p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)')
    if resize:
     w,h=[(600,900),(844,390),(390,844),(1920,1080),(900,900),(1400,560),(1400,900)][i%7];p.set_viewport_size({'width':w,'height':h});p.wait_for_timeout(22);p.evaluate('__VIEWPORT_A__.draw();__VIEWPORT_A__.snapshot()')
   state=p.evaluate(STATE);encoded=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();rows.append({'resizes':resize,'fixedSteps':7200,'simulationSeconds':120,'seed':setup['seed'],'release':release,'hashSha256':hashlib.sha256(encoded).hexdigest(),'stateBytes':len(encoded),'core':state['core']});(a.out/('resize-state.json'if resize else'control-state.json')).write_bytes(encoded);p.close()
  b.close()
 checks={'H.truthHashIdentical':rows[0]['hashSha256']==rows[1]['hashSha256'],'H.nativeReleaseBoth':all(r['release']['ok']for r in rows),'H.core':not any(r['core']for r in rows),'H.pageErrors':not errors};out={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'scope':'120s after identical staged launch; full operational/damage/pose/sensor/track/offboard/aircraft/weapon/journal state and mutation fingerprint, all fixed ticks native. Serialized entity/Map callback presentation fields excluded by native operational contracts, not compared as truth.'};(a.out/'invariance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
