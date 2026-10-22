"""Archive the exact previous eight delivery artifacts; record Git identity."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];dst=R/'archive/v48/WIP_ALL4_TERM';dst.mkdir(parents=True,exist_ok=True)
names=['Aegis_SIM_v48_WIP_ALL4_TERM.html','AEGIS_PLAN_STATUS_v48_WIP_ALL4_TERM.md','SHA256SUMS_v48_WIP_ALL4_TERM.txt','Aegis_SIM_v48_WIP_ALL4_TERM_HTML.zip','SHA256SUMS_v48_WIP_ALL4_TERM_HTML_ZIP.txt','Aegis_SIM_v48_WIP_ALL4_TERM_REPORT.zip','SHA256SUMS_v48_WIP_ALL4_TERM_REPORT_ZIP.txt','.github/workflows/missile-b4-termination.yml'];rows=[]
for name in names:
 src=R/name;out=dst/src.name
 old=subprocess.check_output(['git','show','9a6838aade07c37262453e21cfe415d04d123d8c:'+name],cwd=R)
 if src.exists():
  assert src.read_bytes()==old
  subprocess.run(['git','mv','--sparse',name,str(out.relative_to(R))],cwd=R,check=True)
 assert out.read_bytes()==old
 rows.append({'old':name,'archive':str(out.relative_to(R)),'bytes':len(old),'sha256':hashlib.sha256(old).hexdigest(),'gitBlob':subprocess.check_output(['git','hash-object',str(out)],cwd=R,text=True).strip(),'identical':True})
(H/'archive-verification.json').write_text(json.dumps({'pass':True,'files':rows},indent=2))
print('Archived exact previous artifacts:',len(rows))
