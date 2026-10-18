"""Preserve VP_A's viewport assertions; migrate obsolete shell IDs/navigation."""
import argparse,sys
from pathlib import Path
from verify_regressions import install_navigation
R=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['viewport','extra'],required=True);a=ap.parse_args();install_navigation();f=R/('docs/viewport/A/verify_'+a.part+'.py');s=f.read_text()
if a.part=='viewport':s=s.replace('controlDeckPanel','uiStatusBarA')
else:
 needle="p.locator('#fullscreenBtn').click();p.wait_for_timeout(400);fs="
 s=s.replace(needle,"p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen()}');p.wait_for_timeout(200);"+needle)
sys.argv=[str(f),str(a.html),str(a.out)];exec(compile(s,str(f),'exec'),{'__file__':str(f),'__name__':'__main__'})
