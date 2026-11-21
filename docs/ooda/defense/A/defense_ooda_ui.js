// DEFENSE_OODA_A Commit D: presentation-only owner-local diagnostics.
// This surface reads snapshots on explicit operator request. It is not a
// simulation input, scheduler, timing source, or authority provider.
function defenseOodaDiagnosticOwnersA(){
  const rows=[ACTIVE_SHIP_RUNTIME,...physicalShipsB()],seen=new Set(),out=[];
  for(const r of rows){if(!r||seen.has(r.entityId))continue;seen.add(r.entityId);out.push(r);}return out;
}
function defenseOodaDiagnosticTextA(){
  const step=simStepCounter,lines=['DEFENSE_OODA_A · READ ONLY'];
  for(const r of defenseOodaDiagnosticOwnersA()){
    const o=defenseOodaSnapshotA(r),d=defenseDecisionDiagnosticsViewA1(r);
    if(!o){lines.push(`${r.entityId} · ${r.profileId} · 미지원`);continue;}
    const next=o.nextReadyStep==null?'—':`${o.nextReadyStep} (${Math.max(0,(o.nextReadyStep-step)/60).toFixed(2)} game s)`,reason=o.lastCommand?.reason??d?.lastCommand?.reason??'—';
    lines.push(`${r.entityId} · ${r.profileId}`);
    lines.push(`  provider ${d?.provider??AEGIS_DEFENSE_DECISION_PROVIDER_A1} · mode ${d?.mode??DEFENSE_OODA_IMPLEMENTATION_MODE_A} · phase ${o.phase}`);
    lines.push(`  capacity ${Number(o.capacity?.value??0).toFixed(3)} · slots ${o.usedSlots}/${o.totalSlots} · queue ${o.queueLength}`);
    lines.push(`  next ready ${next} · reason ${reason}`);
    lines.push(`  fallback ${o.diagnostics?.fallback??0} · rejected ${o.diagnostics?.rejected??0}`);
  }
  return lines.join('\n');
}
function defenseOodaInstallDiagnosticUiA(){
  const page=document.querySelector('.control-deck-page[data-page="DEBUG"]')??document.querySelector('#controlDeckDebugPage');
  if(!page||document.getElementById('defenseOodaStatusA'))return false;
  const section=page.querySelector('.control-deck-section')??page,button=document.createElement('button');
  button.id='defenseOodaStatusA';button.className='wep-btn misc';button.type='button';button.textContent='DEFENSE OODA 상태';button.title='함별 DEFENSE_OODA_A 읽기 전용 상태';
  const dialog=document.createElement('dialog');dialog.id='defenseOodaStatusDialogA';dialog.setAttribute('aria-label','DEFENSE OODA 상태');
  dialog.style.cssText='max-width:min(92vw,760px);max-height:80vh;background:#061015;color:#bce9ff;border:1px solid #39768c;padding:8px;';
  const pre=document.createElement('pre');pre.id='defenseOodaStatusTextA';pre.style.cssText='white-space:pre-wrap;margin:0 0 8px;max-height:65vh;overflow:auto;font:11px/1.35 ui-monospace,monospace;';
  const close=document.createElement('button');close.type='button';close.textContent='닫기';close.className='wep-btn misc';
  button.addEventListener('click',()=>{pre.textContent=defenseOodaDiagnosticTextA();if(typeof dialog.showModal==='function')dialog.showModal();else dialog.setAttribute('open','');});
  close.addEventListener('click',()=>{if(typeof dialog.close==='function')dialog.close();else dialog.removeAttribute('open');});
  for(const name of ['pointerdown','pointermove','pointerup','touchstart','touchmove','touchend','wheel','click'])dialog.addEventListener(name,event=>event.stopPropagation(),{passive:name==='wheel'||name.startsWith('touch')});
  dialog.append(pre,close);section.append(button);document.body.append(dialog);return true;
}
