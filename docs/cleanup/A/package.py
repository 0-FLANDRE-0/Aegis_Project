"""Separate runnable HTML and evidence ZIP; no release or tag creation."""
from pathlib import Path
import hashlib,json,zipfile
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda x:hashlib.sha256(x).hexdigest()
html=R/'Aegis_SIM_v48_WIP_CLEAN_A.html';build=json.loads((H/'build.json').read_text())
assert sha(html.read_bytes())==build['sha256']
readme='CLEAN_A 보고서: docs/cleanup/A/REPORT.md\n상태: docs/cleanup/A/STATUS.md\n검수: docs/cleanup/A/ACCEPTANCE.json\n게임 HTML은 별도 HTML.zip입니다.\n전체 합격 보류: 도메인417/420, 최대 유효거리5칸 추가 grid 대기.\n'
def write(z,name,data):
 info=zipfile.ZipInfo(name,(2026,10,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
 z.writestr(info,data,compresslevel=9)
files=[p for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name not in ['FILES_SHA256.json','PACKAGES.json']]
files.append(R/'docs/helicopter/F/verify_regression.py')
manifest={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(files)}
(H/'FILES_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
rz=R/'AEGIS_CLEAN_A_REPORT.zip';hz=R/'Aegis_SIM_v48_WIP_CLEAN_A_HTML.zip'
with zipfile.ZipFile(hz,'w')as z:write(z,html.name,html.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 write(z,'START_HERE.txt',readme.encode());write(z,'docs/cleanup/A/FILES_SHA256.json',(H/'FILES_SHA256.json').read_bytes())
 for p in sorted(files):write(z,str(p.relative_to(R)),p.read_bytes())
with zipfile.ZipFile(hz)as z:assert z.namelist()==[html.name]and sha(z.read(html.name))==build['sha256']and z.testzip()is None
with zipfile.ZipFile(rz)as z:
 assert z.testzip()is None
 for n,s in manifest.items():assert sha(z.read(n))==s['sha256']
data={'html':{'file':html.name,'sha256':build['sha256'],'bytes':html.stat().st_size},'packages':[{'file':p.name,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}for p in [hz,rz]],'reportFiles':len(manifest),'htmlZipOneFile':True,'reportContainsHtml':False,'allZipEntriesVerified':True}
(H/'PACKAGES.json').write_text(json.dumps(data,indent=2)+'\n')
(R/'Aegis_SIM_v48_WIP_CLEAN_A.sha256').write_text(''.join(s['sha256']+'  '+s['file']+'\n'for s in [data['html'],*data['packages']]))
print(json.dumps(data))
