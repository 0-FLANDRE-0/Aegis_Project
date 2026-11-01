"""Deterministic local packaging only; never pushes, merges or publishes.

Run after the root report is finalized. HTML products and evidence are separate
archives. Existing failed/aborted attempts are retained, not pruned to make a
pass-only package. Test controllers assume a checkout of the source repository.
"""
from pathlib import Path
import hashlib
import json
import zipfile

P = Path(__file__).resolve().parent
R = P.parents[3]
OUT = R / 'deliverables' / 'track-b-stabilization-a'
STAMP = (2026, 11, 2, 0, 0, 0)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def archive(path, files):
    rows = []
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as z:
        for name, source in sorted(files.items()):
            raw = source.read_bytes()
            entry = zipfile.ZipInfo(name, STAMP)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            z.writestr(entry, raw, compress_type=zipfile.ZIP_DEFLATED,
                       compresslevel=6)
            rows.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw)})
        meta = zipfile.ZipInfo('ARCHIVE_MANIFEST.json', STAMP)
        z.writestr(meta, json.dumps({'files': rows}, indent=2) + '\n')
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for row in rows:
            assert sha(z.read(row['path'])) == row['sha256']
    return {'path': str(path.relative_to(R)), 'bytes': path.stat().st_size,
            'sha256': sha(path.read_bytes()), 'files': len(rows),
            'roundTripVerified': True}


def main():
    validation = json.loads((P / 'VALIDATION.json').read_text())
    assert validation['reportFinalized'] is True
    assert validation['expectedValuesUpdated'] is False
    assert validation['mainOrReferenceBranchesModified'] is False
    OUT.mkdir(parents=True, exist_ok=True)
    html_files = {}
    for name in ['Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html',
                 'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C_SHADOW.html']:
        path = R / name
        assert path.is_file()
        html_files[name] = path
    html_files['README.md'] = P / 'DOWNLOAD_README.md'
    html_files['VALIDATION.json'] = P / 'VALIDATION.json'
    evidence = {}
    for stage in ['B_stabilization', 'B_stabilization_r2', 'B_stabilization_r3']:
        base = P.parent / stage
        for path in sorted(base.rglob('*')):
            if (path.is_file() and '__pycache__' not in path.parts
                    and path.suffix not in ('.pyc', '.html')
                    and path.name not in ('ARTIFACTS.json', 'REMOTE_READBACK.json')):
                evidence[str(path.relative_to(R))] = path
    rows = [archive(OUT / 'TRACK_B_STABILIZATION_HTML.zip', html_files),
            archive(OUT / 'TRACK_B_STABILIZATION_REPORT.zip', evidence)]
    result = {'schema': 'AEGIS_TRACK_B_STABILIZATION_ARTIFACTS_1',
              'trackBStatus': validation['trackBStatus'],
              'releaseApproved': False, 'archives': rows,
              'htmlSeparateFromReport': True, 'noUploadPerformed': True}
    (P / 'ARTIFACTS.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'SHA256SUMS.txt').write_text(''.join(
        x['sha256'] + '  ' + Path(x['path']).name + '\n' for x in rows))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
