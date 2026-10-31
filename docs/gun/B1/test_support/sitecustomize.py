"""Test configuration only: candidate HTML + AutoAA OFF, original assertions.
No product file, game save field, expected raid value or flight function changes.
Every child inherits this explicit configuration through PYTHONPATH.
"""
import os
if os.environ.get('GUN_B1_REGRESSION')=='OFF':
 from pathlib import Path
 import sys,re,base64,gzip,builtins
 R=Path(__file__).resolve().parents[4];OUT=Path(os.environ.get('GUN_B1_EVIDENCE_ROOT',str(R/'docs/gun/B1/evidence/regression')));candidate=R/'Aegis_SIM_v48_WIP_GUN_B1.html'
 _open=Path.open;_mkdir=Path.mkdir;_readb=Path.read_bytes;_readt=Path.read_text;_exists=Path.exists;_builtinopen=builtins.open
 def mapped(p):
  p=Path(p)
  try:rel=p.absolute().relative_to(R/'docs')
  except ValueError:return p
  return OUT/rel if 'evidence'in rel.parts and rel.parts[:2]!=('gun','B1')else p
 def opening(p,mode='r',*a,**kw):
  p=Path(p)
  if any(c in mode for c in 'wax+'):
   p=mapped(p);_mkdir(p.parent,parents=True,exist_ok=True)
  else:
   alt=mapped(p)
   if alt!=p and _exists(alt):p=alt
  return _open(p,mode,*a,**kw)
 def mkdir(p,*a,**kw):return _mkdir(mapped(p),*a,**kw)
 def readb(p):return _readb(candidate if Path(p).absolute()==R/'Aegis_SIM_v48_WIP_MAP_E.html'else p)
 def readt(p,*a,**kw):return _readt(candidate if Path(p).absolute()==R/'Aegis_SIM_v48_WIP_MAP_E.html'else p,*a,**kw)
 def builtinopen(p,mode='r',*a,**kw):
  if isinstance(p,(str,os.PathLike))and any(c in mode for c in 'wax+'):
   alt=mapped(p)
   if alt!=Path(p):_mkdir(alt.parent,parents=True,exist_ok=True);p=alt
  return _builtinopen(p,mode,*a,**kw)
 Path.open=opening;Path.mkdir=mkdir;Path.read_bytes=readb;Path.read_text=readt;builtins.open=builtinopen
 sys.path.insert(0,str(R/'docs/map/E'));from legacy_test_adapter import install;install()
 sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));import browser_tools,browser,browser_g
 shim="""// GUN_B1 REGRESSION CONFIGURATION: original game funcs, switch OFF even after resets.
{const configured=gunB1AutoState;gunB1AutoState=function(){const s=configured();s.enabled=false;return s;};}
"""
 def wrap(fn):
  def load(b,body,*a,**kw):
   m=re.search(rb'data-c55-index="13">([^<]+)</script>',body)
   if m and b'const GUN_B1_SPEC='in gzip.decompress(base64.b64decode(m[1])):body=browser_tools.instrument(body,shim)
   return fn(b,body,*a,**kw)
  return load
 browser.load_fleet=wrap(browser.load_fleet);browser_g.load_fleet=wrap(browser_g.load_fleet);browser_tools.load_fleet=wrap(browser_tools.load_fleet)
