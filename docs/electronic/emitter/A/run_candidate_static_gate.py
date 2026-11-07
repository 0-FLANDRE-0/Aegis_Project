#!/usr/bin/env python3
"""Static/current-artifact gate for the manifest-selected EMITTER_A candidate."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
MANIFEST = REPO_ROOT / "AEGIS_CURRENT_PRODUCT.json"
PORTABLE_SCRIPTS = (
    "run_baseline_audit.py", "run_stage_b_gate.py", "run_stage_c_gate.py",
    "run_stage_d_gate.py", "run_final_limited_gate.py", "run_performance.py",
    "run_final_regression.py", "run_closure_call_gate.py",
)
FORBIDDEN_PATHS = (
    "/workspace/aegis-ui-a", "/workspace/aegis-asm-seeker-a",
    "/workspace/aegis-performance-c", "/workspace/aegis-seeker-unify-u3",
)


def strict_load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda value: (
        _ for _ in ()).throw(ValueError(f"{path}: non-finite JSON constant {value}")))


def extract_main(path: Path) -> str:
    body = path.read_bytes()
    match = re.search(rb'data-c55-index="13">([^<]+)', body)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match[1])).decode("utf-8")


def function_source(source: str, name: str) -> str:
    match = re.search(rf"function\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise AssertionError(f"function missing: {name}")
    brace = source.find("{", match.end())
    depth, quote, escaped = 0, None, False
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
                return source[match.start():index + 1]
    raise AssertionError(f"unterminated function: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--main-out", type=Path, required=True)
    args = parser.parse_args()
    manifest = strict_load(MANIFEST)
    product = REPO_ROOT / manifest["path"]
    source = extract_main(product)
    args.main_out.parent.mkdir(parents=True, exist_ok=True)
    args.main_out.write_text(source, encoding="utf-8")
    resolver = function_source(source, "electronicPhysicalEmittersF")
    shadow_index = resolver.find("SHIP_EMITTER_MODE_A==='SHADOW'")
    legacy_index = resolver.find("electronicShipPhysicalEmittersLegacyA(r)")
    strict_json_files = sorted((HERE).rglob("*.json"))
    strict_failures = []
    for path in strict_json_files:
        try:
            strict_load(path)
        except Exception as error:  # fail-closed evidence audit
            strict_failures.append({"path": str(path.relative_to(REPO_ROOT)), "error": str(error)})
    path_hits = {
        name: [marker for marker in FORBIDDEN_PATHS if marker in (HERE / name).read_text(encoding="utf-8")]
        for name in PORTABLE_SCRIPTS
    }
    scope = strict_load(HERE / "SCOPE_D.json")
    performance = strict_load(HERE / "PERFORMANCE.json")
    performance_build = strict_load(HERE / "BUILD_PERF_FINAL.json")
    candidate_workflow = (REPO_ROOT / ".github/workflows/aegis-current-candidate.yml").read_text(encoding="utf-8")
    legacy_workflow = (REPO_ROOT / ".github/workflows/aegis-smoke.yml").read_text(encoding="utf-8")
    checks = {
        "manifestProductShaExact": hashlib.sha256(product.read_bytes()).hexdigest() == manifest["sha256"],
        "activeModeEmbedded": "const SHIP_EMITTER_MODE_A='ACTIVE';" in source,
        "legacyCallOnlyInsideShadowBranch": resolver.count("electronicShipPhysicalEmittersLegacyA(r)") == 1 and 0 <= shadow_index < legacy_index,
        "declaredCallPresentInShadowAndActive": resolver.count("electronicShipPhysicalEmittersDeclaredA(r)") == 2 and
            "else out.push(...electronicShipPhysicalEmittersDeclaredA(r))" in resolver,
        "airMissileNulkaTailsPresent": all(marker in resolver for marker in ("targetPool", "enemyMissiles", "nulkaEntities15B")),
        "deterministicBuildScopePass": scope["status"] == "PASS" and scope["scopeProof"]["deterministicTransformExact"],
        "protectedFunctionsExact": all(row["identical"] for row in scope["protected"].values()),
        "strictJson": not strict_failures,
        "portableScriptsNoForbiddenCheckout": all(not hits for hits in path_hits.values()),
        "performanceEvidenceCurrent": performance["status"] == "PASS" and
            performance_build["baseSha256"] == manifest["sha256"] and
            performance["inputs"]["activeSha256"] == performance_build["outputSha256"],
        "candidateWorkflowManifestAuthority": "AEGIS_CURRENT_PRODUCT.json" in candidate_workflow and
            "find . -maxdepth" not in candidate_workflow and manifest["path"] not in candidate_workflow,
        "candidateWorkflowSingleJob": candidate_workflow.count("  current-candidate-gate:") == 1 and
            candidate_workflow.count("\n  current-candidate-gate:") == 1,
        "legacyWorkflowSeparated": legacy_workflow.startswith("name: AEGIS legacy regression matrix\n") and
            "'Aegis_SIM_v*.html'" not in legacy_workflow,
        "legacyNoCandidateGuessing": "find . -maxdepth 1 -type f -name 'Aegis_SIM_v*.html'" not in legacy_workflow and
            "LEGACY_STATIC_SIM_FILE" in legacy_workflow,
    }
    result = {
        "schema": "AEGIS_CURRENT_CANDIDATE_STATIC_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "product": manifest,
        "mainSha256": hashlib.sha256(source.encode()).hexdigest(),
        "checks": checks,
        "strictJsonFiles": len(strict_json_files),
        "strictJsonFailures": strict_failures,
        "portablePathAudit": path_hits,
        "workflowAudit": {
            "candidate": ".github/workflows/aegis-current-candidate.yml",
            "legacy": ".github/workflows/aegis-smoke.yml",
            "candidateProductNameDuplicated": manifest["path"] in candidate_workflow,
        },
    }
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
