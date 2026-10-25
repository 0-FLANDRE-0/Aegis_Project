"""Report bundle only. No modified product HTML exists in this stage."""
from pathlib import Path
import json,hashlib,zipfile
H=Path(__file__).resolve().parent;R=H.parents[3];name='AEGIS_ARH_MEASUREMENT_CONTRACT_A_REPORT.zip';sha=lambda b:hashlib.sha256(b).hexdigest()
assert json.loads((H/'verification.json').read_text())['diagnosticPass']
entries={};exclude={'DELIVERY_MANIFEST.json','delivery.json','remote-publication.json','publication-receipt.json'}
for p in H.rglob('*'):
 if p.is_file()and p.name not in exclude and'__pycache__'not in p.parts and p.suffix not in ['.html','.zip']:entries[str(p.relative_to(R))]=p.read_bytes()
for n in ['docs/missile/fuze-zem/A/browser_tools.py','docs/pip/B/browser_backend.py','docs/helicopter/H/browser.py','docs/missile/termination/A/live-fixture.js','docs/missile/termination/A/cases/normal.json']:entries[n]=(R/n).read_bytes()
entries['REPORT_INDEX.md']='''# 현재 SM-6 ARH 측정 계약 확인

[결과](docs/missile/arh-measurement/A/REPORT.md) · [검수](docs/missile/arh-measurement/A/verification.json) · [재현](docs/missile/arh-measurement/A/REPRODUCE.md)

실제 활성 SM6 프로파일에서도 각도/시커 중심 의존과 생성 잡음/R 불일치가 모두 재현됐다. actual native22점과VM오차0. 계약 검사의FAIL과 재현 절차의PASS를 구분한다. 제품 코드/계수 수정0, 새 비행 적분0.240km 수정후 회복은 아직 시험하지 않았다. 실행 HTML은 포함하지 않는다.
'''.encode()
manifest={'schema':'AEGIS_ARH_MEASUREMENT_CONTRACT_A_REPORT_MANIFEST_1','productCodeChanges':0,'containsHtml':False,'files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]};mb=(json.dumps(manifest,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb
with zipfile.ZipFile(R/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for n,b in sorted(entries.items()):
  i=zipfile.ZipInfo(n,date_time=(2026,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b,compresslevel=9)
with zipfile.ZipFile(R/name)as z:
 assert z.testzip()is None and z.namelist()==sorted(entries)
 for n,b in entries.items():assert z.read(n)==b
b=(R/name).read_bytes();out={'pass':True,'file':name,'bytes':len(b),'sha256':sha(b),'members':len(entries),'crcValid':True,'allUnpackedBytesVerified':True};(H/'delivery.json').write_text(json.dumps(out,indent=2)+'\n');(R/'SHA256SUMS_ARH_MEASUREMENT_CONTRACT_A_REPORT_ZIP.txt').write_text(sha(b)+'  '+name+'\n');print(json.dumps(out))
