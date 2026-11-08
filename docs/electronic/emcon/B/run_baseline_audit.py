#!/usr/bin/env python3
"""Freeze the merged EMITTER_A master-EMCON contract before EMCON_B changes."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_EMITTER_A.html"
PRODUCT_SHA256 = "3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be"
PRODUCT_BYTES = 22_146_163


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack_main(raw: bytes) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match.group(1))).decode()


def declaration_spans(source: str, name: str) -> list[str]:
    spans: list[str] = []
    for match in re.finditer(rf"function\s+{re.escape(name)}\s*\(", source):
        brace = source.find("{", match.end())
        if brace < 0:
            continue
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
                    spans.append(source[match.start() : index + 1])
                    break
    return spans


def select_function(source: str, name: str, contains: str | None = None) -> str:
    spans = declaration_spans(source, name)
    if contains is not None:
        spans = [span for span in spans if contains in span]
    if len(spans) != 1:
        raise AssertionError(f"{name}: expected one selected declaration, got {len(spans)}")
    return spans[0]


FUNCTIONS: dict[str, tuple[str, str | None]] = {
    "applyEmconDesignationF2": ("applyEmconDesignationF2", None),
    "toggleEmcon.operator": ("toggleEmcon", "networkOverrideRadarG(ACTIVE_SHIP_RUNTIME)"),
    "prepareElectronicF": ("prepareElectronicF", None),
    "electronicSettingsF": ("electronicSettingsF", None),
    "electronicCommandF": ("electronicCommandF", None),
    "electronicShipPhysicalEmittersDeclaredA": ("electronicShipPhysicalEmittersDeclaredA", None),
    "electronicPhysicalEmittersF": ("electronicPhysicalEmittersF", None),
    "observerCommandC": ("observerCommandC", None),
    "observerSnapshotC": ("observerSnapshotC", None),
    "networkSetRadarG": ("networkSetRadarG", None),
    "networkGroupStepG": ("networkGroupStepG", None),
    "networkExportElectronicG": ("networkExportElectronicG", None),
    "networkCommandG": ("networkCommandG", None),
    "fleetCommandG": ("fleetCommandG", None),
    "fleetSnapshotG": ("fleetSnapshotG", None),
    "exportOperationalState": ("exportOperationalState", None),
    "prepareOperationalStateV48Wip11B": ("prepareOperationalStateV48Wip11B", None),
    "applyPreparedOperationalStateV48Wip11B": ("applyPreparedOperationalStateV48Wip11B", None),
    "resetElectronicFleetF": ("resetElectronicFleetF", None),
    "shipEmitterRuntimeSnapshotA": ("shipEmitterRuntimeSnapshotA", None),
}


CLASSIFICATION = [
    {
        "symbol": "emconActive",
        "class": "MASTER_OWNER",
        "owner": "active player ship radar-master overlay",
        "notes": "Written only through applyEmconDesignationF2/toggleEmcon-compatible paths.",
    },
    {
        "symbol": "observerC(r).emcon",
        "class": "MASTER_OWNER",
        "owner": "non-player per-ShipRuntime radar-master overlay",
        "notes": "Initialized by prepareElectronicF; commands and network lease may mutate it.",
    },
    {
        "symbol": "applyEmconDesignationF2",
        "class": "MASTER_OWNER",
        "owner": "active-player master write and PD/TWS transition",
        "notes": "Preserves radiation-free selection behavior while stopping precision tracking.",
    },
    {
        "symbol": "toggleEmcon",
        "class": "MASTER_OWNER",
        "owner": "operator-compatible active-player master toggle",
        "notes": "Exits network group radar authority before writing the master.",
    },
    {
        "symbol": "electronicCommandF",
        "class": "MASTER_OWNER",
        "owner": "owner-addressed EW/master command",
        "notes": "Routes active ship through toggleEmcon and NPC through observerC(r).emcon.",
    },
    {
        "symbol": "observerCommandC",
        "class": "MASTER_OWNER",
        "owner": "non-player diagnostic sensor/master command",
        "notes": "Restricted to non-player observer owners.",
    },
    {
        "symbol": "networkSetRadarG / networkGroupStepG",
        "class": "MASTER_OWNER",
        "owner": "temporary group master overlay",
        "notes": "groupBase remembers the individual master; groupLease is time-limited.",
    },
    {
        "symbol": "electronicSettingsF / networkExportElectronicG",
        "class": "COMPATIBILITY_READER",
        "owner": "legacy export and network compatibility view",
        "notes": "Reads the individual master and ECM request state without owning it.",
    },
    {
        "symbol": "electronicShipPhysicalEmittersDeclaredA",
        "class": "PHYSICAL_EMISSION_GATE",
        "owner": "EMITTER_A physical output resolver",
        "notes": "Currently applies the radar master and existing equipment/allocator gates.",
    },
    {
        "symbol": "legacy active SPY/SPQ/NAV update paths + observer step",
        "class": "SENSOR_UPDATE_GATE",
        "owner": "sensor measurement schedulers",
        "notes": "Must consume the same effective decision in EMCON_B, not only hide emitters.",
    },
    {
        "symbol": "surface missile/SPG/auto-radiate checks",
        "class": "WEAPON_DOCTRINE_GATE",
        "owner": "existing fire-control and doctrine paths",
        "notes": "Master behavior remains authoritative; FIRE_CONTROL has no active registry item.",
    },
    {
        "symbol": "fleetEmconG / networkEmconG / uiEmconChipA / mapEmconMenuE / mapAllRadiationE / mapRadarE",
        "class": "UI_ONLY",
        "owner": "operator routing and presentation",
        "notes": "Must call owner-addressed command APIs; render/refresh may not mutate policy.",
    },
    {
        "symbol": "observerSnapshotC / shipEmitterRuntimeSnapshotA / emconDesignationSnapshotF2",
        "class": "DIAGNOSTIC_ONLY",
        "owner": "read-only diagnostics",
        "notes": "No policy authority and no RNG consumption.",
    },
]


def main() -> None:
    raw = PRODUCT.read_bytes()
    if len(raw) != PRODUCT_BYTES or sha(raw) != PRODUCT_SHA256:
        raise AssertionError("EMITTER_A product bytes/SHA mismatch")
    main_source = unpack_main(raw)
    function_hashes = {}
    for label, (name, contains) in FUNCTIONS.items():
        body = select_function(main_source, name, contains)
        function_hashes[label] = {
            "sha256": sha(body.encode()),
            "bytes": len(body.encode()),
            "occurrencesInMain": len(re.findall(rf"\b{re.escape(name)}\b", main_source)),
        }

    emitter_baseline = json.loads((ROOT / "docs/electronic/emitter/A/BASELINE_AUDIT.json").read_text())
    closure = json.loads((ROOT / "docs/electronic/emitter/A/CLOSURE_CALL_GATE.json").read_text())
    representative = {
        "source": "merged EMITTER_A evidence bound to the exact product SHA above",
        "profileCaseCounts": {
            key: len(value["cases"]) for key, value in emitter_baseline["profiles"].items()
        },
        "fleetSceneIds": sorted(emitter_baseline["fleetScenes"]),
        "sovRegisteredInactiveRows": len(emitter_baseline["sovRegistration"]),
        "emitterChecks": emitter_baseline["checks"],
        "closureChecks": closure["checks"],
    }
    checks = {
        "mainHeadExpectedByDirective": True,
        "productBytesExact": len(raw) == PRODUCT_BYTES,
        "productShaExact": sha(raw) == PRODUCT_SHA256,
        "allFunctionsResolved": len(function_hashes) == len(FUNCTIONS),
        "baselineEmitterEvidencePass": emitter_baseline["status"] == "PASS",
        "closureEvidencePass": closure["status"] == "PASS",
        "classificationComplete": len(CLASSIFICATION) == 13,
    }
    result = {
        "schema": "AEGIS_EMCON_B_BASELINE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baseline": {
            "main": "3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941",
            "mergedPullRequest": 73,
            "product": PRODUCT.name,
            "bytes": len(raw),
            "sha256": sha(raw),
            "mainScriptBytes": len(main_source.encode()),
            "mainScriptSha256": sha(main_source.encode()),
        },
        "checks": checks,
        "functionHashes": function_hashes,
        "classification": CLASSIFICATION,
        "representativeSnapshot": representative,
        "behaviorChange": False,
    }
    (HERE / "BASELINE_AUDIT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "baseline": result["baseline"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
