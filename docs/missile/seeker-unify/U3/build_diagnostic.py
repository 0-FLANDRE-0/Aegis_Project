#!/usr/bin/env python3
"""Inject frozen predecessor probes plus U3 probes into a product copy."""
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
MODULES = [
    ROOT / "docs/missile/seeker-unify/A/diagnostic.js",
    ROOT / "docs/missile/asm-seeker/A/diagnostic.js",
    ROOT / "docs/missile/seeker-unify/B/diagnostic_extension.js",
    HERE / "diagnostic_extension.js",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()
    raw = args.base.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main missing")
    source = gzip.decompress(base64.b64decode(match[1])).decode()
    modules = "\n".join(path.read_text() for path in MODULES)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if source.count(anchor) != 1:
        raise AssertionError("diagnostic anchor")
    candidate = source.replace(anchor, modules + "\n" + anchor, 1)
    packed = gzip.compress(candidate.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', output, re.S)
    rows = json.loads(meta[1]);rows[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(packed),sha256=sha(candidate.encode()))
    if "encodedBytes" in rows[13]:rows[13]["encodedBytes"] = len(encoded)
    output = output[:meta.start(1)] + json.dumps(rows,separators=(",", ":")).encode() + output[meta.end(1):]
    args.out.write_bytes(output)
    result={"schema":"AEGIS_SEEKER_UNIFY_U3_DIAGNOSTIC_BUILD_1","baseSha256":sha(raw),"baseMainSha256":sha(source.encode()),"outputSha256":sha(output),"modulesSha256":sha(modules.encode()),"inverseByteExact":candidate.replace(modules+"\n","",1)==source,"testOnlyInstrumentation":True}
    args.receipt.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))


if __name__ == "__main__":
    main()
