// PIP_B presentation only. All tactical commands remain in their native paths.
window.__PIP_B__=(()=>{
 const key='aegis.pip.b.sensor-beams.1',stats={lockedRefreshes:0,canvasCards:0,beamGroups:0};
 let sensorBeams=false,lastLock=null;
 try{sensorBeams=window.localStorage.getItem(key)==='true';}catch(_){}
 const text=document.createElement('pre');text.id='lockedTargetTextB';text.textContent='락 없음';
 const locked=window.__UI_A__.register('LOCKED','락온 표적',text,220,120);
 // Native window menus can extend below a low PiP and under the status bar.
 // Keep the original nodes/listeners, but clamp their open popup to the layout.
 const menus=[...document.querySelectorAll('.ui-window-menu-a')].map(menu=>({menu,win:menu.closest('.ui-window-a')}));
 for(const {menu,win}of menus){menu.dataset.ownerWindowB=win.id;document.getElementById('uiDesktopA').append(menu);
  for(const event of ['pointerdown','pointermove','pointerup','pointercancel','wheel','touchstart','touchmove','touchend','contextmenu'])menu.addEventListener(event,e=>e.stopPropagation(),{passive:event.startsWith('touch')||event==='wheel'});
  new MutationObserver(()=>{if(win.hidden)menu.hidden=true;}).observe(win,{attributes:true,attributeFilter:['hidden']});
 }
 function placeMenus(){for(const {menu,win}of menus){if(menu.hidden)continue;
  const header=win.querySelector('.ui-title-a'),v=AEGIS_VIEWPORT.layout,s=window.__UI_A_SETTINGS__.scale,bar=document.getElementById('uiStatusBarA').getBoundingClientRect();
  menu.style.maxHeight=Math.max(36,(bar.top-v.y-8)/s)+'px';menu.style.overflowY='auto';
  const m=menu.getBoundingClientRect(),w=win.getBoundingClientRect(),h=header.getBoundingClientRect(),x=clamp(w.right-m.width-3,v.x+4,v.x+v.w-m.width-4),y=clamp(h.bottom+m.height<=bar.top-4?h.bottom:h.top-m.height,v.y+4,bar.top-m.height-4);
  menu.style.right='auto';menu.style.left=x/s+'px';menu.style.top=y/s+'px';
 }}
 for(const button of document.querySelectorAll('.ui-title-a button[title="창 메뉴"]'))button.addEventListener('click',placeMenus);
 document.addEventListener('pointerdown',e=>{if(e.target.closest('.ui-window-menu-a,button[title="창 메뉴"]'))return;for(const {menu}of menus)menu.hidden=true;},{capture:true});
 AEGIS_VIEWPORT.subscribe(placeMenus);
 const setting=document.createElement('label');setting.className='ui-settings-a';
 const toggle=document.createElement('input');toggle.type='checkbox';toggle.id='sensorBeams2DB';toggle.checked=sensorBeams;
 setting.append(toggle,document.createTextNode('2D 센서 빔 표시'));
 document.querySelector('#uiWindowA-DEBUG .ui-body-a').append(setting);
 toggle.addEventListener('change',()=>{sensorBeams=toggle.checked;try{window.localStorage.setItem(key,String(sensorBeams));}catch(_){}window.__PIP_A__?.invalidate();});
 // No chart paint is required by this timer. The existing once-per-frame
 // preparation supplies the exact old card fields, including its heading.
 function update(){const id=selectedLockId??null;
  if(id!==lastLock){if(id!==null)window.__UI_A__.open('LOCKED');lastLock=id;}
  text.textContent=id===null?'락 없음':(pipChartFrameA.lockedLines??[]).join('\n');
  stats.lockedRefreshes++;
 }
 setInterval(update,125);update();
 return Object.freeze({beams:()=>sensorBeams,beam(){stats.beamGroups++;},snapshot:()=>({sensorBeams,lastLock,stats:{...stats},text:text.textContent,open:!locked.hidden})});
})();
