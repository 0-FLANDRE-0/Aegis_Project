#!/usr/bin/env python3
"""Preserve permissive WebGL raw evidence and emit strict-JSON report copies."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGETS = (
    HERE / "evidence/final-regression/webgl8/observed-world.json",
    HERE / "evidence/final-regression/webgl8/observed-world-progress.json",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> None:
    rows = []
    token = re.compile(r"(?<![A-Za-z0-9_\"])(-Infinity|Infinity|NaN)(?![A-Za-z0-9_\"])")
    for path in TARGETS:
        original = path.read_bytes()
        raw_path = path.with_suffix(path.suffix + ".raw.txt")
        raw_path.write_bytes(original)
        text = original.decode()
        counts = {
            "-Infinity": text.count("-Infinity"),
            "Infinity": len(re.findall(r"(?<![-A-Za-z0-9_\"])Infinity(?![A-Za-z0-9_\"])", text)),
            "NaN": len(re.findall(r"(?<![A-Za-z0-9_\"])NaN(?![A-Za-z0-9_\"])", text)),
        }
        normalized = token.sub("null", text).encode()
        parsed = json.loads(normalized.decode(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        path.write_text(json.dumps(parsed, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
        rows.append({"path": str(path.relative_to(HERE)), "rawPath": str(raw_path.relative_to(HERE)),
                     "rawSha256": sha(original), "strictSha256": sha(path.read_bytes()),
                     "rawBytes": len(original), "strictBytes": path.stat().st_size,
                     "replacements": counts, "replacement": "NONFINITE_DIAGNOSTIC_SENTINEL_TO_JSON_NULL"})
    receipt = {"schema": "AEGIS_EMITTER_A_STRICT_JSON_NORMALIZATION_1",
               "reason": "Inherited WebGL evidence serializer emitted JavaScript non-finite literals; raw bytes retained verbatim.",
               "gameOrTestOutcomeChanged": False, "rows": rows}
    (HERE / "STRICT_JSON_NORMALIZATION.json").write_text(strict(receipt))
    print(strict(receipt))


if __name__ == "__main__":
    main()
