"""Exact native control/SPG state after paused same-tick input changes.
These are diagnostic measured-track/navigation fixtures, not natural acquisition.
No private function or cache is replaced. Actual-release guards run in other suites.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
from state_helpers import clean
from build import BASE_SHA
FIXTURE=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,w=__AEGIS_ENGAGEMENT_RUNTIME__,r=w.ships.get(w.activePlayerShipId),rows=[];
 d.setTerrainDiagBypass(true);d.setEmcon(false);d.wip119SetMode('MANUAL');
 const f=d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:20,altM:40,speedMps:300,bearingDeg:30});
 const tr=r.combatSystem.trackManager.tracks.get(f.trackId);if(!tr)throw Error('MEASURED_TRACK_REQUIRED');
 Object.assign(tr,{identity:'HOSTILE',_operatorIdentity:'HOSTILE'});
 const take=name=>{const control=d.wip118ControlNow(),spg=d.wip116Spg62ReservationSnapshot(),render=get3DRenderState();rows.push({name,control,spg,frame:render.shipBodyFrame,rng:__HARPOON_DIAG_A__.snapshot().rng});};
 take('initial');take('same-tick-build-again');
 r.navigation.heading+=.17;take('same-tick-heading');
 r.navigation.positionWorld.x+=.01;r.navigation.positionWorld.y-=.015;take('same-tick-origin');
 tr.x+=.38;tr.y-=.19;tr.z+=8;if(tr._kfX){tr._kfX[0]+=100;tr._kfX[1]-=50;tr._kfX[2]+=8;}take('same-tick-new-observation');
 Object.assign(tr,{identity:'FRIEND',_operatorIdentity:'FRIEND'});take('same-tick-protected-observation');
 return {rows,fixture:f,core:__CORE_SELFTEST_FAILURES__,faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()==BASE_SHA;errors=[];cases=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   pair={}
   for name,path in [('baseline',a.baseline),('candidate',a.candidate)]:
    page=load(b,path.read_bytes(),ship=ship,errors=errors);pair[name]=page.evaluate(FIXTURE);page.close()
   old,new=pair['baseline'],pair['candidate'];rows=new['rows'];checks={q['name']+'.stateExact':clean(q)==clean(o)for o,q in zip(old['rows'],rows)}
   checks.update({'framesPresent':all(q['frame']for q in rows),'headingImmediate':rows[2]['frame']!=rows[1]['frame'],'originImmediate':rows[3]['frame']!=rows[2]['frame'],'buildRevisionAdvances':all(v['control']['revision']==i+rows[0]['control']['revision']for i,v in enumerate(rows)),'observedRangeChanges':rows[4]['control']['recommendations'][0]['rangeKm']!=rows[3]['control']['recommendations'][0]['rangeKm'],'faultsZero':all(q['core']==[]and all(f is None for f in q['faults'])for q in pair.values())})
   cases.append({'ship':ship,'checks':checks,'pair':pair,'pass':all(checks.values())});print(json.dumps({'ship':ship,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'cases':cases,'errors':errors,'pass':not errors and all(q['pass']for q in cases)};(a.out/'planner.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
