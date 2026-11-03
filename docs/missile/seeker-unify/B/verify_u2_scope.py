#!/usr/bin/env python3
"""Verify that final U2 is one removable SHADOW block over U1 ACTIVE."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def builder_module():
    path = HERE / "build_product.py"
    spec = importlib.util.spec_from_file_location("seeker_unify_b_builder", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--u1", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    builder = builder_module()
    u1, _ = builder.unpack(args.u1.read_bytes())
    final, _ = builder.unpack(args.final.read_bytes())
    marker = "// SEEKER_UNIFY_B U2: WIP22 ASM + SAM ARH common echo/cell SHADOW."
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    marker_count = final.count(marker)
    start = final.find(marker)
    end = final.find(anchor, start)
    block = final[start:end] if start >= 0 and end >= 0 else ""
    stripped = final[:start] + final[end:] if block else final
    control_flow = re.findall(
        r"(?:if|while|switch)\s*\([^)]*SEEKER_COMMON_U2_MODE|"
        r"SEEKER_COMMON_U2_MODE\s*(?:===|!==|==|!=|\?)",
        block,
    )
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U2_STATIC_SCOPE_1",
        "status": "PASS" if marker_count == 1 and stripped == u1 and not control_flow else "FAIL",
        "u1HtmlSha256": sha(args.u1.read_bytes()),
        "finalHtmlSha256": sha(args.final.read_bytes()),
        "u1MainSha256": sha(u1.encode()),
        "finalMainSha256": sha(final.encode()),
        "u2BlockSha256": sha(block.encode()),
        "u2BlockBytes": len(block.encode()),
        "markerCount": marker_count,
        "sourceWithoutU2EqualsU1": stripped == u1,
        "controlFlowReferences": control_flow,
        "activeLiteralPresent": "SEEKER_COMMON_U2_MODE='ACTIVE'" in block,
        "shadowLiteralCount": block.count("SEEKER_COMMON_U2_MODE='SHADOW'"),
        "tacticalOutputUsedFalse": "tacticalOutputUsed:false" in block,
        "rngConsumedFalse": "rngConsumed:false" in block,
        "truthOutputFalse": "truthOutput:false" in block,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
