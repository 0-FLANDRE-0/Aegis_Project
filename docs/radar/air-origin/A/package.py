from pathlib import Path
import hashlib,html,json,zipfile
B=Path(__file__).resolve().parent;R=B.parents[3];D=R/'downloads';D.mkdir(exist_ok=True)
q=json.loads((B/'evidence/summary.json').read_text());info=json.loads((B/'build.json').read_text());assert q['contractPass']and q['completedJobs']==38
game=R/info['output'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(game)==info['sha256']
page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AIR_ORIGIN_A</title><style>body{font:14px/1.7 system-ui;max-width:1400px;margin:24px auto;padding:0 18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 monospace}img{max-width:100%;height:auto}</style><h1>AIR_ORIGIN_A</h1><p>원점 계약 복구 · 기존 기대값 유지 · PR 검토 후 중단</p><p><a href="REPORT.md">전체 보고서</a> · <a href="AIR_ORIGIN_A.diff">diff</a> · <a href="evidence/summary.json">검증 자료</a> · <a href="README.md">재현</a></p><pre>'+html.escape((B/'REPORT.md').read_text())+'</pre></html>'
(B/'INDEX.html').write_text(page)
include=lambda p:p.is_file()and'__pycache__'not in p.parts and p.name not in ['CHECKSUMS.sha256','REMOTE_READBACK.json']and p.suffix not in ['.pyc','.tmp']
files=sorted(p for p in B.rglob('*')if include(p));assert all(p.stat().st_size<100*1024**2 for p in files)
(B/'CHECKSUMS.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n'for p in [game]+files));files.append(B/'CHECKSUMS.sha256')
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
hz=D/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:add(z,game.name,game.read_bytes())
root=page
for name in ['REPORT.md','AIR_ORIGIN_A.diff','evidence/summary.json','README.md']:root=root.replace('href="'+name+'"','href="docs/radar/air-origin/A/'+name+'"')
with zipfile.ZipFile(rz,'w')as z:
 add(z,'REPORT.html',root.encode());add(z,'README.txt','REPORT.html을 여세요. 게임은 별도 HTML ZIP입니다. 원격 영수증은 후속 커밋에 별도로 있습니다.\n'.encode())
 for p in sorted(files):add(z,p.relative_to(R).as_posix(),p.read_bytes())
for p in [hz,rz]:
 assert p.stat().st_size<100*1024**2
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
(D/'AIR_ORIGIN_A_SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n'for p in [game,hz,rz]))
print(json.dumps([{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in [game,hz,rz]],indent=2))
