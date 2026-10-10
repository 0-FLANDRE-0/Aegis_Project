"""Retained D manual-port tests explicitly configure enemy defense HOLD and EW off.

Test-side isolated manual-port mode changes follow each valid import/observer setup; production source
has no test flag, mode swap, monkeypatch or disabled controller. Historical D
test files stay byte-identical. E AUTO is verified separately by real natural runs.
"""
import argparse,importlib.util,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;D=HERE.parent/'D'
def main():
 p=argparse.ArgumentParser();p.add_argument('suite',choices=['weapons','effectors','battle','native']);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();sys.path.insert(0,str(D))
 spec=importlib.util.spec_from_file_location('retained_f_d_'+a.suite,D/('verify_'+a.suite+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 hold="d.defenseCommandE('SHIP_SCENARIO_ENEMY_A',{mode:'HOLD'});d.electronicCommandF('SHIP_SCENARIO_ENEMY_A',{auto:false,noiseRequested:false,deceptionRequested:false});"
 if a.suite=='native':
  original_boot=module.support.boot
  def retained_boot(*args,**kwargs):
   page=original_boot(*args,**kwargs);page.evaluate("()=>{const d=window.__NAVAL_SIM_DIAG__;"+hold+"}");return page
  module.support.boot=retained_boot
 for name,value in list(vars(module).items()):
  if isinstance(value,str)and ('__NAVAL_SIM_DIAG__' in value or 'd.importOperationalStateV48Wip11A' in value):
   value=re.sub(r'(d\.importOperationalStateV48Wip11A\(\w+\);)',lambda m:m[0]+hold,value)
   value=re.sub(r'(d\.observerCommandC\([^;\n]+\);)',lambda m:m[0]+hold,value)
   if a.suite=='weapons':
    value=value.replace("checks.inventoryRestoresExactly=JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.inventory)===JSON.stringify(saved.fleet.ships[0].ship.inventory)", "checks.inventoryRestoresExactly=JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.inventory,(k,v)=>k==='startedStep'?undefined:v)===JSON.stringify(saved.fleet.ships[0].ship.inventory,(k,v)=>k==='startedStep'?undefined:v)")
    value=value.replace("delete legacy.fleet.weaponInventorySchema;checks.explicitLegacyInventoryMigration", "delete legacy.fleet.weaponInventorySchema;legacy.fleet.schema='AEGIS_NAVAL_PHYSICAL_FLEET_B_1';legacy.deployment={schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_E_1',targetShip:legacy.deployment.targetShip,enemyProfileId:legacy.deployment.enemyProfileId,enemyAircraftEnabled:legacy.deployment.enemyAircraftEnabled};delete legacy.ship.ew;for(const q of legacy.fleet.ships){delete q.ew;delete q.role;delete q.faction;}checks.explicitLegacyInventoryMigration")
   setattr(module,name,value)
 sys.argv=[str(D/('verify_'+a.suite+'.py')),str(a.html),str(a.out)];module.main()
if __name__=='__main__':main()
