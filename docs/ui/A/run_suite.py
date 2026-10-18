"""Local/manual-CI complete UI_A verification (does not edit the artifact)."""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
commands=[['docs/ui/A/verify_static.py',str(a.baseline),str(a.html),str(a.out/'static')],['docs/ui/A/verify_regressions.py',str(a.html),str(a.out/'regressions'),'--parallel','3'],['docs/ui/A/verify_ui.py',str(a.html),str(a.out/'ui')],['docs/ui/A/verify_viewport_legacy.py',str(a.html),str(a.out/'vp-viewport'),'--part','viewport'],['docs/ui/A/verify_viewport_legacy.py',str(a.html),str(a.out/'vp-extra'),'--part','extra'],['docs/viewport/A/verify_invariance.py',str(a.html),str(a.out/'vp-invariance')]]
for part in ['events','storage','hash']:commands.append(['docs/ui/A/verify_contracts.py',str(a.baseline),str(a.html),str(a.out/part),'--part',part])
for args in commands:
 print('RUN '+args[0]+' '+str(args[-1]),flush=True);subprocess.run([sys.executable,*args],cwd=R,check=True)
