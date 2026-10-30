// HELI_D / stage B: anonymous AN/APS-153-like surface-search measurements.
// Band, power scale, range, scan law and errors are assumptions, never hardware claims.
const HELO_RADAR_SPEC_E=Object.freeze(Object.fromEntries(Object.entries({
  band:['X','SIM_TUNED'],periodS:[6,'SIM_TUNED'],maxRangeM:[100000,'SIM_TUNED'],minRangeM:[400,'SIM_TUNED'],
  targetMastHeightM:[30,'SIM_TUNED'],surfaceReferenceZM:[8,'SIM_TUNED'],
  snrReferenceRangeKm:[32,'SIM_TUNED'],snrReferenceRcsM2:[20,'SIM_TUNED'],transmitScale01:[1,'SIM_TUNED'],
  rangeSigmaM:[18,'SIM_TUNED'],azSigmaDeg:[.12,'SIM_TUNED'],surfaceZSigmaM:[8,'SIM_TUNED'],navigationSigmaM:[3,'SIM_TUNED'],
  rangeResolutionM:[30,'SIM_TUNED'],elevationHalfCoverageDeg:[90,'SIM_TUNED'],elSigmaDeg:[.02,'SIM_TUNED'],dopplerSigmaMps:[1.5,'SIM_TUNED'],horizonFadeBandKm:[1.2,'SIM_TUNED'],seaAzimuthCells:[3,'SIM_TUNED'],seaRangeCells:[6,'SIM_TUNED'],receiverNoiseNorm:[1,'SIM_TUNED'],clutterLeak01:[.00001,'SIM_TUNED'],
  surfaceSeaPenalty:[.34,'SIM_TUNED'],surfaceRainPenalty:[.12,'SIM_TUNED'],surfaceSeaFloor:[.42,'SIM_TUNED'],
  downlookSeaPenalty:[.28,'SIM_TUNED'],downlookRainPenalty:[.10,'SIM_TUNED'],downlookSeaFloor:[.55,'SIM_TUNED'],
  maxPlotsPerStep:[32,'SIM_TUNED'],attemptHistoryRevolutions:[3,'SIM_TUNED'],
  surfaceEvidenceFloor:[.78,'SIM_TUNED'],airEvidenceCeiling:[.12,'SIM_TUNED'],missileEvidenceCeiling:[.08,'SIM_TUNED']
}).map(([k,[value,source]])=>[k,Object.freeze({value,source,reference:'APS153_SURFACE_MODE_SIMULATION_ASSUMPTION'})])));
const HELO_RADAR_VALUES_E=Object.freeze(Object.fromEntries(Object.entries(HELO_RADAR_SPEC_E).map(([k,v])=>[k,v.value])));
function heloRadarNewStateE(h){return {angleRad:0,turn:0,attempts:0,plots:0,lastPlotAtS:null,lastSweepAtS:null,
  rng:{state:rfSeedWip13A2('HELO_APS153_E:'+BATTLESPACE_SEED+':'+h.id),spare:null},attempted:new Map(),stepPlots:[],emitting:false,
  stats:{surfaceAccepted:0,airRejected:0,backgroundRejected:0,horizonRejected:0,duplicateRejected:0,scene:0,surfaceAttempts:0,lastEchoSnr:null,lastEchoPd:null}};}
function heloRadarStateE(h){const sensor=heloSensorStateE(h);return sensor.radar??(sensor.radar=heloRadarNewStateE(h));}
function heloRadarSnapshotE(h){
  // Read-only: rendering and UI snapshots never allocate authoritative state.
  const C=HELO_RADAR_VALUES_E,q=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id)?.radar;
  return {radar:{enabled:h.radarOn===true,emitting:q?.emitting===true,azimuthRad:q?.angleRad??0,periodS:C.periodS,turn:q?.turn??0,
    attempts:q?.attempts??0,plots:q?.plots??0,lastPlotAtS:q?.lastPlotAtS??null,lastSweepAtS:q?.lastSweepAtS??null,
    maxRangeM:C.maxRangeM,horizonM:radarHorizonKm(Math.max(0,h.positionM.z),C.targetMastHeightM)*1000,targetMastHeightM:C.targetMastHeightM,surfaceOnly:true}};
}
function heloRadarPlotsE(h){const q=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id)?.radar;return q?.stepPlots?JSON.parse(JSON.stringify(q.stepPlots)):[];}
function heloRadarSeaCalibrationE(env){
  // Reuse the SPQ surface-mode sea-state/rain factors, with independent APS tuning.
  const C=HELO_RADAR_VALUES_E,sea=clamp(Number(env?.wave?.seaState01)||0,0,1),rain=clamp(Number(env?.precipitation01)||0,0,1);
  return clamp(1-C.surfaceSeaPenalty*sea-C.surfaceRainPenalty*rain,C.surfaceSeaFloor,1)*clamp(1-C.downlookSeaPenalty*sea-C.downlookRainPenalty*rain,C.downlookSeaFloor,1);
}
function heloRadarSurfaceMeasurementE(h,echo,evidence,rng){
  // Input is anonymous RF observables only. No reflector or truth object enters here.
  const C=HELO_RADAR_VALUES_E,z=C.surfaceReferenceZM,dz=h.positionM.z-z,slant=Number(echo.rangeM),horizontalSquared=slant*slant-dz*dz;
  if(!Number.isFinite(horizontalSquared)||horizontalSquared<C.minRangeM*C.minRangeM)return null;
  const horizontal=Math.sqrt(horizontalSquared),az=Number(echo.azRad),c=Math.cos(az),s=Math.sin(az),rangeSigmaM=Math.max(C.rangeSigmaM,Number(echo.rangeSigmaM)||C.rangeSigmaM)*slant/Math.max(C.minRangeM,horizontal),azSigmaRad=deg(Math.max(C.azSigmaDeg,Number(echo.azSigmaDeg)||C.azSigmaDeg)),rr=rangeSigmaM*rangeSigmaM,tt=(horizontal*azSigmaRad)**2,nn=C.navigationSigmaM*C.navigationSigmaM,xy=(rr-tt)*c*s;
  const positionM={x:h.positionM.x+horizontal*c+observerNormalC(rng)*C.navigationSigmaM,y:h.positionM.y+horizontal*s+observerNormalC(rng)*C.navigationSigmaM,z},covarianceM2=[rr*c*c+tt*s*s+nn,xy,0,xy,rr*s*s+tt*c*c+nn,0,0,0,C.surfaceZSigmaM*C.surfaceZSigmaM+nn];
  return {positionM,covarianceM2,domainEvidence:{surface:clamp(Math.max(C.surfaceEvidenceFloor,Number(evidence.surface)||0),0,1),air:clamp(Number(evidence.air)||0,0,C.airEvidenceCeiling),missile:clamp(Number(evidence.missile)||0,0,C.missileEvidenceCeiling),background:clamp(Number(evidence.background)||0,0,1)},measuredAtS:simStepCounter*SIM_FIXED_DT};
}
function heloRadarPhysicalGateE(h,q,previousAngle,angle,turn){
  const C=HELO_RADAR_VALUES_E;
  // Physical-only gate is called inside RF synthesis. Private keys never become measurements.
  return (ref,g)=>{
    if(g.horizontalRangeM<C.minRangeM||!anglePassedDuringPositiveSweep(previousAngle,angle,g.azRad))return false;
    const surface=['SHIP','NAVAL_SHIP','SURFACE_TARGET','SURFACE_CONTACT'].includes(ref._physicsKind),propagationHeightM=surface?C.targetMastHeightM:Number(ref.z)||0;
    if(g.horizontalRangeM>radarHorizonKm(h.positionM.z,propagationHeightM)*1000){q.stats.horizonRejected++;return false;}
    // Crossing just past the 0deg wrap belongs to the new revolution, whereas the
    // last negative-bearing crossing belongs to the completed one.
    const positiveBearing=((g.azRad%TAU)+TAU)%TAU,crossedTurn=turn+(angle<previousAngle&&positiveBearing<=angle+1e-12?1:0),key=ref.rfId;
    if(q.attempted.get(key)===crossedTurn){q.stats.duplicateRejected++;return false;}
    q.attempted.set(key,crossedTurn);q.attempts++;if(surface)q.stats.surfaceAttempts++;
    return {propagationHeightM,azimuthPeakGain:true};
  };
}
function heloRadarCollectE(h,q,previousAngle,angle,turn){
  const C=HELO_RADAR_VALUES_E,rx={x:metersToWorld(h.positionM.x),y:metersToWorld(h.positionM.y),z:h.positionM.z,vxMps:h.groundVelocityMps.x,vyMps:h.groundVelocityMps.y,vzMps:h.groundVelocityMps.z},sweep=_ccwDelta(previousAngle,angle),beamAz=angNorm(previousAngle+sweep*.5),beamHalfAzRad=sweep*.5+1e-9,environment=maritimeEnvironmentSnapshotWip13A3();
  const dwell=shipboardRadarEchoFieldWip13B13({radarId:'HELO_APS153',band:C.band,receiver:rx,observerShipId:'HELO:'+h.id,rngState:q.rng,beamAz,beamEl:0,beamHalfAzRad,beamHalfElRad:deg(C.elevationHalfCoverageDeg),
    maxRangeKm:C.maxRangeM/1000,minRangeM:C.minRangeM,rangeResolutionM:C.rangeResolutionM,seaAzimuthCells:C.seaAzimuthCells,seaRangeCells:C.seaRangeCells,maxDistributedEchoes:0,health:1,
    snrReferenceRangeKm:C.snrReferenceRangeKm,snrReferenceRcsM2:C.snrReferenceRcsM2,receiverNoiseNorm:C.receiverNoiseNorm,clutterLeak01:C.clutterLeak01,pdHalfSnr:1,
    rangeSigmaM:C.rangeSigmaM,azSigmaDeg:C.azSigmaDeg,elSigmaDeg:C.elSigmaDeg,dopplerSigmaMps:C.dopplerSigmaMps,losMarginM:C.horizonFadeBandKm,includeSea:true,signalScale01:C.transmitScale01*heloRadarSeaCalibrationE(environment),physicalEchoGate:heloRadarPhysicalGateE(h,q,previousAngle,angle,turn)});
  q.stats.scene=dwell.sceneCount;const out=[];
  for(const echo of dwell.echoes){
    q.stats.lastEchoSnr=echo.snr;q.stats.lastEchoPd=echo.pd;
    const evidence=shipboardRadarDomainEvidenceWip13B13(echo,{elevationObservable:true,surfaceBiased:true});
    if(evidence.candidateDomain==='BACKGROUND'){q.stats.backgroundRejected++;continue;}
    if(!shipboardRadarSurfaceDiscreteEvidenceWip13B13(evidence)){q.stats.airRejected++;continue;}
    const plot=heloRadarSurfaceMeasurementE(h,echo,evidence,q.rng);if(!plot)continue;
    q.stats.surfaceAccepted++;out.push(plot);if(out.length>=C.maxPlotsPerStep)break;
  }
  return out;
}
function heloRadarFixedStepE(dt){
  const C=HELO_RADAR_VALUES_E,now=simStepCounter*SIM_FIXED_DT;
  for(const h of ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[]){
    const existing=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id)?.radar;
    if(!h.radarOn&&!existing)continue;
    const q=heloRadarStateE(h);q.stepPlots=[];q.emitting=heloAirborneE(h)&&h.radarOn===true;
    if(!q.emitting){heloPublishRadarPlotsE(h,[]);continue;}
    const prev=q.angleRad,turn=q.turn,total=prev+TAU*dt/C.periodS,next=((total%TAU)+TAU)%TAU,wrapped=next<prev;
    q.stepPlots=heloRadarCollectE(h,q,prev,next,turn);q.angleRad=next;
    if(wrapped){q.turn++;q.lastSweepAtS=now;for(const [key,rev]of q.attempted)if(rev<q.turn-C.attemptHistoryRevolutions)q.attempted.delete(key);}
    q.plots+=q.stepPlots.length;if(q.stepPlots.length)q.lastPlotAtS=now;
    heloPublishRadarPlotsE(h,q.stepPlots);
  }
}
function heloRadarAuditE(){
  return {schema:'AEGIS_HELO_RADAR_STAGE_B_E1',diagnosticOnly:true,constants:JSON.parse(JSON.stringify(HELO_RADAR_SPEC_E)),aircraft:[...(ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[])].map(h=>{const q=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id)?.radar;return {id:h.id,...heloRadarSnapshotE(h),statistics:q?{...q.stats,rngState:q.rng.state,rngSpare:q.rng.spare}:null,lastPlots:heloRadarPlotsE(h)};})};
}
// DIAGNOSTIC_ONLY: native RF probes use detached scan/RNG state and the real
// canonical helicopter pose/world. No plots are injected into a combat-system file.
function heloRadarNativeProbeE(options={}){
  const h=ENGAGEMENT_RUNTIME.world.entities.helicopters?.get(options.id);if(!h)return {ok:false,reason:'HELO_REQUIRED'};
  const repeat=options.repeat??1,sweeps=options.sweeps??Array.from({length:repeat},()=>({previousAngleRad:options.previousAngleRad,newAngleRad:options.newAngleRad,turn:0}));
  if(!Number.isInteger(repeat)||repeat<1||repeat>4||!Array.isArray(sweeps)||sweeps.length<1||sweeps.length>4||sweeps.some(s=>!Number.isFinite(s.previousAngleRad)||!Number.isFinite(s.newAngleRad)||s.previousAngleRad<0||s.newAngleRad<0||s.previousAngleRad>=TAU||s.newAngleRad>=TAU||!Number.isInteger(s.turn)||s.turn<0||s.turn>1000000||['offsetXM','offsetYM'].some(k=>s[k]!=null&&(!Number.isFinite(s[k])||Math.abs(s[k])>1000))))return {ok:false,reason:'INVALID_SWEEP'};
  const q=heloRadarNewStateE(h);if(Number.isInteger(options.seed))q.rng.state=options.seed>>>0||1;const batches=[];
  for(const sweep of sweeps){const before=q.attempts,surfaceBefore=q.stats.surfaceAttempts,receiver={...h,positionM:{x:h.positionM.x+(sweep.offsetXM??0),y:h.positionM.y+(sweep.offsetYM??0),z:h.positionM.z}},plots=heloRadarCollectE(receiver,q,sweep.previousAngleRad,sweep.newAngleRad,sweep.turn);batches.push({attempts:q.attempts-before,surfaceAttempts:q.stats.surfaceAttempts-surfaceBefore,plots});}
  return {ok:true,batches,statistics:{...q.stats},rngState:q.rng.state};
}
function heloRadarMeasurementProbeE(options={}){
  const h=ENGAGEMENT_RUNTIME.world.entities.helicopters?.get(options.id);if(!h)return {ok:false,reason:'HELO_REQUIRED'};
  const echo=options.echo;if(!echo||!['rangeM','azRad','rangeSigmaM','azSigmaDeg'].every(k=>Number.isFinite(echo[k])))return {ok:false,reason:'ANONYMOUS_MEASUREMENT_REQUIRED'};
  const rng={state:(Number(options.seed)>>>0)||1,spare:null};return {ok:true,plot:heloRadarSurfaceMeasurementE(h,echo,{surface:.85,air:.1,missile:.05,background:.02},rng)};
}
window.__HELO_SENSOR_STAGE_B_E__=Object.freeze({snapshot:heloRadarAuditE,nativeProbe:heloRadarNativeProbeE,measurementProbe:heloRadarMeasurementProbeE});
