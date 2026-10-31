"""Render the approval supplement; preserve original report and measurements."""
from pathlib import Path
import json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence/approval';load=lambda p:json.loads(p.read_text());q=load(E/'summary.json');a=load(B/'approved-expectations.json');build=load(B/'build.json');assert q['pass']and q['approvedExpectationCount']==5
lines=['# AIR_ORIGIN_A — 사용자 승인 기대값 5건 반영','',
'2026-11-01(KST) 사용자 명시 승인에 따라 기대값 5건만 갱신했다. **게임 HTML 변경 0 · 다른 기대값 변경 0 · 허용 오차 변경 0 · 병합 0.**',
'','승인 기록: [approved-expectations.json](approved-expectations.json). 네 습격 검사에는 이전·새 기대값 전체와 값 해시를, world120에는 이전·새 truth hash를 기록했다. 각 항목에 원인 경로와 검토 자료 경로/해시를 남겼다. [승인 전 보고서](REPORT.md)와 모든 기존 raw 결과는 그대로 보존했다.',
'','| 승인 항목 | 이전 기대값 SHA-256 앞 16자리 | 새 기대값 SHA-256 앞 16자리 | 원인 경로 |','|---|---|---|---|']
for r in a['entries']:
 cause='receiver/EKF → AUTO 발사 틱 → 708kg 탄약 질량 제거 시점 → 함 자세/관측 상태'if r['kind']=='paired42'else'56틱 관측 → 4032틱 시커 방사 → 4034틱 표적 회피/RNG'
 lines.append(f"| `{r['id']}` | `{r['oldValueSha256'][:16]}` | `{r['newValueSha256'][:16]}` | {cause} |")
w=next(r for r in a['entries']if r['kind']=='world120');lines+=['','전투 world120 truth hash:','',f"- 이전: `{w['oldExpected']}`",f"- 새 값: `{w['newExpected']}`",'',
'표의 값 해시는 키를 정렬한 UTF-8 JSON(`ensure_ascii=False`, 공백 없는 구분자)에 대한 SHA-256이다. world120 항목의 값 해시는 truth hash 문자열의 JSON 해시이며, 실제 truth hash는 위 두 줄이다. [TSV](evidence/approval/expectation-changes.tsv)에는 전체 값 해시·원인 경로가 있다.',
'','## 검증 결과','',
'| 검사 | 결과 | 출처 |','|---|---|---|',
'| DDG/CG idle·raid·damaged 쌍대 | **42/42** | 모든 6시나리오 main/후보를 새로 실행 |',
'| 승인된 습격 기대값 | **4/4** | 원래 strict 비교 4건 불일치는 로그에 보존하고 새 값과 정확 비교 |',
'| world120 idle / combat | **2/2** | 각 7200틱 새로 실행; idle 기대값 그대로 |',
'| 승인 범위·해시·향후 변화 보호 | **23/23** | 다른 HTML/코어·누락/추가 승인 거부, 미승인 실패 보존, 미래 상태 차이 계속 실패 |',
'| 도메인 합계 | **420/420** | **42건 재실행 + 변경 없는 14 suite의 378건 기존 결과 재사용** |',
'| 새 실행과 검토 당시 물리·관측·RNG | **동일** | 12개 baseline/candidate 상태 비교 및 world120 hash 확인 |',
'| 다른 기대값 / 허용 오차 | **변경 0 / 0** | 공유 verifier의 승인 연결부 외 나머지 byte 동일 |',
'| 게임 HTML | **byte 동일** | 검토한 HTML SHA-256과 동일 |','',
f"영향받은 검사 재실행 경과시간은 {q['freshElapsedS']:.3f}초다(두 프로세스 병렬 실행). 이번에는 378건을 다시 실행했다고 주장하지 않는다. 동일 HTML과 변경 없는 suite·검사·fixture·의존 파일의 기존 통과 결과를 재사용했다. 자연 발사 8발·시커 RF28·CIWS/EW/H3·무잡음 왕복의 앞선 검증 결과도 동일 게임에 대한 기존 증거로 보존했다.",
'','새 측정값은 검토 자료와 그대로다. 바뀐 것은 승인된 기대값이다. 4개 습격 원래 strict 비교 결과는 `observations.airOriginApproval.originalChecks`에 남고, 다른 38개 쌍대 검사 및 idle/damaged 기대값은 갱신하지 않았다. `raidInventoryDeltaBounded`, `sameCombatRng` 등의 판정은 그대로다.',
'','## 적용 방법과 보호','',
'- 공유 verifier에는 명시적인 `--approved-air-origin-baselines` 선택 인자만 추가했다. 인자가 없을 때 기존 기대값 경로를 유지한다.',
'- 승인 파일은 정확한 HTML과 main JS SHA-256을 모두 검사한다. 다른 빌드에 승인 값을 자동 적용하지 않는다.',
'- 승인 목록은 DDG/CG raid의 `samePhysicalState`, `sameExistingObserverState` 4개와 `world120:combat:truthSha256` 1개로 제한한다.',
'- 비교는 이전과 동일한 정확 비교다. 오차 범위 확대·검사 제외·무조건 통과 처리·게임 상태 쓰기는 없다.',
'- AIR 전체 회귀 runner는 승인 파일을 후보에만 전달하고, 새 실행 결과를 `evidence/approval/full-regression/`에 써서 승인 전 raw 자료를 덮지 않는다.',
'',f"게임: `{build['output']}`",f"SHA-256: `{build['sha256']}`",f"main JS SHA-256: `{build['mainSha256']}`",'',
'[보호 검사](evidence/approval/guard-checks.json) · [현재 결과](evidence/approval/summary.json) · [새 쌍대 raw](evidence/approval/fresh/paired42/baseline-comparison.json) · [새 world120 raw](evidence/approval/fresh/map/E/evidence/delivery-world120.json) · [승인 연결 diff](APPROVAL_EXPECTATION_HOOKS.diff)',
'','## 중단 지점','',
'`air-origin-a`에 커밋·push하고 원격 readback을 확인한 뒤 멈춘다. PR #60의 병합은 사용자가 한다. main 병합·release/tag 생성·gun-b2 rebase는 하지 않는다. 사용자 병합 후 gun-b2를 새 main으로 rebase하고 DDG/CG 표적 1기 0°/90° ×각15회(총60회)를 재진단한 뒤 Phase 1 착수 보고를 한다.']
(B/'APPROVAL_REPORT.md').write_text('\n'.join(lines)+'\n')
p=B/'STATUS.json';old=load(p);previous=old.get('beforeApproval',old)
current={'phase':'AIR_ORIGIN_A_USER_APPROVAL_COMMIT_PUSH_READBACK','contractPass':True,'allCurrentApprovedExpectationChecksPass':True,'domainPassed':420,'domainTotal':420,'domainFresh':42,'domainCachedUnchanged':378,'world120FreshPassed':2,'approvalGuardsPassed':23,'approvedExpectationCount':5,'expectedValuesUpdated':True,'expectedValuesUpdatedWithUserApproval':True,'otherExpectationsChanged':0,'tolerancesChanged':0,'gameHtmlChanged':False,'newHtml':build['output'],'sha256':build['sha256'],'approvalRecord':'docs/radar/air-origin/A/approved-expectations.json','currentReport':'docs/radar/air-origin/A/APPROVAL_REPORT.md','preApprovalReport':'docs/radar/air-origin/A/REPORT.md','mainMerged':False,'gunB2Rebased':False,'gunB2Phase1Started':False,'beforeApproval':previous}
p.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
paths=['docs/helicopter/F/verify_regression.py','docs/map/E/verify_delivery_world.py','docs/radar/air-origin/A/run_regressions.py'];patch=subprocess.check_output(['git','diff','--unified=0','891fa17a836313fdb134e26dbb6cb711fbbe44da','--']+paths,cwd=R,text=True);(B/'APPROVAL_EXPECTATION_HOOKS.diff').write_text(patch)
print('APPROVAL_REPORT.md / STATUS.json / APPROVAL_EXPECTATION_HOOKS.diff written')
