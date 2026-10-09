"""Exercise all eight real tubes together at 64x with the fixed-tick profiler."""
import argparse,hashlib,json,math,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'bunkerhill'/'K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load(b,source.read_bytes(),errors=errors)
 result=p.evaluate('''()=>{
  const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;
  d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});
  const track=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);
  if(!track)throw Error('NO_OBSERVED_TRACK');d.a3SetOperatorIdentity(track.trackId,'TRAINING_TARGET');h.select(track.trackId);
  const beforeMass=d.shipMassLedger().massKg,requests=[],ids=h.snapshot().inventory.tubes.map(t=>t.id);
  d.setTimeScale(64);d.profilerResetV48Wip11A();d.profilerEnableV48Wip11A(true);
  for(const id of ids){
   const request=h.fire(track.trackId,id);requests.push({id,request});
   d.runFramesToTicks(60,64,128);
  }
  const concurrent=h.snapshot(),massRemoved=beforeMass-d.shipMassLedger().massKg;
  const run=d.runFramesToTicks(60,64,3072),ended=h.snapshot(),profile=d.profilerSnapshotV48Wip11A();
  d.profilerEnableV48Wip11A(false);
  return {requests,concurrent,ended,profile,run,massRemoved,core:window.__CORE_SELFTEST_FAILURES__};
 }''');b.close()
checks={
 'allEightManualRequestsAccepted':len(result['requests'])==8 and all(r['request']['ok']for r in result['requests']),
 'eightWorldOrdnanceAtOnce':len(result['concurrent']['missiles'])==8 and all(m['alive']for m in result['concurrent']['missiles']),
 'allTubeIdsFixedNoCompaction':[m['tubeId']for m in result['concurrent']['missiles']]==[r['id']for r in result['requests']],
 'eightLoadedRoundsConsumedOnce':all(not t['loaded']for t in result['ended']['inventory']['tubes']) and abs(result['massRemoved']-8*690)<1e-6,
 'rfObservationStorageBounded':all(len(m['seeker']['lastObservations'])<=96 for m in result['ended']['missiles']),
 'allEightFlightStatesFinite':all(math.isfinite(v)for m in result['ended']['missiles']for v in [*m['positionM'].values(),m['speedMps'],m['massKg']]),
 'commonPhysicalContactOccurs':any(m['outcome']=='SURFACE_CONTACT'for m in result['ended']['missiles']),
 'fixedTickAndHarpoonProfilerRecorded':all(k in result['profile']['systems']for k in ['tick.total','harpoon']),
 'coreAndPageErrorsZero':result['core']==[]and not errors}
report={'schema':'HARPOON_A_64X_EIGHT_ROUND_WORKLOAD','source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'hardwareFpsClaim':False,'checks':checks,'details':result,'errors':errors,'pass':all(checks.values())}
(out/'salvo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':checks,'pass':report['pass'],'profiler':result['profile']['systems'].get('harpoon')},ensure_ascii=False))
if not report['pass']:raise SystemExit(1)
