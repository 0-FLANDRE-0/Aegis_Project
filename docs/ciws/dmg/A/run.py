"""Bounded native diagnostic runner. Each combat case starts on a fresh game page."""
from pathlib import Path
import json,sys,time,os
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http,sha,check,PRODUCT
E=P/'evidence';E.mkdir(exist_ok=True);mode=sys.argv[1];assert mode in['equivalence','c1','d1','static','geometry','controls','protection','protection-hp0'];check();started=time.perf_counter();errors=[]
extra=(P/'diagnostic.js').read_text()
if mode.startswith('protection'):extra+='\n'+(P/'protection-trace.js').read_text()
raw=build(extra=extra);server,url=serve(raw)
try:
 with sync_playwright()as pw:
  b=launch(pw)
  if mode=='geometry':
   p=load_fast_http(b,url,own='CG_52_LATE_TICONDEROGA',errors=errors);p.set_default_timeout(600000)
   q=p.evaluate('__CIWS_DMG_A__.geometry()')
   (E/'geometry-metadata.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');p.context.close()
  elif mode=='static':
   p=load_fast_http(b,url,errors=errors);p.set_default_timeout(600000);(E/'native-sources.json').write_text(json.dumps(p.evaluate('__CIWS_DMG_A__.sources()'),indent=2)+'\n')
   for mount in[0,1]:
    for el in[-1,0,2,5]:
     check();r=p.evaluate('c=>__CIWS_DMG_A__.scan(c.el,c.mount)',{'el':el,'mount':mount});(E/f'arc-{mount}-{el}.json').write_text(json.dumps(r,separators=(',',':'))+'\n');print('arc',mount,el,round(time.perf_counter()-started,1),flush=True)
   p.context.close()
  elif mode=='equivalence':
   cases=[{'ship':'CG_52_LATE_TICONDEROGA','bearing':0,'seed':s}for s in[419010,419011]]+[{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':s}for s in[419012,419018]];pairs=[]
   for c in cases:
    pair=[]
    for enabled in[False,True]:
     check();p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(600000);sources=p.evaluate('__CIWS_DMG_A__.sources()');r=p.evaluate('c=>__CIWS_DMG_A__.run(c.c,c.enabled)',{'c':c,'enabled':enabled});sig=r.pop('equivalenceSignature');(E/f'eq-{c["ship"][:2]}-{c["seed"]}-{enabled}.json').write_text(json.dumps({'case':c,'enabled':enabled,'signatureSha256':sha(sig.encode()),**r},separators=(',',':'))+'\n');pair.append({'enabled':enabled,'signatureSha256':sha(sig.encode()),'rng':r['after']['rng'],'result':r['result'],'sourceHashes':{n:sha(s.encode())for n,s in sources.items()}});p.context.close();print('eq',c,enabled,round(time.perf_counter()-started,1),flush=True)
    pairs.append({'case':c,'equal':pair[0]['signatureSha256']==pair[1]['signatureSha256'],'runs':pair});(E/'equivalence.json').write_text(json.dumps({'pass':all(x['equal']for x in pairs),'pairs':pairs,'errors':errors},indent=2)+'\n')
    if not pairs[-1]['equal']:raise RuntimeError('INSTRUMENTATION_EQUIVALENCE_MISMATCH_STOP_BEFORE_MEASUREMENT')
  else:
   eq=json.loads((E/'equivalence.json').read_text());assert eq['pass']and len(eq['pairs'])==4
   if mode=='c1':jobs=[{'ship':'CG_52_LATE_TICONDEROGA','bearing':angle,'seed':seed}for angle in[0,-1,1,-2,2,-5,5,-10,10]for seed in range(419010,419020)]
   elif mode=='d1':jobs=[{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':seed}for seed in range(419010,419040)]
   elif mode=='protection':jobs=[{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419018}]
   elif mode=='protection-hp0':jobs=[{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':s}for s in[419020,419026,419028]]
   else:jobs=[{'ship':'CG_52_LATE_TICONDEROGA','bearing':90,'seed':419018}]
   with(E/(mode+'.jsonl')).open('w')as f:
    for i,c in enumerate(jobs):
     check();p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(600000);r=p.evaluate('c=>__CIWS_DMG_A__.run(c,true)',c);sig=r.pop('equivalenceSignature');f.write(json.dumps({'case':c,'signatureSha256':sha(sig.encode()),**r},separators=(',',':'))+'\n');f.flush();p.context.close();print(mode,i+1,len(jobs),round(time.perf_counter()-started,1),flush=True)
  b.close()
finally:
 server.shutdown();(E/(mode+'-execution.json')).write_text(json.dumps({'mode':mode,'elapsedS':time.perf_counter()-started,'htmlSha256':sha((R/PRODUCT).read_bytes()),'errors':errors},indent=2)+'\n')
assert not errors,errors
