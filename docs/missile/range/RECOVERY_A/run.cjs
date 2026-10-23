const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const H = __dirname, C = path.resolve(H, '../../../envelope/C');
if (isMainThread) {
  (async () => {
    const started = performance.now();
    const parts = await Promise.all(['BASE', 'RANGE_A', 'RECOVERY'].map(version => new Promise((resolve, reject) => {
      const worker = new Worker(__filename, { workerData: { version, controls: process.argv.includes('--controls') } });
      worker.on('error', reject);
      worker.on('message', q => q.progress ? console.log(version, q.progress) : resolve(q));
    })));
    const calls = parts.reduce((n, q) => n + q.results.length, 0);
    const result = { schema: 'AEGIS_RANGE_RECOVERY_A_CASES_1', provenance: 'GAME_ENGINE_COMPUTED', seed: 1831565813, fixedDtS: 1 / 60, versions: parts, calls, fullEnvelopeSweep: false };
    const raw = JSON.stringify(result), out = process.argv[2];
    if (!out) throw Error('Output path required');
    fs.writeFileSync(out, raw);
    const receipt = { sha256: crypto.createHash('sha256').update(raw).digest('hex'), bytes: Buffer.byteLength(raw), elapsedMs: performance.now() - started, calls, workers: 3 };
    fs.writeFileSync(out + '.receipt.json', JSON.stringify(receipt));
    console.log('DONE', JSON.stringify(receipt));
  })().catch(e => { console.error(e); process.exitCode = 1; });
} else {
  const reduce = require('./reduce.cjs');
  const data = JSON.parse(fs.readFileSync(path.join(H, 'inputs-' + workerData.version + '.json')));
  const source = fs.readFileSync(path.join(C, 'native-engine.js'), 'utf8') + '\n' + fs.readFileSync(path.join(C, 'private.js'), 'utf8');
  const factory = new Function('DATA', 'SETTINGS', 'PROFILE', 'PRIVATE_SHIP', source);
  const engine = factory(structuredClone(data.data), structuredClone(data.settings), {}, { entityId: 'ENV_PRIVATE', navigation: { heading: 0, speed: 0, positionWorld: { x: 0, y: 0 } }, weapons: {} });
  const cases = JSON.parse(fs.readFileSync(path.join(H, workerData.controls ? 'control-cases.json' : 'cases.json'))).cases, results = [];
  for (const c of cases) {
    results.push({ caseId: c.caseId, motion: c.motion, result: reduce(engine.runCase(c)) });
    parentPort.postMessage({ progress: results.length });
  }
  parentPort.postMessage({ version: workerData.version, inputHash: crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex'), results });
}
