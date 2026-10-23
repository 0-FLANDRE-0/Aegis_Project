"""Separate single-HTML ZIP and complete limited-experiment evidence ZIP."""
from pathlib import Path
import gzip, hashlib, json, zipfile

H = Path(__file__).resolve().parent
R = H.parents[3]
V = json.loads((H / 'evidence/verification.json').read_text())
assert V['verificationPass']
assert (H / 'REPORT.md').exists()
sha = lambda b: hashlib.sha256(b).hexdigest()
csv = H / 'results/trajectories-10hz.csv'
if csv.exists():
    raw = csv.read_bytes(); dst = csv.with_suffix('.csv.gz'); dst.write_bytes(gzip.compress(raw, 9, mtime=0))
    assert gzip.decompress(dst.read_bytes()) == raw
    csv.unlink()
html_name = 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html'
html = (R / html_name).read_bytes()
execution = 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_HTML.zip'
report = 'Aegis_SIM_v48_WIP_RANGE_RECOVERY_A_REPORT.zip'
def write(name, entries):
    with zipfile.ZipFile(R / name, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path, data in sorted(entries.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0)); info.create_system = 3; info.external_attr = 0o100644 << 16; info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=6)
    with zipfile.ZipFile(R / name) as z:
        assert z.testzip() is None and z.namelist() == sorted(entries)
        for path, data in entries.items():
            assert z.read(path) == data
    data = (R / name).read_bytes()
    return {'file': name, 'bytes': len(data), 'sha256': sha(data), 'members': len(entries), 'crcValid': True, 'allUnpackedBytesVerified': True}
entries = {}
for p in H.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.name not in ['DELIVERY_MANIFEST.json', 'delivery.json', 'remote-publication.json']:
        entries[str(p.relative_to(R))] = p.read_bytes()
support = ['docs/envelope/C/native-engine.js', 'docs/envelope/C/private.js', 'docs/envelope/C/boundaries.json', 'docs/envelope/C/dependencies.json', 'docs/pip/B/browser_backend.py', 'docs/helicopter/H/browser.py', 'docs/multiship/G/browser_g.py', 'docs/bunkerhill/K/browser_i.py', 'docs/performance/F/package.json', 'docs/performance/F/package-lock.json', 'README.md', 'AEGIS_PROJECT_INSTRUCTIONS.md', 'AEGIS_PLAN_STATUS_v48_WIP_RANGE_RECOVERY_A.md', 'SHA256SUMS_v48_WIP_RANGE_RECOVERY_A.txt']
for name in support:
    entries[name] = (R / name).read_bytes()
entries['REPORT_INDEX.md'] = b'# RANGE_RECOVERY_A\n\n[Report](docs/missile/range/RECOVERY_A/REPORT.md) | [Reproduction](docs/missile/range/RECOVERY_A/README.md) | [Evidence](docs/missile/range/RECOVERY_A/evidence/verification.json)\n\nPartial recovery; one moving-target baseline success is still lost. No full envelope sweep. Execution HTML is delivered separately. Raw JSON/CSV retain .gz compression. See DELIVERY_MANIFEST.json for every member hash.\n'
assert not any(n.lower().endswith(('.html', '.zip')) for n in entries)
manifest = {'schema': 'AEGIS_RANGE_RECOVERY_A_REPORT_MANIFEST_1', 'htmlDeliveredSeparately': {'file': html_name, 'bytes': len(html), 'sha256': sha(html)}, 'rawCompression': 'gzip retained with .gz suffix; summary CSV and plots are directly readable', 'files': [{'path': n, 'bytes': len(b), 'sha256': sha(b)} for n, b in sorted(entries.items())]}
mb = (json.dumps(manifest, indent=2) + '\n').encode(); (H / 'DELIVERY_MANIFEST.json').write_bytes(mb); entries['DELIVERY_MANIFEST.json'] = mb
report_info = write(report, entries)
execution_info = write(execution, {html_name: html})
assert execution_info['members'] == 1
for label, info in [('HTML_ZIP', execution_info), ('REPORT_ZIP', report_info)]:
    (R / f'SHA256SUMS_v48_WIP_RANGE_RECOVERY_A_{label}.txt').write_text(info['sha256'] + '  ' + info['file'] + '\n')
result = {'pass': True, 'html': {'file': html_name, 'bytes': len(html), 'sha256': sha(html)}, 'executionZip': execution_info, 'reportZip': report_info, 'reportContainsExecutionHtml': False, 'scenarioQualification': V['candidateQualification']}
(H / 'evidence/delivery.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
