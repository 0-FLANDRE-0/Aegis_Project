# Phase 0 진단 규약

기준은 main `9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c`, 제품은 GUN_B1
`c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc`다.
제품 HTML과 게임 계수는 수정하지 않는다. 변경된 사격통제를 출하하지 않는다.

## 시험 행렬

DDG/CG × 방위 0/90° × 침투 ASM 수 1/2/3/4 × 30개 공통 시드
419010…419039 × BASE/A/B/C/D = 2,400회. 표적 종류·초기 위치·속도·고도,
50초 상한과 표적 전부 종료 시 중단 조건은 B1 G7 `scenario()` 그대로다.
AutoAA는 ON, 기존 CIWS도 그대로다. 표적 센서는 자연 관측 경로다.
고정 시드와 조건은 모두 사전에 고정하며 명중률 목표에 맞춰 조정하지 않는다.

| 조건 | 진단 입력 변경 |
|---|---|
| BASE | 없음 |
| A | 매 틱 기존 정지/수동 항해 명령 + native haltHorizontalContact로 private 횡속도 제거. 속력 0, 함 자세에 따른 trunnion 운동은 유지 |
| B | 실제 own-ship requestFire 안에서 현재 관측·현재 원점으로 기존 continuation solver 호출, 기존 포인팅 재검사. 불일치하면 발사 대기 |
| C | 초기 속도 벡터의 직선 비행. 기존 updateAsmFlightPhysics의 운동 갱신만 진단 래퍼로 대체. 센서·피해·충돌·퇴역 경로는 그대로 실행 |
| D | 공중 사격만 normalizedMiss ≤0.001 추가 검사. 원래 margin의 0.25 하한 때문에 별도 진단 검사 필요. 발사 허용을 완화하지 않음 |

B/D와 운동 통제는 다운로드용 HTML에 들어가지 않는다. 모든 플래그는 기본 OFF다.
B는 실제 클로저를 계측한다. NPC 쪽 동명 함수를 잘못 건드리지 않도록
own-ship의 `solveAirTrack` 클로저를 기준으로 삽입 위치를 검증한다.

## 실행 격리

각 회차는 새 브라우저 게임 페이지/JS 문맥에서 시작한다. 같은 페이지에서
작전 세이브만 불러오는 방식은 사용하지 않는다. 기존 importer는
`maneuver.enabled=false`일 때 telegraph/shaftRpm/propPitch 등 모든 일시 상태를
복원하지 않기 때문이다. 이는 이번 작업에서 게임 저장 정책을 수정할 근거로
사용하지 않는다. 게임 저장 코드는 그대로다.

예비 혼합 실행 전체는 `evidence/development/interleaved-invalid/`에 보존한다.
실패한 사격만 골라 버린 것이 아니라 초기화 격리 조건을 만족하지 않은 묶음
전체를 비교에서 제외했다. 정식 행렬은 원래 `evidence/trials/`의 non-A
1,920회와 아래 A 통제 보완본 480회를 사용한다.
초기 계측 개발 자료 `pilot*`도 정식 결과에 합산하지 않는다.

각 회차의 입력 조건, 새 페이지 시작 항해 상태, 제품/계측 SHA, RNG와 최종 상태를
기록한다. 시드 순서가 결과에 영향을 주지 않도록 문맥을 격리하므로 함종과 방위를
교차 순서로 실행해도 된다. 재시작은 이미 완료된 caseId를 보존하고 나머지만 실행한다.

초반에는 Playwright CDP fulfil로 바이트를 전달했고, 이후 같은 바이트를 loopback
HTTP로 전달했다. 원래 native UI 조작 순서를 유지한다. 4조건의 전체 진단값·결과·RNG
exact equality를 확인한 뒤 완료 회차 경계에서 전환했다. 새 페이지/JS 문맥 격리는
동일하다. 각 회차의 transport 및 전환 기록을 보존한다.

### A 정지 통제 보완

첫 2,400회 완성 후 strict 검사에서 A 4,927발 중 10발이 속도 0 조건을
만족하지 못했다(최대 0.0118941m/s). public shipNav의 STOP 값과 달리 native
dynamics의 private sway가 피격 후 남아 다음 navigation 단계에서 다시 쓰였다.
검수 허용 오차 1e−6m/s는 넓히지 않았다.

추가 진단 hook만 native `haltHorizontalContact()`를 호출해 내부 횡속도를
지운다. 기존 원본 hooks/build fixture와 제품은 그대로다. BASE/B/C/D 네 조건의
전체 결과·RNG·기록 상태 동일을 먼저 확인하고 A 480회를 전부 같은 시드로
재실행했다. A의 문제 조건은 probe와 전체 재실행 간에도 비교한다.

`evidence/trials/`는 원래 2,400회를 모두 보존한다. 최종 분석기는 non-A 1,920회와
`evidence/a-stop-corrected/`의 A 480회를 같은 caseId로 선택한다. 원래 A 480회도
삭제하지 않으며 최초 검수 실패는 `evidence/development/before-a-stop-*`에 있다.
총 행렬 실행은 2,880회, 최종 주 분석은 2,400회다. 두 계측 SHA는 구별한다.

## 계측과 검열

- truth 참조는 진단 로그와 원래 물리 신관 경로에만 있다. B 사격해는 기존 관측
  입력만 사용한다. truth를 현재 사격해에 넣거나 센서 오차를 없애지 않는다.
- CPA는 실제 탄의 유효 swept 구간 전체에서 추적한다. 신관 25m 밖도 기록한다.
  지형/해면/접촉/기폭 중 가장 이른 종료 분율까지만 측정한다.
- `along`은 탄 3D 속도 투영, `cross`는 수평 직교 투영, `vertical`은 world Z다.
  along과 world Z는 기울어진 비행에서 직교하지 않으므로 세 값의 제곱합이나
  원인별 기여율 합계로 해석하지 않는다. 원시 XYZ와 속도 벡터도 보존한다.
- 표적이 사라지거나 시나리오가 끝나 탄 비행이 잘린 경우를 정상 비명중으로
  취급하지 않는다. `LIVE_AT_SCENARIO_END`와 현재까지 최소거리를 별도 기록한다.
  주 비교는 기폭 직전에도 배정한 물리 표적이 살아 있던 탄의 CPA/arrival이다.
- native `arrivalMissM/pk`는 120m 파편 조회 안의 실제 결과다. 조회 밖 ET도 보려면
  기존 `_wip99FragmentArrivalGeometry`로 진단값을 계산해 별도 필드에 기록한다.
  이 진단값으로 피해를 적용하거나 Pk RNG를 한 번 더 호출하지 않는다.
- ET 비율은 실제 폭발한 탄이 분모다. 발사 안 됨/비행 중/해면 충돌은 별도 집계한다.
- 발별 `firstShot`은 해당 마운트의 첫 발이고 `slewS`는 그 마운트의 최근 cue 이후
  시간이다. 재지정이 있었으면 최초 탐지 이후 전체 대기시간과 같지 않다.
  첫 교전 지연 비교에는 회차의 첫 `AUTO_CUE`부터 첫 실제 발사까지의
  `caseFirstAutoCueToFirstReleaseS`도 별도로 사용한다. 모든 cue step은 원시 로그에 있다.
- G7의 기존 비-ASM을 포함할 수 있는 pre-CIWS 카운터는 `LegacyCounter`로 표시한다.
  물리 결과는 kind와 id도 남긴다. 이번 Phase 0의 주 판정은 오차 분포다.

## 보존 및 비교

제품 SHA 동일 여부가 보존 판정의 출발점이다. 보호 함수 281개와 ENV_D 블록도
별도로 해시한다. 계측 ON/플래그 OFF와 native B1의 동일 시드 8조건에서 결과,
RNG, 최종 상태를 비교한다. 실제 B 작동은 해 나이 0과 재계산 호출로 확인한다.

과거 G7는 회차 간 페이지를 재사용했다. 정식 Phase 0의 새 페이지 규약과는
초기화 방식이 달라 모든 과거 숫자의 exact equality를 주장하지 않는다.
차이는 기록하고, 제품 회귀 판정은 같은 초기 조건의 native/계측 A/B로 한다.

CG exact-state 3건과 EW 저장 비교 2건은 지시서 §9에서 승인한 값만 갱신한다.
이전/새 전체 값, 차이 경로, 해시를 보존하고 검증된 게임 코어에서만 적용한다.
원래 B1 보고서와 공통 비교 함수의 허용 오차는 바꾸지 않는다.

## 실행

`TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/gun/B2/diagnostic/run_trials.py --worker 0 --workers 4 --experiments BASE,A,B,C,D`

worker 0…3은 독립 프로세스이며 같은 시뮬 월드나 RNG를 공유하지 않는다.
이는 병렬 시험 실행이며 별도 AI 에이전트를 사용하지 않는다.
`python docs/gun/B2/analyze.py`로 모든 완료 회차를 집계한다.
Phase 0 완료 후 보고서를 push하고 지시서 §2/§12대로 사용자 승인을 기다린다.
