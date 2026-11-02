"""In-memory component A/B at the one changed interception outcome. No tuning."""
import json,re,gzip,base64,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http,sha
import importlib.util
spec=importlib.util.spec_from_file_location('friendly_build',P/'build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder);transform,pack=builder.transform,builder.pack
start=time.perf_counter();errors=[];rows=[]
for mode in ['ciws-only','radar-only']:
 raw=build(False,extra=(R/'docs/ciws/dmg/A/diagnostic.js').read_text());m=re.search(rb'data-c55-index="13">([^<]+)',raw);original=gzip.decompress(base64.b64decode(m[1])).decode();s,changes=transform(original)
 for c in reversed(changes):
  keep=(c is changes[0])if mode=='ciws-only'else(c is not changes[0])
  if not keep:s=s.replace(c['after'],c['before'])
 raw=pack(raw,s);server,url=serve(raw)
 try:
  with sync_playwright()as pw:
   b=launch(pw);p=load_fast_http(b,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);r=p.evaluate('c=>__CIWS_DMG_A__.run(c,true)',{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419025});signature=r.pop('equivalenceSignature');r.update(mode=mode,signatureSha256=sha(signature.encode()));(P/'evidence'/('isolated-'+mode+'.json')).write_text(json.dumps(r,separators=(',',':'))+'\n');rows.append({'mode':mode,'result':r['result']});b.close()
 finally:server.shutdown()
 print(mode,r['result']['shipHits'],r['result']['hpAfter'],round(time.perf_counter()-start,1),flush=True)
(P/'evidence/isolated.json').write_text(json.dumps({'rows':rows,'errors':errors,'wallS':time.perf_counter()-start},indent=2)+'\n')
