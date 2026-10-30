"""Pinned H2 -> H3 owner surface attack capability. Packed record 13 only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1';OLD='v48_WIP_MULTI_SHIP_H2';NEW='v48_WIP_MULTI_SHIP_H3';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 original=s
 def replace(name,f):
  nonlocal s;s=once(s,extract(original,name),f,name)
 def harpoon(f):
  f=once(f,"if(options.routeProgram||harpoonRuntimeA().routeDraft.pointsM.length)return harpoonRouteGateE(trackId,tubeId,options);","if(!options.attackH3&&(options.routeProgram||harpoonRuntimeA().routeDraft.pointsM.length))return harpoonRouteGateE(trackId,tubeId,options);",'typed attack excludes coordinate search')
  f=once(f,"if(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');","if(!options.attackH3&&(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO'))return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');",'retain generic automatic denial')
  f=once(f,"const authority=surfaceMissileIdentityPolicyWip13C4(tr?._operatorIdentity,'MANUAL',false);","const authority=options.attackH3?attackAuthorityH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3):surfaceMissileIdentityPolicyWip13C4(tr?._operatorIdentity,'MANUAL',false);",'distinct surface attack authority')
  f=once(f,"return {ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,rangeKm:readiness.rangeKm,\n    memory:harpoonMemoryA(tr),muzzleM:muzzle,axis,authority,truthUsed:false};","const result={ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,rangeKm:readiness.rangeKm,\n    memory:harpoonMemoryA(tr),muzzleM:muzzle,axis,authority,truthUsed:false};\n  if(options.attackH3){const safe=attackFinalGuardH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3,result);if(!safe.ok)return bad(safe.reason);}\n  return result;",'request and release native safety recheck')
  return f
 def request(f):
  f=f.replace('function harpoonRequestFireA(trackId=selectedLockId,tubeId=null){','function harpoonRequestFireA(trackId=selectedLockId,tubeId=null,options={}){')
  f=f.replace('harpoonAutoTubeGateD(trackId):harpoonGateA(trackId,tubeId)','harpoonAutoTubeGateD(trackId,options):harpoonGateA(trackId,tubeId,options)')
  f=once(f,"remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};","remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS,...(options.attackH3?{attackH3:options.attackH3}:{})};",'pin exact capability until physical release')
  return f
 def release(f):
  f=once(f,'actualRelease:true,routeProgram:pending.routeProgram}','actualRelease:true,routeProgram:pending.routeProgram,...(pending.attackH3?{attackH3:pending.attackH3}:{})}','release capability recheck')
  f=once(f,"notify('HARPOON H'+serial+", "if(pending.attackH3)attackCommitH3(ACTIVE_SHIP_RUNTIME,pending.attackH3,gate,serial);\n  notify('HARPOON H'+serial+",'only native actual release consumes consent')
  return f
 f=extract(original,'createWeaponContextD')
 for name,patch in [('harpoonGateA',harpoon),('harpoonRequestFireA',request),('harpoonReleaseA',release)]:f=once(f,extract(original,'owner/'+name),patch(extract(original,'owner/'+name)),name+' foreign')
 f=once(f,'return {maneuverCoverageH2:',"return {attackPreviewH3:(id,token)=>{sync();return harpoonAutoTubeGateD(id,{attackH3:token});},attackRequestH3:(id,token)=>{sync();return harpoonRequestFireA(id,null,{attackH3:token});},maneuverCoverageH2:",'owner native capability ports');replace('createWeaponContextD',f)
 for name,patch in [('harpoonGateA',harpoon),('harpoonRequestFireA',request),('harpoonReleaseA',release)]:replace(name,patch(extract(original,name)))
 f=extract(original,'tacticalRestoreH1');f=once(f,'maneuverYieldH2(r);',"maneuverYieldH2(r);attackCancelH3(r,'TACTICAL_CONTROL_YIELDED');",'master mode change cancels preparation');replace('tacticalRestoreH1',f)
 f=extract(original,'resetTacticalFleetH1');f=once(f,'resetManeuverFleetH2();','resetManeuverFleetH2();resetAttackFleetH3();','lifecycle clears attack consent and plans');replace('resetTacticalFleetH1',f)
 f=extract(original,'retirePhysicalShipB');f=once(f,'r.combatSystem.maneuverH2=null;',"attackCancelH3(r,'OWNER_RETIRED',true);r.combatSystem.attackH3=null;r.combatSystem.maneuverH2=null;",'retire owner attack');replace('retirePhysicalShipB',f)
 f=extract(original,'exportPhysicalFleetB');f=once(f,'maneuver:maneuverSettingsH2(r),','attack:attackSettingsH3(r),maneuver:maneuverSettingsH2(r),','foreign settings only');replace('exportPhysicalFleetB',f)
 f=extract(original,'exportOperationalState');f=once(f,'ship:{maneuver:','ship:{attack:attackSettingsH3(ACTIVE_SHIP_RUNTIME),maneuver:','own settings only');f=once(f,"deferred:['maneuverGoals", "deferred:['surfaceAttackConsentPlansAndReleaseCapabilities','maneuverGoals",'never save attack authority');replace('exportOperationalState',f)
 f=extract(original,'restorePreparedPhysicalFleetB');f=once(f,'r.restoredManeuverH2=q.maneuver??null;','r.restoredManeuverH2=q.maneuver??null;r.restoredAttackH3=q.attack??null;','restore only validated foreign settings');replace('restorePreparedPhysicalFleetB',f)
 f=extract(original,'prepareOperationalStateV48Wip11B');f=once(f,'migrateManeuverSaveH2(src,harpoonMigrations);','migrateManeuverSaveH2(src,harpoonMigrations);migrateAttackSaveH3(src,harpoonMigrations);','explicit legacy H2 migration');replace('prepareOperationalStateV48Wip11B',f)
 f=extract(original,'applyPreparedOperationalStateV48Wip11B');f=once(f,'restorePreparedPhysicalFleetB(preparedDeployment,src.fleet);',"restorePreparedPhysicalFleetB(preparedDeployment,src.fleet);if(validation.migrations?.some(q=>q.id==='LEGACY_SURFACE_ATTACK_H3'))for(const r of [preparedDeployment.ally,preparedDeployment.enemy].filter(Boolean))if(!r.restoredAttackH3)r.restoredAttackH3={schema:ATTACK_POLICY_H3.schema,enabled:false};",'legacy pending deployment cannot grant enemy attack');f=once(f,'if(src.ship.maneuver){','if(src.ship.attack){ACTIVE_SHIP_RUNTIME.combatSystem.attackH3=null;ACTIVE_SHIP_RUNTIME.restoredAttackH3=src.ship.attack;prepareAttackH3(ACTIVE_SHIP_RUNTIME);}if(src.ship.maneuver){','own settings after detached preflight');replace('applyPreparedOperationalStateV48Wip11B',f)
 f=extract(original,'validatePhysicalFleetB');f=once(f,'validateManeuverSettingsH2(src.ship?.maneuver,errors);','validateManeuverSettingsH2(src.ship?.maneuver,errors);validateAttackSettingsH3(src.ship?.attack,errors);','strict own attack settings');f=once(f,'validateManeuverSettingsH2(q.maneuver,errors);','validateManeuverSettingsH2(q.maneuver,errors);validateAttackSettingsH3(q.attack,errors);','strict foreign attack settings');f=f.replace("[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_H1_1'","[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_H2_1','AEGIS_NAVAL_PHYSICAL_FLEET_H1_1'");f=f.replace('fleet?.schema===MULTISHIP_PHYSICAL_SCHEMA_B)',"[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_H2_1'].includes(fleet?.schema))").replace('fleet.schema===MULTISHIP_PHYSICAL_SCHEMA_B||q.network',"[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_H2_1'].includes(fleet.schema)||q.network");replace('validatePhysicalFleetB',f)
 for name,anchor,added in [('mountTacticalUiH1','mountManeuverUiH2();','mountAttackUiH3();'),('tacticalUpdateUiH1','maneuverUpdateUiH2();','attackUpdateUiH3();')]:
  f=extract(original,name);f=once(f,anchor,anchor+added,'surface attack FLEET presentation');replace(name,f)
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=', '\n'.join((HERE/x).read_text() for x in ['attack.js','ui.js'])+'\nconst NAVAL_WEAPONS_POLICY_D=','canonical surface attack modules')
 s=once(s,"const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_H2_1';","const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_H3_1';",'H3 fleet schema')
 s=once(s,'stepManeuverFleetH2();\n    checkNavObjective();','stepManeuverFleetH2();\n    stepAttackFleetH3();\n    checkNavObjective();','shared fixed attack command phase')
 s=once(s,'maneuverSnapshotH2:maneuverSnapshotH2,',"attackSnapshotH3:attackSnapshotH3,attackCommandH3:attackCommandH3,attackChartProbeH3:attackChartGuardH3,attackMaskProbeH3:(id,tubeId)=>{const r=ENGAGEMENT_RUNTIME.ships.get(id),spec=r?.context.profile.weapons.harpoon?.tubes.find(q=>q.id===tubeId);return spec?attackLauncherMaskH3(r,spec):{ok:false,reason:'MK141_NOT_INSTALLED'};},maneuverSnapshotH2:maneuverSnapshotH2,",'detached diagnostic and operator ports')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_H2','V48_WIP_MULTI_SHIP_H3')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()
