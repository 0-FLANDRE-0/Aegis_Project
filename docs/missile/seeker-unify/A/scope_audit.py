#!/usr/bin/env python3
"""Prove forbidden detection/guidance/damage functions stayed byte-identical."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
PRODUCT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"


def unpack(path: Path) -> str:
    match = re.search(rb'data-c55-index="13">([^<]+)', path.read_bytes())
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode()


def function_source(source: str, name: str) -> str:
    match = re.search(rf"(?:async\s+)?function\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise KeyError(name)
    brace = source.index("{", match.end())
    depth = 0
    string = None
    escape = False
    template_expr = 0
    i = brace
    while i < len(source):
        c = source[i]
        if string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == string and (string != "`" or template_expr == 0):
                string = None
            elif string == "`" and c == "$" and i + 1 < len(source) and source[i + 1] == "{":
                template_expr += 1
                depth += 1
                i += 1
            elif string == "`" and c == "}" and template_expr:
                template_expr -= 1
                depth -= 1
        elif c in "'\"`":
            string = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[match.start(): i + 1]
        i += 1
    raise ValueError(name)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


before = unpack(BASE)
after = unpack(PRODUCT)
names = [
    "asmSeekerEchoMeasurement",
    "asmSeekerCompositeReturns",
    "arhRfTargetEvidenceWip13B12",
    "arhRfCandidateAcceptedWip13B12",
    "updateAsmSeeker",
    "buildEssmArhEchoPool",
    "_v1UpdateArhMeasurementCore",
    "_v1UpdateSarhMeasurementCore",
    "harpoonSeekerA",
    "ramRfMeasurement",
    "ramUpdateSeekerAuthority",
    "shipboardRadarEchoFieldWip13B13",
    "shipboardRadarDomainEvidenceWip13B13",
    "computeGuidanceAccelV1",
    "computeKappaMidcourseAccelV2",
    "computeZEMCorrectionV1",
    "missileThrustN",
    "updateMissileBodyB3",
    "computeInterceptPk",
]
rows = []
for name in names:
    a = function_source(before, name)
    b = function_source(after, name)
    rows.append({"name": name, "baselineSha256": sha(a), "productSha256": sha(b), "byteEqual": a == b})

diff = (HERE / "changes.diff").read_text()
forbidden_tokens = [
    "pdHalfSnr",
    "searchDwellGain",
    "trackDwellGain",
    "gimbal",
    "evidenceThreshold",
    "guidance",
    "thrust",
    "warhead",
    "damage",
]
changed_lines = [line for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
unexpected_tokens = sorted({token for token in forbidden_tokens if any(token.lower() in line.lower() for line in changed_lines)})
result = {
    "schema": "AEGIS_SEEKER_UNIFY_A_STATIC_SCOPE_AUDIT_1",
    "forbiddenFunctions": rows,
    "allForbiddenFunctionsByteEqual": all(row["byteEqual"] for row in rows),
    "changedSourceLines": len(changed_lines),
    "unexpectedChangedLineTokens": unexpected_tokens,
    "allowedChangedProviders": [
        "SURFACE_SHIP_RCS_BASIS_UNIFY_A",
        "surfaceShipRcsReferenceUnifyA",
        "surfaceShipRcsKnotsUnifyA",
        "navalRcsC",
        "computeShipRCS",
        "computeWeightedCentroid",
        "physicalRfRcsM2Wip13A2 band plumbing",
        "asmSeekerShipRfReturn band plumbing",
    ],
    "pass": all(row["byteEqual"] for row in rows) and not unexpected_tokens,
}
(HERE / "STATIC_SCOPE_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"pass": result["pass"], "functions": len(rows), "changedLines": len(changed_lines), "unexpectedTokens": unexpected_tokens}))
