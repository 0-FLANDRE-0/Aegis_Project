// Presentation-only FLEET controls.
function mountManeuverUiH2(){
  const parent=document.getElementById('networkControlsG');if(!parent||document.getElementById('maneuverToggleH2'))return;
  const section=document.createElement('section');section.className='control-deck-section';section.innerHTML=`<div class="control-deck-heading">선택 함정 기동 AI</div><div class="control-deck-grid"><button id="maneuverToggleH2" class="wep-btn misc">기동 AI OFF</button><button id="maneuverResumeH2" class="wep-btn misc">기동 AI 재개</button></div><div id="maneuverStatusH2" class="control-deck-note" role="status"></div><div class="control-deck-note">전술 AI ON · AUTO에서 동작<br>수동 항법·항로 지정 우선 · 재개로 AI에 인계</div>`;parent.append(section);
  bindPress(document.getElementById('maneuverToggleH2'),()=>{const r=fleetOwnerG();maneuverCommandH2(r.entityId,{enabled:!prepareManeuverH2(r).settings.enabled});});bindPress(document.getElementById('maneuverResumeH2'),()=>maneuverCommandH2(fleetOwnerG().entityId,{resume:true}));
}
function maneuverUpdateUiH2(){
  const b=document.getElementById('maneuverToggleH2');if(!b)return;const r=fleetOwnerG(),s=prepareManeuverH2(r),labels={KEEP:'침로 유지',PORT30:'좌현 선회',PORT60:'좌현 선회',STARBOARD30:'우현 선회',STARBOARD60:'우현 선회',FAST:'속력 증가',SLOW:'감속',STOP:'정지 명령',RECOVER:'항로 복귀',SAFETY_HOLD:'진로 확보 대기 · 감속'};
  b.textContent='기동 AI '+(s.settings.enabled?'ON':'OFF');b.setAttribute('aria-pressed',String(s.settings.enabled));document.getElementById('maneuverResumeH2').disabled=s.settings.enabled&&!s.settings.manualNav&&tacticalActiveH1(r);
  document.getElementById('maneuverStatusH2').textContent=s.settings.manualNav?'수동 항법 우선':!s.settings.enabled?'운용자 항법':!maneuverActiveH2(r)?'대기 · 전술 AI ON / AUTO 필요':(labels[s.selected]??s.selected)+(s.command?' · '+((s.command.headingRad*180/Math.PI+450)%360).toFixed(0)+'° / '+s.command.speedKt+' kt':'')+(s.summary?' · 현지 위협 '+s.summary.localThreats:'');
}
