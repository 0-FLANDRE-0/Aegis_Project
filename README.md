# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP11.html`](Aegis_SIM_v48_WIP11.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP11.md`](AEGIS_PLAN_STATUS_v48_WIP11.md)
- HTML SHA-256: `38acac296e67541a9fb6c9b6166f638aac407d73fb63221fe7064b8c9dadfb8a`
- 상태: WIP — 정식 release/tag가 아님

## WIP11 핵심 범위

- 후방 VLS 양옆 구명뗏목 캐니스터 6개를 명시적 크래들 위에 접지
- HSLA-80, DH36, AH36, Grade A steel, aramid 공통 재질표
- 외판·갑판·격벽·문·구조재의 `SIM_TUNED` 두께와 구조 계수
- 동일 재질/두께 장부에서 구조 질량과 관통 저항을 함께 산출
- 수상/수중 외판 고정 저항 상수를 실제 관통 경로에서 제거
- CIC, 탄약고/VLS, 조타·케이블 구역 국부 방호
- 아라미드의 대형 관통 저항 기여는 0으로 유지하고 파편/후면 스폴만 감쇠
- WIP10 전투·센서·질량·GM·후방 형상 계약 보존

## 검증

정적 계약, 시작 자기검사, 결정적 Chromium 회귀, 실제 WebGL 형상·구명뗏목 접지 검사와 WIP10 전환 비교를 수행한다. 세부 수치와 GitHub Actions 결과는 WIP11 상태 문서에 기록한다.

## 다음 단계

- WIP12: 저구경탄·함포탄, 신관, 도탄, 관통, 파편, 폭발과 입·출구 파괴구
- WIP13: 해상사격 FCS
- WIP14: 간단한 표적함과 복수 함선 프로파일

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며, 직전 WIP는 [`archive/v48/WIP10/`](archive/v48/WIP10/)에 바이트 단위로 보존한다.
