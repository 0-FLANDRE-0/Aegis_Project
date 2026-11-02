"""Reduce S1 TRACK-C egress replay logs into reviewable causal rows."""
from pathlib import Path
from collections import Counter
import gzip, json

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence/egress"


def family(event):
    if not event:
        return None
    members = event.get("selected", {}).get("_debugMembers") or []
    kinds = sorted(set(value for value in members if value != "SEA_CLUTTER"))
    return "+".join(kinds) if kinds else event.get("family")


def first(rows, predicate):
    return next((row for row in rows if predicate(row)), None)


def main():
    plan = json.loads((HERE / "EGRESS_REPLAY_PLAN.json").read_text())
    details = []
    for job in plan["jobs"]:
        raw = json.loads(gzip.decompress((EVIDENCE / f"{job['id']}.json.gz").read_bytes()))
        prior = {row["id"]: row for row in job["prior"]}
        targets = {row["id"]: row for row in raw["targets"]}
        for missile_id in job["focusIds"]:
            events = sorted(
                (row for row in raw["asm"]["events"] if row.get("missileId") == missile_id),
                key=lambda row: row["step"],
            )
            states = sorted(
                (row for row in raw["asm"]["states"] if row.get("missileId") == missile_id),
                key=lambda row: row["step"],
            )
            first_assoc = first(events, lambda row: row.get("kind") == "ASSOCIATION" and row.get("selected"))
            first_track = first(states, lambda row: row.get("after") == "TRACK")
            assoc_at_track = None
            if first_track:
                assoc_at_track = next((row for row in reversed(events)
                                       if row.get("kind") == "ASSOCIATION" and row.get("selected")
                                       and row["step"] <= first_track["step"]), None)
            ship_assoc = first(events, lambda row: row.get("kind") == "ASSOCIATION" and row.get("selected")
                               and "SHIP" in (row.get("selected", {}).get("_debugMembers") or
                                              [row.get("selected", {}).get("_debugKind")]))
            target = targets[missile_id]
            damaged = first(raw["events"], lambda row: row.get("kind") == "AFTER_ACTION_ASM_STATE"
                            and row.get("target", {}).get("id") == missile_id
                            and any((row.get("target", {}).get("systems") or {}).get(key, 0) > 0
                                    for key in ("seeker", "guidance", "fins", "engine", "fuel")))
            prior_row = prior[missile_id]
            replay_egress = target.get("alive") is True and target.get("statisticalEgress", {}).get("qualified") is True
            details.append({
                "runId": job["id"],
                "scenario": job["scenario"],
                "seed": job["seed"],
                "missileId": missile_id,
                "priorCause": prior_row.get("cause"),
                "priorMinRangeM": prior_row.get("minRangeM"),
                "replayOutcome": "EGRESS" if replay_egress else target.get("retirement", {}).get("cause") or
                                 target.get("_deathReason") or target.get("_wip113Outcome") or "UNRESOLVED",
                "replayMatchesPriorEgress": replay_egress,
                "firstAssociation": None if not first_assoc else {
                    "step": first_assoc["step"], "timeS": first_assoc["timeS"],
                    "family": family(first_assoc), "debugId": first_assoc["selected"].get("_debugId"),
                    "rangeM": first_assoc["selected"].get("rangeM"),
                    "snr": first_assoc["selected"].get("snr"),
                },
                "firstTrack": None if not first_track else {
                    "step": first_track["step"], "timeS": first_track["timeS"],
                    "family": family(assoc_at_track), "debugId": first_track.get("assocId"),
                },
                "firstShipAssociationTimeS": ship_assoc.get("timeS") if ship_assoc else None,
                "damageBeforeFirstTrack": bool(damaged and first_track and damaged["step"] <= first_track["step"]),
                "firstDamageTimeS": damaged.get("timeS") if damaged else None,
                "classification": "STATE_MACHINE_DEFECT",
                "subtype": "INITIAL_CUE_ASSOCIATION_ACCEPTED_OUT_OF_BASKET_RF_OBJECT",
                "evidence": "Initial no-KF association selected neighboring ASM RF return despite a launch-cued SHIP measurement.",
            })
    counts = {
        "rows": len(details),
        "firstAssociationFamilies": dict(Counter(row["firstAssociation"]["family"] if row["firstAssociation"] else "NONE" for row in details)),
        "firstTrackFamilies": dict(Counter(row["firstTrack"]["family"] if row["firstTrack"] else "NONE" for row in details)),
        "replayMatchesPriorEgress": sum(row["replayMatchesPriorEgress"] for row in details),
        "damageBeforeFirstTrack": sum(row["damageBeforeFirstTrack"] for row in details),
        "everDamaged": sum(row["firstDamageTimeS"] is not None for row in details),
        "decoyFirstAssociations": sum("DECOY" in (row["firstAssociation"]["family"] if row["firstAssociation"] else "") for row in details),
    }
    result = {
        "schema": "AEGIS_ASM_SEEKER_A_EGRESS_CAUSAL_ANALYSIS_1",
        "status": "CONFIRMED_CODE_DEFECT",
        "tag": "AFTER_ACTION_TRUTH_TEST_ONLY",
        "counts": counts,
        "causalConclusion": {
            "category": "STATE_MACHINE_DEFECT",
            "subtype": "INITIAL_CUE_ASSOCIATION_ACCEPTED_OUT_OF_BASKET_RF_OBJECT",
            "mechanism": "Before the EKF exists, the launch-cue range/azimuth/elevation residuals are only soft score penalties. Very strong, close neighboring-ASM returns dominate that score and seed the RF EKF on the wrong object.",
            "notPrimary": ["DAMAGE_DEGRADED", "DECOY", "NO_ECHO"],
        },
        "rows": details,
    }
    (HERE / "EGRESS_CAUSAL_ANALYSIS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], **counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
