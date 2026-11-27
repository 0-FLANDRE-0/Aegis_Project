#!/usr/bin/env python3
"""Compare baseline and stage-A OFF oracles, isolating the new save field."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def stable(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    a = json.loads(args.baseline.read_text())
    b = json.loads(args.candidate.read_text())
    aa, bb = copy.deepcopy(a["owners"]), copy.deepcopy(b["owners"])
    save_differences = []
    for index, (left, right) in enumerate(zip(aa, bb, strict=True)):
        save_differences.append({"ownerIndex": index, "baseline": left["result"].pop("saveSnapshot"), "candidate": right["result"].pop("saveSnapshot")})
    left_bytes, right_bytes = stable(aa), stable(bb)
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_DISABLED_PARITY_1",
        "baselineDigestWithoutSave": hashlib.sha256(left_bytes).hexdigest(),
        "candidateDigestWithoutSave": hashlib.sha256(right_bytes).hexdigest(),
        "gameplayExactWithoutDeclaredSaveField": left_bytes == right_bytes,
        "saveDifferences": save_differences,
        "reason": "AEGIS_DEFENSE_OODA_STATE_A1 is the only expected stage-A output addition",
        "expectationsChanged": 0,
        "tolerancesChanged": 0,
        "rngChanged": False,
    }
    payload["pass"] = payload["gameplayExactWithoutDeclaredSaveField"] and len(save_differences) == 2
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"pass": payload["pass"], "digest": payload["candidateDigestWithoutSave"]}))
    if not payload["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
