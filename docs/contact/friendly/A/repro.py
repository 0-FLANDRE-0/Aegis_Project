import sys,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,load_fast_http,sha
current='--current'in sys.argv;cases=[{'kind':'HELO','moving':False,'seconds':60},{'kind':'HELO','moving':True,'seconds':120},{'kind':'HARPOON','seconds':75}];start=time.perf_counter();errors=[];out=P/'evidence';out.mkdir(exist_ok=True)
raw=build(current,extra=(P/'repro.js').read_text());server,url=serve(raw)
try:
 with sync_playwright()as pw:
  b=launch(pw)
  for i,c in enumerate(cases):
   if '--harpoon-only'in sys.argv and i!=2:continue
   p=load_fast_http(b,url,own='CG_52_LATE_TICONDEROGA',errors=errors);p.set_default_timeout(600000);r=p.evaluate('c=>__FRIENDLY_REPRO_A__.run(c)',c);(out/f'{"after"if current else"before"}-{i}.json').write_text(json.dumps(r,separators=(',',':'))+'\n');p.context.close();print(i,c['kind'],'births',len(r['births']),'serial',r['samples'][-1]['trackSerial'],'tracks',len(r['final']),'wall',round(time.perf_counter()-start,1),flush=True)
  b.close()
finally:server.shutdown()
(out/f'{"after"if current else"before"}-execution.json').write_text(json.dumps({'errors':errors,'wallS':time.perf_counter()-start},indent=2)+'\n')
