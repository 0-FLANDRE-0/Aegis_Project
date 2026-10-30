"""Pinned C → D. Build-time owner closures reuse audited kernels without eval or swaps."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363'
OLD='v48_WIP_MULTI_SHIP_C';NEW='v48_WIP_MULTI_SHIP_D';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def sam_fuze_source(f,foreign=False):
 a=f.index('    // Prefer seeker-locked target; fall back to assigned')
 b=f.index('    // DIAGNOSTIC: track frame-by-frame fuze state',a)
 legacy=f[a:b]
 select="    killTarget=navalFuzeTargetD(m,ACTIVE_SHIP_RUNTIME);\n    if(killTarget){killX=killTarget.x;killY=killTarget.y;killZ=killTarget.z??0;}\n"
 if not foreign:select="    if(physicalShipsB().length){\n"+select+"    }\n    if(!killTarget){\n"+legacy+"    }\n"
 return f[:a]+select+f[b:]
def factory(source):
 rows=json.loads((HERE/'function-index.json').read_text());parts=[]
 for name,q in rows.items():
  f=source[q['start']:q['end']];assert hashlib.sha256(f.encode()).hexdigest()==q['sha256'],name
  if name=='updateMissileBodyB3':f=sam_fuze_source(f,True)
  if name=='c55SensorSweep':
   a=f.index('    const sources=[];');b=f.index('    for(const src of sources)',a);f=f[:a]+'    const sources=navalCiwsSourcesD(owner);\n'+f[b:]
  if name=='createProfileGunModuleWip13B3':f=f.replace('profile.id==="CG_52_LATE_TICONDEROGA"?{restoreInventory','true?{restoreInventory')
  if name=='spawnMainGunProjectileWip13B3':f=f.replace('mainGunProjectilesWip13B3.push(projectile);',"projectile.ownerEntityId=owner.entityId;projectile.id=owner.entityId+':'+projectile.id;mainGunProjectilesWip13B3.push(projectile);shipMassMarkWeaponsV32('OWNER_GUN_FIRE_D');")
  parts.append(f)
 a=source.index('      const hit=ramSweptClosestHit(rm,prev,dt);')
 b=source.index('    for(let i=ramMissiles.length-1;i>=0;i--)if(!ramMissiles[i].alive)',a)
 fuze=source[a:b].rstrip();assert fuze.endswith('}');fuze=fuze[:-1].replace('continue;','return;')
 return (HERE/'factory.js').read_text().replace('// @GENERATED_OWNER_FUNCTIONS_D@','\n'.join(parts)).replace('// @GENERATED_RAM_FUZE_D@','function ramFuzeD(rm,prev,dt){'+fuze+'\n}')
def build(s):
 modules='\n'.join((HERE/n).read_text() for n in ['runtime.js','contact.js','closein.js','state.js'])+'\n'+factory(s)
 q=json.loads((HERE/'function-index.json').read_text())['updateMissileBodyB3'];a=q['start'];b=q['end'];s=s[:a]+sam_fuze_source(s[a:b])+s[b:]
 s=once(s,'const MULTISHIP_PHYSICAL_SCHEMA_B=',modules+'\nconst MULTISHIP_PHYSICAL_SCHEMA_B=','explicit owner weapon services')
 a=s.index('function createProfileCloseInRuntimeA(');b=s.index('  const ciws=createProfileCloseInRuntimeA(',a);f=s[a:b];f=f.replace('engageRangeKm: GUN_CIWS_RANGE_KM','engageRangeKm: profile.weapons.closeIn.mounts.phalanx.engageRangeKm').replace('engageRangeKm: RAM_CIWS_RANGE_KM','engageRangeKm: profile.weapons.closeIn.mounts.seaRam.engageRangeKm');s=s[:a]+f+s[b:];PATCHES.append('close-in ranges from installed owner profile')
 s=once(s,"r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';prepareObserverC(r);","r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';prepareObserverC(r);prepareWeaponsD(r);",'activate owner weapons')
 s=once(s,'function retirePhysicalShipB(r){retireObserverC(r);','function retirePhysicalShipB(r){retireWeaponsD(r);retireObserverC(r);','retire owner ordnance')
 s=once(s,'function resetSpySchedulerState(){\n    resetObserversC();','function resetSpySchedulerState(){\n    resetObserversC();resetWeaponsD();','reset owned combat transients')
 s=once(s,'    stepObserversC(dt);\n    updateMainGunWip13B3(dt);','    stepObserversC(dt);\n    stepWeaponsD(dt);\n    updateMainGunWip13B3(dt);','one fixed-tick owner execution')
 s=once(s,'if(own)vlsIncidentsStepV23(.1,power01,control,p);','if(own)vlsIncidentsStepV23(.1,power01,control,p);else runtime.weapons.executionD?.context.vlsIncidents(.1,power01,control,p);','owner VLS incidents at native damage-control cadence')
 s=once(s,'    if(opts.includeNavalShips)out.push(...navalReflectorsC());','    if(opts.includeNavalShips||physicalShipsB().length)out.push(...navalReflectorsC());\n    out.push(...navalOrdnanceReflectorsD());','common world RF includes actual ordnance and ships')
 s=once(s,'function harpoonImpactA(m,contact){','function harpoonImpactA(m,contact){\n  if(contact.shipRuntimeD)return navalHarpoonContactD(m,contact);','Harpoon actual naval terminal')
 s=once(s,'function resolveMainGunSurfaceImpactWip13B3(projectile,contact){','function resolveMainGunSurfaceImpactWip13B3(projectile,contact){\n  if(contact.shipRuntimeD)return navalGunContactD(projectile,contact);','gun actual naval terminal')
 s=once(s,'const r=harpoonRuntimeA();if(!r.tubes.length)return;','const r=harpoonRuntimeA();if(!r.tubes.length&&!harpoonWorldA().length&&!harpoonBoostersA().length)return;','world Harpoon flight independent of player installation')
 s=once(s,'surfaceTargetFirstAsmContactWip13A({x:metersToWorld(old.x),y:metersToWorld(old.y),z:old.z},{x:m.x,y:m.y,z:m.z});',"surfaceTargetFirstAsmContactWip13A({x:metersToWorld(old.x),y:metersToWorld(old.y),z:old.z},{x:m.x,y:m.y,z:m.z},null,{sourceShipId:m.ownerEntityId,launchCleared:m.tubeCleared&&m.ageS>2});",'Harpoon launch clearance excludes own source geometry')
 s=once(s,'function resolveSurfaceMissileContactWip13C5(m,contact){','function resolveSurfaceMissileContactWip13C5(m,contact){\n  if(contact?.shipRuntimeD)return navalMissileAtContactD(m,contact);','surface SAM naval actual contact')
 s=once(s,'contact=surfaceTargetFirstAsmContactWip13A(startWorld,endWorld,null);',"contact=surfaceTargetFirstAsmContactWip13A(startWorld,endWorld,null,{sourceShipId:m.ownerEntityId??ACTIVE_SHIP_RUNTIME.entityId,launchCleared:!m.vlsPhase&&m.life>2});",'surface SAM launch clearance')
 s=once(s,'function surfaceTargetFirstAsmContactWip13A(startWorld,endWorld,excludeEntityId=null){','function surfaceTargetFirstAsmContactWip13A(startWorld,endWorld,excludeEntityId=null,navalOptions={}){','shared swept contact receiver')
 s=once(s,"let best=null;for(const entity of surfaceContacts){if(!entity.alive||!entity.targetRuntime||excludeEntityId!=null&&String(entity.entityId)===String(excludeEntityId))continue;", "let best=navalFirstContactD(startWorld,endWorld,{excludeShipId:excludeEntityId,...navalOptions});for(const entity of surfaceContacts){if(!entity.alive||!entity.targetRuntime||excludeEntityId!=null&&String(entity.entityId)===String(excludeEntityId))continue;",'earliest actual ship crossing')
 # Own launch/tuning/scheduler remain unchanged. New contact consumers are inactive without a physical fleet.
 s=once(s,'        updateMissile(m, dt);\n        _wip77RecordTrajectorySample(m);','        const navalPreviousD={x:m.x,y:m.y,z:m.z};\n        updateMissile(m, dt);navalMissileContactD(m,navalPreviousD);\n        _wip77RecordTrajectorySample(m);','player real projectile routing')
 s=once(s,'observerSnapshotC:observerSnapshotC,','weaponsSnapshotD:weaponsSnapshotD, weaponCommandD:weaponCommandD, weaponFixtureD:weaponFixtureD, observerSnapshotC:observerSnapshotC,','detached diagnostics')
 # Extend only physical sensor/strike consumers; no target identity crosses into AI rows.
 for name in ['ramRfMeasurement','ramIrMeasurement','ramSweptClosestHit']:
  a=s.index('  function '+name+'(');b=s.index('  function ',a+14);f=s[a:b];f=f.replace('of enemyMissiles','of navalIncomingOrdnanceD(ACTIVE_SHIP_RUNTIME)');f=f.replace('if(!em.alive)continue;', 'if(em.alive===false||em.dead)continue;');s=s[:a]+f+s[b:]
 a=s.index('  function c55SensorSweep(');b=s.index('  function c55ContactAudit(',a);f=s[a:b];lo=f.index('    const sources=[];');hi=f.index('    for(const src of sources)',lo);f=f[:lo]+"    const sources=physicalShipsB().length?navalCiwsSourcesD(ACTIVE_SHIP_RUNTIME):(()=>{\n"+f[lo:hi]+"return sources;})();\n"+f[hi:];s=s[:a]+f+s[b:]
 s=once(s,'for(const em of enemyMissiles){if(!em.alive)continue;const hit=ciwsBulletSweptHit','for(const em of navalIncomingOrdnanceD(ACTIVE_SHIP_RUNTIME)){if(em.alive===false||em.dead)continue;const hit=ciwsBulletSweptHit','player physical Phalanx strikes')
 s=once(s,'      updateRamSixDof(rm,dt,gd.aYawReq,gd.aPitReq);','      updateRamSixDof(rm,dt,gd.aYawReq,gd.aPitReq);navalMissileContactD(rm,prev);if(!rm.alive)continue;','player RAM naval body contact')
 s=once(s,"deploymentState:ships.length?'ACTIVE':deploymentConfigA().enemyProfileId?'PENDING':'NONE',ships:","deploymentState:ships.length?'ACTIVE':deploymentConfigA().enemyProfileId?'PENDING':'NONE',weaponInventorySchema:'AEGIS_WEAPON_INVENTORY_D_1',ships:",'declared owner ammunition codec')
 s=once(s,"for(const q of fleet.ships){","if(fleet.weaponInventorySchema!=null&&fleet.weaponInventorySchema!=='AEGIS_WEAPON_INVENTORY_D_1')err('WEAPON_SCHEMA_D');for(const q of fleet.ships){if(fleet.weaponInventorySchema&&!q?.ship?.inventory)err('WEAPON_INVENTORY_REQUIRED_D');",'explicit legacy ammunition migration')
 s=once(s,"ship:{navigation:jsonSafeCloneV48Wip11A(r.navigation),shipHP:r.health.shipHP,","ship:{inventory:exportWeaponInventoryD(r),navigation:jsonSafeCloneV48Wip11A(r.navigation),shipHP:r.health.shipHP,",'persist foreign finite ammunition')
 s=once(s,"const n=q.ship?.navigation;if(n)","validateWeaponInventoryD(r,q.ship?.inventory,errors);const n=q.ship?.navigation;if(n)",'atomic foreign weapon validation')
 s=once(s,"const r=prepared.enemy,q=fleet.ships[0];if(!r||!q)return;const src=q.ship;","const r=prepared.enemy,q=fleet.ships[0];if(!r||!q)return;const src=q.ship;r.restoredWeaponInventoryD=src.inventory;",'prepare finite ammunition restore')
 s=once(s,'shipDamageVisual:damage,shipInteriorTopology:r.interior.snapshot(),shipCrewSpatial:r.crew.snapshot(),terminalImpacts:[],armorDamagePatches:[],','shipDamageVisual:damage,shipInteriorTopology:r.interior.snapshot(),shipCrewSpatial:r.crew.snapshot(),terminalImpacts:ownerTerminalRenderD(r),armorDamagePatches:ownerArmorRenderD(r),','receiver-local terminal visuals')
 s=once(s,'terminalImpacts:wip12bTerminalEventsSnapshot(),','terminalImpacts:ownTerminalRenderD(),','player excludes foreign local paths')
 s=once(s,'const damage=createShipDamageVisualStateV1(r.flooding.snapshot(),r.damage.control.snapshot(),r.hitHistory,r.geometry.boxes,{terminalEvents:[]});','const damage=createShipDamageVisualStateV1(r.flooding.snapshot(),r.damage.control.snapshot(),r.hitHistory,r.geometry.boxes,{terminalEvents:ownerTerminalRenderD(r)});','owned terminal damage presentation')
 s=once(s,'v.syncDamageScarsV1(st);v.syncCompartmentInteriorV8(st);','v.syncDamageScarsV1(st);v.syncTerminalImpactVisualsV48Wip12B(st);v.syncCompartmentInteriorV8(st);','native owner terminal path rendering')
 s=once(s,"illum:{spg62Mounts:[]},auxNav:observerAuxPresentationC(r),","...ownerWeaponRenderD(r),auxNav:observerAuxPresentationC(r),",'read-only owned fittings')
 s=once(s,"...ramMissiles.filter(r=>r.alive&&(r.life??0)<Math.max(0,r.maxLife??999)).map(wip163RamRenderState)],","...ramMissiles.filter(r=>r.alive&&(r.life??0)<Math.max(0,r.maxLife??999)).map(wip163RamRenderState)],navalMissilesD:physicalShipsB().flatMap(r=>[...r.weapons.executionD.sam.filter(m=>!m.dead).map(wip148MissileRenderState),...r.weapons.executionD.ram.filter(m=>m.alive).map(wip163RamRenderState)]),",'world renderer owned SAM and RAM')
 s=once(s,'this.syncMissileVisuals(st,dt);','this.syncMissileVisuals({...st,missiles:[...st.missiles,...(st.navalMissilesD??[])]},dt);','physical missiles excluded from operator telemetry')
 s=once(s,"mainGunProjectiles:mainGunProjectilesWip13B3.map(wip13b5MainGunProjectileRenderState),","mainGunProjectiles:[...mainGunProjectilesWip13B3,...physicalShipsB().flatMap(r=>r.weapons.executionD.shells)].map(wip13b5MainGunProjectileRenderState),",'world renderer owned shells')
 s=once(s,"ciwsProjectiles:ciwsBullets.map(wip164CiwsBulletRenderState)","ciwsProjectiles:[...ciwsBullets,...physicalShipsB().flatMap(r=>r.weapons.executionD.bullets)].map(wip164CiwsBulletRenderState)",'world renderer owned tracers')
 s=once(s,"id:'HARPOON-'+m.id,label:'RGM-84D'","id:'HARPOON-'+m.id,ownerEntityId:m.ownerEntityId,label:'RGM-84D'",'Harpoon physical presentation source ownership')
 s=once(s,'harpoons:harpoonRenderStatesA(),harpoonBoosters:','harpoons:harpoonRenderStatesA().filter(m=>m.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId),navalHarpoonsD:harpoonRenderStatesA().filter(m=>m.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId),harpoonBoosters:','foreign Harpoon excluded from own follow/status')
 s=once(s,'this.syncHarpoonVisualsA(st,dt);','this.syncHarpoonVisualsA({...st,harpoons:[...st.harpoons,...(st.navalHarpoonsD??[])]},dt);','render actual world Harpoons without own telemetry')
 s=once(s,'const spec=harpoonTubeSpecA(s.tubeId);if(!spec)return;',"const launchOwner=ENGAGEMENT_RUNTIME.ships.get(s.ownerEntityId??ACTIVE_SHIP_RUNTIME.entityId),spec=launchOwner?.context.profile.weapons.harpoon?.tubes.find(q=>q.id===s.tubeId);if(!spec)return;",'Harpoon launch effects from physical owner')
 s=once(s,'axis=shipGameFrameV1().vectorToWorld(spec.axis),e={id:s.id,tubeId:s.tubeId,','axis=shipBodyFrameB(launchOwner).vectorToWorld(spec.axis),e={id:s.id,ownerEntityId:launchOwner.entityId,tubeId:s.tubeId,','owner launch backblast axis')
 s=once(s,'const p=shipGameRenderPointV1(spec.rear.x,spec.rear.y,spec.rear.z);this.spawnEventFlash','const p=ownerHarpoonPointRenderD(launchOwner.entityId,spec.rear);this.spawnEventFlash','owner launch rear flash')
 s=once(s,'const p=shipGameRenderPointV1(e.spec.rear.x,e.spec.rear.y,e.spec.rear.z),d=e.axis,','const p=ownerHarpoonPointRenderD(e.ownerEntityId,e.spec.rear),d=e.axis,','owner backblast origin')
 s=once(s,'const mouth=shipGameRenderPointV1(e.spec.muzzle.x,e.spec.muzzle.y,e.spec.muzzle.z);','const mouth=ownerHarpoonPointRenderD(e.ownerEntityId,e.spec.muzzle);','owner tube mouth puff')
 s=once(s,'v.syncDamageScarsV1(st);v.syncTerminalImpactVisualsV48Wip12B(st);','syncOwnerHarpoonCapsD(v,st);v.syncDamageScarsV1(st);v.syncTerminalImpactVisualsV48Wip12B(st);','foreign canister lids mirror finite owner inventory')
 s=once(s,"cur=sweep.current,prev=sweep.previous,prevZ=prev.z,contact=sweep.hit,targetContact=surfaceTargetFirstAsmContactWip13A(previousWorld,currentWorld);","cur=sweep.current,prev=sweep.previous,prevZ=prev.z,contact=sweep.hit,targetContact=surfaceTargetFirstAsmContactWip13A(previousWorld,currentWorld,ACTIVE_SHIP_RUNTIME.entityId);\n    if(targetContact?.shipRuntimeD&&targetContact.shipRuntimeD!==ACTIVE_SHIP_RUNTIME&&(!contact||targetContact.hit.t<=contact.t)){const k=em.label??'Kh-35U',spec=WIP12B_LIVE_ORDNANCE[wip12bWeaponKey(k)].spec;navalTerminalD(em,targetContact,{weaponKey:k,spec,armed:em._warheadState!=='DUD',ageS:em.life??20,distanceM:em.flight?.distanceM??12000});em.alive=false;em._deathReason='NAVAL_CONTACT';return;}",'legacy ASM foreign physical contact')
 s=s.replace("'bidirectionalWeaponRouting','receiverSpecificEW'","'receiverSpecificEW'").replace("enemyExecution:'PHYSICAL_AND_OBSERVER_ACTIVE_COMBAT_DEFERRED'","enemyExecution:'OWNER_WEAPONS_ACTIVE_SHADOW_AI_D'")
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace("C55Packaging.build='V48_WIP_MULTI_SHIP_C'","C55Packaging.build='V48_WIP_MULTI_SHIP_D'")
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'reusedOwnerFunctions':len(json.loads((HERE/'function-index.json').read_text())),'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
