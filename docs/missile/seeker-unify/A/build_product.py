#!/usr/bin/env python3
"""Build SEEKER_UNIFY_A by changing only surface-ship RCS supply and metadata."""
from __future__ import annotations

import base64
import difflib
import gzip
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
OUT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
BASE_SHA = "9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unpack(raw: bytes) -> tuple[str, re.Match[bytes]]:
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def one(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one anchor, got {count}")
    return source.replace(old, new, 1)


def one_regex(source: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, lambda _: replacement, source, count=1, flags=re.S)
    if count != 1:
        raise AssertionError(f"{label}: expected one regex match, got {count}")
    return result


def transform(source: str) -> str:
    basis = """// SEEKER_UNIFY_A: public-formula surface-ship RCS reference. Absolute class
// measurements are not public. The 1974 Skolnik grazing-incidence formula is
// used only for total beam-aspect scale; existing section/aspect distributions
// remain authoritative. DDG reduction is SIM_TUNED from public qualitative
// shaping evidence, never fitted to seeker range or combat results.
const SURFACE_SHIP_RCS_BASIS_UNIFY_A=deepFreezeShipProfileV48Wip09({
  schema:'AEGIS_SURFACE_SHIP_RCS_BASIS_SEEKER_UNIFY_A_1',
  formula:{source:'PUBLIC_FORMULA',citation:'M. I. Skolnik, An Empirical Formula for the Radar Cross Section of Ships at Grazing Incidence, IEEE TAES-10(2), 1974, DOI:10.1109/TAES.1974.307935',coefficient:52,frequencyUnit:'MHz',displacementUnit:'1000 metric tonnes',outputUnit:'m2',expression:'52*sqrt(f_MHz)*D_kt^(3/2)'},
  bands:{S:{frequencyMHz:3050,frequencySource:'PUBLIC_VALUE_BRIDGEMASTER_E_PROFILE'},X:{frequencyMHz:9400,frequencySource:'PUBLIC_VALUE_SPS73_PROFILE'},IJ:{frequencyMHz:10000,frequencySource:'SIM_TUNED_IJ_X_BAND_CENTRE_PUBLIC_EXACT_SEEKER_CARRIER_UNKNOWN'}},
  profiles:{
    DDG_119_LATE_FLIGHT_IIA:{displacementKt:9.6524456336,displacementSource:'PUBLIC_VALUE_9500_LONG_TON_FLIGHT_IIA_CONVERTED_TO_METRIC',reductionDb:15,reductionSource:'SIM_TUNED',reductionBasis:'PUBLIC_QUALITATIVE_DDG51_RCS_SHAPING__MIDPOINT_OF_DESIGN_ASSUMPTION_RANGE_10_TO_20_DB'},
    CG_52_LATE_TICONDEROGA:{displacementKt:9.7540672,displacementSource:'PUBLIC_VALUE_9600_LONG_TON_CLASS_CONVERTED_TO_METRIC',reductionDb:0,reductionSource:'SIM_TUNED',reductionBasis:'NO_PUBLIC_CLASS_SPECIFIC_REDUCTION_VALUE__CONVENTIONAL_SPRUANCE_DERIVED_FORM_RETAINS_FORMULA'},
    SOVREMENNY_956:{displacementKt:7.94,displacementSource:'PUBLIC_VALUE_FULL_LOAD',reductionDb:0,reductionSource:'SIM_TUNED',reductionBasis:'NO_PUBLIC_CLASS_SPECIFIC_REDUCTION_VALUE__RETAINS_FORMULA'},
    EMPTY_CONTAINER_TEST_HULK_V1:{displacementKt:24.2,displacementSource:'SIM_TUNED_GAME_EMPTY_HULK_MASS',reductionDb:0,reductionSource:'SIM_TUNED',reductionBasis:'GENERIC_NON_LOW_OBSERVABLE_MERCHANT_HULK'}
  },
  resultFitting:false
});
function seekerUnifyBandA(tag){const s=String(tag??'IJ').toUpperCase().replace('/','');return s==='S'?'S':(s==='X'?'X':'IJ');}
function surfaceShipRcsReferenceUnifyA(profileId,band='IJ'){
  const p=SURFACE_SHIP_RCS_BASIS_UNIFY_A.profiles[profileId];if(!p)return null;const key=seekerUnifyBandA(band),f=SURFACE_SHIP_RCS_BASIS_UNIFY_A.bands[key].frequencyMHz,formulaM2=52*Math.sqrt(f)*Math.pow(p.displacementKt,1.5),beamReferenceM2=formulaM2*Math.pow(10,-p.reductionDb/10);
  return {profileId,band:key,formulaM2,beamReferenceM2,reductionDb:p.reductionDb,displacementKt:p.displacementKt,source:'PUBLIC_FORMULA_PLUS_SIM_TUNED_REDUCTION'};
}
function surfaceShipRcsKnotsUnifyA(profileId,band,legacy){const ref=surfaceShipRcsReferenceUnifyA(profileId,band),beam=Math.max(.001,Number(legacy?.[2])||1),scale=ref?ref.beamReferenceM2/beam:1;return legacy.map(v=>v*scale);}
"""
    source = one(
        source,
        "const DDG_119_LATE_FLIGHT_IIA_PROFILE=deepFreezeShipProfileV48Wip09(wip13c51RegisterProfile({",
        basis + "const DDG_119_LATE_FLIGHT_IIA_PROFILE=deepFreezeShipProfileV48Wip09(wip13c51RegisterProfile({",
        "public RCS basis insertion",
    )
    source = one(
        source,
        "p.signature={source:'SIM_TUNED',areaGeometrySource:'MODEL_REGISTRATION',projectedAreaLut:R.projectedAreaLut,areaToRcsScale:1.6,referenceHeightM:R.mastHeightM,provenance:'Static projected area with empirical RF scale, not measured military RCS.'};",
        "p.signature={source:'PUBLIC_FORMULA_PLUS_SIM_TUNED',rcsBasisId:SURFACE_SHIP_RCS_BASIS_UNIFY_A.schema,areaGeometrySource:'MODEL_REGISTRATION',projectedAreaLut:R.projectedAreaLut,areaToRcsScale:1,referenceHeightM:R.mastHeightM,provenance:'Projected-area LUT preserves relative aspect only; absolute beam total is the public-formula RCS reference.'};",
        "Sovremenny signature metadata",
    )
    source = one(
        source,
        "rcsM2:{S:[140,430,1900,510,230],X:[105,350,1540,410,185],IJ:[78,270,1180,325,145]},minimumM2:12",
        "rcsM2:{S:surfaceShipRcsKnotsUnifyA('EMPTY_CONTAINER_TEST_HULK_V1','S',[140,430,1900,510,230]),X:surfaceShipRcsKnotsUnifyA('EMPTY_CONTAINER_TEST_HULK_V1','X',[105,350,1540,410,185]),IJ:surfaceShipRcsKnotsUnifyA('EMPTY_CONTAINER_TEST_HULK_V1','IJ',[78,270,1180,325,145])},minimumM2:12",
        "hulk banded totals",
    )
    source = one(
        source,
        "  ];\n\n  // Gaussian random (Box-Muller)",
        "  ];\n  const SHIP_RCS_SECTION_BEAM_REFERENCE_UNIFY_A=shipRcsSections.reduce((sum,sec)=>sum+sec.rcsBase*sec.beam,0);\n\n  // Gaussian random (Box-Muller)",
        "section beam reference",
    )
    source = one(source, "function computeShipRCS(observerX, observerY, observerZ){", "function computeShipRCS(observerX, observerY, observerZ, band='IJ'){", "compute signature")
    source = one(
        source,
        "    const sideFac = 1.0 - topFac;\n\n    const results = [];",
        "    const sideFac = 1.0 - topFac;\n    const rcsReference=surfaceShipRcsReferenceUnifyA(ACTIVE_SHIP_PROFILE.id,band),sectionScale=rcsReference?rcsReference.beamReferenceM2/SHIP_RCS_SECTION_BEAM_REFERENCE_UNIFY_A:1;\n\n    const results = [];",
        "section normalization setup",
    )
    source = one(source, "const effRCS = sec.rcsBase * angleW * losW * seaW;", "const effRCS = sec.rcsBase * sectionScale * angleW * losW * seaW;", "section normalized RCS")
    source = one(source, "results.push({ ...sec, effRCS, angleW, losW });", "results.push({ ...sec, scaledBaseRCS:sec.rcsBase*sectionScale, effRCS, angleW, losW });", "section audit field")
    source = one(source, "return { totalRCS, sections: results, relBrg, absRelBrg, topFac };", "return { totalRCS, sections: results, relBrg, absRelBrg, topFac, band:seekerUnifyBandA(band), rcsReference, sectionScale };", "RCS audit result")
    source = one(source, "return computeShipRCS(observerX, observerY, 0).totalRCS;", "return computeShipRCS(observerX, observerY, 0, 'S').totalRCS;", "legacy airborne radar band")
    source = one(
        source,
        "function computeWeightedCentroid(observerX, observerY, observerZ){\n    const rcsData = computeShipRCS(observerX, observerY, observerZ);",
        "function computeWeightedCentroid(observerX, observerY, observerZ, band='IJ'){\n    const rcsData = computeShipRCS(observerX, observerY, observerZ, band);",
        "centroid band",
    )
    source = one(source, "const c=computeWeightedCentroid(em.x,em.y,em.z??10);", "const c=computeWeightedCentroid(em.x,em.y,em.z??10,'IJ');", "ASM centroid band")
    source = one(source, "if(needRcs){const rcsData=computeShipRCS(em.x,em.y,alt);", "if(needRcs){const rcsData=computeShipRCS(em.x,em.y,alt,'IJ');", "ASM RCS band")
    source = one(source, "if(ref?._physicsKind==='SHIP')return Math.max(1,computeShipRCS(obsX,obsY,obsZ).totalRCS);", "if(ref?._physicsKind==='SHIP')return Math.max(1,computeShipRCS(obsX,obsY,obsZ,key).totalRCS);", "registry ownship band")
    new_naval = """function navalRcsC(ref,band,x,y,z){
  const r=ref._truthObject,p=resolveShipProfile(r.profileId),n=r.navigation,a=angNorm(Math.atan2(y-n.positionWorld.y,x-n.positionWorld.x)-n.heading),basis=surfaceShipRcsReferenceUnifyA(r.profileId,band);if(!basis)return Math.max(1,p.geometry.lengthM*ref.physicalBeamM*(.10+.36*Math.abs(Math.sin(a))));
  if(sovHullA(r)){const degA=(a*180/Math.PI%360+360)%360,rows=SOV_REG_A.projectedAreaLut,areaAt=deg=>{const u=(deg%360+360)%360,i=Math.floor(u/15),q=rows[i],next=rows[(i+1)%rows.length];return q[1]+(next[1]-q[1])*(u%15)/15;},aspect=areaAt(degA)/Math.max(1,areaAt(90));return Math.max(1,basis.beamReferenceM2*aspect);}
  // Preserve the legacy DDG/CG NPC aspect envelope, normalized to its beam value.
  const aspect=(.10+.36*Math.abs(Math.sin(a)))/.46;return Math.max(1,basis.beamReferenceM2*aspect);
}"""
    source = one_regex(source, r"function navalRcsC\(ref,band,x,y,z\)\{.*?\n\}", new_naval, "NPC public-formula totals")
    return source


def repack(raw: bytes, source: str, match: re.Match[bytes]) -> bytes:
    packed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(packed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    assert meta
    records = json.loads(meta[1])
    records[13].update(rawBytes=len(source.encode()), gzipBytes=len(packed), sha256=sha(source.encode()))
    if "encodedBytes" in records[13]:
        records[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(records, separators=(",", ":")).encode() + out[meta.end(1):]


raw = BASE.read_bytes()
assert sha(raw) == BASE_SHA
before, match = unpack(raw)
after = transform(before)
output = repack(raw, after, match)
check, _ = unpack(output)
assert check == after
OUT.write_bytes(output)

diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="ASM_SEEKER_A/main.js", tofile="SEEKER_UNIFY_A/main.js"))
(HERE / "changes.diff").write_text(diff)
changed_lines = sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))
build = {
    "schema": "AEGIS_SEEKER_UNIFY_A_BUILD_1",
    "baselineCommit": "a36c6bf032f5af8daaf0822d822fbc08ac00a00c",
    "baselineHtml": BASE.name,
    "baselineHtmlSha256": sha(raw),
    "baselineMainSha256": sha(before.encode()),
    "productHtml": OUT.name,
    "productHtmlSha256": sha(output),
    "productMainSha256": sha(after.encode()),
    "changedSourceLines": changed_lines,
    "changeClass": "SURFACE_SHIP_RCS_SUPPLY_AND_PROVENANCE_ONLY"
}
(HERE / "BUILD.json").write_text(json.dumps(build, indent=2) + "\n")
print(json.dumps(build, indent=2))
