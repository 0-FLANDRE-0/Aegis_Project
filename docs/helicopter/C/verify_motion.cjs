const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(__dirname+'/motion.js','utf8');
const {move,C}=vm.runInNewContext(`(()=>{${source};return {move:heloMoveA,C:HELO_VALUES_A};})()`);
const checks={},cases=[];
function fresh(vx=0,vy=0){return {positionM:{x:0,y:0,z:8},airVelocityMps:{x:vx,y:vy},groundVelocityMps:{x:vx,y:vy,z:0},headingRad:0,motionBearingRad:Math.atan2(vy,vx),pitchRad:0,bankRad:0};}
function run(label,h,target,wind,seconds){let previousAngle=h.motionBearingRad,maxTurnRatio=0,maxAir=0,maxClimb=0,maxLongAccel=0,maxLongDecel=0,arrivedAt=null,overshoot=false;
 for(let i=0;i<seconds*60;i++){const previousSpeed=Math.hypot(h.airVelocityMps.x,h.airVelocityMps.y),previousZ=h.positionM.z,q=move(h,target,wind,1/60),speed=Math.hypot(h.airVelocityMps.x,h.airVelocityMps.y),delta=Math.abs(Math.atan2(Math.sin(h.motionBearingRad-previousAngle),Math.cos(h.motionBearingRad-previousAngle)));if(previousSpeed>=30*C.knotMps)maxTurnRatio=Math.max(maxTurnRatio,delta/(C.gravity*Math.tan(C.maxBankRad)/previousSpeed/60));previousAngle=h.motionBearingRad;maxAir=Math.max(maxAir,speed);maxClimb=Math.max(maxClimb,Math.abs(h.positionM.z-previousZ)*60);maxLongAccel=Math.max(maxLongAccel,(speed-previousSpeed)*60);maxLongDecel=Math.max(maxLongDecel,(previousSpeed-speed)*60);if(h.positionM.x>target.x+1)overshoot=true;if(q.arrived&&arrivedAt===null)arrivedAt=(i+1)/60;}
 const d=Math.hypot(target.x-h.positionM.x,target.y-h.positionM.y);cases.push({label,distanceM:d,arrivedAt,maxAir,maxClimb,maxTurnRatio,maxLongAccel,maxLongDecel,overshoot,final:h});checks[label+'.arrives']=arrivedAt!==null&&d<2;checks[label+'.airSpeedBound']=maxAir<=C.maxCruiseKt*C.knotMps+1e-6;checks[label+'.climbBound']=maxClimb<=Math.min(C.verticalMps,C.maxClimbMps)+1e-6;checks[label+'.turnBound']=maxTurnRatio<=1+1e-7;checks[label+'.accelBound']=maxLongAccel<=C.accel+1e-6&&maxLongDecel<=C.decel+1e-6;return h;
}
run('calm',fresh(),{x:5000,y:0},{x:0,y:0},400);
run('crosswind',fresh(),{x:5000,y:0},{x:0,y:20},500);
run('tailwind',fresh(),{x:5000,y:0},{x:15,y:0},500);
run('overshoot',fresh(60,0),{x:200,y:0},{x:0,y:0},600);checks.overshootReturns=cases.at(-1).overshoot;
run('reverseTurn',fresh(60,0),{x:-5000,y:200},{x:0,y:0},500);
const h=fresh();for(let i=0;i<3000;i++)move(h,{x:10000,y:0},{x:0,y:0},1/60);const before=JSON.stringify(h);const target={x:0,y:5000};checks.retargetDoesNotWritePose=before===JSON.stringify(h);const old={...h.airVelocityMps};move(h,target,{x:0,y:0},1/60);checks.retargetNoInstantVelocityReversal=Math.hypot(h.airVelocityMps.x-old.x,h.airVelocityMps.y-old.y)<.5;
const oldMove=vm.runInNewContext(`(()=>{${fs.readFileSync(__dirname+'/../B/motion.js','utf8')};return heloMoveA;})()`);
const aTurn=fresh(C.cruiseKt*C.knotMps),bTurn=fresh(C.cruiseKt*C.knotMps);aTurn.positionM.z=bTurn.positionM.z=50;
let minA=Infinity,minB=Infinity,minRadiusA=Infinity,minRadiusB=Infinity,maxDecel=0,maxHeadingJump=0;
for(let i=0;i<1800;i++){const speed=Math.hypot(bTurn.airVelocityMps.x,bTurn.airVelocityMps.y),heading=bTurn.motionBearingRad;oldMove(aTurn,{x:-6000,y:5000},{x:0,y:0},1/60);move(bTurn,{x:-6000,y:5000},{x:0,y:0},1/60);const av=Math.hypot(aTurn.airVelocityMps.x,aTurn.airVelocityMps.y),bv=Math.hypot(bTurn.airVelocityMps.x,bTurn.airVelocityMps.y);minA=Math.min(minA,av);minB=Math.min(minB,bv);minRadiusA=Math.min(minRadiusA,av*av/(C.gravity*Math.tan(C.maxBankRad)));minRadiusB=Math.min(minRadiusB,bv*bv/(C.gravity*Math.tan(C.maxBankRad)));maxDecel=Math.max(maxDecel,(speed-bv)*60);maxHeadingJump=Math.max(maxHeadingJump,Math.abs(Math.atan2(Math.sin(bTurn.motionBearingRad-heading),Math.cos(bTurn.motionBearingRad-heading))));}
checks.sharpTurnSlows=minB<minA*.75;checks.sharpTurnRadiusNarrows=minRadiusB<minRadiusA*.6;checks.sharpTurnDecelBound=maxDecel<=C.decel+1e-6;checks.sharpTurnNoHeadingSnap=maxHeadingJump<.02;
cases.push({label:'sharpRetargetComparison',minSpeedA:minA,minSpeedB:minB,minRadiusA,minRadiusB,maxDecel,maxHeadingJump});
let follow=fresh();follow.positionM.z=50;const followTarget={x:1000,y:400};for(let i=0;i<18000;i++){followTarget.x+=8/60;move(follow,followTarget,{x:0,y:12},1/60,{targetVelocityMps:{x:8,y:0},headingRad:0});}
checks.movingFollowStation=Math.hypot(follow.positionM.x-followTarget.x,follow.positionM.y-followTarget.y)<2;checks.followWindAndVelocity=Math.hypot(follow.groundVelocityMps.x-8,follow.groundVelocityMps.y)<.1;checks.followAltitude=follow.positionM.z===50;
cases.push({label:'movingFollow',followTarget,final:follow});
const out={pass:Object.values(checks).every(Boolean),checks,cases};const file=process.argv[2];if(file)fs.writeFileSync(file,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({pass:out.pass,checks:Object.keys(checks).length,failed:Object.keys(checks).filter(k=>!checks[k]),cases:cases.map(c=>({label:c.label,d:c.distanceM,arrived:c.arrivedAt}))}));process.exit(out.pass?0:1);
