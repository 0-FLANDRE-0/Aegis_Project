"""Original 88 PIP_B UI assertions on the delivered CLEAN_B file."""
from pathlib import Path
import runpy,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(R/'docs/pip/B'));import browser_backend
browser_backend.install();f=R/'docs/pip/B/verify_ui.py'
sys.argv=[str(f),str(R/'Aegis_SIM_v48_WIP_CLEAN_B.html'),str(H/'evidence/ui')]
runpy.run_path(str(f),run_name='__main__')
