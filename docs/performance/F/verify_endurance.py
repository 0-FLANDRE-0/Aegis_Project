"""120 simulated seconds per profile: native diagnostic combat, exact E/F states.
Functional endurance may run with other regressions; timings are not performance evidence.
"""
import argparse,gzip,hashlib,json,runpy,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
B=runpy.run_path(str(ROOT/'docs/performance/E/benchmark_cumulative.py'))
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw)
  for ship,count in [('CG_52_LATE_TICONDEROGA',64),('DDG_119_LATE_FLIGHT_IIA',16)]:
   pair={}
   for name,src in [('baseline',a.baseline),('candidate',a.html)]:
    page=load(browser,src.read_bytes(),ship,errors=errors);setup=page.evaluate(B['SETUP'],{'fleet':3,'count':count});cdp=page.context.new_cdp_session(page);rows=[]
    for window in range(24):
     result=page.evaluate(B['MEASURE'],300);state=page.evaluate(B['STATE']);payload=json.dumps(state,separators=(',',':')).encode();file=f'{ship}-{name}-w{window}.json.gz';(a.out/file).write_bytes(gzip.compress(payload,9,mtime=0));cdp.send('HeapProfiler.collectGarbage');heap=cdp.send('Runtime.getHeapUsage');rows.append({'window':window,'ticks':result['run']['steps'],'counts':result['profiler']['entityCounts'],'digest':B['digest'](state),'rng':result['rng'],'heapAfterGc':heap['usedSize'],'stateReport':file,'faults':result['faults'],'core':result['core']});print(json.dumps({'ship':ship,'version':name,'window':window,'ticks':rows[-1]['ticks'],'heapAfterGc':heap['usedSize']}),flush=True)
    saved=page.evaluate('()=>{const d=__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A();return d.importOperationalStateV48Wip11A(s)}');reset=page.evaluate('()=>{const d=__NAVAL_SIM_DIAG__;d.resetEntireSessionV48Wip11A();return {core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault(),counts:d.profilerSnapshotV48Wip11A().entityCounts}}');page.close();pair[name]={'setup':setup,'rows':rows,'import':saved,'reset':reset}
   b,c=pair['baseline']['rows'],pair['candidate']['rows'];checks={'all7200TicksCompleted':all(r['ticks']==300 for r in b+c),'all24StatesExact':all(x['digest']==y['digest']for x,y in zip(b,c)),'all24RngExact':all(x['rng']==y['rng']for x,y in zip(b,c)),'all24EntityCountsExact':all(x['counts']==y['counts']for x,y in zip(b,c)),'faultsZero':all(not r['core']and all(f is None for f in r['faults'])for r in b+c),'noUnboundedHeapInTest':max(r['heapAfterGc']for r in c[-4:])<=max(r['heapAfterGc']for r in c[:4])+32*1024*1024,'resetFaultsZero':all(not p['reset']['core']and p['reset']['runtime']is None and p['reset']['presentation']is None for p in pair.values())};cases.append({'ship':ship,'Kh32Count':count,'checks':checks,'pair':pair})
  browser.close()
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'cases':cases,'errors':errors,'pass':not errors and all(all(c['checks'].values())for c in cases),'limits':'24x300 fixed ticks =120 simulated seconds after warm-up, native diagnostic seeded tracks, three owners. Post-GC JS heap only; functional concurrent run, no frame/CPU timing, VRAM, real-hour soak, or natural-acquisition claim.'};(a.out/'endurance.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'failed':[(c['ship'],k)for c in cases for k,v in c['checks'].items()if not v]}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
