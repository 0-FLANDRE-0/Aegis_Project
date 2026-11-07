#!/usr/bin/env python3
"""Inject predecessor probes plus EMITTER_A probes into a disposable product."""
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
    ROOT / "docs/missile/cue-a-1/cue_a_1_stage2_diagnostic.js",
    ROOT / "docs/missile/seeker-unify/U3/diagnostic_extension.js",
    HERE / "baseline_diagnostic.js",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--extra", action="append", type=Path, default=[])
    args = parser.parse_args()
    raw = args.base.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    source = gzip.decompress(base64.b64decode(match[1])).decode()
    module_paths = [*MODULES, *args.extra]
    modules = "\n".join(path.read_text() for path in module_paths)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if source.count(anchor) != 1:
        raise AssertionError("diagnostic anchor mismatch")
    candidate = source.replace(anchor, modules + "\n" + anchor, 1)
    packed = gzip.compress(candidate.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', output, re.S)
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(candidate.encode()), gzipBytes=len(packed), sha256=sha(candidate.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    output = output[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1):]
    args.out.write_bytes(output)
    receipt = {"schema":"AEGIS_EMITTER_A_STAGE_DIAGNOSTIC_BUILD_1","baseSha256":sha(raw),"outputSha256":sha(output),
        "modulesSha256":sha(modules.encode()),"modulePaths":[str(q) for q in module_paths],
        "inverseByteExact":candidate.replace(modules+"\n","",1)==source,"testOnlyInstrumentation":True}
    args.receipt.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
