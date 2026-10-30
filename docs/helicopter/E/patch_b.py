"""Stage B opt-in unified RF and fixed-step surface-only adapter."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def replace(s,old,new,count=1):
 assert s.count(old)==count,(old[:120],s.count(old),count)
 return s.replace(old,new)

def patch(s):
 s=replace(s,'function heloRadarSnapshotE(h){return {radar:null};}',(HERE/'stage_b.js').read_text())
 s=replace(s,'    heloFixedStepA(dt);','    heloFixedStepA(dt);\n    heloRadarFixedStepE(dt);')
 # Missing profile IDs must reach the existing generic size/aspect envelope.
 s=replace(s,"  function surfaceTargetRcsM2Wip13A(obj,band,obsX,obsY){\n    const profile=","  function surfaceTargetRcsM2Wip13A(obj,band,obsX,obsY){\n    if(!obj?.profileId)return null;\n    const profile=")
 s=replace(s,"      const beamGain=Math.exp(-2.7726*((azOff/Math.max(1e-6,halfAz))**2+(elOff/Math.max(1e-6,halfEl))**2)),losQ=terrainAwareRadarLOS(rxX,rxY,rxZ,ref.x,ref.y,ref.z??0,Number(opts.losMarginM)||1.4);if(losQ<=.005)continue;",
 "      const physicalGate=typeof opts.physicalEchoGate==='function'?opts.physicalEchoGate(ref,{azRad:az,horizontalRangeM:h,rangeM}):null;if(physicalGate===false)continue;\n      const beamGain=Math.exp(-2.7726*((physicalGate?.azimuthPeakGain?0:(azOff/Math.max(1e-6,halfAz))**2)+(elOff/Math.max(1e-6,halfEl))**2)),losQ=terrainAwareRadarLOS(rxX,rxY,rxZ,ref.x,ref.y,physicalGate?.propagationHeightM??ref.z??0,Number(opts.losMarginM)||1.4);if(losQ<=.005)continue;")
 s=replace(s,'*health*beamGain*losQ*weatherQ);','*health*beamGain*losQ*weatherQ*(opts.signalScale01??1));')
 return s
