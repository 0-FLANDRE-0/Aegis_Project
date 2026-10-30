// MAP_A observation boundary. Whitelist measured/received fields; no truth lookup,
// diagnostic facade, private RF reference, enemy entity array or new association.
function mapNowA(){return simStepCounter*SIM_FIXED_DT;}
function mapOwnShipA(){const n=ACTIVE_SHIP_RUNTIME.navigation,p=ACTIVE_SHIP_PROFILE.identity??{};return {key:'OWN',kind:'OWN',id:'OWN',label:p.hullNumber??ACTIVE_SHIP_PROFILE.id,x:n.positionWorld.x,y:n.positionWorld.y,z:0,identity:'FRIEND',classification:'SURFACE',measuredAtS:mapNowA(),speedKt:worldSpeedToMps(Math.hypot(n.vx,n.vy))/.514444,headingDeg:shipHdgDeg(),source:'자함 항법'};}
// Same display gate without trackCovarianceMetrics' lazy EKF initializer.
function mapTrackVisibleA(tr){if(!tr||tr.sensorDetected===false||wip121BdaTrackPresentation(tr).hidden||(tr.trackQuality??0)<=.05)return false;const P=tr._kfP;let sigma=tr.measurementSigmaM??0;if(P){const a=P[0],b=P[1],d=P[7];sigma=Math.sqrt(Math.max(1e-6,.5*(a+d+Math.hypot(a-d,2*b))));}return sigma<TRACK_FILTER_MODEL.maxPosSigmaM;}
function mapLaunchReceiptsA(){return harpoonRuntimeA().launches.map(r=>({key:'RECEIPT:'+r.id,kind:'RECEIPT',id:r.id,label:'H'+r.id+' 발사 기록',classification:'자함 하푼 / 무DL',identity:'FRIEND',measuredAtS:r.releaseStep*SIM_FIXED_DT,source:'자함 발사 확인 / 고정 계획',releaseAtS:r.releaseStep*SIM_FIXED_DT,targetTrackId:r.memory?.trackId??null,route:(r.routeProgram?.pointsM??[]).map(p=>({x:p.x,y:p.y})),updatesAfterRelease:false}));}
function mapTrackReadA(id,tr){
 const now=mapNowA(),p=tr.observationReportsC,remote=Object.entries(p?.remote??{}).map(([sourceId,q])=>({sourceId,measuredAtS:q.measuredAtS,receivedAtS:q.receivedAtS,sequence:q.sequence}));
 const sources=Object.entries(surfaceSensorContributorSnapshotWip13B9(tr)).map(([name,q])=>({name,measuredAtS:now-q.ageS,rangeSigmaM:q.rangeSigmaM,azSigmaDeg:q.azSigmaDeg,updates:q.updates}));
 const localAtS=p?.localAtS??(tr.sensorSource!=='OFFBOARD_C'?(Number.isFinite(tr._lastMeasurementStep)?tr._lastMeasurementStep*SIM_FIXED_DT:now-(tr.sensorAge??0)):null);
 if(!sources.length&&localAtS!=null)sources.push({name:tr.sensorSource??'LOCAL',measuredAtS:localAtS});
 const e=tr.isarEvidence,isar=e?{sourceId:e.sourceId,measuredAtS:e.measuredAtS,lengthM:e.lengthM,lengthSigmaM:e.lengthSigmaM,candidates:(e.candidates??[]).map(q=>({label:q.label,confidence:q.confidence}))}:null;
 return {key:'TRACK:'+id,kind:'TRACK',id,label:trackDisplayLabelById(id),x:tr.x,y:tr.y,z:tr.z,classification:tr.classification??tr.domain??'UNKNOWN',identity:tr.identity??'UNKNOWN',operatorIdentity:tr._operatorIdentity??'UNKNOWN',quality:tr.trackQuality,measuredAtS:now-(tr.sensorAge??0),source:tr.sensorSource,local:sources,remote,isar,iff:tr.iffF?{authenticatedFriendly:!!tr.iffF.authenticatedFriendly,measuredAtS:tr.iffF.measuredAtS,expiresAtS:tr.iffF.expiresAtS}:null,identificationEvidence:tr.identificationEvidence??null,emcon:emconActive};
}
function mapEsmReadA(id,c){return {key:'ESM:'+id,kind:'ESM',id,label:'ESM '+id,identity:'UNKNOWN',classification:'방위 접촉',bearingRad:c.bearing,bearingSigmaDeg:c.bearingSigmaDeg,band:c.band??null,emitterClass:c.emitterClass??null,type:c.type??null,confidence:c.confidence??c.quality??c.strength??null,measuredAtS:mapNowA()-(c.age??0),source:'ESM'};}
function mapOwnHelosA(){
 // Same known-own AIR/navigation data, projected without copying RF/ISAR internals.
 const out=[];for(const inv of ACTIVE_SHIP_RUNTIME.aviation.inventory??[]){const h=heloWorldA().get(inv.id);if(!h||h.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId)continue;out.push({key:'HELO:'+h.id,kind:'HELO',id:h.id,label:'H'+(h.slot+1),x:metersToWorld(h.positionM.x),y:metersToWorld(h.positionM.y),z:h.positionM.z,identity:'FRIEND',classification:'AIR',state:h.state,visible:h.visible||h.id===heloUiA.selectedId,radarMode:h.radarMode,routeCount:h.route.length,routeIndex:h.routeIndex,speedKt:Math.hypot(h.groundVelocityMps.x,h.groundVelocityMps.y)/HELO_VALUES_A.knotMps,headingDeg:(h.headingRad*180/Math.PI+450)%360,measuredAtS:mapNowA(),source:'기존 AIR 자함 항공 운용 / 기체 항법'});}return out;
}
function mapReceivedNetworkA(){
 if(!ACTIVE_SHIP_RUNTIME.combatSystem.networkG)return [];
 return networkPictureG(ACTIVE_SHIP_RUNTIME).filter(q=>q.positionM&&(q.localTrackId===null||q.identity==='FRIEND'&&q.sources.some(s=>s.kind==='SELF'))).map(q=>{const self=q.identity==='FRIEND'?q.sources.find(s=>s.kind==='SELF'):null,tr=self&&q.localTrackId!=null?tracks.get(q.localTrackId):null,local=tr&&mapTrackVisibleA(tr)?mapTrackReadA(q.localTrackId,tr):null;return {associatedTrackId:self?q.localTrackId:null,local:local?.local??[],key:(self?'ALLY:':'NET:')+q.id,kind:self?'ALLY':'NET',id:q.id,viewId:self?.senderId??null,label:self?'아군함 '+self.senderId:'NET '+q.id,x:local?.x??metersToWorld(q.positionM.x),y:local?.y??metersToWorld(q.positionM.y),z:local?.z??q.positionM.z,classification:q.classification,identity:q.identity,measuredAtS:mapNowA()-q.ageS,source:'Link 16 수신',remote:q.sources.map(s=>({sourceId:s.senderId,measuredAtS:mapNowA()-s.measurementAgeS,kind:s.kind}))};});
}
function mapOwnMissilesA(){
 // These two native own-weapon pools already supply MSL STATUS and chart icons.
 // Harpoon has NO DL: deliberately no Harpoon world/booster/seeker access here.
 const out=[];for(const [pool,prefix]of [[missiles,'M'],[ramMissiles,'RAM']])for(const m of pool){if(m.dead||m.alive===false||m.ownerEntityId&&m.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId)continue;out.push({key:'MISSILE:'+prefix+':'+m.id,kind:'MISSILE',id:prefix+':'+m.id,label:prefix+m.id,x:m.x,y:m.y,z:m.z,identity:'FRIEND',classification:'자함 무장',targetTrackId:m.assignedTargetId??m.targetId??null,phase:m.guidanceState??m.phase??(m.vlsPhase?'VLS':m.seekerMode??m._v1SarhState??m._v1ArhState??m.motorPhase??'-'),remainingS:Number.isFinite(m.maxLife)&&Number.isFinite(m.life)?Math.max(0,m.maxLife-m.life):null,measuredAtS:mapNowA(),source:'자함 무장 데이터'});}return out;
}
function mapRouteObjectsA(){const out=routePoints.map((p,i)=>({key:'WP:'+i+':'+p.x+':'+p.y,kind:'WP',id:i,label:'WP'+(i+1),x:p.x,y:p.y,measuredAtS:mapNowA(),source:'자함 항해 계획'}));for(const[pIndex,p]of harpoonRuntimeA().routeDraft.pointsM.entries())out.push({key:'HWP:'+pIndex+':'+p.x+':'+p.y,kind:'HWP',id:pIndex,label:'H-WP'+(pIndex+1),x:metersToWorld(p.x),y:metersToWorld(p.y),measuredAtS:mapNowA(),source:'하푼 발사 전 INS 계획'});return out;}
function mapObservedObjectsA(){
 const out=[mapOwnShipA(),...mapOwnHelosA().filter(h=>h.visible),...mapReceivedNetworkA(),...mapOwnMissilesA(),...mapRouteObjectsA()];
 const linked=new Set(out.filter(o=>o.kind==='ALLY'&&o.associatedTrackId!=null).map(o=>o.associatedTrackId));
 for(const [id,tr]of tracks)if(!linked.has(id)&&mapTrackVisibleA(tr)&&Number.isFinite(tr.x)&&Number.isFinite(tr.y))out.push(mapTrackReadA(id,tr));
 for(const [id,c]of esmContacts)out.push(mapEsmReadA(id,c));return out;
}
function mapPrecisionReasonA(o){if(!o)return '선택 없음';if(emconActive)return 'EMCON';if(o.kind==='ESM')return '위치 없음(방위만)';if(o.kind!=='TRACK')return '로컬 트랙 없음(공유만)';const tr=tracks.get(o.id);if(!tr||!mapTrackVisibleA(tr))return '트랙 소실';if(shipEquipmentOfflineV1())return '함 장비 오프라인';if(!Object.values(getSPY1DVFaceStatus()).some(Boolean))return 'SPY 레이더 오프라인';if(!isInRadarSector(tr.x,tr.y,tr.z))return 'SPY 섹터 밖';return '';}
function mapPrecisionCommandA(o){const reason=mapPrecisionReasonA(o);if(reason)return {ok:false,reason};mapLegacyCursorBridgeA(o);lockByCursor(o.id);return {ok:selectedLockId===o.id,trackId:selectedLockId};}
function mapLegacyCursorBridgeA(o){
 // MAP_A_LEGACY_CURSOR_BRIDGE: remove in MAP_B when firing-designation UI and
 // the small release control consume their own explicit track slot. No lock/PD/EMCON writes.
 if(!['TRACK','NET'].includes(o?.kind)||!Number.isFinite(o.x)||!Number.isFinite(o.y))return;
 lockCursor.x=o.x;lockCursor.y=o.y;lockCursor.nx=clamp((o.x-aircraft.x())/Math.max(1e-9,lockCursor.rx),-1,1);lockCursor.ny=clamp((o.y-aircraft.y())/Math.max(1e-9,lockCursor.ry),-1,1);
}
function harpoonRouteUndoMapA(){const r=harpoonRuntimeA();if(!harpoonRouteEditingE()||!r.routeDraft.pointsM.length)return {ok:false,reason:'마지막 점만 취소 가능'};r.routeDraft.pointsM.pop();harpoonUpdateUIA();return {ok:true};}
