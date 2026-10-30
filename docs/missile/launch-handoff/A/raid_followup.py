"""Same original 8-Kh32 AUTO fixture, extended to 120s for outcome diagnosis.
This does NOT replace or relax the original 32s exact-state assertions.
"""
from pathlib import Path
import sys,json,gzip,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import instrument
sys.path.insert(0,str(R/'docs/bunkerhill/K'));from browser_i import launch,load
files={'DZT':(R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html'),'HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])};rows=[];errors=[];start=time.perf_counter()
helper=r'''window.__LH_RAID_AFTER__=()=>({AFTER_ACTION_TRUTH:true,enemies:enemyMissiles.map(t=>({id:t.id,label:t.label,alive:t.alive,reason:t._deathReason??null,retirement:t._wip11cRetirementQueued??null})),sam:missiles.map(m=>({id:m.id,life:m.life,dead:m.dead,reason:m._deathReason??null,handoffAt:m._pitchoverCompleteAt??null})),history:SIM_TEST_INTERCEPT_HISTORY.slice(-128)});'''
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for variant,file in files.items():
   p=load(b,instrument(file.read_bytes(),helper),ship=ship,errors=errors);p.set_default_timeout(240000);initial=p.evaluate('()=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);const fixture=d.wip119DiagSpawnRealAsms({count:8,label:"Kh-32",rangeKm:16,bearingsDeg:[-60,-20,20,60]});d.wip119SetMode("AUTO");return {fixture,state:d.exportOperationalStateV48Wip11A().ship};}');snapshots=[]
   for ticks in [1920,1920,3360]:
    q=p.evaluate('n=>{const d=__NAVAL_SIM_DIAG__,run=d.runFramesToTicks(60,8,n);return {run,state:d.exportOperationalStateV48Wip11A().ship,rng:__HARPOON_DIAG_A__.snapshot().rng,after:__LH_RAID_AFTER__(),core:__CORE_SELFTEST_FAILURES__};}',ticks);snapshots.append(q)
   rows.append({'ship':ship,'variant':variant,'htmlSha256':hashlib.sha256(file.read_bytes()).hexdigest(),'initial':initial,'snapshots':snapshots});p.close();print(ship,variant,'hp',snapshots[-1]['state']['shipHP'],'remainingEnemies',sum(t['alive']for t in snapshots[-1]['after']['enemies']),flush=True)
 b.close()
comparisons=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 a=next(r for r in rows if r['ship']==ship and r['variant']=='DZT');c=next(r for r in rows if r['ship']==ship and r['variant']=='HANDOFF');detail=[]
 for x,y in zip(a['snapshots'],c['snapshots']):
  count=lambda q:sum(t['type']!='EMPTY'for cells in q['state']['inventory']['vls'].values()for t in cells)
  detail.append({'tick':x['run']['simStepCounter'],'baseHP':x['state']['shipHP'],'candidateHP':y['state']['shipHP'],'baseVlsLoaded':count(x),'candidateVlsLoaded':count(y),'baseAliveEnemies':sum(t['alive']for t in x['after']['enemies']),'candidateAliveEnemies':sum(t['alive']for t in y['after']['enemies']),'sameHullDamage':x['state']['damage']==y['state']['damage']})
 comparisons.append({'ship':ship,'checkpoints':detail,'newShipLoss':a['snapshots'][-1]['state']['shipHP']>0 and c['snapshots'][-1]['state']['shipHP']<=0,'worseFinalHP':c['snapshots'][-1]['state']['shipHP']<a['snapshots'][-1]['state']['shipHP']})
o={'records':rows,'comparisons':comparisons,'errors':errors,'elapsedS':time.perf_counter()-start,'method':__doc__};(H/'final-results/raid-followup.json.gz').write_bytes(gzip.compress(json.dumps(o,separators=(',',':')).encode(),9,mtime=0));(H/'final-evidence/raid-followup.json').write_text(json.dumps({'comparisons':comparisons,'errors':errors,'elapsedS':o['elapsedS']},indent=2)+'\n');print(json.dumps({'comparisons':comparisons,'errors':errors}));raise SystemExit(0 if not errors else 1)
