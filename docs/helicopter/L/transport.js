// ISAR results are crew-held information, unlike disposable radar plots.
function isarTransportStepF2(h){const s=isarExistingF2(h);if(!s?.buffer.length)return;const r=heloSensorOwnerE(h);if(!r||!heloHawklinkExistingE(h)?.connected)return;const result=ingestOffboardReportC(r,s.buffer[0]);if(result.ok){s.buffer.shift();s.stats.sent++;}else if(result.reason!=='LINK_UNAVAILABLE'&&result.reason!=='ISAR_QUEUE_FULL'){s.buffer.shift();s.stats.rejected++;}}
function isarReceiverStateF2(r){const o=observerC(r);return o.isarF2??(o.isarF2={queue:[],history:[],lastSequence:{},accepted:0,rejected:0,associated:0});}
function isarFiniteRecordF2(p,keys){return !!p&&typeof p==='object'&&!Array.isArray(p)&&Object.keys(p).sort().join(',')===keys.split(',').sort().join(',');}
function isarReportValidF2(p,now){
 if(!isarFiniteRecordF2(p,'schema,sourceId,sequence,measuredAtS,positionM,covarianceM2,result')||p.schema!=='AEGIS_OFFBOARD_ISAR_C_1'||!/^H[12]$/.test(p.sourceId)||!Number.isInteger(p.sequence)||p.sequence<1||!Number.isFinite(p.measuredAtS)||p.measuredAtS>now+1e-9||now-p.measuredAtS>ISAR_F2.resultMaxAgeS)return false;
 if(!isarFiniteRecordF2(p.positionM,'x,y,z')||!Object.values(p.positionM).every(v=>Number.isFinite(v)&&Math.abs(v)<2e7))return false;const C=p.covarianceM2;if(!Array.isArray(C)||C.length!==9||!C.every(Number.isFinite)||[0,4,8].some(i=>C[i]<1||C[i]>1e10)||C[1]!==C[3]||C[2]!==C[6]||C[5]!==C[7])return false;
 if(C[0]*C[4]-C[1]*C[3]<=0||C[0]*(C[4]*C[8]-C[5]*C[7])-C[1]*(C[3]*C[8]-C[5]*C[6])+C[2]*(C[3]*C[7]-C[4]*C[6])<=0)return false;
 const f=p.result;if(!isarFiniteRecordF2(f,'candidates,quality,lengthM,lengthSigmaM,heightsM,heightSigmaM,mastPosition01,mastSigma01,crossResolutionM,rangeResolutionM,deltaThetaRad')||!['quality','lengthM','lengthSigmaM','heightSigmaM','mastPosition01','mastSigma01','crossResolutionM','rangeResolutionM','deltaThetaRad'].every(k=>Number.isFinite(f[k])&&f[k]>=0)||f.quality>1||f.mastPosition01>1||f.lengthM<=0||f.lengthSigmaM<=0||f.heightSigmaM<=0||f.mastSigma01<=0||f.crossResolutionM<=0||f.rangeResolutionM<=0)return false;
 if(!Array.isArray(f.heightsM)||f.heightsM.length!==ISAR_F2.featureBins||!f.heightsM.every(v=>Number.isFinite(v)&&v>=0&&v<1000)||!Array.isArray(f.candidates)||f.candidates.length!==ISAR_LIBRARY_F2.length)return false;
 const ids=new Set();let prev=Infinity;for(const c of f.candidates){const lib=ISAR_LIBRARY_F2.find(l=>l.classId===c.classId);if(!isarFiniteRecordF2(c,'classId,label,confidence')||!lib||ids.has(c.classId)||c.label!==lib.label||!Number.isFinite(c.confidence)||c.confidence<0||c.confidence>1||c.confidence>prev)return false;ids.add(c.classId);prev=c.confidence;}return f.candidates.reduce((a,b)=>a+b.confidence,0)<=1+1e-9;
}
function ingestOffboardIsarF2(r,p){const now=simStepCounter*SIM_FIXED_DT;if(!isarReportValidF2(p,now))return {ok:false,reason:'ISAR_SCHEMA_OR_TRUTH_FIELDS'};const link=observerC(r).offboard.sources.get(p.sourceId);if(!link?.connected)return {ok:false,reason:'LINK_UNAVAILABLE'};const s=isarReceiverStateF2(r);if(p.sequence<=(s.lastSequence[p.sourceId]??0))return {ok:false,reason:'ISAR_REPLAY'};if(s.queue.length>=ISAR_F2.receiverCapacity)return {ok:false,reason:'ISAR_QUEUE_FULL'};
 s.queue.push({...JSON.parse(JSON.stringify(p)),availableAtS:now+link.latencyS});s.lastSequence[p.sourceId]=p.sequence;s.accepted++;return {ok:true};}
function drainIsarOffboardF2(r){const s=r.combatSystem.observerC?.isarF2;if(!s)return;const now=simStepCounter*SIM_FIXED_DT,pending=[];
 for(const report of s.queue){if(now-report.measuredAtS>ISAR_F2.resultMaxAgeS){s.rejected++;continue;}if(report.availableAtS>now||!observerC(r).offboard.sources.get(report.sourceId)?.connected){pending.push(report);continue;}s.history.push(report);if(s.history.length>ISAR_F2.receiverCapacity)s.history.shift();}s.queue=pending;
 // Crew intelligence survives a coast-file deletion. Reassociation is geometry
 // only and never transfers operator identity, authority, or a previous track ID.
 s.history=s.history.filter(p=>now-p.measuredAtS<=ISAR_F2.resultMaxAgeS);
 for(const report of s.history){const age=now-report.measuredAtS,C=report.covarianceM2;let pick=null;for(const tr of observerC(r).tracks.values()){
  if(!tr.sensorDetected||!(tr.domain==='SURFACE'||tr.classification==='SURFACE'))continue;
  const sigma=trackCovarianceMetrics(tr).posSigmaM??100,variance=Math.max(C[0],C[4])+sigma*sigma+(age*ISAR_F2.positionSpeedPriorMps)**2,gate=Math.min(ISAR_F2.positionGateMaxM,ISAR_F2.positionGateSigma*Math.sqrt(variance)),d=Math.hypot(worldToMeters(tr.x)-report.positionM.x,worldToMeters(tr.y)-report.positionM.y);
  if(d<=gate&&(!pick||d<pick.distance))pick={tr,distance:d};
 }
 if(!pick)continue;const tr=pick.tr;if(!tr.isarEvidence||tr.isarEvidence.measuredAtS<report.measuredAtS){tr.isarEvidence={...JSON.parse(JSON.stringify(report.result)),measuredAtS:report.measuredAtS,sourceId:report.sourceId};s.associated++;debugLog(`ISAR ${r.entityId} TRK ${tr.trackId} ${tr.isarEvidence.candidates[0].label} · 식별 자동 변경 없음`);}
 // No measurement update, identity/authority change, or coast rejuvenation here.
 }
}
function isarIdentificationDecisionF2(tr){const e=tr?.isarEvidence,now=simStepCounter*SIM_FIXED_DT;if(e&&now-e.measuredAtS<=ISAR_F2.resultMaxAgeS){tr.identificationEvidence='ISAR';tr.identificationIsarF2={classId:e.candidates[0].classId,label:e.candidates[0].label,confidence:e.candidates[0].confidence,measuredAtS:e.measuredAtS,sourceId:e.sourceId,ageAtDecisionS:now-e.measuredAtS,decisionAtS:now};}else{tr.identificationEvidence=trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR';delete tr.identificationIsarF2;}}
function isarTrackLabelF2(tr){const e=tr?.isarEvidence;if(!e)return '';const c=e.candidates[0];return `ISAR ${c.label} ${c.confidence.toFixed(2)} · ${e.lengthM.toFixed(0)}±${e.lengthSigmaM.toFixed(0)}m · ${(simStepCounter*SIM_FIXED_DT-e.measuredAtS).toFixed(0)}s` ;}
function isarResetF2(owner){if(owner?.combatSystem.observerC)delete owner.combatSystem.observerC.isarF2;for(const tr of owner?.combatSystem.trackManager?.tracks?.values()??[])if(/^H[12]$/.test(tr.isarEvidence?.sourceId??''))delete tr.isarEvidence;}
