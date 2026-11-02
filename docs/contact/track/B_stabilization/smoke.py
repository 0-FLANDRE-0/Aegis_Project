"""Original B/friendly smoke executors, unchanged assertions; zero-browser plan.

The idle executor stays intact: both original before/after pages run freshly.
Historical A/B bytes are read-only references, never substituted live pages.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
R = P.parents[3]
B = P.parent / 'B'
A = P.parent / 'A'
E = P / 'evidence/smoke'
CANDIDATE = R / 'Aegis_SIM_v48_WIP_TRACK_B_STABLE_A.html'
PIN = '87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18'
A_PIN = 'e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
B_PIN = '0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'
RUNTIME_PIN = 'a173e069a62db844baa4d0dfd298e43209749c93dab5580deaecc30b76905523'
SOURCE_HEAD = '1d92554026d15f417d987aec519007ea9657a6b6'
NAMES = ('helo-hover', 'helo-route', 'harpoon-route')
JOBS = ('repro', 'auto-iff', 'idle')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def packed(path, value):
    raw = json.dumps(value, separators=(',', ':')).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw, 6, mtime=0))
    return {'path': str(path.relative_to(P)), 'rawSha256': sha(raw), 'gzipSha256': sha(path.read_bytes())}


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def load_runtime():
    assert sha((B / 'verify_runtime.py').read_bytes()) == RUNTIME_PIN
    spec = importlib.util.spec_from_file_location('stable_smoke_frozen_b_runtime', B / 'verify_runtime.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    return runtime


def published_manifest(folder):
    result = {}
    for line in (folder / 'CHECKSUMS.sha256').read_text().splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            result[name.strip()] = digest
    return result


def reference_paths():
    paths = []
    for variant in ('baseline', 'active'):
        base = B / 'evidence/runtime' / variant
        paths += [base / 'reproduction-off.json', base / 'auto-iff-comparison.json', base / 'idle-comparison.json',
                  base / 'friendly/auto-iff.json', base / 'friendly/idle-and-dom.json',
                  base / 'friendly/idle-before120.json', base / 'friendly/idle-after120.json']
        for name in NAMES:
            paths += [base / (name + '-off.json'), base / (name + '-off-full-state.json.gz')]
    paths += [A / 'evidence/candidate' / (name + '-off.json') for name in NAMES]
    paths += [A / 'evidence/candidate/friendly' / name for name in
              ('auto-iff.json', 'idle-and-dom.json', 'idle-before120.json', 'idle-after120.json')]
    return paths


def plan(runtime):
    assert sha(CANDIDATE.read_bytes()) == PIN
    assert sha((R / 'Aegis_SIM_v48_WIP_TRACK_A.html').read_bytes()) == A_PIN
    assert sha((R / 'Aegis_SIM_v48_WIP_TRACK_B.html').read_bytes()) == B_PIN
    assert read(P / 'BUILD.json')['htmlSha256'] == read(P / 'SCOPE.json')['candidateHtmlSha256'] == PIN
    original = runtime.provenance()
    assert original['status'] == 'PASS'
    manifests = {A: published_manifest(A), B: published_manifest(B)}
    references = []
    for path in reference_paths():
        folder = A if path.is_relative_to(A) else B
        digest = sha(path.read_bytes())
        expected = manifests[folder].get(str(path.relative_to(folder)))
        assert digest == expected, ('HISTORICAL_REFERENCE_CHECKSUM_MISMATCH', str(path))
        references.append({'path': str(path.relative_to(R)), 'sha256': digest, 'publishedManifestMatch': True})
    for variant, product_pin in [('baseline', A_PIN), ('active', B_PIN)]:
        base = B / 'evidence/runtime' / variant
        for name in ('reproduction-off.json', 'auto-iff-comparison.json', 'idle-comparison.json'):
            assert read(base / name)['productSha256'] == product_pin
    source_pins = {item['path']: item['sha256'] for item in original['files']}
    for path in [Path(__file__), P / 'SMOKE_PLAN.md', B / 'verify_runtime.py', B / 'regression_runner.py',
                 R / 'docs/contact/friendly/A/repro.py', R / 'docs/envelope/D/verify_world120.py',
                 P / 'BUILD.json', P / 'SCOPE.json', P / 'association.js', P / 'patches.json',
                 A / 'CHECKSUMS.sha256', B / 'CHECKSUMS.sha256']:
        source_pins[str(path.relative_to(R))] = sha(path.read_bytes())
    legacy_idle = R / 'Aegis_SIM_v48_WIP_CG_TURRET_A.html'
    friendly = R / 'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'
    legacy_committed_sha = sha(subprocess.check_output(['git', 'show', SOURCE_HEAD + ':' + legacy_idle.name], cwd=R))
    assert sha(legacy_idle.read_bytes()) == legacy_committed_sha
    assert sha(friendly.read_bytes()) == 'cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'
    products = {CANDIDATE.name: PIN, 'Aegis_SIM_v48_WIP_TRACK_A.html': A_PIN,
                'Aegis_SIM_v48_WIP_TRACK_B.html': B_PIN,
                legacy_idle.name: sha(legacy_idle.read_bytes()), friendly.name: sha(friendly.read_bytes())}
    return {'schema': 'AEGIS_TRACK_B_STABILIZATION_SMOKE_PLAN_1', 'status': 'WAITING_FOR_GO',
            'browserProcessesStarted': 0, 'candidate': CANDIDATE.name, 'candidateSha256': PIN,
            'products': products, 'sourcePins': source_pins, 'historicalReferences': references,
            'originalSourceProvenance': original, 'jobs': list(JOBS), 'freshPages': 6,
            'estimatedWallMinutes': [2.5, 3], 'historicalWallSecondsUsedOnlyForEstimate': [60.7199, 25.3951, 52.3079],
            'actualPaths': {'repro': 'frozen B verify_runtime.natural(False), explicit current HTML,3pages',
                            'auto-iff': 'frozen B original_script -> friendly/auto_iff.py complete runpy,1page',
                            'idle': 'frozen B original_script -> friendly/idle_and_dom.py complete runpy,2fresh pages'},
            'idleBeforeProduct': legacy_idle.name, 'idleAfterProduct': CANDIDATE.name,
            'idleBeforeCommittedReference': {'commit': SOURCE_HEAD, 'sha256': legacy_committed_sha},
            'fullStateHistoricalCoverage': {'repro3': 'A+B complete full-state/observer/P/private RNG',
                                             'auto-iff': 'Existing result/rng only; no historical full snapshot',
                                             'idle': 'Original world120 truth/rng/DOM only; no historical observer full snapshot'},
            'envStatusHandling': 'Exact frozen B await through page.evaluate(__ENV_D__.status())',
            'originalAssertionsOrSourcesChanged': False, 'expectedValuesChanged': False,
            'historicalDifferencesApproved': False, 'releaseApproved': False}


def validate(value):
    assert value['candidateSha256'] == PIN
    for name, expected in value['products'].items():
        assert sha((R / name).read_bytes()) == expected, 'PRODUCT_CHANGED: ' + name
    for name, expected in value['sourcePins'].items():
        assert sha((R / name).read_bytes()) == expected, 'SOURCE_CHANGED: ' + name
    for item in value['historicalReferences']:
        assert sha((R / item['path']).read_bytes()) == item['sha256'], 'HISTORICAL_REFERENCE_CHANGED'


def worker(job, value):
    assert os.environ.get('AEGIS_STABLE_SMOKE_PARENT') == str(os.getppid()), 'Internal worker needs its lease-holding parent'
    validate(value)
    runtime = load_runtime()
    runtime.P = P
    out = E / 'jobs' / job
    out.mkdir(parents=True, exist_ok=True)
    opened, mkdir = Path.open, Path.mkdir
    started = time.perf_counter()
    receipt = {'job': job, 'pid': os.getpid(), 'parentPid': os.getppid(), 'candidateSha256': PIN,
               'runtimeSourceSha256': RUNTIME_PIN, 'completed': False, 'releaseApproved': False}
    save(out / 'WORKER.json', receipt)
    code = 1
    try:
        if job == 'repro':
            code = runtime.natural('stable-active', CANDIDATE, out, False)
        else:
            code = runtime.original_script(job, 'stable-active', CANDIDATE, out)
    except BaseException as error:
        save(out / 'WORKER_FAILURE.json', {'type': type(error).__name__, 'message': str(error),
             'traceback': traceback.format_exc(), 'expectedValuesUpdated': False})
    finally:
        Path.open, Path.mkdir = opened, mkdir
    validate(value)
    receipt.update(completed=True, exitCode=code, wallS=time.perf_counter()-started)
    save(out / 'WORKER.json', receipt)
    return code


def compare(runtime):
    rows = []

    def pair(case, label, before, after, byte_paths=None):
        delta = runtime.differences(before, after)
        detail = packed(E / 'comparisons' / (case + '-' + label + '-all-leaf-differences.json.gz'), delta)
        row = {'case': case, 'reference': label, 'allFieldsExact': not delta,
               'referenceCanonicalSha256': canonical(before), 'candidateCanonicalSha256': canonical(after),
               'allLeafDifferences': detail, 'differingLeaves': len(delta), 'differencesApproved': False}
        if byte_paths:
            old, new = byte_paths
            row.update(referenceFileSha256=sha(old.read_bytes()), candidateFileSha256=sha(new.read_bytes()),
                       fileBytesExact=old.read_bytes() == new.read_bytes())
        rows.append(row)
        return row

    strict = []
    reproduction = read(E / 'jobs/repro/reproduction-off.json')
    for name in NAMES:
        current_path = E / 'jobs/repro' / (name + '-off.json')
        current = read(current_path)
        current_state_path = E / 'jobs/repro' / (name + '-off-full-state.json.gz')
        current_state = json.loads(gzip.decompress(current_state_path.read_bytes()))
        current_row = next(item for item in reproduction['records'] if item['name'] == name)
        for variant, label in [('baseline', 'track-a-fresh'), ('active', 'delivered-b')]:
            base = B / 'evidence/runtime' / variant
            result_path = base / (name + '-off.json')
            state_path = base / (name + '-off-full-state.json.gz')
            result = pair(name + '-result', label, read(result_path), current, (result_path, current_path))
            state = pair(name + '-full-state', label, json.loads(gzip.decompress(state_path.read_bytes())),
                         current_state, (state_path, current_state_path))
            old_row = next(item for item in read(base / 'reproduction-off.json')['records'] if item['name'] == name)
            state['referenceOriginalStateStringSha256'] = old_row['stateSha256']
            state['candidateOriginalStateStringSha256'] = current_row['stateSha256']
            state['originalStateStringHashExact'] = old_row['stateSha256'] == current_row['stateSha256']
            strict += [result['allFieldsExact'], result['fileBytesExact'], state['allFieldsExact'],
                       state['fileBytesExact'], state['originalStateStringHashExact']]
        original_a = A / 'evidence/candidate' / (name + '-off.json')
        official = pair(name + '-official-a-result', 'track-a', read(original_a), current,
                        (original_a, current_path))
        strict += [official['allFieldsExact'], official['fileBytesExact']]
    auto = read(E / 'jobs/auto-iff/friendly/auto-iff.json')
    idle = read(E / 'jobs/idle/friendly/idle-and-dom.json')
    for base, label in [(B / 'evidence/runtime/baseline/friendly', 'track-a-fresh'),
                        (B / 'evidence/runtime/active/friendly', 'delivered-b'),
                        (A / 'evidence/candidate/friendly', 'track-a-official')]:
        old_auto, old_idle = read(base / 'auto-iff.json'), read(base / 'idle-and-dom.json')
        pair('auto-iff-raw-envelope', label, old_auto, auto,
             (base / 'auto-iff.json', E / 'jobs/auto-iff/friendly/auto-iff.json'))
        pair('idle-raw-envelope', label, old_idle, idle,
             (base / 'idle-and-dom.json', E / 'jobs/idle/friendly/idle-and-dom.json'))
        for case, before, after in [('auto-iff-original-checks', old_auto['checks'], auto['checks']),
                                    ('auto-iff-native-result-and-rng', old_auto['result'], auto['result']),
                                    ('idle-original-checks', old_idle['checks'], idle['checks']),
                                    ('idle-truth-dom-core-rows', old_idle['rows'], idle['rows'])]:
            strict.append(pair(case, label, before, after)['allFieldsExact'])
        for tag in ('before', 'after'):
            old = base / ('idle-' + tag + '120.json')
            new = E / 'jobs/idle/friendly' / old.name
            result = pair('idle-' + tag + '120-world', label, read(old), read(new), (old, new))
            strict += [result['allFieldsExact'], result['fileBytesExact']]
    checks = {'reproThreeOriginalCasesComplete': reproduction['allThreeCasesComplete'],
              'reproOriginalExecutorPassed': reproduction['status'] == 'PASS',
              'autoIffOriginalChecksPass': all(auto['checks'].values()) and not auto['errors'],
              'idleBothFreshOriginalChecksPass': all(idle['checks'].values()) and not idle['errors'],
              'strictAvailableNativeAndStateComparisonsExact': all(strict)}
    return {'checks': checks, 'comparisons': rows,
            'rawEnvelopeDifferencesRetainedAndUnapproved': [row for row in rows if 'raw-envelope' in row['case'] and not row['allFieldsExact']],
            'historicalFullSnapshotUnavailable': ['auto-iff observer/P/private RNG', 'idle observer full state'],
            'missingHistoricalSnapshotsNotCountedAsPass': True}


def run(value, go_reference):
    validate(value)
    if (E / 'LEASE.json').exists() or (E / 'jobs').exists() or (E / 'SMOKE_RESULTS.json').exists():
        raise ValueError('Existing smoke execution must be archived; refusing overwrite or automatic retry')
    runtime = load_runtime()
    executions = []
    started = time.perf_counter()
    with runtime.slots.heavy_browser_slot() as lease:
        save(E / 'LEASE.json', {**lease, 'parentPid': os.getpid(), 'goReference': go_reference,
             'maxBrowsersThisController': 1, 'freshPagesPlanned': 6})
        for job in JOBS:
            command = [sys.executable, '-u', str(Path(__file__).resolve()), '--worker', job]
            log = E / (job + '.log')
            at = time.perf_counter()
            with log.open('w') as stream:
                result = subprocess.run(command, cwd=R, env={**os.environ, 'TMPDIR': '/dev/shm',
                         'PYTHONDONTWRITEBYTECODE': '1', 'AEGIS_STABLE_SMOKE_PARENT': str(os.getpid())},
                         stdout=stream, stderr=subprocess.STDOUT, timeout=900)
            executions.append({'job': job, 'exitCode': result.returncode, 'wallS': time.perf_counter()-at,
                               'log': str(log.relative_to(P)), 'logSha256': sha(log.read_bytes())})
            save(E / 'EXECUTIONS.json', executions)
            print(job, 'exit', result.returncode, round(executions[-1]['wallS'], 2), flush=True)
    validate(value)
    comparison = compare(runtime)
    checks = {**comparison['checks'], 'allOriginalWorkersExitedZero': len(executions) == 3 and all(r['exitCode'] == 0 for r in executions)}
    output = {'schema': 'AEGIS_TRACK_B_STABILIZATION_SMOKE_1', 'status': 'PASS' if all(checks.values()) else 'FAIL',
              'candidateSha256': PIN, 'checks': checks, 'executions': executions, **comparison,
              'goReference': go_reference, 'leaseReturned': True, 'freshPages': 6,
              'planSha256': sha((E / 'PLAN.json').read_bytes()), 'wallS': time.perf_counter()-started,
              'originalSourceOrAssertionsChanged': False, 'expectedValuesUpdated': False,
              'historicalDifferencesApproved': False, 'releaseApproved': False}
    output['checks'] = checks
    save(E / 'SMOKE_RESULTS.json', output)
    print(json.dumps({'status': output['status'], 'checks': checks, 'wallS': output['wallS']}))
    return 0 if output['status'] == 'PASS' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--go-reference')
    parser.add_argument('--worker', choices=JOBS, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.worker, read(E / 'PLAN.json'))
    if args.run:
        if args.plan or not args.go_reference:
            parser.error('--run requires --go-reference and cannot be combined with --plan')
        try:
            return run(read(E / 'PLAN.json'), args.go_reference)
        except BaseException as error:
            save(E / 'CONTROLLER_FAILURE.json', {'type': type(error).__name__, 'message': str(error),
                 'traceback': traceback.format_exc(), 'rawEvidenceRetained': True, 'releaseApproved': False})
            raise
    if (E / 'jobs').exists() or (E / 'LEASE.json').exists():
        raise ValueError('Archive existing execution before replacing its PLAN')
    value = plan(load_runtime())
    save(E / 'PLAN.json', value)
    print(json.dumps({'browserProcessesStarted': 0, 'freshPages': value['freshPages'],
                      'jobs': value['jobs'], 'estimatedWallMinutes': value['estimatedWallMinutes'],
                      'candidateSha256': PIN, 'historicalReferences': len(value['historicalReferences'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
