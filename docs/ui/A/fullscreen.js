// UI_A: display preferences only; no game-save fields.
async function toggleFullscreen(options){
 try{if(isFullscreenActive()){if(options?.automatic!==true){window.__UI_A_SETTINGS__?.markExit();await (document.exitFullscreen||document.webkitExitFullscreen)?.call(document);}}else{await (document.documentElement.requestFullscreen||document.documentElement.webkitRequestFullscreen)?.call(document.documentElement);await window.__UI_A_SETTINGS__?.lockOrientation();}}catch(err){window.__UI_A_SETTINGS__?.log('Fullscreen: '+(err?.message||err));}refreshFullscreenBtn();
}
window.__UI_A_SETTINGS__=(()=>{
 const KEY='aegis.ui.a.preferences.1',allowed=[85,100,115,130];let scale=100,landscape=true,attempted=false,exited=false,wasFullscreen=false;
 function log(s){try{debugLog(s);}catch(_){(window.__UI_A_EARLY_LOG__??=[]).push(s);}}
 try{const q=JSON.parse(window.localStorage.getItem(KEY)||'null');if(q?.schema===1){scale=allowed.includes(q.scale)?q.scale:100;landscape=q.landscape!==false;}}catch(_){scale=100;}
 function sync(){document.documentElement.style.setProperty('--ui-scale-a',scale/100);for(const e of document.querySelectorAll('[data-ui-scale-a]'))e.value=String(scale);for(const e of document.querySelectorAll('[data-ui-landscape-a]'))e.checked=landscape;window.__UI_A__?.reflow(true);}
 function save(){try{window.localStorage.setItem(KEY,JSON.stringify({schema:1,scale,landscape}));}catch(_){scale=100;}sync();}
 async function lockOrientation(){if(landscape&&isFullscreenActive())try{await window.screen.orientation?.lock?.('landscape');}catch(_){}}
 function mount(host,suffix){const row=document.createElement('div');row.className='ui-settings-a';row.id='uiSettingsA-'+suffix;
  const existing=suffix==='system'?document.getElementById('fullscreenBtn'):null,fs=existing??document.createElement('button');if(!existing){fs.type='button';fs.textContent='⛶ 전체화면';fs.addEventListener('click',()=>toggleFullscreen());}
  const label=document.createElement('label');label.textContent='UI 크기 ';const select=document.createElement('select');select.dataset.uiScaleA='';select.setAttribute('aria-label','UI 크기');for(const n of allowed){const o=document.createElement('option');o.value=n;o.textContent=n+'%';select.append(o);}select.value=String(scale);select.addEventListener('change',()=>{scale=Number(select.value);save();});label.append(select);
  const orientation=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=landscape;check.dataset.uiLandscapeA='';check.addEventListener('change',()=>{landscape=check.checked;save();});orientation.append(check,document.createTextNode(' 가로 고정'));row.append(fs,label,orientation);host.append(row);sync();return row;}
 document.addEventListener('fullscreenchange',()=>{const now=isFullscreenActive();if(wasFullscreen&&!now)exited=true;wasFullscreen=now;});
 sync();return Object.freeze({mount,log,lockOrientation,markExit(){exited=true;},firstButton(e){if(attempted||exited||isFullscreenActive())return;attempted=true;if(e.target.closest('#uiSettingsA-selection button'))return;void toggleFullscreen({automatic:true});},setScale(n){scale=allowed.includes(n)?n:100;save();},snapshot(){return {schema:1,scale,landscape,attempted,exited};},get scale(){return scale/100;}});
})();
