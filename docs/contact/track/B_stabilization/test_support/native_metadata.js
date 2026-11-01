// TEST ONLY. Native innovation-matrix contract checks; no second sensor/model.
// Capture the S actually passed to the native inverse on one actual NIS call,
// then restore that function before invoking the product evidence helper.
window.__TRACK_B_STABILIZATION_METADATA__=Object.freeze({
  run(){
    const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},errors=[],methods=new Set();
    const check=(k,v)=>{checks[k]=!!v;},requireFixture=(ok,why)=>{if(!ok)throw Error('FIXTURE_PRECONDITION:'+why);};
    const available=typeof window.__TRACK_B__?.evidence==='function',evidence=(...args)=>available?__TRACK_B__.evidence(...args):({valid:false,reason:'API_UNAVAILABLE'});
    // All products execute the same real ticks/native inputs, even when the
    // older B build has no candidate evidence API. Unsupported is retained.
    S.advanceTicks(120);
    const snapshot=tr=>JSON.stringify({x:Array.from(tr._kfX),P:Array.from(tr._kfP),measurementStep:tr._lastMeasurementStep,hits:tr.sensorHits,age:tr.sensorAge,source:tr.sensorSource});
    const seed=()=>{
      const tr=updateSensorTrackMeasurement(null,S.air({xM:12000,yM:7000,zM:1500,vxMps:-240,vyMps:30,vzMps:-10}),{source:'SPY1DV_SEARCH_VOLUME',taskType:'SEARCH_VOLUME'});methods.add('updateSensorTrackMeasurement');
      tr._kfX.set([12000,7000,1500,-240,30,-10]);tr._kfP.fill(0);for(let i=0;i<6;i++)tr._kfP[i*6+i]=500;tr._kfP[3]=tr._kfP[18]=20;tr._kfP[10]=tr._kfP[25]=15;trackSyncLegacyFromEkf(tr);return tr;
    };
    const captured=(fn,tr,meas,n)=>{
      const original=_matInv,matrices=[];let nis;
      _matInv=function(matrix,size){if(size===n)matrices.push(Array.from(matrix));return original.apply(this,arguments);};
      try{nis=fn(tr,meas);}finally{_matInv=original;}
      requireFixture(matrices.length===1,'EXACTLY_ONE_NATIVE_INVERSE_'+n+':'+matrices.length);return {nis,dimension:n,matrix:matrices[0],actualNativeNisEvaluations:1,wrapperRestored:_matInv===original};
    };
    // Independent algebra check of the captured native matrix only. This does
    // not compute a second innovation, NIS, gate or association likelihood.
    const logDet=({matrix,dimension:n})=>{const a=Array.from({length:n},(_,i)=>matrix.slice(i*n,(i+1)*n));let sign=1,log=0;for(let i=0;i<n;i++){let p=i;for(let j=i+1;j<n;j++)if(Math.abs(a[j][i])>Math.abs(a[p][i]))p=j;if(p!==i){[a[p],a[i]]=[a[i],a[p]];sign=-sign;}const pivot=a[i][i];requireFixture(Number.isFinite(pivot)&&pivot!==0,'NON_SINGULAR_CAPTURED_NATIVE_S');sign*=Math.sign(pivot);log+=Math.log(Math.abs(pivot));for(let j=i+1;j<n;j++){const q=a[j][i]/pivot;for(let k=i+1;k<n;k++)a[j][k]-=q*a[i][k];}}requireFixture(sign>0,'POSITIVE_CAPTURED_NATIVE_DETERMINANT');return log;};
    const run=(name,fn)=>{try{records[name]=fn();}catch(error){checks[name+'.completed']=false;errors.push({fixture:name,error:String(error.stack??error),classification:String(error).includes('FIXTURE_PRECONDITION:')?'FIXTURE_PRECONDITION_FAILURE':'NATIVE_RUNTIME_FAILURE'});}};
    run('airFourRowsActualNativeMatrix',()=>{
      const tr=seed(),receiver={xM:100,yM:-50,zM:22,vxMps:21,vyMps:3,vzMps:.5},meas=S.air({xM:12000,yM:7000,zM:1500,vxMps:-240,vyMps:30,vzMps:-10,receiver});meas.rangeM+=3;meas.azRad+=.0001;meas.elRad-=.0002;meas.radialMps+=.5;S.assertNoTruthFields(meas);
      const before=snapshot(tr),input=JSON.stringify(meas);methods.add('trackRadarAssociationNisV31');const native=captured(trackRadarAssociationNisV31,tr,meas,4),expected=logDet(native),actual=evidence(tr,meas,'AIR',S.nowS(),S.nowS());
      check('air.actualFourDimensionalEvidence',actual.valid===true&&actual.dimensions===4);check('air.logDetMatchesCapturedNativeS',actual.valid===true&&Math.abs(actual.logDetS-expected)<1e-10);check('air.priorAndMeasurementNotMutated',snapshot(tr)===before&&JSON.stringify(meas)===input);check('air.wrapperRestored',native.wrapperRestored);
      return {native,expectedLogDetS:expected,actual,allReceiverOriginsAndVelocityProvided:true,actualPredictionJacobianAndNoiseFloors:true,physicalTruthUsed:false};
    });
    run('surfacePositionActualNativeMatrix',()=>{
      const tr=seed(),meas=S.surface({xM:12000,yM:7000,vxMps:-240,vyMps:30});const before=snapshot(tr),input=JSON.stringify(meas);methods.add('trackSurfacePositionAssociationNisWip13B9');const native=captured(trackSurfacePositionAssociationNisWip13B9,tr,meas,2),expected=logDet(native),actual=evidence(tr,meas,'SURFACE_POSITION',S.nowS(),S.nowS());
      check('surface.actualPositionOnlyTwoRowsDespiteInputDoppler',Number.isFinite(meas.radialMps)&&actual.valid===true&&actual.dimensions===2);check('surface.logDetMatchesCapturedNativeS',actual.valid===true&&Math.abs(actual.logDetS-expected)<1e-10);check('surface.priorAndMeasurementNotMutated',snapshot(tr)===before&&JSON.stringify(meas)===input);
      return {native,expectedLogDetS:expected,actual,surfaceZPriorNotObservation:true};
    });
    run('cartesianAlignedReportedCovariance',()=>{
      const tr=seed(),report=S.report({xM:12003,yM:6998,zM:1501,covarianceM2:[900,100,0,100,1600,10,0,10,400]});report.domainEvidence={surface:.05,air:.9,missile:.05,background:0};S.assertNoTruthFields(report);methods.add('offboardPlotC');const meas=offboardPlotC(report,S.nowS()),before=snapshot(tr),input=JSON.stringify({report,meas});methods.add('trackCartesianAssociationNisV33');const native=captured(trackCartesianAssociationNisV33,tr,meas,3),expected=logDet(native),actual=evidence(tr,meas,'CARTESIAN',S.nowS(),report.measuredAtS);
      check('cartesian.alignedReportedThreeRows',!meas._reportedSurface&&actual.valid===true&&actual.dimensions===3);check('cartesian.logDetMatchesCapturedNativeS',actual.valid===true&&Math.abs(actual.logDetS-expected)<1e-10);check('cartesian.reportedRAndPriorUnchanged',snapshot(tr)===before&&JSON.stringify({report,meas})===input);
      return {native,expectedLogDetS:expected,actual,claim:'ReportedCartesian3_notPhysical3DRfObservation'};
    });
    run('surfaceFullDopplerCallbackCannotUsePositionCertificate',()=>{
      const files=[];
      for(const[xM,Pxy]of [[4000,225],[5000,1e6]]){
        const initial=S.surface({xM}),tr=updateSensorTrackMeasurement(null,initial,{source:initial.source,taskType:'SURFACE_PRECISION'});updateSensorTrackMeasurement(tr.trackId,initial,{source:initial.source,taskType:'SURFACE_PRECISION'});
        requireFixture(tr.confirmed&&tr.domain==='SURFACE','FIRM_NATIVE_SURFACE_CALLBACK');tr._kfX.set([xM,0,8,0,0,0]);tr._kfP.fill(0);for(const[index,value]of [[0,Pxy],[7,Pxy],[14,16],[21,100],[28,100],[35,16]])tr._kfP[index]=value;trackSyncLegacyFromEkf(tr);files.push(tr);
      }
      // Isolate this actual callback query from the preceding AIR/CARTESIAN
      // fixtures without changing the files themselves or inventing a filter.
      const saved=[...tracks];tracks.clear();for(const tr of files)tracks.set(tr.trackId,tr);
      const plot=S.surface({xM:4001}),before=S.snapshotStore(tracks),nis=files.map(tr=>trackSurfaceRadarAssociationNisV35(tr,plot));methods.add('trackSurfaceRadarAssociationNisV35');
      requireFixture(nis.every(Number.isFinite)&&nis[0]<nis[1]&&nis[1]-nis[0]<1&&Number.isFinite(plot.radialMps),'FULL_SURFACE_NATIVE_THREE_ROW_NEAR_EQUAL');
      let assignment;
      try{methods.add('surfaceAssignmentsPreferEstablishedWip13B14');assignment=surfaceAssignmentsPreferEstablishedWip13B14([plot],trackSurfaceRadarAssociationNisV35,64);check('surfaceCallback.threeRowNisNotCertifiedWithTwoRowEvidence',assignment.size===0);check('surfaceCallback.queryDoesNotMutateFiles',JSON.stringify(before)===JSON.stringify(S.snapshotStore(tracks)));}
      finally{tracks.clear();for(const[id,tr]of saved)tracks.set(id,tr);}
      return {actualNativeFullDopplerCallback:true,inputHasMeasuredDoppler:true,nativeNis:nis,assignment:[...assignment],nativeAppliedDimension:3,positionOnlyCertificateMustBeUnavailable:true};
    });
    run('delayedEpochAndMissingFieldsInvalid',()=>{
      const tr=seed(),report=S.report({measuredAtS:S.nowS()-1,xM:12000,yM:7000,zM:1500});report.domainEvidence={surface:.05,air:.9,missile:.05,background:0};const before=snapshot(tr),input=JSON.stringify(report),meas=offboardPlotC(report,S.nowS()),delayed=evidence(tr,meas,'CARTESIAN',S.nowS(),report.measuredAtS),air=S.air({xM:12000,yM:7000,zM:1500});delete air.sensorVzMps;const missing=evidence(tr,air,'AIR',S.nowS(),S.nowS()),surface=offboardPlotC(S.report(),S.nowS()),priorOnly=evidence(tr,surface,'CARTESIAN',S.nowS(),S.nowS());
      check('epoch.delayedReportNotAlignedByReceiptTime',delayed.valid===false&&delayed.reason==='EPOCH_NOT_ALIGNED');check('epoch.existingAgeSquaredInflationPreserved',meas.cartesianCovarianceM2[0]===report.covarianceM2[0]+180*180&&meas.cartesianCovarianceM2[8]===report.covarianceM2[8]+120*120);check('epoch.missingReceiverVelocityDoesNotBecomeZero',missing.valid===false);check('epoch.reportedSurfacePriorNotPhysicalElevation',priorOnly.valid===false);check('epoch.noPriorOrReportMutation',snapshot(tr)===before&&JSON.stringify(report)===input);
      return {delayed,missing,priorOnly,report,derivedReportedCovariance:meas.cartesianCovarianceM2,receiptTimeNotMeasurementTime:true};
    });
    const beforeQuery=S.afterActionPassiveState();__TRACK_B__.snapshot();__TRACK_B__.snapshot();const afterQuery=S.afterActionPassiveState();check('queries.privateAndGlobalRngAndPhysicalStateUnchanged',beforeQuery===afterQuery);
    return {schema:'AEGIS_TRACK_B_STABLE_NATIVE_METADATA_1',available,classification:'CAPTURED_ACTUAL_NATIVE_INNOVATION_MATRIX_NOT_SECOND_MODEL',actualMethods:[...methods].sort(),checks,records,errors,pass:!errors.length&&Object.values(checks).every(Boolean),originalBFilesChanged:false,naturalRfOrWeaponEvidence:false};
  }
});
