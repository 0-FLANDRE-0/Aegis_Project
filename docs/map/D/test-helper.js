// Test-only observation fixtures, never shipped. No alternate release function.
window.__MB_TEST__={
 reset(){_wip75ResetCase(1831565813);engagementControlMode='MANUAL';worldTimeScale=0;simAccumulator=0;for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);document.getElementById('uiStatusBarA').click();for(let i=0;i<16;i++)vlsCells.fwd[i]=wip125MakeInstalledCell('fwd',i,['SM2','SM2ER','SM6','ESSM4'][i%4]);shipMassMarkWeaponsV32('MAP_B_TEST_LOADOUT');__VIEWPORT_A__.setDistance(40);__VIEWPORT_A__.setPan(0,0);return getVlsCounts();},
 add(o={}){const id=hardKillDiagAddTrack({rangeKm:10,bearingDeg:0,altM:1000,speedMps:0,...o}),tr=tracks.get(id);tr._operatorIdentity=o.identity??'HOSTILE';tr.identity=o.identity??'HOSTILE';return id;},
 patch(id,o){const tr=tracks.get(id);Object.assign(tr,o);if(o.z===null){tr.sensorSource='SPQ9B';delete tr.z;if(tr._kfX)tr._kfX[2]=0;}},
 move(id,rangeKm){const t=tracks.get(id);t.x=aircraft.x()+kmToWorld(rangeKm);t.y=aircraft.y();if(t._kfX){t._kfX[0]=worldToMeters(t.x);t._kfX[1]=worldToMeters(t.y);}},
 lost(id){tracks.delete(id);},
 esm(){esmContacts.set(991,{bearing:Math.PI/4,age:0,bearingSigmaDeg:2,type:'AIR SEARCH RADAR',confidence:.9});return 'ESM:991';},
 tick(n){const obs=[...tracks].map(([id,t])=>[id,structuredClone(t)]);for(let i=0;i<n;i++){for(const [id,o]of obs){const tr=tracks.get(id);if(tr)Object.assign(tr,structuredClone(o),{sensorSource:'TEST',confirmed:true,sensorDetected:true,sensorAge:0,sensorHits:99,memActive:false,reacquiring:false,ttl:TRACK_HARD_TTL});}simulateFixedTick(SIM_FIXED_DT);}return [...tracks].map(([id,t])=>({id,fcq:trackIsFireControlQuality(t),blocked:wip121TargetSupportBlocked(id,t),quality:trackCovarianceMetrics(t),age:t.sensorAge,source:t.sensorSource,confirmed:t.confirmed,bda:wip121BdaTrackPresentation(t)}));},
 cadence(n){for(let i=0;i<n;i++){simStepCounter++;__MAP_B__.testStep?.();}return simStepCounter;},
 commandState(){return JSON.stringify({selectedLockId,mode:radar.mode,pd:radar.pdTracking,emcon:emconActive,rng:SIM_RNG_STATE,step:simStepCounter,tracks:[...tracks],vls:vlsReleaseB2Snapshot(true),weapons:getVlsCounts(),wp:routePoints,route:harpoonRuntimeA().routeDraft});},
 previewAudit(id,w){const a=this.commandState(),tr=mapBObservedTrack(id),q=mapBNativePreview(tr,w);return {q,exact:a===this.commandState()};},
 inventory(){return getVlsCounts();},
 stock(w,n){for(const s of ['fwd','aft'])for(let i=0;i<vlsCells[s].length;i++){const c=vlsCells[s][i];if(c.type===w||w==='ESSM'&&c.type==='ESSM4')vlsCells[s][i]=wip125MakeInstalledCell(s,i,'EMPTY');}for(let i=0;i<n;i++)vlsCells.fwd[i]=wip125MakeInstalledCell('fwd',i,w==='ESSM'?'ESSM4':w);shipMassMarkWeaponsV32('MAP_B_TEST_STOCK');},
 evidence(id,kind){const t=tracks.get(id);if(kind==='FRIEND'){t._operatorIdentity='FRIEND';t.identity='FRIEND';}if(kind==='OFFBOARD'){t.sensorSource='OFFBOARD_C';t.observationReportsC={remote:{H1:{measuredAtS:0,receivedAtS:0,sequence:1}},localAtS:null};}},
 state(){return {lock:selectedLockId,radarMode:radar.mode,pd:radar.pdTracking,emcon:emconActive,missiles:missiles.length,log:vlsReleaseB2Snapshot(true),cursor:{...lockCursor},mode:engagementControlMode};}
};
