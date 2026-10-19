// PIP_A: one shared observer/own-equipment presentation frame, not a track manager.
// Legacy lazy display maintenance occurs once in this preparation phase, never in PiP paint.
let pipChartFrameA={ready:false,step:-1,tracks:new Map(),missiles:[],ramMissiles:[],esm:new Map(),terrain:[],helos:new Map(),network:[],rafts:[],cartridges:[],chaff:[],ciws:[],bullets:[],shells:[],nulka:[]};
const PIP_TRACK_FIELDS_A='trackId trackNumber domain classification identity confirmed x y z vx vy vz sensorAge sensorSource sensorDetected fireControlQuality kinematicQuality trackQuality reacquiring memActive memSigAlongKm memSigCrossKm memDir _memReason _kfNis'.split(' ');
const PIP_MISSILE_FIELDS_A='id ownerEntityId dead _illuminatorGuided sarhAlive assignedTargetId _illuminatorId x y velAngle sarhReceiverStandby terminalSARH state _sarhStableQ essmActiveSeeker seekerType irccmGateTimer _v1SarhState _sarhRawQ _v1ArhState irccmLastTargetAngle seekerAngle heading seekerFov irccmNarrowScale seekerScanFov _rangeKmCached seekerRangeKm isESSM seekerLocked tgtEstSrc coastTimer guidanceCore seekerLockType seekerLockId dlAlive'.split(' ');
function pipCopyFieldsA(source,keys){const out={};for(const k of keys)if(source?.[k]!==undefined)out[k]=source[k];return out;}
function pipOwnFilterA(q){return !q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId;}
function pipCopyMissileA(m){const q=pipCopyFieldsA(m,PIP_MISSILE_FIELDS_A);q._vlsInCell={active:!!m._vlsInCell?.active};for(const key of ['_arhRfSeeker','_sarhRfSeeker'])if(m[key])q[key]=pipCopyFieldsA(m[key],['mode','confidence','gateCenterRangeM','gateRangeHalfM']);if(m._v1ArhEstimate?.posM)q._v1ArhEstimate={posM:{x:m._v1ArhEstimate.posM.x,y:m._v1ArhEstimate.posM.y}};return q;}
function pipPrepareChartFrameA(){
 const frame={ready:true,step:simStepCounter,tracks:new Map(),missiles:missiles.filter(pipOwnFilterA).map(pipCopyMissileA),ramMissiles:ramMissiles.filter(pipOwnFilterA).map(m=>pipCopyFieldsA(m,['id','alive','x','y','vx','vy'])),esm:new Map(),terrain:[],helos:new Map(),network:[],rafts:[],cursor:{x:lockCursor.x,y:lockCursor.y},lockId:selectedLockId,hp:shipHP,radar:{rangeWorld:radar.rangeWorld,mode:radar.mode},shipNav:{heading:shipNav.heading,trail:shipNav.trail},spy:{beamHistory:spyScheduler.beamHistory.map(b=>pipCopyFieldsA(b,['ageS','holdS','type','rangeWorld','azHalfRad','ok','azWorld','trackId','elRad','code'])),faces:Object.fromEntries(Object.entries(spyScheduler.faces).map(([k,v])=>[k,pipCopyFieldsA(v,['load01','lastTask'])]))}};
 // Chart preparation preserves the existing one-per-main-frame cache lifecycle.
 for(const isl of terrainIslands)frame.terrain.push({...pipCopyFieldsA(isl,['id','kind','points','cx','cy','heightM']),chart:ensureTerrainChartProfile(isl)});
 const locked=selectedLockId!=null?tracks.get(selectedLockId):null;if(locked)trackIsFireControlQuality(locked);
 for(const[id,local]of tracks){const tr=networkPresentationTrackG(local),visible=trackIsDisplayable(tr),q=pipCopyFieldsA(tr,PIP_TRACK_FIELDS_A);q._chartVisible=visible;q._chartBda=wip121BdaTrackPresentation(tr);if(visible){q._chartUq=trackCovarianceMetrics(tr);q._kfP=tr._kfP?Array.from(tr._kfP):null;q.covarianceEllipse=tr.covarianceEllipse?{...tr.covarianceEllipse}:null;q.isarLabel=tr.isarEvidence?isarTrackLabelF2(tr):'';if(id===selectedLockId){frame.lockedLines=lockedTrackCardLines(tr,id,tr.classification==='SURFACE');q._chartReady=trackIsFireControlQuality(tr);q._chartArpaReady=!!bridgeMasterEArpaMetrics(tr)?.valid;}}if(tr._harpoonOwnC)q._harpoonOwnC=pipCopyFieldsA(tr._harpoonOwnC,['launchId','confirmed']);frame.tracks.set(id,q);}
 // Display eligibility above refreshes its own lazy covariance only, exactly once per main frame.
 for(const[id,c]of esmContacts)frame.esm.set(id,pipCopyFieldsA(c,['age','bearing','bearingSigmaDeg','type']));
 frame.network=ACTIVE_SHIP_RUNTIME.combatSystem.networkG?networkPictureG(ACTIVE_SHIP_RUNTIME):[];
 for(const inv of ACTIVE_SHIP_RUNTIME.aviation.inventory??[]){const h=heloWorldA().get(inv.id);if(!h||h.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId)continue;const q=pipCopyFieldsA(h,['id','slot','visible','state','onboard','headingRad','navigationMode','routeIndex']);q.positionM={...h.positionM};q.followPointM=h.followPointM?{...h.followPointM}:null;q.route=h.route.map(p=>({x:p.x,y:p.y}));q.chartRadar=heloRadarSnapshotE(h).radar;frame.helos.set(q.id,q);}
 frame.rafts=(ENGAGEMENT_RUNTIME.world.entities.lifeRafts??[]).filter(q=>q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId).map(q=>({positionM:{x:q.positionM.x,y:q.positionM.y},personIds:q.personIds.map(()=>null),capacityPersons:q.capacityPersons}));
 frame.cartridges=ownChaffCartridges.filter(pipOwnFilterA).map(q=>pipCopyFieldsA(q,['x','y','vx','vy']));frame.chaff=ownChaffs.filter(pipOwnFilterA).map(q=>pipCopyFieldsA(q,['life','maxLife','rcsM2','baseRcsM2','radiusM','x','y']));frame.nulka=nulkaEntities15B().filter(pipOwnFilterA).map(q=>pipCopyFieldsA(q,['x','y','payloadActive']));
 frame.ciws=ciws.map(cw=>({...pipCopyFieldsA(cw,['posOffsetM','type','arcCenter','arcHalf','firing','tracking','rangeKm','trackAng']),chartArcs:ciwsWorldArcSegmentsV1(cw)}));frame.bullets=ciwsBullets.filter(pipOwnFilterA).map(q=>pipCopyFieldsA(q,['x','y','vx','vy']));frame.shells=mainGunProjectilesWip13B3.filter(pipOwnFilterA).map(q=>({alive:q.alive,positionM:{x:q.positionM.x,y:q.positionM.y},velocityMps:{x:q.velocityMps.x,y:q.velocityMps.y}}));
 frame.harpoonDraft={pointsM:harpoonRuntimeA().routeDraft.pointsM.map(p=>({x:p.x,y:p.y}))};pipChartFrameA=frame;window.__MAP_A__?.preparePaint();updateTacticalScaleLabel();window.__PIP_A__?.prepared();
}
function drawRadar(view=null){
 if(!view){if(!pipChartFrameA.ready||pipChartFrameA.step!==simStepCounter)pipPrepareChartFrameA();view={target:'MAIN',context:canvas.getContext('2d'),rect:AEGIS_VIEWPORT.twoD,km:tacticalViewKm,center:{x:aircraft.x()+camOffset.x,y:aircraft.y()+camOffset.y}};}
 if(!pipChartFrameA.ready)return;
 const saved={ctx,render:pipRenderContextA,km:tacticalViewKm,zoom:mapZoom,panX:camOffset.x,panY:camOffset.y};
 try{ctx=view.context;pipRenderContextA=view;tacticalViewKm=view.km;camOffset.x=view.center.x-aircraft.x();camOffset.y=view.center.y-aircraft.y();vpUpdateMapZoomA();pipDrawRadarPixelsA();window.__PIP_A__?.painted(view.target,[...pipChartFrameA.tracks].filter(([,q])=>q._chartVisible).map(([id])=>id));}
 finally{ctx=saved.ctx;pipRenderContextA=saved.render;tacticalViewKm=saved.km;mapZoom=saved.zoom;camOffset.x=saved.panX;camOffset.y=saved.panY;}
}

function pipDrawTerrainA(ctx){
    for(const isl of pipChartFrameA.terrain){
      if(!isl.points?.length) continue;
      const prof=isl.chart;
      // very faint land tint so the player reads charted land, not literal terrain fill
      ctx.beginPath();
      ctx.moveTo(isl.points[0].x, isl.points[0].y);
      for(let i=1;i<isl.points.length;i++) ctx.lineTo(isl.points[i].x, isl.points[i].y);
      ctx.closePath();
      ctx.fillStyle = isl.kind==='MAJOR_LANDMASS' ? 'rgba(112,124,96,0.085)' : 'rgba(112,124,96,0.06)';
      ctx.fill();
      ctx.strokeStyle = 'rgba(184,210,176,0.62)';
      ctx.lineWidth = tacticalLineWidthWorld(1.15,0.45);
      ctx.stroke();

      // Relief-driven contours from marching-squares segments of the actual terrain field.
      if(mapZoom>0.24 && prof.contours?.length){
        const n=prof.contours.length;
        for(let li=0; li<n; li++){
          const contour=prof.contours[li], level=contour.level, segments=contour.segments;
          if(!segments?.length) continue;
          const t=(li+1)/(n+1);
          const alpha=(mapZoom>0.7?0.34:0.22) * (1-0.35*t);
          ctx.beginPath();
          for(const seg of segments){ctx.moveTo(seg.a.x,seg.a.y);ctx.lineTo(seg.b.x,seg.b.y);}
          ctx.strokeStyle = `rgba(165,196,155,${alpha.toFixed(3)})`;
          ctx.lineWidth = tacticalLineWidthWorld(li===n-1?0.9:0.7,0.30);
          ctx.lineJoin='round';ctx.lineCap='round';
          ctx.stroke();
          if(mapZoom>0.75 && (li===0 || li===n-1 || (n>4 && li===Math.floor(n*0.5)))){
            const seg=segments[(li*7+Math.floor(segments.length*0.23))%segments.length];
            const lx=(seg.a.x+seg.b.x)*0.5,ly=(seg.a.y+seg.b.y)*0.5;
            ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;
            ctx.fillStyle=`rgba(188,214,178,${Math.min(0.42,alpha+0.08).toFixed(3)})`;
            ctx.textAlign='left';
            ctx.fillText(String(level),lx+3,ly-1);
          }
        }
      }

      if(mapZoom>0.42 && prof.peaks.length){
        ctx.font=`${tacticalFontWorldSize(7,4)}px monospace`;
        ctx.fillStyle='rgba(205,228,196,0.48)';
        ctx.textAlign='center';
        for(const pk of prof.peaks){
          ctx.fillText('△', pk.x, pk.y+2);
          if(mapZoom>0.68) ctx.fillText(String(pk.h), pk.x, pk.y-4);
        }
      }

      if(mapZoom>0.95){
        ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;
        ctx.fillStyle='rgba(190,212,180,0.30)';
        ctx.textAlign='center';
        const label = isl.kind==='MAJOR_LANDMASS' ? `${isl.id} △${Math.round(isl.heightM)}m` : `${isl.id}`;
        ctx.fillText(label, isl.cx, isl.cy);
      }
    }
  }
function pipDrawNetworkA(){
  
  ctx.save();ctx.font=`${tacticalFontWorldSize(8,5)}px monospace`;ctx.lineWidth=tacticalLineWidthWorld(1.1,.45);ctx.textAlign='left';
  for(const q of pipChartFrameA.network){
    if(q.localTrackId!==null||!q.positionM)continue;const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y),friend=q.identity==='FRIEND',color=q.coasting?'rgba(145,165,180,.55)':friend?'rgba(90,220,245,.86)':'rgba(170,165,255,.86)',size=tacticalWorldPx(5,10,3,10);
    ctx.strokeStyle=color;ctx.fillStyle=color;ctx.setLineDash(q.coasting?[3,4]:[4,2]);ctx.strokeRect(x-size,y-size,size*2,size*2);ctx.setLineDash([]);
    const label=(friend?'ALLY':'NET '+q.id)+' '+q.ageS.toFixed(1)+'s'+(q.coasting?' COAST':' · 공유만');ctx.fillText(label,x+size+2,y-size-2);
    if(q.covariance){const rx=metersToWorld(2*Math.sqrt(q.covariance[0])),ry=metersToWorld(2*Math.sqrt(q.covariance[7]));if(rx>1&&ry>1){ctx.globalAlpha=.25;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,TAU);ctx.stroke();ctx.globalAlpha=1;}}
  }ctx.restore();
}
function pipDrawRaftsA(){
  const rows=pipChartFrameA.rafts;if(!rows.length)return;
  ctx.save();ctx.strokeStyle='#ffb458';ctx.fillStyle='#ffb458';ctx.lineWidth=tacticalLineWidthWorld(1.1,.5);
  const r=tacticalWorldPx(3,4,2.5,4),detail=currentTacticalViewKm()<=5;ctx.font=`${tacticalFontWorldSize(7,5)}px monospace`;ctx.textAlign='left';
  for(const q of rows){const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y);ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.stroke();
    ctx.beginPath();ctx.moveTo(x-r*.6,y);ctx.lineTo(x+r*.6,y);ctx.moveTo(x,y-r*.6);ctx.lineTo(x,y+r*.6);ctx.stroke();
    if(detail)ctx.fillText(`RAFT ${q.personIds.length}/${q.capacityPersons}`,x+r+2,y-r-2);
  }
  if(!detail){const x=rows.reduce((s,q)=>s+metersToWorld(q.positionM.x),0)/rows.length,y=rows.reduce((s,q)=>s+metersToWorld(q.positionM.y),0)/rows.length,people=rows.reduce((s,q)=>s+q.personIds.length,0);
    ctx.fillText(`RAFT ${rows.length} · ${people}명`,x+r+2,y-r-2);}
  ctx.restore();
}
function pipDrawHelosA(){
  for(const tr of pipChartFrameA.tracks.values())if(tr._chartVisible&&tr.isarLabel){ctx.save();ctx.font=`${tacticalFontWorldSize(10,6)}px monospace`;ctx.fillStyle="#e8cd90";ctx.fillText(tr.isarLabel,tr.x+tacticalWorldPx(9,15,5,15),tr.y+tacticalWorldPx(15,24,8,24));ctx.restore();}
  if(!pipChartFrameA.helos.size)return;ctx.save();ctx.strokeStyle='#7ae6da';ctx.fillStyle='#a9fff2';ctx.lineWidth=tacticalLineWidthWorld(1,.5);ctx.font=`${tacticalFontWorldSize(10,6)}px monospace`;
  const selected=pipChartFrameA.helos?.get(heloUiA.selectedId),radar=selected?selected.chartRadar:null;
  if(heloAirborneE(selected)&&radar){for(const[radius,dashed]of [[radar.instrumentM,false],[radar.horizonM,true],...(radar.mode==='PERI'?[[radar.minimumM,false]]:[])]){if(!(radius>0))continue;ctx.globalAlpha=dashed?.4:.6;ctx.setLineDash(dashed?[tacticalWorldPx(5,8,2,8),tacticalWorldPx(5,8,2,8)]:[]);ctx.beginPath();ctx.arc(metersToWorld(selected.positionM.x),metersToWorld(selected.positionM.y),metersToWorld(radius),0,2*Math.PI);ctx.stroke();}ctx.setLineDash([]);ctx.globalAlpha=1;}
  for(const h of pipChartFrameA.helos?.values()??[]){if(!h.visible&&h.id!==heloUiA.selectedId)continue;const x=metersToWorld(h.positionM.x),y=metersToWorld(h.positionM.y),r=tacticalWorldPx(6,12,3,12),points=h.navigationMode==='FOLLOW_SHIP'?(h.followPointM?[h.followPointM]:[]):h.route.slice(h.routeIndex);
    if(points.length){ctx.globalAlpha=.55;ctx.setLineDash([r,r]);ctx.beginPath();ctx.moveTo(x,y);for(const p of points)ctx.lineTo(metersToWorld(p.x),metersToWorld(p.y));ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;points.forEach((p,i)=>{const px=metersToWorld(p.x),py=metersToWorld(p.y);ctx.strokeRect(px-r,py-r,r*2,r*2);ctx.fillText(h.navigationMode==='FOLLOW_SHIP'?'FOLLOW H'+(h.slot+1):'H'+(h.slot+1)+' WP'+(h.routeIndex+i+1),px+r*1.5,py);});}
    ctx.save();ctx.translate(x,y);ctx.rotate(h.headingRad);ctx.beginPath();ctx.moveTo(r*1.5,0);ctx.lineTo(-r,r*.75);ctx.lineTo(-r,-r*.75);ctx.closePath();ctx.stroke();ctx.beginPath();ctx.arc(0,0,r*.65,0,2*Math.PI);ctx.stroke();ctx.restore();ctx.fillText('H'+(h.slot+1)+' '+HELO_LABELS_A[h.state],x+r*1.8,y-r);
  }ctx.restore();
}
function pipDrawHarpoonA(ctx,sym){
  const draft=pipChartFrameA.harpoonDraft;if(!draft.pointsM.length)return;
  const cfg=HARPOON_PROFILE_A.sim,origin={x:aircraft.x(),y:aircraft.y()},program=harpoonRouteProgramE(draft.pointsM,{x:worldToMeters(origin.x),y:worldToMeters(origin.y)});
  ctx.save();ctx.strokeStyle='#ffbf67';ctx.fillStyle='#ffda9a';ctx.lineWidth=tacticalLineWidthWorld(1.5,.42);ctx.setLineDash([7*sym,5*sym]);
  ctx.beginPath();ctx.moveTo(origin.x,origin.y);for(const p of draft.pointsM)ctx.lineTo(metersToWorld(p.x),metersToWorld(p.y));ctx.stroke();ctx.setLineDash([]);
  ctx.font=(10*sym)+'px monospace';ctx.textAlign='left';ctx.textBaseline='bottom';
  draft.pointsM.forEach((p,i)=>{const x=metersToWorld(p.x),y=metersToWorld(p.y);ctx.beginPath();ctx.arc(x,y,4*sym,0,Math.PI*2);ctx.stroke();ctx.fillText('H-WP'+(i+1)+(i===draft.pointsM.length-1?' · SEARCH':''),x+7*sym,y-5*sym);});
  if(program){const p=program.searchCenterM;ctx.globalAlpha=.45;ctx.setLineDash([4*sym,4*sym]);ctx.beginPath();ctx.arc(metersToWorld(p.x),metersToWorld(p.y),metersToWorld(cfg.seekerSearchBasketM),0,Math.PI*2);ctx.stroke();}
  ctx.restore();
}
function pipDrawLockedCardA(c,tr,id,drawX,drawY,isSURFACE,col,rw,rh){
    const lines=pipChartFrameA.lockedLines??[];
    const font=tacticalFontWorldSize(8,5.2);
    const headerFont=tacticalFontWorldSize(8.4,5.4);
    const pad=tacticalWorldPx(4.5,6.0,4.2,6.0);
    const lineH=tacticalWorldPx(9.5,12.0,9.0,12.0);
    const gap=tacticalWorldPx(12,18,10,18);
    const margin=tacticalWorldPx(7,10,6,10);
    c.save();
    c.font=`${font}px system-ui`;
    let textW=0;
    for(let i=1;i<lines.length;i++) textW=Math.max(textW,c.measureText(lines[i]).width);
    c.font=`600 ${headerFont}px system-ui`;
    textW=Math.max(textW,c.measureText(lines[0]).width);
    const boxW=textW+pad*2;
    const boxH=lineH*lines.length+pad*1.45;
    const b=tacticalViewportWorldBounds(rw,rh);
    let bx=drawX+gap;
    if(bx+boxW>b.maxX-margin) bx=drawX-gap-boxW;
    bx=clamp(bx,b.minX+margin,b.maxX-margin-boxW);
    let by=drawY-boxH*0.42;
    by=clamp(by,b.minY+margin,b.maxY-margin-boxH);
    const edgeX=bx>drawX?bx:bx+boxW;
    const edgeY=clamp(drawY,by+pad,by+boxH-pad);
    c.strokeStyle='rgba(180,215,225,0.34)';
    c.lineWidth=tacticalLineWidthWorld(0.9,0.42);
    c.setLineDash([tacticalWorldPx(2.5,4,2.2,4),tacticalWorldPx(2.5,4,2.2,4)]);
    c.beginPath();c.moveTo(drawX,drawY);c.lineTo(edgeX,edgeY);c.stroke();c.setLineDash([]);
    c.fillStyle='rgba(2,10,16,0.84)';c.fillRect(bx,by,boxW,boxH);
    c.strokeStyle='rgba(150,205,220,0.40)';c.lineWidth=tacticalLineWidthWorld(1.0,0.45);c.strokeRect(bx,by,boxW,boxH);
    const fcReady=!isSURFACE&&tr._chartReady;
    const arpaReady=isSURFACE&&!!tr._chartArpaReady;
    c.fillStyle=isSURFACE?'rgba(80,190,220,0.13)':(fcReady?'rgba(90,220,155,0.18)':'rgba(220,185,80,0.14)');
    c.fillRect(bx,by,boxW,lineH+pad*0.35);
    c.font=`600 ${headerFont}px system-ui`;c.textAlign='left';
    c.fillStyle=isSURFACE?(arpaReady?'rgba(130,235,255,0.96)':'rgba(120,205,225,0.90)'):(fcReady?'rgba(150,255,195,0.96)':col);
    c.fillText(lines[0],bx+pad,by+pad+headerFont*0.55);
    c.font=`${font}px system-ui`;c.fillStyle='rgba(224,238,242,0.90)';
    for(let i=1;i<lines.length;i++) c.fillText(lines[i],bx+pad,by+pad+lineH*i+font*0.4);
    c.restore();
  }
