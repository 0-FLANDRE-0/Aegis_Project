#!/usr/bin/env python3
"""Create a deterministic report-only ZIP for a rejected diagnostic candidate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
REPORT_ZIP = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_B_REPORT.zip"
CHECKSUMS = ROOT / "ASM_SEEKER_B_CHECKSUMS.sha256"
MANIFEST = HERE / "ARTIFACT_MANIFEST.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_entry(archive: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


doc_files = sorted(
    path for path in HERE.rglob("*")
    if path.is_file() and "__pycache__" not in path.parts and path != MANIFEST
)
manifest = {
    "schema": "AEGIS_ASM_SEEKER_B_ARTIFACT_MANIFEST_1",
    "product": None,
    "productReason": "No B product was generated because the prescribed shadow candidate failed its primary surface-target gate.",
    "baseline": {
        "path": "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html",
        "sha256": "9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f"
    },
    "reportFiles": [
        {"path": str(path.relative_to(HERE)), "bytes": path.stat().st_size, "sha256": sha(path)}
        for path in doc_files
    ]
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
doc_files = sorted(doc_files + [MANIFEST])

with ZipFile(REPORT_ZIP, "w") as archive:
    for path in doc_files:
        write_entry(archive, str(Path("ASM_SEEKER_B_REPORT") / path.relative_to(HERE)), path.read_bytes())

artifacts = [REPORT_ZIP, HERE / "REPORT.md", HERE / "VALIDATION.json"]
CHECKSUMS.write_text("".join(f"{sha(path)}  {path.relative_to(ROOT)}\n" for path in artifacts))
print(json.dumps({
    "reportZip": {"path": REPORT_ZIP.name, "bytes": REPORT_ZIP.stat().st_size, "sha256": sha(REPORT_ZIP)},
    "checksums": CHECKSUMS.name
}, indent=2))
