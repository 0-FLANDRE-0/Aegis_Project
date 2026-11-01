# R4 원래 회귀 최종 결과 — FAIL, 미승인 차이 보존

고정 ACTIVE `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`, SHADOW `3c7d2490e7e0d6fe94452e43d8f22132fbdd8add83986208bf7173068c478444`에서 원래17job을 모두 새 실행했다. R2/R3의 미실행 광역 자료를 통과로 재사용하지 않았다. 원래23개 source/helper·단언·기대값·허용오차 및 제품은 변경하지 않았다.

| 검사 | 실제 결과 |
|---|---|
| 원래 native13 suite |364/364 PASS |
| 기존 paired6case |36/42, FAIL6 |
| domain420 설명 |400 PASS /6 FAIL /14 legacy UI INCOMPLETE |
| D1 30고정시드 |A exact29/30, 전달 B·R1 exact30/30 |
| 기존 UI |213/213 PASS |
| 자연 탐지→LOCK→정식 VLS→full fixed tick→실제 WebGL |8발 실행, 원래29/29 PASS;8개 격추 주장은 아님 |
| 남은16job 환경 중단/OOM 증가 |0 /0 |

paired는 기존 DDG/CG samePhysicalState·sameExistingObserverState4건과 새 raidInventoryDeltaBounded2건이 실패했다. 마지막 이름의 실제 검사는 물리적 상한이 아니라 **loaded VLS cell 수의 정확한 동등 비교**다. A/B/R1→R4는 DDG90→89, CG115→114로 각각 SM2 한 발 추가 소비·현재 SAM 한 개 추가가32초 말에 있다. 해당 exact 비교를 완화하거나 새 baseline으로 승인하지 않았다.

같은32초 자료에서 HP100·물0·module damage0·초기 Kh-32 8개 alive·intercept기록0은 모두 같지만 native 종료까지 본 전투가 아니다. 누적 발사 시각과 shipHitHistory 건수도 원 수집기에 없다. 이 자료로 재사격 단독 원인, 최종 전투 품질 또는 정상 변화 승인을 주장하지 않는다. [첫 phase 검토](PAIRED_FIRST_PHASE_REVIEW.md)에 실제 기준·네 버전 수치·한계를 기록했다.

D1은419012 서명만 A와 달라 이전 미승인 실패를 그대로 유지했다. 실제 선택된 전투/자원 요약은 A/B/R1과30/30 동일하지만 원 strict 검사를 대체하지 않는다. 419025는 기존과 같은 피격 FAIL(HP6.8465988426)을 보존했다. 이전 CG→friendly observer2 차이도 별도 미승인 이력이며 새로 승인하지 않았다.

원래 회귀의 strict 실패는 총7개(paired6+D1419012)이며 전달 B/R1보다 새로 추가된 것은 재고 exact2개다. 별도 guarded 자연6에서 확인된 HP 악화는 이 회귀 완료와 독립적인 material 전투 퇴행이다. **후보·기대값·release 승인은 하지 않는다.**

실제 controller/worker는 모두 종료했고 종료 직후 두 shared browser lease를 각각 nonblocking 획득/반환하여 FREE를 확인했다. 이후 contract_tests의 사전 승인 smoke에 lane을 넘겼다. 누적 controller 승인 phase wall1624.63초(27.08분), 마지막 재개 phase1441.65초(24.03분), 서로 겹치는 worker wall 합3056.32초(50.94분)다. phase 사이 대기·다른 agent 작업시간은 이 수치에 포함하지 않는다. 속도 향상·휴대폰 FPS 또는 성능 비교 근거로 쓰지 않는다.

메모리 전용 supervisor는 원 controller `ac73be71…a2a797fd`를 변경하지 않고 원 execute를 같은 인자로1회 호출했다. 각 남은16job 시작 직전과 종료 후 공유 cgroup 메모리/events만 기록했으며 OOM·OOM kill 증가0이다. 연속 peak 측정이나 개별 제품 메모리 사용량 추정은 아니다. 첫 paired phase에는 후속 supervisor를 소급 적용하지 않았다. 원 raw 결과/status를 덮어쓰지 않았다.

- [REGRESSION_RESULTS.json](REGRESSION_RESULTS.json): 원래17job의 authoritative 실행 결과.
- [FINAL_COMPARISON.json](evidence/regression/FINAL_COMPARISON.json): 읽기 전용 집계·원자료 hash·메모리 receipt·완료/미승인 구분.
- [PRODUCT_SOURCE_PROOF.json](evidence/regression/PRODUCT_SOURCE_PROOF.json): 실제 packed main/module/BUILD/SCOPE7개 검사 PASS.
- [paired-four-version.json.gz](evidence/regression/paired-four-version.json.gz): A/B/R1/R4 모든 leaf와 원 strict 검사.
- [D1 비교](evidence/regression/d1/COMPARISON.json):30개 seed의3기준 서명·전투 요약·전체 leaf 경로.

`FINAL_COMPARISON.evidenceComplete=true`는 고정 제품의 요청된 실행과 자료가 닫혔다는 뜻이다. `overallRegressionStatus=FAIL`, `releaseApproved=false`이며 향후 단계 통과·물리 식별 정확도·완료된 paired 전투를 뜻하지 않는다.
