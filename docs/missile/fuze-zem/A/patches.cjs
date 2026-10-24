// Game changes under test. Parameters are frozen before flight comparisons.
const FUZE_CONST=`// SIM_TUNED: a new geometric look requires >=100ms without a qualified
  // range/beam return. This is a re-arm cadence, not a 60Hz Bernoulli trial.
  const FUZE_OPPORTUNITY_REARM_GAP_S_A = 0.100;`;
const FUZE_DRAW=`function _wip99FuzeDetectionDraw(m,target=null){
    // One independent missile-local stream, separate from simRandom/clutter/Pk.
    let stream=m._fuzeOpportunityRngA;
    if(!stream){
      const mid=(Number(m.id)||1)>>>0;
      stream=m._fuzeOpportunityRngA={state:_mix32((SIM_SEED_BASE>>>0)^Math.imul(mid,0x51f15e5d)^0xd37ec7a1)||1,draws:0,looks:new WeakMap()};
    }
    const key=target&&typeof target==='object'?target:m;
    const now=Number.isFinite(m.life)?m.life:0;
    let look=stream.looks.get(key);
    // Continuous eligible returns share one variate, even when Pd changes with
    // range. Thus encounter Pd is max(Pd), never 1-product(1-Pd) at 60Hz.
    if(!look || now<look.lastSeenS || now-look.lastSeenS>=FUZE_OPPORTUNITY_REARM_GAP_S_A-1e-9){
      const epoch=Math.max(0,Math.floor((now+1e-9)/FUZE_OPPORTUNITY_REARM_GAP_S_A));
      // The simulation-clock epoch decorrelates distinct observation occasions
      // even in diagnostics that reset the missile serial to 1 for every shot.
      stream.state=_xorshift32(_mix32(stream.state^Math.imul((epoch+1)>>>0,0x9e3779b1))||1);
      look={id:++stream.draws,openedS:now,lastSeenS:now,draw:(stream.state>>>0)/4294967296};
      stream.looks.set(key,look);
    }
    look.lastSeenS=now;
    m._wip99FuzeDetectionDraw=look.draw; // compatibility/debug value only
    m._fuzeOpportunityIdA=look.id;m._fuzeOpportunityOpenedSA=look.openedS;
    return look.draw;
  }`;
const ZEM_LINE_BEFORE='let ax=-k*zx, ay=-k*zy, az=-k*zz;';
const ZEM_LINE_AFTER='let ax=k*zx, ay=k*zy, az=k*zz;';
function definitions(symbols,variant){
 const out={},constants=[];
 if(variant.includes('D')){const d=require('./deterministic_patch.cjs').definitions(symbols);Object.assign(out,d.out);constants.push(...d.constants);}
 if(variant.includes('F')){
  constants.push(FUZE_CONST);out._wip99FuzeDetectionDraw=FUZE_DRAW;
  let info=symbols.get('_wip99FuzeDetectionInfo').code;
  info=info.replace('const draw=_wip99FuzeDetectionDraw(m);','const draw=_wip99FuzeDetectionDraw(m,target);');
  info=info.replace('return {detected:draw<=pd,pd,draw,closingMps','return {detected:draw<=pd,pd,draw,opportunityId:m._fuzeOpportunityIdA,opportunityOpenedS:m._fuzeOpportunityOpenedSA,closingMps');
  out._wip99FuzeDetectionInfo=info;
 }
 if(variant.includes('Z')){
  let z=symbols.get('computeZEMCorrectionV1').code;if(!z.includes(ZEM_LINE_BEFORE))throw Error('ZEM_BASELINE_MISMATCH');
  out.computeZEMCorrectionV1=z.replace('Compute predicted CPA (Zero-Effort Miss) and -ZEM direction acceleration','Compute predicted CPA; ZEM is target-minus-missile at future CPA')
   .replace('// a_ZEM = -k * 2 * ZEM / tgo^2','// Relative future position is r+v_rel*t-0.5*a_m*t^2: steer +ZEM.')
   .replace(ZEM_LINE_BEFORE,ZEM_LINE_AFTER);
 }
 if(variant.includes('T')){const t=require('./term_patch.cjs').definitions(symbols);Object.assign(out,t.out);constants.push(...t.constants);}
 return{out,constants};
}
module.exports={definitions,FUZE_CONST,FUZE_DRAW,ZEM_LINE_BEFORE,ZEM_LINE_AFTER};
