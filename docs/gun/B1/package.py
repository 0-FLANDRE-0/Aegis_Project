from pathlib import Path
import json,hashlib,zipfile,html
H=Path(__file__).resolve().parent;R=H.parents[2];D=R/'downloads';D.mkdir(exist_ok=True);a=json.loads((H/'evidence/acceptance.json').read_text());b=json.loads((H/'build.json').read_text());assert a['readyForReview']and a['newFeaturePass'];game=R/b['output'];sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(game.read_bytes())==b['sha256']==a['htmlSha256']
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS GUN_B1 검증 보고서</title><style>body{font:14px/1.6 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1450px;background:#0e1920;color:#e2ebef}a{color:#8cd9ef}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 monospace}.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}figure{margin:0;padding:8px;background:#1a2b35}img{width:100%;height:auto}code{overflow-wrap:anywhere}.note{padding:12px;background:#513c24}</style><h1>GUN_B1</h1><p>CG52 Mod4 교체 · 127 HE-MFP · 관측 기반 수동 대공 · 마운트 자율 대공</p><p class="note">새 기능 검증 완료. 원래 도메인 exact-state 비교는 417/420이며 CG 3건의 동결 기대값은 갱신하지 않았습니다. 원인·실제 전투 결과·모든 원시 실패를 보고서에 기록했습니다.</p><p>게임 HTML SHA-256: <code>'''+b['sha256']+'</code></p><p><a href="REPORT.md">전체 보고서</a> · <a href="STATUS.md">상태</a> · <a href="evidence/acceptance.json">검수</a> · <a href="GUN_B1.diff">diff</a> · <a href="TEST_MIGRATIONS.md">검사 이관</a> · <a href="REUSE_POLICY.md">실행 SHA/재사용</a> · <a href="README.md">재현</a> · <a href="https://github.com/0-FLANDRE-0/Aegis_Project/blob/gun-b1/docs/gun/B1/remote-readback.json">원격 영수증</a></p><div class="gallery">'
images=sorted((H/'evidence/mod4').glob('*.png'))+sorted((H/'evidence/ui').glob('*.png'))+sorted((H/'evidence/ui-handoff').glob('*.png'))+sorted((H/'evidence/label').glob('*.png'))+list((H/'evidence/effects').glob('effects.svg'));assert images
for p in images:
 rel=p.relative_to(H).as_posix();page+='<figure><figcaption>'+html.escape(p.stem)+'</figcaption><a href="'+rel+'"><img loading="lazy" src="'+rel+'" alt="'+html.escape(p.stem)+'"></a></figure>'
page+='</div><h2>전체 보고서</h2><pre>'+html.escape((H/'REPORT.md').read_text())+'</pre></html>';(H/'INDEX.html').write_text(page)
def included(p):return p.is_file()and'__pycache__'not in p.parts and p.name not in ['remote-readback.json','partial.json']and not any(s.endswith(('-pilot','-initial','-prehandoff','-before-phase'))for s in p.relative_to(H).parts)
items=[game]+sorted(p for p in H.rglob('*')if included(p)and p.name!='CHECKSUMS.sha256');(H/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in items))
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=6)
hz=D/'Aegis_SIM_v48_WIP_GUN_B1_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_GUN_B1_REPORT.zip'
with zipfile.ZipFile(hz,'w')as z:add(z,game.name,game.read_bytes())
with zipfile.ZipFile(rz,'w')as z:
 add(z,'README.txt','REPORT.html을 열면 보고서·그래프·스크린샷을 볼 수 있습니다. 게임 HTML은 별도 HTML ZIP입니다. 원격 readback 영수증은 저장소 docs/gun/B1/remote-readback.json에 별도 후속 커밋으로 기록합니다.\n'.encode());root=page
 for p in ['REPORT.md','STATUS.md','GUN_B1.diff','TEST_MIGRATIONS.md','REUSE_POLICY.md','README.md']:root=root.replace('href="'+p+'"','href="docs/gun/B1/'+p+'"')
 root=root.replace('href="evidence/','href="docs/gun/B1/evidence/').replace('src="evidence/','src="docs/gun/B1/evidence/');add(z,'REPORT.html',root.encode())
 for p in sorted(H.rglob('*')):
  if included(p):add(z,p.relative_to(R).as_posix(),p.read_bytes())
for p in [hz,rz]:
 assert p.stat().st_size<100*1024**2
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
with zipfile.ZipFile(hz)as z:assert z.namelist()==[game.name]and z.read(game.name)==game.read_bytes()
(D/'GUN_B1_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in [game,hz,rz]));print(json.dumps([{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in [game,hz,rz]],indent=2))
