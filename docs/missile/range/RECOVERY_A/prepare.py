"""Two-value experimental recovery on the pinned RANGE_A, no engine edits."""
from pathlib import Path
import base64, copy, gzip, hashlib, json, re

H = Path(__file__).resolve().parent
R = H.parents[3]
C = R / 'docs/envelope/C'
NAME = 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'
BASE = R / 'Aegis_SIM_v48_WIP_RANGE_A.html'
if not BASE.exists():
    BASE = R / 'archive/v48/WIP_RANGE_A' / BASE.name
raw = BASE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '8f504eb45c19c34e473d0d04f08180afde95a9c72b5ec935ec0204bd9d7246b5'
h = raw.decode()
m = re.search(r'data-c55-index="13">([^<]+)</script>', h)
s = gzip.decompress(base64.b64decode(m[1])).decode()
edits = [
    ("id:'SM2ER_B4',mode:'LOFT',rangeGoalKm:360,fullLoftKm:360", "id:'SM2ER_B4',mode:'LOFT',rangeGoalKm:360,fullLoftKm:240"),
    ("id:'SM6_B4',mode:'LOFT',rangeGoalKm:450,fullLoftKm:450", "id:'SM6_B4',mode:'LOFT',rangeGoalKm:450,fullLoftKm:260"),
]
for before, after in edits:
    assert s.count(before) == 1
    s = s.replace(before, after)
z = gzip.compress(s.encode(), 9, mtime=0)
h = h[:m.start(1)] + base64.b64encode(z).decode() + h[m.end(1):]
m = re.search(r'const records=(\[.*?\]);', h, re.S)
records = json.loads(m[1])
records[13].update(rawBytes=len(s.encode()), gzipBytes=len(z), sha256=hashlib.sha256(s.encode()).hexdigest())
h = h[:m.start(1)] + json.dumps(records, separators=(',', ':')) + h[m.end(1):]
# Filename/version metadata only; UI nodes, handlers and styles are preserved.
h = h.replace('v48_WIP_RANGE_A', 'v48_WIP_RANGE_RECOVERY_A').replace('V48_WIP_RANGE_A', 'V48_WIP_RANGE_RECOVERY_A')
(R / NAME).write_text(h)
versions = {'BASE': json.loads((C / 'stage0/inputs.json').read_text()), 'RANGE_A': json.loads((C / 'inputs.json').read_text())}
versions['RECOVERY'] = copy.deepcopy(versions['RANGE_A'])
for profile, value in [('SM2ER_BLKIV_ADAPTIVE_ENERGY_LOFT', 240), ('SM6_BLKIA_ADAPTIVE_ENERGY_LOFT', 260)]:
    versions['RECOVERY']['data']['SAM_LOFT_B4_PROFILES'][profile]['fullLoftKm'] = value
    versions['RECOVERY']['profileFingerprintInput']['models']['SAM_LOFT_B4_PROFILES'][profile]['fullLoftKm'] = value
for version, data in versions.items():
    (H / f'inputs-{version}.json').write_text(json.dumps(data, separators=(',', ':')))
conditions = [
    {'id': 'ER150_5', 'weapon': 'SM2ER', 'rangeKm': 150, 'altM': 5000},
    {'id': 'ER267_1', 'weapon': 'SM2ER', 'rangeKm': 267, 'altM': 1000},
    {'id': 'ER323_10', 'weapon': 'SM2ER', 'rangeKm': 323, 'altM': 10000},
    {'id': 'SM6_150_10', 'weapon': 'SM6', 'rangeKm': 150, 'altM': 10000},
    {'id': 'SM6_298_1', 'weapon': 'SM6', 'rangeKm': 298, 'altM': 1000},
    {'id': 'SM6_441_20', 'weapon': 'SM6', 'rangeKm': 441, 'altM': 20000},
]
motions = [{'motion': 'STATIONARY', 'targetSpeedMps': 0}, {'motion': 'INBOUND_300', 'targetSpeedMps': 300}, {'motion': 'OUTBOUND_150', 'targetSpeedMps': -150}]
cases = [{**c, **motion, 'caseId': c['id'] + '_' + motion['motion'], 'telemetry': True} for c in conditions for motion in motions]
(H / 'cases.json').write_text(json.dumps({'seed': 1831565813, 'fixedDtS': 1 / 60, 'conditions': conditions, 'motions': motions, 'cases': cases}, indent=2) + '\n')
controls = [{**c, 'rangeKm': 60, 'originId': c['id'], 'motion': 'OUTBOUND_150_CONTROL_60', 'targetSpeedMps': -150, 'caseId': c['id'] + '_CONTROL60_OUTBOUND_150', 'telemetry': True} for c in conditions]
(H / 'control-cases.json').write_text(json.dumps({'purpose': 'SHORTER_RANGE_MOVING_TARGET_POSITIVE_CONTROL_NOT_RANGE_SWEEP', 'seed': 1831565813, 'fixedDtS': 1 / 60, 'cases': controls}, indent=2) + '\n')
manifest = {'baselineCommit': 'd42284ae4666914c604f77adbde25045a915e93f', 'html': NAME, 'bytes': len(h.encode()), 'sha256': hashlib.sha256(h.encode()).hexdigest(), 'edits': edits, 'tag': 'SIM_TUNED', 'purpose': 'EXPERIMENTAL_RECOVERY_CANDIDATE', 'oldEnvelopeTableRetained': True, 'fullSweepPerformed': False}
(H / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest))
