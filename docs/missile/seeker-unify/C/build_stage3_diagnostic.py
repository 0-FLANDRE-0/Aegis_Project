#!/usr/bin/env python3
"""Inject A/B observers plus CUE_A test-only diagnostics into Stage 3."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def pack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    compressed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(compressed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    metadata = re.search(rb'const records=(\[.*?\]);', output, re.S)
    assert metadata
    rows = json.loads(metadata[1])
    rows[13].update(rawBytes=len(source.encode()), gzipBytes=len(compressed), sha256=sha(source.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    return output[:metadata.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + output[metadata.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("/dev/shm/seeker_c_stage3_diag.html"))
    parser.add_argument("--receipt", type=Path, default=HERE / "CUE_A_DIAGNOSTIC_BUILD.json")
    args = parser.parse_args()
    raw = args.base.read_bytes()
    source, match = unpack(raw)
    paths = [
        ROOT / "docs/missile/seeker-unify/A/diagnostic.js",
        ROOT / "docs/missile/seeker-unify/B/diagnostic_extension.js",
        HERE / "cue_a_diagnostic.js",
    ]
    module_sources = [path.read_text() for path in paths]
    fixture_old = "const em=enemyMissiles.at(-1);em.insTgtX=cueX;em.insTgtY=cueY;em.seekerOn=true;"
    fixture_new = "const em=enemyMissiles.at(-1);em.insTgtX=cueX;em.insTgtY=cueY;if(em._cueLaunchA){em._cueLaunchA.positionM={x:worldToMeters(cueX),y:worldToMeters(cueY)};em._cueLaunchA.timeS=0;delete em._targetCueA;}em.seekerOn=true;"
    assert module_sources[0].count(fixture_old) == 1
    module_sources[0] = module_sources[0].replace(fixture_old, fixture_new, 1)
    modules = "\n".join(module_sources)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    assert source.count(anchor) == 1
    candidate = source.replace(anchor, modules + "\n" + anchor, 1)
    assert candidate.replace(modules + "\n", "", 1) == source
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    args.out.write_bytes(output)
    receipt = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_A_DIAGNOSTIC_BUILD_1",
        "base": str(args.base), "baseSha256": sha(raw), "baseMainSha256": sha(source.encode()),
        "output": str(args.out), "outputSha256": sha(output), "outputMainSha256": sha(candidate.encode()),
        "modules": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())} for path in paths],
        "modulesSha256": sha(modules.encode()), "inverseByteExact": True, "testOnlyInstrumentation": True,
        "fixtureCompatibilityPatch": "controlled setupMissile insTgtX/Y is mirrored into _cueLaunchA; product source unchanged",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
