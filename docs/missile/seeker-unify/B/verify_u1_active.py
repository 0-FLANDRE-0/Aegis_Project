#!/usr/bin/env python3
"""Prove that U1 SHADOW and ACTIVE differ only by the inert mode label."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER = HERE / "build_product.py"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("seeker_unify_b_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shadow", type=Path, required=True)
    parser.add_argument("--active", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    builder = load_builder()
    shadow, _ = builder.unpack(args.shadow.read_bytes())
    active, _ = builder.unpack(args.active.read_bytes())
    shadow_marker = "const SEEKER_COMMON_U1_MODE='SHADOW';"
    active_marker = "const SEEKER_COMMON_U1_MODE='ACTIVE';"
    marker_counts = {
        "shadow": shadow.count(shadow_marker),
        "active": active.count(active_marker),
    }
    normalized = shadow.replace(shadow_marker, active_marker, 1)
    remaining = active.replace(active_marker, "", 1)
    control_flow_references = re.findall(
        r"(?:if|while|switch)\s*\([^)]*SEEKER_COMMON_U1_MODE|"
        r"SEEKER_COMMON_U1_MODE\s*(?:===|!==|==|!=|\?)",
        remaining,
    )
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U1_ACTIVE_GATE_1",
        "status": "PASS" if marker_counts == {"shadow": 1, "active": 1} and normalized == active else "FAIL",
        "shadowHtmlSha256": sha(args.shadow.read_bytes()),
        "activeHtmlSha256": sha(args.active.read_bytes()),
        "shadowMainSha256": sha(shadow.encode()),
        "activeMainSha256": sha(active.encode()),
        "markerCounts": marker_counts,
        "normalizedSourceEqual": normalized == active,
        "nonControlApiReferenceCount": remaining.count("SEEKER_COMMON_U1_MODE"),
        "controlFlowReferences": control_flow_references,
        "calculationBranchOnMode": bool(control_flow_references),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" and not result["calculationBranchOnMode"] else 1)


if __name__ == "__main__":
    main()
