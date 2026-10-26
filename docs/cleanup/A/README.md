# CLEAN_A

기준: `env-d-remeasure-a@837539645b663e8653caa7aac037e6857efe5a2d`.
작업 브랜치: `clean-a`. main 병합·tag·release 없음.

먼저 [REPORT.md](REPORT.md), [ACCEPTANCE.json](ACCEPTANCE.json), [STATUS.json](STATUS.json)을 읽는다.
이 결과는 전체 합격판이 아니다. 도메인은 DDG의 검증된 (a) 기준 3건만 갱신해 417/420이다.
CG 3건은 실제 자원 소모 퇴행으로 유지했다. 게임 비행/교전 코드 조정은 없다.

기존 종료기·공통·RF·WebGL·UI와 120초 상태 비교는 통과했다.
처음 실패했던 인계 수정 3발은 최신에서 모두 회복됐다.

유효구간 120칸 모두 측정 완료했다. 최초 최소거리 사격 1,040발에 더해,
사용자가 “ㅇㅇ 추가 시험 해봐.”로 승인한 ESSM 5칸의 부족 grid 38점×5발=190발을 추가했다.
이번에 확정한 구간은 7~115 / 14~65 / 19~60 / 10~35 / 24~50km다.
승인 원문과 범위는 `scope-approval.json`, 기존 사격과 다른 115칸의 보존 증거는
`evidence/grid-followup.json`에 있다. 첫 실패 뒤 새 사격은 하지 않았다.

아래는 기존 cache를 포함한 후속 작업 재현 명령이다.

```sh
node docs/cleanup/A/intervals.cjs --allow-missing-grid
python docs/cleanup/A/verify_grid_followup.py
python docs/cleanup/A/build.py
node docs/cleanup/A/verify_native.cjs
python docs/cleanup/A/verify_regression_carryforward.py
python docs/cleanup/A/verify_delivery.py
```

`status()`는 match=true, effectiveIntervalsComplete=true, pendingEffectiveCells=0을 반환한다.
HTML SHA는 표가 바뀌어 이전과 다르다. 게임 실행 코드는 byte 동일하다.
기존 300/180/28/8 비행 및 도메인 결과는 원래 실행 HTML SHA와 함께 보존하고,
`evidence/regression-carryforward.json`으로 이번 파일과의 코드 동등성을 확인했다.
이번에 UI88, DDG/CG status/API 독립성, 무표적·전투 120초 해시는 새로 실행했다.
재현 cache를 그대로 사용한 재실행의 freshCalls는 0이므로, 최초 추가 190발의 원시 증거와
`evidence/interval-followup-before.json`을 덮어써서 초기 측정 사실을 바꾸지 않는다.

자료:

- `evidence/part1.json`: 6건 이력, (a)/(b), 판정 guard, 개별 결과와 계측 독립성.
- `approved-raid-baselines.json`: DDG에 한정한 이전/새 exact 값 및 코어 해시 보호.
- `LAUNCH_CAUSAL_CHANGE.diff`: 과거 DZT→HANDOFF 원인 함수 비교. 새 제품 패치가 아님.
- `TEST_BASELINE_UPDATE.diff`: 회귀 도구의 선택적 exact 기준 적용 변경.
- `results/part2-*.json.gz`, `PART2_SHOTS.csv`: 원래 3발의 모든 단계 재실행.
- `results/interval-cells/*.json.gz`: 기존 사격 재사용 목록과 새 최소거리 5발 결과.
- `ENVELOPE_TABLE_D.json`: 새 스키마, 각 `previous`에 이전 값 원문 보존.
- `EFFECTIVE_INTERVALS.csv`: 120칸 구간/요격 지점/끊김점 결과.
- `evidence/c2`, `evidence/world120`: 두 산출물 직접 실행 비교.
- `evidence/native-equivalence.json`, `evidence/delivery.json`: 실제 native 코드 및 포장 동등성.

재현은 저장소 루트에서 실행한다. 브라우저 검수에는 기존 Python Playwright/Chromium 도구,
Node AST 도구에는 acorn이 필요하다. 원래 D2 엔진과 결과는 저장소 `docs/envelope/D2`를 사용한다.
보고 ZIP은 이 폴더와 수정한 회귀 도구를 저장소 상대경로로 포함한다. HTML은 별도 ZIP이다.
