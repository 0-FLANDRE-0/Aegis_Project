function envNativeAsmDamagePrefixD(em, dt){
    if(!em.alive) return;
    if(!em.flight){
      const oldKh35=em.kh35;
      em.flight=createAsmFlightState(em.label??(em.type==='SUPERSONIC'?'Kh-32':'Kh-35U'),em.speedMps??worldSpeedToMps(em.speed??0),em.vz??0,em.heading??0);
      if(em.label==='Kh-35U'){if(oldKh35){em.flight.seekerScanAngle=oldKh35.seekerScanAngle??0;em.flight.seekerScanRate=oldKh35.seekerScanRate??deg(45);em.flight.cruisePhase=oldKh35.cruisePhase??'SEASKIM';}em.kh35=em.flight;}
    }
    em.life += dt;
    missileNavB2Update(em,dt);
    const _w113=wip113RefreshBehavior(em);
    if(em._warheadState==='DETONATED'){const _w11cQ=wip11cQueueAsmRetirement(em,'WARHEAD_AIRBURST',{result:'AIRBURST'});wip173PushVisualEvent('ASM_WARHEAD_AIRBURST',{sourceId:em.id,x:em.x,y:em.y,z:em.z??0,
      vxMps:worldSpeedToMps(em.vx??0),vyMps:worldSpeedToMps(em.vy??0),vzMps:Number(em.vz)||0,massKg:wip173AsmImpactMassKg(em),
      targetLabel:em.label,explosiveMassKg:wip173AsmExplosiveKg(em),warheadState:'DETONATED',physicalWreckage:true,seed:_w11cQ?.seed});
      wip11cMaybeRecordSurfaceBlast({sourceType:'ASM_WARHEAD_AIRBURST',sourceId:em.id,targetLabel:em.label,x:em.x,y:em.y,z:em.z??0,
        vxMps:worldSpeedToMps(em.vx??0),vyMps:worldSpeedToMps(em.vy??0),vzMps:Number(em.vz)||0,explosiveMassKg:wip173AsmExplosiveKg(em),seed:_w11cQ?.seed});
      em.alive=false;retireTruthAssociationV27('ASM',em.id,'WARHEAD_AIRBURST');em._outcomeRecorded=true;wip113SetOutcome(em,'AIR_KILL');notify(`💥 ${em.label} 탄두 공중 유폭!`);return;}
    if(em.life > em.maxLife){ em.alive = false; retireTruthAssociationV27('ASM',em.id,'MAX_LIFE'); return; }
    // WIP68: do not early-return on post-CPA sea impact. The common impact block below must be
    // allowed to classify the event as a real hull hit or an explicit miss and record it in history.
    // Structural damage: chance of failure each frame
    if((em._structDmg ?? 0) > 30){
      const failChance = (em._structDmg / 100) * 0.02 * dt; // higher dmg = higher fail rate
      if(simRandom() < failChance){
        const _w11cQ=wip11cQueueAsmRetirement(em,'DELAYED_STRUCTURAL_FAILURE',{result:'STRUCT_FAIL'});wip173PushVisualEvent('ASM_BREAKUP',{sourceId:em.id,x:em.x,y:em.y,z:em.z??0,
          vxMps:worldSpeedToMps(em.vx??0),vyMps:worldSpeedToMps(em.vy??0),vzMps:Number(em.vz)||0,massKg:wip173AsmImpactMassKg(em),
          targetLabel:em.label,result:'STRUCT_FAIL',warheadState:em._warheadState??'NORMAL',physicalWreckage:true,seed:_w11cQ?.seed});
        em.alive = false; retireTruthAssociationV27('ASM',em.id,'STRUCTURAL_FAILURE');
        if(wip113HasAnySystemDamage(em))wip113SetOutcome(em,'AIR_KILL');
        notify(`💥 ${em.label} 구조파손 추락!`);
        return;
      }
    }

}
