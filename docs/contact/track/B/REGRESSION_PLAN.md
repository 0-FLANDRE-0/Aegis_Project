# TRACK-B 회귀·비교 계획

상태: **준비 단계, 브라우저 시험 미실행**. 기준은 `ee960db`의 최종 TRACK-A, 제품 SHA-256은 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`다. 이번 문서는 B의 연관 변경을 승인하지 않으며 제품·기존 단언·기대값·허용 오차를 수정하지 않는다. 419025 상속 FAIL, CG→friendly observer2 미승인 KNOWN_DELTA, 구형 EMCON UI14 INCOMPLETE는 그대로 유지한다.

## 1. 기존 자료 재사용과 fresh 기준

`regression_runner.py`는 실행 전에 TRACK-A HTML의 실제 SHA, A의 authoritative VALIDATION/complete runtime, 그리고 재사용할 원시 결과 파일이 A의 게시 `CHECKSUMS.sha256`과 같은지 확인한다. provenance가 맞는 TRACK-A 자료만 **기존에 측정된 reference**로 재사용한다. 재사용을 새 TRACK-B 실행 또는 기존 전투 손실 승인으로 세지 않는다.

재사용 대상은 A의 D130 원시 로그와 전체 상태/RNG 서명, 자연 재현3의 OFF 결과, 419025 OFF, idle120, RUNTIME_SUMMARY, REGRESSION_RESULTS와 source/build/scope metadata다. 입력 소스가 다르거나 hash가 맞지 않으면 INCOMPLETE로 멈추고 새 baseline이 필요하다고 보고한다. A/RC1 historical 자료나 FRIENDLY raw를 최종 A 증거처럼 바꿔 쓰지 않는다.

TRACK-B HTML이 아직 없거나 final SHA가 고정되지 않으면 job 목록만 출력한다. 기본 실행은 read-only dry-run이고 `--run --sha <실제 후보 SHA>`가 있어야 브라우저가 열린다.

## 2. 비교의 두 축 — 다른 결과를 자동 합격으로 만들지 않음

1. **원래 검사의 strict 결과:** 기존 native13, UI213, WebGL29, paired42 단언을 그대로 실행한다. A에서 PASS였던 것이 B에서 실패하면 원래 결과는 FAIL이며, 새 알고리즘이 의도됐다는 이유로 기대값을 바꾸지 않는다. 환경/timeout/구형 UI는 INCOMPLETE다.
2. **모든 상태 차이와 원인:** 원시 전후 상태·공분산·분류·identity·authority·sensorAge/hit·source·lifecycle·global/private RNG·scheduler·무장/피해/물리를 보존한다. 변화가 있으면 원래 strict 실패와 별개로 diff를 기록하고 원인 검증/사용자 검토 전 승인하지 않는다. 단순 트랙 수 감소를 PASS로 해석하지 않는다.

paired는 TRACK-A와 TRACK-B를 비교한다. CG→friendly2건을 새 기대값으로 승인하는 경로가 아니다. 원래 paired fixture의 historical normalizer/단언은 변경하지 않되 원시 `pair`의 **모든 JSON leaf**도 별도 diff로 보존한다. host timing/heap 필드는 별도 표시할 뿐 삭제하지 않는다. 원래 비교가 무시하던 performance/aviation까지 통틀어 전체 게임 상태 동일이라고 주장하지 않는다. 새 runtime 전용 snapshot은 관련 mutable track/observer/FCS 상태를 원문 그대로 남겨 누락을 감사해야 한다.

`paired-state-deltas.json.gz`는 원래 전체 paired JSON을 읽어 모든 달라진 leaf와 누락·길이 차이를 남긴다. 원시 pair도 보존한다. 이 파일은 검토 자료이며 자동 KNOWN_DELTA/자동 승인 도구가 아니다. 원인이 입증된 차이만 root가 별도 이유와 미승인 상태를 기록할 수 있다. 새 피격·아군 오인·무방비 전환·원치 않는 발사 등은 그대로 FAIL이다.

## 3. native/runtime 행렬

| 조건 | 기준·필수 기록 | B 판정 원칙 |
|---|---|---|
| 자연 HELO_HOVER_60S | 생성/최대/마지막 파일, x/P·분류·IFF·age·RNG | A는1/1/1. 줄어든 숫자만 보지 않고 false merge/명령 변화 확인 |
| 자연 HELO_ROUTE_120S | 같은 항목+운동·경로·고도 | A는1/1/1. 수상 가정으로 고도 강제되지 않는지 확인 |
| 자연 HARPOON_ROUTE_75S | 생성/최대/마지막, 실제 candidate NIS/gate, 공백·재획득 | A는2/2/1. 47.767s 재획득을 강제 동일ID로 없애지 않음 |
| C55 D130 |419010~419039, DDG119,90°,Kh35U1/11km,MANUAL,AutoAA OFF | 시드별 firing/피격/HP0·탄수·종료시각·전체 서명 및 차이 보존 |
| 419025 상세 | 기존 raw/관측→local file→Phalanx/RAM→동일 틱 RNG/behavior | 상속 FAIL을 숨기지 않음. 나아져도 원인 분리 전 solved/승인 금지 |
| diagnostic OFF/ON/query | 같은 native 입력에서 전체 관련 상태/RNG, ring/조회 | 진단이 명령·필터·실행 횟수·난수에 영향 주면 FAIL |
| 배속1/8/16/64 | 원 fixture/fixed tick 수·state·RNG | 배속끼리 동일. B↔A 차이는 별도 기록 |
| AUTO+IFF ON | 헬기 FRIEND 근거, VLS/ESSM/CIWS 실제 재고 | 자함 헬기에 소모0 유지. truth 예외 금지 |
| IFF OFF/만료 | 미식별·보호 근거 시점·원래 ROE | 강제FRIEND/강제HOSTILE 금지 |
| idle120 | 물리 truth hash·모든 관련 RNG·owner tick 수 | association 변화가 없는 조건에서도 달라지면 원인 조사 |
| native ingress fixture | actual 함수를 통한 one-to-one·2D/3D·stale·NIS거부·외부보고 | fixture-only를 자연 RF나 actual 전투로 부풀리지 않음 |
| network/ESM/ISAR | separate store·CI0.5·freshness·실측/가정·authority | ESM 위치 생성0, ISAR hit/권한승격0, SHARE-only FCS승격0 |
| 성능·owner | 두 owner1회/tick, 평균/p95·트랙/후보 비용·heap sampling | 원시 outlier 유지, nested 비용 합산 금지, speedup/할당률 오인 금지 |

runtime runner는 A의 실제 fixture와 `verify_runtime.py` 관찰 helper를 가능한 범위에서 재사용한다. 다만 A는 동작 보존 단계라 `result==baseline` assert가 들어 있다. B에서 이를 삭제/완화해 성공으로 바꾸지 않는다. 먼저 raw candidate 결과를 저장한 뒤 원래 strict 비교를 적용하고, 실패해도 다른 독립 사례의 원시 비교를 계속 수집하는 별도 B controller를 둔다. 실패한 assert 결과·정확한 변경 필드·공격/보호 결과가 같이 남아야 한다.

본 준비 단계는 B의 shadow/live API와 실제 활성화 범위가 아직 확정되지 않았으므로 runtime controller의 무턱대고 자동화된 policy 선택은 하지 않는다. shadow는 기존 consumer의 상태/RNG와 같아야 하고, live 경로의 의도된 연관 변화는 별도 원인 검토 대상이다. 각 실행은 rollout 설정과 후보 SHA를 함께 고정해야 한다.

## 4. 광역 원래 회귀 수

native13의 기존 단언은364개, TRACK-A→B paired는42개다. 합쳐406개이며, 제거된 `#lockBtn`을 요구하는 구형 EMCON UI14는 INCOMPLETE로 두어 전체420을 설명한다. **414개로 잘못 집계하지 않는다.** 현재 UI213과 자연 탐지→LOCK→정식VLS→full fixed tick→실제 WebGL8발/29단언은420에 중복 더하지 않는 별도 lane이다. WebGL29 PASS를8발 모두 격추했다고 쓰지 않는다.

CG→friendly의 최초404 PASS/observer2 KNOWN_DELTA/구형UI14 INCOMPLETE도 별도 history로 계속 남긴다. 새 TRACK-A→B paired42가 모두 통과하더라도 그 history를 해결/승인하지 않는다. 반대로 B의 의도된 연관 변화로 paired observer가 달라져도 original assertion을 지우지 않는다.

## 5. 실행 격리와 예정 명령

```sh
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/regression_runner.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/regression_runner.py --run --candidate Aegis_SIM_v48_WIP_TRACK_B.html --sha <FROZEN_SHA>
```

첫 명령은 브라우저를 실행하지 않는다. 후보가 고정된 후 root가 실제 실행을 허가한 시점에만 두 번째 명령을 사용한다. `--only`로 독립 suite를 선택할 수 있고 `--resume`은 같은 reference/candidate SHA의 결과만 이어 쓴다. 기존 evidence를 덮어쓰기 전에 보존한다. 신규 구현이 바뀌면 다른 SHA의 결과를 이어 쓰지 않는다.

`--parallel` 기본1, 최대2다. `heavy_browser_slot()`의 두 flock lease는 B runtime/regression 협력 controller가 함께 사용할 수 있다. **모든 heavy 실행은 이 lease 또는 root의 전역 예산 조정에 참여해야 하며**, 다른 미조정 브라우저가 있으면 이 controller의 local2를 전역2로 오인하지 않는다. 짧은 sample도 같은 호스트 부하를 기록하고, sampling값을 실제 할당 byte/count로 단정하지 않는다.

제품·기존 기준·main 수정/병합, PR/release/tag 생성, RF/EKF/무장/피해 계수 보정, 새전술AI/OODA는 이 runner가 수행하지 않는다. 결과는 PASS / FAIL / KNOWN_DELTA(원인 검증·미승인) / INCOMPLETE로 구별하고 `releaseApproved=false`를 유지한다.

## 6. Runtime controller 준비와 RC0 이력

`verify_runtime.py`도 기본은 read-only dry-run이다. TRACK-A / build-time SHADOW / ACTIVE 제품을 각자 고정 SHA로 읽고, 기존 friendly/A 원본 D130·AUTO IFF·idle120 script를 output/HTML 선택만 바꿔 그대로 실행한다. 자연3재현은 같은 기존 `__FRIENDLY_REPRO_A__.run`을 실제 게임에서 실행하고 **비교 전에** 원시 결과와 A의 기존 passive 상태, 모든 열거 가능한 track/owner observer 필드 사본을 저장한다. AFTER_ACTION_TEST_ONLY 사본에는 depth20/cycle marker를 명시하며 진실 상태를 게임 입력으로 되먹이지 않는다.

원본 fixture 및 helper 9파일을 `ee960db`의 git blob hash와 검사한다. D1 원본 signature 동등성, 자연3의 기존 strict equality는 유지한다. 차이가 나도 다른 독립 사례의 결과 수집을 계속하고 FAIL·전체 diff를 남긴다. 각 variant의 진단 OFF/ON을 비교하고 A/B snapshot 반복 조회 전후 전체 상태·private RNG가 같음을 확인한다. SHADOW/ACTIVE 진단 스위치는 build-time 알고리즘 mode를 변경하지 않는다.

Clocks는 원본 24단언을 그대로 실행한다. CPU/owner 측정은 원래 A warmup/bench와 실제 native function에 대한 pass-through kernel counter를 사용한다. 외국/NPC 연관의 전후 차이는 full diff로 남기며 같은 제품 trace OFF/ON 정확성과 구별한다. allocation은 통계적 heap sampling, heap delta는 live heap 변화로 이름 붙이고 모든 outlier를 보존한다.

RC0 ACTIVE SHA `79a098a88c18c7521e54ed1f8115aac9d013321873400076b4e62482b5f78d4a`의 broad lane은 **NOT_EXECUTED**다. native contract에서 own-SPY 연결 누락3건이 먼저 발견되어 root가 시작 예정 작업을 중단했고, 이 controller는 브라우저를 한 번도 시작하지 않았다. `evidence/RC0_BROAD_NOT_EXECUTED.json`은 이 사실만 기록하며 검수 결과가 아니다. 수정 후보 SHA와 native fixture PASS가 전달된 뒤 broad를 한 lane으로 시작한다.
