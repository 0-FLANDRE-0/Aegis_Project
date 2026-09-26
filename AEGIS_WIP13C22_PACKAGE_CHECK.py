#!/usr/bin/env python3
"""Check the packed HTML against the exact C19 baseline and its own C55 manifest."""
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
def unpack(name):
    html = (root / name).read_text()
    manifest = [json.loads(m[0]) for m in re.finditer(r'\{"id":"[^"]+","type":"[^"]+","rawBytes":\d+,"gzipBytes":\d+,"sha256":"[a-f0-9]{64}"\}', html)]
    tags = list(re.finditer(r'<script type="application/octet-stream" data-c55-index="(\d+)">([^<]+)</script>', html))
    assert len(manifest) == len(tags) == 14
    records = []
    for i, tag in enumerate(tags):
        assert int(tag[1]) == i
        packed = base64.b64decode(tag[2])
        raw = gzip.decompress(packed)
        assert manifest[i]['rawBytes'] == len(raw)
        assert manifest[i]['gzipBytes'] == len(packed)
        assert manifest[i]['sha256'] == hashlib.sha256(raw).hexdigest()
        records.append(raw)
    return records

before = unpack('Aegis_SIM_v48_WIP13C19.html')
after = unpack('Aegis_SIM_v48_WIP13C22.html')
changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
assert changed == [13], changed
a, b = [r[13].decode() for r in (before, after)]
left, right = 'const C15_ENVELOPE_DATA=', 'function c15SelectShipLod('
assert a[a.index(left):a.index(right, a.index(left))] == b[b.index(left):b.index(right, b.index(left))]
assert b.count('const SURFACE_MISSILE_PROXIMITY_WIP13C22=') == 1
assert 'standoffM:9' not in b and 'standoffM:7' not in b
assert 'function surfaceMissileFuzeEnvelopeWip13C22(' in b
assert 'actuationRadiusM:Math.min(detectionRadiusM,lethalRadiusM)' in b
assert 'surfaceTargetRcsM2Wip13A(entity' in b
print(json.dumps({'pass': True, 'records': 14, 'changedRecords': changed,
                  'burkeExteriorUnchanged': before[11:13] == after[11:13],
                  'c15InteriorMaskUnchanged': True}, ensure_ascii=False))
