"""Reproduce a named local suite against the full original HTML."""
import argparse,subprocess,sys
from pathlib import Path
from suite_catalog import SUITES,ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('suite',choices=SUITES);p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,default=ROOT/'archive/v48/WIP_PERF_B/Aegis_SIM_v48_WIP_PERF_B.html');a=p.parse_args()
 script,_=SUITES[a.suite];args=[sys.executable,str(ROOT/script)]
 if a.suite in ['baseline','semantics','resources','planner','radar']:args.append(str(a.baseline.resolve()))
 if a.suite=='harpoon':args.append(str(ROOT/'archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html'))
 args.extend([str(a.html.resolve()),str(a.out.resolve())])
 if a.suite=='camera':args.extend(['--suite','camera'])
 raise SystemExit(subprocess.run(args,cwd=ROOT).returncode)
if __name__=='__main__':main()
