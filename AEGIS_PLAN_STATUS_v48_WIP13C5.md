# AEGIS v48 WIP13C5 — Live Surface SARH RF Chain

- 기준 파일: `Aegis_SIM_v48_WIP13C4.html`
- 기준 SHA-256: `85e623e3e4aa4a3aace99ae2a0a8b1cafeed37b1703384df27d30900b9321e2e`
- 결과 파일: `Aegis_SIM_v48_WIP13C5.html`
- 결과 SHA-256: `8d461aa383950729fd8a2f81963fd70e3f8bb323ed40d7ebea7a00a421bd96d7`
- 작성일: 2026-09-24
- 상태: SM-2 제한적 대수상 SARH 실발사와 물리 RF 반사·로컬 추적·선체 충돌·표적 피해 경로 구현 및 결정적 회귀 완료

## 결과

WIP13C4의 candidate-only 계약을 실제 SM-2 비행 경로에 연결했다.

1. 운용자가 익명 composite surface track을 `HOSTILE` 또는 `TRAINING_TARGET`으로 수동 지정한다.
2. surface FCQ, VLS 상태, EMCON, SPG-62 mount/sector/terrain LOS와 시간축 예약을 통과해야 발사된다.
3. SPG-62가 익명 track의 측정 공간을 조사한다.
4. 송신 빔과 미사일 수신 빔에 동시에 들어온 실제 RF 반사만 bistatic echo가 된다.
5. SM-2는 echo의 range/angle/Doppler 측정과 로컬 6-state EKF로 종말 유도한다.
6. 실제 미사일 flight segment가 3D hull과 교차할 때만 WIP12F 관통·신관·폭발을 실행한다.
7. 결과 damage packet이 표적함 파괴구·침수구획·화재·종강도 runtime에 한 번만 적용된다.

공중표적 자동교전은 기존대로 유지하며, 수상표적 `AUTO`/`SEMIAUTO`는 계속 금지한다.

## RF 연결

SARH front-end는 표적함 전용 목록을 사용하지 않는다. WIP13A2/A3의 공통 물리 RF 장면을 그대로 사용한다.

| 반사원 | SARH 처리 |
| --- | --- |
| 자함·형상/RCS 보유 수상표적·일반 수상접촉 | aspect/band RCS와 Tx/Rx geometry로 echo 생성 |
| 항공기·ASM·RCS 보유 ordnance | 동일 echo pool에서 경쟁 |
| chaff | 동일 echo pool과 cluster/association에 참여 |
| 지형 | terrain reflector와 독립 Tx/Rx LOS로 반영 |
| 해면 | 분산 sea-clutter cell로 생성되어 SNR·cluster·오획/품질에 영향 |

물리 반사 합성은 SPG-62→반사원 거리와 반사원→미사일 거리의 독립 경로 손실, 송신/수신 빔 이득, bistatic RCS, weather/multipath, bistatic Doppler를 사용한다. `truthRef`, `entityId`, reflector debug kind는 release·association·guidance state로 전달하지 않는다.

이 공통 SARH front-end는 무기명이 아니라 `SARH + assigned illuminator` 조건으로 동작한다. 따라서 다른 SARH profile도 같은 전체 반사원 경로를 사용한다. 이번 단계에서 실제 수상 release를 새로 연 무장은 SM-2뿐이다.

## 실제 발사와 종말

- `spawnMissile()`에서 익명 surface track을 별도 감지하고 `surfaceSm2LiveReleaseGateWip13C5()`를 통과시킨다.
- VLS 탄을 소비하기 전에 SPG-62 예약을 commit하며 소비 실패 시 rollback한다.
- midcourse cue는 익명 track의 측정 상태만 복사한다.
- terminal guidance source는 `SARH_RF_EKF`이며 조사 상실 시 기존 coast/reacquire 상태기를 사용한다.
- 수상 교전의 중간 sea-clearance는 95 m, terminal floor는 1.5 m의 `SIM_TUNED` 값이다.
- 수상 미사일은 공중표적용 Pk/즉사 분기를 통과하지 않는다.
- swept hull collision은 지정 truth object가 아니라 실제 segment상 최초 물리 수상표적을 판정한다.
- 충돌 상대속도를 표적 좌표계로 변환한 뒤 WIP12F `CONTACT_DIRECT_ACTION`과 WIP13A damage consumer를 실행한다.

## 결정적 실비행 결과

8 km `TRAINING_TARGET` fixture, seed `1350501`, 60 Hz fixed tick:

| 항목 | 결과 |
| --- | --- |
| 비행 시간 | 14.4167 s / 865 ticks |
| SPG-62 실제 조사 | 확인 |
| 최대 물리 echo / 검출 measurement | 46 / 45 |
| SARH 최대 confidence | 0.9822 |
| 종말 guidance authority | `SARH_RF_EKF` |
| 선체 최근접 중심거리 | 8.30 m |
| 충돌 속도 | 862.85 m/s |
| 종료 | `SURFACE_TARGET_CONTACT` / `FUZE_AT_CONTACT` |
| 표적 damage source | `SM2_SURFACE_SARH_LIVE` |
| VLS 소비 | SM-2 1발 |

별도 관통 fixture에서는 850 m/s contact가 side shell을 관통하고 파괴구 1, breach 1, 화재 1을 만들며 9개 coarse 침수구획 consumer에 연결되는 것을 확인했다.

## 검증 결과

| 검증 | 결과 |
| --- | --- |
| WIP13C5 전체 RF→SARH→실비행→충돌 전용 회귀 | 19/19 통과 |
| WIP13C4 authority/FCQ/SPG/terminal foundation | 23/23 통과 |
| 기존 함포·moving-world·WIP12F 회귀 | 79/79 통과 |
| 2D/3D 전환 시 함포 frame 불변 | 9/9 통과 |
| 통합 함상 레이더·교차 도메인 track 계약 | 12/12 통과 |
| ARH 해면 clutter·discrete target validation | 14/14 통과 |
| 핵심 self-test | 실패 0 |

총 156개 명시적 회귀 check가 통과했다.

실행 명령:

```text
AEGIS_REPORT_PATH=artifacts/wip13c5-live-sarh-regression.json node tests/surface-missile-wip13c5-live-sarh.cjs
node tests/surface-missile-wip13c4-foundation.cjs Aegis_SIM_v48_WIP13C5.html
node tests/surface-gun-wip13b13-regression.cjs Aegis_SIM_v48_WIP13C5.html
node tests/surface-gun-wip13b15-view-transition-regression.cjs Aegis_SIM_v48_WIP13C5.html
node tests/shipboard-radar-wip13b14-contract.cjs Aegis_SIM_v48_WIP13C5.html
node tests/arh-seeker-wip13b13-regression.cjs Aegis_SIM_v48_WIP13C5.html
```

## 브라우저 확인

`tests/surface-missile-wip13c5-browser.cjs`를 추가해 실제 페이지 로드, WebGL/Three.js renderer, 전용 fixture와 실비행 fixture를 확인하도록 했다. 현재 실행 환경에는 Playwright가 지정한 Chromium과 대체 시스템 브라우저가 없어 브라우저 회귀 자체는 실행하지 못했다. Node VM에서는 전체 HTML script parse, 초기화, core self-test와 전용 실비행 회귀를 완료했다.

## 모델 경계와 다음 단계

- SM-2MR Block IIIA의 정확한 대수상 envelope, SPG-62 waveform, seeker threshold와 terminal logic은 공개되지 않았으므로 `SIM_TUNED_PUBLIC_UNKNOWN`이다.
- 이번 단계의 live surface terminal은 실제 direct hull contact를 닫았다. surface proximity-first earliest-event arbitration은 후속 종말 확장에서 다룬다.
- ESSM Block 2의 실제 `SURFACE_ARH` release·비행·충돌 연결은 다음 `WIP13C6` 범위다. 기존 ARH 전체 RF 반사원 및 해면 오획 방지 front-end는 그대로 재사용한다.
- WIP14A로 유보한 world/ownship frame 및 VFX 잔류 이동 문제는 이번 단계에 섞지 않았다.

## 산출물

- `Aegis_SIM_v48_WIP13C5.html`
- `WIP13C_SURFACE_MISSILE_ENGAGEMENT_PLAN.md`
- `AEGIS_PLAN_STATUS_v48_WIP13C5.md`
- `tests/surface-missile-wip13c5-live-sarh.cjs`
- `tests/surface-missile-wip13c5-browser.cjs`
- `artifacts/wip13c5-live-sarh-regression.json`
- 상속 foundation/gun/view/radar/ARH 회귀 report
- `SHA256SUMS_v48_WIP13C5.txt`
