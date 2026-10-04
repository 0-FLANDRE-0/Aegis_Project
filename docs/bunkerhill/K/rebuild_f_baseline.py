#!/usr/bin/env python3
"""Recover exact F from small modules and unchanged embedded G/H assets."""
from pathlib import Path
import hashlib,subprocess,sys
if len(sys.argv)!=4:raise SystemExit('usage: rebuild_f_baseline.py UPLOADED_LATEST.html EXACT_STARTUP_A.html OUTPUT_F.html')
here=Path(__file__).resolve().parent;reference=here/'baseline-F'
subprocess.run([sys.executable,str(reference/'extract_embedded_assets.py'),sys.argv[1]],check=True)
subprocess.run([sys.executable,str(reference/'build_bunker.py'),sys.argv[2],sys.argv[3]],check=True)
actual=hashlib.sha256(Path(sys.argv[3]).read_bytes()).hexdigest();expected='993ca479c3cee902348865cfbfca6567f3cec96297a8cd0b7d606c484b3a730c'
if actual!=expected:raise SystemExit('EXACT_F_BASELINE_REBUILD_MISMATCH:'+actual)
print('EXACT_F_BASELINE_OK:'+actual)
