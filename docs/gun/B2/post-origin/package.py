"""Package current report and both 60-case cohorts; no new game HTML."""
from pathlib import Path
import hashlib,html,json,zipfile
from source import P,B,R,SOURCE,SOURCE_SHA,sha
q=json.loads((P/'evidence/summary.json').read_text());assert q['pass']and q['cases']==60 and len(q['adverseHpCases'])==1;assert sha(SOURCE.read_bytes())==SOURCE_SHA
report=(B/'PHASE1_START.md').read_text();page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN B2 post-origin</title><style>body{font:14px/1.7 system-ui;max-width:1450px;margin:24px auto;padding:0 20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 monospace}img{max-width:100%;height:auto}.note{background:#fff0d4;padding:12px}</style><h1>GUN_B2 — 원점 복구 후 재진단 / Phase 1 착수 보고</h1><p class="note">60회 완료 · 제품 코드 변경 0 · DDG90 seed419023 피해 악화 1건을 별도 공개 · Phase1 기능 미적용</p><p><a href="../PHASE1_START.md">착수 보고</a> · <a href="evidence/summary.json">통계</a> · <a href="evidence/adverse-native.json">악화 native 확인</a> · <a href="PROTOCOL.md">규약</a></p><a href="plots/comparison.svg"><img src="plots/comparison.png" alt="post-origin comparison"></a><pre>'+html.escape(report)+'</pre></html>'
(P/'INDEX.html').write_text(page)
exclude={'CHECKSUMS.sha256','REMOTE_READBACK.json'}
files=sorted(p for p in P.rglob('*')if p.is_file()and p.name not in exclude and'__pycache__'not in p.parts and p.suffix not in ['.pyc','.tmp'])
extras=[B/n for n in ['PHASE1_START.md','STATUS.md','BUILD_STATUS.json','README.md','INSTRUCTIONS.md','PHASE0.md','PHASE1_PROPOSAL_DRAFT.md','analyze.py','diagnostic/build_fixture.py','diagnostic/hooks.js','diagnostic/http_browser.py']];files=sorted(set(files+extras));assert all(p.stat().st_size<100*1024**2 for p in files)
(P/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in [SOURCE]+files));files.append(P/'CHECKSUMS.sha256')
dest=R/'downloads/Aegis_SIM_v48_WIP_GUN_B2_POST_ORIGIN_REPORT.zip';dest.parent.mkdir(exist_ok=True)
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
root=page
for old,new in [('../PHASE1_START.md','docs/gun/B2/PHASE1_START.md'),('evidence/summary.json','docs/gun/B2/post-origin/evidence/summary.json'),('evidence/adverse-native.json','docs/gun/B2/post-origin/evidence/adverse-native.json'),('PROTOCOL.md','docs/gun/B2/post-origin/PROTOCOL.md')]:root=root.replace('href="'+old+'"','href="'+new+'"')
root=root.replace('href="plots/','href="docs/gun/B2/post-origin/plots/').replace('src="plots/','src="docs/gun/B2/post-origin/plots/')
with zipfile.ZipFile(dest,'w')as z:
 add(z,'REPORT.html',root.encode());add(z,'README.txt','REPORT.html을 여세요. 게임 HTML은 변경하지 않아 포함하지 않습니다. 60회 전후 raw/CSV와 native 동등성, 악화 사례/RNG, 그림, Phase1 착수 보고가 있습니다. 공통 하네스 재현은 전체 저장소가 필요합니다. 원격 영수증은 후속 커밋입니다.\n'.encode())
 for p in sorted(files):add(z,p.relative_to(R).as_posix(),p.read_bytes())
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and all(z.read(p.relative_to(R).as_posix())==p.read_bytes()for p in files)
assert dest.stat().st_size<100*1024**2
(R/'downloads/GUN_B2_POST_ORIGIN_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in [SOURCE,dest,P/'CHECKSUMS.sha256']))
print(json.dumps({'file':str(dest.relative_to(R)),'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'entries':len(files)+2,'crcPass':True}))
