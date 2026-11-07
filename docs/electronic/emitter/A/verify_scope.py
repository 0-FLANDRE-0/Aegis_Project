#!/usr/bin/env python3
"""Prove EMITTER_A only changes the declared profile/emitter integration surface."""
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
sys.path.insert(0, str(HERE))
from build_product import function_span, transform  # noqa: E402


def unpack(path: Path) -> str:
    body = path.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', body)
    if not match:
        raise AssertionError(f"packed main script missing: {path}")
    return gzip.decompress(base64.b64decode(match[1])).decode()


def function_digest(source: str, name: str) -> str:
    start, end = function_span(source, name)
    return hashlib.sha256(source[start:end].encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--stage", choices=("B", "C", "D"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    before_source = unpack(ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html")
    after_source = unpack(args.product)
    mode = "SHADOW" if args.stage == "B" else "ACTIVE"
    generated = transform(before_source, stage=args.stage, mode=mode)
    deterministic_transform_exact = generated == after_source
    protected = (
        "electronicReceiverPlotsF", "electronicJammerSampleF", "electronicHojF",
        "observerC", "observerHealthC", "electronicAllocatorF", "electronicSettingsF",
        "exportOperationalState", "importOperationalState",
        "arhRfTargetEvidenceWip13B12", "arhRfCandidateAcceptedWip13B12",
    )
    protected_rows = {}
    for name in protected:
        try:
            before_hash = function_digest(before_source, name)
            after_hash = function_digest(after_source, name)
            protected_rows[name] = {"present": True, "before": before_hash,
                                    "after": after_hash, "identical": before_hash == after_hash}
        except AssertionError:
            protected_rows[name] = {"present": False, "before": None, "after": None, "identical": False}
    touched = ["electronicPhysicalEmittersF", "makeBunkerShipProfile"]
    if args.stage == "D":
        touched.append("makeSovProfileA")
    touched_rows = {name: {"before": function_digest(before_source, name),
                           "after": function_digest(after_source, name)} for name in touched}
    new_names = (
        "shipEmitterEquipmentRegistryA", "shipEmitterSovRegistryA",
        "electronicShipPhysicalEmittersLegacyA", "electronicShipPhysicalEmittersDeclaredA",
        "shipEmitterRegistryValidateA", "shipEmitterShadowCompareA",
        "shipEmitterRuntimeSnapshotA", "shipEmitterAuditSnapshotA",
    )
    new_rows = {name: {"absentInBase": f"function {name}(" not in before_source,
                       "presentInProduct": f"function {name}(" in after_source} for name in new_names}
    all_protected = all(q["identical"] for q in protected_rows.values())
    all_new = all(q["absentInBase"] and q["presentInProduct"] for q in new_rows.values())
    result = {
        "schema": "AEGIS_EMITTER_A_SCOPE_HASH_1",
        "stage": args.stage,
        "status": "PASS" if deterministic_transform_exact and all_protected and all_new else "FAIL",
        "scopeProof": {
            "pinnedBaseSha256": hashlib.sha256((ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html").read_bytes()).hexdigest(),
            "deterministicTransformExact": deterministic_transform_exact,
            "method": "product main source equals the pinned base after the fail-closed exact-anchor transform",
        },
        "expectedTouchedFunctions": touched_rows,
        "newFunctions": new_rows,
        "protected": protected_rows,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "transformExact": deterministic_transform_exact,
                      "protectedExact": all_protected, "newFunctionsPresent": all_new}, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
