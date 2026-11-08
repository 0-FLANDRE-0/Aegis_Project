#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../../../..');
const candidateBody = fs.readFileSync(process.env.EMCON_B_CANDIDATE_HTML || path.join(root, 'Aegis_SIM_v48_WIP_EMCON_B.html'));
const baselineBody = fs.readFileSync(process.env.EMCON_B_BASELINE_HTML || path.join(root, 'Aegis_SIM_v48_WIP_EMITTER_A.html'));
const output = path.join(root, 'docs/electronic/emcon/B/B_GATE.json');
const pageErrors = [], consoleErrors = [];
const stable = value => JSON.stringify(value);

async function load(browser, ship, candidate = true) {
  const page = await browser.newPage({ viewport: { width: 1000, height: 760 } });
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 0x6d2b79f5; });
  const body = candidate ? candidateBody : baselineBody;
  await page.route('https://aegis.test/**', route => route.fulfill({ body, contentType: 'text/html' }));
  await page.goto('https://aegis.test/emcon-b?view3d=0', { waitUntil: 'load', timeout: 90000 });
  await page.waitForSelector('#aegisShipConfirmBtn', { timeout: 90000 });
  await page.locator('#aegisShipSelect').selectOption(ship);
  await page.locator('#aegisShipConfirmBtn').click();
  await page.waitForFunction(candidate => window.C55Packaging?.ready && window.__EMITTER_A_BASELINE__ && (!candidate || window.__EMCON_B__), candidate, { timeout: 120000 });
  await page.evaluate(() => {
    window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);
    document.getElementById('wip125DepartBtn').click();
  });
  return page;
}

async function profileMatrix(browser, ship, candidate) {
  const page = await load(browser, ship, candidate);
  const result = await page.evaluate(candidate => {
    const matrix = __EMITTER_A_BASELINE__.matrix();
    if (!candidate) return { matrix };
    const id = matrix.entityId, api = __EMCON_B__, snap = api.snapshot(id);
    const before = api.diagnostic.rng(id);
    for (let i = 0; i < 64; i++) for (const row of snap.equipment) api.decision(id, row.definition.id);
    const after = api.diagnostic.rng(id), invalidState = structuredClone(snap.state);
    invalidState.categoryPolicy.AIR_SEARCH = 'INVALID';
    const invalid = {
      category: api.command(id, { category: 'NO_SUCH_CATEGORY', policy: 'SILENT' }, 'DIAGNOSTIC'),
      equipment: api.command(id, { equipmentId: 'NO_SUCH_EQUIPMENT', override: 'FORCE_SILENT' }, 'DIAGNOSTIC'),
      state: api.validate(id, invalidState),
    };
    const offline = api.diagnostic.offline(id);
    return { matrix, snap, rng: { before, after }, invalid, offline, audit: api.audit() };
  }, candidate);
  await page.close();
  return result;
}

async function fleetIsolation(browser, activeProfileId, allyProfileId) {
  const page = await load(browser, activeProfileId, true);
  const value = await page.evaluate(({ allyProfileId }) => {
    const scene = __EMITTER_A_BASELINE__.fleetScene({ allyProfileId });
    const activeId = scene.owners.find(q => q.role === 'PLAYER').entityId, allyId = scene.owners.find(q => q.role === 'ALLY').entityId;
    const before = { active: __EMCON_B__.snapshot(activeId), ally: __EMCON_B__.snapshot(allyId) };
    const activeSpy = before.active.equipment.find(q => q.definition.category === 'AIR_SEARCH').definition.id;
    const command = __EMCON_B__.command(activeId, { equipmentId: activeSpy, override: 'FORCE_SILENT' }, 'DIAGNOSTIC');
    const after = { active: __EMCON_B__.snapshot(activeId), ally: __EMCON_B__.snapshot(allyId) };
    const physical = __SHIP_EMITTERS_A__.physical();
    return { activeProfileId: scene.activeProfileId, allyProfileId, activeId, allyId, activeSpy, command, before, after, physical, audit: __EMCON_B__.audit() };
  }, { allyProfileId });
  await page.close();
  return value;
}

async function sovInactive(browser) {
  const page = await load(browser, 'DDG_119_LATE_FLIGHT_IIA', true);
  const value = await page.evaluate(() => {
    const scene = __EMITTER_A_BASELINE__.fleetScene({ enemyProfileId: 'SOVREMENNY_956' });
    const id = scene.owners.find(q => q.role === 'ENEMY').entityId;
    const snap = __EMCON_B__.snapshot(id), equipmentId = snap.equipment[0]?.definition.id;
    return { id, snap, decision: __EMCON_B__.decision(id, equipmentId), command: __EMCON_B__.command(id, { equipmentId, override: 'FORCE_RADIATE' }, 'DIAGNOSTIC'), physical: __SHIP_EMITTERS_A__.physical() };
  });
  await page.close();
  return value;
}

const browser = await chromium.launch({ headless: true, executablePath: process.env.AEGIS_CHROMIUM_EXECUTABLE || undefined,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-accelerated-2d-canvas'] });
let baseline = {}, candidate = {}, fleets = {}, sov;
try {
  for (const ship of ['DDG_119_LATE_FLIGHT_IIA', 'CG_52_LATE_TICONDEROGA']) {
    baseline[ship] = await profileMatrix(browser, ship, false);
    candidate[ship] = await profileMatrix(browser, ship, true);
  }
  for (const [key, active, ally] of [
    ['DDG_CG', 'DDG_119_LATE_FLIGHT_IIA', 'CG_52_LATE_TICONDEROGA'],
    ['CG_DDG', 'CG_52_LATE_TICONDEROGA', 'DDG_119_LATE_FLIGHT_IIA'],
    ['DDG_DDG', 'DDG_119_LATE_FLIGHT_IIA', 'DDG_119_LATE_FLIGHT_IIA'],
    ['CG_CG', 'CG_52_LATE_TICONDEROGA', 'CG_52_LATE_TICONDEROGA'],
  ]) fleets[key] = await fleetIsolation(browser, active, ally);
  sov = await sovInactive(browser);
} finally { await browser.close(); }

const checks = {
  pageErrorsZero: pageErrors.length === 0,
  consoleErrorsZero: consoleErrors.length === 0,
  modeShadow: Object.values(candidate).every(q => q.snap.mode === 'SHADOW'),
  baselineMatricesExact: Object.keys(candidate).every(key => stable(candidate[key].matrix) === stable(baseline[key].matrix)),
  defaultStateValid: Object.values(candidate).every(q => q.snap.validation.ok && q.snap.state.revision === 0 && Object.values(q.snap.state.categoryPolicy).every(v => v === 'RADIATE') && Object.values(q.snap.state.equipmentOverride).every(v => v === 'INHERIT')),
  masterAndEcmExact: Object.values(candidate).every(q => q.audit.mismatches === 0 && q.matrix.cases.some(c => c.id === 'EMCON') && q.matrix.cases.some(c => c.id === 'ECM_NOISE')),
  queryRngFree: Object.values(candidate).every(q => stable(q.rng.before) === stable(q.rng.after)),
  strictRejects: Object.values(candidate).every(q => !q.invalid.category.ok && !q.invalid.equipment.ok && !q.invalid.state.ok),
  offlineCannotRadiate: Object.values(candidate).every(q => q.offline.every(d => !d.allowed && !d.emissionActive && d.reason === 'SHIP_OFFLINE')),
  ownerIsolation: Object.values(fleets).every(q => q.command.ok && q.after.active.state.equipmentOverride[q.activeSpy] === 'FORCE_SILENT' && Object.values(q.after.ally.state.equipmentOverride).every(v => v === 'INHERIT')),
  sameAndMixedClassCovered: Object.keys(fleets).sort().join('|') === 'CG_CG|CG_DDG|DDG_CG|DDG_DDG',
  novelPolicyDoesNotChangeTacticalOutput: Object.values(fleets).every(q => q.physical.some(row => row.owner === q.activeId && row.family === 'SHIP SEARCH RADAR')),
  novelPolicySkippedNotMismatch: Object.values(fleets).every(q => q.audit.mismatches === 0 && q.audit.skippedNovelPolicy > 0),
  sovInactiveStrict: sov.snap.validation.ok && sov.snap.equipment.length > 0 && sov.snap.equipment.every(q => !q.decision.allowed && !q.decision.emissionActive) && !sov.command.ok && sov.command.reason === 'REGISTERED_INACTIVE' && !sov.physical.some(q => q.owner === sov.id),
};
const result = { schema: 'AEGIS_EMCON_B_COMMIT_B_GATE_1', status: Object.values(checks).every(Boolean) ? 'PASS' : 'FAIL', checks, pageErrors, consoleErrors, baseline, candidate, fleets, sov };
fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
process.stdout.write(JSON.stringify({ status: result.status, checks, pageErrors, consoleErrors }, null, 2) + '\n');
if (result.status !== 'PASS') process.exitCode = 1;
