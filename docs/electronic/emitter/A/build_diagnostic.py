#!/usr/bin/env python3
"""Build a disposable Commit-A diagnostic copy from the pinned U3 product."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
OUT = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_BASELINE_DIAGNOSTIC.html")
BASE_SHA = "243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError("pinned U3 product SHA mismatch")
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    source = gzip.decompress(base64.b64decode(match[1])).decode()
    module = (HERE / "baseline_diagnostic.js").read_text()
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if source.count(anchor) != 1:
        raise AssertionError("diagnostic anchor mismatch")
    candidate = source.replace(anchor, module + "\n" + anchor, 1)
    packed = gzip.compress(candidate.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', output, re.S)
    rows = json.loads(meta[1])
    rows[13].update(rawBytes=len(candidate.encode()), gzipBytes=len(packed), sha256=sha(candidate.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    output = output[:meta.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + output[meta.end(1):]
    OUT.write_bytes(output)
    receipt = {
        "schema": "AEGIS_EMITTER_A_BASELINE_DIAGNOSTIC_BUILD_1",
        "baseSha256": sha(raw),
        "outputSha256": sha(output),
        "moduleSha256": sha(module.encode()),
        "inverseByteExact": candidate.replace(module + "\n", "", 1) == source,
        "testOnlyInstrumentation": True,
        "output": str(OUT),
    }
    (HERE / "BASELINE_DIAGNOSTIC_BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()

