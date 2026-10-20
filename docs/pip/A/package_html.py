"""Download wrapper only: preserve the verified HTML bytes inside a one-file ZIP."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HTML = 'Aegis_SIM_v48_WIP_PIP_A.html'
BUILD_COMMIT = '9e6e1220de7d28e8df1cf712bb9ef992ce34a83a'
EXPECTED_SHA = '76c77b5c80835f87654c8aa39cd6a82c1ad66de8bc408ebad675997157024847'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'Aegis_SIM_v48_WIP_PIP_A_HTML.zip')
    parser.add_argument('--receipt', type=Path, default=ROOT / 'docs/pip/A/evidence/html-delivery.json')
    args = parser.parse_args()
    original = (ROOT / HTML).read_bytes()
    assert hashlib.sha256(original).hexdigest() == EXPECTED_SHA
    assert original == subprocess.check_output(['git', 'show', BUILD_COMMIT + ':' + HTML], cwd=ROOT)
    # A normalized timestamp makes the wrapper reproducible; it is not a build date.
    entry = zipfile.ZipInfo(HTML, date_time=(2026, 1, 1, 0, 0, 0))
    entry.create_system = 3
    entry.external_attr = 0o100644 << 16
    entry.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        bundle.writestr(entry, original, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(args.output) as bundle:
        assert bundle.namelist() == [HTML]
        assert bundle.testzip() is None
        assert bundle.read(HTML) == original
    packed = args.output.read_bytes()
    receipt = {
        'schema': 'AEGIS_HTML_DOWNLOAD_ZIP_1', 'pass': True,
        'htmlSourceCommit': BUILD_COMMIT, 'html': HTML, 'htmlBytes': len(original),
        'htmlSha256': EXPECTED_SHA, 'zip': args.output.name, 'zipBytes': len(packed),
        'zipSha256': hashlib.sha256(packed).hexdigest(),
        'memberCount': 1, 'members': [HTML], 'crcValid': True,
        'extractedBytesEqualVerifiedHtml': True, 'simulationChanged': False,
        'newSimulationTestsRun': False,
    }
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
