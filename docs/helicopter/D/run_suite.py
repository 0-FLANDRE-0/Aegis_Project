"""Manual/CI entry point for the frozen HELI_C original HTML."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
p = argparse.ArgumentParser()
p.add_argument('suite', choices=['static', 'ui', 'regression', 'altitude', 'model', 'clearance'])
p.add_argument('html', type=Path)
p.add_argument('out', type=Path)
p.add_argument('--baseline', type=Path, default=ROOT / 'archive/v48/WIP_HELI_B/Aegis_SIM_v48_WIP_HELI_B.html')
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env.setdefault('NODE_PATH', str(ROOT / 'docs/performance/F/node_modules'))
cmd = [sys.executable, str(HERE / f'verify_{a.suite}.py')]
if a.suite in ['static', 'regression']:
    cmd.append(str(a.baseline))
cmd += [str(a.html), str(a.out)]
raise SystemExit(subprocess.run(cmd, env=env).returncode)
