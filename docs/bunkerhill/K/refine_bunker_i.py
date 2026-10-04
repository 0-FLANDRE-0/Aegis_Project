"""Rigid SPG parts and equipment-driven close-in release, preserving DDG order."""
def refine_i(source):
    s=source
    def replace(old,new,count=1):
        nonlocal s
        actual=s.count(old)
        if actual!=count:raise RuntimeError(f'I patch expected {count}, got {actual}: {old[:100]}')
        s=s.replace(old,new)
    assert s.count('const SPQ9B_PANEL_COUNT = ACTIVE_SHIP_PROFILE.sensors.spq9b.panelCount;')==1
    replace('!near(SPQ9B_NOMINAL_REVISIT_S,IS_BUNKER?2:1,1e-12)', '!near(SPQ9B_NOMINAL_REVISIT_S,1,1e-12)')
    replace("'CG52 single-panel 2D radar presentation drift'", "'CG52 dual-face 2D radar presentation drift'")
    replace("SPQ9B_RPM+' RPM':'OFFLINE'} · R", "SPQ9B_RPM+' RPM ×2 · SIM-TUNE':'OFFLINE'} · R")
    replace("    const phalanx=ciws[0];phalanx.firing=false;updateCueing(phalanx);\n    const _ciwsDmg=getShipDamageEffects(),phalanxPerformance=ciwsB3Performance(phalanx);",
      "    const _ciwsDmg=getShipDamageEffects();\n    for(const phalanx of ciws.filter(m=>m.type==='GUN')){\n    phalanx.firing=false;updateCueing(phalanx);\n    const phalanxPerformance=ciwsB3Performance(phalanx);")
    replace("    }else phalanx._shotAccumulator=phalanx._shotAccumulator??0;\n\n    // ===== PHALANX BULLETS =====",
      "    }else phalanx._shotAccumulator=phalanx._shotAccumulator??0;\n    }\n\n    // ===== PHALANX BULLETS =====")
    replace("                 engagementTrackId:phalanx.trackingTrackId,",
      "                 mountId:phalanx.id,installationId:phalanx.installationId??null,engagementTrackId:phalanx.trackingTrackId,")
    replace("if(spotTarget)ciwsObserveBulletTargetPlaneCrossing(phalanx,b,spotTarget,prevX,prevY,prevZ,dt);",
      "const shooter=ciws.find(m=>m.type==='GUN'&&m.id===b.mountId)??ciws.find(m=>m.type==='GUN');if(spotTarget&&shooter)ciwsObserveBulletTargetPlaneCrossing(shooter,b,spotTarget,prevX,prevY,prevZ,dt);")
    replace("    const searam=ciws[1];searam.firing=false;searam.reloadTimer=",
      "    for(const searam of ciws.filter(m=>m.type==='RAM')){\n    searam.firing=false;searam.reloadTimer=")
    replace("if(sol&&geometryOk&&qualityOk&&turretOk&&cooldownOk&&!alreadyEngaged&&searam.stateTimer>searam.trackToFireTime){",
      "if(searam.type==='RAM'&&sol&&geometryOk&&qualityOk&&turretOk&&cooldownOk&&!alreadyEngaged&&searam.stateTimer>searam.trackToFireTime){")
    replace("    for(const mount of ciws){if(!shipEquipmentOfflineV1()&&!mount._gameYawDriven)",
      "    } // installed RAM launchers\n\n    for(const mount of ciws){if(!shipEquipmentOfflineV1()&&!mount._gameYawDriven)")
    replace("    lines.push(`PLX:${ciws[0].ammo} RAM:${ciws[1].ammo}/${ramMissiles.filter(r=>r.alive).length} LOCK:${selectedLockId??'-'}`);",
      "    lines.push(IS_BUNKER?`PLX STBD:${ciws.find(m=>m.installation?.hardpointId==='phalanx')?.ammo??0} PORT:${ciws.find(m=>m.installation?.hardpointId==='phalanxPort')?.ammo??0} LOCK:${selectedLockId??'-'}`:`PLX:${ciws[0].ammo} RAM:${ciws[1].ammo}/${ramMissiles.filter(r=>r.alive).length} LOCK:${selectedLockId??'-'}`);")
    replace("    if(ph){\n      const q=Math.round(clamp(ph.trackQuality??0,0,1)*100)",
      "    for(const ph of ciws.filter(m=>m.type==='GUN')){\n      const q=Math.round(clamp(ph.trackQuality??0,0,1)*100)")
    replace("c.fillText(`Phalanx 20mm  ${ph.ammo}/${ph.maxAmmo}발`,10,y);",
      "c.fillText(`Phalanx 20mm${IS_BUNKER?(ph.installation.hardpointId==='phalanx'?' 우현':' 좌현'):''}  ${ph.ammo}/${ph.maxAmmo}발`,10,y);")
    replace("const mount=weapon==='RAM'?ciws.find(c=>c.type==='RAM'):ciws.find(c=>c.type==='GUN');\n    if(!mount||dmg.ciwsPowerFac<=.15) return {ok:false,reason:'CIWS_POWER'};\n    const geom=hardKillMountGeometry(mount,th.tr);",
      "const mounts=ciws.filter(c=>c.type===(weapon==='RAM'?'RAM':'GUN')),mount=mounts.find(c=>(c.ammo??0)>0&&hardKillMountGeometry(c,th.tr).ok)??mounts[0];\n    if(!mount||dmg.ciwsPowerFac<=.15) return {ok:false,reason:'CIWS_POWER'};\n    const geom=hardKillMountGeometry(mount,th.tr);")
    # Compatibility presentation fields must not claim a nonexistent launcher.
    replace("ciws:(()=>{const p=ciws[0],r=ciws[1];",
      "ciws:(()=>{const p=ciws.find(m=>m.type==='GUN'),r=ciws.find(m=>m.type==='RAM');")
    replace("seaRam:{azRelRad:ciwsBodyYawV1(r),elRad:Number(r?.turretEl)||0,tracking:!!r?.tracking,firing:!!r?.firing,state:r?.state??'IDLE'}};})(),",
      "seaRam:r?{azRelRad:ciwsBodyYawV1(r),elRad:Number(r?.turretEl)||0,tracking:!!r?.tracking,firing:!!r?.firing,state:r?.state??'IDLE'}:null};})(),")
    replace("const T=this.THREE,q=st?.ciws?.phalanx,pose=this.phalanxMuzzlePose(st);if(!q||!pose||!this.fxLayer)return;\n      if(q.firing){",
      "const T=this.THREE;if(!this.fxLayer)return;\n      for(const q of (IS_BUNKER?st.mountInventory?.closeIn?.filter(m=>m.type==='GUN')??[]:[st?.ciws?.phalanx])){\n      const pose=this.phalanxMuzzlePose(st,q?.id);if(!q||!pose)continue;\n      const accum=IS_BUNKER?((this._bunkerGunFxAcc??=new Map()).get(q.id)??(()=>{const a={phalanxGunFxAcc:0,phalanxSmokeFxAcc:0};this._bunkerGunFxAcc.set(q.id,a);return a;})()):this;\n      if(q.firing){")
    a=s.index('    updatePhalanxGunFx(st,dt){');b=s.index('      for(let i=this.gunFlashParticles.length-1;',a)
    section=s[a:b].replace('this.phalanxGunFxAcc','accum.phalanxGunFxAcc').replace('this.phalanxSmokeFxAcc','accum.phalanxSmokeFxAcc')
    s=s[:a]+section+'      } // independent installed gun effects; particle aging remains once per frame\n'+s[b:]
    # Mesh builders own fresh buffers/materials and attach disposal of their
    # private paint textures to the body geometry. Plume materials have no
    # shared smoke texture. Dispose unique resources once on normal retirement.
    replace("    syncMissileVisuals(st,dt){", """    disposeOrdnanceVisualV1(visual){
      const root=visual?.mesh;if(!root)return;const geometries=new Set(),materials=new Set();
      root.removeFromParent();root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])if(m)materials.add(m);});
      for(const g of geometries)g.dispose();for(const m of materials)m.dispose();
    },
    syncMissileVisuals(st,dt){""")
    replace("if(!seen.has(id)){layer.remove(v.mesh);this.missileVisuals.delete(id);}",
      "if(!seen.has(id)){this.disposeOrdnanceVisualV1(v);this.missileVisuals.delete(id);}")
    replace("if(!seen.has(key)){layer.remove(v.mesh);this.asmVisuals.delete(key);}",
      "if(!seen.has(key)){this.disposeOrdnanceVisualV1(v);this.asmVisuals.delete(key);}")
    replace("if(!seen.has(key)){layer.remove(v.mesh);v.mesh.traverse(o=>{o.geometry?.dispose?.();if(Array.isArray(o.material))for(const m of o.material)m?.dispose?.();else o.material?.dispose?.();});this.wreckVisuals.delete(key);}",
      "if(!seen.has(key)){this.disposeOrdnanceVisualV1(v);this.wreckVisuals.delete(key);}")
    replace("for(const v of map.values()){if(disposer)this[disposer](v);else for(const o of new Set([v.group,v.mesh,v.root].filter(Boolean)))disposeTree(o);}",
      "for(const v of map.values()){if(disposer)this[disposer](v);else if(['missileVisuals','asmVisuals','wreckVisuals'].includes(key))this.disposeOrdnanceVisualV1(v);else for(const o of new Set([v.group,v.mesh,v.root].filter(Boolean)))disposeTree(o);}")
    # A rendering exception used to escape before the next RAF was queued,
    # halting the whole game. Surface the fault and retain the CIC/reset path.
    replace("  let simRuntimeFault=null;", "  let simRuntimeFault=null,presentationRuntimeFault=null;")
    replace("  function clearSimRuntimeFault(){simRuntimeFault=null;}", """  function clearSimRuntimeFault(){simRuntimeFault=null;presentationRuntimeFault=null;if(lastErrorMsg.startsWith('3D FAULT @'))lastErrorMsg='';}
  function setPresentationRuntimeFault(err){
    const message=String(err?.stack||err?.message||err||'Unknown 3D error');
    presentationRuntimeFault={stage:'EXTERNAL_3D',step:simStepCounter,message,time:performance.now(),action:'RETURN_TO_CIC'};
    lastErrorMsg=`3D FAULT @ step ${simStepCounter}: ${String(err?.message||err)}`;
    debugLog(lastErrorMsg+'\\n'+message);WIP148_EXTERNAL_3D.close();notify('3D 오류 — CIC 전환 / 오류 기록됨');
  }""")
    replace("    if(_wip148External3D)WIP148_EXTERNAL_3D.render(now);",
      "    if(_wip148External3D){try{WIP148_EXTERNAL_3D.render(now);}catch(err){setPresentationRuntimeFault(err);}}")
    replace("    wip150ClearRuntimeFault:()=>{clearSimRuntimeFault();return true;}",
      "    wip150PresentationFault:()=>presentationRuntimeFault?{...presentationRuntimeFault}:null,\n    wip150ClearRuntimeFault:()=>{clearSimRuntimeFault();return true;}")
    return s
