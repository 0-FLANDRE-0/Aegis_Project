# AEGIS Simulator v48 — Release Status

릴리스 기준일: 2026-10-03 (KST)

**상태: v48 STABLE RELEASE / WIP15C byte-identical promotion.**

## 정식 산출물

- simulator: `Aegis_SIM_v48.html`
- bytes: `7,354,511`
- SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- Git blob SHA: `f540b68f138e3ed85614c41f6794be78602229d8`
- promotion source: `Aegis_SIM_v48_WIP15C.html`
- promotion policy: **파일 내용 변경 없이 같은 Git blob을 정식 파일명으로 승격**

따라서 v48은 WIP15C에서 추가 튜닝·상수 변경·HTML 재패킹을 하지 않은 검증본이다. WIP15C는 `archive/v48/WIP15C/`에 보존한다.

## v48에 포함된 주요 통합 범위

### 함정 생존성 / 종말효과

- detailed compartment / flooding / fire / smoke / crew state와 operational snapshot 계층.
- WIP12 계열 공통 terminal-event, 내부 잔존체, 외피 breach, 침수 연결, 제한된 구조·기계 피해 및 표시 계층.
- WIP13 계열 제한적 대수상 교전과 surface terminal fuze/contact 경로.
- 기존 `V48 WIP13A surface target submergedBreachFloods` self-test fixture 결함 수정.
  - 고정 위치가 순간 파면 위에 놓일 수 있던 테스트 오류를 deterministic submerged hull entry fixture로 교체.
  - WIP15C 최종 검사에서 core self-test failures `0`.

### 센서 / 교전 / 요격탄

- missile onboard own-navigation과 truth boundary.
- Kh-35U / Kh-32 / RAM own-navigation 경계.
- 공통 fixed-step VLS release scheduler.
- generic weapon-link / return-link capability와 SM-6 GPS/INU + 양방향 DL profile.
- SM-2MR / SM-2ER / SM-6 / ESSM별 stateful loft.
- ASM seeker SEARCH→ACQUIRE 안정화: acquire hold, 연속 관측 hysteresis, 짧은 confirm-coast.
- SM-2ER 수동 대수상 `LIMITED_SURFACE_SARH`.
- SM-6 수동 대수상 `SURFACE_ARH`.
- surface SM-2ER/SM-6 terminal glide는 관측 target state + onboard own-nav를 사용하며 target truth를 유도에 사용하지 않는다.

### soft-kill / 기만

- SRBOC 6기 × 6튜브 canonical geometry와 실제 tube muzzle launch.
- Mk 214 장전 36발 + 사용자 지정 예비탄 72발, 완전 빈 발사기 단위 재장전.
- Nulka 4기 × 2 canister, 장전 8발 + 사용자 지정 예비탄 16발, 완전 빈 발사기 단위 재장전.
- 별도 active-decoy world entity, 발사/이동/호버/이탈/소멸 상태.
- active RF source가 기존 ASM 측정·연관·HOJ 경로에 들어가며 Nulka identity로 표적 전환을 강제하지 않음.
- SK AUTO와 수동 발사, mass/snapshot/reset/UI/2D/3D 정합.

Nulka의 RF 세기·비행제어·재장전 시간 등 비공개/미확정 항목은 `SIM_TUNED` 게임 추상화이며 실제 장비 성능값으로 취급하지 않는다.

## WIP15C 최종 검증 기록

- package / syntax / exact rebuild: `53/53 PASS`
- WIP15C built-in runtime: `8/8 PASS`
- WIP15B logistics / Nulka: `25/25 PASS`
- WIP14B3 nav / DL / GPS / VLS: `25/25 PASS`
- WIP15B1 ASM acquire contracts: `32/32 PASS`
- pure-sea negative scenes: `48/48`, false TRACK `0`
- live surface evidence: `7/7 PASS`
- final tested runtime page errors: `0`
- core self-test failures: `0`

지원 자료의 세부 조건과 seed는 `docs/wip15/C/`에 보존한다. 위 하위 테스트 일부는 중복되므로 숫자를 합산한 고유 시험 총수는 주장하지 않는다.

## 확인된 surface live 사례

- SM-2ER: 20 km fixed / 20 km 20 kt moving → physical contact.
- SM-6: 20 / 80 / 140 km fixed → physical contact.
- SM-6: 80 km 25 kt moving → physical contact.
- SM-6: 160 km fixed seeds `1503001`, `1503002`, `1503003` → physical contact.

이는 시뮬레이터 fixture 결과이며 실제 무장의 공개 성능·최대사거리·Pk를 뜻하지 않는다. SM-2ER은 실제 게임 내 SPG-62 LOS/geometry/reservation에 의해 policy 상한보다 훨씬 일찍 제한될 수 있다.

## 릴리스 한계

- surface AUTO / SEMIAUTO는 활성화하지 않았다. 대수상 SM-2ER/SM-6는 MANUAL-only 정책이다.
- Nulka/채프/EA는 방어 성공 확률을 직접 강제하지 않으며 실제 기만 성공률을 주장하지 않는다.
- 실기기 모바일 GPU/FPS는 별도 성능 검증 대상이다.
- 여러 `SIM_TUNED` 상수는 게임 모델이며 실제 군용 시스템의 비공개 수치가 아니다.
- 기존 저장 형식 중 WIP15 이전 soft-kill inventory 구조와 호환되지 않는 것은 명시적으로 거부하며 silent migration하지 않는다.

## 역사 보존

- WIP14B4: `archive/v48/WIP14B4/`
- WIP15C: `archive/v48/WIP15C/`
- WIP14/WIP15 설계·감사·검증 문서는 `docs/wip14/`, `docs/wip15/`에 유지한다.

정식 v48은 별도 코드 수정이 아니라 검증된 WIP15C의 바이트 동일 승격이다.
