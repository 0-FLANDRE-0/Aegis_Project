"""Diagnostic report only; no new product HTML or version promotion."""
from pathlib import Path
import json,hashlib,zipfile,subprocess
H=Path(__file__).resolve().parent;R=H.parents[3];name='AEGIS_SM6_240KM_RF_DIAGNOSTIC_A_REPORT.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
v=json.loads((H/'verification.json').read_text());assert v['diagnosticPass']and v['productCodeChanges']==0
entries={};exclude={'DELIVERY_MANIFEST.json','delivery.json','remote-publication.json','publication-receipt.json'}
for p in H.rglob('*'):
 if not p.is_file()or p.name in exclude or'__pycache__'in p.parts or p.suffix in ['.html','.zip']:continue
 entries[str(p.relative_to(R))]=p.read_bytes()
# Source support only. Runtime input HTML stays in the pinned product checkout.
for n in ['docs/missile/fuze-zem/A/browser_tools.py','docs/pip/B/browser_backend.py','docs/helicopter/H/browser.py','docs/missile/termination/A/live-fixture.js','docs/missile/termination/A/cases/normal.json']:entries[n]=(R/n).read_bytes()
entries['REPORT_INDEX.md']='''# SM-6 240km RF 진단

[결과 보고서](docs/missile/sm6-rf/A/REPORT.md) · [검수](docs/missile/sm6-rf/A/verification.json) · [재현](docs/missile/sm6-rf/A/REPRODUCE.md)

NATIVE 전체 반환값 동등성 선행 통과. ARH 추정 오차 → 권한 채택/값 소비 → Kappa 명령 → 기동/항력 증가 → 뒤의 COAST 순서를 확인했다. 반사실 둘 다 HANDOFF 명중을 회복한다. 제품 코드/계수 변경0. 측정 생성/연관/EKF 내부의 단일 세부 원인은 아직 미확정이다. 입력 kit, 선행 NATIVE2발 + 이후6발 raw, CSV, 그림과 재현 도구를 포함한다. 실행 HTML은 포함하지 않으며 제품 기준은 launch-handoff-a@99c2ef33이다.
'''.encode()
manifest={'schema':'AEGIS_SM6_240KM_RF_DIAGNOSTIC_A_MANIFEST_1','diagnosticPass':True,'productCodeChanges':0,'coefficientChanges':0,'containsExecutionHtml':False,'files':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(entries.items())]};mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(H/'DELIVERY_MANIFEST.json').write_bytes(mb);entries['DELIVERY_MANIFEST.json']=mb
assert not any(n.lower().endswith(('.html','.zip'))for n in entries)
with zipfile.ZipFile(R/name,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for n,b in sorted(entries.items()):
  i=zipfile.ZipInfo(n,date_time=(2026,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,b,compresslevel=9)
with zipfile.ZipFile(R/name)as z:
 assert z.testzip()is None and z.namelist()==sorted(entries)
 for n,b in entries.items():assert z.read(n)==b
b=(R/name).read_bytes();assert len(b)<100*1024*1024
out={'pass':True,'file':name,'bytes':len(b),'sha256':sha(b),'members':len(entries),'crcValid':True,'allUnpackedBytesVerified':True,'productCodeChanges':0};(H/'delivery.json').write_text(json.dumps(out,indent=2)+'\n');(R/'SHA256SUMS_SM6_240KM_RF_DIAGNOSTIC_A_REPORT_ZIP.txt').write_text(sha(b)+'  '+name+'\n');print(json.dumps(out))
