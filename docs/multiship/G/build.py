"""Pinned F → G: measured friendly network and no-DL launch correlation."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7'
OLD='v48_WIP_MULTI_SHIP_F';NEW='v48_WIP_MULTI_SHIP_G';PATCHES=[]
def once(s,a,b,label):
 assert s.count(a)==1,(label,s.count(a));PATCHES.append(label);return s.replace(a,b,1)
def extract(s,key):
 q=json.loads((HERE/'patch-index.json').read_text())[key];v=s[q['start']:q['end']];assert hashlib.sha256(v.encode()).hexdigest()==q['sha256'],key;return v
def insert_body(s,code):return s[:s.index('{')+1]+'\n'+code+s[s.index('{')+1:]
def a3(s):
 s=once(s,'harpoonTrackIdentityC(tr);','harpoonTrackIdentityC(tr,ACTIVE_SHIP_RUNTIME);','owner-addressed Harpoon knowledge')
 s=once(s,'const protectedIdentity=!!ownLaunch||',"const protectedIdentity=!!networkProtectionG(ACTIVE_SHIP_RUNTIME,tr)||!!ownLaunch||",'measured protected shared identity cannot grant release')
 return s
def track_gate(s):
 # Parameters have a default object, so match the actual body brace explicitly.
 return once(s,'opts={}){',"opts={}){\n    const networkTr=tracks.get(Number(trackId));if(networkTr&&networkProtectionG(ACTIVE_SHIP_RUNTIME,networkTr))return {ok:false,reason:'NETWORK_PROTECTED_IDENTITY'};",'shared protection at native authority')
def vls_gate(s):
 anchor="if(!s)throw new Error('VLS_RELEASE_STATE_UNINITIALIZED');"
 return once(s,anchor,anchor+"\n    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok){s.lastReject={reason:ng.reason,step:simStepCounter,weapon};return null;}",'network consent before actual VLS cycle')
def low_vls(s):
 return once(s,'opts={}){',"opts={}){\n    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok)return;",'actual round consumption rechecks cooperative consent')
def pending(s):
 anchor="if(engagementControlMode!==WIP119_ENGAGEMENT_MODES.AUTO)return {ok:false,reason:'MODE'};"
 return once(s,anchor,anchor+"const net=networkVlsGateG(ACTIVE_SHIP_RUNTIME,pending.trackId,{automatic:true});if(!net.ok)return net;",'native automatic scheduler consent')
def alias(s):
 return once(s,'if(oldId===newId)return false;',"if(oldId===newId)return false;networkTransferAliasG(ACTIVE_SHIP_RUNTIME,oldId,newId);",'owner-local measured alias lease handoff')
def build(s):
 original=s
 def replace(name,new):
  nonlocal s;s=once(s,extract(original,name),new,name)
 context=extract(original,'createWeaponContextD')
 transforms={'updateTrackOperationalStateA3':a3,'trackEngagementGateA3':track_gate,'vlsReleaseB2Request':vls_gate,'vlsReleaseStandardB1':low_vls,'vlsReleaseEssmB1':low_vls,'wip119FireOne':pending,'wip121TransferEngagementMemory':alias}
 for name,fn in transforms.items():context=once(context,extract(original,'owner/'+name),fn(extract(original,'owner/'+name)),'owner '+name)
 context=once(context,extract(original,'owner/harpoonTrackIdentityC'),'','use explicit owner port instead of duplicated launch association')
 context=once(context,'r.launches.push(harpoonLaunchRecordC(m,gate))','r.launches.push(harpoonLaunchRecordC(m,gate,tracks))','launch exclusion uses owner local files')
 context=once(context,'function harpoonLaunchRecordC(m,gate){','function harpoonLaunchRecordC(m,gate,sourceTracks=tracks){','owner lexical launch record signature')
 context=once(context,'excludedTrackIds:Array.from(tracks.keys()),claimedTrackId:null','excludedTrackIds:Array.from(sourceTracks.keys()),claimedTrackId:null','owner lexical exclusion source')
 context=once(context,'return {launch,step,authority:',"return {launch,step,networkBid:id=>{const tr=tracks.get(id);return tr?networkBidDataG(owner,tr,wip118ControlState,defenseE.mode==='AUTO'?'AUTO':'MANUAL',missiles):{eligible:false,cost:1e6,weapon:null,inFlight:0};},authority:",'read-only native owner bid port')
 context=once(context,'return {launch,step,networkBid:',"return {launch,step,operatorIdentity:(id,identity)=>{sync();const tr=tracks.get(id);if(!tr)return {ok:false,reason:'NO_TRACK'};tr._operatorIdentity=normalizeTrackOperatorIdentityA3(identity);tr._operatorIdentitySetAtStep=simStepCounter;updateTrackOperationalStateA3(tr,{mode:engagementControlMode,assessment:wip118ControlState.assessments.get(id)});return {ok:true,identity:tr.identity};},networkBid:",'owner local operator identity port')
 replace('createWeaponContextD',context)
 for name,fn in transforms.items():replace(name,fn(extract(original,name)))
 for name in ['harpoonMatchLaunchC','harpoonTrackIdentityC']:replace(name,'')
 f=extract(original,'harpoonLaunchRecordC')
 f=once(f,'harpoonLaunchRecordC(m,gate){','harpoonLaunchRecordC(m,gate,sourceTracks=tracks){','owner launch record API')
 f=once(f,'Array.from(tracks.keys())','Array.from(sourceTracks.keys())','preexisting owner files never become own ordnance');replace('harpoonLaunchRecordC',f)
 f=extract(original,'observerAcceptPlotsC');f=once(f,'observerClassifyC(tr,meas);trackRefreshDerivedQuality(tr);','observerClassifyC(tr,meas);networkNoteLocalG(r,tr,meas.source);trackRefreshDerivedQuality(tr);','local observer measured epoch');replace('observerAcceptPlotsC',f)
 f=extract(original,'updateSensorTrackMeasurement');f=once(f,'tr.sensorDetected=true;tr.sensorSource=source;tr.sensorAge=0;','tr.sensorDetected=true;tr.sensorSource=source;tr.sensorAge=0;networkNoteLocalG(ACTIVE_SHIP_RUNTIME,tr,source);','player local measurement epoch');replace('updateSensorTrackMeasurement',f)
 f=extract(original,'resetObserversC');pos=f.rfind('}');replace('resetObserversC',f[:pos]+'resetNetworkFleetG();\n'+f[pos:])
 f=extract(original,'retirePhysicalShipB');f=once(f,'retireWeaponsD(r);','retireNetworkG(r);retireElectronicF(r);retireWeaponsD(r);','link and electronic owner retirement');replace('retirePhysicalShipB',f)
 f=extract(original,'applyDeploymentA');f=once(f,'syncDeploymentUiA();','syncDeploymentUiA();resetNetworkFleetG();','deployment clears peer transient');replace('applyDeploymentA',f)
 f=extract(original,'exportPhysicalFleetB');f=once(f,'ew:electronicSettingsF(r),','network:networkSettingsG(r),ew:networkExportElectronicG(r),','fleet settings and individual radar baseline');replace('exportPhysicalFleetB',f)
 f=extract(original,'restorePreparedPhysicalFleetB');f=once(f,'r.restoredElectronicF=q.ew??null;','r.restoredElectronicF=q.ew??null;r.restoredNetworkG=q.network??null;','detached network settings restore');replace('restorePreparedPhysicalFleetB',f)
 f=extract(original,'validatePhysicalFleetB');f=once(f,"[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_B_1']","[MULTISHIP_PHYSICAL_SCHEMA_B,'AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1']",'explicit old fleet migration')
 f=once(f,"const fleet=src.fleet,err=x=>errors.push('FLEET_'+x);","const fleet=src.fleet,err=x=>errors.push('FLEET_'+x);if(fleet?.schema===MULTISHIP_PHYSICAL_SCHEMA_B)validateNetworkSettingsG(src.ship?.network,errors);",'required player G network preflight')
 f=once(f,"seen.add(q.entityId);if(src.deployment.schema", "seen.add(q.entityId);if(fleet.schema===MULTISHIP_PHYSICAL_SCHEMA_B||q.network)validateNetworkSettingsG(q.network,errors,role);if(src.deployment.schema",'strict ally/enemy settings');replace('validatePhysicalFleetB',f)
 f=extract(original,'exportOperationalState');f=once(f,'ship:{ew:electronicSettingsF(ACTIVE_SHIP_RUNTIME),','ship:{network:networkSettingsG(ACTIVE_SHIP_RUNTIME),ew:networkExportElectronicG(ACTIVE_SHIP_RUNTIME),','player network settings save')
 f=once(f,"deferred:['electronicContactsAndTechniqueTimeline'","deferred:['networkReportsLeasesAndGroupRuntime','electronicContactsAndTechniqueTimeline'",'network transient deferred');replace('exportOperationalState',f)
 f=extract(original,'prepareOperationalStateV48Wip11B');f=once(f,'const harpoonMigrations=[];',"const harpoonMigrations=[];migrateNetworkSaveG(src,harpoonMigrations);",'legacy settings migration before codecs');replace('prepareOperationalStateV48Wip11B',f)
 f=extract(original,'applyPreparedOperationalStateV48Wip11B');f=once(f,"if(src.ship.ew)electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,src.ship.ew);","if(src.ship.ew)electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,src.ship.ew);if(src.ship.network){ACTIVE_SHIP_RUNTIME.combatSystem.networkG=null;ACTIVE_SHIP_RUNTIME.restoredNetworkG=src.ship.network;prepareNetworkG(ACTIVE_SHIP_RUNTIME);}",'restore only settings, no packets or leases');replace('applyPreparedOperationalStateV48Wip11B',f)
 f=extract(original,'observationReportLabelC');f=once(f,"if(!q?.remote.length)return '';","if(!q?.remote.length)return networkTrackLabelG(tr);",'network correction label');replace('observationReportLabelC',f)
 f=extract(original,'drawRadar');f=once(f,'for(const [id,tr] of tracks){','for(const [id,localTr] of tracks){const tr=networkPresentationTrackG(localTr);','CIC correction is a detached display value')
 f=once(f,'drawRescueRaftsCicK();','drawRescueRaftsCicK();drawNetworkPictureG();','receiver remote-only picture');replace('drawRadar',f)
 f=extract(original,'toggleEmcon');f=once(f,'function toggleEmcon(){','function toggleEmcon(){networkOverrideRadarG(ACTIVE_SHIP_RUNTIME);','individual radar command preserves requested toggle');replace('toggleEmcon',f)
 f=extract(original,'setControlDeckTabWip13C');replace('setControlDeckTabWip13C',f.replace("['NAV','ARM','DEBUG']","['NAV','ARM','FLEET','DEBUG']"))
 f=extract(original,'wip13cRunTabInvarianceFixture');f=f.replace("['NAV','ARM','DEBUG','NAV','DEBUG','ARM']","['NAV','ARM','FLEET','DEBUG','NAV','FLEET','DEBUG','ARM']").replace('pages.length===3&&tabs.length===3','pages.length===4&&tabs.length===4');replace('wip13cRunTabInvarianceFixture',f)
 f=extract(original,'installPhysicalFleetRendererB')
 f=once(f,'this.navalFocusB=null;return reset.apply(this,args);','this.navalFocusB=null;this.updateNavalFocusButtonG();return reset.apply(this,args);','camera reset label')
 f=once(f,'this.orbit.targetY=10;return true;','this.orbit.targetY=10;this.updateNavalFocusButtonG();return true;','camera focus label')
 f=once(f,'if(this.navalFocusB&&!wanted.has(this.navalFocusB))this.navalFocusB=null;','if(this.navalFocusB&&!wanted.has(this.navalFocusB))this.navalFocusB=null;this.updateNavalFocusButtonG();','camera retirement label')
 f=once(f,"const root=view.root,toolbar=root?.querySelector('.external3d-toolbar');", "view.updateNavalFocusButtonG=function(){const b=document.getElementById('external3DNavalShipBtn');if(b){b.textContent=this.navalFocusB?'자함 보기':'아군함 보기';b.setAttribute('aria-pressed',String(!!this.navalFocusB));}};\n  const root=view.root,toolbar=root?.querySelector('.external3d-toolbar');",'camera label sync method')
 f=once(f,"button.textContent='아군함 보기';button.onclick=()=>{", "button.textContent='아군함 보기';button.style.pointerEvents='auto';button.setAttribute('aria-pressed','false');for(const ev of ['pointerdown','touchstart','mousedown','wheel'])button.addEventListener(ev,e=>e.stopPropagation(),{passive:false});bindPress(button,()=>{",'actual mouse touch camera input')
 f=once(f,'};toolbar.appendChild(button);}', '});toolbar.appendChild(button);}','bind camera native input')
 replace('installPhysicalFleetRendererB',f)
 modules='\n'.join((HERE/name).read_text()for name in ['network.js','cooperation.js','fleet.js','ui.js','launch-protection.js'])
 s=once(s,'const NAVAL_WEAPONS_POLICY_D=',modules+'\nconst NAVAL_WEAPONS_POLICY_D=','canonical network and observed launch modules')
 s=once(s,"const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_F_1';","const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_G_1';",'G fleet schema')
 s=once(s,'stepObserversC(dt);stepElectronicOwnersF(dt);','stepObserversC(dt);stepElectronicOwnersF(dt);networkFixedStepG(dt);','network transport fixed tick once')
 s=once(s,"bindPress(document.getElementById('emconBtn'), (e)=>{\n    toggleEmcon();","mountNetworkUiG();\n  bindPress(document.getElementById('emconBtn'), (e)=>{\n    toggleEmcon();",'native network UI and individual radar override')
 s=once(s,"lines.push(electronicCicTextF());","lines.push(electronicCicTextF());networkUpdateUiG();",'display-only network status')
 s=s.replace("Object.freeze(['NAV','ARM','DEBUG'])","Object.freeze(['NAV','ARM','FLEET','DEBUG'])").replace("DEBUG:'PAN_ONLY_NO_MAP_COMMAND'","FLEET:'PAN_ONLY_NO_MAP_COMMAND',DEBUG:'PAN_ONLY_NO_MAP_COMMAND'")
 s=once(s,'if(harpoonRouteEditingE()){',"if(harpoonRouteEditingE()&&controlDeckActiveTabWip13C!=='FLEET'){",'fleet map input cannot edit own Harpoon route')
 s=once(s,'function resetNetworkFleetG(){','function resetNetworkFleetG(){fleetResetG();','fleet selection and owner command transient reset')
 s=once(s,'shipOceanEffectsAuditF:shipOceanEffectsAuditF,',"networkSnapshotG:networkSnapshotG,networkCommandG:networkCommandG,networkReceiveProbeG:(receiverId,senderId,packet)=>networkReceiveG(ENGAGEMENT_RUNTIME.ships.get(receiverId),senderId,packet),networkReportsProbeG:id=>networkBuildReportsG(ENGAGEMENT_RUNTIME.ships.get(id)),networkMathProbeG:(a,b)=>({nis:networkNisG(a,b),intersection:networkIntersectionG(a,b)}),networkVlsGateProbeG:(id,trackId,options)=>networkVlsGateG(ENGAGEMENT_RUNTIME.ships.get(id),trackId,options),harpoonCorrelationProbeG:(id,trackId)=>harpoonTrackIdentityC(observerC(ENGAGEMENT_RUNTIME.ships.get(id)).tracks.get(trackId),ENGAGEMENT_RUNTIME.ships.get(id)),shipOceanEffectsAuditF:shipOceanEffectsAuditF,",'detached network diagnostics')
 s=once(s,'networkSnapshotG:networkSnapshotG,','fleetSnapshotG:fleetSnapshotG,fleetSelectG:fleetSelectG,fleetCommandG:fleetCommandG,networkSnapshotG:networkSnapshotG,','owner addressed operator diagnostics')
 return s
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
 html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);src=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(src).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
 html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace('V48_WIP_MULTI_SHIP_F','V48_WIP_MULTI_SHIP_G')
 a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
