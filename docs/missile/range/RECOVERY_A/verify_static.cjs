// Prove the complete packed game differs from RANGE_A in exactly two literals.
const fs = require('fs'), zlib = require('zlib'), crypto = require('crypto'), acorn = require('acorn'), path = require('path');
const H = __dirname, R = path.resolve(H, '../../../..');
const sha = x => crypto.createHash('sha256').update(x).digest('hex');
let base = path.join(R, 'Aegis_SIM_v48_WIP_RANGE_A.html');
if (!fs.existsSync(base)) base = path.join(R, 'archive/v48/WIP_RANGE_A', path.basename(base));
const next = path.join(R, 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html');
function read(p) {
  const raw = fs.readFileSync(p), h = raw.toString(), m = h.match(/data-c55-index="13">([^<]+)<\/script>/);
  const s = zlib.gunzipSync(Buffer.from(m[1], 'base64')).toString();
  let wrapper = h.replace(m[1], '__PACKED_MAIN__');
  const rm = wrapper.match(/const records=(\[.*?\]);/s), records = JSON.parse(rm[1]);
  records[13] = { ...records[13], rawBytes: 'DATA', gzipBytes: 'DATA', sha256: 'DATA' };
  wrapper = wrapper.replace(rm[1], JSON.stringify(records)).replaceAll('v48_WIP_RANGE_RECOVERY_A', 'v48_WIP_RANGE_A').replaceAll('V48_WIP_RANGE_RECOVERY_A', 'V48_WIP_RANGE_A');
  return { raw, h, s, wrapper };
}
const a = read(base), b = read(next), manifest = JSON.parse(fs.readFileSync(path.join(H, 'build.json')));
let reverted = b.s;
for (const [old, value] of manifest.edits) {
  if (reverted.split(value).length !== 2) throw Error('Edit multiplicity');
  reverted = reverted.replace(value, old);
}
function functions(s) {
  const ast = acorn.parse(s, { ecmaVersion: 'latest' }), out = [];
  function walk(n) {
    if (!n || typeof n !== 'object') return;
    if (n.type === 'FunctionDeclaration') out.push({ name: n.id.name, sha256: sha(s.slice(n.start, n.end)), source: s.slice(n.start, n.end) });
    for (const v of Object.values(n)) if (Array.isArray(v)) v.forEach(walk); else if (v && typeof v === 'object') walk(v);
  }
  walk(ast); return out;
}
const af = functions(a.s), bf = functions(b.s);
const changed = af.filter((q, i) => q.name !== bf[i]?.name || q.sha256 !== bf[i]?.sha256);
const fixtures = new Function(bf.find(q => q.name === 'gameFlightTerminationEvaluateV48').source + '\n' + bf.find(q => q.name === 'gameFlightTerminationFixturesV48').source + '\nreturn gameFlightTerminationFixturesV48();')();
const tag = '// ENV_C: RANGE_A aligned diagnostic-only source capsule.';
const env = s => s.slice(s.indexOf(tag), s.indexOf('\n  completeShipStartup();', s.indexOf(tag)));
const live = s => s.slice(0, s.indexOf(tag)) + s.slice(s.indexOf('\n  completeShipStartup();', s.indexOf(tag)));
const checks = {
  pinnedRangeA: sha(a.raw) === '8f504eb45c19c34e473d0d04f08180afde95a9c72b5ec935ec0204bd9d7246b5',
  onlyTwoFullLoftLiterals: reverted === a.s,
  wrapperOnlyVersionAndIntegrity: a.wrapper === b.wrapper,
  namedFunctionsByteIdentical: af.length === bf.length && !changed.length,
  embeddedEnvelopeAndDiagnosticUnchanged: env(a.s) === env(b.s),
  originalSixTerminationFixtures: fixtures.pass && fixtures.cases.length === 6,
};
for (const m of b.h.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) if (!/application\/octet-stream/.test(m[1]) && m[2].trim()) acorn.parse(m[2], { ecmaVersion: 'latest' });
checks.outerJavascriptParses = true;
const q = { pass: Object.values(checks).every(Boolean), checks, htmlSha256: sha(b.raw), namedFunctionCount: af.length, liveNamedFunctionCount: functions(live(a.s)).length, changedFunctions: changed.map(q => q.name), fixtures, preservedSourceSha256: sha(reverted), edits: manifest.edits };
fs.mkdirSync(path.join(H, 'evidence'), { recursive: true });
fs.writeFileSync(path.join(H, 'evidence/static.json'), JSON.stringify(q, null, 2) + '\n');
console.log(JSON.stringify(q));
if (!q.pass) process.exitCode = 1;
