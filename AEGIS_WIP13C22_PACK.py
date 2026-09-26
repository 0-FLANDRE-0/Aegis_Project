#!/usr/bin/env python3
"""Build profile-driven C22 from the verified C19 package and the C22 record-13 patch."""
import base64
import gzip
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent
baseline = (root / 'Aegis_SIM_v48_WIP13C19.html').read_bytes()
assert hashlib.sha256(baseline).hexdigest() == '152237dbb4517d7b6af5dc7ac0e5dc77c70bc00c6ec02aa17b2e1af57778bd77'
html = baseline.decode()
manifest = list(re.finditer(r'\{"id":"[^"]+","type":"[^"]+","rawBytes":\d+,"gzipBytes":\d+,"sha256":"[a-f0-9]{64}"\}', html))
assert len(manifest) == 14
record = 13
encoded = re.search(fr'<script type="application/octet-stream" data-c55-index="{record}">([^<]+)</script>', html)
assert encoded
with tempfile.TemporaryDirectory() as temp:
    original = Path(temp) / 'original.js'
    updated = Path(temp) / 'updated.js'
    original.write_bytes(gzip.decompress(base64.b64decode(encoded[1])))
    subprocess.run(['patch', '--batch', '--silent', '--output', str(updated), str(original),
                    str(root / 'AEGIS_WIP13C22_13.patch')], check=True)
    raw = updated.read_bytes()
packed = gzip.compress(raw, mtime=0)
html = html[:encoded.start(1)] + base64.b64encode(packed).decode() + html[encoded.end(1):]
entry = json.loads(manifest[record][0])
entry.update(rawBytes=len(raw), gzipBytes=len(packed), sha256=hashlib.sha256(raw).hexdigest())
html = html.replace(manifest[record][0], json.dumps(entry, separators=(',', ':')))
old = '<title>AEGIS v48 WIP13C19 — Burke Exterior Finish</title>'
assert html.count(old) == 1
html = html.replace(old, '<title>AEGIS v48 WIP13C22 — Profile Driven Surface Fuze</title>')
old = "window.C55Packaging.build='V48_WIP13C19';window.C55Packaging.stageStatus='C19_EXTERIOR_VISUAL_CHECKED_BROWSER_PENDING'"
assert html.count(old) == 1
html = html.replace(old, "window.C55Packaging.build='V48_WIP13C22';window.C55Packaging.stageStatus='C22_PROFILE_FUZE_REGRESSION'")
old = "badge.textContent='WIP13C19 · BURKE EXTERIOR'"
assert html.count(old) == 1
html = html.replace(old, "badge.textContent='WIP13C22 · PROFILE FUZE'")
out = root / 'Aegis_SIM_v48_WIP13C22.html'
out.write_text(html)
print(json.dumps({'file':out.name,'bytes':out.stat().st_size,
                  'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
                  'changedRecord':record}))
