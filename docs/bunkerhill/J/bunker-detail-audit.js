function vlsInstallationSlotAudit(){
  const sections={};for(const [section,cfg]of Object.entries(ACTIVE_SHIP_PROFILE.weapons.vls.sections)){
    const cells=vlsCells[section],rows=cells.map((cell,index)=>{const slot=wip125InstallationSlot(section,index),registration=shipCellRegistration(section,slot?.row,slot?.col);
      return {index,row:cell.row,col:cell.col,installedRow:slot?.row,installedCol:slot?.col,type:cell.type,registered:!!registration,position:registration?{x:registration.x,y:registration.y,z:registration.z}:null};});
    sections[section]={capacity:cfg.cells,gridRows:cfg.rows,gridColumns:cfg.cols,missingSlots:cfg.rows*cfg.cols-cfg.cells,rows,
      pass:cells.length===cfg.cells&&new Set(rows.map(q=>q.row+':'+q.col)).size===cfg.cells&&rows.every(q=>q.row===q.installedRow&&q.col===q.installedCol&&q.registered)};
  }
  return {schema:'AEGIS_VLS_FIXED_INSTALLATION_AUDIT_G_V1',profileId:ACTIVE_SHIP_PROFILE.id,sections,pass:Object.values(sections).every(q=>q.pass)};
}
function migrateBunkerOperationalInteriorG(source){
  if(!IS_BUNKER||source.profileRevision!=='BUNKERHILL_LATE_D_1')return null;
  const spaces=getShipInteriorTopologyV48Wip06().spaces,byMacro=new Map();
  for(const s of spaces){if(!byMacro.has(s.macroId))byMacro.set(s.macroId,[]);byMacro.get(s.macroId).push(s);}
  const within=(p,s)=>p.x>=s.x0&&p.x<=s.x1&&p.y>=s.y0&&p.y<=s.y1&&p.z>=s.z0&&p.z<=s.z1,
    clamped=(p,s)=>({x:Math.max(s.x0+.06,Math.min(s.x1-.06,p.x)),y:Math.max(s.y0+.06,Math.min(s.y1-.06,p.y)),z:Math.max(s.z0+.06,Math.min(s.z1-.06,p.z))});
  let remapped=0,relocated=0,maxDisplacementM=0;
  for(const person of source.ship.crew.groups){
    const children=byMacro.get(person.spaceId);if(!children?.length)throw Error('LEGACY_SPACE_NOT_REGISTERED');
    const point=person.position??children.find(s=>s.id===person.spaceId)?.center??children[0].center;
    let space=children.find(s=>within(point,s)),position=point;
    if(!space){const candidates=children.map(s=>{const p=clamped(point,s);return {s,p,d:Math.hypot(p.x-point.x,p.y-point.y,p.z-point.z)};}).sort((a,b)=>a.d-b.d||a.s.id.localeCompare(b.s.id));
      space=candidates[0].s;position=candidates[0].p;relocated++;maxDisplacementM=Math.max(maxDisplacementM,candidates[0].d);}
    if(person.spaceId!==space.id)remapped++;
    person.spaceId=space.id;person.cellId=space.parentFloodCellId;person.position={...position};
  }
  const from=source.profileRevision;source.profileRevision=ACTIVE_SHIP_PROFILE.revision;
  return {schema:'AEGIS_CG52_INTERIOR_OPERATIONAL_MIGRATION_G_1',from,to:source.profileRevision,
    personnel:source.ship.crew.groups.length,remapped,relocated,maxDisplacementM,
    policy:'PREFLIGHT_ALL_CODECS_THEN_MAP_LEGACY_SPACE_POSITION_ON_DETACHED_CLONE'};
}
Object.assign(window.__NAVAL_SIM_DIAG__,{vlsInstallationSlotAudit,bunkerInteriorDetailAudit:()=>IS_BUNKER?getShipInteriorTopologyV48Wip06().audit():null});
