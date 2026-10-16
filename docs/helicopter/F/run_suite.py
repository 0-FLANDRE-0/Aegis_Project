"""Single gate runner; Actions remains manual, no workflow dispatch here."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('suite',choices=['static','model','transport','native','iff','policy','ui','visual','regression']);p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--baseline',type=Path,default=ROOT/'archive/v48/WIP_HELI_D/Aegis_SIM_v48_WIP_HELI_D.html');p.add_argument('--false',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
if a.suite in ['model','transport']:
 cmd=['node',str(HERE/f'verify_{a.suite}.cjs'),str(a.out)];cmd+=['--false']if a.false and a.suite=='model'else[]
elif a.suite=='iff':cmd=[sys.executable,str(ROOT/'docs/helicopter/E/verify_stage_a.py'),str(a.html),str(a.out)]
elif a.suite in ['static','native','regression']:cmd=[sys.executable,str(HERE/f'verify_{a.suite}.py'),str(a.baseline),str(a.html),str(a.out)]
else:cmd=[sys.executable,str(HERE/f'verify_{a.suite}.py'),str(a.html),str(a.out)]
raise SystemExit(subprocess.run(cmd,cwd=ROOT).returncode)
