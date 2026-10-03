# AEGIS v48 WIP15C — Surface Standard Missile & WIP13A Flood Fixture Repair Report

작성: 2026-10-03 (KST)

## 1. 기준 / 결과

- 기준: `Aegis_SIM_v48_WIP15B1.html`
- 기준 SHA-256: `0f04b666af1e71f182fc2232b8c29da07dbc692347212726cea40913240b694e`
- 결과: `Aegis_SIM_v48_WIP15C.html`
- 결과 크기: `7,354,511 bytes`
- 결과 SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- decoded C55 main SHA-256: `39895ed13f81f0dae1cf1879c1bb47e2ad365fd4d85535ad74f6fe0ecaae09ca`

WIP15C는 두 범위만 수정한다.

1. SM-2ER Block IV / SM-6 Block IA의 수동 대수상 발사·유도·종말효과 연결.
2. 장기간 남아 있던 `V48 WIP13A surface target submergedBreachFloods` self-test 실패 원인 수정.

ASM seeker WIP15B1, Nulka/SRBOC 물류, B3 weapon link/GPS, 기존 공력·추진·질량 권위는 별도 회귀로 보존했다.

---

## 2. WIP13A `submergedBreachFloods` 원인

### 관측된 실패

이전 deterministic fixture는 local `z=-2.2 m` 위치에 구멍을 만든 뒤 20초 동안 침수 적분을 실행했으나 특정 maritime seed/함 자세에서:

- water = `0 m³`
- inflow = `0 m³/s`

가 되어 self-test가 실패했다.

### 실제 원인

침수 solver 자체가 멈춘 것이 아니었다. 자기검사에서 고정한 `z=-2.2 m` 외판 접촉점이 **현재 흘수 + 순간 파랑면 기준으로 실제 수면 위에 놓일 수 있었다.** 즉 이름은 `submergedBreach`였지만 fixture가 항상 submerged임을 보장하지 않았다.

분류:

`OLD_FIXTURE_Z_MINUS_2P2_COULD_BE_ABOVE_INSTANTANEOUS_WAVE_SURFACE`

### 수정

- 기존 `z=-2.2 m` damage/fire probe는 그대로 보존.
- flooding 검사는 별도 `wip15cSubmergedFloodProbeWip13A()`를 사용.
- 실제 hull crossing을 순회하고 현재 maritime sea surface를 계산해서 **최소 0.75 m 이상 잠긴 entry**를 선택한 뒤 침수 적분.
- 테스트 타깃 생성 시 surface-ship physics state를 먼저 초기화해 draft/attitude 기준을 확정.
- 침수 공식, 파공 유량 공식, stability solver를 통과시키기 위해 숫자를 직접 조정하지 않음.

### 수정 후 seed 142000

- selected local z: `-3.800000000000001 m`
- initial breach submergence: `0.7850367431543872 m`
- 20 s water: `61.71737345814458 m³`
- inflow at 20 s: `3.2060108304425183 m³/s`
- initial draft: `-1.7953626142864323 m`
- target draft: `-1.7853440290022156 m`
- target heel: `0.38212364034996205°`

전체 WIP13A diagnostic check가 true이며 `window.__CORE_SELFTEST_FAILURES__`는 빈 배열이 됐다.

1× / 8× / 16× / 64× fixed-step flooding fixture도 동일 tick count에서 exact 일치했다.

---

## 3. SM-2ER / SM-6 대수상 교전

### 공통 권위

기존 WIP13 surface combat의 익명 관측 track / operator identity / FCS quality 경계를 그대로 사용한다.

- **MANUAL ONLY**
- 허용 identity: `HOSTILE`, `TRAINING_TARGET`
- `FRIEND`, `NEUTRAL`, `UNKNOWN` 보호 유지
- AUTO / SEMIAUTO 표면발사 금지
- surface track confirmation / covariance / freshness / FCS quality 필요
- EMCON 및 함정 피해 / VLS 가용성 재검사
- 실제 surface target truth object ID를 발사 판단에 넘기지 않음

거리 수치는 전부 `SIM_TUNED_PUBLIC_UNKNOWN` 게임 정책값이며 실제 무장 최대사거리 주장에 사용하지 않는다.

### SM-2ER Block IV

- surface mode: `LIMITED_SURFACE_SARH`
- game policy range: 3–120 km
- **SPG-62 필수**
- SPG geometry / reservation / EMCON gate를 실제 release에서 다시 확인
- 표면 SARH physical RF return → missile-local EKF → physical hull contact → WIP12F damage
- live impact source: `SM2ER_SURFACE_SARH_LIVE`

정책의 120 km는 발사 보장거리가 아니다. 저고도 surface illumination은 SPG-62 line-of-sight/geometry 때문에 훨씬 먼저 제한될 수 있으며, 이를 없애기 위해 레이더 지평선이나 SPG gate를 완화하지 않았다.

실제 live fixture 확인:

- 20 km 고정 표적: physical contact / WIP12F damage, impact `1326.77 m/s`
- 20 km / 20 kt 이동 표적: physical contact / WIP12F damage, impact `1326.73 m/s`

### SM-6 Block IA

- surface mode: `SURFACE_ARH`
- game policy range: 3–160 km
- SPG-62 필수 아님; 있으면 optional contributor
- 기존 SM-6 GPS/INU 및 weapon-link 계약 보존
- terminal ARH physical RF return → physical hull contact → WIP12F damage
- live impact source: `SM6_SURFACE_ARH_LIVE`

---

## 4. 장거리 surface trajectory 문제와 수정

초기 surface integration은 발사 자체는 됐지만 SM-6 장거리에서 문제가 있었다.

- surface B4 loft를 막으면 80 km에서 약 1.5 km밖에 상승하지 못하고 약 23 km를 남겨둔 채 sea impact.
- 단순히 기존 B4 loft를 허용하면 80 km에서는 크게 개선되지만 140 km급에서 terminal dive가 너무 일찍 수면으로 수렴했다.

원인은 surface target의 관측 aim height가 수 m 수준인데, B4 `DIVE` 이후 legacy command path와 v1 aim path가 그 수면 근처 reference를 직접 사용해 고고도 에너지 상태에서 지나치게 가파른 terminal descent를 요구한 것이었다.

### WIP15C surface terminal glide

SM-2ER / SM-6 surface runtime에 한해서:

- B4 stateful loft 허용.
- `DIVE` 단계에만 measurement-space terminal glide reference 사용.
- 기준: **12° SIM_TUNED glide**, 최대 추가 aim height `12,000 m`, 마지막 `3 km`에서 smooth fade.
- target X/Y는 받은 관측/track state만 사용.
- own position은 onboard own-navigation `missileNavB2OwnState()`만 사용.
- target truth geometry / hidden target position은 사용하지 않음.
- 최종 근거리에서는 기존 observed surface aim height로 자연스럽게 수렴.
- 짧은 20 km shot은 B4 `DIRECT`이므로 기존 direct surface path를 유지.

이 값들은 실제 SM-6/SM-2ER 생산 유도법을 주장하는 값이 아니라 장거리 game trajectory용 `SIM_TUNED` 값이다.

### live 결과

| Weapon | 조건 | 결과 | impact speed |
| --- | --- | --- | ---: |
| SM-2ER | 20 km fixed | CONTACT | 1326.77 m/s |
| SM-2ER | 20 km / 20 kt | CONTACT | 1326.73 m/s |
| SM-6 | 20 km fixed | CONTACT | 1322.18 m/s |
| SM-6 | 80 km fixed | CONTACT | 352.48 m/s |
| SM-6 | 80 km / 25 kt | CONTACT | 351.97 m/s |
| SM-6 | 140 km fixed | CONTACT | 241.16 m/s |
| SM-6 | 160 km fixed seed 1503001 | CONTACT | 238.69 m/s |
| SM-6 | 160 km fixed seed 1503002 | CONTACT | 236.76 m/s |
| SM-6 | 160 km fixed seed 1503003 | CONTACT | 236.20 m/s |

위 결과는 deterministic simulator fixture 결과다. 실제 무장 사거리/Pk나 모든 표적 기동에서의 안정 명중을 의미하지 않는다.

---

## 5. 회귀 / 검증

- WIP15C package / C55 manifest / JS syntax / exact rebuild: **53/53 PASS**
- WIP15C built-in runtime / flood / policy / terminal / old SM-2 / frozen physics / WebGL context: **8/8 PASS**
- WIP15B Nulka + SRBOC reserve/reload/logistics regression: **25/25 PASS**
- WIP14B3 nav / DL / GPS / VLS / frozen-contract regression: **25/25 PASS**
- WIP15B1 ASM acquisition contracts: **32/32 PASS**
- pure sea-clutter negative scenes: **48/48 no false TRACK**
- WIP15C live surface evidence checks: **7/7 PASS**
- page errors in final runtime suites: `0`
- boot core self-test failures: `0`

기존 SM-2 8 km live surface SARH regression도 physical RF / SPG / local SARH / physical hull contact / WIP12F damage를 유지한다.

WIP15B1의 ASM seeker 안정화 코드는 이번 범위에서 다시 튜닝하지 않았으며 계약·negative-sea 회귀로 확인했다.

---

## 6. 한계 / 다음 확인

1. SM-2ER surface range는 SPG-62의 실제 시뮬레이션 geometry 및 radar-horizon 성격의 제약을 받는다. `maxRangeKm:120`은 policy upper bound일 뿐 120 km release 보장값이 아니다.
2. SM-6 160 km 3-seed 접촉은 game fixture 검증이지 통계적 Pk가 아니다. 회피/재밍/고해상도 해상상태/다방위 표적에는 별도 캠페인이 필요하다.
3. surface terminal glide 12° / +12 km / 3 km fade는 `SIM_TUNED`다.
4. AUTO/SEMIAUTO 대수상 발사는 이번에도 활성화하지 않았다.
5. WIP15C에서는 GitHub branch/main/PR/release를 변경하지 않았다.