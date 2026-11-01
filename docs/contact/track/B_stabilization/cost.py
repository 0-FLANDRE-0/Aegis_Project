"""Read-only plan, then explicitly authorized exclusive fixed-tick cost follow-up.

Only frozen B cost-controller primitives and original A benchmark/fixtures are
reused. No HeapProfiler, allocation wrapper, forced GC or new workload is used.
Default/--plan starts zero browsers. --run also requires a root GO reference.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
import time
import traceback

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]
B = P.parent / 'B'
E = P / 'evidence/cost'
FROZEN_SOURCES = {
    'docs/contact/track/B/measure_cost_final.py': 'e64bee5a2b2569243a63a39a0f16a85ca0a10f9f76a3837bc016aee4b64f0206',
    'docs/contact/track/B/verify_runtime.py': 'a173e069a62db844baa4d0dfd298e43209749c93dab5580deaecc30b76905523',
    'docs/contact/track/A/verify_runtime.py': 'f013a66d3fe6be98f59c670e49855e00e4c8f4eed628a9691ecec3406218474f',
}
CONFIGS = [('track-a-off', 'A', False), ('old-b-off', 'B', False),
           ('stable-shadow-off', 'S', False), ('stable-active-off', 'N', False),
           ('stable-active-on', 'N', True)]
WARMUP = {'kind': 'HELO', 'moving': True, 'seconds': 30, 'observe': False, 'seed': 419010}
TICKS = 2400


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def packed(path, value):
    raw = json.dumps(value, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(raw, 6, mtime=0))
    return {'path': str(path.relative_to(P)), 'rawSha256': sha(raw), 'gzipSha256': sha(path.read_bytes())}


def load_legacy():
    for relative, expected in FROZEN_SOURCES.items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('ORIGINAL_COST_OR_BENCHMARK_SOURCE_CHANGED: ' + relative)
    spec = importlib.util.spec_from_file_location('stable_original_b_final_cost', B / 'measure_cost_final.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_plan(legacy):
    active, shadow = read(P / 'BUILD.json'), read(P / 'BUILD_SHADOW.json')
    pair = read(P / 'MODE_PAIR_PROOF.json')
    assert pair['pass'] and pair['mainEqualAfterSingleTokenNormalization']
    assert pair['activeHtmlSha256'] == active['htmlSha256'] and pair['shadowHtmlSha256'] == shadow['htmlSha256']
    products = {'A': {'file': 'Aegis_SIM_v48_WIP_TRACK_A.html', 'sha256': 'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'},
                'B': {'file': 'Aegis_SIM_v48_WIP_TRACK_B.html', 'sha256': '0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'},
                'S': {'file': shadow['output'], 'sha256': shadow['htmlSha256']},
                'N': {'file': active['output'], 'sha256': active['htmlSha256']}}
    for item in products.values():
        assert sha((R / item['file']).read_bytes()) == item['sha256']
    for name, expected in [('SCOPE.json', active['htmlSha256']), ('SCOPE_SHADOW.json', shadow['htmlSha256'])]:
        scope = read(P / name)
        assert scope['pass'] and scope['candidateHtmlSha256'] == expected
    source_provenance = legacy.runtime.provenance()
    assert source_provenance['status'] == 'PASS'
    pins = {**FROZEN_SOURCES}
    pins.update({item['path']: item['sha256'] for item in source_provenance['files']})
    pins['docs/contact/track/B/regression_runner.py'] = source_provenance['sharedRegressionRunnerSha256']
    for path in [Path(__file__), P / 'COST_PLAN.md', P / 'BUILD.json', P / 'BUILD_SHADOW.json',
                 P / 'MODE_PAIR_PROOF.json', P / 'SCOPE.json', P / 'SCOPE_SHADOW.json',
                 P / 'association.js', P / 'patches.json', P / 'build-manifest.json']:
        pins[str(path.relative_to(R))] = sha(path.read_bytes())
    return {'schema': 'AEGIS_TRACK_B_STABILIZATION_COST_PLAN_1', 'status': 'WAITING_FOR_EXCLUSIVE_GO',
            'browserProcessesStarted': 0, 'products': products, 'sourceAndProofPins': pins,
            'originalSourceProvenance': source_provenance,
            'configs': [list(c) for c in CONFIGS],
            'orders': [list(c) for c in CONFIGS] + [list(c) for c in reversed(CONFIGS)],
            'repetitions': 2, 'warmup': WARMUP, 'measuredFixedTicksPerSample': TICKS,
            'measuredFixedTicksTotal': TICKS * 10, 'warmupFixedTicksTotal': 18000,
            'estimatedExclusiveWallMinutes': [3.5, 5],
            'estimateBasis': 'Historical quiescent six CPU samples: 103.7s total,17.3s/sample; used only to estimate execution time.',
            'cpuBenchmark': '__TRACK_RUNTIME_A__.bench(2400), unchanged original fixed-tick loop',
            'stateValidation': 'Original A passive state plus unchanged B FULL_STATE_HELPER; no field exclusions',
            'heapMetric': 'NET_LIVE_JS_HEAP_DELTA_NOT_TOTAL_ALLOCATION_OR_CHURN',
            'heapSampling': False, 'kernelWrappers': False, 'forcedGC': False,
            'dense128LimitSeparateAndUnchanged': 'Prior Node dense128 worst about42ms remains a separate limitation; this ordinary workload does not resolve it.',
            'productOrCoefficientChanges': False, 'expectedValuesChanged': False, 'releaseApproved': False}


def validate_plan(plan):
    for relative, expected in plan['sourceAndProofPins'].items():
        if sha((R / relative).read_bytes()) != expected:
            raise ValueError('PLANNED_INPUT_CHANGED: ' + relative)
    for item in plan['products'].values():
        if sha((R / item['file']).read_bytes()) != item['sha256']:
            raise ValueError('PLANNED_PRODUCT_CHANGED: ' + item['file'])


def run(plan, legacy, go_reference):
    validate_plan(plan)
    if execution_exists():
        raise ValueError('Existing cost evidence must be archived before a new execution; refusing overwrite')
    from playwright.sync_api import sync_playwright
    support = legacy.support
    harness = support.load_harness()
    helpers = ((R / 'docs/contact/friendly/A/repro.js').read_text() + '\n' +
               support.PASSIVE_HELPER + '\n' + legacy.runtime.FULL_STATE_HELPER)
    rows, errors = [], []
    started = time.perf_counter()
    initial_resource = legacy.resource()
    with legacy.exclusive_browser_budget() as lease:
        lease.update(goReference=go_reference, broadCpuWorkMustBePausedByRoot=True)
        save(E / 'LEASE.json', lease)
        assert not legacy.browser_mains(), 'Other browser before exclusive cost window'
        raw_products = {key: harness.base.build(file=item['file'], record=False, extra=helpers)
                        for key, item in plan['products'].items()}
        save(E / 'TEST_COPIES.json', {key: {'productSha256': plan['products'][key]['sha256'],
             'testCopySha256': sha(raw if isinstance(raw, bytes) else raw.encode())}
             for key, raw in raw_products.items()})
        for repetition, order in [(0, CONFIGS), (1, list(reversed(CONFIGS)))]:
            for label, product, enabled in order:
                tag = f'cpu-{repetition}-{label}'
                save(E / (tag + '-preflight.json'), {'browserMains': legacy.browser_mains(),
                     'resource': legacy.resource(), 'observedAtUnixS': time.time()})
                assert not legacy.browser_mains(), 'Other active browser before fresh cost sample'
                server = None
                at = time.perf_counter()
                with sync_playwright() as playwright:
                    browser = harness.launch(playwright)
                    try:
                        server, url = harness.serve(raw_products[product])
                        page = harness.load_fast_http(browser, url, own='CG_52_LATE_TICONDEROGA', errors=errors)
                        page.set_default_timeout(600000)
                        page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear();if(window.__TRACK_B__){__TRACK_B__.configure({enabled:on,capacity:4096});__TRACK_B__.clear();}}', enabled)
                        page.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)', WARMUP)
                        warm_state = page.evaluate('__TRACK_RUNTIME_B_TEST__.state()')
                        warm_raw = packed(E / (tag + '-warm-full-state.json.gz'), json.loads(warm_state))
                        session = page.context.new_cdp_session(page)
                        heap_before = session.send('Runtime.getHeapUsage')
                        bench = page.evaluate('n=>__TRACK_RUNTIME_A__.bench(n)', TICKS)
                        heap_after = session.send('Runtime.getHeapUsage')
                        session.detach()
                        # Preserve native return before diagnostics/env/readback queries.
                        native_raw = packed(E / (tag + '-native-benchmark-before-aux-queries.json.gz'), bench)
                        state_before = page.evaluate('__TRACK_RUNTIME_B_TEST__.state()')
                        env = page.evaluate('__ENV_D__.status()')
                        diagnostic = page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})')
                        state_after = page.evaluate('__TRACK_RUNTIME_B_TEST__.state()')
                        core = page.evaluate('__CORE_SELFTEST_FAILURES__')
                        checks = {'oneNativeOwner': len(bench['beforeObserverTicks']) == len(bench['afterObserverTicks']) == 1,
                                  'ownersOncePerFixedTick': all(b['ticks']-a['ticks'] == TICKS for a, b in zip(bench['beforeObserverTicks'], bench['afterObserverTicks'])),
                                  'readOnlyQueriesPreserveFullState': state_before == state_after,
                                  'benchmarkAndAfterActionAStateExact': json.loads(state_before)['a'] == json.loads(bench['state']),
                                  'envHashMatch': env['match'] is True, 'coreSelftestsZero': not core,
                                  'aSinkErrorsZero': diagnostic['a']['stats']['errors'] == 0,
                                  'bSinkErrorsZero': diagnostic['b'] is None or diagnostic['b']['stats']['errors'] == 0}
                        costs = bench['costs']
                        row = {'label': label, 'product': product, 'trace': enabled, 'repetition': repetition,
                               'productSha256': plan['products'][product]['sha256'], 'fixedTicks': TICKS,
                               'meanTickMs': sum(costs)/len(costs), 'medianTickMs': support.percentile(costs, .5),
                               'p95TickMs': support.percentile(costs, .95), 'checks': checks,
                               'warmFullStateSha256': sha(warm_state.encode()), 'warmFullState': warm_raw,
                               'aPassiveStateSha256': sha(bench['state'].encode()),
                               'fullStateSha256': sha(state_before.encode()),
                               'fullState': packed(E / (tag + '-full-state.json.gz'), json.loads(state_before)),
                               'aPassiveState': packed(E / (tag + '-a-state.json.gz'), json.loads(bench['state'])),
                               'rawBenchmarkBeforeAuxiliaryQueries': native_raw,
                               'tickCosts': packed(E / (tag + '-tick-costs.json.gz'), costs),
                               'trackCounts': bench['counts'], 'observerBefore': bench['beforeObserverTicks'],
                               'observerAfter': bench['afterObserverTicks'], 'envStatus': env,
                               'diagnosticCounts': {'a': len(diagnostic['a']['records']), 'b': len(diagnostic['b']['records']) if diagnostic['b'] else 0},
                               'heapBefore': heap_before, 'heapAfter': heap_after,
                               'liveHeapDeltaBytes': heap_after['usedSize']-heap_before['usedSize'],
                               'heapMetric': 'NET_LIVE_JS_HEAP_DELTA_INCLUDES_BENCHMARK_RESULT_NOT_TOTAL_ALLOCATION_OR_CHURN',
                               'samplingOrForcedGCUsed': False, 'elapsedWallS': time.perf_counter()-at,
                               'resourceAfter': legacy.resource(), 'automaticApproval': False}
                        rows.append(row)
                        save(E / (tag + '-row.json'), row)
                        print(tag, 'mean', round(row['meanTickMs'], 4), 'p95', round(row['p95TickMs'], 4),
                              'checks', all(checks.values()), flush=True)
                    finally:
                        browser.close()
                        if server:
                            server.shutdown()
                assert not legacy.browser_mains(), 'Browser remains after sample close'
    validate_plan(plan)
    checks = {'tenSamplesComplete': len(rows) == 10,
              'allNativeChecksPass': all(all(row['checks'].values()) for row in rows),
              'warmFullStateExactAcrossConfigsAndRepetitions': len({row['warmFullStateSha256'] for row in rows}) == 1,
              'bodyTracksPAndPrivateRngExactAcrossConfigsAndRepetitions': len({row['fullStateSha256'] for row in rows}) == 1,
              'originalAPassiveStateExactAcrossConfigsAndRepetitions': len({row['aPassiveStateSha256'] for row in rows}) == 1,
              'browserErrorsZero': not errors, 'browsersClosed': not legacy.browser_mains()}
    comparable = all(checks.values())
    if not checks['bodyTracksPAndPrivateRngExactAcrossConfigsAndRepetitions']:
        reference = json.loads(gzip.decompress((P / rows[0]['fullState']['path']).read_bytes()))
        for i, row in enumerate(rows[1:], 1):
            observed = json.loads(gzip.decompress((P / row['fullState']['path']).read_bytes()))
            delta = legacy.runtime.differences(reference, observed)
            row['unapprovedFullStateDelta'] = packed(E / f'comparison-{i}-full-state-delta.json.gz', delta)
            row['differingLeaves'] = len(delta)
    summaries = {}
    for label, _, _ in CONFIGS:
        selected = [row for row in rows if row['label'] == label]
        summaries[label] = {'meanTickMs': sum(row['meanTickMs'] for row in selected)/len(selected),
                            'meanOfPerRunP95TickMs': sum(row['p95TickMs'] for row in selected)/len(selected),
                            'individualMeanTickMs': [row['meanTickMs'] for row in selected],
                            'individualP95TickMs': [row['p95TickMs'] for row in selected],
                            'liveHeapDeltasBytes': [row['liveHeapDeltaBytes'] for row in selected]}
    if comparable:
        for result in summaries.values():
            result['meanOverheadVsTrackAPercent'] = (result['meanTickMs']/summaries['track-a-off']['meanTickMs']-1)*100
            result['meanOverheadVsOldBPercent'] = (result['meanTickMs']/summaries['old-b-off']['meanTickMs']-1)*100
    value = {'schema': 'AEGIS_TRACK_B_STABILIZATION_COST_1', 'status': 'PASS' if comparable else 'NOT_COMPARABLE',
             'comparisonEligible': comparable, 'checks': checks, 'records': rows, 'summary': summaries,
             'browserErrors': errors, 'goReference': go_reference, 'exclusiveBrowserLease': lease,
             'planSha256': sha((E / 'PLAN.json').read_bytes()), 'initialResource': initial_resource,
             'finalResource': legacy.resource(), 'wallS': time.perf_counter()-started,
             'heapMetric': plan['heapMetric'], 'dense128LimitSeparateAndUnchanged': plan['dense128LimitSeparateAndUnchanged'],
             'noOutliersDiscarded': True, 'expectedValuesChanged': False,
             'productOrCoefficientChanges': False, 'performanceApproved': False, 'releaseApproved': False}
    save(E / 'SUMMARY.json', value)
    print(json.dumps({'status': value['status'], 'comparisonEligible': comparable, 'checks': checks, 'wallS': value['wallS']}))
    return 0 if comparable else 1


def execution_exists():
    return (E / 'SUMMARY.json').exists() or (E / 'LEASE.json').exists() or bool(list(E.glob('cpu-*')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--go-reference', help='Root instruction identifying the exclusive browser/CPU time window')
    args = parser.parse_args()
    if args.run and (args.plan or not args.go_reference):
        parser.error('--run requires --go-reference and cannot be combined with --plan')
    legacy = load_legacy()
    if not args.run:
        if execution_exists():
            raise ValueError('Existing cost execution must be archived before replacing its PLAN')
        plan = make_plan(legacy)
        save(E / 'PLAN.json', plan)
        print(json.dumps(plan, indent=2))
        return 0
    try:
        return run(read(E / 'PLAN.json'), legacy, args.go_reference)
    except Exception as error:
        save(E / 'EXECUTION_FAILURE.json', {'schema': 'AEGIS_TRACK_B_STABILIZATION_COST_FAILURE_1',
             'errorType': type(error).__name__, 'message': str(error),
             'traceback': traceback.format_exc(), 'goReference': args.go_reference,
             'browserRunApprovedByThisReceipt': False, 'performanceApproved': False,
             'productOrExpectedValueChanges': False})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
