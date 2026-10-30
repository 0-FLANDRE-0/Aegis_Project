"""Separate single-HTML ZIP and complete 14-condition Kappa evidence ZIP."""
from pathlib import Path
import hashlib, json, zipfile

H = Path(__file__).resolve().parent
R = H.parents[3]
V = json.loads((H / 'evidence/verification.json').read_text())
assert V['verificationPass']
assert (H / 'REPORT.md').exists()
sha = lambda b: hashlib.sha256(b).hexdigest()
html_name = 'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
html = (R / html_name).read_bytes()
execution = 'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A_HTML.zip'
report = 'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A_REPORT.zip'
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
for p in H.rglob('*.gz'):
    b = bytearray(p.read_bytes()); assert b[:2] == b'\x1f\x8b'; b[4:8] = b'\0'*4; p.write_bytes(b)
entries = {}
for p in H.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.name not in ['DELIVERY_MANIFEST.json', 'delivery.json', 'remote-publication.json'] and p.suffix.lower() != '.zip':
        entries[str(p.relative_to(R))] = p.read_bytes()
support = ['docs/envelope/C/extract.cjs', 'docs/envelope/C/generate.py', 'docs/envelope/C/suite.js', 'docs/envelope/C/ENVELOPE_TABLE_C.json', 'docs/missile/range/RECOVERY_A/inputs-RECOVERY.json', 'docs/envelope/C/native-engine.js', 'docs/envelope/C/private.js', 'docs/envelope/C/boundaries.json', 'docs/envelope/C/dependencies.json', 'docs/pip/B/browser_backend.py', 'docs/helicopter/H/browser.py', 'docs/multiship/G/browser_g.py', 'docs/bunkerhill/K/browser_i.py', 'docs/performance/F/package.json', 'docs/performance/F/package-lock.json', 'README.md', 'AEGIS_PROJECT_INSTRUCTIONS.md', 'AEGIS_PLAN_STATUS_v48_WIP_KAPPA_PIP_LOS_A.md', 'SHA256SUMS_v48_WIP_KAPPA_PIP_LOS_A.txt']
for name in support:
    entries[name] = (R / name).read_bytes()
for name in ['docs/envelope/C/REPORT.md', 'docs/missile/range/RECOVERY_A/REPORT.md']:
    entries[name] = (R / name).read_bytes()
entries['REPORT_INDEX.md'] = b'# KAPPA_PIP_LOS_A\n\n[Report](docs/missile/kappa/A/REPORT.md) | [Reproduction](docs/missile/kappa/A/README.md) | [Evidence](docs/missile/kappa/A/evidence/verification.json)\n\nLimited 14-condition acceptance only; no full envelope sweep or global stability certification. Execution HTML is delivered separately. Raw JSON/CSV retain .gz compression. ENV_C and RECOVERY_A reports are historical pre-patch records. See DELIVERY_MANIFEST.json for every member hash.\n'
assert not any(n.lower().endswith(('.html', '.zip')) for n in entries)
manifest = {'schema': 'AEGIS_KAPPA_PIP_LOS_A_REPORT_MANIFEST_1', 'htmlDeliveredSeparately': {'file': html_name, 'bytes': len(html), 'sha256': sha(html)}, 'rawCompression': 'gzip retained with .gz suffix; summary CSV and plots are directly readable', 'files': [{'path': n, 'bytes': len(b), 'sha256': sha(b)} for n, b in sorted(entries.items())]}
mb = (json.dumps(manifest, indent=2) + '\n').encode(); (H / 'DELIVERY_MANIFEST.json').write_bytes(mb); entries['DELIVERY_MANIFEST.json'] = mb
report_info = write(report, entries)
execution_info = write(execution, {html_name: html})
assert execution_info['members'] == 1
for label, info in [('HTML_ZIP', execution_info), ('REPORT_ZIP', report_info)]:
    (R / f'SHA256SUMS_v48_WIP_KAPPA_PIP_LOS_A_{label}.txt').write_text(info['sha256'] + '  ' + info['file'] + '\n')
result = {'pass': True, 'html': {'file': html_name, 'bytes': len(html), 'sha256': sha(html)}, 'executionZip': execution_info, 'reportZip': report_info, 'reportContainsExecutionHtml': False, 'limited14CaseGatePass': V['limited14CaseGatePass'], 'fullModelCertification': False}
(H / 'evidence/delivery.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
