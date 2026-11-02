# TRACK-B 연관 계약 — TRACK-A 보완, 단계 범위 고정

이 문서는 [TRACK-A 계약](../A/TRACK_CONTRACT.md)을 대체하지 않는 **association-only 보완**이다. 기존 raw producer·측정 차원·observed/prior/derived 구분과 비누수 원칙은 A 그대로 유지한다. B는 기존 NIS/거리 후보 중에서 매칭·모호성·추가 sanity를 처리하는 단계이며 새 EKF, 센서, TrackStore, OODA/전술 AI, 피아식별 체계가 아니다.

기준 제품은 TRACK-A RC2 `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA-256 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`, 기준 브랜치 HEAD는 `ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561`이다. B의 최종 HTML/소스 해시는 `BUILD.json`과 검증 레코드에서 확인한다. 준비된 manifest가 존재하는 것, 실제 HTML에 합성된 것, native fixture 통과, 자연 RF/전투 회귀는 서로 다른 증거다.

**문서 작성 시 상태:** 첫 RC0 native integration은 69개 중66개 통과,3개 실패다. own SPY 적용/후처리가 아직 연결되지 않아 `ownAmbiguity.assignmentWithheld`, `ownPermutation.tiedRowsWithheld`, `sanity.distanceStillRejects`가 실패했다. 이 결과는 waived/기존 실패/PASS가 아니다. own SPY·surface 및 네 caller의 held 전달을 보강한 RC1은 후속 테스트 대상이며, RC0 결과를 새 RC1의 합격 자료로 재사용하지 않는다. 최종 상태는 `REPORT.md`/`VALIDATION.json`과 그 파일의 정확한 artifact hash를 따른다.

## 1. ACTIVE/SHADOW는 빌드 정책, 진단 스위치와 별개

`TRACK_B_IMPLEMENTATION_MODE`는 빌드 시 `ACTIVE` 또는 `SHADOW`로 고정한다. 콘솔의 `__TRACK_B__.configure({enabled})`는 bounded 비교 trace를 켜고 끌 뿐 live association 정책을 전환하지 않는다. trace ON 여부로 발사 결과가 달라지면 오류다.

- **ACTIVE 경로:** 이미 계산한 native 후보/NIS를 shared helper에 전달하고, 허용된 경로에서 선택/보류 결과를 사용한다.
- **SHADOW 빌드:** 실제 baseline 선택과 처리 순서를 유지한다. 비교 제안은 진단에만 남기며 legacy winner/기존 생성 경로를 실행한다.
- **경로별 passive 범위:** C55 live, SPQ AIR 순차 연관, focused SPY 선점 경로는 아래 표의 잔여 범위대로 유지한다. 전체 빌드명이 ACTIVE라고 모든 센서 연관이 새 정책을 쓴다고 주장하면 안 된다.

`trackBSelectB`는 callback으로 producer/NIS/EKF를 받지 않는다. 일반 후보는 adapter가 기존 지점에서 이미 계산한 `{i,id,nis,sanity}`이고 assigner는 기존 순수 `bridgeMasterEMinCostAssignmentV35`다. root helper가 선택 전에 실제 센서를 다시 실행하거나 다른 함의 private 상태를 빌려 올 수 없다.

## 2. 고정된 shared 정책

| 항목 | 현재 값/동작 | 의미와 한계 |
|---|---|---|
| native NIS/센서 gate | 각 기존 caller의 값 유지 | B는 그 밖에 추가 association sanity/hold를 적용하므로 전체 동작이 무조건 동일한 refactor는 아님 |
| 위치 innovation hard cap | **2500m** | 기존 `networkAssociationNisG`의 경계를 새 공통 association sanity에 재사용한 **SIM_TUNED 정책**. 로컬 레이더 하드웨어 성능이나 공개 탐지 제원이 아님 |
| radial innovation hard cap | **180m/s** | 실제 radial 관측과 수신기/필터 속도로 residual을 계산할 수 있을 때만 적용. 숨은 실제 속도·Doppler 합성 금지 |
| near matching delta | **Δ total native NIS cost≤1** (+수치 epsilon) | 같은 cardinality의 경쟁 whole matching을 찾는 heuristic. calibrated probability/likelihood ratio/실제 오인 확률이 아님 |
| connected component 상한 | 각 축12 | 초과 component는 계산량을 제한하고 HOLD. 밀집 공습에서 많은 파일의 갱신을 막을 수 있는 실제 위험이며 더 큰 그림을 본 척하지 않음 |
| shared input plot 상한 |256 | 이 입력 계약/검증 범위를 넘는 자료는 정상 해결 완료로 세지 않음 |
| native Hungarian dummy | `gate+.5`, blocked `1e6` | 기존 비용 의미 유지. **최대 cardinality 우선 solver가 아님**. assignment 수 감소가 곧 결함/개선이라는 단정 금지 |
| trace | 기본OFF, capacity1024/설정16~4096 | 진단 메모리만 제한. old records overwrite/dropped/errors를 보고하며 overflow를 coverage PASS로 세지 않음 |

초기 `max(2500m,5σ)`/`max(180m/s,5σ)` 제안은 큰 측정 R가 cap을 무한히 키울 수 있어 첫 게임 fixture 전에 기각됐다. 현재는 track P와 measurement R가 아무리 커져도 위 hard cap이 늘어나지 않는다. 측정σ는 진단 값일 뿐 cap 완화에 쓰지 않는다. 이 기각안의 결과를 현재 정책의 검증으로 합산하지 않는다.

이는 기존 network의 **경계 값**을 재사용한 것이다. network의 전체 state/속도 차이 검사와 local radar의 관측 LOS radial residual이 같은 측정 모델이라는 뜻은 아니다. 새 로컬 적용의 정당성·장거리 영향은 각 실제 입력 경로에서 별도로 검증해야 한다.

### 위치·radial의 실제 사용 차원

- AIR/Cartesian sanity는 관측에 finite z가 있을 때 xyz 위치 residual을 사용한다. Surface sanity는 xy만 사용하고 8m prior를 실제 z 관측으로 취급하지 않는다.
- radial residual은 실제 `radialMps`가 제공되고 해당 filter/receiver velocity와 LOS가 알려질 때만 계산한다. Surface의 수직 성분은 투영 차원 밖이다. AIR LOS의 수직 성분이0이 아니면 receiver vz도 명시적으로 있어야 하며, 누락을 숨은 truth나 임의0으로 보충하지 않는다.
- Doppler가 없는 BridgeMaster/외부 위치 보고에 새 속도 관측을 만들지 않는다. radial guard를 평가하지 못한 상태는 `null`이며 “속도 일치”라는 증거가 아니다.
- `measurementPositionSigmaM`는 제공된 measurement noise의 진단적 변환이다. 어떤 입력에서 sigma 성분이 없어 convenience0이 나와도 실제 수신 noise0/완전한 위치라는 뜻으로 소비하면 안 된다. cap/권한은 이 진단 값으로 확장하지 않는다.

2500m/180m/s의 로컬 적용은 먼 표적의 큰 오차·정당한 재획득을 거부할 수 있다. 이 영향은 자연 RF 및 실제 교전 자료로 확인해야 하며 unit의 distant-P 거부만으로 모든 실제 재획득이 보존되었다고 주장하지 않는다.

## 3. 일대일·모호성 선택

1. adapter가 기존 eligibility/관측 차원/native NIS를 평가한다. 기존에 평가하지 않은 후보를 “native evaluated”로 기록하지 않는다.
2. shared helper는 finite index/전술 track ID/cost를 복사하고, 중복 edge와 gate 밖 자료를 제거한다. `sanity.ok=false` edge는 별도 reject 목록으로 보존한다. 원본 track/measurement를 mutate하지 않는다.
3. bipartite connected component별로 기존 Hungarian을 실행한다. 단일 edge는 바로 선택 가능하다. 큰 component는 명시 HOLD다.
4. 선택된 edge를 하나씩 가린 대안 matching을 비교한다. 대안과 기준 matching의 **cardinality가 같고** total cost 차이가 threshold 이내일 때, 매칭이 달라진 plot/track을 hold 집합에 넣는다. 모든 후보가 둘 이상이라는 이유만으로 무조건 hold하는 정책과 다르다.
5. held plot/track은 새 arbitrary assignment를 소비하지 않는다. ACTIVE caller는 이를 `no match→새 파일`로 잘못 해석하지 않게 해야 한다.

이 helper는 MHT/JPDA가 아니며 시간 전체의 track lineage나 모든 대안을 저장하지 않는다. 같은 cardinality를 비교하는 한계, dummy penalty로 인해 cardinality가 이미 달라질 수 있는 한계, bounded component의 갱신 공백 위험을 남긴다. Hungarian이 한 matching을 반환했다는 사실 자체가 물리적 표적의 정답 ID 증명은 아니다.

## 4. 경로별 적용 범위

아래는 현재 준비된 manifest와 후속 RC1 합성 범위다. 반드시 최종 BUILD의 `allowedChangedSymbols`/changes와 fresh native coverage를 대조한다. RC0에 없던 own 적용을 RC0 시험으로 검증한 것으로 쓰지 않는다.

| 경로 | B의 실제 정책 범위 | 보존·잔여 사항 |
|---|---|---|
| own SPY global `spyGlobalAssignmentsV36` | 기존 사전 후보 graph/native Hungarian 비용에 shared sanity·일대일·ambiguity 적용 | 한 physical dwell의 used 계약 유지. SHADOW에는 실제 기존 Hungarian 결과를 반환 |
| own surface `surfaceAssignmentsPreferEstablishedWip13B14` | established surface stage와 early AIR/cross stage 각각 shared 선택 | established-first 순서와 cross-domain gate를 유지. stage1 held row/track을 stage2에서 되살리지 않음 |
| own held 후처리4곳 | `executeSpyTask`, `spyExecuteSurfacePlotsWip13B9`, `spq9bAcceptSurfacePlotsWip13B1`, `bridgeMasterEAcceptAnonymousPlotsV35` | held plot을 tentative birth/capacity 소비/다른 file 회복으로 보내지 않음. transient held Map 메타데이터만 사용, 작전 저장에 추가 안 함 |
| NPC `observerAcceptPlotsC` | 기존 all-pairs native graph에 shared sanity·선택/hold 적용 | owner store/RNG 및 update closure 유지. selected edge의 실제 EKF 거부와 admissible native fallback 구별, 같은 거부 pair를 두 번 correction하지 않음 |
| Hawklink `drainOffboardC`/`acceptOffboardC` | 같은 source+원 측정 epoch cohort에서 동시 일대일, 정확 반복 payload 및 pair별 재전송/fresh-AIR 관측차원 guard | 다른 source/epoch를 한 덩어리로 합치지 않음. 기존 delayed report 변환·P 확대·native gate25·age와 wire schema 유지 |
| focused own SPY/AIR·surface 선점 | **live 기존 경로 유지** | 예약 file에 대한 최소 native NIS 우선권을 global 매칭으로 바꾸지 않음. focused가 새 sanity/hold 전체로 보호됐다고 주장 금지 |
| SPQ AIR `spq9bBestTrackForPlotV34`/accept | **live 순차 winner 유지, passive B trace만** | 이전 plot의 update 사이에 다음 NIS를 평가하는 native 순서를 보존. trace는 `commonEpoch:false`, partial sequence이며 전체 frozen batch 대안이 아님 |
| C55 자함/NPC | **live 기존 association·RF·제어 유지, shadow graph 비교만** | [C55_AUDIT.md](C55_AUDIT.md)/[C55_FIXTURE_PLAN.md](C55_FIXTURE_PLAN.md). C55 live ambiguity 해결/전체 source-order 문제 closure 아님 |
| ESM/ISAR/IFF/Link16 CI/AI | 새 live 연관·식별 정책 적용 없음 | A의 관측·증거 계약 및 기존 소비자/권한 유지. 새 CEC/원격FCS/OODA 없음 |

### own stage와 hold 전달

surface의 established-first는 별도 우선권이다. 양 stage를 통합한 혼합 Hungarian으로 바꾸지 않는다. stage1 held track을 다음 stage에서 못 쓰게 하는 임시 예약은 필터 hit/실제 수용이 아니다. 반환 Map의 `trackBHeldPlots`는 caller의 생성 분기를 막기 위한 transient association 결과다.

`ASSIGNED`, 실제 `UPDATE_ACCEPTED`, `CONTRIBUTION_WITHOUT_CORRECTION`, `HOLD`, `UNMATCHED/CREATE`는 구분한다. Surface 위치-only candidate가 gate를 통과해도 후속 실제 radial 포함 native EKF가 거부할 수 있다. SPY-preferred SPQ 기여가 correction/hit0인 기존 정책도 그대로다. 선택 성공을 관측 확인 성공으로 부풀리지 않는다.

## 5. Hawklink cohort·replay·시간 계약

cohort는 **같은 source와 원 측정 시각**의 도착한 보고 묶음이다. source+epoch 자체를 “같은 표적”이나 global dedupe key로 쓰지 않는다. 같은 scan의 서로 다른 접촉은 동일 epoch일 수 있기 때문이다. 정확 반복 signature는 보고 position/P/domain evidence 등 실제 내용으로 구분하며, 이 정보는 수신한 payload 범위만 사용한다.

다음은 서로 다른 제약이다.

- 연결/최대 age/지연·queue 등 기존 ingress 거부.
- 후보 pair가 source의 같은/오래된 epoch를 이미 반영했는지.
- source surface 보고가 아직 fresh한 실제 AIR3D 관측 파일을 가정 고도로 덮을 위험이 있는지.
- graph의 near-equal matching ambiguity.

하나의 먼 큰-P 파일이 NIS 안에 들어왔다는 이유로 다른 정상 파일/합당한 신규 접촉 전체를 replay로 막으면 안 된다. pair별 sanity와 eligibility를 먼저 구분한다. 반대로 같은 자료를 재수신했다는 이유만으로 실제 hit/confirmed/age를 늘리지 않는다.

**일반적인 새 시간 정렬기를 구현한 것은 아니다.** 기존 filter state는 기존 tick/predict 지점에 있고, offboard report는 기존 `offboardPlotC`의 나이에 따른 P 증가(age²×속도 prior)를 거쳐 비교된다. payload에 없는 표적 속도를 합성하거나 모든 센서 상태를 공통 진실 epoch로 되돌리는 기능은 없다. source epoch/수신 epoch/state epoch와 그 한계를 계속 표시한다. Link16의0.5 Covariance Intersection은 바꾸지 않는다.

SHADOW Hawklink의 비교는 원래 sequential loop가 실제로 평가한 NIS를 그 자리에서1회 기록한 것이다. 앞 commit 전의 모든 원시 보고를 frozen graph로 평가한 것처럼 `commonEpoch:true`라고 표시하지 않는다. ACTIVE cohort의 전·후 상태와 별도 비교한다.

## 6. C55 shadow는 거리 m, native 결정 대체 아님

C55는 range/az/el3관측이 변환된 상대 xyz 거리 gate를 사용하며 실제 Doppler/NIS가 없다. 별도 파일 snapshot과 원래 source 순서의 실제 accepted measurement로 shadow를 만든다.

- native에서 이미 계산한 d/gate를 포착하고, frozen snapshot으로 추가 계산한 seen-file edge는 `SHADOW_COUNTERFACTUAL_NATIVE_SEEN`으로 표시한다.
- shared solver의 숫자 cost ABI 필드명이 `nis`여도 C55 입력 값은 **거리m**, `costUnits:'m'`, `ambiguityDeltaCost:0`이다. trace는 `distanceM/distanceGateM`만 내보내며 NIS/확률이라고 주장하지 않는다. exact tie에는 공통 수치 epsilon만 적용한다.
- known-own partition은 기존 발사 inventory boolean 그대로다. 적 ASM과 own RAM을 같은 파일에 넣거나, unknown no-DL Harpoon을 숨은 owner로 FRIEND 지정하지 않는다.
- helper의 hold/새 assignment는 native C55 제어·보호·사격에 전달되지 않는다. 전체 제품이 ACTIVE여도 C55 event는 `active:false`, `SHADOW_DISTANCE_ONLY`다.
- native 신규 파일은 pre-sweep old-file 제안에 없으므로 `NATIVE_NEW_FILE`로 구분한다. capacity/overflow/invalid과 native birth를 모두 “unassigned 실패” 하나로 섞지 않는다.
- trace OFF에는 새 snapshot/candidate 배열·추가 producer/NIS/lazy bank 조회가 없다. enabled일 때도 physical source key/proxy ID/실제 속도는 공용 DTO에 넣지 않는다.

C55 direct-native post-RF fixture에서 두 문맥의 own-first/foreign-first 보호, exact-tie shadow hold, no metre-as-NIS, source-key canary 없음이 확인된 RC0 자료가 있다. 이것은 **익명 측정 주입 후 실제 sweep/helper를 실행한 fixture**이며 자연 RF/Pd/실제30시드 교전 증거가 아니다. 최종 candidate에서 다시 묶인 결과는 최종 검증 hash를 따른다.

## 7. 기존 정책과 비누수 보존

| 보존 항목 | 이번 단계에서 하면 안 되는 것 |
|---|---|
| EKF/NIS/관측 noise kernel | 재계산·gain/행렬·RF Pd/Pfa/SNR/RCS/clutter 수치 조정, 음수 고도 clamp 임의 변경 |
| 3D 증거/prior | 기존16s TTL 늘리기, 영구 AIR/고도 고정,8m를 관측 z로 승격 |
| identity/IFF | 분류·near matching을 HOSTILE/FRIEND/NEUTRAL이나 새 IFF 응답으로 만들기, 보호 임의 삭제 |
| authority/무장 | UNKNOWN ROE, MANUAL/HOLD, native 발사 관문, 채널·사각·재고, PN/Kappa/신관/Pk/피해·RNG 보정 |
| 함별 독립성 | own/NPC/Hawklink/Link16/C55/helo 목적별 파일을 공통 TrackStore로 강제 통합, 다른 함 private FCS를 참조 |
| 외부 보고 | ESM bearing에 xy/거리 보충, ISAR를 새 위치 hit/자동식별로 승격, sender6D를 독립 raw6관측으로 위장 |
| AI | H1~H4/OODA/새 utility 점수·자동적성·전술 정책 도입 |

association은 전술 ID, 관측 geometry/noise, 수신 함의 filter estimate와 age, 명시 provenance만 사용한다. target truth ID·실제 owner/faction·시커/INS·숨은 생존/속도는 RF 물리 합성 또는 독립 AFTER_ACTION 시험에서만 사용한다. 새 shared pair copy/trace는 whitelist다. baseline에 남은 legacy boundary debt를 이 단계에서 해결했다고 주장하지 않는다.

## 8. 검증 판정과 미해결 위험

- **RC0의3개 실패는 실패다.** own 연결/후처리가 빠졌던 상태를 전체ACTIVE 성공으로 선언하거나 expected assertion을 바꿔 통과시키지 않는다. RC1은 실제 새 HTML·helper·native caller로 재실행해야 한다.
- 최종 native ingress가 통과해도 synthetic plot fixture다. natural hover60s/route120s/Harpoon75s, false alarms/clutter, 실제 CIWS30/419025, UI213/WebGL8/기존29단언, owner당1tick·1/8/16/64배속·성능을 별도로 본다. 기존 도메인420에 새 fixture 수를 더하지 않는다.
- hard caps는 부당한 큰-P 병합을 막지만 정당한 장거리 재획득도 차단할 수 있다. hold는 ID swap을 줄일 수 있지만 갱신 공백·coast/drop·무방비 결과를 늘릴 수 있다. component12 제한은 밀집 상황에서 특히 주의한다.
- ΔNIS1은 heuristic이고, cost matching은 최대-cardinality 보장이 없으며, focused/SPQ AIR/C55 live가 남아 있다. **모든 경로의 연관·모호성·ID 수명이 해결됐다는 closure는 없다.**
- 일반 source lineage/correlation·identity evidence TTL·lifecycle 재설계는 C/D 단계다. 현재 Hawklink guard가 모든 network replay/correlation 문제를 해결하지 않는다.
- inherited419025는 기존 요격→피격 **FAIL(미해결)**, CG→friendly paired2는 실제 observer 상태 **KNOWN_DELTA(미승인)**다. 구형 EMCON UI14는 **BLOCKED/INCOMPLETE**로 남긴다. B가 이 차이를 재현해도 승인·해결로 바꾸지 않는다.
- `releaseApproved=false`, 기대값·허용 오차 갱신0, main/기준 branch 병합·PR/release/tag 생성 없음을 유지한다. 새 전투 손실/false merge/ID swap이 보이면 원인과 증거를 보고하고 RF/무장/RNG 조정으로 맞추지 않는다.
