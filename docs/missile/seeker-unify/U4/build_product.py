#!/usr/bin/env python3
"""Reproducibly build SEEKER_UNIFY_U4 from the merged, pinned ESM_A product."""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_ESM_A.html"
BASE_SHA = "5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    if not match:
        raise AssertionError("packed main script missing")
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


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
    spans = []
    pattern = re.compile(rf"^[ \t]*function\s+{re.escape(name)}\s*\(", re.MULTILINE)
    for match in pattern.finditer(source):
        paren = source.find("(", match.start(), match.end()); depth = 0; close = -1; quote = None; escaped = False
        for i in range(paren, len(source)):
            c = source[i]
            if quote:
                if escaped: escaped = False
                elif c == "\\": escaped = True
                elif c == quote: quote = None
                continue
            if c in "'\"`": quote = c
            elif c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: close = i; break
        brace = source.find("{", close + 1)
        spans.append((match.start(), brace_end(source, brace)))
    return spans


def function_hashes(source: str, name: str) -> list[str]:
    return [sha(source[start:end].encode()) for start, end in function_spans(source, name)]


def wrap_functions(source: str, name: str, legacy: str, wrapper: str, expected: int) -> str:
    spans = function_spans(source, name)
    if len(spans) != expected:
        raise AssertionError(f"{name}: expected {expected} executable declarations, got {len(spans)}")
    for start, end in reversed(spans):
        original = source[start:end]
        renamed = re.sub(rf"(function\s+){re.escape(name)}(\s*\()", rf"\1{legacy}\2", original, count=1)
        source = source[:start] + renamed + "\n" + wrapper.rstrip() + source[end:]
    return source


def wrap_functions_by_scope(source: str, name: str, legacy: str, wrappers: list[str]) -> str:
    """Wrap same-named declarations in source order with scope-specific wrappers."""
    spans = function_spans(source, name)
    if len(spans) != len(wrappers):
        raise AssertionError(f"{name}: expected {len(wrappers)} executable declarations, got {len(spans)}")
    for index in range(len(spans) - 1, -1, -1):
        start, end = spans[index]
        original = source[start:end]
        renamed = re.sub(rf"(function\s+){re.escape(name)}(\s*\()", rf"\1{legacy}\2", original, count=1)
        source = source[:start] + renamed + "\n" + wrappers[index].rstrip() + source[end:]
    return source


def replace_in_function(source: str, name: str, old: str, new: str, label: str) -> str:
    spans = function_spans(source, name)
    if len(spans) != 1:
        raise AssertionError(f"{label}: expected one {name} declaration, got {len(spans)}")
    start, end = spans[0]
    body = source[start:end]
    if body.count(old) != 1:
        raise AssertionError(f"{label}: expected one anchor in {name}, got {body.count(old)}")
    body = body.replace(old, new, 1)
    return source[:start] + body + source[end:]


def transform_a(source: str, mode: str) -> str:
    source = one(
        source,
        "  HARPOON:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'HARPOON_NATIVE_MONOSTATIC',extentPolicy:'PRE_RESOLVED_ANONYMOUS',angularPolicy:'BODY_RELATIVE_MEASUREMENT',maxCells:96})\n});",
        "  HARPOON:Object.freeze({provenance:'LEGACY_EQUIVALENCE',beamConvention:'HARPOON_NATIVE_MONOSTATIC',extentPolicy:'PRE_RESOLVED_ANONYMOUS',angularPolicy:'BODY_RELATIVE_MEASUREMENT',maxCells:96}),\n  SARH_BISTATIC:Object.freeze({provenance:'LEGACY_EQUIVALENCE',observationModel:'SARH_BISTATIC_4D',beamConvention:'TX_TARGET_RX_SEPARATE',extentPolicy:'SARH_NATIVE_CONNECTED_COMPONENTS',angularPolicy:'BISTATIC_MONOPULSE',requiresIllumination:true})\n});",
        "A SARH profile option",
    )
    source = wrap_functions(source, "_sarhNormalizedBistaticPower", "_sarhNormalizedBistaticPowerLegacyU4A", f"""function _sarhNormalizedBistaticPower(rcsM2,txRangeKm,rxRangeKm,txGain=1,rxGain=1,txLosQ=1,rxLosQ=1,envQ=1){{
    const legacy=_sarhNormalizedBistaticPowerLegacyU4A(rcsM2,txRangeKm,rxRangeKm,txGain,rxGain,txLosQ,rxLosQ,envQ),common=seekerU4SarhBistaticPowerA(rcsM2,txRangeKm,rxRangeKm,txGain,rxGain,txLosQ,rxLosQ,envQ);seekerU4SarhComparePowerA(legacy,common);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?common:legacy;
  }}""", 1)
    source = wrap_functions(source, "_sarhEchoesUnresolved", "_sarhEchoesUnresolvedLegacyU4A", """function _sarhEchoesUnresolved(a,b){
    const legacy=_sarhEchoesUnresolvedLegacyU4A(a,b),common=seekerU4SarhUnresolvedA(a,b);seekerU4SarhCompareUnresolvedA(legacy,common);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?common:legacy;
  }""", 1)
    source = wrap_functions(source, "buildNavalSarhEchoPool", "buildNavalSarhEchoPoolLegacyU4A", """function buildNavalSarhEchoPool(m,cueTrack){
    const legacy=buildNavalSarhEchoPoolLegacyU4A(m,cueTrack),route=seekerU4SarhRouteA('ECHOES',legacy);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?route.tacticalValue:legacy;
  }""", 2)
    source = wrap_functions(source, "_sarhClusterEchoes", "_sarhClusterEchoesLegacyU4A", """function _sarhClusterEchoes(echoes){
    const legacy=_sarhClusterEchoesLegacyU4A(echoes),route=seekerU4SarhRouteA('CELLS',legacy);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?route.tacticalValue:legacy;
  }""", 1)
    source = wrap_functions(source, "_sarhMonopulseMeasurement", "_sarhMonopulseMeasurementLegacyU4A", """function _sarhMonopulseMeasurement(m,cluster){
    const legacy=_sarhMonopulseMeasurementLegacyU4A(m,cluster),route=seekerU4SarhRouteA('MEASUREMENT',legacy);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?route.tacticalValue:legacy;
  }""", 2)
    source = wrap_functions(source, "_sarhBuildMeasurementSet", "_sarhBuildMeasurementSetLegacyU4A", """function _sarhBuildMeasurementSet(m,cueTrack){
    const legacy=_sarhBuildMeasurementSetLegacyU4A(m,cueTrack),route=seekerU4SarhRouteA('PACKET',legacy);return SEEKER_U4_SARH_MODE_A==='ACTIVE'?route.tacticalValue:legacy;
  }""", 2)
    module = (HERE / "sarh_adapter_a.js").read_text().replace("__MODE__", mode).rstrip()
    # The core self-test executes before the historical U1/U2 append block.
    # Install at the top-level self-test boundary (the earlier owner SARH copy
    # lives inside bindOwnerD and is therefore not a global insertion point).
    module_anchor = source.find("function runCoreUnitSelfTests(){")
    if module_anchor < 0:
        raise AssertionError("A early SARH module anchor missing")
    source = source[:module_anchor] + module + "\n\n" + source[module_anchor:]
    old = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON']),reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    if mode == "ACTIVE":
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC']),shadowFamilies:Object.freeze([]),sarhMode:'ACTIVE',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    else:
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells']),shadowComponents:Object.freeze(['adaptSarhBistatic']),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON']),shadowFamilies:Object.freeze(['SARH_BISTATIC']),sarhMode:'SHADOW',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    source = one(source, old, new, "A U2 public contract")
    return source


def transform_b(source: str, mode: str) -> str:
    source = wrap_functions(source, "ramEmitterStrength", "ramEmitterStrengthLegacyU4B", """function ramEmitterStrength(em){
    const legacy=ramEmitterStrengthLegacyU4B(em),common=seekerU4RamEmitterStrengthB(em);seekerU4RamCompareEmitterB(legacy,common);return SEEKER_U4_RAM_MODE_B==='ACTIVE'?common:legacy;
  }""", 1)
    source = wrap_functions_by_scope(source, "ramRfMeasurement", "ramRfMeasurementLegacyU4B", [
        """function ramRfMeasurement(rm,dt){
    const legacy=ramRfMeasurementLegacyU4B(rm,dt),route=seekerU4RamRouteB('RF','OWNER',legacy);return SEEKER_U4_RAM_MODE_B==='ACTIVE'?route.tacticalValue:legacy;
  }""",
        """function ramRfMeasurement(rm,dt){
    const legacy=ramRfMeasurementLegacyU4B(rm,dt),route=seekerU4RamRouteB('RF','PLAYER',legacy);return SEEKER_U4_RAM_MODE_B==='ACTIVE'?route.tacticalValue:legacy;
  }""",
    ])
    source = wrap_functions_by_scope(source, "ramIrMeasurement", "ramIrMeasurementLegacyU4B", [
        """function ramIrMeasurement(rm,dt){
    const legacy=ramIrMeasurementLegacyU4B(rm,dt),route=seekerU4RamRouteB('IR','OWNER',legacy);return SEEKER_U4_RAM_MODE_B==='ACTIVE'?route.tacticalValue:legacy;
  }""",
        """function ramIrMeasurement(rm,dt){
    const legacy=ramIrMeasurementLegacyU4B(rm,dt),route=seekerU4RamRouteB('IR','PLAYER',legacy);return SEEKER_U4_RAM_MODE_B==='ACTIVE'?route.tacticalValue:legacy;
  }""",
    ])
    module = (HERE / "ram_adapter_b.js").read_text().replace("__MODE__", mode).rstrip()
    anchor = source.find("function runCoreUnitSelfTests(){")
    if anchor < 0:
        raise AssertionError("B early RAM module anchor missing")
    source = source[:anchor] + module + "\n\n" + source[anchor:]
    old = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC']),shadowFamilies:Object.freeze([]),sarhMode:'ACTIVE',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    if mode == "ACTIVE":
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic','adaptRamPassive']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC','RAM_PASSIVE_RF','RAM_PASSIVE_IR']),shadowFamilies:Object.freeze([]),sarhMode:'ACTIVE',ramMode:'ACTIVE',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    else:
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic']),shadowComponents:Object.freeze(['adaptRamPassive']),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC']),shadowFamilies:Object.freeze(['RAM_PASSIVE_RF','RAM_PASSIVE_IR']),sarhMode:'ACTIVE',ramMode:'SHADOW',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    return one(source, old, new, "B U2 public contract")


def transform_c(source: str, mode: str) -> str:
    # Association selection consumes anonymous numeric scores only.  Existing
    # weapon hooks continue to own prediction, covariance, NIS/absolute gates
    # and candidate construction.
    source = replace_in_function(source, "asmSeekerAssociateMeasurements", "scored.sort((a,b)=>b.score-a.score);const b=scored[0]", "const b=scored[seekerU4SelectIndexC('ASM',scored.map(q=>q.score),'MAX')]", "C ASM association")
    source = replace_in_function(source, "_sarhAssociateMeasurements", "scored.sort((a,b)=>b.score-a.score);const b=scored[0]", "const b=scored[seekerU4SelectIndexC('SARH',scored.map(q=>q.score),'MAX')]", "C SARH association")
    source = replace_in_function(source, "_arhAssociateMeasurements", "scored.sort((a,b)=>b.score-a.score);const b=scored[0],mm=b.mm", "const b=scored[seekerU4SelectIndexC('ARH',scored.map(q=>q.score),'MAX')],mm=b.mm", "C ARH association")
    source = replace_in_function(source, "harpoonSeekerA", "candidates.sort((a,b)=>a.score-b.score);const best=candidates[0]", "const best=candidates[seekerU4SelectIndexC('HARPOON',candidates.map(q=>q.score),'MIN')]", "C Harpoon association")

    source = wrap_functions(source, "_sarhUpdateStateMachine", "_sarhUpdateStateMachineLegacyU4C", """function _sarhUpdateStateMachine(s,accepted,period,hasIll){
    // Preserved WIP61 contract: if(s.mode==='ACQUIRE')s.acquireHits=0;
    // Preserved WIP61 contract: if(s.mode==='REACQUIRE')s.reacquireHits=0;
    if(SEEKER_U4_COMMON_MODE_C==='ACTIVE')return seekerU4SarhStateC(s,accepted,period,hasIll,SAM_SARH_RF_PROFILE);
    const shadow={...s};seekerU4SarhStateC(shadow,accepted,period,hasIll,SAM_SARH_RF_PROFILE);const legacy=_sarhUpdateStateMachineLegacyU4C(s,accepted,period,hasIll);return seekerU4ShadowStateC('SARH',s,shadow,legacy,{accepted,illuminationAvailable:hasIll});
  }""", 1)
    source = wrap_functions(source, "_arhUpdateStateMachine", "_arhUpdateStateMachineLegacyU4C", """function _arhUpdateStateMachine(s,accepted,period,active){
    const p=getEssmArhProfile();if(SEEKER_U4_COMMON_MODE_C==='ACTIVE')return seekerU4ArhStateC(s,accepted,period,active,p);
    const shadow={...s};seekerU4ArhStateC(shadow,accepted,period,active,p);const legacy=_arhUpdateStateMachineLegacyU4C(s,accepted,period,active);return seekerU4ShadowStateC('ARH',s,shadow,legacy,{accepted,signalAvailable:active});
  }""", 1)
    source = wrap_functions(source, "ramUpdateAngularTrack", "ramUpdateAngularTrackLegacyU4C", """function ramUpdateAngularTrack(tr,meas,dt,cfg){
    if(SEEKER_U4_COMMON_MODE_C==='ACTIVE')return seekerU4RamStateC(tr,meas,dt,cfg);
    const shadow={...tr};seekerU4RamStateC(shadow,meas,dt,cfg);const legacy=ramUpdateAngularTrackLegacyU4C(tr,meas,dt,cfg);return seekerU4ShadowStateC('RAM',tr,shadow,legacy,{accepted:!!meas,signalAvailable:!!meas});
  }""", 1)
    source = wrap_functions(source, "updateAsmSeeker", "updateAsmSeekerLegacyU4C", """function updateAsmSeeker(em,dt){
    // Preserved WIP68 phase guard in the ASM policy hook: em.label!=='Kh-32'.
    return seekerU4RunPolicyC('ASM',()=>em?.seeker,()=>updateAsmSeekerLegacyU4C(em,dt),{signalAvailable:!!em?.seekerOn,destroyed:em?.alive===false});
  }""", 1)
    source = wrap_functions(source, "harpoonSeekerA", "harpoonSeekerALegacyU4C", """function harpoonSeekerA(m,dt,diagnosticObservations=null){
    return seekerU4RunPolicyC('HARPOON',()=>m?.seeker,()=>harpoonSeekerALegacyU4C(m,dt,diagnosticObservations),{signalAvailable:m?.seeker?.active!==false,retired:m?.alive===false});
  }""", 1)
    module = (HERE / "association_state_c.js").read_text().replace("__MODE__", mode).rstrip()
    anchor = source.find("function runCoreUnitSelfTests(){")
    if anchor < 0:
        raise AssertionError("C common engine anchor missing")
    source = source[:anchor] + module + "\n\n" + source[anchor:]
    old = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic','adaptRamPassive']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC','RAM_PASSIVE_RF','RAM_PASSIVE_IR']),shadowFamilies:Object.freeze([]),sarhMode:'ACTIVE',ramMode:'ACTIVE',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    if mode == "ACTIVE":
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic','adaptRamPassive','associateAndTransition']),shadowComponents:Object.freeze([]),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC','RAM_PASSIVE_RF','RAM_PASSIVE_IR']),shadowFamilies:Object.freeze([]),sarhMode:'ACTIVE',ramMode:'ACTIVE',commonStateMode:'ACTIVE',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    else:
        new = "  activeComponents:Object.freeze(['synthesizeEchoes','resolveCells','adaptSarhBistatic','adaptRamPassive']),shadowComponents:Object.freeze(['associateAndTransition']),activeFamilies:Object.freeze(['ASM_WIP22','SAM_ARH','HARPOON','SARH_BISTATIC','RAM_PASSIVE_RF','RAM_PASSIVE_IR']),shadowFamilies:Object.freeze(['COMMON_ASSOCIATION_STATE']),sarhMode:'ACTIVE',ramMode:'ACTIVE',commonStateMode:'SHADOW',reset:()=>undefined,snapshot:seekerU2ActiveSnapshot,"
    return one(source, old, new, "C U2 public contract")


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0); encoded = base64.b64encode(packed)
    output = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb"const records=(\[.*?\]);", output, re.S)
    if not meta: raise AssertionError("packed record metadata missing")
    records = json.loads(meta[1]); records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]: records[13]["encodedBytes"] = len(encoded)
    return output[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + output[meta.end(1):]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--through", choices=("A", "B", "C"), default="A")
    ap.add_argument("--mode", choices=("SHADOW", "ACTIVE"), required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--diff", type=Path)
    args = ap.parse_args()
    raw = BASE.read_bytes()
    if sha(raw) != BASE_SHA: raise AssertionError("pinned ESM_A product SHA mismatch")
    before, match = unpack(raw)
    if args.through == "A":
        after = transform_a(before, args.mode)
    elif args.through == "B":
        after = transform_b(transform_a(before, "ACTIVE"), args.mode)
    else:
        after = transform_c(transform_b(transform_a(before, "ACTIVE"), "ACTIVE"), args.mode)
    output = repack(raw, after, match)
    args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_bytes(output)
    if args.diff:
        args.diff.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="ESM_A/main.js", tofile=f"U4_A_{args.mode}/main.js", n=1)))
    protected = ["allocateSARH", "_v1SelectGuidanceSource", "getSarhTargetStateV1", "_sarhReflectorBistaticRcsM2", "_sarhReceiverBeamGain", "_sarhIlluminatorBeamGain", "updateMissileBodyB3", "surfaceMissileReleaseGateWip13C4", "ramUpdateSeekerAuthority", "ramGuidanceFromEstimateB2", "asmHojGuidanceActive", "harpoonRouteStepE"]
    unchanged = {name: {"before": function_hashes(before, name), "after": function_hashes(after, name), "same": function_hashes(before, name) == function_hashes(after, name)} for name in protected}
    modules = {"A": sha((HERE/"sarh_adapter_a.js").read_bytes())}
    if args.through in ("B", "C"): modules["B"] = sha((HERE/"ram_adapter_b.js").read_bytes())
    if args.through == "C": modules["C"] = sha((HERE/"association_state_c.js").read_bytes())
    wrapped_names = ["_sarhNormalizedBistaticPower","_sarhEchoesUnresolved","buildNavalSarhEchoPool","_sarhClusterEchoes","_sarhMonopulseMeasurement","_sarhBuildMeasurementSet"]
    if args.through in ("B", "C"): wrapped_names += ["ramEmitterStrength", "ramRfMeasurement", "ramIrMeasurement"]
    if args.through == "C": wrapped_names += ["_sarhUpdateStateMachine", "_arhUpdateStateMachine", "ramUpdateAngularTrack", "updateAsmSeeker", "harpoonSeekerA"]
    receipt = {"schema":"AEGIS_SEEKER_UNIFY_U4_BUILD_1","through":args.through,"mode":args.mode,"baseSha256":sha(raw),"baseMainSha256":sha(before.encode()),
      "outputSha256":sha(output),"outputMainSha256":sha(after.encode()),"outputBytes":len(output),"moduleSha256":modules,
      "wrappedFunctions": {name: len(function_spans(before,name)) for name in wrapped_names},
      "unchangedFunctions":unchanged,"broadRegressionRun":False,"release":False}
    args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
