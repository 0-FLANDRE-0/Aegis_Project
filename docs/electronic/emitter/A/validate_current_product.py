#!/usr/bin/env python3
"""Fail-closed validation of the repository current-product manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
MANIFEST = REPO_ROOT / "AEGIS_CURRENT_PRODUCT.json"
EXPECTED_KEYS = {
    "schema", "stage", "path", "sha256", "bytes", "baselinePath",
    "baselineSha256", "branch", "pullRequest", "release",
}
STAGE_POLICY = {
    "EMITTER_A": {
        "branch": "emitter-a",
        "pullRequest": 73,
        "baselineSha256": "243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835",
    },
    "EMCON_B": {
        "branch": "emcon-b",
        "pullRequest": 74,
        "baselineSha256": "3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be",
    },
    "ESM_A": {
        "branch": "esm-a",
        "pullRequest": 75,
        "baselineSha256": "50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee",
    },
    "SEEKER_UNIFY_U4": {
        "branch": "seeker-unify-u4",
        "pullRequest": 76,
        "baselineSha256": "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7",
    },
    "HP_A": {
        "branch": "hp-a",
        "pullRequest": 77,
        "baselineSha256": "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498",
    },
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def repository_file(relative: object) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise AssertionError("manifest path must be a non-empty repository-relative string")
    resolved = (REPO_ROOT / relative).resolve()
    if resolved.parent != REPO_ROOT or resolved.suffix.lower() != ".html":
        raise AssertionError(f"manifest product must be a root HTML file: {relative!r}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    raw = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"non-finite JSON constant: {value}")))
    if not isinstance(manifest, dict) or set(manifest) != EXPECTED_KEYS:
        raise AssertionError("current-product manifest schema keys differ")
    if manifest["schema"] != "AEGIS_CURRENT_PRODUCT_1" or manifest["stage"] not in STAGE_POLICY:
        raise AssertionError("current-product schema or stage mismatch")
    if not isinstance(manifest["bytes"], int) or manifest["bytes"] <= 0:
        raise AssertionError("manifest bytes must be a positive integer")
    policy = STAGE_POLICY[manifest["stage"]]
    if (manifest["branch"] != policy["branch"] or manifest["pullRequest"] != policy["pullRequest"]
            or manifest["baselineSha256"] != policy["baselineSha256"] or manifest["release"] is not False):
        raise AssertionError("manifest publication metadata mismatch")
    product = repository_file(manifest["path"])
    baseline = repository_file(manifest["baselinePath"])
    checks = {
        "strictJson": True,
        "schemaExact": True,
        "stageWhitelisted": manifest["stage"] in STAGE_POLICY,
        "productExists": product.is_file(),
        "productBytesExact": product.is_file() and product.stat().st_size == manifest["bytes"],
        "productSha256Exact": product.is_file() and digest(product) == manifest["sha256"],
        "baselineExists": baseline.is_file(),
        "baselineSha256Exact": baseline.is_file() and digest(baseline) == manifest["baselineSha256"],
    }
    result = {
        "schema": "AEGIS_CURRENT_PRODUCT_VALIDATION_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "manifest": manifest,
        "checks": checks,
        "resolved": {
            "product": product.relative_to(REPO_ROOT).as_posix(),
            "baseline": baseline.relative_to(REPO_ROOT).as_posix(),
        },
    }
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
