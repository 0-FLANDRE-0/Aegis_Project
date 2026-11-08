# 현재 상태 (2026-11-08 ESM_A 착수 기준)

## 레포

- `main` `babb4d7f` (PR #74 EMCON_B 병합)
- 작업 브랜치: `esm-a`
- 기준 제품: `Aegis_SIM_v48_WIP_EMCON_B.html`, 22,162,415 bytes, SHA-256 `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`
- 현재 단계: ESM_A Commit A 무변경 감사
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
| **ESM_A / TRACK-D** | 익명 raw ESM + AOA/TDOA/FDOA + UI/cue + DDG/CG receiver adapter | Commit A 기준 감사 진행 |

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
