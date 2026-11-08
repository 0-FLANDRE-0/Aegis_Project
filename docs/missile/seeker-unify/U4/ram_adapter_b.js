// SEEKER_UNIFY_U4 Commit B — RAM Block 1A passive RF/IR common adapters.
// The physical front ends retain emitter/thermal truth, propagation, clutter,
// flare synthesis and each weapon owner's RNG.  Only an anonymous angular
// measurement crosses this boundary.
const SEEKER_U4_RAM_MODE_B='__MODE__';
const SEEKER_U4_RAM_PROFILE_B=Object.freeze({
  schema:'AEGIS_SEEKER_U4_RAM_PROFILE_B_1',family:'RAM_BLK1A',
  rf:Object.freeze({dimension:'PASSIVE_RF_2D',provenance:'LEGACY_EQUIVALENCE'}),
  ir:Object.freeze({dimension:'PASSIVE_IR_2D',provenance:'LEGACY_EQUIVALENCE'}),
  rngOwner:'WEAPON_OWNER_EXISTING_HANDLE',authorityOwner:'RAM_LOCAL_RUNTIME',
  emitterSignalOwnership:'EMITTER_PLATFORM_AND_PROPAGATION'
});
const SEEKER_U4_RAM_AUDIT_B={rfRoutes:0,irRoutes:0,ownerRoutes:0,playerRoutes:0,nullRoutes:0,
  truthFieldViolations:0,emitterComparisons:0,emitterOwnershipDifferences:0,maxEmitterDifference:0};
function seekerU4RamFiniteB(v,fallback=null){return v==null?fallback:(Number.isFinite(Number(v))?Number(v):fallback);}
function seekerU4RamTruthFreeB(value){
  if(!value||typeof value!=='object')return true;
  const forbidden=/(^|_)(entity|profile|faction|hostile|truth|debug|sourceId|targetId|physicalId|objectId)($|_)/i;
  return Object.entries(value).every(([key,v])=>!forbidden.test(key)&&seekerU4RamTruthFreeB(v));
}
function seekerU4RamMeasurementB(kind,value,origin='PLAYER'){
  if(!value)return null;
  const ir=kind==='IR',cfg=ir?RAM_BLK1A_SEEKER_MODEL.ir:RAM_BLK1A_SEEKER_MODEL.rf,
    snr=Math.max(.001,seekerU4RamFiniteB(value.snr,.001)),
    azSigmaDeg=(ir?cfg.baseAzSigmaDeg:cfg.azSigmaDeg)/Math.sqrt(Math.max(.25,snr)),
    elSigmaDeg=(ir?cfg.baseElSigmaDeg:cfg.elSigmaDeg)/Math.sqrt(Math.max(.25,snr)),
    azSigmaRad=azSigmaDeg*Math.PI/180,elSigmaRad=elSigmaDeg*Math.PI/180,
    dto=Object.freeze({schema:'AEGIS_SEEKER_MEASUREMENT_U4',dimension:ir?'PASSIVE_IR_2D':'PASSIVE_RF_2D',
      values:Object.freeze([seekerU4RamFiniteB(value.azRad,0),seekerU4RamFiniteB(value.elRad,0)]),
      covariance:Object.freeze([azSigmaRad*azSigmaRad,0,0,elSigmaRad*elSigmaRad]),
      quality:seekerU4RamFiniteB(value.quality,0),snr:seekerU4RamFiniteB(value.snr),
      signal:seekerU4RamFiniteB(value.signal),angularExtentRad:seekerU4RamFiniteB(value.extentRad,0),
      compositeCount:Math.max(1,Math.floor(seekerU4RamFiniteB(value.compositeCount,1))),
      elementIndex:ir?seekerU4RamFiniteB(value.elementIndex):null,
      scanPhaseRad:ir?seekerU4RamFiniteB(value.scanPhaseRad):null,
      observationOwner:origin==='OWNER'?'SHIP_OWNED_WEAPON':'PLAYER_WEAPON'});
  if(!seekerU4RamTruthFreeB(dto))SEEKER_U4_RAM_AUDIT_B.truthFieldViolations++;
  return dto;
}
function seekerU4RamRouteB(kind,origin,value){
  if(kind==='IR')SEEKER_U4_RAM_AUDIT_B.irRoutes++;else SEEKER_U4_RAM_AUDIT_B.rfRoutes++;
  if(origin==='OWNER')SEEKER_U4_RAM_AUDIT_B.ownerRoutes++;else SEEKER_U4_RAM_AUDIT_B.playerRoutes++;
  if(!value)SEEKER_U4_RAM_AUDIT_B.nullRoutes++;
  const common=seekerU4RamMeasurementB(kind,value,origin);
  return Object.freeze({schema:'AEGIS_SEEKER_U4_RAM_ROUTE_B_1',kind,origin,common,
    tacticalValue:value,tacticalOutputUsed:SEEKER_U4_RAM_MODE_B==='ACTIVE',rngConsumed:false,truthOutput:false});
}
// DEFECT_FIX: the former function fed the emitting missile's local tracker
// quality back into its physical transmitter strength.  Preserve the existing
// default signal (.65 + .55 * .75) while removing receiver/tracker ownership.
function seekerU4RamEmitterStrengthB(em){
  const phase=String(em?.phase??'').toUpperCase(),on=!!(em?.seekerOn||em?.radarOn||em?.seeker?.emitting||phase==='SEEKERON'||phase==='LOCKED'||phase==='TERMINAL');
  return on ? (.65+.55*.75) : 0;
}
function seekerU4RamCompareEmitterB(legacy,common){
  SEEKER_U4_RAM_AUDIT_B.emitterComparisons++;const d=Math.abs(legacy-common);
  SEEKER_U4_RAM_AUDIT_B.maxEmitterDifference=Math.max(SEEKER_U4_RAM_AUDIT_B.maxEmitterDifference,d);
  if(!Object.is(legacy,common))SEEKER_U4_RAM_AUDIT_B.emitterOwnershipDifferences++;
}
function seekerU4RamSnapshotB(){return Object.freeze({schema:'AEGIS_SEEKER_U4_RAM_SNAPSHOT_B_1',mode:SEEKER_U4_RAM_MODE_B,
  profile:SEEKER_U4_RAM_PROFILE_B,...SEEKER_U4_RAM_AUDIT_B,rngConsumedByCommonLayer:false,truthOutput:false,
  tacticalOutputUsed:SEEKER_U4_RAM_MODE_B==='ACTIVE',mutableTacticalSingleton:false});}
function seekerU4RamAuthorityMatrixB(){
  const track=(valid,quality=0,azRad=0)=>({valid,quality,azRad,elRad:0,azRate:0,elRate:0,measAgeS:valid?0:999}),
    make=()=>({_ramMemTrack:track(true,.7),_ramRfTrack:track(false),_ramIrTrack:track(false),_ramSeekerAuthority:'MEM',life:10}),
    step=(rm,count=80)=>{const timeline=[rm._ramSeekerAuthority];for(let i=0;i<count;i++){ramUpdateSeekerAuthority(rm,.02);const q=rm._ramSeekerAuthority;if(q!==timeline.at(-1))timeline.push(q);}return timeline;};
  const rf=make();rf._ramRfTrack=track(true,.95);const rfTimeline=step(rf);
  const ir=make();ir._ramIrTrack=track(true,.95);const irTimeline=step(ir);
  const both=make();both._ramRfTrack=track(true,.95);both._ramIrTrack=track(true,.95);const bothTimeline=step(both);
  both._ramIrTrack.valid=false;const irDropout=step(both,40);both._ramRfTrack.valid=false;const allDropout=step(both,60);
  const isolatedA=make(),isolatedB=make();isolatedA._ramRfTrack=track(true,.95);step(isolatedA);step(isolatedB);
  return Object.freeze({schema:'AEGIS_SEEKER_U4_RAM_AUTHORITY_MATRIX_B_1',rfTimeline,irTimeline,bothTimeline,irDropout,allDropout,
    isolation:{separateTracks:isolatedA._ramRfTrack!==isolatedB._ramRfTrack,a:isolatedA._ramSeekerAuthority,b:isolatedB._ramSeekerAuthority,
      switchA:isolatedA._ramSourceSwitchCount??0,switchB:isolatedB._ramSourceSwitchCount??0},
    pass:rfTimeline.includes('RF')&&irTimeline.includes('IR')&&bothTimeline.includes('RF')&&bothTimeline.includes('IR')&&
      irDropout.includes('RF')&&allDropout.includes('MEM')&&isolatedA._ramSeekerAuthority==='RF'&&isolatedB._ramSeekerAuthority==='MEM'});
}
window.__SEEKER_U4_B__=Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_B_1',mode:SEEKER_U4_RAM_MODE_B,profile:SEEKER_U4_RAM_PROFILE_B,
  adaptRf:(value,origin)=>seekerU4RamMeasurementB('RF',value,origin),adaptIr:(value,origin)=>seekerU4RamMeasurementB('IR',value,origin),
  route:(kind,origin,value)=>seekerU4RamRouteB(kind,origin,value),legacyEmitterStrength:em=>ramEmitterStrengthLegacyU4B(em),
  physicalEmitterStrength:seekerU4RamEmitterStrengthB,routedEmitterStrength:em=>ramEmitterStrength(em),snapshot:seekerU4RamSnapshotB,authorityMatrix:seekerU4RamAuthorityMatrixB,
  ownershipContract:()=>{const legacy=ramEmitterStrengthLegacyU4B.toString(),now=seekerU4RamEmitterStrengthB.toString();return Object.freeze({
    defectConfirmed:/trackQuality|_seekerQuality/.test(legacy),fixedPathIndependent:!/trackQuality|_seekerQuality/.test(now),
    authorityLocal:ramUpdateSeekerAuthority.toString().includes('_ramSeekerAuthority'),
    guidanceLocal:ramGuidanceFromEstimateB2.toString().includes('_ramRangeEstM')});}});
