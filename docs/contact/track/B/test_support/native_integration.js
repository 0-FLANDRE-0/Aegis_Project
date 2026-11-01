// TEST ONLY. Requires native_support.js in the actual packed-game harness scope.
// New TRACK-B contract assertions may intentionally fail on the TRACK-A baseline.
// No alternate NIS, gate, assignment, EKF, or track classifier is implemented here.
window.__TRACK_B_NATIVE_INTEGRATION__=Object.freeze({
  async run(selected=null){
    const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},afterActionStateByFixture={},errors=[],methods=new Set();
    const check=(name,value)=>{checks[name]=!!value;};
    const seedOwn=plot=>{S.assertNoTruthFields(plot);methods.add('updateSensorTrackMeasurement');return updateSensorTrackMeasurement(null,plot,{source:plot.source,taskType:'SEARCH_VOLUME'});};
    const reset=()=>{__GB_TEST__.reset(419025);S.resetPrivateOwnerEvidence();BATTLESPACE_DIAG_BYPASS=true;emconActive=true;tracks.clear();if(window.__TRACK_A__){__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear();}};
    const task=()=>({type:'SEARCH_VOLUME',face:0,azWorld:0,azHalfRad:.5,elRad:.01,elHalfRad:.2,gateRangeM:50000,rangeWorld:metersToWorld(50000)});
    const assignOwn=plots=>{plots.forEach(S.assertNoTruthFields);methods.add('spyGlobalAssignmentsV36');return spyGlobalAssignmentsV36(plots,new Set(),new Set(),task());};
    const seedFirmSurface=()=>{const plot=S.surface(),tr=seedOwn(plot);updateSensorTrackMeasurement(tr.trackId,plot,{source:plot.source,taskType:'SURFACE_PRECISION'});if(!tr.confirmed)throw Error('NATIVE_FIRM_SURFACE_PRECONDITION');return tr;};
    const fixtures={
      ownDopplerCrossing(){
        const positive=seedOwn(S.air({vxMps:100})),negative=seedOwn(S.air({vxMps:-100}));
        const plots=[S.air({vxMps:-100}),S.air({vxMps:100})],before=S.snapshotStore(tracks),a=assignOwn(plots);
        check('ownCross.twoAssigned',a.size===2);check('ownCross.oneToOne',new Set([...a.values()].map(q=>q.trackId)).size===a.size);
        check('ownCross.measuredDopplerDistinguishes',a.get(0)?.trackId===negative.trackId&&a.get(1)?.trackId===positive.trackId);
        check('ownCross.associationDoesNotMutate',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        return {anonymousInputs:plots,before,assignment:[...a]};
      },
      ownExactAmbiguity(){
        seedOwn(S.air());seedOwn(S.air());const before=S.snapshotStore(tracks),plots=[S.air()],a=assignOwn(plots);
        check('ownAmbiguity.assignmentWithheld',a.size===0);check('ownAmbiguity.existingFilesUnchanged',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        return {anonymousInputs:plots,before,assignment:[...a],note:'Same predicted states and covariance; no observable reason to pick either numeric ID.'};
      },
      ownAmbiguityPermutations(){
        seedOwn(S.air());seedOwn(S.air());const first=assignOwn([S.air({yM:-1}),S.air({yM:1})]);
        const entries=[...tracks];tracks.clear();for(const[id,tr]of entries.reverse())tracks.set(id,tr);
        const second=assignOwn([S.air({yM:1}),S.air({yM:-1})]);
        check('ownPermutation.tiedRowsWithheld',first.size===0&&second.size===0);return {first:[...first],reversed:[...second]};
      },
      ownAirCallerAmbiguityNoBirth(){
        for(let n=0;n<2;n++){const tr=seedOwn(S.air());for(let hit=0;hit<2;hit++)updateSensorTrackMeasurement(tr.trackId,S.air(),{source:'SPY1DV_SEARCH_VOLUME',taskType:'SEARCH_VOLUME'});if(!tr.confirmed)throw Error('NATIVE_FIRM_AIR_PRECONDITION');}
        const before=S.snapshotStore(tracks),plots=[S.air()],originalExtractor=spyCollectUnifiedEchoPlotsWip13B13;methods.add('executeSpyTask');
        // Test-only post-extractor seam; native execute/association/update stay intact.
        spyCollectUnifiedEchoPlotsWip13B13=()=>({surfacePlots:[],airPlots:plots,dwell:{candidateCount:1},falseCount:0,attempted:1});let result;
        try{result=executeSpyTask({...task(),face:SPY1DV_FACE_KEYS[0]});}finally{spyCollectUnifiedEchoPlotsWip13B13=originalExtractor;}
        check('ownAirCaller.heldExistingFilesNotUpdated',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));check('ownAirCaller.heldPlotNotRebornAsTentative',tracks.size===2&&result.hits===0);
        return {postRfExtractorSeam:true,naturalRfNotExercised:true,before,after:S.snapshotStore(tracks),result};
      },
      ownTwoHundredFiftySevenPlotSafety(){
        const tr=seedOwn(S.air()),id=tr.trackId;for(let hit=0;hit<2;hit++)updateSensorTrackMeasurement(id,S.air(),{source:'SPY1DV_SEARCH_VOLUME',taskType:'SEARCH_VOLUME'});
        const before=S.snapshotFile(tr),plots=Array.from({length:257},()=>S.air()),assigned=assignOwn(plots),originalExtractor=spyCollectUnifiedEchoPlotsWip13B13;methods.add('executeSpyTask');
        spyCollectUnifiedEchoPlotsWip13B13=()=>({surfacePlots:[],airPlots:plots,dwell:{candidateCount:257},falseCount:0,attempted:257});let result;
        try{result=executeSpyTask({...task(),face:SPY1DV_FACE_KEYS[0]});}finally{spyCollectUnifiedEchoPlotsWip13B13=originalExtractor;}
        check('largeBatch.realOwnAssignmentReturnedWithoutException',assigned instanceof Map);check('largeBatch.oversizeConnectedComponentHeld',assigned.size===0);
        check('largeBatch.heldCallerDoesNotCreate257Tentatives',tracks.size===1&&tracks.has(id)&&result.hits===0);check('largeBatch.existingFileUntouched',JSON.stringify(before)===JSON.stringify(S.snapshotFile(tr)));
        return {postRfExtractorStressFixture:true,naturalRfFrequencyOrResolutionNotClaimed:true,plotCount:257,assignedCount:assigned.size,before,afterFileCount:tracks.size,afterOriginalFile:S.snapshotFile(tr),result};
      },
      ownPerDwellExclusions(){
        const a=seedOwn(S.air({vxMps:100})),b=seedOwn(S.air({vxMps:-100})),plots=[S.air({vxMps:100}),S.air({vxMps:-100})];methods.add('spyGlobalAssignmentsV36');
        const result=spyGlobalAssignmentsV36(plots,new Set(),new Set([a.trackId]),task());check('dwell.alreadyUsedTrackNotReused',![...result.values()].some(q=>q.trackId===a.trackId));check('dwell.otherFileRemainsUsable',result.get(1)?.trackId===b.trackId);
        methods.add('spyBestPlotForTrackV31');const one=spyBestPlotForTrackV31(a.trackId,[plots[0]],new Set(),{...task(),type:'TRACK_REVISIT'}),two=spyBestPlotForTrackV31(a.trackId,[plots[0]],new Set(),{...task(),type:'TRACK_REVISIT'});
        check('dwell.separateFocusedDwellsRemainLegal',one?.index===0&&two?.index===0);return {assignment:[...result],focusedFirst:one,focusedSecond:two};
      },
      ownNativeCoastAndReacquisition(){
        const initial=S.air({xM:4000,vxMps:100}),tr=seedOwn(initial),id=tr.trackId;
        S.advanceTicks(30);const stored=tracks.get(id);if(!stored)throw Error('NATIVE_COAST_FILE_DROPPED_DURING_SHORT_GAP');
        const before=S.snapshotFile(stored),plot=S.air({xM:stored._kfX[0],yM:stored._kfX[1],zM:stored._kfX[2],vxMps:stored._kfX[3],vyMps:stored._kfX[4],vzMps:stored._kfX[5]}),assignment=assignOwn([plot]);
        check('coast.actualNativePredictionAdvanced',Math.abs(stored._kfX[0]-4000)>20);check('coast.actualMeasurementAgeIncreased',stored.sensorAge>=.49);
        check('coast.validSameFileReacquisition',assignment.get(0)?.trackId===id);check('coast.associationQueryDidNotFreshenFile',JSON.stringify(before)===JSON.stringify(S.snapshotFile(stored)));
        return {shortGapSeconds:.5,actualFullFixedTicks:30,measurementDerivedFromReceiverFilterForSelfConsistencyOnly:true,noPhysicalTargetTruth:true,before,anonymousInput:plot,assignment:[...assignment]};
      },
      npcDopplerCrossing(){
        const owner=S.privateOwner('DOPPLER'),o=observerC(owner),initial=[S.air({vxMps:100}),S.air({vxMps:-100})];
        methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,initial);const before=S.snapshotStore(o.tracks),ids=[...o.tracks.keys()],associated=o.stats.associated;
        observerAcceptPlotsC(owner,[initial[1],initial[0]]);
        check('npcCross.twoFiles',o.tracks.size===2&&ids.every(id=>o.tracks.has(id)));check('npcCross.twoNativeAssociations',o.stats.associated-associated===2);
        check('npcCross.dopplerSignsPreserved',before.every(t=>Math.sign(o.tracks.get(t.id)?._kfX[3])===Math.sign(t.x[3])));
        check('npcCross.independentOwnerStore',o.tracks!==tracks&&tracks.size===0);
        return {before,after:S.snapshotStore(o.tracks),stats:{...o.stats}};
      },
      npcExactAmbiguity(){
        const owner=S.privateOwner('AMBIGUITY'),o=observerC(owner);methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,[S.air(),S.air()]);
        const before=S.snapshotStore(o.tracks),ids=[...o.tracks.keys()];observerAcceptPlotsC(owner,[S.air()]);
        check('npcAmbiguity.existingFilesNotArbitrarilyUpdated',before.every(old=>JSON.stringify(old)===JSON.stringify(S.snapshotFile(o.tracks.get(old.id)))));
        check('npcAmbiguity.noIdentityEscalation',[...o.tracks.values()].every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD'));
        check('npcAmbiguity.newFilesTentative',[...o.tracks.values()].filter(t=>!ids.includes(t.trackId)).every(t=>!t.confirmed));
        return {before,after:S.snapshotStore(o.tracks),stats:{...o.stats}};
      },
      hugeCovarianceDistanceSanity(){
        const tr=seedOwn(S.air({xM:3000}));for(const index of [0,7,14])tr._kfP[index]=1e14;
        const plot=S.air({xM:100000}),before=S.snapshotStore(tracks);methods.add('trackRadarAssociationNisV31');const nis=trackRadarAssociationNisV31(tr,plot),a=assignOwn([plot]);
        check('sanity.fixtureNativeNisEligible',nis<=spyAssociationGateV31(task()));check('sanity.distanceStillRejects',a.size===0);
        check('sanity.nativeFilterStateUnchanged',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));
        return {explicitEstimatedCovarianceFixture:true,anonymousInput:plot,nativeNis:nis,assignment:[...a],before};
      },
      airThenSurfacePrior(){
        const tr=seedOwn(S.air({zM:120})),id=tr.trackId,before=S.snapshotFile(tr),plot=S.surface();methods.add('spq9bAcceptSurfacePlotsWip13B1');
        const accepted=spq9bAcceptSurfacePlotsWip13B1([{plot,pd:.8,panel:0}]);
        check('dimension.sameCanonicalFile',accepted===1&&tracks.size===1&&tracks.has(id));check('dimension.priorDidNotCollapseObservedHeight',Math.abs(tr._kfX[2]-before.x[2])<5&&Math.abs(tr._kfX[2]-8)>50);
        check('dimension.noDopplerOrElevationFabrication',!('elRad'in plot)&&!('elSigmaDeg'in plot));check('dimension.noIdentityEscalation',tr.identity==='UNKNOWN');
        return {anonymousInput:plot,before,after:S.snapshotFile(tr),accepted};
      },
      spqSurfaceAmbiguityNoBirth(){
        seedFirmSurface();seedFirmSurface();const before=S.snapshotStore(tracks);methods.add('spq9bAcceptSurfacePlotsWip13B1');const accepted=spq9bAcceptSurfacePlotsWip13B1([S.surface(),S.surface()].map(plot=>({plot,pd:.8,panel:0})));
        check('spqAmbiguity.noExistingFileUpdate',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));check('spqAmbiguity.noFalseTentativeBirth',tracks.size===2&&accepted===0);return {before,after:S.snapshotStore(tracks),accepted};
      },
      surfaceStagedHoldNoAirFallback(){
        seedFirmSurface();seedFirmSurface();seedOwn(S.air({zM:8}));const before=S.snapshotStore(tracks);methods.add('spq9bAcceptSurfacePlotsWip13B1');const accepted=spq9bAcceptSurfacePlotsWip13B1([{plot:S.surface(),pd:.8,panel:0}]);
        check('surfaceStage.heldEstablishedCompetitionNotSentToAirRecovery',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));check('surfaceStage.noFallbackBirth',tracks.size===3&&accepted===0);return {before,after:S.snapshotStore(tracks),accepted};
      },
      bridgeMasterAmbiguityNoBirth(){
        seedFirmSurface();seedFirmSurface();const before=S.snapshotStore(tracks),plot=S.surface();plot.source='BRIDGEMASTER_E_SURFACE';delete plot.radialMps;delete plot.radialVelSigmaMps;
        methods.add('bridgeMasterEAcceptAnonymousPlotsV35');const accepted=bridgeMasterEAcceptAnonymousPlotsV35([{plot,pd:.8,snr:10,rcs:100}]);
        check('bridgeAmbiguity.noExistingFileUpdate',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));check('bridgeAmbiguity.noFalseTentativeBirth',tracks.size===2&&accepted===0);return {before,after:S.snapshotStore(tracks),accepted};
      },
      spySurfaceAmbiguityNoBirth(){
        seedFirmSurface();seedFirmSurface();const before=S.snapshotStore(tracks),plot=S.surface();plot.source='SPY1DV_SURFACE_SEARCH';methods.add('spyExecuteSurfacePlotsWip13B9');
        const result=spyExecuteSurfacePlotsWip13B9({...task(),type:'SEARCH_HORIZON',expectedRevisitS:.2},{plots:[plot],attempted:1});
        check('spySurfaceAmbiguity.noExistingFileUpdate',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));check('spySurfaceAmbiguity.noFalseTentativeBirth',tracks.size===2&&result.hits===0);return {before,after:S.snapshotStore(tracks),result};
      },
      npcSurfaceThenAir(){
        const owner=S.privateOwner('TWO_TO_THREE'),o=observerC(owner);methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,[S.surface()]);
        const id=[...o.tracks.keys()][0],before=S.snapshotStore(o.tracks);observerAcceptPlotsC(owner,[S.air({zM:50})]);
        check('dimension.npc2DThen3DSameFile',o.tracks.size===1&&o.tracks.has(id));check('dimension.npcActualElevationContributes',(o.tracks.get(id)?._kfX[2]??0)>8);
        return {before,after:S.snapshotStore(o.tracks)};
      },
      nativeFalsePlot(){
        methods.add('spyFalsePlotV31');const plot=spyFalsePlotV31(task());S.assertNoTruthFields(plot);const tr=seedOwn(plot);
        check('falsePlot.oneReturnIsNotConfirmed',tracks.size===1&&!tr.confirmed);check('falsePlot.noIdentityOrAuthorityGrant',tr.identity==='UNKNOWN'&&tr.engagementAuthority!=='AUTO_AUTHORIZED');
        return {actualFalsePlotGenerator:true,naturalFalseAlarmFrequencyNotMeasured:true,anonymousInput:plot,file:S.snapshotFile(tr)};
      },
      hawklinkResolvedBatch(){
        const owner=S.privateOwner('HAWK_BATCH'),o=observerC(owner);methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,[S.surface({yM:-200}),S.surface({yM:200})]);
        const before=S.snapshotStore(o.tracks),ids=[...o.tracks.keys()],at=S.nowS();methods.add('configureOffboardSourceC');configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});
        const reports=[S.report({sequence:1,measuredAtS:at,yM:200}),S.report({sequence:2,measuredAtS:at,yM:-200})];methods.add('ingestOffboardReportC');const accepted=reports.map(p=>ingestOffboardReportC(owner,p));methods.add('drainOffboardC');drainOffboardC(owner);
        check('hawkBatch.nativeSchemaAccepted',accepted.every(q=>q.ok));check('hawkBatch.twoSeparateFiles',o.tracks.size===2&&ids.every(id=>o.tracks.has(id)));
        check('hawkBatch.eachFileReceivedOneReport',ids.every(id=>o.tracks.get(id).observationReportsC?.remote?.H1?.measuredAtS===at));
        check('hawkBatch.ownCanonicalStoreUntouched',tracks.size===0);return {before,after:S.snapshotStore(o.tracks),reports,accepted,stats:{...o.stats},offboardAccepted:o.offboard.accepted};
      },
      hawklinkReplayIsPerPair(){
        S.advanceTicks(720);const owner=S.privateOwner('HAWK_PAIR_REPLAY'),o=observerC(owner),now=S.nowS();methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,[S.surface({yM:-600}),S.surface({yM:600})]);
        methods.add('configureOffboardSourceC');configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});methods.add('ingestOffboardReportC');methods.add('drainOffboardC');
        const reports=[S.report({sequence:1,measuredAtS:now-2,yM:-600}),S.report({sequence:2,measuredAtS:now-3,yM:600})];
        for(const report of reports){const accepted=ingestOffboardReportC(owner,report);if(!accepted.ok)throw Error('REPLAY_FIXTURE_SEED_SCHEMA:'+accepted.reason);drainOffboardC(owner);}
        const old=[...o.tracks.values()].find(t=>t.observationReportsC?.remote?.H1?.measuredAtS===now-2),fresh=[...o.tracks.values()].find(t=>t.observationReportsC?.remote?.H1?.measuredAtS===now-3);
        if(!old||!fresh||old===fresh)throw Error('REPLAY_FIXTURE_REQUIRES_TWO_DISTINCT_NATIVE_FILES');
        // Explicit estimator-covariance fixture, not physical truth or RF tuning.
        for(const tr of [old,fresh])for(const index of [0,7,14])tr._kfP[index]=1e6;
        const oldBefore=S.snapshotFile(old),freshBefore=S.snapshotFile(fresh),incoming=S.report({sequence:3,measuredAtS:now-2,yM:600});
        const accepted=ingestOffboardReportC(owner,incoming);drainOffboardC(owner);
        check('hawkPair.incomingSchemaAccepted',accepted.ok);check('hawkPair.repeatedOtherPairDoesNotBlockValidFile',fresh.observationReportsC?.remote?.H1?.sequence===3&&fresh.sensorHits===freshBefore.hits+1);
        check('hawkPair.repeatedOldFileNotUpdated',JSON.stringify(oldBefore)===JSON.stringify(S.snapshotFile(old)));check('hawkPair.noFalseBirth',o.tracks.size===2);
        return {explicitEstimatedCovarianceFixture:true,physicalTruthUsed:false,reports,incoming,oldBefore,freshBefore,oldAfter:S.snapshotFile(old),freshAfter:S.snapshotFile(fresh),accepted};
      },
      hawklinkDistantReplayDoesNotBlockBirth(){
        S.advanceTicks(720);const owner=S.privateOwner('HAWK_DISTANT_REPLAY'),o=observerC(owner),now=S.nowS();methods.add('configureOffboardSourceC');configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});
        const first=S.report({sequence:1,measuredAtS:now-2,xM:3000}),incoming=S.report({sequence:2,measuredAtS:now-2,xM:100000});methods.add('ingestOffboardReportC');methods.add('drainOffboardC');
        const seed=ingestOffboardReportC(owner,first);drainOffboardC(owner);const old=[...o.tracks.values()][0];if(!seed.ok||!old)throw Error('DISTANT_REPLAY_NATIVE_SEED_FAILED');
        for(const index of [0,7,14])old._kfP[index]=1e14;const before=S.snapshotFile(old),accepted=ingestOffboardReportC(owner,incoming);drainOffboardC(owner);
        check('hawkDistant.incomingSchemaAccepted',accepted.ok);check('hawkDistant.repeatedDistantFileDoesNotBlockLegitimateBirth',o.tracks.size===2&&[...o.tracks.values()].some(t=>t!==old&&t.observationReportsC?.remote?.H1?.sequence===2));
        check('hawkDistant.oldFilterUnchanged',JSON.stringify(before)===JSON.stringify(S.snapshotFile(old)));return {explicitEstimatedCovarianceFixture:true,physicalTruthUsed:false,first,incoming,before,after:S.snapshotStore(o.tracks),accepted};
      },
      hawklinkHugeMeasurementCovariance(){
        const owner=S.privateOwner('HAWK_MEASUREMENT_COV'),o=observerC(owner);methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,[S.surface({xM:3000})]);const old=[...o.tracks.values()][0],before=S.snapshotFile(old);
        methods.add('configureOffboardSourceC');configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});const report=S.report({xM:100000,covarianceM2:[1e10,0,0,0,1e10,0,0,0,16]});
        methods.add('offboardPlotC');methods.add('trackCartesianAssociationNisV33');const measurement=offboardPlotC(report,S.nowS()),nativeNis=trackCartesianAssociationNisV33(old,measurement);methods.add('ingestOffboardReportC');methods.add('drainOffboardC');const accepted=ingestOffboardReportC(owner,report);drainOffboardC(owner);
        check('hawkHugeR.fixtureNativeNisEligible',nativeNis<=25);check('hawkHugeR.schemaAccepted',accepted.ok);check('hawkHugeR.farExistingFileNotMerged',JSON.stringify(before)===JSON.stringify(S.snapshotFile(old)));
        check('hawkHugeR.noForcedConfirmationOrAuthority',[...o.tracks.values()].filter(t=>t!==old).every(t=>!t.confirmed&&t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD'));
        return {explicitLargeReportedCovarianceFixture:true,physicalTruthUsed:false,report,nativeNis,before,after:S.snapshotStore(o.tracks),accepted};
      },
      hawklinkNativeTimeAndDelayContract(){
        S.advanceTicks(960);const now=S.nowS(),owner=S.privateOwner('HAWK_TIME'),o=observerC(owner);methods.add('configureOffboardSourceC');configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});methods.add('ingestOffboardReportC');methods.add('drainOffboardC');
        const future=ingestOffboardReportC(owner,S.report({sequence:1,measuredAtS:now+.001})),tooOld=ingestOffboardReportC(owner,S.report({sequence:1,measuredAtS:now-15.001})),boundary=S.report({sequence:1,measuredAtS:now-15}),accepted=ingestOffboardReportC(owner,boundary);drainOffboardC(owner);
        check('hawkTime.futureRejected',!future.ok&&future.reason==='REPORT_TIME_OR_REPLAY');check('hawkTime.over15SecondsRejected',!tooOld.ok&&tooOld.reason==='REPORT_TIME_OR_REPLAY');check('hawkTime.exact15SecondsAccepted',accepted.ok&&o.tracks.size===1);
        const old=[...o.tracks.values()][0];check('hawkTime.originalAgeNotReceiptEpoch',old?.observationReportsC?.remote?.H1?.measuredAtS===boundary.measuredAtS&&Math.abs(old.sensorAge-15)<1e-8);
        const delayed=S.privateOwner('HAWK_DELAY'),d=observerC(delayed),at=S.nowS(),report=S.report({sourceId:'H2',sequence:1,measuredAtS:at-1});configureOffboardSourceC(delayed,{sourceId:'H2',connected:true,latencyS:.5});const queued=ingestOffboardReportC(delayed,report);drainOffboardC(delayed);
        check('hawkDelay.noEarlyDelivery',queued.ok&&d.tracks.size===0&&d.offboard.queue.length===1);S.advanceTicks(30);drainOffboardC(delayed);const tr=[...d.tracks.values()][0],age=S.nowS()-report.measuredAtS;
        check('hawkDelay.deliveredAtOriginalMeasurementAge',d.tracks.size===1&&Math.abs(tr.sensorAge-age)<1e-8&&tr.observationReportsC?.remote?.H2?.measuredAtS===report.measuredAtS);
        check('hawkDelay.existingAgeSquaredCovariancePreserved',!!tr&&tr._kfP[0]>=report.covarianceM2[0]+age*age*12*12-1e-8);
        return {future,tooOld,boundary,accepted,oldFile:S.snapshotFile(old),delayed:{report,queued,deliveredAtS:S.nowS(),file:S.snapshotFile(tr)},newGeneralTimeAlignmentModelClaimed:false};
      },
      c55BothNativeContexts(){
        if(!window.__TRACK_B_C55_NATIVE__)throw Error('C55_NATIVE_TEST_HELPER_MISSING');const result=__TRACK_B_C55_NATIVE__.run();
        for(const[name,value]of Object.entries(result.checks))check('c55.'+name,value);for(const name of ['c55SensorSweep','c55Bank','c55UpdateFile','c55AssociateCms'])methods.add(name);
        return {classification:result.classification,naturalRfPdDwellOrWeaponEvidence:result.naturalRfPdDwellOrWeaponEvidence,liveC55PolicyChanged:result.liveC55PolicyChanged,records:result.records};
      }
    };
    const names=selected??Object.keys(fixtures);for(const name of names){if(!fixtures[name])throw Error('UNKNOWN_NATIVE_B_FIXTURE:'+name);reset();try{records[name]=fixtures[name]();}catch(error){checks[name+'.completed']=false;errors.push({fixture:name,error:String(error.stack??error)});}afterActionStateByFixture[name]=S.afterActionPassiveState();}
    // Raw AFTER_ACTION strings are consumed only by the runner's SHA-256. They
    // are never passed back to any association/track/gameplay function or saved.
    return {schema:'AEGIS_TRACK_B_NATIVE_INTEGRATION_1',classification:S.classification,naturalRfOrWeaponEvidence:false,actualMethods:[...methods].sort(),checks,records,afterActionStateByFixture,errors,pass:Object.values(checks).every(Boolean)&&errors.length===0,expectationsChanged:false,traceSnapshot:window.__TRACK_A__?__TRACK_A__.snapshot():null};
  }
});
