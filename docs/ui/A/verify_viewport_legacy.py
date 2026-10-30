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
 settled="AEGIS_VIEWPORT.raw.w===600&&AEGIS_VIEWPORT.raw.h===900&&AEGIS_VIEWPORT.edgePanels.length===AEGIS_VIEWPORT.snapshot().panels.length&&AEGIS_VIEWPORT.snapshot().panels.every(p=>{const e=document.getElementById(p.id),r=e.getBoundingClientRect();return AEGIS_VIEWPORT.edgePanels.some(q=>q.id===p.id&&q.edge===p.edge)&&Math.abs(p.x-r.x)<.1&&Math.abs(p.y-r.y)<.1&&Math.abs(p.w-r.width)<.1&&Math.abs(p.h-r.height)<.1})"
 s=s.replace("p.wait_for_timeout(500);burstResult", "p.wait_for_timeout(500);p.wait_for_function("+repr(settled)+",polling=50);p.wait_for_timeout(180);burstResult")
 s=s.replace("p.wait_for_timeout(400);singleResult", "p.wait_for_timeout(400);p.wait_for_function("+repr(settled)+",polling=50);p.wait_for_timeout(180);singleResult")
 s=s.replace("p.evaluate('__WIP148_3D_VIEW__.active=true');p.mouse.move(700,400)","p.evaluate('__WIP148_3D_VIEW__.active=true');p.wait_for_function('__UI_A__.snapshot().windows.CIC.open',polling=50);p.wait_for_timeout(500);p.mouse.move(700,400)")
 s=s.replace('controlDeckPanel','uiStatusBarA')
 s=s.replace("p.evaluate('__VIEWPORT_A__.setPan(0,0);__VIEWPORT_A__.draw()')", "p.evaluate('__UI_A__.close(\"NAV\");__UI_A__.close(\"CIC\");__VIEWPORT_A__.setPan(0,0);__VIEWPORT_A__.draw()')")
 s=s.replace("elapsed=time.monotonic()-start;p.wait_for_timeout(500);burstResult", "elapsed=time.monotonic()-start;p.wait_for_function('AEGIS_VIEWPORT.raw.w===600&&AEGIS_VIEWPORT.raw.h===900');p.wait_for_timeout(350);burstResult")
 s=s.replace("cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1.25});p.wait_for_timeout(400)","cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1.25});p.wait_for_function('Math.abs(AEGIS_VIEWPORT.raw.w-844/1.25)<.1',polling=50);p.wait_for_timeout(200)")
else:
 needle="p.locator('#fullscreenBtn').click();p.wait_for_timeout(400);fs="
 s=s.replace(needle,"p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen()}');p.wait_for_timeout(200);"+needle)
sys.argv=[str(f),str(a.html),str(a.out)];exec(compile(s,str(f),'exec'),{'__file__':str(f),'__name__':'__main__'})
