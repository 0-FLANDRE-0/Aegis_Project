#!/usr/bin/env python3
"""Inject one test-only lexical module into an AEGIS packed HTML."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def pack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    compressed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(compressed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    metadata = re.search(rb'const records=(\[.*?\]);', output, re.S)
    assert metadata
    rows = json.loads(metadata[1])
    rows[13].update(rawBytes=len(source.encode()), gzipBytes=len(compressed), sha256=sha(source.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    return output[:metadata.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + output[metadata.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    raw = args.base.read_bytes()
    source, match = unpack(raw)
    module = args.module.read_text()
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    assert source.count(anchor) == 1
    candidate = source.replace(anchor, module + "\n" + anchor, 1)
    assert candidate.replace(module + "\n", "", 1) == source
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    args.out.write_bytes(output)
    receipt = {
        "schema": "AEGIS_TEST_ONLY_MODULE_INJECTION_1",
        "base": str(args.base), "baseSha256": sha(raw), "baseMainSha256": sha(source.encode()),
        "module": str(args.module), "moduleSha256": sha(module.encode()),
        "output": str(args.out), "outputSha256": sha(output), "outputMainSha256": sha(candidate.encode()),
        "inverseByteExact": True, "testOnlyInstrumentation": True,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
