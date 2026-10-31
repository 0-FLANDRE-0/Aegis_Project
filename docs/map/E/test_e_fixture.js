// TEST ONLY: reproducible observed cues and direct calls to native fixed-step
// soft-kill pipeline. No alternate scheduler/release/damage implementation.
window.__ME_TEST__={
 legacy:id=>mapELegacyNodeE(id),
 reset(){__MD_TEST__.reset();if(typeof ownEcmCommandE==='function')ownEcmCommandE('OFF');return true;},
 cue(){const rows=[0,1].map((i)=>({key:'E_CUE_'+i,source:'TRACK_ESM',trackId:null,emitterContactId:910+i,bearing:shipNav.heading+(i?Math.PI/2:-Math.PI/2),bearingSigmaDeg:1,rangeKm:4+i,rangeSigmaM:50,closureMps:300,ttcS:13+i,missileLikeConfidence:1,activeSeekerConfidence:1,threatScore:99-i,freshnessS:0}));for(const r of rows)esmContacts.set(r.emitterContactId,{age:0,emitterClass:'ACTIVE_SEEKER',type:'ACTIVE SEEKER TRACK',bearing:r.bearing,confidence:1});softKillThreatState.threats=rows;softKillThreatState.primary=rows[0];return rows;},
 command(k){if(typeof ownEcmCommandE==='function')return ownEcmCommandE(k);noiseJamActive=deceptJamActive=k!=='OFF';jammerAutoTrack=true;setSoftKillAutoDoctrine(k!=='OFF');return {ok:true};},
 ecmRun(k,n=1200){this.reset();this.cue();this.command(k);slq32EaState=createShipEaAllocatorStateA();softKillDoctrineState.revision=0;const ea=[],chaff=[],nulka=[];let lastS=0,lastN=0;for(let i=0;i<n;i++){simStepCounter++;for(const c of esmContacts.values())c.age=0;updateSoftKillDoctrine(SIM_FIXED_DT);updateSlq32EaAllocator(SIM_FIXED_DT);updateJammerBearing(SIM_FIXED_DT);updateOwnChaff(SIM_FIXED_DT);const s=skRuntime15B('SRBOC').logistics.expendedRounds,t=skRuntime15B('NULKA').logistics.expendedRounds;if(s!==lastS){chaff.push({step:simStepCounter,expended:s});lastS=s;}if(t!==lastN){nulka.push({step:simStepCounter,expended:t});lastN=t;}if(i%60===0)ea.push(slq32EaAuditSnapshot());}return {chaff,nulka,ea,doctrine:softKillDoctrineAuditSnapshot(),rng:SIM_RNG_STATE,srboc:skLogisticsSnapshot15B('SRBOC'),nulkaStock:skLogisticsSnapshot15B('NULKA')};},
 nativeManual(k,cue=true){if(cue)this.cue();return k==='SRBOC'?{fired:deployOwnChaff()}:nulkaFire15B(softKillPrimaryThreat());},
 npc(){return [...ENGAGEMENT_RUNTIME.ships.values()].filter(r=>r!==ACTIVE_SHIP_RUNTIME).map(r=>({id:r.entityId,settings:electronicSettingsF(r)}));},
 own(){return {level:typeof ownEcmLevelE==='function'?ownEcmLevelE():softKillAutoDoctrine?'FULL':'OFF',noise:noiseJamActive,deception:deceptJamActive,auto:softKillAutoDoctrine,emcon:emconActive,ea:slq32EaAuditSnapshot(),srboc:skLogisticsSnapshot15B('SRBOC'),nulka:skLogisticsSnapshot15B('NULKA'),rng:SIM_RNG_STATE};},
 noStock(k){for(const l of skRuntime15B(k).launchers){for(const t of l.tubes)t.loaded=false;}},
 nativeResetStage(){setSoftKillAutoDoctrine(true);return ownEcmLevelE();},
 nativeLockOff(){__AEGIS_WIP14A14_ENGAGEMENT_UI__.clearLock('MAP_E_TEST');},
 routeInput(){return {mode:inputMode,tab:controlDeckActiveTabWip13C,points:harpoonRuntimeA().routeDraft.pointsM.length,wp:routePoints.length,open:Object.entries(__UI_A__.snapshot().windows).filter(([id,q])=>q.open).map(([id])=>id)};}
};
