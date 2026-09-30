# AEGIS v48 WIP14 — Branch / Handoff Status

갱신: 2026-10-01 (KST)

## 현재 판정

**B3 로컬 구현·전용 검증 통과 / 기존 core 실패 1건 및 WebGL 시각 검증 잔여 / 전체 CLOSED 아님.**

- 로컬 결과: `Aegis_SIM_v48_WIP14B3.html`
- 크기: `7,317,076 bytes`
- SHA-256: `c6a75f9f2c03e925ec298d0cb5885fa9b043c066aeb62117cf4674ec0c313123`
- decoded main SHA-256: `e15323d58d82af8c707b0ef4b7b24b1e2aaade82a39a2def3d73b7a3127dd71b`
- 상세 상태: `docs/wip14/B3/AEGIS_PLAN_STATUS_v48_WIP14B3.md`
- 상세 보고서, evidence JSON, 재생성 도구, 테스트와 체크섬은 대화의 B3 지원 ZIP에 포함.

이번 작업은 대형 HTML을 원격에 업로드하지 않았다. 사용자 업로드 뒤 해당 파일 해시를 대조하고 원격 산출물 기준을 별도로 정리한다. 이 상태 문서 갱신만으로 main/runtime 기준/정식 release를 승격하지 않는다.

## 원격 기준 기록

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 작업 branch: `WIP14`
- 분기 기준 main commit: `a8d14e3484200098be2143e0547c8e922642c042`
- 분기 기준 tree: `92caa0163006e916d98b422440deb80f5cd0d9eb`
- 기존 원격 기준 기록: `Aegis_SIM_v48_WIP13C22.html`

## B3 구현 범위

- 범용 `WEAPON_LINK_B3` packet envelope/queue/scheduler. 방향별 cadence, delay, jitter, loss, out-of-order, TTL와 payload capability를 profile에서 설정한다.
- 현재 SM-6 profile만 return/assistance 활성. 다른 무장도 같은 core를 사용하며 실제 비-SM-6 test profile의 return 활성화를 검증했다. ASM/RAM의 실제 DL 운용은 새로 활성화하지 않았다.
- launcher 송신은 관측 track 추정치만 복사한다. 시커/유도 getter는 live launcher track을 다시 읽거나 전송을 진행하지 않는다.
- return packet은 B2 `_onboardNavB2`의 추정 위치/속도와 추정 불확실성, phase/health를 보낸다. raw physical state와 진단용 truth-error ledger는 제외한다.
- GPS/INU 보정 수식은 B2 보존. GPS는 자기 INS 위치·속도 오차만 보정하며 표적 좌표를 생성하지 않는다. GPS, uplink, downlink 중단/복구는 독립이다.
- support deadline은 launch-time plan에 고정하고 return이 연장하지 못한다. 영구 hard-cut/deadline은 대기 패킷을 폐기한다. BDA 임시 지원 보류는 별도 suspend이며 원래 deadline 안에서만 재개할 수 있다.
- alias 변경은 epoch 재결속과 이전 queue 폐기로 처리하며 deadline은 유지한다.
- bounded assistance는 수신한 onboard state와 launcher track으로 만든 제한된 기존 PIP/Kappa TGO advisory다. confidence/freshness/cap을 적용하고 SARH/ARH 및 terminal 권위를 덮지 않는다. 새 B4 loft 상태기계는 추가하지 않았다.
- DEBUG 페이지의 read-only TX/RX/age/GPS/fix telemetry 추가.

전송·항법 오차·송신주기·지원시간 정책의 신규 수치는 모두 SIM_TUNED 게임 모델이며 실제 무장 통신 규격 또는 공개 성능값으로 취급하지 않는다.

## 실제 검증

- Pure transport 49/49 PASS.
- Packaged Chromium runtime 25/25 PASS; JavaScript page error 0.
- Package/static 41/41 PASS; C55 14개 manifest/gzip/SHA/구문 검사, asset records 0–12 B2 byte-identical.
- B2 nav unit 38/38, VLS timing 12/12, release policy 22/22 PASS.
- 데스크톱/모바일 크기의 2D/3D FIRE handler 및 cooldown/UI 표시 2/2 PASS.
- 명시적 60Hz uplink/zero-delay/zero-loss/return-off/assistance-off 비교 profile에서 4종 요격탄의 B2 대비 위치·속도 차이는 1e-6 SI 허용오차 안. 기본 B3 latency/assistance 설정에서 비행 trace exact를 요구하거나 주장하지 않는다.
- ASM/RAM 항법, RAM 분리 비행, frozen physical contract 및 기존 cell-exit 비교 보존.
- 같은 seed의 90초 SM-6 항법 fixture: GPS on 180 fixes/위치 오차 약 2.9055m, off 0 fixes/약 20.9458m. 이는 테스트 입력과 SIM_TUNED 계수의 결과이며 실제 SM-6 정확도가 아니다.
- B2 원본과 지원 패치로 B3 재생성 후 최종 HTML byte-identical 확인.

검사 그룹은 일부 같은 하위 fixture를 공유하므로 개수를 합산한 고유 테스트 총수를 주장하지 않는다. 1×/8×/16×/64× 비교는 고정 틱 packet/flight fixture 기준이며 실기기 FPS 인증이 아니다.

## 미해결 / 검증 제한

1. seed 142000 clean boot에서 **B2 원본과 B3 모두** `V48 WIP13A surface target submergedBreachFloods` 자기검사 1건이 실패한다. 20초 fixture의 유입/침수량은 두 버전 모두 0이다. 과거 B2의 core failure 0 기록을 이 조건에서 재현하지 못했으며 원인은 확정하지 않았다. 검사를 삭제하거나 침수 물리를 변경해 숨기지 않았다.
2. Native file URL 접근은 Chromium administrator 정책으로 차단되어 전체 HTML을 `set_content`로 실행했다. 빈 페이지에서도 WebGL/WebGL2 context 생성 실패가 재현된다. 함체·연기·카메라의 3D 시각 검사와 실제 모바일 GPU/FPS는 미검증이다. 3D FIRE handler 통과를 WebGL 시각 통과로 표기하지 않는다.

따라서 전용 B3 검증 통과와 전체 프로젝트 CLOSED를 구분한다.

## 보존한 B2 / B1 기록

- B2 HTML SHA-256: `0aefeadc27f5fc4cd34e076f31bd570eadb5f6fdc950bcf37dc07b5f6cb103da`, `7,306,814 bytes`.
- B2 decoded main: `709a11e5a74361b76694e4cc31f4dbea807e574fa8849b9cc642a05a6d53aaae`.
- B2 상태: `docs/wip14/B2/AEGIS_PLAN_STATUS_v48_WIP14B2.md`. 원래 검증 기록은 덮어쓰지 않으며 위 clean-boot 재검사 결과를 최신 한정사항으로 함께 읽는다.
- B2의 generic own-nav, ASM/RAM 수정, VLS ship-wide 0.8초 기본 cadence/0.6~1.0초 설정, 발사 거부 시 탄약 비소모 계약 보존.
- B1 HTML SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`, `7,295,398 bytes`.
- B1 원래 상태/report/evidence/checksum과 own-nav coverage audit는 `docs/wip14/B1/`에 보존.

## 이후 순서

- B3 잔여: 기존 침수 자기검사 원인 확인, WebGL 가능한 환경의 시각 smoke, 사용자 원격 HTML 업로드 해시 확인.
- 다음 기능 단계 B4: SM-2MR/SM-2ER/SM-6/ESSM별 stateful loft 및 180km/2km 회귀. 기존 번호와 범위를 유지한다.
- 최신 계약은 `docs/wip14/WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md`의 B2 → B3 → B4다. 예전 handoff의 B3 흡수/SM-6-only 문구를 신규 계획으로 사용하지 않는다.

## 참고 / 변경하지 않은 것

`docs/wip14/WIP14_REFERENCE_NOTES.md`와 `references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`은 설계 참고본이다.

main, PR, merge, release/tag, 원격 runtime HTML, B4 loft, 공력·추진·질량 튜닝, VLS loadout 수량 및 AIM-174B 운용 등록은 이번 작업에서 변경하지 않았다.
