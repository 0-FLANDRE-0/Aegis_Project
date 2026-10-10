"""Pinned Multi Ship B → C. Only packed main record 13 and build labels change."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946'
OLD='v48_WIP_MULTI_SHIP_B';NEW='v48_WIP_MULTI_SHIP_C';PATCHES=[]
def once(s,a,b,label):
    assert s.count(a)==1,(label,s.count(a))
    PATCHES.append(label);return s.replace(a,b,1)
def block(s,a,b,fn,label):
    start=s.index(a);end=s.index(b,start+len(a));PATCHES.append(label)
    return s[:start]+fn(s[start:end])+s[end:]
def build(s):
    s=once(s,'const MULTISHIP_PHYSICAL_SCHEMA_B=', '\n'.join((HERE/n).read_text() for n in ['physical.js','observer.js','offboard.js'])+'\nconst MULTISHIP_PHYSICAL_SCHEMA_B=','owner measurement services')
    s=once(s,"r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';","r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';prepareObserverC(r);",'observer activation')
    s=once(s,'function retirePhysicalShipB(r){r.rescue?.reset?.();','function retirePhysicalShipB(r){retireObserverC(r);r.rescue?.reset?.();','observer retirement')
    s=once(s,'function resetSpySchedulerState(){','function resetSpySchedulerState(){\n    resetObserversC();','observer lifecycle')
    s=once(s,'    updateBridgeMasterERadar(dt);\n    updateMainGunWip13B3(dt);','    updateBridgeMasterERadar(dt);\n    stepObserversC(dt);\n    updateMainGunWip13B3(dt);','once per fixed tick observers')
    # Shared RF field keeps the legacy RNG path when no explicit observer state is passed.
    s=once(s,'physicalRfReflectorRegistryWip13A2({band});SHIPBOARD_RADAR_RF_SCENE_CACHE','physicalRfReflectorRegistryWip13A2({band,includeNavalShips:true});SHIPBOARD_RADAR_RF_SCENE_CACHE','naval scene only for shipboard receivers')
    s=once(s,'    // Terrain is an extended fixed background.','    if(opts.includeNavalShips)out.push(...navalReflectorsC());\n    // Terrain is an extended fixed background.','physical naval echo sources')
    s=once(s,"    if(ref?._physicsKind==='SHIP')return", "    if(ref?._physicsKind==='NAVAL_SHIP')return navalRcsC(ref,band,obsX,obsY,obsZ);\n    if(ref?._physicsKind==='SHIP')return",'owner hull signature')
    s=block(s,'  function shipboardRadarEchoFieldWip13B13(', '  function shipboardRadarDomainEvidenceWip13B13(', lambda t:t.replace("const radarId=String(opts.radarId??'SPY1DV'),", "const random=()=>opts.rngState?observerRandomC(opts.rngState):shipboardRadarRandomWip13B13(opts.radarId),normal=()=>opts.rngState?observerNormalC(opts.rngState):shipboardRadarRandnWip13B13(opts.radarId);\n    const radarId=String(opts.radarId??'SPY1DV'),").replace('    for(const ref of scene){','    for(const ref of scene){\n      if(ref._physicsKind===\'NAVAL_SHIP\'&&ref._truthObject.entityId===(opts.observerShipId??ACTIVE_SHIP_RUNTIME.entityId))continue;\n      if(ref._physicsKind===\'SHIP\'&&opts.observerShipId&&opts.observerShipId===ACTIVE_SHIP_RUNTIME.entityId)continue;').replace('shipboardRadarRandomWip13B13(radarId)','random()').replace('shipboardRadarRandnWip13B13(radarId)','normal()'),'explicit RF random stream')
    # Common air EKF now accepts a measurement origin; default calls remain byte-equivalent.
    s=once(s,'function trackRadarPrediction(tr){','function trackRadarPrediction(tr,meas={}){','explicit air EKF receiver')
    s=block(s,'  function trackRadarPrediction(', '  function trackEkfRadarJacobian(', lambda t:t.replace('const ox=worldToMeters(aircraft.x()),oy=worldToMeters(aircraft.y()),oz=OWN_ALT_M;', 'const ox=worldToMeters(meas.sensorXWorld??aircraft.x()),oy=worldToMeters(meas.sensorYWorld??aircraft.y()),oz=meas.sensorZM??OWN_ALT_M;').replace('const ovx=worldSpeedToMps(aircraft._vx??0),ovy=worldSpeedToMps(aircraft._vy??0),ovz=0;', 'const ovx=meas.sensorVxMps??worldSpeedToMps(aircraft._vx??0),ovy=meas.sensorVyMps??worldSpeedToMps(aircraft._vy??0),ovz=meas.sensorVzMps??0;'),'air receiver kinematics')
    s=s.replace('pr=trackRadarPrediction(tr),H=trackEkfRadarJacobian(pr)','pr=trackRadarPrediction(tr,meas),H=trackEkfRadarJacobian(pr)')
    s=once(s,'physicalFleetSnapshotB:fleetPhysicalSnapshotB,','observerSnapshotC:observerSnapshotC, observerFixtureC:observerFixtureC, observerPhysicalAuditC:observerPhysicalAuditC, observerFacadeC:id=>observerFacadeC(ENGAGEMENT_RUNTIME.ships.get(id)), observerCommandC:observerCommandC, offboardDiagnosticC:offboardDiagnosticC, offboardFixtureC:offboardFixtureC, offboardSnapshotC:()=>offboardSnapshotC(ACTIVE_SHIP_RUNTIME), physicalFleetSnapshotB:fleetPhysicalSnapshotB,','read-only diagnostics and isolated fixtures')
    s=once(s,"sensorSource=source;tr.sensorAge=0;","sensorSource=source;tr.sensorAge=0;\n    if(tr.observationReportsC&&source!=='OFFBOARD_C')tr.observationReportsC.localAtS=simStepCounter*SIM_FIXED_DT;",'local/offboard contribution age')
    s=once(s,'// Non-SPY sensor adapters may still supply Cartesian measurements. They enter the same\n      // canonical covariance track instead of overwriting x/y/v directly.\n      trackEkfUpdateCartesianPosition(tr,meas);','// Non-SPY sensor adapters enter the canonical covariance track.\n      // A first external plot already initialized P from its covariance: do not count it twice.\n      if(!created||source!==\'OFFBOARD_C\')trackEkfUpdateCartesianPosition(tr,meas);','external first covariance counted once')
    s=s.replace('탐지와 교전 AI는 이후 단계에서 추가됩니다.','함정별 레이더 관측을 적용하며, 교전·전자전·AI는 이후 단계입니다.')
    s=s.replace("enemyExecution:'PHYSICAL_ACTIVE_COMBAT_DEFERRED'","enemyExecution:'PHYSICAL_AND_OBSERVER_ACTIVE_COMBAT_DEFERRED'")
    s=once(s,"'nonplayerCombatTransientState','nonplayerDamageControlAndStructuralTimeline'","'nonplayerCombatTransientState','offboardLinksAndReports','nonplayerDamageControlAndStructuralTimeline'",'offboard transient save boundary')
    s=once(s,"radar:{emconActive:true,mastLostV12:shipSystemDamageB(r,'MAST')>=80,spq9bLostV12:false,bridgeMasterELostV48Wip08:false,spq9bAngleRad:0,bridgeMasterEAngleRad:0}","radar:observerRenderStateC(r)",'read-only foreign rotor presentation')
    s=once(s,'illum:{spg62Mounts:[]},auxNav:[],sim:',"illum:{spg62Mounts:[]},auxNav:observerAuxPresentationC(r),sim:",'owner auxiliary presentation')
    s=once(s,"missilePanel.textContent = lines.join('\\n');","const externalLabelC=observationReportLabelC(tracks.get(selectedLockId));if(externalLabelC)lines.push(externalLabelC);\n    missilePanel.textContent = lines.join('\\n');",'CIC measured age and link')
    s=once(s,"'perObserverMeasurements','bidirectionalWeaponRouting'","'bidirectionalWeaponRouting'",'stage physical report') if s.count("'perObserverMeasurements','bidirectionalWeaponRouting'")==1 else s.replace("'perObserverMeasurements','bidirectionalWeaponRouting'","'bidirectionalWeaponRouting'")
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);source=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(source).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
    html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace("C55Packaging.build='V48_WIP_MULTI_SHIP_B'","C55Packaging.build='V48_WIP_MULTI_SHIP_C'")
    a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
