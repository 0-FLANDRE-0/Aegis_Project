"""Preserve VP_A's viewport assertions; migrate obsolete shell IDs/navigation."""
import argparse,sys
from pathlib import Path
from verify_regressions import install_navigation
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['viewport','extra'],required=True);a=ap.parse_args();install_navigation();f=R/('docs/viewport/A/verify_'+a.part+'.py');s=f.read_text()
sys.path.insert(0,str(R/'docs/helicopter/H'));import browser
native_load=browser.load_fleet
def load(*args,**kw):
 p=native_load(*args,**kw);p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen()}');p.wait_for_timeout(250);return p
browser.load_fleet=load
if a.part=='viewport':
 s=s.replace('controlDeckPanel','uiStatusBarA')
 s=s.replace("p.evaluate('__VIEWPORT_A__.setPan(0,0);__VIEWPORT_A__.draw()')", "p.evaluate('__UI_A__.close(\"NAV\");__UI_A__.close(\"CIC\");__VIEWPORT_A__.setPan(0,0);__VIEWPORT_A__.draw()')")
 s=s.replace("elapsed=time.monotonic()-start;p.wait_for_timeout(500);burstResult", "elapsed=time.monotonic()-start;p.wait_for_function('AEGIS_VIEWPORT.raw.w===600&&AEGIS_VIEWPORT.raw.h===900');p.wait_for_timeout(350);burstResult")
else:
 needle="p.locator('#fullscreenBtn').click();p.wait_for_timeout(400);fs="
 s=s.replace(needle,"p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen()}');p.wait_for_timeout(200);"+needle)
sys.argv=[str(f),str(a.html),str(a.out)];exec(compile(s,str(f),'exec'),{'__file__':str(f),'__name__':'__main__'})
