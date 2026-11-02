// TRACK-A: DIAGNOSTIC_ONLY compatibility views. No consumer, filter, hit,
// identity, authority, RNG, clock or scheduler reads these records back.
const TRACK_A_DIAG={enabled:false,capacity:1024,ring:[],head:0,size:0,serial:0,measurementSerial:0,dropped:0,errors:0,measurements:new WeakMap(),origins:new WeakMap()};
function trackAFiniteA(v){return typeof v==='number'&&Number.isFinite(v)?v:null;}
function trackAScalarA(v){return typeof v==='string'?v.slice(0,160):typeof v==='boolean'?v:trackAFiniteA(v);}
function trackANumbersA(v,max=64){if(!Array.isArray(v)&&!ArrayBuffer.isView(v))return null;const a=Array.from(v).slice(0,max);return a.every(x=>trackAFiniteA(x)!==null)?a:null;}
function trackAExactNumbersA(v,size){return (Array.isArray(v)||ArrayBuffer.isView(v))&&v.length===size?trackANumbersA(v,size):null;}
function trackAFieldsA(v,keys){const out={};for(const k of keys)if(v&&v[k]!==undefined){const q=trackAScalarA(v[k]);if(q!==null)out[k]=q;}return out;}
function trackAVectorA(p,keys=['x','y','z']){if(!p||typeof p!=='object')return null;const out={};for(const k of keys)out[k]=trackAFiniteA(p[k]);return Object.values(out).some(x=>x!==null)?out:null;}
function trackAWorldM_A(v){return trackAFiniteA(v)===null?null:worldToMeters(v);}
function trackANormalizeA(kind,payload,context={}){
 kind=typeof kind==='string'?kind:'UNSPECIFIED';
 const p=payload&&typeof payload==='object'?payload:{},c=context&&typeof context==='object'?context:{},observed={},assumed={},derived={},reported={},rows=[];
 const sourceSensor=trackAScalarA(c.sourceSensor??p.source??p.sourceSensor)??'UNSPECIFIED',observerShip=trackAScalarA(c.observerShip),measuredAtS=trackAFiniteA(p.measuredAtS??c.measuredAtS),receivedAtS=trackAFiniteA(c.receivedAtS??p.receivedAtS);
 let name=kind,physicalDimension=null;
 const take=(key,value)=>{if(trackAFiniteA(value)!==null){observed[key]=value;rows.push(key);}};
 const polar=el=>{take('rangeM',p.measuredRangeM??p.rangeM);take('azRad',p.measuredAzRad??p.azRad);if(el)take('elRad',p.elRad);};
 const xy=()=>{const x=trackAWorldM_A(p.x),y=trackAWorldM_A(p.y);if(x!==null||y!==null)derived.cartesianPositionM={x,y,z:trackAFiniteA(p.z)};};
 if(kind==='AIR_RADAR'){polar(true);take('radialMps',p.radialMps);physicalDimension=rows.length;xy();}
 else if(kind==='SURFACE_RADAR'){polar(false);take('radialMps',p.radialMps);physicalDimension=rows.length;xy();assumed.surfaceReferenceZM={value:trackAFiniteA(p.surfaceReferenceZM),role:'MODEL_PRIOR_NOT_ELEVATION'};}
 else if(kind==='CIWS_LOCAL_RF'){polar(true);physicalDimension=rows.length;derived.relativeCartesianM=trackAVectorA(p,['rxM','ryM','rzM']);}
 else if(kind==='VISUAL_CARTESIAN'){
  take('xM',trackAWorldM_A(p.x));take('yM',trackAWorldM_A(p.y));take('zM',p.z);physicalDimension=rows.length;
  if(p.radialMps!==undefined)assumed.radialMps={value:trackAFiniteA(p.radialMps),role:'OPTICAL_PLACEHOLDER_NOT_DOPPLER'};
 }
 else if(kind==='HELO_RADAR'){polar(false);physicalDimension=rows.length;derived.cartesianPositionM=trackAVectorA(p.positionM);if(!derived.cartesianPositionM)xy();assumed.surfaceReferenceZM={value:trackAFiniteA(p.surfaceReferenceZM??p.positionM?.z??p.z),role:'MODEL_PRIOR_NOT_ELEVATION'};}
 else if(kind==='ESM_BEARING'){take('bearingRad',p.bearingRad??p.bearing);physicalDimension=rows.length;reported.emitterEvidence=trackAFieldsA(p,['band','emitterFamily','family','confidence','type','emitterClass','strength']);}
 else if(kind==='IFF_REPLY'){
  take('rangeM',p.rangeM);take('azRad',p.azRad??p.bearing);take('elRad',p.elRad??p.elevationRad);physicalDimension=rows.length;
  if(typeof p.authenticatedFriendly==='boolean')observed.authenticatedFriendly=p.authenticatedFriendly;
 }
 else if(kind==='ISAR_EVIDENCE'){
  const f=p.result??p;Object.assign(observed,trackAFieldsA(f,['lengthM','lengthSigmaM','mastPosition01','mastSigma01','quality','heightSigmaM','crossResolutionM','rangeResolutionM','deltaThetaRad']));
  const heights=trackANumbersA(f.heightsM,32);if(heights)observed.heightsM=heights;physicalDimension=0;name='ISAR_FEATURE_EVIDENCE_NOT_POSITION_HIT';
  reported.positionGateM=trackAVectorA(p.positionM);reported.candidates=Array.isArray(f.candidates)?f.candidates.slice(0,16).map(q=>trackAFieldsA(q,['classId','label','confidence'])):[];
 }
 else if(kind==='OFFBOARD_PLOT'){
  name='REPORTED_CARTESIAN_POSITION';reported.positionM=trackAVectorA(p.positionM);reported.covarianceM2=trackAExactNumbersA(p.covarianceM2??p.cartesianCovarianceM2,9);
  if(!reported.positionM&&(trackAFiniteA(p.x)!==null||trackAFiniteA(p.y)!==null)){reported.positionM={x:trackAWorldM_A(p.x),y:trackAWorldM_A(p.y),z:trackAFiniteA(p.z)};reported.coordinatesTransformedFromWorld=true;}
  if(reported.positionM)for(const k of ['x','y','z'])if(reported.positionM[k]!==null)rows.push('reported.'+k+'M');
  reported.componentObservability='UPSTREAM_PHYSICAL_DIMENSIONS_NOT_IN_RECEIVED_SCHEMA';
 }
 else if(kind==='NETWORK_TRACK'){
  name='REPORTED_FILTER_STATE';reported.stateM=trackAExactNumbersA(p.stateM,6);reported.covariance=trackAExactNumbersA(p.covariance,36);reported.stateAtS=trackAFiniteA(p.stateAtS);
  if(reported.stateM)for(let i=0;i<reported.stateM.length;i++)rows.push('reported.'+['xM','yM','zM','vxMps','vyMps','vzMps'][i]);
  reported.componentObservability='SENDER_FILTER_ESTIMATE_NOT_SIX_PHYSICAL_MEASUREMENTS';
 }
 else if(kind==='NETWORK_SELF'){
  name='REPORTED_OWN_NAVIGATION';reported.positionM=trackAVectorA(p.positionM);reported.stateM=trackAExactNumbersA(p.stateM,6);reported.navigation=trackAFieldsA(p,['heading','speedMps']);
  if(reported.stateM){for(let i=0;i<reported.stateM.length;i++)rows.push('reported.'+['xM','yM','zM','vxMps','vyMps','vzMps'][i]);derived.navigation={xM:reported.stateM[0],yM:reported.stateM[1],vxMps:reported.stateM[3],vyMps:reported.stateM[4]};assumed.zM={value:reported.stateM[2],role:'SELF_REPORT_PRODUCER_HEIGHT_PRIOR'};assumed.vzMps={value:reported.stateM[5],role:'SELF_REPORT_PRODUCER_VERTICAL_VELOCITY_PRIOR'};}
 }
 const measuredFields=Object.keys(observed),sigmas=trackAFieldsA(p,['rangeSigmaM','azSigmaDeg','elSigmaDeg','radialVelSigmaMps','altitudeSigmaM','bearingSigmaDeg','elevationSigmaDeg','sigmaRad']);
 const uncertainty={providedSigmas:sigmas,cartesianCovarianceM2:trackAExactNumbersA(p.cartesianCovarianceM2,9),relativePositionVarianceM2:trackAExactNumbersA(p.positionVarianceM2,3),covarianceM2:trackAExactNumbersA(p.covarianceM2,9),covariance:trackAExactNumbersA(p.covariance,36),missingNoiseIsUnknown:true};
 const evidence=trackAFieldsA(p.domainEvidence,['surface','air','missile','background','candidateDomain']),features=trackAFieldsA(p.domainEvidence?.features,['heightM','significantDopplerMps','alongM','crossM','verticalStructure']);if(Object.keys(features).length)evidence.features=features;
 const provenance={...trackAFieldsA(c,['sourceId','sequence','senderShip','sourceTrackUid','sourceTrackNumber','independentObservation','retransmission']),...trackAFieldsA(p,['sourceId','sequence']),independence:'NOT_INFERRED_FROM_RECEIPT_OR_PACKET_SEQUENCE'};
 if(!Object.prototype.hasOwnProperty.call(provenance,'independentObservation'))provenance.independentObservation=null;
 const observerState={originM:{x:trackAWorldM_A(p.sensorXWorld),y:trackAWorldM_A(p.sensorYWorld),z:trackAFiniteA(p.sensorZM)},velocityMps:{x:trackAFiniteA(p.sensorVxMps),y:trackAFiniteA(p.sensorVyMps),z:trackAFiniteA(p.sensorVzMps)},missingComponentsRemainUnknown:true};
 return {schema:'AEGIS_MEASUREMENT_CONTRACT_TRACK_A_1',kind,sourceSensor,observerShip,measuredAtS,receivedAtS,measuredFields,measurementModel:{name,dimension:rows.length,physicalObservationDimension:physicalDimension,rows},observed,assumed,derived,reported,observerState,uncertainty,quality:trackAFiniteA(p.quality),qualityOrigin:trackAScalarA(c.qualityOrigin)??(kind==='OFFBOARD_PLOT'?'REPORTED_OR_RECEIVER_AGE_DERIVED':'SOURCE_PROVIDED_NOT_AUTHORITY'),domainEvidence:evidence,provenance};
}
function trackASafeStateA(v){
 if(!v||typeof v!=='object')return null;
 const q=trackAFieldsA(v,['trackId','trackNumber','sensorSource','sensorAge','sensorHits','confirmed','domain','classification','identity','threatStatus','engagementAuthority','memActive','trackLifecycle','ttl','_radar3dAirStepFC','_surface2DOnlyFC','_surfaceMotionPriorWip13B13','id','ownFireEvidence','protectedIdentity','cmsTrackId']);
 q.stateM=trackAExactNumbersA(v.stateM,6);q.covariance=trackAExactNumbersA(v.covariance,36);
 if(v.local)q.local=trackAFieldsA(v.local,['rxM','ryM','rzM','rvxMps','rvyMps','rvzMps','localHits','localAgeS','quality','valid']);return q;
}
function trackAStateA(tr){
 if(!tr)return null;
 const q=trackAFieldsA(tr,['trackId','trackNumber','sensorSource','sensorAge','sensorHits','confirmed','domain','classification','identity','threatStatus','engagementAuthority','memActive','trackLifecycle','ttl','_radar3dAirStepFC','_surface2DOnlyFC','_surfaceMotionPriorWip13B13']);
 q.stateM=trackANumbersA(tr._kfX,6);q.covariance=trackANumbersA(tr._kfP,36);
 if(tr.st){q.local=trackAFieldsA(tr.st,['rxM','ryM','rzM','rvxMps','rvyMps','rvzMps','localHits','localAgeS','quality','valid']);Object.assign(q,trackAFieldsA(tr,['id','ownFireEvidence','protectedIdentity','cmsTrackId','confirmed']));}
 return q;
}
function trackAKindA(p,source){if(source==='OFFBOARD_C')return 'OFFBOARD_PLOT';if(source==='VISUAL')return 'VISUAL_CARTESIAN';if((source??'').startsWith('BRIDGEMASTER_E')||(source??'').includes('_SURFACE'))return 'SURFACE_RADAR';return 'AIR_RADAR';}
function trackATraceEventA(type,payload,context={}){
 if(!TRACK_A_DIAG.enabled)return;
 try{
  const c=context,p=payload&&typeof payload==='object'?payload:{},record={serial:++TRACK_A_DIAG.serial,type,...trackAFieldsA(c,['route','observerShip','tick','timeS','trackId','mountId','decision','reason','nis','gate','distanceM','independentHit','nativeHitIncrement','finalSource','knownOwnLaunch','appliedModel','appliedDimension','gateUnits'])};
  if(Array.isArray(c.appliedFields))record.appliedFields=c.appliedFields.filter(v=>typeof v==='string').slice(0,8).map(v=>v.slice(0,40));
  if(c.kind){let measurementId=TRACK_A_DIAG.measurements.get(p);if(!measurementId){measurementId='M'+(++TRACK_A_DIAG.measurementSerial);TRACK_A_DIAG.measurements.set(p,measurementId);}record.measurementId=measurementId;record.measurement=trackANormalizeA(c.kind,p,c);}
  if(c.before)record.before=trackASafeStateA(c.before);if(c.after)record.after=trackASafeStateA(c.after);
  const safe=JSON.parse(JSON.stringify(record));
  TRACK_A_DIAG.ring[TRACK_A_DIAG.head]=safe;TRACK_A_DIAG.head=(TRACK_A_DIAG.head+1)%TRACK_A_DIAG.capacity;
  if(TRACK_A_DIAG.size<TRACK_A_DIAG.capacity)TRACK_A_DIAG.size++;else TRACK_A_DIAG.dropped++;
 }catch{TRACK_A_DIAG.errors++;} // Diagnostics can never abort or rescue a native decision.
}
function trackATraceContextA(kind,source,observerShip,meas=null){const now=simStepCounter*SIM_FIXED_DT,origin=meas&&TRACK_A_DIAG.origins.get(meas);return {kind,sourceSensor:source,observerShip:observerShip??null,tick:simStepCounter,timeS:now,measuredAtS:kind==='OFFBOARD_PLOT'?null:now,receivedAtS:now,...(origin??{})};}
window.__TRACK_A__=Object.freeze({
 schema:'AEGIS_TRACK_A_DIAGNOSTICS_1',normalize:trackANormalizeA,
 configure(options={}){if(typeof options.enabled==='boolean')TRACK_A_DIAG.enabled=options.enabled;if(Number.isFinite(options.capacity)){const next=Math.max(16,Math.min(4096,Math.floor(options.capacity)));if(next!==TRACK_A_DIAG.capacity){TRACK_A_DIAG.capacity=next;TRACK_A_DIAG.ring=[];TRACK_A_DIAG.head=TRACK_A_DIAG.size=0;}}return {enabled:TRACK_A_DIAG.enabled,capacity:TRACK_A_DIAG.capacity};},
 clear(){TRACK_A_DIAG.ring=[];TRACK_A_DIAG.head=TRACK_A_DIAG.size=TRACK_A_DIAG.serial=TRACK_A_DIAG.measurementSerial=TRACK_A_DIAG.dropped=TRACK_A_DIAG.errors=0;TRACK_A_DIAG.measurements=new WeakMap();TRACK_A_DIAG.origins=new WeakMap();},
 snapshot(){const records=[];for(let i=0;i<TRACK_A_DIAG.size;i++)records.push(TRACK_A_DIAG.ring[(TRACK_A_DIAG.head-TRACK_A_DIAG.size+i+TRACK_A_DIAG.capacity)%TRACK_A_DIAG.capacity]);return JSON.parse(JSON.stringify({schema:'AEGIS_TRACK_A_DIAGNOSTICS_1',enabled:TRACK_A_DIAG.enabled,capacity:TRACK_A_DIAG.capacity,records,stats:{recorded:TRACK_A_DIAG.serial,retained:TRACK_A_DIAG.size,dropped:TRACK_A_DIAG.dropped,errors:TRACK_A_DIAG.errors}}));}
});
