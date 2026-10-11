"""Reproduce a named direct suite against the original HTML, without dispatching CI."""
import argparse,subprocess,sys
from pathlib import Path
from suite_catalog import SUITES
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('suite',choices=SUITES);p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,default=ROOT/'archive/v48/WIP_MULTI_SHIP_H3/Aegis_SIM_v48_WIP_MULTI_SHIP_H3.html');a=p.parse_args()
 script,_=SUITES[a.suite];args=[sys.executable,str(ROOT/'docs/multiship'/script)]
 if a.suite=='baseline':args.append(str(a.baseline))
 if a.suite=='harpoon':args.append(str(ROOT/'archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html'))
 args.extend([str(a.html.resolve()),str(a.out.resolve())])
 if a.suite=='camera':args.extend(['--suite','camera'])
 raise SystemExit(subprocess.run(args,cwd=ROOT).returncode)
if __name__=='__main__':main()
