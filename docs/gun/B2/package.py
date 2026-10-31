"""Package completed Phase 0 evidence only; never include a modified game HTML."""
from pathlib import Path
import datetime,hashlib,html,json,zipfile

B=Path(__file__).resolve().parent;R=B.parents[2];D=R/'downloads';E=B/'evidence'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=load(E/'acceptance.json');s=load(E/'summary.json');f=load(E/'local-finalization.json')
assert a['pass'] and s['complete'] and s['cases']==2400 and f['complete']
assert (B/'PHASE0.md').exists() and not(R/'Aegis_SIM_v48_WIP_GUN_B2.html').exists()
product=R/'Aegis_SIM_v48_WIP_GUN_B1.html'
assert sha(product)==a['productHtmlSha256']=='c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc'
status={'schema':'AEGIS_GUN_B2_PHASE0_STATUS_1','phase':'PHASE0_ONLY_AWAIT_USER_APPROVAL',
 'baselineCommit':'9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c','productHtmlSha256':sha(product),
 'gameCodeChanged':False,'phase1Implemented':False,'newGameHtmlProduced':False,
 'cases':s['cases'],'rawMatrixExecutions':2880,'conditions':len(s['perCondition']),'seedsPerCondition':30,'shells':s['shots'],
 'acceptancePass':a['pass'],'domain':{'pass':420,'reused':378,'fresh':42},
 'decisionRequired':'Allow separate own-air-plot receiver-origin contract repair before Phase 1; conflicts with sensor preservation scope.',
 'localFinalizationUtc':f['utc'],'mainMerge':False,'releaseOrTagCreated':False}
(B/'BUILD_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
(B/'STATUS.md').write_text(f'''# GUN_B2 상태

**Phase 0 완료 · 사용자 승인 대기**

정식 시험 {s['cases']:,}회 / 80조건 ×30시드 / {s['shots']:,}발.
제품 GUN_B1 SHA-256 `{sha(product)}` 유지. 게임 코드/계수 변경 0.
새 B2 게임 HTML은 없으며 Phase 1은 미구현이다.

우선 결정: 센서 변경 금지 범위와 충돌하는 공중 plot receiver 원점 계약 복구를
별도 선행 수정으로 허용할지. 고정 오프셋이나 truth 사격 보정은 제안하지 않는다.

[최종 보고](PHASE0.md) · [검수](evidence/acceptance.json) · [원점 원인](ORIGIN_CONTRACT_FINDING.md)
· [미적용 설계 초안](PHASE1_PROPOSAL_DRAFT.md) · [원격 영수증](https://github.com/0-FLANDRE-0/Aegis_Project/blob/gun-b2/docs/gun/B2/REMOTE_READBACK.json).

지시서 §2/§12: **“push 후 멈추고 사용자 승인을 기다린다.”**
main 병합, release/tag, CI 변경 없음. 승인 전 구현을 진행하지 않는다.
''')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEGIS GUN_B2 Phase 0</title><style>body{font:14px/1.65 system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1500px;background:#101d26;color:#e3edf2}a{color:#8ed7ed}pre{font:12px/1.65 monospace;white-space:pre-wrap;overflow-wrap:anywhere}.note{padding:12px;background:#4b3825}figure{margin:18px 0}img{max-width:100%;height:auto;background:white}</style><h1>GUN_B2 — Phase 0</h1><p class="note">진단 완료 · 제품 코드 변경 없음 · Phase 1 사용자 승인 대기. 게임 HTML은 리포트에 포함하지 않습니다.</p>'''
for name,label in [('PHASE0.md','전체 보고서'),('STATUS.md','상태'),('PROTOCOL.md','시험 규약'),('ORIGIN_CONTRACT_FINDING.md','원점 계약 원인'),('PHASE1_PROPOSAL_DRAFT.md','미적용 설계 초안'),('evidence/acceptance.json','검수'),('evidence/summary.json','전체 통계')]:
 page+=f'<a href="{name}">{label}</a> · '
for name in ['arrival-and-outcomes','cpa-projections','et-distance']:
 page+=f'<figure><figcaption>{name}</figcaption><a href="plots/{name}.svg"><img src="plots/{name}.png" alt="{name}"></a></figure>'
page+='<h2>최종 보고</h2><pre>'+html.escape((B/'PHASE0.md').read_text())+'</pre></html>'
(B/'INDEX.html').write_text(page)
def included(p):
 return p.is_file() and '__pycache__' not in p.parts and p.name not in ['REMOTE_READBACK.json','CHECKSUMS.sha256'] and p.suffix not in ['.pyc','.tmp']
items=sorted(p for p in B.rglob('*') if included(p))
assert all(p.stat().st_size<100*1024**2 for p in items)
(B/'CHECKSUMS.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in [product]+items))
items=sorted(items+[B/'CHECKSUMS.sha256']);D.mkdir(exist_ok=True)
archive=D/'Aegis_SIM_v48_WIP_GUN_B2_PHASE0_REPORT.zip'
def add(z,name,data):
 i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16
 z.writestr(i,data,compresslevel=6)
with zipfile.ZipFile(archive,'w') as z:
 add(z,'README.txt','REPORT.html을 여세요. 정식 원시 로그는 docs/gun/B2/evidence/trials/입니다. development/pilot 자료는 비교에서 제외한 개발 기록입니다. 제품 HTML은 변경하지 않았고 이 ZIP에 포함하지 않습니다. 원격 검증 영수증은 ZIP 생성 뒤 별도 커밋에 기록합니다.\n'.encode())
 root=page
 for name in ['PHASE0.md','STATUS.md','PROTOCOL.md','ORIGIN_CONTRACT_FINDING.md','PHASE1_PROPOSAL_DRAFT.md','evidence/acceptance.json','evidence/summary.json']:
  root=root.replace('href="'+name+'"','href="docs/gun/B2/'+name+'"')
 root=root.replace('href="plots/','href="docs/gun/B2/plots/').replace('src="plots/','src="docs/gun/B2/plots/')
 add(z,'REPORT.html',root.encode())
 for p in items:add(z,p.relative_to(R).as_posix(),p.read_bytes())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert not any(n.startswith('Aegis_SIM_') or n.endswith('_GUN_B2.html') for n in z.namelist())
 assert all(z.read(p.relative_to(R).as_posix())==p.read_bytes() for p in items)
assert archive.stat().st_size<100*1024**2
checksums=D/'GUN_B2_PHASE0_SHA256SUMS.txt'
checksums.write_text(''.join(sha(p)+'  '+p.relative_to(R).as_posix()+'\n' for p in [product,archive,B/'CHECKSUMS.sha256']))
print(json.dumps({'archive':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(items)+2,'crcPass':True},ensure_ascii=False))
