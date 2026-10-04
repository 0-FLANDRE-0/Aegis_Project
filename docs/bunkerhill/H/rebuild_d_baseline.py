#!/usr/bin/env python3
"""Rebuild hash-pinned D for regressions without a second HTML upload."""
from pathlib import Path
import hashlib, subprocess, sys

if len(sys.argv)!=4:raise SystemExit('usage: rebuild_d_baseline.py UPLOADED_F.html EXACT_STARTUP_A.html OUTPUT_D.html')
here=Path(__file__).resolve().parent
reference=here/'baseline-D'
subprocess.run([sys.executable,str(reference/'extract_embedded_assets.py'),sys.argv[1]],check=True)
subprocess.run([sys.executable,str(reference/'build_bunker.py'),sys.argv[2],sys.argv[3]],check=True)
output=Path(sys.argv[3]);expected='c71c0ec6117c1d80d593bc741a1515536ec04e34e79ca81c15ad28d1afd29e2c'
actual=hashlib.sha256(output.read_bytes()).hexdigest()
if actual!=expected:raise SystemExit('EXACT_D_BASELINE_REBUILD_MISMATCH:'+actual)
print('EXACT_D_BASELINE_OK:'+actual)
