from pathlib import Path
import json,hashlib,zipfile,html
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'downloads';D.mkdir(exist_ok=True);j=lambda p:json.loads((H/p).read_text());a=j('evidence/acceptance.json');b=j('build.json');assert a['pass'];game=R/b['output'];sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(game.read_bytes())==b['sha256']==a['htmlSha256']
rows=[('도메인',str(a['counts']['domain'])+'/420'),('UI / MAP_B / 경고 / 추가','88 / 91 / 23 / 13 통과'),('MAP_C','135 / 73 / 45 / 33 / 13 통과'),('MAP_D','84 / 213 / 145 통과'),('종료기 / 실제 자연 WebGL','300발 개별 결과 동일 / 8발 궤적·결과 동일'),('새 MAP_E','UI '+str(a['counts']['E_UI'])+' + 단계 11 + 정책 33 통과'),('EW / H3','94 / 195 D/E 동일'),('보존','native281 / ENV_D120행 동일, world120 무표적·전투 해시 동일')]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS MAP_E 검증 보고서</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1400px;background:#0d171e;color:#e1eaf0}a{color:#8bd9ee}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #3b515d;padding:6px 10px;text-align:left}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}figure{margin:0;padding:8px;background:#192a34}img{width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.6 monospace}code{overflow-wrap:anywhere}</style><h1>MAP_E 검증 보고서</h1><p>레거시 ARM을 제거하고 EMCON/ECM 팝오버, 수동 SRBOC/Nulka 팝업, 지도 하푼 MANUAL 권한을 연결했습니다. 기존 함수와 비행·센서·무장 관문은 보존했습니다.</p><p>HTML SHA-256: <code>'''+b['sha256']+'</code></p><p><a href="REPORT.md">전체 보고서</a> · <a href="STATE.md">상태</a> · <a href="evidence/acceptance.json">검수</a> · <a href="MAP_E.diff">diff</a> · <a href="TEST_MIGRATIONS.md">시험 이관</a> · <a href="data-sources.json">입력 감사</a> · <a href="https://github.com/0-FLANDRE-0/Aegis_Project/blob/map-e/docs/map/E/remote-readback.json">원격 영수증</a></p><table><tr><th>검사</th><th>결과</th></tr>'+''.join('<tr><td>'+html.escape(x)+'</td><td>'+html.escape(y)+'</td></tr>'for x,y in rows)+'</table><p>PC 1400×900 / 폰 832×384 · MAIN / 실제 WebGL 3D+PiP · DDG/CG. UI는 최종 HTML에서 재검증했습니다. 표시 폭 보정 전 native 증거는 실제 실행 SHA를 유지하며, MAP_E_UI 밖 전체 코드 byte 동일 증거로 재사용했습니다. 실제 휴대폰 FPS 측정은 아닙니다. EMCON 비방사 지정의 새 UI 위치는 사용자 결정으로 후속 검토합니다. main 병합·release·tag 생성 없음.</p><div class="gallery">'
images=sorted((H/'evidence/e-new').glob('*.png'))+sorted((H/'evidence/d-ui').glob('*route8.png'));assert images
for p in images:
 rel=p.relative_to(H).as_posix();page+='<figure><figcaption>'+html.escape(p.stem)+'</figcaption><a href="'+rel+'"><img loading="lazy" src="'+rel+'" alt="'+html.escape(p.stem)+'"></a></figure>'
page+='</div><h2>전체 보고서</h2><pre>'+html.escape((H/'REPORT.md').read_text())+'</pre></html>';(H/'INDEX.html').write_text(page)
# Development captures are duplicated/stale presentation versions, never final evidence.
for p in(H/'evidence/development').rglob('*.png'):p.unlink()
for p in(H/'evidence').glob('smoke-*.png'):p.unlink()
def included(p):return p.is_file()and'__pycache__'not in p.parts and p.name!='remote-readback.json'
items=[game]+sorted(p for p in H.rglob('*')if included(p)and p.name!='CHECKSUMS.sha256');(H/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in items))
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
hz=D/'Aegis_SIM_v48_WIP_MAP_E_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_MAP_E_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:add(z,game.name,game.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 add(z,'README.txt','REPORT.html을 열면 검증 결과·스크린샷을 볼 수 있습니다. 게임 HTML은 별도 HTML ZIP에 있습니다. 원격 readback 영수증은 저장소 docs/map/E/remote-readback.json에 별도 기록합니다(아카이브 자체 해시 순환 참조 방지).\n'.encode())
 root=page
 for p in ['REPORT.md','STATE.md','MAP_E.diff','TEST_MIGRATIONS.md','data-sources.json']:root=root.replace('href="'+p+'"','href="docs/map/E/'+p+'"')
 root=root.replace('href="evidence/','href="docs/map/E/evidence/').replace('src="evidence/','src="docs/map/E/evidence/');add(z,'REPORT.html',root.encode())
 for p in sorted(H.rglob('*')):
  if included(p):add(z,p.relative_to(R).as_posix(),p.read_bytes())
for p in[hz,rz]:
 assert p.stat().st_size<100*1024**2,(p,p.stat().st_size)
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
with zipfile.ZipFile(hz)as z:assert z.namelist()==[game.name]and z.read(game.name)==game.read_bytes()
(D/'MAP_E_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game,hz,rz]));print(json.dumps([{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in[game,hz,rz]],indent=2))
