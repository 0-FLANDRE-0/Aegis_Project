// TEST ONLY: actual player/NPC C55 sweep with explicit post-RF fixture evidence.
// RF/Pd/dwell are NOT tested here. Original natural CIWS30 remains separate.
window.__TRACK_B_C55_NATIVE__=Object.freeze({run(){
  const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},copy=S.copy;
  const measurement=(rxM,ryM,rzM=0)=>{const rangeM=Math.hypot(rxM,ryM,rzM);return {attempted:true,accepted:true,rxM,ryM,rzM,rangeM,azRad:Math.atan2(ryM,rxM),elRad:Math.atan2(rzM,Math.hypot(rxM,ryM)),losQ:.99,rangeQ:.99,pd:.8,quality:.8,positionVarianceM2:[36,100,100],damageSigmaFactor:1,damagePdFactor:1,effectiveRangeKm:5,source:'LOCAL_RF'};};
  const liveSnapshot=bank=>[...bank.files.values()].map(r=>({id:r.id,ownFireEvidence:!!r.ownFireEvidence,protectedIdentity:r.protectedIdentity,confirmed:r.confirmed,cmsTrackId:r.cmsTrackId,firstSeenS:r.firstSeenS,st:copy(r.st)}));
  for(const context of ['player','npc']){
    const owner=context==='player'?ACTIVE_SHIP_RUNTIME:S.privateOwner('C55_NPC');let hook;
    if(context==='player')hook={mounts:()=>ciws,bank:c55Bank,sweep:c55SensorSweep,associateCms:c55AssociateCms,swapMeasurement(fn){const original=ciwsLocalMeasurement;ciwsLocalMeasurement=fn;return()=>{ciwsLocalMeasurement=original;};}};
    else{try{prepareWeaponsD(owner);}finally{ENGAGEMENT_RUNTIME.world.entities.navalOrdnanceD?.delete(owner.entityId);}hook=owner.weapons.executionD.context.__trackBTestC55;if(!hook)throw Error('NPC_C55_TEST_ONLY_ACCESSOR_MISSING');}
    const mount=hook.mounts().find(m=>m.type==='GUN')??hook.mounts()[0];if(!mount)throw Error('NATIVE_C55_MOUNT_MISSING');
    const runSweep=(bank,specs)=>{
      const pool=specs.map((q,i)=>({e:{id:900000+i,_fixtureIndex:i,x:metersToWorld(q.meas.rxM),y:metersToWorld(q.meas.ryM),z:q.meas.rzM},key:'TEST_POST_RF_'+i,rcs:null,own:q.own}));
      const oldPool=navalCiwsSourcesD,oldPhysical=physicalShipsB,restoreMeasurement=hook.swapMeasurement((m,e)=>specs[e._fixtureIndex].meas);
      // The pool override selects the same native ship-aware source branch in
      // both contexts without registering any test source in the real world.
      navalCiwsSourcesD=()=>pool;physicalShipsB=()=>[owner];
      try{hook.sweep(mount,bank,SIM_FIXED_DT);for(const file of bank.files.values())hook.associateCms(file,[]);}
      finally{physicalShipsB=oldPhysical;navalCiwsSourcesD=oldPool;restoreMeasurement();}
    };
    const cases={};
    for(const order of ['OWN_FIRST','FOREIGN_FIRST']){
      const bank=hook.bank(mount);bank.files.clear();bank.cues=[];
      const own={own:true,meas:measurement(3000,-40)},foreign={own:false,meas:measurement(3000,40)};runSweep(bank,order==='OWN_FIRST'?[own,foreign]:[foreign,own]);
      const initial=liveSnapshot(bank),ownFile=[...bank.files.values()].find(r=>r.ownFireEvidence),foreignFile=[...bank.files.values()].find(r=>!r.ownFireEvidence);
      if(!ownFile||!foreignFile||bank.files.size!==2)throw Error('NATIVE_C55_PARTITION_SEED_FAILED:'+context+':'+order);
      runSweep(bank,[{own:false,meas:measurement(3000,0)},{own:true,meas:measurement(3000,0)}]);
      checks[context+'.'+order+'.twoIndependentFiles']=bank.files.size===2&&bank.files.has(ownFile.id)&&bank.files.has(foreignFile.id);
      checks[context+'.'+order+'.foreignNotProtected']=foreignFile.ownFireEvidence===false&&foreignFile.protectedIdentity===null;
      checks[context+'.'+order+'.ownProtectionRetained']=ownFile.ownFireEvidence===true&&ownFile.protectedIdentity==='FRIEND';
      cases[order]={initial,afterCrossing:liveSnapshot(bank),source:'EXPLICIT_POST_RF_ANONYMOUS_MEASUREMENTS_PLUS_KNOWN_OWN_LAUNCH_INVENTORY_BIT'};
    }
    const bank=hook.bank(mount);bank.files.clear();bank.cues=[];
    runSweep(bank,[{own:false,meas:measurement(3000,0)},{own:false,meas:measurement(3000,0)}]);const beforeTie=liveSnapshot(bank),beforeSerial=window.__TRACK_B__?__TRACK_B__.snapshot().stats.recorded:null;
    runSweep(bank,[{own:false,meas:measurement(3000,0)}]);const afterTie=liveSnapshot(bank);
    checks[context+'.exactTie.liveFilesNotMerged']=bank.files.size===2;
    let trace=[];
    if(window.__TRACK_B__&&__TRACK_B__.snapshot().enabled){trace=__TRACK_B__.snapshot().records.filter(r=>r.serial>beforeSerial&&r.route==='C55_SHADOW');checks[context+'.exactTie.realShadowHeld']=trace.some(r=>r.decision==='SHADOW_HOLD');checks[context+'.shadowNeverLive']=trace.every(r=>r.active===false);checks[context+'.distanceNotPublishedAsNis']=trace.every(r=>!('nis'in r));checks[context+'.noSourceCanaryLeak']=!JSON.stringify(trace).includes('TEST_POST_RF_');}
    else if(window.__TRACK_B__)checks[context+'.diagnosticOffNoTrace']=__TRACK_B__.snapshot().stats.recorded===0;
    cases.exactTie={beforeTie,afterTie,liveAssociationRemainsLegacyByDesign:true};records[context]={actualFunctions:['c55SensorSweep','c55Bank','c55UpdateFile','c55AssociateCms'],cases};
  }
  return {classification:'DIRECT_NATIVE_POST_RF_C55_FIXTURE_NOT_NATURAL_RF',naturalRfPdDwellOrWeaponEvidence:false,liveC55PolicyChanged:false,checks,records};
}});
