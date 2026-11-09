# 현재 상태 (2026-11-09 SEEKER_CLOSE_A PR #78 폐쇄 보정 기준)

## SEEKER_CLOSE_A 현재 인계

- PR #77 HP_A를 검증된 head `a3e45f7c`에서 merge commit `78b01165`로 먼저 병합했다. SEEKER_CLOSE_A 기준 main은 그 merge commit이고 작업 브랜치는 `seeker-close-a`다.
- 현재 권위 제품은 계속 `Aegis_SIM_v48_WIP_HP_A.html`, 22,200,135 bytes, SHA-256 `9121c448…36fa`다. 제품 코드·RNG·저장 스키마를 바꾸지 않았고 새 정식 HTML도 만들지 않았다.
- 보정된 고정 진단 19발은 TARGET_HIT 16 / DEFENSE_INTERCEPT 1 / DECOY_SEDUCTION 2 / UNCLASSIFIED 0이다. 기존 17발과 합산하지 않는다. 동일 seed와 1x/8x/16x 결과는 exact다.
- 채프·Nulka 요청 경로는 각각 6/6 실제 배치·관측·후보 선택을 거쳤다. 첫 선택 뒤 SHIP 재선택 사건은 12/12, 마지막 기만체 선택 뒤 최종 회복은 10/12다. 반복 seed 2건은 Nulka가 마지막 유효 선택으로 30 km/10 s 이탈까지 유지된 증명된 유인이다.
- hard-kill/CIWS/soft-kill의 설정·교전·명중·격추를 분리했다. DDG는 실제 5in MFF retirement kill, CG는 실제 Mk45 3발/kill 없음이며 CIWS 관측이 불완전한 장면은 `engaged:null`로 보존한다.
- 구형 radar master+ECM과 true all-radiation-silent를 분리했다. 후자는 현재 UI 권위 경로에서 DDG/CG 모두 ECM 요청 보존, radar/ECM allocator/output/coupling/HOJ 0이다.
- 별도 Kh-32 60 km 고정 경계 2건은 SHIP 연관만 사용해 둘 다 TRACK에 도달했다. DDG는 29회 acquire 재시도 뒤 명중, CG는 coast/reacquire 뒤 miss다. 과거 0/20의 대체 통계가 아니며 별도 조사 경계를 유지한다.
- HP_A current-product contract 19/19, 보호 함수 해시 exact, common truth/RNG/save mutation 0이다. PR #78 전용 Actions가 실제 19발 Chromium과 HP_A gate를 독립 재현하도록 추가했다. 증거 비교는 이산 상태·RNG·단계·결과를 exact로 유지하고 runner별 유한 binary64 telemetry만 고정 `1e-12` 절대/상대 한계와 별도 drift receipt로 감사한다. 게임/회귀 허용오차 변경은 0이며 제품 비변경이므로 one-shot 광역은 재실행하지 않는다.
- Commit C 제품 수정은 없다. 문서·재현 진단 PR을 제출하고 병합·release·tag 없이 사용자 결정을 기다린다. 다음 단계는 `통합 기준선 고정 -> 교전·방어 OODA`다.
- PR #78은 `seeker-close-a -> main`으로 제출했으며 OPEN 상태다. 제품은 HP_A 그대로이고 병합은 사용자 결정으로 남겼다.

# 직전 상태 (2026-11-09 HP_A PR 후보 기준)

## HP_A 현재 인계

- 기준 main은 PR #76 merge commit `82617839`; 작업 브랜치는 `hp-a`다.
- 결과 제품은 `Aegis_SIM_v48_WIP_HP_A.html`, 22,200,135 bytes, SHA-256 `9121c448…36fa`다.
- survival만 물리 상실 권위, 기존 equipment/crew gate만 임무상태 권위, HP는 표시 projection이다. reversible HP 0과 stored-HP 권위 복원을 제거했다.
- 피해·침수·종강도·승조원·무장·RNG 계수는 보존했다. 보호 함수 해시는 U4와 exact이며 최종 invalid HP authority use는 0이다.
- B 제한 11/11, C 제한 19/19, 실제 SOV casualty/save, 1x/8x/16x, DDG/CG 공통 경로 PASS다.
- 동결 후보 광역 1회에서 native 364/364, 후보 결정성 42/42, EMCON 14/14, UI 213/213, WebGL 29/29 PASS. paired raw 6건은 HP_A survival 저장 계약 차이지만 최종 이산 결과·RNG·피해·탄약·observer/offboard는 exact다. U4 장면은 상속 byte pin으로 0/0 중단됐고 pin-only 단일 복구 19/19 PASS다. 원시 실패·기대값·허용오차는 보존했다.
- HP_A PR 제출 후보이며 release/tag는 없다. `CONFIRMED_ONLY` 성능은 UNVERIFIED다.

# 직전 상태 (2026-11-08 SEEKER_UNIFY_U4 기준)

## U4 현재 인계

- 기준은 ESM_A merge commit `f17d3777`; 작업 브랜치는 `seeker-unify-u4`다.
- 결과 제품은 `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U4.html`, 22,195,923 bytes, SHA-256 `00d36aad…c498`다.
- A SARH bistatic, B RAM passive RF/IR, C common association/state가 SHADOW gate 뒤 ACTIVE다. U5/U6은 B/C에 흡수됐다.
- 단계 게이트 PASS. 동결 후보 광역 1회에서 native 364/364, 기준 paired 42/42, 결정성 42/42, EMCON 14/14, UI 213/213, WebGL 29/29 PASS다.
- U4 장면 raw 4건은 원시 증거를 유지하며 하네스 판정 결함으로 분리했다. 제품 변경·광역 재실행·기대값/허용오차 변경은 0이다.
- PR #76 제출 후보이며 release/tag는 없다. `CONFIRMED_ONLY` 성능은 UNVERIFIED다.

# 직전 상태 (2026-11-08 ESM_A 종료 후보 기준)

## 레포

- `main` `babb4d7f` (PR #74 EMCON_B 병합, ESM_A PR 전)
- 작업 브랜치: `esm-a`
- 기준 제품: `Aegis_SIM_v48_WIP_EMCON_B.html`, 22,162,415 bytes, SHA-256 `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`
- 현재 단계: ESM_A 구현·보정·최종 광역 검증 완료, PR/Actions 대기
- 게임 소스는 HTML 안의 `data-c55-index="13"` gzip+base64 블록이다. 압축을 풀면 약 40 MB JS다.

  ```python
  m = re.search(rb'data-c55-index="13">([^<]+)', raw)
  js = gzip.decompress(base64.b64decode(m[1]))
  ```

- 고정 작업 규칙: 루트 `AEGIS_PROJECT_INSTRUCTIONS.md` (Truth 경계, 고정 dt, 격리 RNG, 3D는 표시 전용)

## 역할

- 사용자: 방향 결정, 지시서 검토·전달, 플레이 검수, **PR 병합**
- 리뷰 AI: 레포 검토, 결과 해석, 지시서 작성 (`REVIEWER_PLAYBOOK.md`)
- 작업 AI: 구현·시험·PR 생성

## 지금까지 흐름

| 작업 | 내용 | 상태 |
|---|---|---|
| TRACK-A/B/C | 트랙 신뢰성 | main |
| ASM_SEEKER_A (PR #65/66) | 이웃 ASM 오획득 수정. 시커 최초 연관을 hard basket으로 | main |
| ASM_SEEKER_B | 원거리 획득 실패 진단 (원인: 함정 RCS 과소) | 진단만 |
| SEEKER_UNIFY_A (PR #67) | 함정 RCS를 Skolnik 경험식으로 정비. 시커 통합 감사·설계 | main |
| SEEKER_UNIFY_B (PR #68) | U0 cue 바구니 시간 확장, U1 공통 DTO | main |
| SEEKER_UNIFY_C (PR #69) | U2 ACTIVE, 대함 시커 빔·LOS 왕복 보정, CUE_A(cue 필터·수동 RF·위협 가정 스위치) | main |
| CUE_A-1 (PR #70) | Singer cue 필터(τ=60 s, 정확 이산화), 바구니 상한, 수동 RF 함정 레이더 family·대역·회전 레이더, 0.5 km 거리 하한 원복 | main |
| U3 하푼 | U2/CUE_A/HOJ 공통 계약 + 수동 RF 우도 선택 | main (PR #72) |
| **EMITTER_A** | ShipProfile 장비 방사원 등록 + 공통 ShipRuntime 어댑터 | 완료, PR #73 사용자 병합 |
| **EMCON_B** | V2 global hard-off + 함종 중립 소비자 바인딩 + 범주·장비 방사 통제 | 완료, PR #74 사용자 병합 |
| **ESM_A / TRACK-D** | 익명 raw ESM + AOA/TDOA/FDOA + UI/cue + DDG/CG receiver adapter | 구현·보정·최종 광역 PASS, PR 대기 |

## EMITTER_A 결과 요약

- DDG/CG SHADOW exact 뒤 ACTIVE 전환. 물리 출력·receiver plot·RNG·UI·작전 저장 계약 보존.
- SOV 기존 11행 메타데이터만 비활성 등록. 방출/ESM/자체 탐지/공격 0, RF 값 추가 0.
- A–D 게이트 PASS. 최종 광역 1회: Native 364/364, U3 paired 42/42, UI 213/213, WebGL 29/29 PASS.
- 종료 보정: ACTIVE legacy resolver 0, declared resolver 1회/함정. exact 출력/RNG, performance 1.0345×, clean-clone portability PASS.
- 전용 `AEGIS current candidate` Actions run `42373876872` PASS. 기존 광역은 pre-closure 증거이며 반복·재표기하지 않았다.
- 신규 실패·기대값·허용오차 변경 0. 제품/범위/부채는 `docs/electronic/emitter/A/FINAL_REPORT.md` 참조.
- EMITTER_A PR #73은 사용자 결정으로 병합됐다. release/tag는 없다.
- EMCON_B는 Commit A에서 master owner/consumer와 기준을 고정하고, B SHADOW → C ACTIVE → D UI → E lifecycle 순으로 구현했다.

## EMCON_B 병합 결과

- 기존 `emconActive`/`observerC(r).emcon` radar master와 손상·전원·enabled gate를 유지하면서 ShipRuntime별 V2 `allRadiationSilent`와 category/equipment 세부정책을 추가했다. Global hard-off는 radar/ECM `FORCE_RADIATE`를 우선 차단한다.
- 센서 코드는 함종 중립 `AIR_SEARCH_VOLUME / SURFACE_SEARCH_SCAN / NAVIGATION_SCAN`만 요청하며 DDG/CG ShipProfile 바인딩이 실제 장비를 결정한다. 누락·중복·없는 장비는 fail-closed이고 같은 범주의 다른 장비는 대신 통과할 수 없다. 차단 센서 RNG 0, ECM silence에서 allocator/output/coupling/HOJ 0이다.
- UI는 profile registry로 자동 생성되고 390/832/1400 px를 통과한다. FIRE_CONTROL은 등록 장비 없음으로 비활성이고 SPG-62 RF를 추가하지 않았다. 통신 EMCON도 추가하지 않았다.
- save exact/V1 migration/invalid zero mutation, network overlay, reset/destroy/auth Chromium 17/17 PASS. 구형 lock debt 14/14 PASS.
- MAX_THREAT 광역 1회는 수정 전 SHA `3343f5bb…c33`의 증거다. 2차 보정 SHA에서는 지시대로 재실행하지 않았다.
- 보정 제한 closure: correction-2 static 15/15, correction-3 static 17/17·runtime 16/16, hard-silent/breakout 10/10, UI 13/13, lifecycle 17/17, release smoke 7/7, baseline 6/6, lock 14/14 PASS; page/console error 0. 원격 run은 PR 본문에 기록한다.
- 기대값·허용오차 변경 0. CONFIRMED_ONLY 성능은 UNVERIFIED. PR #74는 `babb4d7f`로 병합됐고 release/tag는 없다.

## ESM_A 현재 경계

- Commit A는 EMCON_B 제품 exact rebuild, 기존 anonymous bearing DTO, RF/EMCON/network 소유권과 함수 해시를 동결한다. 제품 동작 변경은 없다.
- Commit B–E에서 단함 AOA, 협동 raw ESM AOA/TDOA/FDOA, UI·수동 cue, DDG/CG profile adapter와 lifecycle을 같은 PR 안에서 순서대로 구현한다.
- SOV Band Stand/MR-184/Mineral과 sensor/EW/weapon capability는 baseline 비활성 상태를 유지한다.

## ESM_A 종료 후보 결과

- 최종 제품 `Aegis_SIM_v48_WIP_ESM_A.html`은 22,182,527 bytes, SHA-256
  `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`이다.
- 공통 추정기는 `r.ew.esmA.contacts`, 기존 소프트킬 소비용 native projection은
  `r.ew.executionF.contacts`를 소유하도록 분리해 초기 전술 회귀를 제거했다.
- 수정 SHA의 승인된 MAX_THREAT 광역 회귀 1회는 정적 17/17, native 364/364,
  후보 결정성 42/42, 현재 EMCON UI 14/14, UI 213/213, WebGL 29/29 PASS다.
- EMCON_B 대비 paired raw 36/42의 여섯 차이는 DDG/CG idle/raid/damaged의
  `state.esmA` 저장 필드뿐이다. 사용자가 의도된 스키마 변경으로 승인했고,
  해당 필드만 제거하면 물리/RNG/피해/탄약/observer/offboard가 모두 exact다.
- 기대값·허용오차 변경은 0이다. SOV ESM 장비와 새 전술/자동 교전 소비자는
  범위 밖이며 release/tag는 없다.

## U3 결과 요약 (병합 기준)

- A–D 단계 게이트 PASS. 각 단계 SHADOW 확인 뒤 ACTIVE 전환.
- 일반 하푼 track cue의 고정 4 km 상한만 제거; 기존 250 m 하한 복구·명명; route prior 4 km 유지.
- 하푼 HOJ는 ASSUMED_THREAT, MAX_THREAT ON/CONFIRMED_ONLY OFF.
- 수동 RF 후보는 gate 뒤 `d² + ln(det(S))`; truth/RNG 사용 0.
- 보정 제한 시험: 225→250 m, 4,800 m 무상한, 실제 발사 cueHandoff/시커/보호 소비, 실제 stale 거부 PASS.
- 보정본 최종 광역 1회: native364/364, UI213/213, WebGL29/29 PASS.
- paired raw38/42의 4건은 D ACTIVE raid 경로로 단계 분리. 기대값 갱신0, 물리·손상·VLS·최종 결과 동일.
- 상세와 잔여는 `docs/missile/seeker-unify/U3/FINAL_REPORT.md`, `BACKLOG.md`를 따른다.
- PR Actions의 Playwright 1.55 job 22개는 Ubuntu 26.04 비호환을 피해 `ubuntu-24.04`로 고정했다. 자동 실행 `42264252460`에서 설치 도달 21/21 성공(기존 22/22 실패 해소). 전체는 29 success / 1 WIP12D CIWS 배속 결정성 failure / 2 checkout-timeout cancelled이며 재실행하지 않았다.
