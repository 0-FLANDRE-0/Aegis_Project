from pathlib import Path
import importlib.util,sys,hashlib
P=Path(__file__).resolve().parent;R=P.parents[3];B=R/'docs/gun/B2/phase1b';sys.path[:0]=[str(B),str(R/'docs/gun/B2/diagnostic')]
spec=importlib.util.spec_from_file_location('native_b2b_harness',B/'harness.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from fast_http import load_fast_http
serve=base.serve;launch=base.launch;sha=lambda b:hashlib.sha256(b).hexdigest()
BASE='Aegis_SIM_v48_WIP_CG_TURRET_A.html';OUT='Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html'
def build(current=False,extra=''):return base.build(file=OUT if current else BASE,record=False,extra=extra)
