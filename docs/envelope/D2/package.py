from pathlib import Path
import hashlib,json,zipfile
H=Path(__file__).resolve().parent;R=H.parents[2];base='Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A';build=json.loads((H/'build.json').read_text());verification=json.loads((H/'evidence/verification.json').read_text());assert verification['pass']
status=R/'AEGIS_PLAN_STATUS_v48_WIP_ENV_D_REMEASURE_A.md'
status.write_text('# ENV_D 재측정 A 상태\n\n기준: near-vertical-path-fix-a / 38a4f97527b48027fa64f0673cea14a9c83c116d.\n\n기본120칸 + 보조6칸 측정 완료. 제품 게임 함수 변경0. 새 표는 지도·발사·AI에 연결하지 않음. 상세 결과와 재현 도구는 docs/envelope/D2/REPORT.md.\n\nmain 병합 및 release/tag 생성 없음.\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[R/build['output'],status,H/'REPORT.md',H/'ENVELOPE_TABLE_D.json',H/'evidence/verification.json'];sums=R/'SHA256SUMS_v48_WIP_ENV_D_REMEASURE_A.txt';sums.write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n'for p in files))
def pack(out,items):
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in items:
   i=zipfile.ZipInfo(str(p.relative_to(R)),date_time=(2026,10,25,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16;z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
html=R/(base+'_HTML.zip');report=R/(base+'_REPORT.zip');pack(html,[R/build['output']]);items=[status,sums]+sorted(p for p in H.rglob('*')if p.is_file()and'__pycache__'not in p.parts and not p.name.endswith('.pyc'));pack(report,items)
delivery=R/'DELIVERY_SHA256SUMS_v48_WIP_ENV_D_REMEASURE_A.txt';delivery.write_text(''.join(sha(p)+'  '+p.name+'\n'for p in [html,report]));print(json.dumps({p.name:{'bytes':p.stat().st_size,'sha256':sha(p)}for p in [R/build['output'],html,report]},indent=2))
