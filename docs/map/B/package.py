from pathlib import Path
import json,hashlib,zipfile,html
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'downloads';D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((H/'build.json').read_text());accept=json.loads((H/'evidence/acceptance.json').read_text());assert accept['pass'];game=R/build['output'];assert sha(game.read_bytes())==build['sha256']==accept['htmlSha256']
rows=[('도메인 회귀','420 / 420'),('기존 UI','88 / 88'),('MAP_B','91 / 91'),('경고 상태 검수','23 / 23 · 실제 발사 6 / 6'),('추가 UI·실제 WebGL PiP','13 / 13'),('종료기 회귀','300발 · 결과 차이 0 · 새 실패 0'),('자연 탐지→정식 VLS→실제 WebGL','8발 / 29검사 · 기존 결과 동일'),('120초 무표적·전투 truth hash','CLEAN_B와 동일'),('비행 함수 지문','281개 동일'),('사거리표','schema3 / 120행 / byte 동일 / match:true')]
images=[('폰: 실제 3D + PiP','extra/832-webgl-pip.png'),('PC: 실제 3D + PiP','extra/1400-webgl-pip.png'),('발수 선택','map-b/832-salvo.png'),('처음 링','map-b/1400-initial-rings.png'),('유효 · 초록','warnings/832-effective-green.png'),('사각지대 · 발사 가능','warnings/832-deadzone-enabled.png'),('최대 사거리 구간 · 발사 가능','warnings/832-maximum-enabled.png'),('최소 유효거리 안쪽 · 발사 가능','warnings/832-below-effective-enabled.png'),('기존 물리적 최소거리 차단','warnings/832-native-min-blocked.png'),('위치 없는 ESM','map-b/832-esm.png'),('최대 사거리 밖','map-b/832-outside.png'),('트랙 소실','map-b/832-lost.png')]
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS MAP_B 검증 보고서</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1250px;background:#0d171e;color:#e1eaf0}a{color:#8bd9ee}h1,h2{line-height:1.3}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #3b515d;padding:6px 10px;text-align:left}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}figure{margin:0;padding:8px;background:#192a34}img{width:100%;height:auto}pre{white-space:pre-wrap;word-break:break-word;font:12px/1.6 monospace}code{overflow-wrap:anywhere}</style><h1>MAP_B 검증 보고서</h1><p>하단 SAM 무장·발수 선택, 측정 사거리 링, 표적 교전 탭을 메인 지도와 PiP에 추가했습니다. 비행·유도·센서·신관·기존 발사 관문과 사거리표는 보존했습니다.</p><p><strong>유효는 초록, 사각지대·최대 사거리 구간·최소 유효거리 안쪽은 주황 경고로 발사 가능.</strong> 기존 관문 거부·최대 사거리 밖·판정 불가·트랙 소실은 빨강으로 차단합니다. 기존 물리적 최소거리 제한은 그대로입니다.</p>'''
page+='<p>브랜치 <code>map-b</code> · main 병합/release/tag 없음. <a href="REPORT.md">전체 보고서</a> · <a href="evidence/acceptance.json">검수 원문</a> · <a href="MAP_B.diff">변경 diff</a> · <a href="data-sources.json">입력 감사</a></p><p>게임 HTML SHA-256: <code>'+build['sha256']+'</code></p><table><tr><th>항목</th><th>결과</th></tr>'+''.join('<tr><td>'+html.escape(a)+'</td><td>'+html.escape(b)+'</td></tr>'for a,b in rows)+'</table>'
page+='<p>자연 발사 8발의 명중은 기존과 같은 4/8입니다. 기존 SM-6/ESSM 비명중 4발은 UI 작업에서 수정하지 않았습니다. 장시간 비행 회귀는 실행한 중간 HTML SHA를 원문에 남겼으며, 최종 파일의 동일 비행 지문과 현재 코어·UI·상태 해시를 별도로 검증했습니다.</p><div class="gallery">'
for label,p in images:
 assert(H/'evidence'/p).exists();page+='<figure><figcaption>'+html.escape(label)+'</figcaption><a href="evidence/'+p+'"><img loading="lazy" src="evidence/'+p+'" alt="'+html.escape(label)+'"></a></figure>'
page+='</div><details><summary>전체 보고서 원문 펼치기</summary><pre>'+html.escape((H/'REPORT.md').read_text())+'</pre></details></html>'
(H/'INDEX.html').write_text(page)
# Content checksums are inside the report. Archive checksums are outside it.
items=[game]+sorted(p for p in H.rglob('*')if p.is_file()and p.name!='CHECKSUMS.sha256'and'__pycache__'not in p.parts)
(H/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+str(p.relative_to(R))+'\n'for p in items))
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
htmlzip=D/'Aegis_SIM_v48_WIP_MAP_B_HTML.zip';reportzip=D/'Aegis_SIM_v48_WIP_MAP_B_REPORT.zip'
with zipfile.ZipFile(htmlzip,'w')as z:add(z,game.name,game.read_bytes())
with zipfile.ZipFile(reportzip,'w')as z:
 add(z,'README.txt','REPORT.html을 브라우저에서 열면 검증 결과와 스크린샷을 볼 수 있습니다. 게임 HTML은 별도 HTML ZIP에 있습니다. 상세 파일은 docs/map/B 아래에 있습니다.\n'.encode())
 root=page.replace('href="REPORT.md"','href="docs/map/B/REPORT.md"').replace('href="MAP_B.diff"','href="docs/map/B/MAP_B.diff"').replace('href="data-sources.json"','href="docs/map/B/data-sources.json"').replace('href="evidence/','href="docs/map/B/evidence/').replace('src="evidence/','src="docs/map/B/evidence/')
 add(z,'REPORT.html',root.encode())
 for p in sorted(H.rglob('*')):
  if p.is_file()and'__pycache__'not in p.parts:add(z,str(p.relative_to(R)),p.read_bytes())
for p in [htmlzip,reportzip]:
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
(D/'MAP_B_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+str(p.relative_to(R))+'\n'for p in [game,htmlzip,reportzip]))
print(json.dumps([{'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in [game,htmlzip,reportzip]],indent=2))
