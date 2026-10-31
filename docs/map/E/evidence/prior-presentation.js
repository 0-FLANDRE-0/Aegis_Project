// MAP_E_UI_BEGIN
// MAP_E: UI reads own navigation/inventory/observed cue only. No truth/RF/NPC
// enumeration. Native release commands remain the sole mutation authority.
window.__MAP_E__=(()=>{
 let menu,decoy,anchorKind=null,lastResult=null,remembered=null,mounted=false,lastRefresh=-Infinity;
 const dom={},levelNames={OFF:'끔',JAM:'재밍 자동',FULL:'전체 자동'},scale=()=>window.__UI_A_SETTINGS__.scale;
 const make=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text)e.textContent=text;return e;};
 function button(text,id,fn){const b=make('button','ui-button-a',text);b.type='button';b.id=id;b.addEventListener('click',fn);return b;}
 function isolate(e){for(const n of ['pointerdown','pointermove','pointerup','pointercancel','click','wheel','touchstart','touchmove','touchend','contextmenu'])e.addEventListener(n,x=>{x.stopPropagation();if(n==='contextmenu')x.preventDefault();},{passive:n.startsWith('touch')||n==='wheel'});}
 function place(e,a){if(e.hidden||!a)return;const v=AEGIS_VIEWPORT.layout,r=e.getBoundingClientRect(),s=scale();e.style.left=Math.max(v.x+4,Math.min(v.x+v.w-r.width-4,a.right-r.width))/s+'px';e.style.top=Math.max(v.y+4,Math.min(v.y+v.h-r.height-4,a.top-r.height-5))/s+'px';}
 function refreshChip(){const chip=document.getElementById('uiEmconChipA');if(!chip)return;chip.textContent='EMCON '+(emconActive?'ON':'OFF')+'\nECM '+ownEcmLevelE();chip.title='레이더 '+(emconActive?'OFF':'ON')+' · ECM '+levelNames[ownEcmLevelE()]+(!softKillAutoDoctrine&&(noiseJamActive||deceptJamActive)?' · 기존 재밍 승인 유지':'');chip.setAttribute('aria-expanded',String(!!menu&&!menu.hidden));chip.setAttribute('aria-controls','mapEmconMenuE');}
 function command(level){const q=ownEcmCommandE(level);refresh();refreshChip();return q;}
 function allRadiation(){
  if(!emconActive||ownEcmLevelE()!=='OFF'||noiseJamActive||deceptJamActive){remembered={owner:ACTIVE_SHIP_RUNTIME,level:ownEcmLevelE()};if(!emconActive)toggleEmcon();command('OFF');}
  else{if(emconActive)toggleEmcon();command(remembered?.owner===ACTIVE_SHIP_RUNTIME?remembered.level:'OFF');}
  refresh();
 }
 function toggleMenu(){if(!mounted)return;menu.hidden=!menu.hidden;decoy.hidden=true;refresh();refreshChip();}
 function close(){if(menu)menu.hidden=true;if(decoy)decoy.hidden=true;refreshChip();}
 function stockReason(k){
  if(shipEquipmentOfflineV1())return k==='SRBOC'?'채프 발사 차단 · 장비 정지':'SHIP_OFFLINE';
  if(k==='SRBOC'){
   if(MK36_RUNTIME_WIP15A.cooldownS>0)return 'Mk 36 SRBOC 대기 '+MK36_RUNTIME_WIP15A.cooldownS.toFixed(1)+'s';
   if(mk36LoadedRounds()<=0)return 'Mk 36 SRBOC — 발사관 탄약 없음';
   if(!mk36SelectLauncher(softKillPrimaryThreat()?.bearing??shipNav.heading))return 'Mk 36 SRBOC — 사용 가능한 발사관 없음';
  }else{
   const error=nulkaCueError15B(softKillPrimaryThreat());if(error)return error;
   if(skRuntime15B('NULKA').cooldownS>1e-9)return 'LAUNCH_CYCLE';
   if(!nulkaSelectLauncher15B(softKillPrimaryThreat().bearing))return 'NO_READY_CANISTER';
  }return null;
 }
 function popup(k){anchorKind=k;lastResult=null;menu.hidden=true;decoy.hidden=false;refresh();refreshChip();}
 function fire(){if(!anchorKind)return;const k=anchorKind;
  // Command happens only in this explicit click handler; no render-time dispatch.
  if(k==='SRBOC'){const n=deployOwnChaff();lastResult={kind:k,ok:n>0,fired:n,reason:n>0?null:document.getElementById('toastWrap')?.firstElementChild?.textContent??'Mk 36 SRBOC — 발사 거부'};}
  else{const q=nulkaFire15B(softKillPrimaryThreat());lastResult={kind:k,...q};}
  refresh();return lastResult;
 }
 function inventoryRendered(){const inv=document.getElementById('uiInventoryA');if(!inv)return;for(const e of [...inv.children]){const label=e.querySelector('span')?.textContent,k=label==='SRBOC'?'SRBOC':label==='Nulka'?'NULKA':null;if(!k)continue;let b=e;if(e.tagName!=='BUTTON'){const font=getComputedStyle(e).font;b=make('button','ui-ammo-a map-ammo-b');b.type='button';b.style.font=font;while(e.firstChild)b.append(e.firstChild);e.replaceWith(b);}b.dataset.decoyE=k;b.setAttribute('aria-label',(k==='SRBOC'?'SRBOC':'Nulka')+' 수동 발사');}window.__MAP_C__?.stabilizeInventory();}
 function refresh(){if(!mounted)return;
  if(armsPanelOpen){const v=AEGIS_VIEWPORT.layout,s=scale();armsPanel.style.left=v.cx/s+'px';armsPanel.style.top=v.cy/s+'px';armsPanel.style.width=Math.min(380,(v.w-20)/s)+'px';armsPanel.style.maxHeight=(v.h-40)/s+'px';}
  const level=ownEcmLevelE();dom.all.textContent='전체 방사 '+(emconActive&&level==='OFF'&&!noiseJamActive&&!deceptJamActive?'ON':'OFF');dom.radar.textContent='레이더 '+(emconActive?'ON':'OFF');for(const [k,e]of Object.entries(dom.levels))e.setAttribute('aria-pressed',String(level===k));dom.note.textContent=!softKillAutoDoctrine&&(noiseJamActive||deceptJamActive)?'기존 재밍 승인: '+(noiseJamActive?'NJ ':'')+(deceptJamActive?'DJ':''):'';place(menu,document.getElementById('uiEmconChipA').getBoundingClientRect());
  if(!decoy.hidden){const a=document.querySelector('[data-decoy-e="'+anchorKind+'"]');if(!a){decoy.hidden=true;return;}const why=stockReason(anchorKind)??(lastResult?.ok===false?lastResult.reason:null);dom.reason.textContent=why??(lastResult?.ok?'발사 완료':'');dom.fire.disabled=!!why;dom.fire.textContent=(anchorKind==='SRBOC'?'SRBOC':'Nulka')+' 발사';place(decoy,a.getBoundingClientRect());}
 }
 function mount(){const host=document.getElementById('uiDesktopA');host.append(armsPanel);armsPanel.style.zIndex='60000';armsPanel.style.pointerEvents='auto';isolate(armsPanel);mapELegacyNodeE('armsBtn').addEventListener('click',()=>{document.getElementById('uiWindowAddA').hidden=true;refresh();});menu=make('aside','ui-mode-menu-a map-popover-e');menu.id='mapEmconMenuE';menu.hidden=true;menu.setAttribute('aria-label','방사 및 ECM 조작');decoy=make('aside','ui-mode-menu-a map-popover-e map-decoy-e');decoy.id='mapDecoyMenuE';decoy.hidden=true;host.append(menu,decoy);isolate(menu);isolate(decoy);
  dom.all=button('전체 방사 OFF','mapAllRadiationE',allRadiation);dom.radar=button('레이더 OFF','mapRadarE',()=>{toggleEmcon();refresh();refreshChip();});menu.append(dom.all,dom.radar,make('span','','ECM'));const row=make('div','map-ecm-levels-e');dom.levels={};for(const[k,label]of Object.entries(levelNames)){const e=button(label,'mapEcm'+k+'E',()=>command(k));e.dataset.ecmLevelE=k;dom.levels[k]=e;row.append(e);}menu.append(row);dom.note=make('small','');menu.append(dom.note);dom.reason=make('small','map-decoy-reason-e');dom.fire=button('발사','mapDecoyFireE',fire);decoy.append(dom.reason,dom.fire);
  const inv=document.getElementById('uiInventoryA');inv.addEventListener('click',e=>{const a=e.target.closest('[data-decoy-e]');if(a){e.stopImmediatePropagation();popup(a.dataset.decoyE);}},{capture:true});
  document.addEventListener('pointerdown',e=>{if(!menu.contains(e.target)&&!document.getElementById('uiEmconChipA').contains(e.target))menu.hidden=true;if(!decoy.contains(e.target)&&!e.target.closest?.('[data-decoy-e]'))decoy.hidden=true;refreshChip();},{capture:true});document.addEventListener('keydown',e=>{if(e.key==='Escape')close();});
  const css=make('style');css.textContent=`#uiDesktopA #uiEmconChipA{white-space:pre;line-height:1.05;font-size:inherit}.map-popover-e{display:flex!important;flex-direction:column;gap:4px;padding:5px;font:11px/1.3 monospace;min-width:180px;max-width:240px}.map-popover-e[hidden]{display:none!important}.map-popover-e .map-ecm-levels-e{display:flex;gap:4px}.map-popover-e button{min-height:28px;min-width:28px;padding:3px 5px;font:11px/1.3 monospace}.map-popover-e button[aria-pressed=true]{border-color:#76dfbd}.map-popover-e small{white-space:normal;overflow-wrap:anywhere;color:#e8bb79}.map-popover-e small:empty{display:none}#uiDesktopA #mapDecoyMenuE #mapDecoyFireE{min-height:40px!important;height:40px!important;margin-top:8px}#uiDesktopA #armsPanelClose{min-height:28px;min-width:28px}.map-decoy-e{min-width:150px}#uiWindowAddA #armsBtn{display:block;width:100%;min-height:28px}#armsPanel{zoom:var(--ui-scale-a)}`;document.head.append(css);mounted=true;inventoryRendered();refreshChip();requestAnimationFrame(function update(now){if(now-lastRefresh>=100){lastRefresh=now;refresh();refreshChip();}requestAnimationFrame(update);});
 }
 return Object.freeze({mount,toggleMenu,inventoryRendered,refreshChip,snapshot(){return {level:ownEcmLevelE(),radarOn:!emconActive,noiseRequested:noiseJamActive,deceptionRequested:deceptJamActive,auto:softKillAutoDoctrine,menuOpen:!!menu&&!menu.hidden,decoyOpen:!!decoy&&!decoy.hidden,decoy:anchorKind,lastResult:lastResult?{kind:lastResult.kind,ok:!!lastResult.ok,reason:lastResult.reason??null,fired:lastResult.fired??null}:null,remembered:remembered?.owner===ACTIVE_SHIP_RUNTIME?remembered.level:null};}});
})();

// MAP_E_UI_END
