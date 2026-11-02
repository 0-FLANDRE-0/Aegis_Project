# R3 — no-C 큰 성분의 bounded exact fallback 설계 검토

읽기 전용 설계 검토다. 이 검토는 제품 수정·브라우저·새 RF/KF/AI 호출을 수행하지 않는다. 권고안은 **13~16행/열, native parent가 모든 행을 실제 track에 배정했고, 기존 lower-bound 인증 C가0인 경우에만** 기존 exact alternative-forbid 경로로 내려가는 것이다. C>0인 R2 lower-bound/residual/S 경로와16 초과 경로는 보존한다.

## 확인된 대상과 목적

고정 R2 `c8a9266f…70d584`의 자연13 실행에서 실제 큰 graph18개를 현재 pure solver와 재생했고, selected/heldPlots/heldTracks가18/18 일치했다. 독립 NIS-only exact reference가 수락했지만 R2가 보류한 pair 출현은 다음3개 graph의35회다. 고유 표적35개라는 뜻이 아니다.

| tick / 시각 | 행×열 / edge | R2 C / 수락 | 기존 exact NIS 기준 수락 |
|---|---|---|---|
| 7 / 0.116667s | 13×13 /91 | 0 /0 |13 |
|80 /1.333333s |13×13 /88 |0 /0 |11 |
|236 /3.933333s |13×13 /85 |0 /0 |11 |

근거: [LARGE_EXACT_REVIEW.json](../B_stabilization_r2/evidence/defense-timing-logger/LARGE_EXACT_REVIEW.json). 세 graph 모두 `LARGE_COMPONENT_UNCERTIFIED_HOLD`이고 C=0이라 R2 residual exact를 실행할 수 없었다. 이는 탐지 실패가 아니라 계산 제한 때문에 남은 보수적 HOLD다. 이를 풀어도 자연전투 결과 개선이 자동으로 보장되는 것은 아니다. 새 fixed tick·무장·피해 결과를 새 제품에서 검증해야 한다.

## 가장 작은 구현 형태

기존 global native winner와 lower bound를 그대로 계산한다. 큰 성분 분기 안에서 다음 조건을 계산한다.

```js
const noCExactFallback = certifiedRows.size === 0
  && base.count === rr.length
  && rr.length <= nativeExactFallbackMaxSize
  && cc.length <= nativeExactFallbackMaxSize;
```

`nativeExactFallbackMaxSize=16`은 계산 비용 상한이며 센서/물리/확률 계수가 아니다. 기존 `TRACK_B_POLICY.maxComponentSize=12`를 전역16으로 바꾸지 않는다. 그러면 legacy SHADOW, residual 범위, 다른 stage 정책까지 바뀐다.

`!noCExactFallback`이면 현재 R2의 refinement·held set 반영·component push·continue를 그대로 실행한다. 조건이 참이면 held set을 아직 반영하지 않고 기존 작은 성분의 exact alternative-forbid loop로 fall-through한다. C=0이므로 이 경로에 앞서 chosen에 lower-bound pair를 넣은 것도 없다. 이렇게 하면 exact loop를 복제하거나 새 solver/helper를 만들 필요가 없다.

13~16 full parent **전체**를 무조건 exact 분기로 우회시키는 것보다 C=0에 한정하는 것이 안전하다. 현재 R2는 C>0을 고정한 뒤 독립 residual의 S 증거로 일부 모호성을 해소할 수 있다. 이를 전역 S certificate 하나로 대체하면, 다른 모호한 부분 때문에 전역 certificate가 실패하면서 기존 R2의 부분 해소를 다시 HOLD로 만들 수 있다. C>0 경로를 보존하면 이 불필요한 회귀를 피한다.

## 증명해야 하는 불변 조건

- 입력 edge의 i/id/NIS, 기존 NIS gate, sanity, delta 및 numeric epsilon, dummy=`gate+.5`, blocked cost, 동일 native Hungarian 함수를 보존한다.
- 기존 native winner `base`만 후보로 삼는다. fallback이 다른 matching을 새 정답으로 선택하거나 native winner의 edge를 다른 edge로 바꾸지 않는다.
- parent full은 `base.count===rr.length`다. 단순히 행·열 수가 같거나 연결 graph라는 뜻이 아니다. 13×16 같은 직사각형도 모든 행이 실제 열에 배정되면 대상이다.
- 원래 alternative-forbid는 base edge 하나를 막아 원 native solver를 실행하고, 기존과 같은 cardinality/비용/delta 판정을 쓴다. unmatched/clutter prior, 최대 cardinality 규칙 또는 새 비용을 넣지 않는다.
- exact tie에서 numeric ID 정렬을 물리적 정답 인증으로 삼지 않는다. 현재 exact-tie/S 차단 규칙을 보존한다. 기존 S certificate를 재사용한다면 NIS-only exact reference와의 차이는 별도로 표시하고 자동 unsound로 부르지 않는다.
- ≤12, C>0, 비full parent, >16의 **pair/held 결과가 기존 R2와 동일**해야 한다. >128 계산 상한 처리도 유지한다.
- C55/SPQ의 live/shadow 소비 경로와 legacy mode token은 변경하지 않는다. SHADOW에서 proposal 계산비가 늘 수 있으나 실제 선택·관측·RNG·무장 경로는 보존해야 한다.

## HOLD 집합과 edge 인증의 함정

기존 exact loop 전체를 재사용해야 한다. “forbid한 그 edge만 모호하면 보류” 또는 “개별 인증된 pair를 바로 수락”으로 단순화하면 안 된다. 하나의 가까운 alternative가 다른 행·열까지 연쇄 교환할 수 있다. 모든 alternative에서 base.map과 달라진 **전체 행**과 base/alternative의 **전체 관련 열**을 모은 뒤, 마지막에 chosen을 heldPlots와 heldTracks 양쪽으로 필터해야 한다.

사용되지 않던 실제 열로 이동하는 직사각형 alternative도 포함한다. row만 보류하거나 base의 기존 열만 보류하면 다른 pair가 모호한 열을 통해 살아남을 수 있다. components는 서로 독립이므로 전역 held set에 한 번만 반영한다. fallback 진입 전에 whole-component held set을 미리 넣었다가 나중에 pair만 추가하는 방식은 모든 새 수락을 최종 필터가 다시 지워버리는 오류를 만든다.

진단에는 계산 방식 표시(`bounded exact fallback`), bound16, native full 여부, lowerBoundCertifiedCount0, 최종 certifiedCount를 구분한다. fallback 인증을 exactResidualCertifiedCount로 잘못 세지 않는다. pair 증거, hit/freshness/mean/P 또는 IFF/권한을 만들어내지는 않는다.

## 검증과 실행 비용

1. 원 captured37graph를 새 pure 모듈로 재생한다. R2 C=0 graph3개는 exact reference와 비교하고, 나머지 R2 graph15개와 기존 small/large fixtures는 원 결과를 보존하는지 확인한다. reference는 기존처럼 계산 상한만128로 올린 private VM이며 새 NIS/S를 만들지 않는다.
2. 12/13/16/17/128/129 경계, full·비full, C0·C>0,13×16/16×13 직사각형, dummy, exact tie, 연쇄 교환, near-equal alternative, ID/입력 순서, 기존 S 해소를 순수 fixture로 검사한다. winner-subset과 row/col 양쪽 HOLD 불변을 포함한다.
3. 실제 source/HTML/build/scope proof 후 fresh native integration·OFF/ON·SHADOW control 및 원래17job을 실행한다. R2/R1 자료는 역사적 비교만 하며 새 R3 통과로 재사용하지 않는다. 자연13의 끝까지 본 전투 결과와 실제 미해결 상태를 따로 보고한다.
4. 비용은 호출 수와 실제 시간 모두 측정한다. n행 exact NIS에는 base1회+forbid 최대n회가 필요하다. 추가 S 검증까지 전부 실행되면 전체 최대 약2(n+1)회이며 n≤16으로 제한된다. solver는 n×(열+n) 행렬을 받아 같은 native Hungarian을 실행한다. 시간 측정 전 성능 개선·무비용을 주장하지 않는다.

현재 captured graph3개는 모두13행이므로, native NIS fallback만 보면 기존 base 뒤에 forbid13회씩, 합39회의 추가 순수 assignment가 생긴다. S 경로가 실행되면 더 늘 수 있다. 이는90초 동안 관찰된 해당 사례의 계산량 추정이며 일반 상한·프레임 시간 실측이 아니다. 최악의13~16 성분이 매tick 반복되는 경우도 별도 순수 microbenchmark로 확인해야 한다. 큰 행렬·측정 생성·RF·전역 RNG를 새로 실행하지 않는다.
