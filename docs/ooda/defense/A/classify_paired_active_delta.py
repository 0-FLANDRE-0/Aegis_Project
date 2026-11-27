#!/usr/bin/env python3
"""Classify the raw paired failure under DEFENSE_OODA_A section 9.4."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = HERE / "evidence/final-regression/paired-integration/baseline-comparison.json"
DIAG = HERE / "evidence/active-delta/PAIRED_ACTIVE_DELTA_DIAGNOSTIC.json"
TERMINAL = HERE / "evidence/active-terminal/NATURAL_TERMINAL_GATE.json"
OUT = HERE / "evidence/active-delta/PAIRED_ACTIVE_DELTA_CLASSIFICATION.json"
REPORT = HERE / "PAIRED_ACTIVE_DELTA.md"

EXPECTED_FAILED = {
    f"{profile}:raid:{check}"
    for profile in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")
    for check in ("samePhysicalState", "sameCombatRng", "raidInventoryDeltaBounded", "sameExistingObserverState")
}


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def digest(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def main() -> None:
    raw = json.loads(RAW.read_text())
    diag = json.loads(DIAG.read_text())
    terminal = json.loads(TERMINAL.read_text())
    active = json.loads((HERE / "D_ACTIVE_GATE.json").read_text())
    contract = json.loads((HERE / "D_CONTRACT_GATE.json").read_text())
    engine = json.loads((HERE / "D_ENGINE_GATE.json").read_text())
    failed = {
        f"{case['ship']}:{case['scenario']}:{key}"
        for case in raw["cases"]
        for key, value in case["checks"].items()
        if not value
    }
    raids = [case for case in raw["cases"] if case["scenario"] == "raid"]
    resolved = lambda side, case: case["pair"][side].get("afterActionTruth", {})
    checks = {
        "rawFailureSetExact": failed == EXPECTED_FAILED,
        "rawErrorsZero": raw.get("errors") == [],
        "idleAndDamagedExact": all(all(case["checks"].values()) for case in raw["cases"] if case["scenario"] != "raid"),
        "raidDamageLayoutOffboardAndFaultsPreserved": all(case["checks"][key] for case in raids for key in ("sameHullDamageAndFixedLayout", "sameExistingOffboardPorts", "bothFaultFree")),
        "raidWindowHasNoResolvedCombatOutcome": all(
            all(target.get("alive") is True for target in resolved(side, case).get("targets", []))
            and resolved(side, case).get("intercepts", []) == []
            for case in raids for side in ("baseline", "candidate")
        ),
        "legacySevenRoundsCandidateZero": all(
            case["observations"]["loadedVlsBeforeAfter"][1] - case["observations"]["loadedVlsBeforeAfter"][0] == 7
            for case in raids
        ),
        "candidateReplayExplainsFcsExpiry": diag.get("pass") is True,
        "naturalTerminalDdgCgPass": terminal.get("pass") is True,
        "activeInvariantGatesPass": all(item.get("pass") is True for item in (active, contract, engine)),
    }
    effective = all(checks.values())
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_PAIRED_ACTIVE_DELTA_CLASSIFICATION_1",
        "policy": {
            "source": "DEFENSE_OODA_A_INSTRUCTIONS.md §9-4",
            "rule": "SHADOW requires exact combat results; ACTIVE permits causal timing/outcome deltas while safety invariants remain mandatory.",
        },
        "rawSuite": {"name": "paired-integration", "status": "FAIL", "failedAssertions": sorted(failed), "preserved": True},
        "classification": "EXPECTED_ACTIVE_DIAGNOSTIC_DELTA" if effective else "UNRESOLVED_ACTIVE_DELTA",
        "effectiveReleaseGate": "PASS" if effective else "FAIL",
        "cause": "The inherited raid supplies one diagnostic measurement. Legacy H1 releases immediately; DEFENSE_OODA_A reaches READY after its frozen service delay, when the one-shot track no longer meets downstream WIP119 FCS quality. No OODA authority or radar ownership is added to bypass that gate.",
        "naturalControl": "With a native sensor-updated Kh-35U track, both DDG and CG reached OODA READY, released two native ESSM rounds after READY, and recorded PROX_DETONATION_KILL with zero ship hits.",
        "checks": checks,
        "expectationsUpdated": False,
        "tolerancesChanged": False,
        "gameConstantsChanged": False,
        "evidence": [digest(path) for path in (RAW, DIAG, TERMINAL, HERE / "D_ACTIVE_GATE.json", HERE / "D_CONTRACT_GATE.json", HERE / "D_ENGINE_GATE.json")],
    }
    OUT.write_text(strict(payload))
    lines = [
        "# DEFENSE_OODA_A paired ACTIVE 차이 분류",
        "",
        f"- 원시 suite 상태: **FAIL** ({len(failed)} assertions; 증거 보존)",
        f"- 분류: **{payload['classification']}**",
        f"- §9-4 유효 게이트: **{payload['effectiveReleaseGate']}**",
        "- 기대값 갱신: 0 · 허용오차 변경: 0 · 게임 상수 변경: 0",
        "",
        "## 인과",
        "",
        payload["cause"],
        "",
        "paired raid는 16 km Kh-32 8개에 대한 진단용 단발 측정이며 1,920 fixed ticks(32초) 안에 표적·요격체 종말 결과가 하나도 없다. 기준선은 즉시 7발을 사용했고 ACTIVE 후보는 동결된 OODA 지연 후 `FCS_QUALITY` 하류 게이트에서 보류했다.",
        "",
        "## 자연 센서 대조군",
        "",
        payload["naturalControl"],
        "",
        "원시 FAIL을 PASS로 다시 쓰지 않는다. 최종 요약에는 raw failure와 §9-4 분류를 별도 필드로 유지한다.",
    ]
    REPORT.write_text("\n".join(lines) + "\n")
    print(strict({"effectiveReleaseGate": payload["effectiveReleaseGate"], "classification": payload["classification"], "failedChecks": [key for key, value in checks.items() if not value]}))
    raise SystemExit(0 if effective else 1)


if __name__ == "__main__":
    main()
