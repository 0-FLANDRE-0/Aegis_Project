// TEST ONLY. Supplemental defect reproductions through actual native functions.
// Separate namespace: native_support.js is reused; existing integration assertions
// and native_integration.js are not edited or loaded by this supplement.
window.__TRACK_B_COHORT_SUPPLEMENT__=Object.freeze({
  state(){return TRACK_B_NATIVE_SUPPORT.afterActionPassiveState();},
  run(){
    const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},errors=[],afterActionStateByFixture={},methods=new Set();
    const check=(name,value)=>{checks[name]=!!value;};
    const requireFixture=(condition,reason)=>{if(!condition)throw Error('FIXTURE_PRECONDITION:'+reason);};
    const close=(a,b,tolerance=1e-6)=>Number.isFinite(a)&&Math.abs(a-b)<=tolerance;
    const reset=()=>{
      __GB_TEST__.reset(419025);S.resetPrivateOwnerEvidence();BATTLESPACE_DIAG_BYPASS=true;emconActive=true;tracks.clear();
      if(window.__TRACK_A__){__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear();}
      if(window.__TRACK_B__){__TRACK_B__.configure({enabled:true,capacity:4096});__TRACK_B__.clear();}
    };
    const seedPair=(label,xs)=>{
      const owner=S.privateOwner(label),o=observerC(owner),initial=xs.map(xM=>S.surface({xM}));initial.forEach(S.assertNoTruthFields);
      methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,initial);
      requireFixture(o.tracks.size===2,'TWO_NATIVE_SURFACE_FILES');
      const files=[...o.tracks.values()].sort((a,b)=>a._kfX[0]-b._kfX[0]);
      for(let i=0;i<files.length;i++){
        const tr=files[i];
        // Explicit receiver-estimator initial condition, not a physical entity
        // or product coefficient change. The actual native EKF was initialized.
        tr._kfX.set([xs[i],0,8,0,0,0]);
        for(let r=0;r<6;r++)for(let c=0;c<6;c++)if(r<3||c<3)tr._kfP[r*6+c]=0;
        tr._kfP[0]=tr._kfP[7]=tr._kfP[14]=225;
        methods.add('trackSyncLegacyFromEkf');trackSyncLegacyFromEkf(tr);
        requireFixture(tr.domain==='SURFACE'&&tr._kfP[0]===225&&tr._kfX[0]===xs[i],'NATIVE_SURFACE_STATE_AND_COVARIANCE');
      }
      return {owner,o,files,initial};
    };
    const fixtures={
      npcActualGreedyTrap(){
        const {owner,o,files,initial}=seedPair('NPC_GREEDY_SUPPLEMENT',[4000,4150]),plots=[S.surface({xM:4040}),S.surface({xM:3940})],before=S.snapshotStore(o.tracks),statsBefore={...o.stats};plots.forEach(S.assertNoTruthFields);
        methods.add('trackSurfacePositionAssociationNisWip13B9');
        // These are actual native NIS calls, not injected costs or a replica.
        const costs=plots.map(plot=>files.map(tr=>trackSurfacePositionAssociationNisWip13B9(tr,plot))),expected=[[1600/450,12100/450],[3600/450,44100/450]];
        const preconditions={actualNativeCostsMatchAnchor:costs.every((row,i)=>row.every((value,j)=>close(value,expected[i][j]))),nativeGateGraph:costs[0][0]<=64&&costs[0][1]<=64&&costs[1][0]<=64&&costs[1][1]>64,nativeCostQueriesDidNotMutate:JSON.stringify(before)===JSON.stringify(S.snapshotStore(o.tracks))};
        requireFixture(Object.values(preconditions).every(Boolean),'NPC_NATIVE_COST_GRAPH:'+JSON.stringify({costs,preconditions}));
        methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,plots);
        const after=S.snapshotStore(o.tracks),associatedDelta=o.stats.associated-statsBefore.associated,birthDelta=o.stats.initiated-statsBefore.initiated;
        check('npcCohort.twoFilesRetained',o.tracks.size===2);
        check('npcCohort.twoNativeCorrections',associatedDelta===2);
        check('npcCohort.noFalseBirth',birthDelta===0);
        check('npcCohort.uniqueTwoEdgeMatchingApplied',files[0]._kfX[0]<4000&&files[1]._kfX[0]<4150);
        check('npcCohort.ownerCanonicalIndependent',o.tracks!==tracks&&tracks.size===0);
        check('npcCohort.noIdentityOrAuthorityGrant',[...o.tracks.values()].every(tr=>tr.identity==='UNKNOWN'&&tr.engagementAuthority==='WITHHELD'));
        return {explicitReceiverFilterInitialCondition:true,physicalTruthUsed:false,initial,plots,nativeCostMatrix:costs,nativeGate:64,fixturePreconditions:preconditions,before,after,associatedDelta,birthDelta,fileCount:o.tracks.size,statsBefore,statsAfter:{...o.stats},legacyDefectObserved:o.tracks.size===3&&associatedDelta===1&&birthDelta===1};
      },
      hawklinkActualSequentialFalseReplay(){
        // The exact4030m midpoint was genuinely non-reproducing: actual native
        // conversion roundoff made T1 cheaper by8.7e-14. Keep that archived run;
        // use a declared1m-left measurement bias to require the intended old T0
        // choice. Initial surface observation range sigma is15m and the report
        // horizontal sigma is20m. Only the fixture's old-path choice is stabilized;
        // no product comparator, gain, threshold, Pd or Pk is changed.
        const {owner,o,files,initial}=seedPair('HAWK_FALSE_REPLAY_SUPPLEMENT',[4000,4060]),now=S.nowS(),reports=[S.report({sequence:1,measuredAtS:now,xM:4029}),S.report({sequence:2,measuredAtS:now,xM:4000})],before=S.snapshotStore(o.tracks);reports.forEach(S.assertNoTruthFields);
        methods.add('offboardPlotC');methods.add('trackCartesianAssociationNisV33');
        const measurements=reports.map(report=>offboardPlotC(report,now)),costs=measurements.map(meas=>files.map(tr=>trackCartesianAssociationNisV33(tr,meas))),expected=[[1.3456,1.5376],[0,5.76]];
        const preconditions={sameSourceAndEpoch:reports.every(q=>q.sourceId==='H1'&&q.measuredAtS===now),actualNativeCostsMatchAnchor:costs.every((row,i)=>row.every((value,j)=>close(value,expected[i][j]))),firstSequentialNativeScoreStrictlyFavorsT0:costs[0][0]<costs[0][1],nativeGateGraph:costs.every(row=>row.every(value=>value<=25)),uniqueFullCohortMatching:costs[0][1]+costs[1][0]<costs[0][0]+costs[1][1]-1,nativeCostQueriesDidNotMutate:JSON.stringify(before)===JSON.stringify(S.snapshotStore(o.tracks))};
        requireFixture(Object.values(preconditions).every(Boolean),'HAWK_NATIVE_COST_GRAPH:'+JSON.stringify({costs,preconditions}));
        methods.add('configureOffboardSourceC');const link=configureOffboardSourceC(owner,{sourceId:'H1',connected:true,latencyS:0});requireFixture(link.ok,'HAWK_LINK_SETUP');
        methods.add('ingestOffboardReportC');const ingested=reports.map(report=>ingestOffboardReportC(owner,report));requireFixture(ingested.every(q=>q.ok),'HAWK_SCHEMA_INGRESS:'+JSON.stringify(ingested));
        const acceptedBefore=o.offboard.accepted,rejectedBefore=o.offboard.rejected;methods.add('drainOffboardC');drainOffboardC(owner);
        const acceptedDelta=o.offboard.accepted-acceptedBefore,rejectedDelta=o.offboard.rejected-rejectedBefore,after=S.snapshotStore(o.tracks),sequences=files.map(tr=>tr.observationReportsC?.remote?.H1?.sequence??null);
        check('hawkCohort.bothNativeReportsAccepted',acceptedDelta===2);
        check('hawkCohort.noFalseRepeatedFixRejection',rejectedDelta===0);
        check('hawkCohort.uniqueFullCohortMatchingApplied',sequences[0]===2&&sequences[1]===1);
        check('hawkCohort.bothOriginalFilesPreserved',o.tracks.size===2&&files.every(tr=>o.tracks.has(tr.trackId)));
        check('hawkCohort.eachOriginalFileUpdatedOnce',files.every((tr,i)=>tr.sensorHits===before[i].hits+1));
        check('hawkCohort.originalMeasurementTimePreserved',files.every(tr=>tr.observationReportsC?.remote?.H1?.measuredAtS===now));
        check('hawkCohort.ownerCanonicalIndependent',o.tracks!==tracks&&tracks.size===0);
        check('hawkCohort.noIdentityOrAuthorityGrant',files.every(tr=>tr.identity==='UNKNOWN'&&tr.engagementAuthority==='WITHHELD'));
        return {explicitReceiverFilterInitialCondition:true,physicalTruthUsed:false,midpointMeasurementBiasM:-1,initialSurfaceRangeSigmaM:15,reportedHorizontalSigmaM:20,priorMidpointAttempt:'Archived actual4030m run did not reproduce: native floating conversion preferred T1;1m fixture bias only stabilizes the old-path choice; no product comparator, coefficient, Pd or Pk changed.',initial,reports,measurements,nativeCostMatrix:costs,nativeGate:25,fixturePreconditions:preconditions,before,after,ingested,acceptedDelta,rejectedDelta,sequences,fileCount:o.tracks.size,legacyDefectObserved:acceptedDelta===1&&rejectedDelta===1&&sequences[0]===1&&sequences[1]===null};
      }
    };
    for(const[name,fixture]of Object.entries(fixtures)){
      reset();try{records[name]=fixture();}catch(error){checks[name+'.completed']=false;errors.push({fixture:name,error:String(error.stack??error),classification:String(error).includes('FIXTURE_PRECONDITION:')?'FIXTURE_PRECONDITION_FAILURE':'NATIVE_RUNTIME_FAILURE'});}
      afterActionStateByFixture[name]=S.afterActionPassiveState();
    }
    return {schema:'AEGIS_TRACK_B_COHORT_SUPPLEMENT_1',classification:S.classification,naturalRfOrWeaponEvidence:false,actualMethods:[...methods].sort(),checks,records,errors,afterActionStateByFixture,pass:!errors.length&&Object.values(checks).every(Boolean),existingAssertionsChanged:false,existingIntegrationHelperChanged:false};
  }
});
