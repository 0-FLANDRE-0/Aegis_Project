"""Pinned D → E. Original AUTO/BDA functions are bound inside the existing owner context."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e'
OLD='v48_WIP_MULTI_SHIP_D';NEW='v48_WIP_MULTI_SHIP_E';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(source,index,name):
 q=index[name];f=source[q['start']:q['end']];assert hashlib.sha256(f.encode()).hexdigest()==q['sha256'],name;return f
def controller(source):
 index=json.loads((HERE/'function-index.json').read_text());parts=[]
 for name in index:
  f=extract(source,index,name)
  if name=='trackEngagementGateA3':f=once(f,'const tr=tracks.get(Number(trackId));',"const pre=defenseGateE(trackId,opts);if(!pre.ok)return pre;const tr=tracks.get(Number(trackId));",'fresh owner safety in native authority')
  if name=='hardKillExistingEngagementCounts':
   a=f.index('PHALANX:');f=f[:a]+"PHALANX:ciws.filter(m=>m.trackingTrackId===trackId&&m.firing).length\n    };\n  }";PATCHES.append('measured Phalanx engagement count without truthRef')
  if name=='wip11cRetirementTrackId':
   f="function wip11cRetirementTrackId(em,opt={}){const id=opt.trackId??opt.engagementTrackId;return Number.isFinite(Number(id))&&id!=null?Number(id):null;}";PATCHES.append('physical retirement cannot resolve foreign numeric IDs in player truth map')
  if name=='wip11cQueueAsmRetirement':f=once(f,'engagementTrackId:trackId,trackCorrelation:',"engagementTrackId:null,observerShipId:owner.entityId,trackCorrelation:",'world wreckage carries no foreign local track ID')
  if name=='wip119FireOne':f=once(f,"if(engagementControlMode!==WIP119_ENGAGEMENT_MODES.AUTO)return {ok:false,reason:'MODE'};","if(engagementControlMode!==WIP119_ENGAGEMENT_MODES.AUTO)return {ok:false,reason:'MODE'};const releaseGate=trackEngagementGateA3(pending.trackId,{automatic:true,mode:'AUTO'});if(!releaseGate.ok)return releaseGate;",'pending salvo actual release authority recheck')
  if name=='wip121TransferEngagementMemory':
   f=once(f,'if(selectedLockId===oldId)',"const oldHandoff=WIP122_SM2_HANDOFF_MEMORY.get(oldId);if(oldHandoff){WIP122_SM2_HANDOFF_MEMORY.delete(oldId);WIP122_SM2_HANDOFF_MEMORY.set(newId,oldHandoff);}for(const p of defenseE.closeIn.values())if(p.command.trackId===oldId)p.command.trackId=newId;for(const m of [...missiles,...ramMissiles])if((m.assignedTargetId??m.targetId)===newId)m.ownerTrackKeyD=ownerTrackKeyD(owner.entityId,newId);for(const mount of ciws)for(const file of c55Bank(mount).files.values())if(file.cmsTrackId===oldId)file.cmsTrackId=newId;if(selectedLockId===oldId)",'atomic native alias transfers owner keys, handoff, CIWS consent/files')
  parts.append(f)
 return '\n'.join(parts)
def owner_context(source,index):
 f=extract(source,index,'createWeaponContextD');template=(HERE.parent/'D/factory.js').read_text()
 for name in ['updateTrackOperationalStateA3','trackEngagementGateA3','wip121TargetSupportBlocked','wip119ReserveAvailable','wip118TrackAcceleration','hardKillExistingEngagementCounts','wip11cQueueAsmRetirement','wip173RecordInterceptBurst']:
  m=re.search(r'^  function '+name+r'\(.*?(?=^  function |^  // Shared world)',template,re.M|re.S);assert m,name
  old=m[0].rstrip();f=once(f,old,'','replace D facade with original owner '+name)
 f=once(f,"selectedMslType='ARH',wip118ControlState={assessments:new Map(),accel:new Map(),recentInterceptEvents:[],interceptSeenKeys:new Set()},","selectedMslType='ARH',",'native owner control state')
 f=once(f,"engagementControlMode='MANUAL',","engagementControlMode='AUTO',",'default enemy self defense AUTO')
 f=once(f,"SPG62_RESERVATION_META={lastPlanStep:-1,hardwareSig:'',engagementSig:'',revision:0},",'','reservation metadata uses native mutable binding')
 f=once(f,'  const SHIP_EXTERNAL_GEOMETRY=',"  let SPG62_RESERVATION_META={lastPlanStep:-1,lastHardwareSig:'',lastEngagementSig:'',revision:0,lastPlanMs:0,failed:[]};\n  const SHIP_EXTERNAL_GEOMETRY=",'offline reset preserves original SPG reservation lifecycle')
 f=once(f,'function sync(){',(HERE/'owner.js').read_text()+'\n'+controller(source)+'\n  function sync(){','audited original control functions')
 f=once(f,'sync();allocateDatalinks();','sync();defenseStepE();allocateDatalinks();','one fixed-tick defense step, native 5Hz decision schedule')
 f=once(f,'    c55StepSensors(dt);','    c55StepSensors(dt);defenseCloseInE();','independent local radar consent')
 f=once(f,'function sync(){emconActive=observerC(owner).emcon;',"function sync(){const o=observerC(owner);for(const q of o.normals)spyScheduler.faces[q.id].load01=clamp(q.usedMs/Math.max(.001,o.model.spy1dv.schedulerFaceBudgetMs*observerHealthC(owner,q.moduleName)),0,1);emconActive=o.emcon;",'weapon support reads actual owner radar face budget')
 f=once(f,'return {launch,step,vlsIncidents:',"return {launch,step,authority:(id,options)=>{sync();return trackEngagementGateA3(id,options);},defenseMode:defenseModeE,defenseSnapshot:defenseSnapshotOwnerE,effectReport:wip121RecordFriendlyInterceptEvent,vlsIncidents:",'owner defense ports')
 return f
def close_in(source,index):
 f=extract(source,index,'ownerCloseInTickD')
 f=f.replace('function ownerCloseInTickD(r,dt,h){','function ownerCloseInOneTickE(r,dt,h,p){').replace('const e=r.weapons.executionD,p=e.closeInPending;if(!p)return;','const e=r.weapons.executionD;if(!p)return;')
 f=f.replace('ownerTrackGateD(r,c.trackId)','ownerTrackGateD(r,c.trackId,c)')
 f=f.replace('simStepCounter>=p.expiresStep','simStepCounter>p.expiresStep')
 f=f.replace('e.closeInPending=null;','clearOwnerCloseInE(r,p);')
 f=once(f,"if((mount.reloadTimer??0)>0)return;","if((mount.reloadTimer??0)>0||c.automatic&&mount.ammo<=HARD_KILL_DOCTRINE.ramReserveRounds)return;",'actual RAM reserve recheck')
 f=once(f,"if(count>0){mount.firing=true;","if(count>0){mount.firing=true;",'native gun burst retained')
 f=f.replace("if(count>0){mount.firing=true;r.mass.markWeaponsDirty('PHALANX_FIRE');clearOwnerCloseInE(r,p);}","if(count>0){mount.firing=true;r.mass.markWeaponsDirty('PHALANX_FIRE');recordOwnerCloseInE(r,p,count);if(!c.automatic)clearOwnerCloseInE(r,p);}")
 f=f.replace("mount.ammo--;mount.reloadTimer=health.reloadIntervalS;clearOwnerCloseInE(r,p);", "mount.ammo--;mount.reloadTimer=health.reloadIntervalS;recordOwnerCloseInE(r,p,1);clearOwnerCloseInE(r,p);")
 helpers="""
function clearOwnerCloseInE(r,p){if(p.command.automatic)r.weapons.executionD.defenseE.closeIn.delete(p.mountId);else r.weapons.executionD.closeInPending=null;}
function recordOwnerCloseInE(r,p,count){const log=r.weapons.executionD.defenseE.closeInLog;log.push({step:simStepCounter,mountId:p.mountId,trackId:p.command.trackId,weapon:p.command.weapon,rounds:count,mode:p.command.automatic?'AUTO':'MANUAL',truthUsed:false});if(log.length>128)log.shift();}
function ownerCloseInTickD(r,dt,h){const e=r.weapons.executionD,manual=e.closeInPending;if(manual)ownerCloseInOneTickE(r,dt,h,manual);for(const p of [...e.defenseE.closeIn.values()])if(p.mountId!==manual?.mountId)ownerCloseInOneTickE(r,dt,h,p);}
"""
 PATCHES.append('per-mount continuous authorized close-in bursts with native solver/slew/ammo/ballistics')
 return f+helpers
def build(s):
 original=s;idx=json.loads((HERE/'patch-index.json').read_text())
 for name in ['createWeaponContextD','ownerCloseInTickD']:
  old=extract(original,idx,name);new=owner_context(original,idx)if name=='createWeaponContextD'else close_in(original,idx);s=once(s,old,new,name)
 f=extract(original,idx,'ownerTrackGateD');f=once(f,"if(options.automatic||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('SHADOW_AI_ONLY');","if(options.automatic)return r.weapons.executionD.context.authority(id,{...options,mode:'AUTO'});if(options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('OWNER_AUTOMATIC_PORT_REQUIRED');",'owner AUTO cannot masquerade as manual consent');s=once(s,extract(original,idx,'ownerTrackGateD'),f,'owner command gate')
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=',(HERE/'runtime.js').read_text()+'\n'+(HERE/'physics.js').read_text()+'\nconst NAVAL_WEAPONS_POLICY_D=','independent defense service')
 s=once(s,'for(const em of enemyMissiles)if(!em.alive&&em._wip11cRetirementQueued&&!em._wip11cWreckCreated)','for(const em of navalRetirementObjectsE())if((em.alive===false||em.dead)&&em._wip11cRetirementQueued&&!em._wip11cWreckCreated)','all real naval ordnance breakup keeps native physical wreckage')
 s=once(s,"r.combatSystem.engagementControl.execution='SHADOW_DECISIONS_D';","r.combatSystem.engagementControl.execution='OWNER_DEFENSE_AI_E';",'canonical owner execution flag')
 s=once(s,'e.context.step(dt);shadowDecisionsD(r);','e.context.step(dt);if(e.defenseE.mode===\'HOLD\')shadowDecisionsD(r);','actual automation log separate from advisory shadow')
 s=once(s,'schema:NAVAL_WEAPONS_POLICY_D.schema,activeAI:false,ships:',"schema:NAVAL_WEAPONS_POLICY_D.schema,activeAI:physicalShipsB().some(r=>r.weapons.executionD?.defenseE.mode==='AUTO'),ships:",'detached defense activation snapshot')
 s=once(s,'weaponsSnapshotD:weaponsSnapshotD,','defenseSnapshotE:defenseSnapshotE,defenseCommandE:defenseCommandE,defenseFixtureE:defenseFixtureE,weaponsSnapshotD:weaponsSnapshotD,','detached diagnostics')
 s=once(s,"tr.classification=tr.domain==='SURFACE'?'SURFACE':(q.missile>.22&&speed>170?'ASM':'AIR');", "tr.classification=tr.domain==='SURFACE'?'SURFACE':(q.missile>.22&&speed>170?'ASM':'AIR');tr.classificationConfidence=clamp(tr.classification==='ASM'?q.missile:tr.classification==='SURFACE'?q.surface:q.air,0,1);",'classification confidence derives from existing filtered anonymous evidence, separately from identity')
 # Versioned deployment codec. Legacy A-D lacks the switch and migrates explicitly to ON.
 s=once(s,"const MULTISHIP_DEPLOYMENT_SCHEMA_A='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1';",(HERE/'deployment.js').read_text()+"\nconst MULTISHIP_DEPLOYMENT_SCHEMA_A='AEGIS_DEPLOYMENT_MULTI_SHIP_E_1';",'versioned aircraft spawn scenario codec')
 s=once(s,'targetShip:\'HULK\',enemyProfileId:null});',"targetShip:'HULK',enemyProfileId:null,enemyAircraftEnabled:true});",'default aircraft ON preserves legacy patrols')
 s=once(s,extract(original,idx,'validateDeploymentA'),'','replace legacy validation with strict migration')
 s=once(s,'MULTISHIP_DEPLOYMENT_STATE_A.draft={schema:input.schema,targetShip:input.targetShip,enemyProfileId:input.enemyProfileId};','MULTISHIP_DEPLOYMENT_STATE_A.draft=normalizeDeploymentE(input);','normalize detached scenario draft')
 s=once(s,"root.querySelector('[data-enemy-choice]').value=q.enemyProfileId??'NONE';","root.querySelector('[data-enemy-choice]').value=q.enemyProfileId??'NONE';root.querySelector('[data-enemy-aircraft-choice]').value=q.enemyAircraftEnabled?'ON':'OFF';",'synchronized startup/loadout aircraft selectors')
 anchor='</select></label></div><p style="margin:10px 0 0;color:#a8c5d3;line-height:1.6">선택한 적함'
 control='</select></label><label style="flex:1;min-width:160px">적 항공기 스폰<select data-enemy-aircraft-choice aria-label="적 항공기 스폰" style="display:block;width:100%;margin-top:6px;padding:10px;background:#102c3b;color:#e0eef4;border:1px solid #527787"><option value="ON">ON · 생성</option><option value="OFF">OFF · 생성 안 함</option></select></label></div><p style="margin:10px 0 0;color:#a8c5d3;line-height:1.6">선택한 적함'
 s=once(s,anchor,control,'predeparture aircraft spawn selector')
 s=once(s,'독립 항해·침수·피해를 적용하며, 함정별 레이더 관측을 적용하며, 교전·전자전·AI는 이후 단계입니다.','독립 항해·레이더·피해와 미사일 자동 방어를 적용합니다. 항공기 스폰 OFF는 초기 생성과 이후 재생성을 끕니다.','player-facing implemented behavior')
 s=once(s,"enemyProfileId:picker.value==='NONE'?null:picker.value}","enemyProfileId:picker.value==='NONE'?null:picker.value,enemyAircraftEnabled:root.querySelector('[data-enemy-aircraft-choice]').value==='ON'}",'native change event')
 s=once(s,'return {config:{schema:config.schema,targetShip:config.targetShip,enemyProfileId:config.enemyProfileId},enemy};','return {config:normalizeDeploymentE(config),enemy};','atomic operational deployment restore')
 s=once(s,"function applyDeploymentA(prepared){","function applyDeploymentA(prepared){\n  if(!prepared.config.enemyAircraftEnabled){targetPool.length=0;SPAWN.timer=0;}",'OFF clears predeparture initial patrols and resets spawn timer')
 s=once(s,'function spawnPatrol(){','function spawnPatrol(){\n    if(!enemyAircraftSpawnsEnabledE())return;','all patrol entry points')
 for n in ['spawnTu22M3','spawnSuFighter']:s=once(s,'function '+n+'(x, y, heading){','function '+n+'(x, y, heading){\n    if(!enemyAircraftSpawnsEnabledE())return null;','normal aircraft constructor gate '+n)
 s=once(s,"if(!DIAG_SUPPRESS_PATROLS && BATTLESPACE.mode==='SANDBOX'){","if(!DIAG_SUPPRESS_PATROLS && enemyAircraftSpawnsEnabledE() && BATTLESPACE.mode==='SANDBOX'){",'OFF consumes no patrol clock or spawn RNG')
 s=s.replace("enemyExecution:'OWNER_WEAPONS_ACTIVE_SHADOW_AI_D'","enemyExecution:'OWNER_DEFENSE_AI_E'")
 s=s.replace("'receiverSpecificEW','enemyAI'","'receiverSpecificEW','enemyOffenseAI','defenseAssessmentAndPendingSalvos'")
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace("C55Packaging.build='V48_WIP_MULTI_SHIP_D'","C55Packaging.build='V48_WIP_MULTI_SHIP_E'")
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'reusedDefenseFunctions':len(json.loads((HERE/'function-index.json').read_text())),'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
