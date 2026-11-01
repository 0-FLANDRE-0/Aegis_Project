"""Read immutable GitHub artifact bytes after a work-branch push. No writes to GitHub."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

P = Path(__file__).resolve().parent
R = P.parents[3]
REPO = '0-FLANDRE-0/Aegis_Project'


def local_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def download(commit, row):
    path = urllib.parse.quote(row['path'], safe='/')
    urls = [f'https://github.com/{REPO}/raw/{commit}/{path}',
            f'https://raw.githubusercontent.com/{REPO}/{commit}/{path}']
    attempts = []
    for url in urls:
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'AEGIS-artifact-checksum-readback'})
                digest, count, prefix = hashlib.sha256(), 0, b''
                with urllib.request.urlopen(req, timeout=45) as response:
                    status = response.status
                    mime = response.headers.get('Content-Type')
                    # Do not log redirect URLs/headers: private GitHub URLs can
                    # contain temporary credentials. Only the public request URL is recorded.
                    while chunk := response.read(1024 * 1024):
                        if not prefix:
                            prefix = chunk[:4]
                        digest.update(chunk)
                        count += len(chunk)
                result = {'path': row['path'], 'requestedUrl': url, 'status': status,
                          'contentType': mime, 'bytes': count, 'sha256': digest.hexdigest(),
                          'expectedBytes': row['bytes'], 'expectedSha256': row['sha256'],
                          'sha256Matches': digest.hexdigest() == row['sha256'],
                          'sizeMatches': count == row['bytes'], 'attempts': attempts}
                if row['path'].endswith('.zip'):
                    result['zipMagicMatches'] = prefix == b'PK\x03\x04'
                assert result['sha256Matches'] and result['sizeMatches'], 'REMOTE_BYTES_MISMATCH'
                assert result.get('zipMagicMatches', True), 'REMOTE_NOT_ZIP'
                return result
            except (urllib.error.URLError, TimeoutError, AssertionError) as exc:
                # Exception strings can embed a redirected URL. Record only
                # the class and HTTP status, never credential-bearing URLs.
                attempts.append({'urlKind': 'githubRaw' if url == urls[0] else 'rawHost',
                                 'attempt': attempt + 1, 'errorType': type(exc).__name__,
                                 'httpStatus': getattr(exc, 'code', None)})
                time.sleep(2)
    raise RuntimeError('REMOTE_READBACK_FAILED: ' + row['path'] + ' ' + json.dumps(attempts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    assert re.fullmatch('[0-9a-f]{40}', args.commit)
    artifacts = json.loads((P / 'ARTIFACTS.json').read_text())
    validation = json.loads((P / 'VALIDATION.json').read_text())
    rows = list(artifacts['archives'])
    for key in ['active', 'shadow']:
        record = validation[key]
        path = R / record['file']
        rows.append({'path': record['file'], 'bytes': path.stat().st_size,
                     'sha256': record['sha256']})
    for relative in ['deliverables/track-b-stabilization-a/SHA256SUMS.txt',
                     str((P / 'VALIDATION.json').relative_to(R))]:
        path = R / relative
        rows.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': local_sha(path)})
    completed = []
    for row in rows:
        assert local_sha(R / row['path']) == row['sha256']
        result = download(args.commit, row)
        completed.append(result)
        print(json.dumps({'path': result['path'], 'sha256Matches': result['sha256Matches'],
                          'bytes': result['bytes']}), flush=True)
    baseline = json.loads((P.parent / 'B_stabilization/BASELINE.json').read_text())
    names = [*baseline['protectedRefs'], 'refs/heads/track-b-stabilization-a']
    refs = {line.split()[1]: line.split()[0] for line in
            subprocess.check_output(['git', 'ls-remote', 'origin', *names], cwd=R, text=True).splitlines()}
    assert refs['refs/heads/track-b-stabilization-a'] == args.commit
    result = {'schema': 'AEGIS_TRACK_B_STABILIZATION_REMOTE_READBACK_1',
              'artifactCommit': args.commit, 'readbackUtc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'status': 'PASS', 'files': completed, 'remoteRefs': refs,
              'protectedRefDifferencesSinceStart': [{'ref': k, 'before': v, 'now': refs.get(k)}
                   for k, v in baseline['protectedRefs'].items() if refs.get(k) != v],
              'remoteWriteScopeByThisWork': ['refs/heads/track-b-stabilization-a'],
              'mainOrReferenceBranchPushesByThisWork': 0, 'prOrReleaseOrTagCreated': False,
              'activePromotionApproved': False}
    (P / 'REMOTE_READBACK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'files': len(completed), 'artifactCommit': args.commit}))


if __name__ == '__main__':
    main()
