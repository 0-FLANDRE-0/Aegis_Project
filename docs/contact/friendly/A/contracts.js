// Test-only synthetic observations. No target truth is supplied to association.
window.__FC_CONTRACTS__=async()=>{
 __GB_TEST__.reset(419010);const checks={},records={};
 const air=(x=4000,y=0,z=50)=>{const dx=x,dy=y,dz=z-22,r=Math.hypot(dx,dy,dz);return {x:metersToWorld(x),y:metersToWorld(y),z,rangeM:r,azRad:Math.atan2(y,x),elRad:Math.atan2(dz,Math.hypot(x,y)),radialMps:0,rangeSigmaM:15,azSigmaDeg:.1,elSigmaDeg:.1,radialVelSigmaMps:3,losUx:dx/r,losUy:dy/r,losUz:dz/r,sensorXWorld:0,sensorYWorld:0,sensorZM:22,sensorVxMps:0,sensorVyMps:0,sensorVzMps:0,source:'SPY1DV_AIR',domainEvidence:{air:.9,surface:.05,missile:.05,background:0}};};
 const surface=(x=4000,y=0)=>({...air(x,y,8),rangeM:Math.hypot(x,y),elRad:undefined,z:8,surfaceReferenceZM:8,source:'SPQ9B_SURFACE_PRECISION',domainEvidence:{surface:.9,air:.05,missile:.05,background:0}});
 let m=air(),tr=updateSensorTrackMeasurement(null,m,{source:m.source,taskType:'SEARCH_VOLUME'}),id=tr.trackId;
 const before={x:[...tr._kfX],P:[...tr._kfP]};trackApplySurfaceDomainConstraint(tr,8);
 checks.surfacePriorDoesNotOverwriteObservedAir=JSON.stringify(before)===JSON.stringify({x:[...tr._kfX],P:[...tr._kfP]});
 tr._kfX[4]=230;trackSyncLegacyFromEkf(tr);let s=surface();
 const assignments=surfaceAssignmentsPreferEstablishedWip13B14([s],trackSurfacePositionAssociationNisWip13B9,64);
 checks.fastTangentialAirCanAssociate2D=assignments.get(0)?.trackId===id;
 const accepted=updateSensorTrackMeasurement(id,s,{source:s.source});checks.surfaceContributionKeepsAir=!!accepted&&tr.domain==='AIR'&&Math.abs(tr.z-50)<1;
 records.airAfter2D={id,z:tr.z,domain:tr.domain,velocityY:tr._kfX[4],nis:tr._kfNis};
 tracks.clear();s=surface();tr=updateSensorTrackMeasurement(null,s,{source:s.source});id=tr.trackId;m=air();
 checks.surfaceAssumptionNotMeasuredDomain=trackMayAcceptAirPlotCrossDomainWip13B14(tr,m);
 const nis=trackRadarAssociationNisV31(tr,m);const found=updateSensorTrackMeasurement(id,m,{source:m.source,taskType:'SEARCH_VOLUME'});
 checks.initial2DAdopts3DWithoutNewId=found?.trackId===id&&tracks.size===1;
 checks.accepted3DClearsSurfacePartition=!trackSurfaceBackedWip13B14(tr);
 records.first3D={nis,id,z:tr.z,domain:tr.domain};
 const far=air(15000,5000,1000);checks.incompatiblePlotStillFailsNativeGate=trackRadarAssociationNisV31(tr,far)>TRACK_FILTER_MODEL.nisGateSearch&&updateSensorTrackMeasurement(id,far,{source:far.source,taskType:'SEARCH_VOLUME'})===null;
 tracks.clear();const a=air(4000,0,50),b=air(4000,400,80);const t1=updateSensorTrackMeasurement(null,a,{source:a.source}),t2=updateSensorTrackMeasurement(null,b,{source:b.source});
 const p1=surface(4000,0),p2=surface(4000,400),as=surfaceAssignmentsPreferEstablishedWip13B14([p1,p2],trackSurfacePositionAssociationNisWip13B9,64);
 checks.resolvedObjectsStayOneToOne=as.size===2&&new Set([...as.values()].map(x=>x.trackId)).size===2&&as.get(0).trackId===t1.trackId&&as.get(1).trackId===t2.trackId;
 records.resolved=[...as];
 records.environment=await window.__ENV_D__.status();checks.environmentTableStillMatches=records.environment.match===true;
 return {checks,records,core:window.__CORE_SELFTEST_FAILURES__,pass:Object.values(checks).every(Boolean)};
};
