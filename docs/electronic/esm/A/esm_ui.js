// ESM_A Commit D — presentation-only ESM state and manual coordinate cue.
// This module consumes anonymous observations/estimates. It never creates a
// radar track, identity evidence, fire-control quality or automatic authority.
const ESM_A_CUE_SCHEMA='AEGIS_ESM_MANUAL_CUE_A_1';

function esmPresentationCopyA(c){
  const e=c?.estimate??null,history=(c?.history??[]).slice(-ESM_A_SPEC.historyMax).map(q=>({
    measuredAtS:q.measuredAtS,bearingRad:q.bearingRad,
    bearingSigmaDeg:rad2deg(Math.sqrt(q.angleCovarianceRad2[0])),
    originM:{x:q.receiver.positionM.x,y:q.receiver.positionM.y,z:q.receiver.positionM.z},
    receiverPlatformId:q.receiver.platformId
  }));
  return {contactId:c.contactId,state:c.state,age:c.age,bearing:c.bearing,
    bearingSigmaDeg:c.bearingSigmaDeg,band:c.band??null,type:c.type??null,
    emitterClass:c.emitterClass??null,quality:c.quality??c.strength??null,
    measuredAtS:c.measuredAtS,identity:'UNKNOWN',source:'PASSIVE_RF_ESM_A',
    estimate:e?esmJsonA(e):null,bearingHistory:history,
    automaticEngagementAuthority:false,truthUsed:false};
}

function esmUiContactA(id){return prepareElectronicF(ACTIVE_SHIP_RUNTIME).contacts.get(Number(id))??null;}
function esmUiAgeA(c){const t=c?.estimate?.measuredAtS??c?.measuredAtS;return Number.isFinite(t)?Math.max(0,simStepCounter*SIM_FIXED_DT-t):Infinity;}
function esmUiWorldA(p){return p&&Number.isFinite(p.x)&&Number.isFinite(p.y)?{x:metersToWorld(p.x),y:metersToWorld(p.y)}:null;}
function esmUiEllipseA(cov){return Array.isArray(cov)&&cov.length===4&&cov.every(Number.isFinite)?esmEllipseA(cov):null;}
function esmUiModeLabelA(state){return ({BEARING_ONLY:'방위만',LIKELIHOOD_REGION:'확률 영역',GEOLOCATED_ESTIMATE:'위치 추정',COAST:'코스팅',LOST:'소실'})[state]??state??'알 수 없음';}

function esmInformationTextA(o){
  const e=o.estimate??null,age=Number.isFinite(e?.ageS)?e.ageS:Math.max(0,mapNowA()-(o.measuredAtS??mapNowA())),lines=[
    `상태: ${esmUiModeLabelA(o.esmState??e?.state)}`,
    `방위 ${Number.isFinite(o.bearingRad)?((o.bearingRad*180/Math.PI+450)%360).toFixed(1):'알 수 없음'}° ±${Number.isFinite(o.bearingSigmaDeg)?o.bearingSigmaDeg.toFixed(1):'알 수 없음'}°`,
    `대역: ${o.band??'보고 없음'} · 방사체 계열: ${o.emitterClass??o.type??'보고 없음'}`,
    `관측 나이: ${Number.isFinite(age)?age.toFixed(1):'알 수 없음'}s · 출처 ${e?.sourceCount??1}개`,
    `방법: ${e?.methods?.length?e.methods.join('+'):'AOA 방위만'}`
  ];
  if((o.esmState??e?.state)==='GEOLOCATED_ESTIMATE'||(o.esmState??e?.state)==='COAST'){
    const p=e?.positionM,ellipse=e?.ellipse95;
    if(p)lines.push(`추정 위치: ${p.x.toFixed(0)}, ${p.y.toFixed(0)} m (관측 기반)`);
    if(ellipse)lines.push(`95% 오차 타원: ${ellipse.major95M.toFixed(0)} × ${ellipse.minor95M.toFixed(0)} m`);
  }else lines.push('거리: 알 수 없음 · 점 표적 권한 없음');
  lines.push('식별: UNKNOWN · 자동 교전 권한 없음');
  return lines.join('\n');
}

function esmDrawEllipseA(context,mode,color,alpha,dashed=false){
  const center=esmUiWorldA(mode.centerM),ellipse=mode.ellipse95??esmUiEllipseA(mode.covarianceM2);if(!center||!ellipse)return;
  context.save();context.translate(center.x,center.y);context.rotate(ellipse.angleRad??0);
  context.strokeStyle=color.replace('__A__',String(alpha));context.fillStyle=color.replace('__A__',String(alpha*.10));
  context.lineWidth=tacticalLineWidthWorld(1.15,.48);context.setLineDash(dashed?[6,5]:[3,4]);
  context.beginPath();context.ellipse(0,0,metersToWorld(ellipse.major95M),metersToWorld(ellipse.minor95M),0,0,TAU);context.fill();context.stroke();context.restore();
}
function esmDrawRayA(context,mode,alpha,viewKm){
  const origin=esmUiWorldA(mode.originM);if(!origin)return;const r=kmToWorld(Math.min(viewKm,Math.max(.5,(mode.maxRangeM??90000)/1000))),sigma=mode.sigmaRad??deg(3),a=mode.bearingRad;
  context.fillStyle=`rgba(255,200,50,${(alpha*.08).toFixed(3)})`;context.beginPath();context.moveTo(origin.x,origin.y);context.arc(origin.x,origin.y,r,a-sigma,a+sigma);context.closePath();context.fill();
  context.strokeStyle=`rgba(255,215,75,${(alpha*.72).toFixed(3)})`;context.lineWidth=tacticalLineWidthWorld(1,.42);context.setLineDash([5,5]);context.beginPath();context.moveTo(origin.x,origin.y);context.lineTo(origin.x+Math.cos(a)*r,origin.y+Math.sin(a)*r);context.stroke();context.setLineDash([]);
}
function esmDrawChartA(context,contacts,viewKm,_tracks){
  for(const [id,c]of contacts){const e=c.estimate??null,state=c.state??e?.state;if(state==='LOST')continue;const age=Number.isFinite(e?.ageS)?e.ageS:c.age??0,alpha=clamp(.78-age*.025,.12,.78),modes=e?.modes??[];
    // Every retained line starts at its measurement-time receiver position.
    const history=(c.bearingHistory??[]).slice(-8);for(const q of history){const o=esmUiWorldA(q.originM);if(!o)continue;const r=kmToWorld(Math.min(viewKm,90)),a=q.bearingRad;context.strokeStyle=`rgba(255,210,60,${(alpha*.18).toFixed(3)})`;context.lineWidth=tacticalLineWidthWorld(.7,.3);context.setLineDash([2,6]);context.beginPath();context.moveTo(o.x,o.y);context.lineTo(o.x+Math.cos(a)*r,o.y+Math.sin(a)*r);context.stroke();context.setLineDash([]);}
    if(!modes.length){const origin=e?.latestOriginM??history.at(-1)?.originM;if(origin)esmDrawRayA(context,{kind:'RAY',originM:origin,bearingRad:c.bearing,sigmaRad:deg(c.bearingSigmaDeg??3),maxRangeM:90000},alpha,viewKm);}
    for(const mode of modes){if(mode.kind==='RAY')esmDrawRayA(context,mode,alpha,viewKm);else if(mode.kind==='ELLIPSE')esmDrawEllipseA(context,mode,state==='COAST'?'rgba(255,165,65,__A__)':'rgba(90,225,255,__A__)',alpha,state!=='GEOLOCATED_ESTIMATE');}
    const p=state==='GEOLOCATED_ESTIMATE'?esmUiWorldA(e?.positionM):null,origin=esmUiWorldA(e?.latestOriginM??history.at(-1)?.originM),anchor=p??(origin?{x:origin.x+Math.cos(c.bearing)*kmToWorld(Math.min(viewKm,90))*.86,y:origin.y+Math.sin(c.bearing)*kmToWorld(Math.min(viewKm,90))*.86}:null);if(!anchor)continue;
    if(p){context.fillStyle=`rgba(110,235,255,${alpha.toFixed(3)})`;context.beginPath();context.arc(p.x,p.y,tacticalWorldPx(3.1,4.2,2.7,4.2),0,TAU);context.fill();}
    context.font=`${tacticalFontWorldSize(7,4)}px system-ui`;context.textAlign='center';context.fillStyle=`rgba(255,225,105,${alpha.toFixed(3)})`;context.fillText(`ESM ${id} · ${esmUiModeLabelA(state)}`,anchor.x,anchor.y-screenPxToWorld(5));
    context.font=`${tacticalFontWorldSize(6,4)}px system-ui`;context.fillText(`${age.toFixed(1)}s · ${e?.sourceCount??1}src · ${e?.methods?.join('+')||'AOA'}`,anchor.x,anchor.y+screenPxToWorld(6));
  }
}

function esmDrawSelectionA(context,o,zoom,viewKm){
  const e=o.estimate??null,p=esmUiWorldA(e?.positionM),origin=o.originWorld??esmUiWorldA(e?.latestOriginM),r=16/zoom;
  context.save();context.strokeStyle='#e0d7aa';context.lineWidth=1/zoom;context.setLineDash([3/zoom,3/zoom]);
  if(p){context.beginPath();context.arc(p.x,p.y,r,0,TAU);context.stroke();}
  else if(origin){const d=kmToWorld(Math.min(viewKm,90))*.88,x=origin.x+Math.cos(o.bearingRad)*d,y=origin.y+Math.sin(o.bearingRad)*d;context.beginPath();context.arc(x,y,r,0,TAU);context.stroke();}
  context.restore();
}

function esmCueRouteCandidateA(c){
  const e=c?.estimate,fail=reason=>({ok:false,reason,truthUsed:false});if(!e||e.state!=='GEOLOCATED_ESTIMATE'||!e.positionM)return fail('ESM_SINGLE_MODE_GEOLOCATION_REQUIRED');
  if((e.modes?.length??0)!==1||e.modes[0].kind!=='ELLIPSE')return fail('ESM_AMBIGUOUS_LIKELIHOOD');
  const age=esmUiAgeA(c),cfg=HARPOON_PROFILE_A.sim;if(!Number.isFinite(age)||age>cfg.maxTrackAgeS)return fail('ESM_ESTIMATE_STALE');
  const ellipse=e.ellipse95??esmUiEllipseA(e.covarianceM2);if(!ellipse||ellipse.major95M>cfg.seekerSearchBasketM)return fail('ESM_AREA_EXCEEDS_TERMINAL_SEARCH_BASKET');
  const r=harpoonRuntimeA(),loaded=r.tubes.filter(t=>t.loaded);if(!r.tubes.length)return fail('MK141_NOT_INSTALLED');if(!loaded.length)return fail('TUBE_EMPTY');if(r.pending)return fail('RELEASE_PENDING');
  if(r.routeDraft.pointsM.length>=cfg.routeMaxPoints)return fail('WAYPOINT_LIMIT');
  let accepted=null;for(const tube of loaded){const spec=harpoonTubeSpecA(tube.id);if(!spec)continue;const muzzle=shipGameFrameV1().pointToWorld(spec.muzzle),prior=r.routeDraft.pointsM.at(-1)??muzzle,target=e.positionM,dx=target.x-prior.x,dy=target.y-prior.y,d=Math.hypot(dx,dy);if(!(d>cfg.routeSearchAheadM+cfg.routeMinLegM))continue;
    const final={x:target.x-dx/d*cfg.routeSearchAheadM,y:target.y-dy/d*cfg.routeSearchAheadM},points=[...r.routeDraft.pointsM.map(p=>({x:p.x,y:p.y})),final],program=harpoonRouteProgramE(points,muzzle);if(!program)continue;const gate=harpoonRouteGateE(null,tube.id,{routeProgram:program});if(gate.ok){accepted={tubeId:tube.id,program,gate,final};break;}if(!accepted)accepted={rejected:gate};}
  if(!accepted||!accepted.gate)return fail(accepted?.rejected?.reason??'INVALID_WAYPOINT_ROUTE');
  const kind=ellipse.major95M<=cfg.seekerSearchBasketM*.5?'ESM_ESTIMATED_POINT':'ESM_ESTIMATED_AREA';return {ok:true,reason:null,schema:ESM_A_CUE_SCHEMA,contactId:c.contactId,provenance:kind,estimateMeasuredAtS:e.measuredAtS,ageS:age,positionM:{x:e.positionM.x,y:e.positionM.y,z:0},covarianceM2:e.covarianceM2.slice(),ellipse95:{...ellipse},methods:[...e.methods],sourceCount:e.sourceCount,tubeId:accepted.tubeId,routeProgram:accepted.program,finalWaypointM:accepted.final,gate:accepted.gate,truthUsed:false,automaticAuthority:false};
}
function esmCueEvaluateA(contactId){return esmCueRouteCandidateA(esmUiContactA(contactId));}
function esmManualCueCommandA(contactId){
  const q=esmCueEvaluateA(contactId);if(!q.ok)return q;const r=harpoonRuntimeA(),wasEditing=harpoonRouteEditingE();if(!wasEditing&&!harpoonRouteToggleE())return {ok:false,reason:'ROUTE_EDIT_UNAVAILABLE',truthUsed:false};
  const add=harpoonRouteAddE(metersToWorld(q.finalWaypointM.x),metersToWorld(q.finalWaypointM.y));if(!add.ok){if(!wasEditing)harpoonRouteToggleE();return {...add,truthUsed:false};}
  const state=prepareEsmA(ACTIVE_SHIP_RUNTIME);state.manualCues??=[];state.manualCues.push({schema:q.schema,contactId:q.contactId,provenance:q.provenance,issuedAtS:simStepCounter*SIM_FIXED_DT,estimateMeasuredAtS:q.estimateMeasuredAtS,positionM:{...q.positionM},covarianceM2:q.covarianceM2.slice(),ellipse95:{...q.ellipse95},methods:q.methods.slice(),sourceCount:q.sourceCount,truthUsed:false,automaticAuthority:false});if(state.manualCues.length>16)state.manualCues.splice(0,state.manualCues.length-16);
  harpoonUpdateUIA();notify('ESM 추정 구역을 하푼 수동 탐색 경로로 지정');return {ok:true,count:add.count,provenance:q.provenance,routeProgram:q.routeProgram,truthUsed:false,automaticAuthority:false};
}

window.__ESM_A_UI__=Object.freeze({schema:'AEGIS_ESM_UI_A_1',evaluateCue:esmCueEvaluateA,manualCue:esmManualCueCommandA,presentation:id=>{const c=esmUiContactA(id);return c?esmPresentationCopyA(c):null;},snapshot:()=>({contacts:[...prepareElectronicF(ACTIVE_SHIP_RUNTIME).contacts.values()].map(esmPresentationCopyA),manualCues:esmJsonA(prepareEsmA(ACTIVE_SHIP_RUNTIME).manualCues??[]),truthUsed:false,automaticEngagementAuthority:false})});
