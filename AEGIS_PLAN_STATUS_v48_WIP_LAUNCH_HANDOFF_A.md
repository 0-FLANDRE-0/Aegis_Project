# AEGIS PLAN STATUS — v48_WIP_LAUNCH_HANDOFF_A

별도 시험 브랜치 `launch-handoff-a`. 기준 `fuze-zem-a@7d863699c596c30b0df5e34734f17fe11cadc21e` 최신 DZT. **인계 교착의 지정 범위 수정·검증, 전면 회귀 승인 보류.** main/원본 브랜치 병합 및 release/tag 생성 없음.

- HTML `Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html`:18,453,184 bytes, SHA-256 `e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7`.
- [상세 보고서](docs/missile/launch-handoff/A/REPORT.md), [인계 계약](docs/missile/launch-handoff/A/MODEL.md), [decoded diff](docs/missile/launch-handoff/A/game-change.diff), [검수](docs/missile/launch-handoff/A/final-evidence/verification.json), [재현](docs/missile/launch-handoff/A/REPRODUCE.md).
- 변경: 공중 Standard B3 인계 준비를 예정3D 경로 대비 자세/속도 정렬·전진 성분·받음각·안전 이격·최소 시간·기존 하류 기저 조건으로 판단. 정상 인계 뒤 launch overlap 종료, 선택 커널로 전달. deadline 강제 해제 없음. ESSM/대수상 기존 계약 유지.
- 보존: DZT, PN/APN/ZEM 이득, Kappa/B4/TGO90, 추진·공력·질량·G·사거리·배터리·시커·신관·파편/Pk, RNG/저장/UI/자산. 기존 선언 중 B3 외 byte 동일.
- 지정 고각10발0→10KILL, 정상 대조10/10 유지. 공통180발159→170효과/lethal, 이 시험 신규 실패0. 자연RF28조건21→24lethal, 신규 실패0.
- **신규 실패3발:** SM-6 100m/20km 정지Kh-35U 시드1(KILL31.20m→TRACKED_DIVERGENCE227.99m); 기존240km/5km 접근250m/s 시드12001 종료기OFF/ON 두 발(AIR명중5.48m→기폭비명중51.31m). 자동 계수 보정하지 않았으며 승인하지 않는다.
- 기존 도메인 **414/420PASS·6FAIL**: DDG/CG raid의 물리/재고/observer exact-state 비교. 원래 assertion 유지. UI88/88, 실제WebGL8발29검사, core0, actual/private10조건 오차0·281함수 해시 일치.
- 배속1/8/16 및64/시점/사통손상8시나리오 물리 동일. 대수상4발 궤적/결과/RNG동일. 무표적120초 hash동일. 전투120초는 변경된 비행 때문에 hash차이,120초 최종 명중으로 추가 판정하지 않음.
- SM-6 잔여 실패: 참고 pitch-only4MISS는 native fragment/Pk 무효기폭; 최종 고각5/5KILL과 구분. 전체월드 자연RF miss는 IOG_MEM/추적 freshness 손실, 신관 작동 없음. 단일 원인 미확정/후속 유도·시커 분석 필요.
- 직전 FUZE_ZEM_A 전달7파일 동일 bytes/blob archive. 기존 ENV_D120행은 HISTORICAL/재계산 필요, 전체 사거리 재측정 없음.
- 실행 HTML1개 ZIP / REPORT ZIP 별도 제공. 독립 Git 원격 전체 readback 영수증은 `docs/missile/launch-handoff/A/remote-publication.json`. 실제 폰 GPU/FPS 미측정.

다음: 신규 SM-6 두 기하 조건의 launch→Kappa→terminal 경로 연속성과 기존6상태 차이 검토. 이번 변경에 PN/추진/한계 보정을 섞지 않는다.
