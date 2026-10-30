"""Rebuild the asset inspection from the user's ZIP or GLB and verified PERF_F."""
import argparse, ast, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('source', type=Path); p.add_argument('--baseline', required=True, type=Path); p.add_argument('--browser', action='store_true')
    a = p.parse_args()
    env = dict(os.environ, AEGIS_SIM_BASELINE=str(a.baseline.resolve()), PYTHONDONTWRITEBYTECODE='1')
    def run(file, *args):
        subprocess.run([sys.executable, str(ROOT / file), *map(str, args)], cwd=ROOT, env=env, check=True)
    run('prepare_source.py', a.source.resolve(), '--baseline', a.baseline.resolve())
    for file in ['extract_helicopter.py', 'pack_asset.py', 'make_clean_glb.py', 'make_viewer.py', 'verify_asset.py', 'measure_size.py']:
        run(file)
    for file in ROOT.glob('*.py'):
        ast.parse(file.read_text(), filename=file.name)
    for file in ROOT.glob('*v01.html'):
        for script in re.findall(r'<script>(.*?)</script>', file.read_text(), re.S):
            subprocess.run(['node', '--check'], input=script, text=True, check=True)
    if a.browser:
        run('verify_browser.py'); run('verify_delivery.py')
