"""Native NIS differential/input invalidation and actual-profile original browser selftests."""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from build import decoded,BASE_SHA
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
NAMES=['_mIdx','_matMul','_matTranspose','_matAdd','_matInv','_matIdentity','_symmetrizeClampP','deg','angNorm','trackEkfInit','trackRadarPrediction','trackEkfRadarJacobian','trackRadarAssociationNisV31','trackEkfUpdateRadar','trackRadarAssociationKernelPerfC','trackRadarAssociationInversePerfC','performanceCSelfTest']
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()==BASE_SHA
 with tempfile.TemporaryDirectory()as tmp:
  t=Path(tmp);sources={}
  for name,path in [('baseline',a.baseline),('candidate',a.candidate)]:
   f=t/(name+'.js');f.write_text(decoded(path.read_text()));sources[name]=json.loads(subprocess.check_output(['node',str(HERE/'function_sources.cjs'),str(f),*NAMES]))
  (t/'functions.json').write_text(json.dumps(sources));isolated=json.loads(subprocess.check_output(['node',str(HERE/'radar-equivalence.cjs'),str(t/'functions.json')]))
 errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   page=load(browser,a.candidate.read_bytes(),ship=ship,errors=errors);v=page.evaluate('({test:__NAVAL_SIM_DIAG__.performanceCSelfTest(),priorA:__NAVAL_SIM_DIAG__.performanceASelfTest(),priorB:__NAVAL_SIM_DIAG__.performanceBSelfTest(),core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()})');page.close()
   checks={**v['test']['checks'],'priorSelftestsRetained':v['priorA']['pass']and v['priorB']['pass'],'coreZero':v['core']==[],'faultsZero':v['runtime']is None and v['presentation']is None};cases.append({'ship':ship,'checks':checks,'pass':all(checks.values())})
  browser.close()
 checks={**isolated['checks'],'nativeNisCasesExact':all(q['exact']and q['sameState']for q in isolated['rows']),'profilesSelftestsPass':all(q['pass']for q in cases),'pageErrorsZero':not errors};report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'checks':checks,'isolated':isolated,'cases':cases,'errors':errors,'pass':all(checks.values())};(a.out/'radar.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'checks':len(checks),'nisCases':len(isolated['rows']),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
