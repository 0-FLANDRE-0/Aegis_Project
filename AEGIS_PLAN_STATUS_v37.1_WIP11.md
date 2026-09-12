# CIWS Closure B2 로컬 RF 속도 안정화 WIP11 — 2026-09-12

## WIP10 live RF 실패 수정

- WIP10 커밋 `ac248018f6616b3924f51b55230b15f125278bdd`의 Actions run `34691679929`(#23)에서 정적·WebGL 검사는 통과했지만 강화한 B2 live RF noise guard가 실패했다.
- 실제로 이동하는 직선 표적은 로컬 RF 70 hit 뒤에도 22.56 m/s², `maneuvering:true`를 기록했다. 가속도 feed-forward 분리만으로는 초기 속도 획득과 측정 잡음의 창 경계 차분을 충분히 억제하지 못했다.
- WIP11은 25 local-hit warm-up 동안 가속도 상태를 0으로 유지하고, 원시 alpha-beta 속도가 아니라 시간상수 0.30초(GUN)·0.35초(RAM)의 저역통과 속도를 측정창 간 차분한다. cue 속도 보정은 평활 속도와 기준 속도 양쪽에도 동일하게 상쇄한다.
- 기존 합성 직선·24 m/s² 횡기동, bounded coast/range, Phalanx/SeaRAM 예측 연결 검사는 유지한다. 강화한 생산 `ciwsLocalMeasurement → ciwsStepLocalTrack` 직선/횡기동 검사를 통과해야만 B2를 완료 처리한다.
- WIP10 HTML·상태 문서는 `archive/v37.1/WIP10/`에 원본 blob 그대로 보존한다. workflow 대표 파일은 `Aegis_SIM_v37.1_WIP11.html`로 변경한다.
- WIP11 HTML SHA-256은 `7ddbacc8e5df0d4c41f61606ee5697204f23d20913e77875dd5973889c29623d`이다. 새 Actions와 artifact 확인 전에는 B2 완료로 승격하지 않는다. B3 부분손상 연속 성능은 수정하지 않았다.

---

# CIWS Closure B2 로컬 RF 안정화 WIP10 — 2026-09-12

## WIP09 artifact 진단 반영

- WIP09 커밋 `20f04cfb14cbb8c5831db367831984400d91b966`의 Actions run `34691302509`(#22)은 B1, B2, 정적, WebGL, 실제 3D 렌더 5개 job이 모두 통과했다.
- B2 artifact의 합성 직선·기동 검사는 통과했지만, 생산 필드 smoke가 물리 이동 없이 `stepCiws`만 호출한 B1 격리 fixture를 사용했다. 실제 객체는 정지한 반면 cue 속도는 -300 m/s여서 81.28 m/s²의 가짜 감속과 기동 판정을 만들었고도 필드 존재만 검사해 통과했다.
- WIP10은 가속도 추정값을 alpha-beta 추적 상태 전파에서 분리한다. 추적 상태는 등속으로 안정적으로 전파하고, 가속도는 거리·품질·freshness·jerk 제한을 거친 사격 예측에만 feed-forward한다.
- 초기 속도 획득을 기동으로 오인하지 않도록 로컬 RF warm-up을 12 hit로 늘리고, GUN/RAM 측정창과 응답·히스테리시스를 완만하게 조정했다.
- 새 live sensor 진단은 실제 객체를 매 고정 tick 이동시킨 뒤 생산 `ciwsLocalMeasurement → ciwsStepLocalTrack` 경로를 사용한다. 직선 표적의 noise guard와 24 m/s² 횡기동 표적의 탐지를 각각 별도 seed로 검사한다.
- WIP09 HTML·상태 문서는 `archive/v37.1/WIP09/`에 원본 blob 그대로 보존한다. workflow 대표 파일은 `Aegis_SIM_v37.1_WIP10.html`로 변경한다.
- WIP10 HTML SHA-256은 `fce6b33d31b36bb7fab7107eed15328068d4564752eb119f1b49564d8e32e928`이다. 새 Actions와 artifact 확인 전에는 B2 완료로 승격하지 않는다. B3 부분손상 연속 성능은 수정하지 않았다.

---

# CIWS Closure B2 가속도·기동 예측 WIP09 — 2026-09-12

## 구현 및 검증 대기

- WIP08의 B1 익명 관측·교전권한·로컬 탐지 경계는 유지한다. 이번 변경은 CIWS 로컬 RF 트랙의 속도 이력으로 가속도와 jerk를 추정하고, 기동 상태를 히스테리시스로 판정하는 B2 범위다.
- 함정 cue 속도 보정량은 가속도 표본 기준에도 같은 양을 반영해 상위 트랙 보정이 로컬 기동으로 오인되지 않게 했다. 실제 ASM 객체는 기존과 같이 로컬 측정 합성 및 충돌 경계 밖의 추적·예측에 전달하지 않는다.
- 추정 가속도와 jerk는 마운트별 상한, 측정 창, 응답·coast 감쇠를 적용한다. 예측은 로컬 hit 수, 품질, freshness, jerk와 마운트별 거리·시간 한계로 제한한다.
- 같은 가속도 예측 함수를 Phalanx Mk244 탄도 반복해와 SeaRAM 선행해에 연결했다. 범위 밖이거나 신뢰도가 낮으면 기존 등속 예측으로 자동 복귀한다.
- 시작 자기검사와 Playwright B2 검사는 직선 표적 noise guard, 횡가속 표적 추정, 예측점 변화, coast 감쇠, 거리 gate, 진단 truth 필드 부재, 생산 로컬 트랙 필드, 1×/8×/16× 결정성을 확인한다.
- WIP08 HTML·상태 문서는 `archive/v37.1/WIP08/`에 원본 blob 그대로 보존한다. workflow 대표 파일은 `Aegis_SIM_v37.1_WIP09.html`로 변경한다.
- WIP09 HTML SHA-256은 `a5f02f99fdf115387702646e6ad2a1f038fd55d6f5bb4bb0afd75998c5d8e368`이다. 이 문서 시점에는 새 Actions와 artifact 결과가 없으므로 B2 완료로 승격하지 않는다. B3 부분손상 연속 성능은 수정하지 않았다.

---

# CIWS Closure B1 종결 검증 WIP08 — 2026-09-12

## Actions 종결 결과

- PR #6 head `6a92d724095b4a4230aec91db62bf2152e2b52e1`의 Actions run `34690224354`(#20)이 완료됐고, `static-smoke`, `webgl-render-probe`, `aegis-3d-render`, `ciws-b1-closure` 4개 job이 모두 통과했다.
- Playwright matrix에서 페이지 로드, 시작 자기검사 실패 0, `CORE SELFTEST PASS`, Phalanx/SeaRAM 허가 교전, 보호 트랙 자동발사 차단, cue/local 탐지 경계, 소실·재획득, 정상·40% 부분손상, 1×/8×/16× 결정성이 모두 통과했다.
- visual test에서 출항 오버레이 종료, 진단 경계 정지 상태, 3D 열기 전·중·닫기 후 상태 동일성이 모두 통과했다. 콘솔 오류와 uncaught page error는 0건이다.
- CIWS artifact ID는 `10297306876`, archive digest는 `sha256:e4de7ac8bdf8930958264fe024449796558670adcab4426058a510f162ca2d69`이다. 내부 matrix/visual JSON의 `pass`는 모두 `true`이고 시뮬레이터 SHA-256은 `d4cc083cf7756f76bd2a40b1d00dae8315e511ed9ba18476011d12549c207168`로 일치한다.
- 이 범위의 CIWS Closure B1 종결 검증은 완료했다. B2(로컬 가속도·기동 추정)는 시작하지 않았으며 다음 코드 작업으로 남긴다.

- WIP07 Actions run `34690047243`(#19)에서 3개 비-CIWS job과 정지 상태 3D 격리 검사는 통과했다. AUTO mode 및 선수 0° 기하 수정 뒤 시작 자기검사는 다음 fixture 단계인 `A3 classification confidence alone must not authorize`에서 실패했다.
- 원인은 fixture 위치·초기 운동을 x축 선수 접근으로 바꾼 뒤 이탈/재접근 전이는 이전 y축의 `vy/_kfX[4]`만 반전한 불일치다. WIP08은 이 두 전이를 `vx/_kfX[3]`로 맞춰 실제 운동 상태와 EKF 상태를 함께 전환한다.
- 생산 분류·권한·CIWS 선택 로직은 수정하지 않았다. WIP07 HTML과 상태 문서는 `archive/v37.1/WIP07/`에 원본 blob 그대로 보존한다.
- workflow 대표 파일은 `Aegis_SIM_v37.1_WIP08.html`이며 HTML SHA-256은 `d4cc083cf7756f76bd2a40b1d00dae8315e511ed9ba18476011d12549c207168`이다. Actions #20과 artifact 확인으로 B1 종결 검증을 완료했으며 B2는 시작하지 않았다.

---

# CIWS Closure B1 종결 검증 WIP07 — 2026-09-12

- WIP06 Actions run `34689854972`(#18)에서 `static-smoke`, `webgl-render-probe`, `aegis-3d-render`가 통과했다. CIWS visual test의 정지 상태 3D 격리 검사도 통과했으며 `CIWS_B1_FAILED_CHECKS []`를 기록했다.
- WIP06에서 AUTO 모드 전달 누락은 해소됐고, 시작 자기검사의 다음 실제 탈락 사유가 `DIRECTION_BLOCKED / 구조물: 함교(상부전)`로 드러났다. 우현 90° fixture를 같은 run에서 실발사가 통과한 Phalanx 브라우저 fixture와 동일한 선수 0° 인바운드 배치로 교체했다.
- 생산 교전 게이트, blind sector, traverse 판정은 완화하지 않았다. 변경은 자기검사 입력 기하만 실제 검증된 경로와 일치시키는 범위다.
- WIP06 HTML과 상태 문서는 `archive/v37.1/WIP06/`에 원본 blob 그대로 보존한다. workflow의 대표 파일은 `Aegis_SIM_v37.1_WIP07.html`로 변경한다.
- WIP07 HTML SHA-256은 `c58612857f35303570c41ed17350165a5dafd31e7369f961c463e105400a5726`이다. B1 완료 승격과 B2 작업은 새 Actions 및 artifact 확인 전까지 보류한다.

---

# CIWS Closure B1 종결 검증 WIP06 — 2026-09-12

- 기준 원격은 PR #6 head `c7ccf2dba2c9f635e2debcb54ae5e58cfeb44f5a`, Actions run `34685404177`(#17)이다. `static-smoke`, `webgl-render-probe`, `aegis-3d-render`는 통과했고 `ciws-b1-closure`의 핵심 브라우저 검사 8개도 통과했다.
- 시작 자기검사 fixture가 `updateTrackOperationalStateA3(...,{mode:'AUTO'})`만 호출하고 실제 `engagementControlMode`는 MANUAL로 남겨 `ciwsObservedThreatAuditB1`에서 `MODE` 차단되던 문제를 수정했다. fixture 동안만 AUTO로 전환하고 기존 모드를 `finally`에서 복원한다.
- 3D 격리 검사는 실행 중 시뮬레이션의 자연스러운 tick 변화를 3D 부작용으로 오판하지 않도록, 진단 경계의 `setPaused(true)`로 물리 시간과 accumulator를 정지한 뒤 3D 열기 전·중·닫기 후 상태를 비교한다.
- 잘못 생성된 `archive/v37.1/WIP05/Aegis_SIM_v37.1_WIP05.html` 0바이트 blob은 루트 WIP05 원본 blob으로 복구한다. 루트 WIP05는 수정하지 않는다.
- workflow의 대표 파일은 `Aegis_SIM_v37.1_WIP06.html`로 변경한다. WIP06 HTML SHA-256은 `d36d0988e2e177cf2a3ef4d1a6a5167cae8b8f92b22ec1f0515194e15f4ce343`이다. B1 완료 승격과 B2 작업은 새 Actions 및 artifact 확인 전까지 보류한다.

---

# CIWS Closure B1 종결 검증 WIP05 — 2026-09-12

- 원격 기준은 PR #6 head `273206404540e52187bc7964a15df9beb0b2ad00`, Actions run `34682645360`이다. `static-smoke`, `webgl-render-probe`, `aegis-3d-render`는 통과했고 `ciws-b1-closure`는 실패했다. 콘솔/page 오류는 0건이며 WIP04 SHA-256은 `c3786921b81436db46fd624a593b5f818d5231fa4cb0fb1aadc8b9f31d27d3f4`로 일치했다.
- 후보 평가에 `ciwsObservedThreatAuditB1` 단계별 사유를 추가했다. 정상 자기검사 fixture는 AUTO gate 통과 뒤 물리 mount 방향 조건에서 탈락하던 선수 방향 대신 연결된 우현 traverse의 인바운드 표적을 사용하며, 재실패 시 정확한 최초 탈락 단계가 자기검사 메시지에 남는다. gate 자체는 약화하거나 삭제하지 않았다.
- SeaRAM fixture의 기존 선수 방위는 SeaRAM 선수 사각과 겹쳤다. WIP05 fixture는 실제 bearing 입력을 지원하고 SeaRAM은 우현 인바운드로 배치한다. JSON snapshot에 후보 사유, SEARCH/TRACK 상태 이력, 로컬 track freshness/LOS/range 품질, traverse와 hardware health를 남긴다.
- 보호 상태는 매 tick 상태를 덮어쓰지 않는다. UNKNOWN은 ASM 자동 적성 증거를 제거한 운동 표적, UNASSESSED는 tentative track, WITHHELD는 memory/FCS 보류 상태로 한 번만 입력하며 실제 updateCIWS가 이후 상태와 발사를 결정한다.
- 소실/재획득은 실제 SPY lifecycle 함수의 dwell miss 두 번(COAST→REACQUIRE)과 accepted reacquisition hit 두 번(REACQUIRE→FIRM)을 사용한다. 재획득 중 CIWS 해제·무발사와 FIRM 복귀 뒤 재교전을 검사한다.
- 기능 검증과 이미지 검증을 별도 Playwright test로 분리하고 각각 120초 제한을 둔다. CIWS 이미지는 출항 버튼으로 VLS 편성 모달을 정상 종료한 뒤 촬영하며, 3D는 full-page가 아니라 `external3DCanvas`만 촬영한다.
- WIP05 HTML SHA-256은 `81a94bd3003c910a9bcee6ea29e646c0500bf4a1051171933db9755b03f3fcc3`이다.
- B1 완료 승격 및 B2 작업은 하지 않았다. 수정 후 Actions 결과는 아직 미실행이며 사용자가 원격 브랜치를 갱신한 뒤 확인한다.

---

# CIWS Closure B1 종결 검증 WIP04 — 2026-09-12

- Actions run `34681951551`에서 브라우저 테스트가 비공개 함수 `_wip75ResetCase`를 페이지 전역 API로 잘못 취급해 실패했다. 같은 문제가 있던 `_wip75CreateTarget`, `_wip75SyncTrack` 직접 의존성도 제거했다.
- 브라우저가 사용하는 단일 명시적 진단 경계 `window.__NAVAL_SIM_DIAG__.ciwsB1Closure`를 추가했다. fixture 준비, 독립 차단 조건, 소실/재획득, 실제 고정-step accumulator 배속 진행, 로컬 탐지 실패 probe와 결과 snapshot은 이 경계로만 제공한다.
- WIP03에서 획득 뒤 트랙이 소실·재획득·보호 상태로 바뀌어도 기존 로컬 접촉을 계속 추적할 수 있던 결함을 확인했다. WIP04는 매 tick 현재 관측 후보와 권한을 재검증하고 후보에서 빠진 파일의 Phalanx/SeaRAM 추적 및 발사를 즉시 해제한다.
- FRIEND, NEUTRAL, UNKNOWN, UNASSESSED, WITHHELD는 각 fixture에서 공통 AUTO 가능 기준을 만든 뒤 해당 운용 상태 입력만 바꾸어 자동발사 0회를 별도로 기록한다.
- 1×/8×/16× 검사는 `worldTimeScale`, `simAccumulator`, `SIM_FIXED_DT`, `simulateFixedTick`으로 구성된 실제 런타임 시간 진행 경계를 사용하고 동일 seed와 6초 시뮬레이션 시간의 결과를 비교한다.
- Playwright 의존성 lockfile을 추가했으며 Actions 설치는 `npm ci`를 사용한다.
- 이 문서 시점에는 수정 커밋의 Actions 재실행 결과가 없으므로 B1은 완료로 승격하지 않는다. B2는 시작하지 않았다.

---

# CIWS Closure B1 종결 검증 결함 수정 — 2026-09-12

## B1 종결용 Actions 검증 추가 — 2026-09-12

- 기준 커밋 `e717666110e3d7762a4fabb45331fbcc3803ad29`에 WIP03 HTML과 대응 상태 문서가 포함되고, HTML SHA-256이 기존 인계값 `56d6fd07ff6701ef3136ded9f62a6eadf501ae92f0fcea5cb5cee51be85daa20`과 일치함을 확인했다.
- GitHub Actions Chromium/Playwright에서 페이지 오류, 시작 자기검사, 허가된 Phalanx/SeaRAM 실발사, 보호 상태 자동발사 차단, cue/local 탐지 경계, 소실/재획득, 정상/40% 부분손상, 동일 seed 1×/8×/16× 고정 tick 결과, 2D/3D 상태 격리를 한 번에 판정하는 종결 검증을 추가했다.
- 검증은 `ciws-b1-results.json`, `ciws-engagement.png`, `aegis-3d.png`, `SHA256SUMS`를 `ciws-b1-closure-<commit SHA>` artifact로 보존한다.
- 이 문서 변경 시점에는 새 Actions 실행 결과가 아직 없으므로 B1을 완료로 승격하지 않는다. 모든 브라우저 항목의 실제 통과 결과가 확인된 뒤에만 완료로 기록하며 B2는 시작하지 않는다.

- WIP02 정적 종결 검토에서 두 안전 결함을 확인해 검증만으로 B1 완료 처리하지 않고 `Aegis_SIM_v37.1_WIP03.html`을 만들었다.
- 첫째, WIP02의 관측 트랙 후보 필터가 A3 자동 교전권한을 확인하지 않아 `FRIEND`, `NEUTRAL`, `UNKNOWN`, `UNASSESSED`, `WITHHELD` 트랙이 CIWS 후보가 될 수 있었다. WIP03은 `trackEngagementGateA3(trackId,{automatic:true})` 통과를 위협 평가의 필수 조건으로 둔다.
- 둘째, WIP02는 함정 cue가 있으면 `ciwsResolveLocalContactB1`에서 로컬 탐지 성공 없이 실제 접촉을 선택할 수 있었다. WIP03은 cue 유무와 관계없이 로컬 RF 탐지를 요구하되, cue가 있을 때만 `cueTrackRangeKm`까지 좁은 빔 획득 범위를 확장한다.
- 따라서 오표적 교전 0회와 CIWS 로컬 센서 실제 접촉 획득을 WIP02 코드로 통과 선언할 수 없으며 B1은 아직 종결되지 않았다.
- 현재 컨테이너에는 Chromium 실행 파일이 없고 GitHub/Ubuntu/npm 경로가 프록시 403으로 차단되어 요구된 실제 브라우저 1×/8×/16×, 정상/부분손상, 콘솔/WebGL 검증은 수행하지 못했다. 새 PR의 Actions artifact에서 실제 브라우저 검증을 계속해야 한다.
- B2는 시작하지 않았다.

---

# CIWS Closure B1 작업 상태 — 2026-09-12

- 현재 작업 파일은 `Aegis_SIM_v37.1_WIP03.html`이다.
- CIWS 상위 위협 평가 `ciwsObservedThreatsB1`과 cueing은 이제 `tracks`의 익명 관측 트랙만 순회한다. 실제 ASM 배열, 실제 객체 ID 역조회, `truthRef`는 이 판단 경로에서 사용하지 않는다.
- 위협 순위는 관측 위치·속도의 상대운동으로 계산한 거리, 폐쇄속도, CPA/TTI, 관측 고도와 현재 RAM 교전 트랙 ID만 사용한다. 동점은 독립 `trackId` 순으로 결정해 고정 seed에서 안정적이다.
- CIWS 로컬 RF 경계 `ciwsResolveLocalContactB1`만 실제 ASM 반사를 순회한다. 선택된 익명 트랙의 예측 위치와 공간 게이트로 반사를 연관하며, cue 유무와 관계없이 로컬 탐지 성공을 요구한다. 이후 탄환·요격탄 충돌 판정은 기존과 같이 truth 물리를 사용한다.
- 마운트에는 상위 관측 파일 키 `trackingTrackId`와 로컬 센서가 획득한 물리 접촉 `trackingTarget`을 분리해 저장한다. SeaRAM 발사체의 `targetId`도 실제 ASM ID가 아니라 관측 트랙 ID다.
- 시작 자기검사에 익명 행만으로 이루어진 CIWS 순위 결정성, 동점 경계, truth 필드 부재 검사를 추가했다.
- JavaScript 문법 검사와 CIWS 판단부 truth 접근 정적 검사를 통과했다. 실제 Chromium/WebGL 검증은 GitHub Actions의 `static-smoke`, `webgl-render-probe`, `aegis-3d-render`와 업로드되는 PNG artifact로 수행한다.
- HTML SHA-256은 `56d6fd07ff6701ef3136ded9f62a6eadf501ae92f0fcea5cb5cee51be85daa20`이다.
- 이번 범위에서 B2(로컬 가속도/기동 추정), B3(부분손상 연속 성능)는 수정하지 않았다. 다음 작업은 CIWS Closure B2다.

---

# 원래 작업 계획 대조 — 2026-09-11

현재 기준: `naval_combined_SI_REFACTOR_WIP202_SM2_PHOTO_BASED_MESH.html`.
2026-09-11 Track Association V31에서 대표 HTML의 SPY 익명 관측 연관과 허위 plot 입력을 구현하고, 대표 파일 직접 브라우저 검사 및 기존 회귀 묶음을 다시 실행했다.

## 3D 보조 레이더 시각화 V37.1_WIP01 작업 업데이트 — 2026-09-12

- 현재 작업 파일은 `Aegis_SIM_v37.1_WIP01.html`이다.
- 3D 툴바에 기존 `SPY RADAR`와 독립된 `SPQ-9B`, `SPS-73` 토글 버튼을 추가했다. SPQ-9B는 주황색, SPS-73은 녹색 활성 상태로 구분한다.
- SPQ-9B는 실제 `spq9bRotorAngle`, 30 RPM, 양면 배열 2개, 1° × 1° 빔, 현재 손상 연동 탐색거리 상태를 읽는다.
- SPS-73은 실제 `sps73RotorAngle`, 24 RPM, 단일 회전 빔, 0.75° × 20° 빔, 177.792 km 계기 최대거리를 읽는다.
- 두 시각화는 EMCON과 센서/전력 손상 상태를 반영한다. 렌더러는 센서 스윕을 별도로 적분하거나 탐지 결과를 물리에 되먹임하지 않는다.
- SPS-73 전용 3D 장비·손상 히트박스는 아직 없으므로 빔 시작점만 기존 후방 마스트 높이에 둔 표현용 설치점이다. 센서 물리 원점과 탐지 로직은 변경하지 않았다.
- JavaScript 문법 검사, 전체 스크립트 초기화, 내장 자기검사 실패 0, 토글 독립성, WebGL 비의존 렌더 객체 생성 검사를 통과했다. 렌더 객체 수는 SPQ-9B 2개, SPS-73 1개이며 정상 전력·EMCON 해제에서 모두 방사 상태가 된다.
- 현재 실행환경에는 Chromium/WebGL 컨텍스트가 없으므로 실제 3D 프레임 육안검사는 남아 있다. 따라서 안정판 `V37.1`로 승격하지 않고 `V37.1_WIP01`로 유지한다.

## A3 상태·교전권한 V37 작업 업데이트 — 2026-09-12

- `classification`, `identity`, `threatStatus`, `engagementAuthority`를 `TRACK_RECORD_V37_A3`의 실제 운용 계약으로 전환했다. 새 트랙의 기본 권한은 `WITHHELD`이며 더 이상 `UNSPECIFIED`가 아니다.
- 식별은 `UNKNOWN / ASSUMED_HOSTILE / HOSTILE / FRIEND / NEUTRAL`, 위협 상태는 `UNASSESSED / MONITOR / THREAT / HARMLESS / LOST / DESTROYED`, 교전권한은 `WITHHELD / MANUAL_ONLY / OPERATOR_RELEASE / AUTO_AUTHORIZED`로 고정했다.
- 센서의 `classificationConfidence`만으로 적성 식별을 만들지 않는다. 자동 `ASSUMED_HOSTILE`은 확정 트랙, ASM 분류, 반복 관측, 미사일형 운동, 자함 접근이라는 독립 증거가 함께 성립할 때만 부여된다.
- `ID` 버튼으로 선택 트랙을 운용자가 `UNKNOWN → HOSTILE → FRIEND → NEUTRAL` 순환 지정할 수 있다. 운용자 식별은 센서 분류와 별도 필드에 보존되며 `FRIEND/NEUTRAL`은 항상 발사 보류다.
- MANUAL은 실제 버튼 조작이 필요한 `MANUAL_ONLY`, SEMIAUTO는 `OPERATOR_RELEASE`, AUTO는 적성·위협·사격통제 품질을 모두 만족할 때만 `AUTO_AUTHORIZED`가 된다. AUTO 판단부와 SM-2/ESSM 발사 함수 양쪽에 같은 권한 게이트를 넣었다.
- HUD와 진단 스냅샷에 네 상태, 운용자 지정, 권한 사유를 노출했다. 새 alias/reacquisition 트랙은 기존 운용자 식별이나 발사권한을 무조건 상속하지 않는다.
- JavaScript 문법 검사와 HTML 전체 스크립트 초기화 하네스에서 시작 셀프테스트 실패 0을 확인했다. 12 km 인바운드 ASM은 `ASSUMED_HOSTILE / THREAT / AUTO_AUTHORIZED`로 전이해 AUTO ESSM 발사 1회를 수행했고, 같은 트랙을 `FRIEND`로 지정한 경우 후보 표시는 유지되지만 `AUTH WITHHELD`, 자동발사 0회를 확인했다.
- 현재 실행환경에 Chromium 실행 파일이 없어 실제 화면 클릭·렌더 검사는 수행하지 못했다. 상태 전이·발사 게이트 구현과 전체 스크립트 런타임 검사는 통과했으며 실제 브라우저 UI 회귀만 남는다.

## SPY 편대 분리·배치 연관 V36 작업 업데이트 — 2026-09-12

- 적 생성량은 바뀌지 않았다. `SPAWN.maxAlive`는 12이며 전투기 편대 간격 0.8~1.8 km, 폭격기 편대 간격 1.5~3.0 km도 유지된다.
- 탐지 수 감소 원인은 V31의 scheduler-cycle-wide 중복 억제였다. 건강한 SPY 면에서도 탐색 plot 품질을 반영한 coarse 위치 게이트가 150 km에서 약 2.8~3.2 km, 200 km에서 약 3.7~4.3 km, 280 km에서 5 km 상한까지 넓어져 편대원을 같은 표적의 중복 plot로 폐기할 수 있었다.
- coarse 재연관과 `sameCycleDuplicate` 폐기 경로를 SPY 운용부에서 제거했다. 측정 공분산은 상태 추정·NIS 연관에만 쓰며 레이더의 물리적 분해능이나 extractor 중복 판정으로 대신 사용하지 않는다.
- 한 실제 dwell의 전체 plot과 기존 공중 트랙으로 NIS 비용 행렬을 만들고 Hungarian 최소비용 1:1 배정을 수행한다. 기존 트랙 하나에 두 개의 분리된 plot이 들어오면 하나만 기존 트랙에 배정되고 나머지는 독립 tentative track을 시작한다.
- `measuredThisCycle`은 더 이상 서로 다른 물리 dwell 사이의 연관 후보를 차단하지 않는다. 같은 dwell 안의 중복 사용은 `usedPlots`/`usedTracks`와 1:1 배정으로 막는다.
- 시작 자기검사에 단일 기존 트랙 대 2개 편대 plot 및 2×2 교차 배정 회귀를 추가했다. 실제 소스 함수를 추출한 독립 런타임 검사에서 편대 사례 `[기존 트랙, 신규 트랙]`과 교차 최소비용 배정이 통과했고 JavaScript 문법도 통과했다.
- 진단 스냅샷은 `associationMode: BATCH_ONE_TO_ONE_V36`을 표시한다. 변경 HTML SHA-256은 `4906c335ef99ca97b67122de31ebe33bb762cb0de36bd66aa121a037cef0c0d0`이다.
- Vercel preview에 변경 HTML 전체를 올려 실제 Chrome에서 출항, EMCON 해제, 1×/4×/16× 탐색을 실행했다. 페이지의 시작 로그에서 `CORE SELFTEST PASS`와 `SPY-ANON-ASSOC-V36`을 직접 확인했으며 시뮬레이터 소스에서 발생한 브라우저 오류는 0이었다. 기록된 오류는 제어 브라우저 확장 자체의 metadata 전송 오류뿐이다.
- 해역 seed `1086574332`의 1× 초기 탐색에서는 새 편대 스폰 전 공중 표시 트랙이 5개에서 7개(`AIR+ASM+UNK`)까지 형성됐다. seed `836588488`와 `2503285408`에서도 재방문·분류·후속 스폰에 따라 각각 5개, 10개까지 증가해 편대 전체가 1~2개 트랙으로 고정 병합되는 기존 증상은 재현되지 않았다.
- 정확한 `truthAircraft / plot / tentative / confirmed` 동시 수치 계측을 위한 preview 전용 표시기를 준비했으나 같은 Vercel 프로젝트의 두 번째 preview 배포가 권한 403으로 거부돼 그 비교는 완료하지 못했다. 대표 HTML에는 해당 임시 표시기를 넣지 않았다.
- 상태는 **구현·문법·소스 기반 배정 회귀·실제 브라우저 기동/자기검사·편대 비병합 smoke 통과 / truth 대 track 정밀 계측 잔여**다.

## SPY 전방위 탐색 V32 작업 업데이트 — 2026-09-11

- 대표 HTML에 `SPY1DV_SEARCH_SECTORS_V32`를 추가했다. `WIP199_SPY_LAYOUT`의 실제 3D 면 중심각을 정렬하고 인접 면 중심각의 이등분선을 각 면의 탐색 경계로 사용한다.
- `spySearchTask`의 고정 중심 ±45°/90° 폭 가정을 제거했다. 수평·입체 탐색 모두 각 면의 실제 담당 폭을 `ceil(담당 폭/명목 step)`개의 동일 폭 셀로 나눠 경계를 정확히 맞춘다.
- `spyFaceSteerLimitRadV32`가 기존 `45° + faceOverlapDeg`와 실제 담당 경계까지 필요한 각도 중 큰 값을 사용한다. 렌더링용 면 법선과 센서용 중심각은 분리하지 않았다.
- `spySearchCoverageAuditV32`와 시작 시 자기검사를 추가했다. 5° 간격 전방위 표본과 각 면 경계 전후 `-2°, -1°, 0°, +1°, +2°`를 검사한다.
- 정적 검증 결과: HTML JavaScript 문법 통과. 수평 7.5° 및 입체 5° 래스터 모두 총 360°, 미커버 방위 0, 조향 한계 초과 셀 0이다. 변경 HTML SHA-256은 `4906c335ef99ca97b67122de31ebe33bb762cb0de36bd66aa121a037cef0c0d0`이다.
- 상태는 **구현 완료 / 실제 브라우저 기동·자기검사 통과 / 전방위 표적·교전 회귀 잔여**다. 2026-09-12 비공개 Vercel 프리뷰에서 대표 HTML의 실제 스크립트 실행과 `CORE SELFTEST PASS`를 확인했다. 다만 아래 1·2번의 360° 실표적 및 ±90° 교전 완료 조건 전체를 이번 브라우저 세션에서 다시 실행한 것은 아니므로 아직 완전 통과로 선언하지 않는다.

## 시각 센서 익명 관측 V33 작업 업데이트 — 2026-09-12

- `updateVisualDetection`의 항공기·ASM 경로에서 `trackIdForTruthV27(...)`와 `truthRef` 전달을 제거했다. 실제 객체는 광학 측정 합성까지만 사용하며 이후 plot에는 객체 ID·도메인·`truthRef`가 없다.
- `acceptVisualAnonymousPlotV33`이 비등방 시각 측정 공분산과 `trackCartesianAssociationNisV33`을 사용해 기존 트랙을 찾고, 게이트 안의 트랙이 없을 때만 `allocateTrackIdV31` 경로로 독립 트랙을 만든다.
- 거리 추정 오차, 방위 오차, 고각 오차를 각각 LOS 방사·횡방향·수직 축으로 분리했다. 시각 센서는 도플러를 측정하지 않으므로 초기 방사속도 불확실성을 220 m/s로 둔다.
- 새 시각 트랙 초기화도 제공된 3×3 공분산을 보존하도록 수정했다. 기존 초기화처럼 큰 거리 오차를 횡방향 전체에 복제해 서로 다른 표적이 같은 트랙에 들어가는 문제를 막았다.
- 정적 독립 검사 결과: JavaScript 문법 통과, 시각 plot 실제 객체 ID 누출 없음, 동일 관측 NIS 0, 5 km 횡방향 오관측 NIS 4187.25(게이트 25), 정밀 레이더 트랙에 1.6 km 편향 시각 거리값을 적용했을 때 방사거리 상태 이동 3.54 m다.
- 상태는 **구현 및 정적 독립검사 완료 / 실제 브라우저 기동·자기검사 통과 / 시각 단독·SPY 융합 시나리오 회귀 잔여**다. 사용자 승인에 따라 전체 HTML을 Vercel 팀 비공개 프리뷰에 올려 실제 스크립트 실행, 출항 및 UI 반응을 확인했다. 변경 HTML SHA-256은 `4906c335ef99ca97b67122de31ebe33bb762cb0de36bd66aa121a037cef0c0d0`이다.

## 실제 브라우저 비공개 프리뷰 검증 — 2026-09-12

- Vercel 팀 인증이 적용된 비공개 프리뷰에서 대표 HTML을 실제 Chrome 페이지로 로드했다. 프리뷰용 포장만 gzip 해제와 로컬 Three.js 제공을 담당하며 대표 HTML의 시뮬레이션 소스는 변경하지 않았다.
- 출항 전 VLS 편성 화면이 정상 렌더링됐다. `장거리 중시` 선택 시 `SM-2 84발 · ESSM 48발`, `표준 방공` 복원 시 `SM-2 72발 · ESSM 96발`로 즉시 갱신됐다.
- `출항 / 편성 확정` 후 2D CIC가 실제로 진행됐고 함속, 방위, SPY 상태, 지형·트랙 표시가 갱신됐다.
- 화면의 DEBUG 로그에서 `CORE SELFTEST PASS`를 확인했다. 브라우저 제어기의 격리된 읽기 평가 컨텍스트에서는 페이지 전역 `window.__CORE_SELFTEST_FAILURES__`와 `window.__NAVAL_SIM_DIAG__`가 노출되지 않아 해당 객체를 직접 호출한 결과로 기록하지 않는다.
- 3D 전환 시 프리뷰에 포함한 Three.js 0.158.0은 정상 로드됐다. 이후 `Error creating WebGL context`로 초기화가 중단됐다. 이는 Three.js 네트워크 로딩 실패가 아니라 현재 제어 브라우저의 WebGL 컨텍스트 부재이며, 따라서 이번 세션에서는 3D 장면 자체의 시각 검증을 완료하지 못했다.
- 브라우저 확장/로그인 과정의 외부 메시지를 제외하면 대표 HTML DEBUG 로그에는 `CORE SELFTEST FAIL`이나 페이지 런타임 예외가 없었다. 3D의 WebGL 환경 오류는 위와 같이 별도 기록한다.

## WebGL 비의존 3D 메시 검사도구 — 2026-09-12

- 별도 개발 도구 `AEGIS_MODEL_INSPECTOR.html`을 추가했다. 본 시뮬레이터의 화면·물리·센서 코드는 변경하지 않았다.
- 대표 HTML이 기존에 노출하던 읽기 전용 `window.__WIP148_3D_VIEW__`와 `window.__WIP200_MISSILE_CATALOG__`를 사용한다. 검사도구 안에 별도의 미사일 형상을 복제하지 않고 실제 `buildMissileMesh` / `buildEnemyAsmMesh` 결과를 가져온다.
- WebGLRenderer를 만들지 않는다. 실제 메시의 정점·인덱스·월드 변환·재질 색을 읽어 Canvas 2D에 측면·상면·정면·사시도의 네 투영으로 그린다.
- SM-2, ESSM, RAM, Kh-32, Kh-35U 전환, 사시도 방위·고각 조절, 삼각형 와이어 표시, 축·치수 표시, 측면 참고 이미지 로컬 오버레이를 지원한다.
- 실제 비공개 Chrome 프리뷰에서 다섯 모델을 모두 전환했다. 표시된 실제 메시 삼각형 수와 경계 치수가 갱신됐으며 페이지 오류는 0이었다. Three.js의 기존 전역 스크립트 사용 중단 예정 경고 1건은 렌더 실패가 아니며 후속 모듈화 후보로 둔다.
- 비공개 프리뷰의 무인 요청은 Vercel SSO로 302 전환되고 `X-Robots-Tag: noindex`가 적용됨을 확인했다.
- 기본적으로 같은 프리뷰의 대표 HTML을 읽고, 필요하면 `?source=`로 다른 동일 출처 HTML을 지정할 수 있다. 로컬 `three.min.js`가 없을 때는 동일 버전의 공식 CDN을 데이터 라이브러리로만 대체 로드한다.
- 검사도구 SHA-256은 `a2dba95ced52ec4024948a9a3c77a7fa98164fc9b0bb5a1b719b386b2cbe4fce`이다.

## WebGL 비의존 재질·텍스처 작업대 — 2026-09-12

- `AEGIS_MODEL_INSPECTOR.html`을 단순 메시 관찰기에서 재질·텍스처 작업대로 확장했다. 본 시뮬레이터의 물리·센서·형상 생성기는 변경하지 않았다.
- 실제 메시를 재질 단위로 분리하고 각 재질의 메시 이름, 삼각형 수, 원본 UV 보유율을 표시한다. 선택 재질 단독 표시도 지원한다.
- 재질별 기본색, 거칠기, 금속성, 투명도를 조절할 수 있다. 거칠기와 금속성은 WebGL 없는 Canvas 2D에서 근사 음영으로 미리 보되, 값 자체는 작업 JSON에 정확히 보존한다.
- PNG/JPEG/WebP 이미지를 선택 재질에 적용할 수 있다. 원본 UV, 미사일 길이축 기준 원통 투영, 측면·상면 평면 투영을 제공하며 혼합률, 가로·세로 반복, 이동, 회전을 조절한다.
- 작업 결과는 `AEGIS_MODEL_TEXTURE_WORKSPACE_V1` JSON으로 저장·복원한다. 텍스처 이미지도 data URL로 JSON 안에 포함하므로 이후 대표 HTML의 실제 재질 정의에 반영할 수 있다. 브라우저 보안상 검사기가 대표 HTML 소스를 직접 덮어쓰지는 않는다.
- 정적 JavaScript 문법 검사와 실제 Three.js 메시를 사용한 재질 분리·UV 수집·월드 변환·삼각형 텍스처 affine mapping 독립 검사가 통과했다. 현재 실행 환경에는 브라우저 실행 파일이 없어 이번 변경의 스크린샷 기반 육안검사는 수행하지 못했다.
- 변경 검사도구 SHA-256은 `b36935f90c10f596bdb96a25dffd725e33b8fecd38f94b2b479af16a96de07f2`이다.

## SPQ-9B 익명 관측 V34 작업 업데이트 — 2026-09-12

- SPQ-9B의 실제 객체 ID 기반 `trackId`/`truthRef` 전달과 객체별 재관측 타이머를 제거했다. 실제 객체는 sweep·LOS·Pd·RCS·측정 합성 경계 안에서만 사용한다.
- `spq9bAnonymousPlotContractV34`는 위치, 거리, 방위/고각, 방사속도, 오차, 품질과 센서 소스만 복사한다. `id`, `objectId`, `domain`, `truthRef`, `isASM`, 표적 이름은 연관 계층으로 넘어갈 수 없다.
- 공통 레이더 NIS 게이트로 기존 트랙을 선택하고, 미연관 plot만 `allocateTrackIdV31` 경로에서 독립 트랙을 만든다. 최근 SPY 측정이 있으면 SPQ plot을 같은 트랙에 소비하되 정밀한 SPY 상태를 덮어쓰지 않고, SPY가 오래되면 SPQ가 같은 트랙을 인수한다.
- 30 RPM·양면 안테나의 명목 같은-방위 재관측을 1초로 명시했다. sweep 판정을 반개구간 `(prev,new]`로 바꿔 프레임 경계 방위의 중복 plot을 막았다.
- 실제 소스 함수를 추출한 독립 런타임 검사에서 익명 신규 트랙, 최근 SPY와의 단일 트랙 수렴, 오래된 SPY 트랙의 SPQ 인수, 1 Hz 방위 재관측을 통과했다. HTML JavaScript 문법과 시작 자기검사의 익명 plot/sweep 계약도 통과했다.
- 사용자 화면 우하단의 임시 `DIAG` 버튼은 제거했고 내부 `window.__NAVAL_SIM_DIAG__` 검사 API는 유지했다.
- 상태는 **구현·문법·독립 연관 검사 완료 / 실제 브라우저의 SPY 정상·고장 시나리오 회귀 잔여**다. 변경 HTML SHA-256은 `4906c335ef99ca97b67122de31ebe33bb762cb0de36bd66aa121a037cef0c0d0`이다.

## SPS-73 익명 수상 관측 V35 작업 업데이트 — 2026-09-12

- SPS-73 운용 경로의 `surfaceTrackId(...)`, 실제 객체 기반 트랙 예약, `truthRef` 전달과 객체별 재관측 타이머를 제거했다. 실제 수상 객체는 안테나 sweep, 수평선/지형 LOS, RCS, 해면 클러터, Pd 및 거리·방위 오차 합성 안에서만 사용한다.
- `sps73AnonymousPlotContractV35`는 2D 거리·방위, 수평 위치, 오차와 품질만 통과시킨다. 객체 ID, 종류, 실제 레이더 높이와 이름은 제거되며 트랙 고도는 측정값이 아닌 고정된 수상 운동모델 기준 8 m를 사용한다.
- 한 회전에서 얻은 모든 plot과 기존 수상 트랙의 NIS 비용 행렬을 만들고 Hungarian 최소비용 1:1 배정을 수행한다. 진실 객체 배열 순서에 따른 선점과 근접·교차 표적의 불필요한 신규 트랙 생성을 줄였다.
- 미연관 plot만 독립 `trackId`/`trackUid`를 만든다. 신규·갱신 SPS 트랙에는 `truthRef:null`이 유지되고, 트랙 용량 200개는 수신할 실제 객체 수가 아니라 유지할 ARPA 파일 수에만 적용된다.
- 24 RPM 회전 주기 2.5초, 탐지 소실 후 6.5초부터 coast 표시, 마지막 측정 후 14초 drop을 사용한다. 실제 수상 객체의 `alive` 변경은 트랙을 직접 삭제하지 않는다.
- 사용자용 SPS 상태표에서 숨겨진 실제 수상 객체 수를 제거하고 `ARPA 관측 트랙/200`만 표시한다. 내부 진단에는 교차 표적 생성, truth 소실, 독립 SPS track-manager step을 추가했다.
- 실제 소스 함수 기반 독립 검사에서 익명 필드 방화벽, 순서 독립 1:1 배정, 독립 신규 트랙, 14초 TTL을 통과했다. 실제 EKF/NIS 검사는 동일 plot NIS 0, 6 km·8° 이탈 plot NIS 687.31(게이트 25), 수평 공분산 125000→2396.62 감소를 확인했다.
- 상태는 **구현·문법·독립 수치검사 완료 / 실제 브라우저 교차 항해·소실·재획득 시나리오 회귀 잔여**다. 변경 HTML SHA-256은 `4906c335ef99ca97b67122de31ebe33bb762cb0de36bd66aa121a037cef0c0d0`이다.

## 결론

**A의 코드 구현은 완료됐고 실제 브라우저 전수 회귀가 남아 있다.** SPY V31/V32/V36, 시각 V33, SPQ-9B V34, SPS-73 V35의 익명 관측과 A3 V37 상태·교전권한 연결이 적용됐다. 남은 것은 V36 장거리 편대 정밀계측, V32 전방위 실표적·교전, V33 시각 단독·SPY 융합, V34 SPY 정상·고장, V35 교차 수상표적·소실·재획득, V37 ID 버튼·모드별 발사 차단의 실제 브라우저 회귀다. 다음 코드 단계는 B(CIWS Closure)다.

## 항목별 확인

| 원래 번호 | 항목 | 판정 | 현재 코드 근거 |
|---|---|---|---|
| 1 | SPY의 실제 객체 기반 관측 연결 제거 | **완료** | V31의 `spySynthesizeAnonymousTruthPlotV31`은 실제 객체를 측정 합성 안에서만 소비한다. `executeSpyTask`는 탐색·전용 재방문 모두 익명 plot 배열과 `trackRadarAssociationNisV31`만 사용하며 `spyTruthForTrackId`, `NO_TRUTH_ASSOC`, SPY의 `truthRef` 전달은 제거됐다. |
| 2 | 트랙 ID와 실제 객체 ID 분리 | **SPY·시각·SPQ-9B·SPS-73 구현 완료 / 브라우저 시나리오 회귀 잔여** | 모든 미연관 센서 plot은 `allocateTrackIdV31`로 독립 키를 받고 역방향 truth 인덱스를 만들지 않는다. SPY V36은 dwell 전체를 최소 총 NIS로 1:1 배정해 편대 plot을 보존하고, 시각 V33·SPQ-9B V34는 공분산/NIS로 연관하며 SPS-73 V35는 한 회전의 거리·방위 plot을 최소 총 NIS로 1:1 배정한다. |
| 3 | 분류·식별·위협·권한 구분 | **V37 구현·런타임 검사 완료 / 실제 브라우저 UI 회귀 잔여** | `TRACK_RECORD_V37_A3`, `updateTrackOperationalStateA3`, `trackEngagementGateA3`가 센서 분류·위협평가·운용자 지정·교전모드를 분리한다. AUTO 판단부와 SM-2/ESSM 발사 함수가 `AUTO_AUTHORIZED`를 이중 확인하며 `FRIEND/NEUTRAL`, `UNKNOWN`, `UNASSESSED`, `WITHHELD` 자동발사를 차단한다. |
| 4 | SPY 허위 관측 입력 | **완료** | `spyFalsePlotV31`이 빔 방위·고각·거리·도플러 범위 안의 낮은 확률 extractor false plot을 만든다. 실제 반사와 같은 익명 배열, 연관 게이트, 미연관 tentative-track 생성 및 coast/drop 수명주기를 사용한다. 수평 탐색은 해면 클러터 배율을 적용한다. |
| 5 | CIWS 판단에서 실제 객체 의존 제거 | 미완료 | `evaluateThreats`(11061행)는 `enemyMissiles`를 순회하고 실제 위치·운동 상태를 사용한다. `updateCueing`도 실제 객체를 선택해 저장한다. 관측 기반 보조 함수가 있어도 상위 선택 경로의 분리는 끝나지 않았다. |
| 6 | CIWS 기동 예측 확장 | 제안한 확장은 미착수로 판단 | `ciwsStepLocalTrack`(10534행), `ciwsGunBallisticInterceptSolution`(10416행)의 확인된 예측은 위치·속도 중심이다. 다른 제어 계층의 가속도 추정이 있으므로 프로젝트 전체에 가속도 추정이 없다는 뜻은 아니다. 제안한 로컬 가속도·jerk 이력·예측 범위 연결은 확인되지 않았다. |
| 7 | CIWS 부분손상의 연속 성능 반영 | 미완료 | `ciwsHardwareHealth01`(10115행)은 연속 값을 만들지만 확인된 운용부 사용처는 작동 여부 임계값 검사다(11096, 11163행). 제안한 장비별 연속 저하 연동은 확인되지 않았다. |
| 8 | 피해→기능 의존 관계 | 부분 완료 / 추가 확장 보류 | 기존 기능 계수와 V29 상태 설명, V30 구역별 보수 전력이 있다. 전체 데이터 경로·냉각 의존 관계를 구현한 것은 아니다. 독립 펌프 고장·수리는 원래 묶음 밖의 추가 후보로만 둔다. |
| 9 | 3D와 시뮬레이션 경계 및 회귀 | 부분 완료 | V25 검사와 V28 관측 항목 보강이 있다. 정상/손상 함선의 3D·배속 비교는 통과 기록이 있지만 실제 표적·발사체를 생성하지 않는 시나리오다. 전체 센서·교전 상태의 순수성 증명은 아니다. VLS 공통 기하 함수는 6105행부터 존재하며 렌더러 객체에 직접 의존하지 않는다. 이름만으로 경계 위반으로 판단하지 않는다. |
| 10 | 다중 플랫폼 최소 준비 | 일부 기반만 있음 / 본격 구현 보류 유지 | 독립 트랙 번호는 도움이 되지만 자함 주요 상태는 전역이다. 기만체의 `ownerId`는 공통 플랫폼 소유권 계약을 의미하지 않는다. 이번 계획에서 Platform 구조 전체 재작성은 하지 않는다. |

## 복구한 작업 순서

1. ~~**A의 SPY 1·2번 잔여 경계**~~ — Track Association V31 완료. 타 센서 호환 어댑터의 truth 경계는 별도 추적한다.
2. ~~**A의 3번 계약 확인 후 4번**~~ — 기존 메타데이터 계약을 유지한 채 V31 허위 관측 완료. 교전수칙은 변경하지 않았다.
3. **B의 5번 → 6·7번.** 기존 관측 기반 함수의 존재를 상위 판단 경로 분리 완료로 오인하지 않는다.
4. **C의 8·9번 잔여 부분.** 기존 보수·배수 연결에서 멈추고 원래 제안 범위만 대조한다. 회귀 검사는 앞선 변경의 검증 수단으로 계속 사용한다.
5. **10번은 최소 준비만 유지.** 두 번째 완전한 플랫폼 추가 전까지 구조 전체 개편을 보류한다.

이 순서는 원래 합의한 계획의 우선순위를 복원한 것이며 각 항목의 구현 완료를 선언하는 문서가 아니다. 한 작업 묶음이 끝날 때 해당 번호의 완료 근거와 남은 범위를 갱신한다. 새 개선 아이디어는 이 순서에 자동 편입하지 않는다.

## 이번에 진행하지 않을 확장

- 독립 펌프 고장·정비 시스템.
- 보수 설비 종류별 세부 수리·부하·우회 공급 추가.
- 새 무장, 새 플랫폼, 새로운 교전수칙.

이미 적용한 V29·V30을 이번 점검에서 되돌리지는 않았다.

## Track Association V31 검증 결과

- 대표 HTML 직접 브라우저 시나리오: 통과. 20초/1200 tick에서 실제 저고도 ASM 1개가 `truthRef` 없는 확정 SPY 트랙 1개로 수렴했다.
- 익명 plot 통계: 실제 반사 258, 허위 4(강제 진단 2 포함), NIS 연관 247, 같은 주기 중복 억제 10, 최종 SPY 트랙 1. 페이지 런타임 오류 0.
- 핵심 자기검사와 독립 트랙 계약 검사: 통과.
- 상태 회귀: 정상 및 손상 함선, 1×/8×/64×, 3D OFF/ON 전 조합에서 동일 checkpoint 해시와 런타임 오류 0으로 통과.

## A 전수 감사 및 추적·교전 성능 검증 — 2026-09-11

대표 HTML을 `http://127.0.0.1:8765/` localhost 서버로 열어 고정 seed 브라우저 검사를 실행했다. 제품 복제본은 사용하거나 수정하지 않았다. 원본 SHA-256은 `e8533ef3f41563391c69dcd01c55c51cec8fbb9e525ea59ea0bc0d06ef4bec66`이다.

### 완료성 판정

- **A 전체: 미완료.** SPY, 시각 V33, SPQ-9B V34, SPS-73 V35의 운영 관측 경로에는 truth lookup/`truthRef` 전달이 없다. A3 운용 연동과 센서별 실제 브라우저 시나리오 회귀가 남았다.
- **A1 및 A4의 SPY 익명 관측/허위 plot: 구현 확인.** 확인된 SPY 트랙은 `associationDomain:null`이며, 같은 표적 주변의 확정 트랙 파편화 최댓값은 1이었다.
- **A2: 센서 구현 완료, 실제 시나리오 검증 잔여.** SPY·시각·SPQ-9B·SPS-73의 관측→연관→신규 트랙 경로는 객체 ID 없이 동작한다. `trackIdForTruthV27` 계열의 남은 호출은 무장 물리·진단·기존 항공 효과 경계와 분리해 최종 전수검사에서 다시 분류한다.
- **A3: 계약만 준비.** 식별·위협·교전권한 필드는 실제 교전 판단에 아직 연결되지 않았다.

### 추적 성능

| 조건 | 결과 |
|---|---|
| LOS가 충분한 4개 사례(20/30 km Kh-35U, 80/100 km Kh-32) | 4/4 확정 및 사격통제 품질 도달 |
| 평균 확정 시간 | 0.954초 |
| 평균 위치 RMS | 48.50 m |
| 최악 위치 P95 | 139.79 m |
| 확정 트랙 파편화 최댓값 | 1 |
| 35 km/20 m, 40 km/35 m 저고도 사례 | 확정 실패. 각각 초기 `earthQ` 0.183 및 0.420으로 지구 곡률/해면 클러터 경계에 위치하며 truth plot은 0 |

### 교전 성능과 발견 결함

- Kh-35U, 고도 18 m, 속도 230 m/s, 12·18·24 km 및 12개 방위각 사례를 실행했다.
- 10개 사례는 익명 SPY 트랙(`300000001`)으로 ESSM을 발사했고, 10/10 모두 근접신관 이력의 `PROX_DETONATION_KILL`, 표적 제거, 함정 무피격을 함께 만족했다. 신관 폭발 miss distance는 0.78~5.60 m였다.
- 2개 사례(+90°, -90°, 모두 12 km)는 트랙이 생성되지 않아 발사하지 못했다. 초기 LOS와 해면 클러터 품질은 정상이었지만 +90°는 선택 면 편향 60.04°/조향 이득 0, -90°는 편향 47.59°로 고정 탐색 래스터 ±45° 밖이었다. 이는 확률적 요격 실패가 아니라 **SPY 방위각 탐색 커버리지 틈**이다.
- 따라서 “발사된 교전의 종말유도”는 이번 표본에서 정확하게 작동했지만, “전방위 표적 추적·교전 성능”은 통과로 판정할 수 없다. 10/12를 무기 Pk 83.3%로 해석해서도 안 된다. 두 건은 센서 미획득이기 때문이다.

### 회귀 결과

- 페이지 런타임 오류 0, 검증 하네스 정상 종료.
- 독립 트랙 계약, 전력/손상통제 검사 통과.
- 정상/손상, 1×/8×/64×, 3D OFF/ON의 동일 checkpoint 해시를 다시 확인했다.
- 상세 원시 결과: `artifacts/a_validation_v32/results.json`; 재현 하네스: `.work/a_validation_v32/check.cjs`.

## 다음에 해야 할 작업

아래 순서는 이번 검증에서 실제로 확인된 결함과 A의 미완료 범위를 기준으로 한다. 각 단계는 구현과 검증을 함께 끝내야 완료로 처리한다.

### 1. SPY 전방위 탐색 커버리지 복구 — 구현 적용 / 직접 브라우저 회귀 잔여

- `WIP199_SPY_LAYOUT`에서 얻은 실제 면 중심각과 탐색 래스터의 방위 범위를 일치시킨다.
- 현재처럼 모든 면을 기계적으로 중심 기준 ±45°로 탐색하지 말고, 인접 면 중심각의 이등분선을 각 면의 탐색 경계로 사용하거나 그와 동등하게 360°를 빈틈없이 덮는 경계 테이블을 만든다.
- 면 중첩 구역에서는 같은 반사가 두 확정 트랙으로 성장하지 않도록 기존 NIS 연관과 같은-dwell 중복 억제를 유지한다.
- `faceOverlapDeg`는 조향 허용 범위에만 쓰고 탐색 래스터가 해당 중첩 범위를 실제로 훑지 않는 현재 불일치를 제거한다.
- 렌더링용 면 배치와 센서 물리용 면 중심을 임의로 분리하지 않는다. 기하 정의가 잘못됐다면 공통 정의를 바로잡고 3D 방향과 센서 방향을 함께 검증한다.

완료 조건:

- 고도 18 m, 거리 12·18·24 km의 표적을 최소 5° 간격으로 360° 배치했을 때, LOS가 유효한 모든 방위에서 truth plot과 익명 tentative track이 생성된다.
- 경계 방위각을 더 촘촘히 검사한다. 각 면 경계 전후 `-2°, -1°, 0°, +1°, +2°`에서 확정 및 사격통제 품질 도달 여부를 확인한다.
- 같은 실제 표적 주변의 확정 트랙 파편화 최댓값은 1이어야 한다.
- ±90° 재현 사례에서 더 이상 무획득/무발사가 발생하지 않아야 한다.

### 2. SPY 전방위 추적·교전 회귀검사 고정

- `.work/a_validation_v32/check.cjs`의 전방위 사례를 일회성 조사 코드가 아니라 반복 가능한 회귀검사로 유지한다.
- 센서 미획득, 사격통제 품질 미달, 발사 거부, 종말유도 실패를 서로 다른 실패 원인으로 집계한다.
- 요격 성공은 `표적이 배열에서 사라짐`만으로 판정하지 않는다. `PROX_DETONATION_KILL` 또는 구조파괴 이력, 표적 제거, 함정 무피격을 함께 확인한다.
- 고정 seed 결과와 여러 seed의 통계 결과를 분리한다. 단일 고정 seed 통과를 Pk 검증으로 표현하지 않는다.
- 지구 곡률, 지형 차폐, 해면 클러터 때문에 관측 불가능한 사례는 센서 결함과 분리해 기록한다.

완료 조건:

- 전방위 탐색 검사가 모든 유효 LOS 사례에서 통과한다.
- 익명 트랙을 지정한 ESSM 교전이 실제 객체 ID를 트랙 레코드에 복구하지 않고 끝까지 진행된다.
- 페이지 오류 0, NaN 0, 잘못된 발사 대상 0, 함정 오인 피격 0을 확인한다.

### 3. 시각 센서 익명 관측 전환 — 구현 적용 / 직접 브라우저 회귀 잔여

- 5979행과 5991행 부근의 `trackIdForTruthV27(...)` 및 `truthRef:trackTruthRefV27(...)` 전달을 제거한다.
- 시각 센서는 실제 객체를 광학 측정 합성 안에서만 소비하고, 이후에는 방위·고각·거리 추정 및 오차만 포함한 익명 관측을 제출한다.
- SPY 트랙과의 연관은 객체 ID가 아니라 공분산/NIS 게이트로 수행한다.
- 거리 정보가 약한 시각 관측이 기존 정밀 레이더 트랙의 거리 상태를 비현실적으로 덮어쓰지 않도록 측정 차원과 공분산을 분리한다.

완료 조건:

- 시각 단독 신규 트랙과 SPY 기존 트랙 결합 모두 `truthRef:null`, 독립 `trackId`, 고유 `trackUid`를 유지한다.
- 동일 표적을 시각/SPY가 동시에 관측해도 확정 트랙은 하나로 수렴한다.
- 시각 접촉 소실 후 실제 객체가 살아 있다는 이유만으로 트랙이 유지되거나 삭제되지 않는다.

### 4. SPQ-9B 익명 관측 전환 — V34 구현 적용 / 직접 브라우저 회귀 잔여

- 실제 객체 기반 `trackId` 및 `truthRef` 전달을 제거했다.
- 회전 안테나의 sweep 시각, 면/빔 폭, Pd, 측정 오차로 생성한 익명 plot을 공통 레이더 NIS 연관기로 보낸다.
- SPY와 SPQ-9B의 같은 표적 plot은 최근 SPY 상태를 우선하며 단일 트랙으로 수렴하고, SPY 상태가 오래되면 SPQ가 트랙을 인수한다.
- SPY 정상·고장 상태의 실제 표적 시나리오 회귀는 아직 남아 있다.

완료 조건:

- SPQ-9B 생성·갱신 트랙에 `truthRef`와 실제 객체 기반 키가 없다.
- 회전 주기보다 빠른 비물리적 갱신이 없고, 블라인드 구간에서는 coast/재획득 수명주기가 작동한다.
- SPY 정상/고장 양쪽에서 중복 확정 트랙과 잘못된 표적 병합이 발생하지 않는다.

현재 검증 결과:

- 익명 plot 필드 계약, 독립 트랙 ID/UID 생성, SPY 우선 수렴, SPQ 인수, 양면 안테나 1 Hz 재관측은 문법·시작 자기검사·독립 런타임 검사를 통과했다.
- 실제 표적을 두고 돌리는 SPY 정상/고장, coast/재획득, 잘못된 병합 확인은 브라우저 회귀 항목으로 남겨 둔다.

### 5. SPS-73 수상 표적 익명 관측 전환 — V35 구현 적용 / 직접 브라우저 회귀 잔여

- `surfaceTrackId(...)`/`truthRef` 기반 직접 연결을 익명 수상 plot 연관으로 교체했다.
- 수상 표적 크기, 실제 레이더 높이, 레이더 수평선, 지형 LOS와 측정 오차는 반사 합성까지만 사용한다. 2D plot에는 실제 표적 높이를 넣지 않는다.
- 한 회전의 모든 거리·방위 plot을 기존 수상 트랙과 최소 총 NIS로 1:1 배정한다. 미연관 plot만 독립 트랙을 만든다.
- 수상 트랙의 표시 번호·UID·분류는 2.5초 sweep과 14초 TTL에 따른 관측 수명주기로 유지한다. 실제 수상 객체의 `alive` 변경은 트랙을 직접 삭제하지 않는다.

완료 조건:

- SPS-73 트랙에 실제 객체 ID 또는 `truthRef`가 남지 않는다.
- 교차·근접 항해하는 두 수상 표적에서 ID swap, 병합, 트랙 복제가 허용 기준 안에 든다.
- 표적 소멸 후 즉시 삭제하지 않고 지정된 coast/drop 시간 뒤 종료한다.

현재 검증 결과:

- 익명 필드 계약, 실제 표적 높이 차단, Hungarian 충돌 배정, 독립 신규 트랙, 2D EKF/NIS, 2.5초 sweep과 14초 TTL의 정적·독립 런타임 검사는 통과했다.
- 두 수상 표적의 실제 교차 항해 전후 ID 연속성, 탐지 소실 후 coast/drop, 재등장 재획득은 브라우저 회귀 항목으로 남겨 둔다.

### 6. A3 상태 계약의 실제 운용 연결

- `classification`, `identity`, `threatStatus`, `engagementAuthority`의 갱신 주체와 전이 조건을 명시한다.
- 분류 신뢰도만으로 적성 식별이나 교전권한이 자동 부여되지 않게 한다.
- 센서 융합, 운용자 지정, 교전 모드가 각 필드에 어떤 권한으로 영향을 주는지 분리한다.
- 기존 교전 동작을 한 번에 바꾸지 말고 먼저 읽기 전용 판단/표시 경로에 연결한 뒤 MANUAL·SEMIAUTO·AUTO별 적용을 별도 검증한다.

현재 상태:

- V37에서 상태 전이, 운용자 식별 버튼, HUD/진단 표시, MANUAL·SEMIAUTO·AUTO 권한 분리와 VLS 자동발사 이중 게이트를 구현했다.
- 시작 셀프테스트와 전체 스크립트 런타임 하네스에서 인바운드 적성 자동허가 및 FRIEND 지정 자동발사 차단을 통과했다.
- 실제 브라우저에서 ID 버튼 순환 표시, 모드 전환, 수동/반자동/자동 발사 동작을 확인하는 UI 회귀만 남는다.

완료 조건:

- 상태 전이표와 코드의 실제 전이가 일치한다.
- `UNKNOWN/UNASSESSED/WITHHELD` 트랙에 자동 발사가 발생하지 않는다.
- 트랙 coast·재획득·alias 승계 과정에서 권한이 새 트랙에 무조건 복사되지 않는다.

### 7. A 완료 선언 전 최종 전수검사

- SPY·시각·SPQ-9B·SPS-73의 운영 경로에서 실제 객체 기반 트랙 키와 `truthRef` 전달을 다시 전수 검색한다.
- `trackIdForTruthV27` 호출은 진단/물리 효과 해석 등 허용된 경계와 금지된 센서-트랙 결합 경로로 분류해 목록화한다. 호출 수가 0이 아니라는 이유만으로 실패시키지 말고 용도를 확인한다.
- 실제 객체 소멸이 트랙 직접 삭제를 일으키는 경로를 모두 점검한다.
- 정상/손상, 1×/8×/64×, 3D OFF/ON 전체 회귀와 전방위 센서·교전 검사를 같은 대표 HTML에서 실행한다.

최종 A 완료 조건:

- 모든 센서가 실제 객체를 관측 합성 경계 안에서만 사용한다.
- 트랙 생성·갱신·융합·소실·재획득이 실제 객체 ID 없이 수행된다.
- A3의 네 상태 필드가 정의된 규칙대로 운용되며 교전권한 안전 조건을 통과한다.
- 전방위 유효 LOS 표적에서 센서 커버리지 틈이 없고, 중복 확정 트랙·잘못된 병합·잘못된 교전이 허용 기준 내다.
- 기존 전체 상태 회귀와 페이지 런타임 검사가 모두 통과한다.

### A 이후 작업

A가 위 조건으로 완료된 뒤에 B를 진행한다.

1. CIWS 상위 위협 선택에서 `enemyMissiles` 직접 순회를 제거하고 관측 트랙만 소비하도록 한다.
2. CIWS 로컬 추적에 가속도/기동 추정과 예측 범위를 연결한다.
3. CIWS 장비 부분손상을 탐색 범위, 추적 오차, 구동 한계, 발사율에 연속적으로 반영한다.
4. 이후 C의 피해→기능 의존 관계와 3D/시뮬레이션 경계 잔여 항목을 진행한다.
