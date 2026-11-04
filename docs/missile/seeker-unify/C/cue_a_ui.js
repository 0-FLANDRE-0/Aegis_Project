// SEEKER_UNIFY_C Stage 3 presentation-only threat-assumption control.
function cueAUpdateUiC(){
  const out=document.getElementById('cueAThreatStatusC');if(!out)return;const assumed=asmCueEnabledAssumptionsA();out.textContent=`${THREAT_ASSUMPTION_MODE} · 가정 기능 ${assumed.length?assumed.map(q=>q.label+' '+q.feature).join(', '):'없음'}`;
  for(const button of document.querySelectorAll('#cueAThreatModesC button'))button.setAttribute('aria-pressed',String(button.dataset.mode===THREAT_ASSUMPTION_MODE));
}
function cueAMountUiC(panel){
  const page=document.querySelector('.control-deck-page[data-page="DEBUG"]')??document.querySelector('#controlDeckDebugPage');if(!page||document.getElementById('cueAThreatModesC'))return;
  const section=document.createElement('section');section.id='cueAThreatModesC';section.className='control-deck-section';section.innerHTML='<div class="control-deck-heading">ASM CUE_A 위협 가정</div><div class="control-deck-grid"><button type="button" class="wep-btn misc" data-mode="MAX_THREAT">MAX THREAT</button><button type="button" class="wep-btn misc" data-mode="CONFIRMED_ONLY">CONFIRMED ONLY</button></div><div id="cueAThreatStatusC" class="control-deck-note" role="status"></div>';(page.querySelector('.control-deck-section:last-of-type')??page).after(section);
  for(const button of section.querySelectorAll('button'))bindPress(button,()=>setThreatAssumptionModeC(button.dataset.mode));cueAUpdateUiC();
}
