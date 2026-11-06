#!/usr/bin/env python3
"""Audit Stage-1b lexical function scope, RNG, and truth boundary."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


HARNESS_ROOT = Path("/workspace/aegis-ui-a")
sys.path[:0] = [
    str(HARNESS_ROOT / "docs/pip/B"),
    str(HARNESS_ROOT / "docs/helicopter/H"),
    str(HARNESS_ROOT / "docs/multiship/G"),
    str(HARNESS_ROOT / "docs/bunkerhill/K"),
]
import browser_backend

browser_backend.install()
from browser_i import launch, load


PAYLOAD_RE = re.compile(rb'(data-c55-index="13">)([^<]+)')


def unpack_bytes(raw: bytes) -> str:
    match = PAYLOAD_RE.search(raw)
    if not match:
        raise AssertionError("main payload not found")
    return gzip.decompress(base64.b64decode(match.group(2))).decode()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def declared_names(source: str) -> set[str]:
    live = source.split(' const source="function missileThrustN', 1)[0]
    return set(re.findall(r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", live))


def instrument(raw: bytes, names: set[str]) -> bytes:
    source = unpack_bytes(raw)
    marker = "  completeShipStartup();"
    if source.count(marker) != 1:
        raise AssertionError("startup marker count")
    injection = (
        "  window.__CUE_A1_SCOPE_FUNCTIONS__=(()=>{const out={};for(const n of "
        + json.dumps(sorted(names), separators=(",", ":"))
        + "){try{const v=eval(n);if(typeof v==='function')out[n]=Function.prototype.toString.call(v);}" 
          "catch(_){}}return out;})();\n"
    )
    source = source.replace(marker, injection + marker)
    payload = base64.b64encode(gzip.compress(source.encode(), compresslevel=9, mtime=0))
    return PAYLOAD_RE.sub(lambda match: match.group(1) + payload, raw, count=1)


def runtime_function_map(pw, path: Path, names: set[str]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, instrument(path.read_bytes(), names), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = page.evaluate("()=>window.__CUE_A1_SCOPE_FUNCTIONS__")
    page.close()
    browser.close()
    if not isinstance(rows, dict):
        raise AssertionError("scope instrumentation did not initialize")
    return rows, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    before_raw, after_raw = args.baseline.read_bytes(), args.candidate.read_bytes()
    names = declared_names(unpack_bytes(before_raw)) | declared_names(unpack_bytes(after_raw))
    with sync_playwright() as pw:
        before, before_errors = runtime_function_map(pw, args.baseline, names)
        after, after_errors = runtime_function_map(pw, args.candidate, names)
    before_names, after_names = set(before), set(after)
    shared = sorted(before_names & after_names)
    changed = sorted(name for name in shared if before[name] != after[name])
    removed = sorted(before_names - after_names)
    added = sorted(after_names - before_names)
    allowed_changed = {
        "seekerSynthesizeMonostaticPowerU2",
        "asmCueSymmetrizeA", "asmCueInitialPacketA", "asmTargetCueStateA",
        "asmTargetCuePredictA", "asmCueScalarUpdateA", "asmCueUpdateA",
        "asmCueAngularUpdateA", "asmTargetCueU0", "asmCueBasketU0",
        "asmTargetCueSnapshotA", "asmCuePredictedAnglesA", "spawnEnemyMissile",
    }
    allowed_removed = {"asmCueLimitVelocityA"}
    allowed_added = {
        "asmCueMatIdentityA", "asmCueMatMulA", "asmCueMatLinearA",
        "asmCueMatSolveA", "asmCueMatrixExpA", "asmSingerAxisDiscreteA",
        "asmSingerDiscreteA", "asmCueCovariancePredictA", "asmCueApplyBoundsA",
        "asmCueSingerPredictDiagnosticA",
    }
    protected = {
        "asmSeekerEchoMeasurement", "asmSeekerCompositeReturns",
        "arhRfTargetEvidenceWip13B12", "arhRfCandidateAcceptedWip13B12",
        "updateAsmSeeker", "buildEssmArhEchoPool", "_v1UpdateArhMeasurementCore",
        "_v1UpdateSarhMeasurementCore", "electronicHojF", "asmUpdateHojTrack",
        "shipboardRadarEchoFieldWip13B13", "missileNavB2Update",
        "computeGuidanceAccelV1", "computeKappaMidcourseAccelV2",
        "computeZEMCorrectionV1", "computeInterceptPk", "applyInterceptResult",
        "gameFlightTerminationEvaluateV48",
    }
    missing_protected = sorted(protected - before_names - after_names)
    protected_changes = sorted(name for name in protected & before_names & after_names if before[name] != after[name])
    core = args.core.read_text()
    forbidden_truth_tokens = (
        "owner", "ship", "entityId", "profileId", "coordinates",
        "physicalShipsB", "targetPool", "_samB1TruthOwnState",
    )
    forbidden_rng_tokens = ("SIM_RNG_STATE", "simRandom", "Math.random", "rand(")
    truth_hits = [token for token in forbidden_truth_tokens if token in core]
    rng_hits = [token for token in forbidden_rng_tokens if token in core]
    unexpected = {
        "changed": sorted(set(changed) - allowed_changed),
        "removed": sorted(set(removed) - allowed_removed),
        "added": sorted(set(added) - allowed_added),
        "missingExpectedChanged": sorted(allowed_changed - set(changed)),
        "missingExpectedRemoved": sorted(allowed_removed - set(removed)),
        "missingExpectedAdded": sorted(allowed_added - set(added)),
        "missingProtected": missing_protected,
        "protectedChanged": protected_changes,
        "truthTokens": truth_hits,
        "rngTokens": rng_hits,
        "pageErrors": before_errors + after_errors,
    }
    checks = {
        "declaredScopeExact": not any(unexpected.values()),
        "allOtherResolvedFunctionsByteEqual": len(shared) - len(changed) > 0,
        "protectedRfPdRcsBeamEkfHojGuidanceStable": not protected_changes and not missing_protected,
        "cueConsumerTruthTokensZero": not truth_hits,
        "cueConsumerGameRngTokensZero": not rng_hits,
        "c52FixedMemoryGuardPreserved": "if(em._c52InsMemory)return q" in core and "if(!em._c52InsMemory)" in core,
        "pageErrorsZero": not before_errors and not after_errors,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE1B_SCOPE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "baselineSha256": hashlib.sha256(before_raw).hexdigest(),
        "candidateSha256": hashlib.sha256(after_raw).hexdigest(),
        "method": "IN_IIFE_RUNTIME_FUNCTION_TO_STRING",
        "checks": checks,
        "resolvedFunctionCounts": {"baseline": len(before_names), "candidate": len(after_names), "shared": len(shared)},
        "unchangedSharedFunctions": len(shared) - len(changed),
        "changed": [{"name": name, "beforeSha256": sha(before[name]), "afterSha256": sha(after[name])} for name in changed],
        "removed": [{"name": name, "sha256": sha(before[name])} for name in removed],
        "added": [{"name": name, "sha256": sha(after[name])} for name in added],
        "protected": [{"name": name, "byteEqual": name not in protected_changes, "sha256": sha(before[name])} for name in sorted(protected) if name in before],
        "unexpected": unexpected,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "changed": changed,
                      "removed": removed, "added": added, "unexpected": unexpected,
                      "unchangedSharedFunctions": result["unchangedSharedFunctions"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
