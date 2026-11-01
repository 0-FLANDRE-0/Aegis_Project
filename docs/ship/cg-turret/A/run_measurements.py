"""CG-only 720 native Pk trials, 45 surface first rounds and natural G7 subset."""
from pathlib import Path
import json,time,sys,os
from playwright.sync_api import sync_playwright
from harness import P,R,B,build,serve,launch,load_fast_http,sha
E=P/'evidence';E.mkdir(exist_ok=True);start=time.perf_counter();errors=[]
extra=(B/'range_probe.js').read_text()+ (B.parent/'phase1/g7_observer.js').read_text()+'''
window.__CG_SURFACE__=c=>{__GB_TEST__.reset(c.seed);return runWip13b11MovingWorldGunFixture({rangeKm:c.rangeKm,ownSpeedKt:20,bearingDeg:0});};
'''
mode=sys.argv[1] if len(sys.argv)>1 else 'range';control=mode=='control';file='Aegis_SIM_v48_WIP_GUN_B2.html' if mode=='baseline' else 'Aegis_SIM_v48_WIP_CG_TURRET_A.html'
raw=build(file=file,extra=extra,origin_control=control);server,url=serve(raw)
try:
 with sync_playwright() as pw:
  browser=launch(pw)
  if mode=='g7':
   jobs=[{'ship':'CG_52_LATE_TICONDEROGA','bearing':b,'count':n,'seed':s,'on':True}for b in[0,90]for n in[1,4]for s in range(419010,419025)]
   with (E/'g7.jsonl').open('w')as f:
    for i,c in enumerate(jobs):
     p=load_fast_http(browser,url,errors=errors);p.set_default_timeout(600000);r=p.evaluate('c=>{const result=__B2_G7_RUN__(c);return{result,diagnostic:__B2_G7_LOG__()}}',c);f.write(json.dumps({**c,**r},separators=(',',':'))+'\n');f.flush();p.context.close()
     if i%3==0:print('G7',i+1,len(jobs),round(time.perf_counter()-start,1),flush=True)
  else:
   p=load_fast_http(browser,url,errors=errors);p.set_default_timeout(600000)
   jobs=[{'bearing':b,'rangeKm':km,'seed':s,'interceptRange':True}for b in[0,90]for km in range(1,10)for s in range(592001,592041)]
   if mode in ['control','baseline']:jobs=[c for c in jobs if c['rangeKm']in[1,5,9]and c['seed']<592004]
   with(E/(mode+'-pk.jsonl')).open('w')as f:
    for i,c in enumerate(jobs):
     q=p.evaluate('c=>__B2_RANGE_PROBE__(c)',c);f.write(json.dumps(q,separators=(',',':'))+'\n');f.flush()
     if i%40==0:print(mode,i+1,len(jobs),round(time.perf_counter()-start,1),flush=True)
   with(E/(mode+'-surface.jsonl')).open('w')as f:
    for km in[5,10,15]:
     for seed in range(723001,723016 if mode=='range' else 723004):
      c={'rangeKm':km,'seed':seed};q=p.evaluate('c=>__CG_SURFACE__(c)',c);f.write(json.dumps({**c,'result':q},separators=(',',':'))+'\n');f.flush()
     print(mode,'surface',km,round(time.perf_counter()-start,1),flush=True)
   p.context.close()
   if mode in ['control','baseline']:
    with(E/(mode+'-g7.jsonl')).open('w')as f:
     for bearing in[0,90]:
      for count in[1,4]:
       c={'ship':'CG_52_LATE_TICONDEROGA','bearing':bearing,'count':count,'seed':419010,'on':True};p=load_fast_http(browser,url,errors=errors);p.set_default_timeout(600000);q=p.evaluate('c=>{const result=__B2_G7_RUN__(c);return{result,diagnostic:__B2_G7_LOG__()}}',c);f.write(json.dumps({**c,**q},separators=(',',':'))+'\n');f.flush();p.context.close();print(mode,'g7',bearing,count,round(time.perf_counter()-start,1),flush=True)
  browser.close()
finally:server.shutdown();(E/(mode+'-execution.json')).write_text(json.dumps({'elapsedS':time.perf_counter()-start,'htmlSha256':sha((R/file).read_bytes()),'originControl':control,'errors':errors},indent=2)+'\n')
assert not errors,errors
