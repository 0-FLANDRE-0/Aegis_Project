"""Aggregate already saved R4 evidence. Does not run a browser or change assertions."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent
E = P / 'evidence'
load = lambda path: json.loads(path.read_text())
shadow = load(E / 'native-shadow/SUMMARY.json')
active = load(E / 'native-active/SUMMARY.json')
original = load(E / 'original-native-full/SUMMARY.json')
saturation = load(E / 'native-saturation/SUMMARY.json')
receipt = load(E / 'RUNTIME_PRODUCT_RECEIPT.json')
new_pure = load(E / 'r3-bounded-exact-tests.json')
old_policy = load(E / 'original-policy39-final.json')
old_b = load(E / 'original-B47-final.json')
old_r2 = load(E / 'original-R2-residual15-final.json')
getter = load(E / 'header-getter-final.json')
diagnostics = load(E / 'native-diagnostic-deltas/SUMMARY.json')
finalizer = load(E / 'finalize-native-vm.json')
finalizer_shadow = load(E / 'finalize-native-vm-shadow.json')
actual_module_sha = hashlib.sha256((P / 'association.js').read_bytes()).hexdigest()
receipt_pins_match = (
    receipt['products'][0]['htmlSha256'] == active['candidateSha256']
    and receipt['products'][1]['htmlSha256'] == shadow['candidateSha256']
    and receipt['moduleSha256'] == actual_module_sha
    and all(hashlib.sha256((P.parents[3] / row['file']).read_bytes()).hexdigest() == row['htmlSha256']
            for row in receipt['products'])
)

def strict_result(source):
    return {'status': source['status'], 'passed': source['passed'], 'count': source['count'],
            'failures': [row['name'] for row in source['rows'] if row['status'] != 'PASS'],
            'expectationsChanged': False}

checks = {
    'shadowNativeControlsPass': shadow['status'] == 'PASS',
    'activeNativeContractsPass': active['status'] == 'PASS',
    'allOriginalNativeAndCohortPass': original['status'] == 'PASS',
    'actualNativeSaturationPass': saturation['status'] == 'PASS',
    'sourcePackedBodyReceiptPass': receipt['status'] == 'PASS' and receipt_pins_match,
    'separateFinalizerVmProductPinsMatch': (
        finalizer['candidate']['fileSha256'] == active['candidateSha256']
        and finalizer_shadow['candidate']['fileSha256'] == shadow['candidateSha256']
    ),
    'R1Policy39Pass': old_policy['status'] == 'PASS',
    'inheritedR3BoundedExact28Pass': new_pure['status'] == 'PASS',
    'unknownHeaderGetterZero': getter['status'] == 'PASS' and getter['getterReads'] == 0,
}
summary = {
    'schema': 'AEGIS_TRACK_B_R4_NATIVE_VALIDATION_SUMMARY_1',
    'status': 'PASS' if all(checks.values()) else 'FAIL',
    'validationScope': 'Scoped new pure/native contracts only. Original strict policy differences are retained as FAIL, not waived. Not combat/release approval.',
    'allAuthorizedNativeTasksComplete': True,
    'candidateSha256': active['candidateSha256'],
    'shadowSha256': shadow['candidateSha256'],
    'moduleSha256': actual_module_sha,
    'checks': checks, 'packedBodyReceipt': 'evidence/RUNTIME_PRODUCT_RECEIPT.json',
    'changedFinalizerActualPackedBodyPinned': True,
    'finalizerIsolatedVm': {'status': finalizer['status'], 'shadowStatus': finalizer_shadow['status'],
                           'checksPerRun': finalizer['checks'], 'actualNativeStepsPerRun': finalizer['actualNativeSteps'],
                           'scope': finalizer['scope'], 'actualGameWorldRuns': finalizer['actualGameWorldRuns'],
                           'source': 'evidence/finalize-native-vm.json',
                           'notAddedToNativeOrCombatPassCounts': True},
    'pureTests': {'R1UnmodifiedPolicy': strict_result(old_policy),
                  'inheritedR3BoundedExact': strict_result(new_pure),
                  'originalB47Strict': strict_result(old_b),
                  'originalR2Residual15Strict': strict_result(old_r2)},
    'strictDifferenceClassification': {
        'bounded.connectedThirteenByThirteenHeld': 'ORIGINAL_BLANKET_COMPONENT_GT12_HOLD_VS_BOUNDED_CERTIFIED_POLICY_CHANGE_NOT_APPROVED_BY_TEST',
        'negative.noCertifiedCDoesNotInvokeResidualEvenWithClearGlobalWinner': 'R2_C0_FULL13_HOLD_VS_R3_C0_BOUNDED_EXACT_CHANGE_NOT_APPROVED_BY_TEST'},
    'rejectedAttemptsPreserved': {
        'generalWhole16Routing': '../B_stabilization_r3/evidence/attempts/general-route/',
        'unknownHeaderSpreadGetterRead': '../B_stabilization_r3/evidence/attempts/unknown-header-spread/',
        'generalRoutingOriginalR2RegressionNotHidden': True,
        'preWhitelistGetterReads': 1, 'finalGetterReads': 0,
        'physicalTruthValuePresent': False, 'actualProducerTruthFieldClaim': False},
    'shadowRawActivePolicyAssertions': {
        'passed': 19, 'count': 23, 'status': 'FAIL4_NOT_APPLIED_SHADOW',
        'failures': shadow['rawNewPolicyFailuresRetained']['candidate-on'],
        'separateStateControlPass': all(shadow['shadowBehaviorControl'].values())},
    'activeAdditionalNative': {
        'oldRepresentative19': True, 'newNative23': True, 'actualNativeMetadata18': True,
        'traceOffOnExact': active['traceOffOn'],
        'positiveCovarianceFixtureIs419012Reproduction': False},
    'allOriginalNative': {
        'groups': original['originalNative']['groups'], 'off': original['originalNative']['offCount'],
        'on': original['originalNative']['onCount'], 'freshContexts': original['contextsExecuted'],
        'cohortCount': original['cohort']['count'],
        'cohortDiagnostics': original['cohort']['actualDiagnosticPolicy'],
        'allNativeResultDeltasToOldB': sum(row['suites'][suite]['rawDeltaCount'] for row in original['rows'] for suite in ['native', 'cohort']),
        'allPerFixtureFullStateHashDeltasToOldB': sum(row['suites'][suite]['stateHashDeltaCount'] for row in original['rows'] for suite in ['native', 'cohort']),
        'source': 'evidence/original-native-full/SUMMARY.json'},
    'actualSaturation': {
        'source': 'evidence/native-saturation/SUMMARY.json', 'rows': saturation['rows'],
        'shadowFullStateEqualsOldB': saturation['shadowOriginalBFullPrivateStateExact'],
        'equal13FullStateAllProductsExact': saturation['equal13AllProductFullPrivateStateExact'],
        'nativeRfGeneration': False},
    'allRawArtifactsExact': False,
    'additionalDiagnosticDifferences': {
        'status': diagnostics['status'], 'source': 'evidence/native-diagnostic-deltas/SUMMARY.json',
        'rows': [{'kind': row['kind'], 'label': row['label'], 'suite': row.get('suite'),
                  'deltaCounts': row['deltaCounts']} for row in diagnostics['rows']],
        'noFieldIgnored': True, 'oldRawChanged': False, 'approved': False},
    'wallS': {'shadowNative': shadow['wallS'], 'activeNative': active['wallS'],
              'originalNativeAndCohort': original['wallS'], 'nativeSaturation': saturation['wallS']},
    'capturedInputCoverage': 'Independent captured records have unavailable pair arrays. Never treat missing arrays as empty graphs or PASS. Natural-world results are a separate lane.',
    'R1R2R3NaturalFailuresOrResultsPreserved': True,
    'R4NaturalCombatResult': 'OTHER_LANE_PENDING_SEPARATE_REVIEW',
    'browserLaneReturned': True,
    'priorSourceRawOrExpectationsChanged': False,
    'sourcePhysicsOrCoefficientsChanged': False,
    'releaseApproved': False, 'performanceApproved': False, 'naturalRfOrCombatEvidence': False,
}
(P / 'NATIVE_SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'status': summary['status'], 'checks': checks, 'strictOriginalB': strict_result(old_b),
                  'strictOriginalR2': strict_result(old_r2)}, indent=2))
