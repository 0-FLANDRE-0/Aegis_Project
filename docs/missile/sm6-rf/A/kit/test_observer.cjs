const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync(__dirname+'/observer.js','utf8');
const setup=String.raw`
const window={};let simStepCounter=1;const targetPool=[{_testFixture:true,x:100,y:20,z:5000,vx:-250,vy:0,vz:0}];
const worldToMeters=x=>x,worldSpeedToMps=x=>x;
const nativeCounts={adapter:0,selected:0,associate:0,ekf:0,pn:0,apn:0,zem:0,kappa:0,bridge:0,dynamics:0};
const adapterValue={isValid:true,source:'ARH_RF_EKF',confidence:.6,posM:{x:130,y:50,z:5030},velMps:{x:-240,y:10,z:5},canAcquireAuthority:true,canHoldAuthority:true};
const pnValue={ax:1,ay:2,az:3},bridgeValue={omegaYaw:.01,omegaPit:.02};
const m={isSM6:true,life:140,x:0,y:0,z:100,vx:700,vy:0,vz:-20,_v1GuidancePhase:'TERMINAL',_v1TerminalActive:true,
 _arhRfSeeker:{mode:'TRACK',trackValid:true,confidence:.6,_kfX:new Float64Array([130,50,5030,-240,10,5]),_kfP:new Float64Array(36).fill(1)},
 _samPrevNormalAccWorld:{x:1,y:2,z:3}};
let TERM_LIVE_LAST_MISSILE_A=m;
function getArhTargetStateV1(){nativeCounts.adapter++;return adapterValue;}
function getGuidanceTargetStateV1(m){nativeCounts.selected++;const v=getArhTargetStateV1(m);return {...v,selfStateM:{posM:{x:m.x,y:m.y,z:m.z},velMps:{x:m.vx,y:m.vy,z:m.vz}}};}
function _arhAssociateMeasurements(m,s,a){nativeCounts.associate++;s.lastNis=1.2;return a[0]??null;}
function _arhEkfUpdate(){nativeCounts.ekf++;return true;}
function computeTruePN3D(){nativeCounts.pn++;return pnValue;}
function computeAPNCorrectionV1(){nativeCounts.apn++;return pnValue;}
function computeZEMCorrectionV1(){nativeCounts.zem++;return pnValue;}
function computeKappaMidcourseAccelV2(){nativeCounts.kappa++;return pnValue;}
function applyAccelCommandToAutopilotV1(){nativeCounts.bridge++;return bridgeValue;}
function updateSamSixDofLiteDynamics(m,dt){nativeCounts.dynamics++;m.x+=m.vx*dt;return 'NATIVE_DYNAMICS_RETURN';}
`;
const checks=String.raw`
window.__SM6_RF_CAUSAL_DIAG__.configure('NATIVE');
const originalPosition={...adapterValue.posM};
assert.strictEqual(getArhTargetStateV1(m),adapterValue);
assert.strictEqual(computeTruePN3D(m,{},4),pnValue);
assert.strictEqual(computeAPNCorrectionV1(m,{}, {},1/60),pnValue);
assert.strictEqual(computeZEMCorrectionV1(m,{},{}),pnValue);
assert.strictEqual(computeKappaMidcourseAccelV2(m,{},1/60),pnValue);
assert.strictEqual(applyAccelCommandToAutopilotV1(m,pnValue,1/60),bridgeValue);
const meas={rangeM:1000,azRad:0,elRad:0};
assert.strictEqual(_arhAssociateMeasurements(m,m._arhRfSeeker,[meas],{},{}),meas);
assert.strictEqual(_arhEkfUpdate(m._arhRfSeeker,meas,m,{},{}),true);
m._v1TargetState=getGuidanceTargetStateV1(m,1/60);
const result=updateSamSixDofLiteDynamics(m,1/60,.01,.02,{massKg:425,thrustN:0,qPa:30000});
assert.strictEqual(result,'NATIVE_DYNAMICS_RETURN');
const rows=window.__SM6_RF_CAUSAL_DIAG__.read();
assert.strictEqual(rows.length,1);
assert.strictEqual(rows[0].before.selectedState.relativePositionErrorM.x,30);
assert.strictEqual(rows[0].afterPhysical.ownPosM.x,700/60);
targetPool[0].x=999;m._v1TargetState.posM.x=-999;
assert.strictEqual(rows[0].before.truth.targetPosM.x,100);
assert.strictEqual(rows[0].before.selectedState.posM.x,130);
assert.deepStrictEqual(nativeCounts,{adapter:2,selected:1,associate:1,ekf:1,pn:1,apn:1,zem:1,kappa:1,bridge:1,dynamics:1});
targetPool[0].x=100;adapterValue.posM={...originalPosition};
window.__SM6_RF_CAUSAL_DIAG__.configure('IDEAL_ARH_VALUES_REAL_VALIDITY');
const ideal=getArhTargetStateV1(m);
assert.deepStrictEqual(ideal.posM,{x:100,y:20,z:5000});
assert.deepStrictEqual(ideal.velMps,{x:-250,y:0,z:0});
assert.strictEqual(ideal.isValid,adapterValue.isValid);
assert.strictEqual(ideal.confidence,adapterValue.confidence);
assert.deepStrictEqual(adapterValue.posM,originalPosition);
window.__SM6_RF_CAUSAL_DIAG__.configure('WITHHOLD_ARH_AUTHORITY');
const withheld=getArhTargetStateV1(m);
assert.strictEqual(withheld.canAcquireAuthority,false);
assert.strictEqual(withheld.canHoldAuthority,false);
assert.strictEqual(adapterValue.canAcquireAuthority,true);
assert.strictEqual(adapterValue.canHoldAuthority,true);
assert.strictEqual(withheld.posM,adapterValue.posM);
assert.throws(()=>window.__SM6_RF_CAUSAL_DIAG__.configure('UNKNOWN'));
return {pass:true,scope:'Stub observer identity/call count, detached logs, adapter counterfactual isolation. Not a native game runtime test.'};
`;
console.log(JSON.stringify(new Function('assert',setup+'\n'+source+'\n'+checks)(assert)));

