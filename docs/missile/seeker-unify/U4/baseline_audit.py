#!/usr/bin/env python3
"""Freeze the merged ESM_A seeker call graph before SEEKER_UNIFY_U4 edits.

This is deliberately a read-only audit.  It extracts the packed main script,
hashes the latest functions (including duplicate owner/player RAM copies), and
emits machine-readable and human-readable evidence from the exact pinned base.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_ESM_A.html"
PRODUCT_SHA = "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7"
PRODUCT_BYTES = 22_182_527
MERGED_MAIN = "f17d3777a625699ab26f6a40de80a383f675ae85"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(raw: bytes) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match[1])).decode("utf-8")


def brace_end(source: str, brace: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char in "\r\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise AssertionError("unterminated function")


def function_spans(source: str, name: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    # The packed product contains diagnostic JavaScript source inside a quoted
    # string.  A declaration must therefore start a real source line; otherwise
    # the audit would hash text embedded in that string as executable code.
    pattern = re.compile(rf"^[ \t]*function\s+{re.escape(name)}\s*\(", re.MULTILINE)
    for match in pattern.finditer(source):
        paren = source.find("(", match.start(), match.end())
        depth = 0
        close = -1
        quote: str | None = None
        escaped = False
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
        if brace < 0:
            raise AssertionError(f"function brace missing: {name}")
        spans.append((match.start(), brace_end(source, brace)))
    return spans


FUNCTIONS = {
    "common": [
        "seekerEchoSampleU1", "seekerResolvedCellU1", "seekerMeasurementU1",
        "seekerEstimateU1", "seekerProfileViewU1", "seekerRngAdapterU1",
        "seekerDelegateU1", "seekerSynthesizeMonostaticPowerU2", "seekerResolveCellsU2",
    ],
    "asm_harpoon": [
        "asmSeekerAssociateMeasurements", "updateAsmSeeker", "asmUpdateHojTrack",
        "asmPassiveRfMeasurementB2", "harpoonMemoryA", "harpoonPredictionA",
        "harpoonRfObservationsA", "harpoonSeekerA",
    ],
    "sarh_arh": [
        "_sarhTruthReflectorPool", "buildNavalSarhEchoPool", "_sarhClusterEchoes",
        "_sarhMonopulseMeasurement", "_sarhBuildMeasurementSet",
        "_sarhAssociateMeasurements", "_sarhUpdateStateMachine",
        "_v1UpdateSarhMeasurementCore", "_v1StepSarhSensorV1",
        "getSarhTargetStateV1", "_v1SelectGuidanceSource",
        "_arhAssociateMeasurements", "_arhUpdateStateMachine",
        "_v1UpdateArhMeasurementCore",
    ],
    "ram": [
        "ownerRamRfD", "ramEmitterStrength", "ramIrSourceSignal",
        "ramRfMeasurement", "ramIrMeasurement", "ramNewAngularTrack",
        "ramUpdateAngularTrack", "ramUpdateSeekerAuthority",
        "ramGuidanceTrackForAuthority", "ramGuidanceFromEstimateB2",
        "initializeRamSeeker", "updateRamMeasurementSeeker", "ramSelectedSeekerTrack",
    ],
}


CLASSIFICATIONS = [
    {
        "area": "U1/U2 anonymous DTO and ASM/ARH/Harpoon echo-cell route",
        "classification": "LEGACY_EQUIVALENCE",
        "evidence": "U1 delegates and U2 ACTIVE families already preserve existing front-end values and RNG ownership.",
    },
    {
        "area": "SARH two-leg path, SPG allocation/emission, two LOS and TX/RX beams",
        "classification": "HARDWARE_DIFFERENCE",
        "evidence": "buildNavalSarhEchoPool derives tx/rx geometry and rejects missing physical illumination before measurement.",
    },
    {
        "area": "SARH anonymous clustering/measurement/association/state",
        "classification": "IMPLEMENTATION_DIVERGENCE",
        "evidence": "Separate SARH implementations duplicate ARH-shaped lifecycle responsibility while retaining a bistatic observable.",
    },
    {
        "area": "RAM player versus owner/NPC RF/IR producer paths",
        "classification": "IMPLEMENTATION_DIVERGENCE",
        "evidence": "ownerRamRfD plus closure-local IR path coexist with global ramRfMeasurement/ramIrMeasurement implementations.",
    },
    {
        "area": "RAM passive RF/IR observation model and RF-first/IR authority",
        "classification": "HARDWARE_DIFFERENCE",
        "evidence": "Bearing-only passive RF and IR measurements cannot be represented as active monostatic radar echoes.",
    },
    {
        "area": "RAM emitter signal ownership",
        "classification": "DEFECT_CANDIDATE",
        "evidence": "ramEmitterStrength multiplies physical emitter strength by em.seeker.trackQuality/_seekerQuality; transmitter output is coupled to a local tracking state.",
    },
    {
        "area": "Common association/state transition ownership",
        "classification": "IMPLEMENTATION_DIVERGENCE",
        "evidence": "ASM, Harpoon, SARH, ARH and RAM each retain separate gate selection and transition code.",
    },
    {
        "area": "Historical debug source fields on physical echo/IR candidates",
        "classification": "UNRESOLVED",
        "evidence": "Debug fields exist in front-end products; U4 must prove they are absent from tactical association and common outputs rather than silently deleting diagnostics.",
    },
]


OWNERS = [
    ["ASM", "per-ASM seeker object", "ASM seeker RNG on weapon", "weapon lifecycle", "HOJ hook retained"],
    ["Harpoon", "m.seeker + m.memory/cueHandoff", "per-Harpoon seeded seeker RNG", "launch/destroy missile lifecycle", "route/INS/HOJ hooks retained"],
    ["SARH", "m._sarhSensorV1", "m._sarhRngState", "v1 missile lifecycle", "SPG allocation and source arbiter retained"],
    ["ARH", "m._arhSensorV1", "m._arhRngState", "v1 missile lifecycle", "SARH/DL source arbiter retained"],
    ["RAM player", "rm._ram*Track + authority fields", "simRandom/gaussRand stream", "RAM missile lifecycle", "MEM/RF/IR authority retained"],
    ["RAM owner/NPC", "owner RAM rm._ram* fields", "owner weapon RNG callback", "owner runtime lifecycle", "same authority/guidance contract"],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=HERE / "U4_BASELINE_AUDIT.json")
    parser.add_argument("--markdown", type=Path, default=HERE / "U4_BASELINE_AUDIT.md")
    args = parser.parse_args()
    raw = PRODUCT.read_bytes()
    if len(raw) != PRODUCT_BYTES or digest(raw) != PRODUCT_SHA:
        raise AssertionError("pinned merged ESM_A product mismatch")
    source = extract_main(raw)
    rows = []
    missing = []
    for group, names in FUNCTIONS.items():
        for name in names:
            spans = function_spans(source, name)
            if not spans:
                missing.append(name)
                continue
            reference_count = source.count(name)
            for occurrence, (start, end) in enumerate(spans, 1):
                body = source[start:end]
                rows.append({
                    "group": group,
                    "name": name,
                    "occurrence": occurrence,
                    "line": source.count("\n", 0, start) + 1,
                    "bytes": len(body.encode()),
                    "sha256": digest(body.encode()),
                    "references": reference_count,
                    "callerReferenceCount": max(0, reference_count - len(spans)),
                })
    if missing:
        raise AssertionError(f"baseline functions missing: {missing}")
    markers = {
        "sarhBistaticDimension": source.count("SARH_BISTATIC_4D"),
        "passiveRfDimension": source.count("PASSIVE_RF_2D"),
        "passiveIrDimension": source.count("PASSIVE_IR_2D"),
        "u2ActiveFamilies": re.findall(r"activeFamilies:Object\.freeze\(\[([^\]]+)\]\)", source)[-1],
        "ramEmitterOwnershipDefect": "em?.seeker?.trackQuality??em?._seekerQuality??.75" in source,
        "sarhTwoLos": all(token in source for token in ("losTx", "losRx")),
        "sarhTxRxRanges": all(token in source for token in ("txRangeM", "rxRangeM")),
        "sarhPathRate": "dopplerPathRateMps" in source,
        "ramOwnerPath": len(function_spans(source, "ownerRamRfD")) == 1,
        "ramPlayerPath": len(function_spans(source, "ramRfMeasurement")) >= 1,
    }
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_BASELINE_AUDIT_1",
        "status": "PASS",
        "mergedMain": MERGED_MAIN,
        "product": PRODUCT.name,
        "productBytes": len(raw),
        "productSha256": digest(raw),
        "packedMainBytes": len(source.encode()),
        "packedMainSha256": digest(source.encode()),
        "functions": rows,
        "markers": markers,
        "classifications": CLASSIFICATIONS,
        "stateOwners": [
            {"family": r[0], "stateOwner": r[1], "rngOwner": r[2], "lifecycleOwner": r[3], "weaponHook": r[4]}
            for r in OWNERS
        ],
        "truthBoundary": {
            "allowed": "physical front-end echo/heat/emitter synthesis only",
            "forbidden": "entity/profile/faction/truth position in common DTO, association, state or guidance consumer",
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# SEEKER_UNIFY_U4 작업 전 감사",
        "",
        "- IMPLEMENTED: 감사 산출물만 구현; 제품 코드 변경 없음",
        "- TESTED: 병합 제품 bytes/SHA, packed-main 구문, 함수 해시·중복 경로 정적 감사",
        "- APPROVED: PR #75 승인 head의 merge commit 병합 결과만 승인됨",
        "- UNRESOLVED: U4 A/B/C의 SHADOW 및 ACTIVE 동등성은 후속 게이트 대상",
        "- RELEASE: 아니오",
        "",
        "## 고정 기준",
        "",
        f"- main merge: `{MERGED_MAIN}`",
        f"- product: `{PRODUCT.name}` ({len(raw):,} bytes)",
        f"- product SHA-256: `{digest(raw)}`",
        f"- packed main SHA-256: `{digest(source.encode())}`",
        "",
        "## 함수·호출 경계",
        "",
        "| 그룹 | 함수 | 발생 | line | bytes | SHA-256 | 외부 참조 수 |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['group']} | `{row['name']}` | {row['occurrence']} | {row['line']} | {row['bytes']} | `{row['sha256'][:16]}…` | {row['callerReferenceCount']} |")
    lines += ["", "## 분류", "", "| 영역 | 분류 | 근거 |", "|---|---|---|"]
    for row in CLASSIFICATIONS:
        lines.append(f"| {row['area']} | `{row['classification']}` | {row['evidence']} |")
    lines += ["", "## 상태·RNG·수명주기 소유자", "", "| 계열 | local state | RNG | lifecycle | 보존 훅 |", "|---|---|---|---|---|"]
    for row in OWNERS:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## 최신 코드와 A 설계 문서의 차이",
        "",
        "- U1에는 네 관측 차원 enum이 이미 존재하고 U2 ACTIVE에는 ASM, SAM ARH, Harpoon echo/cell 계열이 연결돼 있다.",
        "- SARH는 최신 코드에서 `buildNavalSarhEchoPool` → `_sarhClusterEchoes` → `_sarhMonopulseMeasurement` → local EKF/NIS 순으로 독립 구현돼 있다.",
        "- RAM은 owner/NPC closure와 player 경로가 중복돼 있고, 각각 기존 RNG 소유자를 달리한다. 공통화는 RNG callback을 주입해야 한다.",
        "- `ramEmitterStrength`의 추적 품질 역의존은 물리 방사원 소유권 결함 후보로 확인됐다. U4 B에서 기존 기본값이 암시하던 수치만 보존해 좁게 분리하고 별도 보고한다.",
        "",
        "## 정보 비누수 경계",
        "",
        "물리 프런트엔드는 실제 장면을 읽을 수 있다. 공통 DTO, 연관, 상태기계와 유도 소비자에는 익명 관측값·공분산·시각·품질·익명 key만 전달한다. `_debugSource*` 필드는 제품 판단에 사용하지 않으며 진단 사후 비교로만 제한한다.",
    ]
    args.markdown.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": "PASS", "functions": len(rows), "json": str(args.json), "markdown": str(args.markdown)}))


if __name__ == "__main__":
    main()
