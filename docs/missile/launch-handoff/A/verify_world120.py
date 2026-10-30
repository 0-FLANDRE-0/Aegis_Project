"""Run the unchanged original 120s whole-world comparison with selected HTMLs.
Only the two input paths and output folder/labels are adapted.
"""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent;R=H.parents[3]
original=R/'docs/envelope/D/verify_world120.py'
s=original.read_text()
old=R/'Aegis_SIM_v48_WIP_FUZE_ZEM_A.html'
if not old.exists():old=R/'archive/v48/WIP_FUZE_ZEM_A'/old.name
out=H/'final-evidence/world120';out.mkdir(exist_ok=True)
new=Path(json.loads((H/'build.json').read_text())['file'])
s=s.replace("E=H/'evidence/reg-k'",'E=Path('+repr(str(out))+')')
start=s.index("FILES={'recovery':");end=s.index("STATE='''",start)
s=s[:start]+"FILES={'recovery':Path("+repr(str(old))+"),'current':Path("+repr(str(new))+ ")}\n"+s[end:]
exec(compile(s,str(original),'exec'),{'__file__':str(original),'__name__':'__main__'})
