"""Separate game/report ZIPs; immutable bytes, checksums and CRC verified."""
from pathlib import Path
import hashlib,html,json,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];D=R/'downloads';sha=lambda b:hashlib.sha256(b).hexdigest();game=R/'Aegis_SIM_v48_WIP_GUN_B2.html';status=json.loads((P/'BUILD_STATUS.json').read_text());assert status['implemented']and status['within3Hours'];assert json.loads((P/'evidence/scope.json').read_text())['pass'];assert json.loads((P/'evidence/g7-summary.json').read_text())['complete'];report=(P/'REPORT.md').read_text()
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN_B2A report</title><style>body{font:14px/1.7 system-ui;max-width:1500px;margin:25px auto;padding:0 16px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 monospace}img{max-width:100%;height:auto}a{margin-right:14px}.note{background:#fff0cd;padding:12px}</style><h1>GUN_B2A</h1><p class="note">지정 측정 완료. 하푼 nativeFinish/종료로그2단언은 실제 피해MISS로 미통과이며 기준값/계수/seed로 맞추지 않았다.</p><p><a href="REPORT.md">보고서</a><a href="MATCHING.md">적용 전 계산</a><a href="GUN_B2A.diff">게임 diff</a><a href="TEST_REUSE.json">검사 재사용</a><a href="ASSERTION_MIGRATIONS.json">단언 교체</a></p>'''
for n,t in[('single-shot-pk','단발 Pk 전후'),('dispersion-anchor','앵커400발'),('g7-comparison','자연 G7 전후120회')]:page+='<h2>'+t+'</h2><a href="plots/'+n+'.svg"><img src="plots/'+n+'.png" alt="'+t+'"></a>'
page+='<pre>'+html.escape(report)+'</pre></html>';(P/'INDEX.html').write_text(page)
exclude={'REMOTE_READBACK.json','CHECKSUMS.sha256','PACKAGE_RECEIPT.json'};files=sorted(p for p in P.rglob('*')if p.is_file()and p.name not in exclude and'__pycache__'not in p.parts and p.suffix not in ['.pyc','.tmp'])
# Add the exact historical reports referenced by the source-guard reuse ledger.
ledger=json.loads((P/'TEST_REUSE.json').read_text());extras=[R/r['report']for r in ledger['items']];extras += [P.parent/'phase1'/n for n in ['range-table.json','measurement-build.json','REPORT.md','PARAMETERS.md','PROTOCOL.md','evidence/surface/execution.json','evidence/dispersion-final/validation.json']];extras += [R/'docs/radar/air-origin/A/approved-expectations.json',R/'docs/gun/B1/TEST_MIGRATIONS.md',R/'docs/gun/B2/PHASE1_START.md'];files=sorted(set(files+extras));assert all(p.exists()for p in files)
(P/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game]+files));files.append(P/'CHECKSUMS.sha256')
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=7)
gz=D/'Aegis_SIM_v48_WIP_GUN_B2A_HTML.zip';rz=D/'Aegis_SIM_v48_WIP_GUN_B2A_REPORT.zip';D.mkdir(exist_ok=True)
with zipfile.ZipFile(gz,'w')as z:
 add(z,game.name,game.read_bytes());add(z,'SHA256SUMS.txt',(sha(game.read_bytes())+'  '+game.name+'\n').encode());add(z,'README.txt','압축 해제한 Aegis_SIM_v48_WIP_GUN_B2.html을 브라우저로 여세요. B2A 누적 게임용 SIM_TUNED 빌드입니다. 검증과 남은2단언은 별도 REPORT.zip에 있습니다.\n'.encode())
root=page
for prefix in ['plots/']:
 root=root.replace('href="'+prefix,'href="docs/gun/B2/phase1a/'+prefix).replace('src="'+prefix,'src="docs/gun/B2/phase1a/'+prefix)
for n in ['REPORT.md','MATCHING.md','GUN_B2A.diff','TEST_REUSE.json','ASSERTION_MIGRATIONS.json']:root=root.replace('href="'+n+'"','href="docs/gun/B2/phase1a/'+n+'"')
bundle={p.relative_to(R).as_posix():p.read_bytes()for p in files};bundle['REPORT.html']=root.encode();bundle['README.txt']='REPORT.html을 여세요. 새 게임은 별도 HTML.zip에 있습니다. 새 원시/CSV/로그/모든 화면/도구/그림과 주요 역사 참조를 포함합니다. 재현은 공통 하네스와 기존 이력이 있는 전체 저장소가 필요합니다. reused검사는 새 실행으로 표기하지 않습니다. GitHub readback 영수증은 산출물 push후 후속 커밋에 있습니다.\n'.encode();bundle['BUNDLE_CHECKSUMS.sha256']=''.join(sha(v)+'  '+n+'\n'for n,v in sorted(bundle.items())).encode()
with zipfile.ZipFile(rz,'w')as z:
 for n,v in sorted(bundle.items()):add(z,n,v)
receipts=[]
for f in[gz,rz]:
 with zipfile.ZipFile(f)as z:
  assert z.testzip()is None
  if f==gz:assert z.read(game.name)==game.read_bytes()
  else:assert all(z.read(n)==v for n,v in bundle.items())
 assert f.stat().st_size<100*1024**2;receipts.append({'file':f.relative_to(R).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f.read_bytes()),'crcAndMemberEquality':True})
(D/'GUN_B2A_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in[game,gz,rz,P/'CHECKSUMS.sha256']));assert not any(n.endswith(game.name)for n in bundle)
(P/'PACKAGE_RECEIPT.json').write_text(json.dumps({'archives':receipts,'gameHtmlSha256':sha(game.read_bytes()),'allNewScreenshotsIncluded':True,'pngCount':sum(p.suffix.lower()=='.png'for p in files),'reportNoGameHtml':True,'readback':'FOLLOWUP_COMMIT'},indent=2)+'\n');print(json.dumps(receipts))
