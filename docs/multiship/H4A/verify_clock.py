"""Real Harpoon against CG self-defense: full accumulator parity at 1/8/16/64x."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify_harpoon import SETUP
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP_CLOCK=SETUP.replace('enemy=>{','({enemy,scale})=>{').replace('runFramesToTicks(60,1,600)','runFramesToTicks(60,scale,640)')
def stable(v):
 if isinstance(v,dict):return {k:stable(q)for k,q in v.items()if k not in ['performance','lastBuildMs','lastAssessmentMs']}
 if isinstance(v,list):return [stable(q)for q in v]
 return v
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[];reference=None
 with sync_playwright()as pw:
  b=launch(pw)
  for scale in [1,8,16,64]:
   page=load(b,a.html.read_bytes(),ship='CG_52_LATE_TICONDEROGA',errors=errors);setup=page.evaluate(SETUP_CLOCK,{'enemy':'CG_52_LATE_TICONDEROGA','scale':scale})
   row=page.evaluate("""scale=>{const d=__NAVAL_SIM_DIAG__,w=__AEGIS_ENGAGEMENT_RUNTIME__,run=d.runFramesToTicks(60,scale,2688);return {run,state:d.exportOperationalStateV48Wip11A(),defense:d.defenseSnapshotE(),weapons:d.weaponsSnapshotD(),observers:d.observerSnapshotC(),electronic:d.electronicSnapshotF(),flight:__HARPOON_DIAG_A__.snapshot(),worldTime:window.get3DRenderState().sea.environment.timeS,core:__CORE_SELFTEST_FAILURES__,faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};}""",scale)
   signature=stable({k:row[k]for k in ['state','defense','weapons','observers','electronic','flight','worldTime']});reference=reference or signature;defense=row['defense']['ships'][0];ew=row['electronic']['ships'][-1]
   checks={'exactStateAndRngAcrossScales':signature==reference,'full2688Ticks':row['run']['steps']==2688,'sameFixedWorldTime':abs(row['worldTime']-3328/60)<1e-8,'actualLocalPhalanx':any(q['authority']=='LOCAL_SELF_DEFENCE_H4A'and q['rounds']>0 for q in defense['closeInLog']),'actualMeasuredChaff':ew['logistics']['srboc']['expendedRounds']>0,'nativePhysicalResolution':all(not m['alive']for m in row['flight']['missiles']),'faultsZero':row['core']==[]and all(q is None for q in row['faults'])}
   rows.append({'scale':scale,'checks':checks,'setup':setup,'result':row});print(json.dumps({'scale':scale,'failed':[k for k,v in checks.items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'clock-defense.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
