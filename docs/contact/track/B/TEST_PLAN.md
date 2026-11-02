# TRACK-B 시험 계획

기준: `track-b-association`, TRACK-A 기준 커밋 `ee960db`, 압축 해제된 실제 게임 소스 `/dev/shm/track-b-baseline-source.js`. 구현 지시의 TRACK-B 및 필수 매트릭스를 따르며, 기존 기대값·허용 오차를 수정하지 않는다. 이 문서는 시험 설계이고 실행 PASS 보고서가 아니다.

## 시험 계층과 실행 제한

1. **제품 공통 helper 단위시험:** 제품에 내장되는 동일 모듈을 Node VM에서 실행한다. 비용 행렬의 해·보류/거부 결정·비누수·순수성만 확인하며 자연 RF나 게임 전투 시험으로 세지 않는다. 공통 helper의 API는 구현 담당자와 확정한 뒤 fixture를 연결한다.
2. **실제 native 익명 관측 통합시험:** baseline/candidate HTML을 기존 `friendly/A/harness.py`로 로드한다. 실제 SPY·surface·NPC·Hawklink·C55 함수를 실행한다. 합성 입력은 관측/필터 prior만 갖는다. 실제 표적 ID, faction, owner, truth 위치를 연관 함수에 전달하지 않는다. 이 계층은 `DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF`로 표시한다.
3. **자연 RF·fixed tick 회귀:** 기존 헬기/Harpoon 3재현, CIWS 30시드, AUTO IFF, native 13 suite, 현 UI 및 WebGL 시험을 원래 fixture·assertion·RNG로 실행한다. 결과 변화를 시드/타임라인별로 분류한다. 통합 fixture 성공으로 대신하지 않는다.

무거운 브라우저 실행은 root의 슬롯 승인을 받은 뒤 시작한다. 한 lane에서 직렬 실행하며, 실행한 HTML SHA·test source SHA·명령·exit code를 모든 evidence manifest에 기록한다. 개발 중 shadow 결과는 실제 소비자 적용 결과와 구별한다.

확정된 구현 계약: `trackBSolveB({plotCount,pairs:[{i,id,nis,sanity?}],gate},assigner)`를 실제 기존 `bridgeMasterEMinCostAssignmentV35`와 실행한다. ambiguous component의 같은 cardinality 대체 할당 총 NIS 차이가 1 이하이면 보류하고, component 크기 12 초과도 보류한다. 별도 geometry gate는 거리 2500m / radial innovation 180m/s **hard cap**이다. 기존 `networkAssociationNisG`의 한계를 재사용하며 필터 P나 측정 공분산이 크더라도 없애지 않는다. 초기 max(2500m, 5σ) 제안은 브라우저/게임 시험 전에 폐기되었으며 초기 40개 단위시험 기록은 `evidence/proposals/solver-unit-initial40.json`에 PROPOSAL_NOT_FINAL로 보존한다. 기존 게임 fixture·기대값을 갱신한 것이 아니다.

시각 처리는 신규 예측 모델을 만들지 않는다. 로컬 트랙은 현재 fixed tick까지 기존 native predict를 사용하며, delayed Hawklink의 위치·age² 공분산 처리 및 future/maxAge15초 검사를 보존한다. B05는 이 기존 동작 보존을 검사한다. 일반적인 과거 epoch 재정렬 모델을 구현·검증했다고 주장하지 않는다.

**C55는 이번 B에서 live batch로 바꾸지 않고 shadow만 비교한다.** 기존 sweep은 RF 측정과 갱신이 interleave되어 있어 이를 즉시 재배열하면 RNG/제어 경로가 바뀔 수 있다. B08/B09는 기존 live own-fire 보호 양방향 유지와 실제 native 호출에서 나온 shadow 후보/이유를 검사하며, 아직 소비자가 쓰지 않는 제안값을 live 수정 성공으로 보고하지 않는다.

SPQ AIR의 interleaved 경로도 SHADOW 범위다. SPQ SURFACE 실제 caller의 ambiguity hold/no-birth 검수와 이를 혼동하지 않는다. focused SPY의 지정 우선순위와 dwell별 기존 사용 규칙을 보존하는 양성 검사를 둔다. 아직 적용하지 않은 focused 경쟁/모호성 처리까지 live 완료라고 표시하지 않는다.

Hawklink의 SHADOW 빌드는 기존 sequential 소비 경로를 유지한다. ACTIVE의 delivery cohort 제안을 실제 제품의 동시 공통 epoch shadow가 이미 검증한 것으로 표현하지 않는다. 같은 익명 입력을 별도 owner의 A/SHADOW/ACTIVE에 공급한 결과를 비교하여 그 차이를 확인한다. old fix는 후보별로 배제해야 하며, 한 반복 후보가 있다는 이유로 다른 유효 후보나 정당한 새 파일까지 보고 전체를 HOLD하지 않아야 한다.

## 신규 시험 행렬

| ID | 경로 / 입력 | 필수 판정과 남길 증거 |
|---|---|---|
| B01 | own SPY, NPC AIR: 독립 2개 파일에 반대 Doppler의 두 관측이 교차 | 한 dwell당 plot/track 각각 최대 1회; 관측 Doppler가 구분 가능한 교차에서는 번호 교환·합병 없음. 원래/새 후보 NIS·거리·속도·시각·할당을 기록 |
| B02 | own SPY/surface, NPC: 두 파일의 예측/공분산과 후보 비용이 동일한 exact tie | 임의 기존 파일 선택/병합 없음; 기존 firm hit 증가 없음. 보류 또는 새 tentative는 이유와 함께 기록. 실제로 구별 불가능한 교차에 영구 ID 유지 요구를 만들지 않음 |
| B03 | B01/B02의 track/plot 입력 순서 순열 | 관측으로 구별 가능한 할당은 순서에 무관; exact tie의 hold 결과도 순서에 무관. 단순 숫자 ID 정렬을 물리적 근거로 쓰지 않음 |
| B04 | 높은 위치 공분산 + 물리적으로 멀리 떨어진 익명 plot | native NIS 통과 여부와 별개로 거리 sanity 거부; 공분산 팽창만으로 false merge 없음. 숫자 한계는 확정된 제품 policy를 그대로 기록 |
| B05 | 같은 위치 근처의 비현실적 속도 불일치, fresh/coast/측정 시각차 | 각 제품 policy의 경계 안/밖, 시간 정렬 방향 및 age 반영. old fix를 현재 시각으로 승격하지 않음. 유효한 공백 후 재획득은 허용하며 drop 이후 번호 유지 강요 금지 |
| B06 | 2D 수상→3D AIR / 3D AIR→2D 기여, radial 누락 및 빔 직각 이동 | 기존 관측 차원별 EKF를 실제 호출. 8m prior로 관측 고도/vz 분포를 덮지 않음; 누락 Doppler를 0 측정으로 승격하지 않음; UNKNOWN/권한 유지 |
| B07 | native `spyFalsePlotV31` 또는 기존 RF false-plot 진단 경로의 단발·비연속 가짜 관측 | 실제 기존 생성 경로와 RNG 사용. 실제 신호와 잘못 결합/확정되는지 기록; false probability·클러터/Pd·확정 임계값을 바꾸지 않음. noise-tail RF 발생률 검증과 익명 ingress 판정 검증을 분리 |
| B08 | C55 player: 동일/근접 위치의 known own launch + 비자함 RF 관측 교차 | own-fire partition 양방향 유지; 비자함 파일에 ownFire/FRIEND 전염 0, 기존 아군 파일의 유효 보호 삭제 0. 모호한 적 탄을 아군으로 승격하지 않음 |
| B09 | C55 NPC `createWeaponContextD`의 B08 동일 입력 | player/NPC 각각 실제 closure 경로 호출; 분리된 store/RNG 유지. association 이후 파일·protection·audit를 비교. 출력 차이가 있으면 양 경로 코드/문맥 근거 보고 |
| B10 | Hawklink 같은 delivery cohort의 두 report/두 local file, 입력 순서 반전 | 실제 `ingestOffboardReportC`→queue→`drainOffboardC` 실행; 보고 batch의 일대일 유지, 한 파일에 두 별도 표적 합병 없음. 원 측정 시각과 지연 공분산 유지 |
| B11 | Hawklink replay/새 sequence의 동일 old fix/시간차 fix/단절 | 원래 replay 및 독립 hit 정책 유지; stale report가 fresh 파일을 갱신하지 않음; 링크 단절/queue/최대 age와 권한 불변. TRACK-C/D의 새 정책을 선행 구현하지 않음 |
| B12 | network 별도 store·ESM bearing-only·ISAR evidence | B에서 적용하지 않는 경로는 현 결과 보존; network CI0.5, local FCS 권한 상승 0; ESM 위치 생성 0; ISAR 위치 hit/적성 증가 0 |
| B13 | 공통 helper 동일 입력 반복·deep-frozen canary 입력 | 입력/clock/RNG mutate 0, detached 결과, forbidden truth/owner/faction 값 미사용. 같은 관측에서 canary만 바꿔도 결과 동일 |
| B14 | 공통 helper의 bounded 크기/invalid 수치/동률/모든 후보 탈락 | NaN/Infinity나 빈 행렬에서 임의 match 없음. track 및 plot 중복 사용 0, deterministic 종료, 과도한 MHT/JPDA 생성 없음 |

## 실제 게임 함수 사용 증명

`test_support/native_support.js`는 관측 생성·스냅샷·private owner 준비·실제 tick 진행만 제공한다. NIS, predictor, assignment, EKF, gate, classification을 재구현하지 않는다. 각 통합 결과에 호출한 native 함수 이름과 실제 소스 SHA를 기록한다.

own SPY는 `spyGlobalAssignmentsV36`/기존 적용 경로, surface는 `spq9bAcceptSurfacePlotsWip13B1` 또는 `spyExecuteSurfacePlotsWip13B9`, NPC는 `observerAcceptPlotsC`, Hawklink는 ingest/drain 경로를 호출한다. 실제 helper가 바뀌면 새 이름을 호출 목록에 기록하되 시험용 대체 연관 알고리즘을 만들지 않는다.

C55 NPC 함수는 closure 내부에 있다. 필요 시 **시험용 HTML 복사본에만**, baseline/candidate 동일 anchor로 접근자를 추가한다. 접근자는 실제 native post-RF association 함수를 한 번 호출하거나 closure snapshot을 반환하며, RF/Pd·필터·할당·보호 로직을 바꾸지 않는다. 이 방식은 root와 seam을 확정한 뒤 적용한다. 원본 HTML·빌드에는 시험 접근자를 넣지 않는다. 자연 C55 30시드 검수는 접근자/주입 관측을 사용하지 않는다.

시험용 AFTER_ACTION 진실 비교가 필요하면 결과 JSON의 별도 구역으로만 만들며 게임 함수의 입력·실시간 소비자에 노출하지 않는다. 확률 RF를 제거한 deterministic ingress 결과와 자연 RF 결과를 별도 표에 둔다.

## 회귀·완료 판단

- 최초 baseline을 그대로 실행하고 native 실패, 환경/구형 UI 제약, 미승인 delta를 보존한다. `419025`와 paired observer 차이를 PASS로 재명명하거나 기대값 갱신하지 않는다.
- 3재현은 birth/max/final 수뿐 아니라 false merge, 정당한 gap/reacquisition, 후보 rejection 근거를 본다. 단순 파일 수 감소는 성공 조건이 아니다.
- 실제 CIWS 30시드 `419010~419039`에서 HP/피격/HP0/무장 소모/실제 방어 결과를 전후 모두 기록한다. 새 성공→실패는 즉시 보고하고 계수/seed/발사 시각을 바꾸지 않는다.
- trace OFF/ON full game·owner RNG·private RNG 동일; query 무변경; 1/8/16/64배속과 owner별 1회/tick; 120초 idle truth hash; CPU median/p95·통계적 allocation·트랙/후보 수를 기록한다. 짧은 shared-host 측정에서 부호가 바뀌면 속도 향상으로 주장하지 않는다.
- 새로운 B 단위/통합 단언 수는 기존 domain420/UI213/WebGL29에 더하지 않는다. 실패/미완료는 각기 FAIL/BLOCKED로 남긴다.
- baseline 대비 새 명확한 association 보호 위반 0, 정상 재현 악화 0, 영향 받은 전투 변화의 원인 증거, 보호 범위 무변경이 확인되기 전 stage PASS/release approval을 부여하지 않는다.
