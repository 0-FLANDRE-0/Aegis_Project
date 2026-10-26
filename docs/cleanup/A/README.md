# CLEAN_A

기준: `env-d-remeasure-a@837539645b663e8653caa7aac037e6857efe5a2d`.
작업 브랜치: `clean-a`. main 병합·tag·release 없음.

먼저 [REPORT.md](REPORT.md), [ACCEPTANCE.json](ACCEPTANCE.json), [STATUS.json](STATUS.json)을 읽는다.
이 결과는 전체 합격판이 아니다. 도메인은 DDG의 검증된 (a) 기준 3건만 갱신해 417/420이다.
CG 3건은 실제 자원 소모 퇴행으로 유지했다. 게임 비행/교전 코드 조정은 없다.

기존 종료기·공통·RF·WebGL·UI와 120초 상태 비교는 통과했다.
처음 실패했던 인계 수정 3발은 최신에서 모두 회복됐다.

유효구간 최소거리는 120칸 모두 측정했으며, 추가 사격은 1,040발이다.
115칸은 최대구간도 확정됐고 ESSM 5칸은 후속 5km grid가 없다.
사용자의 “최소거리 사격만 추가” 제한 때문에 해당 최대값은 미측정으로 남겼다.
이 5칸을 추측하거나 더 먼 성공 구간으로 대체하지 않았다.

추가 grid 승인이 도착하면 승인 원문과 범위를 `scope-approval.json`에 기록한 뒤 아래를 실행한다.
승인 도착 전 이 파일을 만들거나 플래그를 사용하지 않는다.

```sh
node docs/cleanup/A/intervals.cjs --allow-missing-grid
python docs/cleanup/A/build.py
node docs/cleanup/A/verify_native.cjs
python docs/cleanup/A/verify_delivery.py
```

다음 검증 증거에는 HTML SHA도 기록되므로 재빌드했으면 새 산출물 SHA와 게임 코어 일치를
반드시 확인하고, `report.py`의 부분 완료 상태/190발 상한 설명도 새 실제 결과로 갱신한다.
기존 C2 결과는 표 변경 전 HTML에서 수행한 사실을 보존하고 새 HTML의 게임 코어 동등성을
명시하거나 해당 C2를 다시 실행한다. 측정 완료 전 `effectiveIntervalsComplete`를 강제로 켜지 않는다.

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
