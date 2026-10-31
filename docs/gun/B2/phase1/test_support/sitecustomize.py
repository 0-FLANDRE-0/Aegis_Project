"""Test configuration only: candidate HTML + AutoAA OFF, original assertions.
No product file, game save field, expected raid value or flight function changes.
Every child inherits this explicit configuration through PYTHONPATH.
"""
import os
if os.environ.get('B2_PHASE1_REGRESSION')=='1':
 from pathlib import Path
 import sys,re,base64,gzip,builtins
 R=Path(__file__).resolve().parents[5];OUT=Path(os.environ['B2_OUT']);candidate=R/os.environ.get('B2_HTML','Aegis_SIM_v48_WIP_GUN_B2.html')
 _open=Path.open;_mkdir=Path.mkdir;_readb=Path.read_bytes;_readt=Path.read_text;_exists=Path.exists;_builtinopen=builtins.open
 def mapped(p):
  p=Path(p)
  if p.absolute().is_relative_to(OUT.absolute()):return p
  try:rel=p.absolute().relative_to(R/'docs')
  except ValueError:return p
  return OUT/rel if 'evidence'in rel.parts and rel.parts[:3]!=('radar','air-origin','A')else p
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
 shim="""window.__GUN_B2__?.configure(REPLACE_B2_FLAGS);
// GUN_B1 REGRESSION CONFIGURATION: original game funcs, switch OFF even after resets.
{const configured=gunB1AutoState;gunB1AutoState=function(){const s=configured();s.enabled=false;return s;};}
"""
 import json
 if os.environ.get("B2_ALLOW_AUTO")=="1":
  shim=shim[:shim.index("// GUN_B1 REGRESSION CONFIGURATION")]
 shim=shim.replace("REPLACE_B2_FLAGS",json.dumps(json.loads(os.environ["B2_FLAGS"])if os.environ.get("B2_FLAGS")else{k:os.environ.get("B2_MODE")=="ON" for k in ["alignment","dispersion","airWindow","fuze","fragments"]}))
 def wrap(fn):
  def load(b,body,*a,**kw):
   m=re.search(rb'data-c55-index="13">([^<]+)</script>',body)
   if m and b'const GUN_B1_SPEC='in gzip.decompress(base64.b64decode(m[1])):body=browser_tools.instrument(body,shim)
   return fn(b,body,*a,**kw)
  return load
 browser.load_fleet=wrap(browser.load_fleet);browser_g.load_fleet=wrap(browser_g.load_fleet);browser_tools.load_fleet=wrap(browser_tools.load_fleet)
 # Preserve the already-returned world120 truth snapshot for difference attribution.
 # No extra page evaluation, no changed assertion, and no game/RNG write.
 from playwright.sync_api import Page
 import json
 state_source=(R/'docs/envelope/D/verify_world120.py').read_text()
 state_expression=re.search("STATE='''([\\s\\S]*?)'''",state_source)[1]
 _capture_evaluate=Page.evaluate;_capture_count=[0]
 def capture_evaluate(self,expression,*args,**kw):
  marker='return {fixture,scale,ticks,'
  if isinstance(expression,str) and 'profilerEnableV48Wip11A' in expression and marker in expression:
   af="{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',targets:__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.hostileMissiles.map(m=>({id:m.id,label:m.label,alive:m.alive,reason:m._deathReason??null})),intercepts:__NAVAL_SIM_DIAG__.wip118ControlSnapshot().recentInterceptEvents,core:window.__CORE_SELFTEST_FAILURES__}"
   expression=expression.replace(marker,'return {afterActionTruth:'+af+',fixture,scale,ticks,',1)
  result=_capture_evaluate(self,expression,*args,**kw)
  if expression==state_expression and isinstance(result,str):
   p=OUT/('world120-returned-state-'+str(_capture_count[0])+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(result+'\n');_capture_count[0]+=1
  return result
 Page.evaluate=capture_evaluate
