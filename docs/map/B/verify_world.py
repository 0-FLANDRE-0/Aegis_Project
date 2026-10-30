from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));import browser_tools
f=R/'docs/envelope/D/verify_world120.py';s=f.read_text();out=H/'evidence/world120';out.mkdir(parents=True,exist_ok=True);s=s.replace("E=H/'evidence/reg-k'",'E=Path('+repr(str(out))+')');a=s.index("FILES={'recovery':");z=s.index("STATE='''",a);s=s[:a]+"FILES={'recovery':Path("+repr(str(R/'Aegis_SIM_v48_WIP_CLEAN_B.html'))+"),'current':Path("+repr(str(R/'Aegis_SIM_v48_WIP_MAP_B.html'))+")}\n"+s[z:];exec(compile(s,str(f),'exec'),{'__file__':str(f),'__name__':'__main__'})
