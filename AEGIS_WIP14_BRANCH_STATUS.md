# AEGIS v48 WIP14 — Branch / Handoff Status

작성일: 2026-09-29 (KST)

## 원격 기준

- 저장소: `0-FLANDRE-0/Aegis_Project`
- branch: `WIP14`
- 분기 기준: `main` commit `a8d14e3484200098be2143e0547c8e922642c042`
- 기준 tree: `92caa0163006e916d98b422440deb80f5cd0d9eb`
- branch 생성 당시 `main`의 최신 작업본: `Aegis_SIM_v48_WIP13C22.html`

## 현재 판정

이 branch commit은 **WIP14 계획·인계·참고자료 준비**다. B2/B3 또는 B4 구현 완료를 의미하지 않으며, 시뮬레이터 HTML을 새 기준으로 승격하지 않는다.

## B1 로컬 후보

- 후보 HTML: `Aegis_SIM_v48_WIP14B1.html`
- 크기: `7,295,398 bytes`
- SHA-256: `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`
- 지원 ZIP SHA-256: `15a82f1dd712faa46cdea9330761df6e5bf25a6b5e1947e268274f64f941aa5e`
- 내용: **SM-2MR/SM-2ER/SM-6/ESSM v1 경로의** onboard INS/GPS own-state, seeker/DL re-anchor, DL hard-cut truth boundary, A14 UI/engagement 회귀 보존
- 검사: 정적/결정적/fixed-step 검사는 기록된 범위에서 통과. Chromium 실행 파일 부재로 실제 브라우저 smoke는 미실행

대형 B1 HTML과 지원 ZIP은 이번 commit에 업로드하지 않는다. 대신 status/report/evidence/checksum 파일을 `docs/wip14/B1/`에 보존한다.

## 2026-09-30 추가 own-state 감사

사용자 제공 B1 HTML의 embedded C55 runtime을 추가 감사한 결과, B1 own-navigation boundary가 모든 미사일 계통에 적용된 것은 아님을 확인했다.

- SM-2MR / SM-2ER / SM-6 / ESSM: B1 error-bearing onboard own-state 경로 확인
- Kh-35U / Kh-32: guidance·seeker가 physical `em.x/y/z/vx/vy/vz`를 직접 소비하는 exact-own-state leakage 존재
- RAM Block 1A: B1 nav profile 미적용. vector PN projection과 sea-clearance guidance가 physical own velocity/altitude를 직접 소비
- C52 `INBOUND INS ASM` fixture는 발사 시점 **표적 좌표 기억**을 고정하는 장치이며 missile own-navigation model이 아님
- ASM passive RF bearing correction에는 별도의 target-truth dependency도 확인되어 후속 sensor/truth audit 필요

상세 감사 기록: `docs/wip14/B1/AEGIS_WIP14B1_OWN_NAV_COVERAGE_AUDIT.md`

이 발견은 기존 B1의 SAM/ESSM 검증 결과를 무효화하지 않지만, B1을 "모든 미사일 own-navigation 완료"로 확대 해석하지 않는다. 범용 weapon-link/return-link가 다른 미사일 계통으로 확장될 수 있으므로, raw physical own-state를 guidance가 직접 읽지 않는 공통 missile-navigation adapter를 후속 작업에서 닫아야 한다.

## 갱신된 다음 작업

1. **B2a:** 공통 packet envelope/queue/scheduler, uplink delay/loss/sequence/age/uncertainty
2. **B2b:** 범용 return-link transport 추가. 특정 미사일에 하드코딩하지 않고 무장별 link profile에서 enable/payload/cadence/delay/loss/TTL 등 세부 스펙을 설정하며, 현재 첫 활성 profile은 SM-6 onboard nav/uncertainty/phase/health return
3. **B2c:** profile-bounded launcher assistance와 link-cut/deadline/결정성 통합 회귀. 현재 첫 실제 적용은 SM-6이나 공통 transport/assistance 계약은 다른 미사일도 profile 설정만으로 사용 가능
4. **B3:** B2에 흡수됨. 독립 산출물 번호로 사용하지 않음
5. **B4:** SM-2MR, SM-2ER, SM-6, ESSM별 stateful loft profile 및 180 km/2 km 표적 회귀

B2와 B4는 분리한다. 먼저 link transport를 닫아 장거리 유도의 정보경로를 고정한 다음, 무장별 loft/energy corridor를 조정한다.

## 첨부 자료

- 통합 설계 및 검증 계약: `docs/wip14/WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md`
- 참고 원본 설명: `docs/wip14/WIP14_REFERENCE_NOTES.md`
- 사용자가 제공한 공대공 참고 HTML: `references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`
- B1 status/report/evidence/summary/checksum: `docs/wip14/B1/`

## 변경하지 않은 것

- `main`, release, tag, 기존 WIP13C22 파일
- B2/B3/B4 runtime code와 missile tuning
- VLS inventory와 AIM-174B 운용 등록
- PR 생성 또는 병합
