"""Verify evidence integrity separately from the candidate's remaining regression."""
from pathlib import Path
import gzip, hashlib, json, math, shutil, subprocess

H = Path(__file__).resolve().parent
R = H.parents[3]
O = H / 'results'
E = H / 'evidence'
O.mkdir(exist_ok=True)
E.mkdir(exist_ok=True)
checks, receipts, combined = {}, {}, {}
for group, stem, count in [('primary', 'run', 54), ('controls', 'control', 18)]:
    paths = [Path(f'/tmp/aegis-recovery/{stem}-{i}.json') for i in [1, 2]]
    raw = paths[0].read_bytes()
    checks[group + '.twoIndependentRunsBitIdentical'] = raw == paths[1].read_bytes()
    q = json.loads(raw)
    checks[group + '.complete'] = q['calls'] == count and len(q['versions']) == 3 and sum(len(v['results']) for v in q['versions']) == count
    fixture = json.loads((H / ('cases.json' if group == 'primary' else 'control-cases.json')).read_text())['cases']
    expected = {c['caseId']: c for c in fixture}
    checks[group + '.caseIdsAndMotionParameters'] = all(set(x['caseId'] for x in v['results']) == set(expected) and all(all(x['result'][key] == expected[x['caseId']][key] for key in ['weapon', 'rangeKm', 'altM', 'targetSpeedMps']) for x in v['results']) for v in q['versions'])
    checks[group + '.nativeSuccessOnly'] = all(not x['result']['success'] or x['result']['reason'] == 'INTERCEPT_SUCCESS' and x['result']['fuzeMissM'] is not None for v in q['versions'] for x in v['results'])
    checks[group + '.finite10HzSamples'] = all(math.isfinite(s[k]) for v in q['versions'] for x in v['results'] for s in x['result']['samples'] for k in ['timeS', 'distanceKm', 'altitudeM', 'speedMps', 'mach'])
    checks[group + '.noFullEnvelopeSweep'] = q['fullEnvelopeSweep'] is False
    combined[group] = q
    (O / f'{group}.json.gz').write_bytes(gzip.compress(raw, 9, mtime=0))
    receipts[group] = []
    for i, p in enumerate(paths, 1):
        receipt = json.loads(Path(str(p) + '.receipt.json').read_text())
        checks[f'{group}.{i}.receipt'] = receipt['sha256'] == hashlib.sha256(raw).hexdigest() and receipt['bytes'] == len(raw) and receipt['calls'] == count
        receipts[group].append(receipt)
        (E / f'{group}-run-{i}.json').write_text(json.dumps(receipt, indent=2) + '\n')
        log = Path(f'/tmp/aegis-recovery/{stem}-{i}.log')
        if log.exists():
            shutil.copyfile(log, E / log.name)

inputs = {v: json.loads((H / f'inputs-{v}.json').read_text()) for v in ['BASE', 'RANGE_A', 'RECOVERY']}
def differences(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [q for k in sorted(a.keys() | b.keys()) for q in differences(a.get(k), b.get(k), path + '.' + k)]
    return [] if a == b else [{'path': path, 'before': a, 'after': b}]
diff = differences(inputs['RANGE_A']['data'], inputs['RECOVERY']['data'])
checks['exactTwoDetachedModelDifferences'] = len(diff) == 2 and all(x['path'].endswith('.fullLoftKm') for x in diff)
checks['settingsAndBatteryUnchanged'] = inputs['RANGE_A']['settings'] == inputs['RECOVERY']['settings'] and inputs['RANGE_A']['data']['SAM_MISSILE_PROFILES'] == inputs['RECOVERY']['data']['SAM_MISSILE_PROFILES']
checks['oldEvidenceTrackedChangesZero'] = not subprocess.check_output(['git', 'diff', 'd42284a', '--name-only', '--', 'docs/envelope/C', 'docs/missile/range/A', 'docs/missile/termination/A'], cwd=R, text=True)
static = json.loads((E / 'static.json').read_text())
browser = json.loads((E / 'browser.json').read_text())
checks['staticScope'] = static['pass']
checks['browserNativePath'] = browser['pass'] and len(browser['records']) == 72

by_version = {v: {} for v in inputs}
for q in combined.values():
    for v in q['versions']:
        for x in v['results']:
            by_version[v['version']][x['caseId']] = x
summary = {}
for version, rows in by_version.items():
    summary[version] = {motion: {'successes': sum(x['result']['success'] for x in rows.values() if x['motion'] == motion), 'cases': sum(x['motion'] == motion for x in rows.values())} for motion in ['STATIONARY', 'INBOUND_300', 'OUTBOUND_150', 'OUTBOUND_150_CONTROL_60']}
lost = [k for k, x in by_version['BASE'].items() if x['result']['success'] and not by_version['RECOVERY'][k]['result']['success']]
recovered = [k for k, x in by_version['BASE'].items() if x['result']['success'] and not by_version['RANGE_A'][k]['result']['success'] and by_version['RECOVERY'][k]['result']['success']]
new_losses = [k for k, x in by_version['RANGE_A'].items() if x['result']['success'] and not by_version['RECOVERY'][k]['result']['success']]
checks['knownStationaryFixturesReproduced'] = summary['BASE']['STATIONARY']['successes'] == 6 and summary['RANGE_A']['STATIONARY']['successes'] == 0
result = {'schema': 'AEGIS_RANGE_RECOVERY_A_VERIFICATION_1', 'verificationPass': all(checks.values()), 'checks': checks, 'summary': summary, 'restoredVersusRangeA': recovered, 'baselineSuccessesStillLost': lost, 'newSuccessLossesVersusRangeA': new_losses, 'stationarySixRecovered': summary['RECOVERY']['STATIONARY']['successes'] == 6, 'baselineSuccessesFullyPreserved': not lost, 'candidateQualification': 'PARTIAL_RECOVERY_REMAINING_MOVING_TARGET_REGRESSION' if lost else 'LIMITED_CASES_ONLY_NOT_FULL_ENVELOPE_CERTIFICATION', 'receipts': receipts, 'detachedModelDiff': diff, 'browserNativeCases': len(browser['records']), 'browserSamplePairs': sum(q['samples'] for q in browser['records']), 'full96SweepPerformed': False}
(E / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
raise SystemExit(0 if result['verificationPass'] else 1)
