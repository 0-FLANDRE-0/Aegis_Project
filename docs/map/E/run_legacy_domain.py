import sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).resolve().parent));from legacy_test_adapter import install;install()
p=R/'docs/pip/B/run_domain.py';sys.path.insert(0,str(p.parent));runpy.run_path(str(p),run_name='__main__')
