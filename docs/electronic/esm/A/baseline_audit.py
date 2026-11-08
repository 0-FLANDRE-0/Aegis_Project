#!/usr/bin/env python3
"""Commit-A deterministic audit for the merged EMCON_B product."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_EMCON_B.html"
PRODUCT_SHA = "50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee"
PRODUCT_BYTES = 22_162_415
MAIN_SHA = "2cc2dc1a130f54d7970df9f4be8c8ae4d565d9b65af001ef718cf1fd90fa4d64"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_span(source: str, name: str) -> str:
    matches = list(re.finditer(rf"function\s+{re.escape(name)}\s*\(", source))
    if len(matches) != 1:
        raise AssertionError(f"{name}: expected one function, got {len(matches)}")
    match = matches[0]
    brace = source.find("{", match.end())
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start() : index + 1]
    raise AssertionError(f"{name}: unterminated function")


def between(source: str, start: str, end: str) -> str:
    a = source.index(start)
    b = source.index(end, a)
    return source[a:b]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "A_BASELINE_AUDIT.json")
    args = parser.parse_args()

    raw = PRODUCT.read_bytes()
    packed = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not packed:
        raise AssertionError("packed main script missing")
    source = gzip.decompress(base64.b64decode(packed.group(1))).decode()
    functions = [
        "prepareElectronicF",
        "electronicPhysicalEmittersF",
        "electronicReceiverPlotsF",
        "electronicAcceptPlotsF",
        "stepElectronicReceiversF",
        "electronicCicTextF",
        "networkBuildReportsG",
        "networkReceiveG",
        "networkFixedStepG",
        "mapEsmReadA",
    ]
    frozen_hashes = {name: sha(function_span(source, name).encode()) for name in functions}
    frozen_hashes["ELECTRONIC_POLICY_F"] = sha(
        between(source, "const ELECTRONIC_POLICY_F=", "function electronicShipsF").encode()
    )
    frozen_hashes["NETWORK_POLICY_G"] = sha(
        between(source, "const NETWORK_POLICY_G=", "function networkNowG").encode()
    )

    with tempfile.TemporaryDirectory(prefix="esm-a-audit-") as temp:
        rebuilt = Path(temp) / "rebuilt.html"
        receipt = Path(temp) / "receipt.json"
        subprocess.run(
            [
                "python3",
                str(ROOT / "docs/electronic/emcon/B/build_product.py"),
                "--stage",
                "E",
                "--out",
                str(rebuilt),
                "--receipt",
                str(receipt),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        exact_rebuild = rebuilt.read_bytes() == raw
        rebuild_receipt = json.loads(receipt.read_text())

    receiver = function_span(source, "electronicReceiverPlotsF")
    accept = function_span(source, "electronicAcceptPlotsF")
    anonymous_output = (
        "plots.push({bearing,bearingSigmaDeg:sigma,strength:quality,quality,band:source.band,type:source.family,emitterClass:source.emitterClass,measuredAtS:" in receiver
        and "actual" not in receiver.lower()
        and "truthRef" not in receiver
    )
    strict_consumer = (
        "const allowed=['bearing','bearingSigmaDeg','strength','quality','band','type','emitterClass','measuredAtS'];" in accept
        and "rangeKm:null,identity:'UNKNOWN'" in accept
        and "delete e.contacts.get(found).truthRef" in accept
    )
    correction_static = json.loads((ROOT / "docs/electronic/emcon/B/CORRECTION_3_STATIC.json").read_text())
    correction_runtime = json.loads((ROOT / "docs/electronic/emcon/B/CORRECTION_3_GATE.json").read_text())
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    checks = {
        "mainHeadExact": head == "babb4d7f6d42cc8d774feadce17d8108b3a24040",
        "productBytesExact": len(raw) == PRODUCT_BYTES,
        "productShaExact": sha(raw) == PRODUCT_SHA,
        "packedMainShaExact": sha(source.encode()) == MAIN_SHA,
        "exactRebuild": exact_rebuild,
        "rebuildReceiptExact": rebuild_receipt.get("outputSha256") == PRODUCT_SHA,
        "anonymousReceiverBoundary": anonymous_output,
        "strictExistingConsumerBoundary": strict_consumer,
        "emconBindingStaticPass": correction_static.get("status") == "PASS",
        "emconBindingRuntimePass": correction_runtime.get("status") == "PASS",
    }
    result = {
        "schema": "AEGIS_ESM_A_BASELINE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baseline": {
            "gitHead": head,
            "product": str(PRODUCT.relative_to(ROOT)),
            "bytes": len(raw),
            "sha256": sha(raw),
            "packedMainSha256": sha(source.encode()),
        },
        "checks": checks,
        "frozenFunctionHashes": frozen_hashes,
        "ownership": {
            "physicalRfScene": "electronicPhysicalEmittersF",
            "sensorSynthesis": "electronicReceiverPlotsF",
            "localContactAssociation": "electronicAcceptPlotsF / ShipRuntime.ew.executionF.contacts",
            "network": "prepareNetworkG / networkFixedStepG / ShipRuntime.combatSystem.networkG",
            "ui": "drawRadar + MAP_A mapEsmReadA",
            "resetDestroy": "resetElectronicFleetF / retireElectronicF / resetNetworkFleetG / retireNetworkG",
        },
        "wideRegressionRun": False,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
