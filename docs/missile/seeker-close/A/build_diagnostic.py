#!/usr/bin/env python3
"""Build the non-product SEEKER_CLOSE_A diagnostic HTML."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

from baseline_audit import HP_A_BYTES, HP_A_SHA256, function_spans, sha256, unpack_main


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


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
    return {
        name: [sha256(source[start:end].encode()) for start, end in function_spans(source, name)]
        for name in names
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path, default=HERE / "DIAGNOSTIC_BUILD.json")
    args = parser.parse_args()
    raw = args.product.read_bytes()
    if len(raw) != HP_A_BYTES or sha256(raw) != HP_A_SHA256:
        raise AssertionError("pinned HP_A product mismatch")
    before = unpack_main(raw)
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    if before.count(anchor) != 1:
        raise AssertionError(f"diagnostic anchor count {before.count(anchor)}")
    instrumentation = (ROOT / "docs/missile/asm-seeker/A/diagnostic.js").read_text().rstrip()
    classifier = (HERE / "seeker_close_diag.js").read_text().rstrip()
    after = before.replace(anchor, instrumentation + "\n\n" + classifier + "\n\n" + anchor, 1)
    protected = [
        "seekerU4SelectIndexC", "seekerU4RunPolicyC", "updateAsmSeeker",
        "asmSeekerMeasurement", "asmSeekerAssociateMeasurements",
        "asmSeekerVisibleRfReturns", "updateEnemyMissileBaseC52",
        "nulkaRfReturns15B", "deployOwnChaffForThreat", "harpoonSeekerA",
        "shipOutcomeA", "damageFloodImpactV1", "exportOperationalState",
    ]
    before_hash = hashes(before, protected)
    after_hash = hashes(after, protected)
    if any(not before_hash[name] for name in protected):
        raise AssertionError("protected function declaration missing")
    unchanged = {name: before_hash[name] == after_hash[name] for name in protected}
    if not all(unchanged.values()):
        raise AssertionError("diagnostic injection changed protected function body")
    output = repack(raw, after)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    receipt = {
        "schema": "AEGIS_SEEKER_CLOSE_A_DIAGNOSTIC_BUILD_1",
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
        "protectedFunctionHashesBefore": before_hash,
        "protectedFunctionHashesAfter": after_hash,
        "protectedFunctionHashesExact": all(unchanged.values()),
        "broadRegressionRun": False,
        "release": False,
    }
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
