"""Same-seed H3/H4 full fixed-tick ownship fixtures without allied peers.

Raid files are diagnostic seeded measurements. Physical state and combat RNG
must match; exclude EW/network/tactical/maneuver metadata and profiler. Host timings are observations.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
def physical(value):
    if isinstance(value,dict):return {k:physical(v)for k,v in value.items()if k not in ['performance','ew','network','tactical','maneuver','attack','team']}
    if isinstance(value,list):return [physical(v)for v in value]
    return value
def main():
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
    with sync_playwright()as pw:
        browser=launch(pw)
        for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
            for scenario in ['idle','raid','damaged']:
                pair={}
                for name,source in [('baseline',a.baseline),('candidate',a.candidate)]:
                    page=load(browser,source.read_bytes(),ship=ship,errors=errors)
                    row=page.evaluate('''scenario=>{
                      const d=window.__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);let fixture=null;
                      if(scenario==='raid'){fixture=d.wip119DiagSpawnRealAsms({count:8,label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]});d.wip119SetMode('AUTO');}
                      if(scenario==='damaged'){
                        const exp=d.exportOperationalStateV48Wip11A(),cell=exp.ship.damage.flooding.cells[0];cell.waterM3=Math.min(25,cell.capacityM3*.1);
                        const label=Object.keys(exp.ship.damage.moduleDamage)[0];if(label)exp.ship.damage.moduleDamage[label]=40;
                        d.importOperationalStateV48Wip11A(exp);
                      }
                      const scale={idle:1,raid:8,damaged:16}[scenario],ticks={idle:240,raid:1920,damaged:480}[scenario];
                      d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();const t=performance.now(),run=d.runFramesToTicks(60,scale,ticks),elapsedMs=performance.now()-t;
                      const exp=d.exportOperationalStateV48Wip11A();
                      return {fixture,scale,ticks,elapsedMs,run,profiler:d.profilerSnapshotV48Wip11A(),state:exp.ship,dynamics:d.shipDynamics(),rng:window.__HARPOON_DIAG_A__.snapshot().rng,
                        ownership:d.runtimeOwnershipAuditV48Wip11A(),core:window.__CORE_SELFTEST_FAILURES__,faults:[window.__WIP125_DIAG__.wip150RuntimeFault(),window.__WIP125_DIAG__.wip150PresentationFault()]};
                    }''',scenario)
                    row['heapEstimateBytes']=page.context.new_cdp_session(page).send('Runtime.getHeapUsage')
                    pair[name]=row;page.close();print(json.dumps({'ship':ship,'scenario':scenario,'version':name,'elapsedMs':row['elapsedMs']}),flush=True)
                signature=lambda r:physical({k:r[k]for k in ['state','dynamics','rng']})
                physical_signature=lambda r:physical({k:r[k]for k in ['state','dynamics']})
                shape=lambda r:{'shipHP':r['state']['shipHP'],'water':[c['waterM3']for c in r['state']['damage']['flooding']['cells']],'damage':r['state']['damage']['moduleDamage'],'layout':{section:[[c['row'],c['col'],c['destroyed']]for c in cells]for section,cells in r['state']['inventory']['vls'].items()},'closeIn':[(c['id'],c['ammo'])for c in r['state']['inventory']['closeIn']]}
                count_vls=lambda r:sum(c['type']!='EMPTY'for cells in r['state']['inventory']['vls'].values()for c in cells)
                observations={'oldVersionPhysicalAndRngExact':signature(pair['baseline'])==signature(pair['candidate']),'physicalStateExact':physical_signature(pair['baseline'])==physical_signature(pair['candidate']),'oldRng':pair['baseline']['rng'],'newRng':pair['candidate']['rng'],'loadedVlsBeforeAfter':[count_vls(pair['baseline']),count_vls(pair['candidate'])]}
                checks={'samePhysicalState':observations['physicalStateExact'],'sameCombatRng':observations['oldRng']==observations['newRng'],'sameHullDamageAndFixedLayout':shape(pair['baseline'])==shape(pair['candidate']),'raidInventoryDeltaBounded':scenario!='raid'or abs(count_vls(pair['baseline'])-count_vls(pair['candidate']))<=1,'bothFaultFree':all(r['core']==[]and all(x is None for x in r['faults'])and r['ownership']['pass']for r in pair.values())}
                rows.append({'ship':ship,'scenario':scenario,'checks':checks,'observations':observations,'pair':pair});(a.out/'baseline-comparison-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
        browser.close()
    report={'schema':'AEGIS_MULTI_SHIP_H4_BASELINE_COMPARISON','baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'candidateSha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'backend':'headless Chromium CPU fixtures, terrain bypass; no mobile/hardware FPS claim','timingPolicy':'record observations, no speedup claim from a single run','comparisonScope':'H3/H4 idle, damaged, 8 Kh32 AUTO: physical state and combat RNG exact; exclude existing EW/network/tactical metadata, new attack settings and profiler','behaviorDelta':'Ownship defense/maneuver utility is OFF by default. No allied peers or Harpoon launch in this paired regression; H3-on maneuver and native defense are verified separately.'  ,'cases':rows,'errors':errors,'pass':not errors and all(all(r['checks'].values())for r in rows)}
    (a.out/'baseline-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'failed':[r['ship']+':'+r['scenario']for r in rows if not all(r['checks'].values())]}));raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
