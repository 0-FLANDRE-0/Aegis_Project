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
const out={pass:Object.values(checks).every(Boolean),checks,cases};const file=process.argv[2];if(file)fs.writeFileSync(file,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({pass:out.pass,checks:Object.keys(checks).length,failed:Object.keys(checks).filter(k=>!checks[k]),cases:cases.map(c=>({label:c.label,d:c.distanceM,arrived:c.arrivedAt}))}));process.exit(out.pass?0:1);
