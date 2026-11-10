#!/usr/bin/env python3
"""Build the deterministic, HTML-free SEEKER_CLOSE_A report package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HP_A_BYTES = 22_200_135
HP_A_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def report_files() -> list[Path]:
    local = [
        path for path in HERE.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.name not in {"CHECKSUMS.sha256"}
        and path.suffix.lower() != ".zip"
    ]
    archive = [ROOT / "docs/archive" / name for name in ("DECISIONS.md", "STATUS.md", "BACKLOG.md", "ROADMAP.md")]
    return sorted({*local, *archive}, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    product = args.product.read_bytes()
    if len(product) != HP_A_BYTES or sha256(product) != HP_A_SHA256:
        raise AssertionError("authority HP_A product mismatch")

    files_before_manifest = [path for path in report_files() if path.name != "PACKAGE_MANIFEST.md"]
    rows = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path.read_bytes()),
        }
        for path in files_before_manifest
    ]
    manifest = [
        "# SEEKER_CLOSE_A package manifest",
        "",
        "- Package type: HTML-free report and reproducibility evidence",
        f"- Authority executable (not duplicated): `{args.product.name}`",
        f"- Authority bytes: `{len(product)}`",
        f"- Authority SHA-256: `{sha256(product)}`",
        "- Formal SEEKER_CLOSE_A product change: `false`",
        "- Release/tag: `false`",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
        *[f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |" for row in rows],
        "",
    ]
    (HERE / "PACKAGE_MANIFEST.md").write_text("\n".join(manifest), encoding="utf-8")

    files = report_files()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in files:
            if path.suffix.lower() in {".html", ".htm"}:
                raise AssertionError(f"HTML forbidden in report package: {path}")
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes(), compresslevel=9)

    with zipfile.ZipFile(args.output) as bundle:
        names = bundle.namelist()
        if any(name.lower().endswith((".html", ".htm")) for name in names):
            raise AssertionError("report package contains HTML")
        if len(names) != len(files):
            raise AssertionError("report package entry count mismatch")

    checksums = {
        args.product.name: {"bytes": len(product), "sha256": sha256(product), "authorityOnly": True},
        args.output.name: {"bytes": args.output.stat().st_size, "sha256": sha256(args.output.read_bytes()), "htmlFree": True},
        "evidence/limited/RESULTS.json": {
            "bytes": (HERE / "evidence/limited/RESULTS.json").stat().st_size,
            "sha256": sha256((HERE / "evidence/limited/RESULTS.json").read_bytes()),
        },
        "evidence/hp-contract/contract-gate.json": {
            "bytes": (HERE / "evidence/hp-contract/contract-gate.json").stat().st_size,
            "sha256": sha256((HERE / "evidence/hp-contract/contract-gate.json").read_bytes()),
        },
    }
    lines = [f"{row['sha256']}  {name}" for name, row in checksums.items()]
    (HERE / "CHECKSUMS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {
        "schema": "AEGIS_SEEKER_CLOSE_A_REPORT_PACKAGE_1",
        "output": args.output.name,
        "bytes": args.output.stat().st_size,
        "sha256": sha256(args.output.read_bytes()),
        "entries": len(files),
        "htmlEntries": 0,
        "authorityProduct": checksums[args.product.name],
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
