#!/usr/bin/env python3
"""Inject frozen A/B/C diagnostics plus CUE_A-1 Stage-2 probes."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script not found")
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def pack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    compressed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(compressed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    metadata = re.search(rb'const records=(\[.*?\]);', output, re.S)
    if not metadata:
        raise AssertionError("packed record metadata not found")
    rows = json.loads(metadata[1])
    rows[13].update(rawBytes=len(source.encode()), gzipBytes=len(compressed), sha256=sha(source.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    return output[:metadata.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + output[metadata.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    raw = args.base.read_bytes()
    source, match = unpack(raw)
    paths = [
        ROOT / "docs/missile/seeker-unify/A/diagnostic.js",
        ROOT / "docs/missile/seeker-unify/B/diagnostic_extension.js",
        ROOT / "docs/missile/seeker-unify/C/cue_a_diagnostic.js",
        HERE / "cue_a_1_diagnostic.js",
        HERE / "cue_a_1_stage2_diagnostic.js",
    ]
    modules = [path.read_text() for path in paths]
    fixture_old = "const em=enemyMissiles.at(-1);em.insTgtX=cueX;em.insTgtY=cueY;em.seekerOn=true;"
    fixture_new = "const em=enemyMissiles.at(-1);em.insTgtX=cueX;em.insTgtY=cueY;if(em._cueLaunchA){em._cueLaunchA.positionM={x:worldToMeters(cueX),y:worldToMeters(cueY)};em._cueLaunchA.timeS=0;delete em._targetCueA;}em.seekerOn=true;"
    if modules[0].count(fixture_old) != 1:
        raise AssertionError("upstream fixture anchor changed")
    modules[0] = modules[0].replace(fixture_old, fixture_new, 1)
    joined = "\n".join(modules)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if source.count(anchor) != 1:
        raise AssertionError("diagnostic insertion anchor changed")
    candidate = source.replace(anchor, joined + "\n" + anchor, 1)
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    if check != candidate:
        raise AssertionError("diagnostic repack mismatch")
    args.out.write_bytes(output)
    receipt = {
        "schema": "AEGIS_CUE_A_1_STAGE2_DIAGNOSTIC_BUILD_1",
        "base": str(args.base), "baseSha256": sha(raw), "baseMainSha256": sha(source.encode()),
        "output": str(args.out), "outputSha256": sha(output), "outputMainSha256": sha(candidate.encode()),
        "modules": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())} for path in paths],
        "inverseByteExact": candidate.replace(joined + "\n", "", 1) == source,
        "testOnlyInstrumentation": True,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
