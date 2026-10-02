# AEGIS v48 WIP15 — Local 15B Implementation / Handoff Status

갱신: 2026-10-02

## 현재 판정

**15B 기능 구현·명시한 범위 검증 완료 / 알려진 한계 유지 / 로컬 후보.**

새 기능을 구현하지 않은 준비 상태는 종료했다. 다만 대형 HTML은 아직 이 작업으로 원격 업로드하지 않았으며, 이 문서 갱신만으로 원격 runtime 기준·main·정식 release를 승격하지 않는다.

- repository: `0-FLANDRE-0/Aegis_Project`
- branch: `WIP15`
- 분기 기준: `main@dc8f67b01dc515441d61f057caffc4e550c0bae8`
- 코드 작업 기준: 사용자에게 전달한 `Aegis_SIM_v48_WIP15A.html`
- 15A SHA-256: `462318f7dc4860b526d96a09c9ed069731e242375b9aecedc455a938d7a208f7`
- 최신 로컬 결과: `Aegis_SIM_v48_WIP15B.html`
- 크기: `7,351,441 bytes`
- 15B SHA-256: `0264bb06397b60559daf74f964ab51be4cee95f45fe92dcfb1eb25b773461236`
- 이번 원격 검사에서 루트 `Aegis_SIM_v48_WIP15A.html`은 없었다. 로컬 파일과 원격 실행 기준을 혼동하지 않는다.

상세 인계: `docs/wip15/B/WIP15B_IMPLEMENTATION_HANDOFF.md`.

## 15A 보존

15A에서 정규화한 SRBOC 양현3기씩 총6기/36튜브와 실제 tube muzzle 발사를 유지했다. 기존 C5 함정 형상에 있던 Nulka 쌍열4기를 추가 등록했으며 SRBOC 표면을 이동하거나 교체하지 않았다. 원본15A 파일은 불변이다.

## 15B 구현

| 체계 | 초기 장전 | 예비 | 총량 | 완전히 빈 세트 재장전 |
| --- | ---: | ---: | ---: | --- |
| SRBOC 6기×6튜브 | 36 | 72 | 108 | 6발 / 60초 |
| Nulka 4기×2튜브 | 8 | 16 | 24 | 2발 / 90초 |

60/90초, 비행·RF 수준·Nulka 질량·저장 위치·AUTO 임계값은 SIM_TUNED 게임 설정이다. 실제 장비 제원 또는 취급 절차가 아니다.

- 완전 빈 발사기만 재장전. 예비→작업중→장전으로 이동하고 병렬 bank별 진행. 손상/비활성/장비 오프라인이면 정지·재개. 불충분한 예비는 보충하지 않음.
- canonical canister 입구와 함 local-point 속도에서 발사. 기존 쌍열4기/8입구 정점 직접 감사.
- 관측 cue 기반 DLP, 발사 때 현재 관측 track 식별/신선도/소실 재검사. 적 truth나 실제 seeker 락을 DLP/AUTO가 읽지 않음.
- 별도 world active-decoy의 출발/이동/호버/이탈/낙하/소멸. 오차 있는 자체 제어 관측과 유한 수명.
- 무차원 active RF source를 기존 ASM 측정/연관/EKF 및 HOJ에 연결. 기만체 이름으로 표적을 강제 지정하지 않음.
- 별도 수동 Nulka 버튼, 기존 SK AUTO 통합, 2D 자기 발사 심벌, 3D 탄체/지속 배기, bank 잔탄·재장전 표시.
- 추가 가변 탄약 질량 3,276kg. 장전/예비/작업중 중복 계상 없음.
- 새 snapshot revision과 preflight, 진행 중 reload 복원. 구형15A 저장은 명시적 거부. 공중 기만체와 교전 응답 기록은 combat transient로 초기화.

## 검증과 관찰

15B runtime33/33, geometry8/8, package/source70/70, desktop/mobile-size DOM2/2, B3 runtime25/25, B2 nav38/38, VLS timing12/12, release policy22/22, 보존 transport49/49 및 loft unit33/33 PASS. 하위 시험 중복이 있으므로 개수 합산 금지.

변경 없는 production HTML에서 실제 출항/SK AUTO/기존 Kh35 debug spawn 버튼과 production fixed-step clock으로240초 실행했다. Nulka6발 발사, 최종 장전4/예비12/작업중2/발사6=24. SRBOC 장전32/예비72/발사4=108. page error0.

Xvfb+headed Chromium+ANGLE/SwiftShader WebGL2로 한 기만체의15초 호버 장면 실제 렌더·스크린샷을 확인했다. 이 시각 fixture는 test-only closure 접근을 사용했으며, 별도의 production smoke는 HTML source 삽입 없이 실행했다.

14개 ASM 조건의 성공·실패·관찰창 종료를 모두 보존했다. 20km 수동 Nulka 조건은100초 창에서 피격0/최소 함 중심거리 약125.8m로 통과했지만 미사일은 여전히 비행 중이므로 격추로 표기하지 않는다. 8km 측면·20km AUTO 등은 재획득/함 피격이 남는다. Kh32 대조군도 원래 미스한 조건이므로 no-hit만으로 인과적 Nulka 성공을 주장하지 않는다.

## 유지하는 한계

- 기존 `V48 WIP13A surface target submergedBreachFloods` core 실패1건. 전체 core PASS 아님.
- 실기기 모바일 GPU/FPS와 native file-URL 접근은 미검증.
- 실제 추진기/파형/ERP/전술 최적제어, 독립 기만체 hard-kill 피해, 재장전 승조원 경로는 구현 범위 밖.
- AUTO/기만 유지 효과의 추가 게임 밸런스 검증이 필요하며, 방어 성공 확률을 직접 강제하지 않음.

## 산출물과 다음 인계

대화 산출물은 `Aegis_SIM_v48_WIP15B.html`, `AEGIS_PLAN_STATUS_v48_WIP15B.md`, `AEGIS_WIP15B_REPORT.md`, `AEGIS_WIP15B_VALIDATION_SUMMARY.json`, `SHA256SUMS_v48_WIP15B.txt`, `AEGIS_v48_WIP15B_SUPPORT.zip`이다. 지원 ZIP에 코드 패치·빌더·정점 등록·테스트·전체 evidence·실렌더 스크린샷을 포함한다.

사용자가 최신 HTML을 WIP15에 올리면 위 해시를 대조한 뒤 원격 runtime/README/체크섬·테스트 및 아카이브를 정리한다. 이번에는 작은 인계 문서만 원격에 반영했다. main 수정, PR, merge, release/tag는 수행하지 않았다. 기존 준비 계획은 `docs/wip15/WIP15_SRBOC_NULKA_PREP_PLAN.md`에 역사/범위 기록으로 보존한다.
