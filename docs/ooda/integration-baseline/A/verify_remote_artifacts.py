#!/usr/bin/env python3
"""Read back published branch artifacts and compare complete bytes/SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FILES = [
    "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html",
    "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_HTML.zip",
    "Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A_REPORT.zip",
]


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions-run", required=True, type=int)
    parser.add_argument("--actions-conclusion", default="SUCCESS")
    parser.add_argument("--branch", default="integration-baseline-a")
    args = parser.parse_args()
    rows = []
    for name in FILES:
        local = (ROOT / name).read_bytes()
        url = f"https://raw.githubusercontent.com/0-FLANDRE-0/Aegis_Project/{args.branch}/{name}"
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "AEGIS-INTEGRATION-READBACK"})
        with urllib.request.urlopen(request, timeout=120) as response:
            remote = response.read()
        rows.append({
            "path": name,
            "url": url,
            "localBytes": len(local),
            "remoteBytes": len(remote),
            "localSha256": sha256(local),
            "remoteSha256": sha256(remote),
            "exact": local == remote,
        })
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    payload = {
        "schema": "AEGIS_INTEGRATION_BASELINE_A_REMOTE_RECEIPT_1",
        "repository": "0-FLANDRE-0/Aegis_Project",
        "branch": args.branch,
        "headBeforeReceipt": head,
        "pullRequest": 79,
        "actionsRun": args.actions_run,
        "actionsConclusion": args.actions_conclusion,
        "artifacts": rows,
        "allExact": all(row["exact"] for row in rows),
        "merged": False,
        "release": False,
    }
    (HERE / "REMOTE_RECEIPT.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    raise SystemExit(0 if payload["allExact"] else 1)


if __name__ == "__main__":
    main()

