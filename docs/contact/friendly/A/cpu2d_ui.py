"""Unchanged 213 UI assertions with existing headless CPU-Canvas2D backend."""
from pathlib import Path
import sys,runpy
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'docs/pip/B'))
from browser_backend import install
install();f=R/'docs/gun/B1/run_test_migrations.py';sys.argv=[str(f),'ui'];runpy.run_path(str(f),run_name='__main__')
