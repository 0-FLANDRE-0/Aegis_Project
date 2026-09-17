# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP11B.html`](Aegis_SIM_v48_WIP11B.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP11B.md`](AEGIS_PLAN_STATUS_v48_WIP11B.md)
- HTML SHA-256: `93084bb9b0d9a72f0544b244a5ced6f314fb37a224f18f5739163fd10ed3db62`
- 상태: WIP — 정식 release/tag가 아님

## WIP11B 핵심 범위

- 활성 자함 `destroyShipRuntime()` 우회 옵션 제거 및 무조건 삭제 거부
- 작전 snapshot을 복제한 뒤 7개 codec 전체를 preflight하고, 통과한 입력만 적용
- 거부된 import의 자함·월드·교전 transient 상태 zero-mutation 보장
- `profileRevision` 명시 호환성 검사와 비호환 revision의 migration 요구
- export snapshot을 live 승조원·침수 캐시와 완전히 분리
- WIP11A 소유권 구조와 WIP11 전투·재질·관통·형상 결과 보존

## 검증

- 정적 계약 6종과 HTML JavaScript 문법 검사 통과
- Playwright 전체 `17/17 PASS`
- 잘못된 revision/VLS/재고/침수/승조원/항법 snapshot 6종 모두 거부 및 상태 지문 exact 일치
- WIP11A 동일 seed CIWS·충돌/관통 결과 exact 일치
- WebGL 6시점·후방 형상·구명뗏목·2D 도면 검사 통과
- GitHub Actions는 WIP11B 안전성 job을 포함해 총 `18`개 job으로 구성

## 다음 단계

- WIP12: 저구경탄·함포탄, 신관, 도탄, 관통, 파편, 폭발과 입·출구 파괴구
- WIP13: 해상사격 FCS
- WIP14: 간단한 표적함과 복수 함선 프로파일

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며, WIP10·WIP11·WIP11A는 각각의 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
