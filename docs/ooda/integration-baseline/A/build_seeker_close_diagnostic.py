#!/usr/bin/env python3
"""Build SEEKER_CLOSE_A instrumentation on the frozen integration candidate.

This is diagnostic-only. Protected game functions are hashed before and after
the insertion and must remain byte-identical.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SEEKER_CLOSE = ROOT / "docs/missile/seeker-close/A"
sys.path.insert(0, str(SEEKER_CLOSE))
from baseline_audit import function_spans, unpack_main  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def repack(raw: bytes, source: str) -> bytes:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    metadata = re.search(rb"const records=(\[.*?\]);", output, re.S)
    if not metadata:
        raise AssertionError("packed record metadata missing")
    records = json.loads(metadata.group(1))
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha256(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return output[:metadata.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[metadata.end(1):]


def hashes(source: str, names: list[str]) -> dict[str, list[str]]:
    return {name: [sha256(source[a:b].encode()) for a, b in function_spans(source, name)] for name in names}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    raw = args.product.read_bytes()
    before = unpack_main(raw)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if before.count(anchor) != 1:
        raise AssertionError(f"diagnostic anchor count {before.count(anchor)}")
    instrumentation = (ROOT / "docs/missile/asm-seeker/A/diagnostic.js").read_text().rstrip()
    classifier = (SEEKER_CLOSE / "seeker_close_diag.js").read_text().rstrip()
    after = before.replace(anchor, instrumentation + "\n\n" + classifier + "\n\n" + anchor, 1)
    protected = [
        "seekerU4SelectIndexC", "seekerU4RunPolicyC", "updateAsmSeeker",
        "asmSeekerMeasurement", "asmSeekerAssociateMeasurements",
        "asmSeekerVisibleRfReturns", "updateEnemyMissileBaseC52",
        "nulkaRfReturns15B", "deployOwnChaffForThreat", "harpoonSeekerA",
        "shipOutcomeA", "damageFloodImpactV1", "exportOperationalState",
    ]
    before_hash, after_hash = hashes(before, protected), hashes(after, protected)
    if any(not before_hash[name] for name in protected):
        raise AssertionError("protected function declaration missing")
    unchanged = {name: before_hash[name] == after_hash[name] for name in protected}
    if not all(unchanged.values()):
        raise AssertionError("diagnostic insertion changed protected function body")
    output = repack(raw, after)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    receipt = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_SEEKER_CLOSE_DIAGNOSTIC_BUILD_1",
        "authorityProduct": args.product.name,
        "authorityProductBytes": len(raw),
        "authorityProductSha256": sha256(raw),
        "diagnosticOnly": True,
        "formalProduct": False,
        "output": args.output.name,
        "outputBytes": len(output),
        "outputSha256": sha256(output),
        "baseMainSha256": sha256(before.encode()),
        "diagnosticMainSha256": sha256(after.encode()),
        "instrumentationSha256": sha256(instrumentation.encode()),
        "classifierSha256": sha256(classifier.encode()),
        "protectedFunctionHashesExact": all(unchanged.values()),
        "protectedFunctionHashesBefore": before_hash,
        "protectedFunctionHashesAfter": after_hash,
        "broadRegressionRun": False,
        "release": False,
    }
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"outputBytes": len(output), "outputSha256": receipt["outputSha256"], "protectedExact": True}))


if __name__ == "__main__":
    main()

