# TRACK-B ownship / NPC / SPQ / SURFACE association audit

상태: **READ_ONLY_AUDIT / 구현 전 제안**. 이 문서는 제품·시험 기대값을 바꾸지 않으며 자연 RF 재현을 실행했다는 증거가 아니다. 브라우저·시험·커밋을 실행하지 않았다.

- 작업 기준: `track-b-association`, `ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561`의 TRACK-A 결과.
- 실제 실행 JS: `/dev/shm/track-b-baseline-source.js`, SHA-256 `8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e`.
- 아래 `L`은 위 **고정된 압축 해제 JS**의 행 번호다. 파일 중첩 함수와 canonical 함수를 혼동하지 않는다.
- 규범: `A/INSTRUCTIONS.md`의 TRACK-B 및 `A/FUTURE_STAGES.md`. RF·EKF·관측 원점·기존 gate·분류/IFF/권한/무장 경로를 보존하고, 기존 scalar 후보 결과를 받는 pure solver부터 shadow 비교한다.

## 1. 현재 경로와 일대일 범위

| 경로 | 후보와 선택 | 갱신·used 의미 | 최소 변경 지점 |
|---|---|---|---|
| own SPY AIR focused | `spyBestPlotForTrackV31` L26997–27004: 예약한 track 하나에 plot별 native AIR 4D NIS, 최솟값 선택 | `executeSpyTask` L27082–27089: 실제 update 성공 뒤에만 plot/track을 used로 등록 | 이미 계산한 후보의 ambiguity 설명부터. 예약 파일 우선권을 전체 search와 합치지 않음 |
| own SPY AIR search/remainder | `spyGlobalAssignmentsV36` L27007–27025: native cross-domain eligibility와 4D NIS → rectangular Hungarian | L27076–27105: surface가 수용한 track을 AIR의 usedTracks에 전달. **한 physical dwell**에서 track당 한 번. 같은 25ms scheduler cycle의 다른 dwell은 다시 갱신 가능 | 기존 costs를 pure solver에 전달. 기존 Hungarian 비용/출력은 기준으로 보존 |
| own SURFACE: SPY/SPQ/BridgeMaster | `surfaceAssignmentsPreferEstablishedWip13B14` L27576–27590: established surface를 먼저 Hungarian, 남은 plot에 early AIR/UNKNOWN recovery를 두 번째 Hungarian | 양 stage가 같은 usedTracks/assigned를 공유. SPY focused 성공 plot/track은 remainder에서 제외. SPQ/BridgeMaster도 공용 adapter 이용 | **stage별** 기존 scalar costs 재사용. established-first 우선순위를 없애면 안 됨 |
| NPC SPY/SPQ/NAV | `observerAcceptPlotsC` L4769–4798: 모든 기존 track×plot native NIS를 먼저 계산하고 `{i,id,nis}` 정렬 후 greedy | 성공한 `apply` 뒤에만 usedTracks/usedPlots 추가. 마지막 미사용 plot은 initiate 정책에 따라 새 tentative 생성 | 완성된 후보 graph가 이미 존재하므로 pure solver 최초 live 후보에 가장 적합 |
| own SPQ AIR | `spq9bBestTrackForPlotV34` L34293–34302 + `spq9bAcceptAnonymousPlotsV34` L34303–34324: plot 순서대로 best track | 앞 plot의 EKF correction/source 변경 뒤 다음 plot의 NIS를 계산. 앞서 생성한 새 track도 store에는 들어가지만 usedTracks가 재사용을 막음 | 처음에는 existing greedy의 scalar 결과를 shadow 기록. 진짜 batch 전환에는 candidate 생성 epoch를 고정하는 별도 변경·회귀가 필요 |

Hungarian 원형은 `bridgeMasterEMinCostAssignmentV35` L34553–34568이다. rows=plot, columns=existing track + plot 수만큼 dummy이며 row→column을 한 번씩 배정한다. SPY는 dummy=`gate+0.5`, surface는 stage별 `stageGate+0.5`, blocked=`1e6`을 사용한다. **최소 총 비용 + 유한 dummy penalty**이지 무조건 최대 매칭 수를 먼저 최적화하는 계약이 아니다. 새 helper가 무심코 maximum-cardinality 우선으로 바꾸면 기존 동작 변경이다.

현재 gate 값은 AIR normal36/search64/reacquire96/precision-reacquire180(L25886–25889, L26993–26995), NPC64(L4778–4784), SPQ AIR search64와 cross-domain25의 작은 값(L34297), SPY surface42(L25716), SPQ surface64(L34377), BridgeMaster25(L25815)다. surface cross stage는 기존25와 caller gate 중 작은 값(L27580)을 쓴다. 이 audit은 이를 조절하지 않는다.

## 2. 구체적 선택 문제와 정책상 주의점

### B-ON-1: NPC sorted-edge greedy의 연관 손실 / 순서 의존

L4773–4780에서 생성한 모든 유효 edge를 `nis,i,id`로 정렬하고, L4795에서 이미 사용된 track/plot이면 건너뛴다. 예를 들어 **기존 gate 안**인 scalar 후보가 다음과 같으면:

```text
         track A  track B
plot 0     0.10     0.11
plot 1     0.20    blocked
```

greedy는 plot0→A를 먼저 선택한 뒤 plot1을 기존 파일에 연결하지 못한다. `initiate:true`면 plot1에서 새 파일이 생긴다. 같은 graph의 기존 Hungarian/dummy 비용 계약에서는 plot0→B + plot1→A, 합계0.31이 더 작다. 이는 **논리적 counterexample**이며, 실제 native 관측으로 같은 graph가 만들어지는 fixture를 별도로 확인해야 한다. scalar 예시만으로 자연 RF false split을 입증했다고 쓰면 안 된다.

또한 같은/비슷한 NIS의 여러 매칭에서 현재 tie-break는 plot index와 track id다. 이는 안정적인 반복 실행 순서이지 물리적으로 ID 연속성이 맞다는 증거가 아니다. ambiguity 판정은 번호/identity/faction/truth를 근거로 하면 안 된다.

최소 변경 후보: NPC가 **이미 만든 유효 edge graph**를 shared pure solver에 주고, 기존 apply/confirm/source/identity/authority/initiation 코드와 성공 후 used 의미를 유지한다. 첫 단계는 legacy 선택과 새 선택을 shadow 비교한다.

### B-ON-2: own SPQ AIR는 batch cost graph가 아니라 순차 갱신 graph

L34305–34322에서 plot0 correction 또는 SPY-preferred bookkeeping이 끝난 다음 plot1의 best 후보를 계산한다. 유효한 두 표적이 경쟁하는 sweep에서 RF plot 나열 순서가 선택에 관여할 수 있다. `usedTracks`는 동일 track에 두 번 hit하는 것을 막지만, 가능한 매칭 전체의 최저 비용·모호성은 평가하지 않는다.

batch 전환 제안은 **동일 sweep의 시작 상태**에서 기존 eligibility/NIS를 pair당 한 번 계산하고 pure solver에 전달하는 것이다. solver/diagnostics가 native NIS를 다시 호출하면 안 된다. 다만 기존 sequential 실행에서 used가 된 track은 다음 plot의 NIS 계산을 생략했으므로, 전체 사전행렬은 기존보다 평가 pair 수가 늘 수 있다. 이를 “평가 횟수 불변”이라 주장하면 안 되며 CPU·cache·eligibility counter와 실제 결과 차이를 측정해야 한다. NPC의 기존 all-pairs 지점과 동시에 한꺼번에 전환하지 않는 편이 안전하다.

SPY-preferred 분기 L34308–34313은 실제 EKF/hit을 하지 않고도 association을 소비하여 duplicate를 막는다. 새 solver는 이 결과를 `ASSOCIATE_WITHOUT_HIT`로 유지해야 한다. 선택된 file을 unassigned로 되돌려 새 파일을 만들거나 SPY source를 SPQ로 덮어쓰면 안 된다.

### B-ON-3: own Hungarian은 ambiguity가 해소됐음을 보장하지 않는다

SPY AIR L27017–27024와 surface L27581–27584는 유효 최소비용 매칭 하나를 즉시 채택한다. tie나 거의 같은 대안의 존재를 출력하지 않는다. 따라서 shared solver는 기존 winner와 함께 대안/모호성 정보를 만들 수 있지만, **그 결과를 live hold로 쓰는 것은 새 정책 변경**이다. 먼저 shadow의 conflicting alternatives와 실제 crossing fixture를 확인해야 한다.

특히 surface stage1은 정책상 established surface를 우선한다. L34742–34743의 `runWip13b14CrossDomainAssociationFixture`는 `establishedSurfaceWinsBeforeAirRecovery`를 명시적으로 검사한다. surface 전체를 AIR/Surface 혼합 Hungarian 한 번으로 바꾸는 것은 중립적인 리팩터가 아니다. 우선권은 보존하고 ambiguity도 각 stage 안에서 판정한다.

### B-ON-4: surface position association와 Doppler update의 차원 불일치가 의도적으로 존재

SPY/SPQ/NPC surface 후보는 `trackSurfacePositionAssociationNisWip13B9`(L26187–26190)를 써서 radial 필드를 뺀 r/az2D를 평가한다. 최종 `trackEkfUpdateSurfaceRadar2D`는 실제 radial이 있으면 r/az/radial3D로 기존 gate를 평가한다(L26150–26159). BridgeMaster는 원래 radial이 없으므로2D다.

따라서 위치 cost가 낮아 배정됐다는 사실만으로 실제 update 성공을 보장할 수 없다. NPC greedy는 apply 실패 시 used를 잡지 않고 다른 precomputed pair를 시도할 수 있지만(L4795), own SPQ/BridgeMaster의 caller는 선택된 file의 correction이 거절되면 해당 plot을 rejected 처리하며 대안 재탐색은 하지 않는다(L34380–34382, L34585–34586). 이 차이를 false merge 확정이나 gate 결함으로 단정하지 않는다. **새 solver는 assigned와 accepted/hit을 구분하고 실패 후 native 후처리를 보존해야 한다.** Doppler를 candidate cost에 새로 추가하거나 기존2D gate를 완화하는 변경은 이번 최소 solver 전환과 분리한다.

### B-ON-5: 큰 P에서 작은 NIS — 별도 물리 sanity의 미해결 범위

AIR NIS는 해당 EKF P와 기존 observation noise를 이용하고(L26082–26092), surface도 동일하게 P를 이용한다(L26175–26185). 이 선택 함수에는 별도 고정 meter residual·velocity sanity gate가 없다. P가 커진 file에 먼 관측이 gate 안으로 들어오는 가능성은 구조적으로 남는다. dropPosSigma9km(L25883), coast/drop/partition은 이 문제와 동일한 gate가 아니다.

기존 NIS/threshold를 그대로 유지한 **순수 재할당만으로** 이 모든 false association을 해결했다고 주장할 수 없다. 첫 shadow에 residualM/관측 나이/제공 Doppler residual을 scalar로 기록하고, native 사례로 필요한 sanity 기준과 재획득 보존 영향을 따로 증명해야 한다. 새 기준을 넣는다면 association-only SIM_TUNED 정책임을 명시해야 하며 RF/기동 제원이나 truth에서 편의상 끌어오지 않는다. 이 문서는 신규 meter/speed threshold 값을 제안·확정하지 않는다.

## 3. prediction과 시간 정렬 경계

`trackEkfPredict` L25970–25992는 CV 평균과 P를 mutate하고 legacy 좌표도 동기화한다. `trackRadarAssociationNisV31`도 `trackEkfInit`과 WeakMap kernel cache를 사용하며(L26082–26090), cross-domain eligibility는 거부 통계를 증가시킬 수 있다(L27558, L27566). 진단/solver에서 이를 재호출하여 후보를 보충하지 않는다.

실제 fixed tick은 ownship movement → `updateRadar(dt)` → SPQ → BridgeMaster → 헬기 offboard/`stepObserversC` → EW/network/H4 → IFF → weapons다(L55350–55365). ownship `updateRadar`는 먼저 age/lifecycle와 **한 번의** predict를 수행한 뒤(L39752–39789) `updateSpyScheduler(dt)`를 실행한다(L39850). NPC는 `stepObserversC`에서 먼저 age/predict(L4859), scheduler dwells, SPQ/NAV, offboard drain 순서다(L4860–4861). 각 batch는 그 지점의 이미 예측된 상태를 사용한다.

- 한 physical dwell/sweep 안에서만 solver graph를 만든다. 같은25ms cycle에 있는 다른 physical dwell의 used를 합치지 않는다.
- 현재 tick의 local RF에 `sensorAge`만큼 추가 predict하면 이중 예측이다. `lastMeasurement` 나이와 filter state epoch를 혼동하지 않는다.
- 늦은 외부 보고는 별도 offboard의 age/P 확대 계약을 유지한다. local solver에 sender truth/hidden velocity를 넣거나 보정용 filter를 새로 만들지 않는다.
- 입력에서 측정 시각을 알 수 없으면 unknown으로 남긴다. source별 시간을 같게 보이게 하려고 timestamp를 now로 덮지 않는다.

## 4. shared pure candidate/ambiguity solver 제안

```js
// adapter가 기존 native 계산을 끝내 전달한 detached primitive 값만 사용한다.
solveAssociationB({
  plotKeys, trackKeys,
  edges: [{plotKey, trackKey, nis, nativeGate, eligible, stage}],
  blockedCost, dummyCost, legacyAssignments,
  mode: 'SHADOW'
});
// => {assignments, ambiguousPlots, ambiguousTracks, alternatives, reasons}
```

helper에는 TrackStore, payload truth, identity/faction, receiver owner의 private FCS, RNG, EKF/helper 함수, world API를 전달하지 않는다. observerShip 식별은 진단 소유권용이며 target 매칭 cost로 쓰지 않는다. `eligible:false`, 비유한 NIS, 기존 gate 초과, caller의 used/excluded는 adapter가 보존한다. stage별 track/plot key와 입력 순서를 명시하여 비용 tie도 재현 가능하게 한다.

첫 구현은 기존 Hungarian의 costs/동일 dummy penalty를 재사용하는 bounded pure 선택 + legacy 대비 차이 보고가 적절하다. **최대 matching 수 우선, 새 cost 정규화, 나이·identity 가중치, threshold 일괄 변경**을 몰래 추가하지 않는다. ambiguity는 row의 두 최솟값 차이만으로 확정하지 않는다. 다른 row가 한 후보를 강하게 제약하면 전체 매칭은 유일할 수 있기 때문이다. 경쟁 component의 다른 유효 일대일 해를 비교하고, bounds를 넘으면 `NOT_EVALUATED_BOUND`로 공개한다. 구체적인 near-tie margin/active hold 조건은 native fixture 결과와 별도로 문서화한 뒤 정한다.

live caller가 ambiguity를 보류한다면 `null` match 하나만 반환하는 API는 불충분하다. 현재 caller의 `null→CREATE` 분기 때문에 오히려 duplicate birth가 생길 수 있다. `MATCH / UNMATCHED / AMBIGUOUS_HOLD`를 분리하고 held plot은 기존 file update·새 file 생성 모두 하지 않거나, 승인된 tentative 분기를 명시해야 한다. existing lock/FCS/identity를 바꾸지 않는다. 이는 shadow에서 검증한 다음 단계의 변화다.

우선순위 제안:

1. 기존 all-pairs를 가진 NPC adapter에서 shadow solver와 legacy 결과를 비교.
2. 유일한 매칭·greedy counterexample·ambiguity hold의 작은 실제 native fixture를 통과하면 NPC 한 경로만 전환.
3. own SPY/SURFACE의 기존 Hungarian cost graph를 shadow의 공통 진단 구조로 연결; stage/focused/used 계약 그대로 유지.
4. 마지막으로 SPQ AIR를 sweep 시작 batch 후보로 전환할지 결정. 자연 RF 결과·평가 횟수·CPU 변화는 별도 보고.

## 5. 구현 전 fixture / 회귀 계획

| fixture | 입력과 native 실행 | 확인할 값 |
|---|---|---|
| scalar greedy counterexample | 위2×2 candidate graph, native Hungarian과 shared pure solver/legacy greedy 비교 | 두 매칭의 비용, unmatched/birth 가능성; fixture-only 표시 |
| private NPC native two-file | 별도 prepared runtime에 익명 AIR 또는 surface plot2개로 시작, native predict/accept 반복 | 기존 track IDs·state/P·gate·최종 hits, 한 batch track/plot당≤1, canonical own store 변화0 |
| permutation | 같은 두 plot batch의 입력 순서만 바꾸고 fresh private runtime에서 반복 | physical fixture label로 정렬한 최종 연결/false split/ID swap; truth label은 사후 판정 전용 |
| exact/near tie vs constrained unique | 동률 graph, 근접 대안 graph, 다른 row 때문에 유일한 graph | 임의 ID를 정답 근거로 쓰지 않음; ambiguity/hold/new tentative 구분 |
| AIR3D→surface2D | 실제 고도50/300m의 익명 AIR 측정 후 compatible2D, native NIS reject도 포함 | retained3D16s 이내 z/vz/P 보존, 측정 차원2/3구분, identity/authority 승격0 |
| surface2D→AIR3D | surface prior8m file에 실제 el 포함 AIR 보고 | 기존 native4D gate를 통과한 경우 동일 file, 미통과는 정상 별도 결과; truth 보정0 |
| Doppler disagreement | 위치는 비슷하고 실제 radial이 반대인 surface plots | 2D assignment와3D update의 거부 분리, filter 실패를 성공/hit으로 세지 않음 |
| grown-P / coast / gap | native predict로 P와 age를 키운 뒤 near/far plot, 실제 관측 공백 후 재획득 | 모든 NIS/잔차/epoch 기록; 저번호 강제 유지·큰P 강제 결합 금지; 미해결 sanity 공개 |
| focused / multiple physical dwells | 같은 scheduled file에 두 plot, 다른 physical dwell은 같은cycle 내 반복 | focused 우선권 및 miss 후처리, 한dwell1회·다른dwell 허용, cycle 전체 used 금지 |
| SPQ SPY-preferred | fresh SPY file과 SPQ anonymous plot | association 소비, correction/hit0, source SPY 유지, duplicate0 |
| established-first surface | 기존 `runWip13b14CrossDomainAssociationFixture` 사용 | establishedSurfaceWinsBeforeAirRecovery 등 기존 기대값 불변 |

공통 필수 계측: native NIS/helper 평가 횟수, 기존 값과 새 선택, 후보 수, confirmed/age/lifecycle·분류/identity/authority·state/P, owner별 store/독립 RNG, CPU 평균/p95와 할당. 후보 builder를 또 실행하는 계측은 금지한다. fixture label을 제품 연관 입력으로 넣지 않는다.

그 뒤 원래 세 자연 재현(hover60s/route120s/Harpoon75s), 기존 native/paired/UI/WebGL/배속·owner당1tick·CIWS30을 동일 기준으로 비교한다. A에서 상속된419025 FAIL과 CG→friendly paired2를 새 기대값으로 승인하거나 숨기지 않는다. 변경된 전투 결과는 원인별로 보고하고, 초기 solver 전환과 무관한 RF·물리·무장·IFF·교전권한 개선을 섞지 않는다.

## 6. 이번 audit의 결론과 한계

가장 작은 실질 변경 후보는 **NPC의 기존 precomputed graph에 shared pure solver를 적용하는 것**이다. own SPY/SURFACE는 이미 Hungarian이므로 다시 만들 필요가 없다. SPQ AIR 순차 평가, established-first 정책, candidate/update 차원 차이, broad-P sanity는 별개 문제로 분리한다.

이 audit은 concrete code 구조와 논리적 counterexample을 제시한다. 실제 native crossing에서의 퇴행·개선, false merge/false split 비율, 성능 영향은 아직 검증하지 않았다. 따라서 제품 연결/정책·계수 결정/완료 선언은 하지 않는다.

## 7. 승인된 NPC adapter 패치 — manifest만 준비, 실행 검증 전

`patches-npc.json`은 고정 소스의 `observerAcceptPlotsC` 한 함수에 대한 정확한 네 가지 before/after 변환이다. 압축 해제 소스·HTML을 직접 편집하지 않는다. JSON 파싱, 각 before의 scope 내 단일 일치 및 치환한 함수의 JavaScript 문법만 확인했다. 실제 native 시험·성능·회귀 PASS는 아직 주장하지 않는다.

승인된 shared association policy는 **SIM_TUNED**다. RF 제원·물리 탐지 모델·EKF 이득이 아니다.

- 위치 sanity: **고정2500m hard cap**. filter P와 측정 R가 커져도 이 한계를 늘리지 않는다.
- 실제 radial이 제공된 경우 radial innovation sanity: **고정180m/s hard cap**. 측정 radialσ가 커져도 이 한계를 늘리지 않는다.
- 같은 cardinality의 경쟁 whole matching에서 `ΔtotalNIS≤1`이면 ambiguity로 보류한다.
- 경쟁 component 크기가12를 넘으면 bounded 계산을 넘기지 않고 HOLD한다.

설계 이력: 처음 제안한 `max(2500m,5×measurementσ)` / `max(180m/s,5×radialσ)`는 큰 **측정 covariance 자체가 gate를 무한히 키우는 문제**가 독립 검토에서 발견되어 최초 게임 fixture 이전에 기각됐다. 최종 고정 hard cap은 기존 network association의2500m/180m/s 경계를 재사용한다. 측정σ는 진단에 남길 뿐 cap 완화에 쓰지 않는다. 이는 RF 제원·EKF 계수를 바꾼 것이 아니라 명시적인 SIM_TUNED association 정책이며, 결정 경위는 `IMPLEMENTATION_PLAN.md`의 최종 정책 구역과 일치시킨다. unit41에서 큰R/P에서도 cap이 유지되는 조건을 확인한 뒤 native fixture로 넘어갔다는 실행 증거는 root의 검증 자료를 따른다.

native gate64와 eligibility/NIS 계산은 그대로 유지한다. 기존에 gate를 통과해 저장하던 pair에 `sanity:trackBGeometryB(...)`만 덧붙이고, `trackBSelectB`는 그 **precomputed pair graph**를 받는다. helper가 native NIS를 다시 부르지 않는다.

`selection.active`는 shared module의 frozen association policy에서 오며 진단 ON/OFF 상태가 아니다. SHADOW에서는 selector가 비교 로그만 남기고 원래 sorted pair loop를 그대로 실행한다. ACTIVE에서는 selected pair를 먼저 시도한 뒤, 성공하지 않은 plot/track에 원래 sorted pair의 admissible fallback을 시도한다. held plot/track 또는 실패한 sanity edge는 fallback에서 제외한다. 첫 시도에서 native EKF가 거부한 동일 pair를 fallback에서 다시 correction하지 않도록 attempted-pair set을 둔다. 그렇지 않으면 기존 rejection/quality 변이가 두 번 일어날 수 있다.

apply closure의 EKF·hit spacing·confirmed·source/freshness·분류/IFF/identity/authority 코드는 바꾸지 않는다. 실제 성공 뒤에만 기존 usedTracks/usedPlots를 표시한다. ACTIVE held plot은 기존 `null→새 tentative` 경로로 보내지 않고 rejected를1회 기록하며 `ASSOCIATION_HOLD_NO_INITIATION` 진단을 남긴다. SHADOW의 기존 initiation/실패 fallback은 유지한다.

이 변경은 NPC 한 경로의 association policy만 대상으로 한다. own SPY/SPQ/SURFACE·RF·NIS/EKF kernel·소비자·무장·TRK-C 수명 정책·기대값을 변경하지 않는다. shared module과 최종 빌드에 통합한 뒤 별도 native·자연 RF·전투 회귀가 필요하다.

## 8. own SPY global / surface stage 후속 manifest와 focused 잔여 범위

후속 `patch-own.json`은 SPY global과 established/cross surface stage의 기존 cost matrix에서 scalar pair를 추출하여 공통 selector에 전달한다. cross-domain gate가 blockedCost로 제외한 edge는 되살리지 않는다. **native NIS는 pair당 기존 한 번만** 평가한다. SHADOW 또는 B 비교 trace ON일 때만 기존 native Hungarian을 한 번 실행해 `legacyPairs`를 전달하며, SHADOW는 이 실제 native 결과를 반환한다. ACTIVE·trace OFF에서는 중복 reference solve를 생략한다. solver/진단 ON 여부는 native NIS 입력·gate·RF·EKF를 바꾸지 않는다.

surface의 두 단계는 그대로 둔다. stage1 held row는 stage2로 넘어가지 않고, stage1 held track은 함수 내부의 임시 usedTracks에만 예약한다. 이 임시 예약은 실제 수용된 hit나 caller의 used 표시가 아니다. `Map.trackBHeldPlots`는 반환 Map의 transient 메타데이터이며 canonical track·저장 파일에 쓰지 않는다.

held plot이 기존 `null→CREATE`로 빠지지 않도록 `executeSpyTask`, `spyExecuteSurfacePlotsWip13B9`, `spq9bAcceptSurfacePlotsWip13B1`, `bridgeMasterEAcceptAnonymousPlotsV35` 네 caller가 이를 거절/보류로 처리한다. 나머지 caller의 실제 correction·confirm·source·capacity·분류/IFF/권한은 그대로 둔다. manifest JSON과 치환 후 여섯 함수의 문법만 확인했으며 native 회귀 결과로 간주하지 않는다.

**focused 두 경로는 이 후속 manifest에서 바꾸지 않는다.** `spyBestPlotForTrackV31` L26997–27004와 `spyExecuteSurfacePlotsWip13B9`의 scheduled-file 선점 L27066–27068은 여전히 예약 track 하나의 최소 native NIS를 먼저 고른다. global 결과를 먼저 적용하거나 다른 파일의 FCS 우선권으로 바꾸면 안 된다.

focused의 최소 후속 검토는 (1) 각 plot의 이미 계산한 native NIS를 보존한 채 익명 geometry sanity를 붙이고, (2) 같은 예약 file에 서로 다른 plot이 near-equal인 경우의1-row 경쟁을 shadow 설명하는 것이다. 추가 NIS/필터 재실행은 필요하지 않다. 다만 focused 보류 plot이 remainder global 단계에서 다시 선택되거나 새 tentative가 되는 것을 막으려면 별도 transient held 전달 계약이 필요하다. 보류를 기존 `markSpyDwellMiss`/surface miss로 취급할지도 lifecycle 영향과 함께 공개해야 한다. 이 잔여 경로를 아직 보호한 것처럼 보고하지 않는다.

## 9. 후속 독립 정적 검토와 아직 증명하지 않은 범위

RC0 ACTIVE HTML `79a098a88c18c7521e54ed1f8115aac9d013321873400076b4e62482b5f78d4a`의 익명 실제 함수 fixture는69검사 중66통과·3실패였다. 실패는 `ownAmbiguity.assignmentWithheld`, `ownPermutation.tiedRowsWithheld`, `sanity.distanceStillRejects`다(`evidence/native-integration/active.json`). 셋은 shared solver 자체의 합격 기준을 낮춰 해결할 일이 아니라 **own SPY global에 B guard가 연결되지 않은 구현 누락**이다. `patch-own.json`이 해당 연결을 보완하지만 소스에서 누락이 보완됐다는 정적 확인과 새 frozen HTML의 실제 재검증 PASS는 다르다. RC0 실패를 historical/not-final로 보존하고 최종 native·자연 RF 검증을 기다린다.

`association.js`와 own manifest의 정적 검토에서는 truth/hidden owner/faction 조회, 추가 EKF/NIS 호출, 새 identity·권한 쓰기를 찾지 못했다. native 비용에 기존 cross-domain gate가 적용된 뒤에만 geometry/solver로 넘어간다. SHADOW는 실제 Hungarian `legacyPairs`를 반환하고 ACTIVE는 held row를 네 caller의 생성 경로에서 제외한다. surface stage의 held row/track은 다음 cross stage에 재사용되지 않는다.

다음은 **미검증 또는 명시적으로 미적용인 범위**다.

- focused AIR/surface 선점 경로와 SPQ AIR/C55 live는 현재 우선순위·인터리브를 보존한다. global fixture 합격으로 이들의 모호성/sanity 개선까지 완료했다고 할 수 없다.
- surface candidate의2D NIS와 실제 correction의3D Doppler 거부는 여전히 다르다. 기존 update 거절 후 own caller의 대안 재시도 부재와 NPC의 fallback은 기존 의미를 유지하며, 실제 거부 fixture와 전투 영향은 별도 검증이 필요하다.
- NPC ACTIVE fallback은 selected correction이 실패하면 이미 계산한 원래 admissible edge를 한 번씩 시도한다. 동일 pair 중복 correction은 막았지만, 실패로 달라진 잔여 graph의 ambiguity를 새로 풀었다는 주장은 하지 않는다. 여러 correction 거절이 섞인 조건에서 선택 순서·rejection counter·최종 hit/파일 수를 기록해야 한다.
- 큰 경쟁 component는 HOLD하므로, 이것이 자연 dense raid에서 방어 손실을 만들지 않았는지는 실제 전투 검증이 필요하다. bounded 알고리즘이라는 사실만으로 성공을 보장하지 않는다.
- 추가 source-only 위험: 현재 `trackBSolveB`는 `plotCount>256`에서 throw한다. NPC는 native maxPlots96이지만, own SPY/surface는 원래 `plots.length`를 그대로 넘기며 RF extractor L30870은 모든 discrete candidate를 처리한다. own producer의256상한이 입증되지 않은 상태라면 valid oversized sweep에서 게임 tick을 중단할 수 있다. 이 검토 시점에 root에 즉시 보고했으며, safe bound 처리 또는 producer cap의 명시적 근거·검증 전에는 해소됐다고 세지 않는다.

이 정적 검토는 전체 TRACK-B closure나 release 승인이 아니다. fixture·자연 RF·CIWS/무장·도메인/화면·배속·성능 결과와 범위 밖 코드 불변 증거가 함께 필요하다.
