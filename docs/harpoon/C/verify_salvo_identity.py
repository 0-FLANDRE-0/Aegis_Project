"""Eight real launch tubes, both banks, anonymous radar identity continuity."""
import sys,json,argparse,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args();source=Path(a.html);body=source.read_bytes();sha=hashlib.sha256(body).hexdigest();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors);r=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');const requests=[],samples=[];for(const tube of h.snapshot().inventory.tubes){requests.push(h.fire(t.trackId,tube.id));h.fixedTicks(128);const missiles=h.snapshot().missiles,tracks=window.get3DRenderState().tacticalTracks;samples.push({picture:h.operatorPicture(),comparisons:missiles.filter(m=>m.alive).map(m=>({id:m.id,age:m.ageS,nearbyObservedTracks:tracks.filter(t=>Math.hypot(t.worldXM-m.positionM.x,t.worldYM-m.positionM.y)<180).map(t=>({id:t.id,identity:t.identity,own:t.ownLaunchId,classification:t.classification}))}))});}for(let i=0;i<6;i++){h.fixedTicks(120);const missiles=h.snapshot().missiles,tracks=window.get3DRenderState().tacticalTracks;samples.push({picture:h.operatorPicture(),comparisons:missiles.filter(m=>m.alive).map(m=>({id:m.id,age:m.ageS,nearbyObservedTracks:tracks.filter(t=>Math.hypot(t.worldXM-m.positionM.x,t.worldYM-m.positionM.y)<180).map(t=>({id:t.id,identity:t.identity,own:t.ownLaunchId,classification:t.classification}))}))});}return {requests,samples};}''');core=p.evaluate('window.__CORE_SELFTEST_FAILURES__');b.close()
last=r['samples'][-1];checks={
 'allEightActualRequestsAccepted':all(x['ok']for x in r['requests'])and len(r['requests'])==8,
 'observedOwnReturnsNeverHostile':all(t['identity']not in ['HOSTILE','ASSUMED_HOSTILE']for s in r['samples']for m in s['comparisons']for t in m['nearbyObservedTracks']),
 'bothBanksAllEightCorrectlyCorrelateFriendly':len(last['comparisons'])==8 and all(any(t['identity']=='FRIEND'and t['own']==m['id']for t in m['nearbyObservedTracks'])for m in last['comparisons']),
 'eightDistinctObservedTrackFiles':len({q['trackId']for q in last['picture']['launches']if q['trackId']is not None})==8,
 'coreAndPageErrorsZero':core==[]and not errors}
report={'schema':'HARPOON_C_EIGHT_ROUND_RADAR_IDENTITY_VERIFICATION','source':source.name,'sha256':sha,'truthComparison':'DIAGNOSTIC_ONLY_NOT_FED_BACK_TO_ASSOCIATION','checks':checks,'details':r,'errors':errors,'pass':all(checks.values())}
(out/'salvo_identity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':report['pass']}));raise SystemExit(0 if report['pass']else 1)
