#!/usr/bin/env python3
"""Build deterministic split delivery archives for INTEGRATION_BASELINE_A."""
from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html"
HTML_ZIP = ROOT / "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_HTML.zip"
REPORT_ZIP = ROOT / "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_REPORT.zip"
PACKAGE_SUMS = ROOT / "PACKAGE_CHECKSUMS_v48_WIP_INTEGRATION_BASELINE_A.txt"
CHECKSUMS = HERE / "CHECKSUMS.sha256"
MANIFEST = HERE / "PACKAGE_MANIFEST.md"
FIXED_TIME = (2020, 1, 1, 0, 0, 0)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def arcname(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_zip(target: Path, members: list[Path]) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(members, key=arcname):
            info = zipfile.ZipInfo(arcname(path), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def report_payload() -> list[Path]:
    roots = [
        ROOT / "README.md",
        ROOT / "AEGIS_CURRENT_PRODUCT.json",
        ROOT / "AEGIS_PLAN_STATUS_v48_WIP_INTEGRATION_BASELINE_A.md",
        ROOT / ".github/workflows/aegis-current-candidate.yml",
        ROOT / "docs/archive/STATUS.md",
        ROOT / "docs/archive/ROADMAP.md",
        ROOT / "docs/archive/BACKLOG.md",
        ROOT / "docs/archive/DECISIONS.md",
    ]
    generated = {CHECKSUMS, MANIFEST, HERE / "REMOTE_RECEIPT.json"}
    stage = [path for path in HERE.rglob("*") if path.is_file() and path not in generated]
    payload = sorted({*roots, *stage}, key=arcname)
    html = [path for path in payload if path.suffix.lower() in {".html", ".htm"}]
    if html:
        raise AssertionError(f"report payload contains HTML: {html}")
    return payload


def main() -> None:
    expected = (22_211_451, "baf96f9a1350973d045c9ad4f9025a86c10eaeda3c1924ad52498c45b90d0b5b")
    actual = (PRODUCT.stat().st_size, digest(PRODUCT))
    if actual != expected:
        raise AssertionError({"expected": expected, "actual": actual})

    payload = report_payload()
    checksum_rows = [(PRODUCT, PRODUCT.stat().st_size, digest(PRODUCT))]
    checksum_rows.extend((path, path.stat().st_size, digest(path)) for path in payload)
    CHECKSUMS.write_text("".join(f"{sha}  {arcname(path)}\n" for path, _size, sha in checksum_rows), encoding="utf-8")

    checksum_sha = digest(CHECKSUMS)
    lines = [
        "# INTEGRATION_BASELINE_A package manifest",
        "",
        "Archives are deterministic (fixed ZIP timestamp, sorted entries, deflate level 9).",
        "The HTML archive contains exactly one executable HTML. The report archive contains no HTML.",
        "`PACKAGE_MANIFEST.md` is the manifest itself and is the only intentionally self-unhashed report member.",
        "",
        "## HTML archive payload",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
        f"| `{PRODUCT.name}` | {PRODUCT.stat().st_size} | `{digest(PRODUCT)}` |",
        "",
        "## Report archive payload",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for path, size, sha in checksum_rows[1:]:
        lines.append(f"| `{arcname(path)}` | {size} | `{sha}` |")
    lines.append(f"| `{arcname(CHECKSUMS)}` | {CHECKSUMS.stat().st_size} | `{checksum_sha}` |")
    lines.extend(["", "The external package checksums are stored in `PACKAGE_CHECKSUMS_v48_WIP_INTEGRATION_BASELINE_A.txt`.", ""])
    MANIFEST.write_text("\n".join(lines), encoding="utf-8")

    write_zip(HTML_ZIP, [PRODUCT])
    report_members = [*payload, CHECKSUMS, MANIFEST]
    write_zip(REPORT_ZIP, report_members)

    with zipfile.ZipFile(HTML_ZIP) as archive:
        html_names = [name for name in archive.namelist() if name.lower().endswith((".html", ".htm"))]
        if archive.namelist() != [PRODUCT.name] or len(html_names) != 1:
            raise AssertionError("HTML archive contract failed")
    with zipfile.ZipFile(REPORT_ZIP) as archive:
        if any(name.lower().endswith((".html", ".htm")) for name in archive.namelist()):
            raise AssertionError("report archive contains HTML")

    package_rows = [PRODUCT, HTML_ZIP, REPORT_ZIP]
    PACKAGE_SUMS.write_text("".join(f"{digest(path)}  {path.name}\n" for path in package_rows), encoding="utf-8")
    print(f"html_zip={HTML_ZIP.stat().st_size} {digest(HTML_ZIP)}")
    print(f"report_zip={REPORT_ZIP.stat().st_size} {digest(REPORT_ZIP)}")
    print(f"report_members={len(report_members)}")


if __name__ == "__main__":
    main()

