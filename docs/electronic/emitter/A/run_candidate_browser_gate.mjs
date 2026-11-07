#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const args = Object.fromEntries(process.argv.slice(2).reduce((rows, value, index, all) => {
  if (value.startsWith('--')) rows.push([value.slice(2), all[index + 1]]);
  return rows;
}, []));
if (!args.html || !args.out) throw new Error('usage: run_candidate_browser_gate.mjs --html FILE --out FILE');
const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../../..');
const body = fs.readFileSync(path.resolve(args.html));
const expected = JSON.parse(fs.readFileSync(path.join(repo, 'docs/electronic/emitter/A/BASELINE_AUDIT.json'), 'utf8'));
const pageErrors = [];
const consoleErrors = [];
const stable = value => JSON.stringify(value);

async function load(browser, ship) {
  const page = await browser.newPage({ viewport: { width: 1000, height: 760 } });
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 0x6d2b79f5; });
  await page.route('https://aegis.test/**', route => route.fulfill({ body, contentType: 'text/html' }));
  await page.goto('https://aegis.test/candidate?view3d=0', { waitUntil: 'load', timeout: 90000 });
  await page.waitForSelector('#aegisShipConfirmBtn', { timeout: 90000 });
  await page.locator('#aegisShipSelect').selectOption(ship);
  await page.locator('#aegisShipConfirmBtn').click();
  await page.waitForFunction(() => window.C55Packaging?.ready && window.__WIP125_DIAG__ &&
    window.__EMITTER_A_BASELINE__ && window.__EMITTER_A_CLOSURE_DIAG__, null, { timeout: 120000 });
  await page.evaluate(() => {
    document.getElementById('wip125DepartBtn').click();
    window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);
  });
  return page;
}

async function profile(browser, ship) {
  const page = await load(browser, ship);
  const value = await page.evaluate(() => {
    const matrix = __EMITTER_A_BASELINE__.matrix();
    const definition = __SHIP_EMITTERS_A__.definitions(matrix.profileId);
    const validation = __SHIP_EMITTERS_A__.validate(matrix.profileId);
    const calls = __EMITTER_A_CLOSURE_DIAG__.resolverCalls(null);
    const core = __EMITTER_A_FINAL_DIAG__.coreSelftest();
    const contract = __EMITTER_A_FINAL_DIAG__.contract();
    const id = matrix.entityId, d = __NAVAL_SIM_DIAG__;
    d.setEmcon(false);
    d.electronicCommandF(id, { noiseRequested: true, deceptionRequested: true, autoAim: false, bearingRad: .7 });
    const before = __SHIP_EMITTERS_A__.runtime(id), saved = d.exportOperationalStateV48Wip11A();
    d.setEmcon(true);
    d.electronicCommandF(id, { noiseRequested: false, deceptionRequested: false, autoAim: true, bearingRad: 0 });
    const changed = __SHIP_EMITTERS_A__.runtime(id), imported = d.importOperationalStateV48Wip11A(saved);
    const after = __SHIP_EMITTERS_A__.runtime(id);
    const edge = __EMITTER_A_FINAL_DIAG__.edge();
    return { matrix, definitionFrozen: Object.isFrozen(definition) && Object.isFrozen(definition.entries) && definition.entries.every(Object.isFrozen),
      validation, calls, core, contract, edge, save: { before, changed, after, validationOk: imported.validation.ok } };
  });
  await page.close();
  return value;
}

async function ui(browser) {
  const page = await load(browser, 'DDG_119_LATE_FLIGHT_IIA');
  const value = await page.evaluate(() => {
    const id = __EMITTER_A_BASELINE__.matrix().entityId;
    const snap = () => ({ runtime: __SHIP_EMITTERS_A__.runtime(id), chip: document.getElementById('uiEmconChipA')?.textContent.trim(), menu: getComputedStyle(document.getElementById('mapEmconMenuE')).display });
    const before = snap(); document.getElementById('uiEmconChipA').click(); const opened = snap();
    document.getElementById('mapRadarE').click(); const radarOn = snap();
    document.getElementById('uiEmconChipA').click(); document.getElementById('mapEcmJAME').click(); const jammer = snap();
    return { before, opened, radarOn, jammer };
  });
  await page.close();
  return value;
}

const browser = await chromium.launch({ headless: true,
  executablePath: process.env.AEGIS_CHROMIUM_EXECUTABLE || undefined,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-accelerated-2d-canvas'] });
let profiles, repeat, mixed, sov, uiState;
try {
  profiles = {
    DDG_119_LATE_FLIGHT_IIA: await profile(browser, 'DDG_119_LATE_FLIGHT_IIA'),
    CG_52_LATE_TICONDEROGA: await profile(browser, 'CG_52_LATE_TICONDEROGA'),
  };
  repeat = await profile(browser, 'DDG_119_LATE_FLIGHT_IIA');
  const mixedPage = await load(browser, 'DDG_119_LATE_FLIGHT_IIA');
  mixed = await mixedPage.evaluate(() => ({
    scene: __EMITTER_A_BASELINE__.fleetScene({ allyProfileId: 'CG_52_LATE_TICONDEROGA' }),
    calls: __EMITTER_A_CLOSURE_DIAG__.resolverCalls('CG_52_LATE_TICONDEROGA'),
  }));
  await mixedPage.close();
  const sovPage = await load(browser, 'DDG_119_LATE_FLIGHT_IIA');
  sov = await sovPage.evaluate(() => __EMITTER_A_D_DIAG__.sovScene('ENEMY'));
  await sovPage.close();
  uiState = await ui(browser);
} finally {
  await browser.close();
}

const rows = Object.values(profiles);
const calls = [...rows.map(row => row.calls), mixed.calls];
const checks = {
  pageErrorsZero: pageErrors.length === 0,
  consoleErrorsZero: consoleErrors.length === 0,
  coreSelftestPass: rows.every(row => row.core.pass === true),
  ddgCgSnapshotsExact: Object.entries(profiles).every(([key, row]) => stable(row.matrix) === stable(expected.profiles[key])),
  mixedSnapshotExact: stable(mixed.scene) === stable(expected.fleetScenes.DDG_CG),
  registrySchemaReferencesValid: rows.every(row => row.definitionFrozen && row.validation.ok && row.contract.profiles.every(profileRow => profileRow.frozen && profileRow.uniqueIds && profileRow.uniqueOrders && profileRow.refs.every(ref => ref.sensorOk && ref.hardpointOk && ref.enabledKeyOk && ref.mountKindOk))),
  activeLegacyCallsZero: calls.every(row => row.mode === 'ACTIVE' && row.legacyCalls === 0),
  declaredOncePerShip: calls.every(row => row.declaredCalls === row.shipCount),
  resolverRngExact: calls.every(row => row.rngExact && stable(row.rngBefore) === stable(row.rngAfter)),
  anonymousReceiverNoTruth: rows.every(row => row.edge.anonymousPlots.count > 0 && row.edge.anonymousPlots.forbiddenPresent === false),
  saveRoundTripExact: rows.every(row => row.save.validationOk && stable(row.save.before) === stable(row.save.after) && stable(row.save.before) !== stable(row.save.changed)),
  deterministicRepeatExact: stable(profiles.DDG_119_LATE_FLIGHT_IIA.matrix) === stable(repeat.matrix) && stable(profiles.DDG_119_LATE_FLIGHT_IIA.calls.output) === stable(repeat.calls.output),
  sovPhysicalEmissionZero: sov.sovEmitterCount === 0 && sov.sovReceiver.plots.length === 0 && sov.sovObserver.normals === 0 && sov.sovObserver.tracks === 0 && sov.sovAttack.active === false,
  emconUiExistingOwners: uiState.before.runtime.emcon === true && uiState.opened.menu === 'flex' && uiState.radarOn.runtime.emcon === false && uiState.radarOn.chip.includes('EMCON OFF') && uiState.jammer.runtime.ecm.noiseRequested === true && uiState.jammer.runtime.ecm.deceptionRequested === true && uiState.jammer.chip.includes('ECM JAM'),
};
const result = { schema: 'AEGIS_CURRENT_CANDIDATE_BROWSER_GATE_1', status: Object.values(checks).every(Boolean) ? 'PASS' : 'FAIL', checks, pageErrors, consoleErrors, profiles, repeat, mixed, sov, ui: uiState };
fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
fs.writeFileSync(path.resolve(args.out), JSON.stringify(result, null, 2) + '\n');
process.stdout.write(JSON.stringify({ status: result.status, checks, pageErrors, consoleErrors }, null, 2) + '\n');
if (result.status !== 'PASS') process.exitCode = 1;
