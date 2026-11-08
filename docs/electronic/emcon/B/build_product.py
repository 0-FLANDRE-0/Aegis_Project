#!/usr/bin/env python3
"""Reproducibly build EMCON_B stages from the merged EMITTER_A product."""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_EMITTER_A.html"
BASE_SHA = "3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def function_span(source: str, name: str, contains: str | None = None) -> tuple[int, int]:
    matches = list(re.finditer(rf"function\s+{re.escape(name)}\s*\(", source))
    found: list[tuple[int, int]] = []
    for match in matches:
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
                    body = source[match.start() : index + 1]
                    if contains is None or contains in body:
                        found.append((match.start(), index + 1))
                    break
    if len(found) != 1:
        raise AssertionError(f"{name}: expected one selected function, got {len(found)}")
    return found[0]


def transform(source: str, stage: str) -> str:
    policy = (HERE / "emcon_policy.js").read_text().replace("__EMCON_B_MODE__", "SHADOW" if stage == "B" else "ACTIVE").rstrip() + "\n"
    source = one(source, "// LIVE_CANONICAL. Physical emitters stop at anonymous receiver measurements.\n", policy + "// LIVE_CANONICAL. Physical emitters stop at anonymous receiver measurements.\n", "policy module")
    source = one(source, "function prepareElectronicF(r){\n  const own=", "function prepareElectronicF(r){\n  prepareEmconB(r);\n  const own=", "prepare lifecycle")
    start, end = function_span(source, "electronicShipPhysicalEmittersDeclaredA")
    if stage == "B":
        body = source[start:end]
        body = one(body, "if(sovNoEquipmentA(r)||registry?.physicalEmission===false)return out;", "if(sovNoEquipmentA(r)||registry?.physicalEmission===false){emconShadowResolveB(r,out);return out;}", "inactive shadow")
        last = body.rfind("return out;")
        if last < 0:
            raise AssertionError("declared resolver return missing")
        body = body[:last] + "emconShadowResolveB(r,out);" + body[last:]
    else:
        body = (HERE / "emcon_active_runtime.js").read_text().strip()
    source = source[:start] + body + source[end:]
    if stage in ("C", "D", "E"):
        source = one(source, "if(emconActive) return;\n    spyScheduler.accumulatorS", "if(!emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'AIR_SEARCH')) return;\n    spyScheduler.accumulatorS", "active SPY gate")
        source = one(source, "if(!emconActive&&spq9bHealth01()>.08)spq9bRotorAngle", "if(emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'SURFACE_SEARCH')&&spq9bHealth01()>.08)spq9bRotorAngle", "active SPQ rotor")
        source = one(source, "if(!emconActive && spq9bHealth01()>0.08){", "if(emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'SURFACE_SEARCH') && spq9bHealth01()>0.08){", "active SPQ measurement")
        source = one(source, "if(!emconActive&&bridgeMasterEHealth01()>.08)bridgeMasterERotorAngle", "if(emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'NAV')&&bridgeMasterEHealth01()>.08)bridgeMasterERotorAngle", "active NAV rotor")
        source = one(source, "if(!emconActive&&bridgeMasterEHealth01()>0.08){", "if(emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'NAV')&&bridgeMasterEHealth01()>0.08){", "active NAV measurement")
        source = one(source, "if(emconActive||bridgeMasterEHealth01()<=0.08)return;", "if(!emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'NAV')||bridgeMasterEHealth01()<=0.08)return;", "active NAV shoreline gate")
        source = one(source, "if(!o.enabled.SPY||o.emcon||health<=.05", "if(!emconCategoryAllowsB(r,'AIR_SEARCH')||health<=.05", "observer SPY gate")
        source = one(source, "if(!o.enabled[key]||o.emcon||health<=.08)return;", "if(!emconCategoryAllowsB(r,spq?'SURFACE_SEARCH':'NAV')||health<=.08)return;", "observer auxiliary gate")
        source = one(source, "function electronicJammerSampleF(r,rx,p,kind){\n  const cfg=", "function electronicJammerSampleF(r,rx,p,kind){\n  if(!emconCategoryAllowsB(r,'ECM'))return null;\n  const cfg=", "jammer and HOJ gate")
        # The first declaration is lexically inside createElectronicContextF(owner) despite its
        # column-0 formatting; the later indented declaration is the active-ship compatibility path.
        source = one(source, "\nfunction updateSlq32EaAllocator(dt){\n    if(shipEquipmentOfflineV1())", "\nfunction updateSlq32EaAllocator(dt){\n    if(!emconCategoryAllowsB(owner,'ECM')||shipEquipmentOfflineV1())", "observer allocator gate")
        source = one(source, "\n  function updateSlq32EaAllocator(dt){\n    if(shipEquipmentOfflineV1())", "\n  function updateSlq32EaAllocator(dt){\n    if(!emconCategoryAllowsB(ACTIVE_SHIP_RUNTIME,'ECM')||shipEquipmentOfflineV1())", "active allocator gate")
        source = one(source, "if(r===ACTIVE_SHIP_RUNTIME?emconActive:observerC(r).emcon)return [];\n  const rx=", "if(!emconCategoryAllowsB(r,'AIR_SEARCH'))return [];\n  const rx=", "surface IFF gate")
        source = one(source, "if(shipEquipmentOfflineV1(ship)||(ship===ACTIVE_SHIP_RUNTIME?emconActive:observerC(ship).emcon))return out;", "if(shipEquipmentOfflineV1(ship)||!emconCategoryAllowsB(ship,'AIR_SEARCH'))return out;", "air IFF gate")
    if stage in ("D", "E"):
        ui = (HERE / "emcon_ui.js").read_text().rstrip() + "\n"
        source = one(source, "// MAP_E_UI_BEGIN\n", ui + "// MAP_E_UI_BEGIN\n", "profile-derived EMCON UI module")
        source = one(source,
            "function refreshChip(){const chip=document.getElementById('uiEmconChipA');if(!chip)return;chip.textContent='EMCON '+(emconActive?'ON':'OFF')+'\\nECM '+ownEcmLevelE();chip.title='레이더 '+(emconActive?'OFF':'ON')+' · ECM '+levelNames[ownEcmLevelE()]+(!softKillAutoDoctrine&&(noiseJamActive||deceptJamActive)?' · 기존 재밍 승인 유지':'');chip.setAttribute('aria-expanded',String(!!menu&&!menu.hidden));chip.setAttribute('aria-controls','mapEmconMenuE');}",
            "function refreshChip(){const chip=document.getElementById('uiEmconChipA');if(!chip)return;const q=emconUiChipSnapshotB();chip.textContent=q.text;chip.title=q.title;chip.setAttribute('aria-pressed',String(q.masterSilent));chip.setAttribute('aria-expanded',String(!!menu&&!menu.hidden));chip.setAttribute('aria-controls','mapEmconMenuE');}",
            "selected-owner chip")
        source = one(source,
            "function command(level){const q=ownEcmCommandE(level);refresh();refreshChip();return q;}\n function allRadiation(){\n  if(!emconActive||ownEcmLevelE()!=='OFF'||noiseJamActive||deceptJamActive){remembered={owner:ACTIVE_SHIP_RUNTIME,level:ownEcmLevelE()};if(!emconActive)toggleEmcon();command('OFF');}\n  else{if(emconActive)toggleEmcon();command(remembered?.owner===ACTIVE_SHIP_RUNTIME?remembered.level:'OFF');}\n  refresh();\n }",
            "function command(level){const q=emconUiEcmCommandB(emconUiOwnerB(),level);refresh();refreshChip();return q;}\n function allRadiation(){const q=emconAllRadiationMacroB(emconUiOwnerB());refresh();refreshChip();return q;}",
            "selected-owner commands and all-radiation macro")
        source = one(source,
            "const level=ownEcmLevelE();dom.all.textContent='전체 방사 '+(emconActive&&level==='OFF'&&!noiseJamActive&&!deceptJamActive?'ON':'OFF');dom.radar.textContent='레이더 '+(emconActive?'ON':'OFF');for(const [k,e]of Object.entries(dom.levels))e.setAttribute('aria-pressed',String(level===k));dom.note.textContent=!softKillAutoDoctrine&&(noiseJamActive||deceptJamActive)?'기존 재밍 승인: '+(noiseJamActive?'NJ ':'')+(deceptJamActive?'DJ':''):'';place(menu,document.getElementById('uiEmconChipA').getBoundingClientRect());",
            "const owner=emconUiOwnerB(),level=emconUiEcmLevelB(owner),settings=electronicSettingsF(owner),allSilent=emconUiAllSilentB(owner);dom.all.textContent=allSilent?'전체 방사 복구':'전체 방사 침묵';dom.radar.textContent='RADAR MASTER '+(emconUiMasterSilentB(owner)?'SILENT':'ACTIVE');dom.radar.disabled=owner!==ACTIVE_SHIP_RUNTIME&&owner.role!=='ALLY';for(const [k,e]of Object.entries(dom.levels)){e.setAttribute('aria-pressed',String(level===k));e.disabled=k==='JAM'&&owner!==ACTIVE_SHIP_RUNTIME;}dom.note.textContent=(settings.noiseRequested||settings.deceptionRequested?'기법 요청: '+(settings.noiseRequested?'NJ ':'')+(settings.deceptionRequested?'DJ':''):'기법 요청 없음')+' · 실제 방출 '+(emconCategoryEmittingB(owner,'ECM')?'ON':'OFF');dom.policy.refresh();place(menu,document.getElementById('uiEmconChipA').getBoundingClientRect());",
            "policy UI refresh")
        source = one(source,
            "dom.all=button('전체 방사 OFF','mapAllRadiationE',allRadiation);dom.radar=button('레이더 OFF','mapRadarE',()=>{toggleEmcon();refresh();refreshChip();});menu.append(dom.all,dom.radar,make('span','','ECM'));const row=make('div','map-ecm-levels-e');",
            "dom.all=button('전체 방사 침묵','mapAllRadiationE',allRadiation);dom.radar=button('RADAR MASTER ACTIVE','mapRadarE',()=>{const r=emconUiOwnerB();fleetCommandG(r.entityId,{action:'EMCON',enabled:!emconUiMasterSilentB(r)});refresh();refreshChip();});dom.policy=emconCreatePolicyUiB();menu.append(dom.all,dom.radar,dom.policy.root,make('span','','ECM 기법 요청'));const row=make('div','map-ecm-levels-e');",
            "policy UI mount")
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
        raise AssertionError("pinned EMITTER_A product SHA mismatch")
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    before = gzip.decompress(base64.b64decode(match.group(1))).decode()
    after = transform(before, args.stage)
    packed = gzip.compress(after.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[: match.start(1)] + encoded + raw[match.end(1) :]
    meta = re.search(rb"const records=(\[.*?\]);", output, re.S)
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(after.encode()), gzipBytes=len(packed), sha256=sha(after.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    output = output[: meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1) :]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(output)
    if args.diff:
        args.diff.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="EMITTER_A/main.js", tofile=f"EMCON_B_{args.stage}/main.js", n=1)))
    receipt = {
        "schema": "AEGIS_EMCON_B_BUILD_1",
        "stage": args.stage,
        "baseSha256": sha(raw),
        "baseMainSha256": sha(before.encode()),
        "outputSha256": sha(output),
        "outputMainSha256": sha(after.encode()),
        "outputBytes": len(output),
        "sourceModules": {name: sha((HERE / name).read_bytes()) for name in (["emcon_policy.js"] + (["emcon_active_runtime.js"] if args.stage != "B" else []) + (["emcon_ui.js"] if args.stage in ("D", "E") else []))},
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
