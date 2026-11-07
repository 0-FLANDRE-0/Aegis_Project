#!/usr/bin/env python3
"""Build EMITTER_A stages reproducibly from the pinned U3 product."""
from __future__ import annotations

import argparse
import base64
import difflib
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
BASE_SHA = "243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf"function\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise AssertionError(f"function missing: {name}")
    paren = source.find("(", match.start())
    depth = 0
    quote = None
    escaped = False
    close = -1
    for index in range(paren, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                close = index
                break
    brace = source.find("{", close + 1)
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return match.start(), index + 1
    raise AssertionError(f"unterminated function: {name}")


def transform(source: str, *, stage: str, mode: str) -> str:
    registry = (HERE / "emitter_registry.js").read_text().rstrip() + "\n"
    source = one(source, "function wip13c51RegisterProfile(p){", registry + "function wip13c51RegisterProfile(p){", "registry module")
    source = one(
        source,
        " p15.revision='V48_WIP15B_NULKA_RELOAD'; // Explicit old operational snapshot rejection; no silent ammo padding.\n return p15;",
        " p15.equipment={...(p15.equipment??{}),registryId:'AEGIS_DDG119_EQUIPMENT_EMITTER_A',emitters:shipEmitterEquipmentRegistryA('DDG_119_LATE_FLIGHT_IIA')};\n p15.revision='V48_WIP15B_NULKA_RELOAD'; // Explicit old operational snapshot rejection; no silent ammo padding.\n return p15;",
        "DDG emitter registry",
    )
    source = one(
        source,
        "      secondaryRadars:R.radars,ew:{moduleId:E.SLQ32_CG52_LATE_V1.id,pods:R.ewPods},",
        "      secondaryRadars:R.radars,emitters:shipEmitterEquipmentRegistryA('CG_52_LATE_TICONDEROGA'),ew:{moduleId:E.SLQ32_CG52_LATE_V1.id,pods:R.ewPods},",
        "CG emitter registry",
    )
    if stage == "D":
        source = one(
            source,
            " p.equipment={registryId:'SOV_INACTIVE_ONLY_A',guns:[],closeIn:[],illuminators:[],secondaryRadars:[],ew:{pods:[],installed:false},inactiveHardpoints:R.inactiveHardpoints,sensorRegistration:R.sensorRegistration};",
            " p.equipment={registryId:'SOV_INACTIVE_ONLY_A',guns:[],closeIn:[],illuminators:[],secondaryRadars:[],ew:{pods:[],installed:false},inactiveHardpoints:R.inactiveHardpoints,sensorRegistration:R.sensorRegistration,emitters:shipEmitterSovRegistryA(R.sensorRegistration)};",
            "SOV inactive emitter registry",
        )
    start, end = function_span(source, "electronicPhysicalEmittersF")
    runtime = (HERE / "emitter_runtime.js").read_text().replace("__MODE__", mode).rstrip()
    source = source[:start] + runtime + source[end:]
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("B", "C", "D"), required=True)
    parser.add_argument("--mode", choices=("SHADOW", "ACTIVE"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()
    if args.stage == "B" and args.mode != "SHADOW":
        raise AssertionError("Commit B is SHADOW-only")
    if args.stage in ("C", "D") and args.mode != "ACTIVE":
        raise AssertionError("Commits C/D are ACTIVE")

    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError("pinned U3 product SHA mismatch")
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    before = gzip.decompress(base64.b64decode(match[1])).decode()
    after = transform(before, stage=args.stage, mode=args.mode)
    packed = gzip.compress(after.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', output, re.S)
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(after.encode()), gzipBytes=len(packed), sha256=sha(after.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    output = output[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1):]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(output)
    if args.diff:
        args.diff.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="U3/main.js", tofile=f"EMITTER_A_{args.stage}_{args.mode}/main.js", n=0)))
    receipt = {
        "schema": "AEGIS_EMITTER_A_BUILD_1",
        "stage": args.stage,
        "mode": args.mode,
        "baseSha256": sha(raw),
        "baseMainSha256": sha(before.encode()),
        "outputSha256": sha(output),
        "outputMainSha256": sha(after.encode()),
        "outputBytes": len(output),
        "sourceModules": {name: sha((HERE / name).read_bytes()) for name in ("emitter_registry.js", "emitter_runtime.js")},
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
