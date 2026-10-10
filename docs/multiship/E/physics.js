// Physical breakup/renderer boundary. No controller reads these world collections.
function navalRetirementObjectsE(){
  if(!physicalShipsB().length)return enemyMissiles;
  return [...enemyMissiles,...missiles,...ramMissiles,...harpoonWorldA(),...physicalShipsB().flatMap(r=>[...r.weapons.executionD.sam,...r.weapons.executionD.ram])];
}
