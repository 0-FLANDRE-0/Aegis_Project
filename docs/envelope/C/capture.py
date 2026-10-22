"""Capture detached native model values from the current whole game, no shot execution."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(R/'docs/pip/B'));import browser_backend;browser_backend.install()
sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
p=argparse.ArgumentParser();p.add_argument('html',type=Path);a=p.parse_args();errors=[]
with sync_playwright()as pw:
 b=launch(pw);q=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 data=q.evaluate('__ENV_C__.capture()');audit=q.evaluate('async()=>({status:await __ENV_C__.status(),core:window.__CORE_SELFTEST_FAILURES__??[],tick:__NAVAL_SIM_DIAG__.snapshot()})');b.close()
assert not errors and not audit['core'] and not audit['status']['changedNativeFunctions'],(errors,audit)
(H/'inputs.json').write_text(json.dumps(data,separators=(',',':')))
(H/'capture.json').write_text(json.dumps({'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'errors':errors,'audit':audit},indent=2))
print(json.dumps({'core':audit['core'],'nativeMismatch':audit['status']['changedNativeFunctions'],'profileHash':audit['status']['currentProfileHash'],'errors':errors}))
