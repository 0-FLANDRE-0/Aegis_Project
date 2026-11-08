#!/usr/bin/env python3
"""Freeze the U4 HP authority audit without changing product behavior."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html"
PRODUCT_BYTES = 22_195_923
PRODUCT_SHA256 = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"
HP_A_BASE_MAIN = "82617839e64ea6b70d33ca55b13b3114cca62f3e"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match.group(1))).decode()


def brace_end(source: str, brace: int) -> int:
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(source):
        c = source[i]
        n = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if c in "\r\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if c == "*" and n == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == quote:
                quote = None
            i += 1
            continue
        if c == "/" and n == "/":
            line_comment = True
            i += 2
            continue
        if c == "/" and n == "*":
            block_comment = True
            i += 2
            continue
        if c in "'\"`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise AssertionError("unterminated function")


def function_hashes(source: str, name: str) -> list[str]:
    out: list[str] = []
    pattern = re.compile(rf"^[ \t]*function\s+{re.escape(name)}\s*\(", re.MULTILINE)
    for match in pattern.finditer(source):
        brace = source.find("{", match.end())
        end = brace_end(source, brace)
        out.append(sha(source[match.start():end].encode()))
    return out


CONSUMERS = (
    ("NPC save export", "LEGACY_COMPATIBILITY", "Serialized display field; not authority."),
    ("NPC save restore", "INVALID_AUTHORITY_USE", "Stored HP is written before physical state restore."),
    ("player health facade getter", "LEGACY_COMPATIBILITY", "Compatibility projection exposed to old UI/tests."),
    ("prepared runtime initialization", "LEGACY_COMPATIBILITY", "Initial display cache only."),
    ("impact-time HP projections", "DISPLAY_ONLY", "Four duplicated immediate display calculations."),
    ("damageFloodTickV1 HP projection", "DISPLAY_ONLY", "Fixed-tick display calculation; currently permits false zero."),
    ("HUD and damage panels", "DISPLAY_ONLY", "Numeric presentation only."),
    ("AAR / battle diagnostics", "DISPLAY_ONLY", "Recorded display value, not physical loss authority."),
    ("player save export", "LEGACY_COMPATIBILITY", "Serialized compatibility field."),
    ("player save validation", "LEGACY_COMPATIBILITY", "Legacy field shape validation."),
    ("player save restore", "INVALID_AUTHORITY_USE", "Stored HP overwrites derived display cache."),
    ("test reset/snapshot", "LEGACY_COMPATIBILITY", "Deterministic diagnostics."),
    ("ammo-cookoff direct assignment", "INVALID_AUTHORITY_USE", "Direct HP=0 announces loss without survival authority."),
    ("bottom status bar survival label", "INVALID_AUTHORITY_USE", "HP>0 is used as 생존/상실 authority."),
)


def occurrence_rows(source: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for match in re.finditer(r"(?:runtime\.health\.shipHP|r\.health\.shipHP|shipHP)", source):
        line = source.count("\n", 0, match.start()) + 1
        start = source.rfind("\n", 0, match.start()) + 1
        end = source.find("\n", match.end())
        if end < 0:
            end = len(source)
        text = source[start:end].strip()
        classification = "DISPLAY_ONLY"
        reason = "Numeric presentation or display projection."
        if "=src.shipHP" in text or "=clamp(Number(src.ship.shipHP)" in text:
            classification = "INVALID_AUTHORITY_USE"
            reason = "Stored compatibility HP is trusted during restore."
        elif "shipHP=0" in text.replace(" ", ""):
            classification = "INVALID_AUTHORITY_USE"
            reason = "Direct zero assignment bypasses survival authority."
        elif ".shipHP>0" in text.replace(" ", ""):
            classification = "INVALID_AUTHORITY_USE"
            reason = "Survival label is inferred from display HP."
        elif "export" in text.lower() or "schema" in text.lower() or "shipHP," in text:
            classification = "LEGACY_COMPATIBILITY"
            reason = "Serialized or exposed compatibility value."
        rows.append({"line": line, "token": match.group(0), "classification": classification, "source": text, "reason": reason})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/damage/hp/A/evidence/commit-a")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw = PRODUCT.read_bytes()
    assert len(raw) == PRODUCT_BYTES, (len(raw), PRODUCT_BYTES)
    assert sha(raw) == PRODUCT_SHA256, sha(raw)
    source = unpack(raw)
    functions = [
        "computeShipStatus",
        "createShipSurvivalV1",
        "shipEquipmentOfflineV1",
        "damageFloodTickV1",
        "damageFloodImpactV1",
        "getShipLongitudinalStrengthV48Wip03",
        "exportOperationalState",
        "applyPreparedOperationalStateV48Wip11B",
        "restoreOnePhysicalFleetF",
    ]
    occurrences = occurrence_rows(source)
    invalid = [row for row in occurrences if row["classification"] == "INVALID_AUTHORITY_USE"]
    payload = {
        "schema": "AEGIS_HP_A_BASELINE_AUDIT_1",
        "product": PRODUCT.name,
        "productBytes": len(raw),
        "productSha256": sha(raw),
        "packedMainBytes": len(source.encode()),
        "packedMainSha256": sha(source.encode()),
        "hpABaseMain": HP_A_BASE_MAIN,
        "functionHashes": {name: function_hashes(source, name) for name in functions},
        "shipHpOccurrences": occurrences,
        "invalidAuthorityUseCount": len(invalid),
        "invalidAuthorityUses": invalid,
        "consumerOwnership": [
            {"consumer": consumer, "classification": classification, "reason": reason}
            for consumer, classification, reason in CONSUMERS
        ],
        "authorityFinding": {
            "physicalSurvival": "createShipSurvivalV1 snapshot state/lost/irreversible",
            "missionExecution": "shipEquipmentOfflineV1 plus existing crew combatUnavailable gates",
            "display": "shipHP/runtime.health.shipHP",
            "defect": "display projection can reach zero before survival becomes irreversible; restore and bottom-bar paths also trust display HP",
        },
    }
    (args.out / "baseline-audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    header = "consumer\tclassification\treason\n"
    body = "".join(f"{a}\t{b}\t{c}\n" for a, b, c in CONSUMERS)
    (args.out / "HP_CONSUMER_AUDIT.tsv").write_text(header + body)
    print(json.dumps({"status": "PASS", "occurrences": len(occurrences), "invalidAuthorityUses": len(invalid), "packedMainSha256": payload["packedMainSha256"]}))


if __name__ == "__main__":
    main()
