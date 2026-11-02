#!/usr/bin/env python3
"""Create deterministic user-download and report ZIP artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
PRODUCT_ZIP = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A_DOWNLOAD.zip"
REPORT_ZIP = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A_REPORT.zip"
CHECKSUMS = ROOT / "ASM_SEEKER_A_CHECKSUMS.sha256"
MANIFEST = HERE / "ARTIFACT_MANIFEST.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_entry(archive: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


doc_files = sorted(
    p for p in HERE.rglob("*")
    if p.is_file() and "__pycache__" not in p.parts and p != MANIFEST
)
manifest = {
    "schema": "AEGIS_ASM_SEEKER_A_ARTIFACT_MANIFEST_1",
    "product": {"path": PRODUCT.name, "bytes": PRODUCT.stat().st_size, "sha256": sha(PRODUCT)},
    "reportFiles": [
        {"path": str(p.relative_to(HERE)), "bytes": p.stat().st_size, "sha256": sha(p)}
        for p in doc_files
    ],
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
doc_files.append(MANIFEST)
doc_files.sort()

with ZipFile(PRODUCT_ZIP, "w") as archive:
    write_entry(archive, PRODUCT.name, PRODUCT.read_bytes())
    write_entry(archive, "SHA256SUMS.txt", f"{sha(PRODUCT)}  {PRODUCT.name}\n".encode())

with ZipFile(REPORT_ZIP, "w") as archive:
    for path in doc_files:
        write_entry(archive, str(Path("ASM_SEEKER_A_REPORT") / path.relative_to(HERE)), path.read_bytes())

artifacts = [PRODUCT, PRODUCT_ZIP, REPORT_ZIP, HERE / "REPORT.md", HERE / "VALIDATION.json", HERE / "changes.diff"]
CHECKSUMS.write_text("".join(f"{sha(path)}  {path.relative_to(ROOT)}\n" for path in artifacts))
print(json.dumps({
    "productZip": {"path": PRODUCT_ZIP.name, "bytes": PRODUCT_ZIP.stat().st_size, "sha256": sha(PRODUCT_ZIP)},
    "reportZip": {"path": REPORT_ZIP.name, "bytes": REPORT_ZIP.stat().st_size, "sha256": sha(REPORT_ZIP)},
    "checksums": CHECKSUMS.name,
}, indent=2))
