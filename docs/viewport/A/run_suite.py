"""Manual/local complete verification, static gate first; no Actions dispatch."""
import argparse,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 jobs=[['verify_static.py',str(a.baseline),str(a.html),str(a.out/'static')]]
 for name in ['viewport','invariance','extra']:jobs.append(['verify_'+name+'.py',str(a.html),str(a.out/name)])
 jobs += [['audit_layout.py',str(a.html),str(a.out/'layout')],['audit_layout.py',str(a.html),str(a.out/'layout-coarse'),'--coarse'],['verify_regressions.py',str(a.html),str(a.out/'regressions')],['summarize.py',str(a.out),str(a.html)]]
 for args in jobs:subprocess.run([sys.executable,str(Path(__file__).parent/args[0]),*args[1:]],cwd=R,check=True)
if __name__=='__main__':main()
