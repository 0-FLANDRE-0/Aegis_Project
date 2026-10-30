from pathlib import Path
import hashlib,zipfile
H=Path(__file__).resolve().parent;R=H.parents[3]
html=R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html';status=R/'AEGIS_PLAN_STATUS_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.md';report=H/'REPORT.md';summary=H/'verification-summary.json';diff=H/'kappa-pip.diff'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=R/'SHA256SUMS_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.txt';checks.write_text(''.join(f'{sha(p)}  {p.relative_to(R)}\n'for p in [html,status,report,summary,diff]))
html_zip=R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A_HTML.zip';report_zip=R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A_REPORT.zip'
with zipfile.ZipFile(html_zip,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:z.write(html,html.name)
with zipfile.ZipFile(report_zip,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in [status,checks]:z.write(p,p.relative_to(R))
 for p in sorted(H.rglob('*')):
  if p.is_file()and'__pycache__'not in p.parts:z.write(p,p.relative_to(R))
delivery=R/'DELIVERY_SHA256SUMS_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.txt';delivery.write_text(f'{sha(html_zip)}  {html_zip.name}\n{sha(report_zip)}  {report_zip.name}\n')
print({'html':{'bytes':html.stat().st_size,'sha256':sha(html)},'htmlZip':{'bytes':html_zip.stat().st_size,'sha256':sha(html_zip)},'reportZip':{'bytes':report_zip.stat().st_size,'sha256':sha(report_zip)}})
