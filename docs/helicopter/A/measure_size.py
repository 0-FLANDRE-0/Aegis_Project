"""Assemble only the new asset and decoder; do not write a game release."""
import base64, hashlib, json
from pathlib import Path
from prepare_source import baseline_path, BASELINE_SHA
ROOT = Path(__file__).resolve().parent
baseline = baseline_path().read_bytes()
assert hashlib.sha256(baseline).hexdigest() == BASELINE_SHA
asset = (ROOT / 'seahawk-render-a1.bin.gz').read_bytes()
encoded = base64.b64encode(asset).decode()
loader = (ROOT / 'asset_loader.js').read_text()
addition = ('\n<!-- HELICOPTER ASSET SIZE PROBE; NOT A GAME RELEASE -->\n'
            '<script id="helicopter-render-a1" type="application/octet-stream">' + encoded + '</script>\n'
            '<script>' + loader + '</script>\n').encode()
out = {'baselineBytes': len(baseline), 'baselineSha256': BASELINE_SHA, 'packedAssetBytes': len(asset), 'assetBase64Bytes': len(encoded), 'loaderBytes': len(loader.encode()), 'probeBytes': len(baseline) + len(addition), 'additionalHtmlBytes': len(addition), 'additionalPercent': len(addition) / len(baseline) * 100, 'limits': 'Actual byte assembly of packed asset+existing-engine decoder only. No aircraft physics/sensors/UI/AI payload; no game integration or release claim. No new Three/GLTF/Draco/Meshopt dependency.'}
(ROOT / 'size-report.json').write_text(json.dumps(out, indent=2) + '\n'); print(json.dumps(out))
