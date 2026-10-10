#!/usr/bin/env python3
"""Repack only script 13 from the pinned Harpoon E release; preserve other assets."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842'
OLD='v48_WIP_HARPOON_E'; NEW='v48_WIP_MULTI_SHIP_A'
PATCHES=[]
def once(s,old,new,label):
    if s.count(old)!=1: raise AssertionError((label,s.count(old)))
    PATCHES.append(label); return s.replace(old,new,1)
def span(s,start,end,fn,label):
    a=s.index(start);b=s.index(end,a+len(start)); t=fn(s[a:b]);
    PATCHES.append(label);return s[:a]+t+s[b:]
def build(source):
    s=source
    s=once(s,"const SHIP_STARTUP_SCHEMA=",(HERE/'deployment.js').read_text()+"\nconst SHIP_STARTUP_SCHEMA=",'scenario UI/controller')
    s=once(s,'document.body.appendChild(root);update();','mountDeploymentUiA(root.firstElementChild,root.querySelector("#aegisShipConfirmBtn"));document.body.appendChild(root);update();','initial scenario UI')
    s=once(s,'width:min(560px,96vw);padding:24px;','width:min(560px,96vw);max-height:92vh;overflow:auto;box-sizing:border-box;padding:24px;','mobile selection scroll')
    s=once(s,"root.querySelectorAll('[data-preset]').forEach", "mountDeploymentUiA(root.firstElementChild,root.querySelector('[data-preset]').parentElement);\n    root.querySelectorAll('[data-preset]').forEach",'loadout scenario UI')
    s=once(s,"if(wip125Departed||!shipStartupCanDepart())return false;wip125CommittedLoadout=", "if(wip125Departed||!shipStartupCanDepart())return false;const deploymentPrepared=prepareDeploymentA(MULTISHIP_DEPLOYMENT_STATE_A.draft);applyDeploymentA(deploymentPrepared);if(MULTISHIP_DEPLOYMENT_STATE_A.appliedTarget!==deploymentConfigA().targetShip)spawnSurfaceTraffic();wip125CommittedLoadout=",'atomic departure preflight')
    s=once(s,'function spawnSurfaceTraffic(count=null){','function spawnSurfaceTraffic(count=null){\n    MULTISHIP_DEPLOYMENT_STATE_A.appliedTarget=deploymentConfigA().targetShip;','target configuration bookkeeping')
    s=once(s,'const targetPos=defaultSurfaceTargetPlacementWip13A();', "if(deploymentConfigA().targetShip==='NONE')return surfaceContacts.length;\n    const targetPos=defaultSurfaceTargetPlacementWip13A();",'default target gate')
    s=once(s,'const ENGAGEMENT_RUNTIME=ACTIVE_SHIP_SESSION.engagement;', 'const ENGAGEMENT_RUNTIME=ACTIVE_SHIP_SESSION.engagement;\n'+(HERE/'runtime.js').read_text()+"\nconst MULTISHIP_DAMAGE_REGISTRATION_A=deepFreezeShipProfileV48Wip09("+(HERE/'damage-registration.json').read_text().strip()+');','per-ship context')
    s=once(s,'manualRudderV15:false,c17Ownship:true','manualRudderV15:false,c17Ownship:options.role!=="ENEMY"','role navigation')
    s=once(s,"spawnState:'UNBOUND'", "spawnState:'STATE_BOUND_INACTIVE'",'lifecycle contract')
    s=once(s,"purpose:'ENTITY_IDENTITY_AND_OWNERSHIP_FOUNDATION_ONLY'", "purpose:'INDEPENDENT_STATE_AND_CONTEXT__EXECUTION_DEFERRED'",'stage boundary')
    s=once(s,'const runtime=createShipRuntime(profile,options);\n  if(ENGAGEMENT_RUNTIME.ships.has(runtime.entityId))', 'const id=String(options.entityId??playerShipEntityId(profile));if(ENGAGEMENT_RUNTIME.ships.has(id))throw Error("Duplicate ship runtime: "+id);const runtime=createPreparedShipRuntimeA(profile,options);\n  if(ENGAGEMENT_RUNTIME.ships.has(runtime.entityId))','bound spawning')
    s=once(s,"runtime.lifecycleState='UNBOUND';ENGAGEMENT_RUNTIME.ships.set", "runtime.lifecycleState='STATE_BOUND_INACTIVE';ENGAGEMENT_RUNTIME.ships.set",'spawn state')
    s=once(s,'function bindShipRuntimeSubsystemV48Wip11A(kind,value){\n  const r=ACTIVE_SHIP_RUNTIME;', 'function bindShipRuntimeSubsystemV48Wip11A(kind,value,r=ACTIVE_SHIP_RUNTIME){\n  claimShipMutableRootA(r,kind,value);','explicit binder')
    s=once(s,'function createDamageFloodModel(geo){','function createDamageFloodModel(geo,options={}){','flood profile input')
    s=span(s,'function createDamageFloodModel(', 'function createShipMassLossV16',lambda t:t.replace('ACTIVE_SHIP_PROFILE.damage.flood','(options.profile??ACTIVE_SHIP_PROFILE).damage.flood'),'flood profile reads')
    s=once(s,'const P=ACTIVE_SHIP_PROFILE.damage.control;','const P=(options.profile??ACTIVE_SHIP_PROFILE).damage.control;','damage-control profile')
    s=once(s,'function wip13c52RemapInterior(spaces,portals,equipment,byId,raw,flood){\n const L=shipGeometryLayout()', 'function wip13c52RemapInterior(spaces,portals,equipment,byId,raw,flood,options={}){\n const L=options.geometry??shipGeometryLayout()','remap geometry')
    s=once(s,'window.__C52_INTERIOR_REMAP__={','if(options.publishDiagnostics!==false)window.__C52_INTERIOR_REMAP__={','own diagnostics owner')
    s=once(s,'function createShipInteriorTopologyV48Wip06(flood){','function createShipInteriorTopologyV48Wip06(flood,options={}){','DDG topology input')
    s=span(s,'function createShipInteriorTopologyV48Wip06(', 'let shipInteriorTopologyV48Wip06',lambda t:t.replace('ACTIVE_SHIP_PROFILE.geometry','(options.profile??ACTIVE_SHIP_PROFILE).geometry').replace('shipGeometryLayout()','(options.geometry??shipGeometryLayout())').replace('byId,raw,flood);','byId,raw,flood,options);'),'DDG geometry ownership')
    s=once(s,'function bunkerInteriorAuthored(flood){','function bunkerInteriorAuthored(flood,geometry=shipGeometryLayout()){','CG authored geometry input')
    s=span(s,'function bunkerInteriorAuthored(', 'function createBunkerInterior(',lambda t:t.replace('const L=shipGeometryLayout()','const L=geometry'),'CG authored geometry')
    s=once(s,'function createBunkerInterior(flood){','function createBunkerInterior(flood,geometry=shipGeometryLayout()){','CG topology input')
    s=span(s,'function createBunkerInterior(', 'function bunkerCrewDutyPosts(',lambda t:t.replace('bunkerInteriorAuthored(flood)','bunkerInteriorAuthored(flood,geometry)').replace('shipGeometryLayout()','geometry').replace('geometry=geometry','geometry=shipGeometryLayout()'),'CG topology ownership')
    s=once(s,'function crewDutyPostsV48Wip07(){\n  if(IS_BUNKER)', 'function crewDutyPostsV48Wip07(profile=ACTIVE_SHIP_PROFILE){\n  if(profile.id==="CG_52_LATE_TICONDEROGA")','crew posts profile')
    s=once(s,'const M=V48_WIP07_CREW_DAMAGE_MODEL,defs=ACTIVE_SHIP_PROFILE.crew.departments,', 'const P=options.profile??ACTIVE_SHIP_PROFILE,M=options.profile?{...V48_WIP07_CREW_DAMAGE_MODEL,...P.crew,schema:P.crew.modelId}:V48_WIP07_CREW_DAMAGE_MODEL,defs=P.crew.departments,','crew model profile')
    s=span(s,'function createShipLongitudinalStrengthV48Wip03(', 'let shipLongitudinalStrengthV48Wip03',lambda t:t.replace('wip199HullInterpolatedSection(x)','(options.geometry?.section??wip199HullInterpolatedSection)(x)').replace('wip199HullHalfBeamAt(x,z)','(options.geometry?.halfBeam??wip199HullHalfBeamAt)(x,z)').replace('WIP173_SHIP_BOW_X_M','(options.geometry?.bow??WIP173_SHIP_BOW_X_M)'),'structural geometry input')
    s=once(s,'function createBunkerCiwsRuntime(template){','function createBunkerCiwsRuntime(template,profile=ACTIVE_SHIP_PROFILE,navigation=shipNav){','CG close-in input')
    s=span(s,'function createBunkerCiwsRuntime(', 'function bunker',lambda t:t.replace('ACTIVE_SHIP_PROFILE','profile',100).replace('profile=profile','profile=ACTIVE_SHIP_PROFILE').replace('shipNav.heading','navigation.heading'),'CG close-in ownership')
    a=s.index('  const ciws = IS_BUNKER?');b=s.index('const SHIP_CLOSE_IN_BUILDER_REGISTRY',a);literal=s[a:b].strip()[len('const ciws = '):].strip();assert literal.endswith(';');literal=literal[:-1]
    literal=literal.replace('IS_BUNKER','profile.id==="CG_52_LATE_TICONDEROGA"').replace('ACTIVE_SHIP_PROFILE','profile').replace('WIP199_FINAL_LAYOUT.ciws.phalanx','profile.geometry.hardpoints.phalanx').replace('WIP199_FINAL_LAYOUT.ciws.searam','profile.geometry.hardpoints.seaRam').replace("cueAge:0}):[","cueAge:0},profile,navigation):[")
    s=s[:a]+'function createProfileCloseInRuntimeA(profile,navigation){return '+literal+';}\n  const ciws=createProfileCloseInRuntimeA(ACTIVE_SHIP_PROFILE,shipNav);\n'+s[b:];PATCHES.append('shared CIWS state constructor')
    for name,start,end in [('Radar','  const radar = {','\n\n  // ===== TWS MEM'),('SpyScheduler','  const spyScheduler = {','\n\n  function resetSpySchedulerState')]:
        a=s.index(start);b=s.index(end,a);var='radar' if name=='Radar' else 'spyScheduler';expr=s[a:b].strip().split(' = ',1)[1];assert expr.endswith(';');expr=expr[:-1]
        s=s[:a]+'function createShip'+name+'StateA(){return '+expr+';}\n  const '+var+'=createShip'+name+'StateA();'+s[b:];PATCHES.append('fresh '+name+' constructor')
    for var,name in [('slq32EaState','EaAllocator'),('softKillDoctrineState','SoftKillDoctrine')]:
        start='  let '+var+' = {';a=s.index(start);b=s.index('\n  };',a)+len('\n  };');expr=s[a:b].strip().split(' = ',1)[1][:-1]
        s=s[:a]+'function createShip'+name+'StateA(){return '+expr+';}\n  let '+var+'=createShip'+name+'StateA();'+s[b:];PATCHES.append('fresh '+name+' constructor')
    s=once(s,'function createProfileGunModuleWip13B3(installation,profile=ACTIVE_SHIP_PROFILE){','function createProfileGunModuleWip13B3(installation,profile=ACTIVE_SHIP_PROFILE,ownerOptions={}){','gun owner input')
    s=span(s,'function createProfileGunModuleWip13B3(', 'const SHIP_GUN_BUILDER_REGISTRY',lambda t:t.replace('IS_BUNKER','profile.id==="CG_52_LATE_TICONDEROGA"').replace('hardwareHealth01:wip13b1GunHardwareHealth(spec)','hardwareHealth01:ownerOptions.health?ownerOptions.health(spec):wip13b1GunHardwareHealth(spec)'),'gun installation and health ownership')
    s=once(s,"e.lifecycle={revision:(e.lifecycle.revision||0)+1,lastEvent:'OWNERSHIP_BOUND'};", "r.lifecycleState='OWNERSHIP_BOUND';attachShipContextA(r,'PLAYER');e.lifecycle={revision:(e.lifecycle.revision||0)+1,lastEvent:'OWNERSHIP_BOUND'};",'player context bind')
    for name,path in [('getDamageFloodV1','flooding'),('getDamageControlV1','damage.control'),('getShipInteriorTopologyV48Wip06','interior'),('getShipCrewV21','crew'),('getShipMassLedgerV32','mass'),('getShipDynamicsV15','dynamics'),('getWaveFloodEnvironmentV48Wip05','environment.waveFlood'),('getShipLongitudinalStrengthV48Wip03','damage.strength')]:
        s=once(s,'function '+name+'(){','function '+name+'(runtime=ACTIVE_SHIP_RUNTIME){if(runtime!==ACTIVE_SHIP_RUNTIME){if(!runtime.context)throw Error("SHIP_CONTEXT_UNBOUND");return runtime.'+path+';}','explicit '+name+' owner')
    s=span(s,'function resetEntireSessionV48Wip11A(', 'function runtimeEntityCountsV48Wip11A',lambda t:t.replace('spawnSurfaceTraffic();','applyDeploymentA(prepareDeploymentA(deploymentConfigA()));spawnSurfaceTraffic();'),'full reset prepared ships')
    s=once(s,"forcePreSail:()=>{SHIP_STARTUP_STATE.phase='PREPARING';", "forcePreSail:()=>{SHIP_STARTUP_STATE.phase='PREPARING';MULTISHIP_DEPLOYMENT_STATE_A.committed=null;syncDeploymentUiA();",'preparation reopen')
    s=once(s,'capabilities:{restores:[', 'deployment:deploymentConfigA(),capabilities:{restores:[','deployment export')
    s=once(s,"deferred:['harpoonPrelaunchRouteAndFlight'", "deferred:['enemyShipExecutionAndTransientState','harpoonPrelaunchRouteAndFlight'",'save execution boundary')
    s=once(s,"Object.freeze({id:'aviation',validate:validateOperationalAviationV48Wip11B})", "Object.freeze({id:'aviation',validate:validateOperationalAviationV48Wip11B}),Object.freeze({id:'deployment',validate:validateOperationalDeploymentA})",'deployment codec')
    s=once(s,"'crew','rescue','aviation'])", "'crew','rescue','aviation','deployment'])",'codec inventory')
    s=once(s,'const harpoonMigrations=[];', "const harpoonMigrations=[];if(!Object.hasOwn(src,'deployment')){src.deployment={...MULTISHIP_DEPLOYMENT_DEFAULT_A};harpoonMigrations.push({id:'LEGACY_DEPLOYMENT_MULTI_SHIP_A',policy:'EXPLICIT_HULK_AND_NO_ENEMY'});}",'legacy deployment migration')
    s=once(s,'const resetTransient=options.resetTransient!==false;', 'const preparedDeployment=prepareDeploymentA(src.deployment);\n    const resetTransient=options.resetTransient!==false;','import detached prepare')
    s=once(s,'if(resetTransient)resetEngagementTransientV48Wip11A();resetModules();','if(resetTransient)resetEngagementTransientV48Wip11A();resetModules();applyDeploymentA(preparedDeployment);if(MULTISHIP_DEPLOYMENT_STATE_A.appliedTarget!==deploymentConfigA().targetShip)spawnSurfaceTraffic();','import scenario apply')
    s=once(s,'runtimeOwnershipAuditV48Wip11A:()=>runtimeOwnershipAuditV48Wip11A(),','runtimeOwnershipAuditV48Wip11A:()=>runtimeOwnershipAuditV48Wip11A(),\n    multiShipSnapshotA:multiShipSnapshotA, multiShipIsolationAuditA:multiShipIsolationAuditA, deploymentSnapshotA:deploymentSnapshotA,','new diagnostics')
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    raw=args.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    html=raw.decode();pattern=r'(<script type="application/octet-stream" data-c55-index="13">)(.*?)(</script>)';m=re.search(pattern,html,re.S);assert m
    original=gzip.decompress(base64.b64decode(m[2])).decode();candidate=build(original).replace(OLD,NEW)
    gz=gzip.compress(candidate.encode(),mtime=0);html=html[:m.start(2)]+base64.b64encode(gz).decode()+html[m.end(2):]
    row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW)
    html=html.replace("C55Packaging.build='V48_WIP_HARPOON_E'","C55Packaging.build='V48_WIP_MULTI_SHIP_A'")
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(html);args.output.with_suffix('.main.js').write_text(candidate)
    manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES}
    args.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
