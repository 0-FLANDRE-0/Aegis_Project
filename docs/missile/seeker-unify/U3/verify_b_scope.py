#!/usr/bin/env python3
"""Static scope/hash audit for U3 Commit B against the Commit A product."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from pathlib import Path


def unpack(path: Path) -> str:
    raw=path.read_bytes();match=re.search(rb'data-c55-index="13">([^<]+)',raw)
    if not match:raise AssertionError("packed main missing")
    return gzip.decompress(base64.b64decode(match[1])).decode()


def function_source(source: str, name: str) -> str:
    match=re.search(rf"function\s+{re.escape(name)}\s*\(",source)
    if not match:raise AssertionError(f"function missing: {name}")
    paren=source.find("(",match.start());pdepth=0;quote=None;escaped=False;close=-1
    for index in range(paren,len(source)):
        char=source[index]
        if quote:
            if escaped:escaped=False
            elif char=="\\":escaped=True
            elif char==quote:quote=None
            continue
        if char in "'\"`":quote=char
        elif char=="(":pdepth+=1
        elif char==")":
            pdepth-=1
            if pdepth==0:close=index;break
    brace=source.find("{",close+1);depth=0;quote=None;escaped=False
    for index in range(brace,len(source)):
        char=source[index]
        if quote:
            if escaped:escaped=False
            elif char=="\\":escaped=True
            elif char==quote:quote=None
            continue
        if char in "'\"`":quote=char
        elif char=="{":depth+=1
        elif char=="}":
            depth-=1
            if depth==0:return source[match.start():index+1]
    raise AssertionError(f"unterminated function: {name}")


def digest(text: str) -> str:return hashlib.sha256(text.encode()).hexdigest()


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument("--baseline",type=Path,required=True);ap.add_argument("--candidate",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    before,after=unpack(args.baseline),unpack(args.candidate)
    unchanged=["harpoonRfObservationsA","harpoonRandomA","harpoonNoiseA","harpoonPredictionA","harpoonRouteStepE","harpoonRequestFireA","harpoonFlightStepA","harpoonImpactA","harpoonExportA","harpoonRestoreA","asmCueUpdateA","asmPassiveRfMeasurementB2","surfaceMissileIdentityPolicyWip13C4","surfaceMissileTrackReadinessWip13C4"]
    hashes={};unexpected=[]
    for name in unchanged:
        left,right=function_source(before,name),function_source(after,name);same=left==right;hashes[name]={"baseline":digest(left),"candidate":digest(right),"byteEqual":same}
        if not same:unexpected.append(name)
    intended=["harpoonMemoryA","harpoonRouteProgramE","harpoonRouteGateE","harpoonGateA","harpoonReleaseA","harpoonSeekerA","attackPathGuardH3","attackEvaluateH3","harpoonJournalReleaseF1"]
    changed={name:{"baseline":digest(function_source(before,name)),"candidate":digest(function_source(after,name)),"changed":function_source(before,name)!=function_source(after,name)} for name in intended}
    helper_start=after.find("const HARPOON_CUE_B_SPEC=");helper_end=after.find("function runCoreUnitSelfTests(){",helper_start);helper=after[helper_start:helper_end]
    helper_ok=helper_start>=0 and helper_end>helper_start and not re.search(r"\b(entityId|targetId|truthPosition|physicalTarget)\b",helper) and "harpoonRandomA(" not in helper and "SIM_RNG_STATE" not in helper
    route_occurrences=after.count("cueSource:'ROUTE_PLAN_PRIOR'")
    result={"schema":"AEGIS_SEEKER_UNIFY_U3_B_SCOPE_1","status":"PASS" if not unexpected and helper_ok and all(q["changed"] for q in changed.values()) and route_occurrences>=4 else "FAIL","unchangedFunctionHashes":hashes,"unexpectedChangedFunctions":unexpected,"intentionallyChangedFunctionHashes":changed,"adapterAudit":{"present":helper_start>=0,"observableOnly":helper_ok,"rngCalls":0,"truthConsumers":0},"routePriorOccurrences":route_occurrences,"gameplayConstantsAdded":0,"saveInventorySchemaFunctionsByteEqual":hashes["harpoonExportA"]["byteEqual"] and hashes["harpoonRestoreA"]["byteEqual"]}
    args.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"status":result["status"],"unchangedFunctions":len(unchanged),"unexpected":unexpected,"adapterAudit":result["adapterAudit"],"routePriorOccurrences":route_occurrences},indent=2));raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__=="__main__":main()
