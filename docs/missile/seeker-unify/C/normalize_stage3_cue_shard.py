#!/usr/bin/env python3
"""Project the MAX_THREAT/EMCON-OFF CUE_A rows into the canonical 1,590 matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    docs = [json.loads(path.read_text()) for path in args.inputs]
    rows = []
    for doc in docs:
        assert doc["mode"] == "MAX_THREAT"
        for row in doc["rows"]:
            if row["setup"]["emcon"]:
                continue
            setup = {key: value for key, value in row["setup"].items() if key not in {"emcon", "threatMode"}}
            rows.append({**row, "setup": setup})
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE3_MAIN_CUE_PROJECTION_1",
        "label": "STAGE3_CUE_A_MAX_THREAT_EMCON_OFF",
        "sourceRows": sum(len(doc["rows"]) for doc in docs),
        "projectionPolicy": "MAX_THREAT_AND_EMCON_OFF; remove mode dimensions from setup only",
        "cueCases": rows,
        "pageErrors": [error for doc in docs for error in doc.get("pageErrors", [])],
        "elapsedS": 0,
    }
    assert len(rows) == 120
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"rows": len(rows), "pageErrors": len(result["pageErrors"])}))


if __name__ == "__main__":
    main()
