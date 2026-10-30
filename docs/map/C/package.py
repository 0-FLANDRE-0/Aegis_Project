from pathlib import Path
import json,hashlib,zipfile,html
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'downloads';D.mkdir(exist_ok=True);j=lambda p:json.loads((H/p).read_text());b=j('build.json');a=j('evidence/acceptance.json');assert a['pass'];game=R/b['output'];sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(game.read_bytes())==b['sha256']==a['htmlSha256'];counts=a['counts'];m=j('evidence/motion/motion.json')
rows=[('도메인 회귀','420/420'),('기존 UI / MAP_B','88/88 · 91/91'),('경고 / 추가 UI','23/23 · 13/13 · 경고 실제 발사 6/6'),('종료기','300발 · 결과 차이 0 · 222→222'),('실제 WebGL 자연 발사','8발 · 29검사 · 기존 4/8 명중 유지'),('120초 truth','무표적/전투 둘 다 MAP_B와 동일'),('비행 함수 / 사거리표','281개 동일 · 120행 byte 동일 · match:true'),('추종','12조건 · 각 10초 이상 · 실제 arc 최대 오차 '+format(max(r['maxActualArcErrorPx']for r in m['rows']),'.6g')+'px')]
images=[('폰: 실제 WebGL 3D + PiP','extra/832-webgl-pip.png'),('PC: 실제 WebGL 3D + PiP','extra/1400-webgl-pip.png')]
for w in [832,1400]:
 for s in ['MAIN','PIP']:
  for key,label in [('effective','유효 · 2줄 태그'),('deadzone','사각지대 경고'),('maximum','최대 사거리 경고'),('minimum','최소 유효거리 안쪽 경고'),('outside','사거리 밖'),('lost','트랙 소실'),('cycle','재탭 순환'),('right-list','우클릭 후보 목록')]:images.append((str(w)+' '+s+' · '+label,f'new-ui/{w}.{s}-{key}.png'))
  for key,label in [('initial-rings','초기 링·시간 영역'),('esm','ESM 위치 없음'),('ally','아군 정보·통제 규칙')]:images.append((str(w)+' '+s+' · '+label,f'rules/{w}.{s}-{key}.png'))
 images.extend([(str(w)+' · 시간 블록 위계',f'new-ui/{w}.PIP-clock-layer.png'),(str(w)+' · PiP를 시간 아래로 이동',f'new-ui/{w}.PIP-clock-over-pip.png')])
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS MAP_C 검증 보고서</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1400px;background:#0d171e;color:#e1eaf0}a{color:#8bd9ee}h1,h2{line-height:1.3}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #3b515d;padding:6px 10px;text-align:left}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}figure{margin:0;padding:8px;background:#192a34}img{width:100%;height:auto}pre{white-space:pre-wrap;word-break:break-word;font:12px/1.6 monospace}code{overflow-wrap:anywhere}</style><h1>MAP_C 검증 보고서</h1><p>교전 미니 태그, 하단 고정 발사 슬롯, 오른쪽 위 시간 블록과 직접 탭·재탭 순환을 추가했습니다. 링 형상·색·측정 표·게임 규칙은 보존했습니다.</p><p>최종 HTML SHA-256: <code>'''+b['sha256']+'</code></p><p><a href="REPORT.md">전체 보고서</a> · <a href="STATE.md">상태</a> · <a href="evidence/acceptance.json">최종 검수</a> · <a href="MAP_C.diff">변경 diff</a> · <a href="data-sources.json">입력 감사</a> · <a href="https://github.com/0-FLANDRE-0/Aegis_Project/blob/map-c/docs/map/C/remote-readback.json">원격 readback 영수증(저장소)</a></p><table><tr><th>항목</th><th>결과</th></tr>'+''.join('<tr><td>'+html.escape(x)+'</td><td>'+html.escape(y)+'</td></tr>'for x,y in rows)+'</table><p>main 병합·release·tag 생성 없음. 이 검수는 헤드리스 소프트웨어 GPU 환경의 기능/정합 검사이며 실기기 FPS 수치가 아닙니다. 각 추종 시험의 실제 렌더 표본 수와 시뮬 진행 시간을 전체 보고서에 기록했습니다.</p><div class="gallery">'
for label,p in images:
 assert(H/'evidence'/p).exists(),p;page+='<figure><figcaption>'+html.escape(label)+'</figcaption><a href="evidence/'+p+'"><img loading="lazy" src="evidence/'+p+'" alt="'+html.escape(label)+'"></a></figure>'
page+='</div><h2>전체 보고서</h2><pre>'+html.escape((H/'REPORT.md').read_text())+'</pre></html>';(H/'INDEX.html').write_text(page)
# Retain initial data/logs, avoid shipping duplicate development screenshots.
for p in(H/'evidence/initial').rglob('*.png'):p.unlink()
def included(p):return p.is_file()and'__pycache__'not in p.parts and p.name!='remote-readback.json'
items=[game]+sorted(p for p in H.rglob('*')if included(p)and p.name!='CHECKSUMS.sha256');(H/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+str(p.relative_to(R))+'\n'for p in items))
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
hz=D/'Aegis_SIM_v48_WIP_MAP_C_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_MAP_C_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:add(z,game.name,game.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 add(z,'README.txt','REPORT.html을 열면 결과와 스크린샷을 볼 수 있습니다. 게임 HTML은 별도 HTML ZIP에 있습니다. 원격 readback 영수증은 저장소 docs/map/C/remote-readback.json에 별도 기록됩니다(아카이브 자체 해시의 순환 참조 방지).\n'.encode())
 root=page
 for p in ['REPORT.md','STATE.md','MAP_C.diff','data-sources.json']:root=root.replace('href="'+p+'"','href="docs/map/C/'+p+'"')
 root=root.replace('href="evidence/','href="docs/map/C/evidence/').replace('src="evidence/','src="docs/map/C/evidence/');add(z,'REPORT.html',root.encode())
 for p in sorted(H.rglob('*')):
  if included(p):add(z,str(p.relative_to(R)),p.read_bytes())
for p in [hz,rz]:
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
with zipfile.ZipFile(hz)as z:assert z.namelist()==[game.name]and z.read(game.name)==game.read_bytes()
(D/'MAP_C_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+str(p.relative_to(R))+'\n'for p in [game,hz,rz]));print(json.dumps([{'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in [game,hz,rz]],indent=2))
