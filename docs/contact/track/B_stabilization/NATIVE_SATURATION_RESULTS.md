# 실제 native 포화 경계 검증

최종 제품에서 실제 surface NIS→core→NPC caller→필터 갱신 경로를 검증해 **PASS**했다. old B/SHADOW/ACTIVE3개 fresh context 실행 시간은 49.63초다. 제품·moduleec66·계수·기존 기대값은 변경하지 않았다.

| 제품 | clear13 선택 / HOLD / 미소비 / correction / birth | clear16 | equal13 |
|---|---|---|---|
| baseline | 0 / 13 / 13 / 0 / 0 | 0 / 16 / 16 / 0 / 0 | 0 / 13 / 13 / 0 / 0 |
| shadow | 0 / 13 / 13 / 0 / 0 | 0 / 16 / 16 / 0 / 0 | 0 / 13 / 13 / 0 / 0 |
| active | 13 / 0 / 0 / 13 / 0 | 16 / 0 / 0 / 16 / 0 | 0 / 13 / 13 / 0 / 0 |

old B42/42, SHADOW42/42, ACTIVE44/44. 각 빌드에서 의도한 소비/보류 결과를 따로 검사한 신규 fixture 수이며 기존 도메인420의 통과 수에 더하지 않는다.

13/16 grid는 receiver-owned 초기 추정 위치 x=4000+i×80m, y=0, surface prior z=8m, Pxy=225m²다. 익명 입력은 x+1m이며 기존 S.surface의 rangeσ15m·azimuthσ0.1°·Dopplerσ3m/s를 변경하지 않았다. 실제 native seed caller에서 gate64를 캡처한 뒤, 실제 surface-position NIS로 사전 조건을 확인했다.

| 조건 | 실제 연결 성분 | eligible edges | 첫 대각 NIS | 첫 인접 NIS |
|---|---:|---:|---:|---:|
| clear13 | 13 | 59 | 0.002222222222 | 13.868888888889 |
| clear16 | 16 | 74 | 0.002222222222 | 13.868888888889 |
| equal13 | 13 | 169 | 0.002222222222 | 0.002222222222 |

clear13/16은 원래12개 경계보다 큰 실제 연결 chain이다. ACTIVE는 원래 NIS의 grid diagonal13/16개를 선택하고 원래 surface EKF를 파일당 정확히 한 번 실행했다. 관련 native associated 통계도13/16 증가했으며 새로운 tentative file은0, 기존 ID는 모두 유지됐다. 새 source/gain/filter를 만들거나 값을 조정하지 않았다.

같은 위치에13개 파일·13개 plot을 둔 음성은 모든 NIS가 같다. 모든 제품이 HOLD13·correction0·birth0을 유지했다. ACTIVE/SHADOW trace에는 각각 clear case의 LARGE_COMPONENT_CERTIFIED와 equal case의 LARGE_COMPONENT_UNCERTIFIED_HOLD가 실제 기록됐다.

HOLD 파일의 초기 last-observation age0.5s와 측정 시각을 보존했고 accepted correction만 age0과 독립 hit1회를 추가했다. 0.5s는 명시한 receiver-owned fixture 초기 상태다. 자연 RF가 그 age를 만들었다거나 동기식 batch 도중 시간이 지났다는 뜻이 아니다.

다른 private owner와 전역 canonical store는 바뀌지 않았다. synthetic 비열거 canary getter의 금지 target-property 읽기는0이었다. 실제 물리 target truth 객체를 만들거나 association으로 전달하지 않았다. pass-through 두 함수는 원래 함수를 각각 한 번 호출하고 finally에서 복원했으며 모든 실제 복원 flag가 true다. query/private physical·filter/P·RNG 불변, snapshot, 실제 ENV status, core self-test·진단 오류 검사를 모두 통과했다.

SHADOW의 fixture별 전체 private 상태는 old B와 정확히 같았다. equal13의 전체 private 상태도3개 제품 모두 정확히 같았다. clear13/16 ACTIVE의 갱신 차이는 원시 결과에 그대로 보존했다.

이것은 명시한 추정 prior와 익명 측정을 사용하는 실제 native 경계 시험이다. RF echo 생성·탐지율 또는 자연전투 증거로 세지 않는다. 별도로 실행하는13기 natural RF 사례와 함께 읽어야 하며, 기존 solver47의 포화 정책 교체 strict 차이1건을 자동 승인하거나 기대값을 갱신한 것이 아니다.

소스 위치·함수 scope SHA·실제 gate 문자열은 PROVENANCE.json에, 모든 초기 상태/P·실제 NIS행렬·선택/HOLD·원래 필터 호출·age·canary·private 상태는 각 raw-before-aux.json.gz에 보존했다. 요약은 NATIVE_SATURATION_SUMMARY.json 및 evidence/native-saturation/SUMMARY.json이다.

controller 종료와 공유 lease 반환을 확인해 audit_ciws에 lane을 반환했다. 이후 추가 브라우저는 실행하지 않았다.
