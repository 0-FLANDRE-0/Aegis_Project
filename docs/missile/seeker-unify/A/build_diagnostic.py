#!/usr/bin/env python3
"""Inject SEEKER_UNIFY_A test-only probes into either pinned HTML."""
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


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def pack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    assert meta
    rows = json.loads(meta[1])
    rows[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + out[meta.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    raw = args.base.read_bytes()
    source, match = unpack(raw)
    module = (HERE / "diagnostic.js").read_text()
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    assert source.count(anchor) == 1
    candidate = source.replace(anchor, module + "\n" + anchor, 1)
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    args.out.write_bytes(output)
    receipt = {
        "schema": "AEGIS_SEEKER_UNIFY_A_DIAGNOSTIC_BUILD_1",
        "base": str(args.base),
        "baseSha256": sha(raw),
        "baseMainSha256": sha(source.encode()),
        "output": str(args.out),
        "outputSha256": sha(output),
        "outputMainSha256": sha(candidate.encode()),
        "moduleSha256": sha(module.encode()),
        "inverseByteExact": candidate.replace(module + "\n", "", 1) == source,
        "testOnlyInstrumentation": True,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
