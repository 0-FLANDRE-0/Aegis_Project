"""Package a frozen, fully checked TRACK-A candidate; never approve baseline debt."""
from pathlib import Path
import gzip, hashlib, json, zipfile

P = Path(__file__).resolve().parent
R = P.parents[3]
D = R / 'downloads'
D.mkdir(exist_ok=True)

def sha(data):
    return hashlib.sha256(data).hexdigest()

validation = json.loads((P / 'VALIDATION.json').read_text())
build = json.loads((P / 'BUILD.json').read_text())
html = R / validation['candidate']
assert validation['trackAStatus'] == 'PASS' and validation['finalEvidenceComplete']
assert not validation['releaseApproved'] and validation['finalClosure'] == 'INCOMPLETE'
assert sha(html.read_bytes()) == validation['candidateSha256'] == build['htmlSha256']
assert all(validation['checks'].values())

# Raw per-tick JSONL remains byte-exact after lossless compression. Historical
# evidence is retained; source execution paths may now have a .gz companion.
compressed_path = P / 'RAW_COMPRESSION.json'
compressed = json.loads(compressed_path.read_text()) if compressed_path.exists() else []
for source in sorted((P / 'evidence').rglob('*.jsonl')):
    data = source.read_bytes()
    target = Path(str(source) + '.gz')
    assert not target.exists(), str(target)
    packed = gzip.compress(data, compresslevel=6, mtime=0)
    target.write_bytes(packed)
    assert gzip.decompress(packed) == data
    compressed.append({
        'original': str(source.relative_to(P)), 'gzip': str(target.relative_to(P)),
        'originalSha256': sha(data), 'gzipSha256': sha(packed),
        'originalBytes': len(data), 'gzipBytes': len(packed), 'losslessVerified': True,
    })
    source.unlink()
compressed_path.write_text(json.dumps(compressed, indent=2) + '\n')

def include(path):
    return (path.is_file() and '__pycache__' not in path.parts
            and path.name != 'REMOTE_READBACK.json' and path.suffix != '.flag')

files = [p for p in sorted(P.rglob('*')) if include(p) and p.name != 'CHECKSUMS.sha256']
(P / 'CHECKSUMS.sha256').write_text(''.join(
    sha(p.read_bytes()) + '  ' + str(p.relative_to(P)) + '\n' for p in files))

def write_zip(target, entries):
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, source in entries:
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, source.read_bytes())
    assert target.stat().st_size < 100 * 1024 * 1024, 'GitHub 100MiB file limit'
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert z.namelist() == [n for n, _ in entries]
        for name, source in entries:
            assert sha(z.read(name)) == sha(source.read_bytes()), name

artifacts = []
entries_by_kind = {
    'HTML': [(html.name, html)],
    'REPORT': [('TRACK_A/' + str(p.relative_to(P)), p)
               for p in sorted(P.rglob('*')) if include(p)],
}
for kind, entries in entries_by_kind.items():
    target = D / ('Aegis_SIM_v48_WIP_TRACK_A_' + kind + '.zip')
    write_zip(target, entries)
    artifacts.append({'kind': kind, 'path': str(target.relative_to(R)),
                      'sha256': sha(target.read_bytes()),
                      'bytes': target.stat().st_size, 'members': len(entries),
                      'allMembersReadBackAndHashVerified': True})
(D / 'TRACK_A_SHA256SUMS.txt').write_text(
    sha(html.read_bytes()) + '  ' + html.name + '\n' + ''.join(
        a['sha256'] + '  ' + Path(a['path']).name + '\n' for a in artifacts))
result = {'schema': 'AEGIS_TRACK_A_PACKAGE_1', 'htmlSha256': sha(html.read_bytes()),
          'artifacts': artifacts, 'releaseApproved': False,
          'reportExcludes': ['HTML (separate download)', 'REMOTE_READBACK.json (post-push receipt)',
                             '*.flag (ephemeral runner coordination)', '__pycache__'],
          'replayDependencies': 'Existing repository test fixtures, historical HTMLs, Chromium/Playwright, Node/acorn'}
(D / 'TRACK_A_ARTIFACTS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
