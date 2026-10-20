"""Unchanged existing domain regressions, with the recorded headless 2D backend fix."""
import sys,runpy
from pathlib import Path
from browser_backend import install
install();R=Path(__file__).resolve().parents[3];path=R/'docs/map/A/verify_regressions.py';sys.argv=[str(path),*sys.argv[1:]]
# Child jobs use this same entrypoint, retaining the existing suite implementation.
import subprocess
native=subprocess.run
def run(cmd,*args,**kw):
 if isinstance(cmd,list):cmd=[str(Path(__file__).resolve())if str(x)==str(path)else x for x in cmd]
 return native(cmd,*args,**kw)
subprocess.run=run
runpy.run_path(str(path),run_name='__main__')
