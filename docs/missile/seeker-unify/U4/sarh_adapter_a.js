// SEEKER_UNIFY_U4 Commit A — explicit bistatic SARH common observation adapter.
// The physical front-end still owns SPG allocation/emission, two LOS paths,
// two beams, RCS, clutter and the weapon-local RNG.  This layer consumes the
// resulting anonymous observables and never exposes truth/debug identifiers.
const SEEKER_U4_SARH_MODE_A='__MODE__';
const SEEKER_U4_SARH_PROFILE_A=Object.freeze({
  schema:'AEGIS_SEEKER_U4_SARH_PROFILE_A_1',family:'SARH_BISTATIC',dimension:'SARH_BISTATIC_4D',
  provenance:'LEGACY_EQUIVALENCE',units:Object.freeze({distance:'m',angle:'rad',velocity:'m/s',covariance:'SI_squared'}),
  propagation:'TX_TARGET_PLUS_TARGET_RX',requiresIllumination:true,requiresTxLos:true,requiresRxLos:true,
  requiresTxBeam:true,requiresRxBeam:true,rngOwner:'WEAPON_LOCAL_EXISTING_HANDLE'
});
const SEEKER_U4_SARH_AUDIT_A={echoRoutes:0,cellRoutes:0,measurementRoutes:0,packetRoutes:0,powerComparisons:0,powerMismatches:0,
  unresolvedComparisons:0,unresolvedMismatches:0,invalidCommonEchoes:0,truthFieldViolations:0,maxAbsPowerDifference:0};
function seekerU4SarhFiniteA(v,fallback=null){return v==null?fallback:(Number.isFinite(Number(v))?Number(v):fallback);}
function seekerU4SarhTruthFreeKeysA(value){
  if(!value||typeof value!=='object')return true;
  const forbidden=/(^|_)(entity|profile|faction|hostile|truth|debugSource|sourceId|targetId|physicalId|truthPosition)($|_)/i;
  return Object.keys(value).every(key=>!forbidden.test(key));
}
function seekerU4SarhEchoA(echo,index=0){
  const txRangeM=seekerU4SarhFiniteA(echo?.txRangeM),rxRangeM=seekerU4SarhFiniteA(echo?.rxRangeM??echo?.rangeM),
    txLosQ=seekerU4SarhFiniteA(echo?.txLosQ),rxLosQ=seekerU4SarhFiniteA(echo?.rxLosQ),
    txBeamGain=seekerU4SarhFiniteA((echo?.txBeamGain??1)*(echo?.mountGain??1)),rxBeamGain=seekerU4SarhFiniteA(echo?.rxBeamGain),
    pathRateMps=seekerU4SarhFiniteA(echo?.dopplerPathRateMps),valid=[txRangeM,rxRangeM,txLosQ,rxLosQ,txBeamGain,rxBeamGain,pathRateMps].every(Number.isFinite)&&txLosQ>0&&rxLosQ>0&&txBeamGain>0&&rxBeamGain>0;
  const dto=Object.freeze({schema:'AEGIS_SEEKER_ECHO_SAMPLE_U4',dimension:'SARH_BISTATIC_4D',anonymousEchoKey:`SARH:${index}`,valid,
    pathRangeM:valid?txRangeM+rxRangeM:null,receiverRangeM:rxRangeM,azRad:seekerU4SarhFiniteA(echo?.azRad),elRad:seekerU4SarhFiniteA(echo?.elRad),pathRateMps,
    receivedPower:seekerU4SarhFiniteA(echo?.receivedPowerNorm),snr:seekerU4SarhFiniteA(echo?.snr),apparentRcsM2:seekerU4SarhFiniteA(echo?.rcsM2),
    txLeg:Object.freeze({rangeM:txRangeM,losQ:txLosQ,beamGain:txBeamGain}),rxLeg:Object.freeze({rangeM:rxRangeM,losQ:rxLosQ,beamGain:rxBeamGain}),
    rangeExtentM:seekerU4SarhFiniteA(echo?.rangeExtentM,0),crossExtentM:seekerU4SarhFiniteA(echo?.crossExtentM,0),
    verticalExtentM:seekerU4SarhFiniteA(echo?.verticalExtentM,0),dopplerSpreadMps:seekerU4SarhFiniteA(echo?.dopplerSpreadMps,0),
    environment:Object.freeze({clutterQ:seekerU4SarhFiniteA(echo?.clutterQ),multipathQ:seekerU4SarhFiniteA(echo?.multipathQ),weatherQ:seekerU4SarhFiniteA(echo?.weatherQ)})});
  if(!valid)SEEKER_U4_SARH_AUDIT_A.invalidCommonEchoes++;
  if(!seekerU4SarhTruthFreeKeysA(dto))SEEKER_U4_SARH_AUDIT_A.truthFieldViolations++;
  return dto;
}
function seekerU4SarhCellA(cluster,index=0){
  const members=Object.freeze(Array.from(cluster??[],(echo,i)=>seekerU4SarhEchoA(echo,i))),valid=members.length>0&&members.every(q=>q.valid),
    dto=Object.freeze({schema:'AEGIS_SEEKER_RESOLVED_CELL_U4',dimension:'SARH_BISTATIC_4D',anonymousCellKey:`SARH_CELL:${index}`,valid,members,memberCount:members.length});
  if(!seekerU4SarhTruthFreeKeysA(dto))SEEKER_U4_SARH_AUDIT_A.truthFieldViolations++;
  return dto;
}
function seekerU4SarhMeasurementA(measurement){
  if(!measurement)return null;
  const sig=[seekerU4SarhFiniteA(measurement.rangeSigmaM,0),deg(seekerU4SarhFiniteA(measurement.azSigmaDeg,0)),deg(seekerU4SarhFiniteA(measurement.elSigmaDeg,0)),seekerU4SarhFiniteA(measurement.dopplerSigmaMps,0)],covariance=new Array(16).fill(0);
  for(let i=0;i<4;i++)covariance[i*4+i]=sig[i]*sig[i];
  const dto=Object.freeze({schema:'AEGIS_SEEKER_MEASUREMENT_U4',dimension:'SARH_BISTATIC_4D',
    values:Object.freeze([seekerU4SarhFiniteA(measurement.rangeM,0),seekerU4SarhFiniteA(measurement.azRad,0),seekerU4SarhFiniteA(measurement.elRad,0),seekerU4SarhFiniteA(measurement.dopplerPathRateMps,0)]),
    covariance:Object.freeze(covariance),snr:seekerU4SarhFiniteA(measurement.snr),quality:seekerU4SarhFiniteA(measurement.pd)});
  if(!seekerU4SarhTruthFreeKeysA(dto))SEEKER_U4_SARH_AUDIT_A.truthFieldViolations++;
  return dto;
}
function seekerU4SarhRouteA(kind,value){
  let common=null;
  if(kind==='ECHOES'){SEEKER_U4_SARH_AUDIT_A.echoRoutes++;common=Object.freeze(Array.from(value??[],seekerU4SarhEchoA));}
  else if(kind==='CELLS'){SEEKER_U4_SARH_AUDIT_A.cellRoutes++;common=Object.freeze(Array.from(value??[],seekerU4SarhCellA));}
  else if(kind==='MEASUREMENT'){SEEKER_U4_SARH_AUDIT_A.measurementRoutes++;common=seekerU4SarhMeasurementA(value);}
  else if(kind==='PACKET'){SEEKER_U4_SARH_AUDIT_A.packetRoutes++;common=Object.freeze({schema:'AEGIS_SEEKER_SARH_PACKET_U4',
      echoes:Object.freeze(Array.from(value?.echoes??[],seekerU4SarhEchoA)),cells:Object.freeze(Array.from(value?.clusters??[],seekerU4SarhCellA)),
      measurements:Object.freeze(Array.from(value?.measurements??[],seekerU4SarhMeasurementA)),txStatePresent:!!value?.tx,rxStatePresent:!!value?.rx});}
  return Object.freeze({schema:'AEGIS_SEEKER_U4_ROUTE_A_1',kind,common,tacticalValue:value,tacticalOutputUsed:SEEKER_U4_SARH_MODE_A==='ACTIVE',rngConsumed:false,truthOutput:false});
}
function seekerU4SarhBistaticPowerA(rcsM2,txRangeKm,rxRangeKm,txGain=1,rxGain=1,txLosQ=1,rxLosQ=1,envQ=1){
  const p=SAM_SARH_RF_PROFILE;return Math.max(0,rcsM2)/Math.max(1e-9,p.referenceRcsM2)
    *Math.pow(p.referenceTxRangeKm/Math.max(.25,txRangeKm),2)*Math.pow(p.referenceRxRangeKm/Math.max(.25,rxRangeKm),2)
    *Math.max(0,txGain)*Math.max(0,rxGain)*Math.max(0,txLosQ)*Math.max(0,rxLosQ)*Math.max(0,envQ);
}
function seekerU4SarhComparePowerA(legacy,common){SEEKER_U4_SARH_AUDIT_A.powerComparisons++;const d=Math.abs(legacy-common);SEEKER_U4_SARH_AUDIT_A.maxAbsPowerDifference=Math.max(SEEKER_U4_SARH_AUDIT_A.maxAbsPowerDifference,d);if(!Object.is(legacy,common))SEEKER_U4_SARH_AUDIT_A.powerMismatches++;}
function seekerU4SarhUnresolvedA(a,b){
  const p=SAM_SARH_RF_PROFILE,dr=Math.abs(a.rangeM-b.rangeM),da=_sarhAngularSeparation({az:a.azRad,el:a.elRad},{az:b.azRad,el:b.elRad}),dv=Math.abs(a.dopplerPathRateMps-b.dopplerPathRateMps),
    rAllow=p.unresolvedRangeM+.18*((a.rangeExtentM??0)+(b.rangeExtentM??0)),aAllow=deg(p.unresolvedAngleDeg)+.20*((a.angularExtentRad??0)+(b.angularExtentRad??0)),dAllow=p.unresolvedDopplerMps+.35*((a.dopplerSpreadMps??0)+(b.dopplerSpreadMps??0));
  return dr<=rAllow&&da<=aAllow&&dv<=dAllow;
}
function seekerU4SarhCompareUnresolvedA(legacy,common){SEEKER_U4_SARH_AUDIT_A.unresolvedComparisons++;if(legacy!==common)SEEKER_U4_SARH_AUDIT_A.unresolvedMismatches++;}
function seekerU4SarhSnapshotA(){return Object.freeze({schema:'AEGIS_SEEKER_U4_SARH_SNAPSHOT_A_1',mode:SEEKER_U4_SARH_MODE_A,profile:SEEKER_U4_SARH_PROFILE_A,...SEEKER_U4_SARH_AUDIT_A,
  rngConsumedByCommonLayer:false,truthOutput:false,tacticalOutputUsed:SEEKER_U4_SARH_MODE_A==='ACTIVE',mutableTacticalSingleton:false});}
window.__SEEKER_U4_A__=Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_A_1',mode:SEEKER_U4_SARH_MODE_A,profile:SEEKER_U4_SARH_PROFILE_A,
  adaptEcho:seekerU4SarhEchoA,adaptCell:seekerU4SarhCellA,adaptMeasurement:seekerU4SarhMeasurementA,bistaticPower:seekerU4SarhBistaticPowerA,
  legacyBistaticPower:(...args)=>_sarhNormalizedBistaticPowerLegacyU4A(...args),routedBistaticPower:(...args)=>_sarhNormalizedBistaticPower(...args),
  unresolved:seekerU4SarhUnresolvedA,legacyUnresolved:(a,b)=>_sarhEchoesUnresolvedLegacyU4A(a,b),routedUnresolved:(a,b)=>_sarhEchoesUnresolved(a,b),snapshot:seekerU4SarhSnapshotA,
  sourceContract:()=>{const s=buildNavalSarhEchoPoolLegacyU4A.toString(),a=_v1SelectGuidanceSource.toString(),c=_v1SourceArbiterConfig.toString();return Object.freeze({illumination:s.includes('m.sarhAlive!==true')&&s.includes('spg62ServoMount(ill.id)?.emitting')&&s.includes('SPG62_ENGAGEMENT_STATE'),emcon:s.includes('emconActive'),twoLos:s.includes('txLosQ')&&s.includes('rxLosQ'),twoBeams:s.includes('txBeam')&&s.includes('rxBeam'),sourceArbiter:c.includes('DUAL_MODE_ARH_SARH')&&c.includes('GUIDANCE_SOURCE_ARBITER_V1.SARH')&&a.includes('cfg.priority')});}});
