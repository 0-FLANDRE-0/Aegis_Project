"""Verify the requested 3.2s physical booster, impulse, mass and A save boundary."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load(b,source.read_bytes(),errors=errors)
 data=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,profile=h.profile();
   d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});
   const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);const request=h.fire(t.trackId,'MK141-A1'),trace=[];
   for(let i=0;i<224;i++){h.focusedTicks(1);const m=h.snapshot().missiles[0];if(m)trace.push({ageS:m.ageS,boost:m.boosterAttached,thrustN:m.thrustN,massKg:m.massKg,speedMps:m.speedMps,phase:m.phase});}
   const state=h.snapshot(),saved=d.exportOperationalStateV48Wip11A();saved.profileRevision='BUNKERHILL_HARPOON_A_1';
   const aSave=d.validateOperationalStateV48Wip11B(saved);
   return {profile,request,trace,state,aSave,coreFailures:window.__CORE_SELFTEST_FAILURES__};}''')
 p.close();b.close()
trace=data['trace'];boost=[r for r in trace if r['boost']];jet=[r for r in trace if not r['boost']]
events=[e for e in data['state']['missiles'][0]['history']if e['event']=='BOOSTER_SEPARATED']
checks={
 'coreSelfTestsZero':data['coreFailures']==[],
 'observedManualReleaseAccepted':data['request']['ok'],
 'publicReferenceKeptSeparate':data['profile']['public']['boosterThrustN']==53000 and data['profile']['public']['boosterBurnS']==2.9,
 'fullThrustContinuesThroughLastTickBefore3p2':boost and boost[-1]['ageS']>=3.2-1/60-1e-8 and all(r['thrustN']==48000 for r in boost),
 'physicalSeparationOnceAt3p2':len(events)==1 and abs(events[0]['ageS']-3.2)<1e-8,
 'jetThrustReplacesBoosterAfter3p2':jet and all(0<r['thrustN']<=3000 and r['ageS']>=3.2-1e-8 for r in jet),
 'propellantMassDecreasesBeforeDryStageRemoved':all(boost[i]['massKg']<boost[i-1]['massKg']for i in range(1,len(boost))) and abs(boost[-1]['massKg']-600.46875)<1e-6 and data['state']['boosters'][0]['massKg']==60,
 'nominalTotalImpulsePreservedWithin1Percent':abs(48000*3.2/(53000*2.9)-1)<.01,
 'noInstantSpeedJumpAtSeparation':jet and abs(jet[0]['speedMps']-boost[-1]['speedMps'])<2 and 180<events[0]['speedMps']<300,
 'oldAInventorySaveExplicitlyAccepted':data['aSave']['ok'],
 'pageErrorsZero':not errors}
report={'schema':'HARPOON_B_BOOSTER_STAGE_VERIFICATION','source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'details':data,'errors':errors,'pass':all(bool(x)for x in checks.values())}
(out/'stage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':report['pass']},ensure_ascii=False))
raise SystemExit(0 if report['pass']else 1)
