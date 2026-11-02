# R2: 증명된 고정 매칭 뒤 작은 잔여 성분 정확 해석

R1은 기능·원 회귀 검증을 통과했지만 실제13기 포화에서 기준B보다 나쁜 결과를 보여 최종 승인하지 않는다. 원본 R1 제품/자료는 `../B_stabilization`과 구현 커밋5718f2d에 그대로 보존한다.

실제 t=2.633333s, OWN_SPY_GLOBAL13×13/86edges는 같은 사전 x/P·같은 native NIS와 같은 기준1이다. R1은 row-minimum 하한으로3개만 인증하고10개를 HOLD했다. 같은 비용에 원래 정확 alternative-forbid 정책을 적용하면13개 모두 구별되며 HOLD0이다. 즉 R1 하한은 안전한 충분조건이지만 불완전하여 구별 가능한10개를 불필요하게 보류했다. 출처: R1 `evidence/ablation/GRAPH_EXACT_COMPARISON.json`·`battle-cause-logger/FIRST_13_GRAPH_158.json`; 진단 ON/OFF12검사 동일성 통과.

R2는 센서·EKF·NIS·게이트·기준1·교전권한·발사/유도/신관·피해/RNG·AI/저장 스키마를 바꾸지 않는다. `maxComponentSize12`, 전체 계산 bound128도 그대로다.

1. 큰 성분의 native 전역 Hungarian 최적해와 기존 하한 인증C를 구한다.
2. 부모가 모든 row를 real edge로 매칭했고, C가0보다 크며 아직 미확정 row가 있을 때만 추가 해석한다.
3. C의 row/column을 고정·제거한 **실제 legal-edge graph**를 연결성분으로 분해한다.
4. 각 잔여 성분의 row/column이 모두12이하일 때에만 기존 정확 alternative-forbid 검사를 적용한다. 큰 잔여 문제로 재귀하지 않는다.
5. 추가 수용할 모든 pair는 부모의 원 native NIS winner와 정확히 같아야 한다. 다르면 해당 잔여 성분 전체를 보류한다.
6. 미증명 row/column은 HOLD를 유지한다. parent 부분매칭·C0·큰잔여·실제동률·차원/시각근거부족은 강제 매칭하지 않고 신규birth도 만들지 않는다.

C는 모든 근접 대안에 필수이므로 이를 고정하면 잔여 성분은 분리된다. 정확 해석은 원래 '같은 cardinality의 근접 대안' 정책을 그대로 사용하며, 이를 완전한 posterior/MHT나 새 clutter model이라고 부르지 않는다. 전체128 Hungarian1회 외에 disjoint≤12 문제의 bounded추가계산이 생기므로 R1의 '총 Hungarian호출1회' 성능 가정은 더 이상 일반적이지 않다. 기존R1 검증/기대값은 수정하지 않고 R2에서 별도로 대조한다.

R2는 아직 시험 후보이며 SHADOW→native·capturedgraph·자연13전투→원회귀 순서로 검증한다. 실제전투 개선은 puregraph 증명만으로 선언하지 않는다. C55/SPQ AIR는 계속 SHADOW-only이고, 모든 미승인strict/상속문제도 별도 유지한다.
