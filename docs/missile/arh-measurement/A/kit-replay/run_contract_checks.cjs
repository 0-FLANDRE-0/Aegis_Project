// Isolated game-software measurement contract checks. No product file is changed.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const dir = __dirname;
const source = fs.readFileSync(path.join(dir, 'captured_measurement_function.js'), 'utf8');
const origin = JSON.parse(fs.readFileSync(path.join(dir, 'provenance.json'), 'utf8'));
const sourceHash = crypto.createHash('sha256').update(source).digest('hex');
if (sourceHash !== origin.measurementFunctionSha256) throw Error('CAPTURED_SOURCE_HASH_MISMATCH');
const ctx = {
  Math, deg: x => x * Math.PI / 180,
  clamp: (x, a, b) => Math.max(a, Math.min(b, x)),
  lerp: (a, b, t) => a + (b - a) * t,
  angNorm: x => Math.atan2(Math.sin(x), Math.cos(x)),
  _arhSeekerRandom: () => 0, _arhSeekerRandn: () => 0
};
vm.createContext(ctx);
vm.runInContext(source, ctx);
// These are synthetic uncertainty fields. Angular beam/noise/glint parameters
// deliberately use the defaults of the captured function. This is NOT a
// capture of the current active SM6 profile.
const profile = {
  trackDwellGain: 1, searchDwellGain: 1,
  minRangeSigmaM: 1, baseRangeSigmaM: 1, glintFraction: 0,
  minAzSigmaDeg: .02, baseAzSigmaDeg: .02,
  minElSigmaDeg: .02, baseElSigmaDeg: .02,
  minDopplerSigmaMps: 1, baseDopplerSigmaMps: 1
};
function observe(targetAzDeg, boresightAzDeg, normalDraw = () => 0, overrides = {}) {
  ctx._arhSeekerRandn = normalDraw;
  return ctx._arhV2MonopulseMeasurement(
    { _v1ArhState: 'TRACK', seekerAngle: ctx.deg(boresightAzDeg), seekerEl: 0 },
    [{ azRad: ctx.deg(targetAzDeg), elRad: 0, rangeM: 26000,
      dopplerPathRateMps: 0, baseReceivedPowerNorm: 1,
      receivedPowerNorm: 1, snr: 20 }],
    { ...profile, ...overrides }
  );
}
function gaussian(seed) {
  let state = seed >>> 0;
  const u = () => {
    state ^= state << 13; state ^= state >>> 17; state ^= state << 5;
    return ((state >>> 0) + .5) / 4294967296;
  };
  return () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u());
}
function noiseStats(overrides = {}) {
  const normal = gaussian(0x71c42a19), n = 20000;
  let sum = 0, sumSq = 0, reported = null;
  for (let i = 0; i < n; i++) {
    const measurement = observe(0, 0, normal, overrides);
    const value = measurement.azRad * 180 / Math.PI;
    sum += value; sumSq += value * value; reported = measurement.azSigmaDeg;
  }
  const hi = observe(0, 0, () => 1, overrides);
  const lo = observe(0, 0, () => -1, overrides);
  return {
    samples: n, meanDeg: sum / n,
    empiricalSigmaDeg: Math.sqrt((sumSq - sum * sum / n) / (n - 1)),
    generatedSigmaDeg: (hi.azRad - lo.azRad) / 2 * 180 / Math.PI,
    reportedSigmaDeg: reported
  };
}
const pointAngles = [-.5, -.1, 0, .1, .5].map(input => ({
  inputDeg: input, returnedDeg: observe(input, 0).azRad * 180 / Math.PI
}));
const fixedPoint = [-.5, -.1, 0, .1, .5].map(boresight => ({
  targetDeg: 0, boresightDeg: boresight,
  returnedDeg: observe(0, boresight).azRad * 180 / Math.PI
}));
const noise = noiseStats(), moreGlint = noiseStats({ monopulseGlintDeg: .32 });
const tests = [
  { name: 'NOISELESS_POINT_BEARING_IDENTITY',
    pass: pointAngles.every(x => Math.abs(x.inputDeg - x.returnedDeg) < 1e-8) },
  { name: 'FIXED_POINT_UNBIASED_WHEN_BORESIGHT_MOVES',
    pass: fixedPoint.every(x => Math.abs(x.returnedDeg - x.targetDeg) < 1e-8) },
  { name: 'DECLARED_SIGMA_COVERS_GENERATED_ANGLE_NOISE',
    pass: noise.generatedSigmaDeg <= noise.reportedSigmaDeg * 1.10 },
  { name: 'REPORTED_SIGMA_TRACKS_GENERATOR_NOISE_CHANGE',
    pass: Math.abs(moreGlint.reportedSigmaDeg / noise.reportedSigmaDeg -
      moreGlint.generatedSigmaDeg / noise.generatedSigmaDeg) < .10 }
];
const result = {
  schema: 'AEGIS_ARH_MEASUREMENT_CONTRACT_A',
  scope: 'Captured live function; synthetic single-point inputs and default angular configuration. Not a flight rerun or active-SM6-profile test.',
  measurementFunctionSha256: sourceHash,
  pointAngles, fixedPoint, noise, moreGlint, tests,
  passed: tests.filter(x => x.pass).length, failed: tests.filter(x => !x.pass).length,
  productFilesChanged: 0
};
fs.writeFileSync(path.join(dir, 'contract_results.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
// A non-zero status is expected for the captured baseline: these are contracts
// that currently fail, not tests that call the existing behavior correct.
process.exitCode = result.failed ? 1 : 0;
