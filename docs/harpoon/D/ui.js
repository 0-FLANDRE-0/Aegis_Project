function harpoonUpdateUIA(){
  const host=document.getElementById('harpoonControlsA');if(!host)return;const r=harpoonRuntimeA();host.hidden=!r.tubes.length;if(!r.tubes.length)return;
  const gate=harpoonAutoTubeGateD(),label=document.getElementById('harpoonTubeA');
  if(gate.tubeId)r.selectedTubeId=gate.tubeId; // COMPAT_REQUIRED inventory field, not a manual override.
  label.textContent='AUTO · '+(gate.tubeId?gate.tubeId.replace('MK141-',''):gate.reason==='TUBE_EMPTY'?'소진':'대기');
  label.title='장전·손상·안전 조건과 관측 표적 방향으로 자동 선택'+(gate.reason?' · '+gate.reason:'');
  const button=document.getElementById('harpoonFireA');button.disabled=!gate.ok;
  button.textContent='HARPOON '+r.tubes.filter(t=>t.loaded).length+'/8'+(r.pending?' · OPENING':' · FIRE');
  const picture=harpoonOperatorPictureC(),status=document.getElementById('harpoonStatusA');
  status.textContent=picture.launches.length?picture.launches.slice(-4).map(q=>'H'+q.id+' · NO DL · '+(q.trackId==null?'미관측':q.source+' T'+q.trackId+' ('+q.measurementAgeS.toFixed(1)+'s)')).join(' / '):(gate.ok?'RGM-84D · INS → ARH · NO DL · READY':gate.reason);
  status.title='RGM-84D Block 1C · 공개 제원 / SIM-TUNED 비행·탐색기 · Mk 141 전용';
}
function harpoonBindUIA(){
  if(!document.getElementById('harpoonTubeA'))return;
  bindPress(document.getElementById('harpoonFireA'),()=>{harpoonRequestFireA();harpoonUpdateUIA();});harpoonUpdateUIA();
}
