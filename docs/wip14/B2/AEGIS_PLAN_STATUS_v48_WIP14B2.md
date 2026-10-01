# AEGIS v48 WIP14B2 — Local Candidate / Validation Status

작성: 2026-10-01 (KST)

**상태: 구현·런타임 검증 완료 / WebGL 시각 검증 잔여. B2 전체 CLOSED 아님.**

## 기준과 산출물

- 기준: `Aegis_SIM_v48_WIP14B1.html`
- 기준 SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`
- 로컬 결과: `Aegis_SIM_v48_WIP14B2.html`
- 크기: `7,306,814 bytes`
- 결과 SHA-256: `0aefeadc27f5fc4cd34e076f31bd570eadb5f6fdc950bcf37dc07b5f6cb103da`
- decoded game-main SHA-256: `709a11e5a74361b76694e4cc31f4dbea807e574fa8849b9cc642a05a6d53aaae`

이 문서 업로드는 대형 B2 HTML의 원격 업로드나 main 승격을 의미하지 않는다. HTML은 사용자 업로드 대상이다. 대화에 전달한 지원 ZIP에는 상세 보고서, 실제 evidence JSON, 브라우저 테스트와 exact 재생성 도구가 들어 있다.

## 구현

1. `_onboardNavB2` 공통 missile navigation authority와 무장별 profile. 기존 SAM `_b1Nav`는 같은 객체의 compatibility alias다.
2. Kh-35U/Kh-32 guidance, EKF observer, 거리/방위/고도/phase 판단을 자체 항법 추정치로 연결. physical RF echo synthesis는 별도 observer로 분리하여 항법 오차가 반사파 합성에서 상쇄되지 않게 했다.
3. ASM passive RF는 noisy bearing/confidence/availability만 전달. C52 target-memory와 missile own-state를 분리하고 고정 기억 fixture는 실시간 자함 좌표를 따라가지 않는다.
4. RAM angular RF/IR seeker는 유지하며 PN flight-vector projection과 sea-clearance에 추정 속도·고도를 사용한다. 장거리 절대 표적 기억을 새로 부여하지 않았다.
5. ship-owned `weapons.vlsReleaseB2` 공통 fixed-step release gate. 기본 0.8초, 설정 0.6~1.0초. 첫 준비된 발은 즉시 발사하고 연속 실제 발사 사이를 제한한다. MANUAL/3D 쿨다운 입력은 거부, AUTO pending은 기다린다. 실제 발사 때 기존 권한/FCQ/재고/손상/EMCON 정책과 필요한 SPG 지원을 재검사한다.

새 nav/고도 채널 보조와 cadence 계수는 `SIM_TUNED` 게임 가정이다. B1과 같은 error-state sensor emulator이며 완전한 strapdown INS 또는 실제 무장 hardware 성능 검증이 아니다.

## 검증

| 항목 | 결과 |
| --- | --- |
| 최종 core self-test | 실패 0 |
| 정적 경계/호출 검사 | 16/16 PASS |
| 분리 항법·시커·RAM 경계 단위검사 | 38/38 PASS |
| 4종 VLS × 0.6/0.8/1.0초 | 12/12 PASS |
| 발사 거부 및 기존 EMCON 정책 | 22/22 PASS: 거부 19, AUTO_RADIATE 유지 3 |
| AUTO 대기/취소, 혼합 무장, 배속, 상태 보존 등 | 10/10 PASS |
| B1 nav 수치·상대측정·DL hard-cut | 비교 일치 |
| SM-2MR/ER/SM-6 대표 비행, 동결 물리, 셀 이탈 | 비교 일치 |
| ASM 120초 1×/8×/16×/64× 고정 틱 실행 | 상태 일치 |
| 데스크톱/모바일 Chromium 2D 및 3D FIRE 조작 | PASS |
| C55 14개 manifest/gzip/SHA/JavaScript syntax | PASS |
| C55 records 0–12 | B1 byte-identical |
| 원본 B1에서 B2 재생성 | 최종 HTML byte-identical |
| WebGL 함체·연기·카메라 시각 검증 | BLOCKED_ENVIRONMENT |

대표 release steps: `0 → 48 → 96` = `0 → 0.8 → 1.6 s`. 혼합 무장도 SM-6 0, ESSM 48, SM-2ER 96, SM-2MR 144로 공통 clock을 사용했다. 기존 0.35초 요청 시점에서는 pending을 보존하며, 대기 중 FRIEND로 변경되면 추가 탄약 소모 없이 취소했다.

## 한계와 보존

Chromium 관리 정책이 native local-file/URL navigation을 차단하여 전체 packaged HTML을 `set_content`로 실행했다. 빈 페이지에서도 WebGL context 생성 실패가 재현되었다. 3D 버튼의 실제 release 경로는 검사했지만 3D 함체/연기/카메라 렌더링은 검증하지 못했다. 실제 모바일 GPU/FPS도 미검증이다.

SAM 공력·추진·질량 동결값, VLS loadout 수량, WIP156 in-cell 물리, 종말 피해 권위는 보존했다. 새 항법/진단의 combat RNG 비소비는 검사했다. 단, 정상 ASM의 target-memory drift는 독립 hash로 이전했으므로 이전 ASM combat RNG 소비 순서와 전체 교전 결과까지 B1과 같다고 주장하지 않는다.

기존 자기검사의 완전한 속도축 가정과 INS 오차 크기의 단조 증가 가정을 고쳤다. RAM 정적 검사는 실제 위임 helper를 검사하고, 순간이동 fixture에는 명시적인 항법 샘플 진행을 넣었다. 생산 SAM 물리 튜닝을 바꿔 검사를 맞춘 것이 아니다.

SM-6 초기 비교 차이는 미사일 seed만 고정하고 해역/날씨를 다르게 둔 시험 문제였다. 해역 seed 142000까지 통일한 최종 비교에서 Standard 3종 결과가 일치했다. ESSM은 기존 80km Standard probe 대신 15km 관측 fixture로 검사했고 생산 NEZ gate를 약화시키지 않았다.

## 다음 작업

B2 WebGL 시각 검증과 사용자 HTML 원격 업로드 확인 후 B3 범용 weapon-link transport를 진행한다. SM-6는 return-link의 첫 활성 profile이며 core 전용 제한이 아니다. B4 stateful loft는 그대로 별도 단계다. 최신 단계 번호는 `WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md`의 B2→B3→B4를 따르며 이전 handoff의 B3 흡수/SM-6-only 문구는 역사 기록이다.

main/PR/merge/release/tag와 원격 runtime 기준은 이 문서 추가로 변경하지 않는다.
