"""Execute the exact embedded E navigation/seeker/knowledge functions in isolated deterministic cases."""
import argparse,base64,gzip,hashlib,json,re,subprocess,tempfile
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args();here=Path(__file__).parent
source=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
js=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',source.read_text(),re.S)[1])).decode()
import importlib.util
core=(here.parent/'C/core.js').read_text()
for name in ['D','E']:
 spec=importlib.util.spec_from_file_location('delta_'+name,here.parent/name/'build.py');delta=importlib.util.module_from_spec(spec);spec.loader.exec_module(delta)
 for old,new in delta.patches():
  count=core.count(old);assert count in [0,1],(old[:80],count)
  if count:core=core.replace(old,new)
assert core in js
start=js.index('const HARPOON_PROFILE_A=');end=js.index('\n});',start)+4;profile=js[start:end]
harness=r'''
const checks={},details={};function test(k,v){checks[k]=!!v;}
const make=()=>({id:1,ageS:4,memory:{positionM:{x:6000,y:0,z:8},velocityMps:{x:0,y:0,z:0},covariance:Array(36).fill(0),observationAgeS:0},
 navPositionM:{x:0,y:0,z:15},radarAltitudeM:15,ins:{yawRad:0,pitchRad:0,velocityMps:{x:289,y:0,z:0}},yawRad:0,pitchRad:0,
 seeker:{active:false,mode:'OFF',timerS:0,azRelRad:0,elRelRad:0,scanDirection:1,scanReversals:0,scanBoundsRad:[0,0],candidate:null,lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0}});
const o={rangeM:6000,bearingRad:0,elevationRad:0,radialMps:-289,verticalExtentM:8,dopplerSpreadMps:.8,snr:30},cfg=HARPOON_PROFILE_A.sim;
let m=make();let scan=[];for(let i=0;i<600;i++){harpoonSeekerA(m,1/60,[]);scan.push({az:m.seeker.azRelRad,el:m.seeker.elRelRad,dir:m.seeker.scanDirection});}
test('searchCoversBothEdges',Math.min(...scan.map(s=>s.az))<=-cfg.seekerMinSweepRad+.01&&Math.max(...scan.map(s=>s.az))>=cfg.seekerMinSweepRad-.01);
test('leftRightReversals',m.seeker.scanReversals>=6&&scan.some(s=>s.dir===1)&&scan.some(s=>s.dir===-1));
test('everySampleInsideAzElGimbals',scan.every(s=>Math.abs(s.az)<=cfg.seekerGimbalRad&&Math.abs(s.el)<=cfg.seekerElGimbalRad));
test('finiteRateAtEveryScanStep',scan.slice(1).every((s,i)=>Math.abs(s.az-scan[i].az)<=cfg.seekerSlewRadS/60+1e-9));
details.search={minAzDeg:Math.min(...scan.map(s=>s.az))*180/Math.PI,maxAzDeg:Math.max(...scan.map(s=>s.az))*180/Math.PI,reversals:m.seeker.scanReversals};
m=make();m.memory.positionM={x:6000/Math.sqrt(2),y:6000/Math.sqrt(2),z:8};m.seeker.azRelRad=cfg.seekerGimbalRad;
const angled={...o,bearingRad:cfg.seekerGimbalRad,radialMps:-289/Math.sqrt(2)};
for(let i=0;i<3;i++)harpoonSeekerA(m,.1,[angled]);test('exactGimbalEdgeIsDetectable',m.seeker.mode==='TRACK');
let beyond=make();beyond.memory.positionM={x:6000*Math.cos(deg(46)),y:6000*Math.sin(deg(46)),z:8};beyond.seeker.azRelRad=cfg.seekerGimbalRad;
for(let i=0;i<4;i++)harpoonSeekerA(beyond,.1,[{...o,bearingRad:deg(46),radialMps:-289*Math.cos(deg(46))}]);test('oneDegreeBeyondGimbalNotDetectable',!beyond.seeker.lock&&!beyond.seeker.candidate);
for(const [k,bad]of Object.entries({outsideBeam:{bearingRad:deg(20)},outsideElGimbal:{elevationRad:deg(31)},outsideRange:{rangeM:18001},belowSnr:{snr:2},airborneSmallExtent:{verticalExtentM:.2},diffuseClutter:{dopplerSpreadMps:8},outsideBasket:{rangeM:7200},wrongDoppler:{radialMps:0}})){
 const q=make();for(let i=0;i<5;i++)harpoonSeekerA(q,.1,[{...o,...bad}]);test(k+'CannotAcquire',!q.seeker.lock&&!q.seeker.candidate);
}
m=make();harpoonSeekerA(m,.1,[o]);test('acquisitionHasNoGuidanceLock',m.seeker.mode==='ACQUIRE'&&!m.seeker.lock);
harpoonSeekerA(m,.1,[]);test('interruptedAcquisitionNotTrack',m.seeker.mode==='ACQUIRE'&&!m.seeker.lock);
for(let i=0;i<4;i++)harpoonSeekerA(m,.1,[]);test('acquisitionCandidateTimesOut',m.seeker.mode==='SEARCH'&&!m.seeker.candidate);
m=make();for(let i=0;i<3;i++)harpoonSeekerA(m,.1,[o]);test('threeCorrelatedReturnsConfirmTrack',m.seeker.mode==='TRACK'&&m.seeker.lockCount===3);
harpoonSeekerA(m,.1,[]);test('trackLossUsesCoast',m.seeker.mode==='COAST');harpoonSeekerA(m,.1,[o]);test('shortLossReacquires',m.seeker.mode==='TRACK');
for(let i=0;i<41;i++)harpoonSeekerA(m,.1,[]);test('longLossClearsGuidanceLock',m.seeker.mode==='SEARCH'&&!m.seeker.lock);
for(let i=0;i<3;i++)harpoonSeekerA(m,.1,[o]);test('searchCanAcquireAgain',m.seeker.mode==='TRACK');
const memory={positionM:{x:10000,y:0,z:8},velocityMps:{x:10,y:2,z:0},observationAgeS:5};
const aged=harpoonPredictionA(memory,10,{x:0,y:0,z:0}),correct=harpoonPredictionA({...memory,observationAgeS:0},15,{x:0,y:0,z:0});test('launchObservationAgePropagatesExactly',JSON.stringify(aged)===JSON.stringify(correct));
const launchMemory=harpoonMemoryA({_kfX:[10000,0,8,10,2,0],_kfP:Array(36).fill(0),sensorAge:5,_operatorIdentity:'TRAINING_TARGET'}),current=harpoonPredictionA(launchMemory,10,{x:0,y:0,z:0}),currentReference=harpoonPredictionA({...memory,observationAgeS:0},10,{x:0,y:0,z:0});
test('currentEkfMeasurementAgeIsNotCountedTwice',JSON.stringify(current)===JSON.stringify(currentReference));test('frozenLaunchMemoryHasExplicitReleaseEpoch',launchMemory.stateEpoch==='RELEASE_CURRENT_EKF'&&launchMemory.stateAgeS===0&&launchMemory.observationAgeS===5);
const axis={x:1,y:0,z:0},pos={x:100,y:200,z:15},vel={x:100,y:0,z:0},n={id:1,ageS:0,positionM:{...pos},velocityMps:{...vel},yawRad:0,pitchRad:0,navPositionM:{...pos},ins:harpoonInsInitC(pos,vel,axis,1)};
for(let i=0;i<6000;i++){const before={velocityMps:{...vel},yawRad:0,pitchRad:0};n.ageS+=1/60;n.positionM.x+=100/60;harpoonImuSampleC(n,before,1/60);}
const err=Math.hypot(n.navPositionM.x-n.positionM.x,n.navPositionM.y-n.positionM.y);details.ins100s={positionErrorM:err,samples:n.ins.samples};test('imuPositionIntegratesWithAccumulatedError',err>5&&err<30&&n.ins.samples===6000);
const navBefore={...n.navPositionM};n.positionM.x+=50000;n.positionM.y-=30000;harpoonImuSampleC(n,{velocityMps:{...vel},yawRad:0,pitchRad:0},1/60);
test('physicalPositionJumpDoesNotResetIns',Math.abs(n.navPositionM.x-navBefore.x)<2&&Math.abs(n.navPositionM.y-navBefore.y)<1);
test('noDatalinkOrIlluminatorInProfile',HARPOON_PROFILE_A.dataLink===false&&HARPOON_PROFILE_A.illuminatorRequired===false);
test('builtInSeekerBoundaryAudit',harpoonSeekerCoreAuditC().pass);test('builtInKnowledgeBoundaryAudit',harpoonKnowledgeCoreAuditC().pass);
const oldRecord={id:1,releaseStep:0,positionM:{x:0,y:0,z:10},axis,carrierVelocityMps:{x:0,y:0,z:0},memory,excludedTrackIds:[],claimedTrackId:null};
const tr={trackId:1,_lastMeasurementStep:300,sensorDetected:true,sensorSource:'SPY1DV_SEARCH',measurementSigmaM:10,velocitySigmaMps:10,_kfX:[harpoonLaunchPredictionC(oldRecord,5).x,0,100,225,0,0]};
const prior=harpoonMatchLaunchC(oldRecord,tr,300);
const after={...tr,_lastMeasurementStep:312,_kfX:[tr._kfX[0]+45,0,100,225,0,0]};test('ownCorrelationUsesObservedContinuity',!!harpoonMatchLaunchC(oldRecord,after,312,prior));
test('trackJumpBreaksOwnCorrelation',harpoonMatchLaunchC(oldRecord,{...after,_kfX:[tr._kfX[0]+2000,0,100,225,0,0]},312,prior)==null);
test('inboundCrossingIsNotFriend',harpoonMatchLaunchC(oldRecord,{...tr,_kfX:[tr._kfX[0],0,100,-225,0,0]},300)==null);

// The low vertical extent and broad Doppler samples have no source IDs.
for(const [label,bad]of Object.entries({seaLikeLowExtent:{verticalExtentM:2.5},waveLikeDoppler:{dopplerSpreadMps:3}})){
 const q=make();for(let i=0;i<6;i++)harpoonSeekerA(q,.1,[{...o,...bad}]);test(label+'CannotAcquire',!q.seeker.lock&&!q.seeker.candidate);
}
const program=harpoonRouteProgramE([{x:4000,y:0},{x:8000,y:0}],{x:0,y:0});
const routeMissile=()=>({...make(),boosterAttached:false,tubeCleared:true,positionM:{x:0,y:0,z:15},history:[],route:{program,index:0,completed:false,passes:[],previousInsM:{x:0,y:0}}});
let q=routeMissile();q.navPositionM={x:4001,y:0,z:15};harpoonRouteStepE(q);test('insPassAdvancesIntermediate',q.route.index===1&&!q.route.completed);
q.navPositionM={x:7990,y:0,z:15};harpoonRouteStepE(q);harpoonSeekerA(q,.1,[]);test('finalPointProximityDoesNotActivateSeeker',!q.route.completed&&!q.seeker.active);
q.navPositionM={x:8010,y:0,z:15};harpoonRouteStepE(q);harpoonSeekerA(q,.1,[]);test('finalPlaneCrossingActivatesSearch',q.route.completed&&q.seeker.active&&q.route.passes[1].method==='INS_PLANE_CROSSING');
q=routeMissile();q.positionM={x:9000,y:0,z:15};harpoonRouteStepE(q);test('truthPositionJumpDoesNotAdvanceWaypoint',q.route.index===0);
q=routeMissile();q.navPositionM={x:4500,y:800,z:15};harpoonRouteStepE(q);test('passingFarBesideWaypointDoesNotAdvance',q.route.index===0);
q=routeMissile();q.boosterAttached=true;q.navPositionM={x:4001,y:0,z:15};harpoonRouteStepE(q);test('boosterDoesNotAdvanceWaypoint',q.route.index===0);
test('searchCueProjectsForwardFromLastLeg',program.searchCenterM.x===16000&&program.searchCenterM.y===0);
test('totalPathBudgetIncludesSearchAndTurnReserve',program.routeLengthM===8000&&program.plannedLengthM===18000);
test('duplicateWaypointProgramRejected',harpoonRouteProgramE([{x:4000,y:0},{x:4000,y:0}],{x:0,y:0})===null);
test('invalidCoordinateProgramRejected',harpoonRouteProgramE([{x:NaN,y:0}],{x:0,y:0})===null);

console.log(JSON.stringify({checks,details,pass:Object.values(checks).every(Boolean)}));
'''
stubs="""const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),deg=x=>x*Math.PI/180,angNorm=x=>Math.atan2(Math.sin(x),Math.cos(x)),deepFreezeShipProfileV48Wip09=x=>x;const worldToMeters=x=>x,worldSpeedToMps=x=>x,maritimeSeaLevelAtSimulationMetersWip13A3=()=>0,normalizeTrackOperatorIdentityA3=x=>x;const SIM_FIXED_DT=1/60,simStepCounter=0;"""
with tempfile.TemporaryDirectory()as tmp:
 f=Path(tmp)/'isolated.cjs';f.write_text(stubs+profile+core+harness);r=subprocess.run(['node',str(f)],text=True,capture_output=True,check=True);result=json.loads(r.stdout)
result.update(schema='HARPOON_E_GUIDANCE_VERIFICATION',source=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest())
(out/'guidance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['pass']else 1)
