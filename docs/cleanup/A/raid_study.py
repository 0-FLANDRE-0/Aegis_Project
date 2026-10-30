from pathlib import Path
import argparse,gzip,json,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'docs/missile/fuze-zem/A'),str(R/'docs/bunkerhill/K')]
from browser_tools import instrument
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('variant');ap.add_argument('ship');a=ap.parse_args();v=json.loads((H/'builds.json').read_text())['versions'][a.variant];out=H/'evidence/raid';out.mkdir(exist_ok=True);errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw);p=load(b,instrument((R/v['file']).read_bytes(),(H/'raid_observer.js').read_text()),ship=a.ship,errors=errors);p.set_default_timeout(240000)
 initial=p.evaluate('()=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);const fixture=d.wip119DiagSpawnRealAsms({count:8,label:"Kh-32",rangeKm:16,bearingsDeg:[-60,-20,20,60]});__CLEAN_RAID_A__.start(fixture.map(x=>x.id));d.wip119SetMode("AUTO");return {fixture,state:d.exportOperationalStateV48Wip11A().ship};}')
 rows=[]
 for ticks in [1920,1920,3360,3600]:
  q=p.evaluate('n=>{const d=__NAVAL_SIM_DIAG__,run=d.runFramesToTicks(60,8,n);return {run,state:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),rng:__HARPOON_DIAG_A__.snapshot().rng,observers:d.observerSnapshotC(),offboard:d.offboardSnapshotC(),after:__CLEAN_RAID_A__.read(),core:__CORE_SELFTEST_FAILURES__};}',ticks);rows.append(q);print(a.variant,a.ship,q['run']['simStepCounter'],q['state']['shipHP'],'initialAlive',sum(t['alive']and t['initial']for t in q['after']['targets']),flush=True)
 p.close();b.close()
result={'variant':a.variant,'ship':a.ship,'htmlSha256':v['htmlSha256'],'initial':initial,'snapshots':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'evaluationHorizonS':180,'horizonEndReason':'FIXED_180S_DIAGNOSTIC_HORIZON','scenarioEndPolicy':'Initial 8 have native terminal states AND no active ASM, including native additional spawns. Subsequent 180s continuation is separately reported.'}
(out/(a.variant+'_'+a.ship+'.json.gz')).write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),9,mtime=0));raise SystemExit(1 if errors else 0)
