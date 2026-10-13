"""Manual/CI entry point for the frozen HELI_A original HTML."""
import argparse, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
p = argparse.ArgumentParser()
p.add_argument('suite', choices=['static', 'motion', 'runtime', 'ui', 'native', 'clock', 'baseline'])
p.add_argument('html', type=Path)
p.add_argument('out', type=Path)
p.add_argument('--baseline', type=Path, default=ROOT/'archive/v48/WIP_PERF_F/Aegis_SIM_v48_WIP_PERF_F.html')
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env.setdefault('NODE_PATH', str(ROOT/'docs/performance/F/node_modules'))
if a.suite == 'motion':
    cmd = ['node', str(HERE/'verify_motion.cjs'), str(a.out/'motion.json')]
else:
    name = 'ui' if a.suite == 'native' else a.suite
    cmd = [sys.executable, str(HERE/f'verify_{name}.py')]
    if a.suite in ['static', 'baseline']:
        cmd.append(str(a.baseline))
    cmd += [str(a.html), str(a.out)]
    if a.suite == 'native':
        cmd.append('--native')
raise SystemExit(subprocess.run(cmd, env=env).returncode)
