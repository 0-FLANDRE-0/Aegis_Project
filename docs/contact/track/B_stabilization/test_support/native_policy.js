// TEST ONLY. Additional native association-policy fixtures, not natural RF.
// Reuses immutable B/native_support.js; no alternate NIS, solver, filter or truth.
// Explicit receiver-owned EKF initial conditions are declared in each record.
window.__TRACK_B_STABILIZATION_NATIVE__=Object.freeze({
  state(){return TRACK_B_NATIVE_SUPPORT.afterActionPassiveState();},
  run(selected=null){
    const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},errors=[],afterActionStateByFixture={},traceByFixture={},methods=new Set();
    const check=(key,value)=>{checks[key]=!!value;};
    const requireFixture=(ok,reason)=>{if(!ok)throw Error('FIXTURE_PRECONDITION:'+reason);};
    const reset=()=>{__GB_TEST__.reset(419025);S.resetPrivateOwnerEvidence();BATTLESPACE_DIAG_BYPASS=true;emconActive=true;tracks.clear();};
    const seed=(xM,Pxy,label)=>{
      const plot=S.surface({xM});S.assertNoTruthFields(plot);methods.add('updateSensorTrackMeasurement');
      const tr=updateSensorTrackMeasurement(null,plot,{source:plot.source,taskType:'SURFACE_PRECISION'});
      updateSensorTrackMeasurement(tr.trackId,plot,{source:plot.source,taskType:'SURFACE_PRECISION'});
      requireFixture(tr.confirmed&&tr.domain==='SURFACE','FIRM_NATIVE_SURFACE_'+label);
      // Fixture initial estimator state only; no world target is created/read.
      tr._kfX.set([xM,0,8,0,0,0]);tr._kfP.fill(0);
      for(const[index,value]of [[0,Pxy],[7,Pxy],[14,16],[21,100],[28,100],[35,16]])tr._kfP[index]=value;
      methods.add('trackSyncLegacyFromEkf');trackSyncLegacyFromEkf(tr);return tr;
    };
    const matrix=(files,plot)=>{methods.add('trackSurfacePositionAssociationNisWip13B9');return files.map(tr=>trackSurfacePositionAssociationNisWip13B9(tr,plot));};
    const assign=plot=>{methods.add('surfaceAssignmentsPreferEstablishedWip13B14');return surfaceAssignmentsPreferEstablishedWip13B14([plot],trackSurfacePositionAssociationNisWip13B9,64);};
    const evidence=(files,plot)=>{
      if(typeof trackBEvidenceStableB!=='function')return {available:false};
      // Diagnostic inspection of the actual candidate helper, not a replacement
      // score. The caller uses position-only NIS despite finite input Doppler.
      const copy={...plot};delete copy.radialMps;delete copy.radialVelSigmaMps;
      return {available:true,mode:'SURFACE_POSITION',values:files.map(tr=>trackBEvidenceStableB(tr,copy,'SURFACE_POSITION',S.nowS()))};
    };
    const fixtures={
      covarianceAgreesWithNativeWinner(){
        const precise=seed(4000,225,'PRECISE'),broad=seed(5000,1e6,'BROAD'),files=[precise,broad],plot=S.surface({xM:4001});S.assertNoTruthFields(plot);
        const before=S.snapshotStore(tracks),nis=matrix(files,plot);
        requireFixture(nis.every(Number.isFinite)&&nis[0]<nis[1]&&nis[1]-nis[0]<1,'PRECISE_NATIVE_WINNER_NEAR_EQUAL:'+JSON.stringify(nis));
        const assigned=assign(plot),meta=evidence(files,plot),afterQuery=S.snapshotStore(tracks);
        check('covarianceAgreement.originalNisWinnerSelected',assigned.get(0)?.trackId===precise.trackId);
        check('covarianceAgreement.queryDoesNotUpdateFiles',JSON.stringify(before)===JSON.stringify(afterQuery));
        methods.add('spq9bAcceptSurfacePlotsWip13B1');const accepted=spq9bAcceptSurfacePlotsWip13B1([{plot,pd:.8,panel:0}]);
        check('covarianceAgreement.nativeCallerAcceptedExactlyOne',accepted===1&&tracks.size===2);
        check('covarianceAgreement.preciseFileUpdatedOnce',precise.sensorHits===before.find(t=>t.id===precise.trackId).hits+1);
        check('covarianceAgreement.broadFileUnchanged',JSON.stringify(S.snapshotFile(broad))===JSON.stringify(before.find(t=>t.id===broad.trackId)));
        check('covarianceAgreement.noIdentityOrAuthorityGrant',files.every(tr=>tr.identity==='UNKNOWN'&&tr.engagementAuthority!=='AUTO_AUTHORIZED'));
        return {explicitReceiverOwnedEstimatorInitialCondition:true,seed419012Reproduction:false,naturalRfOrPdEvidence:false,anonymousInput:plot,nativeNis:nis,originalWinner:precise.trackId,before,metadata:meta,queryAssignment:[...assigned],accepted,after:S.snapshotStore(tracks)};
      },
      covarianceConflictsWithNativeWinner(){
        const precise=seed(4000,225,'PRECISE'),broad=seed(4050,1e6,'BROAD'),files=[precise,broad],plot=S.surface({xM:4010});S.assertNoTruthFields(plot);
        const before=S.snapshotStore(tracks),nis=matrix(files,plot);
        requireFixture(nis.every(Number.isFinite)&&nis[1]<nis[0]&&nis[0]-nis[1]<1,'BROAD_NATIVE_WINNER_NEAR_EQUAL:'+JSON.stringify(nis));
        const assigned=assign(plot),meta=evidence(files,plot);check('covarianceConflict.notReplacedByLikelihoodWinner',assigned.size===0);
        check('covarianceConflict.queryDoesNotUpdateFiles',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        methods.add('spq9bAcceptSurfacePlotsWip13B1');const accepted=spq9bAcceptSurfacePlotsWip13B1([{plot,pd:.8,panel:0}]);
        check('covarianceConflict.nativeCallerStillHolds',accepted===0&&tracks.size===2);
        check('covarianceConflict.noUpdatesOrDuplicateBirth',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        return {explicitReceiverOwnedEstimatorInitialCondition:true,physicalTruthUsed:false,anonymousInput:plot,nativeNis:nis,originalWinner:broad.trackId,before,metadata:meta,queryAssignment:[...assigned],accepted,after:S.snapshotStore(tracks)};
      },
      identicalSignalStillHolds(){
        const first=seed(4000,225,'EQUAL_A'),second=seed(4000,225,'EQUAL_B'),files=[first,second],plot=S.surface({xM:4001}),before=S.snapshotStore(tracks),nis=matrix(files,plot);
        requireFixture(nis.every(Number.isFinite)&&Math.abs(nis[0]-nis[1])<1e-9,'EQUAL_NATIVE_NIS');
        const forward=assign(plot),entries=[...tracks];tracks.clear();for(const[id,tr]of entries.reverse())tracks.set(id,tr);const reverse=assign(plot);
        check('equalSignal.forwardAndReverseHeld',forward.size===0&&reverse.size===0);
        check('equalSignal.noFileMutated',before.every(old=>JSON.stringify(old)===JSON.stringify(S.snapshotFile(tracks.get(old.id)))));
        methods.add('spq9bAcceptSurfacePlotsWip13B1');const accepted=spq9bAcceptSurfacePlotsWip13B1([{plot,pd:.8,panel:0}]);
        check('equalSignal.nativeCallerNoUpdateOrBirth',accepted===0&&tracks.size===2&&before.every(old=>JSON.stringify(old)===JSON.stringify(S.snapshotFile(tracks.get(old.id)))));
        return {anonymousInput:plot,nativeNis:nis,before,metadata:evidence(files,plot),forward:[...forward],reverse:[...reverse],accepted,after:S.snapshotStore(tracks)};
      },
      npcCovarianceEvidenceAndOwnerIsolation(){
        const active=S.privateOwner('STABILIZE_ACTIVE'),untouched=S.privateOwner('STABILIZE_UNTOUCHED'),o=observerC(active),other=observerC(untouched);
        const initial=[S.surface({xM:4000}),S.surface({xM:5000})];initial.forEach(S.assertNoTruthFields);methods.add('observerAcceptPlotsC');
        observerAcceptPlotsC(active,initial);observerAcceptPlotsC(untouched,[S.surface({xM:4000})]);
        requireFixture(o.tracks.size===2&&other.tracks.size===1,'TWO_INDEPENDENT_NATIVE_OWNERS');
        const files=[...o.tracks.values()].sort((a,b)=>a._kfX[0]-b._kfX[0]);
        for(const[tr,xM,Pxy]of [[files[0],4000,225],[files[1],5000,1e6]]){
          tr._kfX.set([xM,0,8,0,0,0]);tr._kfP.fill(0);
          for(const[index,value]of [[0,Pxy],[7,Pxy],[14,16],[21,100],[28,100],[35,16]])tr._kfP[index]=value;
          trackSyncLegacyFromEkf(tr);
        }
        const plot=S.surface({xM:4001}),before=S.snapshotStore(o.tracks),otherBefore=S.snapshotStore(other.tracks),stats={...o.stats},nis=matrix(files,plot);
        requireFixture(nis.every(Number.isFinite)&&nis[0]<nis[1]&&nis[1]-nis[0]<1,'NPC_PRECISE_NATIVE_WINNER_NEAR_EQUAL:'+JSON.stringify(nis));
        observerAcceptPlotsC(active,[plot]);
        check('npcCovariance.preciseNativeFileCorrected',o.stats.associated-stats.associated===1&&files[0]._kfX[0]>4000);
        check('npcCovariance.noFalseBirth',o.tracks.size===2&&o.stats.initiated===stats.initiated);
        check('npcCovariance.competingBroadFileUnchanged',JSON.stringify(before[1])===JSON.stringify(S.snapshotFile(files[1])));
        check('npcCovariance.independentOwnerUnchanged',JSON.stringify(otherBefore)===JSON.stringify(S.snapshotStore(other.tracks)));
        check('npcCovariance.globalCanonicalStoreUntouched',tracks.size===0&&o.tracks!==other.tracks&&o.tracks!==tracks);
        check('npcCovariance.noIdentityOrAuthorityGrant',[...o.tracks.values()].every(tr=>tr.identity==='UNKNOWN'&&tr.engagementAuthority==='WITHHELD'));
        return {explicitReceiverOwnedEstimatorInitialCondition:true,physicalTruthUsed:false,anonymousInput:plot,nativeNis:nis,before,otherBefore,after:S.snapshotStore(o.tracks),otherAfter:S.snapshotStore(other.tracks),statsBefore:stats,statsAfter:{...o.stats}};
      },
      surfacePriorDoesNotAddObservationDimension(){
        const a=seed(4000,225,'ALT_A'),b=seed(4000,225,'ALT_B');
        // Receiver state estimate and domain prior differ only in unobserved z.
        a._kfX[2]=120;b._kfX[2]=800;a._kfP[14]=16;b._kfP[14]=1e6;
        for(const tr of [a,b]){tr._surfaceMotionPriorWip13B13=true;trackSyncLegacyFromEkf(tr);}
        const plot=S.surface({xM:4001}),before=S.snapshotStore(tracks),nis=matrix([a,b],plot),assigned=assign(plot),meta=evidence([a,b],plot);
        requireFixture(nis.every(Number.isFinite)&&Math.abs(nis[0]-nis[1])<1e-9,'SURFACE_POSITION_NIS_IGNORES_PRIOR_Z');
        check('surfacePrior.ambiguousDespiteDifferentStoredZ',assigned.size===0);
        check('surfacePrior.noZeroDopplerOrElevationAdded',!('elRad'in plot)&&!('elSigmaDeg'in plot));
        check('surfacePrior.queryIsReadOnly',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        if(meta.available)check('surfacePrior.nativeEvidenceExactlyTwoRows',meta.values.every(q=>q.valid===true&&q.dimensions===2));
        else check('surfacePrior.nativeEvidenceExactlyTwoRows',false);
        return {explicitUnobservedDomainPriorFixture:true,physicalElevationNotMeasured:true,anonymousInput:plot,nativeNis:nis,before,metadata:meta,assignment:[...assigned],after:S.snapshotStore(tracks)};
      }
    };
    const names=selected??Object.keys(fixtures);
    for(const name of names){if(!fixtures[name])throw Error('UNKNOWN_STABILIZATION_NATIVE_FIXTURE:'+name);reset();const beforeSerial=window.__TRACK_B__?__TRACK_B__.snapshot().stats.recorded:0;try{records[name]=fixtures[name]();}catch(error){checks[name+'.completed']=false;errors.push({fixture:name,error:String(error.stack??error),classification:String(error).includes('FIXTURE_PRECONDITION:')?'FIXTURE_PRECONDITION_FAILURE':'NATIVE_RUNTIME_FAILURE'});}afterActionStateByFixture[name]=S.afterActionPassiveState();traceByFixture[name]=window.__TRACK_B__?__TRACK_B__.snapshot().records.filter(row=>row.serial>beforeSerial):[];}
    return {schema:'AEGIS_TRACK_B_STABILIZATION_NATIVE_1',classification:S.classification,naturalRfOrWeaponEvidence:false,existingBHelpersOrAssertionsChanged:false,actualMethods:[...methods].sort(),checks,records,errors,afterActionStateByFixture,traceByFixture,pass:!errors.length&&Object.values(checks).every(Boolean)};
  }
});
