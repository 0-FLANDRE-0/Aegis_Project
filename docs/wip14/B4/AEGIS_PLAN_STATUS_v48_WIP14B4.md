# AEGIS v48 WIP14B4 — WIP14 Closeout Status

갱신: 2026-10-01 (KST)

**상태: WIP14 FEATURE SCOPE CLOSED / KNOWN DEFERRED 유지.**

이 판정은 WIP14에서 계획한 onboard navigation, VLS release scheduling, generic weapon-link/return-link, SM-6 GPS/양방향 DL, per-missile stateful loft 구현 범위의 종료를 뜻한다. 실제 무장 최대사거리 인증, 전 조건 명중 보장, 전체 시뮬레이터의 모든 기존 자기검사 PASS를 뜻하지 않는다.

## 원격 기준

- branch: `WIP14`
- 최종 HTML: `Aegis_SIM_v48_WIP14B4.html`
- 크기: `7,319,028 bytes`
- SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- Git blob SHA: `5e454823e4fd8c608d05ecd5e880a13cf5e5b2ce`
- decoded C55 main SHA-256: `62aa1f6e8a4ff9445f3fde2f4d86e581e6457616daada424bf3c8a4164ba186b`
- 사용자가 WIP14에 업로드한 HTML은 로컬 최종 B4와 Git blob 기준 exact 일치 확인.

## WIP14 완료 범위

### B1
- SM-2MR / SM-2ER / SM-6 / ESSM onboard own-navigation과 truth boundary.
- seeker/DL re-anchor 및 DL hard-cut 뒤 truth 재주입 차단.

### B2
- Kh-35U / Kh-32 / RAM까지 generic missile own-navigation 확장.
- ASM passive RF truth boundary 정리.
- 공통 VLS fixed-step release scheduler. 기본 `0.8 s`, profile 설정 `0.6~1.0 s`.

### B3
- generic packet envelope/queue/scheduler, delay/loss/sequence/age/uncertainty.
- return-link를 특정 미사일 전용으로 하드코딩하지 않는 profile capability로 구현.
- SM-6는 첫 활성 profile이며 GPS/INU own-state와 양방향 DL, bounded launcher assistance를 사용.
- return-link가 launch-time support deadline을 연장하지 않는 계약 유지.

### B4
- SM-2MR / SM-2ER / SM-6 / ESSM별 stateful loft.
- `CLIMB → CRUISE/ENERGY-SHELF → DIVE`의 단방향 전이와 DIVE 후 re-loft 금지.
- 게임 검토 범위 MR `160 km`, ER/SM-6 `260 km`; 이는 명중 보장값이나 실제 무장 제원 인증이 아님.
- 대표 fixture에서 MR 160 km와 ER 260 km 고정표적 요격 확인, SM-6 240 km 고정표적은 seed별 성공/미스가 모두 존재.

## 최종 검증 기록

- B4 stage unit: `33/33 PASS`
- B4 runtime: `8/8 PASS`
- B3 transport: `49/49 PASS`
- B3 runtime: `25/25 PASS`
- package/static: `52/52 PASS`
- B2 nav unit: `38/38 PASS`
- VLS timing: `12/12 PASS`
- release policy: `22/22 PASS`
- desktop/mobile-size UI handler: `2/2 PASS`
- MR160 / ER260 / SM-6 초기260 접근 표적의 전체 단계 비행은 1×/8×/16×/64× fixed-step 배치에서 이력 일치.
- B3 GPS/양방향 DL, B2 ASM/RAM own-nav, VLS scheduler, frozen propulsion/aero/mass, cell-exit/fuze/damage authority 보존.
- C55 assets 0–12는 B3와 byte-identical, B3→B4 재생성 exact.

시험 묶음은 일부 하위 fixture를 공유하므로 위 PASS 수를 합산한 고유 테스트 총수는 주장하지 않는다.

## Known Deferred — WIP14 종료를 막지 않고 별도 추적

1. 기존 `V48 WIP13A surface target submergedBreachFloods` core self-test 실패 1건. B3/B4에서 동일하며 WIP14 유도/DL/loft 변경에서 새로 발생한 실패가 아니다. 침수 작업에서 별도 조사한다.
2. 현재 검사 환경은 native file URL이 관리자 정책으로 차단되고 빈 페이지에서도 WebGL/WebGL2 context 생성이 실패했다. 2D/3D FIRE handler는 검사했으나 실제 3D 함체·연기·카메라와 모바일 GPU/FPS는 별도 환경 검증 대상으로 남긴다.
3. SM-6 장거리 고정표적 seed별 미스, ESSM 중장거리 에너지 부족, 저고도 원거리 센서/조명 제한은 포락선/교전조건 연구 항목으로 남긴다. WIP14 종료를 위해 신관·센서 제한을 임의 완화하지 않는다.

## 보존 산출물

- `Aegis_SIM_v48_WIP14B4.html`
- `AEGIS_PLAN_STATUS_v48_WIP14B4.md`
- `SHA256SUMS_v48_WIP14B4.txt`
- `docs/wip14/B4/AEGIS_WIP14B4_REPORT.md`
- `docs/wip14/B4/AEGIS_WIP14B4_VALIDATION_SUMMARY.json`
- `docs/wip14/B4/AEGIS_PLAN_STATUS_v48_WIP14B4.md`
- B1/B2/B3 상태와 WIP14 설계/참고 문서는 `docs/wip14/` 아래 보존.

대화의 `AEGIS_v48_WIP14B4_SUPPORT.zip`은 재생성 도구·대용량 evidence와 스크린샷을 묶은 검증 패키지다. 저장소에는 최종 report/summary/checksum과 상태문서를 보존하며 ZIP 자체는 병합 필수 산출물로 취급하지 않는다.

## 다음 단계

다음 기능 단계는 WIP15로 분리한다. 첫 범위는 현재 3D 외형의 양현 3기씩 SRBOC 구성과 runtime 4기/24발 불일치를 해소하여 **6기 × 6튜브 = 36발**을 canonical layout으로 통일하고, 실제 발사기/tube 위치에서 Mk 214가 발사되도록 정렬하는 작업이다. Nulka active decoy는 그 정합 작업 뒤 별도 하위 단계에서 연결한다.