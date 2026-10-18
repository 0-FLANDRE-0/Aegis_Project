"""Local/manual verification; ordered static -> native -> scene -> regression."""
from pathlib import Path
import argparse,subprocess
R=Path(__file__).resolve().parents[3]
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 jobs=[['python','docs/sovremenny/A/verify_static.py',str(a.baseline),str(a.html),str(a.out/'static')]]
 for name in ['native','casualty','deployment','visual']:jobs.append(['python','docs/sovremenny/A/verify_'+name+'.py',str(a.html),str(a.out/name)])
 jobs.append(['python','docs/helicopter/F/verify_regression.py',str(a.baseline),str(a.html),str(a.out/'regression'),'--baseline-only'])
 for cmd in jobs:subprocess.run(cmd,cwd=R,check=True)
if __name__=='__main__':main()
