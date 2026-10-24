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
function wip113HasAnySystemDamage(em){return !!em?._systemDamage&&WIP112_ASM_SYSTEM_KEYS.some(k=>(Number(em._systemDamage[k])||0)>0);}
const WIP112_ASM_SYSTEM_KEYS=DATA["WIP112_ASM_SYSTEM_KEYS"];
function simRandom(){SIM_RNG_STATE=_xorshift32(SIM_RNG_STATE);return (SIM_RNG_STATE>>>0)/4294967296;}
function notify(){}
function wip113SetOutcome(em,code){if(!em)return code;em._wip113Outcome=code;em._deathReason=code;return code;}
function retireTruthAssociationV27(){}
function wip11cMaybeRecordSurfaceBlast(){}
function wip173AsmExplosiveKg(em){const p=ASM_PROFILES[em?.label]??ASM_PROFILES['Kh-35U'];return Math.max(0,Number(p?.warhead?.explosiveMassKg)||Number(p?.warheadKg)*2/3||0);}
const ASM_PROFILES=DATA["ASM_PROFILES"];
function wip173AsmImpactMassKg(em){const p=ASM_PROFILES[em?.label]??ASM_PROFILES['Kh-35U'];return Math.max(0,Number(p?.impactMassKg)||0);}
function wip173PushVisualEvent(){}
function wip11cQueueAsmRetirement(em,cause,opt={}){
    if(!em||em._wip11cWreckCreated)return null;
    const previous=em._wip11cRetirementQueued;if(previous)return previous;
    const terminalReport=wip11cTerminalEffectReport(em,opt.source??opt.weaponLabel??cause),reportedTrackId=wip11cRetirementTrackId(em,opt),trackId=reportedTrackId??wip11cTerminalEffectTrackId(terminalReport);
    const queued={cause:String(cause||'COMBAT_KILL'),weaponLabel:opt.weaponLabel??null,result:opt.result??null,step:simStepCounter,seed:wip11cRetirementSeed(em,cause),engagementTrackId:trackId,trackCorrelation:reportedTrackId==null&&trackId!=null?'TERMINAL_EFFECT_GATE':'WEAPON_ASSIGNMENT'};
    Object.defineProperty(em,'_wip11cRetirementQueued',{value:queued,writable:true,configurable:true,enumerable:true});
    // WIP11C BDA: physical breakup is published as an own-force terminal-effect report before
    // the truth association is retired.  Engagement control consumes this report, never alive/dead truth.
    if(trackId!=null)wip121RecordFriendlyInterceptEvent(trackId,{key:`WIP11C_BREAKUP:${trackId}:${simStepCounter}`,effectStep:simStepCounter,
      weapon:opt.weaponLabel??null,evidence:'DIRECT_BREAKUP',result:opt.result??String(cause||'COMBAT_KILL'),source:'WIP11C_ASM_RETIREMENT',terminalReport});
    return queued;
  }
function wip121RecordFriendlyInterceptEvent(){}
function wip11cRetirementSeed(em,cause){return _mix32((SIM_SEED_BASE>>>0)^Math.imul((Number(em?.id)||1)>>>0,0x9e3779b1)^Math.imul((simStepCounter+1)>>>0,0x85ebca6b)^wip11cStringHash(cause))>>>0;}
function wip11cStringHash(value){let h=2166136261>>>0;for(const ch of String(value??'')){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)>>>0;}return h>>>0;}
let simStepCounter=0;
let SIM_SEED_BASE=1831565813;
function _mix32(v){ v=(v^0x9e3779b9)>>>0; v=Math.imul(v^(v>>>16),0x85ebca6b)>>>0; v=Math.imul(v^(v>>>13),0xc2b2ae35)>>>0; return (v^(v>>>16))>>>0; }
function wip11cTerminalEffectTrackId(){return 1;}
function wip11cRetirementTrackId(em,opt={}){
    const explicit=opt.trackId??opt.engagementTrackId;if(explicit!=null&&Number.isFinite(Number(explicit)))return Number(explicit);
    const remembered=em?._wip11cEngagementTrack?.trackId;if(remembered!=null&&Number.isFinite(Number(remembered)))return Number(remembered);
    // Compatibility for truth-bound diagnostics and old fixtures only. Live anonymous SPY files use
    // the friendly-weapon assignment path above and never depend on this reverse lookup.
    const legacy=em?.id==null?null:trackIdForTruthV27('ASM',em.id,false);return legacy==null?null:Number(legacy);
  }
function trackIdForTruthV27(){return 1;}
function wip11cTerminalEffectReport(em,source='FRIENDLY_TERMINAL_EFFECT'){
    if(!em)return null;return {schema:'AEGIS_TERMINAL_EFFECT_REPORT_V48_WIP11C',source:String(source),step:simStepCounter,
      positionM:{x:worldToMeters(Number(em.x)||0),y:worldToMeters(Number(em.y)||0),z:Number(em.z)||0},
      velocityMps:{x:worldSpeedToMps(Number(em.vx)||0),y:worldSpeedToMps(Number(em.vy)||0),z:Number(em.vz)||0}};
  }
const worldSpeedToMps = (wups) => worldToMeters(wups);
const worldToMeters = (wu) => (wu / WORLD_UNITS_PER_KM) * METERS_PER_KM;
const METERS_PER_KM=DATA["METERS_PER_KM"];
let WORLD_UNITS_PER_KM=DATA["WORLD_UNITS_PER_KM"];
function wip113RefreshBehavior(em){
    if(!em||typeof em!=='object')return null;wip112EnsureTargetState(em);
    const f=em.flight,d=em._systemDamage||{},C=WIP113_ASM_DAMAGE_BEHAVIOR;
    const b=em._wip113Behavior||(em._wip113Behavior={active:false,seekerFailed:false,seekerFailedAtS:null,seekerFrozenYaw:null,seekerFrozenPitch:null,guidanceMode:'NORMAL',engineStopped:false,fuelFire:false,fuelFireAtS:null,fuelElapsedS:0,fuelThrustScale:1,fuelEngineStopped:false,finsScale:1,availableG:null});
    b.active=wip113HasAnySystemDamage(em)||em._warheadState!=='NORMAL';
    if((Number(d.seeker)||0)>=C.seekerFailDamage&&!b.seekerFailed){b.seekerFailed=true;b.seekerFailedAtS=Number(em.life)||0;b.seekerFrozenYaw=Number.isFinite(f?.cmdFlightPathYaw)?f.cmdFlightPathYaw:(Number.isFinite(f?.flightPathYaw)?f.flightPathYaw:(Number(em.heading)||0));b.seekerFrozenPitch=Number.isFinite(f?.cmdFlightPath)?f.cmdFlightPath:(Number.isFinite(f?.flightPath)?f.flightPath:0);}
    b.guidanceMode=wip113GuidanceMode(d.guidance);
    b.engineStopped=(Number(d.engine)||0)>=C.engineStopDamage;
    if((Number(d.fuel)||0)>=C.fuelFireDamage&&!b.fuelFire){b.fuelFire=true;b.fuelFireAtS=Number(em.life)||0;}
    if(b.fuelFire){b.fuelElapsedS=Math.max(0,(Number(em.life)||0)-(Number(b.fuelFireAtS)||0));const fadeT=Math.max(0,b.fuelElapsedS-C.fuelFireDelayS);b.fuelThrustScale=clamp(1-fadeT/Math.max(1e-6,C.fuelThrustFadeS),0,1);b.fuelEngineStopped=b.fuelElapsedS>=C.fuelFireDelayS+C.fuelThrustFadeS-1e-9;}else{b.fuelElapsedS=0;b.fuelThrustScale=1;b.fuelEngineStopped=false;}
    b.finsScale=clamp(1-(Number(d.fins)||0)/100,0,1);
    const p=ASM_FLIGHT_PROFILES?.[em.label]??ASM_FLIGHT_PROFILES?.['Kh-35U'];b.availableG=(p?.maxNormalG??0)*(b.guidanceMode==='NORMAL'?b.finsScale:0);
    if(f){f._wip113GuidanceMode=b.guidanceMode;f._wip113FinsScale=b.finsScale;f._wip113FuelThrustScale=b.fuelThrustScale;f._wip113EngineStopped=!!(b.engineStopped||b.fuelEngineStopped);f._wip113AvailableG=b.availableG;}
    return b;
  }
const ASM_FLIGHT_PROFILES=DATA["ASM_FLIGHT_PROFILES"];
function clamp(v,a,b){ return Math.max(a, Math.min(b, v)); }
function wip113GuidanceMode(dmg){const d=Number(dmg)||0;return d>=WIP113_ASM_DAMAGE_BEHAVIOR.guidanceTumbleDamage?'TUMBLE':d>=WIP113_ASM_DAMAGE_BEHAVIOR.guidanceBallisticDamage?'BALLISTIC':'NORMAL';}
const WIP113_ASM_DAMAGE_BEHAVIOR=DATA["WIP113_ASM_DAMAGE_BEHAVIOR"];
function wip112EnsureTargetState(em){
    if(!em||typeof em!=='object')return em;
    if(!em._systemDamage){const d={};for(const k of WIP112_ASM_SYSTEM_KEYS)d[k]=0;Object.defineProperty(em,'_systemDamage',{value:d,writable:true,configurable:true,enumerable:true});}
    if(!('_warheadState' in em))Object.defineProperty(em,'_warheadState',{value:'NORMAL',writable:true,configurable:true,enumerable:true});
    if(!('_wip112ProjectedImpactMassKg' in em)){const p=ASM_PROFILES[em.label]??ASM_PROFILES['Kh-35U'];Object.defineProperty(em,'_wip112ProjectedImpactMassKg',{value:Number(p.impactMassKg)||0,writable:true,configurable:true,enumerable:false});}
    return em;
  }
function missileNavB2Update(m,dt){
    if(!m)return null;
    const n=missileNavB2Init(m),p=missileNavB2ProfileFor(m),h=clamp(Number(dt)||0,0,.25),life=missileNavB2Clock(m);
    if(n.updatedLife===life)return n;
    if(h>0){
      n.step++;n.timeS+=h;
      const a=['x','y','z'];
      for(let i=0;i<3;i++){
        const k=a[i],walk=_samB1HashSigned(m,0xa100+i*0x101,n.step)*(p.biasWalkMps3??0),noise=_samB1HashSigned(m,0xb200+i*0x101,n.step)*(p.accelNoiseMps2??0);
        n.imuBiasMps2[k]=clamp(n.imuBiasMps2[k]+walk*h,-p.accelBiasMps2*3,p.accelBiasMps2*3);
        const accErr=n.imuBiasMps2[k]+noise;
        n.posErrorM[k]+=n.velErrorMps[k]*h+.5*accErr*h*h;
        n.velErrorMps[k]+=accErr*h;
      }
      if(p.gpsAid&&n.gpsAid){
        const interval=Math.max(.1,p.gpsIntervalS??.5);
        while(n.timeS+1e-9>=n.nextGpsS){
          const fix=n.gpsFixCount+1,gpsPos={x:_samB1HashSigned(m,0xc311,fix)*p.gpsPosSigmaM,y:_samB1HashSigned(m,0xc422,fix)*p.gpsPosSigmaM,z:_samB1HashSigned(m,0xc533,fix)*p.gpsPosSigmaM*.75},gpsVel={x:_samB1HashSigned(m,0xd611,fix)*p.gpsVelSigmaMps,y:_samB1HashSigned(m,0xd722,fix)*p.gpsVelSigmaMps,z:_samB1HashSigned(m,0xd833,fix)*p.gpsVelSigmaMps*.75};
          for(const k of ['x','y','z']){n.posErrorM[k]+=clamp(p.gpsPosGain??.5,0,1)*(gpsPos[k]-n.posErrorM[k]);n.velErrorMps[k]+=clamp(p.gpsVelGain??.4,0,1)*(gpsVel[k]-n.velErrorMps[k]);}
          n.gpsFixCount=fix;n.lastGps={fix,timeS:n.nextGpsS,posErrorM:gpsPos,velErrorMps:gpsVel};n.nextGpsS+=interval;
        }
      }
    }
    if(p.altitudeAid&&n.altitudeAid&&h>0){
      // Simulated altitude/vertical-speed instrument updates. No X/Y target or position fix.
      const interval=Math.max(SIM_FIXED_DT,p.altitudeIntervalS);
      while(n.timeS+1e-9>=n.nextAltitudeS){
        const k=++n.altitudeFixCount;
        const ez=_samB1HashSigned(m,0xea31,k)*p.altitudeSigmaM,evz=_samB1HashSigned(m,0xeb42,k)*p.verticalVelocitySigmaMps;
        n.posErrorM.z+=(ez-n.posErrorM.z)*p.altitudeGain;n.velErrorMps.z+=(evz-n.velErrorMps.z)*p.verticalVelocityGain;
        n.nextAltitudeS+=interval;
      }
    }
    if(p.gpsAid&&!n.gpsAid)n.nextGpsS=n.timeS+(p.gpsIntervalS??.5);
    if(p.altitudeAid&&!n.altitudeAid)n.nextAltitudeS=n.timeS+p.altitudeIntervalS;
    // Truth is sampled only here as the physical sensor-synthesis boundary. Guidance consumers receive
    // the error-bearing estimate below and cannot recover this local truth object.
    const truth=_samB1TruthOwnState(m);
    n.posM={x:truth.posM.x+n.posErrorM.x,y:truth.posM.y+n.posErrorM.y,z:truth.posM.z+n.posErrorM.z};
    n.velMps={x:truth.velMps.x+n.velErrorMps.x,y:truth.velMps.y+n.velErrorMps.y,z:truth.velMps.z+n.velErrorMps.z};
    n.updatedLife=life;return n;
  }
function _samB1TruthOwnState(m){return {posM:{x:worldToMeters(m?.x??0),y:worldToMeters(m?.y??0),z:Number(m?.z)||0},velMps:{x:worldSpeedToMps(m?.vx??0),y:worldSpeedToMps(m?.vy??0),z:Number(m?.vz)||0}};}
const SIM_FIXED_DT=DATA["SIM_FIXED_DT"];
function _samB1HashSigned(m,salt,index=0){
    const id=(Number(m?.id)||1)>>>0,step=(Number(index)||0)>>>0,s=(Number(salt)||0)>>>0;
    const h=_mix32((SIM_SEED_BASE>>>0)^Math.imul(id,0x9e3779b1)^Math.imul(step+1,0x85ebca6b)^s^(Number(m?._navStreamSaltB2)||0));
    return (h/0xffffffff)*2-1;
  }
function missileNavB2Clock(m){
    // ASM direct physics fixtures use flight.timeS; the live guidance and dynamics share the same sample.
    return m?.flight&&('timeS' in m.flight)?Number(m.flight.timeS)||0:Number(m?.life)||0;
  }
function missileNavB2ProfileFor(m){
    const explicit=m?.navProfileId??m?._v1Profile?.navProfileId;
    if(explicit){const p=MISSILE_NAV_B2_PROFILES[explicit];if(!p)throw new Error('UNKNOWN_NAV_PROFILE:'+explicit);return p;}
    if(m?.isRAM)return MISSILE_NAV_B2_PROFILES.RAM_INS_B2;
    if(m?.label==='Kh-35U')return MISSILE_NAV_B2_PROFILES.ASM_KH35U_INS_B2;
    if(m?.label==='Kh-32')return MISSILE_NAV_B2_PROFILES.ASM_KH32_INS_B2;
    // Historical B1 mathematical fixtures omit the concrete profile ID. Never use this fallback for ASM/RAM.
    if(m?._v1Profile||m?.guidanceCore==='v1'||m?._legacyNavFixtureB1)return SAM_NAV_B1_PROFILES.ESSM_INS_B1;
    throw new Error('MISSILE_NAV_PROFILE_REQUIRED');
  }
const SAM_NAV_B1_PROFILES=DATA["SAM_NAV_B1_PROFILES"];
const MISSILE_NAV_B2_PROFILES=DATA["MISSILE_NAV_B2_PROFILES"];
function missileNavB2Init(m,force=false){
    if(!m)return null;if(!force&&(m._onboardNavB2||m._b1Nav))return m._onboardNavB2??m._b1Nav;
    const p=missileNavB2ProfileFor(m);m._navStreamSaltB2=p.source==='SIM_TUNED'?({ASM_KH35U_INS_B2:0x3510,ASM_KH32_INS_B2:0x3210,RAM_INS_B2:0x1a10}[p.id]??0):0;const truth=_samB1TruthOwnState(m),axis=(salt,mag)=>_samB1HashSigned(m,salt,0)*mag;
    const posErr={x:axis(0x11a1,p.initialPosErrorM),y:axis(0x22b2,p.initialPosErrorM),z:axis(0x33c3,(p.initialPosErrorZM??p.initialPosErrorM*.65))};
    const velErr={x:axis(0x44d4,p.initialVelErrorMps),y:axis(0x55e5,p.initialVelErrorMps),z:axis(0x66f6,(p.initialVelErrorZMps??p.initialVelErrorMps*.70))};
    const bias={x:axis(0x7717,p.accelBiasMps2),y:axis(0x8828,p.accelBiasMps2),z:axis(0x9939,p.accelBiasMps2*.75)};
    m._onboardNavB2={schema:p.source?MISSILE_NAV_B2_CONTRACT.schema:SAM_NAV_B1_CONTRACT.schema,profileId:p.id,mode:p.mode,timeS:0,step:0,updatedLife:null,
      posErrorM:posErr,velErrorMps:velErr,imuBiasMps2:bias,
      posM:{x:truth.posM.x+posErr.x,y:truth.posM.y+posErr.y,z:truth.posM.z+posErr.z},
      velMps:{x:truth.velMps.x+velErr.x,y:truth.velMps.y+velErr.y,z:truth.velMps.z+velErr.z},
      gpsAid:!!p.gpsAid,gpsFixCount:0,nextGpsS:p.gpsAid?(p.gpsIntervalS??.5):Infinity,lastGps:null};
    const n=m._onboardNavB2;
    if(m._v1Profile||m.guidanceCore==='v1')m._b1Nav=n; // COMPAT_REQUIRED, same object, not a second authority.
    n.altitudeAid=!!p.altitudeAid;n.altitudeFixCount=0;n.nextAltitudeS=p.altitudeAid?p.altitudeIntervalS:Infinity;
    return n;
  }
const SAM_NAV_B1_CONTRACT=DATA["SAM_NAV_B1_CONTRACT"];
const MISSILE_NAV_B2_CONTRACT=DATA["MISSILE_NAV_B2_CONTRACT"];
function deg(d){ return d*Math.PI/180; }
function createAsmFlightState(label,speedMps,initialVzMps=0,initialHeadingRad=0){
    const p=ASM_FLIGHT_PROFILES[label]??ASM_FLIGHT_PROFILES['Kh-35U'],V=Math.max(20,Number(speedMps)||20);
    const gamma=Math.atan2(Number(initialVzMps)||0,Math.max(1,V)),psi=angNorm(Number(initialHeadingRad)||0);
    return {profileId:p.id,bodyDynamics:p.bodyDynamics??'BODY_6DOF_LITE',timeS:0,engineTimeS:0,massKg:p.launchMassKg,
      propellantKg:Math.max(0,p.launchMassKg-p.dryMassKg),fuelKg:p.fuelKg??0,
      bodyPitch:gamma,flightPath:gamma,cmdFlightPath:gamma,pitchRate:0,aoa:0,
      bodyYaw:psi,flightPathYaw:psi,cmdFlightPathYaw:psi,yawRate:0,beta:0,
      normalG:0,lateralG:0,totalNormalG:0,qPa:0,mach:0,momentAuthority:1,
      thrustN:0,dragN:0,maneuverDragN:0,throttle:0,engineSpool:0,
      maxPitchRate:deg(p.maxPitchRateDegS),maxYawRate:deg(p.maxYawRateDegS??p.cruiseHeadingRateDegS??10),
      maxAoA:deg(p.maxAoADeg),maxBeta:deg(p.maxBetaDeg??p.maxAoADeg),
      seekerScanAngle:0,seekerScanRate:deg(45),cruisePhase:'INITIAL',boosterDone:true};
  }
function angNorm(a){
    if(!Number.isFinite(a)){ lastErrorMsg = 'Non-finite angle input'; return 0; }
    return ((a + Math.PI) % TAU + TAU) % TAU - Math.PI;
  }
const TAU=DATA["TAU"];
let lastErrorMsg='';
function wip112AttachObservers(){if(!WIP112_RUNTIME_ENABLED)return;for(const em of enemyMissiles)wip112InstallEnemyObserver(em);for(const m of missiles)wip112InstallInterceptorObserver(m,m.isESSM?'ESSM':'SM2');for(const rm of ramMissiles)wip112InstallInterceptorObserver(rm,'RAM');}
const ramMissiles=[];
function wip112InstallInterceptorObserver(m,weaponType){
    if(!m||m._wip112InterceptorObserver)return;Object.defineProperty(m,'_wip112InterceptorObserver',{value:true,writable:true,configurable:true,enumerable:false});Object.defineProperty(m,'_wip112WeaponType',{value:weaponType,writable:false,configurable:true,enumerable:false});let reason=m._deathReason;
    Object.defineProperty(m,'_deathReason',{configurable:true,enumerable:true,get(){return reason;},set(v){reason=v;if(typeof v==='string'&&v.startsWith('PROX_DETONATION_')&&!m._wip112FragmentRecorded){try{const tgt=wip112ResolveInterceptorTarget(m,weaponType);if(tgt)wip112RecordFragmentSystemDamage(m,tgt,weaponType,v.slice('PROX_DETONATION_'.length));}catch(err){WIP112_DIAG_ERRORS.push(weaponType+':'+String(err?.message??err));}}}});
  }
let WIP112_DIAG_ERRORS=[];
function wip112RecordFragmentSystemDamage(interceptor,em,weaponType,outcome){
    if(!interceptor||!em||interceptor._wip112FragmentRecorded)return null;interceptor._wip112FragmentRecorded=true;wip112EnsureTargetState(em);em._wip112EventSeq=(em._wip112EventSeq??0)+1;
    const missM=Math.max(.75,Number(interceptor._fuzeFragmentArrivalMissM??interceptor._fuzeBurstMissM??0.75)),mvx=worldSpeedToMps(interceptor.vx??0),mvy=worldSpeedToMps(interceptor.vy??0),mvz=interceptor.vz??0,tvx=worldSpeedToMps(em.vx??0),tvy=worldSpeedToMps(em.vy??0),tvz=em.vz??0,kin=_wip88InterceptKinematics(mvx,mvy,mvz,tvx,tvy,tvz);if(weaponType==='ESSM'&&Number.isFinite(Number(interceptor._wip144FragmentFieldEfficiency)))kin.fragmentFieldEfficiency=Number(interceptor._wip144FragmentFieldEfficiency);const detail=_wip88FragmentationPk(missM,weaponType,em.label??'Kh-35U',kin),w=INTERCEPT_FRAGMENT_WARHEADS[weaponType];
    if(!w)return null;const sourceWorld={x:worldToMeters(interceptor.x-em.x),y:worldToMeters(interceptor.y-em.y),z:(interceptor.z??0)-(em.z??0)},expo=wip112ExposureShares(em,sourceWorld),rng={value:wip112HashSeed(em,weaponType==='SM2'?0x11220001:weaponType==='ESSM'?0x11220002:0x11220003)},boxes=wip112BuildSystemBoxes(em),byKey=Object.fromEntries(boxes.map(b=>[b.system,b]));
    const incident=wip112Unit(expo.sourceDirLocal),incidenceCos=clamp(Math.max(Math.abs(incident.x),Math.abs(incident.y),Math.abs(incident.z)),.20,1),fragEnergy=wip112ScaledPenetrationEnergyMJ(w.avgFragmentMassKg,WIP112_DAMAGE_RULES.diagnosticFragmentDiameterM,detail.fragmentImpactSpeedMps,incidenceCos,WIP112_DAMAGE_RULES.fragmentHardness,false),penetratingBySystem={},systemRows=[];
    for(const sh of expo.shares){const box=byKey[sh.system],lambda=Math.max(0,detail.expectedLethalHits*sh.share),hits=wip112Poisson(lambda,rng),barrier=Math.max(1e-9,box.penetrationResistanceMJ)*(fragEnergy.obliquityResistanceFactor??1),penP=clamp(fragEnergy.effectiveEnergyMJ/Math.max(1e-9,barrier),0,1),penHits=hits>0?wip112Binomial(hits,penP,rng):0,stopped=Math.max(0,hits-penHits),dmg=penHits*box.damagePerPenHit+stopped*box.damagePerStoppedHit;penetratingBySystem[sh.system]=penHits;if(dmg>0)wip112ApplySystemDamage(em,sh.system,dmg,{weaponType});systemRows.push({system:sh.system,projectedAreaM2:sh.areaM2,exposureShare:sh.share,expectedHits:lambda,hitFragments:hits,penetratingHits:penHits,penetrationProbability:penP,resistanceMJ:box.penetrationResistanceMJ,damageApplied:dmg});}
    const warheadBefore=em._warheadState,warheadAfter=wip112MaybeUpdateWarheadState(em,penetratingBySystem,rng),row={kind:'FRAGMENT',step:simStepCounter,targetId:em.id,targetLabel:em.label,weaponType,outcome:String(outcome??''),missM,encounterAngleDeg:kin.encounterAngleDeg,expectedLethalHits:detail.expectedLethalHits,fragmentImpactSpeedMps:detail.fragmentImpactSpeedMps,sourceDirLocal:expo.sourceDirLocal,systemRows,warheadBefore,warheadAfter,projectedImpactMassKg:em._wip112ProjectedImpactMassKg,liveBehaviorApplied:false};WIP112_SYSTEM_HIT_LOG.push(row);return row;
  }
const WIP112_SYSTEM_HIT_LOG=[];
function wip112MaybeUpdateWarheadState(em,penetratingBySystem,rng){
    wip112EnsureTargetState(em);if(em._warheadState==='DETONATED')return em._warheadState;
    const fuzeN=Math.max(0,penetratingBySystem.fuze||0),warN=Math.max(0,penetratingBySystem.warhead||0);
    if(fuzeN>0){const p=WIP112_DAMAGE_RULES.fuzeSympatheticDetonationPerPenHit;if(wip112NextIndependent(rng)<p){em._warheadState='DETONATED';return em._warheadState;}em._warheadState='DUD';}
    if(warN>0&&em._warheadState==='NORMAL')em._warheadState='DUD';return em._warheadState;
  }
function wip112NextIndependent(state){state.value=_xorshift32(state.value>>>0);return (state.value>>>0)/4294967296;}
function _xorshift32(state){
    state ^= (state << 13); state >>>= 0;
    state ^= (state >>> 17); state >>>= 0;
    state ^= (state << 5); state >>>= 0;
    return state >>> 0;
  }
const WIP112_DAMAGE_RULES=DATA["WIP112_DAMAGE_RULES"];
function wip112ApplySystemDamage(em,key,amount,meta={}){wip112EnsureTargetState(em);if(!WIP112_ASM_SYSTEM_KEYS.includes(key))return;const before=em._systemDamage[key]??0,after=clamp(before+Math.max(0,Number(amount)||0),0,100);em._systemDamage[key]=after;wip112UpdateProjectedImpactMass(em);return {system:key,before,after,delta:after-before,...meta};}
function wip112UpdateProjectedImpactMass(em){const p=ASM_PROFILES[em.label]??ASM_PROFILES['Kh-35U'],wh=clamp((em._systemDamage?.warhead??0)/100,0,1),loss=(Number(p.warheadKg)||0)*WIP112_DAMAGE_RULES.damageMassLossFractionAtWarhead100*wh;em._wip112ProjectedImpactMassKg=Math.max(1,(Number(p.impactMassKg)||1)-loss);}
function wip112Binomial(n,p,state){n=Math.max(0,Math.floor(Number(n)||0));p=clamp(Number(p)||0,0,1);if(n<=0||p<=0)return 0;if(p>=1)return n;if(n>160){const mean=n*p,var0=n*p*(1-p),u1=Math.max(1e-9,wip112NextIndependent(state)),u2=wip112NextIndependent(state),z=Math.sqrt(-2*Math.log(u1))*Math.cos(TAU*u2);return clamp(Math.round(mean+Math.sqrt(var0)*z),0,n);}let k=0;for(let i=0;i<n;i++)if(wip112NextIndependent(state)<p)k++;return k;}
function wip112Poisson(lambda,state){lambda=Math.max(0,Number(lambda)||0);if(lambda<=0)return 0;if(lambda>24){const u1=Math.max(1e-9,wip112NextIndependent(state)),u2=wip112NextIndependent(state),z=Math.sqrt(-2*Math.log(u1))*Math.cos(TAU*u2);return Math.max(0,Math.round(lambda+Math.sqrt(lambda)*z));}const L=Math.exp(-lambda);let k=0,p=1;do{k++;p*=Math.max(1e-12,wip112NextIndependent(state));}while(p>L&&k<128);return Math.max(0,k-1);}
function wip112ScaledPenetrationEnergyMJ(massKg,diameterM,speedMps,incidenceCos,hardness,hardened){
    // penetrationEnergyState() intentionally floors projectile mass to 1 kg for its ASM use-case. WIP112 preserves that function byte-for-byte,
    // feeds an equivalent 1 kg diagnostic profile, then linearly restores the actual projectile/fragment mass in the returned energy only.
    const prof={impactMassKg:1,diameter:Math.max(.001,diameterM),penetrationHardness:hardness,hardenedPenetrator:!!hardened,length:.10,coherentPenLengthFactor:1};
    const st=penetrationEnergyState(prof,Math.max(0,speedMps),clamp(incidenceCos,0,1));return {...st,effectiveEnergyMJ:st.effectiveEnergyMJ*clamp(massKg,0,1),actualMassKg:massKg};
  }
function penetrationEnergyState(profile,impactSpeedMps,incidenceCos){
    const P=ASM_PENETRATION_MODEL, c=clamp(Number(incidenceCos)||0,0,1), obliquityDeg=rad2deg(Math.acos(c));
    const area=asmCrossSectionAreaM2(profile), sd=asmSectionalDensityKgM2(profile), mass=Math.max(1,Number(profile?.impactMassKg)||1);
    const vNormal=Math.max(0,impactSpeedMps*c);
    const rawKEJ=0.5*mass*vNormal*vNormal;
    let coupling=P.baseEnergyCoupling
      *Math.pow(P.referenceSpeedMps/Math.max(50,vNormal),P.speedCouplingExponent)
      *Math.pow(sd/P.referenceSectionalDensityKgM2,P.sectionalDensityExponent)
      *Math.max(0.25,Number(profile?.penetrationHardness)||1)
      *(profile?.hardenedPenetrator?1.04:0.94); // profile hardening flag is an explicit part of the coupling contract.
    coupling=clamp(coupling,P.minEnergyCoupling,P.maxEnergyCoupling);
    const areaFactor=Math.sqrt(area/Math.max(1e-9,P.referenceAreaM2));
    const obliquityResistanceFactor=1/Math.pow(Math.max(0.18,c),P.obliquityResistanceExponent);
    const continuousWorkMJPerM=P.continuousWorkMJPerMRef*areaFactor*obliquityResistanceFactor;
    const lengthCapM=Math.max(0.25,Number(profile?.length)||1)
      *Math.max(0.25,Number(profile?.coherentPenLengthFactor)||1)
      *Math.pow(Math.max(0.05,c),P.coherentLengthObliquityExponent);
    return {obliquityDeg,incidenceCos:c,vNormalMps:vNormal,rawKEJ,coupling,effectiveEnergyMJ:rawKEJ*coupling/1e6,
      areaM2:area,sectionalDensityKgM2:sd,areaFactor,obliquityResistanceFactor,continuousWorkMJPerM,lengthCapM,
      ricochet:obliquityDeg>=P.ricochetObliquityDeg};
  }
function asmSectionalDensityKgM2(profile){ return Math.max(1,Number(profile?.impactMassKg)||1)/Math.max(1e-6,asmCrossSectionAreaM2(profile)); }
function asmCrossSectionAreaM2(profile){ const d=Math.max(0.05,Number(profile?.diameter)||0.42);return Math.PI*(d*0.5)*(d*0.5); }
function rad2deg(r){ return r*180/Math.PI; }
const ASM_PENETRATION_MODEL=DATA["ASM_PENETRATION_MODEL"];
function wip112Unit(v){const n=Math.hypot(v?.x??0,v?.y??0,v?.z??0);return n>1e-9?{x:v.x/n,y:v.y/n,z:v.z/n}:{x:1,y:0,z:0};}
function wip112BuildSystemBoxes(label){
    const p=ASM_PROFILES[label]??ASM_PROFILES['Kh-35U'],L=Math.max(.5,Number(p.length)||4.45),D=Math.max(.1,Number(p.diameter)||.42),out=[];
    for(const key of WIP112_ASM_SYSTEM_KEYS){const q=WIP112_SYSTEM_LAYOUT[key],a=q.x0*L,b=q.x1*L,c=(a+b)*.5,hl=Math.max(.01,(b-a)*.5),r=Math.max(.02,q.radial*D);
      out.push({system:key,name:key,oX:c,oY:0,hL:hl,hW:r,zMin:-r,zMax:r,bodyLengthM:L,bodyRadiusM:D*.5,surfaceOnly:key==='fins',exposureScale:q.exposureScale??1,penetrationResistanceMJ:q.penetrationResistanceMJ,damagePerPenHit:q.damagePerPenHit,damagePerStoppedHit:q.damagePerStoppedHit,note:q.note});}
    return out;
  }
const WIP112_SYSTEM_LAYOUT=DATA["WIP112_SYSTEM_LAYOUT"];
function wip112HashSeed(em,salt=0){let x=((SIM_SEED_BASE>>>0)^Math.imul(((Number(em?.id)||1)>>>0),0x9e3779b1)^Math.imul(((Number(em?._wip112EventSeq)||0)+1)>>>0,0x85ebca6b)^(salt>>>0))>>>0;return _mix32(x)||1;}
function wip112ExposureShares(em,sourceWorldVec){
    const boxes=wip112BuildSystemBoxes(em?.label),src=wip112WorldVecToLocal(em,wip112Unit(sourceWorldVec));
    const maxFace=Math.max(...boxes.map(b=>b.oX+b.hL)),minFace=Math.min(...boxes.map(b=>b.oX-b.hL)),eps=1e-9;
    const raw=boxes.map(b=>{const lead=src.x>eps?(Math.abs((b.oX+b.hL)-maxFace)<eps):src.x<-eps?(Math.abs((b.oX-b.hL)-minFace)<eps):false;return {system:b.system,areaM2:wip112ProjectedBoxArea(b,src,lead)};});
    const sum=raw.reduce((a,b)=>a+b.areaM2,0)||1;
    return {sourceDirLocal:src,shares:raw.map(q=>({...q,share:q.areaM2/sum}))};
  }
function wip112ProjectedBoxArea(box,sourceDirLocal,axialFaceVisible=true){
    const d=wip112Unit(sourceDirLocal),lx=box.hL*2,ly=box.hW*2,lz=(box.zMax-box.zMin);
    // True projected-area decomposition with axial occlusion.  A pure nose/tail ray can only see the
    // foremost axial face; downstream compartments are geometrically shadowed.  The side/up projected
    // faces remain visible as the encounter becomes oblique, so a broadside fragment field naturally
    // exposes the full longitudinal body.  This is diagnostic geometry only and does not alter WIP88 Pk.
    const axial=axialFaceVisible?Math.abs(d.x)*ly*lz:0;
    const lateral=Math.abs(d.y)*lx*lz+Math.abs(d.z)*lx*ly;
    return Math.max(0,(axial+lateral)*(box.exposureScale??1));
  }
function wip112WorldVecToLocal(em,v){const B=wip112BodyBasis(em);return {x:v.x*B.forward.x+v.y*B.forward.y+v.z*B.forward.z,y:v.x*B.right.x+v.y*B.right.y+v.z*B.right.z,z:v.x*B.up.x+v.y*B.up.y+v.z*B.up.z};}
function wip112BodyBasis(em){
    const f=em?.flight,yaw=Number.isFinite(f?.bodyYaw)?f.bodyYaw:(Number.isFinite(em?.heading)?em.heading:0),pitch=Number.isFinite(f?.bodyPitch)?f.bodyPitch:0,cp=Math.cos(pitch),sp=Math.sin(pitch),cy=Math.cos(yaw),sy=Math.sin(yaw);
    return {forward:{x:cp*cy,y:cp*sy,z:sp},right:{x:-sy,y:cy,z:0},up:{x:-sp*cy,y:-sp*sy,z:cp},yaw,pitch};
  }
const INTERCEPT_FRAGMENT_WARHEADS=DATA["INTERCEPT_FRAGMENT_WARHEADS"];
function _wip88FragmentationPk(missDistM,weaponType,targetLabel,kin={}){
    const w=INTERCEPT_FRAGMENT_WARHEADS[weaponType],tp=INTERCEPT_FRAGMENT_TARGETS[targetLabel]??INTERCEPT_FRAGMENT_TARGETS['Kh-35U'];
    if(!w||!tp)return {pk:0,reason:'NO_FRAGMENT_PROFILE'};
    const r=Math.max(0.75,Number(missDistM)||0.75),vm=Math.max(0,Number(kin.missileSpeedMps)||0),rel=Math.max(0,Number(kin.relativeSpeedMps)||0);
    const enc=clamp(Number(kin.encounterAngleRad)||0,0,Math.PI),vf=_wip88GurneyFragmentSpeed(w);
    // WIP142/WIP148 fragment inventory contract.
    //  - explicit preformed fragments (ESSM) remain independent physical fragments;
    //  - WDU-17/B uses a clustered rod-breakup model: terminal piece count and independent angular coverage
    //    count are intentionally distinct because pieces from the same titanium rod remain spatially correlated;
    //  - untouched legacy profiles retain the old mass/average-fragment/fraction fallback exactly.
    const M=Math.max(1e-6,Number(w.gurneyDrivenMassKg??w.caseMassKg));
    const hasExplicitFragmentCount=Number.isFinite(Number(w.fragmentCount))&&Number(w.fragmentCount)>0;
    const rb=w.fragmentBreakupModel?.enabled?w.fragmentBreakupModel:null;
    const hasRodBreakup=!!(rb&&Number(rb.physicalRodCount)>0&&Number(rb.terminalFragmentsPerRodMean)>0&&Number(rb.independentCoverageFragmentsPerRodMean)>0);
    let N,coverageN,fragmentCountSource,clusterMultiplicity=1;
    if(hasExplicitFragmentCount){
      N=Number(w.fragmentCount);coverageN=N;fragmentCountSource='EXPLICIT';
    }else if(hasRodBreakup){
      N=Number(rb.physicalRodCount)*Number(rb.terminalFragmentsPerRodMean);
      coverageN=Number(rb.physicalRodCount)*Number(rb.independentCoverageFragmentsPerRodMean);
      clusterMultiplicity=Math.max(1,N/Math.max(1e-9,coverageN));
      fragmentCountSource='ROD_BREAKUP_CLUSTERED';
    }else{
      N=(M/Math.max(1e-6,w.avgFragmentMassKg))*(Number(w.effectiveFragmentFraction)??1);
      coverageN=N;fragmentCountSource='LEGACY_DERIVED';
    }
    // WIP144: physical inventory N is fixed. Only ESSM's useful spatial field is allowed to vary, and
    // only when the caller supplies the one-per-detonation draw. Diagnostics without an override retain
    // the exact WIP142/WIP143 physical baseline (efficiency=1).
    const _ffm=(weaponType==='ESSM'&&hasExplicitFragmentCount)?w.fragmentFieldEfficiencyModel:null;
    const fieldEfficiency=_ffm?.enabled&&Number.isFinite(Number(kin.fragmentFieldEfficiency))?clamp(Number(kin.fragmentFieldEfficiency),Number(_ffm.min)||0,Number(_ffm.max)||1):1;
    const effectiveN=N*fieldEfficiency,effectiveCoverageN=coverageN*fieldEfficiency;
    // Forward translation tilts an annular ~90-deg fragment spray toward the nose.
    // User-requested approximation: delta = atan(V_missile / V_fragment).
    const delta=Math.atan2(vm,Math.max(1e-6,vf)),thetaCenter=Math.PI/2-delta;
    const bandHalfAngleDeg=Number(w.annularBandHalfAngleDeg??w.coneHalfAngleDeg),half=deg(bandHalfAngleDeg);
    const bandAreaM2=4*Math.PI*r*r*Math.max(0.10,Math.sin(thetaCenter))*Math.max(0.01,Math.sin(half));
    // First-order encounter-angle weighting from the forward-tilted annulus. It remains continuous,
    // equals 1 head-on, and falls toward a tail chase without a hand-authored Pk lookup table.
    const s=Math.sin(delta),coneAspectFactor=clamp((1+s*Math.cos(enc))/Math.max(1e-6,1+s),0.15,1.0);
    // Spatial coverage uses independent coverage clusters, not raw terminal-piece count.  For normal
    // preformed-fragment profiles coverageN===N, so this algebra reduces EXACTLY to the pre-WIP148 model.
    const fragmentSurfaceDensityM2=(effectiveCoverageN/bandAreaM2)*coneAspectFactor;
    const terminalFragmentSurfaceDensityM2=(effectiveN/bandAreaM2)*coneAspectFactor;
    // Annular-fragment average: fragment radial velocity and missile/target relative translation
    // are treated orthogonally for impact-energy estimation. Full per-fragment Mott/azimuth sampling is deferred.
    const fragmentImpactSpeedMps=Math.hypot(vf,rel);
    const penetrationProbability=1/(1+Math.exp(-(fragmentImpactSpeedMps-tp.fragPenV50Mps)/Math.max(1,tp.fragPenWidthMps)));
    const expectedCoverageIntersections=Math.max(0,fragmentSurfaceDensityM2*tp.vitalAreaM2);
    // A WDU-17/B coverage cell represents several correlated terminal pieces from a common rod breakup.
    // At least one penetrating piece in the cell is sufficient for the existing hard-kill Poisson mapping.
    // For ordinary profiles clusterMultiplicity=1 and clusterKillProbability==penetrationProbability exactly.
    const clusterKillProbability=clamp(1-Math.pow(Math.max(0,1-penetrationProbability),clusterMultiplicity),0,1);
    const expectedLethalHits=Math.max(0,expectedCoverageIntersections*clusterKillProbability);
    const pk=clamp(1-Math.exp(-expectedLethalHits),0,0.9995);
    return {pk,weaponType,warheadId:w.id,targetLabel,missDistM:r,explosiveMassKg:w.explosiveMassKg,gurneyDrivenMassKg:M,fragmentSpeedMps:vf,fragmentCount:N,coverageFragmentCount:coverageN,effectiveFragmentCount:effectiveN,effectiveCoverageFragmentCount:effectiveCoverageN,fragmentClusterMultiplicity:clusterMultiplicity,fragmentFieldEfficiency:fieldEfficiency,fragmentCountSource,coneTiltDeg:rad2deg(delta),coneCenterDeg:rad2deg(thetaCenter),coneHalfAngleDeg:bandHalfAngleDeg,annularBandHalfAngleDeg:bandHalfAngleDeg,coneAspectFactor,bandAreaM2,fragmentSurfaceDensityM2,terminalFragmentSurfaceDensityM2,vitalAreaM2:tp.vitalAreaM2,relativeSpeedMps:rel,missileSpeedMps:vm,targetSpeedMps:Number(kin.targetSpeedMps)||0,encounterAngleDeg:rad2deg(enc),fragmentImpactSpeedMps,penetrationProbability,clusterKillProbability,expectedCoverageIntersections,expectedLethalHits};
  }
function _wip88GurneyFragmentSpeed(w){
    // WIP142: Gurney-driven mass is independent from physical fragment inventory.
    // Legacy SM-2/RAM profiles fall back to caseMassKg byte-for-byte; ESSM uses the explicit
    // gurneyDrivenMassKg proxy so a sourced fragmentCount does not distort the Gurney mass ratio.
    const C=Math.max(1e-6,w.explosiveMassKg),M=Math.max(1e-6,Number(w.gurneyDrivenMassKg??w.caseMassKg)),cm=C/M;
    return w.gurneyMps*Math.sqrt(cm/(1+C/(2*M)));
  }
const INTERCEPT_FRAGMENT_TARGETS=DATA["INTERCEPT_FRAGMENT_TARGETS"];
function _wip88InterceptKinematics(mvx,mvy,mvz,tvx,tvy,tvz){
    const mv=_wip88Vec3(mvx,mvy,mvz),tv=_wip88Vec3(tvx,tvy,tvz),ms=_wip88VecMag(mv),ts=_wip88VecMag(tv);
    const rv={x:mv.x-tv.x,y:mv.y-tv.y,z:mv.z-tv.z},relativeSpeedMps=_wip88VecMag(rv);
    let encounterAngleRad=0;
    if(ms>1e-6&&ts>1e-6){
      // 0=head-on (velocity vectors oppose), PI=tail chase (same direction).
      const c=clamp(-(mv.x*tv.x+mv.y*tv.y+mv.z*tv.z)/(ms*ts),-1,1);
      encounterAngleRad=Math.acos(c);
    }
    return {missileVelMps:mv,targetVelMps:tv,missileSpeedMps:ms,targetSpeedMps:ts,relativeVelMps:rv,relativeSpeedMps,encounterAngleRad,encounterAngleDeg:rad2deg(encounterAngleRad)};
  }
function _wip88VecMag(v){return Math.hypot(v?.x??0,v?.y??0,v?.z??0);}
function _wip88Vec3(x=0,y=0,z=0){return {x:Number(x)||0,y:Number(y)||0,z:Number(z)||0};}
function wip112ResolveInterceptorTarget(m,weaponType){return truthObjectForTrackV27(weaponType==='RAM'?m.targetId:m.assignedTargetId,false);}
function truthObjectForTrackV27(){return targetPool[0]??enemyMissiles[0];}
const missiles=[];
function wip112InstallEnemyObserver(em){
    if(!em||em._wip112EnemyObserver)return;wip112EnsureTargetState(em);Object.defineProperty(em,'_wip112EnemyObserver',{value:true,writable:true,configurable:true,enumerable:false});let hitCount=em._phalanxHitCount;
    Object.defineProperty(em,'_phalanxHitCount',{configurable:true,enumerable:true,get(){return hitCount;},set(v){const old=Number(hitCount)||0;hitCount=v;const nv=Number(v)||0;if(nv>old){try{for(let i=old;i<nv;i++)wip112RecordPhalanxSystemHit(em,0);}catch(err){WIP112_DIAG_ERRORS.push('PHALANX:'+String(err?.message??err));}}}});
  }
function wip112RecordPhalanxSystemHit(){throw Error("NO_PHALANX_IN_ENV_D");}
const enemyMissiles=[];
let WIP112_RUNTIME_ENABLED=DATA["WIP112_RUNTIME_ENABLED"];
function spawnEnemyMissile(fromTarget){
    const ax = aircraft.x(), ay = aircraft.y();
    const toShip = Math.atan2(ay - fromTarget.y, ax - fromTarget.x);
    const dLaunchKm = worldToKm(dist(fromTarget.x, fromTarget.y, ax, ay));

    // Use aircraft's weapon type
    const isSupersonic = (fromTarget.asmType === 'Kh-32');

    // INS target: from aircraft's last known ship position (with additional error)
    const knownX = fromTarget.lastKnownShipX ?? ax;
    const knownY = fromTarget.lastKnownShipY ?? ay;
    const insErrWorld = kmToWorld(rand(0.15, 0.6)); // realistic INS error for modern ASM
    const insErrAng = rand(-Math.PI, Math.PI);

    // Kh-32: cruise alt scales with distance (farther = higher for energy)
    let kh32CruiseAlt;
    if(dLaunchKm > 300) kh32CruiseAlt = rand(35000, 40000);
    else if(dLaunchKm > 160) kh32CruiseAlt = rand(28000, 35000);
    else kh32CruiseAlt = rand(22000, 28000);

    const em = {
      id: enemyMslSerial++,
      x: fromTarget.x, y: fromTarget.y, z: fromTarget.z,
      vz: 0,
      heading: fromTarget.heading,
      speed: Math.hypot(fromTarget.vx, fromTarget.vy),
      vx: fromTarget.vx, vy: fromTarget.vy,

      type: isSupersonic ? 'SUPERSONIC' : 'SUBSONIC',
      label: isSupersonic ? 'Kh-32' : 'Kh-35U',

      phase: 'SEPARATE',
      separateTimer: 0,
      separateDuration: isSupersonic ? rand(2.0, 3.5) : rand(0.8, 1.5),

      insTgtX: knownX + Math.cos(insErrAng) * insErrWorld,
      insTgtY: knownY + Math.sin(insErrAng) * insErrWorld,
      insHeading: toShip,
      launchDistKm: dLaunchKm,

      cruiseAltM:     isSupersonic ? kh32CruiseAlt : rand(10, 15), // Kh-35U/UE public cruise band: 10-15m
      seaskimAltM:    isSupersonic ? 0 : 4,    // Kh-35U/UE terminal sea-skim: about 4m
      seekerOnDistKm: isSupersonic ? 65 : 50,  // Kh-35UE public seeker acquisition range: up to 50km
      seekerFovDeg:   isSupersonic ? 50 : 60,  // Kh-35U: ±30° scan = 60° total
      seekerElDeg:    isSupersonic ? 15 : 10,
      popupStartKm:   isSupersonic ? 0 : 3.5,  // Kh-35U: 3.5km popup decision
      popupAltM:      isSupersonic ? 0 : rand(120, 180),  // Kh-35U: short popup 120-180m

      seekerOn: false,
      seekerLockTimer: 0,
      seekerLocked: false,
      seekerSearchAngle: 0,
      seekerTgtX: null, seekerTgtY: null,


      cruiseSpeedMps:   isSupersonic ? 1200 : 280,
      terminalSpeedMps: isSupersonic ? 1420 : 290,
      speedMps: Math.max(kmhToMps(300), worldSpeedToMps(Math.hypot(fromTarget.vx, fromTarget.vy))),

      rcsM2: isSupersonic ? 0.4 : 0.08, // legacy fallback, overridden by getASMRcs
      alive: true, life: 0, maxLife: 600,

      flight:null,
      kh35:null, // Kh-35U compatibility alias to the common flight state


    };
    em.flight=createAsmFlightState(em.label,em.speedMps,em.vz,em.heading);
    if(!isSupersonic)em.kh35=em.flight;

    fromTarget.asmLaunchRangeKm = isSupersonic ? rand(120, 180) : rand(120, 160);

    tagWorldEntityOwnershipV48Wip11A(em,'HOSTILE_ORDNANCE',`HOSTILE_AIRCRAFT_${fromTarget.id}`);
    missileNavB2Init(em,true);
    enemyMissiles.push(em);
    notify(`⚠ ${em.label} 발사! (T${fromTarget.id} ${Math.round(dLaunchKm)}km)`);
  }
function tagWorldEntityOwnershipV48Wip11A(m){m.ownerEntityId='ENV_PRIVATE';}
const kmhToMps = (kmh) => kmh * (1000/3600);
let enemyMslSerial=1;
function rand(a,b){ return a + simRandom()*(b-a); }
const kmToWorld = (km) => km * WORLD_UNITS_PER_KM;
function dist(ax,ay,bx,by){ return Math.hypot(ax-bx, ay-by); }
const worldToKm = (wu) => wu / WORLD_UNITS_PER_KM;
const aircraft={x:()=>0,y:()=>0};
function missileThrustN(m){
    const t = m.life || 0;
    if(m._propulsionSchedule){
      for(const seg of m._propulsionSchedule){
        if(t >= seg.startS && t < seg.endS && seg.durationS > 0){
          const u = clamp((t - seg.startS) / seg.durationS, 0, 1);
          const raw=lerp(seg.thrustStartN, seg.thrustEndN, u);
          return m._wip14a11Experiment?wip14a11EffectiveThrustN(m,raw,seg):raw;
        }
      }
      return m._wip14a11Experiment?wip14a11EffectiveThrustN(m,0,null):0;
    }

    // Legacy fallback for any non-v1 test object.
    if(t < m.burn1){
      if(m.boosterPropKg != null && m.boosterPropKg <= 0) return 0;
      return m.thrust1N;
    }
    const burn2End = m.burn1 + (m.burn2Sus ?? m.burn2 * 0.55);
    if(t < burn2End){
      if(m.sustainerPropKg != null && m.sustainerPropKg <= 0) return 0;
      const st = (t - m.burn1) / Math.max(1e-6, burn2End - m.burn1);
      const tStart = (m.thrust2Start ?? m.thrust2N);
      const tEnd   = (m.thrust2Mid ?? m.thrust2End ?? m.thrust2N);
      return lerp(tStart, tEnd, st);
    }
    const burn3End = m.burn1 + m.burn2;
    if(t < burn3End){
      if(m.sustainerPropKg != null && m.sustainerPropKg <= 0) return 0;
      return m.thrust3Coast ?? (m.thrust2End ?? 2000);
    }
    return 0;
  }
function wip14a11EffectiveThrustN(m,rawThrustN,seg){
    const cfg=m?._wip14a11Experiment;if(!cfg||!wip14a8IsStandardMissile(m))return rawThrustN;
    const phase=String(seg?.name??wip14a8PropulsionPhase(m)),altitudeM=Number(m.z)||0,pa=wip14a11AirPressurePa(altitudeM),Ae=WIP14A9_AREF_M2;
    const isMk72=phase.startsWith('MK72_')&&!phase.includes('COAST'),isMr=m?._v1Profile?.id==='SM2MR_BLKIIIA_SIM',isMk104=phase.startsWith('MK104_')||(isMr&&(phase==='BOOST'||phase==='SUSTAIN'));
    let mk72Scale=1,pressureCorrectionN=0;
    if(isMk72&&cfg.mk72ReferenceModel===WIP14A11_MK72_MODE.PUBLIC)mk72Scale=WIP14A11_MK72_PUBLIC_ISP_S/WIP14A11_MK72_ACTIVE_ISP_S;
    if(isMk104&&rawThrustN>0){
      if(cfg.mk104ReferenceModel===WIP14A11_MK104_MODE.LOW)pressureCorrectionN=-pa*Ae;
      else if(cfg.mk104ReferenceModel===WIP14A11_MK104_MODE.HIGH)pressureCorrectionN=Math.max(0,WIP14A11_PSL_PA-pa)*Ae;
    }
    const effective=Math.max(0,rawThrustN*mk72Scale+pressureCorrectionN);
    m._wip14a11ThrustState={phase,rawThrustN,effectiveThrustN:effective,mk72Scale,pressureCorrectionN,ambientPressurePa:pa,exitAreaUpperBoundM2:Ae,isMk72,isMk104};return effective;
  }
const WIP14A11_PSL_PA=DATA["WIP14A11_PSL_PA"];
const WIP14A11_MK104_MODE=DATA["WIP14A11_MK104_MODE"];
const WIP14A11_MK72_ACTIVE_ISP_S=DATA["WIP14A11_MK72_ACTIVE_ISP_S"];
const WIP14A11_MK72_PUBLIC_ISP_S=DATA["WIP14A11_MK72_PUBLIC_ISP_S"];
const WIP14A11_MK72_MODE=DATA["WIP14A11_MK72_MODE"];
const WIP14A9_AREF_M2=DATA["WIP14A9_AREF_M2"];
function wip14a11AirPressurePa(altitudeM){const a=speedOfSoundMps(altitudeM),rho=airDensityKgM3(altitudeM);return rho*a*a/1.4;}
function airDensityKgM3(altM){
    const h=clamp(Number(altM)||0,ALT_MIN_M,ATMOSPHERE_MODEL_MAX_M);
    for(let i=1;i<ATM_RHO_TABLE.length;i++){
      if(h<=ATM_RHO_TABLE[i][0]){
        const [h0,r0]=ATM_RHO_TABLE[i-1],[h1,r1]=ATM_RHO_TABLE[i];
        const t=(h-h0)/Math.max(1,h1-h0);
        return Math.exp(lerp(Math.log(r0),Math.log(r1),t));
      }
    }
    return ATM_RHO_TABLE[ATM_RHO_TABLE.length-1][1];
  }
function lerp(a,b,t){ return a + (b-a)*t; }
const ATM_RHO_TABLE=DATA["ATM_RHO_TABLE"];
const ATMOSPHERE_MODEL_MAX_M=DATA["ATMOSPHERE_MODEL_MAX_M"];
const ALT_MIN_M=DATA["ALT_MIN_M"];
function speedOfSoundMps(altM){
    const h = clamp(Number(altM)||0, 0, 50000);
    let T;
    if(h <= 11000) T = 288.15 - 0.0065*h;
    else if(h <= 20000) T = 216.65;
    else if(h <= 32000) T = 216.65 + 0.001*(h-20000);
    else if(h <= 47000) T = 228.65 + 0.0028*(h-32000);
    else T = 270.65;
    return Math.sqrt(1.4 * 287.05 * T);
  }
function wip14a8PropulsionPhase(m,tS=Number(m?.life)||0){
    const seg=m?._propulsionSchedule?.find(x=>tS+1e-12>=x.startS&&tS<x.endS-1e-12);
    if(seg)return seg.name;
    return tS+1e-9>=(m?._propulsionSequenceEndS??Infinity)?'BURNOUT':'COAST';
  }
function wip14a8IsStandardMissile(m){const id=m?._v1Profile?.id;return id==='SM2MR_BLKIIIA_SIM'||id==='SM2ER_BLKIV_SIM'||id==='SM6_BLKIA_SIM';}
const SAM_LOFT_PROFILE_REGISTRY=DATA["SAM_LOFT_PROFILE_REGISTRY"];
const SAM_MISSILE_PROFILES=DATA["SAM_MISSILE_PROFILES"];
function updateMissile(m,dt){
    try{return updateMissileBodyB3(m,dt);}
    finally{if(m?.dead)weaponLinkB3Close(m,'MISSILE_ENDED');}
  }
function weaponLinkB3Close(){}
function updateMissileBodyB3(m, dt){
    // WIP44: common event/guidance/fuze flow is retained, but v1 SM-2/ESSM motion uses
    // SAM BODY_6DOF_LITE after guidance command generation. Legacy missiles keep the old physics branch.
    m.life += dt;
    let _b1RawTrack=null;
    if(m.guidanceCore==='v1'&&m._v1Profile){samNavB1Update(m,dt);weaponLinkB3Tick(m);m._b1GuidanceCueTrack=samB1GuidanceCueTrack(m);}
    const _surfaceStepStart=surfaceMissileRuntimeWip13C6(m)?{x:m.x,y:m.y,z:m.z??0}:null;
    if(m.guidanceCore==='v1')m._gameBatteryRemainingS=Math.max(0,m.maxLife-m.life);
    if(m.life > m.maxLife){
      m._deathReason = m.guidanceCore==='v1' ? 'BATTERY_EXHAUSTED' : 'MAX_LIFE';
      m.dead = true;
      const _closeInfo = m._everClosest != null ? ` (closest ${Math.round(m._everClosest*1000)}m)` : '';
      const _mLbl = m.isESSM ? 'E' : 'M';
      notify(m.guidanceCore==='v1'?'⏱ 배터리 소진: '+_mLbl+m.id+_closeInfo:'⏱ 자폭: '+_mLbl+m.id+_closeInfo);
      return;
    }
    if(gameFlightTerminationTickV48(m,dt)) return;

    // WIP55: onboard SARH receiver runs independently of launch/pitchover guidance authority.
    // allocateSARH() has already assigned illumination for this frame.  Keep the physical RF
    // receiver alive during vertical launch and loft so it can build a local track before PN/APN
    // is allowed to own the missile attitude.
    if(m.guidanceCore==='v1'&&m._v1Profile){
      const _st=m._v1Profile.seekerType;
      if(_st==='SARH'||_st==='DUAL_MODE_ARH_SARH'){
        const _tr=m._b1GuidanceCueTrack??samB1GuidanceCueTrack(m);
        _v1StepSarhSensorV1(m,_tr,dt);
      }
    }

    // 속도 갱신(부스트 + 공기저항) — 고도/상승·하강 반영
    // (단순 모델) 고도가 높을수록 공기저항 ↓, 상승(vz>0)일수록 감속 ↑, 하강(vz<0)일수록 감속 ↓
    const altM = clamp((m.z ?? OWN_ALT_M), ALT_MIN_M, ATMOSPHERE_MODEL_MAX_M);
    const rhoF = airDensityFactor(altM); // 0.12~1.0

    // 상승/하강에 따른 에너지 손실 가중치 (비행경로각 대충 반영)
    const vz_mps_now = (m.vz ?? 0);
    const v_for_frac = Math.max(80, worldSpeedToMps(m.speed));
    const climbFrac = clamp(vz_mps_now / v_for_frac, -0.6, 0.6); // +면 상승
    // 상승은 더 크게, 하강은 완만하게(너무 과감속/과가속 방지)
    const climbFactor = (climbFrac >= 0)
      ? (1.0 + 0.85 * climbFrac)
      : (1.0 + 0.35 * climbFrac);


    // ===== Speed update (forces): thrust + drag + gravity =====
    // v-dot = (T - D)/m - g*sin(gamma)
    const v_mps = Math.max(1.0, worldSpeedToMps(m.speed));
    let massKg = (m.massKg ?? MISSILE_MASS_KG);

    const rho = airDensityKgM3(m.z ?? OWN_ALT_M);
    const q = 0.5 * rho * v_mps * v_mps;
    m.qbar = q;

    // ===== q-based dynamic G-limit (available maneuver) =====
    const gHard = (m.gLimitHard ?? m.gLimit ?? 40);
    const gMinQ = (m.gMinQ ?? MISSILE_G_MIN_Q);
    const qMin = (m.gQminPa ?? MISSILE_Q_MIN_PA);
    const qMax = (m.gQmaxPa ?? MISSILE_Q_MAX_PA);
    let q01g = (q - qMin) / Math.max(1e-6, (qMax - qMin));
    q01g = clamp(q01g, 0.0, 1.0);
    const sQ = q01g*q01g*(3 - 2*q01g); // smoothstep
    const gDynQ = clamp(gMinQ + (gHard - gMinQ) * sQ, gMinQ, gHard);
    m.gLimitDyn = gDynQ; // will be refined after Mach/AoA later

    // ===== TVC (Thrust Vector Control) — extreme agility during early boost =====
    if(m.tvcEnabled && m.life < (m.tvcDuration ?? 3.0) && missileThrustN(m) > 0){
      // ESSM: stronger deflection angle for 50G+ maneuvers
      // SM-2: moderate deflection
      const tvcDeflMax = m.isESSM ? deg(25) : deg(20);
      const tvcForce = (missileThrustN(m) || 0) * Math.sin(tvcDeflMax);
      const tvcG = tvcForce / (massKg * G0);
      const tvcFade = 1.0 - clamp(m.life / (m.tvcDuration ?? 3.0), 0, 1);
      m.gLimitDyn = clamp(m.gLimitDyn + tvcG * tvcFade, gMinQ, gHard);
    }

    // ===== Propellant mass depletion =====
    // v1 profile motors use exact thrust-integral consumption, independent of frame/tick sampling.
    let thrustN = missileThrustN(m);
    m._wip136RawMotorThrustN=thrustN;
    if(m.isESSM&&!m._wip136TvcJettisoned&&thrustN>0){
      const eff=clamp(Number(m._wip136TvcJetVaneEff??window.WIP136_ESSM_TVC_JETVANE_EFF)||1,.85,1);
      thrustN*=eff;m._wip136TvcThrustEfficiency=eff;
    }else if(m.isESSM)m._wip136TvcThrustEfficiency=1;
    m._wip136EffectiveThrustN=thrustN;
    const t_life = m.life || 0;
    const t_prev = Math.max(0, t_life - dt);

    if(m._propulsionSchedule){
      const boostDm = propulsionPropellantKgBetween(m, t_prev, t_life, 'boost');
      const sustainDm = propulsionPropellantKgBetween(m, t_prev, t_life, 'sustain');
      if(boostDm > 0){
        if(boostDm > (m.boosterPropKg ?? 0) + 1e-6) throw new Error('profile boost propellant underflow');
        m.boosterPropKg = Math.max(0, (m.boosterPropKg ?? 0) - boostDm);
      }
      if(sustainDm > 0){
        if(sustainDm > (m.sustainerPropKg ?? 0) + 1e-6) throw new Error('profile sustain propellant underflow');
        m.sustainerPropKg = Math.max(0, (m.sustainerPropKg ?? 0) - sustainDm);
      }
      const attachedBoosterDry=m.boosterSeparated?0:(m.boosterCasingKg??0);
      m.massKg = (m.missileDryKg ?? 0) + attachedBoosterDry + (m.boosterPropKg ?? 0) + (m.sustainerPropKg ?? 0);
      wip14a5AdvanceSm2ErStage(m);wip14a6AdvanceSm6Stage(m);
      m.massKg = (m.missileDryKg ?? 0) + (m.boosterSeparated?0:(m.boosterCasingKg??0)) + (m.boosterPropKg ?? 0) + (m.sustainerPropKg ?? 0);
      massKg = m.massKg;
    } else if(thrustN > 0){
      // Legacy fallback path.
      const isp = (m.ispS ?? 250);
      const mdot = thrustN / Math.max(1e-6, (isp * G0));
      const dmReq = mdot * dt;
      if(t_life < m.burn1){
        if(m.boosterPropKg != null && m.boosterPropKg > 0){
          const dm = Math.min(dmReq, m.boosterPropKg);
          m.boosterPropKg -= dm;
          if(dm < dmReq) thrustN *= (dm / dmReq);
        }
      } else if(m.sustainerPropKg != null && m.sustainerPropKg > 0){
        const dm = Math.min(dmReq, m.sustainerPropKg);
        m.sustainerPropKg -= dm;
        if(dm < dmReq) thrustN *= (dm / dmReq);
      }
      if(!m.boosterSeparated && t_life >= m.burn1){
        m.boosterSeparated = true;
        m.massKg -= (m.boosterCasingKg ?? 0);
      }
      const bProp = Math.max(0, m.boosterPropKg ?? 0);
      const sProp = Math.max(0, m.sustainerPropKg ?? 0);
      const bCase = m.boosterSeparated ? 0 : (m.boosterCasingKg ?? 0);
      m.massKg = (m.missileDryKg ?? 169) + sProp + bProp + bCase;
      massKg = m.massKg;
    }

    // WIP156: while still inside the canister, consume the REAL motor propellant/thrust above,
    // but bypass free-flight aero/guidance and enforce the launcher rail constraint.
    if(_wip156StepVlsInCell(m,dt,thrustN,massKg)) return;

    // ===== Mach-dependent Cd =====
    const aSound = speedOfSoundMps(altM);
    const mach = (aSound > 1e-6) ? (v_mps / aSound) : 0;
    let cd = samParasiticCdV14A5(m,mach);
    if(m._wip14a11Experiment&&wip14a8IsStandardMissile(m))cd=wip14a11ParasiticCd(m,mach,altM,thrustN,cd);
    if(m.isESSM&&!m._wip136TvcJettisoned)cd*=Math.max(1,Number(m._wip136TvcInstalledDragFactor??window.WIP136_ESSM_TVC_INSTALLED_DRAG_FACTOR)||1);
    if(!isFinite(cd)) cd = MISSILE_CD0;
    m.mach = mach;
    m.cd = cd;

    // Basic parasitic drag (D = q * Cd * Aref)
    let D = q * cd * (m.arefM2 || MISSILE_AREF_M2);

    // ===== AoA-induced drag rise + control drag (CL-based) =====
    // Separate reference areas:
    //  - Aref  : drag reference (cross-section)
    //  - Slift : effective lifting reference for normal-force / G capability
    const Aref  = (m.arefM2 || MISSILE_AREF_M2);
    const Slift = (m.liftRefM2 || MISSILE_LIFTREF_M2);

    // Dynamic AoA limit (high q / high Mach => less usable AoA)
    const aoaMaxBase = (m.aoaMax ?? deg(40));
    const aoaQFactor = 1.0 - 0.25 * clamp(q / 45000, 0, 1);     // less harsh than before
    const aoaMachFactor = 0.92 + 0.08 / (1 + 0.9*mach);
    const aoaMaxDynEst = clamp(aoaMaxBase * aoaQFactor * aoaMachFactor, deg(6), aoaMaxBase);
    m.aoaMaxDyn = aoaMaxDynEst;

    // Refine G limit: q-based limit AND AoA/CL-based limit
    const clAlpha = missileCLalphaMach(mach);
    const CLmax = clAlpha * aoaMaxDynEst;
    const gAoa = (q > 1e-3) ? ((q * Slift * CLmax) / (massKg * G0)) : 1.0;
    m.gLimitDyn = clamp(Math.min(m.gLimitDyn, gAoa), 1.0, gHard);

    // Estimate normal accel from last-step turn rates (ties energy loss to actual maneuvering)
    const omY = (m.actOmegaYaw ?? m.omegaYaw ?? 0);
    const omP = (m.actOmegaPit ?? m.omegaPit ?? 0);
    // Body rotation driven by TVC is NOT aerodynamic normal acceleration.  The previous code fed
    // raw body rate into CL/induced-drag, so a near-cell TVC pitch-over looked like an impossible
    // fin-generated 50G turn and bled virtually all speed.  During launch use only a tiny aero
    // share; physical thrust-vector normal acceleration is integrated separately below.
    const launchTvcBodyRotation=m.isESSM&&m.tvcEnabled&&(m.vlsPhase===true||m.pitchoverPhase===true);
    const omegaPrev = Math.hypot(omY, omP) * (launchTvcBodyRotation?0.04:1.0);
    const aNprev = v_mps * omegaPrev; // m/s^2, aerodynamic share only

    // Required CL for that lift
    let CL = 0.0;
    if(q > 1e-3) CL = (massKg * aNprev) / Math.max(1e-6, (q * Slift));

    // AoA drag rise term (Cd_i = CL^2 / (pi*AR*e)) — formally 'lift-induced', but for missiles
    // this primarily captures drag-from-maneuvering (high CL → high drag penalty)
    const AR = (m.aspectRatio ?? MISSILE_AR);
    const eOswald = (m.oswaldEff ?? MISSILE_E_OSWALD);
    const CDi = (AR > 1e-6) ? (CL*CL / (Math.PI * AR * Math.max(1e-6, eOswald))) : 0.0;

    // Control/trim drag grows with AoA (small but matters)
    let aoaEst = (clAlpha > 1e-6) ? (CL / clAlpha) : 0.0;
    aoaEst = clamp(aoaEst, -aoaMaxDynEst, aoaMaxDynEst);
    const aoaNorm = clamp(Math.abs(aoaEst) / Math.max(1e-6, aoaMaxDynEst), 0, 1);
    const CDctrl = (m.cdCtrlK ?? MISSILE_CDCTRL_K) * (aoaNorm*aoaNorm);

    // Wave-drag bump (mostly transonic) + structured AoA penalty
    const tFac = transonicFactor(mach);
    const CDwave = (m.cdWaveK ?? MISSILE_CDWAVE_K) * tFac * Math.pow(aoaNorm, 1.6);
    // Mild AoA penalty across Mach (fin/body trim + separation), ramps strongly near AoA limit
    const CDaoa = (m.cdAoaK ?? 0.06) * Math.pow(aoaNorm, 3.0);

    // Total drag: parasitic (Aref) + induced (Slift)
    D = q * Aref * (cd + CDctrl + CDwave + CDaoa) + q * Slift * CDi;
    // optional debug
    m.cdWave = CDwave;
    m.cdAoa  = CDaoa;
const aDrag = D / massKg;
    // ===== WIP40 physical thrust-vector decomposition during VLS/forward-commit =====
    // Legacy flight integrates longitudinal thrust as scalar speed.  During the TVC launch phase that
    // is insufficient: once the BODY rotates, axial thrust must physically bend the velocity vector.
    // Decompose the actual gimballed thrust vector into velocity-parallel (speed) and normal parts.
    let aThrust=(thrustN||0)/massKg;
    m._tvcThrustNormalAx=0;m._tvcThrustNormalAy=0;m._tvcThrustNormalAz=0;
    const physicalVectorLaunch=!m.samSixDofEnabled&&m.isESSM&&m.tvcEnabled&&(m.vlsPhase===true||m.pitchoverPhase===true)&&thrustN>0;
    if(physicalVectorLaunch){
      const H=m.heading??0,P=m.pitch??0,tyaw=m.tvcYaw??0,tpit=m.tvcPitch??0;
      const cH=Math.cos(H),sH=Math.sin(H),cP=Math.cos(P),sP=Math.sin(P);
      const nx=cP*cH,ny=cP*sH,nz=sP;
      const rx=-sH,ry=cH,rz=0;
      const ux=-sP*cH,uy=-sP*sH,uz=cP;
      // Thrust-vector direction in body basis. tan() composition is normalized, so combined yaw/pitch
      // never creates more than T total force.
      let tx=nx+rx*Math.tan(tyaw)+ux*Math.tan(tpit),ty=ny+ry*Math.tan(tyaw)+uy*Math.tan(tpit),tz=nz+rz*Math.tan(tyaw)+uz*Math.tan(tpit);
      const tn=Math.max(1e-9,Math.hypot(tx,ty,tz));tx/=tn;ty/=tn;tz/=tn;
      const vh=Math.max(1e-9,Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0));
      const vux=worldSpeedToMps(m.vx??0)/vh,vuy=worldSpeedToMps(m.vy??0)/vh,vuz=(m.vz??0)/vh;
      const aTot=thrustN/massKg,along=aTot*(tx*vux+ty*vuy+tz*vuz);
      aThrust=along;
      m._tvcThrustNormalAx=aTot*tx-along*vux;
      m._tvcThrustNormalAy=aTot*ty-along*vuy;
      m._tvcThrustNormalAz=aTot*tz-along*vuz;
      m._tvcThrustVector={x:tx,y:ty,z:tz};
    }

    // Gravity component along current flight-path angle (pitch of velocity)
    const gamma = (m.velPitch || 0);
    const aGrav = G0 * Math.sin(gamma);

    if(!m.samSixDofEnabled){
      let v2 = v_mps + (aThrust - aDrag - aGrav) * dt;
      v2 = Math.max(0.0, v2);
      WIP14A2_SPEED_DIAGNOSTICS.record((m._v1Profile?.id??(m.isESSM?'ESSM_LEGACY':'SM2_LEGACY'))+'_AERO_EMERGENT',v2,null);
      m.speed = mpsToWorldSpeed(v2);
    }
// DL/IOG/SARH 상태 갱신
    const rawTr=m.guidanceCore==='v1'?null:tracks.get(m.assignedTargetId);
    const tr=m.guidanceCore==='v1'?(m._b1GuidanceCueTrack??samB1GuidanceCueTrack(m,rawTr)):rawTr;
    const _b1Own=m.guidanceCore==='v1'?samNavB1OwnState(m):null;

    // SARH legacy midcourse bridge consumes the sensor-derived combat-system track only.
    // The v1 SARH adapter adds terminal receiver/illumination measurement behavior separately.
    const sarhTgt = (m.guidanceCore!=='v1' && m.sarhAlive && tr && trackIsDisplayable(tr)) ? tr : null; // WIP36: v1 SARH never copies combat-track xyz into terminal command

    if(sarhTgt){
      m.lastCmdX = sarhTgt.x;
      m.lastCmdY = sarhTgt.y;
      m.lastCmdVx = sarhTgt.vx;
      m.lastCmdVy = sarhTgt.vy;
      m.lastCmdZ  = sarhTgt.z;
      m.lastCmdVz = (sarhTgt.vz ?? 0);
      m.iogAge = 0;
      m.afterClosestTimer = 0;
      m.closestKm = 999;

      // APN from SARH (high quality)
      const tVxNow = worldSpeedToMps(sarhTgt.vx);
      const tVyNow = worldSpeedToMps(sarhTgt.vy);
      const tVzNow = sarhTgt.vz ?? 0;
      if(m.apnLastVxMps != null && dt > 1e-4){
        const rawAx = (tVxNow - m.apnLastVxMps) / dt;
        const rawAy = (tVyNow - m.apnLastVyMps) / dt;
        const rawAz = (tVzNow - m.apnLastVzMps) / dt;
        const tau = 0.25; const alpha = dt / (tau + dt);
        m.apnAx = lerp(m.apnAx ?? 0, clamp(rawAx,-200,200), alpha);
        m.apnAy = lerp(m.apnAy ?? 0, clamp(rawAy,-200,200), alpha);
        m.apnAz = lerp(m.apnAz ?? 0, clamp(rawAz,-200,200), alpha);
      }
      m.apnLastVxMps = tVxNow; m.apnLastVyMps = tVyNow; m.apnLastVzMps = tVzNow;

      if(m.state !== 'ACTIVE') m.state = 'SARH';
    } else if(m.dlAlive && tr && (m.guidanceCore!=='v1'||weaponLinkB3TrackSnapshot(m,false))){
      // DL mode: track-quality target data
      const tVxNow = worldSpeedToMps(tr.vx);
      const tVyNow = worldSpeedToMps(tr.vy);
      const tVzNow = tr.vz ?? 0;
      if(m.apnLastVxMps != null && dt > 1e-4){
        const rawAx = (tVxNow - m.apnLastVxMps) / dt;
        const rawAy = (tVyNow - m.apnLastVyMps) / dt;
        const rawAz = (tVzNow - m.apnLastVzMps) / dt;
        const tau = 0.40; const alpha = dt / (tau + dt);
        m.apnAx = lerp(m.apnAx ?? 0, clamp(rawAx,-200,200), alpha);
        m.apnAy = lerp(m.apnAy ?? 0, clamp(rawAy,-200,200), alpha);
        m.apnAz = lerp(m.apnAz ?? 0, clamp(rawAz,-200,200), alpha);
      }
      m.apnLastVxMps = tVxNow; m.apnLastVyMps = tVyNow; m.apnLastVzMps = tVzNow;

      m.lastCmdX = tr.x;
      m.lastCmdY = tr.y;
      m.lastCmdVx = tr.vx;
      m.lastCmdVy = tr.vy;
      m.lastCmdZ  = surfaceMissileRuntimeWip13C6(m)?surfaceMissileCommandAimHeightWip15C(m,tr.x,tr.y,Math.max(0,Number(surfaceMissileRuntimeWip13C6(m).aimHeightM)||Number(tr.z)||0)):tr.z;
      m.lastCmdVz = (tr.vz ?? 0);
      m.iogAge = 0;
      m.afterClosestTimer = 0;
      m.closestKm = 999;
      if(m.guidanceCore!=='v1' && m.state !== 'ACTIVE' && m.state !== 'SARH') m.state = 'DL';
    } else {
      if(m.guidanceCore!=='v1' && m.state !== 'ACTIVE') m.state = 'IOG';
      m.iogAge += dt;
    }

    // pitbull
    const refX = tr ? tr.x : m.lastCmdX;
    const refY = tr ? tr.y : m.lastCmdY;
    const refZ = tr ? (surfaceMissileRuntimeWip13C6(m)?surfaceMissileCommandAimHeightWip15C(m,tr.x,tr.y,Math.max(0,Number(surfaceMissileRuntimeWip13C6(m).aimHeightM)||Number(tr.z)||0)):tr.z) : (m.lastCmdZ ?? OWN_ALT_M);
    const dKmToRef = dist3Km(_b1Own?metersToWorld(_b1Own.posM.x):m.x,_b1Own?metersToWorld(_b1Own.posM.y):m.y,_b1Own?_b1Own.posM.z:(m.z ?? OWN_ALT_M),refX,refY,refZ);
 // ===== NEW GUIDANCE: Clean VLS → Midcourse → Terminal =====
    var cmdX=m.lastCmdX??(_b1Own?metersToWorld(_b1Own.posM.x):m.x);
    var cmdY=m.lastCmdY??(_b1Own?metersToWorld(_b1Own.posM.y):m.y);
    var cmdZ = m.lastCmdZ ?? OWN_ALT_M;
    var cmdVx = m.lastCmdVx ?? 0;
    var cmdVy = m.lastCmdVy ?? 0;
    var cmdVz = m.lastCmdVz ?? 0;
    var cueBearing = null;
    var termBlend = 0;
    // Save previous frame command for smoothing
    var prevCmdX = m._prevCmdX ?? cmdX;
    var prevCmdY = m._prevCmdY ?? cmdY;
    var prevCmdZ = m._prevCmdZ ?? cmdZ;
    {

    const mslAlt=_b1Own?_b1Own.posM.z:(m.z??0),ownX=_b1Own?metersToWorld(_b1Own.posM.x):m.x,ownY=_b1Own?metersToWorld(_b1Own.posM.y):m.y;
    var isESSM = m.isESSM ?? false;
    // WIP41: fixed minClimbAlt heuristics retired.  The registry-backed adaptive trajectory
    // planner below owns turn-start / attitude-complete / forward-commit altitude continuously.

    // Track reference: where is the target?
    const tgtX = tr ? tr.x : cmdX;
    const tgtY = tr ? tr.y : cmdY;
    const tgtZ = tr ? (surfaceMissileRuntimeWip13C6(m)?surfaceMissileCommandAimHeightWip15C(m,tr.x,tr.y,Math.max(0,Number(surfaceMissileRuntimeWip13C6(m).aimHeightM)||Number(tr.z)||0)):(tr.z ?? 5000)) : cmdZ;
    const tgtVx = tr ? (tr.vx ?? 0) : cmdVx;
    const tgtVy = tr ? (tr.vy ?? 0) : cmdVy;
    const tgtVz = tr ? (tr.vz ?? 0) : cmdVz;
    const rangeKm = dist3Km(ownX,ownY,mslAlt,tgtX,tgtY,tgtZ);
    m._rangeKmCached = rangeKm;
    const range2dKm = worldToKm(dist(ownX,ownY,tgtX,tgtY));
    const mslSpdMps = Math.max(50, worldSpeedToMps(m.speed));

    // Pre-compute target characteristics (needed by both VLS and midcourse)
    const tgtSpdMpsEarly = worldSpeedToMps(Math.hypot(tgtVx, tgtVy));
    // earlyHighDiver: permissive early detection (for VLS + midcourse start)
    var isHighDiverEarly = (tgtSpdMpsEarly > 450 && tgtVz < -130 && tgtZ > 4000);
    // SI-REFRACTOR WIP7: fast/high inbound threats (Kh-32-like geometry) must NOT make
    // an area-defense missile chase every instantaneous altitude/track update at long range.
    // Classification is purely kinematic: no hidden weapon-label knowledge is required.
    var isFastHighInbound = (!isESSM && tgtSpdMpsEarly > 850 && tgtZ > 9000 && rangeKm > 25);
    m._fastHighInbound = isFastHighInbound;

    // WIP41 adaptive launch/loft plan — same registry result drives both VLS transition and midcourse energy management.
    {
      const mVx=_b1Own?_b1Own.velMps.x:worldSpeedToMps(m.vx??0),mVy=_b1Own?_b1Own.velMps.y:worldSpeedToMps(m.vy??0),mVz=_b1Own?_b1Own.velMps.z:(m.vz??0),tVx=worldSpeedToMps(tgtVx),tVy=worldSpeedToMps(tgtVy),tVz=tgtVz;
      const dx=worldToMeters(tgtX-ownX),dy=worldToMeters(tgtY-ownY),dz=tgtZ-mslAlt,r=Math.max(1,Math.hypot(dx,dy,dz));
      const ux=dx/r,uy=dy/r,uz=dz/r,closing=Math.max(0,-((tVx-mVx)*ux+(tVy-mVy)*uy+(tVz-mVz)*uz));
      const tgoPlan=clamp(r/Math.max(180,closing||mslSpdMps),.2,120);
      const tgtAltSigmaM=tr?trackCovarianceMetrics(tr).altSigmaM:0;
      _samBuildAdaptiveTrajectoryPlan(m,{rangeKm:r/1000,horizRangeM:Math.hypot(dx,dy),tgoS:tgoPlan,closingMps:closing,mslAltM:mslAlt,tgtAltM:tgtZ,tgtAltSigmaM,tgtVzMps:tgtVz,vMps:mslSpdMps,qPa:m.qbar??0});
    }

    // ===== PHASE 1: CELL CLEAR → ADAPTIVE 3-D LAUNCH TRANSITION =====
    if(m.vlsPhase){
      m._vlsPhaseAgeS=(m._vlsPhaseAgeS??0)+dt;
      const cfg=_samVlsControlConfig(m,isESSM);
      const lead=_samLeadPointForLaunch(m,tr,tgtX,tgtY,tgtZ,tgtVx,tgtVy,tgtVz,mslSpdMps,isESSM);
      const cor=_samSetLaunchCorridorCommand(m,lead,isESSM,'VLS');
      cmdX=cor.x;cmdY=cor.y;cmdZ=cor.z;cmdVx=tgtVx;cmdVy=tgtVy;cmdVz=tgtVz;
      m._vlsCorridorActive=true;
      m._vlsPitchStarted=(mslAlt>=cfg.launchClearAltM);

      const hdgErr=Math.abs(angNorm(cor.bearing-(m.heading??0)));
      const pitchErr=Math.abs(cor.desiredPitch-(m.pitch??0));
      const attitudeReady=m._vlsPitchStarted&&mslAlt>=cfg.turnStartAltM&&hdgErr<=cfg.headingTol&&pitchErr<=cfg.pitchTol;
      const missedAttitudeGate=isESSM&&mslAlt>=cfg.attitudeCompleteAltM&&!attitudeReady; // WIP44: ESSM keeps a hard low-altitude TVC checkpoint; SM-2 alignment altitude is a 6DOF result, not a commanded gate.
      m._vlsAttitudeRequirement={altM:mslAlt,targetAltM:cfg.attitudeCompleteAltM,attitudeReady,missed:missedAttitudeGate,hdgErr,pitchErr,desiredPitch:cor.desiredPitch};
      if(isESSM)m._vlsEightMeterRequirement=m._vlsAttitudeRequirement; // compatibility diagnostic alias
      if(missedAttitudeGate&&!m._vlsAttitudeWarned){m._vlsAttitudeWarned=true;debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} 6DOF alignment envelope exceeded at ${mslAlt.toFixed(1)}m (diagnostic ${cfg.attitudeCompleteAltM.toFixed(1)}m) body=${((m.pitch??0)*180/Math.PI).toFixed(1)}° target=${(cor.desiredPitch*180/Math.PI).toFixed(1)}° err=${(pitchErr*180/Math.PI).toFixed(1)}°`);}

      // As soon as the body is on the lead line, transition to forward-commit.  This may happen
      // before 8 m; if it has not happened by 8 m the hard-over simply CONTINUES (no timer cheat).
      if(!isESSM && (m._vlsPhaseAgeS??0)>25 && !m._vlsDeadlockWarned){
        m._vlsDeadlockWarned=true;
        debugLog(`v1: M${m.id} VLS turnover >25s (diagnostic only) alt=${mslAlt.toFixed(0)}m body=${rad2deg(m.pitch??0).toFixed(1)}° target=${rad2deg(cor.desiredPitch).toFixed(1)}° roll=${rad2deg(m.roll??0).toFixed(1)}°`);
      }
      if(attitudeReady){
        // WIP75: freeze the LAST VLS lead solution exactly once at launch-transition exit.
        // Field names follow the measurement instruction; all values are from this same instant.
        if(!isESSM && m._pipSnapAltM==null){
          m._pipSnapAltM=lead.z;
          m._pipSnapTgo=lead.tgo;
          m._pipSnapRangeKm=horizDistKm(ownX,ownY,tgtX,tgtY);
          m._pipSnapTgtAltM=tgtZ;
          m._pipSnapTgtVzMps=tgtVz;
          m._pipSnapLifeS=m.life??0;
        }
        m._sam6dofAlignAltM=mslAlt;
        m.vlsPhase=false;
        m.pitchoverPhase=true;
        m.pitchoverTimer=0;
        m.pitchoverDuration=cfg.pitMaxS;
        m.pitchoverAimX=lead.x;m.pitchoverAimY=lead.y;m.pitchoverAimZ=lead.z;
        debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} BODY PITCHOVER complete alt=${mslAlt.toFixed(1)}m body=${((m.pitch??0)*180/Math.PI).toFixed(1)}° target=${(cor.desiredPitch*180/Math.PI).toFixed(1)}°`);
      }
    }

    // ===== PHASE 1b: FORWARD-COMMIT — BODY ALIGNED, VELOCITY VECTOR CATCHES UP =====
    else if(m.pitchoverPhase){
      const cfg=_samVlsControlConfig(m,isESSM);
      m.pitchoverTimer=(m.pitchoverTimer??0)+dt;
      const lead=_samLeadPointForLaunch(m,tr,tgtX,tgtY,tgtZ,tgtVx,tgtVy,tgtVz,mslSpdMps,isESSM);
      const cor=_samSetLaunchCorridorCommand(m,lead,isESSM,'PITCHOVER');
      cmdX=cor.x;cmdY=cor.y;cmdZ=cor.z;cmdVx=tgtVx;cmdVy=tgtVy;cmdVz=tgtVz;
      m.pitchoverAimX=lead.x;m.pitchoverAimY=lead.y;m.pitchoverAimZ=lead.z;

      const desiredH=cor.bearing,hdgErr=Math.abs(angNorm(desiredH-(m.heading??0)));
      const pitchErr=Math.abs(cor.desiredPitch-(m.pitch??0));
      const vHx=_b1Own?_b1Own.velMps.x:worldSpeedToMps(m.vx??0),vHy=_b1Own?_b1Own.velMps.y:worldSpeedToMps(m.vy??0),forwardMps=Math.hypot(vHx,vHy);
      const attitudeReady=hdgErr<=cfg.headingTol&&pitchErr<=cfg.pitchTol;
      // WIP59: BODY alignment is not enough for a clean hand-off.  ESSM's TVC can rotate the body
      // much faster than the flight path, so the old gate could release the launch controller with
      // 15-25deg of residual velocity-vector error. Full PN then demanded an abrupt opposite-G pull,
      // causing an AoA departure / sea dive. Keep forward-commit until the velocity vector itself is
      // inside the launch corridor. SM-2 keeps its proven WIP56 gate unchanged.
      const velPitchErr=Math.abs((m.velPitch??0)-cor.desiredPitch);
      const velHdg=Math.atan2(vHy,vHx),velHdgErr=Math.abs(angNorm(cor.bearing-velHdg));
      const vectorAligned=!isESSM||(velPitchErr<=deg(9)&&velHdgErr<=deg(12));
      const surfaceVectorAligned=surfaceLaunchVectorAlignedWip13C6(m,isESSM,velPitchErr,velHdgErr,cfg);
      // WIP60: ESSM hand-off is relative to the 3-D intercept corridor, not an absolute 'must be near level'
      // pitch. A +55deg high-angle shot is valid if its BODY and velocity vector are actually aligned there.
      const pitchEnvelopeReady=isESSM?vectorAligned:Math.abs(m.velPitch??0)<=cfg.maxVelExit;
      const velocityReady=forwardMps>=cfg.minForwardMps&&vectorAligned&&surfaceVectorAligned&&pitchEnvelopeReady;
      const clearanceReady=mslAlt>=cfg.exitAltM;
      const minTimeDone=m.pitchoverTimer>=cfg.pitMinS;
      const deadlineExceeded=m.pitchoverTimer>=cfg.pitMaxS;
      m._pitchoverGate={attitudeReady,velocityReady,vectorAligned:vectorAligned&&surfaceVectorAligned,velPitchErr,velHdgErr,clearanceReady,minTimeDone,deadlineExceeded,hdgErr,pitchErr,forwardMps};
      if(deadlineExceeded&&!m._pitchoverDeadlineWarned){m._pitchoverDeadlineWarned=true;debugLog(`v1: E${m.id} FORWARD-COMMIT deadline exceeded — launch controller retains authority`);}
      if(minTimeDone&&attitudeReady&&velocityReady&&clearanceReady){
        m.pitchoverPhase=false;
        m.pitchoverDone=true;
        m._vlsCorridorActive=false;
        m._pitchoverCompleteAt=m.life;
        if(m.isESSM)wip136JettisonEssmTvc(m,'PITCHOVER_COMPLETE');
        debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} FORWARD-COMMIT complete t=${m.pitchoverTimer.toFixed(2)}s alt=${mslAlt.toFixed(1)}m body=${((m.pitch??0)*180/Math.PI).toFixed(1)}° vel=${((m.velPitch??0)*180/Math.PI).toFixed(1)}° Vh=${forwardMps.toFixed(0)}m/s`);
      }
    }

    // ===== PHASE 2: MIDCOURSE (fly toward intercept point) =====
    else {
      const tgtSpdMps = worldSpeedToMps(Math.hypot(tgtVx, tgtVy));
      // Better closing speed: use actual relative velocity along LOS (3D)
      const losX=tgtX-ownX,losY=tgtY-ownY,losZ=tgtZ-mslAlt;
      const losXm = worldToMeters(losX);
      const losYm = worldToMeters(losY);
      const losLen3D = Math.sqrt(losXm*losXm + losYm*losYm + losZ*losZ);
      // Missile velocity (world frame, m/s)
      const mVxMps=_b1Own?_b1Own.velMps.x:worldSpeedToMps(m.vx??0);
      const mVyMps=_b1Own?_b1Own.velMps.y:worldSpeedToMps(m.vy??0);
      const mVzMps=_b1Own?_b1Own.velMps.z:(m.vz??0);
      // Target velocity (already m/s for vz, px/s for vx/vy)
      const tVxMps = worldSpeedToMps(tgtVx);
      const tVyMps = worldSpeedToMps(tgtVy);
      const tVzMps = tgtVz;
      // Closing rate = -(dV · LOS_unit)
      let closingSpd;
      if(losLen3D > 1){
        const ux = losXm/losLen3D, uy = losYm/losLen3D, uz = losZ/losLen3D;
        const dvx = mVxMps - tVxMps, dvy = mVyMps - tVyMps, dvz = mVzMps - tVzMps;
        const closingFromLOS = (dvx*ux + dvy*uy + dvz*uz);
        closingSpd = Math.max(200, closingFromLOS);
      } else {
        closingSpd = Math.max(200, mslSpdMps + tgtSpdMps * 0.4);
      }
      // 3D tgo using LOS-based closing speed (single-shot; closingSpd already accounts for relative velocity)
      // Previous iterative version had wrong formula (used absolute target velocity instead of relative)
      // Result: frame-to-frame tgoEst jitter → command jitter → terminal miss
      const _tgoRawLosS = losLen3D / closingSpd;
      const tgoEst = clamp(_tgoRawLosS, 0.1, 30);
      m._tgoIter = tgoEst;
      // WIP81 observation/input split: preserve the uncapped value for the Kappa-only horizon.
      // No legacy guidance path reads this field.
      m._wip81KappaTgoRawS = _tgoRawLosS;

      // Detect fast+close target: skip lofting, minimal lead, direct intercept
      const isFastClose = !isESSM && ((tgtSpdMps > 400 && rangeKm < 60) || (Math.abs(tgtVz) > 100 && rangeKm < 60));
      // Kh-32-type high-diver: high speed + steep dive + high altitude
      const isHighDiver = isHighDiverEarly;
      m.apnTargetIsHighDiver = isHighDiver;
      // === DIRECT IMPACT MODE: enhanced gating ===
      // Old criteria (range only) was too eager → poor track → bad predictions
      // New: require track/seeker quality + range + vertical-tgo reasonableness
      var isDirectImpact = false;
      var diReason = '';
      {
        // Track quality: SARH > essmActive > DL > IOG
        const trackQuality = m.sarhAlive ? 1.0 :
                             m.essmActiveSeeker ? 0.85 :
                             m.dlAlive ? 0.70 :
                             (m.seekerLocked ? 0.85 : 0.30);
        // Vertical tgo: how soon does vertical component close?
        // If |vz_rel| small, vertical tgo is huge → keep predictive mode
        const vzRelAbs=Math.max(1,Math.abs(tgtVz-mVzMps));
        const vertTgo = Math.abs(tgtZ - mslAlt) / vzRelAbs;
        // ESSM inside 25km with good track: direct impact (short-range interceptor)
        // SM-2 with HD + range reasonable + good track: also direct
        // But if track quality low OR range too far: keep predictive
        if(isESSM && rangeKm < 25 && trackQuality >= 0.70){
          isDirectImpact = true;
          diReason = 'ESSM-close';
        } else if(!isESSM && rangeKm < 30 && trackQuality >= 0.70 &&
                  ((isHighDiver && Math.abs(tgtZ-mslAlt)<2500) || vertTgo < 3.5)){
          // WIP63: do not drop the predictive/loft controller merely because SARH is good.
          // A high-diver may still be several kilometres above the missile; direct-impact that early
          // forces a late pitch reversal and is a reliable recipe for an under-pass.
          isDirectImpact = true;
          diReason = 'SM2-HDshort-vertical-ready';
        } else if(rangeKm < 15 && trackQuality >= 0.50){
          // Very close: direct impact even with weaker track (we're almost there)
          isDirectImpact = true;
          diReason = 'terminal-close';
        } else if(rangeKm < 40 && trackQuality >= 0.80 && !isHighDiver){
          // Regular targets with high quality track
          isDirectImpact = true;
          diReason = 'high-quality';
        }
        m._diTrackQ = trackQuality;
        m._diVertTgo = vertTgo;
        m._diReason = diReason;
      }
      m.directImpactMode = isDirectImpact;
      // One-shot debug: log DI entry with reason + quality
      if(isDirectImpact && !m._diEntered){
        m._diEntered = true;
        const _mLbl = m.isESSM ? 'E' : 'M';
        notify(`🎯 DI: ${_mLbl}${m.id} r=${rangeKm.toFixed(1)}km q=${(m._diTrackQ*100).toFixed(0)}% (${diReason})`);
      }

      // Lead: predict where target will be at intercept
      // Detect LOS rate (crossing target = high LOS rate vs LOS)
      // Crossing detection: component of target velocity perpendicular to LOS
      var crossingFac = 0;
      if(losLen3D > 100){
        const uxL = losXm/losLen3D, uyL = losYm/losLen3D;
        // Target velocity projected on LOS vs perp to LOS
        const tgtLOSdot = tVxMps * uxL + tVyMps * uyL;  // along LOS (m/s)
        const tgtPerpX = tVxMps - tgtLOSdot * uxL;
        const tgtPerpY = tVyMps - tgtLOSdot * uyL;
        const tgtPerpMag = Math.sqrt(tgtPerpX*tgtPerpX + tgtPerpY*tgtPerpY);
        // Normalize: 0 = head-on/tail-chase, 1 = pure crossing
        const tgtSpdH = Math.max(1, Math.sqrt(tVxMps*tVxMps + tVyMps*tVyMps));
        crossingFac = clamp(tgtPerpMag / tgtSpdH, 0, 1);
      }
      m._crossingFac = crossingFac;

      var leadScale;
      if(isESSM){
        leadScale = clamp(0.75 + 0.15 * clamp(rangeKm / 15, 0, 1), 0.75, 0.90);
        leadScale += crossingFac * 0.08;  // reduced from 0.15
        if(isHighDiver) leadScale += 0.05;  // reduced from 0.10
        leadScale = clamp(leadScale, 0.70, 0.95);  // clamp down from 1.05
      } else if(isFastClose){
        leadScale = clamp(rangeKm / 60, 0.1, 0.4);
        leadScale += crossingFac * 0.10;
      } else {
        leadScale = 0.85;
        leadScale += crossingFac * 0.06;  // reduced from 0.10
        if(isHighDiver) leadScale += 0.05;
        leadScale = clamp(leadScale, 0.5, 0.95);  // clamp down from 1.02
      }
      // WIP63: SM-2 vertical-intercept budget.  When a high target is still far above the missile,
      // move the predicted meeting point inward for an inbound threat, reducing outward travel while reserving geometry for climb.
      m._sm2VerticalBudget=null;
      if(!isESSM){
        const predFac=isHighDiver?1.0:0.72;
        let predTimeS=tgoEst*predFac;
        const currentGapM=Math.max(0,tgtZ-mslAlt);
        // WIP63: a heavy SM-2 below a steep diver must not predict the target all the way down
        // to full horizontal TGO and then flatten early.  Bound vertical look-ahead while a real
        // altitude debt remains; the reachable-altitude limiter downstream keeps this from becoming
        // a raw-current-altitude chase.
        if(isHighDiver && currentGapM>500){
          const gap01=_samSmooth01(clamp((currentGapM-500)/6500,0,1));
          const verticalHorizonS=lerp(4.2,1.8,gap01);
          predTimeS=Math.min(predTimeS,verticalHorizonS);
        }
        const predAltM=Math.max(15,tgtZ+tgtVz*predTimeS);
        const deficitM=Math.max(0,predAltM-mslAlt);
        const requiredMps=deficitM/Math.max(2.5,Math.min(tgoEst,8));
        const alt01=_samUpWindow(predAltM,9000,22000);
        const need01=_samUpWindow(requiredMps,100,340);
        const range01=_samUpWindow(rangeKm,22,55);
        const climb01=clamp(alt01*need01*range01,0,1);
        if(climb01>0.001) leadScale=clamp(leadScale*lerp(1.0,1.10,climb01),0.5,0.99);
        m._sm2VerticalBudget={predictedAltM:predAltM,predictionTimeS:predTimeS,currentGapM,deficitM,requiredMps,alt01,need01,range01,climb01};
      }
      m._leadScaleApplied = leadScale;

      // pipX/Y with APN horizontal accel correction
      // apnAx / apnAy are target horizontal accelerations (m/s², world frame)
      // But tgtVx/tgtVy are in px/s, so conversion needed
      var pipX = tgtX + tgtVx * tgoEst * leadScale;
      var pipY = tgtY + tgtVy * tgoEst * leadScale;
      // APN horizontal accel: only at midcourse (>5km)
      // In terminal, small apnAx/y estimates can spiral pip around and fight PN
      if(rangeKm > 5){
        if(m.apnAx != null && Math.abs(m.apnAx) > 0.5){
          const apnAxLim = clamp(m.apnAx, -120, 120);
          pipX += metersToWorld(0.5 * apnAxLim * tgoEst * tgoEst) * leadScale;
        }
        if(m.apnAy != null && Math.abs(m.apnAy) > 0.5){
          const apnAyLim = clamp(m.apnAy, -120, 120);
          pipY += metersToWorld(0.5 * apnAyLim * tgoEst * tgoEst) * leadScale;
        }
      }
      const isDivingMid = (tgtVz < -100);
      const absVz = Math.abs(tgtVz);
      // Vertical speed factor: more lead for faster descents, capped
      const vzSpeedFac = clamp(absVz / 400, 0, 1); // 0 at 0m/s, 1 at 400m/s+

      var vLeadScale;
      if(isHighDiver){
        // ESSM may use nearly full vertical prediction.  SM-2 is much heavier and can arrive at
        // horizontal CPA before it has paid a multi-kilometre altitude debt; while it is still
        // materially below the diver, use the same bounded vertical horizon as the trajectory budget.
        if(!isESSM && m._sm2VerticalBudget){
          vLeadScale=clamp((m._sm2VerticalBudget.predictionTimeS??tgoEst)/Math.max(.1,tgoEst),.12,1.0);
        }else{
          const hdLead = (m.seekerLocked || m.sarhAlive || m.essmActiveSeeker || m.dlAlive) ? 1.00 : 0.95;
          vLeadScale = hdLead;
        }
      } else if(isESSM){
        // ESSM non-diver: aggressive lead
        vLeadScale = clamp(0.6 + vzSpeedFac * 0.15, 0.6, 0.75);
      } else if(isDivingMid){
        // General diving: proportional to speed
        vLeadScale = clamp(0.3 + vzSpeedFac * 0.25, 0.3, 0.6);
      } else if(isFastClose){
        vLeadScale = clamp(rangeKm / 60, 0.05, 0.3);
      } else {
        vLeadScale = 0.7;
      }
      // Compute pipZ: direct impact mode OR 2-stage for high-divers
      // minPipZ: floor for pipZ (prevent missile diving below sea)
      // CRITICAL: must be BELOW target altitude (otherwise missile aims above target)
      // Sea-skimmer fix: if tgtZ low, minPipZ low too
      var minPipZ;
      if(isHighDiver || (isESSM && isDivingMid)){
        minPipZ = 15;
      } else {
        // Default sea-floor protection vs sea-skimmer accommodation
        // tgtZ at 10m → minPipZ should be 5m, not 50m
        // tgtZ at 100m+ → standard 50m floor
        minPipZ = clamp(Math.min(tgtZ - 5, 50 + absVz * 0.1), 5, 200);
      }
      // ===== pipZ: prediction clamped to missile's reachable altitude =====
      // Key insight from debug data: cmdZ was 10499m but missile could only climb
      // to ~8800m in the time available. commanding unreachable altitude causes
      // missile to chase forever while target descends past it.
      //
      // Solution: cap pipZ at missile's realistic reach envelope.

      const rawPredictedZ = tgtZ + tgtVz * tgoEst * vLeadScale;
      let zIntercept = rawPredictedZ;
      if(m.apnAz != null && Math.abs(m.apnAz) > 1.0){
        const apnAzLim = clamp(m.apnAz, -150, 150);
        zIntercept += 0.5 * apnAzLim * tgoEst * tgoEst * vLeadScale;
      }
      // WIP63 actuator-aware high-side bias: when a heavy SM-2 is still materially below a steep
      // diver, retain a bounded fraction of the CURRENT altitude gap instead of assuming the target
      // will descend through the missile's plane before horizontal CPA.  Reachability and target-alt
      // clamps below remain authoritative, so this cannot command an impossible 30 km chase.
      if(isHighDiver && !isESSM && tgtZ>mslAlt+300){
        const currentGap=tgtZ-mslAlt;
        const gapBias=clamp(currentGap*0.30,0,1600);
        zIntercept+=gapBias;
        m._sm2HighSideBiasM=gapBias;
      }else if(!isESSM){
        m._sm2HighSideBiasM=0;
      }
      // Physical bounds (use adaptive minPipZ as floor — sea-skimmer fix)
      const bottomFloor = minPipZ;
      const topCeiling = Math.max(bottomFloor + 50, tgtZ);
      if(topCeiling > bottomFloor){
        zIntercept = clamp(zIntercept, bottomFloor, topCeiling);
      } else {
        zIntercept = Math.max(bottomFloor, zIntercept);
      }

      // === Missile reachable altitude cap (soft) ===
      // Only restrict if genuinely impossible — use generous climb rate
      // For HD intercepts, missile may need to climb beyond steady-state profile
      const mslClimbCap = (m.burnLeft > 0) ? 500 : 350;
      const mslReachAlt = mslAlt + mslClimbCap * tgoEst * 1.1;  // 10% margin
      const mslCurrentReach=mslAlt+Math.max(0,mVzMps)*tgoEst;
      const realisticTop = Math.max(mslReachAlt, mslCurrentReach);
      // Only cap if zIntercept EXCEEDS reachable (otherwise don't interfere)
      if(zIntercept > realisticTop){
        zIntercept = realisticTop;
      }

      var pipZ;
      if(isDirectImpact){
        pipZ = Math.max(minPipZ, zIntercept);
      } else if(isHighDiver){
        const belowK = isESSM ? 15 : 20;
        const belowMin = isESSM ? 40 : 60;
        const belowMax = isESSM ? 500 : 800;
        let belowMargin = clamp(rangeKm * belowK, belowMin, belowMax);
        if(!isESSM){
          // WIP63: 'meet the diver from below' is only useful if the interceptor is already near
          // or above the predicted collision altitude.  If SM-2 is kilometres below, subtracting
          // another 60-800 m biases the solution downward twice and promotes an under-pass.
          const relAltM=mslAlt-zIntercept;
          const belowGeomScale=_samSmooth01(clamp((relAltM+250)/1750,0,1));
          belowMargin*=belowGeomScale;
          m._sm2BelowMarginScale=belowGeomScale;
        }
        pipZ = Math.max(minPipZ, zIntercept - belowMargin);
      } else {
        pipZ = Math.max(minPipZ, zIntercept);
      }
      m._pipZApplied = pipZ;
      m._zInterceptCalc = zIntercept;
      m._mslReachAlt = realisticTop;
      m._lastTrZ = tgtZ;
      m._lastTrVz = tgtVz;

      // === WIP41 REGISTRY-DRIVEN ADAPTIVE LOFT / ALTITUDE GUIDANCE ===
      // The launch planner and the midcourse energy manager share the same continuously evaluated
      // urgency/loftDemand state.  No hard target-label switch and no ESSM-loft=0 special case.
      let guidanceZ=pipZ;
      const traj=m._samTrajPlan, loftProf=_samTrajectoryProfileFor(m)?.loft||{};
      const urgency=traj?.urgency??0, loftDemand0=traj?.loftDemand??0;
      let terminalFade=1;
      if(traj){
        const startR=traj.terminalBlendStartKm??20,fullR=traj.terminalBlendFullKm??8;
        terminalFade=(rangeKm>=startR)?1:(rangeKm<=fullR?0:_samSmooth01((rangeKm-fullR)/Math.max(1e-6,startR-fullR)));
      }
      let loftDemand=clamp(loftDemand0*terminalFade,0,1);
      // A good seeker does not instantly cancel energy management at long range; it only owns the
      // terminal convergence when the registry fade reaches the endgame.
      if(m._v1TerminalActive)loftDemand=0;
      m._hdEnergyShelfActive=false;

      if(!isDirectImpact && traj && loftDemand>0.005){
        let cruiseAlt=Math.max(pipZ,traj.cruiseAltM??pipZ);
        // WIP63 high-target intercept shelf.  WIP61's 7-11 km cap left too much vertical debt
        // for 20-30 km divers, so the missile arrived close in range but far below the intercept.
        // Use the planner's bounded 12-18 km shelf when the vertical budget says the climb is needed.
        if(!isESSM && rangeKm>25 && (isFastHighInbound||isHighDiver)){
          const dynShelf=traj.highTargetShelfAltM??traj.cruiseAltM??cruiseAlt;
          const predAlt=m._sm2VerticalBudget?.predictedAltM??traj.highPredTargetAltM??tgtZ;
          const hardCeil=Math.max(9000,Math.min(19000,predAlt-900));
          const shelf=clamp(dynShelf,7000,hardCeil);
          cruiseAlt=Math.max(cruiseAlt,shelf);
          m._hdEnergyShelfActive=true;m._hdEnergyShelfAltM=shelf;
        }
        guidanceZ=lerp(pipZ,cruiseAlt,loftDemand);
      }
      // Direct/urgent paths naturally converge to PIP because loftDemand is suppressed by urgency.
      // The explicit terminal fade makes the same happen as seeker endgame approaches.
      guidanceZ=lerp(pipZ,guidanceZ,terminalFade);

      // ===== WIP65: SM-2 HIGH-DIVER REACHABLE ENERGY CORRIDOR =====
      // SARH may be measurement-authoritative before terminal energy geometry is good. Keep the
      // earned energy shelf as a partial trajectory reference while a high target is still descending
      // above it, then release at the profile-derived terminal range. This prevents a late 30 km zoom
      // after WIP64 removed the old fake high-altitude q floor.
      m._sm2EnergyCorridor=null;
      if(!isESSM){
        const cProf=loftProf||{};
        if(Number.isFinite(traj?.highTargetShelfAltM) && (traj?.highClimb01??0)>0.01){
          m._sm2EnergyShelfLatchM=traj.highTargetShelfAltM;
        }
        const latchedShelf=m._sm2EnergyShelfLatchM;
        const terminalKm=m._v1Profile?.terminalRangeKm??11;
        const endgameKm=m._v1Profile?.endgameRangeKm??3;
        const releaseKm=Math.max(
          terminalKm*(cProf.highTargetCorridorReleaseTerminalScale??1.10),
          endgameKm*(cProf.highTargetCorridorReleaseEndgameScale??2.50)
        );
        const descendingHigh=(isHighDiver||isFastHighInbound) && tgtVz<-(cProf.highTargetDiveMinMps??80);
        if(descendingHigh && Number.isFinite(latchedShelf) && rangeKm>releaseKm){
          const vNowMps=Math.max(100,Math.hypot(mVxMps,mVyMps,mVzMps));
          const qReservePa=cProf.highTargetCorridorQReservePa??14000;
          const qCeilingM=altitudeForDynamicPressureM(vNowMps,qReservePa,cProf.highTargetCorridorSpeedReserve??0.92);
          const minM=cProf.highTargetCorridorMinM??10000,maxM=cProf.highTargetCorridorMaxM??22000;
          const qMarginM=cProf.highTargetCorridorQCeilingMarginM??1200;
          const corridorAltM=clamp(Math.min(latchedShelf,qCeilingM-qMarginM),minM,maxM);
          const targetAboveM=tgtZ-corridorAltM;
          const nearM=cProf.highTargetCorridorTargetGapNearM??2500;
          const fullM=Math.max(nearM+1,cProf.highTargetCorridorTargetGapFullM??7000);
          const targetGapHold=_samSmooth01(clamp((targetAboveM-nearM)/(fullM-nearM),0,1));
          const rangeRelease01=_samSmooth01(clamp((rangeKm-releaseKm)/Math.max(1,terminalKm*.55),0,1));
          const hold01=targetGapHold*rangeRelease01*clamp(cProf.highTargetCorridorHoldStrength??0.92,0,1);
          if(hold01>0.001){
            guidanceZ=lerp(guidanceZ,corridorAltM,hold01);
            m._hdEnergyShelfActive=true;
            m._hdEnergyShelfAltM=corridorAltM;
          }
          m._sm2EnergyCorridor={active:hold01>0.001,corridorAltM,qCeilingM,qReservePa,targetAboveM,hold01,releaseKm,latchedShelfM:latchedShelf};
        }else if(rangeKm<=Math.max(endgameKm,releaseKm*.55)){
          m._sm2EnergyShelfLatchM=null;
        }
      }
      m._samLoftUrgency=urgency;m._samLoftDemand=loftDemand;m._samLoftCruiseAltM=traj?.cruiseAltM??pipZ;
      m._samLoftProfileId=traj?.profileId??null;m._samLoftRmaxKm=traj?.rmaxKm??null;m._samLoftQWeight=traj?.qWeight??null;

      // ===== Momentum anticipation (unified — applies to all phases) =====
      // If missile's ballistic projection will overshoot intercept point, drop cmdZ
      // This is the ONLY vertical clamp beyond pipZ itself.
      {
        const mslVz=mVzMps;
        const lookAhead = Math.min(tgoEst, 8.0);
        // Simple linear projection (no gravity adjustment needed — pipZ is physical)
        const projectedAlt = mslAlt + mslVz * lookAhead;
        // SI-REFRACTOR WIP5: compare momentum against the CURRENT vertical aim.
        // The old guard compared projectedAlt to zIntercept (target altitude) even during
        // midcourse loft. Any intentional climb was therefore classified as an overshoot
        // and immediately crushed back toward sea level. In terminal guidanceZ naturally
        // converges to zIntercept, so the same guard still works there.
        const verticalAimRef = Math.max(minPipZ, guidanceZ);
        if(projectedAlt > verticalAimRef + 50){
          const overshoot = projectedAlt - verticalAimRef;
          const dropAmount = Math.min(1500, overshoot);
          guidanceZ = Math.max(minPipZ, guidanceZ - dropAmount);
        }
        m._projAlt = projectedAlt;
      }

      // WIP61 SM-2 apex capture: arrest upward momentum before the missile sails kilometres above
      // the energy shelf.  This is a flight-path command only; 6DOF/TVC/aero still determine what it can achieve.
      m._sm2ApexCapture=null;
      if(!isESSM && !m._v1TerminalActive && rangeKm>24){
        const vzUp=Math.max(0,mVzMps),aimAlt=Math.max(minPipZ,guidanceZ),proj4=mslAlt+vzUp*4.0,overshoot=proj4-aimAlt;
        if(vzUp>80 && overshoot>600){
          const u=_samSmooth01(clamp((overshoot-600)/4200,0,1));
          const capPitchDeg=lerp(10,-6,u);
          m._sm2ApexCapture={active:true,vzUp,aimAlt,proj4,overshoot,capPitchDeg};
        }
      }

      if(m._loftB4&&m._loftB4.mode!=='DIRECT'){
        guidanceZ=m._loftB4.phase==='DIVE'?pipZ:m._loftB4.shelfM;
        m._sm2ApexCapture=null;m._sm2EnergyCorridor=null;m._sm2VerticalCapture=null;
      }
      guidanceZ = Math.max(surfaceSm2GuidanceFloorWip13C5(m), guidanceZ);

      // Set guidance command
      const dlActive = m.dlAlive || m.sarhAlive;
      var blendRate;
      if(isESSM){
        blendRate = 0.95;
      } else if(isFastClose || isHighDiver){
        blendRate = 0.95;
      } else {
        blendRate = dlActive ? 0.92 : 0.70;
      }
      // Unified 3D blend: very small axis differential only
      // (removed aggressive XY/Z split — it caused axis fighting)
      var blendRateXY = blendRate;
      var blendRateZ  = blendRate;
      if(isHighDiver){
        // HD: Z tracking must be very fast to follow descending target
        // prevCmdZ carrying stale (higher) value causes missile to lag
        blendRateXY = Math.min(0.99, blendRate + 0.005);
        blendRateZ  = 0.99;  // near-instant cmdZ = guidanceZ
      }
      cmdX = lerp(cmdX, pipX, blendRateXY);
      cmdY = lerp(cmdY, pipY, blendRateXY);
      cmdZ = lerp(cmdZ, guidanceZ, blendRateZ);
      cmdVx = tgtVx;
      cmdVy = tgtVy;
      cmdVz = tgtVz;
      cmdZ = Math.max(15, cmdZ);
      // Sea-floor guard immediately after pitchover (only if pitchoverDone was set)
      if(m.pitchoverDone === true && m.pitchoverTimer != null){
        const timeSincePitchover = m.pitchoverTimer - (m.pitchoverDuration ?? 0.25);
        if(timeSincePitchover < 0.4){
          const minZ=Math.max(25,mslAlt-10);
          cmdZ = Math.max(minZ, cmdZ);
        }
        // Increment timer for the 0.4s grace window
        if(timeSincePitchover < 0.5) m.pitchoverTimer += dt;
      }
      // (removed: redundant cmdIntercept — pipZ already bounded to target altitude)

      // === SEEKER ACTIVATION: distance-based ===
      // === SEEKER / SARH ACTIVATION ===
      if(m.isSM6){
        const sm6SeekerRange=m.pitbullKm??26;
        if(!m.sm6ActiveSeeker&&!m._sm6ArhInhibit&&rangeKm<sm6SeekerRange){
          m.state='ACTIVE';m.sm6ActiveSeeker=true;m.essmActiveSeeker=true;m.terminalSARH=true;m.seekerNoTargetTimer=0;
          notify('SM-6 시커 ON: M'+m.id+' (ARH PRIMARY + SARH FALLBACK, '+Math.round(rangeKm)+'km)');
        }
      } else if(m.seekerType === 'ESSM'){
        // ESSM: distance-based active seeker (ARH)
        var essmSeekerRange = m.pitbullKm ?? 16;
        if(!m.essmActiveSeeker && rangeKm < essmSeekerRange){
          m.state = 'ACTIVE';
          m.essmActiveSeeker = true;
          m.terminalSARH = true;
          m.seekerNoTargetTimer = 0;
          notify('ESSM 시커 ON: E' + m.id + ' (ACTIVE RF + SARH SUPPORT, ' + Math.round(rangeKm) + 'km)');
        }
      } else if(m.seekerType === 'IR'){
        var irSeekerRange = m.pitbullKm ?? 18;
        if(!m.terminalSARH && rangeKm < irSeekerRange){
          m.state = 'ACTIVE';
          m.sarhAlive = false;
          m.seekerNoTargetTimer = 0;
          notify('IR 시커 ON: M' + m.id);
        }
      } else if(m.seekerType === 'SARH' && m.sarhReceiverStandby){
        // SM-2 SARH: quality-based activation (NOT distance-based)
        // Compute illumination quality to target
        var illumQ = computeSarhIllumQ(tgtX, tgtY, tgtZ, aircraft.x(), aircraft.y());
        m._sarhRawQ = illumQ;

        // Smooth into stable quality (low-pass filter)
        var smoothRate = illumQ > m._sarhStableQ ? 0.4 : 0.15; // rises faster than falls
        m._sarhStableQ = lerp(m._sarhStableQ ?? 0, illumQ, clamp(smoothRate * dt * 10, 0, 0.3));

        // WIP54: for v1 SM-2 this legacy stableQ path is diagnostic only. Actual terminal acquisition
        // is SEARCH→ACQUIRE→TRACK in the onboard measurement-native RF seeker. Keeping both as
        // authority gates caused a delayed double-gate, especially against sea-skimmers.
        if(m.guidanceCore==='v1'){
          if(m._sarhStableQ >= (m._sarhAcquireThresh ?? 0.20)) m._sarhStableTime=(m._sarhStableTime??0)+dt;
          else m._sarhStableTime=Math.max(0,(m._sarhStableTime??0)-dt*2);
        } else {
          if(!m.terminalSARH){
            if(m._sarhStableQ >= (m._sarhAcquireThresh ?? 0.20)){
              m._sarhStableTime = (m._sarhStableTime ?? 0) + dt;
              if(m._sarhStableTime > 0.5){
                m.terminalSARH = true;
                notify('SARH 획득: M' + m.id + ' (Q:' + Math.round(m._sarhStableQ * 100) + '%, ' + Math.round(rangeKm) + 'km)');
              }
            } else {
              m._sarhStableTime = Math.max(0, (m._sarhStableTime ?? 0) - dt * 2);
            }
          }
          if(m.terminalSARH && m._sarhStableQ < (m._sarhMaintainThresh ?? 0.12)) m._sarhCoastTime=(m._sarhCoastTime??0)+dt;
        }
      }

      // === TERMINAL GUIDANCE (SM-2 SARH + ESSM ARH) ===
      var seekerRangeActive = m.pitbullKm ?? (isESSM ? 12 : 18);
      // termBlend: how much terminal precision drives guidance
      // For SM-2 SARH: driven by actual illumination quality, not just range
      if(m.sarhAlive){
        termBlend = clamp((m._sarhStableQ ?? 0.5) * 1.2, 0.3, 1.0); // quality-driven
      } else if(m.terminalSARH){
        termBlend = smoothstep(clamp((seekerRangeActive - rangeKm) / (seekerRangeActive * 0.4), 0, 0.7));
      } else {
        termBlend = smoothstep(clamp((seekerRangeActive - rangeKm) / (seekerRangeActive * 0.5), 0, 1));
      }

      // Legacy precision tracker is intentionally bypassed for v1 missiles.
      // v1 terminal/transition guidance must consume only SARH/ARH/DL/MEM sensor estimates;
      // allowing this older block to read targetPool/enemyMissiles truth would silently leak god-view state.
      if(m.guidanceCore !== 'v1' && (m.terminalSARH || m.essmActiveSeeker)){
        // Legacy-only fallback: find actual target for precision tracking.
        var lockObj = null;
        if(m.assignedTargetId != null) lockObj=truthObjectForTrackV27(m.assignedTargetId,true);

        var guidanceQuality = 0.3;
        if(m.sarhAlive){
          // SM-2 SARH: illumination quality drives guidance
          var illQ2 = m._sarhStableQ ?? (m._illQuality ?? 0.5);
          guidanceQuality = clamp(0.5 + illQ2 * 0.5, 0.5, 1.0); // 0.5~1.0
          m._sarhCoastTime = 0;
          if(lockObj){ m.seekerLocked = true; m.seekerLockId = m.assignedTargetId; m.seekerLockType = 'TGT'; }
        } else if(isESSM && m.essmActiveSeeker){
          guidanceQuality = 0.85;
          var seekLock2 = seekerAcquire(m, dt);
          if(seekLock2 && m.seekerLocked){ lockObj = seekLock2; guidanceQuality = 0.95; }
        } else {
          // No illuminator: coast with gradual degradation
          m._sarhCoastTime = (m._sarhCoastTime ?? 0) + dt;
          if(m._sarhCoastTime < 2.0){
            guidanceQuality = 0.60; // inertial memory from last illumination
          } else if(m._sarhCoastTime < 6.0){
            guidanceQuality = clamp(0.60 - (m._sarhCoastTime - 2.0) * 0.08, 0.25, 0.60);
          } else {
            guidanceQuality = 0.25; // heavily degraded
          }
        }

        if(lockObj && guidanceQuality > 0.4){
          // Precision: track actual target with separated H/V lead
          var lx0 = lockObj.x, ly0 = lockObj.y, lz0 = lockObj.z ?? tgtZ;
          var lvx = lockObj.vx ?? tgtVx, lvy = lockObj.vy ?? tgtVy, lvz = lockObj.vz ?? tgtVz;
          var dK3=dist3Km(ownX,ownY,mslAlt,lx0,ly0,lz0);
          var tgo2 = clamp(kmToWorld(dK3) / Math.max(m.speed, 1), 0.05, 4.0);

          // Horizontal lead
          var hLf;
          if(isESSM){
            // ESSM: full lead (50G agility, excellent seeker)
            hLf = clamp(0.8 + 0.2 * termBlend, 0.6, 1.1);
            if(dK3 < 2) hLf *= clamp(dK3 / 2, 0.3, 1.0);
          } else {
            hLf = clamp(0.7 + 0.3 * termBlend, 0.3, 1.1);
            if(dK3 < 3) hLf *= clamp(dK3 / 3, 0.2, 1.0);
            hLf *= clamp(worldSpeedToMps(m.speed) / (1.5 * MACH1_MPS), 0.4, 1.0);
          }

          // Vertical lead: STRONG full-tgo prediction for diving targets
          // For Kh-32 at -800 m/s, must predict FULL descent path, not partial
          var isDivingTerm = (lvz < -80);
          var vLf = hLf;
          if(isDivingTerm){
            // Use PN's iterative tgo (the ACTUAL time to intercept with 3D closing)
            var tgoUse = (m._tgoIter != null) ? m._tgoIter :
                         clamp(dK3 * 1000 / Math.max(300, worldSpeedToMps(m.speed)), 0.1, 6.0);
            // Full tgo for accurate lead (was 0.9× — too conservative)
            vLf = clamp(tgoUse, 0.3, 5.0);
          }

          var lx = lx0 + lvx * tgo2 * hLf;
          var ly = ly0 + lvy * tgo2 * hLf;
          var lz = lz0 + lvz * (isDivingTerm ? vLf : tgo2 * hLf * 0.85);
          // Sea floor: scale with descent speed (faster → higher floor)
          var termMinZ = surfaceMissileRuntimeWip13C6(m)?surfaceMissileGuidanceFloorWip13C6(m):((isHighDiver || (isESSM && isDivingTerm)) ? 10 : clamp(40 + Math.abs(lvz ?? 0) * 0.08, 40, 150));
          lz = Math.max(termMinZ, lz);
          // High-side: missile should be BELOW target for diving intercept
          if(isDivingTerm){
            // Predicted lock altitude matching vLf (use PN's tgo)
            var tgoInt = (m._tgoIter != null) ? m._tgoIter : tgo2;
            const lzIntercept = lz0 + lvz * clamp(tgoInt, 0.3, 5.0);
            // Stay at or below predicted intercept
            lz = Math.min(lz, lzIntercept + 50);
            if(mslAlt > lz0){
              // Already above target: force down hard
              lz = Math.min(lz, lz0 - Math.min((mslAlt - lz0) * 0.3, 600));
            }
            lz = Math.max(termMinZ, lz);
          }

          // Seeker-state response boost
          var seekerBoost = 1.0;
          if(m.sarhAlive) seekerBoost = 1.15; // SM-2 SARH: illuminator active
          if(isESSM && m.essmActiveSeeker) seekerBoost = 1.20; // ESSM ARH: aggressive
          var termRate = isESSM ?
            (0.65 + 0.33 * termBlend * guidanceQuality) * seekerBoost :
            (0.50 + 0.48 * termBlend * guidanceQuality) * seekerBoost;
          termRate = Math.min(termRate, 0.98);
          m._seekerLz = lz;  // debug
          m._seekerCmdZBefore = cmdZ;  // debug
          m._seekerTermRate = termRate;  // debug
          cmdX = lerp(cmdX, lx, termRate);
          cmdY = lerp(cmdY, ly, termRate);
          cmdZ = lerp(cmdZ, lz, termRate);
          cmdZ = Math.max(surfaceSm2GuidanceFloorWip13C5(m), cmdZ);
          cmdVx = lvx; cmdVy = lvy; cmdVz = lvz;
          cueBearing=Math.atan2(ly0-ownY,lx0-ownX);
          m.seekerNoTargetTimer = 0;
        } else {
          cueBearing=Math.atan2(tgtY-ownY,tgtX-ownX);
          preSlewSeekerToBearing(m, dt, cueBearing);
        }
      } else if(m.assignedTargetId != null){
        cueBearing=Math.atan2(tgtY-ownY,tgtX-ownX);
        preSlewSeekerToBearing(m, dt, cueBearing);
      }
    }
}

    // ===== ZEM-based CPA correction (XY + Z, wider activation) =====
    // Apply at all ranges with range-dependent gain
    if(tr && m._predictedCPAm != null && m._rangeKmCached != null && m._predictedCPAm > 30){
      const cpaM = m._predictedCPAm;
      const rngKmNow = m._rangeKmCached;
      // Activate at all ranges but with range-dependent gain
      // Close range = strong, long range = weak (let PN do primary work)
      {
        // Range gain: ramps from 0.2 at 30km to 1.0 at 0km
        const rangeGain = clamp(1.0 - rngKmNow / 30, 0.2, 1.0);
        const cpaGain = clamp((cpaM - 30) / 300, 0, 1.0);
        const totalGain = rangeGain * cpaGain;
        // ZEM components (meters, missile-from-target at CPA time)
        const zx = m._zemXm ?? 0;
        const zy = m._zemYm ?? 0;
        const zz = m._zemZm ?? 0;
        // Split: horizontal and vertical miss separately
        const zHoriz = Math.sqrt(zx*zx + zy*zy);
        const zVert = Math.abs(zz);
        // Horizontal correction (XY)
        if(zHoriz > 10){
          const zuX = zx / zHoriz, zuY = zy / zHoriz;
          // XY correction magnitude (meters): scale with horizontal miss component
          const corrXYm = Math.min(zHoriz * 0.8, rngKmNow * 1000 * 0.15) * totalGain;
          cmdX=(cmdX??ownX)+kmToWorld((-zuX*corrXYm)/1000);
          cmdY=(cmdY??ownY)+kmToWorld((-zuY*corrXYm)/1000);
        }
        // Vertical correction DISABLED
        // PN + pipZ (which uses accurate track z now) handles vertical properly.
        // Adding Z correction here double-corrects and causes missile to over-climb.
        // Re-enable only if vertical miss is confirmed NOT due to command lag.
        m._cpaCorrApplied = totalGain;
        m._cpaCorrZ = zz;
      }
    }

    // Smooth guidance commands to prevent oscillation
    const isDivingSmooth = (cmdVz < -100);
    // Terminal smoothing levels
    const _rngCached = m._rangeKmCached;
    const isTerminalSmooth = (_rngCached != null && _rngCached < 8);
    const isNearTerminal = (_rngCached != null && _rngCached < 3);
    // Midcourse one-shot snapshot at 15km
    if(_rngCached != null && _rngCached < 15 && !m._midEntered){
      m._midEntered = true;
      const _mLbl2 = m.isESSM ? 'E' : 'M';
      const _projAlt = m._projAlt != null ? Math.round(m._projAlt) : '?';
      const _tgo_mid = m._tgoIter != null ? m._tgoIter.toFixed(1) : '?';
      const _tgtZ_mid = m._lastTrZ != null ? Math.round(m._lastTrZ) : '?';
      const _tgtVz_mid = m._lastTrVz != null ? Math.round(m._lastTrVz) : '?';
      const _pipZ_mid = m._pipZApplied != null ? Math.round(m._pipZApplied) : '?';
      const _lz_mid = m._seekerLz != null ? Math.round(m._seekerLz) : '-';
      notify(`📍 MID ${_mLbl2}${m.id} @${_rngCached.toFixed(1)}km: mAlt=${Math.round(m.z ?? 0)} mVz=${Math.round(m.vz ?? 0)} cmdZ=${Math.round(cmdZ ?? 0)} pipZ=${_pipZ_mid} lz=${_lz_mid} tgtZ=${_tgtZ_mid} tgtVz=${_tgtVz_mid} tgo=${_tgo_mid}s`);
    }
    // One-shot debug: log terminal entry with errors + predicted CPA + missile/target state
    if(isTerminalSmooth && !m._termEntered){
      m._termEntered = true;
      const _mLbl = m.isESSM ? 'E' : 'M';
      const _mAlt = Math.round(m.z ?? 0);
      const _mVz = Math.round(m.vz ?? 0);
      const _cmdZ = Math.round(cmdZ ?? 0);
      const _tgtZ_tr = m._lastTrZ != null ? Math.round(m._lastTrZ) : '?';
      const _tgtVz_tr = m._lastTrVz != null ? Math.round(m._lastTrVz) : '?';
      const _pipZ = m._pipZApplied != null ? Math.round(m._pipZApplied) : '?';
      const _tgo = m._tgoIter != null ? m._tgoIter.toFixed(1) : '?';
      const _reach = m._mslReachAlt != null ? Math.round(m._mslReachAlt) : '?';
      const _lz = m._seekerLz != null ? Math.round(m._seekerLz) : '-';
      const _cmdBefore = m._seekerCmdZBefore != null ? Math.round(m._seekerCmdZBefore) : '-';
      const _trate = m._seekerTermRate != null ? m._seekerTermRate.toFixed(2) : '-';
      // REPAIR-2 §15: v1 유도 상태 suffix (phase/source/conf/N·gain/G/SAT/SG)
      const _v1sfx = (m.guidanceCore === 'v1')
        ? ` | v1:${m._v1GuidancePhase ?? '-'} src=${m._v1TargetState?.source ?? '-'} c=${((m._v1TargetState?.confidence ?? 0)*100).toFixed(0)}% N=${(m._v1Profile?.terminalPN ?? 0).toFixed(1)} apn=${(m._v1Profile?.apnGain ?? 0).toFixed(2)} zem=${(m._v1Profile?.zemGain ?? 0).toFixed(2)} g=${(m._v1GCommand ?? 0).toFixed(0)}/${(m._v1GAchieved ?? 0).toFixed(0)}G κctl=${Number.isFinite(m._v1GDeliveryControlEma)?m._v1GDeliveryControlEma.toFixed(2):'-'} κg=${Number.isFinite(m._v1GDeliveryGuidanceEma)?m._v1GDeliveryGuidanceEma.toFixed(2):'-'}${m._v1Saturated ? ' SAT' : ''}${m._v1SoftGuard ? ' SG' : ''} tvc=${(m._v1TvcAuthority ?? 0).toFixed(1)}`
        : '';
      notify(`🎯 TERM ${_mLbl}${m.id}: mAlt=${_mAlt} mVz=${_mVz} cmdZ=${_cmdZ} pipZ=${_pipZ} tgtZ=${_tgtZ_tr} tgtVz=${_tgtVz_tr} tgo=${_tgo}s reach=${_reach} lz=${_lz} cmdB4=${_cmdBefore} rate=${_trate}${_v1sfx}`);
    }
    var smoothFac;
    if(isNearTerminal){
      smoothFac = 1.0;   // no smoothing in very close terminal
    } else if(isTerminalSmooth){
      smoothFac = 0.98;
    } else {
      smoothFac = isESSM ? 0.9 : (isDivingSmooth ? 0.85 : ((m.terminalSARH) ? 0.7 : 0.5));
    }
    cmdX = lerp(prevCmdX, cmdX, smoothFac);
    cmdY = lerp(prevCmdY, cmdY, smoothFac);
    // Asymmetric smoothing for cmdZ: downward corrections go through IMMEDIATELY
    // (prevents overshoot on diving targets), upward gets smoothed (stability)
    if(cmdZ < prevCmdZ){
      // Need to descend. Long-range SM-2 energy-shelf corrections are intentionally low-bandwidth;
      // terminal/high-confidence descent remains fast.
      let descendFac = isESSM ? 0.98 : 0.95;
      if(!isESSM && m._hdEnergyShelfActive && (m._rangeKmCached ?? 0) > 25){
        descendFac = 0.22;
      }
      cmdZ = lerp(prevCmdZ, cmdZ, descendFac);
    } else {
      cmdZ = lerp(prevCmdZ, cmdZ, smoothFac);
    }
    cmdZ = Math.max(surfaceSm2GuidanceFloorWip13C5(m), cmdZ);
    m._prevCmdX = cmdX; m._prevCmdY = cmdY; m._prevCmdZ = cmdZ;

    // ===== Desired direction =====
    // ===== True PN (accel-command) + 1st-order autopilot (more realistic) =====
const dx = cmdX - m.x;
const dy = cmdY - m.y;
const rh2 = dx*dx + dy*dy + 1e-6;
const rh  = Math.sqrt(rh2);
const los = Math.atan2(dy, dx);

// 3D geometry (for pitch / closing speed)
// Final cmdZ floor (all guidance paths).
// A sea-skimming target does NOT imply the interceptor should sea-skim throughout midcourse.
// Keep ESSM safely above the surface until its precision terminal kernel is close enough to take over;
// this prevents noisy low-altitude track estimates from driving a pre-terminal water impact.
let guidanceFloorM = surfaceSm2GuidanceFloorWip13C5(m);
if(m.isESSM && m.guidanceCore === 'v1' && !m._v1TerminalActive && !m._surfaceArh){
  const essmTermKm = m._v1Profile?.terminalRangeKm ?? 10;
  if((m._rangeKmCached ?? 999) > essmTermKm * 1.08) guidanceFloorM = 70; // SIM_TUNED sea-clearance midcourse floor
}
cmdZ = Math.max(guidanceFloorM, cmdZ ?? OWN_ALT_M);
const dzM = cmdZ - (m.z ?? OWN_ALT_M);
const dxM = worldToMeters(dx);
const dyM = worldToMeters(dy);
const rhM = Math.max(1.0, Math.hypot(dxM, dyM));
const r3M = Math.max(1.0, Math.hypot(rhM, dzM));

// elevation(고도) 목표
let desiredPitch = Math.atan2(dzM, rhM);
// WIP8 sensor-realism guard: sea-skimmer track altitude is noisy near the horizon.
// ESSM midcourse therefore holds a modest sea-clearance profile instead of chasing every low-altitude measurement.
// Precision terminal guidance is allowed to descend once inside the terminal gate.
if(m.isESSM && m.guidanceCore === 'v1'){
  const essmTermKm = m._v1Profile?.terminalRangeKm ?? 8;
  const rNow = m._rangeKmCached ?? 999;
  if(rNow > essmTermKm * 1.08){
    const zNow = m.z ?? 0;
    if(zNow < 90) desiredPitch = Math.max(desiredPitch, deg(2.5));
    else desiredPitch = Math.max(desiredPitch, deg(-0.5));
  }
}
// SI-REFRACTOR WIP5: SM-2 midcourse loft needs a flight-path-angle floor.
// A far-away altitude point alone gives only a few degrees of climb, so the missile
// can spend its entire boost/sustain phase below ~1 km. When the current command is
// a genuine loft command, raise the climb angle until the altitude deficit closes.
if(!m.isESSM && !m._v1TerminalActive && (m._rangeKmCached ?? 0) > 25){
  const loftAltErrM = (cmdZ ?? (m.z ?? 0)) - (m.z ?? 0);
  if(loftAltErrM > 500){
    let floorDeg=clamp(7 + loftAltErrM / 900, 8, 20);
    // WIP63: if the vertical budget says a high target still requires substantial altitude work,
    // deliberately trade horizontal progress for climb BEFORE SARH terminal geometry gets urgent.
    // This removes the old pattern of ~20° midcourse followed by a desperate 50-60° late zoom.
    const vbClimb=clamp(m._sm2VerticalBudget?.climb01??0,0,1);
    if(vbClimb>0.02) floorDeg=Math.max(floorDeg,lerp(20,29,vbClimb));
    const loftPitchFloor = deg(floorDeg);
    desiredPitch = Math.max(desiredPitch, loftPitchFloor);
  }
  if(m._hdEnergyShelfActive){
    // Preserve axial energy, but WIP63 lets a genuine high-altitude vertical debt open a steeper
    // 24->31° energy climb.  It remains far below a terminal 50-60° zoom and fades automatically
    // as the predicted intercept corridor descends.
    const vbClimb=clamp(m._sm2VerticalBudget?.climb01??0,0,1);
    const hdMaxPitchDeg=lerp(24,31,vbClimb);
    desiredPitch = clamp(desiredPitch, deg(-10), deg(hdMaxPitchDeg));
    m._sm2HdMidcoursePitchCapDeg=hdMaxPitchDeg;
  }else m._sm2HdMidcoursePitchCapDeg=null;
  if(m._sm2ApexCapture?.active){
    desiredPitch=Math.min(desiredPitch,deg(m._sm2ApexCapture.capPitchDeg));
  }
  // WIP63 vertical-corridor capture.  The high-altitude shelf is an early energy investment, not
  // permission to keep zoom-climbing after the predicted collision altitude has started falling.
  // Look a few seconds ahead using the missile's real vertical momentum; if that projection would
  // overtake the predicted intercept corridor, command the flight path down BEFORE closest approach.
  m._sm2VerticalCapture=null;
  const vb62=m._sm2VerticalBudget;
  if(vb62 && (m._lastTrVz??cmdVz??0)<-80){
    const projT=5.0,projAlt62=(m.z??0)+Math.max(-1200,Math.min(1200,m.vz??0))*projT;
    const corridorAlt=Math.max(200,vb62.predictedAltM??cmdZ??0);
    const excess=projAlt62-corridorAlt;
    if(excess>500){
      const capture01=_samSmooth01(clamp((excess-500)/4500,0,1));
      const capPitchDeg=lerp(4,-20,capture01);
      desiredPitch=Math.min(desiredPitch,deg(capPitchDeg));
      m._sm2VerticalCapture={active:true,projectionS:projT,projectedAltM:projAlt62,corridorAltM:corridorAlt,excessM:excess,capture01,capPitchDeg};
    }
  }
}

// relative velocity (cmd - missile) in m/s
const vrelX = worldSpeedToMps((cmdVx ?? 0) - m.vx);
const vrelY = worldSpeedToMps((cmdVy ?? 0) - m.vy);
const vrelZ = (cmdVz ?? 0) - (m.vz ?? 0);

// LOS rate (yaw) approx: (r x v_rel) / r^2  (rad/s)   [2D]
const losRate = ((dxM)*vrelY - (dyM)*vrelX) / (rhM*rhM + 1e-6);

// LOS rate (pitch) based on elevation angle derivative (rad/s)
const rhDot = ((dxM)*vrelX + (dyM)*vrelY) / rhM;  // m/s
const elRate = (rhM*vrelZ - dzM*rhDot) / (r3M*r3M + 1e-6);

// closing speed along 3D LOS (m/s)
const rHatX = dxM / r3M;
const rHatY = dyM / r3M;
const rHatZ = dzM / r3M;
let Vc = -(vrelX*rHatX + vrelY*rHatY + vrelZ*rHatZ); // + = closing
Vc = clamp(Vc, 0.0, 1600.0);

// 가까워질수록 공격적 (PN 내비게이션 상수)
const close01 = clamp(1.0 - worldToKm(rh) / 10.0, 0, 1);
// 터미널(종말)에서는 더 적극적으로 — 단, 동압/에너지 한계 내에서만
const termBoost01 = Math.max((typeof termBlend !== 'undefined' ? termBlend : 0), smoothstep(clamp((9.0 - (r3M/1000)) / 9.0, 0, 1)));
var N = (m.pnN0 ?? 3.6) + (m.pnNCloseGain ?? 2.0) * close01 + (m.pnNTermGain ?? 1.15) * termBoost01;
// Near-terminal: cap N to prevent overshoot oscillation (actuator cannot keep up)
if(m._rangeKmCached != null && m._rangeKmCached < 3){
  N = Math.min(N, 5.5);
}

// speed
const v_mps2 = Math.max(60, worldSpeedToMps(m.speed));
const v01 = clamp(v_mps2 / (4.2*MACH1_MPS), 0, 1);

// PN accel command (m/s^2)
// Time-to-go damping: PN이 종말에서 과잉 리드/진동하는 걸 줄임
    const tgo = r3M / Math.max(60, Math.max(1, Vc));
    const tgoDampS = (m.pnTgoDampS ?? 0.55) * lerp(1.0, 0.55, termBoost01);
    const dampTgo = clamp(tgo / (tgo + tgoDampS), 0.25, 1.0);
    const Ndamp = clamp(tgo / (tgo + lerp(0.20, 0.10, termBoost01)), 0.65, 1.0);
    const Neff = N * Ndamp;

    const aYawCmd = Neff * Vc * (losRate * dampTgo);
    const aPitCmd = Neff * Vc * (elRate * dampTgo);

    // WIP56 roll-ownership fix.  SAM BODY_6DOF_LITE is a skid-to-turn pitch/yaw model; the
    // physical integrator below owns its roll state.  The old air-to-air bank-to-turn pre-controller
    // rotated the fin-force basis during VLS while pitch/yaw moments stayed in a de-rolled frame,
    // producing false heading drift and, in the worst case, an endless vertical-climb deadlock.
    if(m.roll == null) m.roll = 0;
    if(m.rollRate == null) m.rollRate = 0;
    if(!m.samSixDofEnabled){
      const bankDes = Math.atan2(aYawCmd, aPitCmd);
      const q01r = clamp(q / 30000, 0, 1);
      const bankErr = angNorm(bankDes - m.roll);
      const rollTau = lerp(0.40, 0.12, q01r);
      const rollRateCmd = clamp(bankErr / Math.max(1e-3, rollTau), -deg(420), deg(420));
      const rollAccMax = lerp(deg(260), deg(880), q01r);
      const rollAcc = clamp((rollRateCmd - m.rollRate) / Math.max(1e-3, rollTau*0.55), -rollAccMax, rollAccMax);
      m.rollRate += rollAcc * dt;
      const rollRateMax = lerp(deg(130), deg(520), q01r);
      m.rollRate = clamp(m.rollRate, -rollRateMax, rollRateMax);
      m.roll = angNorm(m.roll + m.rollRate * dt);
    }
// convert to turn-rate commands (rad/s): a_n = V * omega
let omegaYawCmd = aYawCmd / v_mps2;
let omegaPitCmd = aPitCmd / v_mps2;

// ===== APN with per-axis H/V gains and split closureBoost =====
if((m.apnAx != null) && v_mps2 > 20 && r3M > 100){
  const rh2_apn = Math.max(1.0, Math.hypot(dxM, dyM));
  const rhUx = dxM / rh2_apn, rhUy = dyM / rh2_apn;
  const aTperp2D = m.apnAx * (-rhUy) + m.apnAy * rhUx;
  const rhUz = dzM / Math.max(1.0, r3M);
  const aTperpZ  = (m.apnAz ?? 0) * (1.0 - rhUz * rhUz);
  // Per-axis base gains (horizontal slightly higher to improve lateral closure)
  const apnBaseH = m.isESSM ? 0.72 : 0.60;
  const apnBaseV = m.isESSM ? 0.75 : 0.66;
  const isHd = (m.apnTargetIsHighDiver === true);
  // Conservative vertical boost — control allocation handles axis distribution
  const vertBoost = isHd ? (m.isESSM ? 1.10 : 1.12) : 1.0;
  // Confidence
  var apnConfidence = 0.3;
  if(m.sarhAlive || m.essmActiveSeeker) apnConfidence = 1.0;
  else if(m.seekerLocked) apnConfidence = 0.85;
  else if(m.dlAlive) apnConfidence = 0.6;
  const apnGainH = apnBaseH * apnConfidence;
  const apnGainV = apnBaseV * apnConfidence * vertBoost;
  // Split closureBoost: yaw from LOS geometry, pitch from vertical rate
  const losRateMag = Math.abs(losRate);
  const rangeKmLocal = r3M / 1000; // use in-scope r3M (meters)
  const closureBoostYaw = clamp(1.0 + losRateMag * 6 + clamp(20/Math.max(1,rangeKmLocal),0,0.4), 1.0, 1.8);
  const closureBoostPit = clamp(Math.abs(cmdVz ?? 0) / 500, 1.0, 1.8);
  const cap = G0 * 30;
  omegaYawCmd += clamp(apnGainH * aTperp2D * closureBoostYaw, -cap, cap) / v_mps2;
  omegaPitCmd += clamp(apnGainV * aTperpZ  * closureBoostPit, -cap, cap) / v_mps2;
}

// small bias to keep pointing roughly toward LOS (helps when losRate ~ 0)
const losErr = angNorm(los - (m.velAngle ?? m.heading));
// Pitchover: extra LOS bias for rapid alignment
var losBiasPitchoverBoost = 1.0;
if(m.pitchoverPhase === true){
  losBiasPitchoverBoost = m.isESSM ? 3.0 : 2.2; // strong pull toward LOS
}
omegaYawCmd += clamp(losErr, -deg(25), deg(25)) * (m.pnLosBiasK ?? 0.20) * lerp(1.0, 1.45, termBoost01) * losBiasPitchoverBoost;

// pitch bias too: elRate가 작아도(빔/평행 접근) 고도 라인으로 붙게 해서 저고도 표적 놓침 줄임
let pitErrBias = clamp(desiredPitch - (m.velPitch ?? 0), -deg(20), deg(20));
// (climb urgency bias removed — caused over-ascent against descending targets)
// Prevent diving into sea: reduce nose-down command when low
// BUT: if target is also low (sea-skimmer), missile MUST continue descent
const mslAltHere = m.z ?? OWN_ALT_M;
const cmdAltHere2 = cmdZ ?? mslAltHere;
// Suppression only if missile is close to target altitude OR at very low altitude
// Don't suppress when target is below missile (sea-skimmer pursuit)
const altDelta_nd = mslAltHere - cmdAltHere2;
if(mslAltHere < 80 && pitErrBias < 0 && altDelta_nd < 30){
  // Only suppress if missile is already at or below cmdZ
  // (don't prevent descent toward target)
  pitErrBias *= clamp(mslAltHere / 80, 0.15, 1.0);
}
// Boost pitch bias for fast-diving targets
const divingBoost = clamp(Math.abs(cmdVz ?? 0) / 300, 1.0, 3.5);
// Pitchover: extra pitch bias
var pitBiasPitchoverBoost = 1.0;
if(m.pitchoverPhase === true){
  pitBiasPitchoverBoost = m.isESSM ? 3.0 : 2.2;
}
omegaPitCmd += pitErrBias * (m.pnPitchBiasK ?? 0.28) * lerp(1.0, 1.75, termBoost01) * divingBoost * pitBiasPitchoverBoost;

// WIP63: during vertical-corridor capture the trajectory manager owns the sign of the pitch
// command.  PN/APN may still contribute lateral correction, but it cannot keep commanding a climb
// while the missile is projected kilometres above a descending intercept corridor.
if(!m.isESSM && m._sm2VerticalCapture?.active){
  const c01=clamp(m._sm2VerticalCapture.capture01??0,0,1);
  const downRate=deg(lerp(1.5,10.0,c01));
  omegaPitCmd=Math.min(omegaPitCmd,-downRate);
  m._sm2VerticalCaptureRateDegS=-rad2deg(downRate);
}else if(!m.isESSM){
  m._sm2VerticalCaptureRateDegS=0;
}

// === Match target's vertical velocity (close-range only) ===
// Only apply when missile is above or near target, and close enough.
// In midcourse, missile needs freedom to climb toward cmdZ.
const mAltHere = m.z ?? 0;
const cmdAltHere = cmdZ ?? mAltHere;
const nearOrAboveCmd = mAltHere > cmdAltHere - 300;  // missile reached or near cmdZ
if((cmdVz ?? 0) < -100 && (m.vz ?? 0) > -100 && nearOrAboveCmd){
  const vzMismatch = (m.vz ?? 0) - (cmdVz ?? 0);
  const vzCorrGain = clamp(vzMismatch / 600, 0, 1.2);
  // Only apply in close range (10km inner) where intercept geometry is fixed
  const rngFactor = m._rangeKmCached != null
    ? clamp(1.0 - m._rangeKmCached / 10, 0, 1.0)
    : 0;
  omegaPitCmd -= deg(12) * vzCorrGain * rngFactor;
  m._vzMatchActive = true;
  m._vzMismatch = vzMismatch;
}
// ----- Seeker gimbal-aware turn limiting -----
// 저속/저에너지에서 과리드를 줘버리면 미사일이 '먼저 꺾고' 시커 짐벌이 못 따라가면서 락이 풀릴 수 있음.
// cueBearing(=DL/IOG 큐 or 시커락 LOS)을 기준으로, 짐벌 한계 근처에서는 유도 명령을 자동으로 누르고
// 약간의 pursuit 바이어스를 넣어 표적을 시야에 계속 두게 한다.
if(cueBearing != null){
  const gLim = (m.gimbalMax ?? deg(65));
  const gErr = angNorm(cueBearing - m.heading);
  const gAbs = Math.abs(gErr);
  const soft = gLim * 0.78;
  const hard = gLim * 0.96;
  let over = (gAbs - soft) / Math.max(1e-6, (hard - soft));
  over = clamp(over, 0.0, 1.0);
  const overS = over*over*(3 - 2*over); // smoothstep
  const guard = 1.0 - 0.75*overS;       // 최소 25%는 남김

  omegaYawCmd *= guard;
  omegaPitCmd *= guard;

  const v01_turn_local = clamp(v_mps2 / (1.2 * MACH1_MPS), 0.15, 1.0);
  const keepK = (m.gimbalKeepK ?? 1.65) * overS * (0.65 + 0.35*v01_turn_local);
  omegaYawCmd += gErr * keepK;
}

// ===== WIP40 LAUNCH-CONTROL AUTHORITY =====
// During cell-clear/hard-pitchover/forward-commit, PN/APN does not own attitude.  The launch
// controller directly requests body rates toward the corridor; TVC + the normal rate servo provide
// the physical response.  Once pitchoverPhase clears, ordinary guidance resumes.
m._v1LaunchControlAuthority=false;
m._v1AllowLaunchGuidanceOverlap=false;m._v1LaunchGuidanceBlend01=0;
if(m.guidanceCore==='v1'&&(m.vlsPhase===true||m.pitchoverPhase===true)){
  const cfg=_samVlsControlConfig(m,!!m.isESSM);
  const desH=m._vlsDesiredBearing??m.heading??0,desP=m._vlsDesiredPitch??m.pitch??0;
  const yErr=angNorm(desH-(m.heading??0)),pErr=desP-(m.pitch??0);
  const hard=m.vlsPhase===true;
  const rateCap=hard?cfg.hardRateCap:cfg.commitRateCap;
  const gain=hard?cfg.hardGain:cfg.commitGain;
  omegaYawCmd=clamp(yErr*gain,-rateCap,rateCap);
  omegaPitCmd=clamp(pErr*gain,-rateCap,rateCap);
  m._v1LaunchControlAuthority=true;
  // WIP57: after BODY alignment, close/high-urgency SM-2 engagements no longer wait for a hard
  // controller hand-off.  The launch controller still owns safety/clearance, while PN/APN may blend
  // into the forward-commit command as speed and clearance build.  VLS/cell-clear itself stays exclusive.
  if(!m.isESSM&&m.pitchoverPhase===true){
    const rKm=Math.max(0,m._rangeKmCached??999),urg=clamp(m._samTrajPlan?.urgency??0,0,1);
    const close01=1-clamp((rKm-30)/20,0,1);
    const vh=Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0));
    const speed01=clamp((vh-80)/260,0,1),clear01=clamp(((m.z??0)-60)/300,0,1);
    const need=Math.max(close01,urg*.85);
    const blend=clamp(need*Math.max(.25,speed01)*Math.max(.30,clear01),0,.78);
    if(blend>.03){m._v1AllowLaunchGuidanceOverlap=true;m._v1LaunchGuidanceBlend01=blend;}
  }
  // WIP60 ESSM boost-intercept overlap: once clear of the cell, the 3-D launch corridor still owns
  // safety/body alignment, but terminal PN/APN may blend in while the powered TVC is available.
  // This avoids treating TVC as a one-shot 'point the nose' device during a close diving engagement.
  if(m.isESSM&&m.pitchoverPhase===true&&missileThrustN(m)>1000&&(m.life??0)<(m._v1Profile?.tvcDurationSec??3.3)){
    const yAbs=Math.abs(yErr),pAbs=Math.abs(pErr),att01=1-clamp(Math.max(yAbs/Math.max(deg(1),cfg.headingTol*2),pAbs/Math.max(deg(1),cfg.pitchTol*2)),0,1);
    const vh=Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0)),speed01=clamp((vh-70)/220,0,1);
    const blend=clamp(.18+.58*Math.max(att01*.75,speed01*.70),.18,.72);
    m._v1AllowLaunchGuidanceOverlap=true;m._v1LaunchGuidanceBlend01=blend;
  }
}

// ===== GUIDANCE KERNEL / PHASE POLICY =====
{
  const _g=applyGuidanceKernelV1ToLegacyRates(m,omegaYawCmd,omegaPitCmd,dt);
  omegaYawCmd=_g.omegaYawCmd; omegaPitCmd=_g.omegaPitCmd;
}

// WIP40 predictive sea-clearance envelope.  This changes the COMMAND, never the state/velocity.
// It is intentionally inactive inside the last ~200m so it cannot "save" a real miss by cheating.
m._v1SeaClearanceGuard=false;
if(m.guidanceCore==='v1' && m.isESSM){
  const sg=_samSeaClearanceRateGuard(m,true,m._rangeKmCached,dt);
  if(sg){
    m._v1SeaProjectedAltM=sg.projectedAltM;m._v1SeaMarginM=sg.marginM;
    if(sg.active){omegaPitCmd=Math.max(omegaPitCmd,sg.omegaFloor);m._v1SeaClearanceGuard=true;m._v1SeaRequiredPitch=sg.requiredPitch;}
  }
}

// ===== WIP60 SM-2 routine-vs-emergency G command envelope =====
// The general midcourse rate law can bypass the v1 acceleration bridge, so enforce the same
// 18-24G routine / <=28G emergency policy in rate space before the physical 6DOF integrator.
if(m.guidanceCore==='v1'&&!m.isESSM&&!m.vlsPhase&&!m.pitchoverPhase){
  const vCmd=Math.max(80,worldSpeedToMps(m.speed??0));
  const rawRateG=Math.hypot(omegaYawCmd,omegaPitCmd)*vCmd/G0;
  const cmdCapG=_sm2CommandEnvelopeG(m,rawRateG);
  if(Number.isFinite(cmdCapG)&&rawRateG>cmdCapG&&rawRateG>1e-9){
    const sc=cmdCapG/rawRateG;omegaYawCmd*=sc;omegaPitCmd*=sc;m._sm2RateEnvelopeSaturated=true;
  }else m._sm2RateEnvelopeSaturated=false;
}

// ===== WIP44 BODY-6DOF-LITE physical dynamics / legacy fallback =====
if(m.samSixDofEnabled){
  updateSamSixDofLiteDynamics(m,dt,omegaYawCmd,omegaPitCmd,{massKg,qPa:q,rhoKgM3:rho,mach,cdBase:cd,Aref,Slift,thrustN});
  if(_surfaceStepStart&&surfaceMissileSweptContactWip13C5(m,_surfaceStepStart))return;
  if(m.z < 0 && !m.vlsPhase){
    m._deathReason='SEA_IMPACT';m.dead=true;
    const mLabel=m.isESSM?'ESSM E':'SM-2 M';const _closeInfoSea=m._everClosest!=null?` (closest ${Math.round(m._everClosest*1000)}m)`:'';
    notify(`🌊 ${mLabel}${m.id} 해면충돌${_closeInfoSea}`);return;
  }
  m.z=Math.max(0,m.z);
}else{
// G-limit => omega limit (combined yaw+pitch)
const gLimCmd = (m.gLimitDyn ?? m.gLimit ?? 40);
const aMax = gLimCmd * G0;
const omegaMax = aMax / v_mps2; // rad/s (total for G-limit)

// Low-energy/low-speed에서는 실제로 G를 못 뽑는 느낌(선회율 제한)
const v01_turn = clamp(v_mps2 / (1.2 * MACH1_MPS), 0.15, 1.0);
const omegaMaxEff = omegaMax * (0.65 + 0.35 * v01_turn); // better low-speed authority

// 근접일수록 약간 공격적으로(하지만 G-limit은 절대 넘지 않게)
let omegaMaxTotal = omegaMaxEff * (1.0 + 0.10 * close01);
// TVC exists specifically to provide attitude authority before aerodynamic G is available.
// Do not re-clamp launch-phase TVC body rates to the low-q fin-derived omega limit.
if(m.tvcEnabled&&(m.vlsPhase===true||m.pitchoverPhase===true)&&missileThrustN(m)>1000){
  const tvcBodyRateCap=m.vlsPhase===true?deg(390):deg(280);
  omegaMaxTotal=Math.max(omegaMaxTotal,tvcBodyRateCap);
  m._tvcRateAuthorityCap=tvcBodyRateCap;
}else m._tvcRateAuthorityCap=0;

// ===== CONTROL ALLOCATION (situation-adaptive) =====
// Distribute total turn budget between yaw/pitch based on need + situation
let omegaTotCmd = Math.hypot(omegaYawCmd, omegaPitCmd);
{
  if(omegaTotCmd > omegaMaxTotal && omegaTotCmd > 1e-9){
    const absYaw = Math.abs(omegaYawCmd);
    const absPit = Math.abs(omegaPitCmd);
    const totalRaw = absYaw + absPit;

    // === Situation-adaptive minimum fractions ===
    // Default: symmetric 20% / 20%
    var minYawFrac = 0.20;
    var minPitFrac = 0.20;

    // Debug: alt/ct error magnitudes
    const altErrAbs = Math.abs((m.z ?? 0) - (cmdZ ?? (m.z ?? 0)));
    const ctErrAbs = Math.hypot((cmdX ?? m.x) - m.x, (cmdY ?? m.y) - m.y) * worldToMeters(1);

    // HD with LARGE altErr AND small ctErr: pitch priority (alignment)
    // If BOTH errors are large, fall back to natural (need-based) allocation
    const altErrNorm = clamp(altErrAbs / 500, 0, 1);
    const ctErrNorm = clamp(ctErrAbs / 500, 0, 1);

    if(m.apnTargetIsHighDiver && altErrNorm > 0.5 && ctErrNorm < altErrNorm * 0.5){
      // Only favor pitch when altErr dominates ctErr
      minYawFrac = 0.15;  // slightly lower yaw min (don't kill it)
      // pitch min stays 0.20 — rely on natural absPit/(absYaw+absPit) to push pitch
    }
    // If BOTH errors are significant: lower BOTH mins → natural allocation wins
    if(altErrNorm > 0.5 && ctErrNorm > 0.5){
      minYawFrac = 0.15;
      minPitFrac = 0.15;
    }

    // Terminal phase (close range): CPA-minimization mode
    // Keep minimum at 0.15 (not 0.05) to prevent one-axis starvation / oscillation
    const isTerminalCPA = (m._rangeKmCached != null && m._rangeKmCached < 8);
    if(isTerminalCPA){
      minYawFrac = 0.15;
      minPitFrac = 0.15;
    }

    // Need-based allocation
    var yawFrac = totalRaw > 1e-9 ? absYaw / totalRaw : 0.5;
    var pitFrac = totalRaw > 1e-9 ? absPit / totalRaw : 0.5;
    // Enforce minimums (situation-dependent)
    if(yawFrac < minYawFrac){
      yawFrac = minYawFrac;
      pitFrac = 1.0 - minYawFrac;
    } else if(pitFrac < minPitFrac){
      pitFrac = minPitFrac;
      yawFrac = 1.0 - minPitFrac;
    }
    // Preserve G-limit via hypot
    const fracNorm = Math.sqrt(yawFrac*yawFrac + pitFrac*pitFrac);
    const yawBudget = omegaMaxTotal * (yawFrac / fracNorm);
    const pitBudget = omegaMaxTotal * (pitFrac / fracNorm);
    if(absYaw > yawBudget) omegaYawCmd *= yawBudget / absYaw;
    if(absPit > pitBudget) omegaPitCmd *= pitBudget / absPit;
    // Debug
    m._allocYawFrac = yawFrac;
    m._allocPitFrac = pitFrac;
    m._allocAltErr = altErrAbs;
    m._allocCtErr = ctErrAbs;
  }
}

// ===== Autopilot dynamics: angular-rate state + accel limits (much more "6DoF-like") =====
if(m.yawRate == null)   m.yawRate   = 0;
if(m.pitchRate == null) m.pitchRate = 0;
if(m.pitch == null)     m.pitch     = 0;

// VLS phase: climb altitude scales with target altitude/range
{
  const tgtAlt = cmdZ ?? 5000;
  const rangeM = Math.max(500, worldToMeters(Math.hypot((cmdX??m.x)-m.x, (cmdY??m.y)-m.y)));
  const mslAlt = m.z ?? 0;

  // WIP40: v1 ESSM VLS attitude is NOT written directly here.  The launch corridor above
  // commands the rate servo/TVC, and the physical torque/side-force rotates the body/velocity.
  // Retain the old direct-attitude scaffold only for non-v1/legacy missiles.
  if(m.vlsPhase && m.guidanceCore!=='v1'){
    const mclAlt2 = m.isESSM ? 35 : 55;
    const altFrac = clamp((m.z ?? 0) / mclAlt2, 0, 1);
    if(altFrac > 0.7){
      const rampDown = (altFrac - 0.7) / 0.3;
      const targetP = m.isESSM ? lerp(deg(80), deg(55), rampDown) : lerp(deg(80), deg(60), rampDown);
      m.pitch = targetP;
      m.velPitch = lerp(m.velPitch, targetP, 0.5 * dt * 10);
    } else {
      m.pitch = deg(80);
      m.velPitch = lerp(m.velPitch, deg(78), 0.3 * dt * 10);
    }
  }
}
if(m.velAngle == null)  m.velAngle  = m.heading ?? 0;
if(m.heading == null)   m.heading   = m.velAngle;
if(m.velPitch == null)  m.velPitch  = 0;

// dynamic-pressure based responsiveness (higher q => stronger authority / faster response)
const qbar = q; // already computed above: 0.5*rho*v^2
const q01 = clamp(qbar / (m.apQrefPa ?? 25000), 0.10, 1.8);

// TVC agility boost: during TVC phase, dramatically improve response
// ===== (removed) pseudo-TVC autopilot buff =====
// Real TVC now applies via force-vector decomposition (forward cos, lateral sin).
// This autopilot buff (tvcBoost) inflated tauRate/tauDamp/yawAccMax unrealistically.
// Kept as 1.0 for compatibility with the formulas below.
const tvcBoost = 1.0;

// Time constants: larger => "heavier" missile, smaller => snappier
const termAgility = lerp(1.0, 0.55, termBoost01); // stronger terminal agility (tau 45% reduction)
// Seeker-state response boost
var seekerAgility = 1.0;
if(m.sarhAlive) seekerAgility = 0.85;
if(m.isESSM && m.essmActiveSeeker) seekerAgility = 0.82;
if(m.apnTargetIsHighDiver && (m.sarhAlive || m.essmActiveSeeker)){
  seekerAgility *= 0.94;
}
// Pitchover phase: temporary rate-limited rapid turn boost
var pitchoverBoost = 1.0;
if(m.pitchoverPhase === true){
  const pDur = m.pitchoverDuration ?? 0.25;
  const pf = clamp((m.pitchoverTimer ?? 0) / Math.max(0.05, pDur), 0, 1);
  const boostAmt = (1.0 - pf) * (m.isESSM ? 0.5 : 0.35);
  seekerAgility *= (1.0 - boostAmt);
  pitchoverBoost = 1.0 + boostAmt * 2.0; // up to 2.0×/1.7× accel
}
var tauRate = Math.max(0.015, (m.apTauRate ?? 0.07) / Math.sqrt(q01) * termAgility * seekerAgility / tvcBoost);
var tauDamp = Math.max(0.010, (m.apTauDamp ?? 0.04) / Math.sqrt(q01) * termAgility * seekerAgility / tvcBoost);
// Near-terminal: reduce response time drastically (CPA minimization over stability)
if(m._rangeKmCached != null && m._rangeKmCached < 5){
  const nearTermScale = clamp((m._rangeKmCached - 1.0) / 4.0, 0.25, 1.0); // 1km→0.25x, 5km→1.0x
  tauRate *= nearTermScale;
  tauDamp *= nearTermScale;
}

// Angular acceleration limits
const qAcc01 = clamp(q01 / 1.8, 0, 1);
const accBoost = lerp(1.0, 1.75, termBoost01) * tvcBoost;
const yawAccMax = (m.apYawAccMax ?? lerp(deg(300),  deg(1400), qAcc01)) * (0.60 + 0.40*v01_turn) * accBoost * pitchoverBoost;
const pitAccMax = (m.apPitAccMax ?? lerp(deg(280),  deg(1300), qAcc01)) * (0.60 + 0.40*v01_turn) * accBoost * pitchoverBoost;

// Stable angular-rate servo.
// The previous explicit-Euler controller divided by tauRate/tauDamp and then
// integrated with dt. In terminal flight tau can fall below the 1/60 s fixed
// step, which numerically flips the rate sign every tick (commanded dive while
// the velocity vector keeps climbing). Use the exact first-order response for
// the rate error, then enforce the same physical angular-acceleration limits.
const rateAlpha = 1.0 - Math.exp(-dt / Math.max(1e-4, tauRate));
let yawRateDeltaCmd = (omegaYawCmd - m.yawRate) * rateAlpha;
let pitRateDeltaCmd = (omegaPitCmd - m.pitchRate) * rateAlpha;
yawRateDeltaCmd = clamp(yawRateDeltaCmd, -yawAccMax * dt, yawAccMax * dt);
pitRateDeltaCmd = clamp(pitRateDeltaCmd, -pitAccMax * dt, pitAccMax * dt);
if(m.isESSM&&m.tvcEnabled&&(m.vlsPhase===true||m.pitchoverPhase===true)){
  const aeroServoShare=clamp((m.qbar??0)/12000,0.02,0.30);
  yawRateDeltaCmd*=aeroServoShare;pitRateDeltaCmd*=aeroServoShare;
}
// tauDamp is retained as a diagnostic/tuning field, but no longer forms a
// second explicit 1/tau feedback term that can destabilize the integrator.
m._rateServoAlpha = rateAlpha;

// ===== TVC TORQUE (stage 3: force-vector rotation contribution) =====
// Real TVC: nozzle deflection creates lateral thrust component → torque about CoG
// This is a FORCE-BASED angular accel added on top of autopilot's aero-based accel.
let tvcYawAcc = 0;
let tvcPitAcc = 0;
if(m.tvcEnabled && (m.tvcAuthority ?? 0) > 0.01){
  const thrustN = missileThrustN(m) || 0;
  if(thrustN > 0){
    const momentArm = m.tvcMomentArmM ?? 1.6;
    // The nozzle's lateral force simultaneously translates the missile and creates a moment.
    // Pitch/yaw inertia uses a slender-cylinder transverse-axis approximation rather than
    // mass*momentArm² (which heavily overdamped a short ESSM-class airframe).
    const latForceYaw = thrustN * Math.sin(m.tvcYaw ?? 0);
    const latForcePit = thrustN * Math.sin(m.tvcPitch ?? 0);
    const bodyLen=Math.max(1,m._v1Profile?.lengthM??3.66),bodyRad=Math.max(.03,(m._v1Profile?.diameterM??.254)*.5);
    const I_approx=Math.max(1,(massKg/12)*(bodyLen*bodyLen+3*bodyRad*bodyRad));
    // Torque = F × arm,  α = τ / I
    const yawTorque = latForceYaw * momentArm;
    const pitTorque = latForcePit * momentArm;
    // Authority gates the contribution (low-q/early-boost only)
    tvcYawAcc = (yawTorque / I_approx) * (m.tvcAuthority ?? 0);
    tvcPitAcc = (pitTorque / I_approx) * (m.tvcAuthority ?? 0);
    // NaN guard
    if(!Number.isFinite(tvcYawAcc)) tvcYawAcc = 0;
    if(!Number.isFinite(tvcPitAcc)) tvcPitAcc = 0;
    // Launch-phase TVC must be allowed to rotate the small missile before aerodynamic control exists.
    // The old ±30 rad/s² cap made the requested 8 m pitch-over kinematically impossible.
    // Keep a high but finite SIM_TUNED cap during cell-clear/hard-over, then taper afterwards.
    const tvcAccCap=(m.vlsPhase===true)?120:((m.pitchoverPhase===true)?70:30);
    tvcYawAcc = clamp(tvcYawAcc, -tvcAccCap, tvcAccCap);
    tvcPitAcc = clamp(tvcPitAcc, -tvcAccCap, tvcAccCap);
    m._tvcAngularAccCap=tvcAccCap;
  }
}
// Debug state (stage 3 observability)
m.tvcYawAcc = tvcYawAcc;
m.tvcPitAcc = tvcPitAcc;

m.yawRate   += yawRateDeltaCmd + tvcYawAcc * dt;
m.pitchRate += pitRateDeltaCmd + tvcPitAcc * dt;

// ===== Extra aero rate damping (TVC-era safety net only) =====
// Prevents TVC from spinning the body faster than aero can keep up with.
// Autopilot tauDamp already provides primary damping — this is supplemental, weak.
// Stronger at high q (where alpha-spike from fast rotation is dangerous).
if(m.tvcEnabled){
  const qDampRef = 30000; // higher ref → weaker damping at mid q
  const qDamp01 = clamp(q / qDampRef, 0, 1.0);
  // Only 5% damping at low q, up to 25% damping at high q (per second)
  const dampPerSec = 0.05 + 0.20 * qDamp01;
  const dampFactor = Math.max(0, 1.0 - dampPerSec * dt);
  m.yawRate   *= dampFactor;
  m.pitchRate *= dampFactor;
}

// Rate limits (can't exceed G-limit implied omega)
const yawRateMax = omegaMaxTotal;
const pitRateMax = omegaMaxTotal;
m.yawRate   = clamp(m.yawRate,   -yawRateMax, yawRateMax);
m.pitchRate = clamp(m.pitchRate, -pitRateMax, pitRateMax);

// Integrate attitude (nose)
m.heading = angNorm(m.heading + m.yawRate * dt);
m.pitch   = clamp(m.pitch + m.pitchRate * dt, deg(-89.5), deg(89.5));

// optional debug/UI
m.cmdOmegaYaw = omegaYawCmd;
m.cmdOmegaPit = omegaPitCmd;
m.actOmegaYaw = m.yawRate;
m.actOmegaPit = m.pitchRate;
// backward-compat helpers (older code used omegaYaw/omegaPit)
m.omegaYaw = m.yawRate;
m.omegaPit = m.pitchRate;

// ===== TVC STATE UPDATE (stage 2: state tracking only, no force yet) =====
// Updates nozzle deflection state based on 3D LOS error; does NOT affect thrust yet.
if(m.tvcEnabled){
  // 1. Authority: fades with time and dynamic pressure
  const tvcDur = m.tvcDuration ?? 3.3;
  const timeAuth = 1.0 - clamp(m.life / Math.max(0.1, tvcDur), 0, 1);
  const qEnd = m.tvcEffEndQ ?? 30000;
  const qAuth = 1.0 - clamp(q / Math.max(1, qEnd), 0, 1);
  m.tvcAuthority = clamp(timeAuth * qAuth, 0, 1);
  // VLS phase AND pitchover: full authority regardless of q (nozzle is hot, demanding)
  if(m.vlsPhase === true){
    m.tvcAuthority = Math.max(m.tvcAuthority, 1.0);  // FULL authority during VLS
  }
  if(m.pitchoverPhase === true){
    m.tvcAuthority = Math.max(m.tvcAuthority, 0.95);
  }

  // 2. Commanded nozzle angles from 3D LOS error in body frame
  //    Target vector: from missile to current guidance aim (cmdX/Y/Z)
  if(m.tvcAuthority > 0.01){
    const tgtDx = cmdX - m.x;
    const tgtDy = cmdY - m.y;
    const tgtDz = cmdZ - (m.z ?? OWN_ALT_M);
    // Convert XY from pixels to meters for consistent angle computation
    const tgtDxM = worldToMeters(tgtDx);
    const tgtDyM = worldToMeters(tgtDy);
    const tgtDzM = tgtDz;
    const tgtRange3D = Math.sqrt(tgtDxM*tgtDxM + tgtDyM*tgtDyM + tgtDzM*tgtDzM);
    if(tgtRange3D > 1.0){
      // Desired nose direction
      const desiredHeading = Math.atan2(tgtDyM, tgtDxM);
      const desiredPitch = Math.atan2(tgtDzM, Math.sqrt(tgtDxM*tgtDxM + tgtDyM*tgtDyM));
      // Body-frame error = what nozzle should deflect to induce this turn
      const yawErr = angNorm(desiredHeading - m.heading);
      const pitchErr = desiredPitch - (m.pitch ?? 0);
      // Commanded deflection (radians), clamped to max deflection
      const maxYawRad = deg(m.tvcMaxDeflectYawDeg ?? 18);
      const maxPitRad = deg(m.tvcMaxDeflectPitchDeg ?? 18);
      // WIP40 PD TVC servo: position error creates the hard-over, body-rate feedback brakes it
      // before the nose overshoots through the sea-skimmer line.  This is still SIM_TUNED.
      const launchHard=m.vlsPhase===true, kp=launchHard?4.8:3.6, kd=launchHard?0.13:0.18;
      m.tvcCmdYaw = clamp(yawErr*kp-(m.yawRate??0)*kd, -maxYawRad, maxYawRad);
      m.tvcCmdPitch = clamp(pitchErr*kp-(m.pitchRate??0)*kd, -maxPitRad, maxPitRad);
    } else {
      m.tvcCmdYaw = 0;
      m.tvcCmdPitch = 0;
    }
  } else {
    // No authority → command nozzle to center
    m.tvcCmdYaw = 0;
    m.tvcCmdPitch = 0;
  }

  // 3. Slew-rate limited actuator: tvcYaw chases tvcCmdYaw at limited rate
  const slewYawRad = deg(m.tvcSlewRateYawDeg ?? 180);
  const slewPitRad = deg(m.tvcSlewRatePitchDeg ?? 180);
  const maxDeltaYaw = slewYawRad * dt;
  const maxDeltaPit = slewPitRad * dt;
  const errYaw = (m.tvcCmdYaw ?? 0) - (m.tvcYaw ?? 0);
  const errPit = (m.tvcCmdPitch ?? 0) - (m.tvcPitch ?? 0);
  m.tvcYaw = (m.tvcYaw ?? 0) + clamp(errYaw, -maxDeltaYaw, maxDeltaYaw);
  m.tvcPitch = (m.tvcPitch ?? 0) + clamp(errPit, -maxDeltaPit, maxDeltaPit);
}
// Dynamic AoA limit (shared)
const aoaMax = (m.aoaMax ?? deg(40));
const aoaMaxDyn = clamp(aoaMax, deg(6), deg(40));

// ✅ velFollowDyn을 "사용하기 전에" 먼저 선언
const baseFollow = (m.velFollowK0 ?? m.velFollowK ?? 2.2);
// 관성 강화(하지만 너무 둔해지지 않게): 급기동일수록 속도벡터가 늦게 따라오되, 터미널에서 기동성은 확보
const turnSeverity = clamp(omegaTotCmd / Math.max(1e-6, omegaMaxTotal), 0, 1);
// 기존(0.50)보다 완만하게 줄여서 "너무 둔함" 완화
const followPenaltyK = (0.25 - 0.10*termBoost01); // 터미널일수록 속도벡터가 더 빨리 따라옴
const followFactor = (0.98 + 0.32*(1.0 - v01)) * (1.0 - followPenaltyK*turnSeverity);
const velFollowTermBoost = lerp(1.0, 1.85, termBoost01); // stronger terminal tracking
var seekerVFBoost = (m.sarhAlive || m.essmActiveSeeker) ? (m.isESSM ? 1.15 : 1.10) : 1.0;
// High-diver + seeker-active: extra lateral velocity follow
if(m.apnTargetIsHighDiver && (m.sarhAlive || m.essmActiveSeeker)){
  seekerVFBoost *= 1.05;
}
// WIP40: TVC launch flight-path rotation is force-driven, not a synthetic body→velocity snap.
// Keep only a very weak numerical/aero follow term while physical vectored thrust owns the turn.
const launchPhysicalVectoring=m.isESSM&&(m.vlsPhase===true||m.pitchoverPhase===true)&&m.tvcEnabled;
const velFollowRaw=baseFollow*followFactor*velFollowTermBoost*seekerVFBoost;
const velFollowDyn=launchPhysicalVectoring?clamp(velFollowRaw*0.05,0.05,0.18):clamp(velFollowRaw,0.35,25.0);
const prevVelAngle = m.velAngle;
const prevVelPitch = (m.velPitch ?? 0);

let aoaPitchErr = (m.pitch - m.velPitch);
aoaPitchErr = clamp(aoaPitchErr, -aoaMaxDyn, aoaMaxDyn);
m.velPitch = clamp(m.velPitch + aoaPitchErr * velFollowDyn * dt, deg(-85), deg(85));

// ===== AoA / velAngle 안정화 =====
let aoaErr = angNorm(m.heading - m.velAngle);

// AoA 제한(절대 NaN 방지)
aoaErr = clamp(aoaErr, -aoaMaxDyn, aoaMaxDyn);

// velAngle 업데이트
m.velAngle = angNorm(m.velAngle + aoaErr * velFollowDyn * dt);

// ===== G-load estimate (update display + liftAssist) =====
// 속도 벡터가 dt 동안 얼마나 꺾였는지(요/피치)로 가속도 -> G 로드 계산
const dtSafe = Math.max(1e-6, dt);
const dYaw = angNorm(m.velAngle - prevVelAngle);
const dPit = (m.velPitch ?? 0) - prevVelPitch;
const omegaYaw = dYaw / dtSafe;
const omegaPit = dPit / dtSafe;
const omegaTot = Math.hypot(omegaYaw, omegaPit);
const vNowMps = Math.max(1.0, worldSpeedToMps(m.speed));
const aNormal = vNowMps * omegaTot;  // m/s^2
const gLoad = Math.sqrt(1 + (aNormal/G0)*(aNormal/G0));
m.curG = clamp(gLoad, 1.0, (m.gLimitDyn ?? m.gLimit ?? 40));
    // Rebuild velocity components from current speed & velocity angles (keep them consistent)
    const v_mps_now = Math.max(10, worldSpeedToMps(m.speed));
    let cosP = Math.cos(m.velPitch ?? 0);
    m.vx = Math.cos(m.velAngle) * m.speed * cosP;
    m.vy = Math.sin(m.velAngle) * m.speed * cosP;
    m.vz = Math.sin(m.velPitch ?? 0) * v_mps_now;

    // ===== WIP40 physical TVC/body-thrust normal acceleration =====
    // This is the normal component saved from the real 3-D gimballed thrust vector above.  It turns
    // the velocity vector without directly editing velPitch or vz toward a desired state.
    if((m._tvcThrustNormalAx??0)!==0||(m._tvcThrustNormalAy??0)!==0||(m._tvcThrustNormalAz??0)!==0){
      m.vx+=mpsToWorldSpeed((m._tvcThrustNormalAx??0)*dt);
      m.vy+=mpsToWorldSpeed((m._tvcThrustNormalAy??0)*dt);
      m.vz=(m.vz??0)+(m._tvcThrustNormalAz??0)*dt;
      const newVx_mps=worldSpeedToMps(m.vx),newVy_mps=worldSpeedToMps(m.vy),newVz_mps=m.vz,newSpd_mps=Math.hypot(newVx_mps,newVy_mps,newVz_mps);
      if(newSpd_mps>1){m.speed=mpsToWorldSpeed(newSpd_mps);m.velAngle=Math.atan2(newVy_mps,newVx_mps);m.velPitch=Math.atan2(newVz_mps,Math.hypot(newVx_mps,newVy_mps));}
    }

    // gravity: 수직속도에 중력 적용 (탄도 낙하)
    // gravity + lift: 기동 중(고G)엔 일부 양력/받음각 효과로 중력 체감이 줄어듦
    const gNow2 = Math.max(1.0, m.curG || 1.0);
    const gLim2 = (m.gLimitDyn ?? m.gLimit ?? 40);
    const liftAssist = clamp((gNow2 - 1.0) / Math.max(1e-6, (gLim2 - 1.0)), 0, 1) * 0.65;

    m.vz = (m.vz ?? 0) - G0 * (1.0 - liftAssist) * dt;
    // Legacy sea-level velocity clip.  WIP40 v1 ESSM uses a predictive pitch-command guard
    // instead of directly editing vertical velocity (direct clipping hid control-law failures).
    if(!(m.guidanceCore==='v1' && m.isESSM) && (m.z ?? 0) < 50 && m.vz < -120){
      m.vz = Math.max(m.vz, -120 * clamp((m.z ?? 0) / 50, 0.1, 1.0));
    }
    // Climbing missile: reduce gravity penalty when missile is thrusting upward
    // (thrust vector has vertical component that partially counters gravity)
    if(m.vz > 0 && missileThrustN(m) > 1000){
      const thrustLiftFrac = clamp(Math.sin(m.velPitch ?? 0) * 0.3, 0, 0.25);
      m.vz += G0 * thrustLiftFrac * dt; // partial gravity offset from thrust
    }

    // 중력 적용 후 속도벡터 pitch를 재정렬 + vx/vy도 그에 맞춰 재계산 (NaN 방지)
    m.velPitch = Math.asin(clamp((m.vz ?? 0) / v_mps_now, -0.99, 0.99));
    cosP = Math.cos(m.velPitch ?? 0);
    m.vx = Math.cos(m.velAngle) * m.speed * cosP;
    m.vy = Math.sin(m.velAngle) * m.speed * cosP;
    m.vz = Math.sin(m.velPitch ?? 0) * v_mps_now;


    m.x += m.vx * dt;
    m.y += m.vy * dt;
    m.z = (m.z ?? OWN_ALT_M) + (m.vz ?? 0) * dt;
    if(_surfaceStepStart&&surfaceMissileSweptContactWip13C5(m,_surfaceStepStart))return;
    // Altitude floor: destroy missile if it hits the sea
    if(m.z < 0 && !m.vlsPhase){
      wip173PushVisualEvent('SEA_IMPACT',{x:m.x,y:m.y,z:0,
        vxMps:worldSpeedToMps(m.vx??0),vyMps:worldSpeedToMps(m.vy??0),vzMps:Number(m.vz)||0,
        weaponType:m.isESSM?'ESSM':'SM2',massKg:Number(m.massKg)||Number(m._v1Profile?.launchMassKg)||200,impactSpeedMps:worldSpeedToMps(m.speed??0)});
      m._deathReason = 'SEA_IMPACT';
      m.dead = true;
      const mLabel = m.isESSM ? 'ESSM E' : 'SM-2 M';
      const _closeInfoSea = m._everClosest != null ? ` (closest ${Math.round(m._everClosest*1000)}m)` : '';
      notify(`🌊 ${mLabel}${m.id} 해면충돌${_closeInfoSea}`);
      return;
    }
    m.z = Math.max(0, m.z);
// (removed) ad-hoc post-burn energy loss; now handled by drag + induced drag


}

  // ===== Speed-fuse: Mach 0.5 이하로 떨어지면 자폭 (부스트 후에만) =====
const machNow = worldSpeedToMps(m.speed) / speedOfSoundMps(m.z ?? OWN_ALT_M);

if(!Number.isFinite(machNow)){
  m._deathReason = 'SPEED_NAN';
  m.dead = true;
  notify(`속도 계산 오류 자폭: M${m.id}`);
  return;
}

// SAM: 발사 후 부스트 완료 전까지는 저속 자폭 면제 (부스터 가속 시간 필요)
const propulsionEndSec = Math.max(
  (m.burnTotal ?? 0),
  (m.burn1 ?? 0) + (m.burn2 ?? 0)
);
if(machNow <= 0.50 && m.life > propulsionEndSec + 2.0){
  m._deathReason = 'LOW_SPEED';
  m.dead = true;
  const _closeInfoS = m._everClosest != null ? ` (closest ${Math.round(m._everClosest*1000)}m)` : '';
  const _mLbl2 = m.isESSM ? 'E' : 'M';
  notify(`💨 속도저하: ${_mLbl2}${m.id} M${machNow.toFixed(2)}${_closeInfoS}`);
  return;
}

    // ===== PROXIMITY FUZE (Radar_v6_12 style) =====
    // Always track assigned target from far range — no _fuzeCheck gating
    let killTarget = null, killX, killY, killZ;
    const assignId = surfaceMissileRuntimeWip13C6(m)?null:m.assignedTargetId;

    if(physicalShipsB().length){
    killTarget=navalFuzeTargetD(m,ACTIVE_SHIP_RUNTIME);
    if(killTarget){killX=killTarget.x;killY=killTarget.y;killZ=killTarget.z??0;}
    }
    if(!killTarget){
    // Prefer seeker-locked target; fall back to assigned
    if(!surfaceMissileRuntimeWip13C6(m)&&m.seekerLocked && m.seekerLockId != null){
      const tgt=truthObjectForTrackV27(m.seekerLockId,true);
      if(tgt){killTarget=tgt;killX=tgt.x;killY=tgt.y;killZ=tgt.z;}
    }
    if(!killTarget && assignId != null){
      const tgt=truthObjectForTrackV27(assignId,true);
      if(tgt){killTarget=tgt;killX=tgt.x;killY=tgt.y;killZ=tgt.z;}
    }

    }
    // DIAGNOSTIC: track frame-by-frame fuze state for armed missiles
    // If armed missile loses target (ASM hit ship, self-destruct, etc.),
    // report closest-pass as miss instead of silent death
    if(m.proxArmed && !m.proxDetonated && !m.missedTarget){
      if(!killTarget){
        if(!m._lostTargetNotified){
          m._lostTargetNotified = true;
          const _mId_lost = (m.isESSM ? 'E' : 'M') + m.id;
          // Report what the closest pass was
          const _closestKm = m.proxMissDistKm ?? m.closestKm ?? 999;
          if(_closestKm < 1.0){  // was actually close (< 1km)
            // Treat as miss — missile got close but target vanished before fuze trigger
            m.missedTarget = true;
            m._missTime = m.life;
            notify(`빗나감 (표적 소실): ${_mId_lost} closest ${Math.round(_closestKm*1000)}m`);
          } else {
            notify(`⚠ 표적 소실: ${_mId_lost} (closest ${Math.round(_closestKm*1000)}m)`);
          }
        }
      }
    }
    // WIP75: passive rolling telemetry only; it does not feed guidance or fuze logic.
    _wip75RecordGuidanceSample(m);
    if(killTarget && !m.proxDetonated && !m.missedTarget){
      const dkm = dist3Km(m.x,m.y,(m.z ?? OWN_ALT_M), killX, killY, killZ);

      // ===== CPA calculation (UNIFIED METERS) =====
      // Previous version mixed px for XY and m for Z → dotPV meaningless, tMin always clamped to dt
      // All values normalized to meters / meters-per-second for consistent math.
      // Missile velocity (m/s, world frame)
      const mslVxMps = worldSpeedToMps(m.vx ?? (Math.cos(m.velAngle ?? m.heading) * (m.speed ?? 0)));
      const mslVyMps = worldSpeedToMps(m.vy ?? (Math.sin(m.velAngle ?? m.heading) * (m.speed ?? 0)));
      const mslVzMps = m.vz ?? 0;
      // Target velocity (m/s, world frame)
      const tgtVxMps_c = worldSpeedToMps(killTarget.vx ?? 0);
      const tgtVyMps_c = worldSpeedToMps(killTarget.vy ?? 0);
      const tgtVzMps_c = killTarget.vz ?? 0;
      // Relative position (meters, world frame)
      const relXm = worldToMeters(m.x - killX);
      const relYm = worldToMeters(m.y - killY);
      const relZm = (m.z ?? OWN_ALT_M) - killZ;
      // Relative velocity (m/s)
      const relVxMps = mslVxMps - tgtVxMps_c;
      const relVyMps = mslVyMps - tgtVyMps_c;
      const relVzMps = mslVzMps - tgtVzMps_c;
      // Dot products — now unit-consistent
      const dotPV = relXm * relVxMps + relYm * relVyMps + relZm * relVzMps;
      const dotVV = relVxMps * relVxMps + relVyMps * relVyMps + relVzMps * relVzMps;
      // True time of closest approach (seconds)
      const tMinRaw = dotVV > 1e-6 ? -dotPV / dotVV : 0;
      // Sub-frame interpolation: clamp to [-dt, dt] for frame-level CPA
      const tMinSubframe = clamp(tMinRaw, -dt, dt);
      // Sub-frame CPA position (still meters)
      const cXm = relXm + relVxMps * tMinSubframe;
      const cYm = relYm + relVyMps * tMinSubframe;
      const cZm = relZm + relVzMps * tMinSubframe;
      const interpClosest3D = Math.sqrt(cXm*cXm + cYm*cYm + cZm*cZm);
      const interpClosestKm = interpClosest3D / 1000;

      // WIP75: snapshot the best sub-frame CPA seen so far. No value below is consumed by
      // guidance, dynamics or fuze logic; this block is strictly observational.
      if(!m.isESSM && interpClosest3D < (m._wip75BestCpaM ?? Infinity)){
        m._wip75BestCpaM=interpClosest3D;
        const cpaTimeS=(m.life??0)+tMinSubframe;
        m.cpaTimeS=cpaTimeS;
        m.cpaDistM=interpClosest3D;
        m.cpaAltM=(m.z??0)+mslVzMps*tMinSubframe;
        m.cpaTgtAltM=killZ+tgtVzMps_c*tMinSubframe;
        m.cpaMslVzMps=mslVzMps;
        m.cpaMslSpeedMps=Math.hypot(mslVxMps,mslVyMps,mslVzMps);
        m.cpaAvailableG=Number.isFinite(m.availableG)?m.availableG:null;
        m.cpaCommandG=Number.isFinite(m._v1GCommand)?m._v1GCommand:null;
        m.cpaSaturated=!!m._v1Saturated;
        const t2=_wip75NearestGuidanceSample(m,cpaTimeS-2.0);
        m.t2AvailableG=t2?.availableG??null;
        m.t2CommandG=t2?.commandG??null;
        m.t2AltM=t2?.altM??null;
        m.t2SpeedMps=t2?.speedMps??null;
        m.t2GRatio=(Number.isFinite(m.t2AvailableG)&&m.t2AvailableG>1e-9&&Number.isFinite(m.t2CommandG))
          ? (m.t2CommandG/m.t2AvailableG) : null;
        m.pipAltErrorM=(Number.isFinite(m._pipSnapAltM)&&Number.isFinite(m.cpaAltM))
          ? (m._pipSnapAltM-m.cpaAltM) : null;
        m.climbingIntercept=mslVzMps>0;
      }

      // Predicted CPA (NOT clamped to dt) — future closest approach if trajectories held
      // This is for GUIDANCE use: "how close will I miss at this rate?"
      // Only meaningful if closing (tMinRaw > 0, i.e., haven't passed CPA yet)
      let predictedCPAm = null;
      let predictedCPATime = null;
      let zemXm = 0, zemYm = 0, zemZm = 0; // zero-effort-miss vector (m, missile→CPA point)
      if(tMinRaw > 0 && tMinRaw < 60){
        // Future relative position at CPA (meters, missile position - target position)
        const fXm = relXm + relVxMps * tMinRaw;
        const fYm = relYm + relVyMps * tMinRaw;
        const fZm = relZm + relVzMps * tMinRaw;
        predictedCPAm = Math.sqrt(fXm*fXm + fYm*fYm + fZm*fZm);
        predictedCPATime = tMinRaw;
        // ZEM: missile will be at this offset from target at CPA time
        // To fix the miss, guidance should push missile in -ZEM direction
        zemXm = fXm;
        zemYm = fYm;
        zemZm = fZm;
      }
      m._predictedCPAm = predictedCPAm;
      m._predictedCPATime = predictedCPATime;
      m._zemXm = zemXm;
      m._zemYm = zemYm;
      m._zemZm = zemZm;

      // Effective closest-so-far (for proximity fuze) = min of current dist, sub-frame CPA
      const effDkm = Math.min(dkm, interpClosestKm);
      // Track the closest approach ever (for debug on missile death)
      if(m._everClosest == null || effDkm < m._everClosest){
        m._everClosest = effDkm;
      }

      // (1) Arm fuze when entering arm range
      const _armFuzeProfile = _wip143FuzeParamsForMissile(m);
      const armRange = m.proxArmRangeKm ?? (Number(_armFuzeProfile?.armingRangeKm) || (m.isESSM ? 1.6 : 2.2));
      if(effDkm < armRange){
        if(!m.proxArmed){
          const _mId_arm = (m.isESSM ? 'E' : 'M') + m.id;
          const _predStr = (predictedCPAm != null)
            ? ` pred=${predictedCPAm.toFixed(0)}m@${(predictedCPATime ?? 0).toFixed(2)}s`
            : '';
          // Add missile vs target altitude/position breakdown
          const _mAlt_arm = Math.round(m.z ?? 0);
          const _tgtAlt_arm = Math.round(killTarget.z ?? 0);
          const _altDelta = _mAlt_arm - _tgtAlt_arm;
          // Horizontal vs vertical breakdown of CPA
          const _zemX = m._zemXm != null ? Math.round(m._zemXm) : '?';
          const _zemY = m._zemYm != null ? Math.round(m._zemYm) : '?';
          const _zemZ = m._zemZm != null ? Math.round(m._zemZm) : '?';
          notify(`📡 신관 ${_mId_arm} ${(effDkm*1000).toFixed(0)}m${_predStr} mAlt=${_mAlt_arm} tgtAlt=${_tgtAlt_arm} ZEM=(${_zemX},${_zemY},${_zemZ})`);
        }
        m.proxArmed = true;
      }

      // (2) Track proxMissDistKm — always update from armed onward
      if(effDkm < (m.proxMissDistKm ?? 999)){
        m.proxMissDistKm = effDkm;
        m.afterClosestTimer = 0;
      } else {
        m.afterClosestTimer = (m.afterClosestTimer ?? 0) + dt;
      }
      // Also maintain legacy closestKm for compat
      if(effDkm < (m.closestKm ?? 999)) m.closestKm = effDkm;

      // (3) CPA-timed proximity-fuze logic.
      // The old "inside detection radius => detonate immediately" rule exploded
      // at the *outer edge* of the fuze volume (e.g. 59 m for a 60 m ESSM
      // detector) even when the predicted trajectory was a direct hit. That
      // turned a successful guidance solution into an artificial low-Pk burst.
      // A proximity fuze senses range/range-rate and times the burst near CPA.
      const mslSpd = Math.max(50, worldSpeedToMps(m.speed));

      // Fuze detection radius (game-tuned / profile-owned).
      const fuzeDetectM = _wip143FuzeDetectRadiusM(m);

      // WIP99-1: fragment flight-time lead. The legacy 30/Vmissile post-CPA delay
      // pointed in the wrong temporal direction. Estimate the fragment time of flight
      // from the predicted miss and open the imminent-CPA gate that much EARLIER.
      const _fuzeWeaponType = m.isESSM ? 'ESSM' : 'SM2';
      const _fuzeExpectedMissM = Number.isFinite(predictedCPAm)
        ? Math.max(0,predictedCPAm)
        : Math.max(0,Math.min(interpClosest3D,(m.proxMissDistKm??999)*1000));
      const _fuzeLeadTimeS = _wip99FragmentLeadTimeS(_fuzeExpectedMissM,_fuzeWeaponType);
      const _fuzeParams = _wip143FuzeParamsForMissile(m);
      const _fuzeProcessingDelayS = _fuzeParams.processingDelay.enabled
        ? Math.max(0,Number(_fuzeParams.processingDelay.delayS)||0) : 0;

      // Trigger only when CPA is imminent/passed, or when a very-low-range-rate
      // target remains inside the fuze volume. Sub-frame CPA is already solved
      // in SI units above, so use it instead of the current sphere-entry range.
      const _futureCpaInside = predictedCPAm != null && predictedCPAm < fuzeDetectM;
      const _cpaImminent = _futureCpaInside && predictedCPATime != null
                           && predictedCPATime >= 0 && predictedCPATime <= _fuzeLeadTimeS + _fuzeProcessingDelayS + dt * 1.25;
      // Passed-CPA remains a numerical/fallback path only; it no longer carries the
      // old missile-speed-derived post-CPA delay.
      const _passedClose = m.proxArmed && (m.proxMissDistKm ?? 999) * 1000 < fuzeDetectM
                           && (tMinRaw <= 0 || m.afterClosestTimer > 0.05);
      const _relSpeed = Math.sqrt(dotVV);
      const _dwellInside = m.proxArmed && dkm * 1000 < fuzeDetectM && _relSpeed < 25;
      if(_dwellInside) m._fuzeDwell = (m._fuzeDwell ?? 0) + dt;
      else m._fuzeDwell = 0;
      const _slowDwellTrigger = (m._fuzeDwell ?? 0) >= 0.05;
      const _fuzeCandidate = _cpaImminent || _passedClose || _slowDwellTrigger;

      // WIP99-2 sea-clutter false burst occurs only before a valid target candidate.
      // It consumes the interceptor but is NOT counted as a valid target proximity actuation.
      if(!_fuzeCandidate && _fuzeParams.seaClutter.enabled){
        const _clutter=_wip99SeaClutterFalseTrigger(m,killTarget,dt,dkm*1000);
        m._fuzeStage2LastClutter=_clutter;
        if(_clutter.trigger){
          m._fuzeTriggerReason='clutter-early';m._fuzeStage2TerminalReason='clutter-early';m._fuzeBurstMissM=dkm*1000;
          m.proxDetonated=false;m._deathReason='FUZE_CLUTTER_EARLY';m.dead=true;
          if(m.isESSM)WIP143_TDD_EVENT_TRACE.push({kind:'CLUTTER_EARLY',missileId:m.id,lifeS:m.life,rangeM:dkm*1000,missileAltM:m.z??0,targetAltM:killTarget.z??0,clutter:{..._clutter}});
          debugLog(`WIP99 FUZE clutter-early ${(m.isESSM?'E':'M')+m.id} range=${(dkm*1000).toFixed(1)}m alt=${(m.z??0).toFixed(1)}m sea=${seaStateFactor.toFixed(2)}`);
          return;
        }
      }

      // WIP99-2: TDD/receiver acquisition is latched while the target is physically
      // inside the detection volume. Once a valid in-beam return is acquired, the CPA timer
      // owns burst timing; LOS rotation after closest approach does not retroactively erase a
      // real detection. This is both more physical and prevents a head-on pass from becoming
      // an artificial beam-out solely because the fallback frame occurs just after CPA.
      const _stage2SenseEnabled=_fuzeParams.tddBeam.enabled||_fuzeParams.detectionReliability.enabled;
      if(_stage2SenseEnabled && m.proxArmed && dkm*1000 < fuzeDetectM){
        const _sense=_wip99Stage2CandidateDecision(m,killTarget,relXm,relYm,relZm,dotPV);
        m._fuzeStage2LastDecision=_sense;
        if(_sense?.beam?.covered || !_fuzeParams.tddBeam.enabled)m._fuzeStage2BeamSeen=true;
        if(_sense.allow){
          m._fuzeStage2Detected=true;
          if(!m._fuzeStage2DetectionSnapshot){
            m._fuzeStage2DetectionSnapshot=_sense;
            if(m.isESSM)WIP143_TDD_EVENT_TRACE.push({kind:'DETECTION',missileId:m.id,lifeS:m.life,rangeM:dkm*1000,missileAltM:m.z??0,targetAltM:killTarget.z??0,beam:_sense.beam?{..._sense.beam}:null,detection:_sense.detection?{..._sense.detection}:null});
          }
          m._fuzeStage2LastRejectReason=null;
        } else if(!m._fuzeStage2Detected){
          m._fuzeStage2LastRejectReason=_sense.reason;
        }
      }

      let _fuzeCandidateAllowed=_fuzeCandidate;
      if(_fuzeCandidate && _stage2SenseEnabled && !m._fuzeStage2Detected){
        _fuzeCandidateAllowed=false;
        // Preserve the causal reason for validation: if the antenna lobe was ever crossed
        // but no return reached the Pd threshold, this is detection-failed, not beam-out.
        m._fuzeStage2LastRejectReason=m._fuzeStage2BeamSeen?'detection-failed':'beam-out';
      }

      if(_fuzeCandidateAllowed){
        // For an imminent CPA use the analytically predicted miss distance; for
        // a passed CPA use the best measured/sub-frame closest distance.
        const actualMissM = _cpaImminent
          ? Math.min(predictedCPAm ?? Infinity, interpClosest3D, (m.proxMissDistKm ?? 999)*1000)
          : Math.min((m.proxMissDistKm ?? 999)*1000, interpClosest3D);
        const _mId_cpa = (m.isESSM ? 'E' : 'M') + m.id;
        const _trigReason = _cpaImminent ? 'predicted-cpa'
                           : _slowDwellTrigger ? 'slow-dwell'
                           : 'passed-cpa';
        const _predCpaStr = (m.guidanceCore === 'v1' && m._v1PredCPA != null)
          ? ` pred=${m._v1PredCPA.toFixed(0)}m` : '';
        notify(`🎯 CPA: ${_mId_cpa} = ${actualMissM.toFixed(1)}m [${_trigReason}]${_predCpaStr}`);
        m._fuzeBurstMissM = actualMissM;

        const interceptKin = _wip88InterceptKinematics(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0,worldSpeedToMps(killTarget.vx??0),worldSpeedToMps(killTarget.vy??0),killTarget.vz??0);
        // WIP144: one ESSM-only field-quality draw per detonation. This changes useful spatial density,
        // never the physical 1,900-fragment inventory, and uses an isolated deterministic event stream.
        if(m.isESSM){const _ffe=_wip144EssmFieldEfficiencyForEvent(m,killTarget);m._wip144FragmentFieldEfficiency=_ffe;interceptKin.fragmentFieldEfficiency=_ffe;}
        const closingSpd = interceptKin.relativeSpeedMps;
        const isASM = (killTarget.label != null);
        // WIP115 identity boundary: truthTargetLabel is PHYSICS-ONLY (Pk / damage-model selection).
        // Decisions and player-facing text must use observation-derived track classification instead.
        const truthTargetLabel = isASM ? (killTarget.label ?? 'Kh-35U') : (killTarget.acType ?? 'aircraft');
        const displayTargetLabel = trackDisplayLabelOr(m.assignedTargetId,isASM?'ASM':'AIR');
        const _wpnT = m.isESSM ? 'ESSM' : 'SM2';
        const _wpnL = m.isESSM ? 'ESSM' : 'SM-2';
        const _mId = (m.isESSM ? 'E' : 'M') + m.id;

        // WIP99-1 Pk geometry: evaluate where the target/missile relative state is
        // when fragments ARRIVE, not at burst instant. For an analytically imminent
        // CPA, burstOffsetS represents the within-frame time until the ideal lead point.
        const _fragmentFlightTimeS = _wip99FragmentLeadTimeS(actualMissM,_wpnT);
        const _detectionOffsetS = _cpaImminent && Number.isFinite(predictedCPATime)
          ? clamp(predictedCPATime-_fragmentFlightTimeS-_fuzeProcessingDelayS,0,dt*1.25)
          : 0;
        const _burstOffsetS = _cpaImminent
          ? _detectionOffsetS+_fuzeProcessingDelayS
          : _fuzeProcessingDelayS;
        const _fragmentArrival = _wip99FragmentArrivalGeometry(
          relXm,relYm,relZm,relVxMps,relVyMps,relVzMps,_burstOffsetS,_fragmentFlightTimeS);
        const _fragmentArrivalMissM = _fragmentArrival.missM;
        m._fuzeTriggerReason=_trigReason;
        m._fuzeFragmentSpeedMps=_wip99FragmentSpeedMps(_wpnT);
        m._fuzeFragmentFlightTimeS=_fragmentFlightTimeS;
        m._fuzeBurstOffsetS=_burstOffsetS;
        m._fuzeFragmentArrivalMissM=_fragmentArrivalMissM;
        if(m.isESSM)WIP143_TDD_EVENT_TRACE.push({kind:'TRIGGER',missileId:m.id,lifeS:m.life,triggerReason:_trigReason,fuzeDetectM,actualMissM,predictedCPAm,predictedCPATimeS:predictedCPATime,processingDelayS:_fuzeProcessingDelayS,fragmentFlightTimeS:_fragmentFlightTimeS,burstOffsetS:_burstOffsetS,fragmentArrivalMissM:_fragmentArrivalMissM,detectionSnapshot:m._fuzeStage2DetectionSnapshot?JSON.parse(JSON.stringify(m._fuzeStage2DetectionSnapshot)):null});

        const _stage2TimingExit = _fuzeParams.processingDelay.enabled
          && actualMissM < fuzeDetectM && _fragmentArrivalMissM >= fuzeDetectM;
        if(_stage2TimingExit){
          m._fuzeStage2TerminalReason='processing-delay-timing-exit';m.proxDetonated=false;
          m._deathReason='FUZE_PROCESSING_TIMING_EXIT';m.dead=true;
          debugLog(`WIP99 FUZE timing-exit ${_mId} burstMiss=${actualMissM.toFixed(1)}m arrival=${_fragmentArrivalMissM.toFixed(1)}m delay=${_fuzeProcessingDelayS.toFixed(4)}s`);
        } else if(actualMissM < fuzeDetectM){
          // Fuze detonates — evaluate with Pk system (naval style retained)
          m.proxDetonated = true;m._fuzeStage2TerminalReason=null;

          if(isASM){
            if(WIP87_CASE_META){
              WIP87_PROX_CONTEXT={triggerReason:_trigReason,actualMissM:_wip87Finite(actualMissM),fuzeDetectM:_wip87Finite(fuzeDetectM),predictedCPAm:_wip87Finite(predictedCPAm),predictedCPATimeS:_wip87Finite(predictedCPATime),interpClosest3DM:_wip87Finite(interpClosest3D),proxMissDistM:_wip87Finite((m.proxMissDistKm??999)*1000),fragmentSpeedMps:_wip87Finite(m._fuzeFragmentSpeedMps),fragmentFlightTimeS:_wip87Finite(_fragmentFlightTimeS),burstOffsetS:_wip87Finite(_burstOffsetS),fragmentArrivalMissM:_wip87Finite(_fragmentArrivalMissM),processingDelayS:_wip87Finite(_fuzeProcessingDelayS),tddBeam:(m._fuzeStage2DetectionSnapshot??m._fuzeStage2LastDecision)?.beam?{...(m._fuzeStage2DetectionSnapshot??m._fuzeStage2LastDecision).beam}:null,detection:(m._fuzeStage2DetectionSnapshot??m._fuzeStage2LastDecision)?.detection?{...(m._fuzeStage2DetectionSnapshot??m._fuzeStage2LastDecision).detection}:null,cpaDistM:_wip87Finite(m.cpaDistM),cpaAltM:_wip87Finite(m.cpaAltM),cpaTgtAltM:_wip87Finite(m.cpaTgtAltM),missileLifeS:_wip87Finite(m.life),missileSpeedMps:_wip87Finite(worldSpeedToMps(m.speed??0)),targetAltM:_wip87Finite(killTarget.z),targetSpeedMps:_wip87Finite(killTarget.speedMps??worldSpeedToMps(Math.hypot(killTarget.vx??0,killTarget.vy??0))),fragmentFieldEfficiency:_wip87Finite(m._wip144FragmentFieldEfficiency)};
            }
            const pk = computeInterceptPk(_fragmentArrivalMissM, _wpnT, truthTargetLabel, closingSpd, interceptKin);
            let result;
            if(WIP87_CASE_META){
              const _w87OrigSimRandom=simRandom,_w87Rng=[];
              try{simRandom=function(){const v=_w87OrigSimRandom();_w87Rng.push(v);return v;};result=applyInterceptResult(pk, killTarget, _wpnL);}
              finally{simRandom=_w87OrigSimRandom;}
              SIM_TEST_WIP87_PK_TRACE.push({...(WIP87_PENDING_PK??{caseMeta:{...WIP87_CASE_META},calculatedPk:_wip87Finite(pk)}),simRandom1:_wip87Finite(_w87Rng[0]),simRandom2:_wip87Finite(_w87Rng[1]),additionalRandoms:_w87Rng.slice(2),damageThreshold:_wip87Finite(pk*0.7),applyInterceptResult:result,rngStateAfterApply:SIM_RNG_STATE>>>0,targetAliveAfter:!!killTarget.alive,targetStructDmg:_wip87Finite(killTarget._structDmg??0)});
              WIP87_PENDING_PK=null;WIP87_PROX_CONTEXT=null;
            } else result=applyInterceptResult(pk, killTarget, _wpnL);
            m._deathReason = 'PROX_DETONATION_' + result;
            wip173RecordInterceptBurst(m,_wpnT,killTarget,result);
            m.dead = true;
            // REPAIR-2 §13: Kh-32 mission-kill layer (v1) — 크고 빠른 표적은
            // 구조적으로 생존해도 missionKillRadiusM 내 근접파편으로 시커/조종/
            // 구조 손상을 입을 수 있다. Pk를 올리지 않고 '기능 상실'을 모델링.
            if(m.guidanceCore === 'v1' && m._v1Profile && result !== 'KILL'
               && killTarget.alive
               && truthTargetLabel.indexOf('Kh-32') !== -1
               && actualMissM < (m._v1Profile.missionKillRadiusM ?? 80)){
              const _roll = simRandom();
              if(_roll < 0.40){
                killTarget.seekerOn = false;
                killTarget.seekerLocked = false;
                killTarget._v1SeekerKilled = true;
                notify(`🛠 임무파괴(시커): ${displayTargetLabel} ← ${_mId} (${Math.round(actualMissM)}m)`);
                debugLog(`v1 missionKill: ${_mId} → ${truthTargetLabel} SEEKER (${Math.round(actualMissM)}m)`);
              } else if(_roll < 0.70){
                killTarget.vx += mpsToWorldSpeed(rand(-50, 50));
                killTarget.vy += mpsToWorldSpeed(rand(-50, 50));
                killTarget.vz = (killTarget.vz ?? 0) + rand(-35, 15);
                killTarget._v1CtrlDamaged = true;
                notify(`🛠 임무파괴(조종): ${displayTargetLabel} 궤도이탈 ← ${_mId} (${Math.round(actualMissM)}m)`);
                debugLog(`v1 missionKill: ${_mId} → ${truthTargetLabel} CONTROL (${Math.round(actualMissM)}m)`);
              } else if(killTarget.speedMps != null){
                killTarget.speedMps *= 0.78;
                killTarget._v1StructDamaged = true;
                notify(`🛠 임무파괴(구조): ${displayTargetLabel} 감속 ← ${_mId} (${Math.round(actualMissM)}m)`);
                debugLog(`v1 missionKill: ${_mId} → ${truthTargetLabel} STRUCT (${Math.round(actualMissM)}m)`);
              }
            }
            const isDirect = actualMissM < 2.0;
            if(result === 'KILL'){
              const hitType = isDirect ? '직격!' : '요격 성공!';
              notify(hitType + ' ← ' + _mId + ' (' + Math.round(actualMissM) + 'm, Pk ' + Math.round(pk*100) + '%)');
            } else if(result === 'STRUCT_FAIL'){
              notify('구조파괴! ← ' + _mId + ' (' + Math.round(actualMissM) + 'm)');
            } else if(result === 'DAMAGED'){
              notify('파편 피해! ' + displayTargetLabel + ' ← ' + _mId + ' (' + Math.round(actualMissM) + 'm)');
            } else {
              notify('요격 실패! ' + _mId + ' (' + Math.round(actualMissM) + 'm, Pk ' + Math.round(pk*100) + '%)');
            }
          } else {
            // Aircraft: distance-based kill at proxy-fuze range
            if(actualMissM < fuzeDetectM * 0.6){
              killTarget.alive = false;
              retireTruthAssociationV27('AIR',killTarget.id,'INTERCEPT_KILL');
            }
            m._deathReason = 'PROX_DETONATION_AIRCRAFT';
            m.dead = true;
            notify('요격! ' + displayTargetLabel + ' ← ' + _wpnL + ' ' + _mId + ' (' + Math.round(actualMissM) + 'm)');
          }
          return;
        } else {
          // Fuze detection zone missed — missile continues as coast/wasted
          m.missedTarget = true;
          m._missTime = m.life;
          notify('빗나감: ' + _mId + ' (miss ' + Math.round(actualMissM) + 'm)');
        }
      }

      // Coast timeout (legacy fallback)
      if(m.afterClosestTimer > 2.0 && (m.proxMissDistKm ?? 999) > 0.060){
        m.coastHold = true;
      }
    }
  }
function wip173RecordInterceptBurst(){}
let SIM_RNG_STATE=1831565813;
let WIP87_PENDING_PK=DATA["WIP87_PENDING_PK"];
const SIM_TEST_WIP87_PK_TRACE=[];
function applyInterceptResult(pk, em, weaponLabel, engagementTrackId=null){
    if(simRandom() < pk){
      // KILL
      wip11cQueueAsmRetirement(em,'INTERCEPT_KILL',{weaponLabel,result:'KILL',trackId:engagementTrackId});
      em.alive = false;
      em._outcomeRecorded = true;
      retireTruthAssociationV27('ASM',em.id,'INTERCEPT_KILL');
      return 'KILL';
    } else if(pk > 0.1 && simRandom() < pk * 0.7){
      // DAMAGE: fragments hit but didn't destroy
      // Apply structural damage → may cause later failure
      em._structDmg = (em._structDmg ?? 0) + rand(15, 40);
      if(em._structDmg > (ASM_PROFILES[em.label]?.structuralHP ?? 80)){
        // Cumulative damage → structural failure
        wip11cQueueAsmRetirement(em,'INTERCEPT_STRUCTURAL_FAILURE',{weaponLabel,result:'STRUCT_FAIL',trackId:engagementTrackId});
        em.alive = false;
        retireTruthAssociationV27('ASM',em.id,'STRUCTURAL_FAILURE');
        return 'STRUCT_FAIL';
      }
      // Damaged: degrade guidance
      wip11cRememberEngagementTrack(em,engagementTrackId,`${weaponLabel}_DAMAGE`);
      em._guidanceDegraded = true;
      return 'DAMAGED';
    }
    return 'MISS';
  }
function wip11cRememberEngagementTrack(em,trackId,source='FRIENDLY_WEAPON'){
    if(!em||trackId==null)return null;const id=Number(trackId);if(!Number.isFinite(id))return null;
    const row={trackId:id,source:String(source),step:simStepCounter};
    Object.defineProperty(em,'_wip11cEngagementTrack',{value:row,writable:true,configurable:true,enumerable:false});return row;
  }
function computeInterceptPk(missDistM, weaponType, targetLabel, closingSpeedMps, kinematics=null){
    const prof = ASM_PROFILES[targetLabel] ?? ASM_PROFILES['Kh-35U'];
    const targetArea = prof.length * prof.diameter;
    let pk=0,detail=null;
    if(weaponType==='SM2'||weaponType==='ESSM'||weaponType==='RAM'){
      const kin=kinematics??{missileSpeedMps:Math.max(0,Number(closingSpeedMps)||0),targetSpeedMps:0,relativeSpeedMps:Math.max(0,Number(closingSpeedMps)||0),encounterAngleRad:0};
      detail=_wip88FragmentationPk(missDistM,weaponType,targetLabel,kin);pk=detail.pk;
    }else if(weaponType==='GUN'){
      // Legacy compatibility only after WIP50. Live Phalanx impact gating uses swept physical projectile/capsule intersection.
      const vuln=prof.vulnerability,bodyHalf=(prof.length+prof.diameter)*0.3,effectiveMiss=Math.max(0,missDistM-bodyHalf),hitR=8;
      if(effectiveMiss<1)pk=0.80*vuln;else if(effectiveMiss<3)pk=lerp(0.80,0.45,(effectiveMiss-1)/2)*vuln;else if(effectiveMiss<hitR)pk=0.45*clamp((hitR-effectiveMiss)/hitR,0,1)*vuln;
      if(closingSpeedMps>600)pk*=clamp(700/closingSpeedMps,0.4,1.0);pk*=clamp(targetArea/3.0,0.7,1.4);
    }else{
      const vuln=prof.vulnerability,lethalR=10;if(missDistM<lethalR)pk=0.5*clamp((lethalR-missDistM)/lethalR,0,1)*vuln;
    }
    const finalPk=clamp(pk,0,0.9995);WIP88_LAST_PK_DETAIL=detail?{...detail,pk:finalPk}:null;
    if(WIP87_CASE_META){
      WIP87_PENDING_PK={caseMeta:{...WIP87_CASE_META},proxContext:WIP87_PROX_CONTEXT?{...WIP87_PROX_CONTEXT}:null,missDistM:_wip87Finite(missDistM),weaponType,targetLabel,closingSpeedMps:_wip87Finite(closingSpeedMps),profile:_wip87ProfileSnapshot(targetLabel),targetArea:_wip87Finite(targetArea),calculatedPk:_wip87Finite(finalPk),fragmentPhysics:WIP88_LAST_PK_DETAIL?{...WIP88_LAST_PK_DETAIL}:null,rngStateBeforeApply:SIM_RNG_STATE>>>0};
    }
    return finalPk;
  }
function _wip87ProfileSnapshot(label){
    const p=ASM_PROFILES[label] ?? ASM_PROFILES['Kh-35U'];
    return {vulnerability:_wip87Finite(p.vulnerability),length:_wip87Finite(p.length),diameter:_wip87Finite(p.diameter),structuralHP:_wip87Finite(p.structuralHP)};
  }
function _wip87Finite(v){ return Number.isFinite(v) ? v : null; }
let WIP87_PROX_CONTEXT=DATA["WIP87_PROX_CONTEXT"];
let WIP87_CASE_META=DATA["WIP87_CASE_META"];
let WIP88_LAST_PK_DETAIL=DATA["WIP88_LAST_PK_DETAIL"];
function _wip99FragmentSpeedMps(weaponType){
    const w=INTERCEPT_FRAGMENT_WARHEADS[weaponType];
    return w?_wip88GurneyFragmentSpeed(w):0;
  }
function _wip99FragmentArrivalGeometry(relXm,relYm,relZm,relVxMps,relVyMps,relVzMps,burstOffsetS,fragmentFlightTimeS){
    const t=Math.max(0,Number(burstOffsetS)||0)+Math.max(0,Number(fragmentFlightTimeS)||0);
    const x=relXm+relVxMps*t,y=relYm+relVyMps*t,z=relZm+relVzMps*t;
    return {timeFromFrameS:t,xM:x,yM:y,zM:z,missM:Math.hypot(x,y,z)};
  }
function trackDisplayLabelOr(){return "ENV_TARGET";}
function _wip144EssmFieldEfficiencyForEvent(interceptor,target){return _wip144FieldEfficiencyFromU(_wip144EventUniform(interceptor,target));}
function _wip144EventUniform(interceptor,target){
    const mid=(Number(interceptor?.id)||1)>>>0,tid=(Number(target?.id)||1)>>>0;
    let state=_mix32((SIM_SEED_BASE>>>0)^Math.imul(mid,0x7f4a7c15)^Math.imul(tid,0x6d2b79f5)^0x144f1e1d)||1;
    state=_xorshift32(state);return (state>>>0)/4294967296;
  }
function _wip144FieldEfficiencyFromU(u){
    const m=_wip144EssmFieldModel();if(!m?.enabled)return 1;
    return clamp(_wip144TriangularFromU(u,m.min,m.mode,m.max),m.min,m.max);
  }
function _wip144TriangularFromU(u,min,mode,max){
    const a=Number(min),c=Number(mode),b=Number(max),x=clamp(Number(u)||0,0,1),fc=(c-a)/Math.max(1e-12,b-a);
    if(x<fc)return a+Math.sqrt(x*(b-a)*(c-a));
    return b-Math.sqrt((1-x)*(b-a)*(b-c));
  }
function _wip144EssmFieldModel(){return INTERCEPT_FRAGMENT_WARHEADS.ESSM?.fragmentFieldEfficiencyModel??null;}
function _wip99Stage2CandidateDecision(m,target,relXm,relYm,relZm,dotPV,rcsOverrideM2=null){
    if(!_wip99Stage2AnyEnabled(m))return {allow:true,reason:null};
    const beam=_wip99TddBeamInfo(m,relXm,relYm,relZm);
    if(_wip143FuzeParamsForMissile(m).tddBeam.enabled&&!beam.covered)return {allow:false,reason:'beam-out',beam,detection:null};
    const detection=_wip99FuzeDetectionInfo(m,target,relXm,relYm,relZm,dotPV,rcsOverrideM2);
    if(_wip143FuzeParamsForMissile(m).detectionReliability.enabled&&!detection.detected)return {allow:false,reason:'detection-failed',beam,detection};
    return {allow:true,reason:null,beam,detection};
  }
function _wip99FuzeDetectionInfo(m,target,relXm,relYm,relZm,dotPV,rcsOverrideM2=null){
    const p=_wip143FuzeParamsForMissile(m),cfg=p.detectionReliability;
    if(!cfg.enabled)return {detected:true,pd:1,draw:null,rcsM2:null,opticalAreaM2:null,closingMps:null};
    const r=Math.max(1,Math.hypot(relXm,relYm,relZm));
    const closingMps=Math.max(0,-dotPV/r);
    let returnMetric={},signalQ=1;
    if(p.sensorDomain==='ACTIVE_OPTICAL'){
      const opticalAreaM2=_wip149OpticalTargetProxyAreaM2(target,m),ref=Math.max(.01,Number(cfg.opticalAreaRefM2)||.5);
      signalQ=clamp(Math.pow(Math.max(.005,opticalAreaM2)/ref,Number(cfg.areaExponent)||.06),.86,1.08);returnMetric={opticalAreaM2,opticalAreaQ:signalQ};
    }else{
      const rcsM2=Number.isFinite(rcsOverrideM2)?Math.max(0,rcsOverrideM2):(target?.label!=null?getASMRcs(target,m.x,m.y,m.z):targetRcsM2(target,m.x,m.y)),ref=Math.max(.005,Number(cfg.rcsRefM2)||.30);
      signalQ=clamp(Math.pow(Math.max(.005,rcsM2)/ref,Number(cfg.rcsExponent)||.12),.82,1.08);returnMetric={rcsM2,rcsQ:signalQ};
    }
    const closureQ=clamp(cfg.closureFloor+(1-cfg.closureFloor)*(closingMps/Math.max(1,cfg.closureRefMps)),cfg.closureFloor,1);
    let pd=clamp(cfg.basePd*signalQ*closureQ,cfg.minPd,cfg.maxPd),rangePd01=0;
    if(cfg.rangeAware){
      const detectM=Math.max(1,_wip143FuzeDetectRadiusM(m)),fullR=detectM*clamp(Number(cfg.fullPdRadiusFraction)||.55,.20,.95);
      rangePd01=smoothstep(clamp((detectM-r)/Math.max(1,detectM-fullR),0,1));
      pd=lerp(pd,Math.max(pd,Number(cfg.maxPd)||.999),rangePd01);
    }
    const draw=_wip99FuzeDetectionDraw(m);
    return {detected:draw<=pd,pd,draw,closingMps,closureQ,rangePd01,sensorDomain:p.sensorDomain??'RF_TDD',...returnMetric};
  }
function _wip99FuzeDetectionDraw(m){
    if(!Number.isFinite(m?._wip99FuzeDetectionDraw)){
      const mid=(Number(m?.id)||1)>>>0,st=_mix32((SIM_SEED_BASE>>>0)^Math.imul(mid,0x51f15e5d)^0xd37ec7a1)||1;
      m._wip99FuzeDetectionDraw=(st>>>0)/4294967296;
    }
    return m._wip99FuzeDetectionDraw;
  }
function smoothstep(t){ t = clamp(t,0,1); return t*t*(3-2*t); }
function _wip143FuzeDetectRadiusM(m){
    if(m?.isESSM) return Math.max(1,Number(ESSM_BLOCK2_TDD_SIM.detectionRadiusM)||60);
    if(m?.isRAM) return Math.max(1,Number(RAM_BLK1A_AOTD_SIM.sensingRadiusM)||20);
    if(m?._v1Profile?.id==='SM6_BLKIA_SIM')return Math.max(1,Number(SM6_BLOCK_IA_TDD_SIM.detectionRadiusM)||80);
    if(m?._v1Profile?.id==='SM2ER_BLKIV_SIM')return Math.max(1,Number(SM2ER_BLOCK_IV_MK45_MOD10_TDD_SIM.detectionRadiusM)||80);
    if(m?._v1Profile?.id==='SM2MR_BLKIIIA_SIM')return Math.max(1,Number(SM2MR_BLOCK_IIIA_MK45_MOD9_TDD_SIM.detectionRadiusM)||80);
    return (m?.guidanceCore === 'v1' && m?._v1Profile) ? Number(m._v1Profile.fuzeDetectRadiusM)||45 : 45;
  }
const SM2MR_BLOCK_IIIA_MK45_MOD9_TDD_SIM=DATA["SM2MR_BLOCK_IIIA_MK45_MOD9_TDD_SIM"];
const SM2ER_BLOCK_IV_MK45_MOD10_TDD_SIM=DATA["SM2ER_BLOCK_IV_MK45_MOD10_TDD_SIM"];
const SM6_BLOCK_IA_TDD_SIM=DATA["SM6_BLOCK_IA_TDD_SIM"];
const RAM_BLK1A_AOTD_SIM=DATA["RAM_BLK1A_AOTD_SIM"];
const ESSM_BLOCK2_TDD_SIM=DATA["ESSM_BLOCK2_TDD_SIM"];
function targetRcsM2(t, obsX, obsY){
    const toObsAng = Math.atan2(obsY - t.y, obsX - t.x);
    const aspect = Math.abs(angNorm(toObsAng - t.heading)); // 0..π
    const a01 = aspect / Math.PI; // 0=tail..0.5=beam..1=head-on
    let rcs;
    if(a01 < 0.5){
      rcs = 1.5 + (10.0 - 1.5) * (a01 * 2.0); // tail→beam: 1.5→10
    } else {
      rcs = 10.0 + (0.5 - 10.0) * ((a01 - 0.5) * 2.0); // beam→head: 10→0.5
    }
    return Math.max(0.1, rcs);
  }
function getASMRcs(em, obsX, obsY, obsZ){
    const prof = ASM_PROFILES[em.label] ?? ASM_PROFILES['Kh-35U'];
    const toObs = Math.atan2(obsY - em.y, obsX - em.x);
    const aspect = Math.abs(angNorm(toObs - em.heading)); // 0=head, PI=tail
    const a01 = aspect / Math.PI;

    // Elevation angle (for top-down view)
    const dH = worldToMeters(dist(obsX, obsY, em.x, em.y));
    const dZ = (obsZ ?? 0) - (em.z ?? 0);
    const elev = Math.abs(Math.atan2(dZ, Math.max(1, dH)));
    const topFac = clamp(elev / (Math.PI * 0.4), 0, 1); // 0=horizontal, 1=top-down

    // Interpolate RCS: head → side → tail (continuous)
    let rcs;
    if(a01 < 0.5){
      rcs = lerp(prof.rcsHead, prof.rcsSide, a01 * 2); // head→side
    } else {
      rcs = lerp(prof.rcsSide, prof.rcsTail, (a01 - 0.5) * 2); // side→tail
    }
    // Blend with top RCS based on elevation
    rcs = lerp(rcs, prof.rcsTop, topFac);
    return Math.max(0.01, rcs);
  }
function _wip149OpticalTargetProxyAreaM2(target,m){
    const p=ASM_PROFILES[target?.label]??ASM_PROFILES['Kh-35U'],L=Math.max(.1,Number(p.length)||4.45),D=Math.max(.05,Number(p.diameter)||.42);
    const toObs=Math.atan2((m?.y??0)-(target?.y??0),(m?.x??0)-(target?.x??0)),hdg=Number(target?.heading)||0,aspect=Math.abs(Math.sin(angNorm(toObs-hdg)));
    const headArea=Math.PI*Math.pow(D*.5,2),sideArea=L*D;return lerp(headArea,sideArea,aspect);
  }
function _wip143FuzeParamsForMissile(m){
    if(m?.isESSM)return ESSM_BLOCK2_TDD_SIM;
    if(m?.isRAM)return RAM_BLK1A_AOTD_SIM;
    if(m?._v1Profile?.id==='SM6_BLKIA_SIM')return SM6_BLOCK_IA_TDD_SIM;
    if(m?._v1Profile?.id==='SM2ER_BLKIV_SIM')return SM2ER_BLOCK_IV_MK45_MOD10_TDD_SIM;
    if(m?._v1Profile?.id==='SM2MR_BLKIIIA_SIM')return SM2MR_BLOCK_IIIA_MK45_MOD9_TDD_SIM;
    return WIP99_FUZE_STAGE2_PARAMS;
  }
const WIP99_FUZE_STAGE2_PARAMS=DATA["WIP99_FUZE_STAGE2_PARAMS"];
function _wip99TddBeamInfo(m,relXm,relYm,relZm){
    const cfg=_wip143FuzeParamsForMissile(m).tddBeam;
    if(!cfg.enabled)return {covered:true,polarDeg:null,centerDeg:cfg.polarCenterDeg,halfAngleDeg:cfg.halfAngleDeg};
    // rel = missile - target, therefore target-from-missile is -rel.
    const tx=-relXm,ty=-relYm,tz=-relZm,r=Math.hypot(tx,ty,tz);
    if(r<1e-6)return {covered:true,polarDeg:0,centerDeg:cfg.polarCenterDeg,halfAngleDeg:cfg.halfAngleDeg};
    const f=_wip99FuzeBodyForward(m),c=clamp((f.x*tx+f.y*ty+f.z*tz)/r,-1,1),polarDeg=rad2deg(Math.acos(c));
    const lo=Math.max(0,cfg.polarCenterDeg-cfg.halfAngleDeg),hi=Math.min(180,cfg.polarCenterDeg+cfg.halfAngleDeg);
    return {covered:polarDeg>=lo&&polarDeg<=hi,polarDeg,centerDeg:cfg.polarCenterDeg,halfAngleDeg:cfg.halfAngleDeg,loDeg:lo,hiDeg:hi};
  }
function _wip99FuzeBodyForward(m){
    const h=Number.isFinite(m?.heading)?m.heading:(Number.isFinite(m?.velAngle)?m.velAngle:0);
    const p=Number.isFinite(m?.pitch)?m.pitch:(Number.isFinite(m?.velPitch)?m.velPitch:0);
    const cp=Math.cos(p);return {x:cp*Math.cos(h),y:cp*Math.sin(h),z:Math.sin(p)};
  }
function _wip99Stage2AnyEnabled(m){
    const p=_wip143FuzeParamsForMissile(m);
    return !!(p.tddBeam.enabled||p.detectionReliability.enabled||p.processingDelay.enabled||p.seaClutter.enabled);
  }
const seaStateFactor=1.0649859543133355;
const WIP143_TDD_EVENT_TRACE=[];
function _wip99SeaClutterFalseTrigger(m,target,dt,rangeM=Infinity){
    const rate=_wip99SeaClutterRatePerSec(m,target,rangeM);if(!(rate>0))return {trigger:false,ratePerSec:0,p:0,draw:null};
    const p=probabilityFromRatePerSec(rate,dt),draw=_wip99FuzeClutterRandom(m);
    return {trigger:draw<p,ratePerSec:rate,p,draw,seaStateFactor,missileAltM:m.z??0,targetAltM:target?.z??0};
  }
function _wip99FuzeClutterRandom(m){
    if(!Number.isFinite(m?._wip99FuzeClutterState))m._wip99FuzeClutterState=_mix32((SIM_SEED_BASE>>>0)^Math.imul(((Number(m?.id)||1)>>>0),0x3f4a9b17)^0xc17a55e1)||1;
    m._wip99FuzeClutterState=_xorshift32(m._wip99FuzeClutterState>>>0);
    return (m._wip99FuzeClutterState>>>0)/4294967296;
  }
function probabilityFromRatePerSec(ratePerSec, dt){
    if(!(ratePerSec > 0) || !(dt > 0)) return 0;
    return clamp(1 - Math.exp(-ratePerSec * dt), 0, 1);
  }
function _wip99SeaClutterRatePerSec(m,target,rangeM=Infinity){
    const cfg=_wip143FuzeParamsForMissile(m).seaClutter;
    if(!cfg.enabled||!m?.proxArmed)return 0;
    if(Number.isFinite(cfg.activeRangeMultiplier)){const gateM=_wip143FuzeDetectRadiusM(m)*Math.max(1,Number(cfg.activeRangeMultiplier)||1);if(!(rangeM<=gateM))return 0;}
    const mz=Math.max(0,Number(m.z)||0),tz=Math.max(0,Number(target?.z)||0);
    if(tz>cfg.targetMaxAltM||mz>cfg.missileMaxAltM)return 0;
    const altQ=clamp((cfg.missileMaxAltM-mz)/Math.max(1,cfg.missileMaxAltM-cfg.fullEffectAltM),0,1);
    const seaQ=clamp((seaStateFactor-cfg.seaStateMin)/Math.max(.01,cfg.seaStateMax-cfg.seaStateMin),0,1);
    return cfg.falseTriggerRatePerSec*altQ*(.45+.55*seaQ);
  }
function _wip99FragmentLeadTimeS(expectedMissM,weaponType){
    const vf=_wip99FragmentSpeedMps(weaponType);
    if(!(vf>1)||!Number.isFinite(expectedMissM))return 0;
    return clamp(Math.max(0,expectedMissM)/vf,0,WIP99_FUZE_FRAGMENT_LEAD_MAX_S);
  }
const WIP99_FUZE_FRAGMENT_LEAD_MAX_S=DATA["WIP99_FUZE_FRAGMENT_LEAD_MAX_S"];
function _wip75NearestGuidanceSample(m,targetTS){
      const buf=m?._wip75RecentGuidance;
      if(!buf?.length || !Number.isFinite(targetTS)) return null;
      let best=buf[0],bestDt=Math.abs(buf[0].tS-targetTS);
      for(let i=1;i<buf.length;i++){
        const d=Math.abs(buf[i].tS-targetTS);
        if(d<bestDt){best=buf[i];bestDt=d;}
      }
      return best;
    }
function _wip75RecordGuidanceSample(){}
const ACTIVE_SHIP_RUNTIME=PRIVATE_SHIP;
function navalFuzeTargetD(){return null;}
function physicalShipsB(){return [];}
function surfaceMissileSweptContactWip13C5(){throw Error("ENV_AIR_ONLY_BOUNDARY");}
function updateSamSixDofLiteDynamics(m,dt,omegaYawCmd,omegaPitCmd,env){
    const p=m._samSixDof||_samSixDofProfileFor(m); if(!p)return false;
    const mass=Math.max(1,env.massKg),q=Math.max(0,env.qPa),rho=Math.max(0,env.rhoKgM3),mach=Math.max(0,env.mach);
    const Aref=Math.max(1e-4,env.Aref),Slift=Math.max(1e-4,env.Slift),length=Math.max(.5,m._v1Profile?.lengthM??4);
    const thrustN=Math.max(0,env.thrustN??0),cdBase=Math.max(.02,env.cdBase??0.5);
    let vx=worldSpeedToMps(m.vx??0),vy=worldSpeedToMps(m.vy??0),vz=m.vz??0;
    let speed=Math.max(1,Math.hypot(vx,vy,vz));
    let velA=Math.atan2(vy,vx),velP=Math.atan2(vz,Math.hypot(vx,vy));
    m.velAngle=velA;m.velPitch=velP;m.speed=mpsToWorldSpeed(speed);
    const wip14a8ZeroAoa=!!m._wip14a8ZeroAoaDiagnostic;
    if(wip14a8ZeroAoa){omegaYawCmd=0;omegaPitCmd=0;m.heading=velA;m.pitch=velP;m.roll=0;m.yawRate=0;m.pitchRate=0;m.rollRate=0;}
    const wip14a8Vx0=vx,wip14a8Vy0=vy,wip14a8Vz0=vz,wip14a8Speed0=speed,wip14a8Alt0=Number(m.z)||0;

    const prop0=Math.max(1e-6,m._propulsionInitialKg??1),propNow=Math.max(0,(m.boosterPropKg??0)+(m.sustainerPropKg??0));
    const propFrac=clamp(propNow/prop0,0,1);
    let Iy=lerp(p.iyDryKgM2,p.iyKgM2,propFrac),Iz=lerp(p.izDryKgM2,p.izKgM2,propFrac),Ix=lerp(p.ixDryKgM2,p.ixKgM2,propFrac);
    if(m.isSM2ER||m.isSM6){
      const stageC=m.isSM6?WIP14A6_SM6_STAGE_CONTRACT:WIP14A5_SM2ER_STAGE_CONTRACT;
      if(!m.boosterSeparated){const f=clamp((m.boosterPropKg??0)/Math.max(1e-9,stageC.boosterPropKg),0,1);Iy=lerp(p.iyAttachedBurnoutKgM2,p.iyKgM2,f);Iz=lerp(p.izAttachedBurnoutKgM2,p.izKgM2,f);Ix=lerp(p.ixAttachedBurnoutKgM2,p.ixKgM2,f);}
      else{const f=clamp((m.sustainerPropKg??0)/Math.max(1e-9,stageC.upperPropKg),0,1);Iy=lerp(p.iyDryKgM2,p.iyUpperLoadedKgM2,f);Iz=lerp(p.izDryKgM2,p.izUpperLoadedKgM2,f);Ix=lerp(p.ixDryKgM2,p.ixUpperLoadedKgM2,f);}
    }
    if(m.isESSM&&m._wip136TvcJettisoned){
      const jm=Math.max(0,Number(m._wip136TvcJettisonMassKg)||0),arm=Math.max(.2,Number(m._wip136TvcInertiaArmM)||1.50);
      Iy=Math.max(20,Iy-jm*arm*arm);Iz=Math.max(20,Iz-jm*arm*arm);Ix=Math.max(.2,Ix-jm*.13*.13);
    }
    m.sam6dofIx=Ix;m.sam6dofIy=Iy;m.sam6dofIz=Iz;

    const q01=clamp((q-(p.gQminPa??5000))/Math.max(1,(p.gQmaxPa??70000)-(p.gQminPa??5000)),0,1);
    const wip136Bypass=!!(window.WIP136_ESSM_G_CAP_BYPASS&&p.id==='ESSM_BLK2_6DOF_LITE');
    const qSmooth=q01*q01*(3-2*q01),gl=wip138EssmGLimits(p),gHard=wip136Bypass?250:gl.structuralG,gOptimal=wip136Bypass?250:gl.optimalG,gQ=lerp(p.gMinQ??1.2,gOptimal,qSmooth);
    const aoaBase=deg(p.maxAoaDeg??28),aoaQSoft=lerp(1.0,.72,_samSmooth01((q-65000)/90000)),aoaMachSoft=lerp(1.0,.82,_samSmooth01((mach-3.8)/1.4));
    const aoaMax=clamp(aoaBase*aoaQSoft*aoaMachSoft,deg(6),aoaBase);m.aoaMaxDyn=aoaMax;
    const term=_samSixDofTermAuthority(m,p);
    const launchPhase=!!(m.vlsPhase||m.pitchoverPhase);
    // WIP56: launch turnover is not cruise-midcourse.  A distant target used to force the VLS
    // turnover through the low-bandwidth midcourse CN/moment limits, leaving SM-2 nearly vertical
    // for tens of seconds.  Keep the planner's urgent/normal/long aggressiveness, but provide a
    // separate physical authority floor while the launcher transition owns attitude.
    const launchAuthority=launchPhase?clamp(p.launchAeroAuthority??0,0,1):0;
    // WIP73: range/terminal phase is guidance policy, not physical fin geometry.
    // SM-2 keeps its real post-launch actuator/CN authority at any range; energy management belongs
    // to the guidance G-command envelope.  ESSM retains its validated phase schedule.
    const sm2PhysicalAuthority=((p.id==='SM2MR_BLKIIIA_6DOF_LITE'||p.id==='SM2ER_BLKIV_6DOF_LITE'||p.id==='SM6_BLKIA_6DOF_LITE')&&!launchPhase);
    const controlAuthority=sm2PhysicalAuthority?1:Math.max(term,launchAuthority);
    const launchAgg=launchPhase?clamp(m._samTrajPlan?.controlAggressiveness??1,0.25,1):1;
    const finMax=deg(lerp(p.finMaxMidDeg,p.finMaxTermDeg,controlAuthority))*lerp(0.55,1.0,launchAgg);
    const finRate=deg(lerp(p.finRateMidDegS,p.finRateTermDegS,controlAuthority))*lerp(0.65,1.0,launchAgg);
    const finTau=lerp(p.finCmdTauMidS,p.finCmdTauTermS,controlAuthority)/lerp(0.75,1.0,launchAgg);
    const bodyK=.34,finK=.90;
    const cnBody=Math.max(0,p.cnAlpha*aoaMax)*bodyK;
    const cnFin=Math.max(0,p.cnDelta*finMax*(p.finAreaM2/Slift))*finK;
    let gAero=q>1e-6?q*Slift*(cnBody+cnFin)/(mass*G0):1;
    gAero=clamp(gAero,1,gHard);

    // WIP49 acceleration-feedback fin autopilot.
    // Feed-forward still maps requested flight-path normal acceleration into fin deflection, but the
    // previous frame's *actual normal-acceleration vector* closes the inner loop.  Do NOT use body-rate
    // error here: body rotation and flight-path rotation diverge whenever AoA/beta is non-zero.
    const aYawReq=omegaYawCmd*speed,aPitReq=omegaPitCmd*speed;
    const aAeroAvail=Math.max(G0,gAero*G0);
    const yawUx=-Math.sin(velA),yawUy=Math.cos(velA),yawUz=0;
    const pitUx=-Math.sin(velP)*Math.cos(velA),pitUy=-Math.sin(velP)*Math.sin(velA),pitUz=Math.cos(velP);
    const prevN=m._samPrevNormalAccWorld??{x:0,y:0,z:0};
    const aYawDeliveredRaw=prevN.x*yawUx+prevN.y*yawUy+prevN.z*yawUz;
    const aPitDeliveredRaw=prevN.x*pitUx+prevN.y*pitUy+prevN.z*pitUz;
    const fbTau=Math.max(.015,p.finAccelFeedbackTauS??.05),fbK=1-Math.exp(-dt/fbTau);
    m._samFinAccelYawFilt=lerp(m._samFinAccelYawFilt??aYawDeliveredRaw,aYawDeliveredRaw,fbK);
    m._samFinAccelPitFilt=lerp(m._samFinAccelPitFilt??aPitDeliveredRaw,aPitDeliveredRaw,fbK);

    const ffScale=lerp(p.finFeedForwardScaleMid??1,p.finFeedForwardScaleTerm??1,term);
    const kp=lerp(p.finAccelKpMid??0,p.finAccelKpTerm??0,term);
    const ki=lerp(p.finAccelKiMid??0,p.finAccelKiTerm??0,term);
    const intLim=Math.max(0,p.finAccelIntLimit??.30);
    const feedbackQMin=p.finAccelFeedbackQMinPa??6000;
    const controlDemandG=m._v1GAchieved??0;
    const srcAge=m._v1SourceArb?.sourceAgeS??999;
    const accelLoopActive=q>=feedbackQMin&&!m.vlsPhase&&!m.pitchoverPhase&&controlDemandG>=.5&&srcAge>=.05;
    if((m._samFinAccelPrevYawReq??0)*aYawReq<0)m._samFinAccelIntYaw=0;
    if((m._samFinAccelPrevPitReq??0)*aPitReq<0)m._samFinAccelIntPit=0;
    m._samFinAccelPrevYawReq=aYawReq;m._samFinAccelPrevPitReq=aPitReq;

    const yawErrNorm=(aYawReq-(m._samFinAccelYawFilt??0))/aAeroAvail;
    const pitErrNorm=(aPitReq-(m._samFinAccelPitFilt??0))/aAeroAvail;
    let iYaw=m._samFinAccelIntYaw??0,iPit=m._samFinAccelIntPit??0;
    const ffYaw=clamp(ffScale*aYawReq/aAeroAvail,-1,1),ffPit=clamp(ffScale*aPitReq/aAeroAvail,-1,1);
    if(accelLoopActive){
      // Conditional integration / anti-windup: only accumulate error if the tentative command is not
      // saturated, or if the error would drive an already saturated command back toward the linear range.
      const preYaw=ffYaw+kp*yawErrNorm+iYaw,prePit=ffPit+kp*pitErrNorm+iPit;
      const canIYaw=Math.abs(preYaw)<1||Math.sign(yawErrNorm)!==Math.sign(preYaw);
      const canIPit=Math.abs(prePit)<1||Math.sign(pitErrNorm)!==Math.sign(prePit);
      if(canIYaw)iYaw=clamp(iYaw+ki*yawErrNorm*dt,-intLim,intLim); else iYaw*=Math.exp(-dt/.18);
      if(canIPit)iPit=clamp(iPit+ki*pitErrNorm*dt,-intLim,intLim); else iPit*=Math.exp(-dt/.18);
    }else{
      // No useful aerodynamic authority / launch phase: bleed integrators instead of winding them up.
      const bleed=Math.exp(-dt/.12);iYaw*=bleed;iPit*=bleed;
    }
    m._samFinAccelIntYaw=iYaw;m._samFinAccelIntPit=iPit;m._samFinAccelLoopActive=accelLoopActive;
    const yawNorm=clamp(ffYaw+(accelLoopActive?kp*yawErrNorm+iYaw:0),-1,1);
    const pitNorm=clamp(ffPit+(accelLoopActive?kp*pitErrNorm+iPit:0),-1,1);
    let finYawCmd=yawNorm*finMax;
    let finPitCmd=pitNorm*finMax;
    // WIP63 acceleration-loop body-rate damping. omega*Cmd is the requested flight-path turn rate;
    // pitch/yawRate are body angular rates. A tail-controlled missile can otherwise rotate its body
    // much faster than the velocity vector, saturating AoA and wasting terminal energy. This term
    // damps only the actuator command; it does NOT reduce the guidance acceleration request or available G.
    const bodyRateDampGain=Math.max(0,p.finBodyRateDampGain??0);
    if(bodyRateDampGain>0&&!m.vlsPhase&&!m.pitchoverPhase&&q>=feedbackQMin){
      const rateRef=deg(Math.max(20,p.finBodyRateRefDegS??120));
      const pitRateErr=(m.pitchRate??0)-omegaPitCmd;
      const yawRateErr=(m.yawRate??0)-omegaYawCmd;
      const pitDamp=-bodyRateDampGain*clamp(pitRateErr/rateRef,-1,1);
      const yawDamp=-bodyRateDampGain*clamp(yawRateErr/rateRef,-1,1);
      finPitCmd+=pitDamp*finMax; finYawCmd+=yawDamp*finMax;
      m._samBodyRateDampActive=Math.abs(pitDamp)>0.01||Math.abs(yawDamp)>0.01;
      m._samBodyRateDampPit=pitDamp;m._samBodyRateDampYaw=yawDamp;
    }else{m._samBodyRateDampActive=false;m._samBodyRateDampPit=0;m._samBodyRateDampYaw=0;}
    m._samFinYawCmdSm=lerp(m._samFinYawCmdSm??0,finYawCmd,1-Math.exp(-dt/Math.max(.02,finTau)));
    m._samFinPitCmdSm=lerp(m._samFinPitCmdSm??0,finPitCmd,1-Math.exp(-dt/Math.max(.02,finTau)));
    finYawCmd=clamp(m._samFinYawCmdSm,-finMax,finMax);finPitCmd=clamp(m._samFinPitCmdSm,-finMax,finMax);
    const finStep=finRate*dt;
    m.finYaw=clamp((m.finYaw??0)+clamp(finYawCmd-(m.finYaw??0),-finStep,finStep),-finMax,finMax);
    m.finPitch=clamp((m.finPitch??0)+clamp(finPitCmd-(m.finPitch??0),-finStep,finStep),-finMax,finMax);
    if(wip14a8ZeroAoa){finYawCmd=0;finPitCmd=0;m.finYaw=0;m.finPitch=0;m._samFinYawCmdSm=0;m._samFinPitCmdSm=0;}

    // TVC is a real force/moment source, not a G-limit bonus.
    let tvcAuth=0;
    const wip136TvcInstalled=m.isESSM?!m._wip136TvcJettisoned:true;
    if(!wip14a8ZeroAoa&&p.tvc&&m.tvcEnabled&&wip136TvcInstalled&&thrustN>0&&(m.life??0)<(m.isESSM?(window.WIP136_ESSM_TVC_TIMEOUT_S??4.0):(p.tvcDurationS??3.3))){
      const qFade=1-_samSmooth01((q-(p.tvcQFadeStartPa??18000))/Math.max(1,(p.tvcQFadeEndPa??52000)-(p.tvcQFadeStartPa??18000)));
      const launchOwned=!!(m.vlsPhase||m.pitchoverPhase);
      tvcAuth=launchOwned?clamp(Math.max(.95,qFade),0,1):0;
      const maxTvc=deg(p.tvcMaxDeg??22)*lerp(0.60,1.0,launchAgg),gain=p.tvcRateGainS??.15;
      if(m.vlsPhase||m.pitchoverPhase){
        // WIP44: preserve WIP40's physically successful position+rate TVC servo, but let the
        // 6DOF integrator produce the actual angular acceleration and velocity-vector response.
        const kp=m.vlsPhase?4.8:3.6,kd=m.vlsPhase?.13:.18;
        const yErr=angNorm((m._vlsDesiredBearing??m.heading??0)-(m.heading??0));
        const pErr=(m._vlsDesiredPitch??m.pitch??0)-(m.pitch??0);
        m.tvcCmdYaw=clamp(yErr*kp-(m.yawRate??0)*kd,-maxTvc,maxTvc)*tvcAuth;
        m.tvcCmdPitch=clamp(pErr*kp-(m.pitchRate??0)*kd,-maxTvc,maxTvc)*tvcAuth;
      }else{
        m.tvcCmdYaw=clamp((omegaYawCmd-(m.yawRate??0))*gain,-maxTvc,maxTvc)*tvcAuth;
        m.tvcCmdPitch=clamp((omegaPitCmd-(m.pitchRate??0))*gain,-maxTvc,maxTvc)*tvcAuth;
      }
      if(m.isSM2ER||m.isSM6){const cmdMag=Math.hypot(m.tvcCmdYaw??0,m.tvcCmdPitch??0);if(cmdMag>maxTvc&&cmdMag>1e-9){const k=maxTvc/cmdMag;m.tvcCmdYaw*=k;m.tvcCmdPitch*=k;}}
      const step=deg(p.tvcSlewDegS??360)*dt;
      m.tvcYaw=(m.tvcYaw??0)+clamp(m.tvcCmdYaw-(m.tvcYaw??0),-step,step);
      m.tvcPitch=(m.tvcPitch??0)+clamp(m.tvcCmdPitch-(m.tvcPitch??0),-step,step);
      if(m.isSM2ER||m.isSM6){const actualMag=Math.hypot(m.tvcYaw??0,m.tvcPitch??0);if(actualMag>maxTvc&&actualMag>1e-9){const k=maxTvc/actualMag;m.tvcYaw*=k;m.tvcPitch*=k;}}
    }else{
      const step=deg(p.tvcSlewDegS??360)*dt;
      m.tvcYaw=(m.tvcYaw??0)+clamp(-(m.tvcYaw??0),-step,step);m.tvcPitch=(m.tvcPitch??0)+clamp(-(m.tvcPitch??0),-step,step);
      m.tvcCmdYaw=0;m.tvcCmdPitch=0;
    }
    m.tvcAuthority=tvcAuth;
    const tvcMaxSide=thrustN*Math.sin(deg(p.tvcMaxDeg??0))*tvcAuth;
    const gTvc=tvcMaxSide/(mass*G0);
    // WIP49: availableG must reflect the force coefficient envelope actually used below.  The old
    // cnAlpha/fin-area estimate could advertise 2-4x more G than the CN/CY force clamp could deliver.
    const forceCap=_samSixDofAeroForceCap(p,q,Slift,mass,controlAuthority);
    const gAeroBound=Math.min(gQ,gAero,forceCap.gForceCap);
    m.gAvailQ=gQ;m.gAeroCtl=gAero;m.gAeroForceCap=forceCap.gForceCap;m.gAeroCnRaw=forceCap.cnLimRaw;m.gAeroCnOptimal=forceCap.cnOptimal;
    m.availableG=clamp(Math.min(gHard,gOptimal,gAeroBound+gTvc),Math.min(1,gOptimal),gOptimal);m.gLimitDyn=m.availableG;m._sam6dofAuthorityReady=true;

    // Angular dynamics: aerodynamic moment + TVC moment -> p/q/r.
    // WIP48 telemetry keeps raw geometric incidence separate from the coefficient-limited
    // effective alpha/beta used by the lite aero model. This exposes departure-like excursions
    // instead of hiding them behind the AoA clamp.
    const launchIncidence=!!(m.vlsPhase||m.pitchoverPhase);
    const inc3=launchIncidence?_samBodyIncidence3D(m,vx,vy,vz):null;
    const rawAlpha=inc3?inc3.alpha:((m.pitch??velP)-velP);
    const rawBeta=inc3?inc3.beta:angNorm((m.heading??velA)-velA);
    const alpha=clamp(rawAlpha,-aoaMax,aoaMax);
    const beta=clamp(rawBeta,-deg(p.maxBetaDeg??25),deg(p.maxBetaDeg??25));
    const vRef=Math.max(80,speed),qHat=(m.pitchRate??0)*length/(2*vRef),rHat=(m.yawRate??0)*length/(2*vRef),pHat=(m.rollRate??0)*length/(2*vRef);
    const momentScale=lerp(p.midcourseMomentScale??.6,p.terminalMomentScale??1,controlAuthority);
    const qMomentSoft=lerp(1,.55,_samSmooth01((q-(p.qMomentSoftPa??100000))/90000));
    const Cm=(p.cmAlpha*alpha+p.cmDelta*(m.finPitch??0)*momentScale+p.cmQ*qHat)*qMomentSoft;
    const Cn=(p.cnBeta*beta+p.cnDeltaMoment*(m.finYaw??0)*momentScale+p.cnR*rHat)*qMomentSoft;
    const Cl=(p.clP??-20)*pHat;
    let Mpit=q*Slift*length*Cm,Myaw=q*Slift*length*Cn,Mroll=q*Slift*length*Cl;
    if(tvcAuth>0&&thrustN>0){
      const arm=p.tvcMomentArmM??0;
      Myaw+=thrustN*Math.sin(m.tvcYaw??0)*arm;
      Mpit+=thrustN*Math.sin(m.tvcPitch??0)*arm;
    }
    m.pitchRate=(m.pitchRate??0)+(Mpit/Math.max(1,Iy))*dt;
    m.yawRate=(m.yawRate??0)+(Myaw/Math.max(1,Iz))*dt;
    m.rollRate=(m.rollRate??0)+(Mroll/Math.max(.1,Ix))*dt;
    const rateCap=deg(p.maxBodyRateDegS??300);
    m.pitchRate=clamp(m.pitchRate,-rateCap,rateCap);m.yawRate=clamp(m.yawRate,-rateCap,rateCap);m.rollRate=clamp(m.rollRate,-rateCap,rateCap);
    const pitchLimit=m.vlsPhase?deg(90):deg(89.5);
    m.pitch=clamp((m.pitch??velP)+m.pitchRate*dt,-pitchLimit,pitchLimit);
    m.heading=angNorm((m.heading??velA)+m.yawRate*dt);m.roll=angNorm((m.roll??0)+m.rollRate*dt);

    // Body bases including roll.
    const H=m.heading,P=m.pitch,R=m.roll,cH=Math.cos(H),sH=Math.sin(H),cP=Math.cos(P),sP=Math.sin(P),cR=Math.cos(R),sR=Math.sin(R);
    const bx=cP*cH,by=cP*sH,bz=sP;
    const r0x=-sH,r0y=cH,r0z=0,u0x=-sP*cH,u0y=-sP*sH,u0z=cP;
    const rx=r0x*cR+u0x*sR,ry=r0y*cR+u0y*sR,rz=r0z*cR+u0z*sR;
    const ux=-r0x*sR+u0x*cR,uy=-r0y*sR+u0y*cR,uz=-r0z*sR+u0z*cR;
    const vmag=Math.max(1,Math.hypot(vx,vy,vz)),ex=vx/vmag,ey=vy/vmag,ez=vz/vmag;
    const wip14a13AeroKernel=wip14a13ResolveAeroKernel(m);
    const wip14a10WindAxis=wip14a13AeroKernel.windAxis;
    const wip14a10Basis=wip14a10WindAxis?wip14a12ContinuousWindBasis(m,ex,ey,ez,ux,uy,uz,rx,ry,rz):null;

    // Actual aero forces from current alpha/beta + actuator positions.
    const qForceSoft=forceCap.qForceSoft;
    const cnLim=forceCap.cnLim;
    let CN=clamp(p.normalForceAlpha*alpha+p.normalForceDelta*(m.finPitch??0),-cnLim,cnLim);
    let CY=clamp(p.normalForceAlpha*beta+p.normalForceDelta*(m.finYaw??0),-cnLim,cnLim);
    // WIP58: CN/CY share one normal-force envelope.  Independent per-axis clamps allowed
    // diagonal commands to produce sqrt(2) times the advertised G capability.
    const cNorm=Math.hypot(CN,CY);if(cNorm>cnLim&&cNorm>1e-9){const sc=cnLim/cNorm;CN*=sc;CY*=sc;}
    const Fn=q*Slift*CN,Fs=q*Slift*CY;
    const finNorm=clamp(Math.hypot(m.finPitch??0,m.finYaw??0)/Math.max(1e-6,finMax),0,1);
    // WIP59: keep maneuver-drag reference areas dimensionally consistent.  CN/CY are defined on
    // Slift, so the quadratic maneuver term must also use Slift; a SIM_TUNED scale represents
    // missile body/tail efficiency instead of treating the airframe as a finite wing.
    const cdIndBase=(CN*CN+CY*CY)/(Math.PI*Math.max(.8,p.aspectRatio??m.aspectRatio??3.0)*Math.max(.5,p.oswaldEff??m.oswaldEff??.8));
    const maneuverDragScale=clamp(p.maneuverDragScale??.30,.05,1.0);
    const cdControl=(p.cdAlphaK??.07)*(alpha*alpha+beta*beta)+(p.cdDeltaK??.02)*finNorm*finNorm;
    const dragParasiteN=q*Aref*cdBase;
    const dragControlN=q*Aref*cdControl;
    const dragManeuverN=q*Slift*cdIndBase*maneuverDragScale;
    const dragN=dragParasiteN+dragControlN+dragManeuverN;

    // Gimballed thrust direction in body basis.
    let tx=bx,ty=by,tz=bz;
    if(tvcAuth>0){tx=bx+rx*Math.tan(m.tvcYaw??0)+ux*Math.tan(m.tvcPitch??0);ty=by+ry*Math.tan(m.tvcYaw??0)+uy*Math.tan(m.tvcPitch??0);tz=bz+rz*Math.tan(m.tvcYaw??0)+uz*Math.tan(m.tvcPitch??0);const tn=Math.max(1e-9,Math.hypot(tx,ty,tz));tx/=tn;ty/=tn;tz/=tn;}
    let axNoG,ayNoG,azNoG;
    if(wip14a10WindAxis){
      axNoG=(thrustN*tx-dragN*ex+Fs*wip14a10Basis.side.x+Fn*wip14a10Basis.lift.x)/mass;
      ayNoG=(thrustN*ty-dragN*ey+Fs*wip14a10Basis.side.y+Fn*wip14a10Basis.lift.y)/mass;
      azNoG=(thrustN*tz-dragN*ez+Fs*wip14a10Basis.side.z+Fn*wip14a10Basis.lift.z)/mass;
    }else{
      axNoG=(thrustN*tx-dragN*ex+Fs*rx+Fn*ux)/mass;
      ayNoG=(thrustN*ty-dragN*ey+Fs*ry+Fn*uy)/mass;
      azNoG=(thrustN*tz-dragN*ez+Fs*rz+Fn*uz)/mass;
    }
    const ax=axNoG,ay=ayNoG,az=azNoG-G0;
    vx+=ax*dt;vy+=ay*dt;vz+=az*dt;
    speed=Math.max(0,Math.hypot(vx,vy,vz));
    if(wip14a8IsStandardMissile(m)){
      const thrustAlongVelocityN=thrustN*(tx*ex+ty*ey+tz*ez),gravityAlongVelocityN=-mass*G0*ez;
      const liftForceAlongVelocityN=wip14a10WindAxis?Fn*(wip14a10Basis.lift.x*ex+wip14a10Basis.lift.y*ey+wip14a10Basis.lift.z*ez):Fn*(ux*ex+uy*ey+uz*ez);
      const sideForceAlongVelocityN=wip14a10WindAxis?Fs*(wip14a10Basis.side.x*ex+wip14a10Basis.side.y*ey+wip14a10Basis.side.z*ez):Fs*(rx*ex+ry*ey+rz*ez);
      const normalForceAlongVelocityN=liftForceAlongVelocityN+sideForceAlongVelocityN;
      const netAxialForceN=thrustAlongVelocityN-dragN+gravityAlongVelocityN,actualNetAlongVelocityN=netAxialForceN+normalForceAlongVelocityN;
      const fx=wip14a10WindAxis?(thrustN*tx-dragN*ex+Fs*wip14a10Basis.side.x+Fn*wip14a10Basis.lift.x):(thrustN*tx-dragN*ex+Fs*rx+Fn*ux),fy=wip14a10WindAxis?(thrustN*ty-dragN*ey+Fs*wip14a10Basis.side.y+Fn*wip14a10Basis.lift.y):(thrustN*ty-dragN*ey+Fs*ry+Fn*uy),fz=wip14a10WindAxis?(thrustN*tz-dragN*ez+Fs*wip14a10Basis.side.z+Fn*wip14a10Basis.lift.z-mass*G0):(thrustN*tz-dragN*ez+Fs*rz+Fn*uz-mass*G0);
      const vmx=.5*(wip14a8Vx0+vx),vmy=.5*(wip14a8Vy0+vy),vmz=.5*(wip14a8Vz0+vz);
      const thrustPowerW=thrustN*(tx*wip14a8Vx0+ty*wip14a8Vy0+tz*wip14a8Vz0),dragPowerW=-dragN*wip14a8Speed0,gravityPowerW=-mass*G0*wip14a8Vz0;
      const normalAeroPowerW=wip14a10WindAxis?(Fn*(wip14a10Basis.lift.x*wip14a8Vx0+wip14a10Basis.lift.y*wip14a8Vy0+wip14a10Basis.lift.z*wip14a8Vz0)+Fs*(wip14a10Basis.side.x*wip14a8Vx0+wip14a10Basis.side.y*wip14a8Vy0+wip14a10Basis.side.z*wip14a8Vz0)):(Fn*(ux*wip14a8Vx0+uy*wip14a8Vy0+uz*wip14a8Vz0)+Fs*(rx*wip14a8Vx0+ry*wip14a8Vy0+rz*wip14a8Vz0));
      const thrustPowerMidW=thrustN*(tx*vmx+ty*vmy+tz*vmz),dragPowerMidW=-dragN*(ex*vmx+ey*vmy+ez*vmz),gravityPowerMidW=-mass*G0*vmz;
      const normalAeroPowerMidW=wip14a10WindAxis?(Fn*(wip14a10Basis.lift.x*vmx+wip14a10Basis.lift.y*vmy+wip14a10Basis.lift.z*vmz)+Fs*(wip14a10Basis.side.x*vmx+wip14a10Basis.side.y*vmy+wip14a10Basis.side.z*vmz)):(Fn*(ux*vmx+uy*vmy+uz*vmz)+Fs*(rx*vmx+ry*vmy+rz*vmz));
      const altitudeAfterM=wip14a8Alt0+vz*dt,midpointConsistentAltitudeAfterM=wip14a8Alt0+vmz*dt;
      const kineticEnergyJ=.5*mass*wip14a8Speed0*wip14a8Speed0,kineticEnergyAfterJ=.5*mass*speed*speed,potentialEnergyJ=mass*G0*wip14a8Alt0,potentialEnergyAfterJ=mass*G0*altitudeAfterM;
      const kineticEnergyRateW=(kineticEnergyAfterJ-kineticEnergyJ)/dt,kineticPowerMidW=thrustPowerMidW+dragPowerMidW+normalAeroPowerMidW+gravityPowerMidW;
      const mechanicalEnergyRateActualW=(kineticEnergyAfterJ+potentialEnergyAfterJ-kineticEnergyJ-potentialEnergyJ)/dt;
      const mechanicalEnergyRateMidpointW=(kineticEnergyAfterJ+mass*G0*midpointConsistentAltitudeAfterM-kineticEnergyJ-potentialEnergyJ)/dt;
      const mechanicalSourcePowerMidW=thrustPowerMidW+dragPowerMidW+normalAeroPowerMidW;
      const bodyDot=clamp(bx*ex+by*ey+bz*ez,-1,1),soundMps=speedOfSoundMps(wip14a8Alt0),soundAfterMps=speedOfSoundMps(altitudeAfterM);
      const twoStage=!!(m.isSM2ER||m.isSM6),phase=wip14a8PropulsionPhase(m);
      const record={schema:WIP14A8_FORCE_TRACE_SCHEMA,timeS:Number(m.life)||0,dtS:dt,altitudeM:wip14a8Alt0,altitudeAfterM,speedMps:wip14a8Speed0,speedAfterMps:speed,mach, machAfter:speed/Math.max(1,soundAfterMps),massKg:mass,
        rhoKgM3:rho,speedOfSoundMps:soundMps,dynamicPressurePa:q,thrustN,thrustAlongVelocityN,dragParasiteN,dragControlN,dragManeuverN,dragTotalN:dragN,normalForceAlongVelocityN,gravityAlongVelocityN,netAxialForceN,actualNetAlongVelocityN,
        axialAccelerationMps2:netAxialForceN/mass,actualAxialAccelerationMps2:actualNetAlongVelocityN/mass,numericalSpeedAccelerationMps2:(speed-wip14a8Speed0)/dt,
        CdBase:cdBase,CdControl:cdControl,CdInducedEquivalent:q>1e-12?dragManeuverN/(q*Aref):0,referenceAreaM2:Aref,liftReferenceAreaM2:Slift,
        rawAlphaDeg:rad2deg(rawAlpha),rawBetaDeg:rad2deg(rawBeta),alphaDeg:rad2deg(alpha),betaDeg:rad2deg(beta),aoaDeg:rad2deg(Math.hypot(alpha,beta)),finPitchDeg:rad2deg(m.finPitch??0),finYawDeg:rad2deg(m.finYaw??0),
        flightPathAngleDeg:rad2deg(velP),bodyPitchDeg:rad2deg(P),bodyVsVelocityAngleDeg:rad2deg(Math.acos(bodyDot)),propulsionPhase:phase,boosterAttached:twoStage?!m.boosterSeparated:false,boosterSeparated:twoStage?!!m.boosterSeparated:false,
        thrustUnitX:tx,thrustUnitY:ty,thrustUnitZ:tz,velocityUnitX:ex,velocityUnitY:ey,velocityUnitZ:ez,dragAlongVelocityN:-dragN,
        kineticEnergyJ,potentialEnergyJ,kineticEnergyAfterJ,potentialEnergyAfterJ,thrustPowerW,dragPowerW,gravityPowerW,normalAeroPowerW,thrustPowerMidW,dragPowerMidW,gravityPowerMidW,normalAeroPowerMidW,
        kineticEnergyRateW,kineticPowerMidW,kineticPowerResidualMidW:kineticEnergyRateW-kineticPowerMidW,mechanicalEnergyRateActualW,mechanicalEnergyRateMidpointW,mechanicalSourcePowerMidW,
        mechanicalMidpointResidualW:mechanicalEnergyRateMidpointW-mechanicalSourcePowerMidW,semiImplicitPositionEnergyBiasW:mechanicalEnergyRateActualW-mechanicalEnergyRateMidpointW,
        requestedKePlusPeVsThrustDragGravityResidualW:mechanicalEnergyRateActualW-(thrustPowerW+dragPowerW+gravityPowerW),energyAuditScope:'FIXED_MASS_FORCE_SUBSTEP_AFTER_PROPELLANT_DEPLETION',
        forceSumResidualN:Math.hypot(mass*ax-fx,mass*ay-fy,mass*az-fz),axialAccelerationIdentityResidualMps2:netAxialForceN/mass-(thrustAlongVelocityN-dragN+gravityAlongVelocityN)/mass,
        thrustProjectionResidualN:thrustAlongVelocityN-thrustN*(tx*ex+ty*ey+tz*ez),gravityProjectionResidualN:gravityAlongVelocityN-(-mass*G0*ez),zeroAoaDiagnostic:wip14a8ZeroAoa};
      if(wip14a10WindAxis)Object.assign(record,{aeroMode:wip14a13AeroKernel.traceMode,liftForceAlongVelocityN,sideForceAlongVelocityN,
        windDragUnitX:wip14a10Basis.drag.x,windDragUnitY:wip14a10Basis.drag.y,windDragUnitZ:wip14a10Basis.drag.z,
        windLiftUnitX:wip14a10Basis.lift.x,windLiftUnitY:wip14a10Basis.lift.y,windLiftUnitZ:wip14a10Basis.lift.z,
        windSideUnitX:wip14a10Basis.side.x,windSideUnitY:wip14a10Basis.side.y,windSideUnitZ:wip14a10Basis.side.z,
        windDotDragLift:wip14a10Basis.dots.dragLift,windDotDragSide:wip14a10Basis.dots.dragSide,windDotLiftSide:wip14a10Basis.dots.liftSide,
        windDotLiftVelocity:wip14a10Basis.dots.liftVelocity,windDotSideVelocity:wip14a10Basis.dots.sideVelocity,windBasisFallback:wip14a10Basis.fallback,
        CdBaseReferenceAreaM2:Aref,CdControlReferenceAreaM2:Aref,CnCyReferenceAreaM2:Slift,CdInducedReferenceAreaM2:Slift});
      if(m._wip14a12BasisAuditEnabled&&wip14a10Basis?.a12)Object.assign(record,{windBasisAlgorithm:wip14a10Basis.a12.algorithm,windBasisRegion:wip14a10Basis.a12.region,windBodyProjectionMagnitude:wip14a10Basis.a12.bodyProjectionMagnitude,windBodyBlendWeight:wip14a10Basis.a12.bodyWeight,windTransportUsed:wip14a10Basis.a12.transportUsed,windInitialSeed:wip14a10Basis.a12.initialSeed,windHemisphereAligned:wip14a10Basis.a12.hemisphereAligned,windHardFallback:wip14a10Basis.a12.hardFallback,windLastValidReuse:wip14a10Basis.a12.lastValidReuse,windLiftDotPrev:wip14a10Basis.a12.liftDotPrev,windSideDotPrev:wip14a10Basis.a12.sideDotPrev,windLiftDirectionJumpDeg:wip14a10Basis.a12.liftDirectionJumpDeg,windSideDirectionJumpDeg:wip14a10Basis.a12.sideDirectionJumpDeg,windBasisUnitResidual:wip14a10Basis.a12.unitResidual,windBasisOrthogonalityResidual:wip14a10Basis.a12.orthogonalityResidual,windBasisHandednessResidual:wip14a10Basis.a12.handednessResidual,windBasisFinite:wip14a10Basis.a12.finite});
      if(m._wip14a11Experiment){const es=m._wip14a11AeroState??{},ts=m._wip14a11ThrustState??{};Object.assign(record,{
        uncertaintyCaseId:m._wip14a11Experiment.id,aeroUncertaintyModel:m._wip14a11Experiment.aeroModel,baseDragStateModel:m._wip14a11Experiment.baseDragModel,
        mk104ReferenceModel:m._wip14a11Experiment.mk104ReferenceModel,mk72ReferenceModel:m._wip14a11Experiment.mk72ReferenceModel,
        rawMotorThrustN:ts.rawThrustN??thrustN,effectiveMotorThrustN:thrustN,thrustPressureCorrectionN:ts.pressureCorrectionN??0,mk72ThrustScale:ts.mk72Scale??1,
        ambientPressurePa:ts.ambientPressurePa??null,nozzleExitAreaUpperBoundM2:ts.exitAreaUpperBoundM2??null,thrustInterpretationPhase:ts.phase??null,
        aeroCdSource:es.source??'AERO_CURRENT',aeroPowerState:es.powerState??(thrustN>1?'POWERED':'UNPOWERED'),aeroUpperStageApplied:!!es.upperStageApplied,
        aeroBaseDeltaCd:es.baseDeltaCd??0,positionX:m.x,positionY:m.y,windBasisFallbackUsed:wip14a10WindAxis&&wip14a10Basis.fallback!=='BODY_UP_PROJECTION'});}
      wip14a8RecordForceBalance(m,record);
    }
    WIP14A2_SPEED_DIAGNOSTICS.record((m._v1Profile?.id??'SAM')+'_AERO_EMERGENT',speed,null);
    m.vx=mpsToWorldSpeed(vx);m.vy=mpsToWorldSpeed(vy);m.vz=vz;m.speed=mpsToWorldSpeed(speed);
    if(speed>1){m.velAngle=Math.atan2(vy,vx);m.velPitch=Math.atan2(vz,Math.hypot(vx,vy));}
    // WIP59: post-force departure/weathercock guard ported from the air-to-air BODY_6DOF path.
    // 6DOF-lite may lag the flight path, but allowing 50-90deg sustained alpha/beta makes the
    // clamped force model self-inconsistent and creates false energy bleed / sea dives.
    {
      const alphaPostMax=Math.max(deg(8),aoaMax),betaPostMax=Math.max(deg(8),deg(p.maxBetaDeg??25));
      const launchOwned=!!(m.vlsPhase||m.pitchoverPhase);
      const postInc=launchOwned?_samBodyIncidence3D(m,worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0):null;
      let alphaPost=postInc?postInc.alpha:((m.pitch??m.velPitch??0)-(m.velPitch??0));
      let betaPost=postInc?postInc.beta:angNorm((m.heading??m.velAngle??0)-(m.velAngle??0));
      const nPost=Math.hypot(alphaPost/Math.max(1e-6,alphaPostMax),betaPost/Math.max(1e-6,betaPostMax));
      if(nPost>1){
        const guard=clamp((nPost-1)/1.6,0,1);
        if(launchOwned){
          // WIP157: launch controller owns attitude.  Do not reconstruct Euler heading/pitch from
          // velocity angles near vertical; only damp excess body rate and let TVC/fins recover.
          m.pitchRate*=lerp(1,.55,guard);m.yawRate*=lerp(1,.55,guard);m._samAoaGuard=guard;
        }else{
          const sc=1/Math.max(1e-6,nPost);alphaPost*=sc;betaPost*=sc;
          m.pitch=clamp((m.velPitch??0)+alphaPost,deg(-89),deg(89));m.heading=angNorm((m.velAngle??0)+betaPost);
          m.pitchRate*=lerp(1,.55,guard);m.yawRate*=lerp(1,.55,guard);m._samAoaGuard=guard;
        }
      }else m._samAoaGuard=0;
    }
    m.x+=m.vx*dt;m.y+=m.vy*dt;m.z=(m.z??0)+m.vz*dt;

    const along=axNoG*ex+ayNoG*ey+azNoG*ez;
    const nxA=axNoG-along*ex,nyA=ayNoG-along*ey,nzA=azNoG-along*ez;
    const normalG=Math.hypot(nxA,nyA,nzA)/G0;
    m.sam6dofActualNormalG=normalG;m.curG=clamp(Math.sqrt(1+normalG*normalG),1,gHard);
    // Retain the physical normal-acceleration vector for next-frame acceleration-loop feedback.
    m._samPrevNormalAccWorld={x:nxA,y:nyA,z:nzA};

    // WIP48: G-delivery instrumentation. Magnitude-only normal-G can report a perfect
    // delivery ratio even when the force points in the wrong direction, so project the actual
    // normal-acceleration vector onto the post-clamp autopilot command direction.
    const gc=m._v1ControlCommandVec;
    let deliveredG=0,guideRatio=null,controlRatio=null,deliveryValid=false;
    if(gc&&Number.isFinite(gc.ux)&&Number.isFinite(gc.uy)&&Number.isFinite(gc.uz)){
      deliveredG=(nxA*gc.ux+nyA*gc.uy+nzA*gc.uz)/G0;
      const rawG=Math.max(0,m._v1GCommand??0),ctlG=Math.max(0,m._v1GAchieved??0);
      if(rawG>=0.10)guideRatio=deliveredG/Math.max(.10,rawG);
      if(ctlG>=0.10)controlRatio=deliveredG/Math.max(.10,ctlG);
      const srcAge=m._v1SourceArb?.sourceAgeS??999;
      deliveryValid=ctlG>=1.0&&!m.vlsPhase&&!m.pitchoverPhase&&srcAge>=0.08;
      if(deliveryValid){
        const k=1-Math.exp(-dt/0.25); // 0.25 s EMA: actuator/body response is not instantaneous.
        if(Number.isFinite(guideRatio))m._v1GDeliveryGuidanceEma=lerp(m._v1GDeliveryGuidanceEma??guideRatio,guideRatio,k);
        if(Number.isFinite(controlRatio))m._v1GDeliveryControlEma=lerp(m._v1GDeliveryControlEma??controlRatio,controlRatio,k);
      }
    }
    m.sam6dofDeliveredG=deliveredG;
    m._v1GDeliveryGuidanceRatio=guideRatio;m._v1GDeliveryControlRatio=controlRatio;m._v1GDeliveryValid=deliveryValid;
    m._v1BridgeVs6dofAvailRatio=(m.availableG>1e-6)?((m._v1GAchieved??0)/m.availableG):null;

    m.rawAlphaDeg=rad2deg(rawAlpha);m.rawBetaDeg=rad2deg(rawBeta);
    m.effectiveAlphaDeg=rad2deg(alpha);m.effectiveBetaDeg=rad2deg(beta);
    m.rawAoaDeg=rad2deg(Math.hypot(rawAlpha,rawBeta));
    m.aoa=Math.hypot(alpha,beta);m.aoaDeg=rad2deg(m.aoa);
    m.cmdOmegaYaw=omegaYawCmd;m.cmdOmegaPit=omegaPitCmd;m.actOmegaYaw=m.yawRate;m.actOmegaPit=m.pitchRate;m.omegaYaw=m.yawRate;m.omegaPit=m.pitchRate;
    m.finCmdYawDeg=rad2deg(finYawCmd);m.finCmdPitchDeg=rad2deg(finPitCmd);m.finYawDeg=rad2deg(m.finYaw);m.finPitchDeg=rad2deg(m.finPitch);
    m.sam6dofDebug={qPa:q,rhoKgM3:rho,mach,structuralG:gHard,optimalManeuverG:gOptimal,gQ,gAero,gAeroForceCap:forceCap.gForceCap,cnLimitRaw:forceCap.cnLimRaw,cnLimitOptimal:forceCap.cnOptimal,cnLimitEffective:forceCap.cnLim,gAeroBound,gTvc,availableG:m.availableG,launchAgg,normalG,deliveredG,rawAlphaDeg:rad2deg(rawAlpha),rawBetaDeg:rad2deg(rawBeta),alphaDeg:rad2deg(alpha),betaDeg:rad2deg(beta),guidanceDeliveryRatio:guideRatio,controlDeliveryRatio:controlRatio,guidanceDeliveryEma:m._v1GDeliveryGuidanceEma,controlDeliveryEma:m._v1GDeliveryControlEma,bridgeVs6dofAvail:m._v1BridgeVs6dofAvailRatio,aspectRatio:p.aspectRatio??m.aspectRatio??3.0,oswaldEff:p.oswaldEff??m.oswaldEff??.8,finAccelLoopActive:accelLoopActive,finAccelYawReqMps2:aYawReq,finAccelPitReqMps2:aPitReq,finAccelYawDeliveredMps2:m._samFinAccelYawFilt??0,finAccelPitDeliveredMps2:m._samFinAccelPitFilt??0,finAccelFeedForwardScale:ffScale,finAccelIntYaw:iYaw,finAccelIntPit:iPit,bodyRateDampActive:!!m._samBodyRateDampActive,bodyRateDampPit:m._samBodyRateDampPit??0,bodyRateDampYaw:m._samBodyRateDampYaw??0,CN,CY,dragN,dragParasiteN,dragControlN,dragManeuverN,cdIndBase,maneuverDragScale,aoaGuard:m._samAoaGuard??0,Fn,Fs,Mpit,Myaw,Iy,Iz,tvcAuthority:tvcAuth,tvcYawDeg:rad2deg(m.tvcYaw??0),tvcPitchDeg:rad2deg(m.tvcPitch??0),termAuthority:term,controlAuthority};
    if(wip14a10WindAxis)Object.assign(m.sam6dofDebug,{aeroMode:'WIND_AXIS_EXPERIMENTAL',windAxisBasis:wip14a10Basis});
    return true;
  }
const WIP14A2_SPEED_DIAGNOSTICS={record(){},tick(){},enabled:false};
function wip14a8RecordForceBalance(m,r){
    if(!wip14a8IsStandardMissile(m))return;
    m._wip14a8ForceBalance=r;
    const a=m._wip14a8Audit;if(!a?.enabled)return;
    if(a.trace.length<a.maxRecords)a.trace.push(r);else a.truncated=true;
    if(!a.events.launch)wip14a8StoreEvent(a,'launch',r,{definition:'FIRST_FREE_FLIGHT_FORCE_TICK'});
    for(const threshold of WIP14A8_MACH_EVENTS){
      const key='mach'+String(threshold).replace('.','p');
      if(a.previousMach<threshold&&r.mach>=threshold)wip14a8StoreEvent(a,key,r,{thresholdMach:threshold});
    }
    const phase=String(r.propulsionPhase||'');
    const isMk104=phase.startsWith('MK104_')||(!a.twoStage&&(phase==='BOOST'||phase==='SUSTAIN'));
    const prevMk104=String(a.previousPhase||'').startsWith('MK104_')||(!a.twoStage&&(a.previousPhase==='BOOST'||a.previousPhase==='SUSTAIN'));
    if(isMk104&&!prevMk104)wip14a8StoreEvent(a,'mk104Ignition',r);
    if(phase.includes('SUSTAIN')&&String(a.previousPhase||'').includes('BOOST'))wip14a8StoreEvent(a,'mk104BoostToSustain',r);
    if(!a.events.mk104Burnout&&a.previousThrustN>1&&r.thrustN<=1&&r.timeS+1e-9>=(m._propulsionSequenceEndS??Infinity))wip14a8StoreEvent(a,'mk104Burnout',r,{lastPoweredForceBalance:wip14a8CloneRecord(a.previousRecord)});
    const attached=a.twoStage?!!r.boosterAttached:false;
    if(a.twoStage&&a.previousBoosterAttached&&!attached)wip14a8StoreEvent(a,'boosterSeparation',r,{immediateBefore:wip14a8CloneRecord(a.previousRecord)});
    if(!a.events.terminalEntry&&(m._v1TerminalActive||m._wip79ThreeSecEntry))wip14a8StoreEvent(a,'terminalEntry',r);
    if(!a.peakRecord||r.speedAfterMps>a.peakRecord.speedAfterMps)a.peakRecord=r;
    a.previousMach=r.mach;a.previousPhase=phase;a.previousThrustN=r.thrustN;a.previousRecord=r;a.previousBoosterAttached=attached;
  }
function wip14a8CloneRecord(r){return r?{...r}:null;}
const WIP14A8_MACH_EVENTS=DATA["WIP14A8_MACH_EVENTS"];
function wip14a8StoreEvent(a,key,r,extra={}){
    if(!a||a.events[key]||!r)return false;
    a.events[key]={event:key,timeS:r.timeS,...extra,forceBalance:wip14a8CloneRecord(r)};return true;
  }
const WIP14A8_FORCE_TRACE_SCHEMA=DATA["WIP14A8_FORCE_TRACE_SCHEMA"];
function wip14a12ContinuousWindBasis(m,ex,ey,ez,ux,uy,uz,rx,ry,rz){
    const telemetry=m._windBasisTelemetry??(m._windBasisTelemetry=wip14a12NewTelemetry());
    const v=wip14a12Normalize(wip14a12Vec(ex,ey,ez))??wip14a12Vec(1,0,0),up=wip14a12Normalize(wip14a12Vec(ux,uy,uz))??wip14a12Vec(0,0,1),right=wip14a12Normalize(wip14a12Vec(rx,ry,rz))??wip14a12Vec(0,1,0),prev=m._windBasisPrev?.valid?m._windBasisPrev:null,legacy=wip14a10WindBasis(ex,ey,ez,ux,uy,uz,rx,ry,rz),legacyHanded=wip14a12Dot(wip14a12Cross(legacy.drag,legacy.lift),legacy.side)>0;
    const bodyProjection=wip14a12ProjectPlane(up,v),bodyProjectionMagnitude=Math.hypot(bodyProjection.x,bodyProjection.y,bodyProjection.z),bodyLift=wip14a12Normalize(bodyProjection);
    telemetry.minBodyProjectionMagnitude=Math.min(telemetry.minBodyProjectionMagnitude,bodyProjectionMagnitude);
    let lift=null,region='INITIAL',fallback='BODY_UP_PROJECTION',transported=null,transportUsed=false,bodyWeight=1,hardFallback=false,lastValidReuse=false,initialSeed=false,hemisphereAligned=false,useLegacyExact=false;
    if(prev){
      transported=wip14a12TransportLift(prev,v);if(transported){transportUsed=true;telemetry.transportUseCount++;}
      if(!transported){telemetry.hardFallbackCount++;hardFallback=true;}
    }
    if(!prev){
      if(bodyProjectionMagnitude>=WIP14A12_SINGULAR_HIGH&&legacyHanded){lift={...legacy.lift};fallback=legacy.fallback;region='NORMAL';useLegacyExact=true;telemetry.bodyProjectionUseCount++;}
      else{const seeded=wip14a12SeedLift(v,up,right);lift=seeded.lift;fallback=seeded.kind;region=bodyProjectionMagnitude<=WIP14A12_SINGULAR_LOW?'SINGULAR':bodyProjectionMagnitude<WIP14A12_SINGULAR_HIGH?'TRANSITION':'NORMAL';if(region==='NORMAL')telemetry.bodyProjectionUseCount++;}
      initialSeed=true;telemetry.initialSeedCount++;
    }else if(transported){
      if(bodyProjectionMagnitude<=WIP14A12_SINGULAR_LOW||!bodyLift){lift=transported;bodyWeight=0;region='SINGULAR';fallback='PARALLEL_TRANSPORT_SINGULAR';telemetry.singularRegionCount++;}
      else{
        bodyWeight=wip14a12Smooth01((bodyProjectionMagnitude-WIP14A12_SINGULAR_LOW)/(WIP14A12_SINGULAR_HIGH-WIP14A12_SINGULAR_LOW));
        const blended=wip14a12SlerpHemisphere(transported,bodyLift,bodyWeight);lift=blended.vector;hemisphereAligned=blended.hemisphereFlip;if(hemisphereAligned){telemetry.hemisphereAlignmentCount++;telemetry.continuitySignLockCount++;}
        if(bodyProjectionMagnitude<WIP14A12_SINGULAR_HIGH){region='TRANSITION';fallback=hemisphereAligned?'PARALLEL_TRANSPORT_BLEND_SIGN_LOCK':'PARALLEL_TRANSPORT_BLEND';telemetry.blendRegionCount++;}
        else{region='NORMAL';fallback=hemisphereAligned?'CONTINUITY_SIGN_LOCK':'BODY_UP_PROJECTION';telemetry.bodyProjectionUseCount++;if(!hemisphereAligned&&legacyHanded){lift={...legacy.lift};fallback=legacy.fallback;useLegacyExact=true;}}
      }
    }
    if(!lift){const seeded=wip14a12SeedLift(v,up,right);lift=seeded.lift;fallback='HARD_FALLBACK_'+seeded.kind;hardFallback=true;telemetry.hardFallbackCount++;}
    if(!lift&&prev?.liftHat){lift=wip14a12Normalize(wip14a12ProjectPlane(prev.liftHat,v));lastValidReuse=!!lift;if(lastValidReuse){fallback='LAST_VALID_REUSE';telemetry.lastValidReuseCount++;}}
    if(!lift){lift=wip14a12Normalize(wip14a12ProjectPlane(wip14a12LeastParallelWorld(v),v))??wip14a12Vec(0,1,0);fallback='DETERMINISTIC_SAFETY_AXIS';hardFallback=true;telemetry.hardFallbackCount++;}
    let side=useLegacyExact?{...legacy.side}:wip14a12Normalize(wip14a12Cross(lift,v));
    if(!side&&prev?.sideHat){side=wip14a12Normalize(wip14a12ProjectPlane(prev.sideHat,v));lastValidReuse=!!side;if(lastValidReuse)telemetry.lastValidReuseCount++;}
    if(!side){const alt=wip14a12Normalize(wip14a12ProjectPlane(wip14a12LeastParallelWorld(v),v));side=alt?wip14a12Normalize(wip14a12Cross(alt,v)):null;hardFallback=true;telemetry.hardFallbackCount++;}
    if(!side){side=wip14a12Vec(0,1,0);telemetry.invalidBasisCount++;}
    // One frame sign, never independent lift/side flips. This preserves handedness.
    if(prev){const ld=wip14a12Dot(lift,prev.liftHat),sd=wip14a12Dot(side,prev.sideHat);if(ld<0||(Math.abs(ld)<1e-14&&sd<0)){lift=wip14a12Neg(lift);side=wip14a12Neg(side);hemisphereAligned=true;telemetry.hemisphereAlignmentCount++;}}
    const drag=useLegacyExact?{...legacy.drag}:wip14a12Neg(v),liftN=Math.hypot(lift.x,lift.y,lift.z),sideN=Math.hypot(side.x,side.y,side.z),vN=Math.hypot(v.x,v.y,v.z),dragLift=useLegacyExact?legacy.dots.dragLift:wip14a12Dot(drag,lift),dragSide=useLegacyExact?legacy.dots.dragSide:wip14a12Dot(drag,side),liftSide=useLegacyExact?legacy.dots.liftSide:wip14a12Dot(lift,side),liftVelocity=useLegacyExact?legacy.dots.liftVelocity:wip14a12Dot(lift,v),sideVelocity=useLegacyExact?legacy.dots.sideVelocity:wip14a12Dot(side,v),handed=wip14a12Cross(drag,lift),handedResidual=Math.hypot(handed.x-side.x,handed.y-side.y,handed.z-side.z);
    const finite=[drag,lift,side].every(wip14a12Finite);if(!finite)telemetry.nanInfCount++;
    telemetry.maxUnitResidual=Math.max(telemetry.maxUnitResidual,Math.abs(vN-1),Math.abs(liftN-1),Math.abs(sideN-1));telemetry.maxOrthogonalityResidual=Math.max(telemetry.maxOrthogonalityResidual,Math.abs(dragLift),Math.abs(dragSide),Math.abs(liftSide),Math.abs(liftVelocity),Math.abs(sideVelocity));telemetry.maxHandednessResidual=Math.max(telemetry.maxHandednessResidual,handedResidual);
    let liftJumpDeg=0,sideJumpDeg=0,liftDotPrev=null,sideDotPrev=null;if(prev){liftDotPrev=clamp(wip14a12Dot(lift,prev.liftHat),-1,1);sideDotPrev=clamp(wip14a12Dot(side,prev.sideHat),-1,1);liftJumpDeg=rad2deg(Math.acos(liftDotPrev));sideJumpDeg=rad2deg(Math.acos(sideDotPrev));telemetry.maxLiftJumpDeg=Math.max(telemetry.maxLiftJumpDeg,liftJumpDeg);telemetry.maxSideJumpDeg=Math.max(telemetry.maxSideJumpDeg,sideJumpDeg);if(liftDotPrev<0)telemetry.liftSignFlipCount++;if(sideDotPrev<0)telemetry.sideSignFlipCount++;if(prev.boosterSeparated!==!!m.boosterSeparated)telemetry.stageTransitionCount++;const phase=String(m._v1GuidancePhase??'UNSET');if(prev.guidancePhase!==phase)telemetry.guidancePhaseTransitionCount++;}
    if(hardFallback||lastValidReuse){telemetry.currentConsecutiveFallbackTicks++;telemetry.maxConsecutiveFallbackTicks=Math.max(telemetry.maxConsecutiveFallbackTicks,telemetry.currentConsecutiveFallbackTicks);}else telemetry.currentConsecutiveFallbackTicks=0;
    m._windBasisPrev={velocityHat:{...v},liftHat:{...lift},sideHat:{...side},bodyUpHat:{...up},bodyRightHat:{...right},valid:true,boosterSeparated:!!m.boosterSeparated,guidancePhase:String(m._v1GuidancePhase??'UNSET')};
    return {drag,lift,side,fallback,dots:{dragLift,dragSide,liftSide,liftVelocity,sideVelocity},orientation:useLegacyExact?{...legacy.orientation}:{liftBodyUp:wip14a12Dot(lift,up),sideBodyRight:wip14a12Dot(side,right)},a12:{algorithm:'MINIMAL_ROTATION_PARALLEL_TRANSPORT_WITH_SMOOTH_BODY_UP_BLEND',region,bodyProjectionMagnitude,bodyWeight,transportUsed,initialSeed,hemisphereAligned,hardFallback,lastValidReuse,liftDotPrev,sideDotPrev,liftDirectionJumpDeg:liftJumpDeg,sideDirectionJumpDeg:sideJumpDeg,unitResidual:Math.max(Math.abs(vN-1),Math.abs(liftN-1),Math.abs(sideN-1)),orthogonalityResidual:Math.max(Math.abs(dragLift),Math.abs(dragSide),Math.abs(liftSide),Math.abs(liftVelocity),Math.abs(sideVelocity)),handednessResidual:handedResidual,finite}};
  }
function wip14a12Finite(a){return !!a&&Number.isFinite(a.x)&&Number.isFinite(a.y)&&Number.isFinite(a.z);}
function wip14a12Neg(a){return {x:-a.x,y:-a.y,z:-a.z};}
function wip14a12LeastParallelWorld(v){const axes=[{x:1,y:0,z:0},{x:0,y:1,z:0},{x:0,y:0,z:1}];return axes.reduce((best,a)=>Math.abs(wip14a12Dot(a,v))<Math.abs(wip14a12Dot(best,v))?a:best,axes[0]);}
function wip14a12Dot(a,b){return a.x*b.x+a.y*b.y+a.z*b.z;}
function wip14a12SlerpHemisphere(a,b,t){
    let bb=b,d=clamp(wip14a12Dot(a,bb),-1,1),hemisphereFlip=false;
    if(d<0){bb=wip14a12Neg(bb);d=-d;hemisphereFlip=true;}
    if(t<=0)return {vector:a,hemisphereFlip};if(t>=1)return {vector:bb,hemisphereFlip};
    if(d>.999999){const n=wip14a12Normalize(wip14a12Add(wip14a12Scale(a,1-t),wip14a12Scale(bb,t)));return {vector:n??a,hemisphereFlip};}
    const angle=Math.acos(clamp(d,-1,1)),s=Math.sin(angle),wa=Math.sin((1-t)*angle)/s,wb=Math.sin(t*angle)/s;
    return {vector:wip14a12Normalize(wip14a12Add(wip14a12Scale(a,wa),wip14a12Scale(bb,wb)))??a,hemisphereFlip};
  }
function wip14a12Scale(a,s){return {x:a.x*s,y:a.y*s,z:a.z*s};}
function wip14a12Add(a,b){return {x:a.x+b.x,y:a.y+b.y,z:a.z+b.z};}
function wip14a12Normalize(a){const n=Math.hypot(a.x,a.y,a.z);if(!Number.isFinite(n)||n*n<WIP14A12_BASIS_EPS2)return null;const k=1/n;return {x:a.x*k,y:a.y*k,z:a.z*k};}
const WIP14A12_BASIS_EPS2=DATA["WIP14A12_BASIS_EPS2"];
function wip14a12Smooth01(x){x=clamp(x,0,1);return x*x*(3-2*x);}
const WIP14A12_SINGULAR_LOW=DATA["WIP14A12_SINGULAR_LOW"];
function wip14a12SeedLift(v,up,right){
    let candidate=wip14a12ProjectPlane(up,v),kind='BODY_UP_PROJECTION',n=wip14a12Normalize(candidate);
    if(!n){candidate=wip14a12ProjectPlane(right,v);n=wip14a12Normalize(candidate);kind='BODY_RIGHT_PROJECTION';}
    if(!n){candidate=wip14a12ProjectPlane(wip14a12LeastParallelWorld(v),v);n=wip14a12Normalize(candidate);kind='WORLD_AXIS_PROJECTION';}
    return {lift:n,kind};
  }
function wip14a12ProjectPlane(a,n){return wip14a12Cross(n,wip14a12Cross(a,n));}
function wip14a12Cross(a,b){return {x:a.y*b.z-a.z*b.y,y:a.z*b.x-a.x*b.z,z:a.x*b.y-a.y*b.x};}
const WIP14A12_SINGULAR_HIGH=DATA["WIP14A12_SINGULAR_HIGH"];
function wip14a12TransportLift(prev,newV){
    const oldV=wip14a12Normalize(prev?.velocityHat),oldLift=wip14a12Normalize(prev?.liftHat);if(!oldV||!oldLift)return null;
    const d=clamp(wip14a12Dot(oldV,newV),-1,1),c=wip14a12Cross(oldV,newV),cn=Math.hypot(c.x,c.y,c.z);let rotated;
    if(cn>1e-12){const k=wip14a12Scale(c,1/cn),angle=Math.atan2(cn,d),ca=Math.cos(angle),sa=Math.sin(angle);rotated=wip14a12Add(wip14a12Add(wip14a12Scale(oldLift,ca),wip14a12Scale(wip14a12Cross(k,oldLift),sa)),wip14a12Scale(k,wip14a12Dot(k,oldLift)*(1-ca)));}
    else if(d>=0)rotated=oldLift;
    else rotated=oldLift; // deterministic 180-degree case: rotate about the previous lift axis.
    return wip14a12Normalize(wip14a12ProjectPlane(rotated,newV));
  }
function wip14a10WindBasis(ex,ey,ez,ux,uy,uz,rx,ry,rz){
    const en=Math.max(1e-15,Math.hypot(ex,ey,ez));ex/=en;ey/=en;ez/=en;
    const upDot=ux*ex+uy*ey+uz*ez;
    let lx=ux-upDot*ex,ly=uy-upDot*ey,lz=uz-upDot*ez,ln=Math.hypot(lx,ly,lz),fallback='BODY_UP_PROJECTION';
    if(ln<1e-10){
      const rightDot=rx*ex+ry*ey+rz*ez;lx=rx-rightDot*ex;ly=ry-rightDot*ey;lz=rz-rightDot*ez;ln=Math.hypot(lx,ly,lz);fallback='BODY_RIGHT_PROJECTION';
    }
    if(ln<1e-10){
      let fx=0,fy=0,fz=1;if(Math.abs(ez)>.9){fx=1;fy=0;fz=0;}
      const fd=fx*ex+fy*ey+fz*ez;lx=fx-fd*ex;ly=fy-fd*ey;lz=fz-fd*ez;ln=Math.max(1e-15,Math.hypot(lx,ly,lz));fallback='WORLD_AXIS_PROJECTION';
    }
    lx/=ln;ly/=ln;lz/=ln;
    if(lx*ux+ly*uy+lz*uz<0){lx=-lx;ly=-ly;lz=-lz;}
    let sx=ly*ez-lz*ey,sy=lz*ex-lx*ez,sz=lx*ey-ly*ex,sn=Math.max(1e-15,Math.hypot(sx,sy,sz));sx/=sn;sy/=sn;sz/=sn;
    if(sx*rx+sy*ry+sz*rz<0){sx=-sx;sy=-sy;sz=-sz;}
    const dx=-ex,dy=-ey,dz=-ez;
    return {drag:{x:dx,y:dy,z:dz},lift:{x:lx,y:ly,z:lz},side:{x:sx,y:sy,z:sz},fallback,
      dots:{dragLift:dx*lx+dy*ly+dz*lz,dragSide:dx*sx+dy*sy+dz*sz,liftSide:lx*sx+ly*sy+lz*sz,liftVelocity:lx*ex+ly*ey+lz*ez,sideVelocity:sx*ex+sy*ey+sz*ez},
      orientation:{liftBodyUp:lx*ux+ly*uy+lz*uz,sideBodyRight:sx*rx+sy*ry+sz*rz}};
  }
function wip14a12Vec(x=0,y=0,z=0){return {x:Number(x)||0,y:Number(y)||0,z:Number(z)||0};}
function wip14a12NewTelemetry(){return {schema:'AEGIS_WIND_BASIS_TELEMETRY_V48_WIP14A12',initialSeedCount:0,transportUseCount:0,bodyProjectionUseCount:0,blendRegionCount:0,singularRegionCount:0,continuitySignLockCount:0,hemisphereAlignmentCount:0,hardFallbackCount:0,lastValidReuseCount:0,currentConsecutiveFallbackTicks:0,maxConsecutiveFallbackTicks:0,maxLiftJumpDeg:0,maxSideJumpDeg:0,liftSignFlipCount:0,sideSignFlipCount:0,minBodyProjectionMagnitude:Infinity,invalidBasisCount:0,nanInfCount:0,maxUnitResidual:0,maxOrthogonalityResidual:0,maxHandednessResidual:0,stageTransitionCount:0,guidancePhaseTransitionCount:0,historyResetCount:0,lifecycleLaunchInitializations:1,lifecycleDisposals:0};}
function wip14a13ResolveAeroKernel(m){
    const standard=wip14a8IsStandardMissile(m),requested=String(m?._wip14a10AeroMode??'').toUpperCase();
    if(!standard)return {kernel:'LEGACY',traceMode:'LEGACY',windAxis:false,standard:false,explicit:false};
    if(requested==='LEGACY')return {kernel:'LEGACY',traceMode:'LEGACY',windAxis:false,standard:true,explicit:true};
    if(requested==='WIND_AXIS_EXPERIMENTAL')return {kernel:'WIND_AXIS_CONTINUOUS',traceMode:'WIND_AXIS_EXPERIMENTAL',windAxis:true,standard:true,explicit:true};
    return {kernel:STANDARD_AERO_KERNEL,traceMode:'WIND_AXIS_CONTINUOUS',windAxis:true,standard:true,explicit:requested==='WIND_AXIS_CONTINUOUS'};
  }
const STANDARD_AERO_KERNEL=DATA["STANDARD_AERO_KERNEL"];
function _samBodyIncidence3D(m,vxMps,vyMps,vzMps){
    const H=Number(m?.heading)||0,P=Number(m?.pitch)||0,R=Number(m?.roll)||0;
    const cH=Math.cos(H),sH=Math.sin(H),cP=Math.cos(P),sP=Math.sin(P),cR=Math.cos(R),sR=Math.sin(R);
    const bx=cP*cH,by=cP*sH,bz=sP;
    const r0x=-sH,r0y=cH,r0z=0,u0x=-sP*cH,u0y=-sP*sH,u0z=cP;
    const rx=r0x*cR+u0x*sR,ry=r0y*cR+u0y*sR,rz=r0z*cR+u0z*sR;
    const ux=-r0x*sR+u0x*cR,uy=-r0y*sR+u0y*cR,uz=-r0z*sR+u0z*cR;
    const vf=vxMps*bx+vyMps*by+vzMps*bz;
    const vr=vxMps*rx+vyMps*ry+vzMps*rz;
    const vu=vxMps*ux+vyMps*uy+vzMps*uz;
    const alpha=Math.atan2(-vu,Math.max(1e-9,vf));
    const beta=Math.atan2(-vr,Math.max(1e-9,Math.hypot(vf,vu)));
    return {alpha,beta,forwardMps:vf,rightMps:vr,upMps:vu};
  }
function _samSixDofAeroForceCap(p,q,Slift,mass,term){
    const qForceSoft=lerp(1,p.qForceSoftMin??.65,_samSmooth01((q-(p.qForceSoftPa??110000))/100000));
    const cnLimRaw=lerp(p.midcourseCnLimit??.7,p.terminalCnLimit??1.5,term)*qForceSoft;
    // WIP58: the normal operating load envelope is distinct from the structural hard limit.
    // Translate optimalManeuverG back into a combined CN/CY coefficient cap so actual aerodynamic
    // force cannot routinely exceed the advertised optimal-G ceiling at high dynamic pressure.
    const wip136Bypass=!!(window.WIP136_ESSM_G_CAP_BYPASS&&p.id==='ESSM_BLK2_6DOF_LITE');
    const gl=wip138EssmGLimits(p),gOptimal=wip136Bypass?999:gl.optimalG;
    const cnOptimal=q>1e-6?(gOptimal*Math.max(1,mass)*G0/(q*Math.max(1e-6,Slift))):cnLimRaw;
    const cnLim=Math.min(cnLimRaw,cnOptimal);
    const gForceCap=q>1e-6?(q*Slift*Math.max(.05,cnLim)/(Math.max(1,mass)*G0)):0;
    return {qForceSoft,cnLimRaw,cnOptimal,cnLim,gForceCap};
  }
const G0=DATA["G0"];
function wip138EssmGLimits(p){
    if(p?.id!=='ESSM_BLK2_6DOF_LITE')return {structuralG:p?.structuralG??40,optimalG:Math.min(p?.structuralG??40,p?.optimalManeuverG??p?.structuralG??40)};
    const structuralG=Math.max(1,Number(window.WIP138_ESSM_STRUCTURAL_G)||55),optimalG=Math.min(structuralG,Math.max(1,Number(window.WIP138_ESSM_OPTIMAL_G)||44));
    return {structuralG,optimalG};
  }
const window=SETTINGS;
function _samSmooth01(x){ x=clamp(x,0,1); return x*x*(3-2*x); }
function _samSixDofTermAuthority(m,p){
    const r=Math.max(0,m._rangeKmCached??999);
    const full=Math.max(.5,p.terminalFullRangeKm??8),fade=Math.max(1,p.terminalFadeRangeKm??18);
    return 1-clamp((r-full)/fade,0,1);
  }
const WIP14A5_SM2ER_STAGE_CONTRACT=DATA["WIP14A5_SM2ER_STAGE_CONTRACT"];
const WIP14A6_SM6_STAGE_CONTRACT=DATA["WIP14A6_SM6_STAGE_CONTRACT"];
const mpsToWorldSpeed = (mps) => metersToWorld(mps);
const metersToWorld = (m) => (m / METERS_PER_KM) * WORLD_UNITS_PER_KM;
function _samSixDofProfileFor(m){
    const id=m?._v1Profile?.sixDofProfileId;
    return id?SAM_6DOF_LITE_REGISTRY[id]:null;
  }
const SAM_6DOF_LITE_REGISTRY=DATA["SAM_6DOF_LITE_REGISTRY"];
function _sm2CommandEnvelopeG(m, rawDemandG=0){
    const prof=m?._v1Profile;
    if(!(prof?.id==='SM2MR_BLKIIIA_SIM'||prof?.id==='SM2ER_BLKIV_SIM'||prof?.id==='SM6_BLKIA_SIM'))return null;
    const e=prof.commandGEnvelope||{};
    const r=Math.max(0,m._rangeKmCached??999),phase=m._v1GuidancePhase??'MIDCOURSE';
    let base;
    if(phase==='ENDGAME'||phase==='TERMINAL')base=e.terminalG??24;
    else if(phase==='TRANSITION')base=e.transitionG??22.5;
    else{
      const near=e.midcourseNearKm??28,far=Math.max(near+1,e.midcourseFarKm??70);
      const near01=1-clamp((r-near)/(far-near),0,1);
      base=lerp(e.cruiseG??18,e.midcourseG??21,near01);
    }
    base=clamp(base,e.cruiseG??18,e.terminalG??24);
    const emergency=e.emergencyG??28;
    const demand01=_samSmooth01((rawDemandG-(base+1.0))/Math.max(.5,emergency-base-1.0));
    const rangeNeed=_samInvWindow(r,e.emergencyRangeFullKm??3,e.emergencyRangeZeroKm??10);
    const tgo=m._v1PredCPATime??999,cpa=Math.max(0,m._v1PredCPA??0);
    const tgoNeed=(tgo>0&&tgo<999)?_samInvWindow(tgo,e.emergencyTgoFullS??1,e.emergencyTgoZeroS??2.8):0;
    const cpaNeed=_samUpWindow(cpa,e.emergencyCpaStartM??12,e.emergencyCpaFullM??55);
    const planUrg=clamp(m._samTrajPlan?.urgency??0,0,1),urgStart=e.emergencyUrgencyStart??.78;
    const urgencyNeed=_samSmooth01((planUrg-urgStart)/Math.max(.01,1-urgStart))*_samInvWindow(r,8,18);
    // Very-close range alone can open some reserve; full 28G still requires demand plus either
    // a short-TGO miss trend or extreme launch/intercept urgency.
    const geometryNeed=Math.max(rangeNeed*.58,tgoNeed*Math.max(.30,cpaNeed),urgencyNeed);
    const emergency01=clamp(demand01*geometryNeed,0,1);
    const cap=lerp(base,emergency,emergency01);
    m._sm2CommandBaseG=base;m._sm2EmergencyBlend=emergency01;m._sm2CommandCapG=cap;
    return cap;
  }
function _samUpWindow(v,start,full){
    if(full<=start)return v>=full?1:0;
    return _samSmooth01((v-start)/(full-start));
  }
function _samInvWindow(v,fullAt,zeroAt){
    if(zeroAt<=fullAt)return v<=fullAt?1:0;
    return 1-_samSmooth01((v-fullAt)/(zeroAt-fullAt));
  }
function _samSeaClearanceRateGuard(m,isESSM,rangeKm,dt){
      if(!(m?.guidanceCore==='v1'&&isESSM)||m.vlsPhase)return null;
      const c=_samVlsControlConfig(m,isESSM),own=samNavB1OwnState(m),alt=own.posM.z,vz=own.velMps.z;
      const r=Number.isFinite(rangeKm)?rangeKm:999,downV=Math.max(0,-vz),baseLook=Math.max(.35,c.seaLookaheadS);
      // WIP59: include current downward normal acceleration in the look-ahead.  The old guard used
      // only vz+gravity, so a TVC/fin nose-over could become unrecoverable before vz itself looked bad.
      const look=clamp(Math.max(baseLook,.55+downV/140),baseLook,1.35);
      const prevNz=Math.min(0,m._samPrevNormalAccWorld?.z??0);
      const rangeBlend=clamp((r-.25)/1.5,0,1),margin=lerp(3,c.seaMarginM,rangeBlend);
      const projected=alt+vz*look+.5*prevNz*look*look-.5*G0*look*look;
      if(projected>=margin||r<=.20)return {active:false,projectedAltM:projected,marginM:margin,omegaFloor:0};
      const v=Math.max(80,worldSpeedToMps(m.speed??0));
      const reqVz=(margin-alt)/look-.5*prevNz*look+.5*G0*look;
      const reqPitch=Math.asin(clamp(reqVz/v,-.35,.55));
      const err=reqPitch-(m.velPitch??0);
      const omegaFloor=err>0?clamp(err*4.4,0,deg(58)):0;
      return {active:omegaFloor>0,projectedAltM:projected,marginM:margin,requiredPitch:reqPitch,omegaFloor,lookaheadS:look,downNormalMps2:prevNz};
    }
function samNavB1OwnState(m){samNavB1Init(m);return missileNavB2OwnState(m);}
function missileNavB2OwnState(m){
    const n=missileNavB2Init(m);if(!n)return {posM:{x:0,y:0,z:0},velMps:{x:0,y:0,z:0},mode:'NONE',profileId:null};
    return {posM:_samB1VecCopy(n.posM),velMps:_samB1VecCopy(n.velMps),mode:n.mode,profileId:n.profileId,gpsAid:!!n.gpsAid,gpsFixCount:n.gpsFixCount??0,timeS:n.timeS??0};
  }
function _samB1VecCopy(v){return {x:Number(v?.x)||0,y:Number(v?.y)||0,z:Number(v?.z)||0};}
function samNavB1Init(m,force=false){if(m&&!m._v1Profile&&!m.navProfileId&&!m.isRAM&&!ASM_PASSIVE_RF_B2_PROFILES[m.label])m._legacyNavFixtureB1=true;return missileNavB2Init(m,force);}
const ASM_PASSIVE_RF_B2_PROFILES=DATA["ASM_PASSIVE_RF_B2_PROFILES"];
function _samVlsControlConfig(m,isESSM){
      const p=m?._v1Profile||{},plan=m?._samTrajPlan,lp=_samTrajectoryProfileFor(m)?.launch||{};
      if(plan){
        return {launchClearAltM:plan.launchClearAltM,turnStartAltM:plan.turnStartAltM,attitudeCompleteAltM:plan.attitudeCompleteAltM,
          exitAltM:plan.exitAltM,initialPitch:deg(plan.initialPitchDeg),lowFloor:deg(plan.directPitchFloorDeg),trackFloor:deg(plan.trackPitchFloorDeg),
          pitchCeiling:deg(plan.pitchCeilingDeg),lookaheadM:plan.lookaheadM,minForwardMps:plan.minForwardMps,maxVelExit:deg(plan.maxVelExitDeg),
          headingTol:deg(plan.headingToleranceDeg),pitchTol:deg(plan.pitchToleranceDeg),pitMinS:plan.pitMinS,pitMaxS:plan.pitMaxS,
          seaMarginM:plan.seaMarginM,seaLookaheadS:plan.seaLookaheadS,launchLoftPitch:deg(plan.launchLoftPitchDeg),
          hardRateCap:deg(plan.hardRateCapDegS),commitRateCap:deg(plan.commitRateCapDegS),hardGain:plan.hardGain,commitGain:plan.commitGain};
      }
      // Safe fallback only; normal v1 shots always receive a registry-backed adaptive plan.
      return {launchClearAltM:lp.launchClearAltM??(isESSM?.25:1.2),turnStartAltM:lp.turnStartNormalM??(isESSM?.25:65),attitudeCompleteAltM:lp.attitudeNormalM??(isESSM?20:110),
        exitAltM:lp.exitNormalM??(isESSM?30:145),initialPitch:deg(lp.initialPitchDeg??90),lowFloor:deg(lp.directPitchFloorDeg??(isESSM?2.5:6)),trackFloor:deg(lp.trackPitchFloorDeg??(isESSM?2:5)),
        pitchCeiling:deg(lp.pitchCeilingDeg??(isESSM?58:68)),lookaheadM:lp.lookaheadM??1000,minForwardMps:lp.minForwardNormalMps??(isESSM?145:250),maxVelExit:deg(lp.maxVelPitchNormalDeg??(isESSM?36:50)),
        headingTol:deg(lp.headingToleranceDeg??12),pitchTol:deg(lp.pitchToleranceDeg??10),pitMinS:lp.pitMinS??.1,pitMaxS:lp.pitMaxS??2,
        seaMarginM:lp.seaMarginM??10,seaLookaheadS:lp.seaLookaheadS??.8,launchLoftPitch:0,hardRateCap:deg(lp.hardRateCapDegS??120),commitRateCap:deg(lp.commitRateCapDegS??80),hardGain:lp.hardGain??3,commitGain:lp.commitGain??2.5};
    }
function _samTrajectoryProfileFor(m){
    const id=m?._v1Profile?.loftProfileId;
    return SAM_LOFT_PROFILE_REGISTRY[id]||null;
  }
function applyGuidanceKernelV1ToLegacyRates(m,omegaYawCmd,omegaPitCmd,dt){
    m._v1TerminalActive=false;m._wip79KappaActive=false;
    const launchOverlap=!!(m._v1AllowLaunchGuidanceOverlap&&m.pitchoverPhase&&!m.vlsPhase);
    // Surface mode uses the existing point-intercept kernel, not the air-target
    // opposite-velocity terminal constraint. Select before sampling any estimator.
    const kappaRequested=(m.guidanceCore==='v1'&&!m.isESSM&&!surfaceMissileRuntimeWip13C6(m)&&(m._v1Profile?.id==='SM2MR_BLKIIIA_SIM'||m._v1Profile?.id==='SM2ER_BLKIV_SIM'||m._v1Profile?.id==='SM6_BLKIA_SIM')&&
      (m._wip79MidcourseMode==='KAPPA_V2'||m._wip79MidcourseMode==='KAPPA_V2_HD_ONLY'));
    let kappaMode=false;
    if(m.isESSM&&m.guidanceCore==='v1'&&!m.vlsPhase&&!m.pitchoverPhase&&m._loftB4&&m._loftB4.mode!=='DIRECT'&&m._loftB4.phase!=='DIVE'){
      const ts=getGuidanceTargetStateV1(m,dt);m._v1TargetState=ts;
      if(ts.isValid){const k=computeKappaMidcourseAccelV2(m,ts,dt);if(k.valid&&k.waypointB4){
        const br=applyAccelCommandToAutopilotV1(m,k,dt);
        if(br){m._wip79KappaActive=true;m._v1GuidancePhase='B4_'+m._loftB4.phase;
          return {omegaYawCmd:br.omegaYaw,omegaPitCmd:br.omegaPit};}
      }}
    }

    // WIP79 experimental branch: Kappa owns post-pitchover midcourse. At PIP tgo<=3 s,
    // latch a clean handoff to the existing terminal PNG/APN/ZEM kernel. ACC is intentionally absent.
    if(kappaRequested&&!m.vlsPhase&&!m.pitchoverPhase){
      const ts=getGuidanceTargetStateV1(m,dt);m._v1TargetState=ts;
      kappaMode=_wip79ResolveKappaEligibility(m,ts);
      if(kappaMode&&ts.isValid){
        const k=computeKappaMidcourseAccelV2(m,ts,dt);
        if(k.valid){
          if(!m._wip79KappaTerminalLatched && k.tgo<=WIP79_KAPPA_TERMINAL_TGO_S){
            m._wip79KappaTerminalLatched=true;_wip79CaptureTerminalEntry(m,ts,k);
          }
          if(!m._wip79KappaTerminalLatched){
            const br=applyAccelCommandToAutopilotV1(m,k,dt);
            if(br){omegaYawCmd=br.omegaYaw;omegaPitCmd=br.omegaPit;m._wip79KappaActive=true;m._v1GuidancePhase='KAPPA_MIDCOURSE';}
          }else{
            const phase=(ts.rangeKm<=(m._v1Profile.endgameRangeKm??3))?'ENDGAME':'TERMINAL';
            const a=computeGuidanceAccelV1(m,ts,dt,phase);m._v1GuidancePhase=a.phase;
            const br=applyAccelCommandToAutopilotV1(m,a,dt);
            if(br){omegaYawCmd=br.omegaYaw;omegaPitCmd=br.omegaPit;}
            _wip79CaptureThreeSecEntry(m,ts,k.tgo);
            m._v1TerminalActive=true;
          }
        }
      }
    }

    // LEGACY/WIP77 path, also used as fallback if Kappa state is unavailable.
    if(!kappaMode || (!m._wip79KappaActive&&!m._wip79KappaTerminalLatched)){
      m._v1TerminalActive=false;
      if(m.guidanceCore==='v1' && m._v1Profile && ((!m.vlsPhase && !m.pitchoverPhase) || launchOverlap)){
        const prof=m._v1Profile;
        if(m.isESSM) updateEssmTvcV1(m,null,dt);
        const ts=getGuidanceTargetStateV1(m,dt); m._v1TargetState=ts;
        if(ts.isValid){
          const termRange=((prof.id==='SM2MR_BLKIIIA_SIM'||prof.id==='SM2ER_BLKIV_SIM'||prof.id==='SM6_BLKIA_SIM')&&(m._fastHighInbound||m.apnTargetIsHighDiver))?Math.max(prof.terminalRangeKm,18):prof.terminalRangeKm;
          const inTerm=ts.rangeKm<=termRange, inTrans=!inTerm&&ts.rangeKm<=termRange*1.6;
          if(inTerm||inTrans){
            const a=computeGuidanceAccelV1(m,ts,dt); m._v1GuidancePhase=a.phase;
            const br=applyAccelCommandToAutopilotV1(m,a,dt);
            if(br){
              let w=1;
              if(inTrans){
                const t01=clamp((termRange*1.6-ts.rangeKm)/(termRange*0.6),0,1),ease=_samSmooth01(t01);
                w=(ts.source==='SARH_RF_EKF'||ts.source==='ARH_RF_EKF')?lerp(.10,.86,ease):(0.55*ease);
              }
              let verticalReady=1;
              if(!m.isESSM && ts.source==='SARH_RF_EKF' && m._sm2VerticalBudget){
                const currentGap=Math.max(0,(ts.posM?.z??0)-(ts.selfStateM?.posM?.z??samNavB1OwnState(m).posM.z));
                const predictedDebt=Math.max(0,m._sm2VerticalBudget.deficitM??0);
                const gap=Math.max(predictedDebt,currentGap*.78);
                verticalReady=1-_samSmooth01(clamp((gap-900)/4100,0,1));
                m._sm2SarhVerticalReady=verticalReady;m._sm2SarhCurrentGapM=currentGap;
              } else m._sm2SarhVerticalReady=1;
              if(!m.isESSM && ts.source==='SARH_RF_EKF' && m.apnTargetIsHighDiver && inTerm){
                const floor=clamp(prof.sarhVerticalPnBlendFloor??0.18,0.05,0.60),vr=clamp(verticalReady,0,1);
                const geomBlend=lerp(floor,1.0,vr);w*=geomBlend;m._sm2SarhPnBlend=geomBlend;
              }else if(!m.isESSM)m._sm2SarhPnBlend=1;
              if(launchOverlap)w*=clamp(m._v1LaunchGuidanceBlend01??0,0,.80);
              omegaYawCmd=omegaYawCmd*(1-w)+br.omegaYaw*w; omegaPitCmd=omegaPitCmd*(1-w)+br.omegaPit*w;
              m._v1TerminalActive=inTerm&&!launchOverlap&&verticalReady>.72;
              if(inTerm&&!m._v1TermLogged){m._v1TermLogged=true;debugLog(`v1 TERMINAL ${m.isESSM?'E':'M'}${m.id}: src=${ts.source} conf=${(ts.confidence*100).toFixed(0)}% N=${(a.N||0).toFixed(1)} predCPA=${(a.predictedCPA||0).toFixed(0)}m`);}
            }
          } else m._v1GuidancePhase='MIDCOURSE';
          _wip79CaptureThreeSecEntry(m,ts,null);
        } else m._v1GuidancePhase=(ts.source==='LOST')?'LOST':'MIDCOURSE';
      }
    }
    // WIP77 energy-preserving command bandwidth remains a LEGACY midcourse policy.
    // KAPPA_V2 already performs energy/trajectory shaping, so do not stack that heuristic on top.
    if(!m.isESSM&&!m._v1TerminalActive&&!m._wip79KappaActive&&(m._rangeKmCached??0)>20){
      const r=m._rangeKmCached??0; let capDeg=r>60?2.5:r>40?3:r>25?4:5; if(m._hdEnergyShelfActive) capDeg=Math.min(capDeg,3);
      const cap=deg(capDeg),om=Math.hypot(omegaYawCmd,omegaPitCmd); if(om>cap&&om>1e-9){const sc=cap/om;omegaYawCmd*=sc;omegaPitCmd*=sc;m._energyRateLimited=true;}else m._energyRateLimited=false;m._energyRateCapDeg=capDeg;
    }else m._energyRateLimited=false;
    return {omegaYawCmd,omegaPitCmd};
  }
function debugLog(){}
function updateEssmTvcV1(m, aCmd, dt){
    const prof = m._v1Profile;
    if(!prof || !prof.tvcEnabled) return;
    // WIP60: TVC is not merely a VLS alignment aid. During the powered early-burn window it remains
    // available to the intercept autopilot even after forward-commit, with q-based blending to the fins.
    const duration=Math.max(.1,window.WIP136_ESSM_TVC_TIMEOUT_S??prof.tvcDurationSec??4.0);
    const thrustActive=missileThrustN(m)>1000&&(m.life??0)<duration&&!m._wip136TvcJettisoned;
    const q=Math.max(0,m.qbar??0),qStart=m._samSixDof?.tvcQFadeStartPa??18000,qEnd=m._samSixDof?.tvcQFadeEndPa??52000;
    const qFade=1-_samSmooth01((q-qStart)/Math.max(1,qEnd-qStart));
    let auth=(thrustActive&&(m.vlsPhase||m.pitchoverPhase))?Math.max(.95,qFade):0;
    m._v1TvcActive=auth>.01;
    m._v1TvcAuthority=clamp(auth,0,1);
  }
function _wip79CaptureThreeSecEntry(m,ts,tgoOverride=null){
    if(m._wip79ThreeSecEntry||!ts?.isValid)return;
    const tgo=Number.isFinite(tgoOverride)?tgoOverride:(Number.isFinite(m._tgoIter)?m._tgoIter:null);
    if(!(Number.isFinite(tgo)&&tgo<=WIP79_KAPPA_TERMINAL_TGO_S))return;
    const vx=worldSpeedToMps(m.vx??0),vy=worldSpeedToMps(m.vy??0),vz=m.vz??0;
    const av=Number.isFinite(m.availableG)?m.availableG:null,cmd=Number.isFinite(m._v1GCommand)?m._v1GCommand:null;
    m._wip79ThreeSecEntry={
      t:m.life??0,pipTgoS:tgo,rangeKm:ts.rangeKm??m._rangeKmCached??null,
      altDiffM:Number.isFinite(ts?.posM?.z)?(m.z??0)-ts.posM.z:null,
      missileAltM:m.z??null,targetAltM:ts?.posM?.z??null,speedMps:Math.hypot(vx,vy,vz),vzMps:vz,
      availableG:av,commandG:cmd,gRatio:(av>1e-9&&cmd!=null)?cmd/av:null,
      guidancePhase:m._v1GuidancePhase??null,midcourseKernel:m._wip79MidcourseMode??'LEGACY'
    };
  }
const WIP79_KAPPA_TERMINAL_TGO_S=DATA["WIP79_KAPPA_TERMINAL_TGO_S"];
function computeGuidanceAccelV1(m, targetState, dt, phaseOverride=null){
    const prof = m._v1Profile;
    if(!prof) return { ax:0, ay:0, az:0, phase:'NONE' };
    if(!targetState.isValid){
      // No target — coast
      return { ax:0, ay:0, az:0, phase:'COAST' };
    }
    const rangeKm = targetState.rangeKm;
    const inBoost = m.life < 1.0;
    // WIP7: fast/high inbound threats have very short terminal time-to-go. Begin the
    // precision PN/APN chain earlier, while keeping the long-range energy-rate gate intact.
    const terminalRangeEff = ((prof.id === 'SM2MR_BLKIIIA_SIM'||prof.id === 'SM2ER_BLKIV_SIM'||prof.id === 'SM6_BLKIA_SIM') && (m._fastHighInbound || m.apnTargetIsHighDiver))
      ? Math.max(prof.terminalRangeKm, 18)
      : prof.terminalRangeKm;
    const inTerminal = rangeKm <= terminalRangeEff;
    const inEndgame = rangeKm <= prof.endgameRangeKm;

    let phase;
    if(phaseOverride) phase=phaseOverride;
    else if(inBoost) phase = 'BOOST';
    else if(inEndgame) phase = 'ENDGAME';
    else if(inTerminal) phase = 'TERMINAL';
    else if(rangeKm < terminalRangeEff * 1.6) phase = 'TRANSITION';
    else phase = 'MIDCOURSE';

    // Choose PN gain based on phase
    let N = prof.basePN || 4.0;
    if(phase === 'TERMINAL' || phase === 'ENDGAME'){
      N = prof.terminalPN || 4.5;
    } else if(phase === 'TRANSITION'){
      N = lerp(prof.basePN, prof.terminalPN, 0.5);
    }

    // Confidence-based gain scaling
    const confScale = clamp(targetState.confidence, 0.3, 1.0);
    N *= lerp(0.8, 1.0, confScale);

    // 1) True 3D PN
    const pn = computeTruePN3D(m, targetState, N);

    // 2) APN correction (transition+terminal)
    let apn = { ax:0, ay:0, az:0 };
    if(phase === 'TERMINAL' || phase === 'TRANSITION' || phase === 'ENDGAME'){
      apn = computeAPNCorrectionV1(m, targetState, prof, dt);
    }

    // 3) ZEM refinement (terminal+endgame only)
    let zem = { ax:0, ay:0, az:0, predictedCPA:0, predictedCPATime:0 };
    if(phase === 'TERMINAL' || phase === 'ENDGAME'){
      zem = computeZEMCorrectionV1(m, targetState, prof);
    }

    // Store for debug
    m._v1PredCPA = zem.predictedCPA;
    m._v1PredCPATime = zem.predictedCPATime;

    // Combine
    let ax = pn.ax + apn.ax + zem.ax;
    let ay = pn.ay + apn.ay + zem.ay;
    let az = pn.az + apn.az + zem.az;

    // BOOST phase: very gentle commands
    if(phase === 'BOOST'){
      ax *= 0.3; ay *= 0.3; az *= 0.3;
    } else if(phase === 'MIDCOURSE'){
      // WIP42: no local hard-coded loft acceleration here.  Launch and midcourse energy management
      // are both owned by SAM_LOFT_PROFILE_REGISTRY / registry-driven altitude guidance downstream.
    }

    return { ax, ay, az, phase, N, predictedCPA: zem.predictedCPA, predictedCPATime: zem.predictedCPATime };
  }
function computeZEMCorrectionV1(m, targetState, profile){
    // Compute predicted CPA (Zero-Effort Miss) and -ZEM direction acceleration
    if(!targetState.isValid || targetState.rangeM < 5){
      return { ax:0, ay:0, az:0, predictedCPA:0, predictedCPATime:0 };
    }
    const own=samNavB1OwnState(m);
    const mPosX=own.posM.x,mPosY=own.posM.y,mPosZ=own.posM.z;
    const mVx=own.velMps.x,mVy=own.velMps.y,mVz=own.velMps.z;
    const rx = targetState.posM.x - mPosX;
    const ry = targetState.posM.y - mPosY;
    const rz = targetState.posM.z - mPosZ;
    const rvx = targetState.velMps.x - mVx;
    const rvy = targetState.velMps.y - mVy;
    const rvz = targetState.velMps.z - mVz;
    const dotPV = rx*rvx + ry*rvy + rz*rvz;
    const dotVV = rvx*rvx + rvy*rvy + rvz*rvz;
    const tgo = dotVV > 1e-6 ? -dotPV / dotVV : 0;
    if(tgo < 0.05 || tgo > 5.0){
      return { ax:0, ay:0, az:0, predictedCPA:0, predictedCPATime:tgo };
    }
    // ZEM = future relative position at tgo
    const zx = rx + rvx * tgo;
    const zy = ry + rvy * tgo;
    const zz = rz + rvz * tgo;
    const zMag = Math.sqrt(zx*zx + zy*zy + zz*zz);
    // a_ZEM = -k * 2 * ZEM / tgo^2
    const gain = (profile.zemGain || 1.0) * clamp(targetState.confidence, 0.2, 1.0);
    const k = gain * 2 / (tgo * tgo);
    let ax=-k*zx, ay=-k*zy, az=-k*zz;
    const rawG=Math.hypot(ax,ay,az)/G0;
    // WIP57: ZEM is a refinement term, not an unbounded 1/tgo^2 actuator request.  Cap it against
    // both a profile ceiling and the current physical 6DOF authority, then approach the cap smoothly.
    const physG=Number.isFinite(m.availableG)?Math.max(1,m.availableG):(profile.maxGSeaLevel??20);
    const capG=Math.max(1.5,Math.min(profile.zemMaxG??10,physG*0.55));
    if(rawG>capG&&rawG>1e-9){const x=clamp((rawG-capG)/Math.max(.5,capG),0,1),soft=capG*(1+0.12*(1-x));const sc=soft/rawG;ax*=sc;ay*=sc;az*=sc;}
    m._v1ZemRawG=rawG;m._v1ZemCapG=capG;m._v1ZemDeliveredCmdG=Math.hypot(ax,ay,az)/G0;
    return {
      ax, ay, az,
      predictedCPA: zMag,
      predictedCPATime: tgo
    };
  }
function computeAPNCorrectionV1(m, targetState, profile, dt){
    // Need target acceleration estimate; use filtered estimate from last frames.
    // WIP42: DL_TRACK / SARH_RF_EKF / ARH_RF_EKF / IOG_MEM are independent estimators.
    // Never differentiate velocity across a guidance-source boundary: reseed the derivative history
    // and suppress APN for that single transition sample instead of manufacturing a huge fake target G.
    const source = targetState.source ?? 'UNKNOWN';
    if(!m._v1AccelEst) m._v1AccelEst = { x:0, y:0, z:0, lastVx:null, lastVy:null, lastVz:null, lastSource:null, sourceResetCount:0 };
    const ae = m._v1AccelEst;
    const sourceChanged = ae.lastSource != null && ae.lastSource !== source;
    if(sourceChanged){
      ae.x = ae.y = ae.z = 0;
      ae.lastVx = targetState.velMps.x;
      ae.lastVy = targetState.velMps.y;
      ae.lastVz = targetState.velMps.z;
      ae.lastSource = source;
      ae.sourceResetCount = (ae.sourceResetCount ?? 0) + 1;
      m._v1ApnSourceReset = `${ae.lastSource}`;
      return { ax:0, ay:0, az:0 };
    }
    m._v1ApnSourceReset = null;
    ae.lastSource = source;
    if(ae.lastVx != null){
      const sampleDt = Math.max(1e-4, dt ?? (1/60));
      const ax = (targetState.velMps.x - ae.lastVx) / sampleDt;
      const ay = (targetState.velMps.y - ae.lastVy) / sampleDt;
      const az = (targetState.velMps.z - ae.lastVz) / sampleDt;
      // Low-pass filter
      const alpha = 0.15;
      ae.x = lerp(ae.x, ax, alpha);
      ae.y = lerp(ae.y, ay, alpha);
      ae.z = lerp(ae.z, az, alpha);
    }
    ae.lastVx = targetState.velMps.x;
    ae.lastVy = targetState.velMps.y;
    ae.lastVz = targetState.velMps.z;
    // Project out LOS-parallel component
    const rangeM = targetState.rangeM;
    if(rangeM < 1) return { ax:0, ay:0, az:0 };
    const own=targetState.selfStateM??samNavB1OwnState(m),mPosX=own.posM.x,mPosY=own.posM.y,mPosZ=own.posM.z;
    const rx = targetState.posM.x - mPosX;
    const ry = targetState.posM.y - mPosY;
    const rz = targetState.posM.z - mPosZ;
    const ux = rx/rangeM, uy = ry/rangeM, uz = rz/rangeM;
    const aLosComp = ae.x*ux + ae.y*uy + ae.z*uz;
    const apnX = ae.x - aLosComp * ux;
    const apnY = ae.y - aLosComp * uy;
    const apnZ = ae.z - aLosComp * uz;
    // Gain × confidence
    const gain = (profile.apnGain || 0.5) * clamp(targetState.confidence, 0.2, 1.0);
    return { ax: apnX * gain, ay: apnY * gain, az: apnZ * gain };
  }
function computeTruePN3D(m, targetState, N){
    if(!targetState.isValid || targetState.rangeM < 1) {
      return { ax:0, ay:0, az:0 };
    }
    const own=samNavB1OwnState(m);
    const mPosX=own.posM.x,mPosY=own.posM.y,mPosZ=own.posM.z;
    const mVx=own.velMps.x,mVy=own.velMps.y,mVz=own.velMps.z;
    const tx = targetState.posM.x;
    const ty = targetState.posM.y;
    const tz = targetState.posM.z;
    const tvx = targetState.velMps.x;
    const tvy = targetState.velMps.y;
    const tvz = targetState.velMps.z;

    const rx = tx - mPosX, ry = ty - mPosY, rz = tz - mPosZ;
    const rvx = tvx - mVx, rvy = tvy - mVy, rvz = tvz - mVz;
    const rMag = Math.sqrt(rx*rx + ry*ry + rz*rz);
    if(rMag < 1) return { ax:0, ay:0, az:0 };

    // Unit r
    const ux = rx / rMag, uy = ry / rMag, uz = rz / rMag;
    // Closing speed Vc.  WIP42: fade PN authority smoothly near CPA instead of the old
    // Vc<50 m/s hard step, which produced a one-frame guidance discontinuity.
    const Vc = -(rvx*ux + rvy*uy + rvz*uz);
    if(Vc <= 0){
      m._v1PnClosingWeight = 0;
      return { ax:0, ay:0, az:0 };
    }
    const closingWeight = smoothstep((Vc - 20) / (80 - 20));
    m._v1PnClosingWeight = closingWeight;
    if(closingWeight <= 0) return { ax:0, ay:0, az:0 };
    // omega = (r × rv) / r²
    const cx = ry*rvz - rz*rvy;
    const cy = rz*rvx - rx*rvz;
    const cz = rx*rvy - ry*rvx;
    const r2 = rMag * rMag;
    const wx = cx / r2, wy = cy / r2, wz = cz / r2;
    // a_PN = N * Vc * (omega × u)
    const VcEff = Vc * closingWeight;
    const ax = N * VcEff * (wy*uz - wz*uy);
    const ay = N * VcEff * (wz*ux - wx*uz);
    const az = N * VcEff * (wx*uy - wy*ux);
    return { ax, ay, az };
  }
function _wip79CaptureTerminalEntry(m,ts,k){
    if(m._wip79KappaTerminalEntry)return;
    const vx=worldSpeedToMps(m.vx??0),vy=worldSpeedToMps(m.vy??0),vz=m.vz??0;
    m._wip79KappaTerminalEntry={
      t:m.life??0,pipTgoS:k?.tgo??null,rangeKm:ts?.rangeKm??m._rangeKmCached??null,
      altDiffM:Number.isFinite(ts?.posM?.z)?(m.z??0)-ts.posM.z:null,
      missileAltM:m.z??null,targetAltM:ts?.posM?.z??null,speedMps:Math.hypot(vx,vy,vz),vzMps:vz,
      availableG:m.availableG??null,commandG:m._v1GCommand??null,omegaR:k?.omegaR??null,K1:k?.K1??null,K2:k?.K2??null,
      // WIP83 observation-only PIP/terminal-vector state at the 3 s handoff.
      pipPredAltM:k?.pip?.z??null,kappaGammaFDeg:k?.gammaFDeg??null,kappaTgoRawS:k?.tgoRaw??null
    };
  }
function _wip79ResolveKappaEligibility(m,ts){
    const mode=String(m._wip79MidcourseMode??'LEGACY');
    if(mode==='KAPPA_V2')return true;
    if(mode!=='KAPPA_V2_HD_ONLY')return false;
    if(m._wip79KappaEligible==null)m._wip79KappaEligible=_wip79HighDiverEligibleFromEstimate(m,ts);
    return !!m._wip79KappaEligible;
  }
function _wip79HighDiverEligibleFromEstimate(m,ts){
    if(!ts?.isValid)return false;
    const z=Number(ts?.posM?.z),vz=Number(ts?.velMps?.z);
    return !!m.apnTargetIsHighDiver || (Number.isFinite(z)&&Number.isFinite(vz)&&z>=18000&&vz<=-120);
  }
function applyAccelCommandToAutopilotV1(m, aCmd, dt){
    const prof = m._v1Profile;
    if(!prof) return null;
    const own=samNavB1OwnState(m),mVx=own.velMps.x,mVy=own.velMps.y,mVz=own.velMps.z;
    const vH = Math.hypot(mVx, mVy);
    const vTot = Math.max(60, Math.hypot(vH, mVz));
    if(vH < 1) return null;
    // 1-3) 속도 평행성분 제거 → 순수 normal acceleration
    let ax = aCmd.ax, ay = aCmd.ay, az = aCmd.az;
    const ux = mVx / vTot, uy = mVy / vTot, uz = mVz / vTot;
    const aPar = ax*ux + ay*uy + az*uz;
    ax -= aPar*ux; ay -= aPar*uy; az -= aPar*uz;
    // 4-5) 가용 G clamp: profile maxG + 고도(동압 proxy) + 저속 fin authority + TVC
    const altM = own.posM.z;
    let maxG;
    // WIP73: once BODY-6DOF has a valid q/force sample, that is the physical source of truth.
    // The old altitude proxy must not remain as a hidden second ceiling.  It is fallback-only before
    // the first 6DOF authority sample (or on legacy non-6DOF missiles).
    const sixDofAuthorityReady=m.samSixDofEnabled&&m._sam6dofAuthorityReady&&Number.isFinite(m.availableG)&&m.availableG>0;
    if(sixDofAuthorityReady&&((prof.id==='SM2MR_BLKIIIA_SIM'||prof.id==='SM2ER_BLKIV_SIM'||prof.id==='SM6_BLKIA_SIM')||(m.isESSM&&window.WIP136_ESSM_G_CAP_BYPASS))){
      maxG=m.availableG;
    }else{
      const altFac = clamp(altM / 12000, 0, 1);
      maxG = lerp(prof.maxGSeaLevel ?? 30, prof.maxGHighAlt ?? 16, altFac);
      const spdFac = clamp(vTot / 350, 0.25, 1.0) * (prof.finAuthority ?? 1.0);
      const tvcAuth = m._v1TvcAuthority ?? 0;
      maxG *= Math.max(spdFac, tvcAuth * 0.9);
      if(sixDofAuthorityReady)maxG=Math.min(maxG,m.availableG); // preserve validated ESSM/legacy behavior
    }
    const aMag = Math.hypot(ax, ay, az);
    const rawDemandG=aMag/G0;
    const sm2CommandCap=_sm2CommandEnvelopeG(m,rawDemandG);
    if(Number.isFinite(sm2CommandCap))maxG=Math.min(maxG,sm2CommandCap);
    m._v1AutopilotMaxG=maxG;
    const maxA = maxG * 9.81;
    m._v1GCommand = rawDemandG;
    if(aMag > maxA && aMag > 1e-9){
      const s = maxA / aMag;
      ax *= s; ay *= s; az *= s;
      if(!m._v1Saturated) debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} autopilot SATURATED ${m._v1GCommand.toFixed(0)}G→${maxG.toFixed(0)}G`);
      m._v1Saturated = true;
    } else m._v1Saturated = false;
    m._v1GAchieved = Math.hypot(ax, ay, az) / 9.81;
    // WIP48: retain the post-clamp normal-acceleration direction for the 6DOF delivery meter.
    // Saturation above only scales magnitude, so this direction is also the raw guidance direction.
    const ctlMag=Math.hypot(ax,ay,az);
    m._v1ControlCommandVec=ctlMag>1e-9?{ux:ax/ctlMag,uy:ay/ctlMag,uz:az/ctlMag,accelMps2:ctlMag,g:m._v1GAchieved}:{ux:0,uy:0,uz:0,accelMps2:0,g:0};
    // 6-8) 분해: 수평횡 → yaw, 피치면 법선 → pitch; omega = a_n / V
    const hx = mVx / Math.max(1, vH), hy = mVy / Math.max(1, vH);
    const aLat = ax * (-hy) + ay * (hx);
    const aAlongH = ax * hx + ay * hy;
    const pAng = Math.atan2(mVz, Math.max(1, vH));
    const aVert = az * Math.cos(pAng) - aAlongH * Math.sin(pAng);
    let omegaYaw = aLat / vTot;
    let omegaPit = aVert / vTot;
    // 9) rate limit (각가속 한계/lag는 하류 기존 자동조종이 추가 적용)
    const maxRate = deg(m.isESSM ? 60 : 42);  // SIM_TUNED
    omegaYaw = clamp(omegaYaw, -maxRate, maxRate);
    omegaPit = clamp(omegaPit, -maxRate, maxRate);
    // §12 time-to-sea soft guard: 임박 시 '하강 pitch만' 감쇠 (상승/수평/측방 자유)
    m._v1SoftGuard = false;
    if(altM < 40 && mVz < -5){
      const tts = altM / Math.max(1, -mVz);
      if(tts < 0.5 && omegaPit < 0){
        omegaPit *= clamp(tts / 0.5, 0.15, 1.0);
        m._v1SoftGuard = true;
      }
    }
    // 10) 기록
    return { omegaYaw, omegaPit, gCommand: m._v1GCommand, gAchieved: m._v1GAchieved, saturated: m._v1Saturated };
  }
function computeKappaMidcourseAccelV2(m,targetState,dt){
    const azObs=_wip86UpdateKappaAzEstimate(m,targetState,dt);
    const st=_wip79KappaPipState(m,targetState);
    if(!st)return {valid:false,ax:0,ay:0,az:0,tgo:null};
    const om=_wip79KappaOmegaPerM(m),g=_wip79KappaGainsFromX(om.omega*st.rgoM),t=Math.max(.08,st.controlTgoS??st.tgo);
    const pex=st.pip.x-st.mPos.x-st.mVel.x*t;
    const pey=st.pip.y-st.mPos.y-st.mVel.y*t;
    const pez=st.pip.z-st.mPos.z-st.mVel.z*t;
    const vex=st.vFinal.x-st.mVel.x,vey=st.vFinal.y-st.mVel.y,vez=st.vFinal.z-st.mVel.z;
    // Modern Missile Guidance general form: proportional PIP term minus K2 * terminal-velocity error.
    // K2 is negative in the small-x limit, so this sign drives gamma toward gamma_f.
    const kp=g.K1/(t*t),kv=(-g.K2)/t;
    const rawAx=kp*pex+kv*vex,rawAy=kp*pey+kv*vey,rawAz=kp*pez+kv*vez;
    // Kappa's aerodynamic command is normal acceleration (ADD paper: n_vκ), not commanded axial thrust.
    // The vector form can contain a component parallel to missile velocity; fins cannot realize that component.
    // Remove it BEFORE G saturation so a fictitious axial demand cannot steal real normal-force authority.
    const invV=1/Math.max(1e-9,st.speed),vhx=st.mVel.x*invV,vhy=st.mVel.y*invV,vhz=st.mVel.z*invV;
    const axial=rawAx*vhx+rawAy*vhy+rawAz*vhz;
    const ax=rawAx-axial*vhx,ay=rawAy-axial*vhy,az=rawAz-axial*vhz;
    const rawVectorG=Math.hypot(rawAx,rawAy,rawAz)/G0,rawG=Math.hypot(ax,ay,az)/G0;
    const dbg={valid:true,ax,ay,az,tgo:st.tgo,controlHorizonS:st.controlTgoS??null,waypointB4:!!st.waypointB4,targetPip:st.targetPip??null,tgoRaw:st.tgoRaw,tgoCapS:Number.isFinite(Number(window.WIP81_KAPPA_TGO_CAP_S))?Number(window.WIP81_KAPPA_TGO_CAP_S):null,rgoM:st.rgoM,pip:st.pip,vFinal:st.vFinal,gammaFDeg:rad2deg(st.gammaF),policy:st.policy,
      K1:g.K1,K2:g.K2,omega:om.omega,omegaR:g.x,series:g.series,rawG,rawVectorG,discardedAxialMps2:axial,
      azEstMps2:azObs?.estMps2??0,azRawMps2:azObs?.rawMps2??null,azFilteredMps2:azObs?.filteredMps2??null,azTauS:azObs?.tauS??null,azClamped:!!azObs?.clamped,azSourceReset:!!azObs?.sourceReset,
      posErrM:{x:pex,y:pey,z:pez},velErrMps:{x:vex,y:vey,z:vez},qPa:om.q};
    m._wip79Kappa=dbg;
    // WIP81 diagnostic-only gain envelope. Never consumed by guidance.
    const gs=m._wip81KappaStats??(m._wip81KappaStats={samples:0,omegaRMin:Infinity,omegaRMax:-Infinity,K1Min:Infinity,K1Max:-Infinity,K2Min:Infinity,K2Max:-Infinity,nonFinite:0,signFault:0,tgoRawMaxS:0,tgoUsedMaxS:0,
      // WIP83 observation-only envelopes: never consumed by guidance.
      gammaFMinDeg:Infinity,gammaFMaxDeg:-Infinity,pipAltMinM:Infinity,pipAltMaxM:-Infinity});
    gs.samples++;
    if(Number.isFinite(g.x)&&Number.isFinite(g.K1)&&Number.isFinite(g.K2)){
      gs.omegaRMin=Math.min(gs.omegaRMin,g.x);gs.omegaRMax=Math.max(gs.omegaRMax,g.x);
      gs.K1Min=Math.min(gs.K1Min,g.K1);gs.K1Max=Math.max(gs.K1Max,g.K1);
      gs.K2Min=Math.min(gs.K2Min,g.K2);gs.K2Max=Math.max(gs.K2Max,g.K2);
      if(!(g.K1>0&&g.K2<0))gs.signFault++;
    }else gs.nonFinite++;
    if(Number.isFinite(st.tgoRaw))gs.tgoRawMaxS=Math.max(gs.tgoRawMaxS,st.tgoRaw);
    if(Number.isFinite(t))gs.tgoUsedMaxS=Math.max(gs.tgoUsedMaxS,t);
    const _gfd=rad2deg(st.gammaF),_paz=st.pip?.z;
    if(Number.isFinite(_gfd)){gs.gammaFMinDeg=Math.min(gs.gammaFMinDeg,_gfd);gs.gammaFMaxDeg=Math.max(gs.gammaFMaxDeg,_gfd);}
    if(Number.isFinite(_paz)){gs.pipAltMinM=Math.min(gs.pipAltMinM,_paz);gs.pipAltMaxM=Math.max(gs.pipAltMaxM,_paz);}
    return dbg;
  }
function _wip79KappaGainsFromX(xIn){
    const x=clamp(Math.abs(Number(xIn)||0),0,50);
    if(x<0.05){
      const x2=x*x,x4=x2*x2,x6=x4*x2;
      return {K1:6 + x2/10 - x4/1400 + x6/126000,
              K2:-2 + x2/30 - 13*x4/12600 + 11*x6/378000,
              x,series:true};
    }
    const sh=Math.sinh(x),ch=Math.cosh(x);
    const den=x*sh-2*(ch-1);
    if(!Number.isFinite(den)||Math.abs(den)<1e-12)return {K1:6,K2:-2,x,series:true,fallback:true};
    const K1=x*x*(ch-1)/den;
    const K2=(x*x-x*sh)/den;
    if(!Number.isFinite(K1)||!Number.isFinite(K2))return {K1:6,K2:-2,x,series:true,fallback:true};
    return {K1,K2,x,series:false};
  }
function _wip79KappaOmegaPerM(m){
    const own=samNavB1OwnState(m),vx=own.velMps.x,vy=own.velMps.y,vz=own.velMps.z;
    const V=Math.max(80,Math.hypot(vx,vy,vz));
    const alt=own.posM.z,rho=airDensityKgM3(alt),q=Math.max(0,m.qbar??(.5*rho*V*V));
    const mach=V/Math.max(1,speedOfSoundMps(alt));
    const Aref=Math.max(1e-5,m.arefM2??m._v1Profile?.refAreaM2??MISSILE_AREF_M2);
    const Slift=Math.max(1e-5,m.liftRefM2??m._v1Profile?.aero?.liftRefM2??MISSILE_LIFTREF_M2);
    const cla=Math.max(.1,m._samSixDof?.normalForceAlpha??missileCLalphaMach(mach));
    const cd0=Math.max(.02,samParasiticCdV14A5(m,mach));
    const Lalpha=q*Slift*cla, D0=q*Aref*cd0;
    if(!(Lalpha>1e-6)||!(D0>0))return {omega:0,omega2:0,q,Lalpha,D0,cla,cd0,V};
    const T=Math.max(0,missileThrustN(m)),mass=Math.max(1,m.massKg??MISSILE_MASS_KG);
    const tau=T/Lalpha;
    const den=mass*mass*Math.pow(V,4)*Math.max(.05,2*cla+tau);
    const omega2=den>0 ? D0*Lalpha*Math.pow(tau+1,2)/den : 0;
    return {omega:Math.sqrt(Math.max(0,omega2)),omega2:Math.max(0,omega2),q,Lalpha,D0,cla,cd0,V,T,mass,tau};
  }
const MISSILE_MASS_KG=DATA["MISSILE_MASS_KG"];
function samParasiticCdV14A5(m,mach){
    const id=m?._v1Profile?.id;
    if(m?.isSM6)return wip14a6Sm6Cd(m,mach);
    if(m?.isSM2ER)return wip14a5Sm2ErCd(m,mach);
    if(m?.isESSM||id==='ESSM_BLK2_SIM')return wip14a7AeroCd('ESSM_254',mach);
    if(id==='SM2MR_BLKIIIA_SIM')return wip14a7AeroCd('STANDARD_UPPER_343',mach);
    return missileCdMach(mach);
  }
function missileCdMach(mach){return wip14a7AeroCd('GENERIC',mach);}
function wip14a7AeroCd(curveId,mach){
    const c=WIP14A7_AERO_CURVES[curveId]??WIP14A7_AERO_CURVES.GENERIC,m=Math.max(0,Number(mach)||0),last=c.points[c.points.length-1];
    return m<=last[0]?interp1Table(c.points,m):last[1]+(m-last[0])*c.postTableSlopePerMach;
  }
function interp1Table(table, x){
    if(!table || table.length === 0) return x;
    if(x <= table[0][0]) return table[0][1];
    for(let i=1;i<table.length;i++){
      const x0 = table[i-1][0], y0 = table[i-1][1];
      const x1 = table[i][0],   y1 = table[i][1];
      if(x <= x1){
        const t = (x - x0) / Math.max(1e-9, (x1 - x0));
        return y0 + (y1 - y0) * t;
      }
    }
    return table[table.length-1][1];
  }
const WIP14A7_AERO_CURVES=DATA["WIP14A7_AERO_CURVES"];
function wip14a5Sm2ErCd(m,mach){
    const table=m?.boosterSeparated?WIP14A5_SM2ER_CD.upper:WIP14A5_SM2ER_CD.attached;
    return wip14a7AeroCd(m?.boosterSeparated?'STANDARD_UPPER_343':'STANDARD_BOOSTED_532',mach);
  }
const WIP14A5_SM2ER_CD=DATA["WIP14A5_SM2ER_CD"];
function wip14a6Sm6Cd(m,mach){return wip14a7AeroCd(m?.boosterSeparated?'STANDARD_UPPER_343':'STANDARD_BOOSTED_532',mach);}
function missileCLalphaMach(mach){
    // Lift curve slope per rad (CNα/CLα). Values tuned for missile-like authority (ref area ~ cross-section).
    // Drops in transonic, recovers in supersonic. Higher than simple airfoil CLα to avoid artificial 3G ceiling.
    if(mach < 0.70) return 11.0;
    if(mach < 0.95) return lerp(11.0, 8.2, (mach - 0.70) / 0.25);
    if(mach < 1.20) return lerp(8.2, 7.2, (mach - 0.95) / 0.25);
    if(mach < 2.50) return lerp(7.2, 9.2, (mach - 1.20) / 1.30);
    return 9.2;
  }
const MISSILE_LIFTREF_M2=DATA["MISSILE_LIFTREF_M2"];
const MISSILE_AREF_M2=DATA["MISSILE_AREF_M2"];
function _wip79KappaPipState(m,targetState){
    if(!targetState?.isValid)return null;
    const own=targetState.selfStateM??samNavB1OwnState(m),mPos=_samB1VecCopy(own.posM),mVel=_samB1VecCopy(own.velMps);
    const fallbackRaw=targetState.rangeM/Math.max(200,Math.hypot(mVel.x-targetState.velMps.x,mVel.y-targetState.velMps.y,mVel.z-targetState.velMps.z));
    const baseTgoRaw=Number.isFinite(m._wip81KappaTgoRawS)?m._wip81KappaTgoRawS:(Number.isFinite(m._tgoIter)?m._tgoIter:fallbackRaw);
    const tgoRaw=weaponLinkB3AdvisedTgo(m,targetState,baseTgoRaw);
    const tgo=_wip81KappaTgoLimit(tgoRaw);
    const _w86az=Number(m._wip86KappaAzEst?.estMps2)||0;
    const pip={x:targetState.posM.x+targetState.velMps.x*tgo,
               y:targetState.posM.y+targetState.velMps.y*tgo,
               // WIP86: observation-derived vertical acceleration only. Clamp to a physical prediction envelope.
               z:clamp(targetState.posM.z+targetState.velMps.z*tgo+.5*_w86az*tgo*tgo,0,60000)};
    const dx=pip.x-mPos.x,dy=pip.y-mPos.y,dz=pip.z-mPos.z,rgoM=Math.max(1,Math.hypot(dx,dy,dz));
    const speed=Math.max(80,Math.hypot(mVel.x,mVel.y,mVel.z));
    // Game terminal-vector heading follows the observed/estimated PIP LOS.
    // Do not automatically reverse a retreating/crossing target's heading.
    let hx=dx,hy=dy;
    let hm=Math.max(1,Math.hypot(hx,hy));
    hx/=hm;hy/=hm;
    let gammaF=0;
    const policy=String(m._wip79KappaTerminalPolicy??window.WIP79_KAPPA_TERMINAL_POLICY??'PIP_LOS');
    if(policy==='PIP_LOS')gammaF=Math.atan2(dz,Math.max(1,Math.hypot(dx,dy)));
    else if(policy==='TARGET_GAMMA_OPPOSE_H'){
      gammaF=Math.atan2(-targetState.velMps.z,Math.max(1,Math.hypot(targetState.velMps.x,targetState.velMps.y)));
    }
    gammaF=clamp(gammaF,deg(-60),deg(60));
    const c=Math.cos(gammaF);
    const vFinal={x:speed*c*hx,y:speed*c*hy,z:speed*Math.sin(gammaF)};
    return loftB4ShapeWaypoint(m,targetState,{tgo,tgoRaw,mPos,mVel,pip,rgoM,speed,vFinal,gammaF,policy});
  }
function loftB4ShapeWaypoint(m,ts,base){
    const s=m._loftB4,p=loftB4Profile(m);
    if(!s||!p||s.mode==='DIRECT'||s.phase==='DIVE'||m.vlsPhase||m.pitchoverPhase||!ts?.isValid)return base;
    const own=ts.selfStateM??missileNavB2OwnState(m),a=own.posM,v=own.velMps;
    const dx=base.pip.x-a.x,dy=base.pip.y-a.y,h=Math.hypot(dx,dy),speed=Math.max(80,Math.hypot(v.x,v.y,v.z));
    if(!(h>1)||!Number.isFinite(h))return base;
    // A local game-path waypoint, not a new sensor contact or a modification to the target track.
    const forward=Math.min(h*.7,Math.max(1500,speed*p.horizonS));
    const dz=clamp(s.shelfM-a.z,-forward*Math.tan(deg(p.pitchDeg)),forward*Math.tan(deg(p.pitchDeg)));
    const gamma=Math.atan2(dz,Math.max(1,forward)),c=Math.cos(gamma),ux=dx/h,uy=dy/h;
    const pip={x:a.x+forward*ux,y:a.y+forward*uy,z:a.z+dz};
    const controlTgoS=Math.max(2,Math.hypot(forward,dz)/speed);
    s.lastWaypoint={...pip};s.controlHorizonS=controlTgoS;
    return {...base,targetPip:{...base.pip},pip,rgoM:Math.hypot(forward,dz),
      vFinal:{x:speed*c*ux,y:speed*c*uy,z:speed*Math.sin(gamma)},gammaF:gamma,
      controlTgoS,waypointB4:true,policy:'B4_'+s.phase};
  }
function loftB4Profile(m){return SAM_LOFT_B4_PROFILES[m?._v1Profile?.loftProfileId]??null;}
const SAM_LOFT_B4_PROFILES=DATA["SAM_LOFT_B4_PROFILES"];
function _wip81KappaTgoLimit(rawS){
    const raw=Math.max(.08,Number(rawS)||.08);
    const cap=Number(window.WIP81_KAPPA_TGO_CAP_S);
    return Number.isFinite(cap) ? clamp(raw,.08,Math.max(.08,cap)) : raw;
  }
function weaponLinkB3AdvisedTgo(m,targetState,base){
    const r=m?._weaponLinkB3;if(!r)return base;
    const terminalKm=Number(m._v1Profile?.terminalRangeKm)||0;
    const phase=(targetState.rangeKm<=terminalKm*1.6||m.life<1)?'TERMINAL':String(m._v1GuidancePhase??'MIDCOURSE');
    const result=WEAPON_LINK_B3.advisedTgo(r,base,weaponLinkB3Now(m),{phase,source:targetState.source,
      seekerAcknowledged:['SARH_RF_EKF','ARH_RF_EKF'].includes(targetState.source)});
    m._b3AssistanceApplied=result;return result.value;
  }
function weaponLinkB3Now(m){
    const r=m?._weaponLinkB3;
    return r?r.plan.launchStep+Math.max(0,Math.round((Number(m.life)||0)/SIM_FIXED_DT)):simStepCounter;
  }
const WEAPON_LINK_B3=DATA["WEAPON_LINK_B3"];
function _wip86UpdateKappaAzEstimate(m,targetState,dt){
    const vz=Number(targetState?.velMps?.z),source=String(targetState?.source??'UNKNOWN');
    if(!Number.isFinite(vz))return {estMps2:0,rawMps2:null,filteredMps2:0,tauS:Number(window.WIP86_KAPPA_AZ_TAU_S)||3,source,sourceReset:false,clamped:false};
    const tau=clamp(Number(window.WIP86_KAPPA_AZ_TAU_S)||3,.25,30);
    const sampleDt=Math.max(1e-4,Number(dt)||(1/60));
    let st=m._wip86KappaAzEst;
    const sourceChanged=!!st&&st.lastSource!=null&&st.lastSource!==source;
    if(!st||st.lastVz==null||sourceChanged){
      st=m._wip86KappaAzEst={lastVz:vz,lastSource:source,estMps2:0,rawMps2:0,filteredMps2:0,tauS:tau,sourceResetCount:(st?.sourceResetCount??0)+(sourceChanged?1:0),sourceReset:sourceChanged,clamped:false,samples:0,minEstMps2:Infinity,maxEstMps2:-Infinity,minRawMps2:Infinity,maxRawMps2:-Infinity};
      return {estMps2:0,rawMps2:0,filteredMps2:0,tauS:tau,source,sourceReset:sourceChanged,clamped:false};
    }
    const raw=(vz-st.lastVz)/sampleDt;
    const alpha=1-Math.exp(-sampleDt/tau);
    const filtered=st.estMps2+alpha*(raw-st.estMps2);
    const est=clamp(filtered,-2*G0,3*G0);
    st.lastVz=vz;st.lastSource=source;st.rawMps2=raw;st.filteredMps2=filtered;st.estMps2=est;st.tauS=tau;st.sourceReset=false;st.clamped=Math.abs(est-filtered)>1e-9;st.samples=(st.samples??0)+1;
    if(Number.isFinite(est)){st.minEstMps2=Math.min(st.minEstMps2,est);st.maxEstMps2=Math.max(st.maxEstMps2,est);}
    if(Number.isFinite(raw)){st.minRawMps2=Math.min(st.minRawMps2,raw);st.maxRawMps2=Math.max(st.maxRawMps2,raw);}
    return {estMps2:est,rawMps2:raw,filteredMps2:filtered,tauS:tau,source,sourceReset:false,clamped:st.clamped};
  }
function getGuidanceTargetStateV1(m, dt){
    const prof = m._v1Profile;
    if(!prof){ return { isValid:false, source:'LOST', confidence:0 }; }

    // B3: local received packet / own seeker / IOG only. Transmitter lives in the fixed tick.
    const tr = samB1GuidanceCueTrack(m);

    // Source priority
    let sarhSt = null, arhSt = null, dlSt = null, memSt = null;

    if(prof.seekerType === 'SARH' || prof.seekerType === 'DUAL_MODE_ARH_SARH'){
      sarhSt = m._wip75DeterministicRf ? _wip75DeterministicSarhState(m,tr) : getSarhTargetStateV1(m, tr, dt);
      sarhSt = samNavB1ReanchorRelativeCandidate(m,sarhSt);
    }
    if(prof.seekerType === 'DUAL_MODE_ARH_SARH'){
      updateArhSeekerV1(m, tr, dt);
      arhSt = samNavB1ReanchorRelativeCandidate(m,getArhTargetStateV1(m, dt));
    }
    // Receiver getter cannot query a live launcher track.
    dlSt = getDlTargetStateV1(m, null, dt);
    // Memory state (from last good fix)
    memSt = getMemTargetStateV1(m, dt);

    // WIP43: stable source arbitration. Do not let independent EKFs chatter across a single
    // confidence threshold; keep estimator states separate and switch only through hysteresis/dwell.
    const chosen = _v1SelectGuidanceSource(
      m,
      [arhSt,sarhSt,dlSt,memSt].filter(Boolean),
      prof,
      dt
    );

    if(!chosen){
      m._v1GuidanceAuthority='LOST';
      if(!m.isESSM&&!m.isSM6) m.state='IOG'; // legacy SM-2 compatibility mirror only.
      return { isValid:false, source:'LOST', confidence:0 };
    }
    m._v1GuidanceAuthority=chosen.source;
    // SM-2 compatibility state is now a mirror of the actual arbiter-selected estimator; resource
    // allocators never write it for v1.  ESSM keeps ACTIVE as an onboard-seeker hardware-state flag.
    if(!m.isESSM&&!m.isSM6){
      if(chosen.source==='SARH_RF_EKF') m.state='SARH';
      else if(chosen.source==='DL_TRACK') m.state='DL';
      else m.state='IOG';
    }

    // Update memory with an actual chosen fix (only for SARH/ARH/DL — not MEM itself).
    // A short arbiter-held propagated sample is intentionally not allowed to refresh memory age.
    const b3MemoryKey=chosen.source==='DL_TRACK'?`${m._weaponLinkB3?.epoch}:${m._weaponLinkB3?.uplink.rxSeq}`:null;
    if(chosen.source !== 'IOG_MEM' && !chosen._arbHeld && (chosen.source!=='DL_TRACK'||b3MemoryKey!==m._b3MemSequence)){
      if(b3MemoryKey)m._b3MemSequence=b3MemoryKey;
      m._v1Mem = {
        posM: { x: chosen.posM.x, y: chosen.posM.y, z: chosen.posM.z },
        velMps: { x: chosen.velMps.x, y: chosen.velMps.y, z: chosen.velMps.z },
        ts: m.life
      };
    }

    const aim=surfaceMissileAimStateWip13C7(m,chosen);
    // Compute derived
    const own=samNavB1OwnState(m);
    const mPosX=own.posM.x,mPosY=own.posM.y,mPosZ=own.posM.z;
    const mVx=own.velMps.x,mVy=own.velMps.y,mVz=own.velMps.z;

    const rx = aim.posM.x - mPosX;
    const ry = aim.posM.y - mPosY;
    const rz = aim.posM.z - mPosZ;
    const rangeM = Math.sqrt(rx*rx + ry*ry + rz*rz);
    const rangeKm = rangeM / 1000;
    // WIP61: receiver TRACK is not synonymous with terminal guidance.  Assert the legacy compatibility
    // flag only after the arbiter actually selected robust SARH and the engagement reached transition geometry.
    if(!m.isESSM&&!m.isSM6){
      const baseTerm=prof.terminalRangeKm??11;
      const termEff=(m._fastHighInbound||m.apnTargetIsHighDiver)?Math.max(baseTerm,18):baseTerm;
      m.terminalSARH=(chosen.source==='SARH_RF_EKF' && rangeKm<=termEff*1.6);
    }

    const rvx = aim.velMps.x - mVx;
    const rvy = aim.velMps.y - mVy;
    const rvz = aim.velMps.z - mVz;

    // Closing speed: -dot(rv, unit_r)
    const ur = rangeM > 1 ? [rx/rangeM, ry/rangeM, rz/rangeM] : [0,0,0];
    const closingMps = -(rvx*ur[0] + rvy*ur[1] + rvz*ur[2]);

    return {
      isValid: true,
      source: chosen.source,
      confidence: chosen.confidence,
      posM: aim.posM,
      measurementPosM: aim.measurementPosM,
      aimPolicy: aim.aimPolicy,
      velMps: aim.velMps,
      accMps2: aim.accMps2 || { x:0, y:0, z:0 },
      rangeM,
      rangeKm,
      closingMps,
      latencySec: chosen.latencySec || 0,
      noiseSigmaM: chosen.noiseSigmaM || 0,
      qualityNotes: chosen.qualityNotes || '',
      selfStateM: own,
      sourceArbiter: m._v1SourceArb ? {
        current: m._v1SourceArb.current,
        sourceAgeS: m._v1SourceArb.sourceAgeS ?? 0,
        candidate: m._v1SourceArb.candidate,
        candidateAgeS: m._v1SourceArb.candidateAgeS ?? 0,
        belowHoldAgeS: m._v1SourceArb.belowHoldAgeS ?? 0,
        switchCount: m._v1SourceArb.switchCount ?? 0,
        lastSwitchReason: m._v1SourceArb.lastSwitchReason ?? ''
      } : null
    };
  }
function surfaceMissileAimStateWip13C7(m, measured){
  const runtime=surfaceMissileRuntimeWip13C6(m);
  if(!runtime||!measured?.isValid||!measured.posM||!measured.velMps)return measured;
  const referenceM=Number(runtime.aimHeightM);
  if(!Number.isFinite(referenceM))return measured;
  const g=surfaceMissileGlideAimWip15C(m,measured.posM,referenceM);
  return {...measured,
    measurementPosM:{...measured.posM},
    posM:{...measured.posM,z:g.aimM},
    velMps:{...measured.velMps,z:0},accMps2:{...(measured.accMps2??{x:0,y:0}),z:0},
    aimPolicy:g.glide?'WIP15C_SURFACE_TERMINAL_GLIDE':'C4_OBSERVED_SURFACE_REFERENCE',surfaceGlide:g.glide,truthUsed:false};
}
function surfaceMissileGlideAimWip15C(m,targetPosM,referenceM){
  let aimM=Math.max(surfaceMissileGuidanceFloorWip13C6(m),referenceM),glide=null;
  const key=surfaceMissileVariantKeyWip15C(m),cfg=SURFACE_STANDARD_GLIDE_WIP15C[key];
  if(cfg?.enabled&&m._loftB4?.mode!=='DIRECT'&&m._loftB4?.phase==='DIVE'&&targetPosM){
    const own=missileNavB2OwnState(m),dx=Number(targetPosM.x)-Number(own?.posM?.x),dy=Number(targetPosM.y)-Number(own?.posM?.y),horizM=Math.hypot(dx,dy);
    if(Number.isFinite(horizM)){const horizKm=horizM/1000,u=clamp(horizKm/Math.max(.1,cfg.terminalFadeKm),0,1),fade=u*u*(3-2*u),extra=Math.min(cfg.maxExtraM,horizM*Math.tan(deg(cfg.glideDeg)))*fade;aimM=Math.max(aimM,referenceM+Math.max(0,extra));glide={weaponKey:key,horizKm,extraM:extra,glideDeg:cfg.glideDeg,fade};}
  }
  return {aimM,glide};
}
const SURFACE_STANDARD_GLIDE_WIP15C=DATA["SURFACE_STANDARD_GLIDE_WIP15C"];
function surfaceMissileVariantKeyWip15C(value){
  if(value&&typeof value==='object'){if(value.isESSM)return 'ESSM';if(value.isSM6||value._v1Profile?.id==='SM6_BLKIA_SIM'||String(value.weaponType??'').toUpperCase()==='SM6')return 'SM6';if(value.isSM2ER||value._v1Profile?.id==='SM2ER_BLKIV_SIM'||String(value.weaponType??'').toUpperCase()==='SM2ER')return 'SM2ER';}
  const q=String(value?.weaponKey??value?.weaponType??value??'').toUpperCase().replace(/[^A-Z0-9]/g,'');if(q.includes('ESSM'))return 'ESSM';if(q.includes('SM6'))return 'SM6';if(q.includes('SM2ER')||q.includes('RIM156'))return 'SM2ER';if(q.includes('SM2'))return 'SM2';return q||'UNKNOWN';
}
function surfaceMissileGuidanceFloorWip13C6(m){
  const runtime=surfaceMissileRuntimeWip13C6(m);if(!runtime)return 30;
  const p=m._surfaceArh?SURFACE_ARH_LIVE_PROFILE_V48_WIP13C6.guidance:SURFACE_SARH_LIVE_PROFILE_V48_WIP13C5.guidance;
  const r=Number(m._v1TargetState?.rangeKm??m._rangeKmCached),term=Number(m._v1Profile?.terminalRangeKm)||(m.isESSM?10:11);
  return Number.isFinite(r)&&r<=term*1.65?p.terminalFloorM:p.seaClearanceMidcourseM;
}
const SURFACE_SARH_LIVE_PROFILE_V48_WIP13C5=DATA["SURFACE_SARH_LIVE_PROFILE_V48_WIP13C5"];
const SURFACE_ARH_LIVE_PROFILE_V48_WIP13C6=DATA["SURFACE_ARH_LIVE_PROFILE_V48_WIP13C6"];
function surfaceMissileRuntimeWip13C6(m){return m?._surfaceSarh??m?._surfaceArh??null;}
function _v1SelectGuidanceSource(m, candidates, prof, dt){
    const cfg = _v1SourceArbiterConfig(prof);
    const step = clamp(Number.isFinite(dt) ? dt : 0, 0, 0.25);
    const nowLife = Number.isFinite(m?.life) ? m.life : 0;
    const bySource = new Map();
    for(const st of (candidates||[])) if(st?.source) bySource.set(st.source, st);

    let arb = m._v1SourceArb;
    if(!arb || arb.profileKey !== prof?.seekerType){
      arb = m._v1SourceArb = {
        profileKey: prof?.seekerType ?? 'SARH',
        current:null, sourceAgeS:0,
        candidate:null, candidateAgeS:0,
        belowHoldAgeS:0,
        switchCount:0,
        lastSwitchFrom:'NONE', lastSwitchTo:'NONE', lastSwitchReason:'INIT',
        lastGoodState:null, lastGoodLife:nowLife
      };
    }
    arb.sourceAgeS = (arb.sourceAgeS ?? 0) + step;

    const priority = cfg.priority;
    const priIndex = (src) => {
      const j = priority.indexOf(src);
      return j < 0 ? 999 : j;
    };
    const bestAcquire = (filterFn=null) => {
      for(const src of priority){
        if(filterFn && !filterFn(src)) continue;
        const st = bySource.get(src), rule = cfg.source[src];
        if(_v1SourceMeets(st,rule,'acquire')) return st;
      }
      return null;
    };

    // Initial acquisition: no handoff discontinuity exists yet, so take the highest valid source immediately.
    if(!arb.current){
      const first = bestAcquire();
      if(!first) return null;
      _v1CommitSourceSwitch(arb, first.source, 'INITIAL_ACQUIRE', nowLife);
      arb.lastGoodState = _v1CloneGuidanceCandidate(first);
      arb.lastGoodLife = nowLife;
      const out = _v1CloneGuidanceCandidate(first);
      out.qualityNotes = `${out.qualityNotes||''} ARB=INIT`.trim();
      return out;
    }

    const currentSt = bySource.get(arb.current) ?? null;
    const currentRule = cfg.source[arb.current];
    const currentMeetsHold = _v1SourceMeets(currentSt,currentRule,'hold');

    if(currentSt?.isValid){
      // Preserve the newest actual estimate even if it is temporarily below the hold threshold.
      arb.lastGoodState = _v1CloneGuidanceCandidate(currentSt);
      arb.lastGoodLife = nowLife;
    }

    if(currentMeetsHold) arb.belowHoldAgeS = 0;
    else arb.belowHoldAgeS = (arb.belowHoldAgeS ?? 0) + step;

    // Promotion is considered only for sources above the current source in the priority chain.
    const currentIdx = priIndex(arb.current);
    const promotion = bestAcquire(src => priIndex(src) < currentIdx);
    if(promotion){
      if(arb.candidate === promotion.source) arb.candidateAgeS = (arb.candidateAgeS ?? 0) + step;
      else { arb.candidate = promotion.source; arb.candidateAgeS = step; }
      const dwell = cfg.source[promotion.source]?.promoteDwellS ?? 0;
      if(arb.candidateAgeS + 1e-9 >= dwell){
        _v1CommitSourceSwitch(arb,promotion.source,`${promotion.source}_PROMOTION`,nowLife);
        arb.lastGoodState = _v1CloneGuidanceCandidate(promotion);
        arb.lastGoodLife = nowLife;
        const out = _v1CloneGuidanceCandidate(promotion);
        out.qualityNotes = `${out.qualityNotes||''} ARB=PROMOTE`.trim();
        return out;
      }
    } else {
      arb.candidate = null;
      arb.candidateAgeS = 0;
    }

    // Keep the current estimator while it satisfies the lower hold threshold.
    if(currentMeetsHold){
      const out = _v1CloneGuidanceCandidate(currentSt);
      out.qualityNotes = `${out.qualityNotes||''} ARB=HOLD`.trim();
      return out;
    }

    // Short debounce: a one/few-frame confidence dip or invalid sample must not force a handoff.
    const grace = currentRule?.dropoutGraceS ?? 0;
    if((arb.belowHoldAgeS ?? 0) + 1e-9 < grace){
      if(currentSt?.isValid){
        const out = _v1CloneGuidanceCandidate(currentSt);
        out.qualityNotes = `${out.qualityNotes||''} ARB=DEBOUNCE`.trim();
        return out;
      }
      const held = _v1HeldSourceState(arb,nowLife);
      if(held) return held;
    }

    // Current source genuinely degraded: fall back immediately to the best source that currently
    // satisfies its acquire threshold. A higher source that survived this long may also be used;
    // at this point maintaining guidance continuity is more important than promotion dwell.
    const fallback = bestAcquire(src => src !== arb.current);
    if(fallback){
      const oldSource = arb.current;
      _v1CommitSourceSwitch(arb,fallback.source,`${oldSource??'NONE'}_DROP_FALLBACK`,nowLife);
      arb.lastGoodState = _v1CloneGuidanceCandidate(fallback);
      arb.lastGoodLife = nowLife;
      const out = _v1CloneGuidanceCandidate(fallback);
      out.qualityNotes = `${out.qualityNotes||''} ARB=FALLBACK`.trim();
      return out;
    }

    _v1CommitSourceSwitch(arb,null,'NO_VALID_SOURCE',nowLife);
    return null;
  }
function _v1HeldSourceState(arb, nowLife){
    const last = arb?.lastGoodState;
    if(!last || !last.posM || !last.velMps) return null;
    const age = Math.max(0, (Number.isFinite(nowLife) ? nowLife : 0) - (arb.lastGoodLife ?? 0));
    const held = _v1CloneGuidanceCandidate(last);
    held.posM.x += held.velMps.x * age;
    held.posM.y += held.velMps.y * age;
    held.posM.z += held.velMps.z * age;
    held.confidence = clamp((held.confidence ?? 0) * Math.exp(-age / 0.20), 0, 1);
    held.noiseSigmaM = (held.noiseSigmaM ?? 0) + 60 * age;
    held._arbHeld = true;
    held.qualityNotes = `${held.qualityNotes||''} ARB_HOLD=${age.toFixed(3)}s`.trim();
    return held;
  }
function _v1CloneGuidanceCandidate(st){
    if(!st) return null;
    return {
      ...st,
      posM: st.posM ? {x:st.posM.x,y:st.posM.y,z:st.posM.z} : undefined,
      velMps: st.velMps ? {x:st.velMps.x,y:st.velMps.y,z:st.velMps.z} : undefined,
      accMps2: st.accMps2 ? {x:st.accMps2.x,y:st.accMps2.y,z:st.accMps2.z} : {x:0,y:0,z:0}
    };
  }
function _v1CommitSourceSwitch(arb, nextSource, reason, nowLife){
    if(arb.current !== nextSource){
      arb.switchCount = (arb.switchCount ?? 0) + (arb.current ? 1 : 0);
      arb.lastSwitchFrom = arb.current ?? 'NONE';
      arb.lastSwitchTo = nextSource ?? 'LOST';
      arb.lastSwitchReason = reason;
      arb.lastSwitchLife = nowLife;
    }
    arb.current = nextSource ?? null;
    arb.sourceAgeS = 0;
    arb.candidate = null;
    arb.candidateAgeS = 0;
    arb.belowHoldAgeS = 0;
  }
function _v1SourceMeets(st, rule, mode){
    if(!st || !st.isValid || !rule) return false;
    // WIP61: an estimator being numerically alive is not enough to seize guidance authority.
    // SARH acquisition requires a fresh, consecutive-hit TRACK with enough RF evidence; short
    // COAST/REACQUIRE intervals may HOLD authority so one missed dwell cannot bounce DL<->SARH.
    if(mode === 'acquire' && st.canAcquireAuthority === false) return false;
    if(mode === 'hold' && st.canHoldAuthority === false) return false;
    const c = Number.isFinite(st.confidence) ? st.confidence : 0;
    return c >= (mode === 'hold' ? rule.hold : rule.acquire);
  }
function _v1SourceArbiterConfig(prof){
    return prof?.seekerType === 'DUAL_MODE_ARH_SARH'
      ? GUIDANCE_SOURCE_ARBITER_V1.DUAL_MODE_ARH_SARH
      : GUIDANCE_SOURCE_ARBITER_V1.SARH;
  }
const GUIDANCE_SOURCE_ARBITER_V1=DATA["GUIDANCE_SOURCE_ARBITER_V1"];
function getMemTargetStateV1(m, dt){
    if(!m._v1Mem) return { isValid:false, source:'IOG_MEM', confidence:0 };
    const memAge = m.life - m._v1Mem.ts;
    if(memAge > 4){ return { isValid:false, source:'IOG_MEM', confidence:0 }; }
    // Propagate position by velocity
    const px = m._v1Mem.posM.x + m._v1Mem.velMps.x * memAge;
    const py = m._v1Mem.posM.y + m._v1Mem.velMps.y * memAge;
    const pz = m._v1Mem.posM.z + m._v1Mem.velMps.z * memAge;
    // Confidence decays with age
    const conf = clamp(0.4 - memAge * 0.08, 0.05, 0.4);
    return {
      isValid: true,
      source: 'IOG_MEM',
      confidence: conf,
      posM: { x:px, y:py, z:pz },
      velMps: m._v1Mem.velMps,
      accMps2: { x:0, y:0, z:0 },
      latencySec: 0.0,
      noiseSigmaM: 50 + memAge * 30,
      qualityNotes: `MEM age=${memAge.toFixed(1)}s`
    };
  }
function getDlTargetStateV1(){return idealState('DL_TRACK');}
function getArhTargetStateV1(){return idealState('ARH_RF_EKF');}
function updateArhSeekerV1(m){m._v1ArhState='TRACK';m.essmActiveSeeker=true;}
function samNavB1ReanchorRelativeCandidate(m,st){
    if(!st?.isValid||!['SARH_RF_EKF','ARH_RF_EKF'].includes(st.source)||!st.posM||!st.velMps)return st;
    const truth=_samB1TruthOwnState(m),own=samNavB1OwnState(m),dp={x:own.posM.x-truth.posM.x,y:own.posM.y-truth.posM.y,z:own.posM.z-truth.posM.z},dv={x:own.velMps.x-truth.velMps.x,y:own.velMps.y-truth.velMps.y,z:own.velMps.z-truth.velMps.z};
    return {...st,posM:{x:st.posM.x+dp.x,y:st.posM.y+dp.y,z:st.posM.z+dp.z},velMps:{x:st.velMps.x+dv.x,y:st.velMps.y+dv.y,z:st.velMps.z+dv.z},relativeReanchoredB1:true,qualityNotes:`${st.qualityNotes||''} NAV_REANCHOR_B1`.trim()};
  }
function getSarhTargetStateV1(){return idealState('SARH_RF_EKF');}
function _wip75DeterministicSarhState(m,tr){
    if(!m?._wip75DeterministicRf) return null;
    const tgt=_v1FindTarget(m);
    const illReady=(m._illuminatorId!=null)&&(m.sarhAlive!==false);
    if(!tgt||!illReady){
      return {isValid:false,source:'SARH_RF_EKF',confidence:0,canAcquireAuthority:false,canHoldAuthority:false};
    }
    return {
      isValid:true,source:'SARH_RF_EKF',confidence:1,
      posM:{x:worldToMeters(tgt.x),y:worldToMeters(tgt.y),z:tgt.z??0},
      velMps:{x:worldSpeedToMps(tgt.vx??0),y:worldSpeedToMps(tgt.vy??0),z:tgt.vz??0},
      accMps2:{x:0,y:0,z:0},latencySec:0,noiseSigmaM:0,
      canAcquireAuthority:true,canHoldAuthority:true,
      qualityNotes:'WIP75 deterministic RF surrogate'
    };
  }
function _v1FindTarget(m){
    const id = m.assignedTargetId;
    if(id == null) return null;
    return truthObjectForTrackV27(id,true);
  }
function samB1GuidanceCueTrack(){return tracks.get(1);}
const ownY=0;
const ownX=0;
function preSlewSeekerToBearing(m, dt, bearing){
  if(m.seekerAngle == null) m.seekerAngle = m.heading;
  const slew = (m.seekerSlewRate ?? deg(120)); // rad/s
  const maxStep = slew * dt;
  const err = angNorm(bearing - m.seekerAngle);
  m.seekerAngle = angNorm(m.seekerAngle + clamp(err, -maxStep, maxStep));
  // keep within gimbal about missile boresight
  const gLim = (m.gimbalMax ?? deg(60));
  const gErr = angNorm(m.seekerAngle - m.heading);
  m.seekerAngle = angNorm(m.heading + clamp(gErr, -gLim, gLim));
}
const MACH1_MPS=DATA["MACH1_MPS"];
function seekerAcquire(m, dt){
    const ax = m.x, ay = m.y;
    const isIR = (m.seekerType === 'IR');

    let gErr = angNorm(m.seekerAngle - m.heading);
    gErr = clamp(gErr, -m.gimbalMax, m.gimbalMax);
    m.seekerAngle = angNorm(m.heading + gErr);

    const candidates = [];

    let gateCenterAngle = m.seekerAngle;
    let searchGate = m.seekerFov * m.fovGateLoose;
    let lockGate = m.seekerFov * m.fovLockLoose;
    let irccmAnchor = { valid:false, type:null, id:null, angle:m.seekerAngle };

    if(isIR){
      m.irccmGateTimer = Math.max(0, (m.irccmGateTimer ?? 0) - dt);
      irccmAnchor = getIrccmAnchor(m, ax, ay);

      const canGate = !!(m.irccmGatewidthEnabled && irccmAnchor.valid);
      const wideGate = m.seekerFov * m.fovGateLoose;
      const narrowScale = clamp(m.irccmNarrowScale ?? 0.28, 0.12, 0.65);
      const narrowSearchGate = Math.max(deg(1.2), wideGate * narrowScale);
      const narrowLockGate = Math.max(deg(0.8), (m.seekerFov * m.fovLockLoose) * narrowScale);

      if(canGate){
        gateCenterAngle = irccmAnchor.angle;
        let sawOffAxisFlare = false;

        for(const f of flares){
          const dKm = dist3Km(ax,ay,(m.z ?? OWN_ALT_M), f.x,f.y,(f.z ?? OWN_ALT_M));
          if(dKm > m.seekerRangeKm) continue;

          const a = Math.atan2(f.y - ay, f.x - ax);
          const relToSeeker = Math.abs(angNorm(a - m.seekerAngle));
          if(relToSeeker > wideGate) continue;

          const relToAnchor = Math.abs(angNorm(a - gateCenterAngle));
          if(relToAnchor > narrowSearchGate){
            sawOffAxisFlare = true;
            break;
          }
        }

        if(sawOffAxisFlare){
          m.irccmGateTimer = Math.max(m.irccmGateTimer ?? 0, m.irccmGateDuration ?? 0.90);
        }

        if((m.irccmGateTimer ?? 0) > 0){
          searchGate = narrowSearchGate;
          lockGate = narrowLockGate;
        } else {
          gateCenterAngle = m.seekerAngle;
        }
      }
    }

    const scoreCenterAngle = gateCenterAngle;

    for(const t of targetPool){
      if(!t.alive) continue;
      if(terrainLineOfSightFactor(ax,ay,m.z??OWN_ALT_M,t.x,t.y,t.z??0)<=0) continue;
      const tTrackId=trackIdForTruthV27('AIR',t.id,false);if(tTrackId==null)continue;
      if(m.dlAlive && m.assignedTargetId != null && tTrackId !== m.assignedTargetId) continue;

      const dKm = dist3Km(ax,ay,(m.z ?? OWN_ALT_M), t.x,t.y,t.z);

      // IR seeker: effective range depends on target aspect (rear=far, front=close)
      let effRange = m.seekerRangeKm;
      let irSig = 0.5;
      if(isIR){
        irSig = irSignature(t, ax, ay);
        effRange = irSeekerEffectiveRange(m.seekerMaxRangeKm, irSig);
      }
      if(dKm > effRange) continue;

      const a = Math.atan2(t.y - ay, t.x - ax);
      const rel = Math.abs(angNorm(a - scoreCenterAngle));
      if(rel > searchGate) continue;

      let score;
      if(isIR){
        // IR scoring
        const distScore = 1.0 - (dKm / effRange);
        const angScore  = 1.0 - (rel / Math.max(searchGate, deg(0.5)));
        const trackBias = (tTrackId === m.seekerLockId || tTrackId === m.assignedTargetId) ? 0.18 : 0.0;
        score = distScore*0.36 + angScore*0.30 + irSig*0.34 + trackBias;
      } else {
        // ARH scoring: PD-MTI with range/doppler/angle gates
        const vr = closingSpeedKmh3(ax,ay,m.vx,m.vy,(m.z??OWN_ALT_M),(m.vz??0), t.x,t.y,t.vx,t.vy,t.z,(t.vz??0));
        const nf = notchFactor(Math.abs(vr));
        const distScore = 1.0 - (dKm / m.seekerRangeKm);
        const angScore  = 1.0 - (rel / Math.max(searchGate, deg(0.5)));

        // Range gate: prefer targets near predicted range from DL/IOG command
        let rangeGateScore = 1.0;
        if(m.lastCmdX != null){
          const predDist = dist3Km(ax,ay,(m.z??0), m.lastCmdX,m.lastCmdY,(m.lastCmdZ??5000));
          const rangeErr = Math.abs(dKm - predDist);
          rangeGateScore = clamp(1.0 - rangeErr / 8.0, 0.15, 1.0); // ±8km window
        }

        // Track memory bias: strongly prefer already-tracked target
        const trackBias = (tTrackId === m.seekerLockId) ? 0.25 :
                          (tTrackId === m.assignedTargetId) ? 0.15 : 0.0;

        // Doppler discrimination: |Vc| provides velocity gate confidence
        const absVr = Math.abs(vr);
        const dopplerConf = clamp(absVr / 600, 0.1, 1.0);

        // Altitude-based clutter model
        let clutterPenalty = 1.0;
        if(t.z < 100) clutterPenalty = 0.35;
        else if(t.z < 500) clutterPenalty = 0.60;
        else if(t.z < 2000) clutterPenalty = 0.85;
        else if(t.z > 5000) clutterPenalty = 1.15; // clear sky: excellent detection
        // PD-MTI recovery
        clutterPenalty = clamp(clutterPenalty + 0.30 * dopplerConf, 0, 1.0);
        // Look-down geometry bonus: missile above target → cleaner PD returns
        const altAdv = ((m.z ?? 0) - t.z);
        if(altAdv > 500){
          const lookDownBonus = clamp(altAdv / 3000, 0, 0.45);
          clutterPenalty = clamp(clutterPenalty + lookDownBonus, 0, 1.0);
        }

        score = (distScore*0.30 + angScore*0.25 + rangeGateScore*0.25 + dopplerConf*0.20)
                * clutterPenalty + trackBias;
        score *= (1.0 - 0.50*nf);
      }

      candidates.push({ type:'TGT', id:tTrackId, x:t.x, y:t.y, z:t.z, vx:t.vx, vy:t.vy, vz:(t.vz??0), score, nf:0, irSig });
    }

    // Enemy missile candidates (ARH seeker can detect ASMs)
    if(!isIR){
      for(const em of enemyMissiles){
        if(!em.alive) continue;
        if(terrainLineOfSightFactor(ax,ay,m.z??OWN_ALT_M,em.x,em.y,em.z??0)<=0) continue;
        // Only if this missile is assigned to an ASM track OR no specific target
        const emTrackId = trackIdForTruthV27('ASM',em.id,false);
        if(m.assignedTargetId != null && m.assignedTargetId !== emTrackId) continue;

        const dKm = dist3Km(ax,ay,(m.z ?? OWN_ALT_M), em.x,em.y,em.z);
        if(dKm > m.seekerRangeKm) continue;

        const a = Math.atan2(em.y - ay, em.x - ax);
        const rel = Math.abs(angNorm(a - scoreCenterAngle));
        if(rel > searchGate) continue;

        const vr = closingSpeedKmh3(ax,ay,m.vx,m.vy,(m.z??OWN_ALT_M),(m.vz??0), em.x,em.y,em.vx,em.vy,em.z,(em.vz??0));
        const nf = notchFactor(Math.abs(vr));
        const distScore = 1.0 - (dKm / m.seekerRangeKm);
        const angScore  = 1.0 - (rel / Math.max(searchGate, deg(0.5)));
        const absVr = Math.abs(vr);
        const dopplerConf = clamp(absVr / 600, 0.1, 1.0);
        const trackBias = (emTrackId === m.seekerLockId) ? 0.25 : (emTrackId === m.assignedTargetId) ? 0.20 : 0.0;

        // ASMs have small RCS but high closing speed → strong doppler return
        let clutterPen = 1.0;
        if(em.z < 100) clutterPen = 0.45;
        else if(em.z < 500) clutterPen = 0.70;
        const altAdv = ((m.z ?? 0) - em.z);
        if(altAdv > 300) clutterPen = clamp(clutterPen + clamp(altAdv/2000, 0, 0.4), 0, 1);
        clutterPen = clamp(clutterPen + 0.35 * dopplerConf, 0, 1);

        let score = (distScore*0.30 + angScore*0.25 + dopplerConf*0.25 + 0.20) * clutterPen + trackBias;
        score *= (1.0 - 0.45*nf);
        if(score > 0.001) candidates.push({ type:'TGT', id: emTrackId, x:em.x, y:em.y, z:em.z, vx:em.vx, vy:em.vy, vz:(em.vz??0), score, nf:0, irSig:0 });
      }
    }

    // Chaff candidates (ARH only — IR completely ignores chaff)
    if(!isIR){
      for(const c of chaffs){
        if(terrainLineOfSightFactor(ax,ay,m.z??OWN_ALT_M,c.x,c.y,c.z??OWN_ALT_M)<=0) continue;
        const dKm = dist3Km(ax,ay,(m.z ?? OWN_ALT_M), c.x,c.y,(c.z ?? OWN_ALT_M));
        if(dKm > m.seekerRangeKm) continue;
        const a = Math.atan2(c.y - ay, c.x - ax);
        const rel = Math.abs(angNorm(a - scoreCenterAngle));
        if(rel > searchGate) continue;
        const distScore = 1.0 - (dKm / m.seekerRangeKm);
        const angScore  = 1.0 - (rel / Math.max(searchGate, deg(0.5)));
        let score = (distScore*0.45 + angScore*0.55) * c.strength;
        score *= (1.0 - (m.chaffResistance ?? 0.65));
        if(score > 0.001) candidates.push({ type:'CHAFF', id:c.id, x:c.x, y:c.y, z:(c.z ?? OWN_ALT_M), score, nf:0 });
      }
    }

    // Flare candidates (IR only — ARH completely ignores flares)
    if(isIR){
      for(const f of flares){
        if(terrainLineOfSightFactor(ax,ay,m.z??OWN_ALT_M,f.x,f.y,f.z??OWN_ALT_M)<=0) continue;
        const dKm = dist3Km(ax,ay,(m.z ?? OWN_ALT_M), f.x,f.y,(f.z ?? OWN_ALT_M));
        if(dKm > m.seekerRangeKm) continue;
        const a = Math.atan2(f.y - ay, f.x - ax);
        const rel = Math.abs(angNorm(a - scoreCenterAngle));
        if(rel > searchGate) continue;
        const distScore = 1.0 - (dKm / m.seekerRangeKm);
        const angScore  = 1.0 - (rel / Math.max(searchGate, deg(0.5)));
        const freshness = 1.0 - clamp(f.life / f.maxLife, 0, 1);
        let score = (distScore*0.3 + angScore*0.3 + freshness*0.4) * f.strength;
        score *= (1.0 - (m.flareResistance ?? 0.25));
        if((m.irccmGateTimer ?? 0) > 0 && irccmAnchor.valid) score *= 0.18;
        if(score > 0.001) candidates.push({ type:'FLARE', id:f.id, x:f.x, y:f.y, z:(f.z ?? OWN_ALT_M), score, nf:0 });
      }
    }

    if(candidates.length === 0){
      m.seekerLockedPrev = m.seekerLocked;
      m.seekerLocked = false;
      m.seekerLockId = null;
      m.seekerLockType = null;
      return null;
    }

    candidates.sort((a,b)=> b.score - a.score);
    const best = candidates[0];

    const bestRel = Math.abs(angNorm(Math.atan2(best.y-ay, best.x-ax) - scoreCenterAngle));
    let lockOk = (bestRel <= lockGate);

    if(best.type === 'TGT' && !isIR){
      // ARH notch loss
      const nf = best.nf;
      const pKeep = 1.0 - m.seekerNotchLossBasePerSec * nf * dt;
      if(simRandom() > pKeep) lockOk = false;
    }

    if(lockOk){
      m.seekerLockedPrev = m.seekerLocked;
      m.seekerLocked = true;
      m.seekerLockType = best.type;
      m.seekerLockId = best.id;

      const aT = Math.atan2(best.y - ay, best.x - ax);
      const err = angNorm(aT - m.seekerAngle);
      const maxStep = m.seekerSlewRate * dt;
      m.seekerAngle = angNorm(m.seekerAngle + clamp(err, -maxStep, maxStep));
      if(isIR && best.type === 'TGT'){
        m.irccmLastTargetAngle = aT;
        m.irccmLastTargetId = best.id;
      }
      m.seekerNoTargetTimer = 0;
      m.seekerCoastTimer = 0;  // reset coast
      return best;
    }

    m.seekerLockedPrev = m.seekerLocked;
    m.seekerLocked = false;
    m.seekerLockId = null;
    m.seekerLockType = null;
    return null;
  }
const chaffs=[];
function notchFactor(absVrKmh){
    // 0이면 완전 안전(노치 없음), 1이면 완전 노치에 가까움
    const x = clamp((NOTCH_KMH - absVrKmh) / NOTCH_KMH, 0, 1);
    return x*x*(3 - 2*x); // smoothstep
  }
const NOTCH_KMH=DATA["NOTCH_KMH"];
function closingSpeedKmh3(observerX, observerY, observerVx, observerVy, observerZ, observerVz,
                            tgtX, tgtY, tgtVx, tgtVy, tgtZ, tgtVz){
    const L = losUnit3(observerX, observerY, observerZ, tgtX, tgtY, tgtZ);
    if(L.rKm < 1e-6) return 0;
    const relVx_mps = worldSpeedToMps(tgtVx - observerVx);
    const relVy_mps = worldSpeedToMps(tgtVy - observerVy);
    const relVz_mps = (tgtVz ?? 0) - (observerVz ?? 0);
    const vr_mps = relVx_mps*L.ux + relVy_mps*L.uy + relVz_mps*L.uz; // +면 벌어짐
    const closing_mps = -vr_mps;
    return mpsToKmh(closing_mps);
  }
const mpsToKmh = (mps) => mps * 3.6;
function losUnit3(ax,ay,az_m, bx,by,bz_m){
    const dx = bx-ax, dy = by-ay;
    const rh = Math.hypot(dx,dy);
    const rhKm = worldToKm(rh);
    const dzKm = mToKm((bz_m ?? az_m) - az_m);
    const rKm = Math.hypot(rhKm, dzKm);
    if(rKm < 1e-6) return {ux:0, uy:0, uz:0, rKm:0};
    const ux = (rh>1e-6) ? (dx/rh) : 0;
    const uy = (rh>1e-6) ? (dy/rh) : 0;
    const uz = dzKm / rKm;
    return {ux, uy, uz, rKm};
  }
const mToKm = (m)=> m/1000;
function irSeekerEffectiveRange(baseRangeKm, irSig){
    // Hot rear: full range. Cold front: ~25% range
    return baseRangeKm * (0.25 + 0.75 * irSig);
  }
function irSignature(target, observerX, observerY){
    const toObsAng = Math.atan2(observerY - target.y, observerX - target.x);
    const aspect = Math.abs(angNorm(toObsAng - target.heading)); // 0=tail, π=head-on
    const a01 = aspect / Math.PI; // 0=tail..1=head-on
    // Rear is hot (engine), front is cold
    // tail(0): 1.0, beam(0.5): 0.5, head-on(1.0): 0.15
    if(a01 < 0.5) return 1.0 - 0.5 * (a01 * 2.0);
    return 0.5 - 0.35 * ((a01 - 0.5) * 2.0);
  }
function terrainLineOfSightFactor(obsX,obsY,obsAltM,tgtX,tgtY,tgtAltM){
    if(BATTLESPACE_DIAG_BYPASS||terrainIslands.length===0)return 1;
    const segDx=tgtX-obsX,segDy=tgtY-obsY,segLen=Math.hypot(segDx,segDy);if(segLen<1e-9)return 1;
    for(const island of terrainIslands){
      if(pointSegmentDistance(island.cx,island.cy,obsX,obsY,tgtX,tgtY)>island.boundRadiusWorld)continue;
      const ts=[];const poly=island.points;
      if(pointInTerrainPolygon(obsX,obsY,poly))ts.push(0);
      if(pointInTerrainPolygon(tgtX,tgtY,poly))ts.push(1);
      for(let i=0;i<poly.length;i++){
        const a=poly[i],b=poly[(i+1)%poly.length],t=_segmentEdgeT(obsX,obsY,tgtX,tgtY,a.x,a.y,b.x,b.y);
        if(t!=null)ts.push(t);
      }
      ts.sort((a,b)=>a-b);const uniq=[];for(const t of ts){if(!uniq.length||Math.abs(t-uniq[uniq.length-1])>1e-6)uniq.push(t);}
      if(uniq.length===0)continue;
      const bounds=[0,...uniq,1];
      for(let k=0;k<bounds.length-1;k++){
        const t0=bounds[k],t1=bounds[k+1];
        if(t1-t0<1e-7)continue;
        const tm=(t0+t1)*0.5;
        const mx=obsX+segDx*tm,my=obsY+segDy*tm;
        if(!pointInTerrainPolygon(mx,my,poly))continue;
        const intervalMeters=worldToMeters(segLen*Math.max(0,t1-t0));
        const samples=Math.max(1,Math.min(20,Math.ceil(intervalMeters/500)));
        for(let j=0;j<samples;j++){
          const tj=t0 + (t1-t0)*((j+0.5)/samples);
          const sx=obsX+segDx*tj, sy=obsY+segDy*tj;
          const rayAlt=lerp(obsAltM??0,tgtAltM??0,tj);
          const terrAlt=terrainElevationInsideIsland(island,sx,sy);
          if(rayAlt <= terrAlt + 8) return 0;
        }
      }
    }
    return 1;
  }
function terrainElevationInsideIsland(island,x,y){
    const prof=ensureTerrainReliefProfile(island),raw=terrainRawReliefV2(island,prof,x,y),h=Math.max(0,Number(island.heightM)||0);
    return clamp(h*(raw/Math.max(.05,prof.rawMax)),0,h);
  }
function terrainRawReliefV2(island,prof,x,y){
    const bound=Math.max(1,island.boundRadiusWorld||1),dx=x-island.cx,dy=y-island.cy,d=Math.hypot(dx,dy),edgeDist=distanceToTerrainEdge(x,y,island);
    const coastT=clamp(edgeDist/Math.max(1,bound*prof.coastRiseFrac),0,1),coastSmooth=coastT*coastT*(3-2*coastT),coastEnv=Math.pow(coastSmooth,prof.coastPower);
    if(coastEnv<=1e-8)return 0;
    let raw=prof.baseLevel*(.42+.58*clamp(1-d/bound,0,1));
    for(const m of prof.massifs){const md=Math.hypot(x-m.x,y-m.y);raw+=m.amp*Math.exp(-.5*Math.pow(md/Math.max(1,m.width),2));}
    for(const r of prof.ridges){const rd=pointSegmentDistance(x,y,r.ax,r.ay,r.bx,r.by);raw+=r.amp*Math.exp(-.5*Math.pow(rd/Math.max(1,r.width),2));}
    for(const pk of prof.peaks){const pd=Math.hypot(x-pk.x,y-pk.y);raw+=pk.amp*Math.exp(-.5*Math.pow(pd/Math.max(1,pk.width),2));}
    for(const v of prof.valleys){const vd=pointSegmentDistance(x,y,v.ax,v.ay,v.bx,v.by);raw-=v.amp*Math.exp(-.5*Math.pow(vd/Math.max(1,v.width),2));}
    raw=Math.max(0,raw);
    const nx=dx/bound,ny=dy/bound,n=terrainFbm2D(prof.noiseSeed,nx*prof.noiseFreq,ny*prof.noiseFreq,prof.noiseOctaves);
    raw*=clamp(1+prof.noiseAmp*((n-.5)*2),.58,1.42);
    return Math.max(0,raw*coastEnv);
  }
function terrainFbm2D(seed,x,y,octaves=3){
    let amp=.58,freq=1,sum=0,norm=0;
    for(let i=0;i<octaves;i++){sum+=terrainValueNoise2D((seed+i*0x6d2b79f5)>>>0,x*freq,y*freq)*amp;norm+=amp;amp*=.5;freq*=2.03;}
    return norm>0?sum/norm:.5;
  }
function terrainValueNoise2D(seed,x,y){
    const x0=Math.floor(x),y0=Math.floor(y),tx=x-x0,ty=y-y0,fx=terrainNoiseFade(tx),fy=terrainNoiseFade(ty);
    const a=terrainHash2D01(seed,x0,y0),b=terrainHash2D01(seed,x0+1,y0),c=terrainHash2D01(seed,x0,y0+1),d=terrainHash2D01(seed,x0+1,y0+1);
    return lerp(lerp(a,b,fx),lerp(c,d,fx),fy);
  }
function terrainHash2D01(seed,ix,iy){
    const a=terrainMix32((Number(seed)>>>0)^Math.imul((ix|0),0x1f123bb5)^Math.imul((iy|0),0x5f356495));
    return a/4294967295;
  }
function terrainMix32(x){
    x=(Number(x)>>>0)+0x9e3779b9; x^=x>>>16; x=Math.imul(x,0x85ebca6b); x^=x>>>13; x=Math.imul(x,0xc2b2ae35); x^=x>>>16; return x>>>0;
  }
function terrainNoiseFade(t){t=clamp(t,0,1);return t*t*t*(t*(t*6-15)+10);}
function pointSegmentDistance(x,y,ax,ay,bx,by){
    const dx=bx-ax,dy=by-ay,l2=dx*dx+dy*dy;
    if(l2<1e-12)return Math.hypot(x-ax,y-ay);
    const t=clamp(((x-ax)*dx+(y-ay)*dy)/l2,0,1),px=ax+t*dx,py=ay+t*dy;return Math.hypot(x-px,y-py);
  }
function distanceToTerrainEdge(x,y,island){
    let best=Infinity;const poly=island.points;
    for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];best=Math.min(best,pointSegmentDistance(x,y,a.x,a.y,b.x,b.y));}
    return best;
  }
function ensureTerrainReliefProfile(island){
    if(island._reliefProfile) return island._reliefProfile;
    const h=Math.max(1,island.heightM||1),kind=island.kind||'ISLAND',bound=Math.max(1,island.boundRadiusWorld||1);
    const seed=(Number(island.terrainSeed)>>>0)||terrainHashStringU32(`${BATTLESPACE_SEED}|${island.id}|${Math.round(island.cx)}|${Math.round(island.cy)}|${h}`),rnd=terrainSeededRandom(seed^0x1867a11d);
    const type=String(island.geomorphType||terrainPickGeomorph(kind,h,rnd)),axis=Number.isFinite(Number(island.longAxisRad))?Number(island.longAxisRad):rnd()*TAU;
    const ux=Math.cos(axis),uy=Math.sin(axis),px=-uy,py=ux,major=kind==='MAJOR_LANDMASS';
    const massifs=[],ridges=[],valleys=[],peaks=[];
    const point=(t,off=0)=>({x:island.cx+ux*bound*t+px*bound*off,y:island.cy+uy*bound*t+py*bound*off});
    const fitPoint=(p)=>{if(pointInTerrainPolygon(p.x,p.y,island.points))return {x:p.x,y:p.y};let lo={x:island.cx,y:island.cy},hi={x:p.x,y:p.y};for(let k=0;k<14;k++){const m={x:(lo.x+hi.x)*.5,y:(lo.y+hi.y)*.5};if(pointInTerrainPolygon(m.x,m.y,island.points))lo=m;else hi=m;}return lo;};
    const addRidge=(a,b,widthFrac,amp)=>{a=fitPoint(a);b=fitPoint(b);ridges.push({ax:a.x,ay:a.y,bx:b.x,by:b.y,width:bound*widthFrac,amp});};
    const addValley=(a,b,widthFrac,amp)=>{a=fitPoint(a);b=fitPoint(b);valleys.push({ax:a.x,ay:a.y,bx:b.x,by:b.y,width:bound*widthFrac,amp});};
    const addPeak=(p,widthFrac,amp)=>{p=fitPoint(p);peaks.push({x:p.x,y:p.y,width:bound*widthFrac,amp});};
    const addMassif=(p,widthFrac,amp)=>{p=fitPoint(p);massifs.push({x:p.x,y:p.y,width:bound*widthFrac,amp});};
    let baseLevel=.05,coastRiseFrac=.16,coastPower=1.0,noiseAmp=.10,noiseFreq=2.4,noiseOctaves=3;

    if(type==='VOLCANIC'){
      const c=point((rnd()-.5)*.12,(rnd()-.5)*.12);baseLevel=.035;coastRiseFrac=.075+rnd()*.045;coastPower=.58+rnd()*.18;noiseAmp=.07;noiseFreq=2.7;
      addMassif(c,.34+rnd()*.08,.34);addPeak(c,.13+rnd()*.045,1.02);
      const spokes=5+Math.floor(rnd()*3),phase=rnd()*TAU;
      for(let i=0;i<spokes;i++){
        const a=phase+TAU*i/spokes+(rnd()-.5)*.16,inner={x:c.x+Math.cos(a)*bound*.06,y:c.y+Math.sin(a)*bound*.06},outer={x:c.x+Math.cos(a)*bound*(.48+rnd()*.14),y:c.y+Math.sin(a)*bound*(.48+rnd()*.14)};
        addRidge(inner,outer,.030+rnd()*.020,.12+rnd()*.08);
        const va=a+Math.PI/spokes,vi={x:c.x+Math.cos(va)*bound*.16,y:c.y+Math.sin(va)*bound*.16},vo={x:c.x+Math.cos(va)*bound*(.46+rnd()*.10),y:c.y+Math.sin(va)*bound*(.46+rnd()*.10)};addValley(vi,vo,.025+rnd()*.015,.045+rnd()*.045);
      }
    }else if(type==='RIDGE'||type==='MOUNTAIN_CHAIN'||type==='COASTAL_HIGHLANDS'){
      const chain=type==='MOUNTAIN_CHAIN',coastal=type==='COASTAL_HIGHLANDS';baseLevel=chain ? .035 : .045;coastRiseFrac=coastal ? .12 : (chain ? .11 : .14)+rnd()*.05;coastPower=.88+rnd()*.22;noiseAmp=chain ? .13 : .11;noiseFreq=chain?3.0:2.6;
      const count=chain?6:4,pts=[];const coastalOff=coastal?((rnd()<.5?-1:1)*(.12+rnd()*.10)):0;
      for(let i=0;i<count;i++){const t=lerp(chain?-.72:-.58,chain ? .72 : .58,i/(count-1)),bend=(rnd()-.5)*(chain ? .16 : .12)+coastalOff;pts.push(point(t,bend));}
      for(let i=0;i<pts.length-1;i++)addRidge(pts[i],pts[i+1],chain ? .040 : .052,(chain ? .48 : .40)+rnd()*.12);
      for(let i=1;i<pts.length-1;i++)addPeak(pts[i],(chain ? .070 : .095)+rnd()*.035,(chain ? .58 : .50)+rnd()*.30);
      if(chain){addPeak(pts[0],.085,.44+rnd()*.18);addPeak(pts.at(-1),.085,.44+rnd()*.18);}
      addMassif(point(0,coastalOff*.55),chain ? .46 : .40,chain ? .12 : .16);
      const branches=chain?(5+Math.floor(rnd()*4)):(3+Math.floor(rnd()*3));
      for(let i=0;i<branches;i++){
        const src=pts[1+Math.floor(rnd()*Math.max(1,pts.length-2))],side=rnd()<.5?-1:1,ang=axis+side*((.62+rnd()*.55)),len=bound*((chain ? .24 : .20)+rnd()*(chain ? .22 : .17));
        const dst={x:src.x+Math.cos(ang)*len,y:src.y+Math.sin(ang)*len};addRidge(src,dst,(chain ? .026 : .033)+rnd()*.018,(chain ? .14 : .12)+rnd()*.13);
      }
      const valleyCount=chain?4:3;
      for(let i=0;i<valleyCount;i++){const off=(i%2?1:-1)*(.12+rnd()*.10),a=point(-.46+rnd()*.18,off),b=point(.32+rnd()*.20,off+(rnd()-.5)*.08);addValley(a,b,.035+rnd()*.025,.08+rnd()*.10);}
      if(coastal){const lowSide=-Math.sign(coastalOff||1),a=point(-.45,lowSide*.22),b=point(.48,lowSide*.28);addValley(a,b,.055,.13+rnd()*.08);}
    }else if(type==='ERODED_HIGHLAND'||type==='ERODED_MASSIF'){
      const massif=type==='ERODED_MASSIF';baseLevel=massif ? .08 : .07;coastRiseFrac=(massif ? .18 : .20)+rnd()*.08;coastPower=1.05+rnd()*.22;noiseAmp=massif ? .17 : .15;noiseFreq=3.1;noiseOctaves=3;
      addMassif(point((rnd()-.5)*.10,(rnd()-.5)*.10),massif ? .52 : .46,massif ? .30 : .27);
      if(massif)addMassif(point((rnd()-.5)*.35,(rnd()-.5)*.25),.34+rnd()*.10,.18+rnd()*.10);
      const pc=massif?(5+Math.floor(rnd()*3)):(3+Math.floor(rnd()*3));
      for(let i=0;i<pc;i++){const pp=point((rnd()-.5)*(massif?1.05:.78),(rnd()-.5)*(massif ? .54 : .44));addPeak(pp,(massif ? .075 : .095)+rnd()*.055,(massif ? .34 : .32)+rnd()*.34);if(i>0)addRidge(peaks[i-1],pp,(massif ? .032 : .040)+rnd()*.022,.10+rnd()*.15);}
      const vc=massif?5:3;
      for(let i=0;i<vc;i++){const a=point((rnd()-.5)*.75,(rnd()-.5)*.48),ang=axis+(rnd()-.5)*Math.PI*.95,len=bound*(.28+rnd()*.32),b={x:a.x+Math.cos(ang)*len,y:a.y+Math.sin(ang)*len};addValley(a,b,.035+rnd()*.035,.08+rnd()*.13);}
    }else{ // ROLLING
      baseLevel=.11;coastRiseFrac=.25+rnd()*.10;coastPower=1.22+rnd()*.20;noiseAmp=.16;noiseFreq=2.8;noiseOctaves=3;
      addMassif(point(0,0),.54,.20);
      const hc=4+Math.floor(rnd()*3);for(let i=0;i<hc;i++){const pp=point((rnd()-.5)*.72,(rnd()-.5)*.58);addPeak(pp,.13+rnd()*.08,.22+rnd()*.22);}
      for(let i=1;i<peaks.length;i+=2)addRidge(peaks[i-1],peaks[i],.055+rnd()*.025,.06+rnd()*.08);
      for(let i=0;i<2;i++){const a=point(-.35+rnd()*.20,(rnd()-.5)*.32),b=point(.28+rnd()*.22,(rnd()-.5)*.32);addValley(a,b,.055+rnd()*.030,.04+rnd()*.055);}
    }

    const prof={version:'GEOMORPH_V2',type,seed,baseLevel,coastRiseFrac,coastPower,noiseAmp,noiseFreq,noiseOctaves,noiseSeed:terrainMix32(seed^0xa53c9e17),massifs,ridges,valleys,peaks,radialBins:new Array(720),rawMax:1};
    // Normalize the canonical height field once per island so its strongest sampled summit approaches heightM.
    let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(const p of island.points){minX=Math.min(minX,p.x);minY=Math.min(minY,p.y);maxX=Math.max(maxX,p.x);maxY=Math.max(maxY,p.y);}
    const sn=major?30:24;let rawMax=1e-6;
    for(let j=0;j<=sn;j++){const y=lerp(minY,maxY,j/sn);for(let i=0;i<=sn;i++){const x=lerp(minX,maxX,i/sn);if(!pointInTerrainPolygon(x,y,island.points))continue;rawMax=Math.max(rawMax,terrainRawReliefV2(island,prof,x,y));}}
    for(const pk of peaks)rawMax=Math.max(rawMax,terrainRawReliefV2(island,prof,pk.x,pk.y));
    for(const r of ridges)rawMax=Math.max(rawMax,terrainRawReliefV2(island,prof,(r.ax+r.bx)*.5,(r.ay+r.by)*.5));
    prof.rawMax=Math.max(.05,rawMax);island._reliefProfile=prof;return prof;
  }
function pointInTerrainPolygon(x,y,poly){
    let inside=false;
    for(let i=0,j=poly.length-1;i<poly.length;j=i++){
      const a=poly[i],b=poly[j];
      if(((a.y>y)!==(b.y>y)) && x < (b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x) inside=!inside;
    }
    return inside;
  }
function terrainPickGeomorph(kind,heightM,rnd){
    const h=Math.max(0,Number(heightM)||0),u=rnd();
    if(kind==='MAJOR_LANDMASS'){
      if(u<.38)return 'MOUNTAIN_CHAIN';
      if(u<.70)return 'COASTAL_HIGHLANDS';
      return 'ERODED_MASSIF';
    }
    if(h>=250&&u<.24)return 'VOLCANIC';
    if(u<.48)return 'RIDGE';
    if(u<.80)return 'ERODED_HIGHLAND';
    return 'ROLLING';
  }
function terrainSeededRandom(seed){
    let x=(Number(seed)>>>0)||0x1865a17d;
    return ()=>{x^=x<<13;x>>>=0;x^=x>>>17;x>>>=0;x^=x<<5;x>>>=0;return x/4294967296;};
  }
let BATTLESPACE_SEED=2047861954;
function terrainHashStringU32(str){
    let h=2166136261>>>0;str=String(str??'');
    for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}
    return terrainMix32(h);
  }
function _segmentEdgeT(ax,ay,bx,by,cx,cy,dx,dy){
    const rx=bx-ax, ry=by-ay, sx=dx-cx, sy=dy-cy, den=rx*sy-ry*sx;
    if(Math.abs(den)<1e-12) return null;
    const qx=cx-ax,qy=cy-ay,t=(qx*sy-qy*sx)/den,u=(qx*ry-qy*rx)/den;
    if(t>=-1e-9&&t<=1+1e-9&&u>=-1e-9&&u<=1+1e-9) return clamp(t,0,1);
    return null;
  }
const terrainIslands=[];
const BATTLESPACE_DIAG_BYPASS=true;
const targetPool=[];
const OWN_ALT_M=DATA["OWN_ALT_M"];
function dist3Km(ax,ay,az_m, bx,by,bz_m){
    const rhKm = worldToKm(dist(ax,ay,bx,by));
    const dzKm = mToKm((bz_m ?? az_m) - az_m);
    return Math.hypot(rhKm, dzKm);
  }
const flares=[];
function getIrccmAnchor(m, ax, ay){
    let t = null;
    if(m.seekerLockType === 'TGT' && m.seekerLockId != null){
      t = truthObjectForTrackV27(m.seekerLockId,true);
    }
    if(!t && m.assignedTargetId != null){
      t = truthObjectForTrackV27(m.assignedTargetId,true);
    }
    if(t){
      const ang = Math.atan2(t.y - ay, t.x - ax);
      return { valid:true, type:'TGT', id:t.id, x:t.x, y:t.y, z:t.z, angle:ang };
    }
    if(Number.isFinite(m.irccmLastTargetAngle)) {
      return { valid:true, type:'MEM', id:(m.irccmLastTargetId ?? null), angle:m.irccmLastTargetAngle };
    }
    return { valid:false, type:null, id:null, angle:m.seekerAngle };
  }
function computeSarhIllumQ(){return 1;}
function surfaceSm2GuidanceFloorWip13C5(m){return surfaceMissileGuidanceFloorWip13C6(m);}
function altitudeForDynamicPressureM(vMps,qTargetPa,speedReserve=1.0){
    const vEff=Math.max(1,Math.abs(vMps||0)*clamp(speedReserve,0.1,1.5));
    const qTarget=Math.max(1,qTargetPa||1);
    const qAt=(alt)=>0.5*airDensityKgM3(alt)*vEff*vEff;
    if(qAt(ALT_MIN_M)<qTarget)return ALT_MIN_M;
    if(qAt(ATMOSPHERE_MODEL_MAX_M)>qTarget)return ATMOSPHERE_MODEL_MAX_M;
    let lo=ALT_MIN_M,hi=ATMOSPHERE_MODEL_MAX_M;
    for(let i=0;i<22;i++){
      const mid=(lo+hi)*0.5;
      if(qAt(mid)>=qTarget)lo=mid; else hi=mid;
    }
    return (lo+hi)*0.5;
  }
function wip136JettisonEssmTvc(m,reason='PITCHOVER_COMPLETE'){
    if(!m?.isESSM||m._wip136TvcJettisoned)return false;
    const kg=clamp(Number(m._wip136TvcJettisonMassKg??window.WIP136_ESSM_TVC_JETTISON_KG)||0,0,Math.max(0,(m.missileDryKg??0)-1));
    m._wip136TvcJettisoned=true;m._wip136TvcJettisonReason=reason;m._wip136TvcJettisonTimeS=m.life??0;m._wip136TvcJettisonAltM=m.z??0;
    m._wip136TvcJettisonSpeedMps=worldSpeedToMps(m.speed??0);m._wip136TvcJettisonMach=m.mach??null;m._wip136TvcJettisonQPa=m.qbar??null;
    m._wip136DryBeforeJettisonKg=m.missileDryKg??null;m._wip136TvcJettisonMassKg=kg;m.missileDryKg=Math.max(1,(m.missileDryKg??1)-kg);
    m.massKg=Math.max(1,(m.massKg??1)-kg);m.tvcEnabled=false;m.tvcAuthority=0;m._v1TvcAuthority=0;m._v1TvcActive=false;m.tvcCmdYaw=0;m.tvcCmdPitch=0;m.tvcYaw=0;m.tvcPitch=0;
    return true;
  }
function surfaceLaunchVectorAlignedWip13C6(m,isESSM,velPitchErr,velHdgErr,cfg){
  if(isESSM)return velPitchErr<=deg(9)&&velHdgErr<=deg(12);
  // Air SM-2 remains on its previous hand-off contract. Surface mode reuses the
  // existing profile tolerances for BOTH attitude and the flight-path vector.
  return !surfaceMissileRuntimeWip13C6(m)||(velPitchErr<=cfg.pitchTol&&velHdgErr<=cfg.headingTol);
}
function horizDistKm(ax, ay, bx, by){
    return worldToKm(dist(ax, ay, bx, by));
  }
function _samSetLaunchCorridorCommand(m,lead,isESSM,phase){
      const c=_samVlsControlConfig(m,isESSM),own=m.guidanceCore==='v1'?samNavB1OwnState(m):null,alt=own?own.posM.z:(m.z??0),ox=own?metersToWorld(own.posM.x):m.x,oy=own?metersToWorld(own.posM.y):m.y;
      const dxM=worldToMeters(lead.x-ox),dyM=worldToMeters(lead.y-oy),hM=Math.max(30,Math.hypot(dxM,dyM));
      const targetElev=Math.atan2(lead.z-alt,hM),floor=phase==='VLS'?c.lowFloor:c.trackFloor;
      const directPitch=clamp(Math.max(targetElev,floor),floor,c.pitchCeiling);
      // Registry planner may bias a long-range shot above direct LOS.  Urgent shots have loftDemand≈0,
      // so they remain direct.  SM-2 additionally holds near-vertical until its adaptive turnStartAltM.
      const loftPitch=clamp(Math.max(directPitch,c.launchLoftPitch??0),floor,c.pitchCeiling);
      let desiredPitch=loftPitch;
      if(phase==='VLS'&&alt<c.turnStartAltM)desiredPitch=c.initialPitch;
      const brg=Math.atan2(dyM,dxM),look=Math.max(250,c.lookaheadM);
      // WIP155: tan(90deg) is numerically unbounded.  During the exact vertical cell-hold,
      // command a finite +Z look point and keep the horizontal command at the missile position.
      const verticalHold=Math.abs(Math.cos(desiredPitch))<1e-6;
      const horizWorld=verticalHold?0:metersToWorld(look);
      const x=ox+Math.cos(brg)*horizWorld,y=oy+Math.sin(brg)*horizWorld,z=verticalHold?(alt+look):(alt+Math.tan(desiredPitch)*look);
      m._vlsDesiredPitch=desiredPitch;m._vlsDesiredBearing=brg;m._vlsTargetElev=targetElev;m._vlsLeadTgo=lead.tgo;
      return {x,y,z,desiredPitch,bearing:brg,config:c};
    }
function _samLeadPointForLaunch(m,tr,tgtX,tgtY,tgtZ,tgtVx,tgtVy,tgtVz,mslSpdMps,isESSM){
      const own=m.guidanceCore==='v1'?samNavB1OwnState(m):null,ox=own?metersToWorld(own.posM.x):m.x,oy=own?metersToWorld(own.posM.y):m.y,oz=own?own.posM.z:(m.z??0);
      const dxM=worldToMeters(tgtX-ox),dyM=worldToMeters(tgtY-oy),dzM=tgtZ-oz,rM=Math.max(1,Math.hypot(dxM,dyM,dzM));
      const projSpd=Math.max(isESSM?650:750,mslSpdMps),tgo=clamp(rM/Math.max(300,projSpd+350),.35,12);
      const leadFrac=isESSM?.72:.65;
      const zTgo=(tgtVz<0)?Math.min(tgo,Math.max(.15,tgtZ/Math.max(1,-tgtVz))):tgo;
      return {x:tgtX+tgtVx*tgo*leadFrac,y:tgtY+tgtVy*tgo*leadFrac,z:Math.max(5,tgtZ+tgtVz*zTgo*leadFrac),tgo};
    }
function _samBuildAdaptiveTrajectoryPlan(m,ctx){
    const p=_samTrajectoryProfileFor(m);
    if(!p?.enabled)return null;
    const u=p.urgency||{},l=p.loft||{},la=p.launch||{};
    const rangeKm=Math.max(.01,ctx.rangeKm??0),tgo=Math.max(.05,ctx.tgoS??0),alt=ctx.mslAltM??(m.z??0),tgtAlt=ctx.tgtAltM??0,tgtVz=ctx.tgtVzMps??0;
    const closing=Math.max(0,ctx.closingMps??0),v=Math.max(30,ctx.vMps??0),q=Math.max(0,ctx.qPa??m.qbar??0);
    const rangeUrg=_samInvWindow(rangeKm,u.rangeFullKm??8,u.rangeZeroKm??30);
    const tgoUrg=_samInvWindow(tgo,u.tgoFullS??6,u.tgoZeroS??20);
    const seaUrg=_samInvWindow(tgtAlt,u.seaFullAltM??40,u.seaZeroAltM??250);
    const diveUrg=_samUpWindow(Math.max(0,-tgtVz),u.diveStartMps??80,u.diveFullMps??320);
    const closeUrg=_samUpWindow(closing,u.closingStartMps??450,u.closingFullMps??1100);
    // Sea-skimming or diving alone is not an automatic emergency at long range: it amplifies
    // the range/TGO pressure instead of acting as a hidden target-class switch.
    const timePressure=Math.max(rangeUrg,tgoUrg);
    const urgency=clamp(Math.max(
      rangeUrg*.58+tgoUrg*.38+closeUrg*.16,
      seaUrg*timePressure*.78+diveUrg*.22+closeUrg*.12,
      diveUrg*timePressure*.72+closeUrg*.20+rangeUrg*.18
    ),0,1);

    const rmax=_samEstimateRmaxKm(p,alt,v,tgtAlt),rFrac=clamp(rangeKm/Math.max(1,rmax),0,1.25);
    const rangeLoft=_samSmooth01((rFrac-(l.minRangeFrac??.25))/Math.max(1e-6,(l.fullRangeFrac??.8)-(l.minRangeFrac??.25)));
    const tgoLoft=_samSmooth01((tgo-(l.tgoMinS??10))/Math.max(1e-6,(l.tgoFullS??30)-(l.tgoMinS??10)));
    const qRise=_samSmooth01((q-(l.qMinPa??5000))/Math.max(1,(l.qOptLowPa??16000)-(l.qMinPa??5000)));
    const qFall=_samSmooth01((q-(l.qOptHighPa??50000))/Math.max(1,(l.qTooHighPa??90000)-(l.qOptHighPa??50000)));
    const qW=clamp(lerp(l.qLowFloor??.4,1,qRise)*lerp(1,l.qHighFloor??.6,qFall),.2,1);
    const horizM=Math.max(100,ctx.horizRangeM??rangeKm*1000),elev=Math.atan2(tgtAlt-alt,horizM);
    let geom=1;
    if(elev>0)geom*=1+(l.targetHighGain??.2)*clamp(elev/deg(20),0,1);
    else geom*=1+(l.targetLowGain??.1)*clamp((-elev)/deg(15),0,1);
    const loftDemand=clamp(rangeLoft*tgoLoft*qW*geom*(1-(l.urgencySuppression??.9)*urgency),0,1);
    const bias=clamp(loftDemand-urgency,-1,1);
    const pick=(urgent,normal,long)=>bias<0?lerp(normal,urgent,-bias):lerp(normal,long,bias);
    const turnStartAltM=pick(la.turnStartUrgentM??1,la.turnStartNormalM??1,la.turnStartLongM??1);
    const attitudeCompleteAltM=pick(la.attitudeUrgentM??10,la.attitudeNormalM??20,la.attitudeLongM??30);
    const exitAltM=pick(la.exitUrgentM??15,la.exitNormalM??30,la.exitLongM??50);
    const minForwardMps=pick(la.minForwardUrgentMps??100,la.minForwardNormalMps??140,la.minForwardLongMps??180);
    const maxVelExitDeg=pick(la.maxVelPitchUrgentDeg??30,la.maxVelPitchNormalDeg??40,la.maxVelPitchLongDeg??50);
    let launchLoftPitchDeg=(la.maxLaunchLoftPitchDeg??20)*loftDemand;
    const cruiseBase=lerp(l.cruiseAltMinM??500,l.cruiseAltMaxM??4000,clamp(rFrac,0,1));
    // WIP63 high-altitude vertical budget.  Estimate where a descending target will be over a
    // bounded planning horizon, then ask how much average vertical closure the interceptor still owes.
    // Long/high shots may trade some horizontal progress for an earlier climb, but the shelf remains
    // hard-bounded and never becomes the target's raw altitude.
    const highPredH=Math.min(tgo,l.highTargetPredictionHorizonS??30);
    const highPredTargetAltM=Math.max(0,tgtAlt+tgtVz*highPredH);
    const highAltEvalM=Math.max(highPredTargetAltM,tgtAlt*0.70);
    const highTarget01=(l.highTargetStartAltM!=null&&l.highTargetFullAltM!=null)
      ? _samUpWindow(highAltEvalM,l.highTargetStartAltM,l.highTargetFullAltM) : 0;
    const highVerticalDeficitM=Math.max(0,highPredTargetAltM-alt);
    const highRequiredVerticalMps=highVerticalDeficitM/Math.max(4,Math.min(tgo,30));
    const highVerticalNeed01=(l.highTargetVerticalNeedStartMps!=null&&l.highTargetVerticalNeedFullMps!=null)
      ? _samUpWindow(highRequiredVerticalMps,l.highTargetVerticalNeedStartMps,l.highTargetVerticalNeedFullMps) : 0;
    const highRange01=(l.highTargetRangeStartKm!=null&&l.highTargetRangeFullKm!=null)
      ? _samUpWindow(rangeKm,l.highTargetRangeStartKm,l.highTargetRangeFullKm) : 0;
    const highClimb01=clamp(highTarget01*highVerticalNeed01*highRange01,0,1);
    let highTargetShelfAltM=null;
    if(highClimb01>0.0001){
      const shelfShape=clamp(.45*highTarget01+.35*highVerticalNeed01+.20*highRange01,0,1);
      let shelf=lerp(l.highTargetShelfMinM??11500,l.highTargetShelfMaxM??17500,shelfShape);
      const predCap=Math.max(l.cruiseAltMinM??2200,highPredTargetAltM-(l.highTargetShelfBelowPredictedM??1200));
      shelf=Math.min(shelf,predCap,l.highTargetShelfHardMaxM??19000);
      highTargetShelfAltM=Math.max(cruiseBase,shelf);
      launchLoftPitchDeg=lerp(launchLoftPitchDeg,Math.max(launchLoftPitchDeg,l.highTargetLaunchLoftMaxDeg??42),highClimb01);
    }
    // WIP61: cruiseAlt is an ENERGY shelf, not the target's current altitude.  The old max(tgtAlt,...)
    // silently turned a 31-35 km Kh-32 into a 31-35 km 'cruise' command even though SM-2's registered
    // loft shelf tops out near 12.5 km.  PIP/terminalFade already own the later climb to intercept altitude.
    let cruiseAltM=Math.max(0,cruiseBase);
    if(highTargetShelfAltM!=null) cruiseAltM=lerp(cruiseAltM,Math.max(cruiseAltM,highTargetShelfAltM),highClimb01);
    let terminalBlendStartKm=l.terminalBlendStartKm??20,terminalBlendFullKm=l.terminalBlendFullKm??8;
    // WIP53: low-altitude SARH terminal-geometry limiter.  Low targets are NOT forced into an
    // emergency/direct profile at long range; the planner simply bounds how much vertical separation
    // it is allowed to create before terminal convergence.  High-altitude shots keep their energy shelf and converge upward through PIP/terminal fade.
    const tgtAltSigmaM=Math.max(0,ctx.tgtAltSigmaM??0);
    const lowAltEvalM=Math.max(0,tgtAlt-0.65*tgtAltSigmaM);
    const lowTarget01=(l.lowTargetFullAltM!=null&&l.lowTargetZeroAltM!=null)
      ? _samInvWindow(lowAltEvalM,l.lowTargetFullAltM,l.lowTargetZeroAltM) : 0;
    let lowTargetCruiseCapM=null;
    if(lowTarget01>0.0001){
      terminalBlendStartKm=lerp(terminalBlendStartKm,l.lowTargetTerminalBlendStartKm??terminalBlendStartKm,lowTarget01);
      terminalBlendFullKm=lerp(terminalBlendFullKm,l.lowTargetTerminalBlendFullKm??terminalBlendFullKm,lowTarget01);
      const slopeDeg=l.lowTargetCruiseSlopeDeg??10;
      const geomCap=tgtAlt+Math.tan(deg(slopeDeg))*terminalBlendStartKm*1000;
      lowTargetCruiseCapM=Math.min(l.lowTargetCruiseHardMaxM??Infinity,geomCap);
      cruiseAltM=lerp(cruiseAltM,Math.min(cruiseAltM,lowTargetCruiseCapM),lowTarget01);
      launchLoftPitchDeg*=lerp(1,l.lowTargetLaunchLoftScale??0.75,lowTarget01);
    }
    const plan={profileId:p.id,urgency,loftDemand,bias,rmaxKm:rmax,rFrac,qWeight:qW,tgoS:tgo,
      turnStartAltM,attitudeCompleteAltM,exitAltM,minForwardMps,maxVelExitDeg,launchLoftPitchDeg,cruiseAltM,
      directPitchFloorDeg:la.directPitchFloorDeg??3,trackPitchFloorDeg:la.trackPitchFloorDeg??2,
      pitchCeilingDeg:la.pitchCeilingDeg??60,initialPitchDeg:la.initialPitchDeg??88,launchClearAltM:la.launchClearAltM??.5,
      headingToleranceDeg:la.headingToleranceDeg??12,pitchToleranceDeg:la.pitchToleranceDeg??10,pitMinS:la.pitMinS??.1,pitMaxS:la.pitMaxS??2,
      lookaheadM:la.lookaheadM??1000,seaMarginM:la.seaMarginM??10,seaLookaheadS:la.seaLookaheadS??.8,
      hardRateCapDegS:pick(la.hardRateUrgentDegS??la.hardRateCapDegS??120,la.hardRateNormalDegS??la.hardRateCapDegS??120,la.hardRateLongDegS??la.hardRateCapDegS??120),
      commitRateCapDegS:pick(la.commitRateUrgentDegS??la.commitRateCapDegS??80,la.commitRateNormalDegS??la.commitRateCapDegS??80,la.commitRateLongDegS??la.commitRateCapDegS??80),
      hardGain:pick(la.hardGainUrgent??la.hardGain??3,la.hardGainNormal??la.hardGain??3,la.hardGainLong??la.hardGain??3),
      commitGain:pick(la.commitGainUrgent??la.commitGain??2.5,la.commitGainNormal??la.commitGain??2.5,la.commitGainLong??la.commitGain??2.5),
      controlAggressiveness:pick(la.controlUrgent??1,la.controlNormal??0.7,la.controlLong??0.4),
      terminalBlendStartKm,terminalBlendFullKm,maxLoftPitchDeg:l.maxPitchDeg??20,
      lowTarget01,lowTargetCruiseCapM,tgtAltSigmaM,lowAltEvalM,
      highPredTargetAltM,highTarget01,highVerticalDeficitM,highRequiredVerticalMps,highVerticalNeed01,highRange01,highClimb01,highTargetShelfAltM};
    m._samTrajPlan=plan;
    return loftB4UpdatePlan(m,ctx,plan);
  }
function loftB4UpdatePlan(m,ctx,plan){
    const p=loftB4Profile(m);
    const surfaceKey=surfaceMissileRuntimeWip13C6(m)?surfaceMissileVariantKeyWip15C(m):null;
    if(!p||m.guidanceCore!=='v1'||!m._onboardNavB2||(surfaceKey&&!['SM2ER','SM6'].includes(surfaceKey)))return plan;
    const own=missileNavB2OwnState(m),age=Number(m.life)||0;
    const r=Math.max(.001,Number(ctx.horizRangeM)/1000),alt=own.posM.z;
    if(!Number.isFinite(r)||!Number.isFinite(alt))return plan;
    let s=m._loftB4;
    if(!s){
      const factor=_samSmooth01((r-p.startKm)/Math.max(1,p.fullLoftKm-p.startKm));
      // Do not insert a shelf below an already high target: preserve the existing direct climb.
      const highTarget=(Number(ctx.tgtAltM)||0)>=p.shelfMaxM;
      const mode=r>p.startKm&&!highTarget?p.mode:'DIRECT';
      const shelf=lerp(p.shelfMinM,p.shelfMaxM,factor);
      s=m._loftB4={schema:'AEGIS_GAME_TRAJECTORY_B4',profileId:p.id,mode,
        phase:mode==='DIRECT'?'DIRECT':'CLIMB',directReason:mode==='DIRECT'?(highTarget?'HIGH_TARGET':'SHORT_RANGE'):null,initialRangeKm:r,rangeGoalKm:p.rangeGoalKm,
        shelfM:Math.max(shelf,Math.min(Number(ctx.tgtAltM)||0,p.shelfMaxM)),
        descentStartKm:Math.max(p.descentFloorKm,r*p.descentFraction),phaseStartS:age,lastStep:-1,
        transitions:[{phase:mode==='DIRECT'?'DIRECT':'CLIMB',reason:'LAUNCH_PLAN',step:simStepCounter,ageS:age}]};
    }
    // This function may be queried by multiple consumers, but time advances only at fixed ticks.
    if(s.lastStep!==simStepCounter){
      s.lastStep=simStepCounter;s.rangeKm=r;s.targetAltitudeM=Number(ctx.tgtAltM)||0;
      s.navAltitudeM=alt;s.speedMps=Math.hypot(own.velMps.x,own.velMps.y,own.velMps.z);
      s.targetTgoS=Math.max(0,(Number(ctx.rangeKm)||r)*1000/Math.max(180,Number(ctx.closingMps)||s.speedMps));
      s.navUncertaintyM=weaponLinkB3NavUncertainty(m)?.posSigmaM??null;
      s.targetAltitudeSigmaM=Number(ctx.tgtAltSigmaM)||0;
      s.mach=s.speedMps/Math.max(1,speedOfSoundMps(Math.max(0,alt)));
      s.dynamicPressurePa=.5*airDensityKgM3(Math.max(0,alt))*s.speedMps*s.speedMps;
      s.energyHeightM=alt+s.speedMps*s.speedMps/(2*G0);
      // Four lofted SAM routes opt in; ER/SM-6 retain their existing profile limits.
      if((p.id==='SM2MR_B4'||p.id==='ESSM_B4'||p.id==='SM2ER_B4'||p.id==='SM6_B4') && s.mode!=='DIRECT' && s.phase!=='DIVE'){
        gameB4ReplanShelf(m,s,p,ctx,age,r,alt);
        if(Number.isFinite(s.gameDesiredShelfM)){
          // Per-tick change clamp prevents abrupt waypoint jumps between logic ticks.
          const changeLimit=(p.id==='ESSM_B4'?720:1100)*SIM_FIXED_DT;
          s.shelfM+=clamp(s.gameDesiredShelfM-s.shelfM,-changeLimit,changeLimit);
        }
      }
      if(s.mode!=='DIRECT'&&!m.vlsPhase&&!m.pitchoverPhase){
        const energyLow=age>(m.burnTotal??1000)+5&&s.speedMps<p.energyReleaseMps;
        if(r<=s.descentStartKm||energyLow||m._wip79KappaTerminalLatched){
          loftB4Transition(s,'DIVE',energyLow?'ENERGY_LOW':m._wip79KappaTerminalLatched?'TERMINAL_HANDOFF':'REMAINING_ROUTE',simStepCounter,age);
        }else if(s.phase==='CLIMB'&&age-s.phaseStartS>=2&&alt>=s.shelfM-Math.max(400,s.shelfM*.035)){
          loftB4Transition(s,'CRUISE','SHELF_CAPTURE',simStepCounter,age);
        }
      }
    }
    plan.statefulProfileId=p.id;plan.statefulPhase=s.phase;plan.statefulShelfM=s.shelfM;plan.gameDynamicShelfGoalM=s.gameDesiredShelfM??null;plan.gameDynamicShelfReplans=s.gameShelfReplans??0;
    // Existing launch-clearance/pitchover behavior remains untouched. Only post-launch loft is latched.
    return plan;
  }
function loftB4Transition(s,phase,reason,step,age){
    const ranks={DIRECT:3,CLIMB:0,CRUISE:1,DIVE:2};
    if(phase===s.phase||ranks[phase]<ranks[s.phase])return;
    s.phase=phase;s.phaseStartS=age;s.transitions.push({phase,reason,step,ageS:age});
    if(s.transitions.length>4)s.transitions.shift();
  }
function gameB4ReplanShelf(m,s,p,ctx,age,r,alt){
    if(s.mode==='DIRECT'||s.phase==='DIVE'||m.vlsPhase||m.pitchoverPhase)return;
    if(s.lastGameShelfReviewS!=null && age-s.lastGameShelfReviewS<0.50)return;
    s.lastGameShelfReviewS=age;
    // Preserve initial-route intent but allow changes in target position and remaining game range.
    // In contrast to rerunning the entire route from scratch, the live term is deliberately small.
    const den=Math.max(1,p.fullLoftKm-p.startKm);
    const initialFactor=_samSmooth01((s.initialRangeKm-p.startKm)/den);
    const liveFactor=_samSmooth01((r-p.startKm)/den);
    const factor=clamp(initialFactor*0.84+liveFactor*0.16,0,1);
    let goal=lerp(p.shelfMinM,p.shelfMaxM,factor);
    // If the observed target changes altitude, update the game waypoint without assuming
    // the target has any special category or inventing a new radar contact.
    const targetAltitude=Math.max(0,Number(ctx.tgtAltM)||0);
    goal=Math.max(goal,Math.min(p.shelfMaxM,targetAltitude));
    // Late in the game run, a slowed projectile should not chase a stale high waypoint.
    const v=Math.max(0,s.speedMps||0);
    const late=age>Math.max(8,(Number(m.burnTotal)||0)*0.60);
    const lowSpeed=late?clamp((p.energyReleaseMps+95-v)/Math.max(160,p.energyReleaseMps*.55),0,1):0;
    goal=lerp(goal,Math.min(goal,Math.max(p.shelfMinM,alt+1750)),lowSpeed*.45);
    s.gameDesiredShelfM=clamp(goal,p.shelfMinM,p.shelfMaxM);
    s.gameShelfReplans=(s.gameShelfReplans||0)+1;
  }
function weaponLinkB3NavUncertainty(m){
    // Estimated uncertainty from instrument history/profile only. Never measured truth error.
    const n=m?._onboardNavB2??m?._b1Nav;if(!n)return null;
    const p=missileNavB2ProfileFor(m),hasFix=!!(p.gpsAid&&n.lastGps);
    const age=hasFix?Math.max(0,n.timeS-n.lastGps.timeS):Math.max(0,n.timeS);
    const pos0=hasFix?Math.max(1,p.gpsPosSigmaM):p.initialPosErrorM;
    const vel0=hasFix?Math.max(.01,p.gpsVelSigmaMps):p.initialVelErrorMps;
    return {posSigmaM:pos0+vel0*age+1.5*p.accelBiasMps2*age*age,
      velSigmaMps:vel0+3*p.accelBiasMps2*age};
  }
function _samEstimateRmaxKm(profile,altM,vMps,tgtAltM){
    const base=profile?.nominalRmaxKm??60,rhoF=airDensityFactor(Math.max(0,altM));
    const altEff=clamp(0.78+0.55*(1-Math.pow(rhoF,0.42)),0.76,1.28);
    const mach=vMps/Math.max(1,speedOfSoundMps(Math.max(0,altM)));
    const speedEff=clamp(0.64+0.18*mach,0.62,1.28);
    const tgtEff=clamp(1+(tgtAltM-altM)/50000,0.84,1.12);
    return clamp(base*altEff*speedEff*tgtEff,profile?.minRmaxKm??10,profile?.maxRmaxKm??180);
  }
function airDensityFactor(altM){
    return clamp(airDensityKgM3(altM)/ATM_RHO_TABLE[0][1],0,1);
  }
function trackCovarianceMetrics(tr){
    trackEkfInit(tr);const P=tr._kfP;
    const a=P[0],b=P[1],d=P[7],disc=Math.sqrt(Math.max(0,(a-d)*(a-d)+4*b*b)),lmax=Math.max(1e-6,0.5*(a+d+disc)),lmin=Math.max(1e-6,0.5*(a+d-disc));
    const ang=0.5*Math.atan2(2*b,a-d);
    return {posSigmaM:Math.sqrt(lmax),posMinorSigmaM:Math.sqrt(lmin),ellipseAngleRad:ang,altSigmaM:Math.sqrt(Math.max(1e-6,P[14])),vxSigmaMps:Math.sqrt(Math.max(1e-6,P[21])),vySigmaMps:Math.sqrt(Math.max(1e-6,P[28])),vzSigmaMps:Math.sqrt(Math.max(1e-6,P[35])),velSigmaMps:Math.sqrt(Math.max(1e-6,Math.max(P[21],P[28],P[35])))};
  }
function trackEkfInit(tr,meas=null){
    if(tr?._kfX&&tr?._kfP) return tr;
    const x=new Float64Array(6);
    x[0]=worldToMeters(tr?.x??aircraft.x()); x[1]=worldToMeters(tr?.y??aircraft.y()); x[2]=tr?.z??OWN_ALT_M;
    x[3]=worldSpeedToMps(tr?.vx??0); x[4]=worldSpeedToMps(tr?.vy??0); x[5]=tr?.vz??0;
    const P=new Float64Array(36);
    if(meas){
      const basis=trackMeasurementBasis(meas), r=Math.max(100,meas.rangeM??Math.hypot(x[0]-worldToMeters(aircraft.x()),x[1]-worldToMeters(aircraft.y()),x[2]-OWN_ALT_M));
      const sr=Math.max(4,meas.rangeSigmaM??60), saz=r*deg(Math.max(0.005,meas.azSigmaDeg??0.10)), sel=r*deg(Math.max(0.008,meas.elSigmaDeg??0.14));
      if(meas.cartesianCovarianceM2?.length===9){
        const C=trackCartesianMeasurementCovarianceV33(meas);for(let rr=0;rr<3;rr++)for(let cc=0;cc<3;cc++)P[_mIdx(rr,cc,6)]=C[_mIdx(rr,cc,3)];
      }else{
        _outerAdd3(P,0,...basis.ur,sr*sr); _outerAdd3(P,0,...basis.uaz,Math.max(sr,saz)**2); _outerAdd3(P,0,...basis.uel,Math.max(sr,sel)**2);
      }
      const srv=Math.max(2,meas.radialVelSigmaMps??8), st=TRACK_FILTER_MODEL.initialTransverseVelSigmaMps, sv=TRACK_FILTER_MODEL.initialVerticalVelSigmaMps;
      _outerAdd3(P,3,...basis.ur,srv*srv); _outerAdd3(P,3,...basis.uaz,st*st); _outerAdd3(P,3,...basis.uel,sv*sv);
    }else{
      const ps=Math.max(40,tr?.measurementSigmaM??100), as=Math.max(60,tr?.altitudeSigmaM??80), vs=Math.max(20,tr?.velocitySigmaMps??80);
      P[_mIdx(0,0,6)]=ps*ps;P[_mIdx(1,1,6)]=ps*ps;P[_mIdx(2,2,6)]=as*as;
      P[_mIdx(3,3,6)]=vs*vs;P[_mIdx(4,4,6)]=vs*vs;P[_mIdx(5,5,6)]=vs*vs;
    }
    tr._kfX=x; tr._kfP=_symmetrizeClampP(P); tr._kfNis=0; tr._maneuverProbability=0; tr._kfPredictAgeS=0;
    trackSyncLegacyFromEkf(tr); return tr;
  }
function trackSyncLegacyFromEkf(tr){
    if(!tr?._kfX)return;const x=tr._kfX;tr.x=metersToWorld(x[0]);tr.y=metersToWorld(x[1]);tr.z=clamp(x[2],ALT_MIN_M,TRACK_ALT_MAX_M);tr.vx=mpsToWorldSpeed(x[3]);tr.vy=mpsToWorldSpeed(x[4]);tr.vz=x[5];
    trackRefreshDerivedQuality(tr);
  }
function trackRefreshDerivedQuality(tr){
    if(!tr)return;const u=trackCovarianceMetrics(tr),age=Math.max(0,tr.sensorAge??0),expected=Math.max(0.05,tr._spyExpectedRevisitS??0.30);
    const posQ=Math.exp(-u.posSigmaM/550),altQ=Math.exp(-u.altSigmaM/500),velQ=Math.exp(-u.velSigmaMps/95),freshQ=Math.exp(-age/Math.max(0.5,expected*6));
    tr.kinematicQuality=clamp(0.40*posQ+0.18*altQ+0.30*velQ+0.12*freshQ,0,1);
    let fc=clamp(0.44*posQ+0.16*altQ+0.32*velQ+0.08*freshQ,0,1);if(!tr.confirmed)fc*=0.45;if(tr.reacquiring)fc*=0.50;if(tr.memActive)fc*=0.36;
    tr.fireControlQuality=clamp(fc,0,1);tr.trackQuality=clamp(tr.kinematicQuality*(tr.confirmed?1:0.68),0.02,1);
    tr.measurementSigmaM=u.posSigmaM;tr.altitudeSigmaM=u.altSigmaM;tr.velocitySigmaMps=u.velSigmaMps;
    tr.memSigPosKm=u.posSigmaM/1000;tr.memSigAltM=u.altSigmaM;tr.memSigVelMps=u.velSigmaMps;
    tr.covarianceEllipse={majorSigmaM:u.posSigmaM,minorSigmaM:u.posMinorSigmaM,angleRad:u.ellipseAngleRad};
  }
const TRACK_ALT_MAX_M=DATA["TRACK_ALT_MAX_M"];
function _symmetrizeClampP(P,n=6){
    for(let r=0;r<n;r++){
      for(let c=r+1;c<n;c++){const v=0.5*(P[_mIdx(r,c,n)]+P[_mIdx(c,r,n)]);P[_mIdx(r,c,n)]=v;P[_mIdx(c,r,n)]=v;}
      const ii=_mIdx(r,r,n); P[ii]=Math.max(1e-6,Number.isFinite(P[ii])?P[ii]:1e6);
    }
    return P;
  }
function _mIdx(r,c,n){ return r*n+c; }
const TRACK_FILTER_MODEL=DATA["TRACK_FILTER_MODEL"];
function _outerAdd3(M,offset,ux,uy,uz,varv){
    const u=[ux,uy,uz]; for(let r=0;r<3;r++)for(let c=0;c<3;c++)M[_mIdx(offset+r,offset+c,6)]+=varv*u[r]*u[c];
  }
function trackCartesianMeasurementCovarianceV33(meas){
    const R=new Float64Array(9);
    if(meas?.cartesianCovarianceM2?.length===9){
      for(let i=0;i<9;i++)R[i]=Number(meas.cartesianCovarianceM2[i])||0;
      return _symmetrizeClampP(R,3);
    }
    const sxy=Math.max(25,meas?.rangeSigmaM??100),sz=Math.max(30,meas?.altitudeSigmaM??sxy*0.7);
    R[0]=sxy*sxy;R[4]=sxy*sxy;R[8]=sz*sz;return R;
  }
function trackMeasurementBasis(meas){
    const az=Number.isFinite(meas.azRad)?meas.azRad:Math.atan2(meas.losUy??0,meas.losUx??1);
    const el=Number.isFinite(meas.elRad)?meas.elRad:Math.asin(clamp(meas.losUz??0,-1,1));
    const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
    return {ur:[ce*ca,ce*sa,se],uaz:[-sa,ca,0],uel:[-se*ca,-se*sa,ce]};
  }
function surfaceMissileCommandAimHeightWip15C(m,targetXWorld,targetYWorld,referenceM){
  return surfaceMissileGlideAimWip15C(m,{x:worldToMeters(targetXWorld),y:worldToMeters(targetYWorld)},referenceM).aimM;
}
function weaponLinkB3TrackSnapshot(m,coast=false){
    const r=m?._weaponLinkB3;if(!r)return null;
    const t=WEAPON_LINK_B3.targetState(r,weaponLinkB3Now(m),coast);if(!t)return null;
    const P=Float64Array.from(t.covariance),sig=Math.sqrt(Math.max(1,P[0],P[7]));
    return {id:r.trackId,x:metersToWorld(t.posM.x),y:metersToWorld(t.posM.y),z:t.posM.z,
      vx:mpsToWorldSpeed(t.velMps.x),vy:mpsToWorldSpeed(t.velMps.y),vz:t.velMps.z,
      confirmed:true,sensorDetected:true,ttl:Math.max(0,r.profile.uplink.maxAgeS-t.ageS),sensorAge:t.ageS,
      fireControlQuality:t.quality,trackQuality:t.quality,kinematicQuality:t.quality,classification:t.classification,
      sensorSource:t.valid?'B3_DL_RX':'B3_DL_COAST',_kfX:new Float64Array([t.posM.x,t.posM.y,t.posM.z,t.velMps.x,t.velMps.y,t.velMps.z]),_kfP:P,
      _b1PosSigmaM:sig,_b1AltSigmaM:Math.sqrt(Math.max(1,P[14])),_b1VelSigmaMps:Math.sqrt(Math.max(.01,P[21],P[28],P[35])),
      _b1RxLife:Math.max(0,(r.uplink.lastRxStep-r.plan.launchStep)*SIM_FIXED_DT),_b1RxSeq:t.sequence,_b1DlSnapshot:true,
      _b3Epoch:t.epoch,_b3PacketAgeS:t.ageS,_b3TransportAgeS:t.transportAgeS,_b3Valid:t.valid};
  }
function trackIsDisplayable(tr){
    if(!tr||tr.sensorDetected===false)return false;
    // WIP11C BDA presentation: a retired ASM track may remain internally available for
    // anonymous-search reassociation, but it must not coast across the PPI as a live threat
    // after own-force kill confirmation.  Wreckage is a separate world/render collection.
    if(wip121BdaTrackPresentation(tr).hidden)return false;
    const u=trackCovarianceMetrics(tr);
    return (tr.trackQuality??0)>0.05 && u.posSigmaM<TRACK_FILTER_MODEL.maxPosSigmaM;
  }
function wip121BdaTrackPresentation(tr){
    const q=wip121AssessmentForTrack(tr?.trackId,tr),state=String(q.state??'UNASSESSED'),a=q.assessment;
    // Direct-breakup/fuze BDA is stronger evidence than a later kinematic sea-impact inference.
    // Keep the kill presentation authoritative if both happen to coexist on one coasted file.
    if(state==='KILL_ASSESSMENT'||state==='DESTROYED'){
      const ev=a?.bdaEvent??a?.killPlausibility?.event??null,now=simStepCounter*SIM_FIXED_DT,eventT=Number(ev?.t),ageS=Number.isFinite(eventT)?Math.max(0,now-eventT):0;
      const confirmAfterS=Number.isFinite(Number(ev?.confirmAfterS))?Math.max(0,Number(ev.confirmAfterS)):WIP118_KILL_ASSESSMENT_POLICY.bdaFuzeNoReturnConfirmS;
      const confirmedAgeS=Math.max(0,ageS-confirmAfterS),hidden=state==='DESTROYED'&&confirmedAgeS+1e-9>=WIP118_KILL_ASSESSMENT_POLICY.bdaDestroyedDisplayHoldS;
      return {state,kind:state==='KILL_ASSESSMENT'?'BDA':'KILL',hidden,ageS,confirmedAgeS,confirmAfterS,evidence:ev?.evidence??null};
    }
    if(tr?._wip11cObservedSeaImpact)return {state:'HARMLESS',kind:'SEA_IMPACT',hidden:true,ageS:Math.max(0,(simStepCounter-Number(tr._wip11cObservedSeaImpact.step||simStepCounter))*SIM_FIXED_DT),confirmedAgeS:0,evidence:'OBSERVED_SEA_IMPACT'};
    return {state,kind:'LIVE',hidden:false,ageS:null,confirmedAgeS:null};
  }
const WIP118_KILL_ASSESSMENT_POLICY=DATA["WIP118_KILL_ASSESSMENT_POLICY"];
function wip121AssessmentForTrack(trackId,tr=null){
    const id=Number(trackId??tr?.trackId),a=Number.isFinite(id)?wip118ControlState.assessments.get(id):null;
    return {id:Number.isFinite(id)?id:null,assessment:a??null,state:a?.state??tr?.threatStatus??'UNASSESSED'};
  }
const wip118ControlState={assessments:new Map(),accel:new Map()};
const tracks=new Map();
const MISSILE_CDWAVE_K=DATA["MISSILE_CDWAVE_K"];
function transonicFactor(mach){
    const x = (mach - MISSILE_CDWAVE_M0) / Math.max(1e-6, MISSILE_CDWAVE_SIG);
    return Math.exp(-x*x); // 0..1
  }
const MISSILE_CDWAVE_SIG=DATA["MISSILE_CDWAVE_SIG"];
const MISSILE_CDWAVE_M0=DATA["MISSILE_CDWAVE_M0"];
const MISSILE_CDCTRL_K=DATA["MISSILE_CDCTRL_K"];
const MISSILE_E_OSWALD=DATA["MISSILE_E_OSWALD"];
const MISSILE_AR=DATA["MISSILE_AR"];
const MISSILE_CD0=DATA["MISSILE_CD0"];
function wip14a11ParasiticCd(m,mach,altitudeM,thrustN,currentCd){
    const cfg=m._wip14a11Experiment,upperStage=!(m.isSM2ER||m.isSM6)||!!m.boosterSeparated,powerState=thrustN>1?'POWERED':'UNPOWERED';let cd=currentCd,source='AERO_CURRENT',components=null,baseDeltaCd=0;
    if(upperStage&&cfg.aeroModel!==WIP14A11_AERO_MODE.CURRENT){
      const band=cfg.aeroModel.endsWith('_LOW')?'LOW':cfg.aeroModel.endsWith('_HIGH')?'HIGH':'NOMINAL',b=wip14a9BuildupOne({altitudeM,mach,powerState,band});cd=b.Cd0;components={...b.components};source=cfg.aeroModel;
    }else if(upperStage&&cfg.baseDragModel===WIP14A11_BASE_DRAG_MODE.NOMINAL_SPLIT&&powerState==='UNPOWERED'){
      const on=wip14a9BuildupOne({altitudeM,mach,powerState:'POWERED',band:'NOMINAL'}),off=wip14a9BuildupOne({altitudeM,mach,powerState:'UNPOWERED',band:'NOMINAL'});baseDeltaCd=off.components.CdBase-on.components.CdBase;cd=currentCd+baseDeltaCd;source='AERO_CURRENT_PLUS_NOMINAL_UNPOWERED_BASE_DELTA';components={poweredBase:on.components.CdBase,unpoweredBase:off.components.CdBase};
    }
    m._wip14a11AeroState={source,powerState,upperStageApplied:upperStage,baseDeltaCd,currentCd,selectedCd:cd,components};return Math.max(.02,cd);
  }
const WIP14A11_BASE_DRAG_MODE=DATA["WIP14A11_BASE_DRAG_MODE"];
function wip14a9BuildupOne(opts={}){
    const band=String(opts.band??'NOMINAL').toUpperCase(),c=WIP14A9_RANGE[band]??WIP14A9_RANGE.NOMINAL,mach=Math.max(.05,Number(opts.mach)||.05),altitudeM=clamp(Number(opts.altitudeM)||0,0,50000),powered=String(opts.powerState??'POWERED').toUpperCase()!=='UNPOWERED';
    const atm=wip14a9Atmosphere(altitudeM,mach),diameterM=.343,radiusM=diameterM*.5,lengthM=4.85,Aref=WIP14A9_AREF_M2;
    const reynoldsNumber=atm.rhoKgM3*atm.speedMps*lengthM/Math.max(1e-12,atm.dynamicViscosityPaS),cfFlatPlate=.455/(Math.pow(Math.log10(Math.max(1e5,reynoldsNumber)),2.58)*Math.pow(1+.144*mach*mach,.65));
    const coneSlantM=Math.hypot(c.noseLengthM,radiusM),cylinderLengthM=Math.max(.1,lengthM-c.noseLengthM),bodyWettedAreaM2=Math.PI*diameterM*cylinderLengthM+Math.PI*radiusM*coneSlantM;
    const noseHalfAngleRad=Math.atan2(radiusM,c.noseLengthM),beta=Math.sqrt(Math.max(.1225,mach*mach-1)),noseSupCd=Math.min(c.noseCapCd,2*noseHalfAngleRad*c.noseFactor/beta),transonicBlend=wip14a9Smooth01((mach-.82)/.38),CdNose=c.noseSubCd*(1-transonicBlend)+noseSupCd*transonicBlend;
    const transonicShape=mach<1.3?.4+1.4*Math.exp(-Math.pow((mach-1.02)/.20,2)):1+.08*Math.min(3,mach-1.3),CdBody=c.bodyWaveCd*transonicShape;
    const CdSkin=cfFlatPlate*(bodyWettedAreaM2/Aref)*c.roughnessFactor;
    const finWettedAreaM2=2*c.finPlanformTotalM2*(1+.5*c.finThicknessChord),CdFinProfile=cfFlatPlate*(finWettedAreaM2/Aref)*c.roughnessFactor*(1+2*c.finThicknessChord);
    const finWaveBlend=wip14a9Smooth01((mach-.80)/.40),CdFinWave=finWaveBlend*4*c.finThicknessChord*c.finThicknessChord/Math.max(.35,beta)*(c.finPlanformTotalM2/Aref)*c.finWaveFactor;
    const baseMachShape=mach<1?1:1/Math.sqrt(mach),CdBase=(powered?c.poweredBaseCd:c.unpoweredBaseCd)*baseMachShape;
    const CdInterference=(CdFinProfile+CdFinWave)*c.interferenceFraction+c.interferenceFloorCd,CdMisc=c.miscCd*(1+.04*Math.max(0,mach-1));
    const components={CdNose,CdBody,CdSkin,CdBase,CdFinProfile,CdFinWave,CdInterference,CdMisc},Cd0=Object.values(components).reduce((a,b)=>a+b,0),dragN=atm.qPa*Aref*Cd0;
    return {schema:'AEGIS_STANDARD_CD0_BUILDUP_POINT_V48_WIP14A9',diagnosticOnly:true,band,powerState:powered?'POWERED':'UNPOWERED',altitudeM,mach,diameterM,lengthM,referenceAreaM2:Aref,temperatureK:atm.temperatureK,rhoKgM3:atm.rhoKgM3,speedOfSoundMps:atm.soundMps,speedMps:atm.speedMps,dynamicPressurePa:atm.qPa,dynamicViscosityPaS:atm.dynamicViscosityPaS,reynoldsNumber,cfFlatPlate,bodyWettedAreaM2,finWettedAreaM2,noseHalfAngleDeg:rad2deg(noseHalfAngleRad),components,Cd0,dragN,limitations:['TRANSITION_NOT_MODELED','ADIABATIC_OR_HOT_WALL_CORRECTION_NOT_MODELED','ROUGHNESS_BOUNDED_NOT_MEASURED','TRANSONIC_BRIDGE_IS_SIM_ASSUMPTION','PRODUCTION_FIN_AND_BASE_GEOMETRY_PUBLIC_UNKNOWN']};
  }
function wip14a9Smooth01(x){x=clamp(Number(x)||0,0,1);return x*x*(3-2*x);}
function wip14a9Atmosphere(altitudeM,mach){
    const base=wip14a7AtmosphereState(altitudeM,0),temperatureK=base.soundMps*base.soundMps/(1.4*287.05),dynamicViscosityPaS=1.458e-6*Math.pow(temperatureK,1.5)/(temperatureK+110.4),speedMps=Math.max(0,Number(mach)||0)*base.soundMps;
    return {...base,temperatureK,dynamicViscosityPaS,speedMps,mach:Number(mach)||0,qPa:.5*base.rhoKgM3*speedMps*speedMps};
  }
function wip14a7AtmosphereState(altM,speedMps=0){
    const altitudeM=clamp(Number(altM)||0,0,50000),soundMps=speedOfSoundMps(altitudeM),rhoKgM3=airDensityKgM3(altitudeM),speed=Math.max(0,Number(speedMps)||0);
    return {altitudeM,temperatureDerivedSoundMps:soundMps,soundMps,rhoKgM3,speedMps:speed,mach:speed/Math.max(1,soundMps),qPa:.5*rhoKgM3*speed*speed};
  }
const WIP14A9_RANGE=DATA["WIP14A9_RANGE"];
const WIP14A11_AERO_MODE=DATA["WIP14A11_AERO_MODE"];
function _wip156StepVlsInCell(m,dt,thrustN,massKg){
  const c=m?._vlsInCell;if(!c?.active)return false;
  const step=Math.max(0,Number(dt)||0),mass=Math.max(1,Number(massKg)||1),T=Math.max(0,Number(thrustN)||0);
  const ol=m._wip199VlsOriginMeta?wip148VlsCellLocal(m._wip199VlsOriginMeta):{xM:0,zM:0,deckM:0},f=shipGameFrameV1(),axis=f.vectorToWorld({x:0,y:0,z:1});
  const v0=Math.max(0,c.axialSpeedMps??0),v1=Math.max(0,v0+(T/mass-G0*axis.z)*step);
  c.axialSpeedMps=v1;c.travelM=Math.max(0,(c.travelM||0)+.5*(v0+v1)*step);
  const o=shipGamePointStateV1({x:ol.xM,y:ol.zM,z:ol.deckM+c.travelM}),angles=shipGameAnglesV1(axis);
  m.x=metersToWorld(o.xM);m.y=metersToWorld(o.yM);m.z=o.zM;
  // A near-vertical Mk41 cell axis has no useful azimuth.  Its tiny X/Y projection comes from
  // ship roll/pitch and can point exactly opposite the target, so preserve the intended launch
  // azimuth while the canister constrains position/velocity to the physical deck-normal axis.
  const launchAzimuth=Number.isFinite(c.launchAzimuthRad)?c.launchAzimuthRad:(Number.isFinite(m.heading)?m.heading:angles.az);
  m.heading=angNorm(launchAzimuth);m.pitch=angles.el;m.pitchRate=0;m.yawRate=0;m.rollRate=0;m.roll=0;
  m.finYaw=0;m.finPitch=0;m.tvcYaw=0;m.tvcPitch=0;m.tvcCmdYaw=0;m.tvcCmdPitch=0;m.tvcAuthority=0;
  const vx=o.vxMps+axis.x*v1,vy=o.vyMps+axis.y*v1,vz=o.vzMps+axis.z*v1,spd=Math.hypot(vx,vy,vz);
  m.vx=mpsToWorldSpeed(vx);m.vy=mpsToWorldSpeed(vy);m.vz=vz;m.speed=mpsToWorldSpeed(spd);m.velAngle=Math.hypot(vx,vy)>1e-9?Math.atan2(vy,vx):(m.heading??0);m.velPitch=Math.atan2(vz,Math.hypot(vx,vy));
  m.curG=1;m._vlsLaunchState={shipVxMps:o.vxMps,shipVyMps:o.vyMps,relativeVxMps:axis.x*v1,relativeVyMps:axis.y*v1,relativeVzMps:axis.z*v1,relativePitchDeg:angles.el*180/Math.PI};
  const distanceExit=c.travelM+1e-9>=Math.max(.01,c.effectiveTravelM||.01),timeoutExit=(m.life??0)+1e-9>=Math.max(.05,c.maxInCellTimeS||.30);
  if(distanceExit||timeoutExit){c.active=false;c.exitLifeS=m.life??0;c.exitSpeedMps=spd;c.exitVzMps=vz;c.exitReason=distanceExit?'DISTANCE':'MAX_TIME';m._vlsCellExited=true;m._vlsCellExitLifeS=c.exitLifeS;m._vlsCellExitSpeedMps=spd;m._vlsCellExitVzMps=vz;m._vlsCellExitReason=c.exitReason;if(m.isSM2ER)wip14a5Sm2ErStageEvent(m,'CELL_CLEAR');if(m.isSM6)wip14a6Sm6StageEvent(m,'CELL_CLEAR');}
  return true;
}
function wip14a6Sm6StageEvent(m,event){
    const st=m?._sm6Stage;if(!st||st.events.includes(event))return false;
    const next={STOWED:{CELL_CLEAR:'BOOST'},BOOST:{BOOST_BURNOUT:'SEPARATION'},SEPARATION:{BOOSTER_SEPARATED:'UPPER_STAGE'},UPPER_STAGE:{MISSION_END:'ENDED'}}[st.phase]?.[event];
    if(!next)return false;st.phase=next;st.stageIndex=(next==='UPPER_STAGE'||next==='ENDED')?1:0;st.events.push(event);
    if(event==='BOOSTER_SEPARATED'){
      const C=WIP14A6_SM6_STAGE_CONTRACT;m.boosterSeparated=true;m.tvcEnabled=false;m.tvcAuthority=0;m._v1TvcAuthority=0;m.tvcCmdYaw=0;m.tvcCmdPitch=0;m.tvcYaw=0;m.tvcPitch=0;
      m.arefM2=C.upperRefAreaM2;m.liftRefM2=C.upperLiftRefM2;st.boosterAttached=false;st.discardedBoosterKg=C.boosterDryKg;
      m.massKg=(m.missileDryKg??C.upperDryKg)+(m.boosterPropKg??0)+(m.sustainerPropKg??0);
    }
    st.eventLog.push({event,tS:m.life??0,altM:m.z??0,speedMps:worldSpeedToMps(m.speed??0),massKg:m.massKg??null});return true;
  }
function wip14a5Sm2ErStageEvent(m,event){
    const st=m?._sm2erStage;if(!st||st.events.includes(event))return false;
    const next={STOWED:{CELL_CLEAR:'BOOST'},BOOST:{BOOST_BURNOUT:'SEPARATION'},SEPARATION:{BOOSTER_SEPARATED:'UPPER_STAGE'},UPPER_STAGE:{MISSION_END:'ENDED'}}[st.phase]?.[event];
    if(!next)return false;st.phase=next;st.stageIndex=(next==='UPPER_STAGE'||next==='ENDED')?1:0;st.events.push(event);
    if(event==='BOOSTER_SEPARATED'){
      m.boosterSeparated=true;m.tvcEnabled=false;m.tvcAuthority=0;m._v1TvcAuthority=0;m.tvcCmdYaw=0;m.tvcCmdPitch=0;m.tvcYaw=0;m.tvcPitch=0;
      m.arefM2=WIP14A5_SM2ER_STAGE_CONTRACT.upperRefAreaM2;m.liftRefM2=WIP14A5_SM2ER_STAGE_CONTRACT.upperLiftRefM2;st.boosterAttached=false;st.discardedBoosterKg=WIP14A5_SM2ER_STAGE_CONTRACT.boosterDryKg;
      m.massKg=(m.missileDryKg??WIP14A5_SM2ER_STAGE_CONTRACT.upperDryKg)+(m.boosterPropKg??0)+(m.sustainerPropKg??0);
    }
    st.eventLog.push({event,tS:m.life??0,altM:m.z??0,speedMps:worldSpeedToMps(m.speed??0),massKg:m.massKg??null});
    return true;
  }
function shipGameAnglesV1(p){return {az:Math.atan2(p.y,p.x),el:Math.atan2(p.z,Math.hypot(p.x,p.y))};}
function shipGamePointStateV1(p){return {xM:p.x,yM:p.y,zM:p.z,vxMps:0,vyMps:0,vzMps:0};}
function shipGameFrameV1(){return {vectorToWorld:p=>({...p}),pointToWorld:p=>({...p}),pointToBody:p=>({...p}),vectorToBody:p=>({...p})};}
function wip148VlsCellLocal(meta){
 if(!meta)return {xM:0,zM:0,deckM:8.5};
 const sec=meta.section==='aft'?'aft':'fwd';
 // CG-52 has eight physical rows in BOTH banks and three crane gaps per bank.
 // A valid address is never clamped or relocated to a different installed cell.
 // Keep the DDG compatibility normalization exactly as before.
 const r=IS_BUNKER?Number(meta.row):Math.max(0,Math.min(sec==='aft'?7:3,Number(meta.row)||0)),col=IS_BUNKER?Number(meta.col):Math.max(0,Math.min(7,Number(meta.col)||0));
 const c=Number.isInteger(r)&&Number.isInteger(col)?shipCellRegistration(sec,r,col):null;
 if(!c)throw Error('VLS_UNINSTALLED_SLOT:'+sec+':'+r+':'+col);
 let x=c.x,y=c.y;
 if(meta.weaponType==='ESSM'){const q=clamp(Math.floor(Number(meta.quadIndex)||0),0,3),o=[[-.22,-.22],[.22,-.22],[-.22,.22],[.22,.22]][q];x+=o[0]*.649;y+=o[1]*.649;}
 return {xM:x,zM:y,deckM:c.z};
}
function shipCellRegistration(section,row,col){return shipAssetRegistration().cells[section]?.find(c=>c.row===row&&c.col===col)??null;}
function shipAssetRegistration(){return SELECTED_SHIP_REGISTRATION;}
let SELECTED_SHIP_REGISTRATION=DATA["SELECTED_SHIP_REGISTRATION"];
const IS_BUNKER=DATA["IS_BUNKER"];
function wip14a6AdvanceSm6Stage(m){
    if(!m?.isSM6||!m._sm6Stage)return;const C=WIP14A6_SM6_STAGE_CONTRACT,t=m.life??0,st=m._sm6Stage;
    if(st.phase==='STOWED'&&m._vlsCellExited)wip14a6Sm6StageEvent(m,'CELL_CLEAR');
    if(st.phase==='BOOST'&&t+1e-9>=C.mk72BurnS&&(m.boosterPropKg??0)<=1e-5)wip14a6Sm6StageEvent(m,'BOOST_BURNOUT');
    if(st.phase==='SEPARATION'&&t+1e-9>=C.separationS)wip14a6Sm6StageEvent(m,'BOOSTER_SEPARATED');
    st.boosterAttached=!m.boosterSeparated;st.massKg=m.massKg??null;st.boosterPropKg=m.boosterPropKg??0;st.upperPropKg=m.sustainerPropKg??0;
  }
function wip14a5AdvanceSm2ErStage(m){
    if(!m?.isSM2ER||!m._sm2erStage)return;
    const C=WIP14A5_SM2ER_STAGE_CONTRACT,t=m.life??0;
    if(m._sm2erStage.phase==='STOWED'&&m._vlsCellExited)wip14a5Sm2ErStageEvent(m,'CELL_CLEAR');
    if(m._sm2erStage.phase==='BOOST'&&t+1e-9>=C.mk72BurnS&&(m.boosterPropKg??0)<=1e-5)wip14a5Sm2ErStageEvent(m,'BOOST_BURNOUT');
    if(m._sm2erStage.phase==='SEPARATION'&&t+1e-9>=C.separationS)wip14a5Sm2ErStageEvent(m,'BOOSTER_SEPARATED');
    m._sm2erStage.boosterAttached=!m.boosterSeparated;m._sm2erStage.massKg=m.massKg??null;m._sm2erStage.boosterPropKg=m.boosterPropKg??0;m._sm2erStage.upperPropKg=m.sustainerPropKg??0;
  }
function propulsionPropellantKgBetween(m, t0, t1, reservoir=null){
    const schedule = m._propulsionSchedule;
    if(!schedule) return 0;
    let kg = 0;
    for(const seg of schedule){
      if(reservoir && seg.reservoir !== reservoir) continue;
      const imp = integrateLinearThrustSegmentNs(seg, t0, t1);
      const ispS = Math.max(1, Number(seg.ispS) || Number(m.ispS) || 250);
      kg += imp / (ispS * G0);
    }
    return kg;
  }
function integrateLinearThrustSegmentNs(seg, aS, bS){
    const a = clamp(aS, seg.startS, seg.endS);
    const b = clamp(bS, seg.startS, seg.endS);
    if(!(b > a) || !(seg.durationS > 0)) return 0;
    const u0 = (a - seg.startS) / seg.durationS;
    const u1 = (b - seg.startS) / seg.durationS;
    const t0 = lerp(seg.thrustStartN, seg.thrustEndN, u0);
    const t1 = lerp(seg.thrustStartN, seg.thrustEndN, u1);
    return 0.5 * (t0 + t1) * (b - a);
  }
const MISSILE_Q_MAX_PA=DATA["MISSILE_Q_MAX_PA"];
const MISSILE_Q_MIN_PA=DATA["MISSILE_Q_MIN_PA"];
const MISSILE_G_MIN_Q=DATA["MISSILE_G_MIN_Q"];
function _v1StepSarhSensorV1(){}
function gameFlightTerminationTickV48(m,dt){
    if(window.AEGIS_GAME_TERMINATION_ENABLED===false || m.dead || m.guidanceCore!=='v1' || !m._v1Profile)return false;
    const id=m._v1Profile.id;
    if(!['SM2MR_BLKIIIA_SIM','SM2ER_BLKIV_SIM','SM6_BLKIA_SIM','ESSM_BLK2_SIM'].includes(id))return false;
    const hasArh=id==='SM6_BLKIA_SIM'||id==='ESSM_BLK2_SIM';
    const sensorActive=hasArh?!!m.essmActiveSeeker:(!!m.sarhAlive||!!m._gameFlightTerm?.everTracked);
    if(!sensorActive)return false;
    const primary=hasArh?m._arhRfSeeker:m._sarhRfSeeker;
    const secondary=hasArh?m._sarhRfSeeker:null;
    const fresh=s=>s?.mode==='TRACK'&&s.trackValid===true&&Number.isFinite(s.lastHitAgeS)&&s.lastHitAgeS<=.30&&Number.isFinite(s.confidence)&&s.confidence>=.13;
    const useSarh=hasArh&&!fresh(primary)&&m.sarhAlive===true&&fresh(secondary);
    const s=useSarh?secondary:primary;
    const alternateGuidance=m.dlAlive===true&&m._v1TargetState?.isValid===true&&m._v1TargetState.source==='DL_TRACK';
    const aim=hasArh?(s?_arhEkfAim(s):null):(s?_sarhEkfAim(s):null);
    const own=samNavB1OwnState(m);
    const reason=gameFlightTerminationEvaluateV48(m,{
      profileId:id,kind:hasArh?'ARH':'SARH',sensorActive,alternateGuidance,
      observationKind:useSarh?'SARH':(hasArh?'ARH':'SARH'),
      nowS:m.life,mode:s?.mode||'OFF',trackValid:!!s?.trackValid,
      hitAgeS:Number(s?.lastHitAgeS??Infinity),confidence:Number(s?.confidence??0),
      trackPosM:aim?.posM??null,trackVelMps:aim?.velMps??null,
      ownPosM:own?.posM??null,ownVelMps:own?.velMps??null,
      // Read a *fuze outcome*, not truth-side CPA or physics collision state.
      fuzeDetonated:!!m.proxDetonated
    });
    if(!reason)return false;
    m._deathReason=reason;m._gameTermReason=reason;m.dead=true;
    debugLog('GAME_TERM: '+String(m.id)+' '+id+' '+reason+' life='+m.life.toFixed(2));
    return true;
  }
function gameFlightTerminationEvaluateV48(m,ob){
    if(!m || !ob || !ob.profileId || !ob.sensorActive)return null;
    const now=Number(ob.nowS)||0;
    const memo=m._gameFlightTerm||(m._gameFlightTerm={firstActiveS:now,lastGoodS:null,predictedCrossS:null,lastRangeM:null,lastState:'',everTracked:false});
    // GAME-TERM-SUPPORT-GUARD-V2: preserve native SARH/DL fallback authority.
    memo.lastState=String(ob.mode||'OFF');
    if(ob.alternateGuidance===true)memo.lastSupportS=now;
    const fresh=ob.mode==='TRACK' && ob.trackValid===true &&
      Number.isFinite(ob.hitAgeS) && ob.hitAgeS<=.30 &&
      Number.isFinite(ob.confidence) && ob.confidence>=.13;
    if(fresh && ob.trackPosM && ob.trackVelMps && ob.ownPosM && ob.ownVelMps){
      const dx=ob.trackPosM.x-ob.ownPosM.x,dy=ob.trackPosM.y-ob.ownPosM.y,dz=ob.trackPosM.z-ob.ownPosM.z;
      const rvx=ob.trackVelMps.x-ob.ownVelMps.x,rvy=ob.trackVelMps.y-ob.ownVelMps.y,rvz=ob.trackVelMps.z-ob.ownVelMps.z;
      const rng=Math.hypot(dx,dy,dz);
      const closing=rng>1?-(dx*rvx+dy*rvy+dz*rvz)/rng:0;
      memo.everTracked=true;memo.lastGoodS=now;memo.lastRangeM=rng;memo.lastTrackKind=ob.observationKind??ob.kind;
      memo.lastClosingMps=closing;
      // Update predicted crossing time from current *observed local track*, not from Kappa's capped TGO.
      // Only use terminal-range track snapshots as a terminal-expiry clock.
      if(rng<=35000 && closing>120){
        const remaining=rng/closing; // SIM_TUNED policy: no guidance-style TGO cap in the expiry clock
        memo.predictedCrossS=now+remaining;
        memo.lastTgoS=remaining;
      }
      return null;
    }
    if(ob.alternateGuidance===true)return null;
    const supportGapS=memo.lastSupportS==null?Infinity:now-memo.lastSupportS;
    const searching=['SEARCH','COAST','REACQUIRE','LOST'].includes(String(ob.mode||'OFF'));
    const sinceGood=memo.lastGoodS==null?Infinity:(now-memo.lastGoodS);
    const pastCross=memo.predictedCrossS!=null&&now>=memo.predictedCrossS+2.5;
    // A prior fresh terminal track, expired expected crossing, no physical fuze outcome,
    // and a continuous local observation gap together justify a game terminal miss.
    if(memo.everTracked && searching && sinceGood>=2.5 && supportGapS>=2.5 && pastCross && !ob.fuzeDetonated){
      return 'TERMINAL_MISS_POST_CROSS';
    }
    // Search-only missiles must not linger forever after *onboard seeker activation*.
    // This fallback is ARH-only: SARH still has ship-side guidance/illumination paths.
    if(ob.kind==='ARH' && !memo.everTracked && searching && now-Math.max(memo.firstActiveS,memo.lastSupportS??memo.firstActiveS)>=12 && !ob.fuzeDetonated){
      return 'TERMINAL_SEARCH_NO_ACQUISITION';
    }
    return null;
  }
function _sarhEkfAim(s){if(!s?._kfX||!s.trackValid)return null;return {posM:{x:s._kfX[0],y:s._kfX[1],z:s._kfX[2]},velMps:{x:s._kfX[3],y:s._kfX[4],z:s._kfX[5]}};}
function _arhEkfAim(s){if(!s?._kfX||!s.trackValid)return null;return {posM:{x:s._kfX[0],y:s._kfX[1],z:s._kfX[2]},velMps:{x:s._kfX[3],y:s._kfX[4],z:s._kfX[5]}};}
function weaponLinkB3Tick(){}
function samNavB1Update(m,dt){if(!m||m.guidanceCore!=='v1'||!m._v1Profile)return null;return missileNavB2Update(m,dt);}
function vlsReleaseEssmB1(opts={}){
    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok)return;
    if(!shipGameVlsReadyV1('ESSM'))return;
    // VLS damage check
    const _vlsDmgE = getShipDamageEffects();
    if(!_vlsDmgE.vlsAvailable){
      notify('⚠ VLS 발사 불가 — 전력/발사관 피해!');
      return;
    }
    if(_vlsDmgE.combatEff < 0.15){
      notify('⚠ 전투체계 심각 손상 — 사격통제 불가!');
      return;
    }
    // WIP111 ESSM EMCON doctrine: Block 2 ARH terminal autonomy does not create an EMCON fire-control track.
    // Until an ESM/external-DL fire-control-quality track path exists, ESSM launch doctrine remains BLOCK_FIRE.
    if(emconActive && ESSM_EMCON_POLICY === 'BLOCK_FIRE'){ notify('EMCON 중 — 발사 불가'); return; }
    if(selectedLockId == null){ notify('락온 없음'); return; }

    const ax = aircraft.x(), ay = aircraft.y();
    const tr = tracks.get(selectedLockId);
    const surfaceSelected=surfaceTrackWip13C5(tr);
    const surfaceRelease=surfaceSelected?surfaceEssmLiveReleaseGateWip13C6(selectedLockId,{mode:engagementControlMode,automatic:opts.automatic===true}):null;
    if(surfaceRelease){
      if(!surfaceRelease.ok){notify(`⚠ ESSM 대수상 발사 차단 — ${surfaceRelease.reason}`);return;}
    }else{
      if(!trackIsFireControlQuality(tr)){notify('⚠ ESSM 사격통제 품질 트랙 없음');return;}
      const a3Gate=trackEngagementGateA3(selectedLockId,{automatic:opts.automatic===true});
      if(!a3Gate.ok){notify(`⚠ ESSM 교전 차단 — ${trackA3ReasonKo(a3Gate.reason)}`);return;}
    }

    const tx = tr.x;
    const ty = tr.y;
    const initHeading = Math.atan2(ty - ay, tx - ax);
    const v0Mps = 0; // WIP156: true in-cell ignition from launcher-relative rest
    const launch0 = _vlsVerticalLaunchState(v0Mps,initHeading);
    const initVelPitch = launch0.velPitch;
    const v0 = launch0.speed;
    const vz0 = launch0.vz;
    const launchBodyHeading = initHeading; // WIP157: vertical-body azimuth is assigned to the intended pitchover bearing; ship velocity remains only in velAngle/vx/vy

    const seedX = tr.x;
    const seedY = tr.y;
    const seedVx = tr.vx;
    const seedVy = tr.vy;
    const seedZ  = surfaceRelease?(surfaceRelease.fireControl?.handoffState?.zM??tr.z??0):(tr.z??OWN_ALT_M);
    const seedVz = tr.vz ?? 0;

    const m = {
      id: missileSerial++,
      spawnTime: performance.now(),
      isESSM: true, // flag for ESSM-specific behavior

      x: ax, y: ay,
      z: 0,
      pitch: launch0.bodyPitch,
      velPitch: initVelPitch,
      vz: vz0,              // consistent with speed + flight-path angle
      vlsPhase: true,

      heading: launchBodyHeading,
      velAngle: launch0.velAngle,
      speed: v0,
      vx: launch0.vx,
      vy: launch0.vy,
      _vlsLaunchState:{shipVxMps:launch0.shipVxMps,shipVyMps:launch0.shipVyMps,relativeVxMps:0,relativeVyMps:0,relativeVzMps:v0Mps,relativePitchDeg:90},
      _vlsInCell:_wip156CreateVlsInCellState(true,launchBodyHeading),

      // --- ESSM Block 2 Physics ---
      seekerType: 'ESSM',   // dual-mode: active + semi-active
      massKg:     280,       // SIM_TUNED Block 2 launch mass
      missileDryKg: 160.7, // WIP136 launch dry mass = 280 - 119.3 kg; TVC jettison later subtracts fixed hardware mass
      boosterPropKg: 0,
      sustainerPropKg: 119.3,
      boosterCasingKg: 0,   // integral motor (no jettison)
      boosterSeparated: true, // no booster to separate
      ispS:       256.4248649567, // WIP136 provisional sweep center; runtime resolver may vary
      arefM2:     Math.PI*.127*.127, // physical 254 mm frontal reference
      liftRefM2:  0.13,
      cdScale: 1.0,          // dedicated ESSM_254 curve owns zero-lift Cd
      cdA: MISSILE_CDA * 0.7,
      inducedDragK: 0.04,    // more efficient fins

      // --- Guidance / autopilot ---
      pnN0: 5.2,
      pnNCloseGain: 3.0,
      pnLosBiasK: 0.25,
      apTauBase: 0.07,
      apQrefPa: 14000,
      pnTgoDampS: 0.30,

      // TVC: aggressive boost-phase vectoring.  Values are SIM_TUNED for the requested
      // near-cell pitch-over; they are not asserted as public ESSM Block 2 actuator data.
      tvcEnabled: true,
      tvcDuration: 4.0,  // WIP136 fail-safe max; normal separation follows pitch-over completion
      // --- Full TVC model state (populated incrementally across stages) ---
      // Geometry: thrust-vector deflection limits (deg)
      tvcMaxDeflectYawDeg: 22,
      tvcMaxDeflectPitchDeg: 22,
      // Actuator slew rates (deg/s).  Fast enough to reach hard-over almost immediately after cell clear.
      tvcSlewRateYawDeg: 360,
      tvcSlewRatePitchDeg: 360,
      // Current commanded vs actual nozzle angles (radians, populated at runtime)
      tvcCmdYaw: 0,
      tvcCmdPitch: 0,
      tvcYaw: 0,
      tvcPitch: 0,
      // Authority scheduling: falls off with time and dynamic pressure
      tvcAuthority: 0,
      tvcEffEndQ: 50000,  // Pa — TVC stays effective to higher q (ESSM is aggressive)
      // Moment arm from nozzle to CoG (meters) — for torque calc
      tvcMomentArmM: 1.70,
      // The same nozzle lateral force causes BOTH translation and torque; do not partition it.
      tvcForceFracForMoment: 1.0,
      tvcForceFracForTranslation: 1.0,

      // WIP136 documentation mirrors only; initializeMissileV1 resolves the 8 s concentric-grain schedule.
      thrust1N:  0,
      burn1:     0,
      thrust2Start: 0, thrust2Mid:0, thrust2End:0, thrust2N:0,
      burn2:     8.0, burn2Sus:8.0, thrust3Coast:0,
      burnTotal: 8.0,

      minSpeed: mpsToWorldSpeed(0.25 * MACH1_MPS),
      stallSpeed: mpsToWorldSpeed(0.35 * MACH1_MPS),

      gLimit: 55.0,
      curG: 1.0,

      aoaMax: deg(65.0),
      noseKp: 5.2,
      noseKp0: 5.2,
      velFollowK: 3.4,  // ESSM: fast velocity vector following
      velFollowK0: 2.2,
      aoaEnergyLossK: 0.15,   // ESSM: optimized for high-G
      gEnergyLossK: 0.12,

      terminalBlendStartKm: 12.0,   // shorter terminal transition
      terminalBlendEndKm:   6.0,

      state: 'IOG',
      dlAlive: false,
      assignedTargetId: selectedLockId,
      _surfaceArh:surfaceRelease?{
        schema:'AEGIS_ESSM_SURFACE_ARH_RUNTIME_V48_WIP13C6',mode:'SURFACE_ARH',trackId:selectedLockId,
        aimHeightM:seedZ,launchFcsQuality01:Number(surfaceRelease.fireControl?.quality01)||0,
        launchBasketMargin:Number(surfaceRelease.fireControl?.acquisitionBasketMargin)||0,truthUsed:false
      }:null,

      pitbullKm: 16.0,       // active seeker ON at 16km
      essmActiveSeeker: false, // active seeker state
      // WIP37: Block 2 retains a semi-active receive path. It may accept SPG-62 support
      // before/while ARH is active; ARH and SARH keep independent local tracks.
      sarhReceiverStandby: true,
      _sarhRawQ: 0,
      _sarhStableQ: 0,
      _sarhStableTime: 0,
      _sarhAcquireThresh: 0.30,
      _sarhMaintainThresh: 0.16,

      seekerMaxRangeKm: 14.0,
      seekerMinRangeKm: 6.0,
      seekerRangeKm:    14.0,
      seekerFov: deg(14),
      gimbalMax: deg(75),     // wider gimbal
      seekerSlewRate: deg(350),
      seekerAngle: initHeading,

      seekerLocked: false,
      seekerLockType: null,
      seekerLockId: null,
      seekerLockedPrev: false,

      seekerNoTargetTimer: 0,
      seekerNoTargetLimit: 60.0,

      lockStickiness: 2.2,
      chaffResistance: 0.65,
      flareResistance: 1.0,
      fovGateLoose: 1.4,
      fovLockLoose: 1.2,

      irccmGatewidthEnabled: false,
      irccmGateTimer: 0,
      irccmGateDuration: 0,
      irccmNarrowScale: 1.0,
      irccmLastTargetAngle: initHeading,
      irccmLastTargetId: selectedLockId,

      seekerNotchLossBasePerSec: 0.5,

      lastCmdX: seedX,
      lastCmdY: seedY,
      lastCmdVx: seedVx,
      lastCmdVy: seedVy,
      lastCmdZ:  seedZ,
      lastCmdVz: seedVz,
      iogAge: 0,

      closestKm: 999,
      afterClosestTimer: 0,
      // Radar_v6_12 style proximity fuze state
      proxArmRangeKm: ESSM_BLOCK2_TDD_SIM.armingRangeKm,
      proxArmed: false,
      proxMissDistKm: 999,
      proxDetonated: false,
      missedTarget: false,
      pitchoverPhase: false,
      pitchoverTimer: 0,
      pitchoverDuration: 1.35,  // WIP40 diagnostic deadline; completion is alignment/velocity/clearance-gated, never timer-only
      coastHold: false,

      life: 0,
      maxLife: 60.0,         // 60s max flight (shorter than SM-2)
      dead: false
    };

    // WIP111: ESSM EMCON launch is BLOCK_FIRE and is already rejected before target/launch processing above.
    // Block 2 ARH terminal autonomy does not by itself provide a fire-control-quality track under EMCON.
    // Permitting EMCON engagement requires an ESM/external-DL track-acquisition path first; the old
    // unreachable "degraded EMCON launch" notification was removed rather than reviving partial doctrine.
    const _wip148LaunchMeta=wip148PeekVlsLaunchMeta('ESSM');
    if(!consumeVlsCell('ESSM')){ notify('⚠ ESSM 잔탄 없음!'); return; }
    wip199BindPhysicalVlsOrigin(m,_wip148LaunchMeta);
    // === v1 Guidance activation: SM-2 and ESSM ===
    if(m.isESSM){
      initializeMissileV1(m, 'ESSM_BLK2_SIM');
    } else {
      initializeMissileV1(m, 'SM2MR_BLKIIIA_SIM');
    }
    tagWorldEntityOwnershipV48Wip11A(m,'FRIENDLY_ORDNANCE',ACTIVE_SHIP_RUNTIME.entityId);
    missiles.push(m);
    const tgtLabel = trackDisplayLabelById(selectedLockId);
    notify(`ESSM${surfaceRelease?' 대수상':''} 발사: E${m.id} → ${tgtLabel}`);
    allocateDatalinks();
  }
function allocateDatalinks(){for(const m of missiles)m.dlAlive=true;}
function trackDisplayLabelById(){return "ENV_TARGET";}
function initializeMissileV1(m, profileId){
    // LEGACY_COMPARE 테스트 모드: 홀수 id는 legacy 유지 → 동일 조건 비교
    if(GUIDANCE_TEST_MODE === 'LEGACY_COMPARE' && (m.id % 2 === 1)){
      m.guidanceCore = 'legacy';
      debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} legacy fallback used (LEGACY_COMPARE)`);
      return;
    }
    m.guidanceCore = 'v1';
    m._v1Profile = SAM_MISSILE_PROFILES[profileId];
    if(!m._v1Profile){
      console.warn('Unknown v1 profile:', profileId);
      m.guidanceCore = 'legacy';
      debugLog(`v1: ${m.id} legacy fallback used (unknown profile ${profileId})`);
      return;
    }
    const prof = m._v1Profile;
    m._wip79MidcourseMode=((prof.id==='SM2MR_BLKIIIA_SIM'||prof.id==='SM2ER_BLKIV_SIM'||prof.id==='SM6_BLKIA_SIM'))?String(window.WIP79_SM2_MIDCOURSE_MODE||'LEGACY'):'LEGACY';
    m._wip79KappaTerminalPolicy=String(window.WIP79_KAPPA_TERMINAL_POLICY||'PIP_LOS');
    m._wip79KappaEligible=null;m._wip79ThreeSecEntry=null;
    m._samLoftProfile = SAM_LOFT_PROFILE_REGISTRY[prof.loftProfileId] || null;
    applySamPhysicalProfile(m, prof);
    if(prof.id==='ESSM_BLK2_SIM'){
      m._wip136TvcJettisoned=false;m._wip136TvcJettisonMassKg=window.WIP136_ESSM_TVC_JETTISON_KG;
      m._wip136TvcInertiaArmM=1.50;m._wip136TvcInstalledDragFactor=window.WIP136_ESSM_TVC_INSTALLED_DRAG_FACTOR;
      m._wip136TvcJetVaneEff=window.WIP136_ESSM_TVC_JETVANE_EFF;
    }
    initializeSamSixDofLite(m);
    // 6DOF structural limit is authoritative when enabled; legacy/profile limit remains fallback.
    m.gLimit = m.samSixDofEnabled ? (m.gLimitHard ?? prof.maxGSeaLevel ?? m.gLimit) : (prof.maxGSeaLevel ?? m.gLimit);
    m._v1ArhState = 'OFF';
    m._v1Mem = null;
    m._v1SarhWasAlive = false;
    samNavB1Init(m,true);samB1InitializeLaunchCue(m);weaponLinkB3Init(m);
    if(wip14a8IsStandardMissile(m))m._wip14a10AeroMode=STANDARD_AERO_KERNEL;
    m._windBasisPrev=null;m._windBasisTelemetry=wip14a12NewTelemetry();m._wip14a12DisposedBasisTelemetry=null;
    debugLog(`v1: ${m.isESSM?'E':'M'}${m.id} initialized ${profileId} (mass=${m.massKg}kg gLim=${m.gLimit}G)`);
  }
function weaponLinkB3Init(){}
function samB1InitializeLaunchCue(m){
    if(!m||m._b1LaunchCue)return m?._b1LaunchCue??null;
    if(!Number.isFinite(m.lastCmdX)||!Number.isFinite(m.lastCmdY))return null;
    const st={isValid:true,source:'LAUNCH_INIT',confidence:.35,noiseSigmaM:120,posM:{x:worldToMeters(m.lastCmdX),y:worldToMeters(m.lastCmdY),z:Number(m.lastCmdZ)||0},velMps:{x:worldSpeedToMps(m.lastCmdVx??0),y:worldSpeedToMps(m.lastCmdVy??0),z:Number(m.lastCmdVz)||0}};
    m._b1LaunchCue=_samB1TrackLikeFromState(m,st,'LAUNCH_INIT');return m._b1LaunchCue;
  }
function _samB1TrackLikeFromState(m,st,label='STATE'){
    if(!st?.isValid||!st.posM||!st.velMps)return null;const sig=Math.max(8,Number(st.noiseSigmaM)||50),q=clamp(Number(st.confidence)||.1,.05,1),P=_samB1CovarianceFromSigma(sig,Math.max(2,sig*.08),sig);
    return {id:m.assignedTargetId??null,x:metersToWorld(st.posM.x),y:metersToWorld(st.posM.y),z:st.posM.z,vx:mpsToWorldSpeed(st.velMps.x),vy:mpsToWorldSpeed(st.velMps.y),vz:st.velMps.z,confirmed:true,sensorDetected:true,ttl:1,sensorAge:0,fireControlQuality:q,trackQuality:q,kinematicQuality:q,sensorSource:`B1_${label}_${st.source??'UNKNOWN'}`,_kfX:new Float64Array([st.posM.x,st.posM.y,st.posM.z,st.velMps.x,st.velMps.y,st.velMps.z]),_kfP:P,_b1GuidanceCue:true,_b1Source:st.source??label};
  }
function _samB1CovarianceFromSigma(posSigmaM=80,velSigmaMps=25,altSigmaM=posSigmaM){
    const P=new Float64Array(36),pp=Math.max(1,posSigmaM)**2,vv=Math.max(.1,velSigmaMps)**2,aa=Math.max(1,altSigmaM)**2;P[0]=pp;P[7]=pp;P[14]=aa;P[21]=vv;P[28]=vv;P[35]=vv;return P;
  }
function initializeSamSixDofLite(m){
    const p=_samSixDofProfileFor(m);
    if(!p?.enabled){m.samSixDofEnabled=false;return;}
    m.samSixDofEnabled=true;m._samSixDof=p;
    const gl=wip138EssmGLimits(p);m.gLimitHard=gl.structuralG;m.gLimitOptimal=gl.optimalG;m.gLimit=m.gLimitOptimal;
    m.gMinQ=p.gMinQ??1.2;m.gQminPa=p.gQminPa??5000;m.gQmaxPa=p.gQmaxPa??70000;
    m.yawRate=m.yawRate??0;m.pitchRate=m.pitchRate??0;m.rollRate=m.rollRate??0;m.roll=m.roll??0;
    m.finYaw=m.finYaw??0;m.finPitch=m.finPitch??0;
    m.tvcYaw=m.tvcYaw??0;m.tvcPitch=m.tvcPitch??0;m.tvcCmdYaw=0;m.tvcCmdPitch=0;
    m.availableG=1;m.sam6dofActualNormalG=0;m._sam6dofAlignAltM=null;
    // WIP48: make induced-drag geometry explicit per 6DOF profile. Values currently preserve
    // the WIP47 fallback behavior; future missile-specific tuning can change them independently.
    m.aspectRatio=p.aspectRatio??m.aspectRatio??3.0;m.oswaldEff=p.oswaldEff??m.oswaldEff??0.80;
    m.sam6dofDeliveredG=0;m._v1GDeliveryGuidanceRatio=null;m._v1GDeliveryControlRatio=null;
    m._v1GDeliveryGuidanceEma=null;m._v1GDeliveryControlEma=null;m._v1GDeliveryValid=false;
    m._samPrevNormalAccWorld={x:0,y:0,z:0};m._samFinAccelYawFilt=0;m._samFinAccelPitFilt=0;
    m._samFinAccelIntYaw=0;m._samFinAccelIntPit=0;m._samFinAccelPrevYawReq=0;m._samFinAccelPrevPitReq=0;
    m._samFinAccelLoopActive=false;m._sam6dofAuthorityReady=false;
  }
function applySamPhysicalProfile(m, prof){
    if(!m || !prof) return;
    const physicalContract=wip127ResolveSamPhysicalContract(prof);
    const propulsion=physicalContract.propulsion??prof.propulsion;
    const budget = derivePropulsionBudget(propulsion);
    const launchMassKg = Math.max(1, Number(prof.massKg) || m.massKg || MISSILE_MASS_KG);
    const derivedDryMassKg = launchMassKg - budget.propellantKg;
    const dryMassKg = Number.isFinite(physicalContract.dryMassKg)?Number(physicalContract.dryMassKg):derivedDryMassKg;
    const boosterDryMassKg=Math.max(0,Number(physicalContract.boosterDryMassKg)||0);
    if(!(dryMassKg > 0)) throw new Error(`${prof.id}: propulsion propellant exceeds launch mass`);
    if(Number.isFinite(physicalContract.dryMassKg)&&Math.abs((dryMassKg+boosterDryMassKg+budget.propellantKg)-launchMassKg)>1e-6){
      throw new Error(`${prof.id}: explicit dry/booster/propellant/launch mass mismatch`);
    }

    m.massKg = launchMassKg;
    m.missileDryKg = dryMassKg;
    m.boosterPropKg = budget.byReservoir.boost || 0;
    m.sustainerPropKg = budget.byReservoir.sustain || 0;
    m.boosterCasingKg = boosterDryMassKg;
    m.boosterSeparated = !physicalContract.twoStage;
    m.ispS = budget.ispS;
    m._propulsionSchedule = budget.schedule;
    m._propulsionModel = propulsion?.model ?? 'PROFILE_SEGMENTS';
    m._propulsionMotor = propulsion?.motor ?? 'SIM';
    m._mk104Profile = physicalContract.mk104Profile;
    m._mk72Profile=physicalContract.mk72Profile??null;m.isSM2ER=prof.id==='SM2ER_BLKIV_SIM'||!!m.isSM2ER;m.isSM6=prof.id==='SM6_BLKIA_SIM'||!!m.isSM6;
    m.tvcEnabled=!!prof.tvcEnabled;m.tvcDuration=Number(prof.tvcDurationSec)||0;
    if(m.isSM2ER){const C=WIP14A5_SM2ER_STAGE_CONTRACT;m._visualProfileId=C.visualProfileId;m._sm2erStage={schema:'AEGIS_SM2ER_STAGE_V48_WIP14A5',phase:'STOWED',stageIndex:0,boosterAttached:true,events:[],eventLog:[],discardedBoosterKg:0,massKg:launchMassKg,boosterPropKg:C.boosterPropKg,upperPropKg:C.upperPropKg};m.arefM2=C.attachedRefAreaM2;m.liftRefM2=C.attachedLiftRefM2;}
    if(m.isSM6){const C=WIP14A6_SM6_STAGE_CONTRACT;m._visualProfileId=C.visualProfileId;m._sm6Stage={schema:'AEGIS_SM6_STAGE_V48_WIP14A6',phase:'STOWED',stageIndex:0,boosterAttached:true,events:[],eventLog:[],discardedBoosterKg:0,massKg:launchMassKg,boosterPropKg:C.boosterPropKg,upperPropKg:C.upperPropKg};m.arefM2=C.attachedRefAreaM2;m.liftRefM2=C.attachedLiftRefM2;}
    m._mk104BoostFraction = propulsion?.wip127?.boostFraction ?? null;
    m._mk104BoostTimeS = propulsion?.wip127?.boostTimeS ?? null;
    m._mk104SustainFraction = propulsion?.wip127?.sustainFraction ?? null;
    m._mk104SustainTimeS = propulsion?.wip127?.sustainTimeS ?? null;
    m._propulsionActiveBurnTotalS = propulsion?.wip127?.burnTotalS ?? budget.schedule.filter(seg=>Math.max(seg.thrustStartN,seg.thrustEndN)>0).reduce((a,seg)=>a+seg.durationS,0);
    m._propulsionSequenceEndS = budget.burnTotalS;
    m._propulsionInitialKg = budget.propellantKg;
    m._propulsionExpectedImpulseNs = budget.totalImpulseNs;

    // Compatibility timing fields used by legacy pitchover/low-speed gates.
    const boostEnd = budget.schedule.find(seg => seg.reservoir !== 'boost')?.startS ?? budget.burnTotalS;
    m.burn1 = boostEnd;
    m.burn2 = Math.max(0, budget.burnTotalS - boostEnd);
    const activeSustain = budget.schedule.filter(seg => seg.reservoir === 'sustain' && seg.name !== 'TAILOFF')
      .reduce((acc, seg) => acc + seg.durationS, 0);
    m.burn2Sus = activeSustain;
    m.burnTotal = budget.burnTotalS;

    // Legacy debug fields mirror the profile but do not drive v1 thrust anymore.
    const boostSeg = budget.schedule.find(seg => seg.reservoir === 'boost');
    const sustainSeg = budget.schedule.find(seg => seg.name === 'SUSTAIN') || budget.schedule.find(seg => seg.reservoir === 'sustain');
    const tailSeg = budget.schedule.find(seg => seg.name === 'TAILOFF');
    m.thrust1N = boostSeg?.thrustStartN ?? 0;
    m.thrust2Start = sustainSeg?.thrustStartN ?? 0;
    m.thrust2Mid = sustainSeg ? 0.5 * (sustainSeg.thrustStartN + sustainSeg.thrustEndN) : 0;
    m.thrust2End = sustainSeg?.thrustEndN ?? 0;
    m.thrust2N = m.thrust2Mid;
    m.thrust3Coast = tailSeg ? 0.5 * (tailSeg.thrustStartN + tailSeg.thrustEndN) : 0;

    if(!m.isSM2ER&&!m.isSM6)m.arefM2 = prof.refAreaM2 ?? m.arefM2 ?? MISSILE_AREF_M2;
    if(!m.isSM2ER&&!m.isSM6)m.liftRefM2 = prof.aero?.liftRefM2 ?? m.liftRefM2 ?? MISSILE_LIFTREF_M2;
    m.cdScale = prof.aero?.cdScale ?? m.cdScale ?? 1.0;
    m.inducedDragK = prof.aero?.inducedDragK ?? m.inducedDragK ?? 0.05;
    m.cdA = m.arefM2 * MISSILE_CD0; // compatibility/debug only; force model uses arefM2 + Cd(M)
    if(prof.maxFlightTimeS != null) m.maxLife = Math.max(m.burnTotal + 5, prof.maxFlightTimeS);

    // Keep the launch-mass identity explicit for regression diagnostics.
    const reconstructed = m.missileDryKg + m.boosterCasingKg + m.boosterPropKg + m.sustainerPropKg;
    if(Math.abs(reconstructed - launchMassKg) > 1e-6){
      throw new Error(`${prof.id}: mass budget mismatch ${reconstructed} vs ${launchMassKg}`);
    }
  }
function derivePropulsionBudget(propulsion){
    const schedule = buildPropulsionSchedule(propulsion);
    const defaultIspS = Math.max(1, Number(propulsion?.ispS) || 250);
    const byReservoir = {};
    let totalImpulseNs = 0, propellantKg = 0;
    for(const seg of schedule){
      const imp = integrateLinearThrustSegmentNs(seg, seg.startS, seg.endS);
      const segIspS = Math.max(1, Number(seg.ispS) || defaultIspS);
      const segPropKg = imp / (segIspS * G0);
      totalImpulseNs += imp;
      propellantKg += segPropKg;
      byReservoir[seg.reservoir] = (byReservoir[seg.reservoir] || 0) + segPropKg;
    }
    // Whole-motor effective Isp, preserving old behavior for equal-Isp motors.
    const ispS = propellantKg > 0 ? totalImpulseNs / (propellantKg * G0) : defaultIspS;
    const burnTotalS = schedule.length ? schedule[schedule.length-1].endS : 0;
    return { schedule, ispS, totalImpulseNs, propellantKg, byReservoir, burnTotalS };
  }
function buildPropulsionSchedule(propulsion){
    const src = propulsion?.segments ?? [];
    let cursor = 0;
    return src.map((seg, idx) => {
      const durationS = Math.max(0, Number(seg.durationS) || 0);
      const out = {
        name: seg.name ?? `SEG${idx+1}`,
        reservoir: seg.reservoir ?? 'sustain',
        startS: cursor,
        endS: cursor + durationS,
        durationS,
        thrustStartN: Math.max(0, Number(seg.thrustStartN) || 0),
        thrustEndN: Math.max(0, Number(seg.thrustEndN ?? seg.thrustStartN) || 0),
        // WIP133: optional segment-specific effective Isp; legacy profiles fall back to propulsion.ispS.
        ispS: Math.max(1, Number(seg.ispS ?? propulsion?.ispS) || 250)
      };
      cursor = out.endS;
      return out;
    });
  }
function wip127ResolveSamPhysicalContract(prof){
    if(prof?.id==='SM6_BLKIA_SIM'){const C=WIP14A6_SM6_STAGE_CONTRACT;return {propulsion:wip14a6BuildSm6Propulsion(),dryMassKg:C.upperDryKg,boosterDryMassKg:C.boosterDryKg,twoStage:true,boosterSeparationS:C.separationS,mk104Profile:'CORRECTED',mk72Profile:'WIP14A6_WORKING'};}
    if(prof?.id==='SM2ER_BLKIV_SIM'){const C=WIP14A5_SM2ER_STAGE_CONTRACT;return {propulsion:wip14a5BuildSm2ErPropulsion(),dryMassKg:C.upperDryKg,boosterDryMassKg:C.boosterDryKg,twoStage:true,boosterSeparationS:C.separationS,mk104Profile:'CORRECTED',mk72Profile:'WIP14A5_WORKING'};}
    const essm=wip136ResolveEssmPhysicalContract(prof);
    if(essm)return {...essm,mk104Profile:null};
    if(!(prof?.id==='SM2MR_BLKIIIA_SIM'||prof?.id==='SM2ER_BLKIV_SIM'||prof?.id==='SM6_BLKIA_SIM'))return {propulsion:prof?.propulsion,dryMassKg:null,mk104Profile:null};
    const mode=String(window.MK104_PROFILE||'CORRECTED').toUpperCase();
    if(mode==='LEGACY')return {propulsion:prof.propulsion,dryMassKg:null,mk104Profile:'LEGACY'};
    return {propulsion:wip127BuildMk104CorrectedPropulsion(),dryMassKg:WIP127_MK104_CORRECTED.missileDryKg,mk104Profile:'CORRECTED'};
  }
const WIP127_MK104_CORRECTED=DATA["WIP127_MK104_CORRECTED"];
function wip127BuildMk104CorrectedPropulsion(boostFraction=window.WIP127_MK104_BOOST_FRACTION,boostTimeS=window.WIP127_MK104_BOOST_TIME_S){
    const C=WIP127_MK104_CORRECTED,f=clamp(Number(boostFraction)||.50,.01,.99),boostS=clamp(Number(boostTimeS)||4.5,.05,C.burnTotalS-.05),sustainS=C.burnTotalS-boostS;
    const boostIspS=WIP133_MK104_BOOST_ISP_S,sustainIspS=WIP133_MK104_SUSTAIN_ISP_S;
    // WIP133 canonical: propellant mass split is fixed independently from phase impulse.
    // Each phase impulse is derived from its propellant mass and effective Isp.
    const boostPropKg=C.propellantKg*f,sustainPropKg=C.propellantKg*(1-f);
    const boostImpulseNs=boostPropKg*boostIspS*G0,sustainImpulseNs=sustainPropKg*sustainIspS*G0;
    const totalImpulseNs=boostImpulseNs+sustainImpulseNs;
    const boostThrustN=boostImpulseNs/boostS,sustainThrustN=sustainImpulseNs/sustainS;
    return {
      model:'INTEGRAL_DUAL_THRUST_SOLID_FIXED_PHASE_ISP',motor:C.motor,ispS:C.ispS,
      wip127:{profile:'CORRECTED',boostFraction:f,sustainFraction:1-f,boostTimeS:boostS,sustainTimeS:sustainS,burnTotalS:C.burnTotalS,boostThrustN,sustainThrustN,totalImpulseNs,missileDryKg:C.missileDryKg,boostIspS,sustainIspS,phaseIspSourceClass:'SIM_TUNED_ASSUMED_FORMULATION_DIFFERENCE'},
      segments:[
        {name:'BOOST',reservoir:'boost',durationS:boostS,thrustStartN:boostThrustN,thrustEndN:boostThrustN,ispS:boostIspS},
        {name:'SUSTAIN',reservoir:'sustain',durationS:sustainS,thrustStartN:sustainThrustN,thrustEndN:sustainThrustN,ispS:sustainIspS}
      ]
    };
  }
const WIP133_MK104_SUSTAIN_ISP_S=DATA["WIP133_MK104_SUSTAIN_ISP_S"];
const WIP133_MK104_BOOST_ISP_S=DATA["WIP133_MK104_BOOST_ISP_S"];
function wip136ResolveEssmPhysicalContract(prof){
    if(prof?.id!=='ESSM_BLK2_SIM')return null;
    return {propulsion:wip136BuildEssmPropulsion(),dryMassKg:WIP136_ESSM_CONTRACT.launchDryKg,essmContract:WIP136_ESSM_CONTRACT};
  }
const WIP136_ESSM_CONTRACT=DATA["WIP136_ESSM_CONTRACT"];
function wip136BuildEssmPropulsion(avgIspS=window.WIP136_ESSM_AVG_ISP_S,deltaS=window.WIP136_ESSM_ISP_DELTA_S){
    const C=WIP136_ESSM_CONTRACT,g=WIP136_ESSM_GRAIN_GEOMETRY,isp=wip136EssmPhaseIsp(avgIspS,deltaS),f=isp.fractions;
    const rodMass=C.propellantKg*f.rod,ringMass=C.propellantKg*f.annulus;
    const rodNorm=_wip136RodShapeIntegral(0,g.rodBurnoutS),ringNorm=_wip136RingShapeIntegral(0,g.annulusBurnoutS);
    const segs=[];let rodConsumed=0,ringConsumed=0;
    for(let a=0,i=0;a<C.burnTotalS-1e-9;i++){
      const b=Math.min(C.burnTotalS,a+g.segmentDtS),dt=b-a;
      let dmRod=rodMass*_wip136RodShapeIntegral(a,b)/Math.max(1e-12,rodNorm);
      let dmRing=ringMass*_wip136RingShapeIntegral(a,b)/Math.max(1e-12,ringNorm);
      if(b>=C.burnTotalS-1e-9){dmRod=Math.max(0,rodMass-rodConsumed);dmRing=Math.max(0,ringMass-ringConsumed);}
      rodConsumed+=dmRod;ringConsumed+=dmRing;
      const dm=dmRod+dmRing,effIsp=dm>0?(dmRod*isp.lowSmokeIspS+dmRing*isp.aluminizedIspS)/dm:isp.avgIspS;
      const thrustN=dm>0?(dm/dt)*effIsp*G0:0;
      segs.push({name:`MIXED_${String(i).padStart(2,'0')}`,reservoir:'sustain',durationS:dt,thrustStartN:thrustN,thrustEndN:thrustN,ispS:effIsp});
      a=b;
    }
    return {model:'CONCENTRIC_DUAL_FORMULATION_GRAIN_PROTOTYPE',motor:C.motor,ispS:isp.avgIspS,
      wip136:{architecture:'SIM_ASSUMED_CONCENTRIC_ROD_PLUS_ANNULUS',burnTotalS:C.burnTotalS,rodBurnoutS:g.rodBurnoutS,propellantKg:C.propellantKg,
        avgIspS:isp.avgIspS,lowSmokeIspS:isp.lowSmokeIspS,aluminizedIspS:isp.aluminizedIspS,ispDeltaS:isp.deltaS,
        rodMassKg:rodMass,annulusMassKg:ringMass,rodMassFraction:f.rod,annulusMassFraction:f.annulus,
        provenance:'MASS/BURN CONTRACT USER_SPECIFIED+VIDEO_DERIVED; GEOMETRY/ISP/THRUST SHAPE SIM_ASSUMED_PROVISIONAL'},segments:segs};
  }
function _wip136RingShapeIntegral(a,b){
    const g=WIP136_ESSM_GRAIN_GEOMETRY,T=g.annulusBurnoutS,r0=g.annulusInnerRadiusMm,R=g.annulusOuterRadiusMm,k=(R-r0)/T,aa=clamp(a,0,T),bb=clamp(b,0,T);
    if(!(bb>aa))return 0;return r0*(bb-aa)+0.5*k*(bb*bb-aa*aa);
  }
const WIP136_ESSM_GRAIN_GEOMETRY=DATA["WIP136_ESSM_GRAIN_GEOMETRY"];
function _wip136RodShapeIntegral(a,b){
    const g=WIP136_ESSM_GRAIN_GEOMETRY,T=g.rodBurnoutS,r0=g.rodRadiusMm,aa=clamp(a,0,T),bb=clamp(b,0,T);
    if(!(bb>aa))return 0;return r0*(bb-aa)-0.5*(r0/T)*(bb*bb-aa*aa);
  }
function wip136EssmPhaseIsp(avgIspS=window.WIP136_ESSM_AVG_ISP_S,deltaS=window.WIP136_ESSM_ISP_DELTA_S){
    const f=wip136EssmGeometryFractions(),avg=Math.max(180,Number(avgIspS)||250),d=Number(deltaS)||0;
    // Mass-weighted average stays exactly avg: f_r*Isp_r + f_a*Isp_a = avg; Isp_a-Isp_r=d.
    return {lowSmokeIspS:avg-f.annulus*d,aluminizedIspS:avg+f.rod*d,avgIspS:avg,deltaS:d,fractions:f};
  }
function wip136EssmGeometryFractions(){
    const g=WIP136_ESSM_GRAIN_GEOMETRY,r1=g.rodRadiusMm,r2=g.annulusInnerRadiusMm,R=g.annulusOuterRadiusMm;
    const rodA=r1*r1,ringA=R*R-r2*r2,sum=Math.max(1e-9,rodA+ringA);
    return {rod:rodA/sum,annulus:ringA/sum};
  }
function wip14a5BuildSm2ErPropulsion(){
    const C=WIP14A5_SM2ER_STAGE_CONTRACT,curve=WIP14A4_MK72_WORKING.thrustShapeNormalized,impulse=C.boosterPropKg*C.mk72IspS*G0;
    let area=0;for(let i=1;i<curve.length;i++)area+=(curve[i][0]-curve[i-1][0])*(curve[i][1]+curve[i-1][1])*.5;
    const scale=impulse/Math.max(1e-9,area),segments=[];
    for(let i=1;i<curve.length;i++)segments.push({name:`MK72_${String(i).padStart(2,'0')}`,reservoir:'boost',durationS:curve[i][0]-curve[i-1][0],thrustStartN:curve[i-1][1]*scale,thrustEndN:curve[i][1]*scale,ispS:C.mk72IspS});
    segments.push({name:'MK72_SEPARATION_COAST',reservoir:'boost',durationS:C.separationDelayS,thrustStartN:0,thrustEndN:0,ispS:C.mk72IspS});
    const upper=wip127BuildMk104CorrectedPropulsion();
    for(const seg of upper.segments)segments.push({...seg,name:'MK104_'+seg.name,reservoir:'sustain'});
    return {model:'TWO_STAGE_MK72_TVC_PLUS_MK104_DUAL_THRUST',motor:'MK72_PLUS_MK104',ispS:(impulse+upper.wip127.totalImpulseNs)/((C.boosterPropKg+C.upperPropKg)*G0),segments,
      wip14a5:{mk72ImpulseNs:impulse,mk72AverageThrustN:impulse/C.mk72BurnS,mk72CurveScaleN:scale,mk72BurnS:C.mk72BurnS,separationS:C.separationS,mk104IgnitionS:C.separationS,mk104BurnS:upper.wip127.burnTotalS,sourceClass:C.sourceClass}};
  }
const WIP14A4_MK72_WORKING=DATA["WIP14A4_MK72_WORKING"];
function wip14a6BuildSm6Propulsion(){
    const base=wip14a5BuildSm2ErPropulsion(),C=WIP14A6_SM6_STAGE_CONTRACT;
    return {...base,model:'SM6_TWO_STAGE_MK72_TVC_PLUS_MK104_DUAL_THRUST',
      wip14a6:{...base.wip14a5,profileId:C.profileId,sourceClass:C.sourceClass}};
  }
const GUIDANCE_TEST_MODE='OFF';
function wip199BindPhysicalVlsOrigin(m,meta){if(meta)throw Error("ENV_A_SEA_LEVEL_ORIGIN_ONLY");return false;}
function consumeVlsCell(){return true;}
function wip148PeekVlsLaunchMeta(){return null;}
const MISSILE_CDA=DATA["MISSILE_CDA"];
function _wip156CreateVlsInCellState(weaponTypeOrEssm,launchAzimuthRad=null){
    const type=weaponTypeOrEssm===true?'ESSM':String(weaponTypeOrEssm??'SM2').toUpperCase();
    const c=type==='ESSM'?WIP156_VLS_IN_CELL_PROFILE.ESSM_BLOCK2:(type==='SM6'?WIP156_VLS_IN_CELL_PROFILE.SM6_BLOCK_IA:(type==='SM2ER'?WIP156_VLS_IN_CELL_PROFILE.SM2ER_BLOCK_IV:WIP156_VLS_IN_CELL_PROFILE.SM2MR_BLOCK_IIIA));
    return {active:true,profileId:c.id,launchAzimuthRad:Number.isFinite(launchAzimuthRad)?angNorm(launchAzimuthRad):null,travelM:0,effectiveTravelM:c.effectiveTravelM,maxInCellTimeS:c.maxInCellTimeS,ignitionLifeS:0,exitLifeS:null,exitSpeedMps:null,exitVzMps:null,exitReason:null};
  }
const WIP156_VLS_IN_CELL_PROFILE=DATA["WIP156_VLS_IN_CELL_PROFILE"];
let missileSerial=1;
function _vlsVerticalLaunchState(verticalMps,fallbackHeading=0){
    const vz=Math.max(0,Number(verticalMps)||0);
    const shipVxWorld=Number(shipNav.vx)||0,shipVyWorld=Number(shipNav.vy)||0;
    const shipVxMps=worldSpeedToMps(shipVxWorld),shipVyMps=worldSpeedToMps(shipVyWorld);
    const shipHorizMps=Math.hypot(shipVxMps,shipVyMps);
    const speedMps=Math.hypot(shipHorizMps,vz);
    const velAngle=shipHorizMps>1e-9?Math.atan2(shipVyMps,shipVxMps):fallbackHeading;
    return {
      vx:shipVxWorld,vy:shipVyWorld,vz,
      speed:mpsToWorldSpeed(speedMps),speedMps,
      velAngle,velPitch:Math.atan2(vz,shipHorizMps),bodyPitch:Math.PI/2,
      shipVxMps,shipVyMps,shipHorizMps,
      launcherRelativeVxMps:0,launcherRelativeVyMps:0,launcherRelativeVzMps:vz,
      launcherRelativePitch:Math.PI/2
    };
  }
const shipNav={heading:0,speed:0,turnRate:0,positionWorld:{x:0,y:0}};
function trackA3ReasonKo(reason){return ({NO_TRACK:'트랙 없음',MODE:'AUTO 모드 아님',IDENTITY_UNKNOWN:'식별 미확정',UNASSESSED:'위협 미평가',AUTHORITY_WITHHELD:'교전권한 보류',PROTECTED_IDENTITY:'우군/중립 트랙',FCS_QUALITY:'사격통제 품질 부족'})[reason]??String(reason??'교전 불가');}
function trackEngagementGateA3(){return {ok:true};}
function trackIsFireControlQuality(){return true;}
const engagementControlMode='MANUAL';
function surfaceEssmLiveReleaseGateWip13C6(){throw Error("ENV_AIR_ONLY_BOUNDARY");}
function surfaceTrackWip13C5(tr){return !!tr&&(tr.domain==='SURFACE'||tr.classification==='SURFACE');}
const ESSM_EMCON_POLICY=DATA["ESSM_EMCON_POLICY"];
const emconActive=false;
function getShipDamageEffects(){return {vlsAvailable:true,combatEff:1};}
function shipGameVlsReadyV1(){return true;}
let selectedLockId=1;
function networkVlsGateG(){return {ok:true};}
function vlsReleaseStandardB1(opts={}){
    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok)return;
    const _requestedWeapon=String(opts.weaponType??'SM2').toUpperCase();
    const _weaponType=_requestedWeapon==='SM6'?'SM6':(_requestedWeapon==='SM2ER'?'SM2ER':'SM2');
    const _isSm2Er=_weaponType==='SM2ER',_isSm6=_weaponType==='SM6';
    const _profileId=_isSm6?'SM6_BLKIA_SIM':(_isSm2Er?'SM2ER_BLKIV_SIM':'SM2MR_BLKIIIA_SIM');
    const _weaponLabel=_isSm6?'SM-6 Block IA':(_isSm2Er?'SM-2ER Block IV':'SM-2MR Block IIIA');
    if(!shipGameVlsReadyV1(_weaponType))return;
    // VLS damage check
    const _vlsDmg = getShipDamageEffects();
    if(!_vlsDmg.vlsAvailable){
      notify('⚠ VLS 발사 불가 — 전력/발사관 피해!');
      return;
    }
    if(_vlsDmg.combatEff < 0.15){
      notify('⚠ 전투체계 심각 손상 — 사격통제 불가!');
      return;
    }

    // WIP13C5: surface release is a separate manual authority path. It must pass the
    // anonymous surface FCQ and reserve a usable SPG-62 window before a round is consumed.
    const _selectedPreflightTrack=selectedLockId!=null?tracks.get(selectedLockId):null;
    const _surfaceStandardSelected=surfaceTrackWip13C5(_selectedPreflightTrack);
    let _surfaceStandardRelease=null;
    if(_surfaceStandardSelected){
      _surfaceStandardRelease=_isSm6
        ?surfaceEssmLiveReleaseGateWip13C6(selectedLockId,{weaponKey:'SM6',mode:typeof engagementControlMode==='string'?engagementControlMode:'MANUAL',automatic:opts.automatic===true})
        :surfaceSm2LiveReleaseGateWip13C5(selectedLockId,{weaponKey:_weaponType,mode:typeof engagementControlMode==='string'?engagementControlMode:'MANUAL',automatic:opts.automatic===true});
      if(!_surfaceStandardRelease.ok){notify(`⚠ ${_weaponLabel} 대수상 발사 차단 — ${_surfaceStandardRelease.reason}`);return;}
    }

    // REPAIR-2 §5: SM-2 EMCON 정책 — SARH terminal은 함 조명 필수.
    // SM2_EMCON_POLICY: 'BLOCK_FIRE' | 'AUTO_RADIATE' (v1 profile 섹션에 선언)
    if(typeof emconActive !== 'undefined' && emconActive){
      if(SM2_EMCON_POLICY === 'BLOCK_FIRE'){
        notify('⚠ EMCON ON — SM-2 발사 차단 (SARH 조명 불가)');
        return;
      } else {
        toggleEmcon();  // AUTO_RADIATE: 발사 전 자동 방사
        notify('📡 SM-2 AUTO_RADIATE: EMCON 자동 해제');
      }
    }

  const ax = aircraft.x(), ay = aircraft.y();
  // SAM: aim toward locked target or cursor direction
  let initHeading;
  if(selectedLockId != null){
    const tr = tracks.get(selectedLockId);
    if(!_surfaceStandardRelease){
      if(!trackIsFireControlQuality(tr)){ notify('⚠ 사격통제 품질 트랙 없음'); return; }
      const a3Gate=trackEngagementGateA3(selectedLockId,{automatic:opts.automatic===true});
      if(!a3Gate.ok){notify(`⚠ SM-2 교전 차단 — ${trackA3ReasonKo(a3Gate.reason)}`);return;}
    }
    initHeading = Math.atan2(tr.y - ay, tr.x - ax);
  } else {
    initHeading = Math.atan2(lockCursor.y - ay, lockCursor.x - ax);
  }
  // WIP155: exact vertical launcher-relative launch + full ship inertial-velocity inheritance.
  // No target-directed horizontal seed is injected at spawn; pitchover belongs to the launch controller.
  const v0Mps = 0; // WIP156: ignition begins at launcher-relative rest; motor thrust creates cell-exit velocity
  const launch0 = _vlsVerticalLaunchState(v0Mps,initHeading);
  const initVelPitch = launch0.velPitch;
  const v0 = launch0.speed;
  const vx0 = launch0.vx, vy0 = launch0.vy, vz0 = launch0.vz;
  const launchBodyHeading = initHeading; // WIP157: vertical-body azimuth is assigned to the intended pitchover bearing; ship velocity remains only in velAngle/vx/vy

  // ===== (A) 정상 발사: 락온이 있을 때 =====
  if(selectedLockId != null){
    const tr = tracks.get(selectedLockId);
    if(!_surfaceStandardRelease&&!trackIsFireControlQuality(tr)) return;

    const seedX = tr.x;
    const seedY = tr.y;
    const seedVx = tr.vx;
    const seedVy = tr.vy;
    const seedZ  = _surfaceStandardRelease?Math.max(0,Number(_surfaceStandardRelease.fireControl?.handoffState?.zM)||Number(tr.z)||0):(tr.z ?? OWN_ALT_M);
    const seedVz = tr.vz ?? 0;

    const m = {
      id: missileSerial++,
      spawnTime: performance.now(),

      x: ax, y: ay,
    z: 0,                    // ground level
    pitch: launch0.bodyPitch, // WIP155: exact +Z body axis at cell exit
    velPitch: initVelPitch,  // inertial flight-path angle includes inherited ship horizontal velocity
    vz: vz0,                 // consistent with speed + flight-path angle
    vlsPhase: true,          // VLS climb until minClimbAlt

      heading: launchBodyHeading, // at +90deg pitch azimuth is geometrically degenerate; align with inherited flow to avoid artificial beta
      velAngle: launch0.velAngle,
      speed: v0,
      vx: vx0, vy: vy0,
      _vlsLaunchState:{shipVxMps:launch0.shipVxMps,shipVyMps:launch0.shipVyMps,relativeVxMps:0,relativeVyMps:0,relativeVzMps:v0Mps,relativePitchDeg:90},
      _vlsInCell:_wip156CreateVlsInCellState(_weaponType,launchBodyHeading),

      // --- SM-2 family spawn shell; selected v1 profile injects authoritative one/two-stage physics ---
      isSM2ER:_isSm2Er, isSM6:_isSm6, weaponType:_weaponType, _visualProfileId:_isSm6?'SM6_BLKIA_FOUNDATION':(_isSm2Er?'SM2ER_BLKIV_FOUNDATION':null),
      sm6ActiveSeeker:false, essmActiveSeeker:false,
      seekerType: 'SARH',  // SM-2 family: SARH terminal
      sarhReceiverStandby: true, // receiver armed from launch
      _sarhRawQ: 0,         // instantaneous illumination quality
      _sarhStableQ: 0,      // smoothed stable quality
      _sarhStableTime: 0,   // seconds quality has been above threshold
      _sarhAcquireThresh: 0.35, // quality needed to START SARH
      _sarhMaintainThresh: 0.20, // quality needed to MAINTAIN SARH
      massKg:     _isSm6?1497:(_isSm2Er?1466:708), // finalized by selected profile
      missileDryKg: _isSm6?425:(_isSm2Er?394:450),    // placeholder until v1 propulsion budget is applied
      boosterPropKg: 151,   // integral motor boost-grain placeholder
      sustainerPropKg: 107, // integral motor sustain-grain placeholder
      boosterCasingKg: 0,
      boosterSeparated: true,
      ispS:       250,
      arefM2:     MISSILE_AREF_M2,
      liftRefM2:  MISSILE_LIFTREF_M2,
      cdScale: 1.0,
      cdA: MISSILE_CDA,
      inducedDragK: 0.05,

      // --- Guidance / autopilot ---
      pnN0: 5.2,
      pnNCloseGain: 3.0,
      pnLosBiasK: 0.30,
      apTauBase: selectedMslType === 'IR' ? 0.10 : 0.14,
      apQrefPa:  selectedMslType === 'IR' ? 12000 : 15000,

      // TVC during boost: critical for VLS pitchover authority
      tvcEnabled: _isSm2Er||_isSm6,
      tvcDuration: (_isSm2Er||_isSm6)?6.08:0,

      // Compatibility mirrors only; v1 profile schedule drives thrust.
      thrust1N:  90000,
      burn1:     5.0,
      thrust2Start: 18000,
      thrust2Mid:   13000,
      thrust2End:   8000,
      thrust2N:  13000,
      burn2:     28.0,
      burn2Sus:  24.0,
      thrust3Coast: 1500,
      burnTotal: 33.0,

      minSpeed: mpsToWorldSpeed(0.20 * MACH1_MPS),
      stallSpeed: mpsToWorldSpeed(0.28 * MACH1_MPS),

      gLimit: 40.0,
      curG: 1.0,

      aoaMax: deg(55.0),
      noseKp: 3.4,
      noseKp0: 3.4,
      velFollowK: 2.4,
      velFollowK0: 2.4,
      aoaEnergyLossK: 0.20,
      gEnergyLossK: 0.14,

      terminalBlendStartKm: 22.0,
      terminalBlendEndKm:   13.0,

      state: 'IOG',
      dlAlive: false,
      assignedTargetId: selectedLockId,
      _surfaceSarh:_surfaceStandardRelease&&_surfaceStandardRelease.capability?.requiresSpg62?{
        schema:'AEGIS_STANDARD_SURFACE_SARH_RUNTIME_V48_WIP15C',weaponKey:_weaponType,mode:'LIMITED_SURFACE_SARH',trackId:selectedLockId,
        aimHeightM:seedZ,launchFcsQuality01:Number(_surfaceStandardRelease.fireControl?.quality01)||0,launchBasketMargin:Number(_surfaceStandardRelease.fireControl?.acquisitionBasketMargin)||0,
        predictedCpaT:Number(_surfaceStandardRelease.capability?.window?.predictedCpaT),committedIlluminatorId:Number(_surfaceStandardRelease.capability?.illuminatorId),truthUsed:false
      }:null,
      _surfaceArh:_surfaceStandardRelease&&!_surfaceStandardRelease.capability?.requiresSpg62?{
        schema:'AEGIS_STANDARD_SURFACE_ARH_RUNTIME_V48_WIP15C',weaponKey:_weaponType,mode:'SURFACE_ARH',trackId:selectedLockId,aimHeightM:seedZ,
        launchFcsQuality01:Number(_surfaceStandardRelease.fireControl?.quality01)||0,launchBasketMargin:Number(_surfaceStandardRelease.fireControl?.acquisitionBasketMargin)||0,truthUsed:false
      }:null,

      pitbullKm: _isSm6?26.0:22.0, // SM-6 SIM_TUNED ARH handover; exact public range unknown

      seekerMaxRangeKm: _isSm6?24.0:18.0,
      seekerMinRangeKm: _isSm6?8.0:10.0,
      seekerRangeKm:    _isSm6?24.0:18.0,
      seekerFov: deg(12),
      gimbalMax: deg(70),
      seekerSlewRate: deg(280),
      seekerAngle: initHeading,

      seekerLocked: false,
      seekerLockType: null,
      seekerLockId: null,
      seekerLockedPrev: false,

      seekerNoTargetTimer: 0,
      seekerNoTargetLimit: 10.0,

      lockStickiness: 1.9,
      chaffResistance: selectedMslType !== 'IR' ? 0.55 : 1.0,    // SARH: somewhat vulnerable, IR: immune
      flareResistance: selectedMslType !== 'IR' ? 1.0  : 0.25,   // SARH: immune, IR: vulnerable
      fovGateLoose: 1.35,
      fovLockLoose: 1.15,

      // R-73 style IRCCM gatewidth: flare 감지 시 시커 탐색 게이트를 급격히 축소
      irccmGatewidthEnabled: selectedMslType === 'IR',
      irccmGateTimer: 0,
      irccmGateDuration: 0.90,
      irccmNarrowScale: 0.28,
      irccmLastTargetAngle: initHeading,
      irccmLastTargetId: selectedLockId,

      seekerNotchLossBasePerSec: 0.65,

      lastCmdX: seedX,
      lastCmdY: seedY,
      lastCmdVx: seedVx,
      lastCmdVy: seedVy,
      lastCmdZ:  seedZ,
      lastCmdVz: seedVz,
      iogAge: 0,

      closestKm: 999,
      afterClosestTimer: 0,
      // Radar_v6_12 style proximity fuze state
      proxArmRangeKm: 2.2,
      proxArmed: false,
      proxMissDistKm: 999,
      proxDetonated: false,
      missedTarget: false,
      pitchoverPhase: false,
      pitchoverTimer: 0,
      pitchoverDuration: 0.35,
      coastHold: false,

      life: 0,
      maxLife: 120.0,
      dead: false
    };

    const _surfaceReservationCommit=_surfaceStandardRelease?.capability?.requiresSpg62?surfaceSm2CommitReservationWip13C5(selectedLockId,_surfaceStandardRelease.capability,m.id):null;
    if(_surfaceStandardRelease?.capability?.requiresSpg62&&!_surfaceReservationCommit?.ok){notify(`⚠ ${_weaponLabel} 대수상 발사 차단 — ${_surfaceReservationCommit?.reason??'SPG62_RESERVATION_COMMIT_FAILED'}`);return;}
    const _wip148LaunchMeta=wip148PeekVlsLaunchMeta(_weaponType);
    if(!consumeVlsCell(_weaponType)){surfaceSm2RollbackReservationWip13C5(_surfaceReservationCommit);notify(`⚠ ${_weaponLabel} 잔탄 없음!`); return; }
    wip199BindPhysicalVlsOrigin(m,_wip148LaunchMeta);
    // === v1 Guidance activation: selected SM-2 family profile ===
    initializeMissileV1(m,_profileId);
    tagWorldEntityOwnershipV48Wip11A(m,'FRIENDLY_ORDNANCE',ACTIVE_SHIP_RUNTIME.entityId);
    missiles.push(m);
    if(_surfaceStandardRelease){if(m._surfaceSarh){spg62ReplanReservations('WIP15C_SURFACE_SARH_LAUNCH');allocateSARH();notify(`${_weaponLabel} 대수상 발사: M${m.id} → ${trackDisplayLabelById(m.assignedTargetId)} · SPG-${(m._surfaceSarh.committedIlluminatorId??0)+1}`);}else notify(`${_weaponLabel} 대수상 ARH 발사: M${m.id} → ${trackDisplayLabelById(m.assignedTargetId)}`);}
    else notify(`${_weaponLabel} 발사: M${m.id} → ${trackDisplayLabelById(m.assignedTargetId)}`);
    allocateDatalinks();
    return m;
  }

  // ===== (B) 무락온 발사 — REPAIR-2 §5: SM-2MR Block IIIA는 ARH maddog 금지 =====
  // SM-2MR은 SARH terminal 미사일: 무락온 ARH 자율탐색 발사는 비활성화한다.
  // 테스트용 IOG-only 발사가 필요하면 SM2_ALLOW_IOG_TEST_FIRE = true 설정.
  if(!SM2_ALLOW_IOG_TEST_FIRE){
    notify('⚠ SM-2 발사 불가 — 락온/트랙 필요 (SARH 유도탄)');
    return;
  }
  // (이하 IOG_ONLY_TEST 경로: 레거시 maddog 객체를 SARH/IOG로 강등해 발사,
  //  표적 미할당 + SARH 미조명이므로 정밀 명중 불가 — §5 요구 충족)
  // 초기 커맨드는 "기수 정면 멀리"로 잡아서 앞으로 쭉 나가게
  const far = kmToWorld(120);
  const seedX = ax + Math.cos(initHeading) * far;
  const seedY = ay + Math.sin(initHeading) * far;
  const seedZ = 8000;   // SAM: aim for mid-altitude when no lock
  const seedVz = 0;

  const m = {
    id: missileSerial++,
    spawnTime: performance.now(),

    x: ax, y: ay,
    z: 0,
    pitch: launch0.bodyPitch,
    velPitch: initVelPitch,
    vlsPhase: true,
    vz: vz0,

    heading: launchBodyHeading,
    velAngle: launch0.velAngle,
    speed: v0,
    vx: vx0, vy: vy0,
    _vlsLaunchState:{shipVxMps:launch0.shipVxMps,shipVyMps:launch0.shipVyMps,relativeVxMps:0,relativeVyMps:0,relativeVzMps:v0Mps,relativePitchDeg:90},
    _vlsInCell:_wip156CreateVlsInCellState(_weaponType,launchBodyHeading),

      // --- SM-2 family test shell; selected v1 profile injects authoritative physics ---
      isSM2ER:_isSm2Er, isSM6:_isSm6, weaponType:_weaponType, _visualProfileId:_isSm6?'SM6_BLKIA_FOUNDATION':(_isSm2Er?'SM2ER_BLKIV_FOUNDATION':null),
      sm6ActiveSeeker:false, essmActiveSeeker:false,
      seekerType: 'SARH',  // REPAIR-2 §5: IOG_ONLY_TEST — ARH maddog 금지
      massKg:     _isSm6?1497:(_isSm2Er?1466:708),
      missileDryKg: _isSm6?425:(_isSm2Er?394:450),
      boosterPropKg: 151,
      sustainerPropKg: 107,
      boosterCasingKg: 0,
      boosterSeparated: true,
      ispS:       250,
      arefM2:     MISSILE_AREF_M2,
      liftRefM2:  MISSILE_LIFTREF_M2,
      cdScale: 1.0,
      cdA: MISSILE_CDA,
      inducedDragK: 0.06,

      tvcEnabled: _isSm2Er||_isSm6,
      tvcDuration: (_isSm2Er||_isSm6)?6.08:0,

      // Compatibility mirrors; v1 Mk104 integral-motor profile drives actual thrust
      thrust1N:  90000,
      burn1:     5.0,
      thrust2Start: 18000,
      thrust2Mid:   13000,
      thrust2End:   8000,
      thrust2N:  13000,
      burn2:     28.0,
      burn2Sus:  24.0,
      thrust3Coast: 1500,
      burnTotal: 33.0,

    minSpeed: mpsToWorldSpeed(0.20 * MACH1_MPS),
    stallSpeed: mpsToWorldSpeed(0.28 * MACH1_MPS),

    gLimit: 40.0,
    curG: 1.0,

    aoaMax: deg(55.0),
    noseKp: 3.4,
    noseKp0: 3.4,
    velFollowK: 2.4,
    velFollowK0: 2.4,
    aoaEnergyLossK: 0.28,
    gEnergyLossK: 0.22,

    terminalBlendStartKm: 22.0,
    terminalBlendEndKm:   13.0,

    // IOG-only diagnostic path; SM-2 remains SARH-dependent and is never ARH maddog
    state: 'IOG',  // REPAIR-2 §5: IOG-only test fire (was ACTIVE maddog)
    dlAlive: false,
    assignedTargetId: null,     // 아직 목표 없음(시커가 물면 할당)

    pitbullKm: 999,  // REPAIR-2 §5: 자율 terminal 획득 금지 (was 0 immediate)

    seekerMaxRangeKm: 18.0,
    seekerMinRangeKm: 10.0,
    seekerRangeKm:    18.0,
    seekerFov: deg(10),
    gimbalMax: deg(65),
    seekerSlewRate: deg(220),
    seekerAngle: initHeading,

    seekerLocked: false,
    seekerLockType: null,
    seekerLockId: null,
    seekerLockedPrev: false,

    seekerNoTargetTimer: 0,
    seekerNoTargetLimit: 60.0,

    lockStickiness: 1.9,
    chaffResistance: selectedMslType !== 'IR' ? 0.55 : 1.0,
    flareResistance: selectedMslType !== 'IR' ? 1.0  : 0.25,
    fovGateLoose: 1.35,
    fovLockLoose: 1.15,

    // R-73 style IRCCM gatewidth: flare 감지 시 시커 탐색 게이트를 급격히 축소
    irccmGatewidthEnabled: selectedMslType === 'IR',
    irccmGateTimer: 0,
    irccmGateDuration: 0.90,
    irccmNarrowScale: 0.28,
    irccmLastTargetAngle: initHeading,
    irccmLastTargetId: null,

    seekerNotchLossBasePerSec: 0.65,

    lastCmdX: seedX,
    lastCmdY: seedY,
    lastCmdVx: 0,
    lastCmdVy: 0,
    lastCmdZ:  seedZ,
    lastCmdVz: seedVz,
    iogAge: 0,

    closestKm: 999,
    afterClosestTimer: 0,
    coastHold: false,
    // Radar_v6_12 style proximity fuze state
    proxArmRangeKm: 2.2,
    proxArmed: false,
    proxMissDistKm: 999,
    proxDetonated: false,
    missedTarget: false,
    pitchoverPhase: false,
    pitchoverTimer: 0,
    pitchoverDuration: 0.35,

    life: 0,
    maxLife: 120.0,
    dead: false
  };

  const _wip148LaunchMeta=wip148PeekVlsLaunchMeta(_weaponType);
  if(!consumeVlsCell(_weaponType)){ notify(`⚠ ${_weaponLabel} 잔탄 없음!`); return; }
  wip199BindPhysicalVlsOrigin(m,_wip148LaunchMeta);
  tagWorldEntityOwnershipV48Wip11A(m,'FRIENDLY_ORDNANCE',ACTIVE_SHIP_RUNTIME.entityId);
  initializeMissileV1(m,_profileId);
  missiles.push(m);
  notify(`${_weaponLabel} 무유도 발사: M${m.id}`);
  // DL 할당 대상 아님(assignedTargetId가 없어서)
}
const SM2_ALLOW_IOG_TEST_FIRE=DATA["SM2_ALLOW_IOG_TEST_FIRE"];
function allocateSARH(){for(const m of missiles){m.sarhAlive=true;m._illuminatorGuided=true;m._illuminatorId=0;m._illQuality=1;}}
function spg62ReplanReservations(){}
function surfaceSm2RollbackReservationWip13C5(){throw Error("ENV_AIR_ONLY_BOUNDARY");}
function surfaceSm2CommitReservationWip13C5(){throw Error("ENV_AIR_ONLY_BOUNDARY");}
const selectedMslType='SARH';
const lockCursor={x:0,y:0};
function toggleEmcon(){}
const SM2_EMCON_POLICY=DATA["SM2_EMCON_POLICY"];
function surfaceSm2LiveReleaseGateWip13C5(){throw Error("ENV_AIR_ONLY_BOUNDARY");}