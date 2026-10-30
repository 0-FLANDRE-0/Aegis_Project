"""Stage B gate: native common RF scene, anonymous surface measurements and fixed clock.
Native probes use canonical exported/imported helicopter poses and detached receiver RNG;
no plot is injected into the ship track file and no external report port is connected.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
RCS_FIXTURE=r'''()=>{const d=__NAVAL_SIM_DIAG__,generic=[];for(const sizeClass of['SMALL','LARGE']){d.createSurfaceFixture({rangeKm:20,bearingDeg:90,headingDeg:0,speedKt:0,sizeClass,radarHeightM:30});d.stepTicks(1);generic.push(d.surfaceAudit().truth[0]);}d.createWip13aSurfaceTargetFixture({rangeKm:20,bearingDeg:90,headingDeg:0,speedKt:0});return{generic,profiled:d.wip13aSurfaceTargetAudit().entities[0].rcsM2};}'''
SETUP=r'''
 const d=__NAVAL_SIM_DIAG__,api=__HELO__,audit=__HELO_SENSOR_STAGE_B_E__,id=api.snapshot().aircraft[0].id;
 const hover=alt=>{const save=d.exportOperationalStateV48Wip11A(),h=save.ship.aviation.aircraft[0];Object.assign(h,{state:'ARRIVED_HOVER',visible:true,onboard:false,stateTick:0,targetAltitudeM:alt,positionM:{x:0,y:0,z:alt},departPointM:{x:0,y:0,z:alt},holdPointM:{x:0,y:0,z:alt},engine01:[1,1],rotor01:1,blades01:1,tail01:1,radarOn:false,route:[],routeIndex:0,waypointM:null,navigationMode:'ROUTE',followPointM:null,airVelocityMps:{x:0,y:0},groundVelocityMps:{x:0,y:0,z:0},motion:{airSpeedMps:0,groundSpeedMps:0,stopDistanceM:0,braking:false,turnRateRadS:0,longitudinalAccelMps2:0}});const valid=d.validateOperationalStateV48Wip11B(save);if(!valid.ok)throw Error(JSON.stringify(valid));d.importOperationalStateV48Wip11A(save);d.setTerrainDiagBypass(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:0,precipitation01:0});return api.snapshot().aircraft[0];};
 const probe=(seed=1234567,repeat=1)=>audit.nativeProbe({id,previousAngleRad:1.55,newAngleRad:1.59,seed,repeat});
 const target=(rangeKm=70,sizeClass='LARGE',height=30)=>d.createSurfaceFixture({rangeKm,bearingDeg:90,headingDeg:0,speedKt:0,sizeClass,radarHeightM:height});
'''
FIXTURE='()=>{'+SETUP+r'''
 const checks={},rows={},initial=api.snapshot();checks.defaultRadarOff=initial.aircraft.every(h=>h.radarOn===false&&h.sensorsE.radar.enabled===false&&!h.sensorsE.radar.emitting);
 checks.constantsTagged=Object.values(audit.snapshot().constants).every(v=>v.source==='SIM_TUNED');checks.frequencyAndPowerAssumed=audit.snapshot().constants.band.value==='X'&&audit.snapshot().constants.transmitScale01.source==='SIM_TUNED';
 const invalid=[{enabled:'true'},{enabled:1},{enabled:null},{enabled:true,truthRef:{}}];checks.invalidRadarCommandZeroWrites=invalid.every(p=>{const before=JSON.stringify(api.snapshot());return !api.command(id,'SET_RADAR',p).ok&&JSON.stringify(api.snapshot())===before;});
 checks.onboardRadarOnNoSeparateEmission=api.command(id,'SET_RADAR',{enabled:true}).ok;d.stepTicks(2);checks.onboardRadarOnNoSeparateEmission&&=!api.snapshot().aircraft[0].sensorsE.radar.emitting;
 hover(50);target();rows.low=[];for(let i=1;i<=32;i++)rows.low.push(probe(i*1234567,2));checks.low50BeyondMastHorizon=rows.low.every(q=>q.batches.every(b=>b.plots.length===0));checks.lowHorizonReported=Math.abs(api.snapshot().aircraft[0].sensorsE.radar.horizonM-4.12*(Math.sqrt(50)+Math.sqrt(30))*1000)<1e-7;
 hover(300);target();rows.high=[];for(let i=1;i<=32;i++)rows.high.push(probe(i*1234567,2));const highHits=rows.high.reduce((n,q)=>n+q.batches[0].plots.length,0);checks.high300Same70kmTargetDetected=highHits>=8;checks.highHorizonReported=api.snapshot().aircraft[0].sensorsE.radar.horizonM>90000;checks.sameSurfaceHorizonExpansion=api.snapshot().aircraft[0].sensorsE.radar.horizonM>4.12*(Math.sqrt(50)+Math.sqrt(30))*1000+40000;
 checks.oncePerPhysicalPerRevolution=rows.high.every(q=>q.batches[0].attempts>0&&q.batches[1].attempts===0&&q.batches[1].plots.length===0&&q.statistics.duplicateRejected>=q.batches[0].attempts);checks.nativeProbeDoesNotCommitRadarState=audit.snapshot().aircraft[0].radar.attempts===0;
 rows.moving= audit.nativeProbe({id,seed:1234567,sweeps:[{previousAngleRad:1.55,newAngleRad:1.59,turn:0},{previousAngleRad:1.56,newAngleRad:1.60,turn:0,offsetXM:200}]});checks.movingReceiverNoSecondSurfaceAttempt=rows.moving.batches[0].surfaceAttempts===1&&rows.moving.batches[1].surfaceAttempts===0;
 rows.nextTurn=audit.nativeProbe({id,seed:1234567,sweeps:[{previousAngleRad:1.55,newAngleRad:1.59,turn:0},{previousAngleRad:1.55,newAngleRad:1.59,turn:1}]});checks.nextRevolutionPermitsNewAttempt=rows.nextTurn.batches.every(b=>b.surfaceAttempts===1);
 d.createSurfaceFixture({rangeKm:20,bearingDeg:0,headingDeg:0,speedKt:0,sizeClass:'LARGE',radarHeightM:30});rows.wrap=audit.nativeProbe({id,seed:1234567,sweeps:[{previousAngleRad:6.25,newAngleRad:.03,turn:0},{previousAngleRad:0,newAngleRad:.04,turn:1,offsetYM:-100}]});checks.zeroWrapBelongsNewRevolution=rows.wrap.batches[0].surfaceAttempts===1&&rows.wrap.batches[1].surfaceAttempts===0;target();

 const offboard=d.offboardSnapshotC();checks.stageBNoUnexpectedOffboardSource=offboard.helicopterImplemented===true?offboard.sources.every(s=>['H1','H2'].includes(s.sourceId)):offboard.sources.length===0&&offboard.queued===0&&offboard.accepted===0;
 const rngBefore=JSON.stringify(__HARPOON_DIAG_A__.snapshot().rng),repeatA=probe(989898),repeatB=probe(989898);checks.nativePrivateRngRepeatable=JSON.stringify(repeatA)===JSON.stringify(repeatB);checks.nativeProbeNoCombatRngChanges=rngBefore===JSON.stringify(__HARPOON_DIAG_A__.snapshot().rng);
 const measurements=rows.high.flatMap(q=>q.batches[0].plots);const exactKeys=q=>Object.keys(q).sort().join(',')==='covarianceM2,domainEvidence,measuredAtS,positionM';checks.anonymousMeasurementSchema=measurements.length>0&&measurements.every(q=>exactKeys(q)&&Object.keys(q.positionM).sort().join(',')==='x,y,z'&&Object.keys(q.domainEvidence).sort().join(',')==='air,background,missile,surface');checks.noTruthInOutput=!/(truthRef|truthId|targetId|objectId|entityId|rfId|_physicsKind|_truthObject|sizeClass)/.test(JSON.stringify(measurements));checks.surfaceBiasedEvidence=measurements.every(q=>q.domainEvidence.surface>=.78&&q.domainEvidence.air<=.12&&q.domainEvidence.missile<=.08);checks.referenceAltitudeNotMastTruth=measurements.every(q=>q.positionM.z===8);
 const spd=C=>C.length===9&&C.every(Number.isFinite)&&C[0]>=1&&C[4]>=1&&C[8]>=1&&Math.abs(C[1]-C[3])+Math.abs(C[2]-C[6])+Math.abs(C[5]-C[7])<1e-8&&C[0]*C[4]>C[1]*C[3]&&C[0]*(C[4]*C[8]-C[5]*C[7])-C[1]*(C[3]*C[8]-C[5]*C[6])+C[2]*(C[3]*C[7]-C[4]*C[6])>0;
 checks.covarianceFiniteSymmetricPositiveDefinite=measurements.every(q=>spd(q.covarianceM2));
 const near=audit.measurementProbe({id,seed:123,echo:{rangeM:10000,azRad:0,rangeSigmaM:18,azSigmaDeg:.12,truthRef:'POISON',targetId:123}}).plot,far=audit.measurementProbe({id,seed:123,echo:{rangeM:80000,azRad:0,rangeSigmaM:18,azSigmaDeg:.12}}).plot;checks.transverseVarianceGrowsWithRange=far.covarianceM2[4]>near.covarianceM2[4]*50;checks.navigationCovarianceAdded=near.covarianceM2[0]>18*18&&near.covarianceM2[8]===73;checks.measurementPoisonFieldsDropped=exactKeys(near)&&!/truthRef|targetId|POISON/.test(JSON.stringify(near));checks.measurementRangeAzNoTruthAltitude=near.positionM.z===8&&near.positionM.x>9900;
 const close=audit.measurementProbe({id,seed:123,echo:{rangeM:300,azRad:0,rangeSigmaM:18,azSigmaDeg:.12}});checks.nearHorizonProjectionNeverWarped=close.ok&&close.plot===null;
 // Same geometry and private random seed: high sea/rain must lower physical SNR.
 target(20);rows.calm=probe(1234567);d.wip13a3SetManualWeather({hsM:6,windSpeedMps:22,precipitation01:.8});rows.rough=probe(1234567);checks.seaRainLowerNativeSnr=rows.calm.statistics.lastEchoSnr>rows.rough.statistics.lastEchoSnr&&rows.rough.statistics.lastEchoSnr>0;checks.seaRainLowerNativePd=rows.calm.statistics.lastEchoPd>rows.rough.statistics.lastEchoPd;
 d.wip13a3SetManualWeather({hsM:0,windSpeedMps:0,precipitation01:0});target(20,'SMALL');d.stepTicks(1);rows.smallTruth=d.surfaceAudit().truth;rows.small=[];for(let i=1;i<=16;i++)rows.small.push(probe(i*1234567));target(20,'LARGE');d.stepTicks(1);rows.largeTruth=d.surfaceAudit().truth;rows.large=probe(1234567);const smallSnr=rows.small.map(q=>q.statistics.lastEchoSnr).filter(Number.isFinite);checks.smallTargetLowerNativeSnr=smallSnr.length>0&&Math.max(...smallSnr)<rows.large.statistics.lastEchoSnr;checks.genericSizeRcsEnvelopeUsed=rows.smallTruth[0].sizeClass==='SMALL'&&rows.largeTruth[0].sizeClass==='LARGE'&&rows.smallTruth[0].rcsM2<rows.largeTruth[0].rcsM2;
 d.createSurfaceFixture({rangeKm:20,bearingDeg:0,headingDeg:0,speedKt:0,sizeClass:'LARGE',radarHeightM:30});
 checks.radarOnAccepted=api.command(id,'SET_RADAR',{enabled:true}).ok;const beforeOn=audit.snapshot();d.setEmcon(true);d.stepTicks(1080);const live=audit.snapshot(),h=api.snapshot().aircraft[0];checks.liveFixedStepScanner=live.aircraft[0].radar.attempts>0&&live.aircraft[0].radar.turn>=2&&live.aircraft[0].radar.plots>0;checks.motherEmconDoesNotStopAirborneRadar=h.sensorsE.radar.emitting&&h.radarOn;
 const readBefore=JSON.stringify(audit.snapshot());for(let i=0;i<100;i++){audit.snapshot();api.snapshot();}checks.readOnlyRadarSnapshots=readBefore===JSON.stringify(audit.snapshot());
 const prior=live.aircraft[0].radar;checks.radarOffAccepted=api.command(id,'SET_RADAR',{enabled:false}).ok;d.stepTicks(180);const afterOff=audit.snapshot().aircraft[0].radar;checks.radarOffNoEmission=!afterOff.emitting;checks.radarOffNoAttemptsOrPlots=afterOff.attempts===prior.attempts&&afterOff.plots===prior.plots&&afterOff.azimuthRad===prior.azimuthRad;checks.radarOffNoStaleBatch=audit.snapshot().aircraft[0].lastPlots.length===0;
 checks.otherAircraftIndependent=api.snapshot().aircraft[1].radarOn===false&&!api.snapshot().aircraft[1].sensorsE.radar.emitting;
 // Real aircraft reflector: a second canonical helicopter is placed well aloft
 // through the validated physical-state codec. No AIR plot is synthesized here.
 const airSave=d.exportOperationalStateV48Wip11A(),airH=airSave.ship.aviation.aircraft[1];Object.assign(airH,{state:'ARRIVED_HOVER',visible:true,onboard:false,stateTick:0,targetAltitudeM:1000,positionM:{x:0,y:20000,z:1000},departPointM:{x:0,y:20000,z:1000},holdPointM:{x:0,y:20000,z:1000},engine01:[1,1],rotor01:1,blades01:1,tail01:1});checks.nativeAirPhysicalFixtureValid=d.validateOperationalStateV48Wip11B(airSave).ok;d.importOperationalStateV48Wip11A(airSave);d.setTerrainDiagBypass(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:0,precipitation01:0});d.createSurfaceFixture({rangeKm:20,bearingDeg:0,headingDeg:0,speedKt:0,sizeClass:'LARGE',radarHeightM:30});
 rows.air=probe(1234567);checks.noAirTargetReport=rows.air.batches.every(b=>b.plots.length===0)&&rows.air.statistics.airRejected>0;
 rows.asmId=d.spawnRealKh35Regression({rangeKm:2,bearingDeg:90,launchAltM:10});rows.asm=probe(1234567);checks.nativeAsmPhysicalFixtureCreated=Number.isInteger(rows.asmId);checks.noAsmTargetReport=rows.asm.batches.every(b=>b.plots.length===0)&&rows.asm.statistics.airRejected>0;
 checks.coreSelfTestsPass=__CORE_SELFTEST_FAILURES__.length===0;
 return {checks,highHits,rows,live,afterOff,final:api.snapshot()};
}'''
CLOCK='scale=>{'+SETUP+r'''
 hover(300);target(20);api.command(id,'SET_RADAR',{enabled:true});d.setEmcon(true);const run=d.runFramesToTicks(60,scale,1152);return {scale,run,radar:audit.snapshot(),aircraft:api.snapshot().aircraft,rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,default=(ROOT/'archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html')if(ROOT/'archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html').exists()else(ROOT/'Aegis_SIM_v48_WIP_HELI_C.html'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];clock=[]
 with sync_playwright()as pw:
  b=launch(pw);baselinePage=load_fleet(b,a.baseline.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);baselineRcs=baselinePage.evaluate(RCS_FIXTURE);baselinePage.close();rcsPage=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);candidateRcs=rcsPage.evaluate(RCS_FIXTURE);rcsPage.close();page=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);result=page.evaluate(FIXTURE);page.close()
  class Controlled:
   def new_page(self,**options):
    p=b.new_page(**options);p.add_init_script('window.requestAnimationFrame=()=>0;');return p
  for scale in [1,8,16,64]:
   page=load_fleet(Controlled(),a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);clock.append(page.evaluate(CLOCK,scale));page.close()
  b.close()
 result['checks']['baselineGenericProfileDefaultBugWitness']=baselineRcs['generic'][0]['rcsM2']==baselineRcs['generic'][1]['rcsM2']
 result['checks']['genericSizeEnvelopeRestored']=candidateRcs['generic'][0]['rcsM2']<candidateRcs['generic'][1]['rcsM2']
 result['checks']['explicitProfiledHulkRcsUnchanged']=baselineRcs['profiled']==candidateRcs['profiled']
 signature=lambda q:json.dumps({k:q[k]for k in ['radar','aircraft','rng']},sort_keys=True)
 for row in clock:result['checks']['fixedClock'+str(row['scale'])]=signature(row)==signature(clock[0])
 result['checks']['allClockCoreSelfTestsPass']=all(not r['core']for r in clock)
 out={'pass':all(result['checks'].values())and not errors,'checks':result['checks'],'runtime':result,'clock':clock,'rcsRegression':{'baseline':baselineRcs,'candidate':candidateRcs},'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'evidenceScope':'Exact candidate HTML; actual unified RF native probes with owned physical helicopter poses, independent detached receiver RNG, range/az covariance and fixed-step scanner; no remote report delivery or combat track injection'};(a.out/'stage-b.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(out['checks']),'failed':[k for k,v in out['checks'].items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
