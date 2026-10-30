"""Serial paired CPU workload, original native diagnostic launches, no overrides.
Direct H4A to current-original cumulative comparison; do not add stepwise ratios.
Measured tracks are diagnostic workloads, not natural acquisition. No render FPS claim.
Run without concurrent verification jobs. Alternating AB/BA order, reverse second pass.
"""
import argparse,gzip,hashlib,json,os,platform,shutil,statistics,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
BASE_SHA='3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a'
CG='CG_52_LATE_TICONDEROGA'
SETUP=r'''o=>{const d=__NAVAL_SIM_DIAG__;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;
Object.assign(cfg,{enemyProfileId:o.fleet===3?'DDG_119_LATE_FLIGHT_IIA':null,allyProfileId:o.fleet===3?'CG_52_LATE_TICONDEROGA':null,targetShip:'NONE',enemyAircraftEnabled:false});
const draft=__AEGIS_DEPLOYMENT_A__.setDraft(cfg);if(!draft.ok)throw Error('Draft '+JSON.stringify(draft));document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);d.setTerrainDiagBypass(true);d.setEmcon(false);
const w=__AEGIS_ENGAGEMENT_RUNTIME__;for(const r of w.ships.values())if(r.entityId!==w.activePlayerShipId)d.observerCommandC(r.entityId,{emcon:false});
let fixture=[];for(let i=0;i<o.count;i+=16)fixture.push(...d.wip119DiagSpawnRealAsms({count:Math.min(16,o.count-i),label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]}));
d.wip119SetMode('AUTO');const run=d.runFramesToTicks(60,1,120);d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();
return {draft,fixture,run,initial:d.profilerSnapshotV48Wip11A().entityCounts};}'''
MEASURE=r'''ticks=>{const d=__NAVAL_SIM_DIAG__,start=performance.now();const run=d.runFramesToTicks(60,1,ticks);return {elapsedMs:performance.now()-start,run,profiler:d.profilerSnapshotV48Wip11A(),core:__CORE_SELFTEST_FAILURES__,faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()],rng:__HARPOON_DIAG_A__.snapshot().rng};}'''
STATE=r'''()=>{const d=__NAVAL_SIM_DIAG__;return {importFingerprint:d.operationalImportMutationFingerprintV48Wip11B(),observer:d.observerSnapshotC(),weapons:d.weaponsSnapshotD(),defense:d.defenseSnapshotE(),ew:d.electronicSnapshotF(),rng:__HARPOON_DIAG_A__.snapshot().rng};}'''
# Existing foreign defense snapshots contain host performance.now() durations.
# They measure this optimization and are not simulation clocks or weapon decisions.
PERFORMANCE_FIELDS=['performance','profiler','lastBuildMs','lastAssessmentMs']
def clean(v):
 if isinstance(v,dict):return {k:clean(q)for k,q in v.items()if k not in PERFORMANCE_FIELDS}
 if isinstance(v,list):return [clean(q)for q in v]
 return v
def digest(v):return hashlib.sha256(json.dumps(clean(v),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);p.add_argument('--repeats',type=int,default=2);p.add_argument('--resume-first-pass',type=Path,help='Reuse the exact first pass; run opposite version order within every case in pass two');p.add_argument('--recheck',action='store_true',help='Revalidate preserved raw states with explicit host-duration normalization; do not rerun timings');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()==BASE_SHA
 if a.recheck:
  path=a.out/'benchmark.json';raw=path.read_bytes();q=json.loads(raw);assert q['sha256']==hashlib.sha256(a.candidate.read_bytes()).hexdigest();assert q['baselineSha256']==BASE_SHA
  previous=a.out/'benchmark-before-timing-normalization.json.gz'
  if not previous.exists():previous.write_bytes(gzip.compress(raw,9,mtime=0))
  for row in q['rows']:
   stateBytes=gzip.decompress((a.out/row['stateReport']).read_bytes());row['rawStateSha256']=hashlib.sha256(stateBytes).hexdigest();row['stateDigest']=digest(json.loads(stateBytes))
  for pair in q['pairs']:
   rows={r['version']:r for r in q['rows']if r['repeat']==pair['repeat']and r['config']==pair['config']};assert len(rows)==2
   pair['checks']['authoritativeStateExact']=rows['baseline']['stateDigest']==rows['candidate']['stateDigest']
  q['checks']['allPairedStateExact']=all(all(p['checks'].values())for p in q['pairs']);q['pass']=all(q['checks'].values());q['conditions']['excludedHostPerformanceFields']=PERFORMANCE_FIELDS
  q['conditions']['comparisonRecheck']='Preserved full state bytes revalidated; lastBuildMs/lastAssessmentMs are existing performance.now() duration diagnostics. Timings unchanged; no new browser run.'
  q['comparisonPreNormalization']={'report':previous.name,'sha256':hashlib.sha256(previous.read_bytes()).hexdigest()};path.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'failed':[p for p in q['pairs']if not all(p['checks'].values())]}));raise SystemExit(0 if q['pass']else 1)
 rows=[];pairs=[];errors=[];cases=[dict(fleet=f,count=n)for f in [1,3]for n in [0,8,32,64]]
 startRep=0;firstPass=None
 if a.resume_first_pass:
  original=a.resume_first_pass/'benchmark.json';prior=json.loads(original.read_text());assert prior['pass']and not prior['errors']and prior['sha256']==hashlib.sha256(a.candidate.read_bytes()).hexdigest()and prior['baselineSha256']==BASE_SHA
  rows=[r for r in prior['rows']if r['repeat']==0];pairs=[q for q in prior['pairs']if q['repeat']==0];assert len(rows)==16 and len(pairs)==8
  assert all(all(q['checks'].values())for q in pairs)and prior['conditions']['warmTicks']==120 and prior['conditions']['measuredTicks']==240
  for r in rows:shutil.copyfile(a.resume_first_pass/r['stateReport'],a.out/r['stateReport'])
  firstPass={'reportSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'scriptSha256':hashlib.sha256((a.resume_first_pass/'benchmark-source.py').read_bytes()).hexdigest(),'note':'First pass setup/measurement/state functions and AB/BA order are unchanged; only pass-two order is corrected. Full original report/source retained separately.'};startRep=1
 with sync_playwright()as pw:
  browser=launch(pw)
  for rep in range(startRep,a.repeats):
   for i,o in enumerate(cases if rep%2==0 else list(reversed(cases))):
    pair={}
    for name,source in [('baseline',a.baseline),('candidate',a.candidate)][::1 if (rep+cases.index(o))%2==0 else -1]:
     page=load(browser,source.read_bytes(),ship=CG,errors=errors);setup=page.evaluate(SETUP,o);result=page.evaluate(MEASURE,240);state=page.evaluate(STATE);page.close()
     stateBytes=json.dumps(state,separators=(',',':')).encode();filename=f"state-r{rep}-f{o['fleet']}-n{o['count']}-{name}.json.gz";(a.out/filename).write_bytes(gzip.compress(stateBytes,9,mtime=0))
     row={'version':name,'repeat':rep,'config':o,'setup':setup,'result':result,'stateDigest':digest(state),'stateReport':filename};rows.append(row);pair[name]=row
     (a.out/'benchmark-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'version':name,'repeat':rep,**o,'msPerTick':round(result['elapsedMs']/240,3)}),flush=True)
    pairs.append({'repeat':rep,'config':o,'checks':{'authoritativeStateExact':pair['baseline']['stateDigest']==pair['candidate']['stateDigest'],'combatRngExact':pair['baseline']['result']['rng']==pair['candidate']['result']['rng'],'entityCountsExact':pair['baseline']['result']['profiler']['entityCounts']==pair['candidate']['result']['profiler']['entityCounts'],'runsComplete':all(q['result']['run']['steps']==240 for q in pair.values()),'faultsZero':all(q['result']['core']==[]and all(v is None for v in q['result']['faults'])for q in pair.values())}})
  browser.close()
 summary=[]
 for o in cases:
  versions={n:[r['result']['elapsedMs']/240 for r in rows if r['version']==n and r['config']==o]for n in ['baseline','candidate']};before=statistics.mean(versions['baseline']);after=statistics.mean(versions['candidate']);summary.append({**o,'msPerTick':versions,'meanBefore':before,'meanAfter':after,'observedReductionPercent':100*(1-after/before)})
 checks={'allPairedStateExact':all(all(p['checks'].values())for p in pairs),'pageErrorsZero':not errors,'repeatCount':a.repeats>=2}
 checks['oppositeOrderWithinEachCase']=all([r['version']for r in rows if r['repeat']==0 and r['config']==o]==list(reversed([r['version']for r in rows if r['repeat']==1 and r['config']==o]))for o in cases)
 report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'baselineSha256':BASE_SHA,'checks':checks,'pass':all(checks.values()),'rows':rows,'pairs':pairs,'summary':summary,'errors':errors,'conditions':{'seed':1831565813,'browser':'Chromium headless','platform':platform.platform(),'hostCpu':os.cpu_count(),'warmTicks':120,'measuredTicks':240,'owners':'ownCG; optional allyCG+enemyDDG','Kh32':'native launch helper,16km/10000m initial; diagnostic seeded measured tracks','order':'serial; alternate AB/BA by original case index; opposite version order within each case in pass two; reversed case traversal','firstPassSource':firstPass,'excludedHostPerformanceFields':PERFORMANCE_FIELDS,'limits':'Host CPU observations, no mobile/real GPU FPS, no natural acquisition or missile interception-rate certification. Profiler phase sensors_tracks_ew is called twice per tick; aggregate by calls.'}}
 (a.out/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'failed':[q for q in pairs if not all(q['checks'].values())],'summary':summary}),flush=True);raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
