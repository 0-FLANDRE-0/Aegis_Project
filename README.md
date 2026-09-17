# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP11A.html`](Aegis_SIM_v48_WIP11A.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP11A.md`](AEGIS_PLAN_STATUS_v48_WIP11A.md)
- HTML SHA-256: `d18981ca9db5a525417020e5501dce3c638e27cdc97de0f3558fba2e455b1b7a`
- 상태: WIP — 정식 release/tag가 아님

## WIP11A 핵심 범위

- immutable `ShipProfile`과 mutable `ShipRuntime`의 소유권 경계 확정
- 자함 상태를 `ACTIVE_SHIP_RUNTIME` 아래에 묶고 월드 상태는 `ENGAGEMENT_RUNTIME`이 소유
- `aircraft`를 `ownshipReference` 호환 별칭으로 격리
- WIP199 함체 형상을 `CANONICAL_SHIP_EXTERNAL_GEOMETRY`로 직접 소비하고 옛 형상 지층은 진단 fixture로 분류
- 함선·센서·무기 registry 공통 조회 facade
- `reset / spawn / destroy / export / import / enterCombat` lifecycle·작전 snapshot 계약
- 기본 비활성 subsystem profiler와 60 Hz/120 Hz 업데이트 권한 명세
- WIP11 재질·관통·질량·형상 및 모든 전투 결과 보존

## 검증

- 정적 계약 6종과 HTML JavaScript 문법 검사 통과
- Playwright 전체 `17/17 PASS`
- WIP11 동일 seed CIWS·충돌/관통 결과 exact 일치
- WebGL 6시점·후방 형상·구명뗏목·2D 도면 검사 통과
- GitHub Actions는 WIP11A 전용 job을 더해 총 `18`개 job으로 구성

## 다음 단계

- WIP12: 저구경탄·함포탄, 신관, 도탄, 관통, 파편, 폭발과 입·출구 파괴구
- WIP13: 해상사격 FCS
- WIP14: 간단한 표적함과 복수 함선 프로파일

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며, WIP10과 WIP11은 각각 [`archive/v48/WIP10/`](archive/v48/WIP10/), [`archive/v48/WIP11/`](archive/v48/WIP11/)에 바이트 단위로 보존한다.
