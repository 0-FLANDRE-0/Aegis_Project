"""Reuse actual B2B instrumentation against explicitly selected product bytes."""
from pathlib import Path
import importlib.util,sys
P=Path(__file__).resolve().parent;R=P.parents[3];B=R/'docs/gun/B2/phase1b'
sys.path[:0]=[str(B),str(R/'docs/gun/B2/diagnostic')]
spec=importlib.util.spec_from_file_location('b2b_harness',B/'harness.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
cg_spec=importlib.util.spec_from_file_location('cg_build',P/'build.py');cg_build=importlib.util.module_from_spec(cg_spec);cg_spec.loader.exec_module(cg_build)
unpack=cg_build.unpack;pack=cg_build.pack
from fast_http import load_fast_http
serve=module.serve;launch=module.launch;sha=module.sha
def build(file='Aegis_SIM_v48_WIP_CG_TURRET_A.html',extra='',record=False,origin_control=False):
 raw=module.build(file=file,extra=extra,record=record)
 if origin_control:
  s=unpack(raw);new='moduleName:hp[hardpointId].name,trunnionOffsetM:g.trunnionOffsetM,exposedBarrelM:g.barrelM,sourceNode:g.yawNode';old='moduleName:hp[hardpointId].name,trunnionOffsetM:{x:.91,y:0,z:2.87},exposedBarrelM:6.206,sourceNode:g.yawNode';assert s.count(new)==1;s=s.replace(new,old,1);raw=pack(raw,s)
 return raw
