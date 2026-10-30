"""Pinned H1 -> H2 command-only maneuver utility; packed record13 only."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058';OLD='v48_WIP_MULTI_SHIP_H1';NEW='v48_WIP_MULTI_SHIP_H2';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def build(s):
 original=s
 def replace(name,f):
  nonlocal s;s=once(s,extract(original,name),f,name)
 f=extract(original,'createWeaponContextD');f=once(f,'return {launch,step,operatorIdentity:',"return {maneuverCoverageH2:(observation,pose)=>maneuverCoverageNativeH2(owner,observation,pose,{illuminators:SPG62_ILLUMINATORS,closeIn:ciws,spg62Quality,ciwsGameConstraintsV1}),launch,step,operatorIdentity:",'native owner mask preview');replace('createWeaponContextD',f)
 f=extract(original,'physicalShipCommandB');f=f.replace('function physicalShipCommandB(entityId,command){',"function physicalShipCommandB(entityId,command,origin='OPERATOR'){")
 f=once(f,'if(command.targetSpeedKt!=null)r.navigation.targetSpeedKt=',"if(origin==='OPERATOR'&&(command.targetSpeedKt!=null||command.targetRudder!=null))maneuverNoteOperatorH2(r);if(command.targetSpeedKt!=null)r.navigation.targetSpeedKt=",'validated manual foreign NAV ownership');replace('physicalShipCommandB',f)
 for name in ['addWaypoint','clearRoute','undoLastWp']:
  f=extract(original,name)
  if name=='undoLastWp':f=once(f,'routePoints.pop();','maneuverNoteOperatorH2(ACTIVE_SHIP_RUNTIME);routePoints.pop();','manual route removal')
  else:f=once(f,'{\n','{\n    maneuverNoteOperatorH2(ACTIVE_SHIP_RUNTIME);\n','manual route command')
  replace(name,f)
 f=extract(original,'updateRouteNav').replace('if(!shipNav.manualRudderV15)','if(!maneuverOwnsH2(ACTIVE_SHIP_RUNTIME)&&!shipNav.manualRudderV15)').replace('if(!shipNav.manualSpeedV15&&','if(!maneuverOwnsH2(ACTIVE_SHIP_RUNTIME)&&!shipNav.manualSpeedV15&&');replace('updateRouteNav',f)
 f=extract(original,'tacticalRestoreH1');pos=f.rfind('}');replace('tacticalRestoreH1',f[:pos]+'maneuverYieldH2(r);\n'+f[pos:])
 f=extract(original,'resetTacticalFleetH1');pos=f.rfind('}');replace('resetTacticalFleetH1',f[:pos]+'resetManeuverFleetH2();\n'+f[pos:])
 f=extract(original,'retirePhysicalShipB');f=once(f,'r.combatSystem.tacticalH1=null;','r.combatSystem.maneuverH2=null;r.combatSystem.tacticalH1=null;','retire maneuver owner');replace('retirePhysicalShipB',f)
 f=extract(original,'exportPhysicalFleetB');f=once(f,'tactical:tacticalSettingsH1(r),','maneuver:maneuverSettingsH2(r),tactical:tacticalSettingsH1(r),','foreign maneuver settings');f=once(f,'navigation:jsonSafeCloneV48Wip11A(r.navigation)','navigation:maneuverExportNavigationH2(r)','export original NAV command');replace('exportPhysicalFleetB',f)
 f=extract(original,'exportOperationalState');f=once(f,'ship:{tactical:','ship:{maneuver:maneuverSettingsH2(ACTIVE_SHIP_RUNTIME),tactical:','own maneuver settings');f=once(f,'navigation:jsonSafeCloneV48Wip11A(shipNav)','navigation:maneuverExportNavigationH2(ACTIVE_SHIP_RUNTIME)','own requested NAV baseline');f=once(f,"deferred:['utilityDecisionsPrioritiesAndEffectOwnership'","deferred:['maneuverGoalsScoresAndCommandOwnership','utilityDecisionsPrioritiesAndEffectOwnership'",'maneuver transient deferred');replace('exportOperationalState',f)
 f=extract(original,'restorePreparedPhysicalFleetB');f=once(f,'r.restoredTacticalH1=q.tactical??null;','r.restoredTacticalH1=q.tactical??null;r.restoredManeuverH2=q.maneuver??null;','restore foreign settings only');replace('restorePreparedPhysicalFleetB',f)
 f=extract(original,'prepareOperationalStateV48Wip11B');f=once(f,'migrateTacticalSaveH1(src,harpoonMigrations);','migrateTacticalSaveH1(src,harpoonMigrations);migrateManeuverSaveH2(src,harpoonMigrations);','explicit H1/G/F/B legacy migration');replace('prepareOperationalStateV48Wip11B',f)
 f=extract(original,'applyPreparedOperationalStateV48Wip11B');f=once(f,"for(const key of ['heading','speed','targetSpeedKt','rudder','targetRudder','turnRate','vx','vy','manualSpeedV15','manualRudderV15'])if(key in nav)shipNav[key]=nav[key];","for(const key of ['heading','speed','targetSpeedKt','rudder','targetRudder','turnRate','vx','vy','manualSpeedV15','manualRudderV15'])if(key in nav)shipNav[key]=nav[key];if(src.ship.maneuver?.enabled)for(const k of MANEUVER_NAV_KEYS_H2){if(Object.hasOwn(nav,k))shipNav[k]=nav[k];else delete shipNav[k];}",'restore requested H2 native telegraph');f=once(f,'if(src.ship.tactical){','if(src.ship.maneuver){ACTIVE_SHIP_RUNTIME.combatSystem.maneuverH2=null;ACTIVE_SHIP_RUNTIME.restoredManeuverH2=src.ship.maneuver;prepareManeuverH2(ACTIVE_SHIP_RUNTIME);}if(src.ship.tactical){','own settings after successful preflight');replace('applyPreparedOperationalStateV48Wip11B',f)
 f=extract(original,'validatePhysicalFleetB');f=once(f,'validateTacticalSettingsH1(src.ship?.tactical,errors);','validateTacticalSettingsH1(src.ship?.tactical,errors);validateManeuverSettingsH2(src.ship?.maneuver,errors);validateManeuverNavigationH2(src.ship?.navigation,errors);','strict own H2 settings');f=f.replace("[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_G_1'","[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_H1_1','AEGIS_NAVAL_PHYSICAL_FLEET_G_1'");f=once(f,'validateTacticalSettingsH1(q.tactical,errors);','validateTacticalSettingsH1(q.tactical,errors);validateManeuverSettingsH2(q.maneuver,errors);validateManeuverNavigationH2(q.ship?.navigation,errors);','strict foreign H2 settings');replace('validatePhysicalFleetB',f)
 f=extract(original,'migrateNetworkSaveG');f=f.replace("['AEGIS_NAVAL_PHYSICAL_FLEET_G_1'","['AEGIS_NAVAL_PHYSICAL_FLEET_H1_1','AEGIS_NAVAL_PHYSICAL_FLEET_G_1'");replace('migrateNetworkSaveG',f)
 f=extract(original,'mountTacticalUiH1');pos=f.rfind('}');replace('mountTacticalUiH1',f[:pos]+'mountManeuverUiH2();\n'+f[pos:])
 f=extract(original,'tacticalUpdateUiH1');pos=f.rfind('}');replace('tacticalUpdateUiH1',f[:pos]+'maneuverUpdateUiH2();\n'+f[pos:])
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=', '\n'.join((HERE/x).read_text() for x in ['maneuver.js','ui.js'])+'\nconst NAVAL_WEAPONS_POLICY_D=','canonical command-only maneuver modules')
 s=once(s,"const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_H1_1';","const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_H2_1';",'H2 fleet schema')
 for name in ['rudL','rudR']:
  anchor="document.getElementById('"+name+"').addEventListener('click', () => { shipNav.manualRudderV15=true;";s=once(s,anchor,anchor.replace('shipNav.manualRudderV15=true;',"maneuverNoteOperatorH2(ACTIVE_SHIP_RUNTIME);shipNav.manualRudderV15=true;"),'native rudder manual priority')
 for name in ['spdD','spdU']:
  anchor="document.getElementById('"+name+"').addEventListener('click', () => { ";s=once(s,anchor,anchor+'maneuverNoteOperatorH2(ACTIVE_SHIP_RUNTIME);','native telegraph manual priority')
 s=once(s,'setShipRudderTest: (rudderDeg=0) => {shipNav.manualRudderV15=true;',"setShipRudderTest: (rudderDeg=0) => {maneuverNoteOperatorH2(ACTIVE_SHIP_RUNTIME);shipNav.manualRudderV15=true;",'diagnostic native rudder priority')
 s=once(s,'updateRouteNav();\n    checkNavObjective();','updateRouteNav();\n    stepManeuverFleetH2();\n    checkNavObjective();','one shared fixed tick command phase')
 s=once(s,'tacticalSnapshotH1:tacticalSnapshotH1,','maneuverSnapshotH2:maneuverSnapshotH2,maneuverCommandH2:maneuverCommandH2,maneuverCoverageProbeH2:(id,observation,heading)=>{const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!r)return null;return maneuverCoverageH2(r,observation,{x:worldToMeters(r.navigation.positionWorld.x),y:worldToMeters(r.navigation.positionWorld.y),heading});},maneuverGuardProbeH2:(id,prediction,traffic=[])=>maneuverPathGuardH2(ENGAGEMENT_RUNTIME.ships.get(id),prediction,traffic),tacticalSnapshotH1:tacticalSnapshotH1,','detached maneuver and diagnostic-only preview ports')
 s=once(s,'window.__CORE_SELFTEST_FAILURES__=failures.slice();',"const maneuverH2=maneuverSelfTestH2();if(!maneuverH2.pass)failures.push('MANEUVER_H2 '+JSON.stringify(maneuverH2.checks));window.__CORE_SELFTEST_FAILURES__=failures.slice();",'startup transition self-test')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_H1','V48_WIP_MULTI_SHIP_H2')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sha256':manifest['htmlSha256'],'main':manifest['mainSha256'],'bytes':len(html.encode()),'patches':len(PATCHES)}))
if __name__=='__main__':main()
