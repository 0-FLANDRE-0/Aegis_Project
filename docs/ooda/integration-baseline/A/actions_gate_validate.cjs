#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const paths = process.argv.slice(2);
if (paths.length !== 6) {
  console.error('usage: actions_gate_validate.cjs BASELINE CANDIDATE CONTRACT CONTRACT_REPEAT CREW CREW_REPEAT');
  process.exit(2);
}
const [baseline, candidate, contract, contractRepeat, crew, crewRepeat] = paths.map(path => JSON.parse(fs.readFileSync(path)));
if (candidate.deterministicDigest !== baseline.deterministicDigest) throw Error('baseline/candidate oracle digest mismatch');
if (contract.deterministicDigest !== contractRepeat.deterministicDigest) throw Error('contract oracle repeat mismatch');
if (crew.deterministicDigest !== crewRepeat.deterministicDigest) throw Error('crew contract oracle repeat mismatch');
const owners = contract.owners || [];
const mismatch = owners.reduce((n, q) => n + (q.active?.diagnostics?.shadowMismatchCount || 0) + (q.foreign?.diagnostics?.shadowMismatchCount || 0), 0);
const errors = owners.reduce((n, q) => n + (q.browser?.consoleErrors?.length || 0) + (q.browser?.pageErrors?.length || 0), 0);
const oracleErrors = [...(baseline.owners || []), ...(candidate.owners || [])]
  .reduce((n, q) => n + (q.result?.browser?.consoleErrors?.length || 0) + (q.result?.browser?.pageErrors?.length || 0), 0);
if (owners.length !== 2 || mismatch !== 0 || errors !== 0) throw Error('contract gate failed');
if (oracleErrors !== 0) throw Error('baseline/candidate oracle console error');
if (owners.some(q => q.forbidden.length || !q.readOnly.rngExact || !q.readOnly.saveExact)) throw Error('read-only/truth audit failed');
const crewFailed = Object.entries(crew.checks || {}).filter(([, value]) => !value).map(([key]) => key);
if (!Object.keys(crew.checks || {}).length || crewFailed.length) throw Error(`crew contract failed: ${crewFailed.join(',')}`);
console.log(JSON.stringify({status: 'PASS', ownerCount: owners.length, mismatch, errors, oracleErrors, crewChecks:Object.keys(crew.checks).length, crewDigest:crew.deterministicDigest}));

