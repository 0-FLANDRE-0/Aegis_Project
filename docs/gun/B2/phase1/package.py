"""Separate downloadable game and report, deterministic ZIP container metadata."""
from pathlib import Path
import csv,hashlib,html,json,zipfile
P=Path(__file__).resolve().parent;R=P.parents[3];B=P.parent;D=R/'downloads';D.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();game=R/'Aegis_SIM_v48_WIP_GUN_B2.html'
assert json.loads((P/'evidence/effects-summary.json').read_text())['complete']
assert json.loads((P/'evidence/product-invariants.json').read_text())['pass']
assert json.loads((P/'evidence/g7-repeat.json').read_text())['pass']
report=(P/'REPORT.md').read_text();assert 'FINAL_PHASE1_REPORT'in report
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GUN_B2 Phase1 report</title><style>body{font:14px/1.7 system-ui;max-width:1500px;margin:24px auto;padding:0 18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.65 monospace}img{max-width:100%;height:auto}a{margin-right:14px}.note{background:#fff1d6;padding:12px}</style><h1>GUN_B2 Phase 1</h1><p class="note">요청 기능·측정 완료. 새 ON 동작 차이와 근거리 효과는 검토 사항이다. 피해 계수·기대값을 결과에 맞추지 않았다.</p><p><a href="REPORT.md">보고서</a><a href="PARAMETERS.md">수치/모델</a><a href="PROTOCOL.md">시험 규약</a><a href="evidence/regression-failures.csv">원시 실패 목록</a><a href="MEDIA_INDEX.tsv">전체 화면 원본 색인</a></p>'''
for name,title in [('dispersion-anchor','16,459m 산포 앵커'),('single-shot-pk','실제 native 단발 Pk 곡선'),('g7-effects','전체 native 960회')]:page+='<h2>'+title+'</h2><a href="plots/'+name+'.svg"><img src="plots/'+name+'.png" alt="'+title+'"></a>'
page+='<pre>'+html.escape(report)+'</pre><p>원격 readback 영수증은 산출물 push 후 별도 커밋에 추가됩니다. ZIP는 해당 산출물 커밋의 고정본입니다.</p></html>';(P/'INDEX.html').write_text(page)
exclude={'CHECKSUMS.sha256','REMOTE_READBACK.json','BUNDLE_CHECKSUMS.sha256','PACKAGE_RECEIPT.json'}
files=sorted(p for p in P.rglob('*')if p.is_file()and p.name not in exclude and'__pycache__'not in p.parts and p.suffix not in ['.pyc','.tmp'])
media=[p for p in files if p.suffix.lower()=='.png'];selected=set()
for p in media:
 rel=p.relative_to(P).as_posix()
 if rel.startswith('plots/')or rel.startswith('evidence/label-final/')or(rel.startswith('evidence/regression/ON/webgl8/')and'native-observed-launch'in p.name):selected.add(p)
with(P/'MEDIA_INDEX.tsv').open('w',newline='')as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['repositoryPath','bytes','sha256','includedInReportZip','source'])
 for p in media:w.writerow([p.relative_to(R).as_posix(),p.stat().st_size,sha(p.read_bytes()),int(p in selected),'Original screenshot retained in repository; no recompression/edit'])
files=[p for p in files if p.suffix.lower()!='.png'or p in selected];files.append(P/'MEDIA_INDEX.tsv')
extras=[B/n for n in ['INSTRUCTIONS.md','PHASE1_START.md','PHASE0.md','PHASE1_PROPOSAL_DRAFT.md','STATUS.md','BUILD_STATUS.json','approved-gun-baselines.json']]
extras += [R/'docs/gun/B1/TEST_MIGRATIONS.md',R/'docs/radar/air-origin/A/approved-expectations.json']
extras += [p for p in(B/'post-origin').rglob('*')if p.is_file()and p.suffix in ['.jsonl','.json','.csv','.md']and p.name!='REMOTE_READBACK.json']
files=sorted(set(files+extras));assert all(p.stat().st_size<100*1024**2 for p in files)
(P/'CHECKSUMS.sha256').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in [game]+files));files.append(P/'CHECKSUMS.sha256')
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,data,compresslevel=7)
gameZip=D/'Aegis_SIM_v48_WIP_GUN_B2_HTML.zip';reportZip=D/'Aegis_SIM_v48_WIP_GUN_B2_PHASE1_REPORT.zip'
with zipfile.ZipFile(gameZip,'w')as z:
 add(z,game.name,game.read_bytes());add(z,'SHA256SUMS.txt',(sha(game.read_bytes())+'  '+game.name+'\n').encode());add(z,'README.txt','Aegis_SIM_v48_WIP_GUN_B2.html을 압축 해제한 뒤 브라우저로 여세요. 게임용 SIM_TUNED 모델입니다. 전체 검증과 새 ON 차이는 별도 PHASE1_REPORT.zip에 있습니다.\n'.encode())
root=page
for prefix in ['plots/','evidence/']:
 root=root.replace('href="'+prefix,'href="docs/gun/B2/phase1/'+prefix).replace('src="'+prefix,'src="docs/gun/B2/phase1/'+prefix)
for name in ['REPORT.md','PARAMETERS.md','PROTOCOL.md','MEDIA_INDEX.tsv']:root=root.replace('href="'+name+'"','href="docs/gun/B2/phase1/'+name+'"')
bundle={p.relative_to(R).as_posix():p.read_bytes()for p in files};bundle['REPORT.html']=root.encode();bundle['README.txt']='REPORT.html을 여세요. 게임 HTML은 별도 HTML.zip에 있습니다. 현재 단계의 원시 수치·CSV·시험 로그·코드·그림과 대표 화면을 포함합니다. 전체 중복 회귀 PNG는 저장소에 원본 그대로 두고 MEDIA_INDEX.tsv에 경로/해시/포함 여부를 기록했습니다(단일 ZIP 100MB 제한). 모델 재현은 공통 하네스가 있는 전체 저장소가 필요합니다. 원격 readback 영수증은 산출물 업로드 뒤 후속 커밋에 있습니다.\n'.encode();bundle['BUNDLE_CHECKSUMS.sha256']=''.join(sha(data)+'  '+name+'\n'for name,data in sorted(bundle.items())).encode()
with zipfile.ZipFile(reportZip,'w')as z:
 for name,data in sorted(bundle.items()):add(z,name,data)
receipts=[]
for file in [gameZip,reportZip]:
 with zipfile.ZipFile(file)as z:
  assert z.testzip()is None
  if file==gameZip:assert z.read(game.name)==game.read_bytes()
  else:assert all(z.read(n)==v for n,v in bundle.items())
 assert file.stat().st_size<100*1024**2
 receipts.append({'file':file.relative_to(R).as_posix(),'bytes':file.stat().st_size,'sha256':sha(file.read_bytes()),'crcAndMemberEquality':True})
(D/'GUN_B2_PHASE1_SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(R).as_posix()+'\n'for p in [game,gameZip,reportZip,P/'CHECKSUMS.sha256']))
(P/'PACKAGE_RECEIPT.json').write_text(json.dumps({'archives':receipts,'gameHtmlSha256':sha(game.read_bytes()),'pngIncluded':len(selected),'pngOriginalsIndexed':len(media),'remoteReadback':'FOLLOWUP_COMMIT_AFTER_ARTIFACT_PUSH','noGameHtmlInReportZip':all(not n.endswith('Aegis_SIM_v48_WIP_GUN_B2.html')for n in bundle)},indent=2)+'\n');print(json.dumps(receipts))
