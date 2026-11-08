#!/usr/bin/env python3
"""Reproducibly build cumulative ESM_A commits from merged EMCON_B."""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_EMCON_B.html"
BASE_SHA = "50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def function_spans(source: str, name: str) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for match in re.finditer(rf"function\s+{re.escape(name)}\s*\(", source):
        brace = source.find("{", match.end())
        depth = 0
        quote: str | None = None
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
                    found.append((match.start(), index + 1))
                    break
    return found


def function_span(source: str, name: str, *, last: bool = False) -> tuple[int, int]:
    spans = function_spans(source, name)
    if not spans:
        raise AssertionError(f"function missing: {name}")
    return spans[-1 if last else 0]


def function_hash(source: str, name: str, *, last: bool = False) -> str:
    start, end = function_span(source, name, last=last)
    return sha(source[start:end].encode())


def inject_after_function(source: str, name: str, payload: str, *, last: bool = False) -> str:
    _, end = function_span(source, name, last=last)
    return source[:end] + "\n" + payload.rstrip() + "\n" + source[end:]


def transform(source: str, stage: str) -> str:
    core = (HERE / "esm_core.js").read_text()
    core = core.replace("__ESM_A_REQUIRE_PROFILE__", "true" if stage == "E" else "false")
    core = core.replace("__ESM_A_STAGE__", stage)
    source = inject_after_function(source, "electronicCicTextF", core)

    if stage in ("C", "D", "E"):
        network = (HERE / "esm_network.js").read_text()
        old = "  }\n}\nfunction networkSnapshotG()"
        new = "  }\n  esmNetworkFixedStepA(dt);\n}\nfunction networkSnapshotG()"
        source = one(source, old, new, "ESM raw network fixed step")
        source = inject_after_function(source, "networkFixedStepG", network)

    if stage in ("D", "E"):
        ui = (HERE / "esm_ui.js").read_text().rstrip() + "\n"
        source = one(source, "function mapEsmReadA(id,c){", ui + "function mapEsmReadA(id,c){", "ESM UI module")
        start, end = function_span(source, "mapEsmReadA")
        source = source[:start] + (HERE / "esm_map_read.js").read_text().strip() + source[end:]
        source = one(
            source,
            "function esmSegment(o){const own=mapOwnShipA(),r=kmToWorld(Math.min(view().km,90));return [toScreen(own.x,own.y),toScreen(own.x+Math.cos(o.bearingRad)*r,own.y+Math.sin(o.bearingRad)*r)];}",
            "function esmSegment(o){const origin=o.originWorld??mapOwnShipA(),r=kmToWorld(Math.min(view().km,90));return [toScreen(origin.x,origin.y),toScreen(origin.x+Math.cos(o.bearingRad)*r,origin.y+Math.sin(o.bearingRad)*r)];}",
            "historical ESM hit-test origin",
        )
        source = one(
            source,
            "if(o.kind==='ESM'){sections.push({name:'ESM · '+age(o).toFixed(1)+'s',text:`방위 ${fmt((o.bearingRad*180/Math.PI+450)%360,1)}° ±${fmt(o.bearingSigmaDeg,1)}°\\n거리: 알 수 없음\\n대역: ${o.band??'보고 없음'} · 방사체 계열: ${o.emitterClass??o.type??'보고 없음'}\\n신뢰도: ${fmt(o.confidence,2)}`});return {header,sections};}",
            "if(o.kind==='ESM'){sections.push({name:'ESM · '+age(o).toFixed(1)+'s',text:esmInformationTextA(o)});return {header,sections};}",
            "ESM state information",
        )
        source = one(
            source,
            "if(o&&o.kind==='ESM'){const own=mapOwnShipA(),r=kmToWorld(Math.min(currentTacticalViewKm(),90))*.88,x=own.x+Math.cos(o.bearingRad)*r,y=own.y+Math.sin(o.bearingRad)*r;context.strokeStyle='#e0d7aa';context.setLineDash([3/mapZoom,3/mapZoom]);context.beginPath();context.arc(x,y,16/mapZoom,0,Math.PI*2);context.stroke();}",
            "if(o&&o.kind==='ESM'){esmDrawSelectionA(context,o,mapZoom,currentTacticalViewKm());}",
            "ESM selection rendering",
        )
        source = one(
            source,
            "for(const[id,c]of esmContacts)frame.esm.set(id,pipCopyFieldsA(c,['age','bearing','bearingSigmaDeg','type']));",
            "for(const[id,c]of esmContacts)frame.esm.set(id,esmPresentationCopyA(c));",
            "PiP ESM presentation copy",
        )
        source = one(source, "    // ===== ESM Contacts (bearing-only passive display) =====", "    // ===== ESM Contacts (historical origin / likelihood / estimate) =====", "ESM chart label")
        block_start = source.index("    for(const [id,c] of esmContacts){", source.index("// ===== ESM Contacts (historical"))
        block_end = source.index("\n\n    // ===== Mk 36", block_start)
        source = source[:block_start] + "    esmDrawChartA(ctx,esmContacts,viewKm,tracks);" + source[block_end:]

    if stage == "E":
        profiles = (HERE / "esm_profiles_lifecycle.js").read_text().rstrip() + "\n"
        source = one(source, "function shipEmitterEquipmentRegistryA(profileId){", profiles + "function shipEmitterEquipmentRegistryA(profileId){", "receiver profile module")
        source = one(
            source,
            "p15.equipment={...(p15.equipment??{}),registryId:'AEGIS_DDG119_EQUIPMENT_EMITTER_A',emitters:shipEmitterEquipmentRegistryA('DDG_119_LATE_FLIGHT_IIA')};",
            "p15.equipment={...(p15.equipment??{}),registryId:'AEGIS_DDG119_EQUIPMENT_EMITTER_A',emitters:shipEmitterEquipmentRegistryA('DDG_119_LATE_FLIGHT_IIA'),esmReceiver:esmReceiverProfileForShipA('DDG_119_LATE_FLIGHT_IIA')};",
            "DDG ESM receiver profile",
        )
        source = one(
            source,
            "secondaryRadars:R.radars,emitters:shipEmitterEquipmentRegistryA('CG_52_LATE_TICONDEROGA'),ew:{moduleId:E.SLQ32_CG52_LATE_V1.id,pods:R.ewPods},",
            "secondaryRadars:R.radars,emitters:shipEmitterEquipmentRegistryA('CG_52_LATE_TICONDEROGA'),esmReceiver:esmReceiverProfileForShipA('CG_52_LATE_TICONDEROGA'),ew:{moduleId:E.SLQ32_CG52_LATE_V1.id,pods:R.ewPods},",
            "CG ESM receiver profile",
        )
        source = one(source, "function resetElectronicFleetF(){\n  for(const r of electronicShipsF()){", "function resetElectronicFleetF(){\n  for(const r of electronicShipsF()){esmResetRuntimeA(r);", "ESM reset")
        source = one(source, "function retireElectronicF(r){\n  r.ew.executionF?.contacts.clear();", "function retireElectronicF(r){\n  esmRetireRuntimeA(r);r.ew.executionF?.contacts.clear();", "ESM retire")
        source = one(source, "network:networkSettingsG(ACTIVE_SHIP_RUNTIME),ew:networkExportElectronicG(ACTIVE_SHIP_RUNTIME),emconB:emconExportStateB(ACTIVE_SHIP_RUNTIME),navigation:", "network:networkSettingsG(ACTIVE_SHIP_RUNTIME),ew:networkExportElectronicG(ACTIVE_SHIP_RUNTIME),emconB:emconExportStateB(ACTIVE_SHIP_RUNTIME),esmA:esmExportStateA(ACTIVE_SHIP_RUNTIME),navigation:", "active ESM export")
        source = one(source, "network:networkSettingsG(r),ew:networkExportElectronicG(r),emconB:emconExportStateB(r),profileId:r.profileId,", "network:networkSettingsG(r),ew:networkExportElectronicG(r),emconB:emconExportStateB(r),esmA:esmExportStateA(r),profileId:r.profileId,", "fleet ESM export")
        source = one(source, "r.restoredElectronicF=q.ew??null;r.restoredEmconB=q.emconB??null;r.restoredNetworkG=q.network??null;", "r.restoredElectronicF=q.ew??null;r.restoredEmconB=q.emconB??null;r.restoredEsmA=q.esmA??null;r.restoredNetworkG=q.network??null;", "fleet ESM restore handoff")
        source = one(source, "validateEmconSaveB(src.profileId,src.ship?.emconB,errors,'ship');", "validateEmconSaveB(src.profileId,src.ship?.emconB,errors,'ship');validateEsmSaveA(src.profileId,src.ship?.esmA,errors,'ship');", "active ESM preflight")
        source = one(source, "seen.add(q.entityId);validateEmconSaveB(q.profileId,q.emconB,errors,'fleet.'+q.entityId);", "seen.add(q.entityId);validateEmconSaveB(q.profileId,q.emconB,errors,'fleet.'+q.entityId);validateEsmSaveA(q.profileId,q.esmA,errors,'fleet.'+q.entityId);", "fleet ESM preflight")

    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("B", "C", "D", "E"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()
    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA:
        raise AssertionError("pinned EMCON_B product SHA mismatch")
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    before = gzip.decompress(base64.b64decode(match.group(1))).decode()
    after = transform(before, args.stage)
    packed = gzip.compress(after.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[: match.start(1)] + encoded + raw[match.end(1) :]
    meta = re.search(rb"const records=(\[.*?\]);", output, re.S)
    records = json.loads(meta.group(1))
    records[13].update(rawBytes=len(after.encode()), gzipBytes=len(packed), sha256=sha(after.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    output = output[: meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1) :]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(output)
    if args.diff:
        args.diff.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="EMCON_B/main.js", tofile=f"ESM_A_{args.stage}/main.js", n=1)))
    unchanged_names = ["electronicPhysicalEmittersF", "electronicJammerSampleF", "emconEquipmentDecisionB", "networkBuildReportsG", "networkReceiveG", "asmPassiveRfMeasurementB2"]
    unchanged = {name: {"before": function_hash(before, name), "after": function_hash(after, name), "same": function_hash(before, name) == function_hash(after, name)} for name in unchanged_names}
    modules = ["esm_core.js"] + (["esm_network.js"] if args.stage in ("C", "D", "E") else []) + (["esm_ui.js", "esm_map_read.js"] if args.stage in ("D", "E") else []) + (["esm_profiles_lifecycle.js"] if args.stage == "E" else [])
    receipt = {"schema": "AEGIS_ESM_A_BUILD_1", "stage": args.stage, "baseSha256": sha(raw), "baseMainSha256": sha(before.encode()), "outputSha256": sha(output), "outputMainSha256": sha(after.encode()), "outputBytes": len(output), "sourceModules": {name: sha((HERE / name).read_bytes()) for name in modules}, "unchangedFunctions": unchanged}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
