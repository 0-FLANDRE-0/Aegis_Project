"""Pinned E → F. Reuse audited soft-kill kernels with explicit owner bindings."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2'
OLD='v48_WIP_MULTI_SHIP_E';NEW='v48_WIP_MULTI_SHIP_F';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,index,name):
 q=index[name];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],name;return v
def owner_context(source,index):
 parts=[]
 for name in index:
  f=extract(source,index,name)
  if name=='updateSoftKillThreatManager':
   f=f.replace('if(!trackIsDisplayable(tr)) continue;',"if(!trackIsDisplayable(tr)||['FRIEND','NEUTRAL'].includes(tr.identity??tr._operatorIdentity))continue;")
  if name=='mk36FireRound':f=f.replace('id:MK36_RUNTIME_WIP15A.serial++,kind:',"ownerEntityId:owner.entityId,id:'MK214:'+owner.entityId+':'+MK36_RUNTIME_WIP15A.serial++,kind:")
  if name=='bloomMk214Cloud':f=f.replace('id:MK36_RUNTIME_WIP15A.serial++,kind:',"ownerEntityId:owner.entityId,id:'CHAFF:'+owner.entityId+':'+MK36_RUNTIME_WIP15A.serial++,kind:")
  if name=='nulkaFire15B':f=f.replace('const q={id:',"const q={ownerEntityId:owner.entityId,profileId:owner.profileId,id:").replace('nulkaEntities15B().length>=p.maxActiveEntities','nulkaEntities15B().filter(q=>q.ownerEntityId===owner.entityId).length>=p.maxActiveEntities')
  parts.append(f)
 return (HERE/'owner.js').read_text().replace('// @ORIGINAL_EW_FUNCTIONS_F@','\n'.join(parts))
def owner_ocean(source):
 index=json.loads((HERE/'ocean-index.json').read_text());span=extract(source,index,'syncOceanEffects')
 kernel=span.strip().removesuffix(',').replace('syncOceanEffects(st){','function syncOceanEffectsOwnerF(st){',1)
 start=kernel.index('      const env=st.sea?.environment')
 end=kernel.index('      const history=fx.history;',start)
 kernel=kernel[:start]+'      // Shared ocean uniforms are updated by the owning view.\n      fx.last={x,y,time,speed};\n'+kernel[end:]
 kernel=kernel.replace('shipGeometryLayout()','this.ownerRuntime.geometry.layout')
 return (HERE/'ocean.js').read_text().replace('// @ORIGINAL_OWNER_OCEAN_KERNEL_F@',kernel)
def build(s):
 original=s;idx=json.loads((HERE/'patch-index.json').read_text());reuse=json.loads((HERE/'function-index.json').read_text())
 replacements={}
 for name in ['normalizeDeploymentE','validateDeploymentA','syncDeploymentUiA','mountDeploymentUiA','prepareDeploymentA','applyDeploymentA','restorePreparedPhysicalFleetB']:replacements[name]=''
 replacements['restorePreparedPhysicalFleetB']=extract(original,idx,'restorePreparedPhysicalFleetB').replace('function restorePreparedPhysicalFleetB(','function restoreOnePhysicalFleetF(')
 f=extract(original,idx,'validatePhysicalFleetB')
 f=f.replace("fleet.schema!==MULTISHIP_PHYSICAL_SCHEMA_B","![MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(fleet.schema)")
 f=f.replace('fleet.ships.length>1','fleet.ships.length>2').replace("fleet.ships.length!==1","fleet.ships.length!==[src.deployment?.allyProfileId,src.deployment?.enemyProfileId].filter(Boolean).length")
 f=f.replace("!src.deployment?.enemyProfileId","!(src.deployment?.enemyProfileId||src.deployment?.allyProfileId)")
 f=f.replace("if(!q||q.entityId!=='SHIP_SCENARIO_ENEMY_A'||q.profileId!==src.deployment?.enemyProfileId||q.profileRevision!==SHIP_PROFILE_REGISTRY[q.profileId]?.revision)","const role=q?.entityId===DEPLOYMENT_POLICY_F.allyId?'ALLY':q?.entityId===DEPLOYMENT_POLICY_F.enemyId?'ENEMY':null,expected=role==='ALLY'?src.deployment?.allyProfileId:src.deployment?.enemyProfileId;if(!q||!role||seen.has(q.entityId)||q.profileId!==expected||q.profileRevision!==SHIP_PROFILE_REGISTRY[q.profileId]?.revision)")
 f=f.replace("role:'ENEMY'","role").replace("for(const q of fleet.ships){", "const seen=new Set();for(const q of fleet.ships){")
 f=f.replace('const r=createPreparedShipRuntimeA(',"seen.add(q.entityId);if(src.deployment.schema===DEPLOYMENT_POLICY_F.schema){if(q.role!==role||q.faction!==(role==='ALLY'?'FRIENDLY':'HOSTILE'))err('FACTION_F');validateElectronicSettingsF(q.ew,errors);if(!q.ship?.inventory?.softKill15B)err('SOFTKILL_REQUIRED_F');}\n    const r=createPreparedShipRuntimeA(")
 f=f.replace('validateWeaponInventoryD(r,q.ship?.inventory,errors);','validateWeaponInventoryD(r,q.ship?.inventory,errors);if(q.ship?.inventory?.softKill15B)validateSoftKillOwnerF(r,q.ship.inventory,errors);')
 replacements['validatePhysicalFleetB']=f
 f=extract(original,idx,'exportPhysicalFleetB').replace("deploymentConfigA().enemyProfileId?","(deploymentConfigA().enemyProfileId||deploymentConfigA().allyProfileId)?").replace('return {entityId:r.entityId,','return {entityId:r.entityId,role:r.role,faction:r.faction,ew:electronicSettingsF(r),');replacements['exportPhysicalFleetB']=f
 replacements['exportWeaponInventoryD']=extract(original,idx,'exportWeaponInventoryD').replace("schema:'AEGIS_WEAPON_INVENTORY_D_1',","schema:'AEGIS_WEAPON_INVENTORY_D_1',...exportSoftKillOwnerF(r),")
 replacements['restoreWeaponInventoryD']=extract(original,idx,'restoreWeaponInventoryD').replace("if(!q)return;","if(!q)return;restoreSoftKillOwnerF(r,q);")
 replacements['asmNoiseJammerAtSeeker']="function asmNoiseJammerAtSeeker(em,p){return electronicJammerAtReceiverF(em,p,'NOISE');}"
 replacements['asmDeceptionJammerAtSeeker']="function asmDeceptionJammerAtSeeker(em,p){return electronicJammerAtReceiverF(em,p,'DECEPTION');}"
 replacements['asmShipHojEmitterSignal15B']="function asmShipHojEmitterSignal15B(em,s,p){return electronicHojF(em,s,p);}"
 replacements['updateESM']="function updateESM(dt){stepElectronicReceiversF(dt);}"
 replacements['resetObserversC']=extract(original,idx,'resetObserversC').replace('\n}', '\n  if(ACTIVE_SHIP_RUNTIME.ew)resetElectronicFleetF();\n}')
 replacements['retirePhysicalShipB']=extract(original,idx,'retirePhysicalShipB').replace('{retireObserverC(r);','{retireElectronicF(r);retireObserverC(r);')
 replacements['bloomMk214Cloud']=extract(original,idx,'bloomMk214Cloud').replace("function bloomMk214Cloud(cart){","function bloomMk214Cloud(cart){\n    if(cart.ownerEntityId&&cart.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId){const owner=ENGAGEMENT_RUNTIME.ships.get(cart.ownerEntityId);if(owner)return prepareElectronicF(owner).context.bloom(cart);return;}").replace('id:MK36_RUNTIME_WIP15A.serial++,kind:', 'ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,id:MK36_RUNTIME_WIP15A.serial++,kind:')
 replacements['nulkaFire15B']=extract(original,idx,'nulkaFire15B').replace('const q={id:', 'const q={ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,profileId:ACTIVE_SHIP_RUNTIME.profileId,id:').replace('nulkaEntities15B().length>=p.maxActiveEntities','nulkaEntities15B().filter(q=>q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId).length>=p.maxActiveEntities')
 replacements['updateSoftKillThreatManager']=extract(original,idx,'updateSoftKillThreatManager').replace('if(!trackIsDisplayable(tr)) continue;',"if(!trackIsDisplayable(tr)||['FRIEND','NEUTRAL'].includes(tr.identity??tr._operatorIdentity))continue;")
 replacements['applyPreparedOperationalStateV48Wip11B']=extract(original,idx,'applyPreparedOperationalStateV48Wip11B').replace("ledger.markWeaponsDirty('OPERATIONAL_STATE_IMPORT');","ledger.markWeaponsDirty('OPERATIONAL_STATE_IMPORT');if(src.ship.ew)electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,src.ship.ew);")
 replacements['stepObserversC']=extract(original,idx,'stepObserversC')+'\n'
 f=extract(original,idx,'shipboardRadarEchoFieldWip13B13')
 f=f.replace('const clutterLeakRaw=','const electronic=electronicRadarInterferenceF(opts);\n    const clutterLeakRaw=').replace('interference=noise+localClutter','interference=noise*(1+electronic.noise)+localClutter')
 # Replay is a bounded receiver measurement bias, never a truth-associated track.
 f=f.replace('q.rangeM+normal()*rangeSigmaM','q.rangeM+normal()*rangeSigmaM+Math.min(350,electronic.replay*12)')
 replacements['shipboardRadarEchoFieldWip13B13']=f
 for name,value in replacements.items():s=once(s,extract(original,idx,name),value,name)
 save=(HERE/'save.js').read_text().replace('// @ORIGINAL_SOFTKILL_VALIDATOR_F@',extract(original,reuse,'skValidate15B'))
 modules='\n'.join([(HERE/'deployment.js').read_text(),(HERE/'electronic.js').read_text(),owner_context(original,reuse),save,owner_ocean(original)])
 s=once(s,"const MULTISHIP_DEPLOYMENT_LEGACY_SCHEMA_E='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1';",modules,'owner deployment and electronic modules')
 s=once(s,"const MULTISHIP_DEPLOYMENT_SCHEMA_A='AEGIS_DEPLOYMENT_MULTI_SHIP_E_1';","const MULTISHIP_DEPLOYMENT_SCHEMA_A=DEPLOYMENT_POLICY_F.schema;",'versioned deployment F')
 s=once(s,"targetShip:'HULK',enemyProfileId:null,enemyAircraftEnabled:true});","targetShip:'HULK',enemyProfileId:null,allyProfileId:null,enemyAircraftEnabled:true,placementSeed:(Number(window.__NAVAL_SIM_SEED__??1831565813)>>>0),allyEmcon:false,enemyEmcon:false});",'scenario defaults')
 s=once(s,"if(!['ENEMY','UNASSIGNED'].includes(options.role??'UNASSIGNED'))","if(!['ALLY','ENEMY','UNASSIGNED'].includes(options.role??'UNASSIGNED'))",'prepared ally role')
 s=once(s,"runtime.role=role;runtime.executionState=", "runtime.role=role;runtime.faction=['PLAYER','ALLY'].includes(role)?'FRIENDLY':role==='ENEMY'?'HOSTILE':'UNASSIGNED';runtime.executionState=",'canonical faction')
 s=once(s,"const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_B_1';","const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_F_1';",'two-owner fleet schema')
 s=once(s,'let placed=false;for(let ring=0;ring<12&&!placed;ring++)','let placed=r.role===\'ENEMY\';for(let ring=0;ring<12&&!placed;ring++)','enemy open-water search belongs to far placement')
 s=once(s,'    stepObserversC(dt);','    stepObserversC(dt);stepElectronicOwnersF(dt);','fixed-tick independent electronic controllers')
 s=once(s,'!!(deceptJamActive&&em.seekerOn&&j.active','!!(em.seekerOn&&j.active','replay uses actual received foreign emission')
 s=once(s,"ship:{navigation:jsonSafeCloneV48Wip11A(shipNav),shipHP,inventory:","ship:{ew:electronicSettingsF(ACTIVE_SHIP_RUNTIME),navigation:jsonSafeCloneV48Wip11A(shipNav),shipHP,inventory:",'player electronic settings export')
 s=once(s,"deferred:['nonplayerCombatTransientState','offboardLinksAndReports'","deferred:['electronicContactsAndTechniqueTimeline','nonplayerCombatTransientState','offboardLinksAndReports'",'explicit EW transient save boundary')
 s=once(s,'const result=validateDeploymentA(src.deployment);for(const code of result.errors)operationalErrorV48Wip11B(errors,code);',"const result=validateDeploymentA(src.deployment);for(const code of result.errors)operationalErrorV48Wip11B(errors,code);if(src.deployment?.schema===DEPLOYMENT_POLICY_F.schema)validateElectronicSettingsF(src.ship?.ew,errors);",'atomic player EW preflight')
 # Equipment truth markers are limited to own expendables. Remote decoys enter anonymous RF only.
 start=s.index('    // ===== ESM Contacts (bearing-only passive display) =====');end=s.index('    // Ship marker (small ship shape',start);chunk=s[start:end]
 chunk=chunk.replace('for(const q of ownChaffCartridges){','for(const q of ownChaffCartridges.filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){').replace('for(const oc of ownChaffs){','for(const oc of ownChaffs.filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){').replace('for(const q of nulkaEntities15B()){','for(const q of nulkaEntities15B().filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){')
 s=s[:start]+chunk+s[end:];PATCHES.append('CIC owner-only physical expendable markers')
 s=s.replace("button.textContent='배치 함정 보기'","button.textContent='아군함 보기'").replace('const r=physicalShipsB()[0];if(!r){notify(\'배치한 함정이 없습니다.\');return;}',"const r=physicalShipsB().find(q=>q.role==='ALLY');if(!r){notify('배치한 아군함이 없습니다.');return;}")
 s=once(s,'defenseSnapshotE:defenseSnapshotE,','electronicSnapshotF:electronicSnapshotF,electronicCommandF:electronicCommandF,electronicReleaseF:electronicReleaseF,electronicReceiverProbeF:(id,plots)=>electronicAcceptPlotsF(ENGAGEMENT_RUNTIME.ships.get(id),plots),friendlyIffProbeF:id=>friendlyIffPlotsF(ENGAGEMENT_RUNTIME.ships.get(id)),electronicRadarProbeF:electronicRadarInterferenceF,defenseSnapshotE:defenseSnapshotE,','detached electronic diagnostics')
 s=once(s,"missilePanel.textContent = lines.join('\\n');","lines.push(electronicCicTextF());\n    missilePanel.textContent = lines.join('\\n');",'CIC observed ESM summary')
 s=once(s,'function disposePhysicalShipPresenterB(v){','function disposePhysicalShipPresenterB(v){\n  disposeShipOceanEffectsF(v);','dispose owned ocean meshes')
 s=once(s,'v.syncCiwsVisuals(st);\n      // Borrow unused work budget','v.syncCiwsVisuals(st);syncShipOceanEffectsF(this,v,st);\n      // Borrow unused work budget','owner speed and world-history ocean effects')
 s=once(s,'electronicSnapshotF:electronicSnapshotF,','shipOceanEffectsAuditF:shipOceanEffectsAuditF,electronicSnapshotF:electronicSnapshotF,','detached ocean presentation diagnostics')
 s=s.replace("'receiverSpecificEW',",'').replace("'receiverSpecificEW'", "'friendlyNetwork'")
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);source=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(source).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_E','V48_WIP_MULTI_SHIP_F')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'reusedFunctions':len(json.loads((HERE/'function-index.json').read_text())),'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
