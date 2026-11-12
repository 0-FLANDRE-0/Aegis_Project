#!/usr/bin/env python3
"""Validate deterministic archive shape and manifest bytes/SHA after extraction."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

from package_artifacts import FIXED_TIME, report_member_allowed


ROW = re.compile(r"^\| `([^`]+)` \| (\d+) \| `([0-9a-f]{64})` \|$")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("html_zip", type=Path)
    parser.add_argument("report_zip", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    first_archives = {path.name: {"bytes": path.stat().st_size, "sha256": digest(path.read_bytes())} for path in (args.html_zip, args.report_zip)}
    subprocess.run([sys.executable, str(Path(__file__).with_name("package_artifacts.py"))], check=True)
    second_archives = {path.name: {"bytes": path.stat().st_size, "sha256": digest(path.read_bytes())} for path in (args.html_zip, args.report_zip)}
    manifest_text = args.manifest.read_text()
    rows = {match.group(1): {"bytes": int(match.group(2)), "sha256": match.group(3)} for line in manifest_text.splitlines() if (match := ROW.match(line))}
    checks = {}
    checks["deterministicSecondBuild"] = first_archives == second_archives
    archive_rows = {}
    with tempfile.TemporaryDirectory(prefix="aegis-integration-package-") as tmp:
        temp = Path(tmp)
        for kind, path in (("html", args.html_zip), ("report", args.report_zip)):
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist();checks[kind+"ZipCrc"] = archive.testzip() is None
                checks[kind+"SortedUnique"] = names == sorted(set(names))
                checks[kind+"FixedTimestamps"] = all(info.date_time == FIXED_TIME for info in archive.infolist())
                target = temp / kind;archive.extractall(target)
                archive_rows[kind] = {name: {"bytes": (target/name).stat().st_size, "sha256": digest((target/name).read_bytes())} for name in names}
    html_names = list(archive_rows["html"]);report_names = list(archive_rows["report"])
    checks["htmlExactlyOneProduct"] = html_names == [args.product.name]
    checks["htmlPayloadExact"] = archive_rows["html"].get(args.product.name) == {"bytes": args.product.stat().st_size, "sha256": digest(args.product.read_bytes())}
    checks["reportHtmlZero"] = not any(name.lower().endswith((".html", ".htm")) for name in report_names)
    checks["reportExcludedByproductsZero"] = all(report_member_allowed(Path(name)) for name in report_names)
    report_rows = {name: row for name, row in rows.items() if name != args.product.name}
    root = Path(__file__).resolve().parents[4]
    expected_report = sorted([*report_rows, args.manifest.resolve().relative_to(root).as_posix()])
    checks["reportManifestListExact"] = report_names == expected_report
    checks["reportManifestBytesShaExact"] = all(archive_rows["report"].get(name) == row for name, row in report_rows.items())
    synthetic = [Path("x/__pycache__/a.py"),Path("x/a.pyc"),Path("x/a.pyo"),Path("x/.DS_Store"),Path("x/a.swp"),Path("x/a.swo"),Path("x/a~"),Path("x/a.tmp")]
    checks["syntheticExclusionRules"] = all(not report_member_allowed(path) for path in synthetic) and all(report_member_allowed(Path("x")/name) for name in ("a.json","a.md","a.log","fixture.py"))
    failed = [name for name, value in checks.items() if not value]
    payload = {"schema":"AEGIS_INTEGRATION_BASELINE_PACKAGE_CONTRACT_A_2","checks":checks,"firstArchives":first_archives,"secondArchives":second_archives,"htmlMembers":html_names,"reportMemberCount":len(report_names),"failed":failed,"status":"PASS" if not failed else "FAIL"}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":payload["status"],"htmlMembers":len(html_names),"reportMembers":len(report_names),"failed":failed}))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()
