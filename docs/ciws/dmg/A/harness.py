"""Read-only diagnostics over immutable user-selected CG_TURRET_A; no product output HTML."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent;R=P.parents[3];B=R/'docs/gun/B2/phase1b'
sys.path[:0]=[str(B),str(R/'docs/gun/B2/diagnostic')]
spec=importlib.util.spec_from_file_location('b2b_harness',B/'harness.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from fast_http import load_fast_http
serve=base.serve;launch=base.launch;sha=lambda b:hashlib.sha256(b).hexdigest()
PRODUCT='Aegis_SIM_v48_WIP_CG_TURRET_A.html'
EXPECTED='af105075c65bf9c8774c8b1d347273476e53a3a5869c12387b2cd8d46824d933'
def check():
 deadline=datetime.fromisoformat(json.loads((P/'TASK_CLOCK.json').read_text())['deadlineUtc'])
 if datetime.now(timezone.utc)>=deadline:raise TimeoutError('CIWS_DMG_A_3H_WALL_CLOCK_CAP')
def build(extra=''):
 check();assert sha((R/PRODUCT).read_bytes())==EXPECTED
 return base.build(file=PRODUCT,record=False,extra=extra)
