// LIVE_CANONICAL: ShipRuntime owns evacuation control; free rafts belong to the world.
// Capacity is public USN Mark 7 information. Geometry, provision, boarding interval,
// launch stations and leeway below are SIM_TUNED, not a CG-52 equipment inventory.
const SHIP_RESCUE_MK7_K=deepFreezeShipProfileV48Wip09({
  schema:'AEGIS_RESCUE_MODULE_MK7_K_1',capacityPersons:25,
  capacitySource:'US_NAVY_DVIDS_5627398__MIL_DTL_32532A',
  capacitySourceUrl:'https://www.dvidshub.net/image/5627398/uss-makin-island-installs-life-rafts-onboard',
  tuningBasis:'SIM_TUNED_NOT_SHIP_SPECIFIC_STOWAGE_OR_RAFT_HYDRODYNAMICS',
  minimumLaunchIntervalS:4,outerRadiusM:2.75,freeboardM:.12,windLeeway01:.025,
  departureMps:1.2,departureDecayS:35,velocityRelaxationS:2,
  minimumSeparationM:5.9,separationPasses:6
});
function createShipRescueK({ownerEntityId,roster,entities,launchPose,environment,seaLevel,avoidHull}){
  const M=SHIP_RESCUE_MK7_K,maxRafts=Math.ceil(roster/M.capacityPersons);
  let timeS=0,lastLaunchTimeS=-M.minimumLaunchIntervalS,serial=0;
  const own=()=>entities.filter(q=>q.ownerEntityId===ownerEntityId);
  const pending=()=>entities.find(q=>q.ownerEntityId===ownerEntityId&&q.phase==='BOARDING');
  const copy=q=>({...q,personIds:[...q.personIds],positionM:{...q.positionM},velocityMps:{...q.velocityMps}});
  function reset(){for(let i=entities.length-1;i>=0;i--)if(entities[i].ownerEntityId===ownerEntityId)entities.splice(i,1);timeS=serial=0;lastLaunchTimeS=-M.minimumLaunchIntervalS;}
  function release(q){if(!q||q.phase!=='BOARDING')return;q.phase='AFLOAT';q.releasedAtS=timeS;
    const side=q.stationIndex===0?-1:1,a=q.headingRad+side*Math.PI/2;
    q.velocityMps.x+=M.departureMps*Math.cos(a);q.velocityMps.y+=M.departureMps*Math.sin(a);
  }
  function surfacePose(q){const p=q.positionM,h=q.headingRad,dx=Math.cos(h),dy=Math.sin(h),sx=-dy,sy=dx;
    p.z=seaLevel(p.x,p.y)+M.freeboardM;
    q.pitchRad=clamp(Math.atan((seaLevel(p.x+dx,p.y+dy)-seaLevel(p.x-dx,p.y-dy))/2),-deg(18),deg(18));
    q.rollRad=clamp(Math.atan((seaLevel(p.x+sx,p.y+sy)-seaLevel(p.x-sx,p.y-sy))/2),-deg(18),deg(18));
  }
  function board(personId){
    if(!Number.isInteger(personId)||personId<1||personId>roster)return false;
    // Crew history and a raft manifest refer to the same person; no second survivor is created.
    if(entities.some(q=>q.ownerEntityId===ownerEntityId&&q.personIds.includes(personId)))return false;
    let q=pending();
    if(!q){if(serial>=maxRafts||timeS-lastLaunchTimeS+1e-9<M.minimumLaunchIntervalS)return false;
      const stationIndex=serial%2,p=launchPose(stationIndex,serial),id=`${ownerEntityId}.RAFT.${++serial}`;
      q=tagWorldEntityOwnershipV48Wip11A({schema:'AEGIS_WORLD_LIFE_RAFT_K_1',id,serial,capacityPersons:M.capacityPersons,
        personIds:[],phase:'BOARDING',stationIndex,bornAtS:timeS,releasedAtS:null,headingRad:p.headingRad,pitchRad:0,rollRad:0,
        positionM:{x:p.x,y:p.y,z:0},velocityMps:{x:p.vxMps,y:p.vyMps}},'SURVIVAL_RAFT',ownerEntityId);
      entities.push(q);lastLaunchTimeS=timeS;surfacePose(q);
    }
    if(q.personIds.length>=M.capacityPersons)return false;
    q.personIds.push(personId);if(q.personIds.length===M.capacityPersons)release(q);return true;
  }
  function step(dt,crew){
    if(!(Number.isFinite(dt)&&dt>0))return;timeS+=dt;
    const boarding=pending();if(boarding&&(crew.mode==='LOST'||crew.fit+crew.injured===0))release(boarding);
    if(!entities.length)return;
    const wind=environment().wind,wx=M.windLeeway01*wind.speedMps*Math.cos(wind.directionRad),wy=M.windLeeway01*wind.speedMps*Math.sin(wind.directionRad),mix=1-Math.exp(-dt/M.velocityRelaxationS);
    for(const q of entities){if(q.ownerEntityId!==ownerEntityId)continue;
      if(q.phase==='BOARDING'){const p=launchPose(q.stationIndex,q.serial-1);q.positionM.x=p.x;q.positionM.y=p.y;q.headingRad=p.headingRad;q.velocityMps.x=p.vxMps;q.velocityMps.y=p.vyMps;}
      else {const age=Math.max(0,timeS-q.releasedAtS),a=q.headingRad+(q.stationIndex===0?-1:1)*Math.PI/2,v=M.departureMps*Math.exp(-age/M.departureDecayS);
        q.velocityMps.x+=(wx+v*Math.cos(a)-q.velocityMps.x)*mix;q.velocityMps.y+=(wy+v*Math.sin(a)-q.velocityMps.y)*mix;
        q.positionM.x+=q.velocityMps.x*dt;q.positionM.y+=q.velocityMps.y*dt;
        if(crew.mode!=='LOST')avoidHull?.(q);
      }
    }
    // SIM_TUNED contact constraints keep inflated tubes from occupying the same
    // water. Boarding rafts remain tethered; only free rafts move apart. This
    // neither applies forces to the ship nor consumes a combat RNG sample.
    const rafts=own();for(let pass=0;pass<M.separationPasses;pass++){
      for(let i=0;i<rafts.length;i++)for(let j=i+1;j<rafts.length;j++){
        const a=rafts[i],b=rafts[j],dx=b.positionM.x-a.positionM.x,dy=b.positionM.y-a.positionM.y,d=Math.hypot(dx,dy);
        if(d>=M.minimumSeparationM)continue;
        const af=a.phase==='AFLOAT',bf=b.phase==='AFLOAT';if(!af&&!bf)continue;
        const fallback=a.headingRad+(a.stationIndex===0?-1:1)*Math.PI/2,nx=d>1e-8?dx/d:Math.cos(fallback),ny=d>1e-8?dy/d:Math.sin(fallback),push=M.minimumSeparationM-d,k=af&&bf?.5:1;
        if(af){a.positionM.x-=nx*push*k;a.positionM.y-=ny*push*k;}
        if(bf){b.positionM.x+=nx*push*k;b.positionM.y+=ny*push*k;}
      }
      if(crew.mode!=='LOST')for(const q of rafts)if(q.phase==='AFLOAT')avoidHull?.(q);
    }
    for(const q of rafts)surfacePose(q);
  }
  function snapshot(){return {schema:'AEGIS_SURVIVAL_RAFT_STATE_K_1',moduleId:M.schema,ownerEntityId,capacityPersons:M.capacityPersons,
    provisionBasis:'SIM_TUNED_CEIL_PROFILE_ROSTER_OVER_CAPACITY',maxRafts,timeS,lastLaunchTimeS,serial,rafts:own().map(copy)};}
  function summary(){let rafts=0,afloat=0,boarding=0,persons=0;for(const q of entities)if(q.ownerEntityId===ownerEntityId){rafts++;persons+=q.personIds.length;if(q.phase==='AFLOAT')afloat++;else boarding++;}
    return {rafts,afloat,boarding,persons,capacityPersons:M.capacityPersons,maxRafts};}
  function restore(src){reset();timeS=src.timeS;lastLaunchTimeS=src.lastLaunchTimeS;serial=src.serial;for(const q of src.rafts)entities.push(copy(q));return summary();}
  return {board,step,reset,snapshot,summary,restore};
}
function rescueLaunchPoseK(stationIndex,serial=0,nav=shipNav){
  const deck=ACTIVE_SHIP_PROFILE.geometry.hardpoints.flightDeck,geo=shipGeometryLayout(),side=stationIndex===0?-1:1;
  const x=deck.x+((Math.floor(serial/2)%3)-1)*Math.min(4,deck.hL*.45),y=side*(geo.hullSection(x).b+SHIP_RESCUE_MK7_K.outerRadiusM+1.5),h=nav.heading,c=Math.cos(h),s=Math.sin(h);
  return {x:worldToMeters(nav.positionWorld.x)+x*c-y*s,y:worldToMeters(nav.positionWorld.y)+x*s+y*c,headingRad:h,
    vxMps:nav.speed*c,vyMps:nav.speed*s};
}
function rescueAvoidHullK(q){
  const nav=ACTIVE_SHIP_RUNTIME.navigation,h=nav.heading,c=Math.cos(h),s=Math.sin(h),dx=q.positionM.x-worldToMeters(nav.positionWorld.x),dy=q.positionM.y-worldToMeters(nav.positionWorld.y),x=dx*c+dy*s,y=-dx*s+dy*c,geo=shipGeometryLayout();
  if(x<geo.stats.bounds.stern||x>geo.stats.bounds.bow)return;
  const b=geo.hullSection(x).b+SHIP_RESCUE_MK7_K.outerRadiusM+.5;if(Math.abs(y)>=b)return;
  const side=y===0?(q.stationIndex===0?-1:1):Math.sign(y),push=side*b-y;
  q.positionM.x-=push*s;q.positionM.y+=push*c;
}
function shipRescueK(){
  const r=ACTIVE_SHIP_RUNTIME;if(!r.rescue)r.rescue=createShipRescueK({ownerEntityId:r.entityId,roster:ACTIVE_SHIP_PROFILE.crew.roster,
    entities:ENGAGEMENT_RUNTIME.world.entities.lifeRafts,launchPose:rescueLaunchPoseK,environment:maritimeEnvironmentSnapshotWip13A3,
    seaLevel:maritimeSeaLevelAtSimulationMetersWip13A3,avoidHull:rescueAvoidHullK});return r.rescue;
}
function rescueRenderStatesK(){return ENGAGEMENT_RUNTIME.world.entities.lifeRafts.map(q=>({id:q.id,ownerEntityId:q.ownerEntityId,
  phase:q.phase,persons:q.personIds.length,capacityPersons:q.capacityPersons,xM:q.positionM.x,yM:q.positionM.z,zM:q.positionM.y,
  headingRad:q.headingRad,pitchRad:q.pitchRad,rollRad:q.rollRad,presentationOnly:true,physicsFeedback:false}));}
function spyCicFaceLayoutK(headingRad=shipNav.heading){return SPY1DV_FACE_KEYS.map(face=>{
  const physicalRelativeRad=SPY1DV_FACE_CENTER_REL[face];
  // Preserve the established DDG 45/135-degree CIC schematic. CG uses its
  // registered cardinal normals, including the source mesh's tiny tolerances.
  const relativeRad=IS_BUNKER?physicalRelativeRad:Math.round(physicalRelativeRad/(Math.PI/4))*(Math.PI/4);
  return {face,relativeRad,physicalRelativeRad,angleRad:relativeRad+headingRad,halfRad:Math.PI/4,moduleName:SPY1DV_FACE_MODULE[face]};});}
function drawRescueRaftsCicK(){
  const rows=ENGAGEMENT_RUNTIME.world.entities.lifeRafts;if(!rows.length)return;
  ctx.save();ctx.strokeStyle='#ffb458';ctx.fillStyle='#ffb458';ctx.lineWidth=tacticalLineWidthWorld(1.1,.5);
  const r=tacticalWorldPx(3,4,2.5,4),detail=currentTacticalViewKm()<=5;ctx.font=`${tacticalFontWorldSize(7,5)}px monospace`;ctx.textAlign='left';
  for(const q of rows){const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y);ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.stroke();
    ctx.beginPath();ctx.moveTo(x-r*.6,y);ctx.lineTo(x+r*.6,y);ctx.moveTo(x,y-r*.6);ctx.lineTo(x,y+r*.6);ctx.stroke();
    if(detail)ctx.fillText(`RAFT ${q.personIds.length}/${q.capacityPersons}`,x+r+2,y-r-2);
  }
  if(!detail){const x=rows.reduce((s,q)=>s+metersToWorld(q.positionM.x),0)/rows.length,y=rows.reduce((s,q)=>s+metersToWorld(q.positionM.y),0)/rows.length,people=rows.reduce((s,q)=>s+q.personIds.length,0);
    ctx.fillText(`RAFT ${rows.length} · ${people}명`,x+r+2,y-r-2);}
  ctx.restore();
}
function validateOperationalRescueK(src,ctx,errors){
  const err=(code,path='')=>operationalErrorV48Wip11B(errors,code,path),groups=src.ship?.crew?.groups;
  if(!Array.isArray(groups))return;
  const evacuated=new Set();for(const g of groups){if(g.evacuated!==0&&g.evacuated!==1)err('RESCUE_PERSON_COUNT',String(g.id));
    if(g.evacuated===1){if(g.dead!==0||g.fit!==0||g.injured!==0)err('RESCUE_PERSON_STATUS',String(g.id));evacuated.add(Number(g.id));}}
  const s=src.ship?.rescue;if(s===undefined){if(src.capabilities?.restores?.includes('survivalRafts'))err('RESCUE_MISSING');return;}
  if(!operationalRecordV48Wip11B(s)){err('RESCUE_STATE');return;}
  const M=SHIP_RESCUE_MK7_K,max=Math.ceil(ctx.crewExpectedCount/M.capacityPersons);
  if(s.schema!=='AEGIS_SURVIVAL_RAFT_STATE_K_1'||s.moduleId!==M.schema)err('RESCUE_SCHEMA');
  if(s.ownerEntityId!==src.shipId)err('RESCUE_OWNER');
  if(s.capacityPersons!==M.capacityPersons||s.maxRafts!==max||s.provisionBasis!=='SIM_TUNED_CEIL_PROFILE_ROSTER_OVER_CAPACITY')err('RESCUE_PROVISION');
  if(!operationalFiniteV48Wip11B(s.timeS)||s.timeS<0||!operationalFiniteV48Wip11B(s.lastLaunchTimeS)||s.lastLaunchTimeS<-M.minimumLaunchIntervalS||s.lastLaunchTimeS>s.timeS)err('RESCUE_TIME');
  if(!Array.isArray(s.rafts)||s.rafts.length>max){err('RESCUE_RAFTS');return;}
  if(s.serial!==s.rafts.length)err('RESCUE_SERIAL');
  const seen=new Set();let boarding=0;
  for(let i=0;i<s.rafts.length;i++){const q=s.rafts[i],id=`${src.shipId}.RAFT.${i+1}`;
    if(!operationalRecordV48Wip11B(q)){err('RESCUE_RAFT',id);continue;}
    if(q.schema!=='AEGIS_WORLD_LIFE_RAFT_K_1'||q.id!==id||q.serial!==i+1||q.ownerEntityId!==src.shipId||q.worldEntityClass!=='SURVIVAL_RAFT')err('RESCUE_RAFT_ID',id);
    if(q.capacityPersons!==M.capacityPersons||!Array.isArray(q.personIds)||q.personIds.length<1||q.personIds.length>M.capacityPersons){err('RESCUE_MANIFEST',id);continue;}
    for(const n of q.personIds){if(!Number.isInteger(n)||!evacuated.has(n)||seen.has(n))err('RESCUE_PERSON_ID',id+':'+n);seen.add(n);}
    if(!['BOARDING','AFLOAT'].includes(q.phase))err('RESCUE_PHASE',id);
    if(q.phase==='BOARDING'){boarding++;if(q.personIds.length===M.capacityPersons||i!==s.rafts.length-1||q.releasedAtS!==null||src.ship.crew.mode==='LOST')err('RESCUE_BOARDING',id);}
    else if(!operationalFiniteV48Wip11B(q.releasedAtS)||q.releasedAtS<q.bornAtS||q.releasedAtS>s.timeS)err('RESCUE_RELEASE',id);
    if(!operationalFiniteV48Wip11B(q.bornAtS)||q.bornAtS<0||q.bornAtS>s.timeS||(i&&q.bornAtS<s.rafts[i-1].bornAtS+M.minimumLaunchIntervalS-1e-8))err('RESCUE_BIRTH',id);
    if(q.stationIndex!==i%2)err('RESCUE_STATION',id);
    for(const key of ['headingRad','pitchRad','rollRad'])if(!operationalFiniteV48Wip11B(q[key]))err('RESCUE_ATTITUDE',id+'.'+key);
    for(const [key,axes]of [['positionM',['x','y','z']],['velocityMps',['x','y']]])if(!operationalRecordV48Wip11B(q[key])||!axes.every(a=>operationalFiniteV48Wip11B(q[key][a])))err('RESCUE_KINEMATICS',id+'.'+key);
  }
  if(boarding>1||seen.size!==evacuated.size||[...evacuated].some(id=>!seen.has(id)))err('RESCUE_CREW_CONSERVATION');
  if(s.rafts.length&&s.lastLaunchTimeS!==s.rafts.at(-1).bornAtS)err('RESCUE_LAST_LAUNCH');
}
function migrateLegacyRescueK(src){
  if(src.ship.rescue!==undefined)return null;
  const M=SHIP_RESCUE_MK7_K,people=src.ship.crew.groups.filter(g=>g.evacuated===1).map(g=>Number(g.id)),rafts=[];
  const maxRafts=Math.ceil(ACTIVE_SHIP_PROFILE.crew.roster/M.capacityPersons),serial=Math.ceil(people.length/M.capacityPersons),timeS=Math.max(src.ship.crew.timeS,Math.max(0,serial-1)*M.minimumLaunchIntervalS);
  for(let i=0;i<serial;i++){const p=rescueLaunchPoseK(i%2,i,src.ship.navigation),side=i%2===0?-1:1,a=p.headingRad+side*Math.PI/2;
    // Old saves had no raft positions. Explicitly reconstruct only their recorded
    // evacuated survivors outside the source hull; do not claim historical sea positions.
    rafts.push({schema:'AEGIS_WORLD_LIFE_RAFT_K_1',id:`${src.shipId}.RAFT.${i+1}`,serial:i+1,ownerEntityId:src.shipId,worldEntityClass:'SURVIVAL_RAFT',
      capacityPersons:M.capacityPersons,personIds:people.slice(i*M.capacityPersons,(i+1)*M.capacityPersons),phase:'AFLOAT',stationIndex:i%2,
      bornAtS:i*M.minimumLaunchIntervalS,releasedAtS:i*M.minimumLaunchIntervalS,headingRad:p.headingRad,pitchRad:0,rollRad:0,
      positionM:{x:p.x+Math.floor(i/2)*6*Math.cos(a),y:p.y+Math.floor(i/2)*6*Math.sin(a),z:M.freeboardM},velocityMps:{x:0,y:0}});
  }
  src.ship.rescue={schema:'AEGIS_SURVIVAL_RAFT_STATE_K_1',moduleId:M.schema,ownerEntityId:src.shipId,capacityPersons:M.capacityPersons,
    provisionBasis:'SIM_TUNED_CEIL_PROFILE_ROSTER_OVER_CAPACITY',maxRafts,timeS,lastLaunchTimeS:serial?(serial-1)*M.minimumLaunchIntervalS:-M.minimumLaunchIntervalS,serial,rafts};
  return {schema:'AEGIS_LEGACY_RESCUE_MIGRATION_K_1',persons:people.length,rafts:serial,policy:'PREFLIGHT_THEN_DETACHED_RECONSTRUCTION__LEGACY_WORLD_POSITIONS_UNAVAILABLE'};
}
function rescueModuleAuditK(){
  // DIAGNOSTIC_ONLY: isolated world array and environment; never active crew.
  const foreign={ownerEntityId:'OTHER',id:'OTHER.RAFT'},entities=[foreign],factory=()=>createShipRescueK({ownerEntityId:'DIAG',roster:26,entities,
    launchPose:side=>({x:0,y:side?20:-20,headingRad:0,vxMps:0,vyMps:0}),environment:()=>({wind:{speedMps:6,directionRad:0}}),seaLevel:(x,y)=>.2*Math.sin(x*.1+y*.02)});
  const r=factory(),checks={firstPerson:r.board(1),duplicateBlocked:!r.board(1),unknownPersonBlocked:!r.board(0)&&!r.board(27)};
  for(let i=2;i<=25;i++)r.board(i);checks.fullReleased=r.summary().afloat===1;checks.intervalBlocks=!r.board(26);
  const before=r.snapshot().rafts[0].positionM;for(let i=0;i<240;i++)r.step(1/60,{mode:'ABANDONED',fit:1,injured:0});
  checks.drift=Math.hypot(r.snapshot().rafts[0].positionM.x-before.x,r.snapshot().rafts[0].positionM.y-before.y)>1;
  checks.lastPerson=r.board(26);r.step(1/60,{mode:'ABANDONED',fit:0,injured:0});
  const s=r.snapshot();checks.lastPartialReleased=r.summary().afloat===2&&s.rafts[1].personIds.length===1;
  s.rafts[0].personIds.length=0;checks.detached=r.summary().persons===26;
  const restore=r.snapshot();r.reset();r.restore(restore);checks.restoreExact=JSON.stringify(r.snapshot())===JSON.stringify(restore);
  r.reset();checks.resetOwnOnly=entities.length===1&&entities[0]===foreign&&r.summary().rafts===0;
  return {schema:'AEGIS_RESCUE_MODULE_AUDIT_K_1',checks,pass:Object.values(checks).every(Boolean)};
}
