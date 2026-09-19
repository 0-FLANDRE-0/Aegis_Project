const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12B.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(Boolean);
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename:`inline-${index + 1}.js` });

const start = html.indexOf('// ===== V48 WIP12B LIVE ORDNANCE TERMINAL-EFFECT INTEGRATION =====');
const end = html.indexOf('function _wip143FuzeParamsForMissile', start);
assert(start >= 0 && end > start, 'WIP12B source bounds missing');
const source = html.slice(start, end);
const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const sourceHasAll = (...needles) => needles.every(needle => source.includes(needle));
const topProjection = html.indexOf("wip202DrawShipProjection(c,'top'");
const topFunnelOverlay = html.indexOf("wip12bDrawCanonicalFunnelProjection(c,'top'", topProjection);
const sideProjection = html.indexOf("wip202DrawShipProjection(c,'side'");
const sideFunnelOverlay = html.indexOf("wip12bDrawCanonicalFunnelProjection(c,'side'", sideProjection);

const checks = {
  title: html.includes('<title>AEGIS v48 WIP12B — Live Ordnance Terminal Effects and Damage Visualization</title>'),
  syntax: scripts.length > 0,
  contract: sourceHasAll("schema:'AEGIS_LIVE_TERMINAL_EFFECTS_V48_WIP12B'", "liveAuthority:'OBSERVE_EXISTING_COMBAT_RESULT_NO_SECOND_DAMAGE_APPLICATION'", "asmIntegration:'LEGACY_ASM_PENETRATION_COMPAT_EXACT_PARITY'"),
  fiveLiveFamilies: ['KH32','KH35U','SM2','ESSM','RAM'].every(id => source.includes(`${id}:wip12bLiveSpec`)),
  massSeparated: sourceHasAll('penetratorMassKg:ASM_PROFILES', 'penetratorMassKg:37.421', 'penetratorMassKg:23.19', 'penetratorMassKg:5.607'),
  asmCompatibility: sourceHasAll("integrationMode:'LEGACY_ASM_COMPAT'", "mode:'LEGACY_ASM_PENETRATION_COMPAT'", "damageAppliedBy:'LEGACY_ASM_DAMAGE_PATH'"),
  interceptorCommonEvents: sourceHasAll("integrationMode:'COMMON_FRAGMENT_TERMINAL_EVENT'", 'function wip12bRecordInterceptorTerminalEffect', "damageAppliedBy:'EXISTING_INTERCEPT_FRAGMENT_PK'"),
  dualFuzePaths: sourceHasAll("fuzePaths:Object.freeze(['PROXIMITY','CONTACT_DIRECT_ACTION','DUD'])", "architecture:'DUAL_INDEPENDENT_PATH'", "mode:'EARLIEST_VALID_EVENT'"),
  sourcedSm2AndRamContact: hasAll("directActionFuze:{enabled:true,sourceClass:'PRIMARY_ARCHITECTURE_NUMERIC_NONE'}", "contactFuze:{enabled:true,sourceClass:'PRIMARY_ARCHITECTURE_NUMERIC_NONE'}"),
  essmAssumptionExplicit: hasAll("directActionFuze:{enabled:true,sourceClass:'SIM_WORKING_ASSUMPTION_PUBLIC_IDENTITY_UNRESOLVED'}"),
  contactAndProximityResolution: sourceHasAll('function wip12bProximityTrace', 'function wip12bResolveSurfaceTerminal', "fuzePath==='PROXIMITY'", "fuze:{armed:false,functioning:fuzePath!=='DUD'"),
  liveAsmHooks: hasAll("wip12bRecordLegacyAsmTerminalEffect({impactEventId:'dud:'", "wip12bRecordLegacyAsmTerminalEffect({impactEventId:'blast:'", 'wip12bRecordLegacyAsmTerminalEffect({impactEventId:`wip11c-wreck:'),
  liveInterceptorHook: hasAll('wip12bRecordInterceptorTerminalEffect(interceptor,weaponType,target,result);return ev;'),
  boundedIdempotentLedger: sourceHasAll('const WIP12B_TERMINAL_EVENT_MAX=32', 'existing=WIP12B_TERMINAL_EVENTS.find', 'if(existing)return existing', 'persistentSnapshot:false'),
  renderState: hasAll("terminalEffectsRevision:'V48_WIP12B_LIVE_ORDNANCE_VISUALIZATION'", 'terminalImpacts:wip12bTerminalEventsSnapshot()'),
  pathVisualization: hasAll('syncTerminalImpactVisualsV48Wip12B(st)', "group.name='V48_WIP12B_TERMINAL_EVENT:'", "line.name='TERMINAL_PATH'", "mesh.name=`TERMINAL_${kind}`"),
  terminalEffectsInteriorOnly: hasAll('showTerminalInteriorEffects=!!window.__WIP148_3D_VIEW__?.interiorTopologyVisible', 'if(showTerminalInteriorEffects)for(const h of shipHitHistory)', 'this.terminalImpactLayer.visible=!!this.interiorTopologyVisible', 'hiddenOutsideInterior:!interiorMode&&!visible', 'visibleInInterior:interiorMode&&visible'),
  detailedInteriorFix: hasAll("coarseFloodCompartmentProxy:false", 'coarseCompartmentProxyRetired:!this.compartmentInteriorV8', 'this.disposeCompartmentInteriorV8(this.compartmentInteriorV8)', 'syncDetailedInteriorDamageVisibilityV48Wip12B(st)'),
  detailedInteriorEnvelopeClip: hasAll('interiorEnvelopeFragmentsV48Wip12B(s,options={})', 'allInteriorContained:', 'outsideInteriorVertices:', "s?.id==='upper.vls.aft'"),
  detailedHazards: hasAll("group.name='V48_WIP12B_DETAILED_INTERIOR_HAZARDS'", "add(s,'FLOOD'", "add(s,'FIRE'", "add(s,'SMOKE'", 'group.userData.envelopeClipped=true'),
  funnelExtensionAuthority: hasAll("revision:'V48_WIP12B_FUNNEL_EXTENSION'", 'aftExtensionM:1.75,forwardExtensionM:.50', 'aftExtensionM:1.25,forwardExtensionM:1.00', 'xAftM:5.25,xFwdM:17.10', 'xAftM:-17.65,xFwdM:-5.80'),
  funnelConsumersCoupled: hasAll('function wip12bDrawCanonicalFunnelProjection', 'funnelGeometryAuditV48Wip12B()', 'funnelGeometry3DAuditV48Wip12B()', "blindHalfDeg:41", "blindHalfDeg:45", "blindHalfDeg:54", "'FUNNEL_SHELL_'+F.id"),
  funnel2DOverlayVisible: topProjection >= 0 && topFunnelOverlay > topProjection && sideProjection >= 0 && sideFunnelOverlay > sideProjection && hasAll('oldAft=F.xAftM+F.aftExtensionM', 'oldFwd=F.xFwdM-F.forwardExtensionM', 'oldRoofAft=F.roofAftXM+F.aftExtensionM', 'oldRoofFwd=F.roofFwdXM-F.forwardExtensionM'),
  transparencyFix: hasAll("inside(o,'crewInteriorV48Wip07')", "inside(o,'terminalImpactV48Wip12B')") && !html.includes("inside(o,'damageInterior'))return"),
  noPhysicsFromRenderer: hasAll("physicsFeedback:false,maxEvents:32", "group.userData.physicsFeedback=false"),
  scopeHeld: sourceHasAll("surfaceFireControl:'DEFERRED_WIP13'", "gunLaunch:'DEFERRED'", 'persistentDamagePatch:false'),
  rngNeutralIntegration: !source.includes('simRandom(') && !source.includes('rand('),
  diagnosticsExposed: hasAll('wip12bTerminalEffectsContract:()', 'wip12bResolveSurfaceTerminal:', 'wip12bTerminalDiagnostics:()', 'wip12bTerminal3DAudit:()', 'wip12bInteriorDamage3DAudit:()'),
  bootSelftest: hasAll('V48 WIP12B live terminal effects ', 'LIVE-ORDNANCE-TERMINAL-EFFECTS-V48-WIP12B SELFTEST PASS')
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'LIVE_ORDNANCE_TERMINAL_EFFECTS_V48_WIP12B_STATIC_CONTRACT', file:path.basename(file), checks }, null, 2));
