function harpoonUpdateUIA(){
  const host=document.getElementById('harpoonControlsA');if(!host)return;const r=harpoonRuntimeA();host.hidden=!r.tubes.length;if(!r.tubes.length)return;
  const gate=harpoonAutoTubeGateD(),label=document.getElementById('harpoonTubeA');
  if(gate.tubeId)r.selectedTubeId=gate.tubeId;
  label.textContent='AUTO · '+(gate.tubeId?gate.tubeId.replace('MK141-',''):gate.reason==='TUBE_EMPTY'?'소진':'대기');
  label.title='장전·손상·안전 조건과 입력 경로/관측 표적 방향으로 자동 선택'+(gate.reason?' · '+gate.reason:'');
  const button=document.getElementById('harpoonFireA');button.disabled=!gate.ok;
  button.textContent='HARPOON '+r.tubes.filter(t=>t.loaded).length+'/8'+(r.pending?' · OPENING':' · FIRE');
  const route=document.getElementById('harpoonRouteE'),note=document.getElementById('harpoonRouteNoteE'),draft=r.routeDraft;
  route.disabled=!!r.pending||!r.tubes.some(t=>t.loaded);route.textContent=draft.editing?'웨이포인트 해제':'웨이포인트 지정';route.setAttribute('aria-pressed',String(draft.editing));
  note.textContent=draft.pointsM.length?'H-WP '+draft.pointsM.length+'/8 · '+(gate.rangeKm?gate.rangeKm.toFixed(1)+' km 계획':'경로 검사: '+gate.reason)+' · 마지막 점 통과 후 전방 탐색':
    (draft.editing?'CIC 탭으로 경유점 추가 · 간격 2 km 이상 · 마지막 점 = 탐색 시작':'경유점 없이 관측 표적 발사 · 경유점 지정 시 좌표 탐색 발사');
  const picture=harpoonOperatorPictureC(),status=document.getElementById('harpoonStatusA');
  status.textContent=picture.launches.length?picture.launches.slice(-4).map(q=>'H'+q.id+' · NO DL · '+(q.trackId==null?'미관측':q.source+' T'+q.trackId+' ('+q.measurementAgeS.toFixed(1)+'s)')).join(' / '):(gate.ok?'RGM-84D · INS → ARH · NO DL · READY':gate.reason);
  status.title='RGM-84D Block 1C · 공개 제원 / SIM-TUNED 비행·경로·탐색기 · Mk 141 전용';
}
function harpoonBindUIA(){
  if(!document.getElementById('harpoonTubeA'))return;
  bindPress(document.getElementById('harpoonFireA'),()=>{harpoonRequestFireA();harpoonUpdateUIA();});
  document.getElementById('harpoonRouteE').addEventListener('click',e=>{e.preventDefault();harpoonRouteToggleE();});harpoonUpdateUIA();
}
