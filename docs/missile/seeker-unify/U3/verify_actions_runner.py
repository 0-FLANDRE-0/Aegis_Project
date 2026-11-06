#!/usr/bin/env python3
"""Verify the Playwright 1.55 jobs use an Ubuntu release it supports."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    text = args.workflow.read_text()
    yaml.safe_load(text)
    jobs_anchor = re.search(r"^jobs:\s*$", text, re.M)
    if not jobs_anchor:
        raise AssertionError("jobs mapping missing")
    tail = text[jobs_anchor.end() :]
    headers = list(re.finditer(r"^  ([A-Za-z0-9_-]+):\s*$", tail, re.M))
    rows = []
    for index, match in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(tail)
        body = tail[match.end() : end]
        runner_match = re.search(r"^    runs-on:\s*([^\s#]+)", body, re.M)
        if not runner_match:
            continue
        rows.append(
            {
                "job": match.group(1),
                "runner": runner_match.group(1),
                "usesPlaywrightInstall": "npx playwright install" in body,
            }
        )
    playwright = [row for row in rows if row["usesPlaywrightInstall"]]
    non_playwright = [row for row in rows if not row["usesPlaywrightInstall"]]
    checks = {
        "yamlParses": True,
        "expectedPlaywrightJobCount": len(playwright) == 22,
        "allPlaywrightJobsPinned": all(row["runner"] == "ubuntu-24.04" for row in playwright),
        "nonPlaywrightJobsNotMassPinned": all(row["runner"] == "ubuntu-latest" for row in non_playwright),
        "noUbuntu2604": "ubuntu-26.04" not in text,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_ACTIONS_RUNNER_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "cause": "ubuntu-latest resolved ubuntu-26.04, unsupported by Playwright 1.55 Chromium dependency installer",
        "resolution": "Pin only jobs invoking npx playwright install to ubuntu-24.04",
        "checks": checks,
        "playwrightJobs": playwright,
        "nonPlaywrightJobs": non_playwright,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
