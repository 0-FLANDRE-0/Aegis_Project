"""Actual selected product plus the existing read-only Phase0 shot recorder."""
from pathlib import Path
import gzip,base64,hashlib,json,re,sys
P=Path(__file__).resolve().parent;B=P.parent;R=P.parents[3];D=B/'diagnostic';sys.path[:0]=[str(D),str(R/'docs/missile/fuze-zem/A')]
from browser_tools import instrument,launch
from http_browser import serve,load_http
sha=lambda b:hashlib.sha256(b).hexdigest()
OFF={k:False for k in ['alignment','dispersion','airWindow','fuze','fragments']}
def build(file='Aegis_SIM_v48_WIP_GUN_B2.html',flags=None,record=True,extra=''):
 source=R/file;body=source.read_bytes();hooks=(D/'hooks.js').read_text();needle='pointing=g2nativePointing(q.module,q.solution,q.bodyAzRad,q.elevationRad)';assert hooks.count(needle)==1;hooks=hooks.replace(needle,"pointing=(typeof gunB2Pointing==='function'?gunB2Pointing:g2nativePointing)(q.module,q.solution,q.bodyAzRad,q.elevationRad)",1)
 scope={'__file__':str(D/'build_fixture.py'),'__name__':'_b2_phase1_instrumenter','B2_PRODUCT':source,'B2_PRODUCT_SHA':sha(body),'B2_RECORDING_HOOKS':hooks};code=(D/'build_fixture.py').read_text();needle=" raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED";assert code.count(needle)==1;code=code.replace(needle,' raw=B2_PRODUCT.read_bytes();assert hashlib.sha256(raw).hexdigest()==B2_PRODUCT_SHA',1);needle="(H/'hooks.js').read_text()";assert code.count(needle)==1;code=code.replace(needle,'B2_RECORDING_HOOKS',1);exec(compile(code,str(D/'build_fixture.py')+'::B2_EXPLICIT_PRODUCT','exec'),scope);raw=scope['build'](record)
 config='window.__GUN_B2__?.configure('+json.dumps(flags or{},separators=(',',':'))+');\n'
 return instrument(raw,config+extra)
