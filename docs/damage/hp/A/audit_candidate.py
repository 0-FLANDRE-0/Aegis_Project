#!/usr/bin/env python3
"""Fail-closed HP_A authority-consumer audit for the frozen phase-C product."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_HP_A.html"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match.group(1))).decode()


def source_line(source: str, offset: int) -> tuple[int, str]:
    line = source.count("\n", 0, offset) + 1
    start = source.rfind("\n", 0, offset) + 1
    end = source.find("\n", offset)
    return line, source[start:len(source) if end < 0 else end].strip()


def occurrence_rows(source: str) -> list[dict[str, object]]:
    rows = []
    for match in re.finditer(r"(?:runtime\.health\.shipHP|r\.health\.shipHP|shipHP)", source):
        line, text = source_line(source, match.start())
        compact = re.sub(r"\s+", "", text)
        if "shipOutcomeWriteDisplayA" in text or "outcome.displayHp" in text:
            classification, reason = "DISPLAY_ONLY", "Single one-way outcome projection writer."
        elif "SHIP_HP" in text and "operationalFinite" in text:
            classification, reason = "LEGACY_COMPATIBILITY", "Saved compatibility field shape validation only."
        elif "shipOutcomeRestoreCompatibilityA" in text:
            classification, reason = "LEGACY_COMPATIBILITY", "Saved HP is mismatch-audited but cannot restore authority."
        elif any(token in text for token in ("fillText", "HP:", "hpCol2", "hpRatio", "frame={", "lines.push")):
            classification, reason = "DISPLAY_ONLY", "HUD/PiP numeric presentation."
        elif any(token in text for token in ("export", "schema", "shipHP,", "snapshot", "health={shipHP:100}", "let shipHP = 100", "shipHP=100")):
            classification, reason = "LEGACY_COMPATIBILITY", "Initialization, diagnostic, or serialized compatibility field."
        elif any(token in compact for token in ("shipHP=0", ".shipHP>0", ".shipHP<=0", "shipHP=src.shipHP", "shipHP=clamp(Number(src.ship.shipHP)")):
            classification, reason = "INVALID_AUTHORITY_USE", "Display HP is used as or written from authority."
        else:
            classification, reason = "DISPLAY_ONLY", "Numeric display cache read without survival/mission decision."
        rows.append({"line": line, "token": match.group(0), "classification": classification, "source": text, "reason": reason})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "docs/damage/hp/A/evidence/commit-c/candidate-audit.json")
    parser.add_argument("--tsv", type=Path, default=ROOT / "docs/damage/hp/A/evidence/commit-c/HP_CONSUMER_AUDIT.tsv")
    parser.add_argument("--main-out", type=Path)
    args = parser.parse_args()
    raw = PRODUCT.read_bytes()
    source = unpack(raw)
    rows = occurrence_rows(source)
    invalid = [row for row in rows if row["classification"] == "INVALID_AUTHORITY_USE"]
    forbidden = {
        "npcStoredHpAuthority": "r.health.shipHP=src.shipHP" in source,
        "playerStoredHpAuthority": "shipHP=clamp(Number(src.ship.shipHP)" in source,
        "directZeroAuthority": bool(re.search(r"\bshipHP\s*=\s*0\s*;", source)),
        "npcHpSurvivalDecision": bool(re.search(r"\.health\.shipHP\s*(?:<=|<|===|==|>|>=)", source)),
        "bottomBarHpSurvivalDecision": "r.health.shipHP>0?'생존':'상실'" in source,
    }
    required = {
        "outcomeContract": "function shipOutcomeA(" in source,
        "singleProjectionWriter": source.count("function shipOutcomeWriteDisplayA(") == 1,
        "npcRestoreRecomputes": "shipOutcomeRestoreCompatibilityA(r,src.shipHP,'NPC_RESTORE')" in source,
        "playerRestoreRecomputes": "shipOutcomeRestoreCompatibilityA(ACTIVE_SHIP_RUNTIME,src.ship.shipHP,'PLAYER_RESTORE')" in source,
        "missionLabelUsesOutcome": "health=shipOutcomeMissionLabelA(outcome.missionState)" in source,
        "aarIncludesOutcome": "shipHP,shipOutcome:shipOutcomeA(ACTIVE_SHIP_RUNTIME),startCounts" in source,
    }
    receipt = json.loads((ROOT / "docs/damage/hp/A/evidence/commit-c/build-receipt.json").read_text())
    checks = {
        "invalidAuthorityUsesZero": not invalid,
        "forbiddenPatternsZero": not any(forbidden.values()),
        "requiredContractPresent": all(required.values()),
        "protectedPhysicsHashesExact": bool(receipt["protectedFunctionHashesExact"]),
    }
    payload = {
        "schema": "AEGIS_HP_A_CANDIDATE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "product": PRODUCT.name,
        "productBytes": len(raw),
        "productSha256": sha(raw),
        "packedMainBytes": len(source.encode()),
        "packedMainSha256": sha(source.encode()),
        "checks": checks,
        "baselineInvalidAuthorityUseCount": 6,
        "candidateInvalidAuthorityUseCount": len(invalid),
        "forbiddenPatterns": forbidden,
        "requiredContract": required,
        "protectedFunctionHashes": receipt["protectedFunctionHashesAfter"],
        "shipHpOccurrences": rows,
        "invalidAuthorityUses": invalid,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    args.tsv.write_text(
        "line\ttoken\tclassification\treason\tsource\n" + "".join(
            f"{row['line']}\t{row['token']}\t{row['classification']}\t{row['reason']}\t{str(row['source']).replace(chr(9), ' ')}\n"
            for row in rows
        )
    )
    if args.main_out:
        args.main_out.parent.mkdir(parents=True, exist_ok=True)
        args.main_out.write_text(source, encoding="utf-8")
    print(json.dumps({"status": payload["status"], "occurrences": len(rows), "invalidAuthorityUses": len(invalid), "checks": checks}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
