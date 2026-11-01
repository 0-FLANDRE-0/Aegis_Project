'use strict';
// Fixture-only tests of the shipped TRACK-A compatibility adapter. These do not
// claim natural RF, actual weapon, association, or combat validation.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),assert=require('assert');
const here=__dirname,modulePath=path.resolve(process.argv[2]||path.join(here,'measurement-contract.js'));
const outputAt=process.argv.indexOf('--out'),outputPath=outputAt>=0?path.resolve(process.argv[outputAt+1]):null;
if(!fs.existsSync(modulePath)){
 const result={suite:'TRACK_A_CONTRACT_UNIT',status:'BLOCKED',reason:'Measurement contract module is not available',module:modulePath,fixtureOnly:true};
 if(outputPath){fs.mkdirSync(path.dirname(outputPath),{recursive:true});fs.writeFileSync(outputPath,JSON.stringify(result,null,2)+'\n');}
 console.log(JSON.stringify(result));process.exit(2);
}
const source=fs.readFileSync(modulePath,'utf8'),results=[],records={};
let randomCalls=0,wallClockCalls=0,simulationClockReads=0;
const math=Object.create(Math);math.random=()=>{randomCalls++;throw Error('Contract must not draw randomness');};
class ForbiddenDate{constructor(){wallClockCalls++;throw Error('Contract must not read wall clock');}static now(){wallClockCalls++;throw Error('Contract must not read wall clock');}}
const sandbox={window:{},Math:math,Date:ForbiddenDate,performance:{now(){wallClockCalls++;throw Error('Contract must not read performance clock');}},worldToMeters:x=>x/.0038,SIM_FIXED_DT:1/60,console};
Object.defineProperty(sandbox,'simStepCounter',{get(){simulationClockReads++;return 60;},set(){throw Error('Diagnostic wrote simulation clock');}});
Object.defineProperty(sandbox,'SIM_RNG_STATE',{get(){return 123456789;},set(){throw Error('Diagnostic wrote game RNG');}});
vm.createContext(sandbox);vm.runInContext(source,sandbox,{filename:modulePath});
const api=sandbox.window.__TRACK_A__;
function test(name,fn){try{fn();results.push({name,status:'PASS'});}catch(e){results.push({name,status:'FAIL',message:String(e.stack||e)});}}
const clone=x=>JSON.parse(JSON.stringify(x));
function finiteTree(x,at='$'){
 if(typeof x==='number')assert(Number.isFinite(x),'non-finite number at '+at);
 if(x&&typeof x==='object')for(const[k,v]of Object.entries(x))finiteTree(v,at+'.'+k);
}
function referenceSet(x,out=new Set()){
 if(x&&typeof x==='object'&&!out.has(x)){out.add(x);for(const y of Object.values(x))referenceSet(y,out);}return out;
}
function detached(input,output){const refs=referenceSet(input);for(const r of referenceSet(output))assert(!refs.has(r),'returned an input object/array by reference');}
function fields(r){return Array.from(r.measuredFields);}
function fieldValue(r,name){
 const o=r.observed;
 if(o&&Object.prototype.hasOwnProperty.call(o,name))return o[name];
 if(o?.values&&Object.prototype.hasOwnProperty.call(o.values,name))return o.values[name];
 if(o?.vector&&Array.isArray(o.vector)){const i=Array.from(r.measurementModel.rows).indexOf(name);if(i>=0)return o.vector[i];}
 throw Error('No observed value for '+name);
}
function containsNumber(x,n){return typeof x==='number'?x===n:!!x&&typeof x==='object'&&Object.values(x).some(y=>containsNumber(y,n));}
function noPolicy(r){
 const serialized=JSON.stringify(r);
 assert(!serialized.includes('SECRET_TRUTH_CANARY_A'),'hidden truth value copied');
 const forbidden=new Set(['truthRef','objectId','entityId','rfId','_truthObject','_physicsKind','_sourceSeed','faction','owner','ownerSide','ownerEntityId','truth','alive','dead','seeker','ins','navPositionM','actualPositionM','targetId','targetEntityId','truthTrack']);
 for(const o of referenceSet(r))for(const k of Object.keys(o))assert(!forbidden.has(k),'forbidden field copied: '+k);
}
function model(r,dimension,physical=dimension){
 assert.equal(r.measurementModel.dimension,dimension);
 assert.strictEqual(r.measurementModel.physicalObservationDimension,physical);
 assert.equal(Array.from(r.measurementModel.rows).length,dimension);
 finiteTree(r);noPolicy(r);
}
const context={sourceSensor:'UNIT_SENSOR',observerShip:'SELF_RECEIVER',measuredAtS:12.5,receivedAtS:12.8,sourceId:'H1',sequence:7};
const radar={source:'PAYLOAD_SOURCE',rangeM:4123,azRad:.35,elRad:.07,radialMps:-210,rangeSigmaM:15,azSigmaDeg:.1,elSigmaDeg:.2,radialVelSigmaMps:4,x:15.2,y:3.8,z:50,sensorXWorld:1.9,sensorYWorld:0,sensorZM:22,sensorVxMps:3,sensorVyMps:1,sensorVzMps:0,quality:.7,domainEvidence:{air:.85,surface:.05,missile:.1,background:0}};
const surface={...radar,source:'SPQ9B_SURFACE_PRECISION',z:8,surfaceReferenceZM:8};delete surface.elRad;
test('api.available',()=>{assert(api&&typeof api.normalize==='function');for(const n of ['configure','clear','snapshot'])assert.equal(typeof api[n],'function',n);});
test('air.fourObservedChannels',()=>{const r=api.normalize('AIR_RADAR',radar,context);model(r,4);assert.deepStrictEqual(fields(r),['rangeM','azRad','elRad','radialMps']);for(const n of fields(r))assert.equal(fieldValue(r,n),radar[n]);records.air=r;});
test('metadata.sourceObserverAndTimestamps',()=>{const r=api.normalize('AIR_RADAR',radar,context);assert.equal(r.sourceSensor,context.sourceSensor);assert.equal(r.observerShip,context.observerShip);assert.equal(r.measuredAtS,12.5);assert.equal(r.receivedAtS,12.8);assert.equal(r.quality,.7);});
test('metadata.payloadSourceFallback',()=>{const r=api.normalize('AIR_RADAR',radar,{});assert.equal(r.sourceSensor,'PAYLOAD_SOURCE');});
test('metadata.unknownTimesNotZero',()=>{const r=api.normalize('AIR_RADAR',radar,{});assert.strictEqual(r.measuredAtS,null);assert.strictEqual(r.receivedAtS,null);});
test('metadata.genuineZeroTimestampPreserved',()=>{const r=api.normalize('AIR_RADAR',radar,{...context,measuredAtS:0,receivedAtS:0});assert.strictEqual(r.measuredAtS,0);assert.strictEqual(r.receivedAtS,0);});
test('metadata.packetMeasurementTimeAuthoritative',()=>{const r=api.normalize('OFFBOARD_PLOT',{sourceId:'H1',sequence:21,measuredAtS:4,positionM:{x:8000,y:0,z:8},covarianceM2:[100,0,0,0,100,0,0,0,16]},{...context,measuredAtS:12.5,receivedAtS:12.8});assert.equal(r.measuredAtS,4);assert.equal(r.receivedAtS,12.8);records.delayedReport=r;});
test('metadata.packetZeroTimeNotReplacedByReceipt',()=>{const r=api.normalize('OFFBOARD_PLOT',{measuredAtS:0,positionM:{x:1,y:2,z:8}},{...context,measuredAtS:12.5,receivedAtS:12.8});assert.strictEqual(r.measuredAtS,0);assert.equal(r.receivedAtS,12.8);});
test('metadata.receiverGeometryPreservedInMeters',()=>{const r=api.normalize('AIR_RADAR',radar,context);assert.deepStrictEqual(clone(r.observerState.originM),{x:500,y:0,z:22});assert.deepStrictEqual(clone(r.observerState.velocityMps),{x:3,y:1,z:0});});
test('metadata.receiverGeometryNeverUsesOwnTruthFallback',()=>{const r=api.normalize('AIR_RADAR',{rangeM:1000,azRad:.1,elRad:0,radialMps:0},context);assert(!containsNumber(r.observerState,22));assert(!containsNumber(r.observerState,500));const nums=[];for(const o of referenceSet(r.observerState))for(const v of Object.values(o))if(typeof v==='number')nums.push(v);assert.deepStrictEqual(nums,[]);});
test('surface.threeWithActualDoppler',()=>{const r=api.normalize('SURFACE_RADAR',surface,context);model(r,3);assert.deepStrictEqual(fields(r),['rangeM','azRad','radialMps']);assert(!fields(r).includes('elRad'));assert(!fields(r).includes('zM'));assert(containsNumber(r.assumed,8));records.surface3=r;});
test('surface.bridgeMasterTwoOnly',()=>{const p={...surface,source:'BRIDGEMASTER_E'};delete p.radialMps;const r=api.normalize('SURFACE_RADAR',p,context);model(r,2);assert.deepStrictEqual(fields(r),['rangeM','azRad']);assert(!fields(r).includes('radialMps'));});
test('surface.zeroDopplerIsGenuineChannelWhenProvided',()=>{const r=api.normalize('SURFACE_RADAR',{...surface,radialMps:0},context);model(r,3);assert.equal(fieldValue(r,'radialMps'),0);});
test('surface.noInventedHeightWhenPriorMissing',()=>{const p={...surface};delete p.surfaceReferenceZM;delete p.z;const r=api.normalize('SURFACE_RADAR',p,context);assert(!fields(r).some(x=>/^(elRad|zM|altitudeM)$/.test(x)));assert(!containsNumber(r.assumed,8));});
test('ciws.threePolarNotSixCartesian',()=>{const p={rangeM:1000,azRad:.2,elRad:.01,rxM:980,ryM:200,rzM:10,positionVarianceM2:[9,25,25],source:'LOCAL_RF',quality:.8};const r=api.normalize('CIWS_LOCAL_RF',p,context);model(r,3);assert.deepStrictEqual(fields(r),['rangeM','azRad','elRad']);assert(!fields(r).some(x=>/^r?[xyz]M$/.test(x)));assert(containsNumber(r.derived,980));records.ciws=r;});
test('visual.xyzNotPlaceholderDoppler',()=>{const r=api.normalize('VISUAL_CARTESIAN',{x:15.2,y:3.8,z:50,radialMps:0,rangeSigmaM:60,altitudeSigmaM:40,source:'VISUAL'},context);model(r,3);assert.deepStrictEqual(fields(r),['xM','yM','zM']);assert(!fields(r).includes('radialMps'));assert.equal(fieldValue(r,'xM'),4000);assert.equal(fieldValue(r,'yM'),1000);assert.equal(fieldValue(r,'zM'),50);});
test('helo.rangeBearingAndSurfacePrior',()=>{const p={measuredRangeM:17000,measuredAzRad:.25,positionM:{x:16000,y:4100,z:8},covarianceM2:[100,0,0,0,900,0,0,0,16],measuredAtS:4,scanOrdinalF:9,domainEvidence:{surface:.98,air:.02,missile:0,background:0}};const r=api.normalize('HELO_RADAR',p,context);model(r,2);assert.deepStrictEqual(fields(r),['rangeM','azRad']);assert.equal(fieldValue(r,'rangeM'),17000);assert.equal(fieldValue(r,'azRad'),.25);assert(containsNumber(r.assumed,8));assert(containsNumber(r.derived,16000));records.helo=r;});
test('esm.bearingOnlyNeverInventsRange',()=>{const r=api.normalize('ESM_BEARING',{bearing:.75,bearingSigmaDeg:2,confidence:.7,band:'IJ',family:'NAVIGATION RADAR',rangeM:9999,x:15.2,y:3.8,z:50},context);model(r,1);assert.deepStrictEqual(fields(r),['bearingRad']);assert.equal(fieldValue(r,'bearingRad'),.75);assert(!containsNumber(r.observed,9999));assert(!containsNumber(r.derived,4000));assert(!containsNumber(r.reported,9999));records.esm=r;});
test('iff.observationDoesNotCreateAuthority',()=>{const r=api.normalize('IFF_REPLY',{rangeM:4000,bearing:.2,elevationRad:.02,rangeSigmaM:80,bearingSigmaDeg:1,elevationSigmaDeg:.5,authenticatedFriendly:true,measuredAtS:2,expiresAtS:5,identity:'HOSTILE',engagementAuthority:'GRANTED'},context);model(r,3);assert(fields(r).includes('authenticatedFriendly'));assert.equal(fieldValue(r,'authenticatedFriendly'),true);assert(!Object.prototype.hasOwnProperty.call(r,'identity'));assert(!Object.prototype.hasOwnProperty.call(r,'engagementAuthority'));});
test('isar.featuresNotNewKinematicHit',()=>{const p={positionM:{x:8000,y:0,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],result:{lengthM:154.6,lengthSigmaM:6,heightsM:[5,8,14,20],heightSigmaM:2,mastPosition01:.4,mastSigma01:.05,candidates:[{classId:'BURKE_IIA',label:'Burke IIA',confidence:.8}],quality:.7},measuredAtS:7,sourceId:'H1',sequence:3};const r=api.normalize('ISAR_EVIDENCE',p,context);model(r,0,0);assert(!fields(r).some(x=>['xM','yM','zM','rangeM','azRad'].includes(x)));assert(fields(r).includes('lengthM'));assert(!Object.prototype.hasOwnProperty.call(r,'sensorHits'));assert(!Object.prototype.hasOwnProperty.call(r,'identity'));records.isar=r;});
test('offboard.reportedXYZNotPhysicalThreeD',()=>{const p={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:19,measuredAtS:10,positionM:{x:8000,y:200,z:8},covarianceM2:[100,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:0,background:0}};const r=api.normalize('OFFBOARD_PLOT',p,context);model(r,3,null);assert.deepStrictEqual(fields(r),[]);assert(containsNumber(r.reported,8000));assert(containsNumber(r.reported,8));assert(!containsNumber(r.observed,8));records.offboard=r;});
test('network.reportedSixStateNotSixIndependentObservations',()=>{const p={stateM:[8000,200,50,-100,20,1],covariance:Array.from({length:36},(_,i)=>i%7===0?100:0),sourceId:'ALLY_RADAR',sourceTrackUid:'OBS-12',measuredAtS:10,sequence:4,domain:'AIR',classification:'ASM',identity:'HOSTILE',engagementAuthority:'GRANTED'};const r=api.normalize('NETWORK_TRACK',p,context);model(r,6,null);assert.deepStrictEqual(fields(r),[]);assert(containsNumber(r.reported,-100));assert(!Object.prototype.hasOwnProperty.call(r,'engagementAuthority'));records.network=r;});
test('network.reconciledEstimateEpochIsNotMeasurementOrReceiptTime',()=>{const p={stateM:[8000,200,50,0,0,0],covariance:Array.from({length:36},(_,i)=>i%7===0?100:0),stateAtS:50},r=api.normalize('NETWORK_TRACK',p,{sourceSensor:'LINK16_CI',observerShip:'SELF_RECEIVER',measuredAtS:null,receivedAtS:null});model(r,6,null);assert.strictEqual(r.measuredAtS,null);assert.strictEqual(r.receivedAtS,null);assert.equal(r.reported.stateAtS,50);assert.deepStrictEqual(fields(r),[]);});
test('networkSelf.notTargetObservation',()=>{const r=api.normalize('NETWORK_SELF',{stateM:[1,2,8,4,5,0],positionM:{x:1,y:2,z:8},headingRad:.2,speedMps:4},context);model(r,6,null);assert.deepStrictEqual(fields(r),[]);assert(containsNumber(r.assumed,8));assert(containsNumber(r.assumed,0));noPolicy(r);});
test('provenance.explicitSequenceAndSourceSurvive',()=>{const r=api.normalize('OFFBOARD_PLOT',{positionM:{x:1,y:2,z:8},covarianceM2:[1,0,0,0,1,0,0,0,1],sourceId:'H2',sequence:44,measuredAtS:5},{observerShip:'SELF_RECEIVER',receivedAtS:6});assert(JSON.stringify(r.provenance).includes('H2'));assert(containsNumber(r.provenance,44));assert.equal(r.measuredAtS,5);assert.equal(r.receivedAtS,6);});
test('provenance.receiptDoesNotImplyIndependence',()=>{const r=api.normalize('OFFBOARD_PLOT',{positionM:{x:1,y:2,z:8},sourceId:'H2',sequence:44},{});assert.strictEqual(r.provenance.independentObservation,null);});
test('owner.receiverContextsDetachedAndDistinct',()=>{const a=api.normalize('AIR_RADAR',radar,{...context,observerShip:'SHIP_A'}),b=api.normalize('AIR_RADAR',radar,{...context,observerShip:'SHIP_B'});assert.equal(a.observerShip,'SHIP_A');assert.equal(b.observerShip,'SHIP_B');assert.notStrictEqual(a,b);assert.notStrictEqual(a.observed,b.observed);});
test('privacy.truthAndPolicyCanariesDropped',()=>{const secret='SECRET_TRUTH_CANARY_A',p={...radar,truthRef:{objectId:secret},objectId:secret,entityId:secret,rfId:secret,_truthObject:{x:123,faction:secret},faction:secret,owner:secret,ownerSide:secret,ownerEntityId:secret,alive:true,dead:false,seeker:{track:secret},ins:{position:secret},targetId:secret,identity:'HOSTILE',engagementAuthority:'GRANTED',domainEvidence:{...radar.domainEvidence,truthRef:{objectId:secret}}};for(const kind of ['AIR_RADAR','SURFACE_RADAR','CIWS_LOCAL_RF','VISUAL_CARTESIAN','HELO_RADAR','ESM_BEARING','IFF_REPLY','ISAR_EVIDENCE','OFFBOARD_PLOT','NETWORK_TRACK','NETWORK_SELF'])noPolicy(api.normalize(kind,p,context));});
test('purity.frozenInputUnchanged',()=>{const freeze=x=>{if(x&&typeof x==='object'){Object.freeze(x);for(const y of Object.values(x))freeze(y);}return x;};const p=freeze(clone(radar)),c=freeze(clone(context)),before=JSON.stringify({p,c});api.normalize('AIR_RADAR',p,c);assert.equal(JSON.stringify({p,c}),before);});
test('purity.noReturnedAliases',()=>{const p={...surface,domainEvidence:{surface:.9,features:{heightM:8}},cartesianCovarianceM2:[100,0,0,0,400,0,0,0,16]},c={...context,lineage:['S1','S2']},r=api.normalize('SURFACE_RADAR',p,c);detached({p,c},r);});
test('purity.repeatIsExact',()=>{const a=api.normalize('AIR_RADAR',radar,context),b=api.normalize('AIR_RADAR',radar,context);assert.equal(JSON.stringify(a),JSON.stringify(b));});
test('purity.normalizeNoClockOrRngRead',()=>{const clocks=simulationClockReads;api.normalize('AIR_RADAR',radar,context);assert.equal(simulationClockReads,clocks);assert.equal(randomCalls,0);assert.equal(wallClockCalls,0);});
test('robust.nonfiniteNeverBecomesValidZero',()=>{const r=api.normalize('AIR_RADAR',{rangeM:NaN,azRad:Infinity,elRad:-Infinity,radialMps:undefined,rangeSigmaM:NaN,quality:Infinity},{});finiteTree(r);assert.deepStrictEqual(fields(r),[]);assert(!containsNumber(r.observed,0));});
test('robust.partialObservationMask',()=>{const r=api.normalize('AIR_RADAR',{rangeM:1000,azRad:NaN,elRad:undefined,radialMps:Infinity},{...context});assert.deepStrictEqual(fields(r),['rangeM']);assert.equal(r.measurementModel.dimension,1);finiteTree(r);});
test('uncertainty.providedNoiseNotReplacedByFallback',()=>{const r=api.normalize('AIR_RADAR',{rangeM:1000,azRad:.1,elRad:.2,radialMps:0,rangeSigmaM:7,azSigmaDeg:.03,elSigmaDeg:.08,radialVelSigmaMps:2},context);const q=r.uncertainty.providedSigmas;assert.equal(q.rangeSigmaM,7);assert.equal(q.azSigmaDeg,.03);assert.equal(q.elSigmaDeg,.08);assert.equal(q.radialVelSigmaMps,2);});
test('uncertainty.missingNoiseStaysUnknown',()=>{const r=api.normalize('AIR_RADAR',{rangeM:1000,azRad:.1,elRad:.2,radialMps:0},context);assert.equal(Object.keys(r.uncertainty.providedSigmas).length,0);assert.strictEqual(r.uncertainty.cartesianCovarianceM2,null);assert.equal(r.uncertainty.missingNoiseIsUnknown,true);});
test('uncertainty.cartesianCovarianceExactShape',()=>{for(const a of [[1,0],new Array(10).fill(1)]){const r=api.normalize('OFFBOARD_PLOT',{positionM:{x:1,y:2,z:8},covarianceM2:a},context);assert.strictEqual(r.uncertainty.covarianceM2,null);assert.strictEqual(r.reported.covarianceM2,null);}});
test('uncertainty.networkCovarianceExactShape',()=>{for(const a of [[1,0],new Array(37).fill(1)]){const r=api.normalize('NETWORK_TRACK',{stateM:[1,2,3,4,5,6],covariance:a},context);assert.strictEqual(r.uncertainty.covariance,null);assert.strictEqual(r.reported.covariance,null);}});
test('uncertainty.ciwsVarianceExactShape',()=>{for(const a of [[1,2],new Array(4).fill(1)]){const r=api.normalize('CIWS_LOCAL_RF',{rangeM:100,azRad:.1,elRad:0,positionVarianceM2:a},context);assert.strictEqual(r.uncertainty.relativePositionVarianceM2,null);}});
test('robust.nullPayload',()=>{for(const p of [null,undefined,42,'not-a-plot']){const r=api.normalize('AIR_RADAR',p,{});assert.deepStrictEqual(fields(r),[]);finiteTree(r);noPolicy(r);}});
test('trace.defaultOff',()=>{const s=api.snapshot();assert.strictEqual(s.enabled,false);assert(Array.isArray(s.records));assert.equal(s.records.length,0);});
const emit="trackATraceEventA('MEASUREMENT',{rangeM:1000,azRad:.2,surfaceReferenceZM:8},{kind:'SURFACE_RADAR',sourceSensor:'UNIT',observerShip:'SELF',measuredAtS:1,receivedAtS:1,trackId:42,nis:2,gate:64,decision:'ACCEPT'})";
test('trace.disabledEventDoesNotRecord',()=>{api.clear();const a=JSON.stringify(api.snapshot());vm.runInContext(emit,sandbox);assert.equal(JSON.stringify(api.snapshot()),a);});
test('trace.boundedCapacityAndOverflow',()=>{api.configure({enabled:true,capacity:16});api.clear();for(let i=0;i<48;i++)vm.runInContext(emit,sandbox);const s=api.snapshot();assert.equal(s.records.length,16);assert(s.stats);records.traceOverflow=s;});
test('trace.overflowOrderAndDropAccounting',()=>{const s=api.snapshot();assert.equal(s.stats.recorded,48);assert.equal(s.stats.dropped,32);assert.equal(s.records[0].serial,33);assert.equal(s.records[15].serial,48);});
test('trace.nativeGateResultCopiedWithoutRecalculation',()=>{api.clear();vm.runInContext("trackATraceEventA('CANDIDATE',{rangeM:1000,azRad:.2},{kind:'SURFACE_RADAR',sourceSensor:'UNIT',observerShip:'SELF',trackId:42,nis:101.1,gate:96,decision:'REJECT',reason:'NIS',finalSource:'SPY'})",sandbox);const r=api.snapshot().records[0];assert.equal(r.nis,101.1);assert.equal(r.gate,96);assert.equal(r.decision,'REJECT');assert.equal(r.trackId,42);assert.equal(r.reason,'NIS');assert.equal(r.finalSource,'SPY');});
test('trace.snapshotDetached',()=>{const a=api.snapshot(),before=JSON.stringify(api.snapshot());assert(a.records.length);a.records.length=0;if(a.stats)for(const k of Object.keys(a.stats))if(typeof a.stats[k]==='number')a.stats[k]=-999;assert.equal(JSON.stringify(api.snapshot()),before);});
test('trace.queryNoStateMutation',()=>{const before=JSON.stringify(api.snapshot()),clocks=simulationClockReads;for(let i=0;i<20;i++)api.snapshot();assert.equal(JSON.stringify(api.snapshot()),before);assert.equal(simulationClockReads,clocks);});
test('trace.clearOnlyDiagnostic',()=>{api.clear();assert.equal(api.snapshot().records.length,0);assert.equal(sandbox.SIM_RNG_STATE,123456789);});
test('trace.capacityBounds',()=>{api.configure({enabled:true,capacity:1});assert(api.snapshot().capacity>=16);api.configure({enabled:true,capacity:100000});assert(api.snapshot().capacity<=4096);api.configure({enabled:false,capacity:16});});
test('trace.privacyNoForbiddenFields',()=>{api.configure({enabled:true,capacity:16});api.clear();vm.runInContext("trackATraceEventA('MEASUREMENT',{rangeM:1000,azRad:.2,truthRef:{objectId:'SECRET_TRUTH_CANARY_A'},_truthObject:{faction:'SECRET_TRUTH_CANARY_A'}},{kind:'SURFACE_RADAR',observerShip:'SELF',sourceSensor:'UNIT',trackId:42})",sandbox);noPolicy(api.snapshot());api.configure({enabled:false});});
test('trace.beforeAfterStateRewhitelisted',()=>{api.configure({enabled:true,capacity:16});api.clear();vm.runInContext("trackATraceEventA('APPLY',{rangeM:1000,azRad:.2},{kind:'SURFACE_RADAR',observerShip:'SELF',sourceSensor:'UNIT',trackId:42,before:{trackId:42,sensorSource:'SPY',truthRef:{objectId:'SECRET_TRUTH_CANARY_A'},_truthObject:{owner:'SECRET_TRUTH_CANARY_A'}},after:{trackId:42,sensorSource:'SPQ',faction:'SECRET_TRUTH_CANARY_A',targetId:'SECRET_TRUTH_CANARY_A'}})",sandbox);const s=api.snapshot();assert.equal(s.records.length,1);noPolicy(s);assert.equal(s.records[0].before.trackId,42);assert.equal(s.records[0].after.trackId,42);api.configure({enabled:false});});
test('global.noRandomOrWallClockCalls',()=>{assert.equal(randomCalls,0);assert.equal(wallClockCalls,0);});
const failed=results.filter(r=>r.status==='FAIL');
const result={suite:'TRACK_A_CONTRACT_UNIT',status:failed.length?'FAIL':'PASS',fixtureOnly:true,naturalRfOrWeaponEvidence:false,module:modulePath,moduleSha256:crypto.createHash('sha256').update(source).digest('hex'),assertionCount:results.length,passed:results.length-failed.length,failed:failed.length,randomCalls,wallClockCalls,results,records};
if(outputPath){fs.mkdirSync(path.dirname(outputPath),{recursive:true});fs.writeFileSync(outputPath,JSON.stringify(result,null,2)+'\n');}
console.log(JSON.stringify({status:result.status,assertions:results.length,passed:result.passed,failed:failed.map(r=>({name:r.name,message:r.message.split('\n')[0]})),moduleSha256:result.moduleSha256}));
process.exitCode=failed.length?1:0;
