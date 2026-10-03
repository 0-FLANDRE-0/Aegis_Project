# AEGIS v48 WIP15C — Plan / Status

갱신: 2026-10-03 (KST)

**상태: WIP15C 구현 및 명시 범위 검증 통과 / GitHub 미반영.**

## 기준

- baseline: `Aegis_SIM_v48_WIP15B1.html`
- baseline SHA-256: `0f04b666af1e71f182fc2232b8c29da07dbc692347212726cea40913240b694e`
- result: `Aegis_SIM_v48_WIP15C.html`
- result bytes: `7,354,511`
- result SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- decoded main SHA-256: `39895ed13f81f0dae1cf1879c1bb47e2ad365fd4d85535ad74f6fe0ecaae09ca`

## 완료

- `V48 WIP13A surface target submergedBreachFloods` 원인 분석 및 fixture 수정.
  - 침수 물리 오류가 아니라 고정 `z=-2.2m` probe가 순간 파면 위에 놓일 수 있던 테스트 결함.
  - 실제 현재 파면 아래 최소 0.75 m의 hull entry를 찾는 deterministic wet fixture로 교체.
  - core self-test failures: **0**.
- SM-2ER Block IV 수동 대수상 `LIMITED_SURFACE_SARH` live release 연결.
  - SPG-62 필수, geometry/reservation/EMCON gate 보존.
  - physical RF/SARH + physical hull contact + WIP12F damage.
- SM-6 Block IA 수동 대수상 `SURFACE_ARH` live release 연결.
  - SPG-62 필수 아님, optional contributor.
  - GPS/INU / B3 weapon-link / ARH / physical hull contact / WIP12F damage 보존.
- surface SM-2ER/SM-6만 B4 stateful loft를 사용할 수 있게 하고, DIVE에 source-pure terminal glide 추가.
  - `SIM_TUNED`: 12°, 최대 +12 km aim height, 마지막 3 km smooth fade.
  - 관측 target state + onboard own-nav만 사용, target truth 미사용.
- MANUAL-only, FRIEND/NEUTRAL/UNKNOWN 보호 및 AUTO/SEMIAUTO 금지 유지.

## 확인한 live 사례

- SM-2ER: 20 km fixed / 20 km 20 kt moving → physical contact.
- SM-6: 20 / 80 / 140 km fixed → physical contact.
- SM-6: 80 km 25 kt moving → physical contact.
- SM-6: 160 km fixed seed 1503001 / 1503002 / 1503003 → 모두 physical contact.

이는 simulator fixture 결과이며 실제 무장 성능·Pk 주장이 아니다.

## 검증

- package / syntax / exact rebuild `53/53`
- WIP15C built-in runtime `8/8`
- WIP15B logistics/Nulka `25/25`
- WIP14B3 nav/DL/GPS/VLS `25/25`
- WIP15B1 ASM acquire contracts `32/32`
- pure-sea negative scenes `48/48` false TRACK 없음
- live surface evidence checks `7/7`
- final tested runtime page errors `0`

## 남은 한계

- SM-2ER의 원거리 surface release는 SPG-62 line-of-sight/geometry/reservation에 의해 policy max보다 훨씬 먼저 차단될 수 있음. 이를 우회하지 않음.
- SM-6 160 km 결과를 전 조건 최대사거리/Pk로 일반화하지 않음.
- 새 terminal glide 수치는 `SIM_TUNED`.
- surface AUTO/SEMIAUTO는 미활성.
- GitHub `WIP15` / `main` / PR / release는 이번 로컬 작업에서 변경하지 않음.