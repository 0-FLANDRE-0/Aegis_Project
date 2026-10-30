from pathlib import Path
import json,hashlib,zipfile,html
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'downloads';D.mkdir(exist_ok=True);j=lambda p:json.loads((H/p).read_text());b=j('build.json');a=j('evidence/acceptance.json');assert a['pass'];game=R/b['output'];sha=lambda q:hashlib.sha256(q).hexdigest();assert sha(game.read_bytes())==b['sha256']==a['htmlSha256']
rows=[('도메인','420/420'),('UI / MAP_B / 경고 / 추가','88 / 91 / 23 / 13 전부 통과'),('MAP_C','135 / 73 / 45 / 33 / 13 전부 통과'),('종료기 / 실제 자연 WebGL','300발 / 8발, 이전 결과 동일'),('120초 truth','무표적/전투 해시 동일'),('native / 사거리표','281함수 / 120행 byte 동일'),('MAP_D','native '+str(a['counts']['D_native'])+' / UI '+str(a['counts']['D_ui'])+' / 경계 '+str(a['counts']['D_edges'])+' 통과')]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS MAP_D 검증 보고서</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1400px;background:#0d171e;color:#e1eaf0}a{color:#8bd9ee}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #3b515d;padding:6px 10px;text-align:left}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}figure{margin:0;padding:8px;background:#192a34}img{width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 monospace}code{overflow-wrap:anywhere}</style><h1>MAP_D 검증 보고서</h1><p>RGM-84 하푼과 Mk45를 기존 지도·PiP의 선택/태그/발사 슬롯에 연결했습니다. 기존 비행·탄도·신관·사통·권한과 사거리표는 보존했습니다.</p><p>HTML SHA-256: <code>'''+b['sha256']+'</code></p><p><a href="REPORT.md">전체 보고서</a> · <a href="STATE.md">상태</a> · <a href="evidence/acceptance.json">검수</a> · <a href="MAP_D.diff">diff</a> · <a href="data-sources.json">입력 감사</a> · <a href="https://github.com/0-FLANDRE-0/Aegis_Project/blob/map-d/docs/map/D/remote-readback.json">원격 영수증</a></p><table><tr><th>항목</th><th>결과</th></tr>'+''.join('<tr><td>'+html.escape(x)+'</td><td>'+html.escape(y)+'</td></tr>'for x,y in rows)+'</table><p>PC 1400×900 / 폰 832×384 · MAIN / 실제 WebGL 3D+PiP · DDG/CG. CG 평상시 공동 사계는 360°이며 공동 사각은 기존25° 횡경사의 내림각 한계로 재현했습니다. 헤드리스 기능 검사이며 실제 휴대폰 FPS 측정은 아닙니다. main 병합·release·tag 생성 없음.</p><div class="gallery">'
images=[]
for group in ['d-ui','d-edges']:
 for p in sorted((H/'evidence'/group).glob('*.png')):images.append(p)
assert images
for p in images:
 rel=p.relative_to(H).as_posix();label=p.stem;page+='<figure><figcaption>'+html.escape(label)+'</figcaption><a href="'+rel+'"><img loading="lazy" src="'+rel+'" alt="'+html.escape(label)+'"></a></figure>'
page+='</div><h2>전체 보고서</h2><pre>'+html.escape((H/'REPORT.md').read_text())+'</pre></html>';(H/'INDEX.html').write_text(page)
# Keep development results/logs but avoid duplicate development screenshots.
for p in(H/'evidence/development').rglob('*.png'):p.unlink()
def included(p):return p.is_file()and'__pycache__'not in p.parts and p.name!='remote-readback.json'
items=[game]+sorted(p for p in H.rglob('*')if included(p)and p.name!='CHECKSUMS.sha256');(H/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in items))
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
hz=D/'Aegis_SIM_v48_WIP_MAP_D_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_MAP_D_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:add(z,game.name,game.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 add(z,'README.txt','REPORT.html을 열면 검증 결과와 스크린샷을 볼 수 있습니다. 게임 HTML은 별도 HTML ZIP에 있습니다. 원격 readback 영수증은 저장소 docs/map/D/remote-readback.json에 별도 기록합니다(아카이브 자체 해시 순환 참조 방지).\n'.encode())
 root=page
 for p in ['REPORT.md','STATE.md','MAP_D.diff','data-sources.json']:root=root.replace('href="'+p+'"','href="docs/map/D/'+p+'"')
 root=root.replace('href="evidence/','href="docs/map/D/evidence/').replace('src="evidence/','src="docs/map/D/evidence/');add(z,'REPORT.html',root.encode())
 for p in sorted(H.rglob('*')):
  if included(p):add(z,p.relative_to(R).as_posix(),p.read_bytes())
for p in[hz,rz]:
 assert p.stat().st_size<100*1024**2
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
with zipfile.ZipFile(hz)as z:assert z.namelist()==[game.name]and z.read(game.name)==game.read_bytes()
(D/'MAP_D_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game,hz,rz]));print(json.dumps([{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in[game,hz,rz]],indent=2))
