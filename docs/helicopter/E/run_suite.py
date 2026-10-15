"""Reproduce A/B/C gates against the frozen HELI_D original HTML."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
p = argparse.ArgumentParser()
p.add_argument('suite', choices=['static', 'codec', 'regression', 'stage_a', 'stage_b', 'stage_c', 'ui', 'visual', 'transport'])
p.add_argument('html', type=Path)
p.add_argument('out', type=Path)
p.add_argument('--baseline', type=Path, default=ROOT / 'archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html')
p.add_argument('--phase', choices=['A', 'B', 'C'], default='C')
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env.setdefault('NODE_PATH', str(ROOT / 'docs/performance/F/node_modules'))
script = HERE / ('verify_transport.cjs' if a.suite == 'transport' else f'verify_{a.suite}.py')
if not script.is_file():
    p.error(f'{a.suite} source is not available at this gate: {script.name}')
cmd = ['node' if a.suite == 'transport' else sys.executable, str(script)]
if a.suite in ['static', 'regression']:
    cmd.append(str(a.baseline))
cmd += [str(a.html), str(a.out)]
if a.suite in ['static', 'codec']:
    cmd += ['--phase', a.phase]
if a.suite == 'codec':
    cmd += ['--baseline', str(a.baseline)]
raise SystemExit(subprocess.run(cmd, env=env).returncode)
