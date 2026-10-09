"""Exercise observed-track release, independent RF flight, ownership and save safety."""
import argparse, hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'bunkerhill'/'K'))
from browser_i import launch,load

ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks={};details={};errors=[]
def check(name,value):checks[name]=bool(value)
def setup(page,range_km=8,bearing=0,speed=8):
    return page.evaluate('''opts=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;
      d.setEmcon(false);d.createWip13aSurfaceTargetFixture(opts);
      const audit=d.wip13b9StepSurfaceSensors(1200).audit,t=audit.surfaceTracks.find(t=>t.confirmed);
      if(!t)throw Error('NO_OBSERVED_SURFACE_TRACK');h.select(t.trackId);return {id:t.trackId,audit};
    }''',dict(rangeKm=range_km,bearingDeg=bearing,headingDeg=90,speedKt=speed))
with sync_playwright()as pw:
    b=launch(pw);body=source.read_bytes();p=load(b,body,errors=errors);s=setup(p);tid=s['id'];details['anonymousTrack']=s
    check('coreSelfTestsZero',p.evaluate('window.__CORE_SELFTEST_FAILURES__')==[])
    details['ownership']=p.evaluate('window.__NAVAL_SIM_DIAG__.runtimeOwnershipAuditV48Wip11A?.()??window.__NAVAL_SIM_DIAG__.runtimeOwnershipAuditV48Wip11A')
    check('runtimeOwnershipAuditPass',details['ownership']['pass'])
    gates=p.evaluate('''id=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,rows={};
      for(const identity of ['UNKNOWN','FRIEND','NEUTRAL','HOSTILE','TRAINING_TARGET']){d.a3SetOperatorIdentity(id,identity);rows[identity]=h.gate(id);}
      rows.auto=h.gate(id,undefined,{automatic:true,mode:'AUTO'});return rows;}''',tid)
    details['gates']=gates
    check('protectedAndUnknownDenied',all(not gates[k]['ok']for k in ['UNKNOWN','FRIEND','NEUTRAL']))
    check('manualHostileAndTrainingAllowed',gates['HOSTILE']['ok']and gates['TRAINING_TARGET']['ok'])
    check('automaticDenied',not gates['auto']['ok'])
    recheck=p.evaluate('''id=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;const request=h.fire(id);d.a3SetOperatorIdentity(id,'NEUTRAL');h.focusedTicks(14);const snapshot=h.snapshot();d.a3SetOperatorIdentity(id,'TRAINING_TARGET');return {request,snapshot};}''',tid)
    details['releaseRecheck']=recheck
    check('authorityRecheckedAtActualRelease',recheck['request']['ok']and not recheck['snapshot']['missiles']and all(t['loaded']for t in recheck['snapshot']['inventory']['tubes']))
    damage=p.evaluate('''id=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.wip101SetModuleDamage('Mk 141(A)',100);const gate=h.gate(id);d.wip101SetModuleDamage('Mk 141(A)',0);return gate;}''',tid)
    check('physicalLauncherDamageInhibits',not damage['ok']and damage['reason']=='MK141_LAUNCHER_DAMAGED')
    p.locator('#modeAimBtn').click();p.locator('#harpoonTubeA').select_option('MK141-A4')
    pre=p.evaluate('window.__NAVAL_SIM_DIAG__.shipMassLedger().massKg');p.locator('#harpoonFireA').click();p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(12)')
    released=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');post=p.evaluate('window.__NAVAL_SIM_DIAG__.shipMassLedger().massKg');details['release']=released
    check('actualArmButtonReleasesSelectedTube',len(released['missiles'])==1 and released['missiles'][0]['tubeId']=='MK141-A4')
    check('fixedTubeIdentityAndSelection',released['inventory']['selectedTubeId']=='MK141-A4'and [t['id']for t in released['inventory']['tubes']]==['MK141-A1','MK141-A2','MK141-A3','MK141-A4','MK141-B1','MK141-B2','MK141-B3','MK141-B4']and not released['inventory']['tubes'][3]['loaded'])
    check('exactLaunchMassRemovedOnce',abs(pre-post-690)<1e-6)
    memory=released['missiles'][0]['memory'];rng=released['rng'];p.evaluate('window.__HARPOON_DIAG_A__.forgetCombatTracksDiagnostic()')
    samples=[]
    for i in range(16):
        p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(180)');state=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');m=state['missiles'][0]
        samples.append({k:m.get(k)for k in ['ageS','positionM','phase','speedMps','alive','outcome','boosterAttached','wingDeploy01','fuelKg','impact','normalAccelerationMps2']})
        if not m['alive']:break
    details['flightSamples']=samples;details['lastMissile']=m;details['target']=p.evaluate('window.__NAVAL_SIM_DIAG__.wip13aSurfaceTargetSnapshot()')
    check('frozenTrackSurvivesCombatTrackDeletion',m['memory']==memory)
    check('combatRngNotConsumedByHarpoonFlight',state['rng']==rng)
    check('physicalBoosterSeparationAndWings',not m['boosterAttached']and m['wingDeploy01']==1 and any(e['event']=='BOOSTER_SEPARATED'for e in m['history']))
    check('independentArhAcquired',m['seeker']['lockCount']>=2)
    check('physicalMovingTargetContact',m['outcome']=='SURFACE_CONTACT'and m['impact']['armed'])
    check('warheadFillNotAssemblyTnt',m['impact']['explosiveMassKg']==97.5)
    impacts=details['target']['damage']['impacts']
    check('commonDamageAppliedOnce',len(impacts)==1 and impacts[0]['impactEventId']==m['impact']['eventId'] and impacts[0]['source']=='RGM84D_LIVE')
    check('seekerObservationsAnonymous',not any(key in json.dumps(m['seeker']['lastObservations'])for key in ['entityId','objectId','rfId','truth','sourceId']))
    check('normalForceBounded',all((q['normalAccelerationMps2']or 0)<=4*9.80665+1e-8 for q in samples))
    saved=p.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()')
    safety=p.evaluate('''saved=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,rows=[];
      for(const kind of ['duplicate','wrongId','stringLoaded','wrongCount','wrongSelected','missing']){
        const bad=structuredClone(saved),v=bad.ship.inventory.harpoon;
        if(kind==='duplicate')v.tubes[1].id=v.tubes[0].id;if(kind==='wrongId')v.tubes[0].id='NOT_INSTALLED';if(kind==='stringLoaded')v.tubes[0].loaded='yes';if(kind==='wrongCount')v.tubes.pop();if(kind==='wrongSelected')v.selectedTubeId='BAD';if(kind==='missing')delete bad.ship.inventory.harpoon;
        const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let rejected=false;try{d.importOperationalStateV48Wip11B(bad);}catch(e){rejected=true;}
        rows.push({kind,rejected,unchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B())});
      }
      const valid=d.validateOperationalStateV48Wip11B(saved);d.importOperationalStateV48Wip11B(saved);return {rows,valid,restored:h.snapshot()};}''',saved)
    details['saveSafety']=safety
    check('allInvalidSavesRejectWithoutMutation',all(r['rejected']and r['unchanged']for r in safety['rows']))
    check('saveRestoresFixedAmmoResetsOrdnance',safety['valid']['ok']and safety['restored']['inventory']==saved['ship']['inventory']['harpoon']and not safety['restored']['missiles'])
    legacy=p.evaluate('''saved=>{const old=structuredClone(saved);old.profileRevision='BUNKERHILL_LATE_G_1';delete old.ship.inventory.harpoon;const d=window.__NAVAL_SIM_DIAG__;return d.validateOperationalStateV48Wip11B(old);}''',saved)
    details['legacyMigration']=legacy;check('legacyCgMigrationExplicit',legacy['ok']and any(x['id']=='LEGACY_CG52_MK141_INITIAL_LOAD_A1'for x in legacy['migrations']))
    p.close()
    # Opposite Mk 141 bank, independent sensing and a physical target west of ownship.
    p=load(b,body,errors=errors);s=setup(p,bearing=180);tid=s['id']
    p.evaluate('''id=>{window.__NAVAL_SIM_DIAG__.a3SetOperatorIdentity(id,'TRAINING_TARGET');window.__HARPOON_DIAG_A__.fire(id,'MK141-B4');}''',tid)
    p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(3000)');other=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');details['oppositeBank']=other
    check('oppositeBankPhysicalLaunchAndImpact',other['missiles'][0]['tubeId']=='MK141-B4'and other['missiles'][0]['outcome']=='SURFACE_CONTACT')
    p.close()
    # No acquisition: remove the physical target while keeping the prelaunch observation.
    p=load(b,body,errors=errors);s=setup(p);tid=s['id'];p.evaluate('''id=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.a3SetOperatorIdentity(id,'TRAINING_TARGET');h.fire(id);h.focusedTicks(12);d.createWip13aSurfaceTargetFixture({rangeKm:60,bearingDeg:100});h.forgetCombatTracksDiagnostic();h.focusedTicks(4200);}''',tid)
    miss=p.evaluate('window.__HARPOON_DIAG_A__.snapshot().missiles[0]');details['noTargetCase']={k:miss.get(k)for k in ['outcome','positionM','ageS','phase','impact']}
    check('absentTargetNeverForcedHit',not miss.get('impact'))
    p.close()
    # Full fixed-tick scheduler, actual accumulator at 1x/8x/16x/64x.
    cases=[]
    for scale in [1,8,16,64]:
        p=load(b,body,errors=errors);s=setup(p);tid=s['id']
        case=p.evaluate('''opts=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.a3SetOperatorIdentity(opts.id,'TRAINING_TARGET');h.fire(opts.id);
          d.setTimeScale(opts.scale);const before=d.ciwsB1Closure.snapshot().simStepCounter,run=d.runFramesToTicks(60,opts.scale,3072),state=h.snapshot(),target=d.wip13aSurfaceTargetSnapshot();
          return {scale:opts.scale,run,before,missile:state.missiles[0],damage:target.damage,worldRng:state.rng,inventory:state.inventory};}''',{'id':tid,'scale':scale})
        cases.append(case);p.close();print(json.dumps({'stage':'timescale','scale':scale,'outcome':case['missile']['outcome']}),flush=True)
    details['timeScales']=cases
    signature=lambda c:json.dumps({k:c[k]for k in ['missile','damage','worldRng','inventory']},sort_keys=True)
    check('fullScheduler1_8_16_64ExactlyDeterministic',all(signature(c)==signature(cases[0])for c in cases))
    check('allScaleCasesCompletePhysicalContact',all(c['missile']['outcome']=='SURFACE_CONTACT'for c in cases))
    p=load(b,body,ship='DDG_119_LATE_FLIGHT_IIA',errors=errors)
    ddg=p.evaluate('''()=>({inventory:window.__HARPOON_DIAG_A__.snapshot().inventory,gate:window.__HARPOON_DIAG_A__.gate(),core:window.__CORE_SELFTEST_FAILURES__,ops:window.__NAVAL_SIM_DIAG__.operationalImportSafetyAuditV48Wip11B(),hidden:document.getElementById('harpoonControlsA').hidden})''');details['ddg']=ddg
    check('ddg119HasNoMk141OrHarpoonAmmo',ddg['inventory']['tubes']==[]and ddg['hidden']and ddg['gate']['reason']=='MK141_NOT_INSTALLED')
    check('ddgCoreAndOperationalRegression',ddg['core']==[]and ddg['ops']['pass']);b.close()
check('pageErrorsZero',not errors)
result={'schema':'HARPOON_A_RUNTIME_VERIFICATION','source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'runtime.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':checks,'pass':result['pass'],'errors':errors},ensure_ascii=False))
if not result['pass']:raise SystemExit(1)
