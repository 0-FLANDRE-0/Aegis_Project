#!/usr/bin/env python3
"""Compare baseline/product managed and NPC radar diagnostic receipts."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def managed_key(row: dict) -> tuple:
    q = row["setup"]
    return tuple(q[k] for k in ("seed", "kind", "rangeKm", "radar"))


def npc_key(row: dict) -> tuple:
    q = row["setup"]
    return tuple(q[k] for k in ("seed", "targetProfile", "observerKind", "rangeKm"))


def compare(name: str, baseline: dict, product: dict, key, fields: tuple[str, ...]) -> dict:
    a = {key(row): row for row in baseline["rows"]}
    b = {key(row): row for row in product["rows"]}
    changes = []
    for condition in sorted(set(a) | set(b), key=str):
        before, after = a.get(condition), b.get(condition)
        if before is None or after is None or any(before.get(f) != after.get(f) for f in fields):
            changes.append({
                "condition": list(condition),
                "baseline": None if before is None else {f: before.get(f) for f in fields},
                "product": None if after is None else {f: after.get(f) for f in fields},
            })
    truth_exposure = sum(
        1 for row in product["rows"]
        for track in row.get("tracks", row.get("rows", []))
        if track.get("truthRefExposed")
    )
    return {
        "name": name,
        "baselineRows": len(a),
        "productRows": len(b),
        "pageErrors": {
            "baseline": baseline.get("pageErrors", []),
            "product": product.get("pageErrors", []),
        },
        "baselineTrackCreated": sum(bool(row.get("trackCreated")) for row in a.values()),
        "productTrackCreated": sum(bool(row.get("trackCreated")) for row in b.values()),
        "productTruthReferenceExposure": truth_exposure,
        "changedConditions": changes,
        "pass": not changes and not truth_exposure and not baseline.get("pageErrors") and not product.get("pageErrors"),
    }


def main() -> None:
    managed = compare(
        "ownship managed radar acceptors",
        read("BASELINE_MANAGED_RADAR.json"),
        read("PRODUCT_MANAGED_RADAR.json"),
        managed_key,
        ("trackCreated", "confirmedSurface"),
    )
    npc = compare(
        "NPC observer radar/track store",
        read("BASELINE_NPC_RADAR.json"),
        read("PRODUCT_NPC_RADAR.json"),
        npc_key,
        ("trackCreated",),
    )
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_RADAR_PATH_COMPARISON_1",
        "pass": managed["pass"] and npc["pass"],
        "managed": managed,
        "npc": npc,
    }
    (ROOT / "RADAR_PATH_RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Managed and NPC radar path validation",
        "",
        f"**Result: {'PASS' if result['pass'] else 'FAIL'}**",
        "",
        "| path | baseline rows | product rows | baseline tracks | product tracks | changed conditions | truth refs |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in (managed, npc):
        lines.append(
            f"| {row['name']} | {row['baselineRows']} | {row['productRows']} | "
            f"{row['baselineTrackCreated']} | {row['productTrackCreated']} | "
            f"{len(row['changedConditions'])} | {row['productTruthReferenceExposure']} |"
        )
    lines += [
        "",
        "The managed test drives production SPY-1D(V), SPQ-9B and BridgeMaster-E",
        "plot acceptors into the ownship TrackStore. The NPC test advances",
        "`stepObserversC` and reads only each observer's anonymous track store.",
        "Neither test treats a direct RF echo as a completed track.",
    ]
    (ROOT / "RADAR_PATH_RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"pass": result["pass"], "managedChanges": len(managed["changedConditions"]), "npcChanges": len(npc["changedConditions"])}))


if __name__ == "__main__":
    main()
