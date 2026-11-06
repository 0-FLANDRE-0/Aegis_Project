#!/usr/bin/env python3
"""Inject the unchanged ASM_SEEKER_A after-action observer into Stage 2."""
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
    parser.add_argument("--base", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html")
    parser.add_argument("--out", type=Path, default=Path("/dev/shm/seeker_c_stage2_asm_diag.html"))
    parser.add_argument("--receipt", type=Path, default=HERE / "BEAM_STAGE2_ASM_DIAGNOSTIC_BUILD.json")
    parser.add_argument("--build-receipt", type=Path, default=HERE / "BUILD.json")
    args = parser.parse_args()
    build = json.loads(args.build_receipt.read_text())
    raw = args.base.read_bytes()
    assert sha(raw) == build["productHtmlSha256"]
    source, match = unpack(raw)
    assert sha(source.encode()) == build["productMainSha256"]
    observer = (ROOT / "docs/missile/asm-seeker/A/diagnostic.js").read_text()
    fixture_old = "const em=enemyMissiles.at(-1);D.missileIds.add(em.id);em.insTgtX=targetX;em.insTgtY=targetY;em.seekerOn=true;"
    fixture_new = "const em=enemyMissiles.at(-1);D.missileIds.add(em.id);em.insTgtX=targetX;em.insTgtY=targetY;if(em._cueLaunchA){em._cueLaunchA.positionM={x:worldToMeters(targetX),y:worldToMeters(targetY)};em._cueLaunchA.timeS=0;delete em._targetCueA;}em.seekerOn=true;"
    assert observer.count(fixture_old) == 1
    observer = observer.replace(fixture_old, fixture_new, 1)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    assert source.count(anchor) == 1
    candidate = source.replace(anchor, observer + "\n" + anchor, 1)
    assert candidate.replace(observer + "\n", "", 1) == source
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    args.out.write_bytes(output)
    receipt = {
        "schema": f"AEGIS_SEEKER_UNIFY_C_STAGE{build.get('completedStage', 2)}_ASM_DIAGNOSTIC_BUILD_1",
        "base": args.base.name,
        "baseSha256": sha(raw),
        "baseMainSha256": sha(source.encode()),
        "output": str(args.out),
        "outputSha256": sha(output),
        "outputMainSha256": sha(candidate.encode()),
        "observerSha256": sha(observer.encode()),
        "fixtureCompatibilityPatch": "controlled targetX/Y is mirrored into _cueLaunchA; product source unchanged",
        "inverseByteExact": True,
        "testOnlyInstrumentation": True,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
