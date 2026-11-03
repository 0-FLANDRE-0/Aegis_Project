#!/usr/bin/env python3
"""Build SEEKER_UNIFY_B from the pinned SEEKER_UNIFY_A product.

U0 can be built in SHADOW mode (legacy gate remains authoritative while both
gates are counted) or ACTIVE mode.  The committed product is ACTIVE only after
the U0 gates pass.  Later U1/U2 transformations are appended in this same
single-pass builder so every anchor remains pinned and auditable.
"""
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
BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
DEFAULT_OUT = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html"
BASE_SHA = "53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8"


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


def transform_u0(source: str, mode: str) -> str:
    mode = mode.upper()
    if mode not in {"SHADOW", "ACTIVE"}:
        raise ValueError(mode)

    target_cue = f"""// SEEKER_UNIFY_B U0: cue uncertainty grows only from information age.
// These are the three frozen SIM_TUNED constants committed before effect tests;
// no target truth, target identity, target profile, or target velocity is read.
const ASM_CUE_BASKET_U0=Object.freeze({{
  schema:'AEGIS_ASM_CUE_BASKET_U0_1',source:'SIM_TUNED',resultFitting:false,
  assumedMaxTargetSpeedMps:18.0,minAcqRangeFloorM:1500,minAcqRangeFrac:0.5,
  mode:'{mode}'
}});
function asmTargetCueStateU0(em){{
  // em.life is missile age, hence launch is time zero in this clock domain.
  return em._targetCueU0??(em._targetCueU0={{schema:'AEGIS_TARGET_CUE_U0_1',rangeRefTimeS:0,bearingRefTimeS:0,source:'LAUNCH',passiveCorrectionAttempts:0,passiveBearingClockUpdates:0}});
}}
function asmTargetCueU0(em){{
  const q=asmTargetCueStateU0(em);
  return {{positionM:{{x:worldToMeters(em.insTgtX),y:worldToMeters(em.insTgtY),z:ASM_SEEKER_PROFILES[em.label]?.aimHeightM??5}},velocityMps:null,
    rangeRefTimeS:q.rangeRefTimeS,bearingRefTimeS:q.bearingRefTimeS,source:q.source}};
}}
function asmTargetCuePassiveBearingUpdateU0(em,measurement,profile,correctedBearingRad){{
  const q=asmTargetCueStateU0(em);q.passiveCorrectionAttempts++;
  const sigma=Math.max(1e-9,Number(profile?.bearingErrorRad)||0),residual=Math.abs(angNorm(measurement.bearingRad-correctedBearingRad));
  q.lastPassiveBearingResidualRad=residual;q.lastPassiveBearingConverged=residual<=3*sigma;
  if(q.lastPassiveBearingConverged){{q.bearingRefTimeS=Math.max(0,Number(em.life)||0);q.source='PASSIVE_BEARING';q.passiveBearingClockUpdates++;}}
  return q.lastPassiveBearingConverged;
}}
function asmCueBasketU0(em,own,p){{
  const cue=asmTargetCueU0(em),now=Math.max(0,Number(em.life)||0),rangeAgeS=Math.max(0,now-cue.rangeRefTimeS),bearingAgeS=Math.max(0,now-cue.bearingRefTimeS);
  const dx=cue.positionM.x-worldToMeters(own.x),dy=cue.positionM.y-worldToMeters(own.y),dz=cue.positionM.z-(own.z??0),rangeM=Math.max(1,Math.hypot(dx,dy,dz)),horizontalM=Math.max(1,Math.hypot(dx,dy));
  const rangeUncertaintyM=ASM_CUE_BASKET_U0.assumedMaxTargetSpeedMps*rangeAgeS,bearingUncertaintyM=ASM_CUE_BASKET_U0.assumedMaxTargetSpeedMps*bearingAgeS,rangeHalfM=Math.max(1200,.12*rangeM,rangeUncertaintyM);
  // The uncertainty basket cannot authorize a direction the physical search
  // pattern never illuminates. This is the existing weapon-profile half-sector,
  // not a new tuned constant.
  const searchHalfAzRad=Number.isFinite(Number(p?.searchSectorAzDeg))?deg(Math.max(0,Number(p.searchSectorAzDeg))):Math.PI;
  return {{cue,rangeM,azRad:Math.atan2(dy,dx),elRad:Math.atan2(dz,horizontalM),rangeLowM:Math.max(rangeM-rangeHalfM,ASM_CUE_BASKET_U0.minAcqRangeFloorM,ASM_CUE_BASKET_U0.minAcqRangeFrac*rangeM),rangeHighM:rangeM+rangeHalfM,azHalfRad:Math.min(searchHalfAzRad,Math.max(deg(5),Math.atan(bearingUncertaintyM/Math.max(rangeM,1)))),searchHalfAzRad,elHalfRad:deg(4),rangeAgeS,bearingAgeS}};
}}
"""
    source = one(
        source,
        "function createAsmSeekerState(label){",
        target_cue + "function createAsmSeekerState(label){",
        "U0 TargetCue and frozen basket insertion",
    )
    source = one(
        source,
        "      deception:null,hoj:null};",
        "      lastCueBasketU0:null,cueLegacyPassCountU0:0,cueExpandedPassCountU0:0,cueExpandedOnlyCountU0:0,\n      deception:null,hoj:null};",
        "U0 seeker diagnostics",
    )

    old_association = """    if(!s._kfX){
      const dx=worldToMeters(em.insTgtX-own.x),dy=worldToMeters(em.insTgtY-own.y),dz=(p.aimHeightM??5)-(own.z??0),cueRange=Math.max(1,Math.hypot(dx,dy,dz)),cueAz=Math.atan2(dy,dx),cueEl=Math.atan2(dz,Math.max(1,Math.hypot(dx,dy)));
      for(const m of measurements){const evidence=clamp(Number(m.targetEvidence)||0,0,1);if(!arhRfCandidateAcceptedWip13B12(s.mode,evidence)){s.lastRejectedLowEvidence++;s.lowEvidenceRejectTotal=(s.lowEvidenceRejectTotal??0)+1;continue;}s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),cueRangeScaleM=Math.max(1200,cueRange*.12),cueAzScaleRad=deg(5),cueElScaleRad=deg(4);
        // ASM_SEEKER_A: before an EKF exists, the launch cue is an acquisition
        // basket, not merely a soft score. Reuse the existing residual scales;
        // no RF/Pd/noise/beam/gimbal or guidance coefficient changes.
        if(rangeErr>cueRangeScaleM||azErr>cueAzScaleRad||elErr>cueElScaleRad)continue;
        const score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/cueRangeScaleM,0,4)-5*clamp(azErr/cueAzScaleRad,0,4)-3*clamp(elErr/cueElScaleRad,0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});}
"""
    new_association = """    if(!s._kfX){
      const basket=asmCueBasketU0(em,own,p),cueRange=basket.rangeM,cueAz=basket.azRad,cueEl=basket.elRad;
      s.lastCueBasketU0={rangeLowM:basket.rangeLowM,rangeHighM:basket.rangeHighM,azHalfDeg:basket.azHalfRad*180/Math.PI,searchSectorAzDeg:basket.searchHalfAzRad*180/Math.PI,rangeAgeS:basket.rangeAgeS,bearingAgeS:basket.bearingAgeS,source:basket.cue.source};
      for(const m of measurements){const evidence=clamp(Number(m.targetEvidence)||0,0,1);if(!arhRfCandidateAcceptedWip13B12(s.mode,evidence)){s.lastRejectedLowEvidence++;s.lowEvidenceRejectTotal=(s.lowEvidenceRejectTotal??0)+1;continue;}s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),cueRangeScaleM=Math.max(1200,cueRange*.12),cueAzScaleRad=deg(5),cueElScaleRad=deg(4);
        // U0 changes only the hard pre-EKF basket. Legacy scales below remain
        // authoritative for scoring, preserving score ordering and RNG use.
        const legacyPass=rangeErr<=cueRangeScaleM&&azErr<=cueAzScaleRad&&elErr<=cueElScaleRad,expandedPass=m.rangeM>=basket.rangeLowM&&m.rangeM<=basket.rangeHighM&&azErr<=basket.azHalfRad&&elErr<=basket.elHalfRad;
        if(legacyPass)s.cueLegacyPassCountU0++;if(expandedPass)s.cueExpandedPassCountU0++;if(expandedPass&&!legacyPass)s.cueExpandedOnlyCountU0++;
        if((ASM_CUE_BASKET_U0.mode==='ACTIVE'?!expandedPass:!legacyPass))continue;
        const score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/cueRangeScaleM,0,4)-5*clamp(azErr/cueAzScaleRad,0,4)-3*clamp(elErr/cueElScaleRad,0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});}
"""
    source = one(source, old_association, new_association, "U0 pre-EKF basket")

    old_passive = """    const r=Math.hypot(dx,dy),az=Math.atan2(dy,dx),corrected=az+angNorm(meas.bearingRad-az)*p.correctionGain*meas.confidence*dt;
    em.insTgtX=o.x+Math.cos(corrected)*r;em.insTgtY=o.y+Math.sin(corrected)*r;return true;"""
    new_passive = """    const r=Math.hypot(dx,dy),az=Math.atan2(dy,dx),corrected=az+angNorm(meas.bearingRad-az)*p.correctionGain*meas.confidence*dt;
    em.insTgtX=o.x+Math.cos(corrected)*r;em.insTgtY=o.y+Math.sin(corrected)*r;asmTargetCuePassiveBearingUpdateU0(em,meas,p,corrected);return true;"""
    source = one(source, old_passive, new_passive, "U0 passive bearing clock")
    return source


def transform_u1(source: str, mode: str) -> str:
    """Install the common DTO/unit/RNG boundary without replacing calculations."""
    mode = mode.upper()
    if mode == "NONE":
        return source
    if mode not in {"SHADOW", "ACTIVE"}:
        raise ValueError(mode)
    layer = f"""// SEEKER_UNIFY_B U1: common DTO/unit/RNG boundary.
// Every calculation below is still delegated to the byte-preserved legacy
// weapon function.  The common layer only materializes anonymous SI DTOs; it
// consumes no RNG, changes no profile object, and returns the legacy value.
const SEEKER_COMMON_U1_MODE='{mode}';
const SEEKER_OBSERVATION_DIMENSION_U1=Object.freeze({{
  ACTIVE_MONOSTATIC_4D:'ACTIVE_MONOSTATIC_4D',SARH_BISTATIC_4D:'SARH_BISTATIC_4D',
  PASSIVE_RF_2D:'PASSIVE_RF_2D',PASSIVE_IR_2D:'PASSIVE_IR_2D'
}});
const seekerFiniteU1=(v,fallback=null)=>v==null?fallback:(Number.isFinite(Number(v))?Number(v):fallback);
const seekerFreezeArrayU1=a=>Object.freeze(Array.from(a??[],v=>seekerFiniteU1(v,0)));
const seekerDtoListU1=(v,make)=>Object.freeze(Array.isArray(v)?v.map(make):[]);
function seekerEchoSampleU1(q={{}},dimension=SEEKER_OBSERVATION_DIMENSION_U1.ACTIVE_MONOSTATIC_4D){{
  const g=q?._g??q;
  return Object.freeze({{schema:'AEGIS_SEEKER_ECHO_SAMPLE_U1',dimension,
    rangeM:seekerFiniteU1(q.rangeM??g.rangeM),pathRangeM:seekerFiniteU1(q.pathRangeM),
    azRad:seekerFiniteU1(q.azRad??q.bearingRad??g.az),elRad:seekerFiniteU1(q.elRad??q.elevationRad??g.el),
    pathRateMps:seekerFiniteU1(q.pathRateMps??q.radialMps??g.radialMps),
    receivedPower:seekerFiniteU1(q.receivedPower??q.receivedPowerNorm??q.signal??q.power),snr:seekerFiniteU1(q.snr),
    apparentRcsM2:seekerFiniteU1(q.apparentRcsM2??q.rcsM2??q.rcs),
    rangeExtentM:seekerFiniteU1(q.rangeExtentM??q.extentRangeM,0),crossExtentM:seekerFiniteU1(q.crossExtentM??q.extentCrossM,0),
    verticalExtentM:seekerFiniteU1(q.verticalExtentM??q.extentVerticalM,0),dopplerSpreadMps:seekerFiniteU1(q.dopplerSpreadMps,0),
    clutterObservable:Object.freeze({{surfaceRelativeDopplerMps:seekerFiniteU1(q.surfaceRelativeDopplerMps),estimatedAltitudeM:seekerFiniteU1(q.estimatedAltitudeM)}})}});
}}
function seekerResolvedCellU1(q={{}},dimension=SEEKER_OBSERVATION_DIMENSION_U1.ACTIVE_MONOSTATIC_4D){{
  const e=seekerEchoSampleU1(q,dimension);
  return Object.freeze({{schema:'AEGIS_SEEKER_RESOLVED_CELL_U1',dimension,rangeM:e.rangeM,pathRangeM:e.pathRangeM,azRad:e.azRad,elRad:e.elRad,
    pathRateMps:e.pathRateMps,snr:e.snr,receivedPower:e.receivedPower,rangeExtentM:e.rangeExtentM,crossExtentM:e.crossExtentM,
    verticalExtentM:e.verticalExtentM,dopplerSpreadMps:e.dopplerSpreadMps,memberCount:Math.max(0,Math.floor(seekerFiniteU1(q._memberCount??q.memberCount,1)))}});
}}
function seekerMeasurementU1(q={{}},dimension=SEEKER_OBSERVATION_DIMENSION_U1.ACTIVE_MONOSTATIC_4D){{
  const values=dimension.endsWith('_2D')?[seekerFiniteU1(q.azRad,0),seekerFiniteU1(q.elRad,0)]:
    [seekerFiniteU1(q.rangeM??q.pathRangeM,0),seekerFiniteU1(q.azRad,0),seekerFiniteU1(q.elRad,0),seekerFiniteU1(q.radialMps??q.pathRateMps,0)];
  let covariance=q.covariance?seekerFreezeArrayU1(q.covariance):null;
  if(!covariance){{const sig=dimension.endsWith('_2D')?[seekerFiniteU1(q.azSigmaRad??(q.azSigmaDeg==null?null:deg(q.azSigmaDeg)),0),seekerFiniteU1(q.elSigmaRad??(q.elSigmaDeg==null?null:deg(q.elSigmaDeg)),0)]:
      [seekerFiniteU1(q.rangeSigmaM,0),seekerFiniteU1(q.azSigmaRad??(q.azSigmaDeg==null?null:deg(q.azSigmaDeg)),0),seekerFiniteU1(q.elSigmaRad??(q.elSigmaDeg==null?null:deg(q.elSigmaDeg)),0),seekerFiniteU1(q.radialVelSigmaMps??q.pathRateSigmaMps,0)];
    const n=sig.length,c=new Array(n*n).fill(0);for(let i=0;i<n;i++)c[i*n+i]=sig[i]*sig[i];covariance=Object.freeze(c);}}
  return Object.freeze({{schema:'AEGIS_SEEKER_MEASUREMENT_U1',dimension,values:Object.freeze(values),covariance,snr:seekerFiniteU1(q.snr),quality:seekerFiniteU1(q.quality??q.confidence)}});
}}
function seekerTargetCueU1(em){{const q=asmTargetCueU0(em);return Object.freeze({{schema:'AEGIS_TARGET_CUE_U1',positionM:Object.freeze({{x:q.positionM.x,y:q.positionM.y,z:q.positionM.z}}),velocityMps:q.velocityMps?Object.freeze({{x:q.velocityMps.x,y:q.velocityMps.y,z:q.velocityMps.z}}):null,rangeRefTimeS:q.rangeRefTimeS,bearingRefTimeS:q.bearingRefTimeS,source:q.source}});}}
function seekerEstimateU1(s={{}},mode=s.mode??'INVALID'){{
  const x=s._kfX??s.x??null,P=s._kfP??s.covariance??[];
  return Object.freeze({{schema:'AEGIS_SEEKER_ESTIMATE_U1',valid:!!(s.trackValid??s.valid),mode:String(mode),
    position:x?Object.freeze({{x:seekerFiniteU1(x[0],0),y:seekerFiniteU1(x[1],0),z:seekerFiniteU1(x[2],0)}}):null,
    velocity:x&&x.length>=6?Object.freeze({{x:seekerFiniteU1(x[3],0),y:seekerFiniteU1(x[4],0),z:seekerFiniteU1(x[5],0)}}):null,
    bearing:Number.isFinite(s.azRad)?Object.freeze({{azRad:s.azRad,elRad:seekerFiniteU1(s.elRad,0)}}):null,
    covariance:seekerFreezeArrayU1(P),ageS:seekerFiniteU1(s.measAgeS??s.lastHitAgeS??s.ageS,0),quality:seekerFiniteU1(s.quality??s.confidence,0)}});
}}
function seekerProfileViewU1(family,p={{}}){{
  const degrees=v=>v==null?null:deg(v),km=v=>v==null?null:Number(v)*1000;
  const f=String(family),view={{schema:'AEGIS_SEEKER_PROFILE_VIEW_U1',family:f,readOnly:true,units:'SI'}};
  if(f==='ASM_WIP22')Object.assign(view,{{instrument:Object.freeze({{maxRangeM:km(p.searchMaxKm)}}),sensitivity:Object.freeze({{referenceRangeM:km(p.snrRefKm),referenceRcsM2:seekerFiniteU1(p.refRcsM2)}}),antenna:Object.freeze({{searchHalfAzRad:degrees(p.searchBeamHalfAzDeg),searchHalfElRad:degrees(p.searchBeamHalfElDeg),trackHalfAzRad:degrees(p.trackBeamHalfAzDeg),trackHalfElRad:degrees(p.trackBeamHalfElDeg),gimbalAzRad:degrees(p.gimbalAzLimitDeg)}}),resolution:Object.freeze({{rangeM:seekerFiniteU1(p.unresolvedRangeM),angleRad:degrees(p.unresolvedAngleDeg),dopplerMps:seekerFiniteU1(p.unresolvedDopplerMps)}})}});
  else if(f==='HARPOON')Object.assign(view,{{instrument:Object.freeze({{maxRangeM:seekerFiniteU1(p.seekerRangeM)}}),sensitivity:Object.freeze({{referenceRangeM:seekerFiniteU1(p.seekerReferenceRangeM),referenceRcsM2:seekerFiniteU1(p.seekerReferenceRcsM2),referenceSnr:seekerFiniteU1(p.seekerReferenceSnr)}}),antenna:Object.freeze({{searchHalfAzRad:seekerFiniteU1(p.seekerBeamHalfRad),searchHalfElRad:seekerFiniteU1(p.seekerBeamHalfElRad),gimbalAzRad:seekerFiniteU1(p.seekerGimbalRad)}})}});
  else if(f==='SAM_ARH')Object.assign(view,{{sensitivity:Object.freeze({{referenceRangeM:km(p.referenceRangeKm),referenceRcsM2:seekerFiniteU1(p.referenceRcsM2),referenceSnr:seekerFiniteU1(p.referenceSnr)}}),antenna:Object.freeze({{searchHalfAzRad:degrees(p.searchBeamHalfDeg),trackHalfAzRad:degrees(p.trackBeamHalfDeg)}}),resolution:Object.freeze({{rangeM:seekerFiniteU1(p.unresolvedRangeM),angleRad:degrees(p.unresolvedAngleDeg),dopplerMps:seekerFiniteU1(p.unresolvedDopplerMps)}})}});
  else if(f==='RAM')Object.assign(view,{{passiveRf:Object.freeze({{frameS:seekerFiniteU1(p.rf?.frameS),gimbalRad:degrees(p.rf?.gimbalDeg)}}),passiveIr:Object.freeze({{frameS:seekerFiniteU1(p.ir?.frameS),gimbalRad:degrees(p.ir?.gimbalDeg)}})}});
  else Object.assign(view,{{hardwareDifference:f==='SARH_BISTATIC'||f.startsWith('RAM_')}});
  return Object.freeze(view);
}}
function seekerRngAdapterU1(uniform,normal){{return Object.freeze({{schema:'AEGIS_SEEKER_RNG_ADAPTER_U1',uniform,normal,seedPolicy:'DELEGATE_EXISTING_HANDLE',advancePolicy:'CALL_THROUGH_ONLY'}});}}
function seekerDelegateU1(stage,legacy,self,args,adapt,rng=null){{const value=legacy.apply(self,args),dto=adapt?adapt(value,args):null;return Object.freeze({{stage,value,dto,rng}});}}
const _u1AsmVisible=asmSeekerVisibleRfReturns;asmSeekerVisibleRfReturns=function(...a){{return seekerDelegateU1('ASM_RAW_ECHO',_u1AsmVisible,this,a,v=>seekerDtoListU1(v,q=>seekerEchoSampleU1(q))).value;}};
const _u1AsmComposite=asmSeekerCompositeReturns;asmSeekerCompositeReturns=function(...a){{return seekerDelegateU1('ASM_RESOLVED_CELL',_u1AsmComposite,this,a,v=>seekerDtoListU1(v,q=>seekerResolvedCellU1(q))).value;}};
const _u1AsmMeasurement=asmSeekerEchoMeasurement;asmSeekerEchoMeasurement=function(...a){{return seekerDelegateU1('ASM_MEASUREMENT',_u1AsmMeasurement,this,a,v=>v?seekerMeasurementU1(v):null,seekerRngAdapterU1(simRandom,randn)).value;}};
const _u1AsmEkf=asmSeekerEkfUpdate;asmSeekerEkfUpdate=function(...a){{return seekerDelegateU1('ASM_EKF_EVENT',_u1AsmEkf,this,a,(_,q)=>seekerEstimateU1(q[0])).value;}};
const _u1SamPool=buildEssmArhEchoPool;buildEssmArhEchoPool=function(...a){{return seekerDelegateU1('SAM_ARH_RAW_ECHO',_u1SamPool,this,a,v=>seekerDtoListU1(v,q=>seekerEchoSampleU1(q))).value;}};
const _u1SamCells=_arhClusterEchoes;_arhClusterEchoes=function(...a){{return seekerDelegateU1('SAM_ARH_RESOLVED_CELL',_u1SamCells,this,a,v=>seekerDtoListU1(v,q=>seekerResolvedCellU1(Array.isArray(q)?q[0]??{{}}:q))).value;}};
const _u1Sarh=_v1UpdateSarhMeasurementCore;_v1UpdateSarhMeasurementCore=function(...a){{const m=a[0];return seekerDelegateU1('SARH_BISTATIC_EVENT',_u1Sarh,this,a,(_,q)=>seekerEstimateU1(q[0]?._sarhRfSeeker??{{}},'SARH'),seekerRngAdapterU1(()=>_sarhSeekerRandom(m),()=>_sarhSeekerRandn(m))).value;}};
const _u1ArhCore=_v1UpdateArhMeasurementCore;_v1UpdateArhMeasurementCore=function(...a){{const m=a[0];return seekerDelegateU1('SAM_ARH_MEASUREMENT_EKF_EVENT',_u1ArhCore,this,a,(_,q)=>seekerEstimateU1(q[0]?._arhRfSeeker??{{}},'ARH'),seekerRngAdapterU1(()=>_arhSeekerRandom(m),()=>_arhSeekerRandn(m))).value;}};
const _u1Harpoon=harpoonRfObservationsA;harpoonRfObservationsA=function(...a){{const m=a[0];return seekerDelegateU1('HARPOON_RAW_ECHO',_u1Harpoon,this,a,v=>seekerDtoListU1(v,q=>seekerEchoSampleU1(q)),seekerRngAdapterU1(()=>harpoonRandomA(m),()=>harpoonNoiseA(m))).value;}};
const _u1RamRf=ramRfMeasurement;ramRfMeasurement=function(...a){{return seekerDelegateU1('RAM_PASSIVE_RF',_u1RamRf,this,a,v=>v?seekerMeasurementU1(v,SEEKER_OBSERVATION_DIMENSION_U1.PASSIVE_RF_2D):null,seekerRngAdapterU1(simRandom,gaussRand)).value;}};
const _u1RamIr=ramIrMeasurement;ramIrMeasurement=function(...a){{return seekerDelegateU1('RAM_PASSIVE_IR',_u1RamIr,this,a,v=>v?seekerMeasurementU1(v,SEEKER_OBSERVATION_DIMENSION_U1.PASSIVE_IR_2D):null,seekerRngAdapterU1(simRandom,gaussRand)).value;}};
window.__SEEKER_COMMON_U1__=Object.freeze({{schema:'AEGIS_SEEKER_COMMON_U1_1',mode:SEEKER_COMMON_U1_MODE,units:Object.freeze({{distance:'m',angle:'rad',velocity:'m/s',rcs:'m2',covariance:'SI_squared',snr:'dimensionless'}}),dimensions:SEEKER_OBSERVATION_DIMENSION_U1,
  echoSample:seekerEchoSampleU1,resolvedCell:seekerResolvedCellU1,measurement:seekerMeasurementU1,targetCue:seekerTargetCueU1,estimate:seekerEstimateU1,profileView:seekerProfileViewU1,rngAdapter:seekerRngAdapterU1,
  delegates:Object.freeze(['asmSeekerVisibleRfReturns','asmSeekerCompositeReturns','asmSeekerEchoMeasurement','asmSeekerEkfUpdate','buildEssmArhEchoPool','_arhClusterEchoes','_v1UpdateSarhMeasurementCore','_v1UpdateArhMeasurementCore','harpoonRfObservationsA','ramRfMeasurement','ramIrMeasurement']),truthUsed:false}});
"""
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    return one(source, anchor, layer + "\n" + anchor, "U1 common DTO boundary")


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("SHADOW", "ACTIVE"), default="ACTIVE")
    parser.add_argument("--u1-mode", choices=("NONE", "SHADOW", "ACTIVE"), default="NONE")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--receipt", type=Path, default=HERE / "BUILD.json")
    args = parser.parse_args()

    raw = BASE.read_bytes()
    assert sha(raw) == BASE_SHA
    before, match = unpack(raw)
    after = transform_u1(transform_u0(before, args.mode), args.u1_mode)
    output = repack(raw, after, match)
    check, _ = unpack(output)
    assert check == after
    args.out.write_bytes(output)

    diff = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="SEEKER_UNIFY_A/main.js", tofile="SEEKER_UNIFY_B/main.js"))
    if args.mode == "ACTIVE":
        (HERE / "changes.diff").write_text(diff)
    build = {
        "schema": "AEGIS_SEEKER_UNIFY_B_BUILD_1",
        "baselineCommit": "ba9bc114485838b52450164d5af026fd3d8f5e88",
        "baselineHtml": BASE.name,
        "baselineHtmlSha256": sha(raw),
        "baselineMainSha256": sha(before.encode()),
        "mode": args.mode,
        "u1Mode": args.u1_mode,
        "productHtml": args.out.name,
        "productHtmlSha256": sha(output),
        "productMainSha256": sha(after.encode()),
        "changedSourceLines": sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))),
        "u0Constants": json.loads((HERE / "U0_FROZEN_CONSTANTS.json").read_text()),
    }
    args.receipt.write_text(json.dumps(build, indent=2) + "\n")
    print(json.dumps(build, indent=2))


if __name__ == "__main__":
    main()
