"""Native close-in regression isolated from H2 navigation and simultaneous EW.
The historical E fixture with default EW enabled also fails on untouched H4;
this case isolates actual hard-kill mechanics. Combined EW is verified separately.
"""
import runpy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'E/verify_closein.py'
sys.path.insert(0,str(SOURCE.parent));scope=runpy.run_path(str(SOURCE))
old=" d.createTerminalAsmFixture({label:'Kh-35U'"
new=" d.tacticalCommandH1(id,{enabled:false});d.maneuverCommandH2(id,{enabled:false});d.electronicCommandF(id,{auto:false,noiseRequested:false,deceptionRequested:false});d.createTerminalAsmFixture({label:'Kh-35U'"
f=scope['FIXTURE'];assert f.count(old)==1;f=f.replace(old,new)
fn=scope['main'];fn.__globals__['FIXTURE']=f
if __name__=='__main__':fn()
