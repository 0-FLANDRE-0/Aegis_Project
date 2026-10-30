"""Create deterministic HTML-only and evidence/report delivery archives."""
from pathlib import Path
import hashlib,zipfile

H=Path(__file__).resolve().parent;R=H.parents[3]
html=R/'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html'
html_zip=R/'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A_HTML.zip'
report_zip=R/'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A_REPORT.zip'
stamp=(2026,1,1,0,0,0)

def add(z,path,arc):
    info=zipfile.ZipInfo(arc,stamp);info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
    z.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

with zipfile.ZipFile(html_zip,'w') as z:add(z,html,html.name)
files=[R/'AEGIS_PLAN_STATUS_v48_WIP_ARH_MEASUREMENT_FIX_A.md',R/'SHA256SUMS_v48_WIP_ARH_MEASUREMENT_FIX_A.txt']
files += sorted(p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
with zipfile.ZipFile(report_zip,'w') as z:
    for p in files:add(z,p,p.relative_to(R).as_posix())
for p in [html_zip,report_zip]:print(p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
