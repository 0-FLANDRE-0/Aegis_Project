// TEST ONLY. Actual native surface NIS -> core -> NPC caller -> EKF update.
// No RF return is generated. The grid and x/P/age are explicitly declared
// receiver-owned estimator initial conditions, not physical target truth.
// Requires the immutable B native_support.js and original A passive helper.
window.__TRACK_B_STABILIZATION_SATURATION__=Object.freeze({
  state(){return TRACK_B_NATIVE_SUPPORT.afterActionPassiveState();},
  run(selected=null){
    const S=TRACK_B_NATIVE_SUPPORT,checks={},records={},errors=[],afterActionStateByFixture={},methods=new Set();
    const mode=window.__TRACK_B__?.stabilizationMode??'ORIGINAL_B_ACTIVE',active=mode==='ACTIVE';
    const check=(key,value)=>{checks[key]=!!value;},requireFixture=(ok,why)=>{if(!ok)throw Error('FIXTURE_PRECONDITION:'+why);};
    const fileSnapshot=tr=>({...S.snapshotFile(tr),lastMeasurementStep:tr._lastMeasurementStep??null,lastIndependentHitS:tr.lastIndependentHitS??null,predictAgeS:tr._kfPredictAgeS??null});
    const ownerSnapshot=owner=>{const o=observerC(owner);return {tracks:[...o.tracks.values()].map(fileSnapshot),rng:S.copy(o.rng),serial:o.serial,ticks:o.tickCount,lastTick:o.lastTick,stats:{...o.stats},rotors:{...o.rotors}};};
    const graphComponents=(matrix,gate)=>{
      const byRow=new Map(),byCol=new Map();let edgeCount=0;
      for(let i=0;i<matrix.length;i++)for(let j=0;j<matrix[i].length;j++)if(Number.isFinite(matrix[i][j])&&matrix[i][j]<=gate){if(!byRow.has(i))byRow.set(i,[]);if(!byCol.has(j))byCol.set(j,[]);byRow.get(i).push(j);byCol.get(j).push(i);edgeCount++;}
      const visited=new Set(),components=[];
      for(const start of byRow.keys()){if(visited.has(start))continue;const rr=new Set(),cc=new Set(),queue=[start];while(queue.length){const i=queue.pop();if(rr.has(i))continue;rr.add(i);visited.add(i);for(const j of byRow.get(i)??[]){if(cc.has(j))continue;cc.add(j);for(const k of byCol.get(j)??[])if(!rr.has(k))queue.push(k);}}components.push({plotIndices:[...rr].sort((a,b)=>a-b),fileIndices:[...cc].sort((a,b)=>a-b)});}
      return {edgeCount,components};
    };
    const reset=()=>{__GB_TEST__.reset(419025);S.resetPrivateOwnerEvidence();BATTLESPACE_DIAG_BYPASS=true;emconActive=true;tracks.clear();S.advanceTicks(120);};
    const fixture=(name,count,tied)=>{
      reset();const owner=S.privateOwner('SATURATION_'+name),other=S.privateOwner('SATURATION_UNTOUCHED_'+name),o=observerC(owner),now=S.nowS(),ageS=.5;
      const initial=Array.from({length:count},(_,i)=>S.surface({xM:4000+(tied?0:i*80)}));initial.forEach(S.assertNoTruthFields);
      const originalSelect=trackBSelectB,originalUpdate=trackEkfUpdateSurfaceRadar2D,coreCalls=[],updates=[],foreignUpdates=[],wrapperState={selectRestored:false,updateRestored:false};let phase='SEED',canaryReads=0;
      trackBSelectB=function(input){const result=originalSelect.apply(this,arguments);if(input.route==='NPC_OBSERVER'&&input.observerShip===owner.entityId)coreCalls.push({phase,gate:input.gate,plotCount:input.plotCount,pairs:input.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis,sanity:p.sanity?{ok:p.sanity.ok,distanceM:p.sanity.distanceM}:null})),selected:result.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),heldPlots:[...result.heldPlots],heldTracks:[...result.heldTracks],components:S.copy(result.components),stabilizationActive:result.stabilizationActive??null});return result;};
      trackEkfUpdateSurfaceRadar2D=function(tr,plot,options){const owned=o.tracks.get(tr.trackId)===tr,before=owned?fileSnapshot(tr):null;const result=originalUpdate.apply(this,arguments);if(phase==='MEASUREMENT'){const record={trackId:tr.trackId,result,before,after:owned?fileSnapshot(tr):null};(owned?updates:foreignUpdates).push(record);}return result;};
      try{
        methods.add('observerAcceptPlotsC');observerAcceptPlotsC(owner,initial);observerAcceptPlotsC(other,[S.surface({xM:15000})]);
        requireFixture(o.tracks.size===count,'NATIVE_ESTIMATOR_SEED_COUNT_'+count);
        const files=[...o.tracks.values()].sort((a,b)=>a._kfX[0]-b._kfX[0]||a.trackId-b.trackId),ids=files.map(tr=>tr.trackId),seedCall=coreCalls.find(c=>c.phase==='SEED');
        requireFixture(!!seedCall&&Number.isFinite(seedCall.gate)&&seedCall.gate>0,'ACTUAL_NATIVE_CALLER_GATE_CAPTURED');
        for(let i=0;i<count;i++){
          const tr=files[i],xM=4000+(tied?0:i*80);tr._kfX.set([xM,0,8,0,0,0]);tr._kfP.fill(0);
          for(const[index,value]of [[0,225],[7,225],[14,16],[21,100],[28,100],[35,16]])tr._kfP[index]=value;
          // An owned prior at the current state epoch, last observed .5s ago.
          // Explicit fixture status; no claim that this age came from RF.
          tr.sensorAge=ageS;tr.lastMeasurementS=now-ageS;tr._lastMeasurementStep=Math.round((now-ageS)/SIM_FIXED_DT);tr.lastIndependentHitS=now-ageS;tr._kfPredictAgeS=ageS;trackSyncLegacyFromEkf(tr);
        }
        const plots=Array.from({length:count},(_,i)=>S.surface({xM:4001+(tied?0:i*80)}));
        for(const plot of plots){S.assertNoTruthFields(plot);for(const key of ['truthRef','objectId','rfId','_truthObject','faction','owner'])Object.defineProperty(plot,key,{enumerable:false,get(){canaryReads++;throw Error('SYNTHETIC_TRUTH_CANARY_READ:'+key);}});}
        const inputBefore=JSON.stringify(plots),before=ownerSnapshot(owner),otherBefore=ownerSnapshot(other),globalBefore=S.snapshotStore(tracks),statsBefore={...o.stats};
        methods.add('trackSurfacePositionAssociationNisWip13B9');const matrix=plots.map(plot=>files.map(tr=>trackSurfacePositionAssociationNisWip13B9(tr,plot))),graph=graphComponents(matrix,seedCall.gate),originalBound=__TRACK_B__.policy.maxComponentSize;
        const connected=graph.components.length===1&&graph.components[0].plotIndices.length===count&&graph.components[0].fileIndices.length===count;
        const diagonal=tied?matrix.every(row=>row.every(value=>Number.isFinite(value)&&Math.abs(value-matrix[0][0])<=1e-9)):matrix.every((row,i)=>Number.isFinite(row[i])&&row[i]<=seedCall.gate&&row.every((value,j)=>i===j||!Number.isFinite(value)||row[i]<value));
        const adjacent=tied||Array.from({length:count-1},(_,i)=>matrix[i][i+1]<=seedCall.gate&&matrix[i+1][i]<=seedCall.gate).every(Boolean);
        requireFixture(connected&&count>originalBound&&diagonal&&adjacent,'ACTUAL_NATIVE_ELIGIBLE_CHAIN_OR_TIE:'+JSON.stringify({count,originalBound,graph,diagonal,adjacent}));
        requireFixture(JSON.stringify(before)===JSON.stringify(ownerSnapshot(owner)),'NATIVE_NIS_QUERY_PRESERVES_PRIOR');
        const serialBefore=__TRACK_B__.snapshot().stats.recorded;phase='MEASUREMENT';observerAcceptPlotsC(owner,plots);phase='DONE';
        const calls=coreCalls.filter(c=>c.phase==='MEASUREMENT'),after=ownerSnapshot(owner),call=calls[0],expectedUpdates=!tied&&active?count:0,selectedPairs=call?.selected??[],held=call?.heldPlots??[],used=new Set(selectedPairs.map(p=>p.i)),counts=new Map();for(const u of updates)counts.set(u.trackId,(counts.get(u.trackId)??0)+1);
        check(name+'.oneActualNativeCoreBatch',calls.length===1&&call.plotCount===count);
        check(name+'.actualNativeGateAndEdgesPreserved',!!call&&call.gate===seedCall.gate&&call.pairs.length===graph.edgeCount&&call.pairs.every(p=>Math.abs(p.nis-matrix[p.i][ids.indexOf(p.id)])<=1e-9));
        check(name+'.expectedSelectedCount',selectedPairs.length===expectedUpdates);
        check(name+'.oneToOneNoReuse',new Set(selectedPairs.map(p=>p.id)).size===selectedPairs.length&&used.size===selectedPairs.length);
        check(name+'.heldAndUsedDisjoint',selectedPairs.every(p=>!held.includes(p.i)&&!call.heldTracks.includes(p.id)));
        check(name+'.allUnconsumedPlotsExplicitlyHeld',Array.from({length:count},(_,i)=>i).every(i=>used.has(i)||held.includes(i)));
        check(name+'.nativeCorrectionCallsExactlyOnce',updates.length===expectedUpdates&&updates.every(u=>u.result===true)&&[...counts.values()].every(n=>n===1));
        check(name+'.nativeAssociationStatsMatch',o.stats.associated-statsBefore.associated===expectedUpdates);
        check(name+'.noTentativeBirth',o.stats.initiated===statsBefore.initiated&&o.tracks.size===count&&ids.every(id=>o.tracks.has(id)));
        check(name+'.otherOwnerAndGlobalStoreUnchanged',JSON.stringify(otherBefore)===JSON.stringify(ownerSnapshot(other))&&JSON.stringify(globalBefore)===JSON.stringify(S.snapshotStore(tracks))&&o.tracks!==observerC(other).tracks&&o.tracks!==tracks&&foreignUpdates.length===0);
        check(name+'.anonymousInputsAndTruthCanariesUntouched',JSON.stringify(plots)===inputBefore&&canaryReads===0&&!JSON.stringify(call??{}).includes('SYNTHETIC_TRUTH_CANARY'));
        check(name+'.noIdentityOrAuthorityGrant',[...o.tracks.values()].every(tr=>tr.identity==='UNKNOWN'&&tr.engagementAuthority==='WITHHELD'));
        if(expectedUpdates){
          check(name+'.declaredGridDiagonalConsumed',selectedPairs.every(p=>p.id===ids[p.i]));
          check(name+'.eachFilterMovesTowardItsMeasuredPosition',after.tracks.every((tr,i)=>tr.x[0]>before.tracks[i].x[0]&&tr.x[0]<4001+i*80));
          check(name+'.onlyRealUpdateFreshensAgeAndAddsOneHit',after.tracks.every((tr,i)=>tr.age===0&&tr.lastMeasurementS===now&&tr.hits===before.tracks[i].hits+1));
        }else{
          check(name+'.heldFiltersAndAgeNotFreshened',JSON.stringify(before.tracks)===JSON.stringify(after.tracks)&&after.tracks.every(tr=>tr.age===ageS&&tr.lastMeasurementS===now-ageS));
          check(name+'.allPlotsHeldAndZeroCreate',held.length===count&&updates.length===0&&o.stats.initiated===statsBefore.initiated);
        }
        const proposalTrace=__TRACK_B__.snapshot().records.filter(row=>row.serial>serialBefore&&row.route==='NPC_OBSERVER');
        return {classification:'DIRECT_NATIVE_ESTIMATOR_GRID_NOT_RF_GENERATION',mode,count,tied,fixtureOwnedPrior:{positionM:'4000+i*80,0,8 (or all4000 for tie)',horizontalVarianceM2:225,ageS,lastMeasurementS:now-ageS,stateEpochS:now,physicalTruthObjectCreated:false},actualInputNoise:{rangeSigmaM:plots[0].rangeSigmaM,azSigmaDeg:plots[0].azSigmaDeg,radialVelSigmaMps:plots[0].radialVelSigmaMps,changedFromImmutableSurfaceHelper:false},actualNativeGate:seedCall.gate,originalComponentBound:originalBound,nativeNisMatrix:matrix,eligibleGraph:graph,expectedUpdates,before,after,otherBefore,otherAfter:ownerSnapshot(other),statsBefore,statsAfter:{...o.stats},coreCalls:calls,corrections:updates,unusedPlotIndices:Array.from({length:count},(_,i)=>i).filter(i=>!used.has(i)),heldPlotIndices:held,canaryReads,wrapperState,ageNotice:expectedUpdates?'Native accepted corrections reset only their own measurement ages.':'HOLD: stored .5s last-observation ages were preserved; no batch-time elapsed/aging claim.',proposalTrace};
      }finally{trackBSelectB=originalSelect;trackEkfUpdateSurfaceRadar2D=originalUpdate;wrapperState.selectRestored=trackBSelectB===originalSelect;wrapperState.updateRestored=trackEkfUpdateSurfaceRadar2D===originalUpdate;}
    };
    const specs={clear13:[13,false],clear16:[16,false],equal13:[13,true]},names=selected??Object.keys(specs);
    for(const name of names){if(!specs[name])throw Error('UNKNOWN_NATIVE_SATURATION_FIXTURE:'+name);try{records[name]=fixture(name,...specs[name]);}catch(error){checks[name+'.completed']=false;errors.push({fixture:name,error:String(error.stack??error),classification:String(error).includes('FIXTURE_PRECONDITION:')?'FIXTURE_PRECONDITION_FAILURE':'NATIVE_RUNTIME_FAILURE'});}afterActionStateByFixture[name]=S.afterActionPassiveState();}
    return {schema:'AEGIS_TRACK_B_STABLE_NATIVE_SATURATION_1',mode,classification:'ACTUAL_NATIVE_SURFACE_NIS_CORE_CALLER_FILTER_NOT_NATURAL_RF',naturalRfOrCombatEvidence:false,coefficientsOrExpectedValuesChanged:false,actualMethods:[...methods].sort(),checks,records,errors,afterActionStateByFixture,pass:!errors.length&&Object.values(checks).every(Boolean)};
  }
});
