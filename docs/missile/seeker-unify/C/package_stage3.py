#!/usr/bin/env python3
"""Build deterministic, directly downloadable Stage-3 delivery ZIPs."""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DOWNLOADS = ROOT / "downloads"
HTML = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
HTML_ZIP = DOWNLOADS / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C_HTML.zip"
REPORT_ZIP = DOWNLOADS / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C_REPORT.zip"
CHECKSUMS = DOWNLOADS / "SEEKER_UNIFY_C_SHA256SUMS.txt"
MANIFEST = HERE / "REPORT_MANIFEST_SHA256.txt"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files() -> list[Path]:
    return sorted(
        path for path in HERE.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path != MANIFEST
    )


def add(zf: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    info = zipfile.ZipInfo(archive_name, (1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    report_files = files()
    MANIFEST.write_text("".join(
        f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in report_files
    ))
    report_files = files() + [MANIFEST]

    with zipfile.ZipFile(HTML_ZIP, "w") as zf:
        add(zf, HTML, HTML.name)
    with zipfile.ZipFile(REPORT_ZIP, "w") as zf:
        for path in sorted(report_files):
            add(zf, path, path.relative_to(ROOT).as_posix())

    with zipfile.ZipFile(HTML_ZIP) as zf:
        assert zf.namelist() == [HTML.name]
        assert zf.testzip() is None
        assert hashlib.sha256(zf.read(HTML.name)).hexdigest() == sha(HTML)
    with zipfile.ZipFile(REPORT_ZIP) as zf:
        assert zf.testzip() is None
        assert not any(name.lower().endswith(".html") for name in zf.namelist())
        assert f"docs/missile/seeker-unify/C/{MANIFEST.name}" in zf.namelist()

    checksum_paths = [HTML, HTML_ZIP, REPORT_ZIP, HERE / "REPORT.md", HERE / "CUE_A_FINAL_RESULTS.json"]
    CHECKSUMS.write_text("".join(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in checksum_paths))
    print(f"HTML_SHA256={sha(HTML)}")
    print(f"HTML_ZIP_SHA256={sha(HTML_ZIP)}")
    print(f"REPORT_ZIP_SHA256={sha(REPORT_ZIP)}")
    print(f"REPORT_FILES={len(report_files)}")


if __name__ == "__main__":
    main()
