// MAP_A_UI: independent transient operator state. Never serialized in game saves.
window.__MAP_A__=(()=>{
 const KEY='aegis.map.a.input.1',host=document.getElementById('uiDesktopA'),pointers=new Map();
 let enabled=true,lookup=null,controlled=null,firingTarget=null,lastRecord=null,picture=[],pictureAt=-Infinity,lastInfo=-Infinity,actionSignature='',gesture=null,longTimer=0,pinch=null,suppressUntil=-Infinity,measure=null,lastUndoCount=0;
 const additions=new Map(),counts={ship:0,helo:0,harpoon:0,precision:0,identity:0,undo:0};
 try{const s=JSON.parse(window.localStorage.getItem(KEY)||'null');if(s?.schema===1&&typeof s.enabled==='boolean')enabled=s.enabled;}catch(_){}
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;};
 const body=el('div','map-info-a'),head=el('div','map-info-head-a'),detail=el('div','map-info-detail-a'),notice=el('p','map-notice-a'),actions=el('div','map-info-actions-a');body.append(head,detail,notice,actions);const info=window.__UI_A__.register('INFO','정보',body,240,160);info.setAttribute('aria-label','지도 객체 정보');
 const menu=el('aside','map-menu-a'),candidates=el('aside','map-menu-a'),undo=el('button','map-undo-a'),measurement=el('div','map-measure-a');menu.id='mapContextMenuA';candidates.id='mapCandidatesA';undo.id='mapUndoA';measurement.id='mapMeasurementA';menu.setAttribute('aria-label','지도 상황 메뉴');candidates.setAttribute('aria-label','겹친 객체 선택');undo.type='button';for(const e of [menu,candidates,undo,measurement]){e.hidden=true;host.append(e);isolate(e);}
 function isolate(e){for(const n of ['pointerdown','pointermove','pointerup','pointercancel','mousedown','mouseup','click','dblclick','touchstart','touchmove','touchend','wheel','contextmenu'])e.addEventListener(n,v=>{v.stopPropagation();if(n==='contextmenu')v.preventDefault();},{passive:n.startsWith('touch')||n==='wheel'});}
 const setting=el('label','ui-settings-a','지도 입력: '),select=el('select');select.id='mapInputModeA';select.setAttribute('aria-label','지도 입력');for(const [value,text]of [['NEW','신규(MAP_A)'],['LEGACY','기존']]){const o=el('option','',text);o.value=value;select.append(o);}setting.append(select);document.querySelector('#uiWindowA-DEBUG .ui-body-a').append(setting);select.value=enabled?'NEW':'LEGACY';select.addEventListener('change',()=>setMode(select.value==='NEW'));
 function setMode(on){enabled=!!on;select.value=enabled?'NEW':'LEGACY';resetGesture();closeTransient();try{window.localStorage.setItem(KEY,JSON.stringify({schema:1,enabled}));}catch(_){}refresh(true);return enabled;}
 function currentTool(){return harpoonRouteEditingE()?'HARPOON_INS':controlled?'NAV':'NONE';}
 function planningReason(){return harpoonRouteEditingE()?'하푼 계획 작성 중':'';} // MAP_B weapon planning joins this one policy point.
 function controlReason(o){if(planningReason())return planningReason();if(!o)return '선택 없음';if(o.kind==='OWN')return '';if(o.kind==='ALLY')return '항로 명령 미지원';if(o.kind==='HELO'){if(o.state==='LOST')return '운용 불가';if(wip125PreSailOpen)return '출항 후 사용 가능';if(shipEquipmentOfflineV1())return '모함 항공 통제 불가';return '';}return '통제 가능한 플랫폼 아님';}
 function records(force=false){const now=performance.now();if(force||now-pictureAt>=100){picture=mapObservedObjectsA();pictureAt=now;}return picture;}
 function resolve(key,force=false){return records(force).find(o=>o.key===key)??mapLaunchReceiptsA().find(o=>o.key===key)??null;}
 function controlObject(){if(!controlled)return null;if(controlled==='OWN')return mapOwnShipA();return mapOwnHelosA().find(h=>h.key===controlled)??null;}
 function lookupObject(){const o=lookup?resolve(lookup):null;if(o){lastRecord=o;return o;}return lookup&&lastRecord?{...lastRecord,lost:true}:null;}
 function show(o){if(!o)return;lookup=o.key;lastRecord=o;mapLegacyCursorBridgeA(o);actionSignature='';window.__UI_A__.open('INFO');refresh(true);}
 function showControlInfo(){show(controlObject()??mapOwnShipA());}
 function takeControl(o){const reason=controlReason(o);if(reason)return {ok:false,reason};if(controlled!==o.key){controlled=o.key;additions.set(controlled,0);}refresh(true);return {ok:true};}
 function releaseControl(){controlled=null;refresh(true);return {ok:true};}
 function pointSig(p){return p.map(o=>o.key).sort().join('|');}
 function segmentDistance(x,y,a,b){const dx=b.x-a.x,dy=b.y-a.y,u=clamp(((x-a.x)*dx+(y-a.y)*dy)/(dx*dx+dy*dy||1),0,1);return Math.hypot(x-a.x-u*dx,y-a.y-u*dy);}
 function esmSegment(o){const own=mapOwnShipA(),r=kmToWorld(Math.min(currentTacticalViewKm(),90));return [worldToScreen(own.x,own.y),worldToScreen(own.x+Math.cos(o.bearingRad)*r,own.y+Math.sin(o.bearingRad)*r)];}
 function hits(x,y){const v=AEGIS_VIEWPORT.twoD;if(x<v.x||x>v.x+v.w||y<v.y||y>v.y+v.h)return [];return records().map(o=>{if(o.kind==='ESM'){const[a,b]=esmSegment(o);return {...o,distancePx:segmentDistance(x,y,a,b)};}const p=worldToScreen(o.x,o.y);return {...o,distancePx:Math.hypot(x-p.x,y-p.y)};}).filter(o=>o.distancePx<=(o.kind==='ESM'?12:20)).sort((a,b)=>a.distancePx-b.distancePx||a.key.localeCompare(b.key));}
 function putText(e,text){if(e.textContent!==text)e.textContent=text;}
 function age(o){return Math.max(0,mapNowA()-(o?.measuredAtS??mapNowA()));}
 function fmt(n,d=1){return Number.isFinite(n)?n.toFixed(d):'알 수 없음';}
 function section(name,text){const group=el('section','map-source-a');group.append(el('h4','',name),el('pre','',text));return group;}
 function information(o){
  if(!o)return {header:'선택 없음',sections:[]};
  const row=(o.kind==='ESM'||o.kind==='RECEIPT')?[]:[`위치 추정/항법 (m): ${fmt(worldToMeters(o.x),0)}, ${fmt(worldToMeters(o.y),0)}${Number.isFinite(o.z)?' · 고도 '+fmt(o.z,0):''}`];
  const header=`${o.label}\n${o.classification??'-'} · ${o.identity??'-'}\n${o.lost?'트랙 소실 · 마지막 보고':'마지막 갱신'} ${age(o).toFixed(1)}초 전${o.quality!=null?' · 품질 '+fmt(o.quality,2):''}`,sections=[];
  if(o.kind==='ESM'){sections.push({name:'ESM · '+age(o).toFixed(1)+'s',text:`방위 ${fmt((o.bearingRad*180/Math.PI+450)%360,1)}° ±${fmt(o.bearingSigmaDeg,1)}°\n거리: 알 수 없음\n대역: ${o.band??'보고 없음'} · 방사체 계열: ${o.emitterClass??o.type??'보고 없음'}\n신뢰도: ${fmt(o.confidence,2)}`});return {header,sections};}
  if(o.kind==='TRACK'){
   if(row.length)sections.push({name:'융합된 관측 추정',text:row.join('\n')});
   sections.push({name:'자체 레이더',text:emconActive?'EMCON — 능동 관측 없음':o.local?.length?o.local.map(q=>`${q.name} · ${fmt(mapNowA()-q.measuredAtS,1)}s 전${q.rangeSigmaM!=null?' · 거리 σ '+fmt(q.rangeSigmaM,1)+'m':''}${q.azSigmaDeg!=null?' · 방위 σ '+fmt(q.azSigmaDeg,2)+'°':''}`).join('\n'):'자체 관측 기여 없음'});
   if(o.remote?.length)sections.push({name:'데이터링크',text:o.remote.map(q=>`${q.sourceId} · 측정 ${fmt(q.measuredAtS,1)}s (${fmt(mapNowA()-q.measuredAtS,1)}s 전)\n수신 ${fmt(q.receivedAtS,1)}s · 보고 #${q.sequence??'-'}`).join('\n')});
   const esm=esmContacts.get(o.id);if(esm){const e=mapEsmReadA(o.id,esm);sections.push(...information(e).sections);} // Existing same-file association only.
   if(o.isar){const c=o.isar.candidates[0];sections.push({name:'데이터링크 ISAR · '+fmt(mapNowA()-o.isar.measuredAtS,1)+'s',text:`${o.isar.sourceId} · ${c?.label??'후보 없음'} ${fmt(c?.confidence,2)}\n전장 ${fmt(o.isar.lengthM,0)}±${fmt(o.isar.lengthSigmaM,0)}m`});}
   if(o.iff||o.identificationEvidence)sections.push({name:'식별 근거',text:`${o.identificationEvidence??'운용자 미지정'}${o.iff?'\nIFF '+(o.iff.authenticatedFriendly?'아군 응답':'응답 없음')+' · '+fmt(mapNowA()-o.iff.measuredAtS,1)+'s 전':''}`});
  }else if(o.kind==='HELO'){sections.push({name:o.source+' · '+fmt(age(o),1)+'s',text:row.concat(`단계: ${HELO_LABELS_A[o.state]??o.state}`,`레이더: ${o.radarMode}`,`경로점: ${o.routeCount} · 현재 ${o.routeIndex+1}`,`속력: ${fmt(o.speedKt,1)}kt`).join('\n')});
  }else if(o.kind==='ALLY'||o.kind==='NET'){if(o.local?.length)sections.push({name:'자체 레이더 (기존 연관)',text:emconActive?'EMCON — 능동 관측 없음':o.local.map(q=>q.name+' · '+fmt(mapNowA()-q.measuredAtS,1)+'s 전').join('\n')});sections.push({name:o.source+' · '+fmt(age(o),1)+'s',text:row.concat((o.remote??[]).map(q=>q.sourceId+' · '+fmt(mapNowA()-q.measuredAtS,1)+'s 전')).join('\n')});
  }else if(o.kind==='MISSILE'){sections.push({name:o.source+' · '+fmt(age(o),1)+'s',text:`표적 트랙: ${o.targetTrackId??'-'}\n단계: ${o.phase}\n남은 시간: ${Number.isFinite(o.remainingS)?fmt(o.remainingS,1)+'s':'알 수 없음'}`});
  }else if(o.kind==='RECEIPT'){sections.push({name:'자함 발사 확인',text:`발사 시각: ${fmt(o.releaseAtS,1)}s\n지정 트랙: ${o.targetTrackId??'좌표/INS 검색'}\n현재 위치: 알 수 없음(데이터링크 없음)\n발사 후 경로 갱신: 없음\n기억 계획 경로(m):\n${o.route.length?o.route.map((p,i)=>`${i+1}: ${fmt(p.x,0)}, ${fmt(p.y,0)}`).join('\n'):'직접 INS 계획'}`});
  }else sections.push({name:o.source??'자함 계획',text:row.concat(o.kind==='OWN'?[`속력 ${fmt(o.speedKt,1)}kt · 침로 ${fmt(o.headingDeg,0)}°`]:[]).join('\n')});
  return {header,sections};
 }
 function action(label,fn,reason='',id=''){const wrap=el('div','map-action-a'),why=el('small','map-disabled-reason-a',reason),b=el('button','',label);b.type='button';if(label==='정밀추적')b.classList.add('ui-danger-a');b.disabled=!!reason;b.title=reason;why.hidden=!reason;if(id)b.id=id;b.addEventListener('click',()=>{const r=fn();if(r?.reason)putText(notice,r.reason);refresh(true);});wrap.append(why,b);return wrap;}
 function precision(o){counts.precision++;return mapPrecisionCommandA(o);}
 function identity(o,id){const current=resolve(o.key,true);if(!current||current.kind!=='TRACK')return {ok:false,reason:'트랙 소실'};counts.identity++;return setTrackOperatorIdentityA3(current.id,id);}
 function openIdentity(o,x,y){menu.replaceChildren(el('strong','',o.label+' · ID 변경'));for(const id of ['UNKNOWN','HOSTILE','TRAINING_TARGET','FRIEND','NEUTRAL'])menu.append(action(id,()=>{const r=identity(o,id);hide(menu);return r;},'', 'mapIdentityA-'+id));menu.hidden=false;place(menu,x,y);}
 function isarReason(o){const h=controlObject();if(h?.kind!=='HELO'||h.radarMode!=='ISAR')return 'ISAR 모드 헬기 통제 필요';if(o.kind!=='TRACK'||o.classification!=='SURFACE')return '수상 트랙 필요';return '';}
 function shootIsar(o){const r=isarReason(o);if(r)return {ok:false,reason:r};return heloCommandA(controlObject().id,'ISAR_TARGET',{x:worldToMeters(o.x),y:worldToMeters(o.y)});}
 function deleteReason(o){const a=o?.kind==='WP'?routePoints:harpoonRuntimeA().routeDraft.pointsM;if(!['WP','HWP'].includes(o?.kind)||o.id!==a.length-1)return '마지막 점만 취소 가능';if(o.kind==='HWP'&&!harpoonRouteEditingE())return '하푼 경로 편집 필요';return '';}
 function deleteLast(o){const now=resolve(o.key,true);if(!now)return {ok:false,reason:'점이 더 이상 없음'};const why=deleteReason(now);if(why)return {ok:false,reason:why};counts.undo++;if(now.kind==='WP')undoLastWp();else harpoonRouteUndoMapA();pictureAt=-Infinity;refresh(true);return {ok:true};}
 function append(x,y){const tool=currentTool();let r={ok:false};if(tool==='HARPOON_INS'){r=harpoonRouteAddE(x,y);if(r.ok){counts.harpoon++;lastUndoCount=harpoonRuntimeA().routeDraft.pointsM.length;}}else if(controlled==='OWN'){addWaypoint(x,y);counts.ship++;r={ok:true};}else{const h=controlObject();if(h?.kind==='HELO'){r=heloCommandA(h.id,'ROUTE_APPEND',{x:worldToMeters(x),y:worldToMeters(y)});if(r.ok)counts.helo++;}}
  if(r.ok&&tool==='NAV')additions.set(controlled,(additions.get(controlled)??0)+1);pictureAt=-Infinity;refresh(true);return r;
 }
 function undoLast(){counts.undo++;if(currentTool()==='HARPOON_INS'){const r=harpoonRouteUndoMapA();lastUndoCount=harpoonRuntimeA().routeDraft.pointsM.length;refresh(true);return r;}if(!controlled||(additions.get(controlled)??0)<1)return {ok:false,reason:'이번 통제에서 추가한 점 없음'};if(controlled==='OWN')undoLastWp();else heloCommandA(controlObject()?.id,'UNDO_ROUTE');additions.set(controlled,Math.max(0,(additions.get(controlled)??0)-1));pictureAt=-Infinity;refresh(true);return {ok:true};}
 undo.addEventListener('click',undoLast);
 function viewPlatform(o){if(o.kind==='HELO')return heloFocusViewB(o.id);const v=window.__WIP148_3D_VIEW__;v.resetCamera();v.focusPhysicalShipB(o.kind==='ALLY'?o.viewId:null);return v.open();}
 function buildActions(o){actions.replaceChildren();if(!o)return;const lost=o.lost?'트랙 소실':'';
  if(['TRACK','NET','ESM'].includes(o.kind)){
   actions.append(action('정밀추적',()=>precision(resolve(o.key,true)),lost||mapPrecisionReasonA(o),'mapPrecisionA'));
   actions.append(action('ID 변경',()=>{const r=actions.getBoundingClientRect();openIdentity(o,r.x,r.y);},lost||(o.kind!=='TRACK'?'로컬 트랙 없음':''),'mapIdentityA'));
   if(!isarReason(o))actions.append(action('ISAR 촬영',()=>shootIsar(o),lost,'mapIsarA'));
  }else if(['OWN','ALLY','HELO'].includes(o.kind)){
   actions.append(action('통제',()=>takeControl(resolve(o.key,true)??o),lost||controlReason(o),'mapControlA'));
   if(controlled===o.key)actions.append(action('통제 해제',releaseControl,'','mapReleaseControlA'));
   if(o.kind==='OWN'||o.kind==='HELO'&&o.visible||o.kind==='ALLY'&&o.viewId)actions.append(action('3D 보기',()=>viewPlatform(o),'','mapViewA'));
   if(o.kind==='OWN')for(const receipt of mapLaunchReceiptsA().slice(-8))actions.append(action(receipt.label,()=>show(receipt)));
  }else if(o.kind==='WP'||o.kind==='HWP')actions.append(action('삭제',()=>deleteLast(o),lost||deleteReason(o),'mapDeletePointA'));
 }
 function refresh(force=false){const t=performance.now();if(!force&&t-lastInfo<250)return;lastInfo=t;const o=lookupObject(),s=information(o);putText(head,s.header);const text=JSON.stringify(s.sections);if(detail.dataset.signature!==text){detail.dataset.signature=text;detail.replaceChildren(...s.sections.map(q=>section(q.name,q.text)));}
  const signature=JSON.stringify([o?.key,o?.lost,controlled,planningReason(),o?mapPrecisionReasonA(o):'',o?isarReason(o):'',o?.kind==='WP'||o?.kind==='HWP'?deleteReason(o):'',mapLaunchReceiptsA().length]);if(force||signature!==actionSignature){actionSignature=signature;buildActions(o);}
  const editing=currentTool()==='HARPOON_INS',hcount=harpoonRuntimeA().routeDraft.pointsM.length;undo.hidden=!enabled||!(editing?hcount>0:controlled&&(additions.get(controlled)??0)>0);undo.textContent=editing?'마지막 경유점 취소':'마지막 WP 취소';const v=AEGIS_VIEWPORT.layout,b=document.getElementById('uiStatusBarA').getBoundingClientRect(),scale=window.__UI_A_SETTINGS__.scale;undo.style.left=(v.x+6)/scale+'px';undo.style.bottom=(v.y+v.h-b.y+6)/scale+'px';
  if(measure){measurement.hidden=false;measurement.textContent=`측정 ${fmt(measure.distanceM/1000,2)}km · ${fmt(measure.bearingDeg,1)}°`;measurement.style.left=(v.x+6)/scale+'px';measurement.style.bottom=(v.y+v.h-b.y+42)/scale+'px';}
 }
 function place(node,x,y){const v=AEGIS_VIEWPORT.twoD,scale=window.__UI_A_SETTINGS__.scale;node.style.minWidth=Math.min(170,Math.max(1,v.w-8)/scale)+'px';node.style.maxWidth=Math.max(1,v.w-8)/scale+'px';node.style.maxHeight=Math.max(1,v.h-8)/scale+'px';const r=node.getBoundingClientRect();node.style.left=Math.max(v.x+4,Math.min(v.x+v.w-r.width-4,x))/scale+'px';node.style.top=Math.max(v.y+4,Math.min(v.y+v.h-r.height-4,y))/scale+'px';}
 function hide(node){node.hidden=true;}
 function closeTransient(){hide(menu);hide(candidates);}
 function choose(rows,x,y,context=false){closeTransient();if(rows.length===1){if(context)contextFor(rows[0],x,y);else show(rows[0]);return;}if(!rows.length){if(context)contextFor(null,x,y);return;}candidates.replaceChildren(el('strong','','겹친 객체 선택'));for(const o of rows)candidates.append(action(o.kind+' · '+o.label,()=>{hide(candidates);if(context)contextFor(resolve(o.key,true)??o,x,y);else show(resolve(o.key,true)??o);}));candidates.hidden=false;place(candidates,x,y);}
 function contextFor(o,x,y){hide(candidates);menu.replaceChildren(el('strong','',o?.label??'빈 바다'));const closeCall=fn=>()=>{const r=fn();hide(menu);return r;};
  if(o){menu.append(action('정보 보기',closeCall(()=>show(o))));if(['TRACK','NET','ESM'].includes(o.kind)){menu.append(action('정밀추적',closeCall(()=>precision(resolve(o.key,true))),mapPrecisionReasonA(o)));menu.append(action('ID 변경',()=>openIdentity(o,x,y),o.kind!=='TRACK'?'로컬 트랙 없음':''));if(!isarReason(o))menu.append(action('ISAR 촬영',closeCall(()=>shootIsar(o))));}
   else if(['OWN','ALLY','HELO'].includes(o.kind)){menu.append(action('통제',closeCall(()=>takeControl(o)),controlReason(o)));if(controlled===o.key)menu.append(action('통제 해제',closeCall(releaseControl)));if(o.kind==='OWN'||o.kind==='HELO'&&o.visible||o.kind==='ALLY'&&o.viewId)menu.append(action('3D 보기',closeCall(()=>viewPlatform(o))));else menu.append(action('3D 보기',()=>{},'사용 가능한 아군함·헬기 시점 없음'));}
   else if(o.kind==='WP'||o.kind==='HWP'){menu.append(action('삭제',closeCall(()=>deleteLast(o)),deleteReason(o)));menu.append(action('마지막 점 취소',closeCall(()=>{if(o.kind==='WP'){undoLastWp();return {ok:true};}return harpoonRouteUndoMapA();}),o.kind==='HWP'&&!harpoonRouteEditingE()?'하푼 경로 편집 필요':''));}
  }else{const p=screenToWorld(x,y),base=controlObject()??mapOwnShipA();menu.append(action('여기로 화면 중심',closeCall(()=>{camOffset.x=p.x-aircraft.x();camOffset.y=p.y-aircraft.y();})));menu.append(action('거리·방위 측정',closeCall(()=>{const dx=worldToMeters(p.x-base.x),dy=worldToMeters(p.y-base.y);measure={distanceM:Math.hypot(dx,dy),bearingDeg:(Math.atan2(dy,dx)*180/Math.PI+450)%360};refresh(true);})));menu.append(action('항로점 추가',closeCall(()=>append(p.x,p.y)),currentTool()==='NAV'?'':'NAV 통제 필요'));menu.append(action('경유점 추가',closeCall(()=>append(p.x,p.y)),currentTool()==='HARPOON_INS'?'':'하푼 경로 편집 필요'));}
  menu.hidden=false;place(menu,x,y);
 }
 function tap(x,y){const rows=hits(x,y);if(rows.length){choose(rows,x,y);return;}if(currentTool()==='NONE'){lookup=null;lastRecord=null;refresh(true);}else{const p=screenToWorld(x,y);append(p.x,p.y);}}
 function killLong(){window.clearTimeout(longTimer);longTimer=0;}
 function resetGesture(){killLong();for(const id of pointers.keys())try{canvas.releasePointerCapture(id);}catch(_){}pointers.clear();gesture=null;pinch=null;canvas.classList.remove('dragging');}
 function stop(e){e.stopImmediatePropagation();if(e.cancelable)e.preventDefault();}
 function contextAt(x,y){records(true);choose(hits(x,y),x,y,true);}
 function down(e){if(!enabled)return;stop(e);if(e.button===2||(e.pointerType==='pen'&&(e.buttons&2))){resetGesture();contextAt(e.clientX,e.clientY);suppressUntil=performance.now()+350;return;}if(e.button!==0)return;const now=performance.now();pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});try{canvas.setPointerCapture?.(e.pointerId);}catch(_){}
  if(pointers.size!==1||e.isPrimary===false){killLong();if(gesture)gesture.multi=true;const[a,b]=[...pointers.values()];if(a&&b)pinch={distance:Math.hypot(a.x-b.x,a.y-b.y),km:tacticalViewKm};suppressUntil=now+300;return;}
  records(true);gesture={id:e.pointerId,x:e.clientX,y:e.clientY,t:now,cam:{...camOffset},moved:false,multi:false,menu:false,blocked:!menu.hidden||!candidates.hidden,signature:pointSig(hits(e.clientX,e.clientY))};if(gesture.blocked){closeTransient();return;}
  longTimer=setTimeout(()=>{if(!gesture||gesture.moved||gesture.multi)return;gesture.menu=true;contextAt(gesture.x,gesture.y);},550);canvas.classList.add('dragging');
 }
 function move(e){if(!enabled)return;stop(e);if(e.pointerType==='pen'&&(e.button===2||(e.buttons&2))){if(menu.hidden&&candidates.hidden){resetGesture();contextAt(e.clientX,e.clientY);suppressUntil=performance.now()+350;}return;}const point=pointers.get(e.pointerId);if(!point)return;point.x=e.clientX;point.y=e.clientY;if(pointers.size>1){if(pinch){const[a,b]=[...pointers.values()],d=Math.hypot(a.x-b.x,a.y-b.y);if(d>1){tacticalViewKm=clamp(pinch.km*pinch.distance/d,VP_TACTICAL_DISTANCE_A.minKm,VP_TACTICAL_DISTANCE_A.maxKm);vpUpdateMapZoomA();updateTacticalScaleLabel();}}return;}
  const g=gesture;if(!g||g.id!==e.pointerId||g.menu||g.blocked)return;const dx=e.clientX-g.x,dy=e.clientY-g.y;if(Math.hypot(dx,dy)>=10){g.moved=true;killLong();}if(g.moved){const a=screenToWorld(g.x,g.y),b=screenToWorld(e.clientX,e.clientY);camOffset.x=g.cam.x+a.x-b.x;camOffset.y=g.cam.y+a.y-b.y;}
 }
 function up(e){if(!enabled)return;stop(e);killLong();const g=gesture;if(pointers.size>1||g?.multi)suppressUntil=performance.now()+300;pointers.delete(e.pointerId);try{canvas.releasePointerCapture(e.pointerId);}catch(_){}if(g?.id===e.pointerId){gesture=null;canvas.classList.remove('dragging');const elapsed=performance.now()-g.t;if(!g.moved&&!g.multi&&!g.menu&&!g.blocked&&elapsed<350&&performance.now()>=suppressUntil&&Math.hypot(e.clientX-g.x,e.clientY-g.y)<10){records(true);if(pointSig(hits(e.clientX,e.clientY))===g.signature)tap(e.clientX,e.clientY);}}if(!pointers.size)pinch=null;
 }
 for(const[n,fn]of [['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',e=>{if(enabled){stop(e);suppressUntil=performance.now()+300;resetGesture();}}],['contextmenu',e=>{if(enabled){stop(e);if(menu.hidden&&candidates.hidden)contextAt(e.clientX,e.clientY);}}]])canvas.addEventListener(n,fn,{capture:true,passive:false});
 canvas.addEventListener('wheel',()=>{if(enabled&&gesture){gesture.multi=true;killLong();}},{capture:true,passive:true});
 for(const type of ['touchstart','touchmove','touchend','touchcancel'])canvas.addEventListener(type,e=>{if(!enabled)return;stop(e);if(e.touches.length>1){killLong();if(gesture)gesture.multi=true;suppressUntil=performance.now()+300;}},{capture:true,passive:false});
 document.addEventListener('pointerdown',e=>{if(menu.contains(e.target)||candidates.contains(e.target))return;if(e.target!==canvas)closeTransient();},{capture:true});
 document.addEventListener('keydown',e=>{if(e.key!=='Escape'||document.querySelector('dialog[open]'))return;if(!menu.hidden)hide(menu);else if(!candidates.hidden)hide(candidates);else if(!info.hidden)window.__UI_A__.close('INFO');else return;e.preventDefault();e.stopImmediatePropagation();},{capture:true});
 AEGIS_VIEWPORT.subscribe(()=>{resetGesture();for(const n of [menu,candidates])if(!n.hidden){const r=n.getBoundingClientRect();place(n,r.x,r.y);}refresh(true);});
 function draw(context){if(!enabled)return;const rows=records(),o=rows.find(q=>q.key===lookup),c=controlObject();context.save();context.lineWidth=1/mapZoom;
  if(o&&o.kind==='ESM'){const own=mapOwnShipA(),r=kmToWorld(Math.min(currentTacticalViewKm(),90))*.88,x=own.x+Math.cos(o.bearingRad)*r,y=own.y+Math.sin(o.bearingRad)*r;context.strokeStyle='#e0d7aa';context.setLineDash([3/mapZoom,3/mapZoom]);context.beginPath();context.arc(x,y,16/mapZoom,0,Math.PI*2);context.stroke();}
  else if(o&&Number.isFinite(o.x)){context.strokeStyle='#e8eef2';context.setLineDash([3/mapZoom,3/mapZoom]);context.beginPath();context.arc(o.x,o.y,16/mapZoom,0,Math.PI*2);context.stroke();}
  context.setLineDash([]);if(c){const r=23/mapZoom,d=7/mapZoom;context.strokeStyle='#9fffd0';for(const[a,b]of [[-1,-1],[-1,1],[1,-1],[1,1]]){context.beginPath();context.moveTo(c.x+a*(r-d),c.y+b*r);context.lineTo(c.x+a*r,c.y+b*r);context.lineTo(c.x+a*r,c.y+b*(r-d));context.stroke();}}context.restore();
 }
 function tapeModel(bearing,heading,width=300){const wrap=a=>((a+180)%360+360)%360-180,ppd=width/60,delta=wrap(heading-bearing);return {bearing:((bearing%360)+360)%360,heading:((heading%360)+360)%360,deltaDeg:delta,markerPx:clamp(delta,-28,28)*ppd,edge:Math.abs(delta)>28?(delta<0?'left':'right'):null,ticks:Array.from({length:36},(_,i)=>({degrees:i*10,label:i%3===0?String(i*10).padStart(3,'0'):'',x:wrap(i*10-bearing)*ppd}))};}
 let tapeElements=null;
 function updateTape(tape,bearing,heading){if(!tapeElements){const rail=el('div','map-tape-rail-a'),ticks=[];for(let i=0;i<36;i++){const t=el('span','map-tape-tick-a'),label=el('span','map-tape-label-a');t.append(label);rail.append(t);ticks.push({t,label});}const marker=el('span','map-tape-heading-a'),center=el('span','map-tape-center-a','▼'),value=el('div','map-tape-value-a'),hdg=el('div','map-tape-own-a');rail.append(marker,center);tape.replaceChildren(rail,value,hdg);tapeElements={rail,ticks,marker,value,hdg};}
  const width=tape.clientWidth-16,m=tapeModel(bearing,heading,width),s=tapeElements;for(const [i,q]of m.ticks.entries()){const{t,label}=s.ticks[i];t.style.transform=`translateX(${q.x}px)`;t.hidden=Math.abs(q.x)>width/2+3;label.textContent=q.label;t.dataset.degrees=q.degrees;}
  s.marker.style.transform=`translateX(${m.markerPx}px)`;s.marker.textContent=m.edge==='left'?'◀':m.edge==='right'?'▶':'◆';s.marker.dataset.heading=heading;s.value.textContent=String(Math.round(m.bearing)%360).padStart(3,'0')+'°';s.hdg.textContent='HDG '+String(Math.round(m.heading)%360).padStart(3,'0')+'°';tape.dataset.bearing=bearing;
 }
 function loop(){refresh();requestAnimationFrame(loop);}requestAnimationFrame(loop);refresh(true);
 return Object.freeze({setMode,showControlInfo,controlLabel(hull){const o=controlObject();return o?'통제: '+o.label:'통제 없음 · '+hull;},updateTape,draw,
  snapshot(){const o=lookupObject();return {schema:'AEGIS_MAP_A_UI_1',presentationOnly:true,enabled,controlPlatform:controlled,lookupTarget:lookup,currentTool:currentTool(),firingDesignatedTarget:firingTarget,info:information(o),object:o,menuOpen:!menu.hidden,candidatesOpen:!candidates.hidden,candidateLabels:[...candidates.querySelectorAll('button')].map(b=>b.textContent),counts:{...counts},measurement:measure?{...measure}:null};},
  // Read-only inspection; tests use native pointer events and the visible command buttons.
  objects(){return records(true).map(o=>({...o}));},hitTest:hits,tapeModel,receipt(id){const o=mapLaunchReceiptsA().find(q=>q.id===id);if(o)show(o);return !!o;}
 });
})();
