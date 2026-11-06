// SEEKER_UNIFY_U3 Commit D: rank only already-gated, anonymous passive-RF
// measurements.  The innovation covariance is diagonal in this producer, so
// det(S)=Sa*Se and the approved score is d^2 + ln(det(S)).
const SEEKER_U3_PASSIVE_RF_MODE_D='__MODE__';
const SEEKER_U3_PASSIVE_RF_AUDIT_D={comparisons:0,differences:0,tiesResolved:0,lastDifference:null};
function seekerU3PassiveRfObservableSignatureD(candidate){
  if(!candidate)return null;
  return Object.freeze({family:candidate.family,emitterClass:candidate.emitterClass,band:candidate.band,
    frequencyMHz:candidate.frequencyMHz,worldAz:candidate.worldAz,worldEl:candidate.worldEl,
    snr:candidate.snr,bearingSigmaRad:candidate.bearingSigmaRad,elevationSigmaRad:candidate.elevationSigmaRad,
    d2:candidate.d2,innovationDet:candidate.innovationDet,selectionScore:candidate.selectionScore});
}
function seekerU3PassiveRfLegacyCompareD(a,b){return a.d2-b.d2;}
function seekerU3PassiveRfCandidateCompareD(a,b){
  const numeric=['selectionScore','d2','innovationDet','frequencyMHz','worldAz','worldEl','bearingSigmaRad','elevationSigmaRad','snr','receivedW'];
  for(const key of numeric){const delta=Number(a[key])-Number(b[key]);if(delta!==0)return delta;}
  for(const key of ['family','emitterClass','band','frequencyProvenance']){const delta=String(a[key]??'').localeCompare(String(b[key]??''),'en');if(delta!==0)return delta;}
  return 0; // Observationally identical candidates produce the same tactical measurement.
}
function seekerU3PassiveRfSelectionD(candidates){
  const legacy=[...candidates].sort(seekerU3PassiveRfLegacyCompareD)[0]??null,
    ranked=[...candidates].sort(seekerU3PassiveRfCandidateCompareD)[0]??null;
  if(SEEKER_U3_PASSIVE_RF_MODE_D==='SHADOW'&&legacy&&ranked){
    SEEKER_U3_PASSIVE_RF_AUDIT_D.comparisons++;
    const legacySignature=seekerU3PassiveRfObservableSignatureD(legacy),rankedSignature=seekerU3PassiveRfObservableSignatureD(ranked);
    if(JSON.stringify(legacySignature)!==JSON.stringify(rankedSignature)){
      SEEKER_U3_PASSIVE_RF_AUDIT_D.differences++;
      SEEKER_U3_PASSIVE_RF_AUDIT_D.lastDifference=Object.freeze({legacy:legacySignature,ranked:rankedSignature});
    }
    const ordered=[...candidates].sort(seekerU3PassiveRfCandidateCompareD);
    if(ordered.length>1&&ordered[0].selectionScore===ordered[1].selectionScore)SEEKER_U3_PASSIVE_RF_AUDIT_D.tiesResolved++;
  }
  return Object.freeze({legacy,ranked,selected:SEEKER_U3_PASSIVE_RF_MODE_D==='ACTIVE'?ranked:legacy});
}
function seekerU3PassiveRfAuditSnapshotD(){return Object.freeze({mode:SEEKER_U3_PASSIVE_RF_MODE_D,
  comparisons:SEEKER_U3_PASSIVE_RF_AUDIT_D.comparisons,differences:SEEKER_U3_PASSIVE_RF_AUDIT_D.differences,
  tiesResolved:SEEKER_U3_PASSIVE_RF_AUDIT_D.tiesResolved,lastDifference:SEEKER_U3_PASSIVE_RF_AUDIT_D.lastDifference,
  score:'d2 + ln(det(S))',gateOwner:'asmPassiveRfMeasurementB2',truthFieldsUsed:false,rngConsumed:false});}

