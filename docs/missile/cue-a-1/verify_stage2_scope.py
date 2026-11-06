#!/usr/bin/env python3
"""Audit Stage-2 function scope, anonymous selection, RNG and HOJ preservation."""
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
sys.path[:0] = [str(HARNESS_ROOT / p) for p in ("docs/pip/B", "docs/helicopter/H", "docs/multiship/G", "docs/bunkerhill/K")]
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
    source = unpack_bytes(raw);marker = "  completeShipStartup();"
    if source.count(marker) != 1:
        raise AssertionError("startup marker count")
    injection = (
        "  window.__CUE_A1_STAGE2_SCOPE_FUNCTIONS__=(()=>{const out={};for(const n of "
        + json.dumps(sorted(names), separators=(",", ":"))
        + "){try{const v=eval(n);if(typeof v==='function')out[n]=Function.prototype.toString.call(v);}" 
          "catch(_){}}return out;})();\n"
    )
    source = source.replace(marker, injection + marker)
    payload = base64.b64encode(gzip.compress(source.encode(), compresslevel=9, mtime=0))
    return PAYLOAD_RE.sub(lambda match: match.group(1) + payload, raw, count=1)


def runtime_map(pw, path: Path, names: set[str]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = [];browser = launch(pw)
    page = load(browser, instrument(path.read_bytes(), names), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = page.evaluate("()=>window.__CUE_A1_STAGE2_SCOPE_FUNCTIONS__")
    page.close();browser.close()
    if not isinstance(rows, dict):
        raise AssertionError("scope instrumentation unavailable")
    return rows, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--passive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    before_raw, after_raw = args.baseline.read_bytes(), args.candidate.read_bytes()
    before_source, after_source = unpack_bytes(before_raw), unpack_bytes(after_raw)
    names = declared_names(before_source) | declared_names(after_source)
    with sync_playwright() as pw:
        before, before_errors = runtime_map(pw, args.baseline, names)
        after, after_errors = runtime_map(pw, args.candidate, names)
    before_names, after_names = set(before), set(after);shared = sorted(before_names & after_names)
    changed = sorted(name for name in shared if before[name] != after[name])
    removed = sorted(before_names - after_names);added = sorted(after_names - before_names)
    expected_changed = {"electronicPhysicalEmittersF", "asmPassiveEmitterGainA", "asmPassiveReceiverGainA", "asmPassiveRfMeasurementB2"}
    expected_added = {"asmPassiveFrequencyA", "asmPassiveFrequencyAcceptedA", "asmPassivePositiveSweepOffsetA"}
    protected = {"electronicHojF", "asmUpdateHojTrack", "asmSeekerEchoMeasurement", "asmSeekerCompositeReturns",
                 "updateAsmSeeker", "buildEssmArhEchoPool", "_v1UpdateArhMeasurementCore", "_v1UpdateSarhMeasurementCore",
                 "shipboardRadarEchoFieldWip13B13", "missileNavB2Update", "computeGuidanceAccelV1",
                 "computeKappaMidcourseAccelV2", "computeZEMCorrectionV1", "computeInterceptPk", "applyInterceptResult",
                 "gameFlightTerminationEvaluateV48"}
    protected_changes = sorted(name for name in protected & before_names & after_names if before[name] != after[name])
    passive = args.passive.read_text()
    family_pos = passive.find("ASM_MIDCOURSE_PASSIVE_FAMILIES.includes(family)")
    geometry_pos = passive.find("source.point.x")
    candidate_match = re.search(r"candidates\.push\(\{(.*?)\}\);", passive, re.S)
    sample_match = re.search(r"s\.sample=\{source:'PASSIVE_RF_CUE_A'.*?\};", passive, re.S)
    if not candidate_match or not sample_match:
        raise AssertionError("passive candidate/payload not found")
    candidate_source, sample_source = candidate_match.group(1), sample_match.group(0)
    forbidden_identity = ("owner", "ship", "entityId", "profileId", "truthRef", "point", "coordinates")
    candidate_hits = [token for token in forbidden_identity if token in candidate_source]
    payload_hits = [token for token in forbidden_identity if token in sample_source]
    rng_hits = [token for token in ("SIM_RNG_STATE", "simRandom", "Math.random", "rand(") if token in passive]
    unexpected = {
        "changed": sorted(set(changed) - expected_changed), "missingChanged": sorted(expected_changed - set(changed)),
        "added": sorted(set(added) - expected_added), "missingAdded": sorted(expected_added - set(added)),
        "removed": removed, "protectedChanged": protected_changes, "candidateIdentityTokens": candidate_hits,
        "payloadIdentityTokens": payload_hits, "gameRngTokens": rng_hits, "pageErrors": before_errors + after_errors,
    }
    checks = {
        "functionScopeExact": not any(unexpected.values()),
        "allOtherResolvedFunctionsByteEqual": len(shared) - len(changed) > 3000,
        "hojByteEqual": before.get("electronicHojF") == after.get("electronicHojF") and before.get("asmUpdateHojTrack") == after.get("asmUpdateHojTrack"),
        "familyFilterBeforeGeometry": 0 <= family_pos < geometry_pos,
        "candidateContainsNoTruthIdentityOrCoordinates": not candidate_hits,
        "measurementPayloadContainsNoTruthIdentityOrCoordinates": not payload_hits,
        "isolatedHashSaltsPreserved": "0x6e51" in passive and "0x6e52" in passive and not rng_hits,
        "pageErrorsZero": not before_errors and not after_errors,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE2_SCOPE_AUDIT_1", "status": "PASS" if all(checks.values()) else "FAIL",
        "baselineSha256": hashlib.sha256(before_raw).hexdigest(), "candidateSha256": hashlib.sha256(after_raw).hexdigest(),
        "checks": checks, "resolvedFunctionCounts": {"baseline": len(before_names), "candidate": len(after_names), "shared": len(shared)},
        "unchangedSharedFunctions": len(shared) - len(changed),
        "changed": [{"name": name, "beforeSha256": sha(before[name]), "afterSha256": sha(after[name])} for name in changed],
        "added": [{"name": name, "sha256": sha(after[name])} for name in added], "removed": removed,
        "protected": [{"name": name, "byteEqual": name not in protected_changes, "sha256": sha(before[name])} for name in sorted(protected) if name in before],
        "unexpected": unexpected,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks, "changed": changed, "added": added,
                      "unexpected": unexpected, "unchangedSharedFunctions": result["unchangedSharedFunctions"]}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
