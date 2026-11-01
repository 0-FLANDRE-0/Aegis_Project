// TEST_ONLY / AFTER_ACTION_PURE_CAPTURED_GRAPH_DIAGNOSTIC.
// Replays captured edge data in private VMs; never calls world/RF/filter methods.
const fs = require('fs'), path = require('path'), vm = require('vm');
const zlib = require('zlib'), crypto = require('crypto');
const D = __dirname, P = path.resolve(D, '../..'), R = path.resolve(P, '../../../..');
const hash = x => crypto.createHash('sha256').update(x).digest('hex');
const baselinePath = path.join(R, 'Aegis_SIM_v48_WIP_TRACK_B.html');
const baselineSha = '0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6';
const modulePath = path.join(P, 'association.js'), buildPath = path.join(P, 'BUILD.json');
function unpack(raw) {
  const match = /data-c55-index="13">([^<]+)<\/script>/.exec(raw.toString('utf8'));
  if (!match) throw Error('ACTUAL_PACKED_MAIN_13_REQUIRED');
  return zlib.gunzipSync(Buffer.from(match[1], 'base64')).toString('utf8');
}
function assignmentSource(source) {
  const startToken = '  function bridgeMasterEMinCostAssignmentV35(';
  const endToken = '  function bridgeMasterEGlobalAssignmentsV35(';
  const a = source.indexOf(startToken), b = source.indexOf(endToken, a);
  if (a < 0 || b < 0 || source.indexOf(startToken, a + 1) !== -1) throw Error('NATIVE_ASSIGNER_NOT_UNIQUE');
  return source.slice(a, b);
}
const baselineRaw = fs.readFileSync(baselinePath);
if (hash(baselineRaw) !== baselineSha) throw Error('FROZEN_DELIVERED_B_CHANGED');
const native = assignmentSource(unpack(baselineRaw));
const moduleText = fs.readFileSync(modulePath, 'utf8'), buildRaw = fs.readFileSync(buildPath), build = JSON.parse(buildRaw);
const candidatePath = path.join(R, build.output), candidateRaw = fs.readFileSync(candidatePath), candidateSource = unpack(candidateRaw);
const declared = build.modules.find(m => m.path === 'association.js');
if (!declared || hash(candidateRaw) !== build.htmlSha256 || hash(candidateSource) !== build.mainSha256 ||
    hash(moduleText) !== declared.sourceSha256 || hash(moduleText) !== declared.renderedSha256 ||
    candidateSource.split(moduleText).length !== 2) throw Error('FROZEN_R2_PRODUCTION_MODULE_MISMATCH');
if (assignmentSource(candidateSource) !== native) throw Error('NATIVE_ASSIGNER_CHANGED');
const boundToken = 'maxComponentSize:12,';
if (moduleText.split(boundToken).length !== 2) throw Error('REFERENCE_COMPUTATIONAL_BOUND_TOKEN_NOT_UNIQUE');
const referenceText = moduleText.replace(boundToken, 'maxComponentSize:128,');
function load(text) {
  const context = {window: {}, Math, Number, Map, Set, Float64Array, Int32Array, Uint8Array, Array, Object, JSON};
  vm.createContext(context);
  vm.runInContext(native + '\n' + text, context, {timeout: 3000});
  return {api: context.window.__TRACK_B__, assign: vm.runInContext('bridgeMasterEMinCostAssignmentV35', context)};
}
const current = load(moduleText), exactNis = load(referenceText);
const inputPath = process.argv[2], outputPath = path.resolve(process.argv[3] || path.join(D, 'LARGE_EXACT_REVIEW.json'));
if (!inputPath) throw Error('Usage: node offline_large_review.cjs captured-graphs.json [output-within-this-folder.json]');
if (!outputPath.startsWith(D + path.sep)) throw Error('OUTPUT_MUST_STAY_IN_DEFENSE_TIMING_LOGGER_FOLDER');
const raw = fs.readFileSync(inputPath), parsed = JSON.parse(raw);
const graphs = Array.isArray(parsed) ? parsed : parsed.graphs;
if (!Array.isArray(graphs)) throw Error('CAPTURED_GRAPH_ARRAY_REQUIRED');
const key = p => JSON.stringify([p.i, p.id]);
const triples = pairs => pairs.map(p => ({i: p.i, id: p.id, nis: p.nis}));
const canonicalPairs = pairs => triples(pairs).sort((a, b) => key(a).localeCompare(key(b)));
const canonicalIds = ids => Array.from(ids).sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const fields = (o, names) => Object.fromEntries(names.filter(k => Object.prototype.hasOwnProperty.call(o, k)).map(k => [k, o[k]]));
function components(list) {
  return list.map(c => ({...fields(c, ['edgeCount', 'ambiguous', 'reason', 'certifiedCount',
    'evidenceResolved', 'lowerBoundCertifiedCount', 'exactResidualCertifiedCount',
    'residualComponentsSolved', 'residualRefinementRejected']), plots: Array.from(c.plots), tracks: Array.from(c.tracks)}));
}
const rows = [];
for (const [ordinal, g] of graphs.entries()) {
  const pairs = g.inputPairs ?? g.pairs;
  if (!g.input || !Array.isArray(pairs)) throw Error('MISSING_CAPTURED_INPUT_GRAPH_AT_' + ordinal);
  const input = {...g.input, pairs};
  if (Array.isArray(g.inputLegacyPairs)) input.legacyPairs = g.inputLegacyPairs;
  const now = current.api.solve(input, current.assign), ref = exactNis.api.legacySolve(input, exactNis.assign);
  const ns = new Set(now.pairs.map(key)), rs = new Set(ref.pairs.map(key));
  const captured = g.actualSelectedPairs ?? g.selectedPairs;
  const capturedHeldPlots = g.actualHeldPlots ?? g.heldPlots;
  const capturedHeldTracks = g.actualHeldTracks ?? g.heldTracks;
  const comparisons = {
    selectedPairs: Array.isArray(captured) ? equal(canonicalPairs(now.pairs), canonicalPairs(captured)) : null,
    heldPlots: Array.isArray(capturedHeldPlots) ? equal(canonicalIds(now.heldPlots), canonicalIds(capturedHeldPlots)) : null,
    heldTracks: Array.isArray(capturedHeldTracks) ? equal(canonicalIds(now.heldTracks), canonicalIds(capturedHeldTracks)) : null
  };
  const productSha = g.productSha256 ?? g.candidateSha256 ?? g.htmlSha256 ?? null;
  rows.push({ordinal, ...fields(g, ['version', 'productSha256', 'candidateSha256', 'htmlSha256', 'step', 'timeS']),
    inputGraphSha256: hash(JSON.stringify(input)), route: input.route, gate: input.gate,
    plotCount: input.plotCount, inputPairCount: pairs.length,
    currentR2PureMatchesActuallyCaptured: comparisons,
    capturedProductIsFrozenR2: productSha == null ? null : productSha === build.htmlSha256,
    actualComponents: g.actualComponents ?? g.components ?? null,
    currentR2Components: components(now.components), exactNativeNisReferenceComponents: components(ref.components),
    currentR2Selected: triples(now.pairs), currentR2HeldPlots: Array.from(now.heldPlots), currentR2HeldTracks: Array.from(now.heldTracks),
    exactNativeNisReferenceSelected: triples(ref.pairs), exactNativeNisReferenceHeldPlots: Array.from(ref.heldPlots),
    exactNativeNisReferenceHeldTracks: Array.from(ref.heldTracks),
    currentAcceptedAbsentFromExactNativeNisReference: now.pairs.filter(p => !rs.has(key(p))).map(p => ({...p})),
    currentHeldButExactNativeNisReferenceResolved: ref.pairs.filter(p => !ns.has(key(p))).map(p => ({...p})),
    actuallyCapturedSelected: captured ?? null, actuallyCapturedHeldPlots: capturedHeldPlots ?? null,
    actuallyCapturedHeldTracks: capturedHeldTracks ?? null,
    interpretation: 'A current acceptance absent from NIS-only reference is NOT automatically unsound. Current secondary S evidence may legitimately resolve NIS ambiguity; inspect component evidence/certification and preserved native edge metadata.'});
}
const result = {
  schema: 'AEGIS_R2_CAPTURED_LARGE_GRAPH_EXACT_REVIEW_1',
  classification: 'TEST_ONLY_AFTER_ACTION_PURE_CAPTURED_GRAPH_NO_NEW_MEASUREMENT',
  calculationStatus: 'COMPLETE', graphs: rows.length,
  provenance: {toolPath: path.relative(R, __filename), toolSha256: hash(fs.readFileSync(__filename)),
    inputPath: path.resolve(inputPath), inputSha256: hash(raw), modulePath: path.relative(R, modulePath),
    actualProductionModuleSha256: hash(moduleText), testOnlyReferenceModuleSha256: hash(referenceText),
    baselineHtmlPath: path.relative(R, baselinePath), baselineHtmlSha256: baselineSha,
    frozenR2HtmlPath: path.relative(R, candidatePath), frozenR2HtmlSha256: build.htmlSha256,
    frozenR2BuildSha256: hash(buildRaw), nativeHungarianSourceSha256: hash(native),
    nativeHungarianSource: native},
  computationalReference: 'Actual captured native graph; R2 API legacySolve in private VM; only its computational component ceiling12→128. Same native Hungarian source. No recomputed NIS/S, changed gate/delta, RF/filter/world access or product coefficient edits.',
  currentR2ReplayKnownProductFailures: rows.filter(r => r.capturedProductIsFrozenR2 === true &&
    Object.values(r.currentR2PureMatchesActuallyCaptured).some(v => v !== true)).map(r => r.ordinal),
  missingProductIdentityOrdinals: rows.filter(r => r.capturedProductIsFrozenR2 == null).map(r => r.ordinal),
  selectedCount: rows.reduce((n, r) => n + r.currentR2Selected.length, 0),
  exactNativeNisReferenceSelectedCount: rows.reduce((n, r) => n + r.exactNativeNisReferenceSelected.length, 0),
  currentAcceptedAbsentFromExactNativeNisReferenceCount: rows.reduce((n, r) => n + r.currentAcceptedAbsentFromExactNativeNisReference.length, 0),
  currentHeldButExactNativeNisReferenceResolvedCount: rows.reduce((n, r) => n + r.currentHeldButExactNativeNisReferenceResolved.length, 0),
  referenceIsNotPhysicalIdentityTruth: true, automaticallyApproveNisReferenceDisagreements: false,
  gameWorldCalls: 0, rfCalls: 0, filterCalls: 0, newMeasurementsOrNisGenerated: 0,
  originalNativeFunctionBytesChanged: false, gameProductChanged: false, expectedValuesChanged: false,
  rows, releaseApproved: false
};
fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({calculationStatus: result.calculationStatus, graphs: rows.length,
  knownR2ReplayFailures: result.currentR2ReplayKnownProductFailures,
  currentAcceptedAbsentFromNisOnlyReference: result.currentAcceptedAbsentFromExactNativeNisReferenceCount,
  currentHeldButNisOnlyReferenceResolved: result.currentHeldButExactNativeNisReferenceResolvedCount,
  notAutomaticallyUnsound: true, outputPath, releaseApproved: false}));
