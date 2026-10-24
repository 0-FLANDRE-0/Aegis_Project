const fs=require('fs'),path=require('path');
const {H,R,unpack,baseline,mainScope,sha}=require('./source.cjs');
const {definitions}=require('./patches.cjs');
const D=path.join(R,'docs/envelope/D'),input=JSON.parse(fs.readFileSync(path.join(D,'inputs.json')));
const symbols=mainScope(unpack(baseline())).symbols;
const native=fs.readFileSync(path.join(D,'diagnostic/native-engine.js'),'utf8'),originalPrivate=fs.readFileSync(path.join(D,'diagnostic/private.js'),'utf8');
const hooks=fs.readFileSync(path.join(H,'hooks.js'),'utf8');
let privateSource=originalPrivate.replace('q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);','q._kfP=new Float64Array(36);q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);').replace('const samples=[],phases=[];let lastPhase',"diagCaseA={fuze:[],phases:[],passes:[],maxDemand:null,lastRange:null,lastSlope:0,lastPhase:''};\n const samples=[],phases=[];let lastPhase");
privateSource=privateSource.replace('simStepCounter++;apogeeM=', 'diagStepA(m,t);\n  simStepCounter++;apogeeM=');
privateSource=privateSource.replace('targetAltitudeM:t.z,phase:phase()', 'targetAltitudeM:t.z,phase:phase(),telemetry:diagTelemetryA(m)');
privateSource=privateSource.replace('batteryRemainingS:m._gameBatteryRemainingS??null};',"batteryRemainingS:m._gameBatteryRemainingS??null,diagnostic:diagCaseA,termFinal:m._gameFlightTerm?{...m._gameFlightTerm}:null,fuzeState:Object.fromEntries(Object.entries(m).filter(([k])=>k.startsWith('_fuze')&&k!=='_fuzeOpportunityRngA'&&k!=='_fuzeSignalChannelsA')),opportunityDraws:m._fuzeOpportunityRngA?.draws??0,nativeCpa:{timeS:m.cpaTimeS??null,distanceM:m.cpaDistM??null,altM:m.cpaAltM??null,targetAltM:m.cpaTgtAltM??null,speedMps:m.cpaMslSpeedMps??null,availableG:m.cpaAvailableG??null,commandG:m.cpaCommandG??null,t2AvailableG:m.t2AvailableG??null,t2CommandG:m.t2CommandG??null,t2AltM:m.t2AltM??null,t2SpeedMps:m.t2SpeedMps??null}};");
privateSource=privateSource.replace('return {runCase,profiles:',`return {runCase,unit:{draw:_wip99FuzeDetectionDraw,info:_wip99FuzeDetectionInfo,candidate:_wip99Stage2CandidateDecision,ownState:samNavB1OwnState,signal:typeof samFuzeSignalSweepA==='function'?samFuzeSignalSweepA:null,signalPower:typeof samFuzeSignalPowerA==='function'?samFuzeSignalPowerA:null,signalSpec:typeof SAM_FUZE_SIGNAL_SPEC_A==='object'?SAM_FUZE_SIGNAL_SPEC_A:null,clutter:_wip99SeaClutterFalseTrigger,zem:computeZEMCorrectionV1,autopilot:applyAccelCommandToAutopilotV1,terminate:gameFlightTerminationEvaluateV48,banDetectionDraw(){_wip99FuzeDetectionDraw=function(){throw Error('SAM_DETECTION_RNG_FORBIDDEN');};},setNavigationSeed(s){SIM_SEED_BASE=s>>>0;},globalRng(){return SIM_RNG_STATE>>>0;},consumeGlobalRng(){return simRandom();},worldUnitsPerKm:WORLD_UNITS_PER_KM,profile:SAM_MISSILE_PROFILES.SM2MR_BLKIIIA_SIM},profiles:`);
if(privateSource===originalPrivate)throw Error('NO_MEASUREMENT_INSTRUMENTATION');
const sourceCache=new Map();
function sourceFor(variant='BASE'){
 if(sourceCache.has(variant))return sourceCache.get(variant);
 const p=definitions(symbols,variant);let s=native;
 for(const [name,code]of Object.entries(p.out)){const old=symbols.get(name).code;if(s.split(old).length!==2){if(name==='surfaceMissileSweptContactWip13C5'&&native.includes(require(path.join(D,'diagnostic/boundaries.json'))[name].code))continue;throw Error('NATIVE_COPY_MISMATCH:'+name);}s=s.replace(old,code);}
 const source=p.constants.join('\n')+'\n'+s+'\n'+hooks+'\n'+privateSource;
 const out={source,hash:sha(source),patches:Object.keys(p.out),functionHashes:Object.fromEntries(Object.entries(p.out).map(([k,v])=>[k,sha(v)]))};sourceCache.set(variant,out);return out;
}
function create(variant='BASE',environment={}){let {source}=sourceFor(variant);if(Number.isFinite(environment.seaStateFactor)){const b=require(path.join(D,'diagnostic/boundaries.json')).seaStateFactor.code;if(!source.includes(b))throw Error('SEA_BOUNDARY_MISSING');source=source.replace(b,'const seaStateFactor='+JSON.stringify(environment.seaStateFactor)+';');}return new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source)(structuredClone(input.data),structuredClone(input.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});}
const seeds=require(path.join(D,'engine.cjs')).seeds;
module.exports={create,sourceFor,symbols,seeds,input,privateSource,hooks,originalPrivate,native};
