"""Physical hull contact and grounding without merchant or observer proxies."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,enemy in [(o,e)for o in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for e in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']]:
   page=load(b,a.html.read_bytes(),ship=own,errors=errors)
   row=page.evaluate('''enemy=>{const d=window.__NAVAL_SIM_DIAG__,checks={};window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;cfg.enemyProfileId=enemy;cfg.targetShip='NONE';window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();
    d.setTerrainDiagBypass(true);const save=d.exportOperationalStateV48Wip11A(),n=save.fleet.ships[0].ship.navigation;Object.assign(n,{heading:Math.PI,speed:4,targetSpeedKt:8,vx:-4*.0038,vy:0});n.positionWorld={x:80*.0038,y:0};n.previousPositionWorld={...n.positionWorld};d.importOperationalStateV48Wip11A(save);d.runFramesToTicks(60,1,1);
    const contact=d.physicalFleetSnapshotB().ships[0],ownAfter=d.exportOperationalStateV48Wip11A().ship;
    checks.contactResolved=contact.events.some(q=>q.kind==='NAVAL_HULL_CONTACT'&&q.closingMps>0)&&Math.hypot(contact.navigation.positionWorld.x-ownAfter.navigation.positionWorld.x,contact.navigation.positionWorld.y-ownAfter.navigation.positionWorld.y)>80*.0038;
    checks.contactCreatesPhysicalDamage=contact.flood.waterM3>=0&&d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.damage.flooding.openings.length>0;
    d.resetEntireSessionV48Wip11A();d.setTerrainDiagBypass(false);const island=window.get3DRenderState().terrainIslands[0];const ground=d.exportOperationalStateV48Wip11A();ground.fleet.ships[0].ship.navigation.positionWorld={x:island.centerXM*.0038,y:island.centerZM*.0038};ground.fleet.ships[0].ship.navigation.previousPositionWorld={...ground.fleet.ships[0].ship.navigation.positionWorld};d.importOperationalStateV48Wip11A(ground);d.runFramesToTicks(60,1,1);const grounded=d.physicalFleetSnapshotB().ships[0];checks.groundingStopsOwner=grounded.events.some(q=>q.kind==='TERRAIN_CONTACT')&&grounded.navigation.speed===0&&grounded.navigation.vx===0&&grounded.navigation.vy===0;
    checks.playerAliasesPinned=d.runtimeOwnershipAuditV48Wip11A().pass;checks.noFault=!window.__WIP125_DIAG__.wip150RuntimeFault();return {checks,contact,grounded,pass:Object.values(checks).every(Boolean)};
   }''',enemy);row.update(own=own,enemy=enemy);rows.append(row);page.close();print(json.dumps({'own':own,'enemy':enemy,'checks':row['checks']}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(r['pass']for r in rows)};(a.out/'contacts.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
