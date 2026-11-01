from pathlib import Path
import json,hashlib,html,statistics,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';sha=lambda b:hashlib.sha256(b).hexdigest()
j=lambda p:json.loads((P/p).read_text())
s=j('evidence/summary.json');render=j('evidence/render.json');scope=j('evidence/scope.json');build=j('build.json');reg=j('evidence/regression/execution.json')
if not any(r['suite']=='native-origin-control'for r in reg['rows']):reg['rows'].append(j('evidence/regression/native-origin-control-execution.json'))
assert {'native','geometry','physical_adapter','map','ui','map-ui213','webgl8','native-origin-control'}<={r['suite']for r in reg['rows']},'REGRESSION_STILL_RUNNING'
webgl=j('evidence/regression/webgl8/observed-world.json');assert webgl['pass']and len(webgl['records'])==8
assert s['g7']['n']==60 and s['attempts']==720 and all(r['exactOutsideInstallationOrigin']for r in s['performance'])
lines=['# CG_TURRET_A','',f'기준 main: `{build["baselineMainCommit"]}` (PR #61 병합본). 기준 B2B SHA-256 `{build["baselineSha256"]}` 일치. 브랜치 `cg-turret-a`.','', '## 변경과 범위','', 'CG 전·후방의 숨겨진 원래 3D Warehouse 둥근 포탑을 복구하고, 덧씌운 buildMk45 메시 생성 호출을 제거했다. 원래 mk45f_yaw/mk45f_pitch 및 mk45a_yaw/mk45a_pitch를 MAP_E와 같은 축·정지 고각 보정으로 연결한다. buildMk45 함수 자체와 DDG 모델은 그대로다.','', '표현 메시의 54구경 외형과 설치 성능의 Mod 4(62구경)가 다르다. 이는 사용자 지정 범위에 따른 의도된 표현이다. 화면의 `Mk 45 Mod 4` 표기는 장비 프로파일 성능을 뜻하며, 이번에 UI 문구를 추가하거나 바꾸지 않았다. 기존 원본 출처 표기를 보존했다.','', '| 마운트 | trunnion x/y/z (m) | 노출 포신 (m) |','|---|---|---|']
for q in render['records']['current']['specs']:
 m=q['spec']['mount'];o=m['trunnionOffsetM'];lines.append(f'|{q["id"]}|{o["x"]} / {o["y"]} / {o["z"]}|{m["exposedBarrelM"]}|')
lines += ['', '이전 두 마운트 값은 `(0.91, 0, 2.87)` / `6.206 m`였다. 복구 값은 내장 BUNKER_REGISTRATION.guns의 trunnionOffsetM/barrelM을 직접 사용한다. 수직 기준은 기존 함 로컬 +Z 위, 원본 CG 등록과 같은 기준이며 수선·함체 기준은 바꾸지 않았다.','',f'CG 모듈 성능은 B2B와 동일하다: `MK45_MOD4_CG52_MK160_V1`, 823 m/s, 사통 0.8–24 km, 600발×2, MFF/HE/SAP. [정적 감사](evidence/scope.json)와 [실제 런타임 spec](evidence/render.json)을 함께 보존한다.','', '## T1–T6','', '| 항목 | 결과 |','|---|---|', '| T1 외형 | 원본 MAP_E 포탑 메시 지문 일치; PC 1400×900 / 폰 832×384 전·후방 비교 캡처 |',f'| T2 포구 | 실제 native spawn과 메시 포구 중심 18자세, 최대 {s["maxMuzzleErrorM"]:.9f} m ≤ 0.1 m |','| T3 사계 | 원래 CG 등록 삼각형/BVH와 기존 클리어런스 함수 그대로. 아래 차이 표 |','| T4 성능 | 성능 레지스트리 및 런타임 spec의 원점 외 항목 동일 |',f'| T5 회귀 | CG 단발 {s["attempts"]}시도 / {s["actualReleases"]}발; 수상45발; G7 {s["g7"]["n"]}회. 아래 분리·회귀 결과 |','| T6 렌더 | DDG PC/폰 전체 캡처 차이 0 pixel; WebGL 자연8발 결과 아래 |','', '포구 측정은 실제 렌더 메시의 마지막 평면 정점 중심을 사용한다. 최대 축상 정점에서 2mm 이내의 중복 제거 정점을 평균했다. 게임 native spawn 원점을 같은 함 로컬 좌표계로 역변환해 비교했다. 선회는 각 마운트의 중립 방위 기준 -90/0/+90°, 고각0/30/60°다. 런타임/렌더 상태에는 진단용 입력을 주었고 제품 로직은 바꾸지 않았다.','', '기존 renderer.contractAudit()의 sourcePreserved=false는 B2B와 동일하게 남는다. retainedTriangles=749201, sourceTriangles=740819, declaredSourceTriangles=767571로 전후 세 값이 같다. profile/guns/CIWS/SPG/VLS/nav/readOnly 검사는 통과한다. 기존 집계 실패를 PASS로 바꾸거나 제품 감사 함수를 수정하지 않았다.','', '## 사계와 단발 Pk','', '| 마운트 | 5° 격자 표본 | 이전 clear | 현재 clear | 상태/가림물 변경 |','|---|---:|---:|---:|---:|']
for c in s['clearance']:lines.append(f'|{c["mount"]}|{c["samples"]}|{c["oldClear"]}|{c["newClear"]}|{c["changed"]}|')
lines += ['', '원점이 낮아져 정면 고도10m 표적에서 계획 요격거리2–4km가 새로 HULL:0에 가린다. 별도 사각 보정이나 클리어런스 완화를 하지 않았다. 단발 조건은 B2B와 같은 Kh-35U/10m/280m/s, 이상 지속 관측, 계획 요격거리1–9km×방위0/90°×40공통시드592001–592040이다. 미발사를 격추 실패로 집계하지 않고 분리했다. 내장 GUN_B2_RANGE_TABLE은 지시된 변경 범위 밖이라 B2B 값 그대로이며, 현재 CG 원점의 새 측정표로 오인하지 않도록 이 보고서에 명시한다. 발사 관문/링 값은 갱신하지 않았다.','', '| 방위 | km | 이전/현재 발사 | 이전 Pk 평균 | 현재 Pk 평균 | 이전/현재 KILL·STRUCT_FAIL |','|---|---:|---:|---:|---:|---:|']
pklabel=lambda v:f'{v:.6f}'if v is not None else '미발사'
for p in s['pk']:lines.append(f'|{p["bearing"]}|{p["rangeKm"]}|{p["oldReleases"]}/{p["newReleases"]}|{pklabel(p["oldMeanPk"])}|{pklabel(p["newMeanPk"])}|{p["oldKills"]}/{p["newKills"]}|')
lines += ['', '## 수상 첫발','', '| 거리 | B2B | 현재 |','|---|---:|---:|']
for r in s['surface']:lines.append(f'|{r["rangeKm"]}km|{r["oldHits"]}/15|{r["newHits"]}/15|')
lines += ['', '시드723001–723015, 자함20kt, 기존 실제 moving-world fixture. firstRoundHit와 fixture 종합 pass를 혼동하지 않는다. 5/10km에서는 기존 meaningfulMovingFrame 조건이 false여서 종합 pass=0/15이고, 15km는6/15이다. 전후 동일하며 기존 검사·허용치를 바꾸지 않았다.','', '## 자연 탐지 G7와 원점 분리','', 'CG만 방위0/90° × 표적1/4기 ×15시드419010–419024, 60회. 매번 새 페이지에서 자연 RF와 전체 fixed tick을 실행했다. DDG G7 및 CG 함포 비개입 항목은 source guard로 이전 결과를 재사용하며 새 실행이라고 표시하지 않는다.','',f'B2B 대비 HP 악화 {s["g7"]["hpWorse"]}, 개선 {s["g7"]["hpBetter"]}, 동일 {s["g7"]["hpSame"]}. 원시 결과에는 각 시드의 발사수·CIWS탄·HP·표적별 결과를 모두 남겼다.','', '| 방위 | 표적 수 | 이전 평균 HP | 현재 평균 HP | 이전/현재 평균 함포 발사 |','|---|---:|---:|---:|---:|']
for b in[0,90]:
 for n in[1,4]:
  rr=[r for r in s['g7']['rows']if(r['bearing'],r['count'])==(b,n)];m=lambda k:statistics.mean(r[k]for r in rr);lines.append(f'|{b}|{n}|{m("oldHp"):.6f}|{m("newHp"):.6f}|{m("oldShots"):.3f}/{m("newShots"):.3f}|')
iso=s['originIsolation'];lines += ['',f'원점만 B1 값으로 되돌린 진단 빌드와 B2B를 Pk18조건·수상9조건·G7 4조건에서 대조했다. host 실행시간 필드만 제외하고 **{sum(r["exact"]for r in iso["pairs"])}/{len(iso["pairs"])} 완전 일치**. CG 프로파일 생성부는 원점을 역복구하면 B2B와 byte 동일하고, 나머지 시뮬 함수도 전부 byte 동일하다. 따라서 새 CG 함포 차이는 원점 변경으로 제한된다. 진단의 수정 계수·검사 완화는0이며, 이 차이 기록의 승인은 지시서 §3의 사전 승인에 근거한다. 다른 기대값 파일은 변경하지 않았다.','', '## 기존 회귀와 보존','', '| suite | exit | 시간(s) |','|---|---:|---:|']
for r in reg['rows']:lines.append(f'|{r["suite"]}|{r["exit"]}|{r["elapsedS"]:.2f}|')
priorWebgl=json.loads((R/'docs/gun/B2/phase1/evidence/regression/ON/webgl8/observed-world.json').read_text());beforeWebgl={(r['weapon'],r['enabled']):r for r in priorWebgl['records']};lines += ['', 'WebGL8은 자연 탐지·LOCK·정식 VLS·전체 tick·실제 렌더가 작동하는8회 회귀이며,8발 전부 격추했다는 뜻은 아니다. 과거 B2B가 재사용하던 동일 관측 회귀와 결과를 아래에 비교한다.','', '| 미사일 | 종료기 | 이전 종료/표적 생존 | 현재 종료/표적 생존 |','|---|---|---|---|']
for r in webgl['records']:
 o=beforeWebgl[r['weapon'],r['enabled']];a=o['final'];b=r['final'];lines.append(f'|{r["weapon"]}|{r["enabled"]}|{a["missile"]["reason"]} / {a["targetAlive"]}|{b["missile"]["reason"]} / {b["targetAlive"]}|')
 assert a['targetAlive']==b['targetAlive']and a['missile']['reason']==b['missile']['reason']
native=j('evidence/native-approved.json')
from zoneinfo import ZoneInfo
runpath=E/'range-execution.json';teststart=datetime.datetime.fromtimestamp(runpath.stat().st_mtime,datetime.timezone.utc)-datetime.timedelta(seconds=json.loads(runpath.read_text())['elapsedS']);testend=datetime.datetime.now(datetime.timezone.utc);wall=(testend-teststart).total_seconds();assert wall<=3600
lines += ['',f'검수 벽시계: {teststart.astimezone(ZoneInfo("Asia/Seoul")).isoformat()} ~ {testend.astimezone(ZoneInfo("Asia/Seoul")).isoformat()}, {wall/60:.2f}분 / 60분 상한. G7 단독 lane {j("evidence/g7-execution.json")["elapsedS"]:.2f}s, CG720+수상45 lane {j("evidence/range-execution.json")["elapsedS"]:.2f}s. 겹친 실행시간을 합산하지 않았다.']
lines += ['', '최종 패키징에서 loader manifest의 encodedBytes 한 값을 실제 base64 길이에 맞췄다. 이전 측정 HTML과 최종 HTML의 압축된 main payload 자체가 byte 동일함을 PACKAGING_FINALIZATION.json에서 증명한다. 측정된 코드·입력은 그대로이고, 최종 HTML의 자연 WebGL8 시험도 별도로 완료했다.']
lines += ['',f'Native 원시 결과는 {native["rawPassed"]}/41이다. `CG.G2.10.280` 한 건이 기존의 탄도 시험 명중 대신 전방 HULL:0 가림·후방 사계 밖으로 바뀌었다. 원점만 역복구한 동일 진단은41/41이다. 사용자 §3의 원점 차이 사전 승인에 따라 이 한 기대값만 새 문서에서 이관해 {native["approvedPassed"]}/41로 기록했다. 0.35m 허용치와 다른40개 기대값은 그대로다. [이전/현재/원인 기록](evidence/native-approved.json). 원본 실패 로그와 exit=1은 보존한다.','', 'UI76의 옛 “faceted 생성 메시 / 원본 숨김” 두 단언만 요청된 “원본 표시 / 생성 메시 없음”으로 바꾼 private 진단을 사용했다. 포구≤0.1m는 별도18자세 시험에서 검증했다. 나머지74개 단언과 원본 시험 파일은 그대로다. [단언 이관](evidence/regression/ship/cg-turret/A/evidence/ui-assertion-migration.json).','', '진단 개발 중 MAP_E에 B1 이후 API를 호출한1회와, snapshot의 존재하지 않는 id를 사용해 자세를 바꾸지 못한1회를 수정했다. 후자는 9.35m라는 잘못된 초기 진단값을 냈다. hardpointId로 렌더 snapshot을 지정한18자세 재시험에서0.000656m로 확인했다. 게임 제품이나 계수를 변경해 해결한 것이 아니다.','',f'보호 함수281/281, DDG renderer builder, 전체 SAM/RF/EKF/신관/파편/저장/ENV_D 코드와 표는 B2B byte 동일. 기존 WIP148_EXTERNAL_3D/buildMk45 전체도 동일하다. 새 심벌0, 기존 변경 심벌은 {scope["changed"]}.','', '## 남은 사항','', '- CG 정면 저고도 클리어런스가 줄어드는 것은 원래 포구 높이 복구의 결과다. 사용자 지정 범위대로 유지했다.','- CG 표시용 내장 사거리표는 B2B 역사 데이터이며, 갱신은 별도 작업이다.','- 원래 둥근 메시/Mod4 성능 차이와 기존 sourcePreserved 집계 실패를 기록했다.','- CIWS/피해 RNG, B3 극각 모델, 새 포탑 제작, NPC 함포 개선은 수행하지 않았다.','- 실제 기기 성능 측정은 아니며, 폰 크기는 헤드리스832×384 캡처다.','',f'제품 SHA-256: `{build["htmlSha256"]}`. main 병합·release/tag 생성 없음.','']
(P/'REPORT.md').write_text('\n'.join(lines));
fig,axes=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
for ax,b in zip(axes,[0,90]):
 rr=[r for r in s['pk']if r['bearing']==b];ax.plot([r['rangeKm']for r in rr],[r['oldMeanPk']for r in rr],label='B2B');ax.plot([r['rangeKm']for r in rr],[r['newMeanPk']for r in rr],label='CG_TURRET_A');ax.set(title=f'CG bearing {b} deg',xlabel='Planned intercept range (km)',ylabel='Mean native Pk per released shot',ylim=(0,1));ax.grid(alpha=.3);ax.legend()
for ext in['png','svg']:
 f=E/('pk-comparison.'+ext);fig.savefig(f,dpi=150)
 if ext=='svg':f.write_text('\n'.join(l.rstrip()for l in f.read_text().splitlines())+'\n')
plt.close(fig)
page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CG_TURRET_A</title><style>body{font:14px/1.6 system-ui;max-width:1500px;margin:auto;padding:16px}img{width:100%}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style><h1>CG_TURRET_A 비교</h1><p>왼쪽 MAP_E 원본 / 가운데 B2B / 오른쪽 현재. 동일 마운트·카메라·크기.</p>'
for w in[1400,832]:
 for key in['mk45','mk45Aft']:
  page+=f'<h2>{w}px / {key}</h2><div class="grid">'
  for n in['MAP_E','B2B','current']:page+=f'<figure><figcaption>{n}</figcaption><img src="evidence/screenshots/{n}-{w}-{key}.png"></figure>'
  page+='</div>'
page+='<h2>DDG 전후</h2><div class="grid">'
for n in['DDG-before','DDG-after']:page+=f'<figure><figcaption>{n}</figcaption><img src="evidence/screenshots/{n}-1400-mk45.png"></figure>'
page+='</div><h2>실측 Pk</h2><img src="evidence/pk-comparison.png"><pre>'+html.escape((P/'REPORT.md').read_text())+'</pre></html>';(P/'INDEX.html').write_text(page)
status={'implemented':True,'baselineMainCommit':build['baselineMainCommit'],'htmlSha256':build['htmlSha256'],'scopePass':scope['pass'],'renderPass':render['pass'],'originIsolationPass':iso['allExact'],'rawRegressionExitFailures':[r for r in reg['rows']if r['exit']],'regressionExitFailures':[r for r in reg['rows']if r['exit']and not(r['suite']=='native'and native['pass'])],'nativeRawPassed':native['rawPassed'],'nativeApprovedPassed':native['approvedPassed'],'pkAttempts':s['attempts'],'pkReleases':s['actualReleases'],'g7Fresh':s['g7']['n'],'surfaceFresh':45,'knownLegacyAuditFailure':'sourcePreserved; exact same counts in B2B','mainMerged':False,'releaseOrTag':False,'completedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(P/'BUILD_STATUS.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status))
