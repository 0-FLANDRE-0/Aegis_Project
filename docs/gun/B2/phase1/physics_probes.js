// TEST ONLY: isolated physical inputs; no live control/track is fed truth.
window.__B2_PHYSICS_PROBES__=()=>{
 const saved=gunB1PhysicalAir,oldFlags={...gunB2Flags},rng=SIM_RNG_STATE,results={};
 try{
  function pass(dt,cross=5,armed=true,speed=800){
   const target={id:9201,label:'Kh-35U',x:0,y:metersToWorld(cross),z:100,heading:Math.PI/2,alive:true},row={kind:'ASM',object:target,positionM:{x:0,y:cross,z:100},velocityMps:{x:0,y:0,z:0}},p={id:'MK45-71',ageS:0,flightDistanceM:armed?500:0,velocityMps:{x:speed,y:0,z:0},positionM:{x:-40,y:0,z:100},mffB1:{etTimeS:100,clutterBudget:Infinity,clutterExposure:0}};gunB1PhysicalAir=()=>[row];let event=null;
   for(let i=0;i<100&&p.positionM.x<40;i++){const prev={...p.positionM},next={x:prev.x+speed*dt,y:0,z:100},e=gunB1ShellEvent(p,prev,next,dt);if(e){event={...e,timeS:p.ageS+e.t*dt};break;}p.positionM=next;p.ageS+=dt;p.flightDistanceM+=speed*dt;}
   return {event,passes:p._gunB2Fuze?.passes??0,clutterExposure:p.mffB1.clutterExposure,globalRng:SIM_RNG_STATE};
  }
  gunB2Configure({fuze:true,fragments:true});results.timeSteps=[1/30,1/60,1/120].map(dt=>({dt,...pass(dt)}));results.outsidePattern=pass(1/30,0);results.unarmed=pass(1/60,5,false);results.fast=pass(1/30,5,true,1900);
  gunB1PhysicalAir=()=>[];const make=()=>({id:'MK45-9',ageS:.12,flightDistanceM:500,velocityMps:{x:800,y:0,z:0},mffB1:{etTimeS:.123,clutterBudget:Infinity,clutterExposure:0}});results.et=gunB1ShellEvent(make(),{x:0,y:0,z:100},{x:80,y:0,z:100},.1);
  const clutter=()=>({id:'MK45-9',ageS:1,flightDistanceM:500,velocityMps:{x:700,y:0,z:-100},mffB1:{etTimeS:100,clutterBudget:.00001,clutterExposure:0}}),a=clutter(),b=clutter(),prev={x:0,y:0,z:1},next={x:70,y:0,z:-9};gunB2Configure({fuze:false});const old=gunB1ShellEvent(a,prev,next,.1);gunB2Configure({fuze:true});const fresh=gunB1ShellEvent(b,prev,next,.1);results.clutter={old,fresh,exposureOld:a.mffB1.clutterExposure,exposureNew:b.mffB1.clutterExposure};
  const vf=_wip88GurneyFragmentSpeed(GUN_B1_SPEC.fragments),v={x:800,y:0,z:0},tv={x:0,y:0,z:0},flight=.005;
  function field(theta,targetVelocity=tv,carrier=v){const v=carrier,r={x:(v.x+vf*Math.cos(theta)-targetVelocity.x)*flight,y:(vf*Math.sin(theta)-targetVelocity.y)*flight,z:-targetVelocity.z*flight},kin=_wip88InterceptKinematics(v.x,v.y,v.z,targetVelocity.x,targetVelocity.y,targetVelocity.z);return gunB2FragmentDetail(Math.hypot(r.x,r.y,r.z),'MFF_127_SIM','Kh-35U',kin,r,v,targetVelocity);}
  results.fragmentInside=field(Math.PI/2);results.fragmentForward=field(0);results.fragmentAft=field(Math.PI);results.fragmentMoving=field(Math.PI/2,{x:250,y:100,z:0});results.fragmentFrameRows=[300,800,1500].map(speed=>field(Math.PI/2,tv,{x:speed,y:0,z:0}));results.expectedBodySolidAngleSr=4*Math.PI*Math.sin(deg(GUN_B2_SPEC.fragments.halfAngleDeg));results.expectedCoverageFragments=GUN_B1_SPEC.fragments.fragmentCount;results.fragmentUnknown=gunB2FragmentationPk(10,'MFF_127_SIM','Kh-35U',{});
  results.rngBefore=rng;results.rngAfter=SIM_RNG_STATE;results.core=window.__CORE_SELFTEST_FAILURES__;return results;
 }finally{gunB1PhysicalAir=saved;gunB2Configure(oldFlags);}
};
