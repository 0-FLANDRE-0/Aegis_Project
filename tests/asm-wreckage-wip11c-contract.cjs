const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12B.html');
const archived = path.join(__dirname, '../archive/v48/WIP11B/Aegis_SIM_v48_WIP11B.html');
const rootBaseline = path.join(__dirname, '../Aegis_SIM_v48_WIP11B.html');
const baselineFile = process.argv[3] || process.env.WRECK_BASELINE_SIM_FILE || (fs.existsSync(archived) ? archived : rootBaseline);
const html = fs.readFileSync(file, 'utf8');
const baseline = fs.readFileSync(baselineFile, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(source => source.trim());
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename:`${path.basename(file)}#inline-${index + 1}` });

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
function functionSource(source,name){
  const needle=`function ${name}(`,start=source.indexOf(needle);if(start<0)return null;
  const open=source.indexOf('{',start);let depth=1,state='code',escape=false,templateTargets=[];
  for(let i=open+1;i<source.length;i++){
    const c=source[i],n=source[i+1];
    if(state==='line'){if(c==='\n')state='code';continue;}
    if(state==='block'){if(c==='*'&&n==='/'){state='code';i++;}continue;}
    if(state==='single'||state==='double'){if(escape){escape=false;continue;}if(c==='\\'){escape=true;continue;}if((state==='single'&&c==="'")||(state==='double'&&c==='"'))state='code';continue;}
    if(state==='template'){if(escape){escape=false;continue;}if(c==='\\'){escape=true;continue;}if(c==='`'){state='code';continue;}if(c==='$'&&n==='{'){depth++;templateTargets.push(depth-1);state='code';i++;}continue;}
    if(c==='/'&&n==='/'){state='line';i++;continue;}if(c==='/'&&n==='*'){state='block';i++;continue;}
    if(c==="'"){state='single';continue;}if(c==='"'){state='double';continue;}if(c==='`'){state='template';continue;}
    if(c==='{'){depth++;continue;}if(c==='}'){depth--;if(templateTargets.length&&depth===templateTargets.at(-1)){templateTargets.pop();state='template';continue;}if(depth===0)return source.slice(start,i+1);}
  }
  throw new Error(`unterminated function ${name}`);
}
const exactAuthorityFunctions=['_wip88InterceptKinematics','_wip88FragmentationPk','computeInterceptPk','getGuidanceTargetStateV1','computeGuidanceAccelV1','applyGuidanceKernelV1ToLegacyRates','updateMissile','ramGuidanceTrackForAuthority','ciwsGunBallisticInterceptSolution','ciwsInterceptSolution','hardKillKinematicInterceptEstimate'];
const guidanceAndPkExactWip11bParity=exactAuthorityFunctions.every(name=>functionSource(html,name)===functionSource(baseline,name));
const applyNow=functionSource(html,'applyInterceptResult')??'',applyBase=functionSource(baseline,'applyInterceptResult')??'',killDecisionNeedles=['if(simRandom() < pk)','else if(pk > 0.1 && simRandom() < pk * 0.7)','rand(15, 40)',"return 'KILL'","return 'STRUCT_FAIL'","return 'DAMAGED'","return 'MISS'"];
const bdaDecisionSource=['wip11cUpdateObservedSeaImpactTrack','wip11cTerminalEffectTrackId','wip121TerminalEffectCorrelationCandidates','wip121RecordFriendlyInterceptEvent','wip121KillPlausibility','wip121TargetSupportBlocked','wip121BdaTrackPresentation','wip121ReleaseTargetFireControlSupport','wip118UpdateKillAssessment'].map(name=>functionSource(html,name)??'').join('\n');
const core = html.slice(html.indexOf('// ===== V48 WIP11C ASM WRECKAGE'), html.indexOf('function wip173RecordInterceptBurst'));
const fixedTick = html.slice(html.indexOf('function simulateFixedTick'), html.indexOf('// ===== WIP150 RUNTIME FAULT'));
const checks = {
  title: html.includes('<title>AEGIS v48 WIP11C — ASM Wreckage and Water-Surface Effects</title>') || html.includes('<title>AEGIS v48 WIP12A — Common Terminal Ballistics Foundation</title>') || html.includes('<title>AEGIS v48 WIP12B — Live Ordnance Terminal Effects and Damage Visualization</title>'),
  syntax: scripts.length > 0,
  exactWip11bBaselinePresent: baseline.includes('<title>AEGIS v48 WIP11B — Operational Import Safety Hardening</title>'),
  threatAndWreckAuthoritySplit: hasAll("const asmWreckage=[]", 'hostileMissiles:null,asmWreckage:null', 'e.world.entities.asmWreckage=asmWreckage', "threatPolicy:'RETIRED_IMMEDIATELY'"),
  deferredFinalStateCreation: fixedTick.indexOf('updateCIWS(dt)') < fixedTick.indexOf('wip11cFinalizeQueuedAsmRetirement(em)') && fixedTick.indexOf('wip11cFinalizeQueuedAsmRetirement(em)') < fixedTick.indexOf('enemyMissiles.splice(i,1)'),
  allCombatKillPathsQueueWreckage: hasAll("wip11cQueueAsmRetirement(em,'INTERCEPT_KILL'", "wip11cQueueAsmRetirement(em,'INTERCEPT_STRUCTURAL_FAILURE'", "wip11cQueueAsmRetirement(em,'PHALANX_KILL'", "wip11cQueueAsmRetirement(em,'PHALANX_STRUCTURAL_FAILURE'", "wip11cQueueAsmRetirement(em,'WARHEAD_AIRBURST'", "wip11cQueueAsmRetirement(em,'DELAYED_STRUCTURAL_FAILURE'"),
  componentDamageCoupled: hasAll('function wip11cAsmDamageSnapshot(em)', 'fuelDamagePct:plan.damage.fuel', 'burning:plan.burning', 'systemDamage:{...plan.damage}', "mode=airburst?'EXPLOSIVE_BREAKUP':structural?'STRUCTURAL_BREAKUP':'INTERCEPT_BREAKUP'"),
  fixedStepBallistics: hasAll('function updateAsmWreckageV48Wip11C(dt)', 'airDensityKgM3(Math.max(0,w.z))', 'w.vzMps-=9.80665*step', 'w.x+=mpsToWorldSpeed(w.vxMps)*step', 'w.yaw=angNorm(w.yaw+w.yawRateRadS*step)'),
  independentRandomness: hasAll("randomness:'INDEPENDENT_DETERMINISTIC_STREAM'", 'function wip11cIndependentRng(seed)', 'wip11cRetirementSeed(em,cause)') && !core.includes('simRandom()') && !core.includes('rand('),
  waterSurfaceAuthority: hasAll("schema:'AEGIS_WATER_SURFACE_EVENT_V48_WIP11C'", "'WATER_ENTRY'", "'WATER_SURFACE_BLAST'", 'function wip11cMaybeRecordSurfaceBlast(opt={})', 'if(heightM>couplingHeightM)return null'),
  waterPresentationLayers: hasAll('spawnWaterColumn(pos,k,opt={})', "kind:'WATER_COLUMN'", 'spawnWaterSurfaceRings(pos,k,opt={})', "kind:'WATER_RING'", "kind:'WATER_FOAM'", "else if(ev.type==='WATER_ENTRY')", "else if(ev.type==='WATER_SURFACE_BLAST')"),
  physicalWreckRenderer: hasAll('function wip11cWreckRenderState(w)', 'asmWreckage:asmWreckage.filter(w=>w.alive).map(wip11cWreckRenderState)', 'buildAsmWreckMesh(s)', 'syncAsmWreckVisuals(st,dt)', 'this.syncAsmWreckVisuals(st,dt)', 'flameAcc:0', 'wreckSmoke:true'),
  interceptorSmokePersistence: hasAll("schema:'AEGIS_INTERCEPTOR_SMOKE_VISUAL_V48_WIP11C'", 'schemaVersion:3', "weaponKinds:Object.freeze(['SM2','ESSM','RAM'])", 'lifetimeMultiplier:8', 'samplingSpacingMultiplier:3.5', 'expansionRateMultiplier:.15', 'agedTrailStart01:.36', 'agedTrailKeepNumerator:2', 'agedTrailKeepDenominator:3', 'agedExpansionBoost:1.8', 'agedOpacityHoldEnd01:.86', 'maxInterceptorParticles:9000', 'maxGlobalSmokeParticles:12000', 'overloadPolicy:\'THIN_AGED_INTERCEPTOR_SMOKE_EVENLY_FIRST\'', 'interceptorTrail:true', 'wip11cScaleInterceptorSmoke(kind,base)', 'wip11cInterceptorSmokeAgeVisual(age01)', 'wip11cInterceptorSmokeAudit()', 'longTrailBoundedLoad'),
  asmSmokeAltitudeGate: hasAll("schema:'AEGIS_ASM_SMOKE_ALTITUDE_VISUAL_V48_WIP11C'", "smokeCapableLabels:Object.freeze(['Kh-32'])", 'hiddenAtOrBelowM:5000', 'fullDensityAtOrAboveM:8000', "lowAltitudePolicy:'NO_NEW_SMOKE_PARTICLES'", "kh35uPolicy:'TURBOJET_NO_SMOKE_CLOUD'", 'asmSmokeAltitudeFactor(altM)', 'wip11cAsmSmokeAltitudeAudit()', 'asmSmokeVisibility>0'),
  bdaStateAndAuthorityGate: hasAll("KILL_ASSESSMENT:'KILL_ASSESSMENT'", "killAssessment?'KILL_ASSESSMENT'", "state=kp.confirmed?'DESTROYED':'KILL_ASSESSMENT'", "assessment?.state==='KILL_ASSESSMENT'", "assessmentState==='KILL_ASSESSMENT'"),
  breakupReportBridge: hasAll('wip121RecordFriendlyInterceptEvent(trackId', "evidence:'DIRECT_BREAKUP'", "source:'WIP11C_ASM_RETIREMENT'", "source:'INTERCEPTOR_TERMINAL_REPORT'", 'bdaDirectBreakupConfirmS:0.35', 'bdaFuzeNoReturnConfirmS:1.5', 'measurementStep>effectStep'),
  anonymousTrackBdaProvenance: hasAll('function wip11cFriendlyWeaponTrackId(interceptor,weaponType)', 'function wip11cRememberEngagementTrack(em,trackId', 'function wip11cRetirementTrackId(em,opt={})', 'const assignedTrackId=wip11cFriendlyWeaponTrackId(interceptor,weaponType)', "directBreakup?'DIRECT_BREAKUP':'FUZE_DETONATION'", 'engagementTrackId:phalanx.trackingTrackId', "applyInterceptResult(pkRaw,tgt,'SeaRAM',rm.targetId)", 'mergeWindowS=Math.max(.12,WIP118_KILL_ASSESSMENT_POLICY.schedulerFrameS+SIM_FIXED_DT*2)'),
  directBreakupPromotionRefreshesProvenance: hasAll('rank>oldRank)Object.assign(nearby,{step:reportStep,effectStep,t:now', "rank===oldRank&&evidence==='DIRECT_BREAKUP'", 'terminalReport:terminalReport??nearby.terminalReport', 'resolvedByReturnStep:null'),
  terminalEffectAliasCorrelation: hasAll("schema:'AEGIS_TERMINAL_EFFECT_REPORT_V48_WIP11C'", 'function wip11cTerminalEffectTrackId(report)', 'function wip121TerminalEffectCorrelationCandidates(originTrackId,event)', "source:'TERMINAL_EFFECT_TRACK_CORRELATION'", 'measurementStep>effectStep', 'skipTerminalCorrelation:true', 'correlatedTrackIds'),
  reacquireTransfersEveryEffector: hasAll('for(const rm of ramMissiles)if(rm.alive&&rm.targetId===oldId)rm.targetId=newId', 'for(const b of ciwsBullets)if(b.engagementTrackId===oldId)b.engagementTrackId=newId', 'if(mount.trackingTrackId===oldId)mount.trackingTrackId=newId', 'SPG62_ENGAGEMENT_STATE.delete(oldId)', 'SPG62_RESERVATION_STATE.delete(oldId)', 'if(selectedLockId===oldId)selectedLockId=newId', "phase:allowFresh?'POST_LOSS_SAME_FRAME':'PREEXISTING_LOST'", 'wip121TryAliasReacquire(id,tr,{allowExistingFresh:true})'),
  ghostMemAndSpgRelease: hasAll('bdaDestroyedDisplayHoldS:1.25', 'function wip121BdaTrackPresentation(tr)', 'function wip121TargetSupportBlocked(trackId,tr=null)', "state==='KILL_ASSESSMENT'&&evidence==='DIRECT_BREAKUP'", 'function wip121ReleaseTargetFireControlSupport(trackId', 'SPG62_ENGAGEMENT_STATE.delete(id)', 'SPG62_RESERVATION_STATE.delete(id)', 'if(wip121BdaTrackPresentation(tr).hidden)return false', 'if(wip121TargetSupportBlocked(targetId,tr))return false', "tag=bdaPresentation.kind", "if(vv > 0.02&&!isBdaTrack)"),
  observedSeaImpactCoastRetirement: hasAll('WIP11C_OBSERVED_SEA_IMPACT_TRACK_POLICY', 'function wip11cUpdateObservedSeaImpactTrack(tr,dt)', 'minDescentMps:45', 'maxPredictedImpactTimeS:.35', 'shipClearanceMarginM:25', 'impactTimeS<=P.maxPredictedImpactTimeS', 'shipClearanceM>WIP118_SHIP_ENVELOPE_RADIUS_M+P.shipClearanceMarginM', 'altM<=P.maxEstimatedAltitudeM', "wip121ReleaseTargetFireControlSupport(tr.trackId,'OBSERVED_SEA_IMPACT')", "kind:'SEA_IMPACT'", "evidence:'OBSERVED_SEA_IMPACT'", 'wip11cClearObservedSeaImpactTrack(tr);'),
  physicalVlsLaunchAzimuthPreserved: hasAll('function _wip156CreateVlsInCellState(isESSM,launchAzimuthRad=null)', 'launchAzimuthRad:Number.isFinite(launchAzimuthRad)?angNorm(launchAzimuthRad):null', 'const launchAzimuth=Number.isFinite(c.launchAzimuthRad)?c.launchAzimuthRad', 'm.heading=angNorm(launchAzimuth)', '_wip156CreateVlsInCellState(false,launchBodyHeading)', '_wip156CreateVlsInCellState(true,launchBodyHeading)', 'launchAzimuth=m._vlsInCell?.launchAzimuthRad'),
  bdaDecisionNoTruthDeadRead: !bdaDecisionSource.includes('truthEnded') && !bdaDecisionSource.includes('enemyMissiles') && !bdaDecisionSource.includes('truthObjectForTrackV27'),
  guidanceAndPkExactWip11bParity,
  killProbabilityThresholdsPreserved: killDecisionNeedles.every(q=>applyNow.includes(q)&&applyBase.includes(q))&&(applyNow.match(/simRandom\(\)/g)?.length??0)===(applyBase.match(/simRandom\(\)/g)?.length??0),
  noDuplicateFakeBreakup: hasAll('target&&!ev.physicalWreckage', "if(!ev.physicalWreckage)this.spawnAsmBreakup"),
  residualImpactBounded: hasAll("residualShipImpactPolicy:'LEGACY_DUD_COMPAT_KINETIC_ONLY__TERMINAL_WARHEAD_MIGRATION_DEFERRED_TO_WIP12A'", 'function wip11cResolveWreckShipImpact(w)', "wip173PushVisualEvent('SHIP_WRECK_IMPACT'", 'explosiveMassKg:0'),
  movingWorldAndReset: hasAll('for(const w of asmWreckage){if(w.alive){w.x-=dx;w.y-=dy;w.prevX-=dx;w.prevY-=dy;}}', 'resetAsmWreckageV48Wip11C();', 'waterSurfaceEvents:WIP11C_WATER_SURFACE_EVENTS.length'),
  operationalZeroMutationExtended: hasAll('wreckIds:asmWreckage.map(q=>q.id)', 'waterSurfaceEventIds:WIP11C_WATER_SURFACE_EVENTS.map(q=>q.id)', 'wreckSerial:WIP11C_WRECK_SERIAL', 'waterEventSerial:WIP11C_WATER_EVENT_SERIAL'),
  diagnosticSurface: hasAll('wip11cWreckageContract:()', 'wip11cWreckageSnapshot:()', 'wip11cCreateWreckageFixture:', 'wip11cDiagnosticKillLiveAsm:', 'wip11cWreckageDiagnostic:()'),
  priorSafetyPreserved: hasAll("schema:'AEGIS_OPERATIONAL_IMPORT_SAFETY_V48_WIP11B'", "invalidInputMutationPolicy:'ZERO_AUTHORITATIVE_MUTATION'", "schema:'AEGIS_MATERIAL_PROTECTION_V48_WIP11'", 'const SIM_FIXED_DT = 1 / 60;'),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'ASM_WRECKAGE_WATER_SURFACE_V48_WIP11C_STATIC_CONTRACT', file:path.basename(file), baseline:path.basename(baselineFile), checks }, null, 2));
