// Native gate bodies run against detached observation/inventory inputs only.
// Native release checks must retain observed protection/BDA evidence even when
// a file is hidden by display policy. This detached whitelist is used only by
// the gate, never to draw a hidden contact or expose unobserved target data.
function mapDObservedHarpoonTrack(id){
 const t=tracks.get(Number(id));if(!t)return null;
 // Explicit observation/evidence whitelist. No entity/truth/object reference is copied.
 const keys=['trackId','trackUid','x','y','z','vx','vy','vz','classification','domain','classificationConfidence','classificationProbs','domainEvidence','confirmed','sensorDetected','sensorAge','sensorHits','sensorSource','memActive','reacquiring','_surfaceSensorContributorsWip13B9','_surfaceManeuverProbabilityWip13B10','_maneuverProbability','_surfaceExtentWip13B8','_surfaceExtentEstimateWip13B8','measurementSigmaM','kinematicQuality','lastUpdateSeen','ttl','isASM','_surfaceContributorsWip13B9','_surfaceMotionPriorWip13B1','_surfaceExtentWip13B1','_surfaceMotionWip13B1','trackQuality','fireControlQuality','rangeSigma','rangeSigmaM','posSigmaM','velSigmaMps','altSigmaM','azSigma','zSigma','confidence','identity','_operatorIdentity','threatStatus','engagementAuthority','_a3AuthorityReason','_a3StateRevision','_a3StateChangedStep','_lastMeasurementStep','_spyExpectedRevisitS','_lastPredictionStep','_kfStep','_kfX','_kfP','_harpoonOwnC','iffF','observationReportsC','surfaceContributorsWip13B9','surfaceMotionPriorWip13C','surfaceExtent','extent','targetSupport','bdaEvidence','identificationEvidence'];
 const out={};for(const k of keys)if(t[k]!==undefined)out[k]=structuredClone(t[k]);out._wip11cObservedSeaImpact=!!t._wip11cObservedSeaImpact;out.trackId=Number(id);return out;
}
function mapDHarpoonPreview(trackId,options={},observed=mapDObservedHarpoonTrack(trackId)){
 const r=structuredClone(ACTIVE_SHIP_RUNTIME.weapons.harpoon),tracks=new Map(observed?[[Number(trackId),structuredClone(observed)]]:[]),selectedLockId=Number(trackId);
 const harpoonRuntimeA=()=>r;
 // Same canonical transform as shipGameFrameV1, without its shared WeakMap cache.
 const shipGameFrameV1=()=>createShipBodyFrameV1(floodAttitudePreviewV1.snapshot(),{x:worldToMeters(aircraft.x()),y:worldToMeters(aircraft.y()),z:OWN_ALT_M},shipNav.heading);
 /* MAP_D_NATIVE_GATE_COPIES */
 try{return harpoonAutoTubeGateD(trackId,{mode:engagementControlMode,...options});}
 catch(e){return {ok:false,reason:'PREVIEW_UNAVAILABLE',detail:String(e),truthUsed:false};}
}
function mapDHarpoonSetSearchPoint(xM,yM){return window.__MAP_D__.appendSearchPoint(xM,yM);}
