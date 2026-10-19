"""Full PIP_A acceptance plus all MAP_A runtime regressions; manual/local only."""
import argparse,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
def run(script,*args):subprocess.run([sys.executable,str(script),*map(str,args)],cwd=R,check=True)
run(H/'verify_static.py',a.base,a.html,a.out/'static')
for part in ['input','invariance']:run(H/'verify_pip.py',a.html,a.out/part,'--part',part)
run(H/'verify_render.py',a.html,a.out/'render');run(H/'verify_precision.py',a.html,a.out/'precision')
run(H/'run_map.py',a.base,a.html,a.out/'map-regressions')
run(R/'docs/map/A/verify_regressions.py',a.html,a.out/'regressions','--parallel','2')
run(H/'verify_visual.py',a.base,a.html,a.out/'visual')
run(H/'summarize.py',a.html,a.out)
