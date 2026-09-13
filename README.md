# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 안정판

- 시뮬레이터: [`Aegis_SIM_v37.1.html`](Aegis_SIM_v37.1.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v37.1.md`](AEGIS_PLAN_STATUS_v37.1.md)
- GitHub Release: [`v37.1`](../../releases/tag/v37.1)
- HTML SHA-256: `b9faba85b522b2696e2adc7e46479dac4dbeb1d0dc1bbd94f0a1b5e4037b28ca`

## v37.1 핵심 범위

- SPY-1D(V), SPQ-9B, SPS-73 및 시각 센서의 익명 관측·트랙 연관 경계
- A3 식별·위협·교전권한 상태와 MANUAL / SEMIAUTO / AUTO 발사 게이트
- CIWS Closure B1: 관측 트랙 기반 위협 선택, 권한 재검증, 로컬 RF 획득
- CIWS Closure B2: 로컬 속도·가속도·기동 추정과 Phalanx/SeaRAM 예측
- CIWS Closure B3: 부분손상에 따른 센서·구동·발사 성능의 연속 열화
- Phalanx Block 1B 공통 센서: 자체 탐색 15 km, 유효 추적 기준 10 km
- 고정 시간 간격과 고정 seed를 사용한 1× / 8× / 16× 결정성
- 2D/3D 상태 격리와 표시 전용 Three.js 렌더러

## 검증

정식 승격 전 GitHub Actions에서 정적 검사, 시작 자기검사, CIWS B1/B2/B3 Chromium 회귀, 실제 3D 렌더, WebGL probe를 모두 통과한다. 세부 실행 결과와 artifact digest는 상태 문서에 기록한다.

## 개발과 아카이브

루트에는 최신 안정판만 둔다. 이전 WIP와 상태 문서는 [`archive/README.md`](archive/README.md)에서 확인할 수 있다. 다음 기능은 별도 WIP 버전에서 시작한다.
