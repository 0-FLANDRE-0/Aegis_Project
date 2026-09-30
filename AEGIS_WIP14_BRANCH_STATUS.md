# AEGIS v48 WIP14 — Branch / Handoff Status

갱신: 2026-10-01 (KST)

## 현재 판정

**B2 로컬 구현·런타임 검증 완료 / WebGL 시각 검증 잔여. B2 전체 CLOSED 아님.**

- 로컬 결과: `Aegis_SIM_v48_WIP14B2.html`
- 크기: `7,306,814 bytes`
- SHA-256: `0aefeadc27f5fc4cd34e076f31bd570eadb5f6fdc950bcf37dc07b5f6cb103da`
- decoded game-main SHA-256: `709a11e5a74361b76694e4cc31f4dbea807e574fa8849b9cc642a05a6d53aaae`
- 상세 상태: `docs/wip14/B2/AEGIS_PLAN_STATUS_v48_WIP14B2.md`
- 상세 보고서·evidence·재생성 도구·브라우저 테스트는 대화의 B2 지원 ZIP에 포함.

대형 HTML은 아직 이 브랜치에 올리지 않았다. 사용자가 WIP14에 업로드하면 실제 파일 해시를 확인한 뒤 README·고정 지침·테스트/체크섬을 원격 산출물과 함께 정리한다. 이 문서 추가만으로 main/runtime 기준/정식 release가 승격되지 않는다.

## 원격 기준

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 작업 branch: `WIP14`
- 분기 기준 main commit: `a8d14e3484200098be2143e0547c8e922642c042`
- 분기 기준 tree: `92caa0163006e916d98b422440deb80f5cd0d9eb`
- 원격 기준 HTML: `Aegis_SIM_v48_WIP13C22.html`

## B2 구현과 검증 범위

- generic missile own-navigation adapter/profile에 SM-2MR/ER/SM-6/ESSM 및 Kh-35U/Kh-32/RAM 연결.
- ASM guidance와 EKF observer는 항법 추정치를 사용. 실제 RF 합성은 별도 physical observer 사용.
- C52 target-memory와 own-navigation 분리. passive RF는 noisy bearing/confidence/availability를 전달.
- RAM angular RF/IR 체계는 유지하고 PN/sea-clearance만 error-bearing own-state로 연결.
- 공통 ship-owned fixed-step VLS release gate. 첫 준비된 발은 즉시, 연속 발사 사이 기본 0.8초. 0.6~1.0초 설정 가능.
- MANUAL/3D 쿨다운 요청은 거부, AUTO pending은 대기. 실제 발사 때 기존 권한·FCQ·재고·손상·EMCON 정책과 필요한 SPG 지원 재확인.
- core failure 0; static 16/16; nav/boundary units 38/38; VLS timing 12/12; release policy 22/22; integration 10/10 PASS.
- B1 nav 수치, re-anchor, DL cut, Standard 3종 대표 비행, frozen physical hashes, WIP156 cell-exit 비교 일치.
- ASM 120초 1×/8×/16×/64× fixed-step 결과 일치. 데스크톱/모바일 Chromium의 2D/3D FIRE 조작 통과.
- C55 14 records 검증, records 0–12 byte-identical, B1→B2 재생성 exact.

Chromium native URL 접근은 환경 정책으로 차단되어 전체 HTML을 set_content로 실행했다. 빈 페이지에서도 WebGL context 생성에 실패하므로 함체·연기·카메라의 실제 3D 렌더링 및 실기기 모바일 성능은 미검증이다. 새 nav/altitude-aid/cadence 계수는 SIM_TUNED 게임 가정이다.

## B1 보존 기준

- 후보 HTML: `Aegis_SIM_v48_WIP14B1.html`
- 크기: `7,295,398 bytes`
- SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`
- 지원 ZIP SHA-256: `15a82f1dd712faa46cdea9330761df6e5bf25a6b5e1947e268274f64f941aa5e`
- SM-2MR/SM-2ER/SM-6/ESSM의 onboard INS/GPS, seeker/DL re-anchor, DL hard-cut 및 A14 회귀.
- 당시 정적·결정적 검사 통과, Chromium 실행파일 부재로 browser smoke 미실행.
- B1 원래 상태/report/evidence/checksum은 `docs/wip14/B1/`에 보존.
- 추가 own-state 감사: `docs/wip14/B1/AEGIS_WIP14B1_OWN_NAV_COVERAGE_AUDIT.md`.

B1의 ASM/RAM coverage gap을 B2에서 수정했지만 B1 과거 기록은 덮어쓰지 않는다. ASM 전체 교전 trace의 B1 exact parity는 요구하지 않는다. target-memory drift를 독립 hash로 옮겨 과거 ASM combat RNG 소비 순서도 달라질 수 있으며 신규 항법/진단 자체의 combat RNG 비소비는 별도로 검사했다.

## 이후 순서

1. **B2 잔여:** WebGL 가능한 환경의 시각 smoke 및 사용자가 올린 대형 HTML 원격 해시 확인.
2. **B3a:** generic packet envelope/queue/scheduler, uplink delay/loss/sequence/age/uncertainty.
3. **B3b:** generic return-link capability. 미사일별 enable/payload/cadence/delay/loss/TTL; 현재 첫 활성 profile만 SM-6.
4. **B3c:** profile-bounded assistance, deadline/link-cut 및 결정성 회귀.
5. **B4:** 기존 번호 유지. SM-2MR/SM-2ER/SM-6/ESSM별 stateful loft 및 180 km/2 km 회귀.

최신 계약은 `docs/wip14/WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md`의 **B2 → B3 → B4**다. 고정 지침의 이전 handoff에 남은 B3 흡수/SM-6-only 문구를 새 계획으로 사용하지 않는다. README/고정 지침의 원격 산출물 기준 갱신은 사용자 HTML 업로드 확인과 함께 진행한다.

## 참고 자료

- `docs/wip14/WIP14_REFERENCE_NOTES.md`
- `references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`

## 변경하지 않은 것

main, PR, merge, release/tag, 원격 WIP13C22 HTML, B3/B4 runtime, VLS loadout 수량, AIM-174B 운용 등록은 변경하지 않았다. B2는 로컬 산출물이며 대형 HTML을 API로 업로드하지 않았다.
