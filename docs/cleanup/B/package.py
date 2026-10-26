"""Separate executable HTML and a checksummed evidence ZIP; no release/tag."""
from pathlib import Path
import hashlib,json,zipfile
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((H/'build.json').read_text());html=R/build['output'];assert sha(html.read_bytes())==build['sha256'];assert json.loads((H/'ACCEPTANCE.json').read_text())['pass']
files=[p for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name not in ['FILES_SHA256.json','PACKAGES.json','remote-publication.json']];files.append(R/'docs/helicopter/F/verify_regression.py')
manifest={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(files)};(H/'FILES_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
def write(z,name,b):
 info=zipfile.ZipInfo(name,(2026,10,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,b,compresslevel=9)
hz=R/'Aegis_SIM_v48_WIP_CLEAN_B_HTML.zip';rz=R/'AEGIS_CLEAN_B_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:write(z,html.name,html.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 write(z,'START_HERE.txt','CLEAN_B 보고서: docs/cleanup/B/REPORT.md\n검수: docs/cleanup/B/ACCEPTANCE.json\n상태: docs/cleanup/B/STATUS.json\n게임 HTML은 별도 HTML ZIP입니다.\n'.encode());write(z,'docs/cleanup/B/FILES_SHA256.json',(H/'FILES_SHA256.json').read_bytes())
 for p in sorted(files):write(z,str(p.relative_to(R)),p.read_bytes())
with zipfile.ZipFile(hz)as z:assert z.namelist()==[html.name]and z.testzip()is None and sha(z.read(html.name))==build['sha256']
with zipfile.ZipFile(rz)as z:
 assert z.testzip()is None
 for n,s in manifest.items():assert sha(z.read(n))==s['sha256']
out={'html':{'file':html.name,'bytes':html.stat().st_size,'sha256':build['sha256']},'packages':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in [hz,rz]],'reportFiles':len(files),'htmlZipOneFile':True,'allEntriesVerified':True};(H/'PACKAGES.json').write_text(json.dumps(out,indent=2)+'\n');(R/'Aegis_SIM_v48_WIP_CLEAN_B.sha256').write_text(''.join(r['sha256']+'  '+r['file']+'\n'for r in [out['html'],*out['packages']]));print(json.dumps(out))
