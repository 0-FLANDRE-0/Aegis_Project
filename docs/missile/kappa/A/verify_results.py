"""Verify the requested 14-condition A/B evidence without tuning failures away."""
from pathlib import Path
import filecmp, gzip, hashlib, json, math, shutil

H = Path(__file__).resolve().parent
E = H / 'evidence'; O = H / 'results'
E.mkdir(exist_ok=True); O.mkdir(exist_ok=True)
p = Path('/tmp/aegis-kappa/run-1.json'); raw = p.read_bytes(); j = json.loads(raw)
fixture = json.loads((H / 'cases.json').read_text()); expected = {c['caseId']: c for c in fixture['cases']}
checks = {'twoIndependentRunsBitIdentical': filecmp.cmp(p, '/tmp/aegis-kappa/run-2.json', shallow=False), 'exactly14UniqueConditions': len(expected) == 14 and j['uniqueConditions'] == 14 and j['calls'] == 28, 'noRangeSweep': j['fullEnvelopeSweep'] is False}
versions = {v['version']: {q['caseId']: q for q in v['results']} for v in j['versions']}
checks['completeBeforeAfter'] = set(versions) == {'CURRENT', 'PATCHED'} and all(set(v) == set(expected) for v in versions.values())
checks['sameRequestedKinematics'] = all(all(x['result'][k] == expected[i][k] for k in ['weapon', 'rangeKm', 'altM', 'targetSpeedMps', 'crossSpeedMps']) for v in versions.values() for i, x in v.items())
traces = [x['result']['diagnosticTicks'] for v in versions.values() for x in v.values()]
checks['finiteNativeTrajectory'] = all(math.isfinite(s[k]) for v in versions.values() for x in v.values() for s in x['result']['samples'] for k in ['timeS', 'xM', 'yM', 'altitudeM', 'speedMps', 'mach'])
fresh = [s for trace in traces for s in trace if s['kappaFresh']]
checks['observedPipAndVFinalLogged'] = all(s['kappaPipM'] and s['kappaVFinalMps'] and all(math.isfinite(s[n][axis]) for n in ['kappaPipM', 'kappaVFinalMps'] for axis in ['x', 'y', 'z']) for s in fresh)
configured = sorted({s['configuredPolicy'] for trace in traces for s in trace}); policies = sorted({s['kappaPolicy'] for s in fresh})
checks['onlyDefaultConfiguredPolicyUsed'] = configured == ['PIP_LOS']
checks['tgo90Preserved'] = fresh and all(s['kappaTgoCapS'] == 90 and s['kappaTgoS'] <= 90 + 1e-9 for s in fresh)
checks['nativeFuzeOnlySuccess'] = all(not x['result']['success'] or x['result']['reason'] == 'INTERCEPT_SUCCESS' and x['result']['fuzeMissM'] is not None for v in versions.values() for x in v.values())
receipts = []
for i in [1, 2]:
    r = json.loads(Path(f'/tmp/aegis-kappa/run-{i}.json.receipt.json').read_text()); receipts.append(r)
    checks[f'run{i}Receipt'] = r['sha256'] == hashlib.sha256(raw).hexdigest() and r['bytes'] == len(raw) and r['calls'] == 28
    (E / f'run-{i}-receipt.json').write_text(json.dumps(r, indent=2)+'\n')
    shutil.copyfile(f'/tmp/aegis-kappa/run-{i}.log', E / f'run-{i}.log')
kit = json.loads((H / 'kit/AEGIS_KAPPA_PIP_LOS_Small_Repro_Results.json').read_text())
kit_deltas = []
for q in kit['results']:
    v = versions[q['version']]
    match = next(x['result'] for x in v.values() if x['result']['weapon'] == q['weapon'] and x['result']['rangeKm'] == q['rangeKm'] and x['result']['altM'] == q['altM'] and x['result']['targetSpeedMps'] == q['targetSpeedMps'] and x['result']['crossSpeedMps'] == 0)
    kit_deltas.append({'version': q['version'], 'sameOutcome': match['reason'] == q['reason'] and match['success'] == q['success'], 'timeDeltaS': abs(match['flightTimeS']-q['flightS']), 'closestDeltaM': abs(match['closestM']-q['closestM'])})
checks['providedSmallReproReproduced'] = all(q['sameOutcome'] and q['timeDeltaS'] < 1e-6 and q['closestDeltaM'] < 1e-6 for q in kit_deltas)
static = json.loads((E / 'static.json').read_text()); browser = json.loads((E / 'browser.json').read_text())
checks['staticSourceScope'] = static['pass']; checks['wholeGameNativePathAndIsolation'] = browser['pass'] and len(browser['records']) == 28
summary = {version: {group: {'successes': sum(x['result']['success'] for x in v.values() if x['group'] == group), 'cases': sum(x['group'] == group for x in v.values())} for group in ['SEA_REPRO', 'CONTROL', 'CROSS']} for version, v in versions.items()}
losses = [i for i, x in versions['CURRENT'].items() if x['result']['success'] and not versions['PATCHED'][i]['result']['success']]
gains = [i for i, x in versions['CURRENT'].items() if not x['result']['success'] and versions['PATCHED'][i]['result']['success']]
gates = {'fourSpecifiedSeaImpactsRepaired': summary['CURRENT']['SEA_REPRO']['successes'] == 0 and summary['PATCHED']['SEA_REPRO']['successes'] == 4, 'sixNormalControlsPreserved': summary['CURRENT']['CONTROL']['successes'] == 6 and summary['PATCHED']['CONTROL']['successes'] == 6, 'allExistingSuccessesPreservedIncludingCrossers': not losses, 'sourceAndParametersProtected': static['pass']}
result = {'schema': 'AEGIS_KAPPA_PIP_LOS_A_VERIFICATION_1', 'verificationPass': all(checks.values()), 'checks': checks, 'limited14CaseGatePass': all(gates.values()), 'gates': gates, 'summary': summary, 'successToFailure': losses, 'improvedCases': gains, 'configuredPolicies': configured, 'effectiveFreshPolicies': policies, 'nondefaultPoliciesCertified': False, 'receipts': receipts, 'kitComparison': kit_deltas, 'browserCasePairs': len(browser['records']), 'browserSamplePairs': sum(q['samples'] for q in browser['records']), 'full96SweepPerformed': False, 'fullModelCertification': False}
(E / 'verification.json').write_text(json.dumps(result, indent=2)+'\n')
with gzip.open(O / 'ab-results.json.gz', 'wb', compresslevel=9) as f:
    f.write(raw)
for name in ['build', 'static', 'browser']:
    shutil.copyfile(f'/tmp/aegis-kappa/{name}.log', E / (name+'.log'))
print(json.dumps(result))
raise SystemExit(0 if result['verificationPass'] else 1)
