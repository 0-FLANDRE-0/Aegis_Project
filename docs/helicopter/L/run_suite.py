"""Local/manual workflow suite, ordered static -> pure -> native/UI/clock -> regression."""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).resolve().parents[3]
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 jobs=[['python','docs/helicopter/L/verify_static.py',str(a.baseline),str(a.html),str(a.out/'static')],['node','docs/helicopter/L/verify_model.cjs',str(a.out/'model')]]
 for file,folder in [('L/verify_native.py','native'),('L/verify_classes.py','classes'),('L/verify_ui.py','ui'),('L/verify_clock.py','clock'),('K/verify_native.py','emcon')]:jobs.append(['python','docs/helicopter/'+file,str(a.html),str(a.out/folder)])
 jobs.append(['python','docs/helicopter/F/verify_regression.py',str(a.baseline),str(a.html),str(a.out/'regression'),'--baseline-only'])
 for cmd in jobs:subprocess.run(cmd,cwd=R,check=True)
if __name__=='__main__':main()
