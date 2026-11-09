#!/usr/bin/env python3
"""Reproducibly build HP_A from the exact merged SEEKER_UNIFY_U4 product."""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html"
BASE_BYTES = 22_195_923
BASE_SHA256 = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match.group(1))).decode(), match


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def brace_end(source: str, brace: int) -> int:
    depth = 0; quote = None; escaped = False; line_comment = False; block_comment = False; i = brace
    while i < len(source):
        c = source[i]; n = source[i + 1] if i + 1 < len(source) else ""
        if line_comment:
            if c in "\r\n": line_comment = False
            i += 1; continue
        if block_comment:
            if c == "*" and n == "/": block_comment = False; i += 2; continue
            i += 1; continue
        if quote:
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == quote: quote = None
            i += 1; continue
        if c == "/" and n == "/": line_comment = True; i += 2; continue
        if c == "/" and n == "*": block_comment = True; i += 2; continue
        if c in "'\"`": quote = c
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    raise AssertionError("unterminated function")


def function_spans(source: str, name: str) -> list[tuple[int, int]]:
    out = []
    for match in re.finditer(rf"^[ \t]*function\s+{re.escape(name)}\s*\(", source, re.MULTILINE):
        brace = source.find("{", match.end())
        out.append((match.start(), brace_end(source, brace)))
    return out


def function_hashes(source: str, name: str) -> list[str]:
    return [sha(source[a:b].encode()) for a, b in function_spans(source, name)]


def wrap_function(source: str, name: str, legacy: str, wrapper: str) -> str:
    spans = function_spans(source, name)
    if len(spans) != 1:
        raise AssertionError(f"{name}: expected one declaration, got {len(spans)}")
    start, end = spans[0]
    original = source[start:end]
    renamed = re.sub(rf"(function\s+){re.escape(name)}(\s*\()", rf"\1{legacy}\2", original, count=1)
    return source[:start] + renamed + "\n" + wrapper.rstrip() + source[end:]


def transform(source: str, phase: str = "C") -> str:
    module = (HERE / "outcome_contract_a.js").read_text().rstrip()
    anchor = source.find("function runCoreUnitSelfTests(){")
    if anchor < 0:
        raise AssertionError("HP_A module anchor missing")
    source = source[:anchor] + module + "\n\n" + source[anchor:]
    source = one(source, "function runCoreUnitSelfTests(){\n    const failures = [];", "function runCoreUnitSelfTests(){\n    const failures = [];\n    try{const audit=shipOutcomeSelfTestA();if(!audit.pass)failures.push('HP_A outcome contract '+JSON.stringify(audit.checks));}catch(err){failures.push('HP_A outcome contract '+String(err?.message??err));}", "HP_A core self-test")
    source = wrap_function(source, "computeShipStatus", "computeShipStatusLegacyHpA", """function computeShipStatus(runtime=ACTIVE_SHIP_RUNTIME){
    const status=computeShipStatusLegacyHpA(runtime);return {...status,damageSeverityPct:status.overall};
  }""")

    replacements = (
        ("cascade.residualSupplement=residualSupplement;if(residualSupplement.accepted&&!owner){const status=computeShipStatus();shipHP=floodAttitudePreviewV1.snapshot().irreversible?0:Math.max(0,100-status.overall);}", "cascade.residualSupplement=residualSupplement;if(residualSupplement.accepted&&!owner)shipOutcomeProjectA(ACTIVE_SHIP_RUNTIME,'IMPACT_RESIDUAL_SUPPLEMENT');", "residual impact projection"),
        ("const impulse=v48Wip02TransferredImpulse(impact,localDir,true),impactResponse=getShipDynamicsV15().impactImpulse({pointLocal:entry,impulseLocal:impulse,source:`${w.sourceLabel} WRECK`,impactState:impact}),status=computeShipStatus();shipHP=floodAttitudePreviewV1.snapshot().irreversible?0:Math.max(0,100-status.overall);", "const impulse=v48Wip02TransferredImpulse(impact,localDir,true),impactResponse=getShipDynamicsV15().impactImpulse({pointLocal:entry,impulseLocal:impulse,source:`${w.sourceLabel} WRECK`,impactState:impact});shipOutcomeProjectA(ACTIVE_SHIP_RUNTIME,'WRECK_IMPACT');", "wreck projection"),
        ("const status=computeShipStatus();shipHP=floodAttitudePreviewV1.snapshot().irreversible?0:Math.max(0,100-status.overall);", "shipOutcomeProjectA(ACTIVE_SHIP_RUNTIME,'DIRECT_IMPACT');", "two direct impact projections"),
    )
    for old, new, label in replacements[:2]:
        source = one(source, old, new, label)
    old, new, label = replacements[2]
    if source.count(old) != 2:
        raise AssertionError(f"{label}: expected two anchors, got {source.count(old)}")
    source = source.replace(old, new, 2)

    source = one(source, "const survival=survivalModel.snapshot();const hp=survival.irreversible?0:Math.max(0,100-computeShipStatus(runtime).overall);if(own)shipHP=hp;else runtime.health.shipHP=hp;", "const survival=survivalModel.snapshot();shipOutcomeProjectA(runtime,'DAMAGE_FLOOD_TICK');", "fixed tick projection")
    source = one(source, "damageFloodTickV1.lastState='NORMAL';updateShipSurvivalBannerV1(floodAttitudePreviewV1.snapshot());}", "damageFloodTickV1.lastState='NORMAL';shipOutcomeResetA(ACTIVE_SHIP_RUNTIME,'RESET_MODULES');updateShipSurvivalBannerV1(floodAttitudePreviewV1.snapshot());}", "player reset outcome")
    source = one(source, "claimShipMutableRootA(r,'survival',r.survival);claimShipMutableRootA(r,'physicalAccumulators',r.physicalAccumulators);return r;", "claimShipMutableRootA(r,'survival',r.survival);claimShipMutableRootA(r,'physicalAccumulators',r.physicalAccumulators);shipOutcomeResetA(r,'PREPARE_PHYSICAL_SHIP');return r;", "NPC outcome baseline")

    # Commit B stops after the common one-way projection is ACTIVE. Commit C
    # adds save migration, authority-consumer removal and presentation changes.
    if phase == "B":
        return source
    if phase != "C":
        raise AssertionError(f"unsupported HP_A build phase: {phase}")

    source = one(source, "r.clock={...q.clock};r.health.shipHP=src.shipHP;const f=r.flooding,fs=src.damage.flooding;", "r.clock={...q.clock};const f=r.flooding,fs=src.damage.flooding;", "NPC saved HP authority removal")
    source = one(source, "r.dynamics.restoreOperationalPose(q.survival);\n}", "r.dynamics.restoreOperationalPose(q.survival);shipOutcomeRestoreCompatibilityA(r,src.shipHP,'NPC_RESTORE');\n}", "NPC derived outcome restore")

    source = one(source, "navigation:maneuverExportNavigationH2(ACTIVE_SHIP_RUNTIME),shipHP,inventory:", "navigation:maneuverExportNavigationH2(ACTIVE_SHIP_RUNTIME),shipHP,survival:jsonSafeCloneV48Wip11A(floodAttitudePreviewV1.snapshot()),inventory:", "player survival export")
    source = one(source, "migrateEmconSaveB(src,harpoonMigrations);migrateEsmSaveA(src,harpoonMigrations);", "migrateEmconSaveB(src,harpoonMigrations);migrateEsmSaveA(src,harpoonMigrations);if(!Object.hasOwn(src.ship??{},'survival')){src.ship.survival=null;harpoonMigrations.push({id:'LEGACY_SHIP_SURVIVAL_HP_A',policy:'RECOMPUTE_FROM_DAMAGE_AND_FLOOD'});}", "legacy player survival migration")
    source = one(source, "if(!operationalFiniteV48Wip11B(src.ship?.shipHP)||src.ship.shipHP<0||src.ship.shipHP>100)operationalErrorV48Wip11B(errors,'SHIP_HP');", "if(!operationalFiniteV48Wip11B(src.ship?.shipHP)||src.ship.shipHP<0||src.ship.shipHP>100)operationalErrorV48Wip11B(errors,'SHIP_HP');const survival=src.ship?.survival;if(survival!=null&&(!operationalRecordV48Wip11B(survival)||!['NORMAL','DAMAGED','FLOODING','CRITICAL','CAPSIZING','CAPSIZED','SINKING','LOST'].includes(survival.state)||![survival.timeS,survival.phaseS,survival.heelRad,survival.trimRad,survival.draftM,survival.waterM3,survival.capTimer,survival.sinkTimer].every(operationalFiniteV48Wip11B)||typeof survival.irreversible!=='boolean'||typeof survival.lost!=='boolean'))operationalErrorV48Wip11B(errors,'SHIP_SURVIVAL_HP_A');", "player survival validation")
    source = one(source, "if(fs){for(const o of fs.openings??[]){flood.addOpening({id:o.id,a:o.a,b:o.b,x:o.x,y:o.y,z:o.z,normal:o.normal,kind:o.kind,damage:o.work,areaM2:o.areaM2,perforated:o.areaM2>0});if(o.seal01)flood.seal(o.id,o.seal01);}for(const c of fs.cells??[])flood.setWater(c.id,c.waterM3);for(const d of fs.doors??[])flood.setDoor(d.id,d.open);for(const p of fs.pumps??[])flood.setPump(p.id,p.enabled);if(fs.hydrostatics?.pose)flood.setAttitude(fs.hydrostatics.pose);}", "if(fs){for(const o of fs.openings??[]){flood.addOpening({id:o.id,a:o.a,b:o.b,x:o.x,y:o.y,z:o.z,normal:o.normal,kind:o.kind,damage:o.work,areaM2:o.areaM2,perforated:o.areaM2>0});if(o.seal01)flood.seal(o.id,o.seal01);}for(const c of fs.cells??[])flood.setWater(c.id,c.waterM3);for(const d of fs.doors??[])flood.setDoor(d.id,d.open);for(const p of fs.pumps??[])flood.setPump(p.id,p.enabled);if(fs.hydrostatics?.pose)flood.setAttitude(fs.hydrostatics.pose);}if(src.ship.survival){floodAttitudePreviewV1.restorePhysical(src.ship.survival);getShipDynamicsV15().restoreOperationalPose(src.ship.survival);flood.setAttitude(src.ship.survival);}", "player survival restore")
    source = one(source, "if(src.ship.crew)getShipCrewV21().restoreOperational(src.ship.crew);shipRescueK().restore(src.ship.rescue);shipHP=clamp(Number(src.ship.shipHP),0,100);ACTIVE_SHIP_RUNTIME.aviation.inventory=", "if(src.ship.crew)getShipCrewV21().restoreOperational(src.ship.crew);shipRescueK().restore(src.ship.rescue);shipOutcomeRestoreCompatibilityA(ACTIVE_SHIP_RUNTIME,src.ship.shipHP,'PLAYER_RESTORE');ACTIVE_SHIP_RUNTIME.aviation.inventory=", "player saved HP authority removal")

    source = one(source, "shipHP = 0;\n        notify('💥💥 탄약고 유폭! 함선 상실!');", "shipOutcomeProjectA(ACTIVE_SHIP_RUNTIME,'AMMO_COOKOFF_EVENT');\n        notify('💥💥 탄약고 유폭!');", "ammo cookoff false loss authority")
    source = one(source, "health=r.health.shipHP>0?'생존':'상실';", "outcome=shipOutcomeA(r),health=shipOutcomeMissionLabelA(outcome.missionState);", "bottom bar authority")
    source = one(source, "el.querySelector('#crewStateV21').textContent=crew.label+' · '+crew.reason+' / 선체: '+physical.label;", "const outcome=shipOutcomeA(ACTIVE_SHIP_RUNTIME);el.querySelector('#crewStateV21').textContent=crew.label+' · '+crew.reason+' / 선체: '+physical.label+' / 임무: '+shipOutcomeMissionLabelA(outcome.missionState)+' / 표시 HP '+Math.max(0,Math.round(outcome.displayHp))+'%';", "damage panel state separation")
    source = one(source, "const crew=shipCrewV21?.snapshot();el.style.display=p.state==='NORMAL'&&!crew?.combatUnavailable?'none':'block';el.textContent=(crew?.combatUnavailable?crew.label+' · ':'')+p.label", "const crew=shipCrewV21?.snapshot(),outcome=shipOutcomeA(ACTIVE_SHIP_RUNTIME);el.style.display=p.state==='NORMAL'&&!crew?.combatUnavailable?'none':'block';el.textContent='임무 '+shipOutcomeMissionLabelA(outcome.missionState)+' · '+(crew?.combatUnavailable?crew.label+' · ':'')+p.label", "survival banner mission label")
    source = one(source, "shipHP,startCounts,endCounts", "shipHP,shipOutcome:shipOutcomeA(ACTIVE_SHIP_RUNTIME),startCounts,endCounts", "battle result outcome")
    source = one(source, "simStepCounter,shipHP,selectedLockId", "simStepCounter,shipHP,shipOutcome:shipOutcomeA(ACTIVE_SHIP_RUNTIME),selectedLockId", "diagnostic snapshot outcome")
    return source


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb"const records=(\[.*?\]);", output, re.S)
    if not meta:
        raise AssertionError("packed record metadata missing")
    records = json.loads(meta.group(1))
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return output[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1):]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "Aegis_SIM_v48_WIP_HP_A.html")
    parser.add_argument("--receipt", type=Path, default=HERE / "evidence/commit-b/build-receipt.json")
    parser.add_argument("--phase", choices=("B", "C"), default="C")
    args = parser.parse_args()
    raw = BASE.read_bytes()
    assert len(raw) == BASE_BYTES, (len(raw), BASE_BYTES)
    assert sha(raw) == BASE_SHA256, sha(raw)
    source, match = unpack(raw)
    protected = ["createShipSurvivalV1", "damageFloodImpactV1", "getShipLongitudinalStrengthV48Wip03"]
    before = {name: function_hashes(source, name) for name in protected}
    transformed = transform(source, args.phase)
    after = {name: function_hashes(transformed, name) for name in protected}
    if before != after:
        raise AssertionError({"protectedFunctionHashDrift": {name: [before[name], after[name]] for name in protected if before[name] != after[name]}})
    output = repack(raw, transformed, match)
    args.out.write_bytes(output)
    receipt = {
        "schema": "AEGIS_HP_A_BUILD_RECEIPT_1",
        "phase": args.phase,
        "base": BASE.name,
        "baseBytes": len(raw),
        "baseSha256": sha(raw),
        "output": args.out.name,
        "outputBytes": len(output),
        "outputSha256": sha(output),
        "packedMainBytes": len(transformed.encode()),
        "packedMainSha256": sha(transformed.encode()),
        "protectedFunctionHashesBefore": before,
        "protectedFunctionHashesAfter": after,
        "protectedFunctionHashesExact": before == after,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
