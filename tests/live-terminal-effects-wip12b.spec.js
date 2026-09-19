const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12B.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/live-terminal-effects-wip12b';

test.use({ viewport:{ width:1600, height:900 } });

test('v48 WIP12B integrates live ordnance and dual fuze paths without changing legacy authority', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481220; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.wip12bTerminalDiagnostics, null, { timeout:45_000 });

  await page.evaluate(() => { document.getElementById('shipDetailPanel').style.display = 'block'; });
  await page.waitForTimeout(80);
  const funnelIndicatorPixels = await page.evaluate(() => {
    const canvas=document.getElementById('shipDetailCanvas'),ctx=canvas.getContext('2d'),points=[[149,72],[169,72],[211,72],[191,72]];
    return points.map(([x,y])=>{const rgba=[...ctx.getImageData(x,y,1,1).data];return {x,y,rgba};});
  });
  await page.evaluate(() => { document.getElementById('shipDetailPanel').style.display = 'none'; });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, contract = d.wip12bTerminalEffectsContract(), ordnance = d.wip12bLiveOrdnance(), diagnostic = d.wip12bTerminalDiagnostics();
    const contactA = d.wip12bResolveSurfaceTerminal({ weaponKey:'SM2', fuzePath:'CONTACT_DIRECT_ACTION', impactEventId:'WIP12B_DETERMINISTIC_CONTACT' });
    const contactB = d.wip12bResolveSurfaceTerminal({ weaponKey:'SM2', fuzePath:'CONTACT_DIRECT_ACTION', impactEventId:'WIP12B_DETERMINISTIC_CONTACT' });
    const proximity = d.wip12bResolveSurfaceTerminal({ weaponKey:'ESSM', fuzePath:'PROXIMITY', impactEventId:'WIP12B_PROXIMITY', detonationPoint:{x:-.4,y:0,z:0} });
    const dud = d.wip12bResolveSurfaceTerminal({ weaponKey:'RAM', fuzePath:'DUD', impactEventId:'WIP12B_DUD' });

    d.wip12bResetTerminalEvents();
    d.wip12bResolveSurfaceTerminal({ weaponKey:'SM2', fuzePath:'CONTACT_DIRECT_ACTION', impactEventId:'WIP12B_LEDGER_ONCE', record:true });
    d.wip12bResolveSurfaceTerminal({ weaponKey:'SM2', fuzePath:'CONTACT_DIRECT_ACTION', impactEventId:'WIP12B_LEDGER_ONCE', record:true });
    const deduped = d.wip12bTerminalEvents();

    d.wip12bResetTerminalEvents();
    d.wip12bRecordInterceptorTerminalEffect({id:901,x:0,y:0,z:30,vx:1,vy:0,vz:0,_fuzeTriggerReason:'proximity'}, 'SM2', {id:501,label:'Kh-35U'}, 'KILL');
    d.wip12bRecordInterceptorTerminalEffect({id:902,x:0,y:0,z:20,vx:1,vy:0,vz:0,_fuzeTriggerReason:'contact'}, 'RAM', {id:502,label:'Kh-32'}, 'DAMAGE');
    const interceptEvents = d.wip12bTerminalEvents();

    const liveNormalProbe = d.runWip113DudImpactProbe({ dud:false, rangeKm:2.4, altM:12, speedMps:280 }), liveNormalEvents = d.wip12bTerminalEvents();
    const liveDudProbe = d.runWip113DudImpactProbe({ dud:true, rangeKm:2.4, altM:12, speedMps:280 }), liveDudEvents = d.wip12bTerminalEvents();
    const renderState = window.get3DRenderState();
    return { contract, ordnance, diagnostic, contactA, contactB, proximity, dud, deduped, interceptEvents, liveNormalProbe, liveNormalEvents, liveDudProbe, liveDudEvents, renderState:{terminalEffectsRevision:renderState.terminalEffectsRevision,terminalImpacts:renderState.terminalImpacts}, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const keys = Object.keys(result.ordnance);
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    diagnostic: result.diagnostic.pass && Object.values(result.diagnostic.checks).every(Boolean),
    fiveLiveFamilies: keys.join(',') === 'KH32,KH35U,SM2,ESSM,RAM',
    separateMasses: keys.every(key => result.ordnance[key].spec.body.penetratorMassKg < result.ordnance[key].spec.body.massKg),
    dualFuzeInterceptors: ['SM2','ESSM','RAM'].every(key => result.ordnance[key].fuze.channels.includes('PROXIMITY') && result.ordnance[key].fuze.channels.includes('CONTACT_DIRECT_ACTION') && result.ordnance[key].fuze.channels.includes('DUD')),
    essmCaveat: result.ordnance.ESSM.fuze.contactSourceClass === 'SIM_WORKING_ASSUMPTION_PUBLIC_IDENTITY_UNRESOLVED',
    deterministicContact: JSON.stringify(result.contactA.trace) === JSON.stringify(result.contactB.trace) && result.contactA.trace.terminationReason === 'FUZE_AT_CONTACT' && result.contactA.trace.boundaryResults.length === 1,
    proximityWinsBeforeHull: result.proximity.trace.terminationReason === 'PROXIMITY_FUZE' && result.proximity.trace.boundaryResults.length === 0 && result.proximity.damagePacket.breaches.length === 0,
    dudNoWarheadEffect: !result.dud.trace.finalState.fuze.detonated && result.dud.damagePacket.blast.length === 0 && result.dud.damagePacket.warheadFragments.length === 0,
    ledgerIdempotent: result.deduped.length === 1 && result.deduped[0].impactEventId === 'WIP12B_LEDGER_ONCE',
    interceptorProximityAndContact: result.interceptEvents.length === 2 && result.interceptEvents[0].fuzePath === 'PROXIMITY' && result.interceptEvents[1].fuzePath === 'CONTACT_DIRECT_ACTION' && result.interceptEvents.every(e => e.damageAppliedBy === 'EXISTING_INTERCEPT_FRAGMENT_PK' && e.coordinateSpace === 'TARGET_LOCAL_METRES'),
    liveNormalAsmObserved: result.liveNormalProbe.outcome === 'NORMAL_HIT' && result.liveNormalEvents.length === 1 && result.liveNormalEvents[0].weaponKey === 'KH35U' && result.liveNormalEvents[0].fuzePath === 'CONTACT_DIRECT_ACTION' && result.liveNormalEvents[0].damageAppliedBy === 'LEGACY_ASM_DAMAGE_PATH',
    liveDudAsmObserved: result.liveDudProbe.outcome === 'DUD_PENETRATION' && result.liveDudEvents.length === 1 && result.liveDudEvents[0].fuzePath === 'DUD' && result.liveDudEvents[0].damageAppliedBy === 'LEGACY_ASM_DAMAGE_PATH',
    legacyNotDoubleApplied: result.liveNormalEvents[0].applicationAuthority === 'OBSERVED_ALREADY_APPLIED' && result.liveDudEvents[0].applicationAuthority === 'OBSERVED_ALREADY_APPLIED',
    renderContract: result.renderState.terminalEffectsRevision === 'V48_WIP12B_LIVE_ORDNANCE_VISUALIZATION' && result.renderState.terminalImpacts.length === result.liveDudEvents.length,
    funnel2DIndicatorExtended: funnelIndicatorPixels.length === 4 && funnelIndicatorPixels.every(sample => sample.rgba[0] >= 110 && sample.rgba[3] === 255),
    scopeHeld: result.contract.surfaceFireControl === 'DEFERRED_WIP13' && result.contract.gunLaunch === 'DEFERRED' && result.contract.persistentDamagePatch === false && result.contract.persistentSnapshot === false
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/live-terminal-effects-results.json`, `${JSON.stringify({ schema:'AEGIS_LIVE_TERMINAL_EFFECTS_BROWSER_V48_WIP12B', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, funnelIndicatorPixels, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP12B renders penetration history and detailed interior hazards through damage openings', async ({ page }) => {
  test.setTimeout(300_000);
  const consoleErrors = [], pageErrors = [], localThree = process.env.THREE_LOCAL_FILE || process.env.THREE_JS_LOCAL;
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  if (localThree) {
    await page.route('**/__wip12b_three.min.js', route => route.fulfill({ status:200, contentType:'application/javascript', body:fs.readFileSync(localThree) }));
    await page.addInitScript(() => { window.__NAVAL_THREE_URL__ = '/__wip12b_three.min.js'; });
  }
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`, { waitUntil:'load' });
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true || !!window.__WIP148_3D_VIEW__?._loadError, null, { timeout:120_000 });
  const ready = await page.evaluate(() => ({ ready:window.__WIP148_3D_VIEW__.ready, loadError:window.__WIP148_3D_VIEW__._loadError }));
  expect(ready).toEqual({ ready:true, loadError:null });
  await page.locator('#wip125DepartBtn').click();
  await expect(page.locator('#wip125LoadoutOverlay')).toBeHidden();

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__;v.active=false;d.runWip113DudImpactProbe({dud:false,rangeKm:2.4,altM:12,speedMps:280});const hazard=d.wip12bInteriorHazardPresentationProbe({flood01:.58,fire01:.42,smoke01:.68});
    v.active=true;const base=performance.now();v.render(base);v.render(base+16.667);v.active=false;
    const before=v.interiorDamagePresentationAuditV48Wip12B(),terminalBefore=v.terminalImpactAuditV48Wip12B(),renderState=window.get3DRenderState(),coarse=!!v.shipRoot?.getObjectByName('COMPARTMENT_INTERIOR_V8');
    if(!v.interiorTopologyVisible)v.toggleInteriorTopology();v.active=true;v.render(base+33.334);v.active=false;
    const after=v.interiorDamagePresentationAuditV48Wip12B(),terminalAfter=v.terminalImpactAuditV48Wip12B(),interior=v.interiorAuditV48Wip06(),funnelAuthority=d.wip12bFunnelGeometryAudit(),funnel3D=v.funnelGeometry3DAuditV48Wip12B();
    return {hazard:{spaceId:hazard.spaceId,row:hazard.state.hazards.find(h=>h.spaceId===hazard.spaceId)},before,after,terminalBefore,terminalAfter,interior,funnelAuthority,funnel3D,coarse,renderState:{holes:renderState.shipDamageVisual.scars.filter(s=>s.hole&&s.sealed<=.9).length,terminalImpacts:renderState.terminalImpacts.length},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    openDamageExists: result.renderState.holes >= 1,
    coarseProxyRetired: !result.coarse && result.before.coarseCompartmentProxyRetired && result.terminalBefore.coarseCompartmentProxyPresent === false,
    detailedTopologyThroughHole: result.before.visibleThroughOpenDamage && result.before.detailedTopologyVisible,
    detailedHazards: result.hazard.row.flood01 === .58 && result.hazard.row.fire01 === .42 && result.hazard.row.smoke01 === .68 && result.before.activeDetailedHazards >= 1 && result.before.renderedHazardVolumes >= 3 && result.before.hazardEnvelopeClipped && result.before.hazardFragmentCount >= 3 && result.before.hazardSpaces.includes(result.hazard.spaceId),
    terminalTracePrepared: result.renderState.terminalImpacts === 1 && result.terminalBefore.sourceEvents === 1 && result.terminalBefore.renderedEvents === 1 && result.terminalBefore.pathVisuals === 1 && result.terminalBefore.markerVisuals >= 2 && result.terminalBefore.allShipLocalEventsRepresented,
    terminalHiddenOutsideInterior: result.terminalBefore.hiddenOutsideInterior && !result.terminalBefore.visible && result.terminalBefore.visibilityMatchesInterior,
    terminalVisibleOnlyInInterior: result.terminalAfter.visibleInInterior && result.terminalAfter.visible && result.terminalAfter.visibilityMatchesInterior,
    interiorModeTransparent: result.after.interiorMode && result.after.exteriorTransparentInInteriorMode && result.interior.exteriorTransparent,
    interiorEnvelopeContained: result.interior.allSpacesRepresented && result.interior.allInteriorContained && result.interior.superstructureOutsideVertices === 0 && result.interior.hullOutsideVertices === 0 && result.interior.outsideInteriorVertices === 0,
    funnelAuthorityCoupled: result.funnelAuthority.pass && Object.values(result.funnelAuthority.checks).every(Boolean) && result.funnelAuthority.spgBlindHalfDeg.join(',') === '41,45,54',
    funnelMeshesMatchAuthority: result.funnel3D.pass && Object.values(result.funnel3D.checks).every(Boolean) && result.funnel3D.rows.FWD.matched && result.funnel3D.rows.AFT.matched,
    presentationOnly: result.terminalBefore.presentationOnly && !result.terminalBefore.physicsFeedback && result.before.presentationOnly && !result.before.physicsFeedback
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/terminal-interior-3d-results.json`, `${JSON.stringify({ schema:'AEGIS_TERMINAL_INTERIOR_3D_BROWSER_V48_WIP12B', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, ready, result }, null, 2)}\n`);
  await page.screenshot({ path:`${artifactDir}/terminal-interior-3d.png`, fullPage:true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
