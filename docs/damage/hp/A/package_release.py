#!/usr/bin/env python3
"""Create deterministic, separate HP_A executable and evidence packages."""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_HP_A.html"
HTML_ZIP = ROOT / "Aegis_SIM_v48_WIP_HP_A_HTML.zip"
REPORT_ZIP = ROOT / "Aegis_SIM_v48_WIP_HP_A_REPORT.zip"
CHECKSUMS = ROOT / "PACKAGE_CHECKSUMS_v48_WIP_HP_A.txt"
FIXED_TIME = (2026, 11, 9, 0, 0, 0)

ROOT_REPORT_FILES = (
    ROOT / "AEGIS_CURRENT_PRODUCT.json",
    ROOT / "AEGIS_PLAN_STATUS_v48_WIP_HP_A.md",
    ROOT / "AEGIS_PROJECT_INSTRUCTIONS.md",
    ROOT / "README.md",
    ROOT / ".github/workflows/aegis-current-candidate.yml",
    ROOT / "docs/electronic/emitter/A/validate_current_product.py",
    ROOT / "docs/archive/BACKLOG.md",
    ROOT / "docs/archive/DECISIONS.md",
    ROOT / "docs/archive/ROADMAP.md",
    ROOT / "docs/archive/STATUS.md",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def report_files() -> list[Path]:
    files = list(ROOT_REPORT_FILES)
    for path in HERE.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.suffix.lower() == ".html":
            continue
        files.append(path)
    unique = {path.resolve(): path for path in files}
    return sorted(unique.values(), key=lambda path: path.relative_to(ROOT).as_posix())


def build() -> None:
    raw = PRODUCT.read_bytes()
    if len(raw) != 22_200_135 or hashlib.sha256(raw).hexdigest() != "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa":
        raise AssertionError("HP_A frozen product identity differs")

    with zipfile.ZipFile(HTML_ZIP, "w") as archive:
        add_bytes(archive, PRODUCT.name, raw)

    selected = report_files()
    if any(path.suffix.lower() == ".html" for path in selected):
        raise AssertionError("report package selection contains HTML")
    with zipfile.ZipFile(REPORT_ZIP, "w") as archive:
        for path in selected:
            add_bytes(archive, path.relative_to(ROOT).as_posix(), path.read_bytes())

    lines = [
        "# HP_A detached package checksums",
        "# bytes  sha256  path",
    ]
    for path in (PRODUCT, HTML_ZIP, REPORT_ZIP, ROOT / "AEGIS_CURRENT_PRODUCT.json", HERE / "FINAL_REPORT.md", HERE / "PACKAGE_MANIFEST.md"):
        lines.append(f"{path.stat().st_size}  {digest(path)}  {path.relative_to(ROOT).as_posix()}")
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with zipfile.ZipFile(HTML_ZIP) as archive:
        if archive.namelist() != [PRODUCT.name]:
            raise AssertionError("executable package membership differs")
    with zipfile.ZipFile(REPORT_ZIP) as archive:
        if any(name.lower().endswith(".html") for name in archive.namelist()):
            raise AssertionError("report package contains HTML")
    print(CHECKSUMS.read_text(), end="")


if __name__ == "__main__":
    build()
