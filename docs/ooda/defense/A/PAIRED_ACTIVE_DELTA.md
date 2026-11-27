# DEFENSE_OODA_A paired ACTIVE 차이 분류

- 원시 suite 상태: **FAIL** (8 assertions; 증거 보존)
- 분류: **EXPECTED_ACTIVE_DIAGNOSTIC_DELTA**
- §9-4 유효 게이트: **PASS**
- 기대값 갱신: 0 · 허용오차 변경: 0 · 게임 상수 변경: 0

## 인과

The inherited raid supplies one diagnostic measurement. Legacy H1 releases immediately; DEFENSE_OODA_A reaches READY after its frozen service delay, when the one-shot track no longer meets downstream WIP119 FCS quality. No OODA authority or radar ownership is added to bypass that gate.

paired raid는 16 km Kh-32 8개에 대한 진단용 단발 측정이며 1,920 fixed ticks(32초) 안에 표적·요격체 종말 결과가 하나도 없다. 기준선은 즉시 7발을 사용했고 ACTIVE 후보는 동결된 OODA 지연 후 `FCS_QUALITY` 하류 게이트에서 보류했다.

## 자연 센서 대조군

With a native sensor-updated Kh-35U track, both DDG and CG reached OODA READY, released two native ESSM rounds after READY, and recorded PROX_DETONATION_KILL with zero ship hits.

원시 FAIL을 PASS로 다시 쓰지 않는다. 최종 요약에는 raw failure와 §9-4 분류를 별도 필드로 유지한다.
