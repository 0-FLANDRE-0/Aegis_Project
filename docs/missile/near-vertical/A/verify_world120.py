"""Run the existing 120-second idle/combat truth-hash comparison on BASE/FINAL."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[3];original=R/'docs/envelope/D/verify_world120.py';s=original.read_text();out=H/'world120';out.mkdir(exist_ok=True);build=json.loads((H/'build.json').read_text());base=Path(build['variants']['BASE']['file']);final=Path(build['variants']['FINAL']['file'])
s=s.replace("E=H/'evidence/reg-k'",'E=Path('+repr(str(out))+')');start=s.index("FILES={'recovery':");end=s.index("STATE='''",start);s=s[:start]+"FILES={'recovery':Path("+repr(str(base))+"),'current':Path("+repr(str(final))+ ")}\n"+s[end:];exec(compile(s,str(original),'exec'),{'__file__':str(original),'__name__':'__main__'})
