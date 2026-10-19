"""MAP_A complete reproducible suite; never dispatches GitHub Actions."""
import argparse,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
def run(script,*args):subprocess.run([sys.executable,str(H/script),*map(str,args)],cwd=R,check=True)
run('verify_static.py',a.base,a.html,a.out/'static')
for part in ['input','invariance','legacy','3d']:run('verify_map.py',a.html,a.out/part,'--part',part,*(['--baseline',a.base]if part=='legacy'else[]))
for script,out in [('verify_additional.py','additional'),('verify_preferences.py','preferences'),('verify_menu_bounds.py','bounds'),('capture_examples.py','examples'),('verify_ui_a1.py','ui-a1')]:run(script,a.html,a.out/out)
run('capture_routes.py',a.html,a.out/'examples')
for part in ['events','hash']:run('run_contracts.py',a.base,a.html,a.out/('ui-a1-'+part),'--part',part)
run('verify_regressions.py',a.html,a.out/'regressions','--parallel','2')
run('summarize.py',a.html,a.out)
