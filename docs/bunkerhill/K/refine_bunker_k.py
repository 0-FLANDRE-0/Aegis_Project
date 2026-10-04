"""Profile-bound SPY CIC sectors and shared progressive survivor rafts."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def refine_k(source):
    s=source
    def replace(old,new,count=1):
        nonlocal s
        n=s.count(old)
        if n!=count:raise RuntimeError(f'K patch expected {count}, got {n}: {old[:120]}')
        s=s.replace(old,new)
    replace('interior:null,crew:null,mass:null,dynamics:null,aviation:', 'interior:null,crew:null,rescue:null,mass:null,dynamics:null,aviation:')
    replace('countermeasures:null,activeDecoys:[]}', 'countermeasures:null,activeDecoys:[],lifeRafts:[]}')
    replace('function createShipCrewV48Wip07(topology,posts=crewDutyPostsV48Wip07()){',
      (HERE/'ship-rescue-k.js').read_text()+'\nfunction createShipCrewV48Wip07(topology,posts=crewDutyPostsV48Wip07(),options={}){')
    replace('shipCrewV21=build(getShipInteriorTopologyV48Wip06(),crewDutyPostsV48Wip07());',
      'shipCrewV21=build(getShipInteriorTopologyV48Wip06(),crewDutyPostsV48Wip07(),{boardSurvivor:person=>shipRescueK().board(person.id),onReset:()=>ACTIVE_SHIP_RUNTIME.rescue?.reset()});')
    start=s.index('function createShipCrewV48Wip07(');end=s.index('function runV48Wip07CrewDamageProbe',start)
    part=s[start:end]
    old='  function syncTeams(orders=[]){\n';assert part.count(old)==1
    part=part.replace(old,old+"    if(['ABANDONED','LOST'].includes(mode))return;\n")
    old='  function reset(){\n';assert part.count(old)==1
    part=part.replace(old,old+'    options.onReset?.();\n')
    old="for(const g of groups)if(!g.dead&&!g.evacuated){const mk=g.injured&&g.mobility01<.5?'STRETCHER':'ABANDON';setDestination(g,posts.abandonSpaceId,mk,true);}"
    assert part.count(old)==1
    part=part.replace(old,"assignAbandonRoutes();")
    anchor='  function abandon(){';assert part.count(anchor)==1
    part=part.replace(anchor,"  function assignAbandonRoutes(){for(const g of groups)if(!g.dead&&!g.evacuated){g.teamId=null;g.pendingTeamId=null;g.underCare=false;const mk=g.injured&&g.mobility01<.5?'STRETCHER':'ABANDON';setDestination(g,posts.abandonSpaceId,mk,true);}}\n"+anchor)
    old='g.evacuated=g.fit+g.injured;g.fit=g.injured=0;report(\'퇴함\',g);'
    assert part.count(old)==1
    part=part.replace(old,"if(options.boardSurvivor&&options.boardSurvivor({id:g.id})!==true)continue;"+old)
    old='seen=new Set(damageEvents.map(e=>e.id));markDirty();return snapshot();'
    assert part.count(old)==1
    part=part.replace(old,"seen=new Set(damageEvents.map(e=>e.id));if(mode==='ABANDONED')assignAbandonRoutes();markDirty();return snapshot();")
    s=s[:start]+part+s[end:]
    # Only authoritative fixed ticks advance leeway and boarding. No render RNG.
    replace('    advanceOwnshipWorldWip14A(dt);',
      '    advanceOwnshipWorldWip14A(dt);\n    if(ACTIVE_SHIP_RUNTIME.rescue)ACTIVE_SHIP_RUNTIME.rescue.step(dt,getShipCrewV21().snapshot());')
    replace("const faceAngles = [-Math.PI/4, Math.PI/4, Math.PI*3/4, -Math.PI*3/4].map(a => a + shipNav.heading);",
      'const faceAngles = spyCicFaceLayoutK().map(q=>q.angleRad);')
    # Readiness used DDG names even on CG. Keep its thresholds and select the
    # installed module that already owns this face's physical health.
    start=s.index('  function getSPY1DVFaceStatus(){');end=s.index('\n  }',start)
    old=s[start:end];new=old
    for face,name in [('F1','AN/SPY-1D(V)(전좌)'),('F2','AN/SPY-1D(V)(전우)'),('F3','AN/SPY-1D(V)(후우)'),('F4','AN/SPY-1D(V)(후좌)')]:
        text="getModuleDmg('"+name+"')";assert new.count(text)==1
        new=new.replace(text,'getModuleDmg(SPY1DV_FACE_MODULE.'+face+')')
    s=s[:start]+new+s[end:]
    replace('// ===== AN/SPY-1D(V) 4-FACE PESA RADAR VISUALIZATION =====', '// ===== SELECTED SHIP SPY 4-FACE PESA RADAR VISUALIZATION =====')
    replace('// 4 fixed faces, each covers 90° sector', '// Selected physical face centres also own boundaries, load arcs and labels.')
    replace('    // Ship trail\n', '    drawRescueRaftsCicK();\n\n    // Ship trail\n')
    replace('      activeDecoys:nulkaEntities15B().map(nulkaRenderState15B),',
      '      lifeRafts:rescueRenderStatesK(),\n      activeDecoys:nulkaEntities15B().map(nulkaRenderState15B),')
    replace("    e.lifecycle={revision:(e.lifecycle.revision||0)+1,lastEvent:'OWNERSHIP_BOUND'};",
      "    shipRescueK();\n    e.lifecycle={revision:(e.lifecycle.revision||0)+1,lastEvent:'OWNERSHIP_BOUND'};")
    replace("function runtimeEntityCountsV48Wip11A(){return {activeDecoys:",
      "function runtimeEntityCountsV48Wip11A(){return {lifeRafts:ENGAGEMENT_RUNTIME.world.entities.lifeRafts.length,activeDecoys:")
    replace('profileImmutable:Object.isFrozen(ACTIVE_SHIP_PROFILE)&&r.profileId===ACTIVE_SHIP_PROFILE.id,',
      'rescueOwned:!!r.rescue&&Array.isArray(e.world.entities.lifeRafts),profileImmutable:Object.isFrozen(ACTIVE_SHIP_PROFILE)&&r.profileId===ACTIVE_SHIP_PROFILE.id,')
    replace("codecIds:Object.freeze(['envelope','navigation','weapons','loads','damageFlooding','crew','aviation'])",
      "codecIds:Object.freeze(['envelope','navigation','weapons','loads','damageFlooding','crew','rescue','aviation'])")
    replace("Object.freeze({id:'crew',validate:validateOperationalCrewV48Wip11B}),Object.freeze({id:'aviation',",
      "Object.freeze({id:'crew',validate:validateOperationalCrewV48Wip11B}),Object.freeze({id:'rescue',validate:validateOperationalRescueK}),Object.freeze({id:'aviation',")
    replace("'flooding','crewCasualtyAndLocation'],resetsCombatTransient:",
      "'flooding','crewCasualtyAndLocation','survivalRafts'],resetsCombatTransient:")
    replace('},crew,aviation:{inventory:jsonSafeCloneV48Wip11A(',
      '},crew,rescue:shipRescueK().snapshot(),aviation:{inventory:jsonSafeCloneV48Wip11A(')
    replace("    const validation={schema:'AEGIS_OPERATIONAL_PREFLIGHT_V48_WIP11B',ok:errors.length===0,errors,codecs,",
      "    if(errors.length===0){const migration=migrateLegacyRescueK(src);if(migration)migrations.push(migration);}\n    const validation={schema:'AEGIS_OPERATIONAL_PREFLIGHT_V48_WIP11B',ok:errors.length===0,errors,codecs,")
    replace('if(src.ship.crew)getShipCrewV21().restoreOperational(src.ship.crew);shipHP=',
      'if(src.ship.crew)getShipCrewV21().restoreOperational(src.ship.crew);shipRescueK().restore(src.ship.rescue);shipHP=')
    replace('el.querySelector(\'#crewTotalsV21\').textContent=`가용 ${crew.fit} · 부상 ${crew.injured} · 사망 ${crew.dead} · 퇴함 ${crew.evacuated} / ${crew.total}명`;',
      "const rescue=shipRescueK().summary();\n  el.querySelector('#crewTotalsV21').textContent=`가용 ${crew.fit} · 부상 ${crew.injured} · 사망 ${crew.dead} · 퇴함 ${crew.evacuated} / ${crew.total}명`+(rescue.rafts?` · 구명뗏목 ${rescue.rafts}척 · 탑승 ${rescue.persons}명 (척당 ${rescue.capacityPersons}명)`: '');")
    replace('퇴함은 구조 완료가 아닙니다.', '퇴함한 인원은 25인승 구명뗏목에 탑승하며, 퇴함은 구조 완료가 아닙니다.')
    replace('정원 310명에 보수반 20명', '정원 ${ACTIVE_SHIP_PROFILE.crew.roster}명에 보수반 20명')
    replace('this.syncNulkaVisuals15B(st);this.syncVisualEvents(st);', 'this.syncNulkaVisuals15B(st);this.syncRescueRaftsK(st);this.syncVisualEvents(st);')
    replace('    const valsM = [0, 1, 25, 60, 80, 1000, 123456.789];',
      "    try{const audit=rescueModuleAuditK();if(!audit.pass)failures.push('K rescue module '+JSON.stringify(audit.checks));}catch(err){failures.push('K rescue module '+String(err?.message??err));}\n    const valsM = [0, 1, 25, 60, 80, 1000, 123456.789];")
    replace("const maps=[['terrainVisuals','disposeTerrainVisual'],", "const maps=[['rescueRaftVisualsK','disposeRescueRaftK'],['terrainVisuals','disposeTerrainVisual'],")
    replace('  completeShipStartup();',
      (HERE/'rescue-renderer-k.js').read_text()+"\nObject.assign(window.__NAVAL_SIM_DIAG__,{spyCicFaceLayoutK:()=>spyCicFaceLayoutK(),rescueSnapshotK:()=>shipRescueK().snapshot(),rescueSummaryK:()=>shipRescueK().summary(),rescueModuleAuditK,rescueModuleK:()=>jsonSafeCloneV48Wip11A(SHIP_RESCUE_MK7_K)});\n  completeShipStartup();")
    return s
