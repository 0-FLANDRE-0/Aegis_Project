# TRACK-C — 트랙 수명·재획득·식별 근거 / C55·SPQ AIR

IMPLEMENTED: C-1 읽기 전용 view·사후 물리 계보, C-2 근거 수명 감사·alias 승계 제한, C55 자함/NPC·SPQ AIR ACTIVE 후보.

TESTED: 원래20개 회귀 작업, native364·paired42·UI213·WebGL8발/29검사, D1 30쌍, 통계60쌍/120회, 별도 native·정보 격리·수집 동등성 검사. 최종 검증 **PASS**.

APPROVED: **사용자 지시서 §5·§6의 조건부 승인 충족; 정확 기대값 승인5건, 허용 오차 변경0**.

UNRESOLVED: 남은 물리 재연관·중복은 아래 수치대로 보존한다. 모든 트랙의 영구적인 ID 무오류를 주장하지 않는다. 기존 C55 CMS 보호 latch, 수동 FRIEND/AIR IFF 수명 차이, 기존 SM-6/ESSM 표본 비명중은 임의 수정하지 않았다.

RELEASE: **검증된 산출물. PR/main 실제 병합 여부는 MERGE_READBACK.json의 원격 영수증이 최종 기준**. GitHub release·tag는 생성하지 않는다.

## 1. 기준과 변경 범위

기준 main `d328c941d71e39ef616d4136c70bed0eeebe7f06`, R4 HTML SHA `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`. 작업 브랜치 `track-c-lifecycle-a`.

제품: [Aegis_SIM_v48_WIP_TRACK_C.html](../../../../Aegis_SIM_v48_WIP_TRACK_C.html) · SHA-256 `3f2af4c1e18ef30ce4b8dfe4cc2b28f2b91cf96c62306e8f9c55df4a8c508c81`. SHADOW는 같은 폴더의 `Aegis_SIM_v48_WIP_TRACK_C_SHADOW.html`; 현재 C의 별도 비교용이며 기본 제품과 혼동하지 않는다.

실제 기존 함수 수정은5개(함수 occurrence 기준): SPQ AIR 수용1, own/NPC alias 재획득2, own/NPC C55 sensor sweep2. 여기에 읽기 전용 수명·근거 view와 관측 기반 solver 어댑터를 추가했다. `changes.diff`, `BUILD.json`, `SCOPE.json`에 전체 소스 변경과 역패치 증명이 있다. 역패치하면 기존 main 소스가 byte 단위로 복구된다. RF Pd/잡음/RCS/빔, native EKF 예측·보정/P·이득, IFF/ROE resolver, 무장·피해·함정 물리·AI 계수, 저장 스키마 변경 **0**.

C55의 기존 연관 gate는 미터였지만 축별 필터에는 `_c55P`가 있었다. 최초 감사의 ‘공분산 없음’ 가정을 정정하고 `PLAN_C55_ADDENDUM.json`을 ACTIVE 시험 전에 고정했다. 기존 거리 gate로 후보를 제한하고, 기존 corrector와 같은 P+R·R floor를 읽어 NIS를 계산한다. 공용 R4 solver·δ=1을 사용하며, 결과에 맞춘 계수·gate 조정은 없다. SPQ AIR는 기존 native NIS/교차 domain gate와 SPY 우선 추가-hit 억제를 보존한다.

## 2. 수명·독립 관측·식별 계약

전체 감사와 baseline 소스 위치·SHA는 `AUDIT.md`, `SOURCE_AUDIT.json` 및 `evidence/source-audit/`에 있다. player/NPC TrackStore의 native confirmation·age/TTL·memory/coast/drop·owner별 예측/수용 순서를 그대로 읽는다. contributor가 `receivedAtS` 또는 독립 fix 시각을 저장하지 않으면 null로 표시하며, 수신/재전송/ISAR를 새 위치 hit로 만들지 않는다.

3D AIR 실측 증거의 기존16초 계약을 유지한다. 2D 수상의8m는 모델 prior이며 관측 고도가 아니다. 운용자 FRIEND 지속성과 AIR IFF 만료는 바꾸지 않는다. IFF 무응답으로 HOSTILE을 새로 부여하지 않는다. classification·identity·threat·authority·IFF·실제 발사 근거·CMS 보호를 분리해 표시한다. 기존 ISAR `identificationEvidence`·교전 로그는 그대로이며, C view가 모든 예전 UI/증거 포트를 대체하지는 않는다.

alias 승계는 기존 관측 위치/속도 gate 안에서 **전임 파일 하나와 후속 확정 파일 하나**로 구별되는 경우에만 기존 BDA/FCS/참조 이전을 허용한다. FRIEND/NEUTRAL/TRAINING·유효 IFF·tentative/memory/reacquiring·모호한 전임/후속에서는 승계를 막는다. 예전 classification/identity/operator/IFF/authority를 새 파일에 복사하지 않는다.

콘솔: `__TRACK_C__.snapshot()`; 진단을 시작할 때 `__TRACK_C__.configure({enabled:true}); __TRACK_C__.clear()`; 수명 변경 샘플은 `__TRACK_C__.sample()`. 기본 OFF. 진단은 게임 저장에 넣지 않으며, 새 세션/불러오기 후 장기 진단을 이어갈 때는 `clear()`로 새 기록을 시작한다.

## 3. 전투 통계 — 사전 계획 그대로

`PLAN.json`의 시드/조건/판정을 첫 실행 전에 고정했다. R4/C 같은60쌍, 각 제품 초기 ASM320발; D1은 별도30쌍이다. 6발×20,13발×10,2발/3발/교차×각10. 최대600 simulation초, 초기 ASM 전부 native 종말 또는30km 밖으로10초 연속 이탈 후5초 안정화까지 실행한다. 시험이 물체를 강제 삭제/격추하지 않는다. HP를 승인 판정에 사용하지 않는다.

|주 판정|R4|C|C−R4|총 차이95% paired 구간|one-sided exact harm p|판정|
|---|---:|---:|---:|---|---:|---|
|초기 ASM의 실제 함 접촉/유출|24|15|-9|[-19.0, 0.0]|0.968750|WITHIN_USER_SAMPLING_VARIATION_OR_BETTER|
|피해가 있는 native 피격 콜백(잔해 포함)|30|21|-9|[-29.0, 7.0]|0.812500|WITHIN_USER_SAMPLING_VARIATION_OR_BETTER|

20개 seed block의 exact sign-flip와 고정 seed20261102·200000회 층화 paired bootstrap이다. 사전 허용 오차 없는 정식 noninferiority 증명으로 해석하지 않는다. 사용자 지정 ‘시드 간 변동 범위 안/악화 없음’ 규칙이며 원시 p와 모든 시드 차이를 남겼다.

|조건|시드 쌍|R4 격추/유출/피격콜백/이탈|C 격추/유출/피격콜백/이탈|
|---|---:|---|---|
|S6|20|111 / 1 / 4 / 8|110 / 2 / 2 / 8|
|S13|10|71 / 23 / 26 / 31|84 / 13 / 19 / 29|
|TWO|10|20 / 0 / 0 / 0|20 / 0 / 0 / 0|
|THREE|10|30 / 0 / 0 / 0|30 / 0 / 0 / 0|
|CROSS|10|20 / 0 / 0 / 0|20 / 0 / 0 / 0|

전체 표·per-seed 결과·각 종료시각은 `STATISTICS.json`. native 해면/수명/지형 등 기타 종말은 각 METRICS `initialOutcomes`의 원래 사유로 남는다. 개별 불리/유리한 시드를 제외하지 않는다. 침수는 native 종료시각의 보조값이며 별도 모델로 시간 보정하지 않는다.

## 4. 사후 물리 계보

물리 label은 테스트 빌드의 AFTER_ACTION private 저장소에서만 사용한다. 실제 echo/측정 객체 또는 owner·sensor·tick·정확한 측정 fingerprint로 연결하며 가까운 truth로 추정해 붙이지 않는다. standalone HTML에는 물리 label hook이 없다. 알고리즘·KF·식별·권한·AI가 이 결과를 읽는 경로도 없다.

|진단 사건(전체120회)|R4|C|
|---|---:|---:|
|실제 수용된 KF UPDATE|827850|814018|
|추가 hit 없는 메타데이터 연관|13877|12773|
|KF 계보와 다른 메타데이터 연관(필터 오병합에 합산 안 함)|68|50|
|이미 confirmed인 파일의 생존 물체 간 KF 재연관|23001|14152|
|확정 전 물체 재연관|5023|4077|
|동시에 확정된 중복 파일 쌍|2197|1239|
|같은 epoch의 상호 ID 교환(confirmed)|891|364|
|같은 물체의 native memory 재획득|852|778|
|native DROP 후 재생성|0|0|
|비자함탄→자함탄 보호 오염|0|0|
|관측된 자함 발사탄 보호 상실|0|0|
|실제 ASM을 자함 발사체로 잘못 표기|0|0|
|기존 처리부 오경보 — 반사체 없음, 정확 생성 이력 검증|6|4|
|출처 미해결 측정 레코드|0|0|
|정확한 측정 fingerprint 충돌|0|0|

confirmed 파일 생존 물체 재연관 /1000 실제 KF UPDATE: R4 **27.784**, C **17.385**. 각 실행의 관측 수·종료시각이 다르므로 원시 개수만으로 동일 노출시간의 오류율이나 통계적 우월성을 주장하지 않는다. owner와 C55 mount store를 섞어 중복으로 세지 않는다. 중복은 같은 owner/store의 확정·비memory 파일 쌍이며 C55는 기존 .22초 freshness도 적용한다. 추가 hit 없는 SPQ 연관은 별도 집계하며 KF 물리 계보를 덮어쓰지 않는다. 전임 생존을 모르면 죽었다고 가정하지 않는다. 세부 정의와 전체 사건은 `LINEAGE_RESULTS.json` 및 각 실행의 `LINEAGE_ANALYSIS.json.gz`.

처음 RF 반사체 연결이 없었던 R4 6건/C 4건은 기존 `spyFalsePlotV31`의 receiver/processing 오경보였다. 추가10회 인과 재현에서 생성 tick·source·거리/방위/고각/도플러가 모두 정확히 일치하고, 원래 전투 final·전체 사후 계보·private RNG도 동일했다. 실제 반사체가 없으므로 physical UID를 날조하지 않았으며, 원본 UNLINKED 기록과 생성 증거를 함께 보존한다(`NOISE_ORIGIN_CLOSURE.json`). 계보 감사는 반사체 연결 또는 이 정확한 무반사체 생성 증거로 출처를 닫고, 실제 native noise KF 생성 횟수도 업데이트 분모에 포함한다. 미해결 측정을 단순 제외하거나 거리로 오경보 추정하지 않았다.

HOLD는 별도 batch record·다음 native 갱신·native 무장 발사/명중 시각으로 검토했다. 13개 연결 native fixture는13개 모두 연관하고, 구별 불가능한48개는48개 HOLD했다. 일반적인13발 포화가 크기만으로 모두 중단되는 정책으로 바꾸지 않았다. 원래 공용 solver의 큰 성분 정책을 그대로 사용한다. C55 후보 HOLD/선택 record와 기존 SPY의 full hold-duration record는 raw에 남아 있다.

이탈 원인(분류만; 시커 수정0):

|사후 분류|R4|C|
|---|---:|---:|
|DECOY_LURE|0|0|
|SEEKER_LOSS|36|34|
|OTHER|3|3|

DECOY_LURE는 실제 수용된 Nulka/채프 위주 신호와 유지된 RF 유도를 근거로 한다. SEEKER_LOSS는 native SEARCH/REACQUIRE/유효 track 상실이다. 혼합 echo·coast·그 밖의 경우는 OTHER로 두고 원래 신호 전이/사유를 기록했다. 반사 신호의 마지막 선택을 유일한 반사실적 원인이라고 단정하지 않는다.

## 5. D1·상속 이슈·승인

D1:30쌍 모두 native 종말. 물리 유출4→4, 피해 콜백4→4, 격추22→22, 이탈0→0; 두 주 판정의 모든 시드 차이는0이다. 기존 helper `shipHits`8→8에는 `miss:true,dmg:0` 네 건씩이 포함되어 별도로 보존했다. 판정 입력은 B와 같은 실제 접촉/피해 callback이다(`D1_ANALYSIS_CONTRACT.json`, 후보 결과를 보기 전에 정의).

새 내부 서명 차이는419015/419026 두 건. `D1_CAUSE_REPORT.md`와4회 원인 재현에서 원래 전체 signature가 모두 정확히 재현됐다. 첫 차이는 같은 RF 관측의 거리 우선→native P+R NIS 선택이다.419026 RAM 발사는최대13tick 늦고 Phalanx는10tick 빠르며, 실제 후속 기하·피해 RNG 분기가 다르다. 모두 동일하다고 숨기지 않았고 raw leaf 차이를 보존했다. diffuse 공분산 파일을 선택하는 성향은 명시한 한계이며 보정 계수를 추가하지 않았다.

419025는 여전히 실제 피격1건이다. ‘무피격으로 고침’으로 표시하지 않는다. 과거 friendly-contact의 CIWS 성분 분리 시험과 현재30시드 통과를 근거로 지시서 조건 충족 시 기대 결과를 승인한다. 보호 오염을 고쳐 실제 사격·피해·후속 교전 분기가 달라진 경로이며 Pd/Pk/피해 RNG를 보상하지 않았다.

상속 observer2건은 CG_TURRET_A→FRIENDLY_CONTACT_A의 DDG/CG raid observer 차이다. 최근3D 실측을8m prior로 덮지 않는 기존 승인 범위의 원인이다. 과거 물리·combat RNG·선체·재고·offboard·fault 검사는 정확히 같고 observer만 다르다. 옛 raw와 이전/새 값·hash를 승인 파일에 보존한다. 현재 C↔R4 paired42는 기대값 갱신 없이 이미42/42이다.

구형 EMCON UI14는 사용자 명시 승인으로 **폐기**한다.14개 PASS로 계산하지 않는다. `EMCON_RETIREMENT_MATRIX.md`에 옛7항목×두 크기와 현재 UI213·native27·추가 실제 DOM36검사의 대응을 기록했다. 제거된 LOCK/FIRE 노드를 되살리지 않았다.

정확 승인 기록: APPROVED_EXPECTATIONS.json(5건), APPROVED_COMPARISONS.json. reviewed HTML/main SHA·통계/검증 SHA가 같을 때만 적용하고 다른 기대값/허용 오차는 바꾸지 않는다.

## 6. 회귀와 보존 검수

|검수|결과|
|---|---|
|native13 / paired|364/364 +42/42, 원래 단언 변경0|
|구형420건 체계|현재406/406 +구형 UI14폐기;420/420으로 과장하지 않음|
|UI / 현재 EMCON|213/213 +36/36;native EMCON27/27|
|실제 WebGL|8발·29/29,8회 모두 실제 render frame 증가;8발의 native final이 과거 동일 R4 제품과 정확히 같음|
|직접 C native|ACTIVE40/40,SHADOW37/37;truth poison read0|
|익명 ingress|기존47검사×R4/C OFF/C ON; 전체 출력·물리/private RNG 같음|
|owner·ENV|실제 출항 DDG+아군 CG 두 owner, 각600tick 한 번씩;R4/C OFF/C ON 상태·private RNG 정확히 같고 복원 후 ENV match:true|
|NPC C55|DDG6km,CG6km 및CG2km 실제 로컬 RF; 자함탄 보호 유지·오염0,각3600tick|
|자연 헬기·하푼 /AUTO IFF /idle120|새 R4와 C 전체 native 출력 정확히 같음; 자율 아군 사격/불명령 탄 소모0;idle truth hash 동일|
|배속·저장|기존 ISAR/하푼1/8/16/64 fixed 결과, 실제 발사,85검사 헬기 codec/불변·migration·roundtrip 등 통과|
|진단 수동성|R4↔SHADOW, C OFF↔ON native final·private RNG 정확히 같음|
|로그 분리 저장|R4/C 모두 이전 최종상태·사후 계보 값 전체·private RNG 정확히 같음; 조각 SHA/무손실 gzip 검증|

표의 전체 기계 판정과 입력 SHA는 `VALIDATION.json`. ‘관측 있음’과 ‘기존 native 판정에서 성공함’을 구별했다. WebGL 표본의 SM-6/ESSM 비명중 사유(LOW_SPEED /TERMINAL_MISS_POST_CROSS)는 R4와 같고 이번에 조정하지 않았다.

## 7. 실행 환경·비용·재현

고정 Chromium/Playwright headless, 협력 heavy browser slot 최대2, cgroup4CPU/16GiB 상한. 시험용 기록·직렬화 비용이 포함되므로 폰 FPS나 게임 자체 프레임 개선 수치로 해석하지 않는다.13개 native solver fixture 약3.2ms,48개 완전 모호 fixture 약14.5ms는 단일 호스트 표본일 뿐, 실제 폰 성능 기준이 아니다.

통계 최초 착수부터 이 보고서 생성까지 **91.00분**, 전체 지시서 수신부터 **208.94분**. 전체4시간 상한은 계속 유지한다. 최종 push/readback/병합 시각은 별도 영수증이 확정한다. 초기 revision의 OOM 미완료·테스트 setup 오류·수정 전 자료를 `evidence/attempts/`에 보존하고 최종 통과 수에 넣지 않았다.

13발 초기 R4는 기존 exporter의10MiB 한도, C는 전체 큰 로그를 반복 stringify하던 브라우저 메모리 한도에 걸렸다. 완료/미완료를 보존하고 simulation 종료 **후** AFTER_ACTION 값을 별도 스트림으로 내보냈다. 기존10MiB 한도와 legacy roundtrip·native 성공 판정은 바꾸지 않았다. root/candidate record를500개씩 나눠 UTF-8 SHA를 확인하고 무손실 gzip으로 저장했다. failed attempt1은 남고 같은 seed/product/helper의 attempt2를 선택한다. 그 밖의 정상 실행은 다시 골라서 대체하지 않았다.

재현은 새 작업사본에서 `regression.py --run`, `battles.py --run --resume`, `analyze.py statistics`, `analyze.py lineage`, `validate.py --strict` 순서이다. 원본 evidence를 덮어쓰지 않는다. 원래 repository 테스트·Python/Playwright/Chromium 의존성이 필요하고 게임 HTML과 시험 환경은 별개이다. `DIRECTIVE.md`, `PLAN.json`, `BUDGET.json`, JOB/PLAN/PHYSICAL_PROBE/EXPORT_TRANSPORT/EXECUTION·각 source/hash가 함께 제공된다.

## 8. 남은 범위

모든 물리 ID 오류 제거, C55 CMS 보호 latch 재설계, 수동 FRIEND와 AIR IFF 만료 통합, ASM 시커 수정, HP 지표 수정, OODA·TRACK-D는 하지 않았다. 고도 없는 데이터의 날조·ESM 거리 추정·ISAR 위치 hit·truth 기반 식별/연관·무장/피해 계수 조정도 없다. **남은 오류 개수와 재현 조건을 보존한 범위 승인**이며, 무오류 추적 엔진 완성 선언이 아니다.
