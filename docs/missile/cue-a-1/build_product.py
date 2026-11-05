#!/usr/bin/env python3
"""Build CUE_A-1 incrementally from the pinned SEEKER_UNIFY_C product."""
from __future__ import annotations

import argparse
import base64
import difflib
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"
BASE_SHA = "efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script not found")
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def transform_stage1a(source: str) -> str:
    """Restore the legacy ASM floor while preserving the SAM floor."""
    source = one(
        source,
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08}),",
        "ASM_WIP22:Object.freeze({provenance:'SIM_TUNED',definition:'ONE_WAY_PATTERN_AND_LOS_WITH_ROUND_TRIP_WEATHER_PATH',beamConvention:'TX_RX_SEPARATE',extentPolicy:'POWER_WEIGHTED_RMS',angularPolicy:'AXIS_SEPARATE_COMPOSITE',oneWaySidelobeFloor:.08,rangeFloorKm:.5,rangeFloorProvenance:'LEGACY_EQUIVALENCE'}),",
        "ASM U2 range floor profile",
    )
    source = one(
        source,
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING'})",
        "SAM_ARH:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'TX_RX_SEPARATE',extentPolicy:'MAX_MEMBER',angularPolicy:'SPHERICAL_MEMBER_PRESERVING',rangeFloorKm:.20,rangeFloorProvenance:'LEGACY_EQUIVALENCE'})",
        "SAM U2 range floor profile",
    )
    source = one(
        source,
        "*Math.pow(q.referenceRangeKm/Math.max(.20,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        "*Math.pow(q.referenceRangeKm/Math.max(option.rangeFloorKm,q.rangeKm),4)\n      *Math.max(0,q.txGain)",
        "profile-specific TX/RX range floor",
    )
    return source


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    if not meta:
        raise AssertionError("packed record metadata not found")
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + out[meta.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--through", choices=("stage1a",), default="stage1a")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path, default=HERE / "BUILD_STAGE1A.json")
    args = parser.parse_args()

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError(f"baseline SHA mismatch: {sha(raw)}")
    before, match = unpack(raw)
    after = transform_stage1a(before)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    if check != after:
        raise AssertionError("repacked main script mismatch")
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="SEEKER_UNIFY_C/main.js", tofile="CUE_A_1_STAGE1A/main.js"))
    (HERE / "changes-stage1a.diff").write_text(diff)
    build = {
        "schema": "AEGIS_CUE_A_1_BUILD_STAGE1A_1",
        "baselineCommit": "4faeb4e079b7baddcb1e1b8c1b892af804565938",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "through": args.through,
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "rangeFloors": {
            "ASM_WIP22": {"km": 0.5, "provenance": "LEGACY_EQUIVALENCE"},
            "SAM_ARH": {"km": 0.20, "provenance": "LEGACY_EQUIVALENCE"},
        },
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
    }
    args.receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
