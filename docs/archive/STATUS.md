# 현재 상태 (2026-11-08 EMCON_B 후보 기준)

## 레포

- `main` `3dbe3b84` (PR #73 EMITTER_A 병합)
- 작업 브랜치: `emcon-b` (PR #74 검토 후보, main 미변경)
- 기준 제품: `Aegis_SIM_v48_WIP_EMITTER_A.html`, SHA-256 `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- 후보 제품: `Aegis_SIM_v48_WIP_EMCON_B.html`, 22,157,395 bytes, SHA-256 `3343f5bbe7d6adac0694656ebafef538c3b7407d7ce642225fff94207c142c33`
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
| **EMCON_B** | 범주·장비 방사 통제 + profile UI + 실제 gate | A–E 구현/단계 검증 완료, PR #74 검토 후보 |

## EMITTER_A 결과 요약

- DDG/CG SHADOW exact 뒤 ACTIVE 전환. 물리 출력·receiver plot·RNG·UI·작전 저장 계약 보존.
- SOV 기존 11행 메타데이터만 비활성 등록. 방출/ESM/자체 탐지/공격 0, RF 값 추가 0.
- A–D 게이트 PASS. 최종 광역 1회: Native 364/364, U3 paired 42/42, UI 213/213, WebGL 29/29 PASS.
- 종료 보정: ACTIVE legacy resolver 0, declared resolver 1회/함정. exact 출력/RNG, performance 1.0345×, clean-clone portability PASS.
- 전용 `AEGIS current candidate` Actions run `42373876872` PASS. 기존 광역은 pre-closure 증거이며 반복·재표기하지 않았다.
- 신규 실패·기대값·허용오차 변경 0. 제품/범위/부채는 `docs/electronic/emitter/A/FINAL_REPORT.md` 참조.
- EMITTER_A PR #73은 사용자 결정으로 병합됐다. release/tag는 없다.
- EMCON_B는 Commit A에서 master owner/consumer와 기준을 고정하고, B SHADOW → C ACTIVE → D UI → E lifecycle 순으로 구현했다.

## EMCON_B 후보 결과

- 기존 `emconActive`/`observerC(r).emcon` master와 손상·전원·enabled gate를 유지하면서 ShipRuntime별 category/equipment 세부정책만 추가했다.
- DDG/CG registry의 SPY, SPQ, NAV, SLQ-32 EA가 물리 방출과 실제 own/NPC 측정/ECM gate를 함께 소비한다. 차단 센서 RNG 0, ECM silence에서 allocator/output/coupling/HOJ 0이다.
- UI는 profile registry로 자동 생성되고 390/832/1400 px를 통과한다. FIRE_CONTROL은 등록 장비 없음으로 비활성이고 SPG-62 RF를 추가하지 않았다. 통신 EMCON도 추가하지 않았다.
- save exact/legacy migration/invalid zero mutation, network lease/restore, reset/destroy/auth Chromium 16/16 PASS. 구형 lock debt 14/14 PASS.
- 최종 MAX_THREAT 광역은 정확히 1회 실행했다. 완료 행: 85/85, 8/8, 12/12, 30/30, 13/13, 10/10, paired 42/42, WebGL 29/29. 대형 진단 renderer crash와 SOV/UI fixture는 원시 실패를 보존하고 EMITTER_A 재현으로 상속 부채를 분리했다.
- 후보 workflow 로컬 동등 경로: manifest/SHA, exact rebuild, static 11/11, baseline Chromium 6/6, lifecycle 16/16 PASS; page/console error 0. 원격 run은 PR 본문에 기록한다.
- 기대값·허용오차 변경 0. CONFIRMED_ONLY 성능은 UNVERIFIED. main/merge/release/tag 변경 없음.

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
