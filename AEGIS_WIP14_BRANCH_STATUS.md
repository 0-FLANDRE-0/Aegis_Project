# AEGIS v48 WIP14 — Branch / Closeout Status

갱신: 2026-10-01 (KST)

## 판정

**WIP14 FEATURE SCOPE CLOSED / MERGED TO `main` VIA PR #38.**

최종 runtime 후보는 `Aegis_SIM_v48_WIP14B4.html`이다. 사용자가 WIP14 branch에 업로드한 원격 HTML은 로컬 최종 B4와 Git blob SHA 기준 exact 일치한다.

- HTML: `Aegis_SIM_v48_WIP14B4.html`
- 크기: `7,319,028 bytes`
- SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- Git blob SHA: `5e454823e4fd8c608d05ecd5e880a13cf5e5b2ce`
- decoded C55 main SHA-256: `62aa1f6e8a4ff9445f3fde2f4d86e581e6457616daada424bf3c8a4164ba186b`
- root status: `AEGIS_PLAN_STATUS_v48_WIP14B4.md`
- root checksum: `SHA256SUMS_v48_WIP14B4.txt`
- B4 report/evidence/status/checksum: `docs/wip14/B4/`

분기 이후 `main`은 움직이지 않은 상태에서 WIP14 종료 정리를 완료했고, PR #38로 `main`에 병합했다. merge commit은 `c0364caa1b742a097aa336274afe5c3c2611551a`이며 병합 과정에서 별도 기능 변경이나 튜닝을 추가하지 않았다.

## 완료 범위

- **B1:** SM-2MR/ER, SM-6, ESSM onboard own-navigation 및 seeker/DL truth boundary.
- **B2:** Kh-35U/Kh-32/RAM generic own-navigation, ASM passive RF truth boundary, 공통 VLS fixed-step release scheduler(기본 0.8 s, 0.6~1.0 s 설정).
- **B3:** generic packet transport와 profile 기반 return-link capability. SM-6는 첫 양방향 DL profile이며 GPS/INU 보정과 bounded assistance를 사용. return-link는 support deadline을 연장하지 않음.
- **B4:** SM-2MR/ER, SM-6, ESSM별 stateful loft와 단방향 CLIMB→CRUISE/ENERGY-SHELF→DIVE 전이. 게임 검토 범위 MR160 / ER260 / SM-6 260 km.

## 최종 검증

- B4 stage `33/33`, runtime `8/8`
- B3 transport `49/49`, runtime `25/25`
- package/static `52/52`
- B2 nav `38/38`
- VLS timing `12/12`, release policy `22/22`
- desktop/mobile-size handler `2/2`
- MR160 / ER260 / SM-6 초기260 접근 표적의 전체 단계 비행 1×/8×/16×/64× fixed-step 이력 일치
- B3 GPS/양방향 DL, B2 ASM/RAM, VLS scheduler, frozen propulsion/aero/mass, cell-exit/fuze/damage authority 보존
- C55 assets 0–12 B3 byte-identical, B3→B4 재생성 exact

하위 fixture 일부가 중복되므로 PASS 수를 합산한 고유 시험 총수는 주장하지 않는다.

## Known Deferred

WIP14 기능 범위 종료 뒤 별도로 추적한다.

1. `V48 WIP13A surface target submergedBreachFloods` 기존 core self-test 실패 1건. B3/B4 공통이며 WIP14 유도/DL/loft에서 새로 발생한 실패가 아니다.
2. 로컬 검사 환경에서는 native file URL/WebGL이 제한됐다. PR #38 GitHub Actions의 generic `webgl-render-probe`는 SwiftShader WebGL2로 통과했지만, 기존 `aegis-3d-render` job은 `SIM_FILE=Aegis_SIM_v48_WIP12D.html`로 고정된 legacy audit를 실행해 WIP03 damage attachment / BridgeMaster E mesh audit에서 실패했다. 이는 B4 HTML을 렌더해 발견한 신규 실패가 아니며 workflow 기준 갱신은 별도 유지보수 항목으로 둔다. 실제 모바일 GPU/FPS는 미검증.
3. SM-6 장거리 고정표적 seed별 미스, ESSM 중장거리 에너지 부족, 저고도 장거리 센서/조명 제한은 포락선 연구 항목. 종료를 위해 센서/신관을 완화하지 않음.

## 산출물

- root: `Aegis_SIM_v48_WIP14B4.html`, `AEGIS_PLAN_STATUS_v48_WIP14B4.md`, `SHA256SUMS_v48_WIP14B4.txt`
- B4: `docs/wip14/B4/AEGIS_PLAN_STATUS_v48_WIP14B4.md`, `AEGIS_WIP14B4_REPORT.md`, `AEGIS_WIP14B4_VALIDATION_SUMMARY.json`, `SHA256SUMS_v48_WIP14B4.txt`
- B1/B2/B3 상태와 설계/참고 기록은 `docs/wip14/`에 보존
- 대화의 `AEGIS_v48_WIP14B4_SUPPORT.zip`은 대용량 evidence/스크린샷/재생성 도구 묶음이며 저장소 병합 필수 산출물은 아님

## 다음 단계

WIP15에서 soft-kill 물리 배치를 시작한다. 현재 **3D 모델은 양현 3기씩 SRBOC가 보이지만 runtime은 4기/24발**이므로, 먼저 6기×6튜브=36발 canonical layout과 실제 launcher/tube 발사 원점을 정합한다. Nulka active decoy는 그 정합 뒤 별도 하위 단계에서 구현한다.

main/PR/merge/release/tag 자체는 이 상태 문서를 작성하는 시점까지 변경하지 않았다.
