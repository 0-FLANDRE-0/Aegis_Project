"""Hash public GitHub download bytes after pushing only the work branch."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys, urllib.request
from zoneinfo import ZoneInfo

P = Path(__file__).resolve().parent
R = P.parents[3]
commit = sys.argv[1]
assert len(commit) == 40 and all(c in '0123456789abcdef' for c in commit)
protected = {
    'main': '8fdd69533ff96fa652ceec752f6852eaf89fbebc',
    'cg-turret-a': '6d306849f290f987cd39c31c901adb4478b07edd',
    'friendly-contact-a': '4ba64ba0cace9124497a710d00df1b174984ffdc',
    'track-a-contract-trace': 'ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561',
}
refs = subprocess.check_output(
    ['git', 'ls-remote', 'origin', *['refs/heads/' + n for n in protected],
     'refs/heads/track-b-association'], cwd=R, text=True)
actual = {line.split()[1].rsplit('/', 1)[-1]: line.split()[0] for line in refs.splitlines()}
assert all(actual.get(k) == v for k, v in protected.items()), actual
assert actual.get('track-b-association') == commit, actual

paths = [
    'Aegis_SIM_v48_WIP_TRACK_B.html',
    'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html',
    'downloads/Aegis_SIM_v48_WIP_TRACK_B_HTML.zip',
    'downloads/Aegis_SIM_v48_WIP_TRACK_B_SHADOW_HTML.zip',
    'downloads/Aegis_SIM_v48_WIP_TRACK_B_REPORT.zip',
    'downloads/TRACK_B_SHA256SUMS.txt', 'downloads/TRACK_B_ARTIFACTS.json',
    *['docs/contact/track/B/' + n for n in
      ['BUILD.json', 'VALIDATION.json', 'SCOPE.json', 'REPORT.md', 'changes.diff', 'CHECKSUMS.sha256']],
]
records = []
for path in paths:
    url = 'https://raw.githubusercontent.com/0-FLANDRE-0/Aegis_Project/' + commit + '/' + path
    request = urllib.request.Request(url, headers={'User-Agent': 'AEGIS-TRACK-B-readback'})
    digest = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(request, timeout=90) as response:
        content_type = response.headers.get('Content-Type')
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            count += len(block)
    local = hashlib.sha256((R / path).read_bytes()).hexdigest()
    assert digest.hexdigest() == local, path
    assert count == (R / path).stat().st_size, path
    if path.endswith('.zip'):
        assert content_type.split(';')[0] == 'application/zip', (path, content_type)
    records.append({'path': path, 'url': url, 'sha256': local, 'bytes': count,
                    'contentType': content_type, 'remoteBytesMatch': True})

result = {
    'schema': 'AEGIS_TRACK_B_REMOTE_READBACK_1',
    'verifiedAtKst': datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
    'contentCommit': commit, 'workBranch': 'track-b-association',
    'protectedRefs': actual, 'protectedRefsUnchanged': True, 'records': records,
    'allRemoteBytesMatch': True, 'releaseApproved': False,
    'prMergeReleaseTagCreated': False,
    'receiptExcludedFromReportArchiveToAvoidHashCycle': True,
}
(P / 'REMOTE_READBACK.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'remoteFilesVerified': len(records), 'contentCommit': commit,
                  'protectedRefsUnchanged': True, 'releaseApproved': False}))
