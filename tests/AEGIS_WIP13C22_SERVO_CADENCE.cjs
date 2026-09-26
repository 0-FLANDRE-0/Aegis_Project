const fs=require('fs'),vm=require('vm'),assert=require('assert'),zlib=require('zlib');
const html=fs.readFileSync(process.argv[2]||'Aegis_SIM_v48_WIP13C22.html','utf8');
const record=html.match(/<script type=\"application\/octet-stream\" data-c55-index=\"13\">([^<]+)<\/script>/);
if(!record)throw Error('MISSING_C55_MAIN_RECORD');
const src=zlib.gunzipSync(Buffer.from(record[1],'base64')).toString('utf8');
const start=src.indexOf('  const SPG62_SERVO_POLICY=');
const end=src.indexOf('  const SPG62_RESERVATIONS =',start);
assert(start>0&&end>start);
const units=src.slice(start,end);
function setup(bearingDeg,initialDeg=0){
 const deg=v=>v*Math.PI/180, angNorm=v=>Math.atan2(Math.sin(v),Math.cos(v));
 const mount={illId:0,azRad:deg(initialDeg),elRad:0,azRateRadS:0,elRateRadS:0,commandAzRad:0,commandElRad:0,targetTrackId:null,mode:'HOLD',aligned:false,settleS:0,emitting:false};
 const tr={x:Math.cos(deg(bearingDeg))*1000,y:Math.sin(deg(bearingDeg))*1000,z:0};
 const row={targetId:42,illId:0,cueStartT:0,startT:0,endT:20};
 const globals={Math,Number,Map,deg,angNorm,clamp:(v,a,b)=>Math.max(a,Math.min(b,v)),worldToMeters:v=>v,
   shipNav:{heading:0},_sarhIlluminatorWorldState:()=>({x:0,y:0,z:0}),
   SPG62_ILLUMINATORS:[{id:0}],ACTIVE_SHIP_RUNTIME:{combatSystem:{fireControl:{spg62Servo:{mounts:[mount]}}}},
   SPG62_ENGAGEMENT_STATE:new Map(),SPG62_RESERVATIONS:new Map([[0,[row]]]),
   SPG62_RESERVATION_STATE:new Map([[42,row]]),tracks:new Map([[42,tr]]),
   spg62ActiveReservationForTarget:id=>id===42?row:null,
   spg62CurrentIlluminatorScore:()=>1,wip121TargetSupportBlocked:()=>false,
   shipEquipmentOfflineV1:()=>false,emconActive:false,
   SPG62_RESERVATION_POLICY:{minScore:.05}};
 const context=vm.createContext(globals);vm.runInContext(units+'\nthis.drive={step:spg62ServoStep,ready:spg62ServoReady,boresight:spg62ServoBoresight,cease:spg62ServoCeaseTarget,policy:SPG62_SERVO_POLICY};',context);
 return {context,mount,tr,row,drive:context.drive};
}
const dt=1/60,seq=setup(90);let maxAcc=0,maxRate=0,firstIllTick=-1;
for(let k=0;k<500;k++){
 const old=seq.mount.azRateRadS;seq.drive.step(dt,k*dt);
 maxAcc=Math.max(maxAcc,Math.abs(seq.mount.azRateRadS-old)/dt);
 maxRate=Math.max(maxRate,Math.abs(seq.mount.azRateRadS));
 if(seq.drive.ready(0,42)&&firstIllTick<0)firstIllTick=k;
 if(k===0)assert(Math.abs(seq.mount.azRad)<.01,'90 degree target jumped on first tick');
 if(k<10)assert(!seq.drive.ready(0,42),'premature illumination');
}
assert(maxAcc<=2.5000001,`exceeded angular acceleration ${maxAcc}`);
assert(maxRate<=seq.drive.policy.maxTrainRateRadS+1e-9);
assert(firstIllTick>15 && firstIllTick<480,'settle never completed');
assert(Math.abs(seq.mount.azRad-Math.PI/2)<.01,'final bearing not aligned');
const wrap=setup(-179,179);wrap.drive.step(dt,0);
assert(wrap.mount.azRateRadS>0,'wrap took long negative route');
for(let k=1;k<240;k++)wrap.drive.step(dt,k*dt);
assert(wrap.drive.ready(0,42),'wrap alignment not reached');
const silent=setup(70);silent.drive.step(dt,0);silent.context.SPG62_RESERVATIONS.get(0).length=0;
silent.drive.step(dt,dt);assert(silent.mount.mode==='HOLD'&&!silent.mount.emitting,'RF persists after support withdrawal');
const seq2=setup(90);for(let k=0;k<500;k++)seq2.drive.step(dt,k*dt);
assert(Math.abs(seq.mount.azRad-seq2.mount.azRad)<1e-12&&seq.mount.mode===seq2.mount.mode,'fixed tick nondeterminism');
for(const ticksPerRender of [1,8,16,64]){
 const caseAtScale=setup(90);
 for(let frame=0;frame<Math.ceil(500/ticksPerRender);frame++)for(let j=0;j<ticksPerRender&&frame*ticksPerRender+j<500;j++){
   const k=frame*ticksPerRender+j;caseAtScale.drive.step(dt,k*dt);
 }
 assert(Math.abs(caseAtScale.mount.azRad-seq.mount.azRad)<1e-12&&caseAtScale.mount.mode===seq.mount.mode,
   `render cadence ${ticksPerRender} altered fixed-tick servo`);
}
// Exercise the actual SARH allocator against a scheduled anonymous track.
const integration=setup(90),g=integration.context,missile={id:777,assignedTargetId:42,dead:false,isESSM:false,seekerType:'SARH',guidanceCore:'v1',state:'DL',sarhReceiverStandby:false};
Object.assign(g,{missiles:[missile],simStepCounter:0,SIM_FIXED_DT:dt,aircraft:{x:()=>0,y:()=>0},
 spg62MaybeReplanReservations:()=>{},spg62ResetReservations:()=>{g.SPG62_RESERVATIONS.get(0).length=0;g.SPG62_RESERVATION_STATE.clear()},
 spg62ReservationNowS:()=>g.simStepCounter*dt,
 clearSpg62MissileAssignment:m=>{m.sarhAlive=false;m._illuminatorGuided=false;m._illuminatorId=null;m._illQuality=0},
 spg62SupportClassForMissile:()=>3,isAegisAvailable:()=>true,buildSpg62Engagements:()=>[],sortSpg62Engagements:()=>[],emconActive:false});
const alloc=src.slice(src.indexOf('  function allocateSARH(){'),src.indexOf('  function updateModeButtonLabel(){'));
vm.runInContext(alloc+'\nthis.allocate=allocateSARH;',g);
let firstEmission=-1;
for(let k=0;k<260;k++){
 g.simStepCounter=k;integration.drive.step(dt,k*dt);g.allocate();
 if(k===0){assert(!missile.sarhAlive&&!integration.mount.emitting&&g.SPG62_ENGAGEMENT_STATE.size===0,'instant illumination before slew');}
 if(missile.sarhAlive&&firstEmission<0)firstEmission=k;
 if(missile.sarhAlive)assert(integration.mount.emitting&&g.SPG62_ENGAGEMENT_STATE.get(42)?.illId===0,'RF ownership mismatch');
}
assert(firstEmission>15&&firstEmission<260,'SARH never received physical illumination');
g.SPG62_RESERVATIONS.get(0).length=0;g.SPG62_RESERVATION_STATE.clear();g.simStepCounter++;
integration.drive.step(dt,g.simStepCounter*dt);g.allocate();assert(!missile.sarhAlive&&!integration.mount.emitting&&g.SPG62_ENGAGEMENT_STATE.size===0,'support withdrawal left RF on');
console.log(JSON.stringify({checks:'PASS',firstReadyS:firstIllTick*dt,firstEmissionS:firstEmission*dt,maxAccelerationRadS2:maxAcc,maxRateRadS:maxRate,determinism:'exact',renderCadences:[1,8,16,64],silentWithdrawal:true}));
