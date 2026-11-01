// TEST ONLY: initialise a saved flight pose / native launch, then run real fixed ticks.
const FC_REPRO={events:[],active:false,installed:false};
function fcTrackSummary(){return [...tracks.values()].map(t=>({id:t.trackId,number:t.trackNumber,source:t.sensorSource,domain:t.domain,classification:t.classification,identity:t.identity,hits:t.sensorHits,confirmed:t.confirmed,ageS:t.sensorAge,visible:trackIsDisplayable(t),xM:worldToMeters(t.x),yM:worldToMeters(t.y),zM:t.z,vx:worldSpeedToMps(t.vx),vy:worldSpeedToMps(t.vy),vz:t.vz,nis:t._kfNis,rejectedNis:t._kfRejectedNis,iff:t.iffF??null,own:t._harpoonOwnC??null}));}
function fcReproInstall(){if(FC_REPRO.installed)return;FC_REPRO.installed=true;const native=updateSensorTrackMeasurement;
 updateSensorTrackMeasurement=function(id,meas,meta){let nearest=[];
  if(FC_REPRO.active&&id==null)nearest=[...tracks.values()].filter(t=>t._kfX&&t._kfP).map(t=>({id:t.trackId,nis:trackRadarAssociationNisV31(t,meas),positionNis:typeof trackCartesianAssociationNisV33==='function'?trackCartesianAssociationNisV33(t,meas):null,age:t.sensorAge,domain:t.domain,xM:t._kfX[0],yM:t._kfX[1],zM:t._kfX[2],vx:t._kfX[3],vy:t._kfX[4],vz:t._kfX[5]})).sort((a,b)=>a.nis-b.nis).slice(0,3);
  const out=native.apply(this,arguments);
  if(FC_REPRO.active&&(id==null||!out))FC_REPRO.events.push({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,requested:id??null,id:out?.trackId??null,source:meta?.source??meas.source,task:meta?.taskType,meas:{xM:worldToMeters(meas.x),yM:worldToMeters(meas.y),zM:meas.z,rangeM:meas.rangeM,az:meas.azRad,el:meas.elRad,radialMps:meas.radialMps,rangeSigmaM:meas.rangeSigmaM,azSigmaDeg:meas.azSigmaDeg,elSigmaDeg:meas.elSigmaDeg,rvSigma:meas.radialVelSigmaMps,sensorX:meas.sensorXWorld,sensorY:meas.sensorYWorld,sensorZ:meas.sensorZM},nearest});return out;
 };
}
window.__FRIENDLY_REPRO_A__={
 run(c={}){__GB_TEST__.reset(c.seed??419010);FC_REPRO.active=false;FC_REPRO.events=[];
  BATTLESPACE_DIAG_BYPASS=true;emconActive=false;gunB1SetAuto(false);
  let h=null,release=null;
  if(c.kind==='HELO'){
   const s=exportOperationalState(),a=s.ship.aviation.aircraft[0],z=c.altM??50;
   Object.assign(a,{state:'ARRIVED_HOVER',visible:true,onboard:false,stateTick:0,targetAltitudeM:z,positionM:{x:4000,y:0,z},departPointM:{x:4000,y:0,z},holdPointM:{x:4000,y:0,z},engine01:[1,1],rotor01:1,blades01:1,tail01:1,iffOn:c.iff!==false,radarOn:false,radarMode:'STBY'});
   const v=validateOperationalStateV48Wip11B(s);if(!v.ok)throw Error(JSON.stringify(v));importOperationalState(s);h=heloWorldA().get(a.id);
   if(c.moving){heloCommandA(h.id,'ROUTE_APPEND',{x:4000,y:6000});heloCommandA(h.id,'ROUTE_APPEND',{x:1000,y:6000});}
  }else{
   const api=window.__HARPOON_DIAG_A__;api.routeToggle();for(const p of(c.route??[{x:3000,y:0},{x:3000,y:8000},{x:12000,y:8000}]))api.routeAdd(p);release=api.fire();
  }
  if(c.auto)engagementControlMode='AUTO';
  const inventory=()=>JSON.stringify({vls:Object.fromEntries(Object.entries(vlsCells).map(([section,arr])=>[section,arr.map(x=>({type:x.type,essmCount:x.essmCount}))])),ciws:ciws.map(x=>({id:x.id,ammo:x.ammo}))}),inventoryBefore=inventory();
  if(c.observe!==false){fcReproInstall();FC_REPRO.active=true;}
  const samples=[];for(let i=0;i<Math.round((c.seconds??60)/SIM_FIXED_DT);i++){
   if(Number.isFinite(c.emconAtS)&&i===Math.round(c.emconAtS/SIM_FIXED_DT)&&!emconActive)toggleEmcon('DIAGNOSTIC');
   simulateFixedTick(SIM_FIXED_DT);
   if(i%60===59){const m=c.kind==='HARPOON'?harpoonWorldA()[0]:null;samples.push({timeS:simStepCounter*SIM_FIXED_DT,tracks:fcTrackSummary(),truthDiagnosticOnly:h?{x:h.positionM.x,y:h.positionM.y,z:h.positionM.z,state:h.state}:m?{position:m.positionM,phase:m.phase,alive:m.alive}:null,trackSerial:trackIdSerialV27});}
  }
  FC_REPRO.active=false;return {case:c,release,samples,births:FC_REPRO.events,rng:SIM_RNG_STATE,step:simStepCounter,final:fcTrackSummary(),picture:__HARPOON_DIAG_A__.operatorPicture(),inventoryUnchanged:inventoryBefore===inventory(),core:window.__CORE_SELFTEST_FAILURES__,faults:[window.__WIP125_DIAG__.wip150RuntimeFault(),window.__WIP125_DIAG__.wip150PresentationFault()]};
 }
};
