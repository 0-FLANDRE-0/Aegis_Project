"""Pinned HELI_E1 -> HELI_F1; exact kernel edits, packed13 only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE_SHA='4515668a06d7efcbae351b8e7b1d433c8c534e2b479c0ea3f1e9a7d826e2a352'
def decoded(s,i=13):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="'+str(i)+r'">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 def edit(old,new,n):
  nonlocal s
  assert s.count(old)==n,(old[:90],s.count(old),n);s=s.replace(old,new)
 # Both LIVE_CANONICAL active and foreign-owner execution closure are patched.
 edit("  // Anonymous offboard reports do not provide local fire-control release authority.\n  if(!heloHarpoonLocalObservationE(tr,cfg.maxTrackAgeS))return bad('LOCAL_SURFACE_OBSERVATION_REQUIRED');\n",'',2)
 edit('surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm,maxRangeKm:cfg.maxLaunchRangeKm})','surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm,maxRangeKm:cfg.maxLaunchRangeKm,includeOffboardAgeF1:true})',2)
 edit('  const readiness=surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm',"  if(Number(tr.sensorAge)>cfg.maxTrackAgeS)return bad('SURFACE_TRACK_COAST_EXPIRED');\n  const readiness=surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm",2)
 # Shared readiness opts in only for Harpoon. SAM/GUN policy stays byte-identical.
 old='measurementAgeS=ages.length?Math.min(...ages):Math.max(0,Number(tr.sensorAge)||0),limitS=SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4.fireControl.maxMeasurementAgeS;'
 new='measurementAgeS=weaponPolicy?.includeOffboardAgeF1&&tr.observationReportsC?Math.min(...ages,Math.max(0,Number(tr.sensorAge)||0)):(ages.length?Math.min(...ages):Math.max(0,Number(tr.sensorAge)||0)),limitS=SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4.fireControl.maxMeasurementAgeS;'
 edit(old,new,2)
 # Remove obsolete helper entirely, not a second permissive authority path.
 a=s.index('function heloHarpoonLocalObservationE(');b=s.index('\n}',a)+2;s=s[:a]+s[b:]
 edit("tr._operatorIdentity=normalized;tr._operatorIdentitySetAtStep=", "tr._operatorIdentity=normalized;tr.identificationEvidence=trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR';tr._operatorIdentitySetAtStep=",1)
 edit("tr.identity=tr._operatorIdentity;return {ok:true};", "tr.identity=tr._operatorIdentity;tr.identificationEvidence=trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR';return {ok:true};",1)
 edit("return {ok:true,trackId:Number(trackId),identity:tr.identity,threatStatus:tr.threatStatus,engagementAuthority:tr.engagementAuthority};", "return {ok:true,trackId:Number(trackId),identity:tr.identity,identificationEvidence:tr.identificationEvidence,threatStatus:tr.threatStatus,engagementAuthority:tr.engagementAuthority};",1)
 edit("identity:'UNKNOWN',threatStatus:'UNASSESSED',engagementAuthority:'WITHHELD'};","identity:'UNKNOWN',identificationEvidence:null,threatStatus:'UNASSESSED',engagementAuthority:'WITHHELD'};",1)
 edit("surfaceSensorContributors:(tr.domain===","identificationEvidence:tr.identificationEvidence??null,surfaceSensorContributors:(tr.domain===",1)
 edit('tr._operatorIdentity=normalizeTrackOperatorIdentityA3(identity);tr._operatorIdentitySetAtStep=simStepCounter;',"tr._operatorIdentity=normalizeTrackOperatorIdentityA3(identity);tr.identificationEvidence=trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR';tr._operatorIdentitySetAtStep=simStepCounter;",1)
 # Track evidence belongs to receiver-owned tracks. Reserved ISAR is never synthesized.
 edit("tr.observationReportsC??={localAtS:priorLocalS,remote:{}};", "tr.observationReportsC??={localAtS:priorLocalS,remote:{}};\n  tr.identificationEvidence??=Number.isFinite(priorLocalS)?'LOCAL_SENSOR':'OPERATOR_ONLY';",1)
 edit("if(tr.observationReportsC&&source!=='OFFBOARD_C')tr.observationReportsC.localAtS=simStepCounter*SIM_FIXED_DT;", "if(source!=='OFFBOARD_C')tr.identificationEvidence??='LOCAL_SENSOR';\n    if(tr.observationReportsC&&source!=='OFFBOARD_C')tr.observationReportsC.localAtS=simStepCounter*SIM_FIXED_DT;",1)
 edit("observerClassifyC(tr,meas);networkNoteLocalG", "tr.identificationEvidence??='LOCAL_SENSOR';observerClassifyC(tr,meas);networkNoteLocalG",1)
 # Fleet/foreign manual wrappers delegate Harpoon quality to the same native gate.
 edit('function fleetTrackGateG(r,id){','function fleetTrackGateG(r,id,weapon=null){',1)
 edit("if(!tr.confirmed||tr.sensorDetected===false||networkLocalAgeG(tr)>2||tr.memActive||tr.reacquiring)return {ok:false,reason:'현지 추적 불충분 / 오래된 관측'};","if(weapon!=='HARPOON'&&(!tr.confirmed||tr.sensorDetected===false||networkLocalAgeG(tr)>2||tr.memActive||tr.reacquiring))return {ok:false,reason:'현지 추적 불충분 / 오래된 관측'};",1)
 edit('const gate=fleetTrackGateG(r,c.trackId);','const gate=fleetTrackGateG(r,c.trackId,c.weapon);',1)
 edit("if(!tr)return bad('NO_TRACK');if(!tr.confirmed||tr.sensorDetected===false||tr.sensorAge>2)return bad('FCS_TRACK_STALE');","if(!tr)return bad('NO_TRACK');if(options.weapon!=='HARPOON'&&(!tr.confirmed||tr.sensorDetected===false||tr.sensorAge>2))return bad('FCS_TRACK_STALE');",1)
 # Record release only after final native recheck and ammunition commit. No extra RNG.
 edit("  harpoonWorldA().push(m);harpoonSyncWorldCoordinatesA(m);getShipMassLedgerV32().markWeaponsDirty('MK141_HARPOON_RELEASE');", "  harpoonJournalReleaseF1(ACTIVE_SHIP_RUNTIME,m,gate,gate.routeProgram?null:tracks.get(gate.trackId));\n  harpoonWorldA().push(m);harpoonSyncWorldCoordinatesA(m);getShipMassLedgerV32().markWeaponsDirty('MK141_HARPOON_RELEASE');",2)
 edit('function harpoonFinishA(m,reason){','function harpoonFinishA(m,reason,contact=null){',1)
 edit('if(!m.alive)return;m.alive=false;m.outcome=reason;m.endedStep=simStepCounter;','if(!m.alive)return;m.alive=false;m.outcome=reason;m.endedStep=simStepCounter;harpoonJournalFinishF1(m,reason,contact);',1)
 edit("harpoonFinishA(m,'NAVAL_CONTACT');", "harpoonFinishA(m,'NAVAL_CONTACT',contact);",1)
 edit("harpoonFinishA(m,'SURFACE_CONTACT');", "harpoonFinishA(m,'SURFACE_CONTACT',contact);",1)
 edit('for(const m of harpoonWorldA())if(m.ownerEntityId===r.entityId)m.alive=false;',"for(const m of harpoonWorldA())if(m.ownerEntityId===r.entityId)harpoonFinishA(m,'OWNER_RETIRED');",1)
 edit('for(const m of harpoonWorldA())harpoonFlightStepA(m,dt);',"for(const m of harpoonWorldA()){harpoonFlightStepA(m,dt);if(!m.alive&&!m.outcome)harpoonJournalFinishF1(m,m._deathReason??'LOST');}",1)
 edit('function harpoonResetA(full=false){','function harpoonResetA(full=false){\n  harpoonJournalResetF1();',1)
 edit('  apsMountPerformanceUiF(panel);','  apsMountPerformanceUiF(panel);harpoonJournalMountF1(panel);',1)
 # Reference-only metadata correction, no numeric/radar model changes.
 edit('const APS_REFS_F=Object.freeze({',"const APS_REFS_F=Object.freeze({\n USER_DESIGN_TARGET:{title:'사용자 감각 목표',status:'물리 근거 또는 공개 장비 제원 아님'},",1)
 for key in ['shortTargetRangeM','longSmallTargetAltitudeM','longSmallTargetRangeM','longSmallTargetHsM','longMediumTargetAltitudeM','longMediumTargetRangeM','longMediumTargetHsM']:
  pat=r"("+key+r":\[[^,]+,)'GENERIC_RADAR_PRINCIPLE'";s,count=re.subn(pat,r"\1'USER_DESIGN_TARGET'",s);assert count==1,key
 edit('// Hawklink transport reads only its own radios and anonymous radar measurements.',(HERE/'engagement.js').read_text()+'\n// Hawklink transport reads only its own radios and anonymous radar measurements.',1)
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_E1','v48_WIP_HELI_F1');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 return html.replace('v48_WIP_HELI_E1','v48_WIP_HELI_F1').replace('V48_WIP_HELI_E1','V48_WIP_HELI_F1'),main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();html,main=build(a.baseline.read_bytes());a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);a.output.with_suffix('.main.js').write_text(main);a.output.with_suffix('.manifest.json').write_text(json.dumps({'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(main.encode()).hexdigest(),'bytes':len(html.encode())},indent=2)+'\n')
