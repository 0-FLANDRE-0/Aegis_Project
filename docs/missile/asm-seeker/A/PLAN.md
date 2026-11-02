# ASM_SEEKER_A 사전 고정 계획

## 기준과 시간 상한

- 기준 commit: `e10b1bdf8822655d3b9d5c29491161e5e24ee203`
- 기준 HTML: `Aegis_SIM_v48_WIP_TRACK_C.html`
- 기준 HTML SHA-256: `3f2af4c1e18ef30ce4b8dfe4cc2b28f2b91cf96c62306e8f9c55df4a8c508c81`
- 기준 main JS SHA-256: `b036ce98279685c884896b918f9fc05f26b2980811c05e3eed39b25016d5827f`
- 작업 브랜치: `asm-seeker-a`
- S0+S1 벽시계 상한: 첫 계획 기록부터 3시간. 상한에 도달하면 증거를 보존하고 멈춘다.
- S2+S3는 S1에서 Confirmed 코드 결함이 있을 때만 자동 시작하며 별도 3시간 상한을 쓴다.

## 불변 조건

실제 물체 ID·소속은 사후 진단에만 쓴다. 시커·유도에는 cue/basket과 센서 측정만 입력한다. Pd, 잡음, RCS, 빔폭, 탐색 구역, gimbal, 유도 이득, 추진, 피해 계수는 결과에 맞춰 바꾸지 않는다. Harpoon 값을 다른 기종에 복사하지 않는다. 진단 ON/OFF는 native final, RNG, tick을 정확히 보존해야 한다.

## S0

live packed JS에서 `ASM_PROFILES`, `ASM_SEEKER_PROFILES`, 모든 발사·스폰 경로와 공용 WIP22 시커 상태기계를 열거한다. 제품 코드 변경은 없다.

## S1 고정 시험

### A. Kh-35U 다중 함정 재현

- 표적함과 자함의 시커 관측 방위 차이: `0, 5, 10, 20, 40°`
- 발사 거리: `20 km`, `45 km`
- 시드: `519000..519009`
- 총 100회. 두 함 모두 ±28° 탐색 구역 안에 들어가는 경우와 40° 바깥 대조군을 포함한다.
- 지표: SEARCH↔ACQUIRE 전이, 첫 후보/첫 TRACK 시각·거리, 측정 후보 UID 교체, acquire hit 연속성, body yaw/velocity heading/조향 명령 반전.

### B. TRACK-C 이탈 재현

TRACK-C 통계 raw의 qualified egress 전부를 원 제품과 같은 시드·시나리오로 재실행한다. 최초 분기 시점에서 `DAMAGE_DEGRADED`, `MULTI_TARGET_ALTERNATION`, `GATE_REJECT`, `NO_ECHO`, `DECOY`, `GEOMETRY_OVERSHOOT`, `STATE_MACHINE_DEFECT`, `COORDINATE_DEFECT`, `OTHER`로 분류한다. 가까운 truth를 원인으로 추정하지 않고, 실제 RF 후보·거부·상태·조향 이벤트를 연결한다.

### C. 다른 기종

S0에서 확인된 각 시커 탑재 ASM에 대해 단일 표적 및 자함+표적함 기본 기하를 시드 `519100..519109`로 각각 10회 수행한다.

## 판정

Confirmed 코드 결함만 최소 수정한다. 정당한 피격 저하·기만·가림·클러터·SNR·기동 한계 실패는 유지한다. 결함이 없거나 계수 문제만 남으면 S1 보고 후 멈춘다. 수정하면 같은 행렬과 회귀를 S3에서 실행하고, 무표적 해역의 강제 TRACK/명중이 0인지 확인한다.
