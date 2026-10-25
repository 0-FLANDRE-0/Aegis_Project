"""Check saved diagnostic arithmetic; does not execute or modify the game."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
meta = json.loads((ROOT / 'provenance.json').read_text())
for name, digest in meta['evidenceSha256'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name

def read(name):
    with (ROOT / name).open(newline='') as f:
        return list(csv.DictReader(f))

native = read('HANDOFF_NATIVE_onset.csv')
ideal = read('HANDOFF_IDEAL_onset.csv')

def at(rows, seconds):
    r = min(rows, key=lambda x: abs(float(x['timeS']) - seconds))
    assert abs(float(r['timeS']) - seconds) < 1e-6
    return r

rows = []
for t in [147.85, 147.95, 148.5]:
    r = at(native, t)
    before = float(r['kfBefore.velocityErrorRawMps'])
    after = float(r['kfAfter.velocityErrorRawMps'])
    assert r['ekfFresh'] == 'True' and r['ekfAccepted'] == 'True'
    assert after > before
    rows.append({'timeS': float(r['timeS']), 'beforeErrorMps': before,
                 'afterErrorMps': after, 'estimatedLateralVelocityMps': float(r['kfAfter.vy'])})

r = at(native, 147.95)
raw = float(r['arhVelocityErrorRawMps'])
consumed = float(r['velocityErrorMps'])
assert abs(raw - consumed) < 1e-10
i = at(ideal, 148.5)
assert float(i['arhVelocityErrorRawMps']) > 200
assert float(i['velocityErrorMps']) < 1e-9
assert abs(float(i['physicalLateralYM'])) < 1

initial = next(x for x in native if x['ekfFresh'] == 'True' and not x['kfBefore.x'])
time = float(initial['timeS'])
anchor = meta['physicalTruthAnchor']
target_x = anchor['targetPosM']['x'] - 250 * (time - anchor['timeS'])
target_y = anchor['targetPosM']['y']
own_y = float(initial['physicalLateralYM'])
own_z = float(initial['altitudeBeforeM'])
range_m = float(initial['rangeKm']) * 1000
dx = math.sqrt(range_m**2 - (target_y - own_y)**2 - (5000 - own_z)**2)
own_x = target_x - dx
mr = float(initial['measurement.rangeM'])
az = float(initial['measurement.azRad'])
el = float(initial['measurement.elRad'])
measured_point = [own_x + mr * math.cos(el) * math.cos(az),
                  own_y + mr * math.cos(el) * math.sin(az),
                  own_z + mr * math.sin(el)]
logged_point = [float(initial['kfAfter.' + x]) for x in ['x', 'y', 'z']]
init_error = math.dist(measured_point, logged_point)
assert init_error < 1e-6

result = {
    'savedEvidenceArithmeticChecks': 'PASS',
    'scope': 'Saved CSV and truth-anchor arithmetic only. No live game execution.',
    'nativeUpdates': rows,
    'rawVersusConsumedErrorDifferenceMpsAt147_95': abs(raw - consumed),
    'idealAdapterAt148_5': {
        'rawReceiverVelocityErrorMps': float(i['arhVelocityErrorRawMps']),
        'consumedVelocityErrorMps': float(i['velocityErrorMps']),
        'physicalLateralYM': float(i['physicalLateralYM'])},
    'nativeInitPositionReconstructionErrorM': init_error,
    'initAssumptions': ['same PRE_DYNAMICS row', 'straight AIR target at z=5000',
                        'target motion anchored to saved actual physical truth']
}
(ROOT / 'evidence_results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
