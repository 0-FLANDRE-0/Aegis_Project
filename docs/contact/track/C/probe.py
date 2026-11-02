from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path[:0]=[str(R/'docs/missile/fuze-zem/A'),str(R/'docs/gun/B2/phase1b'),str(R/'docs/gun/B2/diagnostic')]
from browser_tools import instrument,launch
from fast_http import load_fast_http
from http_browser import serve
from playwright.sync_api import sync_playwright
sp=importlib.util.spec_from_file_location('original_passive',P.with_name('A')/'verify_runtime.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['ACTIVE','SHADOW'],default='ACTIVE');a=ap.parse_args()
 out=P/'evidence'/('native-'+a.mode.lower());out.mkdir(parents=True,exist_ok=True)
 f=R/('Aegis_SIM_v48_WIP_TRACK_C'+('_SHADOW'if a.mode=='SHADOW'else'')+'.html');raw=f.read_bytes();helper=(P/'native.js').read_text()+'\n'+m.PASSIVE_HELPER
 server,url=serve(instrument(raw,helper));errors=[];at=time.monotonic()
 try:
  with sync_playwright()as pw:
   browser=launch(pw);page=load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(180000)
   result=page.evaluate('__TRACK_C_NATIVE__.run()');result.update(errors=errors,htmlSha256=hashlib.sha256(raw).hexdigest(),helperSha256=hashlib.sha256(helper.encode()).hexdigest(),wallS=time.monotonic()-at,actualProductFunctions=True)
   (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));browser.close()
 finally:server.shutdown()
 return 0 if result['pass']and not errors else 1

if __name__=='__main__':raise SystemExit(main())
