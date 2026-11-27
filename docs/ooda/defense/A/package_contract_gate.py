#!/usr/bin/env python3
"""Validate deterministic DEFENSE_OODA_A archive shape and member hashes."""
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

    archives = (args.html_zip, args.report_zip)
    first = {path.name: {"bytes": path.stat().st_size, "sha256": digest(path.read_bytes())} for path in archives}
    subprocess.run([sys.executable, str(Path(__file__).with_name("package_artifacts.py"))], check=True)
    second = {path.name: {"bytes": path.stat().st_size, "sha256": digest(path.read_bytes())} for path in archives}
    rows = {
        match.group(1): {"bytes": int(match.group(2)), "sha256": match.group(3)}
        for line in args.manifest.read_text(encoding="utf-8").splitlines()
        if (match := ROW.match(line))
    }

    checks: dict[str, bool] = {"deterministicSecondBuild": first == second}
    extracted: dict[str, dict[str, dict[str, object]]] = {}
    with tempfile.TemporaryDirectory(prefix="aegis-defense-ooda-package-") as temporary:
        root = Path(temporary)
        for kind, path in (("html", args.html_zip), ("report", args.report_zip)):
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                checks[kind + "ZipCrc"] = archive.testzip() is None
                checks[kind + "SortedUnique"] = names == sorted(set(names))
                checks[kind + "FixedTimestamps"] = all(info.date_time == FIXED_TIME for info in archive.infolist())
                target = root / kind
                archive.extractall(target)
                extracted[kind] = {
                    name: {
                        "bytes": (target / name).stat().st_size,
                        "sha256": digest((target / name).read_bytes()),
                    }
                    for name in names
                }

    html_names = list(extracted["html"])
    report_names = list(extracted["report"])
    checks["htmlExactlyOneProduct"] = html_names == [args.product.name]
    checks["htmlPayloadExact"] = extracted["html"].get(args.product.name) == {
        "bytes": args.product.stat().st_size,
        "sha256": digest(args.product.read_bytes()),
    }
    checks["reportHtmlZero"] = not any(name.lower().endswith((".html", ".htm")) for name in report_names)
    checks["reportExcludedByproductsZero"] = all(report_member_allowed(Path(name)) for name in report_names)

    report_rows = {name: row for name, row in rows.items() if name != args.product.name}
    repository = Path(__file__).resolve().parents[4]
    manifest_name = args.manifest.resolve().relative_to(repository).as_posix()
    checks["reportManifestListExact"] = report_names == sorted([*report_rows, manifest_name])
    checks["reportManifestBytesShaExact"] = all(extracted["report"].get(name) == row for name, row in report_rows.items())

    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_PACKAGE_CONTRACT_1",
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "firstArchives": first,
        "secondArchives": second,
        "htmlMembers": html_names,
        "reportMemberCount": len(report_names),
        "failed": failed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": checks, "failed": failed}))
    raise SystemExit(0 if not failed else 1)


if __name__ == "__main__":
    main()

