// HELI_F1: observed release provenance and write-only after-action journal.
// No sensor/controller/weapon-authority path may read the journal or its outcomes.
const HARPOON_JOURNAL_SPEC_F1=Object.freeze({maxRecords:Object.freeze({value:64,source:'SIM_TUNED',reference:'User-requested bounded after-action journal'})});
const TRACK_IDENTIFICATION_EVIDENCE_F1=Object.freeze({LOCAL_SENSOR:'LOCAL_SENSOR',OPERATOR_ONLY:'OPERATOR_ONLY',ISAR:'ISAR'});
function trackCompositionF1(tr){
  if(!tr)return null;const q=tr.observationReportsC,remote=!!q&&Object.keys(q.remote??{}).length>0,
    local=q?Number.isFinite(q.localAtS):tr.sensorSource!=='OFFBOARD_C';
  return remote?(local?'MIXED':'OFFBOARD'):'LOCAL';
}
function trackIdentificationEvidenceF1(tr){
  // ISAR is reserved; no observation in F1 can generate that evidence.
  return tr?.identificationEvidence??(trackCompositionF1(tr)==='OFFBOARD'?'OPERATOR_ONLY':'LOCAL_SENSOR');
}
function harpoonJournalWriteStateF1(r){
  if(!r.combatSystem.harpoonJournalF1){const state={records:[]};r.combatSystem.harpoonJournalF1=state;claimShipMutableRootA(r,'harpoonJournalF1',state);}
  return r.combatSystem.harpoonJournalF1;
}
function harpoonJournalReleaseF1(r,m,gate,tr){
  const state=harpoonJournalWriteStateF1(r);
  state.records.push({missileId:m.id,ownerEntityId:r.entityId,launchAtS:simStepCounter*SIM_FIXED_DT,trackId:gate.trackId??null,
    trackComposition:trackCompositionF1(tr),predictionSigmaM:gate.predictionSigmaM??null,
    operatorIdentity:tr?normalizeTrackOperatorIdentityA3(tr._operatorIdentity):'COORDINATE_SEARCH',
    identificationEvidence:tr?trackIdentificationEvidenceF1(tr):null,rangeKm:gate.rangeKm??null,
    launchBasis:'OBSERVED_RELEASE_STATE',updatesAfterRelease:false,termination:null});
  if(state.records.length>HARPOON_JOURNAL_SPEC_F1.maxRecords.value)state.records.shift();
}
function harpoonJournalFinishF1(m,reason,contact=null){
  // AFTER_ACTION_TRUTH boundary: actual collision recipient only. Never intended track truth.
  // This writer has no return data and changes no tactical/sensor/guidance state.
  const owner=ENGAGEMENT_RUNTIME.ships.get(m.ownerEntityId),state=owner?.combatSystem.harpoonJournalF1;
  const row=state?.records.find(q=>q.missileId===m.id);if(!row||row.termination)return;
  const ship=contact?.shipRuntimeD,entity=contact?.entity;
  let category='NONE';
  if(ship)category=ship.faction===owner.faction?'FRIENDLY':(['FRIENDLY','HOSTILE'].includes(ship.faction)?'HOSTILE':'NONE');
  else if(entity){const p=surfaceTargetProfileWip13A(entity.profileId);if(entity.truthKind==='EMPTY_CONTAINER_TEST_HULK'||p?.identity?.basis?.includes('MERCHANT'))category='NEUTRAL_MERCHANT';}
  const result=contact?'HIT':(/SELF_DESTRUCT/.test(reason)?'SELF_DESTRUCT':'LOST');
  row.termination={atS:simStepCounter*SIM_FIXED_DT,result,reason,hitCategory:category,basis:'AFTER_ACTION_TRUTH'};
}
function harpoonJournalResetF1(){for(const r of ENGAGEMENT_RUNTIME.ships.values())if(r.combatSystem.harpoonJournalF1)r.combatSystem.harpoonJournalF1.records.length=0;}
// DIAGNOSTIC_ONLY readers: detached values and copyable DEBUG text, never fire control.
function harpoonJournalSnapshotF1(ownerId=ACTIVE_SHIP_RUNTIME.entityId){
  const r=ENGAGEMENT_RUNTIME.ships.get(ownerId);return JSON.parse(JSON.stringify({schema:'AEGIS_HARPOON_AFTER_ACTION_F1',ownerEntityId:ownerId,
    records:r?.combatSystem.harpoonJournalF1?.records??[]}));
}
function harpoonJournalTextF1(){
  const snap=harpoonJournalSnapshotF1(fleetOwnerG()?.entityId??ACTIVE_SHIP_RUNTIME.entityId),labels={HOSTILE:'적성',FRIENDLY:'아군',NEUTRAL_MERCHANT:'중립 상선',NONE:'없음'};
  return ['교전 로그 · '+snap.ownerEntityId+' · 최대 64건',
    '종료 결과는 AFTER_ACTION_TRUTH 사후 기록. 하푼의 실시간 전술 보고/DL이 아님.',
    ...snap.records.map(q=>`${q.launchAtS.toFixed(2)}s | track ${q.trackId??'좌표'} | ${q.trackComposition??'COORDINATE'} | 2σ ${q.predictionSigmaM==null?'—':q.predictionSigmaM.toFixed(1)+'m'} | ${q.operatorIdentity} | ${q.identificationEvidence??'—'} | ${q.rangeKm==null?'—':q.rangeKm.toFixed(2)+'km'}\n  `+(q.termination?`AFTER_ACTION_TRUTH | ${q.termination.atS.toFixed(2)}s | ${q.termination.result} | ${labels[q.termination.hitCategory]} | ${q.termination.reason}`:'발사 기록 · 종료 미기록'))].join('\n');
}
function harpoonJournalMountF1(panel){
  const page=panel.querySelector('.control-deck-page[data-page="DEBUG"]');if(!page||document.getElementById('harpoonJournalF1'))return;
  const button=document.createElement('button');button.id='harpoonJournalF1';button.className='wep-btn misc';button.textContent='교전 로그';page.querySelector('.control-deck-section')?.append(button);
  const dialog=document.createElement('dialog');dialog.id='harpoonJournalDialogF1';dialog.setAttribute('aria-label','교전 로그 · 사후 분석');
  dialog.style.cssText='width:min(880px,92vw);max-height:86dvh;margin:auto;padding:12px;box-sizing:border-box;overflow:auto;pointer-events:auto;background:#071b27;color:#d9edf1;border:1px solid #568995;border-radius:6px';
  dialog.innerHTML='<p>교전 로그 · AFTER_ACTION_TRUTH 사후 분석</p><textarea id="harpoonJournalTextF1" readonly aria-label="복사 가능한 교전 로그" style="width:100%;height:55dvh;box-sizing:border-box;background:#05131e;color:#d9edf1;font:11px monospace"></textarea><button id="harpoonJournalCopyF1">전체 선택·복사</button> <button id="harpoonJournalCloseF1">닫기</button>';
  panel.append(dialog);bindPress(button,()=>{document.getElementById('harpoonJournalTextF1').value=harpoonJournalTextF1();dialog.showModal();});
  bindPress(document.getElementById('harpoonJournalCopyF1'),()=>{const text=document.getElementById('harpoonJournalTextF1');text.focus();text.select();navigator.clipboard?.writeText(text.value).catch(()=>{});});
  bindPress(document.getElementById('harpoonJournalCloseF1'),()=>dialog.close());
}
window.__HARPOON_JOURNAL_F1__=Object.freeze({snapshot:harpoonJournalSnapshotF1,text:harpoonJournalTextF1});
