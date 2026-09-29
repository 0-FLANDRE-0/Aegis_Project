# AEGIS v48 WIP14B1 — Onboard navigation / datalink truth boundary

## 결과

**PASS_WITH_BROWSER_ENVIRONMENT_BLOCKED**

B1은 미사일이 시뮬레이션의 물리 좌표를 유도용으로 그대로 아는 구조를 제거했다. 물리 truth는 운동 적분, RF 측정 합성, 충돌·신관, 진단 비교에만 남기고, 미사일 유도는 형식별 onboard 항법 추정치를 사용한다. DL이 끊긴 뒤 launcher의 현재 전역 track을 다시 읽던 우회 경로도 차단했다.

브랜치, 커밋, 푸시는 생성하지 않았다.

## 형식별 onboard 항법

| 미사일 | B1 항법 프로파일 | GPS aid | 동작 |
|---|---|---:|---|
| SM-2MR Block IIIA | `SM2MR_INS_B1` | 없음 | 초기 위치·속도 오차와 IMU bias/noise가 고정 스텝에서 누적 |
| SM-2ER Block IV | `SM2ER_INS_B1` | 없음 | ER 전용 INS 오차 계수 사용 |
| SM-6 Block IA | `SM6_GPS_INU_B1` | 0.5 s | GPS가 own position/velocity 오차만 제한 |
| ESSM Block 2 | `ESSM_INS_B1` | 없음 | 단거리용 별도 INS 오차 계수 사용 |

오차는 미사일 ID, 시뮬레이션 seed, 고정 스텝으로 결정되며 전투/시커 RNG를 소비하지 않는다. GPS fix도 SIM_TUNED 오차를 가진다. GPS가 표적 위치나 완전한 자체 truth를 제공하지 않는다.

## Truth 사용 경계

| 영역 | 물리 truth 사용 | 유도용 onboard state 사용 |
|---|---:|---:|
| 운동·공력·추진 적분 | 예 | 아니오 |
| RF echo/상대측정 합성 | 예 | 측정 결과를 onboard 원점에 재정렬 |
| 충돌·근접신관 | 예 | 아니오 |
| PN/APN/ZEM/Kappa | 아니오 | 예 |
| PIP/range/TGO/발사 전이 | 아니오 | 예 |
| 자동조종 명령 변환 | 아니오 | 예 |
| 진단 오차 비교 | 예 | 예 |

SARH/ARH는 물리적인 상대거리·상대속도를 측정할 수 있으므로 RF 합성 경계에서는 truth를 사용한다. 하지만 측정으로 만든 절대 표적 상태는 미사일의 오차가 포함된 onboard 위치/속도에 다시 붙는다. 따라서 정확한 물리 좌표가 유도로 역류하지 않는다.

## B1 datalink 경계

- Launcher track은 `dlAlive=true`일 때만 복사된 `B1_DL_RX` 스냅샷이 된다.
- 같은 고정 스텝에서 여러 유도 소비자가 조회해도 receive sequence는 한 번만 증가한다.
- DL hard cut 이후 live global track 변화는 수신 스냅샷을 갱신하지 않는다.
- 단절 직후에는 마지막 로컬 수신 상태, 이후에는 IOG memory/시커 상태가 유도 연속성을 담당한다.
- B1은 transport를 추가하지 않은 의도적인 zero-latency one-way adapter다. 지연, jitter, 손실, 순번 거부, packet age와 uncertainty 증가는 B2 범위다.

DL 단절 픽스처에서는 launcher 원본 track을 약 `311,276 m` 이동시켰지만 미사일 유도 큐 이동은 `0 m`였다. 새 receive sequence도 생성되지 않았다.

## 예시 공대공 HTML에서 반영한 설계 원칙

검토한 예시는 다음 구조를 분명히 분리하고 있었다.

1. 물리 truth와 error-bearing INS/GPS own-state
2. 송신·도착시각, 순번, 지연, 손실을 가진 단방향 packet transport
3. 미사일 onboard nav/uncertainty를 반환하는 제한형 양방향 link
4. `CLIMB → CRUISE → DIVE`로만 진행하고 DIVE 후 재로프트를 금지하는 stateful corridor

B1에는 1번과 DL hard boundary만 적용했다. 2번은 B2, 3번은 SM-6 한정 B3, 4번은 함대공 미사일별 B4로 분리했다. 공대공 수치나 AIM-174B 프로파일을 함정 VLS에 그대로 복사하지 않았다.

## 180 km / 2 km 표적 로프팅 원인

현재 로프팅은 미사일 형식별 registry가 이미 존재하지만, 상태형 전이보다 매 프레임 계산되는 연속 weight에 크게 의존한다. 장거리 저고도 사례에서 핵심 병목은 midcourse의 `tgoEst = clamp(rawTgo, 0.1, 30)`이다.

| 미사일 | 원래 TGO | 사용 TGO | TGO weight | 초기 q 적용 후 demand 상한 | guard 전 유도고도 |
|---|---:|---:|---:|---:|---:|
| SM-2ER | 150 s | 30 s | 0.4044 | 0.1820 | 약 4.27 km |
| SM-6 | 150 s | 30 s | 0.3589 | 0.1615 | 약 4.10 km |

여기에 urgency, range weight, terminal fade, momentum guard가 추가로 작용한다. 따라서 사용자 관측의 약 2.4 km apex와 미도달 현상은 코드상 충분히 재현 가능한 경로다. B1에서는 원인만 고정 진단으로 남겼고, 로프팅/공력값은 변경하지 않았다.

## B4 로프팅 분리 원칙

공통 엔진은 공유하되 프로파일과 상태 전이는 형식별로 분리해야 한다.

| 미사일 | 예정된 프로파일 성격 |
|---|---|
| SM-2MR | 중거리·SARH 지원시간을 고려한 완만한 climb/cruise와 이른 terminal 수렴 |
| SM-2ER | booster와 장거리 에너지 회랑을 이용하는 높은 cruise, SARH 종말 전이 |
| SM-6 | 더 긴 에너지 shelf, GPS/INU 및 ARH handoff를 고려한 늦은 terminal 수렴 |
| ESSM | direct/mild loft 중심, 장거리 Standard 로프트를 공유하지 않음 |

각 프로파일은 최소한 latched corridor, phase hysteresis, DIVE 이후 재로프트 금지, 형식별 terminal release 조건을 가져야 한다. 공통 30초 TGO 제한을 그대로 로프트 authority에 쓰지 않는다.

## 회귀 및 동결 검증

- Core self-test: `0` failures
- B1 contract/nav/reanchor/DL cut/loft diagnosis: PASS
- onboard nav 1×/8×/16×: exact fixed-step determinism PASS
- SM-6 90초 GPS/INU: 180 fixes, 최종 위치 오차 약 `3.84 m`
- SM-2ER 90초 INS: 위치 오차 약 `9.92 → 26.70 m`
- A14 AUTO/SEMIAUTO 실제 발사, ready-only VLS, 3D 단축조작: PASS
- FRIEND/NEUTRAL 발사 차단: PASS
- A13 공력·추진·질량·형상·WIND basis frozen hash: 모두 exact PASS
- Standard closure/geometry/stability: SM-2MR/SM-2ER/SM-6 모두 PASS
- 물리 fixed-step 1×/8×/16×: PASS
- C55 records 0–12: A14와 byte-identical
- C55 record 13/manifest/gzip/SHA 및 재패키징: PASS

항법 오차가 실제 유도 입력이 되었으므로 A14와 비행 trace fingerprint는 의도대로 바뀐다. frozen 물리 hash는 그대로이며 peak Mach 변화는 SM-2MR `-0.00020`, SM-2ER `-0.00186`, SM-6 `+0.00540` 이내였다.

## 브라우저 검증

Playwright 모듈은 있었지만 지정 Chromium 실행파일이 존재하지 않아 실제 Chromium/WebGL smoke test는 실행하지 못했다. 이를 PASS로 표기하지 않고 `BLOCKED_ENVIRONMENT`로 기록했다. DOM/C55 초기화와 런타임 자기진단은 Node VM에서 전부 실행했다.

## 파일 해시

- `Aegis_SIM_v48_WIP14B1.html`: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`
- `source14b1.js`: `dcec641772f3e9e3324ad1e43403fd1c70b661b692ff2c3edd85dceeee1b03d9`

## 남은 범위

- B2: 단방향 DL packet delay/jitter/loss/sequence/age/uncertainty
- B3: SM-6 limited return packet과 bounded launcher guidance assistance
- B4: 미사일별 stateful loft corridor 및 180 km / 2 km 실제 교전 회귀
- Chromium이 있는 환경에서 3D UI 시각·클릭 smoke test

