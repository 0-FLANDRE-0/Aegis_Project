#!/usr/bin/env python3
"""Build the deterministic SEEKER_UNIFY_A report bundle and delivery receipt."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
PRODUCT_ZIP = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A_HTML.zip"
ARCHIVE = ROOT / "AEGIS_SEEKER_UNIFY_A_REPORT.zip"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_files() -> list[Path]:
    root_names = {
        "REPORT.md", "VALIDATION.json", "BUILD.json", "PRODUCT_BUILD.json", "SCOPE.json",
        "STATIC_SCOPE_AUDIT.json", "changes.diff", "PLAN.md", "RCS_SOURCES.md",
        "RCS_INVENTORY.json", "RCS_AUDIT.md", "RCS_EFFECTIVE_ASPECTS.md", "RANGE_REDIAGNOSIS.md",
        "RANGE_REDIAGNOSIS.json", "RADAR_PATH_RESULTS.md", "RADAR_PATH_RESULTS.json",
        "APPROVED_EXPECTATION_DELTAS.json", "REGRESSION_RESULTS.json",
        "REGRESSION_RESULTS_RAW.json", "S3_BATTLE_RESULTS.json", "BATTLE_FIXTURE_PROVENANCE.json", "UNIFY_AUDIT.md",
        "UNIFY_DESIGN.md", "PROFILE_MIGRATION_TABLE.json", "BASELINE_DIAGNOSTICS.json",
        "PRODUCT_DIAGNOSTICS.json", "BASELINE_MANAGED_RADAR.json", "PRODUCT_MANAGED_RADAR.json",
        "BASELINE_NPC_RADAR.json", "PRODUCT_NPC_RADAR.json",
        "DIAGNOSTIC_PRODUCT_V4_BUILD.json",
    }
    files = [P / name for name in sorted(root_names)]
    evidence_names = {
        "native.json", "classes.json", "clock.json", "ui.json", "ui-clock.json",
        "casualty.json", "deployment.json", "visual.json", "observed-world.json",
        "baseline-comparison.json", "source-provenance.json", "shard-0.json", "shard-1.json",
    }
    for path in (P / "evidence").rglob("*"):
        if path.is_file() and path.name in evidence_names:
            files.append(path)
    scripts = [path for path in P.glob("*.py") if path.name != Path(__file__).name]
    files.extend(scripts)
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(missing)
    return sorted(set(files), key=lambda path: str(path.relative_to(ROOT)))


def main() -> None:
    validation = json.loads((P / "VALIDATION.json").read_text())
    if validation["status"] != "PASS":
        raise SystemExit("Refusing to package a non-PASS validation")
    files = selected_files()
    manifest = {
        "schema": "AEGIS_SEEKER_UNIFY_A_ARTIFACT_MANIFEST_1",
        "product": {
            "path": PRODUCT.name,
            "sha256": sha(PRODUCT),
            "bytes": PRODUCT.stat().st_size,
        },
        "reportFiles": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha(path),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }
    manifest_path = P / "ARTIFACT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    files.append(manifest_path)
    sums = "".join(f"{sha(path)}  {path.relative_to(ROOT)}\n" for path in files)
    with zipfile.ZipFile(PRODUCT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        info = zipfile.ZipInfo(PRODUCT.name)
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, PRODUCT.read_bytes())
        info = zipfile.ZipInfo("SHA256SUMS.txt")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, f"{sha(PRODUCT)}  {PRODUCT.name}\n".encode())
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files, key=lambda value: str(value.relative_to(ROOT))):
            info = zipfile.ZipInfo("SEEKER_UNIFY_A/" + str(path.relative_to(ROOT)))
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
        info = zipfile.ZipInfo("SEEKER_UNIFY_A/SHA256SUMS.txt")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, sums.encode())
    delivery = {
        "schema": "AEGIS_SEEKER_UNIFY_A_DELIVERY_1",
        "product": manifest["product"],
        "productZip": {
            "path": PRODUCT_ZIP.name,
            "sha256": sha(PRODUCT_ZIP),
            "bytes": PRODUCT_ZIP.stat().st_size,
        },
        "reportZip": {
            "path": ARCHIVE.name,
            "sha256": sha(ARCHIVE),
            "bytes": ARCHIVE.stat().st_size,
        },
        "releaseOrTag": False,
    }
    (P / "DELIVERY.json").write_text(json.dumps(delivery, indent=2) + "\n")
    print(json.dumps(delivery))


if __name__ == "__main__":
    main()
