#!/usr/bin/env python3
"""Fail-closed static gate for the frozen SEEKER_UNIFY_U4 candidate.

This gate deliberately does not execute the project-wide regression.  It
validates the pinned product, build receipt, completed A/B/C limited gates and
the retained final-regression review, then exports the packed main script for
``node --check`` in Actions.
"""
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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def strict_json(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant in {path}: {value}")
        ),
    )


def unpack_main(product: Path) -> str:
    raw = product.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match[1])).decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--main-out", type=Path, required=True)
    args = parser.parse_args()

    product = args.product.resolve()
    manifest = strict_json(ROOT / "AEGIS_CURRENT_PRODUCT.json")
    build = strict_json(HERE / "BUILD_FINAL.json")
    gates = {name: strict_json(HERE / f"{name}_GATE.json") for name in ("A", "B", "C")}
    broad = strict_json(HERE / "FINAL_REGRESSION.json")
    review = strict_json(HERE / "FINAL_REGRESSION_REVIEW.json")
    main_source = unpack_main(product)

    product_sha = digest(product)
    main_sha = hashlib.sha256(main_source.encode("utf-8")).hexdigest()
    expected_sha = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"
    expected_main_sha = "e06c2e6133b66fe8be2f6c1305b39473a7776176680390a45673e7487e9a462e"
    markers = (
        "SARH_BISTATIC_4D",
        "PASSIVE_RF_2D",
        "PASSIVE_IR_2D",
        "SEEKER_U4_COMMON_MODE_C",
        "window.__SEEKER_U4_C__",
    )
    checks = {
        "manifestStage": manifest.get("stage") == "SEEKER_UNIFY_U4",
        "manifestProduct": manifest.get("path") == product.name,
        "manifestProductExact": manifest.get("sha256") == product_sha and manifest.get("bytes") == product.stat().st_size,
        "productPinned": product_sha == expected_sha and product.stat().st_size == 22_195_923,
        "packedMainPinned": main_sha == expected_main_sha,
        "buildReceiptExact": build.get("outputSha256") == product_sha and build.get("outputMainSha256") == main_sha and build.get("outputBytes") == product.stat().st_size,
        "buildMode": build.get("through") == "C" and build.get("mode") == "ACTIVE" and build.get("broadRegressionRun") is False,
        "stageGates": all(gate.get("status") == "PASS" and gate.get("broadRegressionRun") is False for gate in gates.values()),
        "rawBroadCandidateExact": broad.get("complete") is True and broad.get("candidateSha256") == product_sha and broad.get("broadRun", {}).get("candidateFrozen") is True,
        "oneBroadRunRecorded": review.get("mode") == "MAX_THREAT" and review.get("broadRunsExecuted") == 1,
        "reviewAccepted": review.get("status") == "PASS_WITH_RETAINED_RAW_HARNESS_ASSERTION_DEFECTS" and review.get("unexplainedFailures") == [],
        "reviewNoProductMutation": review.get("productCodeChangedAfterBroad") is False and review.get("broadRegressionRerun") is False,
        "noExpectationOrToleranceChange": review.get("expectedValuesUpdated") is False and review.get("tolerancesChanged") is False,
        "activeMarkers": all(marker in main_source for marker in markers),
        "commonNoRngOrSaveSchema": review.get("correctedSceneChecks", {}).get("commonLayerNoRngOrSaveSchema") is True,
        "anonymousContract": review.get("correctedSceneChecks", {}).get("anonymousContractPass") is True,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_CANDIDATE_STATIC_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "product": product.relative_to(ROOT).as_posix(),
        "productBytes": product.stat().st_size,
        "productSha256": product_sha,
        "packedMainSha256": main_sha,
        "checks": checks,
        "broadRegressionRun": False,
        "release": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.main_out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    args.main_out.write_text(main_source, encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
