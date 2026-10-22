/*
 * AEGIS v48 B4 Dynamic Loft — portable source transplant (game-only).
 * Node .js (CommonJS). No automatic global patches. This transforms the
 * unpacked c55-game-main JavaScript as an exact-match, fail-closed codemod.
 * It does NOT create a standalone B4 runtime plugin: B4 depends on many local
 * game-simulation variables and must be inserted at the original call sites.
 *
 * Targets ONLY: SM-2MR B4 profile + ESSM Block 2 B4 profile and dynamic shelf.
 * SM-2ER, SM-6, Harpoon, RAM, propulsion, seekers, damage are untouched.
 */
'use strict';

const PATCH_ID = 'V48_GAME_B4_DYNAMIC_TEST';
const LOFT_ANCHOR = 'function loftB4UpdatePlan(m,ctx,plan){';
const HELPER_INJECTION = `// V48-GAME-B4-EXP: game-only smooth dynamic shelf controller for two legacy profiles.
  // Does not modify propulsion, aerodynamic forces, speed, fuel, seekers, or hit calculations.
  window.__AEGIS_GAME_B4_EXPERIMENT__=Object.freeze({id:'V48_GAME_B4_DYNAMIC_TEST',profiles:['SM2MR_B4','ESSM_B4'],originalPreserved:true,experimental:true});
  function gameB4ReplanShelf(m,s,p,ctx,age,r,alt){
    if(s.mode==='DIRECT'||s.phase==='DIVE'||m.vlsPhase||m.pitchoverPhase)return;
    if(s.lastGameShelfReviewS!=null && age-s.lastGameShelfReviewS<0.50)return;
    s.lastGameShelfReviewS=age;
    // Preserve initial-route intent but allow changes in target position and remaining game range.
    // In contrast to rerunning the entire route from scratch, the live term is deliberately small.
    const den=Math.max(1,p.fullLoftKm-p.startKm);
    const initialFactor=_samSmooth01((s.initialRangeKm-p.startKm)/den);
    const liveFactor=_samSmooth01((r-p.startKm)/den);
    const factor=clamp(initialFactor*0.84+liveFactor*0.16,0,1);
    let goal=lerp(p.shelfMinM,p.shelfMaxM,factor);
    // If the observed target changes altitude, update the game waypoint without assuming
    // the target has any special category or inventing a new radar contact.
    const targetAltitude=Math.max(0,Number(ctx.tgtAltM)||0);
    goal=Math.max(goal,Math.min(p.shelfMaxM,targetAltitude));
    // Late in the game run, a slowed projectile should not chase a stale high waypoint.
    const v=Math.max(0,s.speedMps||0);
    const late=age>Math.max(8,(Number(m.burnTotal)||0)*0.60);
    const lowSpeed=late?clamp((p.energyReleaseMps+95-v)/Math.max(160,p.energyReleaseMps*.55),0,1):0;
    goal=lerp(goal,Math.min(goal,Math.max(p.shelfMinM,alt+1750)),lowSpeed*.45);
    s.gameDesiredShelfM=clamp(goal,p.shelfMinM,p.shelfMaxM);
    s.gameShelfReplans=(s.gameShelfReplans||0)+1;
  }
  `;
const CURRENT_PROFILE_MR = "SM2MR_ADAPTIVE_ENERGY_LOFT:Object.freeze({id:'SM2MR_B4',mode:'LOFT',rangeGoalKm:160,fullLoftKm:160,startKm:32,shelfMinM:7500,shelfMaxM:17500,";
const NEW_PROFILE_MR = CURRENT_PROFILE_MR.replace('shelfMaxM:17500','shelfMaxM:22500');
const CURRENT_PROFILE_ESSM = "ESSM_BLK2_ADAPTIVE_LAUNCH_LOFT:Object.freeze({id:'ESSM_B4',mode:'MILD_LOFT',rangeGoalKm:null,fullLoftKm:50,startKm:24,shelfMinM:900,shelfMaxM:3500,";
const NEW_PROFILE_ESSM = CURRENT_PROFILE_ESSM.replace('shelfMaxM:3500','shelfMaxM:7500');
const BEFORE_TICK = `      s.energyHeightM=alt+s.speedMps*s.speedMps/(2*G0);
      if(s.mode!=='DIRECT'&&!m.vlsPhase&&!m.pitchoverPhase){`;
const AFTER_TICK = `      s.energyHeightM=alt+s.speedMps*s.speedMps/(2*G0);
      // Only two legacy game routes opt in; ER/SM-6 keep their exact baseline logic.
      if((p.id==='SM2MR_B4'||p.id==='ESSM_B4') && s.mode!=='DIRECT' && s.phase!=='DIVE'){
        gameB4ReplanShelf(m,s,p,ctx,age,r,alt);
        if(Number.isFinite(s.gameDesiredShelfM)){
          // Per-tick change clamp prevents abrupt waypoint jumps between logic ticks.
          const changeLimit=(p.id==='ESSM_B4'?720:1100)*SIM_FIXED_DT;
          s.shelfM+=clamp(s.gameDesiredShelfM-s.shelfM,-changeLimit,changeLimit);
        }
      }
      if(s.mode!=='DIRECT'&&!m.vlsPhase&&!m.pitchoverPhase){`;
const BEFORE_DEBUG = 'plan.statefulProfileId=p.id;plan.statefulPhase=s.phase;plan.statefulShelfM=s.shelfM;';
const AFTER_DEBUG = 'plan.statefulProfileId=p.id;plan.statefulPhase=s.phase;plan.statefulShelfM=s.shelfM;plan.gameDynamicShelfGoalM=s.gameDesiredShelfM??null;plan.gameDynamicShelfReplans=s.gameShelfReplans??0;';

function count(s, part) {
  return s.split(part).length - 1;
}
function requireCount(s, part, wanted, label) {
  const found = count(s, part);
  if (found !== wanted) throw Error(`Unsupported B4 source (${label}): expected ${wanted} matching anchor(s), got ${found}. Refusing partial patch.`);
}
function applyAegisB4DynamicLoft(unpackedSource) {
  if (typeof unpackedSource !== 'string') throw TypeError('Expected unpacked game-main JS source string');
  const wasPatched = unpackedSource.includes('function gameB4ReplanShelf(m,s,p,ctx,age,r,alt){');
  if (wasPatched) {
    requireCount(unpackedSource,'function gameB4ReplanShelf(m,s,p,ctx,age,r,alt){',2,'already-patched helpers');
    requireCount(unpackedSource,NEW_PROFILE_MR,1,'already-patched MR profile');
    requireCount(unpackedSource,NEW_PROFILE_ESSM,1,'already-patched ESSM profile');
    requireCount(unpackedSource,AFTER_DEBUG,2,'already-patched debug');
    requireCount(unpackedSource,AFTER_TICK,2,'already-patched dynamic step');
    return {source:unpackedSource, status:'already_applied', changes:[]};
  }
  // Exact v48 anchors. On newer/modified branches, STOP; do not guess.
  requireCount(unpackedSource,CURRENT_PROFILE_MR,1,'MR profile');
  requireCount(unpackedSource,CURRENT_PROFILE_ESSM,1,'ESSM profile');
  requireCount(unpackedSource,LOFT_ANCHOR,2,'two B4 function definitions');
  requireCount(unpackedSource,BEFORE_TICK,2,'per-tick update entry');
  requireCount(unpackedSource,BEFORE_DEBUG,2,'debug plan state');
  let next=unpackedSource.replace(CURRENT_PROFILE_MR,NEW_PROFILE_MR)
    .replace(CURRENT_PROFILE_ESSM,NEW_PROFILE_ESSM)
    .replaceAll(LOFT_ANCHOR,HELPER_INJECTION+LOFT_ANCHOR)
    .replaceAll(BEFORE_TICK,AFTER_TICK)
    .replaceAll(BEFORE_DEBUG,AFTER_DEBUG);
  requireCount(next,'function gameB4ReplanShelf(m,s,p,ctx,age,r,alt){',2,'inserted helper');
  requireCount(next,AFTER_TICK,2,'inserted tick loop');
  requireCount(next,AFTER_DEBUG,2,'inserted debug');
  requireCount(next,NEW_PROFILE_MR,1,'changed MR cap');
  requireCount(next,NEW_PROFILE_ESSM,1,'changed ESSM cap');
  return {source:next,status:'patched',changes:[
    'MR shelfMaxM 17500 -> 22500', 'ESSM shelfMaxM 3500 -> 7500',
    'gameB4ReplanShelf helper before both B4 definitions',
    '0.5s target-shelf update / smooth per-tick shelf step in both B4 definitions',
    'two read-only debug plan fields'
  ]};
}
module.exports = {PATCH_ID, applyAegisB4DynamicLoft};
