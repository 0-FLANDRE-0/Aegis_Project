# AEGIS v48 WIP14B1 작업 상태

- 상태: 완료 — `PASS_WITH_BROWSER_ENVIRONMENT_BLOCKED`
- 기준: `Aegis_SIM_v48_WIP14A14.html`
- 결과: `Aegis_SIM_v48_WIP14B1.html`
- Git: 브랜치/커밋/푸시 생성 안 함

## B 단계 번호

| 이전 번호 | 새 번호 | 범위 | 상태 |
|---|---|---|---|
| A15 | B1 | 미사일 onboard INS/GPS own-state 및 DL truth 우회 차단 | 완료 |
| A16 | B2 | 단방향 DL 패킷 지연·손실·순번·age/uncertainty | 대기 |
| A17 | B3 | SM-6 제한형 양방향 DL return/assist | 대기 |
| A18 | B4 | 미사일별 상태형 로프팅 | 대기 |

## B1 변경됨

- 물리 좌표와 미사일 onboard 항법 추정치를 분리
- SM-2MR, SM-2ER, ESSM은 형식별 INS 오차 상태 사용
- SM-6는 0.5초 주기의 SIM_TUNED GPS/INU own-state 보정 사용
- GPS는 미사일 자신의 위치/속도 보정에만 사용하고 표적 좌표 생성에는 사용하지 않음
- DL 수신은 `dlAlive`가 참일 때 복사된 미사일 로컬 스냅샷으로만 갱신
- DL 단절 후 launcher의 live track을 다시 읽는 우회 경로 차단
- SARH/ARH 상대측정은 미사일 onboard 항법 원점으로 재정렬
- PN/APN/ZEM/Kappa/자동조종 및 발사 전이의 own-state 소비자를 onboard 항법 상태로 연결
- 고정 스텝마다 한 번만 DL receive sequence를 갱신하고, 항법 난수는 전투 RNG와 분리

## 변경되지 않음

- A13 공력·추진·질량·형상·WIND basis 동결 계약
- Mk104/Mk72 추진, 기준면적, CN/CY/Cd, 6DOF 계수
- A14 자율/반자율 교전, ready-only VLS 표시, 3D AUTO LOCK/LOCK OFF/FIRE
- AIM-174B는 참고 자료 전용이며 함정 VLS registry에 추가하지 않음
- B1 DL은 의도적으로 0지연 단방향 adapter 상태이며 패킷 transport는 B2에서 구현
- 로프팅 수치와 전이 로직은 B1에서 수정하지 않음

## 180 km / 표적 2 km 로프팅 진단

- 현재 midcourse TGO가 원래 약 150초여도 30초로 제한됨
- SM-2ER TGO weight `0.4044`, 초기 q weight 적용 후 loft demand 상한 `0.1820`
- SM-6 TGO weight `0.3589`, 초기 q weight 적용 후 loft demand 상한 `0.1615`
- 이후 urgency/range/terminal fade/momentum guard가 더 낮출 수 있어 약 2.4 km 저고도 비행 증상과 코드 경로가 일치함
- 수정은 B4에서 SM-2MR/SM-2ER/SM-6/ESSM별 `CLIMB → CRUISE → DIVE/TERMINAL` 상태형 프로파일로 수행

## 검증 상태

- JavaScript syntax / C55 manifest·gzip·SHA / 재패키징: PASS
- Core self-test: 0 failures
- B1 항법·DL hard-cut·상대측정 재정렬·1×/8×/16× 결정성: PASS
- A14 교전/VLS/3D 회귀: PASS
- A13 frozen physical contract hash audit: PASS
- Standard 비행 closure/geometry/stability 및 1×/8×/16×: PASS
- 브라우저 smoke: `BLOCKED_ENVIRONMENT` — Playwright Chromium 실행파일 없음

