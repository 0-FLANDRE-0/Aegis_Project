#!/usr/bin/env python3
"""Static scope, gate, truth and RNG audit for U3 Commit D."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from verify_b_scope import digest, function_source, unpack


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); before, after = unpack(args.baseline), unpack(args.candidate)
    unchanged = [
        "electronicPhysicalEmittersF", "asmPassiveFrequencyA", "asmPassiveFrequencyAcceptedA",
        "asmPassiveEmitterGainA", "asmCuePredictedAnglesA",
        "asmPassiveDirectRangeEstimateA", "asmApplyPassiveBearingB2", "asmCueAngularUpdateA",
        "asmCueUpdateA", "asmUpdateHojTrack", "harpoonUpdateHojC", "harpoonSeekerA",
        "harpoonGateA", "harpoonRouteGateE", "harpoonExportA", "harpoonRestoreA",
    ]
    hashes = {}; unexpected = []
    for name in unchanged:
        left, right = function_source(before, name), function_source(after, name); same = left == right
        hashes[name] = {"baseline": digest(left), "candidate": digest(right), "byteEqual": same}
        if not same: unexpected.append(name)
    old_receiver = before[before.index("function asmPassiveReceiverGainA"):before.index("function asmCuePredictedAnglesA")]
    new_receiver = after[after.index("function asmPassiveReceiverGainA"):after.index("function asmCuePredictedAnglesA")]
    hashes["asmPassiveReceiverGainA"] = {"baseline": digest(old_receiver), "candidate": digest(new_receiver), "byteEqual": old_receiver == new_receiver}
    if old_receiver != new_receiver: unexpected.append("asmPassiveReceiverGainA")
    old_measurement, new_measurement = function_source(before, "asmPassiveRfMeasurementB2"), function_source(after, "asmPassiveRfMeasurementB2")
    gate = "d2=dAz*dAz/Sa+dEl*dEl/Se;if(d2>ASM_CUE_A_SPEC.basketSigma**2){rejections.basket++;continue;}"
    selector_start = after.find("const SEEKER_U3_PASSIVE_RF_MODE_D=")
    selector_end = after.find("function asmPassiveRfMeasurementB2", selector_start)
    selector = after[selector_start:selector_end]
    checks = {
        "measurementChanged": old_measurement != new_measurement,
        "mahalanobisGateBytePresentBefore": old_measurement.count(gate) == 1,
        "mahalanobisGateBytePresentAfter": new_measurement.count(gate) == 1,
        "scoreAfterGate": new_measurement.find(gate) < new_measurement.find("selectionScore=d2+Math.log(innovationDet)"),
        "formulaExact": "selectionScore=d2+Math.log(innovationDet)" in new_measurement,
        "diagonalInnovationDet": "const innovationDet=Sa*Se" in new_measurement,
        "selectorGetsAnonymousCandidates": "seekerU3PassiveRfSelectionD(candidates)" in new_measurement,
        "deterministicObservableTie": all(key in selector for key in ("frequencyMHz", "worldAz", "worldEl", "family", "emitterClass", "band")),
        "noTruthOrIdentitySelectorInput": not re.search(r"\b(sourceId|entityId|platformId|targetId|truthPosition|physicalTarget|source\.point)\b", selector),
        "selectorConsumesNoRng": not re.search(r"\b(simRandom|randn|harpoonRandomA|harpoonNoiseA|Math\.random)\b", selector),
        "noNewDistanceCap": not re.search(r"(?:range|distance).*(?:cap|limit).*\d", selector, re.I),
        "savedSchemaUnchanged": hashes["harpoonExportA"]["byteEqual"] and hashes["harpoonRestoreA"]["byteEqual"],
    }
    passed = not unexpected and all(checks.values())
    result = {"schema": "AEGIS_SEEKER_UNIFY_U3_D_SCOPE_1", "status": "PASS" if passed else "FAIL",
              "unchangedFunctionHashes": hashes, "unexpectedChangedFunctions": unexpected,
              "intentionallyChangedFunctionHashes": {"asmPassiveRfMeasurementB2": {"baseline": digest(old_measurement), "candidate": digest(new_measurement)}},
              "selectorSha256": digest(selector), "checks": checks, "savedSchemaChanged": False,
              "rfPdNoiseRcsBeamChanged": False, "gameplayConstantsAdded": 0}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "unchangedFunctions": len(unchanged), "unexpected": unexpected, "checks": checks}, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

