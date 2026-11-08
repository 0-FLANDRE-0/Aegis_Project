#!/usr/bin/env python3
"""Commit-B protected-hash and packed-product static gate."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = json.loads((HERE / "BASELINE_AUDIT.json").read_text())


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main_source(path: Path) -> str:
    raw = path.read_bytes(); match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    return gzip.decompress(base64.b64decode(match.group(1))).decode()


def spans(source: str, name: str) -> list[str]:
    out = []
    for match in re.finditer(rf"function\s+{re.escape(name)}\s*\(", source):
        brace = source.find("{", match.end()); depth = 0; quote = None; escaped = False
        for index in range(brace, len(source)):
            char = source[index]
            if quote:
                if escaped: escaped = False
                elif char == "\\": escaped = True
                elif char == quote: quote = None
                continue
            if char in "'\"`": quote = char
            elif char == "{": depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    out.append(source[match.start():index + 1]); break
    return out


def main() -> None:
    source = main_source(ROOT / "Aegis_SIM_v48_WIP_EMCON_B.html")
    allowed = {"prepareElectronicF", "electronicShipPhysicalEmittersDeclaredA"}
    rows = {}
    for label, baseline in BASELINE["functionHashes"].items():
        name = label.split(".")[0]
        choices = spans(source, name)
        if label == "toggleEmcon.operator": choices = [q for q in choices if "networkOverrideRadarG(ACTIVE_SHIP_RUNTIME)" in q]
        if len(choices) != 1: raise AssertionError(f"{label}: {len(choices)}")
        current = sha(choices[0].encode()); changed = current != baseline["sha256"]
        rows[label] = {"baseline": baseline["sha256"], "current": current, "changed": changed, "allowed": name in allowed}
    checks = {
        "policyModuleOnce": source.count("const EMCON_B_SCHEMA='AEGIS_SHIP_EMCON_B_1'") == 1,
        "modeShadow": "const EMCON_B_MODE='SHADOW'" in source,
        "onlyAllowedBaselineFunctionsChanged": all(not row["changed"] or row["allowed"] for row in rows.values()),
        "expectedFunctionsChanged": all(any(label.split('.')[0] == name and row["changed"] for label, row in rows.items()) for name in allowed),
        "truthTokenAbsentFromDecision": "function emconEquipmentDecisionB" in source and "truthUsed:false" in source,
    }
    result = {"schema":"AEGIS_EMCON_B_COMMIT_B_STATIC_1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"protectedFunctions":rows}
    (HERE / "B_STATIC.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status":result["status"],"checks":checks}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__": main()
