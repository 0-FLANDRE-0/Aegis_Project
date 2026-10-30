"""Stage A exact patches; invoked by the pinned HELI_D builder."""
from pathlib import Path
HERE=Path(__file__).resolve().parent

def replace(s,old,new,count=1):
 assert s.count(old)==count,(old[:120],s.count(old),count)
 return s.replace(old,new)

def patch(s):
 # A module follows the flight runtime/UI and precedes the original RF kernel.
 anchor='// PHYSICAL ONLY: runtime identities and geometry stop at anonymous echo extraction.\n'
 s=replace(s,anchor,(HERE/'stage_a.js').read_text()+'\n'+anchor)
 s=replace(s,'    out.push(...navalOrdnanceReflectorsD());','    out.push(...navalOrdnanceReflectorsD());\n    out.push(...heloPhysicalReflectorsE());')
 s=replace(s,"for(const m of targetPool)if(m.alive!==false)sources.push({e:m,key:'AIR:'+m.id,rcs:null,own:false});return sources;","for(const m of targetPool)if(m.alive!==false)sources.push({e:m,key:'AIR:'+m.id,rcs:null,own:false});sources.push(...heloCiwsSourcesE());return sources;")
 s=replace(s,"    for(const e of targetPool)if(e.alive!==false)sources.push({e,key:'AIR:'+e.id,rcs:targetRcsM2(e,metersToWorld(o.xM),metersToWorld(o.yM)),own:false});","    for(const e of targetPool)if(e.alive!==false)sources.push({e,key:'AIR:'+e.id,rcs:targetRcsM2(e,metersToWorld(o.xM),metersToWorld(o.yM)),own:false});\n    sources.push(...heloCiwsSourcesE());")
 s=replace(s,"const operatorIdentity=ownLaunch?ownLaunch.identity:normalizeTrackOperatorIdentityA3(tr._operatorIdentity);","const operatorIdentity=ownLaunch?ownLaunch.identity:(heloFriendlyIffEvidenceE(tr)?'FRIEND':normalizeTrackOperatorIdentityA3(tr._operatorIdentity));",2)
 s=replace(s,"tr.identity=tr._operatorIdentity??'UNKNOWN';tr.threatStatus=","tr.identity=heloFriendlyIffEvidenceE(tr)?'FRIEND':tr._operatorIdentity??'UNKNOWN';tr.threatStatus=")
 s=replace(s,'    stepWeaponsD(dt);','    heloIffStepE(dt);\n    stepWeaponsD(dt);')
 return s
