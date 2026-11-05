#!/usr/bin/env python3
"""Create the separated execution and evidence deliveries for CUE_A-1."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1.html"
STATUS = ROOT / "AEGIS_PLAN_STATUS_v48_WIP_CUE_A_1.md"
EXECUTION = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1_EXECUTION.zip"
REPORT = ROOT / "Aegis_SIM_v48_WIP_CUE_A_1_REPORT.zip"
CHECKSUMS = ROOT / "SHA256SUMS_v48_WIP_CUE_A_1.txt"
MANIFEST = HERE / "DELIVERY_MANIFEST.json"
EXPECTED_PRODUCT_SHA = "0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert PRODUCT.is_file() and sha(PRODUCT) == EXPECTED_PRODUCT_SHA
assert STATUS.is_file()

for path in (EXECUTION, REPORT):
    path.unlink(missing_ok=True)

with zipfile.ZipFile(EXECUTION, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    archive.write(PRODUCT, PRODUCT.name)

report_members = [
    ROOT / "AEGIS_PROJECT_INSTRUCTIONS.md",
    STATUS,
]
for path in sorted(HERE.rglob("*")):
    if not path.is_file():
        continue
    if "__pycache__" in path.parts or path.suffix in (".pyc", ".zip"):
        continue
    if path == MANIFEST:
        continue
    report_members.append(path)

entries = []
for path in report_members:
    relative = path.relative_to(ROOT).as_posix()
    entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})

manifest = {
    "schema": "AEGIS_CUE_A_1_DELIVERY_MANIFEST_1",
    "product": {
        "path": PRODUCT.name,
        "bytes": PRODUCT.stat().st_size,
        "sha256": sha(PRODUCT),
        "includedInReportZip": False,
    },
    "executionZip": {
        "path": EXECUTION.name,
        "bytes": EXECUTION.stat().st_size,
        "sha256": sha(EXECUTION),
        "members": [PRODUCT.name],
    },
    "reportZipPolicy": {
        "htmlMembers": 0,
        "manifestSelfHashExcluded": True,
        "membersBelow": len(entries) + 1,
    },
    "reportMembers": entries,
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

with zipfile.ZipFile(REPORT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in report_members + [MANIFEST]:
        archive.write(path, path.relative_to(ROOT).as_posix())

checksummed = [PRODUCT, STATUS, EXECUTION, REPORT]
CHECKSUMS.write_text("".join(f"{sha(path)}  {path.name}\n" for path in checksummed))

with zipfile.ZipFile(EXECUTION) as archive:
    assert archive.testzip() is None
    assert archive.namelist() == [PRODUCT.name]
    assert hashlib.sha256(archive.read(PRODUCT.name)).hexdigest() == EXPECTED_PRODUCT_SHA
with zipfile.ZipFile(REPORT) as archive:
    assert archive.testzip() is None
    assert not any(name.lower().endswith(".html") for name in archive.namelist())
    assert "docs/missile/cue-a-1/DELIVERY_MANIFEST.json" in archive.namelist()

print(
    json.dumps(
        {
            "execution": {"bytes": EXECUTION.stat().st_size, "sha256": sha(EXECUTION)},
            "report": {"bytes": REPORT.stat().st_size, "sha256": sha(REPORT)},
            "reportMembers": len(entries) + 1,
            "checksums": CHECKSUMS.name,
        },
        indent=2,
    )
)
