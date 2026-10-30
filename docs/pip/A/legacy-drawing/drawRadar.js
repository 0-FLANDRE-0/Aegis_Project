function drawRadar(){
    vpUpdateMapZoomA();const raw=AEGIS_VIEWPORT.raw,vp=AEGIS_VIEWPORT.twoD,rw=raw.w,rh=raw.h;
    ctx.fillStyle = '#030a10';
    ctx.fillRect(raw.x,raw.y,rw,rh);

    // Apply camera pan + zoom
    ctx.save();
    ctx.beginPath();ctx.rect(vp.x,vp.y,vp.w,vp.h);ctx.clip();
    const origin=worldToScreen(0,0);ctx.translate(origin.x,origin.y);ctx.scale(mapZoom,mapZoom);
    const ax = aircraft.x(), ay = aircraft.y();
    const sym = tacticalSymbolWorldScale();
    const viewKm = currentTacticalViewKm();
    updateTacticalScaleLabel();

    // 360° PPI Radar circle
    ctx.save();
    ctx.translate(ax,ay);

    // Tactical map background (full extent)
    ctx.beginPath();
    ctx.arc(0,0, radar.rangeWorld, 0, TAU);
    ctx.fillStyle = 'rgba(2, 8, 16, 0.5)';
    ctx.fill();

    // Sensor detection range circle (distinct from map extent)
    const sensorWorld = kmToWorld(SPY1DV_SEARCH_MAX_RANGE_KM);
    ctx.strokeStyle = 'rgba(0,255,120,0.15)';
    ctx.lineWidth = tacticalLineWidthWorld(1.0,0.45);
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.arc(0,0, sensorWorld, 0, TAU);
    ctx.stroke();
    ctx.setLineDash([]);

    // Map extent border
    ctx.strokeStyle = 'rgba(0,120,255,0.12)';
    ctx.lineWidth = tacticalLineWidthWorld(0.8,0.38);
    ctx.beginPath();
    ctx.arc(0,0, radar.rangeWorld, 0, TAU);
    ctx.stroke();

    // Range rings (full circles)
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = tacticalLineWidthWorld(0.8,0.38);
    // Adaptive range ring step based on current view
    const ringStep = (viewKm <= 20) ? 5 : (viewKm <= 50) ? 10 : (viewKm <= 150) ? 20 : 50;
    const maxRing = Math.min(RADAR_MAX_KM, viewKm * 1.5);
    for(let r=ringStep; r<=maxRing; r+=ringStep){
      const rr = kmToWorld(r);
      ctx.beginPath();
      ctx.arc(0,0, rr, 0, TAU);
      ctx.stroke();
      // Range label
      ctx.font = `${tacticalFontWorldSize(8,5)}px system-ui`;
      ctx.fillStyle = 'rgba(255,255,255,0.2)';
      ctx.textAlign = 'center';
      ctx.fillText(r+'', 0, -rr - 3);
    }

    // Compass lines (N/S/E/W) — fixed true north
    const compassR = Math.max(radar.rangeWorld, 400);
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = tacticalLineWidthWorld(0.5,0.28);
    for(let a=0; a<4; a++){
      const ang = a * Math.PI/2 - Math.PI/2;
      ctx.beginPath();
      ctx.moveTo(0,0);
      ctx.lineTo(Math.cos(ang)*compassR, Math.sin(ang)*compassR);
      ctx.stroke();
    }
    // Compass labels (fixed position, not rotating)
    ctx.font = `${tacticalFontWorldSize(10,6)}px system-ui`;
    ctx.fillStyle = 'rgba(0,255,120,0.35)';
    const cLabelR = compassR + 8;
    ctx.textAlign = 'center';
    ctx.fillText('N', 0, -cLabelR);
    ctx.fillText('S', 0, cLabelR + 10);
    ctx.textAlign = 'left';
    ctx.fillText('E', cLabelR + 2, 4);
    ctx.textAlign = 'right';
    ctx.fillText('W', -cLabelR - 2, 4);

    // ===== SELECTED SHIP SPY 4-FACE PESA RADAR VISUALIZATION =====
    if(emconActive){
      // EMCON ON: no radar visualization, just dark circle
      ctx.strokeStyle = 'rgba(80,80,80,0.15)';
      ctx.lineWidth = tacticalLineWidthWorld(1.0,0.45);
      ctx.setLineDash([6,8]);
      ctx.beginPath();
      ctx.arc(0,0, radar.rangeWorld, 0, TAU);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = `${tacticalFontWorldSize(9,5)}px system-ui`;
      ctx.fillStyle = 'rgba(255,80,80,0.4)';
      ctx.textAlign = 'center';
      ctx.fillText('EMCON — RADAR OFF', 0, -radar.rangeWorld - 14);
    } else {
    // Selected physical face centres also own boundaries, load arcs and labels.
    const FACE_COLORS = [
      'rgba(0,255,120,',   // Face 1: N (green)
      'rgba(80,180,255,',  // Face 2: E (blue)
      'rgba(255,200,60,',  // Face 3: S (yellow)
      'rgba(255,100,180,', // Face 4: W (pink)
    ];
    const faceAngles = spyCicFaceLayoutK().map(q=>q.angleRad);
    const faceHalf = Math.PI/4;

    // Draw face sector boundaries (subtle)
    for(let f=0; f<4; f++){
      const a1 = faceAngles[f] - faceHalf;
      const a2 = faceAngles[f] + faceHalf;
      ctx.strokeStyle = FACE_COLORS[f] + '0.12)';
      ctx.lineWidth = tacticalLineWidthWorld(0.5,0.28);
      ctx.beginPath();
      ctx.moveTo(0,0);
      ctx.lineTo(Math.cos(a1)*radar.rangeWorld, Math.sin(a1)*radar.rangeWorld);
      ctx.stroke();
    }

    // WIP9: draw ONLY beam dwells actually executed by the SPY scheduler.
    // Persistence makes many recent electronic scans visible at once, but they are not fake concurrent beams.
    const SPY1DV_BEAM_VIS_ALPHA_SCALE = 0.78; // WIP11: slightly dimmer scheduler beam phosphor
    const TASK_RGB = {
      SEARCH_VOLUME:'80,230,180', SEARCH_HORIZON:'80,210,255', TRACK_REVISIT:'120,255,150',
      TRACK_CONFIRM:'255,210,80', TRACK_REACQUIRE:'255,145,70', SURFACE_TRACK:'70,235,210', SURFACE_CONFIRM:'125,255,225', SURFACE_REACQUIRE:'255,180,75', HIGH_THREAT:'255,90,70', MISSILE_SUPPORT:'255,100,235', SPG_HANDOFF:'255,195,90', PRECISION_LOCK:'255,245,160', PRECISION_REACQUIRE:'255,165,95'
    };
    for(const beam of spyScheduler.beamHistory){
      const life=clamp(1-(beam.ageS??0)/Math.max(0.05,beam.holdS??0.5),0,1);
      if(life<=0) continue;
      const rgb=TASK_RGB[beam.type]||'150,220,255';
      const rr=Math.min(beam.rangeWorld??sensorWorld,sensorWorld);
      const half=clamp(beam.azHalfRad??deg(1),deg(0.25),beam.type==='PRECISION_REACQUIRE'?deg(10):deg(4.5));
      const isSearch=beam.type==='SEARCH_VOLUME'||beam.type==='SEARCH_HORIZON';
      const strong=beam.type==='PRECISION_LOCK'||beam.type==='PRECISION_REACQUIRE'||beam.type==='MISSILE_SUPPORT'||beam.type==='HIGH_THREAT';
      const alpha=(beam.ok?1.0:0.62)*life;

      // Beam footprint/fan. Very low alpha is intentional: overlapping real dwells build phosphor-like density.
      ctx.fillStyle=`rgba(${rgb},${(alpha*SPY1DV_BEAM_VIS_ALPHA_SCALE*(isSearch?0.025:0.038)).toFixed(3)})`;
      ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,rr,beam.azWorld-half,beam.azWorld+half);ctx.closePath();ctx.fill();

      ctx.strokeStyle=`rgba(${rgb},${(alpha*SPY1DV_BEAM_VIS_ALPHA_SCALE*(strong?0.72:(isSearch?0.24:0.46))).toFixed(3)})`;
      ctx.lineWidth=strong?tacticalLineWidthWorld(1.45,0.60):(isSearch?tacticalLineWidthWorld(0.55,0.24):tacticalLineWidthWorld(0.9,0.38));
      if(!beam.ok&&!isSearch) ctx.setLineDash([3,4]);
      ctx.beginPath();ctx.moveTo(Math.cos(beam.azWorld)*Math.min(rr,kmToWorld(2)),Math.sin(beam.azWorld)*Math.min(rr,kmToWorld(2)));
      ctx.lineTo(Math.cos(beam.azWorld)*rr,Math.sin(beam.azWorld)*rr);ctx.stroke();ctx.setLineDash([]);

      // Dwell endpoint / track pinprick.
      const ex=Math.cos(beam.azWorld)*rr,ey=Math.sin(beam.azWorld)*rr;
      ctx.fillStyle=`rgba(${rgb},${(alpha*SPY1DV_BEAM_VIS_ALPHA_SCALE*(strong?0.85:0.42)).toFixed(3)})`;
      ctx.beginPath();ctx.arc(ex,ey,strong?tacticalWorldPx(1.4,2.8,1.1,2.8):tacticalWorldPx(0.9,1.6,0.8,1.6),0,TAU);ctx.fill();
      if((beam.ageS??1)<0.13){
        ctx.font=`${tacticalFontWorldSize(6,4)}px monospace`;ctx.textAlign='center';ctx.fillStyle=`rgba(${rgb},${(alpha*SPY1DV_BEAM_VIS_ALPHA_SCALE*0.88).toFixed(3)})`;
        const tid=beam.trackId!=null?` ${trackTruthDomainV27(beam.trackId)??'TRACK'}:${tracks.get(beam.trackId)?.trackNumber??beam.trackId}`:'';
        const el=`${beam.elRad>=0?'+':''}${Math.round(beam.elRad*180/Math.PI)}°`;
        ctx.fillText(`${beam.code}${tid} ${el}`,Math.cos(beam.azWorld)*rr*0.78,Math.sin(beam.azWorld)*rr*0.78-3);
      }
    }

    // Inner face-load arcs: scheduler utilization by array face, not radar detection truth.
    const loadR=Math.min(sensorWorld*0.11,kmToWorld(12));
    for(let f=0;f<4;f++){
      const face=SPY1DV_FACE_KEYS[f],fs=spyScheduler.faces[face],alive=spyFaceHealth01(face)>0;
      const a1=faceAngles[f]-faceHalf+deg(3),span=faceHalf*2-deg(6);
      ctx.strokeStyle=alive?(FACE_COLORS[f]+'0.13)'):'rgba(255,60,60,0.20)';ctx.lineWidth=tacticalLineWidthWorld(3.5,1.4);
      ctx.beginPath();ctx.arc(0,0,loadR,a1,a1+span);ctx.stroke();
      if(alive&&fs){
        ctx.strokeStyle=FACE_COLORS[f]+`${(0.28+0.52*fs.load01).toFixed(2)})`;ctx.lineWidth=tacticalLineWidthWorld(3.5,1.4);
        ctx.beginPath();ctx.arc(0,0,loadR,a1,a1+span*clamp(fs.load01,0,1));ctx.stroke();
      }
    }

    // Face labels: live scheduler load / health / last task.
    ctx.font = `${tacticalFontWorldSize(6,4)}px monospace`;
    for(let f=0; f<4; f++){
      const face=SPY1DV_FACE_KEYS[f],fs=spyScheduler.faces[face],health=spyFaceHealth01(face);
      const labelR = Math.min(sensorWorld * 0.17, kmToWorld(18));
      const lx = Math.cos(faceAngles[f]) * labelR;
      const ly = Math.sin(faceAngles[f]) * labelR;
      ctx.fillStyle = health>0 ? (FACE_COLORS[f] + '0.70)') : 'rgba(255,70,70,0.75)';
      ctx.textAlign = 'center';
      ctx.fillText(`${face} ${health>0?Math.round((fs?.load01??0)*100)+'%':'OFF'}`, lx, ly);
      ctx.font='5px monospace';
      ctx.fillText(`${health>0?'H'+Math.round(health*100):'ARRAY FAIL'} ${SPY1DV_TASK_CODE[fs?.lastTask]??'-'}`,lx,ly+7);
      ctx.font='6px monospace';
    }
    // ===== BridgeMaster E MECHANICAL 2-D SURFACE-SEARCH SWEEP =====
    if(!emconActive&&bridgeMasterEHealth01()>.08){
      const sweepAng=shipNav.heading+bridgeMasterERotorAngle;
      const sweepR=Math.min(kmToWorld(BRIDGEMASTER_E_DISPLAY_SCALE_MAX_KM),radar.rangeWorld*0.95);
      ctx.strokeStyle='rgba(105,255,175,0.18)';ctx.lineWidth=tacticalLineWidthWorld(0.75,0.30);
      ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(sweepAng)*sweepR,Math.sin(sweepAng)*sweepR);ctx.stroke();
      ctx.fillStyle='rgba(105,255,175,0.012)';ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,sweepR,sweepAng-BRIDGEMASTER_E_BEAM_AZ_HALF,sweepAng+BRIDGEMASTER_E_BEAM_AZ_HALF);ctx.closePath();ctx.fill();
      for(let i=1;i<=5;i++){
        const a=sweepAng-deg(18)*i/5,alpha=0.045*(1-i/5);
        ctx.strokeStyle=`rgba(105,255,175,${alpha.toFixed(3)})`;ctx.lineWidth=tacticalLineWidthWorld(0.35,0.22);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(a)*sweepR,Math.sin(a)*sweepR);ctx.stroke();
      }
    }
    // ===== AN/SPQ-9B DUAL BACK-TO-BACK ROTATING PLANAR ARRAYS =====
    if(!emconActive&&spq9bHealth01()>.08){
      const sweepR = kmToWorld(SPQ9B_SEARCH_MAX_RANGE_KM);
      const clampR = Math.min(sweepR, radar.rangeWorld * 0.95);
      for(let panel=0;panel<SPQ9B_PANEL_COUNT;panel++){
        const sweepAng = shipNav.heading + spq9bRotorAngle + panel*SPQ9B_PANEL_SEPARATION_RAD;
        const panelAlpha = panel===0 ? 0.24 : 0.19;
        // Narrow X-band horizon beam. Two lines 180° apart are real back-to-back arrays.
        ctx.strokeStyle = `rgba(0,205,255,${panelAlpha})`;
        ctx.lineWidth = tacticalLineWidthWorld(0.9,0.36);
        ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(sweepAng)*clampR,Math.sin(sweepAng)*clampR);ctx.stroke();
        const fanHalf=SPQ9B_BEAM_AZ_HALF;
        ctx.fillStyle=`rgba(0,205,255,${panel===0?'0.020':'0.016'})`;
        ctx.beginPath();ctx.moveTo(0,0);ctx.arc(0,0,clampR,sweepAng-fanHalf,sweepAng+fanHalf);ctx.closePath();ctx.fill();

        // Short phosphor trail behind each physical panel.
        const trailSpan=deg(16),trailSteps=6;
        for(let i=1;i<=trailSteps;i++){
          const tAng=sweepAng-trailSpan*i/trailSteps;
          const a=0.075*(1-i/trailSteps);
          ctx.strokeStyle=`rgba(0,205,255,${a.toFixed(3)})`;ctx.lineWidth=tacticalLineWidthWorld(0.45,0.22);
          ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(Math.cos(tAng)*clampR,Math.sin(tAng)*clampR);ctx.stroke();
        }
        ctx.fillStyle='rgba(0,220,255,0.24)';ctx.beginPath();ctx.arc(Math.cos(sweepAng)*clampR,Math.sin(sweepAng)*clampR,1.7,0,TAU);ctx.fill();
      }
    }    // ===== ILLUMINATOR BEAMS (when active) =====
    {
      // WIP92: render one beam per physical target engagement, not once per missile sharing it.
      const drawnIlluminations = new Set();
      if(!emconActive) for(const m of missiles){
        if(m.dead || !m._illuminatorGuided || !m.sarhAlive || m.assignedTargetId==null || m._illuminatorId==null) continue;
        const key=`${m.assignedTargetId}:${m._illuminatorId}`;
        if(drawnIlluminations.has(key)) continue;
        drawnIlluminations.add(key);
        const tr = tracks.get(m.assignedTargetId);
        if(!tr) continue;
        const dx = tr.x - ax, dy = tr.y - ay;
        const r = Math.min(Math.hypot(dx, dy), radar.rangeWorld);
        const a = Math.atan2(dy, dx);
        ctx.strokeStyle = 'rgba(255,180,40,0.35)';
        ctx.lineWidth = tacticalLineWidthWorld(1.5,0.55);
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(255,180,40,0.5)';
        ctx.font = '6px system-ui';
        ctx.textAlign = 'center';
        ctx.fillText(`ILL-${m._illuminatorId+1}`, Math.cos(a) * r * 0.3, Math.sin(a) * r * 0.3 + 3);
      }
    }

    } // end EMCON else

    ctx.restore();

    // ===== WIP26-UI1 CHART-STYLE TERRAIN =====
    // Display charted coastline/relief cues instead of a solid literal landmass fill.
    drawTerrainChartLayer(ctx);

    // BridgeMaster E navigation video: short-lived sampled shoreline returns from the mechanical sweep.
    if(!emconActive&&bridgeMasterEShoreEchoes.length){
      for(const e of bridgeMasterEShoreEchoes){const a=clamp((e.life/1.7)*(e.strength??1)*0.55,0,0.55);ctx.fillStyle=`rgba(110,255,180,${a.toFixed(3)})`;ctx.beginPath();ctx.arc(e.x,e.y,1.3*sym,0,TAU);ctx.fill();}
    }

    drawRescueRaftsCicK();drawNetworkPictureG();heloDrawMapA();window.__MAP_A__?.draw(ctx);

    // Ship trail
    if(shipNav.trail.length > 1){
      ctx.strokeStyle = 'rgba(56,180,140,0.22)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for(let i=0;i<shipNav.trail.length;i++){
        if(i===0) ctx.moveTo(shipNav.trail[i].x, shipNav.trail[i].y);
        else ctx.lineTo(shipNav.trail[i].x, shipNav.trail[i].y);
      }
      ctx.stroke();
    }

    // Ship heading line
    {
      const hlLen = 20;
      const hx = Math.cos(shipNav.heading) * hlLen;
      const hy = Math.sin(shipNav.heading) * hlLen;
      ctx.strokeStyle = 'rgba(212,160,23,0.55)';
      ctx.lineWidth = tacticalLineWidthWorld(1.2,0.50);
      ctx.setLineDash([3,4]);
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(ax + hx, ay + hy);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // ===== Waypoint Route =====
    if(routePoints.length > 0){
      // Draw route lines
      ctx.strokeStyle = 'rgba(80,255,200,0.35)';
      ctx.lineWidth = tacticalLineWidthWorld(1.2,0.50);
      ctx.setLineDash([5,5]);
      ctx.beginPath();
      ctx.moveTo(ax, ay); // start from ship
      for(let wi=0; wi<routePoints.length; wi++){
        ctx.lineTo(routePoints[wi].x, routePoints[wi].y);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw waypoint markers
      for(let wi=0; wi<routePoints.length; wi++){
        const wp = routePoints[wi];
        const isActive = (wi === activeWpIdx && activeWpIdx < routePoints.length);
        const isPassed = (wi < activeWpIdx);
        const isLast = (wi === routePoints.length - 1);

        // Marker circle
        ctx.beginPath();
        const wr = (isActive ? 5 : 3.5) * sym;
        ctx.arc(wp.x, wp.y, wr, 0, TAU);
        if(isPassed){
          ctx.strokeStyle = 'rgba(80,255,200,0.15)';
          ctx.fillStyle = 'rgba(80,255,200,0.05)';
        } else if(isActive){
          ctx.strokeStyle = 'rgba(80,255,200,0.8)';
          ctx.fillStyle = 'rgba(80,255,200,0.15)';
        } else {
          ctx.strokeStyle = 'rgba(80,255,200,0.4)';
          ctx.fillStyle = 'rgba(80,255,200,0.05)';
        }
        ctx.lineWidth = isActive ? tacticalLineWidthWorld(1.5,0.60) : tacticalLineWidthWorld(1.0,0.45);
        ctx.fill();
        ctx.stroke();

        // Final destination: extra ring
        if(isLast && !isPassed){
          ctx.beginPath();
          ctx.arc(wp.x, wp.y, 8*sym, 0, TAU);
          ctx.strokeStyle = 'rgba(80,255,200,0.25)';
          ctx.lineWidth = tacticalLineWidthWorld(0.8,0.35);
          ctx.stroke();
        }

        // WP number label
        ctx.font = `${tacticalFontWorldSize(7,4)}px system-ui`;
        ctx.fillStyle = isPassed ? 'rgba(80,255,200,0.2)' : 'rgba(80,255,200,0.6)';
        ctx.textAlign = 'left';
        ctx.fillText((wi+1) + '', wp.x + (isActive ? 7 : 5)*sym, wp.y - 3*sym);
      }
    }

    // ===== Navigation Objective (legacy fallback) =====
    {
      const navX = navObjective.x, navY = navObjective.y;
      const ndKm = worldToKm(dist(ax, ay, navX, navY));
      if(!navObjective.reached && routePoints.length === 0){
        const nr = kmToWorld(navObjective.radiusKm);
        ctx.strokeStyle = 'rgba(80,255,200,0.4)';
        ctx.lineWidth = tacticalLineWidthWorld(1.5,0.55);
        ctx.setLineDash([6,4]);
        ctx.beginPath();
        ctx.arc(navX, navY, nr, 0, TAU);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.moveTo(navX - 6, navY); ctx.lineTo(navX + 6, navY);
        ctx.moveTo(navX, navY - 6); ctx.lineTo(navX, navY + 6);
        ctx.stroke();
        ctx.font = `${tacticalFontWorldSize(8,5)}px system-ui`;
        ctx.fillStyle = 'rgba(80,255,200,0.7)';
        ctx.textAlign = 'center';
        ctx.fillText(`OBJ ${ndKm.toFixed(0)}km`, navX, navY - 10);
      } else {
        ctx.fillStyle = 'rgba(80,255,200,0.5)';
        ctx.font = `${tacticalFontWorldSize(9,5)}px system-ui`;
        ctx.textAlign = 'center';
        ctx.fillText('✓ 도달', navX, navY + 4);
      }
    }

    // ===== ESM Contacts (bearing-only passive display) =====
    for(const [id,c] of esmContacts){
      const alpha=clamp(0.72-c.age*0.02,0.12,0.72), sigma=deg(c.bearingSigmaDeg??3);
      const rayKm=Math.min(viewKm,90);
      const rayR=kmToWorld(rayKm), a0=c.bearing-sigma, a1=c.bearing+sigma;
      ctx.fillStyle=`rgba(255,200,50,${alpha*0.08})`;
      ctx.beginPath();ctx.moveTo(ax,ay);ctx.arc(ax,ay,rayR,a0,a1);ctx.closePath();ctx.fill();
      ctx.strokeStyle=`rgba(255,210,60,${alpha*0.65})`;ctx.lineWidth=tacticalLineWidthWorld(1.0,0.42);ctx.setLineDash([5,5]);
      ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(ax+Math.cos(c.bearing)*rayR,ay+Math.sin(c.bearing)*rayR);ctx.stroke();ctx.setLineDash([]);
      const lx=ax+Math.cos(c.bearing)*rayR*0.88,ly=ay+Math.sin(c.bearing)*rayR*0.88;
      ctx.font=`${tacticalFontWorldSize(7,4)}px system-ui`;ctx.fillStyle=`rgba(255,220,80,${alpha})`;ctx.textAlign='center';
      const assoc=tracks.get(id); const suffix=assoc&&trackIsDisplayable(assoc)?` / T${id}`:'';
      ctx.fillText(`ESM ${c.type}${suffix}`,lx,ly-4);
      ctx.font=`${tacticalFontWorldSize(6,4)}px system-ui`;ctx.fillText(`BRG ${String(Math.round(((c.bearing*180/Math.PI)+450)%360)).padStart(3,'0')}° ±${(c.bearingSigmaDeg??3).toFixed(1)}°`,lx,ly+6);
    }

    // ===== Mk 36 SRBOC / Mk 214 cartridges + physical chaff clouds =====
    for(const q of ownChaffCartridges.filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){
      ctx.fillStyle='rgba(235,235,255,0.9)';ctx.beginPath();ctx.arc(q.x,q.y,tacticalWorldPx(1.0,2.2,0.9,2.2),0,TAU);ctx.fill();
      ctx.strokeStyle='rgba(200,210,255,0.35)';ctx.lineWidth=tacticalLineWidthWorld(1.0,0.42);ctx.beginPath();ctx.moveTo(q.x,q.y);ctx.lineTo(q.x-(q.vx??0)*0.08,q.y-(q.vy??0)*0.08);ctx.stroke();
    }
    for(const oc of ownChaffs.filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){
      const lifeA=clamp(1-oc.life/oc.maxLife,0,1),rfA=clamp((oc.rcsM2??0)/Math.max(1,oc.baseRcsM2??1),0,1),a=lifeA*(0.35+0.65*rfA);
      const rr=metersToWorld(Math.max(8,oc.radiusM??60));
      const g=ctx.createRadialGradient(oc.x,oc.y,0,oc.x,oc.y,rr);g.addColorStop(0,`rgba(205,205,255,${0.22*a})`);g.addColorStop(0.55,`rgba(180,185,255,${0.10*a})`);g.addColorStop(1,'rgba(160,170,255,0)');
      ctx.fillStyle=g;ctx.beginPath();ctx.arc(oc.x,oc.y,rr,0,TAU);ctx.fill();
      if((oc.rcsM2??0)>300){ctx.strokeStyle=`rgba(190,200,255,${0.22*a})`;ctx.setLineDash([3,4]);ctx.beginPath();ctx.arc(oc.x,oc.y,rr,0,TAU);ctx.stroke();ctx.setLineDash([]);}
    }

    // WIP15B own equipment marker, not a manufactured radar track.
    for(const q of nulkaEntities15B().filter(q=>!q.ownerEntityId||q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId)){ctx.save();ctx.translate(q.x,q.y);ctx.fillStyle=q.payloadActive?'#ffd095':'#7f8b8f';ctx.beginPath();const tf=ctx.getTransform(),radius=2.5/Math.max(1e-9,Math.hypot(tf.a,tf.b));ctx.arc(0,0,radius,0,Math.PI*2);ctx.fill();ctx.restore();}
    // Ship marker (small ship shape, rotated to heading)
    ctx.save();
    ctx.translate(ax, ay);
    ctx.rotate(shipNav.heading);
    ctx.strokeStyle = 'rgba(100,200,255,0.75)';
    ctx.fillStyle = 'rgba(100,200,255,0.18)';
    ctx.lineWidth = 1.2*sym;
    ctx.beginPath();
    ctx.moveTo(8*sym, 0);      // bow
    ctx.lineTo(3*sym, 3*sym);
    ctx.lineTo(-6*sym, 3*sym);     // stern
    ctx.lineTo(-7*sym, 0);
    ctx.lineTo(-6*sym, -3*sym);
    ctx.lineTo(3*sym, -3*sym);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // CIWS position indicators (drawn in viz section below)

    // Unified manual-designation / lock bracket.
    const lcx=lockCursor.x,lcy=lockCursor.y;
    const lockedTr=selectedLockId!=null?tracks.get(selectedLockId):null;
    const cursorReady=lockedTr?trackIsFireControlQuality(lockedTr):false;
    const cursorCol=lockedTr?(cursorReady?'rgba(110,255,170,0.96)':'rgba(255,215,105,0.92)'):'rgba(70,170,255,0.84)';
    const cursorHalfW=10*sym,cursorHalfH=10*sym,cursorCorner=5*sym;
    drawTacticalBracket(ctx,lcx,lcy,cursorHalfW,cursorHalfH,cursorCol,tacticalLineWidthWorld(1.7,0.78),cursorCorner,true,cursorReady);

      // tracks
    for(const [id,localTr] of tracks){const tr=networkPresentationTrackG(localTr);
      if(!trackIsDisplayable(tr)) continue;
      const drawX = tr.x;
      const drawY = tr.y;
      const isLock = (id === selectedLockId);
      const bdaPresentation=wip121BdaTrackPresentation(tr),isBdaTrack=bdaPresentation.kind==='BDA'||bdaPresentation.kind==='KILL';

      // Classification is sensor-derived; internal truth association never decides symbol/color.
      const ownRadar=tr._harpoonOwnC;
      const isFriend=tr.identity==='FRIEND';
      const isASM = tr.classification==='ASM';
      const isAIR = tr.classification==='AIR';
      const isSURFACE = tr.classification==='SURFACE';
      const col = isBdaTrack?(bdaPresentation.kind==='BDA'?'rgba(255,190,70,0.94)':'rgba(165,175,180,0.80)'):(isLock ? 'rgba(255,220,120,0.98)' : (isFriend ? 'rgba(90,220,245,0.94)' : ownRadar ? 'rgba(255,210,80,0.86)' : isASM ? (['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)?'rgba(255,60,60,0.92)':'rgba(255,210,80,0.86)') : (isAIR ? 'rgba(0,255,120,0.86)' : (isSURFACE ? 'rgba(100,230,255,0.90)' : 'rgba(255,210,80,0.86)'))));
      ctx.fillStyle = col;
      ctx.strokeStyle = col;

      // WIP10 covariance ellipse: 2σ horizontal uncertainty from the full 6×6 P matrix.
      // This is combat-system uncertainty, not a decorative/random MEM bubble.
      if(tr.confirmed && tr._kfP && !isBdaTrack){
        const ce=tr.covarianceEllipse??trackCovarianceMetrics(tr);
        const majorM=ce.majorSigmaM??ce.posSigmaM??0,minorM=ce.minorSigmaM??ce.posMinorSigmaM??0,ang=ce.angleRad??ce.ellipseAngleRad??0;
        const majorW=metersToWorld(majorM*2.0),minorW=metersToWorld(minorM*2.0);
        if(majorW>1.5){
          ctx.save();ctx.translate(drawX,drawY);ctx.rotate(ang);
          const a=clamp(0.08+(1-(tr.fireControlQuality??0))*0.20,0.08,0.30);
          ctx.strokeStyle=isLock?`rgba(255,220,120,${a.toFixed(2)})`:`rgba(180,235,255,${a.toFixed(2)})`;
          ctx.lineWidth=tacticalLineWidthWorld(1.0,0.45);ctx.setLineDash(tr.reacquiring||tr.memActive?[3,4]:[6,6]);
          ctx.beginPath();ctx.ellipse(0,0,Math.max(2,majorW),Math.max(1.5,minorW),0,0,TAU);ctx.stroke();ctx.setLineDash([]);ctx.restore();
          ctx.strokeStyle=col;
        }
      }

      // Basic plot. BDA/confirmed-kill uses a crossed mark, never the live red ASM dot.
      if(isBdaTrack){const r=(bdaPresentation.kind==='BDA'?5.2:4.5)*sym;ctx.lineWidth=tacticalLineWidthWorld(1.5,0.62);ctx.beginPath();ctx.moveTo(drawX-r,drawY-r);ctx.lineTo(drawX+r,drawY+r);ctx.moveTo(drawX+r,drawY-r);ctx.lineTo(drawX-r,drawY+r);ctx.stroke();ctx.beginPath();ctx.arc(drawX,drawY,r*1.35,0,TAU);ctx.stroke();}
      else {ctx.beginPath();ctx.arc(drawX, drawY, (tr.confirmed?3.2:2.0)*sym, 0, TAU);ctx.fill();}
      if(isSURFACE&&tr.confirmed){ctx.lineWidth=1.0*sym;ctx.strokeRect(drawX-5.5*sym,drawY-5.5*sym,11*sym,11*sym);}
      if(!tr.confirmed){ ctx.font=`${tacticalFontWorldSize(6,4)}px system-ui`; ctx.fillText('TENT',drawX+5*sym,drawY-5*sym); }

      // 속도 벡터(방향)
      const vv = Math.hypot(tr.vx, tr.vy);
      if(vv > 0.02&&!isBdaTrack){
        const vx = tr.vx / vv * 18*sym;
        const vy = tr.vy / vv * 18*sym;
        ctx.lineWidth = 2*sym;
        ctx.beginPath();
        ctx.moveTo(drawX, drawY);
        ctx.lineTo(drawX + vx, drawY + vy);
        ctx.stroke();
      }

      // ===== 모양 표시 =====
      // The selected track is framed by the unified lock bracket drawn at lockCursor.
      if(!isBdaTrack&&!isLock && radar.mode === 'TWS'){
        const hasDL = missiles.some(mm => !mm.dead && mm.dlAlive && mm.assignedTargetId === id);
        if(hasDL){
          ctx.lineWidth = 2.0*sym;
          const s = 16*sym;
          ctx.beginPath();
          ctx.moveTo(drawX, drawY - s/2);
          ctx.lineTo(drawX + s/2, drawY);
          ctx.lineTo(drawX, drawY + s/2);
          ctx.lineTo(drawX - s/2, drawY);
          ctx.closePath();
          ctx.stroke();
        }
      }
      // ===== MEM 표시 (품질 기반) =====
      if(tr.memActive&&!isBdaTrack){
        const tq = tr.trackQuality ?? 0.5;
        const sigAlong = kmToWorld(tr.memSigAlongKm ?? 0.06);
        const sigCross = kmToWorld(tr.memSigCrossKm ?? 0.04);
        const memDir = tr.memDir ?? 0;

        // Elliptical uncertainty (along-track × cross-track)
        ctx.save();
        ctx.translate(drawX, drawY);
        ctx.rotate(memDir);

        // Uncertainty ellipse: opacity based on quality
        const ellipseAlpha = clamp(0.06 + (1 - tq) * 0.15, 0.06, 0.2);
        ctx.strokeStyle = 'rgba(255,255,255,' + ellipseAlpha.toFixed(2) + ')';
        ctx.lineWidth = tq > 0.5 ? tacticalLineWidthWorld(1.5,0.55) : tacticalLineWidthWorld(1.0,0.45);
        ctx.setLineDash(tq > 0.5 ? [5,6] : [3,4]);
        ctx.beginPath();
        ctx.ellipse(0, 0, Math.max(6, sigAlong), Math.max(4, sigCross), 0, 0, TAU);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();

        // Bracket: size and opacity based on quality
        const s = lerp(22, 14, tq); // worse quality → bigger bracket
        const bracketAlpha = clamp(0.15 + tq * 0.25, 0.15, 0.4);
        ctx.strokeStyle = 'rgba(255,255,255,' + bracketAlpha.toFixed(2) + ')';
        ctx.lineWidth = tq > 0.5 ? tacticalLineWidthWorld(2.0,0.75) : tacticalLineWidthWorld(1.5,0.55);

        ctx.beginPath();
        ctx.moveTo(drawX - s/2, drawY - s/2 + 6);
        ctx.lineTo(drawX - s/2, drawY - s/2);
        ctx.lineTo(drawX - s/2 + 6, drawY - s/2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(drawX + s/2, drawY + s/2 - 6);
        ctx.lineTo(drawX + s/2, drawY + s/2);
        ctx.lineTo(drawX + s/2 - 6, drawY + s/2);
        ctx.stroke();

        // Label: reason + quality indicator
        ctx.font = `${tacticalFontWorldSize(10,6)}px system-ui`;
        const labelAlpha = clamp(0.4 + tq * 0.4, 0.3, 0.8);
        const memLabel = (tr._memReason === 'HORIZON') ? 'MEM-H' :
                         (tr._memReason === 'MISS') ? 'MEM-?' :
                         'MEM';
        ctx.fillStyle = tq > 0.5 ? 'rgba(255,255,255,' + labelAlpha.toFixed(2) + ')' :
                        tq > 0.2 ? 'rgba(255,200,100,' + labelAlpha.toFixed(2) + ')' :
                                   'rgba(255,100,100,' + labelAlpha.toFixed(2) + ')';
        ctx.fillText(memLabel, drawX + s/2 + 3, drawY + 4);

        ctx.strokeStyle = col;
      }

      // ===== Threat Classification Tag =====
      {
        const ax2 = aircraft.x(), ay2 = aircraft.y();
        const dKm2 = worldToKm(dist(ax2, ay2, tr.x, tr.y));
        const alt2 = tr.z ?? 5000;
        const hasMsl = missiles.some(mm => !mm.dead && mm.assignedTargetId === id);

        let tag = '';
        if(isBdaTrack){
          tag=bdaPresentation.kind;
        } else if(ownRadar){
          tag = (ownRadar.launchId==null?'OWN?':'H'+ownRadar.launchId)+' '+(ownRadar.confirmed?(tr.sensorAge<=.35&&!tr.memActive?'RADAR':'EST'):'OWN?');
        } else if(isASM){
          tag = alt2 < 30 ? 'SK' : (alt2 < 200 ? 'LO' : 'ASM');
        } else if(isSURFACE){
          tag = 'SUR';
        } else if(!isAIR){
          tag = 'UNK';
        } else if(dKm2 < 15){
          tag = 'CLS';
        }

        if(tag){
          ctx.font = `${tacticalFontWorldSize(7,4)}px system-ui`;
          ctx.fillStyle = isBdaTrack?(bdaPresentation.kind==='BDA'?'rgba(255,195,75,0.92)':'rgba(175,185,190,0.82)'):(isFriend ? 'rgba(90,220,245,.94)' : ownRadar ? 'rgba(255,210,80,.86)' : isASM ? (['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)?'rgba(255,80,80,0.8)':'rgba(255,210,80,.86)') : (isSURFACE ? 'rgba(100,230,255,0.82)' : 'rgba(255,200,60,0.8)'));
          ctx.textAlign = 'left';
          ctx.fillText(tag, drawX + 8, drawY - 6);
        }

        // Missile assigned indicator (small diamond)
        if(hasMsl&&!isBdaTrack){
          ctx.strokeStyle = 'rgba(80,180,255,0.6)';
          ctx.lineWidth = tacticalLineWidthWorld(1.0,0.42);
          ctx.beginPath();
          ctx.moveTo(drawX - 12, drawY); ctx.lineTo(drawX - 9, drawY - 3);
          ctx.lineTo(drawX - 6, drawY); ctx.lineTo(drawX - 9, drawY + 3);
          ctx.closePath(); ctx.stroke();
        }
      }

      // ===== LOCKED TRACK COMPACT FCS CARD =====
      if(isLock){
        drawLockedTrackInfoCard(ctx,tr,id,drawX,drawY,isSURFACE,col,rw,rh);
        ctx.fillStyle=col;
        ctx.strokeStyle=col;
      }
    }

    // chaff dots
    // Enemy expendables are not shown unless a sensor-specific contact model detects them.
    // flare dots (orange/yellow)
    // Enemy expendables are not shown unless a sensor-specific contact model detects them.
    // missiles
    harpoonDrawCicA(ctx,sym);
    for(const m of missiles){
      if(m.dead) continue;
      if(m._vlsInCell?.active) continue; // WIP156: ignition occurs below/inside the VLS; marker appears at cell exit

      ctx.fillStyle = 'rgba(255,255,255,0.92)';
      ctx.beginPath();
      ctx.arc(m.x,m.y, 3.2*sym, 0, TAU);
      ctx.fill();

      ctx.strokeStyle = 'rgba(255,255,255,0.55)';
      ctx.lineWidth = 2*sym;
      ctx.beginPath();
      ctx.moveTo(m.x, m.y);
      ctx.lineTo(m.x + Math.cos(m.velAngle)*18*sym, m.y + Math.sin(m.velAngle)*18*sym);
      ctx.stroke();

      // seeker / SARH fan display
      {
        const sarhStandby = !!(m.sarhReceiverStandby || m.terminalSARH || m.state === 'SARH' || m._illuminatorId != null || (m._sarhStableQ ?? 0) > 0.06);
        const sarhSectorActive = sarhStandby && !(m.essmActiveSeeker === true && m.state === 'ACTIVE');
        const arhSectorActive = (m.state === 'ACTIVE') && !sarhSectorActive;
        if(sarhSectorActive || arhSectorActive){
          const gateActive = arhSectorActive && (m.seekerType === 'IR' && (m.irccmGateTimer ?? 0) > 0.02);
          const sarhSeek = m._sarhRfSeeker ?? null;
          const sarhState = sarhSeek?.mode ?? m._v1SarhState ?? 'SEARCH';
          const sarhQ = clamp(sarhSeek?.confidence ?? m._sarhStableQ ?? m._sarhRawQ ?? 0, 0, 1);
          const sarhCoast = sarhSectorActive && (sarhState === 'COAST' || sarhState === 'LOST' || !m.sarhAlive);
          const sarhLocked = sarhSectorActive && (sarhState === 'TRACK' || sarhState === 'REACQUIRE');
          const arhSeek = m._arhRfSeeker ?? null;
          const arhState = arhSeek?.mode ?? m._v1ArhState ?? 'SEARCH';
          const arhQ = clamp(arhSeek?.confidence ?? 0,0,1);
          const arhCoast = arhSectorActive && (arhState==='COAST'||arhState==='LOST');
          const arhLocked = arhSectorActive && (arhState==='TRACK'||arhState==='REACQUIRE');
          const drawCenter = (gateActive && Number.isFinite(m.irccmLastTargetAngle)) ? m.irccmLastTargetAngle : (m.seekerAngle ?? m.heading ?? m.velAngle ?? 0);
          const trackFov = sarhSectorActive ? deg((sarhState==='REACQUIRE'||sarhState==='COAST') ? 28 : 14) : (arhSectorActive ? deg((arhState==='REACQUIRE'||arhState==='COAST') ? 24 : 15) : (gateActive ? Math.max(deg(1.2), m.seekerFov * (m.irccmNarrowScale ?? 0.28)) : (m.seekerFov ?? deg(10))));
          const scanFov = sarhSectorActive ? deg(110) : (arhSectorActive ? deg(76) : (m.seekerScanFov ?? trackFov));
          const sectorRangeKm = sarhSectorActive
            ? clamp(Number.isFinite(m._rangeKmCached) ? Math.min(m.seekerRangeKm ?? 18, Math.max(1.2, m._rangeKmCached + (m.isESSM ? 0.7 : 1.2))) : (m.seekerRangeKm ?? 18), 1.2, m.seekerRangeKm ?? 18)
            : (m.seekerRangeKm ?? 12);
          const r = kmToWorld(sectorRangeKm);
          const sectorCol = sarhSectorActive
            ? (sarhCoast ? 'rgba(255,180,70,' : (sarhLocked ? 'rgba(255,210,90,' : 'rgba(255,155,70,'))
            : (arhCoast ? 'rgba(255,150,70,' : (arhLocked ? 'rgba(255,80,80,' : (gateActive ? 'rgba(255,170,50,' : 'rgba(80,140,255,')));

          // SARH acquisition/search envelope: wide dashed fan, like Sparrow/Phoenix STT-SARH view.
          if(sarhSectorActive && scanFov > trackFov * 1.10){
            ctx.fillStyle = sectorCol + '0.020)';
            ctx.beginPath();
            ctx.moveTo(m.x,m.y);
            ctx.arc(m.x,m.y, r, drawCenter - scanFov*0.5, drawCenter + scanFov*0.5);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = sectorCol + '0.11)';
            ctx.lineWidth = tacticalLineWidthWorld(1.0,0.36);
            ctx.setLineDash([4,4]);
            ctx.beginPath();
            ctx.arc(m.x,m.y, r, drawCenter - scanFov*0.5, drawCenter + scanFov*0.5);
            ctx.stroke();
            ctx.setLineDash([]);
          }

          ctx.fillStyle = sectorCol + (sarhSectorActive ? '0.050)' : '0.055)');
          ctx.beginPath();
          ctx.moveTo(m.x,m.y);
          ctx.arc(m.x,m.y, r, drawCenter - trackFov*0.5, drawCenter + trackFov*0.5);
          ctx.closePath();
          ctx.fill();

          ctx.strokeStyle = sectorCol + (sarhSectorActive ? '0.30)' : '0.26)');
          ctx.lineWidth = tacticalLineWidthWorld(sarhSectorActive ? 1.7 : 1.5, sarhSectorActive ? 0.60 : 0.55);
          ctx.beginPath();
          ctx.arc(m.x,m.y, r, drawCenter - trackFov*0.5, drawCenter + trackFov*0.5);
          ctx.stroke();

          if(sarhSectorActive){
            const gateCenterKm = clamp(Number.isFinite(sarhSeek?.gateCenterRangeM) ? sarhSeek.gateCenterRangeM/1000 : (Number.isFinite(m._rangeKmCached) ? m._rangeKmCached : sectorRangeKm * 0.72), 0.4, Math.max(0.45, sectorRangeKm));
            const gateWidthKm = Number.isFinite(sarhSeek?.gateRangeHalfM) ? Math.max(.08,2*sarhSeek.gateRangeHalfM/1000) : (m.isESSM ? 1.6 : 2.8);
            const rIn = kmToWorld(Math.max(0.15, gateCenterKm - gateWidthKm*0.5));
            const rOut = kmToWorld(Math.max(0.20, gateCenterKm + gateWidthKm*0.5));
            ctx.strokeStyle = sectorCol + '0.34)';
            ctx.lineWidth = tacticalLineWidthWorld(1.05,0.42);
            ctx.setLineDash([3,3]);
            ctx.beginPath(); ctx.arc(m.x,m.y,rIn,drawCenter-trackFov*0.5,drawCenter+trackFov*0.5); ctx.stroke();
            ctx.beginPath(); ctx.arc(m.x,m.y,rOut,drawCenter-trackFov*0.5,drawCenter+trackFov*0.5); ctx.stroke();
            ctx.setLineDash([]);

            const txtR = Math.min(r, kmToWorld(6.0));
            const tx = m.x + Math.cos(drawCenter) * txtR + 4*sym;
            const ty = m.y + Math.sin(drawCenter) * txtR - 4*sym;
            const status = sarhState==='ACQUIRE'?'ACQ':(sarhState==='REACQUIRE'?'REACQ':(sarhState==='LOST'?'LOST':(sarhState==='SEARCH'?'BUILD':sarhState)));
            ctx.fillStyle = sectorCol + '0.78)';
            ctx.font = `700 ${tacticalFontWorldSize(7,4.5)}px Consolas, monospace`;
            ctx.textAlign = 'left';
            ctx.fillText(`SARH ${status} ${Math.round(sarhQ*100)}%`, tx, ty);
          }

          if(arhSectorActive){
            const gateCenterKm=clamp(Number.isFinite(arhSeek?.gateCenterRangeM)?arhSeek.gateCenterRangeM/1000:(Number.isFinite(m._rangeKmCached)?m._rangeKmCached:sectorRangeKm*.7),.25,Math.max(.3,sectorRangeKm));
            const gateWidthKm=Number.isFinite(arhSeek?.gateRangeHalfM)?Math.max(.06,2*arhSeek.gateRangeHalfM/1000):1.2;
            const rIn=kmToWorld(Math.max(.12,gateCenterKm-gateWidthKm*.5)),rOut=kmToWorld(Math.max(.16,gateCenterKm+gateWidthKm*.5));
            ctx.strokeStyle=sectorCol+'0.30)';ctx.lineWidth=tacticalLineWidthWorld(1.0,.40);ctx.setLineDash([3,3]);ctx.beginPath();ctx.arc(m.x,m.y,rIn,drawCenter-trackFov*.5,drawCenter+trackFov*.5);ctx.stroke();ctx.beginPath();ctx.arc(m.x,m.y,rOut,drawCenter-trackFov*.5,drawCenter+trackFov*.5);ctx.stroke();ctx.setLineDash([]);
            const txtR=Math.min(r,kmToWorld(4.8)),tx=m.x+Math.cos(drawCenter)*txtR+4*sym,ty=m.y+Math.sin(drawCenter)*txtR-4*sym,status=arhState==='ACQUIRE'?'ACQ':(arhState==='REACQUIRE'?'REACQ':(arhState==='SEARCH'?'SEARCH':arhState));
            ctx.fillStyle=sectorCol+'0.78)';ctx.font=`700 ${tacticalFontWorldSize(7,4.5)}px Consolas, monospace`;ctx.textAlign='left';ctx.fillText(`ARH ${status} ${Math.round(arhQ*100)}%`,tx,ty);
          }

          if(arhSectorActive && m.seekerLocked){
            const gc = clamp(arhQ, 0, 1);
            const barLen = 12 * gc * sym;
            const bx = m.x + Math.cos(drawCenter) * 22*sym;
            const by = m.y + Math.sin(drawCenter) * 22*sym;
            ctx.strokeStyle = sectorCol + '0.7)';
            ctx.lineWidth = tacticalLineWidthWorld(2.0,0.8);
            ctx.beginPath();
            ctx.moveTo(bx, by);
            ctx.lineTo(bx + Math.cos(drawCenter) * barLen, by + Math.sin(drawCenter) * barLen);
            ctx.stroke();
          }

          if(sarhCoast || (arhSectorActive && m.seekerLocked && (m.tgtEstSrc === 'COAST' || (m.coastTimer??0) > 0.1))){
            ctx.strokeStyle = sarhSectorActive ? 'rgba(255,200,60,0.42)' : 'rgba(255,200,60,0.40)';
            ctx.lineWidth = tacticalLineWidthWorld(1.0,0.42);
            ctx.setLineDash([3,3]);
            ctx.beginPath();
            ctx.moveTo(m.x, m.y);
            ctx.lineTo(m.x + Math.cos(drawCenter)*r*0.7, m.y + Math.sin(drawCenter)*r*0.7);
            ctx.stroke();
            ctx.setLineDash([]);
          }
        }
      }

      // dotted line to seeker/SARH target
      if((m.state==='ACTIVE' && m.seekerLocked) || m.state==='SARH' || m.terminalSARH){
        let tx=null, ty=null;
        if(m.state==='ACTIVE' && m.seekerLocked){
          if(m.guidanceCore==='v1' && m.seekerLockType==='RF_EKF' && m._v1ArhEstimate?.posM){
            tx=metersToWorld(m._v1ArhEstimate.posM.x); ty=metersToWorld(m._v1ArhEstimate.posM.y);
          } else if(m.seekerLockType==='TGT'){
            const est=m._v1ArhEstimate; const tr=tracks.get(m.seekerLockId);
            if(est){ tx=metersToWorld(est.posM.x); ty=metersToWorld(est.posM.y); }
            else if(trackIsDisplayable(tr)){ tx=tr.x; ty=tr.y; }
          } else if(m.seekerLockType==='CHAFF'){
            const c = chaffs.find(x=>x.id===m.seekerLockId);
            if(c){ tx=c.x; ty=c.y; }
          } else if(m.seekerLockType==='FLARE'){
            const f = flares.find(x=>x.id===m.seekerLockId);
            if(f){ tx=f.x; ty=f.y; }
          }
        }
        if(tx==null && (m.state==='SARH' || m.terminalSARH)){
          const tr = tracks.get(m.assignedTargetId);
          if(trackIsDisplayable(tr)){ tx=tr.x; ty=tr.y; }
        }
        if(tx!=null){
          const sarhLine = (m.state==='SARH' || m.terminalSARH) && !(m.state==='ACTIVE' && m.seekerLocked);
          ctx.strokeStyle = sarhLine ? 'rgba(255,210,90,0.76)' : 'rgba(255,80,80,0.75)';
          ctx.lineWidth = tacticalLineWidthWorld(1.5,0.55);
          ctx.setLineDash(sarhLine ? [5,4] : [6,6]);
          ctx.beginPath();
          ctx.moveTo(m.x,m.y);
          ctx.lineTo(tx,ty);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      // DL line to target
      if(m.dlAlive){
        const tr = tracks.get(m.assignedTargetId);
        const tx = trackIsDisplayable(tr) ? tr.x : null;
        const ty = trackIsDisplayable(tr) ? tr.y : null;
        if(tx!=null){
          ctx.strokeStyle = 'rgba(80,160,255,0.55)';
          ctx.lineWidth = tacticalLineWidthWorld(1.2,0.50);
          ctx.setLineDash([4,4]);
          ctx.beginPath();
          ctx.moveTo(m.x,m.y);
          ctx.lineTo(tx,ty);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }
    }

    // Enemy truth objects are intentionally NOT rendered; ASM symbols come from sensor tracks above.

    // ===== CIWS Visualization =====
    // Range circles
    {
      const gunR = kmToWorld(GUN_CIWS_RANGE_KM);
      ctx.strokeStyle = 'rgba(255,255,100,0.07)';
      ctx.lineWidth = tacticalLineWidthWorld(0.7,0.30);
      ctx.setLineDash([3,5]);
      ctx.beginPath(); ctx.arc(ax, ay, gunR, 0, TAU); ctx.stroke();
      ctx.setLineDash([]);
    }
    {
      const ramR = kmToWorld(RAM_CIWS_RANGE_KM);
      ctx.strokeStyle = 'rgba(255,160,60,0.06)';
      ctx.lineWidth = tacticalLineWidthWorld(0.7,0.30);
      ctx.setLineDash([4,6]);
      ctx.beginPath(); ctx.arc(ax, ay, ramR, 0, TAU); ctx.stroke();
      ctx.setLineDash([]);
    }

    // CIWS mount positions
    for(const cw of ciws){
      // CIWS position on ship centerline (visible on radar)
      const fwdAng = shipNav.heading;
      const posOff = kmToWorld((cw.posOffsetM ?? 0) / 1000);
      const cwPx = ax + Math.cos(fwdAng) * posOff;
      const cwPy = ay + Math.sin(fwdAng) * posOff;

      // Draw firing arc indicator
      const isGun = (cw.type === 'GUN');
      const arcR = kmToWorld(isGun ? 0.8 : 1.2);
      const arcCenterAng = shipNav.heading + (cw.arcCenter ?? 0);
      const arcH = (cw.arcHalf ?? deg(130));
      ctx.strokeStyle = isGun ? 'rgba(80,180,255,0.12)' : 'rgba(255,200,50,0.12)';
      ctx.lineWidth = tacticalLineWidthWorld(0.6,0.28);
      ctx.beginPath();
      for(const [lo,hi] of ciwsWorldArcSegmentsV1(cw).open){ctx.moveTo(cwPx+Math.cos(arcCenterAng+lo)*arcR,cwPy+Math.sin(arcCenterAng+lo)*arcR);ctx.arc(cwPx,cwPy,arcR,arcCenterAng+lo,arcCenterAng+hi);}
      ctx.stroke();
      ctx.strokeStyle='rgba(255,95,75,.25)';ctx.beginPath();
      for(const [lo,hi] of ciwsWorldArcSegmentsV1(cw).blocked){ctx.moveTo(cwPx+Math.cos(arcCenterAng+lo)*arcR,cwPy+Math.sin(arcCenterAng+lo)*arcR);ctx.arc(cwPx,cwPy,arcR,arcCenterAng+lo,arcCenterAng+hi);}
      ctx.stroke();

      ctx.fillStyle = cw.firing
        ? (isGun ? 'rgba(255,255,0,0.9)' : 'rgba(255,140,40,0.9)')
        : 'rgba(150,150,150,0.5)';
      ctx.beginPath();
      ctx.arc(cwPx, cwPy, (isGun ? 2 : 2.5)*sym, 0, TAU);
      ctx.fill();

      // Phalanx: tracking beam
      if(isGun && cw.tracking){
        ctx.strokeStyle = cw.firing ? 'rgba(255,255,0,0.35)' : 'rgba(255,255,0,0.12)';
        ctx.lineWidth = tacticalLineWidthWorld(0.8,0.34);
        ctx.beginPath();
        ctx.moveTo(cwPx, cwPy);
        const beamLen = kmToWorld(cw.rangeKm);
        ctx.lineTo(cwPx + Math.cos(cw.trackAng)*beamLen, cwPy + Math.sin(cw.trackAng)*beamLen);
        ctx.stroke();
      }
    }

    // WIP13B5 presentation-only streaks. Endpoints follow authoritative projectile velocity;
    // neither the 2D map nor the 3D renderer advances a projectile or changes hit geometry.
    for(const b of ciwsBullets){
      const speed=Math.hypot(b.vx||0,b.vy||0)||1,ux=(b.vx||0)/speed,uy=(b.vy||0)/speed,len=kmToWorld(.0075);
      ctx.strokeStyle='rgba(255,190,72,.82)';ctx.lineWidth=tacticalLineWidthWorld(1.55,.72);ctx.beginPath();ctx.moveTo(b.x-ux*len,b.y-uy*len);ctx.lineTo(b.x,b.y);ctx.stroke();
      ctx.fillStyle = 'rgba(255,249,205,0.96)';
      ctx.beginPath();
      ctx.arc(b.x, b.y, 1.15*sym, 0, TAU);
      ctx.fill();
    }
    for(const p of mainGunProjectilesWip13B3){
      if(!p.alive)continue;const x=metersToWorld(p.positionM.x),y=metersToWorld(p.positionM.y),speed=Math.hypot(p.velocityMps.x,p.velocityMps.y)||1,ux=p.velocityMps.x/speed,uy=p.velocityMps.y/speed,len=kmToWorld(.018);
      ctx.strokeStyle='rgba(255,170,54,.90)';ctx.lineWidth=tacticalLineWidthWorld(2.1,.95);ctx.beginPath();ctx.moveTo(x-ux*len,y-uy*len);ctx.lineTo(x,y);ctx.stroke();ctx.fillStyle='rgba(255,249,218,.98)';ctx.beginPath();ctx.arc(x,y,1.45*sym,0,TAU);ctx.fill();
    }

    // SeaRAM interceptor missiles (orange triangles)
    for(const rm of ramMissiles){
      if(!rm.alive) continue;
      const hdg = Math.atan2(rm.vy, rm.vx);
      const sz = 3*sym;
      ctx.fillStyle = 'rgba(255,160,40,0.9)';
      ctx.beginPath();
      ctx.moveTo(rm.x + Math.cos(hdg)*sz*2, rm.y + Math.sin(hdg)*sz*2);
      ctx.lineTo(rm.x - Math.cos(hdg)*sz + Math.sin(hdg)*sz, rm.y - Math.sin(hdg)*sz - Math.cos(hdg)*sz);
      ctx.lineTo(rm.x - Math.cos(hdg)*sz - Math.sin(hdg)*sz, rm.y - Math.sin(hdg)*sz + Math.cos(hdg)*sz);
      ctx.closePath();
      ctx.fill();
      // Trail
      ctx.strokeStyle = 'rgba(255,140,40,0.3)';
      ctx.lineWidth = tacticalLineWidthWorld(1.0,0.42);
      ctx.beginPath();
      ctx.moveTo(rm.x, rm.y);
      ctx.lineTo(rm.x - Math.cos(hdg)*kmToWorld(0.3), rm.y - Math.sin(hdg)*kmToWorld(0.3));
      ctx.stroke();
    }

    // ===== Ship HP Bar =====
    {
      const barW = 44*sym, barH = 4*sym;
      const bx = ax - barW/2, by = ay + 10*sym;
      ctx.fillStyle = 'rgba(0,0,0,0.5)';
      ctx.fillRect(bx, by, barW, barH);
      const hpRatio = clamp(shipHP / 100, 0, 1);
      const hpCol = hpRatio > 0.5 ? 'rgba(0,255,80,0.8)' : (hpRatio > 0.2 ? 'rgba(255,200,0,0.8)' : 'rgba(255,40,40,0.8)');
      ctx.fillStyle = hpCol;
      ctx.fillRect(bx, by, barW * hpRatio, barH);
      ctx.strokeStyle = 'rgba(255,255,255,0.3)';
      ctx.lineWidth = 0.5*sym;
      ctx.strokeRect(bx, by, barW, barH);
      ctx.font = `${tacticalFontWorldSize(7,4)}px system-ui`;
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      ctx.textAlign = 'center';
      ctx.fillText(`HP:${Math.round(shipHP)}%`, ax, by + barH + 9*sym);
    }

    ctx.restore(); // end camera pan
    drawMapScaleBar(ctx);
    drawSpySchedulerScreenOverlay(ctx,rw,rh);
  }