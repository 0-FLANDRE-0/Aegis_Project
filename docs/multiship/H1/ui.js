// Presentation only. Commands apply to the FLEET-selected friendly owner.
function mountTacticalUiH1(){
  const parent=document.getElementById('networkControlsG');if(!parent||document.getElementById('tacticalToggleH1'))return;
  const section=document.createElement('section');section.className='control-deck-section';section.innerHTML=`<div class="control-deck-heading">선택 함정 전술 AI</div><div class="control-deck-grid"><button id="tacticalToggleH1" class="wep-btn misc">전술 AI OFF</button><button id="tacticalResumeH1" class="wep-btn misc">AI 운용 재개</button></div><div id="tacticalStatusH1" class="control-deck-note" role="status"></div><div id="tacticalReasonH1" class="control-deck-note"></div><div class="control-deck-note">AUTO에서 방어 태세·우선순위·살보 조절<br>수동 레이더·전자전 및 공동 EMCON 우선</div>`;
  parent.append(section);bindPress(document.getElementById('tacticalToggleH1'),()=>{const r=fleetOwnerG();tacticalCommandH1(r.entityId,{enabled:!prepareTacticalH1(r).settings.enabled});});
  bindPress(document.getElementById('tacticalResumeH1'),()=>tacticalCommandH1(fleetOwnerG().entityId,{resume:true}));
}
function tacticalUpdateUiH1(){
  const b=document.getElementById('tacticalToggleH1');if(!b)return;const r=fleetOwnerG(),s=prepareTacticalH1(r),q=s.summary,labels={WATCH:'감시',CONSERVE:'탄약 절약',DEFEND:'방어',SATURATED:'포화 대응',DEGRADED:'손상 대응'};
  b.textContent='전술 AI '+(s.settings.enabled?'ON':'OFF');b.setAttribute('aria-pressed',String(s.settings.enabled));
  const resume=document.getElementById('tacticalResumeH1');resume.disabled=!s.settings.manualRadar&&!s.settings.manualEw&&s.settings.enabled;
  document.getElementById('tacticalStatusH1').textContent=!s.settings.enabled?'기존 AUTO 운용':!tacticalActiveH1(r)?'대기 · AUTO에서 동작':labels[s.posture]+(s.settings.manualRadar?' · 레이더 수동':'')+(s.settings.manualEw?' · 전자전 수동':'')+(tacticalGroupAuthorityH1(r)?' · 공동 EMCON 우선':'');
  document.getElementById('tacticalReasonH1').textContent=q?'현지 위협 '+q.localThreats+' · 미대응 '+q.unserved+' · 방어 가용탄 '+q.availableRounds+(s.priorities[0]?' · 우선 T'+s.priorities[0].trackId:''):'상황 판단 대기';
}
