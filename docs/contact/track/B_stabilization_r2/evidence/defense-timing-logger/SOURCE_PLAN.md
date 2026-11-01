# 실제 방어 관문 반환 관찰기 — TEST ONLY

`extension.js`는 제품에 내장하지 않는 수집기 확장이다. API는 `window.__DEFENSE_CAUSE__.install()` / `.snapshot()`이다. 설치 전에는 실제 게임 함수 바인딩을 바꾸지 않는다. **원래 battle.js의 install/source receipt 수집 직후** 설치한다. 브라우저 실행·OFF/ON guard·원시 결과 해석은 audit_ciws가 담당한다.

- 12~26초, receiver-local track `300000003/4`의 **실제** `wip119EvaluateRow` 실행 문맥에서 FCQ 및 A3 원 반환만 관찰한다. `confirmed/memActive/reacquiring/FCQ/threatStatus/_a3AuthorityReason`, recommendation·plan·브레이크·limit/reserve의 명시적 scalar whitelist를 저장한다. `Infinity/-Infinity`는 문자열로 보존하며 값0과 필드 부재를 구분한다.
- 같은 구간의 실제 response-memory 갱신, pending/FireOne/취소 반환과 기존 response map·자체 배정 SAM 상태·VLS release state를 읽는다. Response/DecisionTrack/refresh/공분산·planner·RF·NIS·KF·무장 함수를 새로 조회하지 않는다.
- 90초 전체에서 실제 `trackBSelectB` 반환에 12개 초과 성분이 있으면 **실제 input graph와 실제 소비 반환**을 복사한다. i/id/NIS, native sanity/evidence scalar, gate, 성분의 전체 plot/track 배열·인증/잔여해결 필드가 대상이다. solver를 재실행하지 않는다. 물리 truth는 이 자료에 없다.
- 실제 `simulateFixedTick` 반환 뒤1Hz로 EW execution의 기존 scalar/own command flags, 현재 chaff·active-decoy pose/RF scalar, 살아 있는 ASM의 기존 pose·시커 scalar를 **별도 `afterActionSnapshots`**에 저장한다. `AFTER_ACTION_TRUTH_TEST_ONLY`, `neverTacticalInput:true`와 raw world 단위 metadata를 붙인다. EW 준비·decoy·seeker 초기화·pose/aim helper를 호출하지 않는다. 이 자료는 실제 EW/시커 이력 조사용이며 전술 판정의 입력이 아니다.

모든 wrapper는 원 함수를 원래 `this/args`로 정확히1회 호출하고 원 반환 객체·원 예외를 그대로 보존한다. 원본 row/plan/track/시커 객체는 수정하지 않는다. 관찰 데이터만 복사한다. 함수 source receipt는 wrapper 직전의 실제 설치된 함수 문자열이며, Select/tick은 기존 battle wrapper일 수 있음을 snapshot에 명시한다. 실제 제품 원함수 receipt는 `battle.nativeSources`와 함께 확인해야 한다.

cap은 일반 record12000, 큰 graph256, 사후1Hz256, fault64다. 누락은 `dropped/graphDropped/afterActionDropped/faultDropped`로 별도 계수한다. cap에 닿은 자료를 완전한 원인 증거로 취급하지 않는다. logger가 꺼진 원래 실행과 전체 native/passive state 및 global/private RNG guard를 통과하기 전에는 결과를 해석·승인하지 않는다.

로컬 정적/가짜 함수 검증: `node --check` PASS. 실제 게임을 실행하지 않는 mock에서10항목 PASS(설치 전 비활성, 중복 install 무효, 호출1회·this/args/반환 identity, 원 예외 identity·문맥 복구, 입력 상태 불변, graph whitelist, logger fault0, post-tick 사후 분리, Infinity 표기, 값0 보존). 이는 실제 native 게임 동등성 검증이나 회귀 통과를 대신하지 않는다. 이 작성자의 브라우저 실행0회, 제품·기대값 수정0이다.
