#!/usr/bin/env python3
"""Static scope/provenance audit for U3 Commit C against Commit B."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from verify_b_scope import digest, function_source, unpack


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--baseline",type=Path,required=True);ap.add_argument("--candidate",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    before,after=unpack(args.baseline),unpack(args.candidate)
    unchanged=["electronicHojF","asmHojEmitterSignal","asmEnsureHojState","asmHojGuidanceActive","asmSeekerHorizontalGuidanceAngle","harpoonRfObservationsA","harpoonRandomA","harpoonNoiseA","harpoonMemoryA","harpoonGateA","harpoonRouteGateE","harpoonImpactA","harpoonExportA","harpoonRestoreA","asmPassiveRfMeasurementB2"]
    hashes={};unexpected=[]
    for name in unchanged:
        left,right=function_source(before,name),function_source(after,name);same=left==right;hashes[name]={"baseline":digest(left),"candidate":digest(right),"byteEqual":same}
        if not same:unexpected.append(name)
    original=function_source(before,"asmUpdateHojTrack");legacy=function_source(after,"asmUpdateHojTrackLegacyU3").replace("function asmUpdateHojTrackLegacyU3(","function asmUpdateHojTrack(",1)
    legacy_equal=original==legacy
    intended=["asmUpdateHojTrack","harpoonReleaseA","harpoonSeekerA","harpoonFlightStepA","harpoonRenderStatesA"]
    changed={name:{"baseline":digest(function_source(before,name)),"candidate":digest(function_source(after,name)),"changed":function_source(before,name)!=function_source(after,name)} for name in intended}
    common_start=after.find("const SEEKER_U3_HOJ_MODE_C=");common_end=after.find("function asmHojGuidanceActive",common_start);common=after[common_start:common_end]
    harpoon_start=after.find("const HARPOON_HOJ_C_PROFILE=");harpoon_end=after.find("function runCoreUnitSelfTests(){",harpoon_start);harpoon=after[harpoon_start:harpoon_end]
    checks={"legacyBodyByteEqual":legacy_equal,"commonPresent":common_start>=0 and common_end>common_start,"harpoonAdapterPresent":harpoon_start>=0 and harpoon_end>harpoon_start,
      "assumedThreatDeclared":"'RGM-84D':Object.freeze({terminalHoj:'ASSUMED_THREAT'})" in after,"profileReusesExistingGameAbstraction":"...ASM_SEEKER_PROFILES['Kh-35U']" in harpoon,
      "harpoonIndependentRng":"uniform:()=>harpoonRandomA(m),normal:()=>harpoonNoiseA(m)" in harpoon,"asmRngPreserved":"uniform:simRandom,normal:randn" in common,
      "noMidcoursePassiveRf":"asmPassiveRfMeasurementB2" not in harpoon,"featureGateBeforeSignal":common.find("!ports.enabled()")<common.find("ports.signal("),
      "saveInventorySchemaUnchanged":hashes["harpoonExportA"]["byteEqual"] and hashes["harpoonRestoreA"]["byteEqual"],
      "noNewTruthConsumer":not re.search(r"\b(targetId|entityId|truthPosition|physicalTarget)\b",common+harpoon)}
    passed=not unexpected and all(q["changed"] for q in changed.values()) and all(checks.values())
    result={"schema":"AEGIS_SEEKER_UNIFY_U3_C_SCOPE_1","status":"PASS" if passed else "FAIL","unchangedFunctionHashes":hashes,"unexpectedChangedFunctions":unexpected,"intentionallyChangedFunctionHashes":changed,"checks":checks,"numericPolicy":"REUSE_EXISTING_KH35U_GAME_HOJ_ABSTRACTION_NO_RESULT_FITTING","savedSchemaChanged":False}
    args.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"status":result["status"],"unchangedFunctions":len(unchanged),"unexpected":unexpected,"checks":checks},indent=2));raise SystemExit(0 if passed else 1)


if __name__=="__main__":main()
