# 안정화 후보 구현의 독립 정적 검토

상태: **READ_ONLY_SOURCE_REVIEW / 실제 실행 검증 대기**. 제품·패치·시험 기대값을 수정하지 않았고 브라우저·시험을 실행하지 않았다. `POLICY_REVIEW.md`는 구현 전 설계로 보존하며, 이 문서는 실제 선택된 구현과 그 차이를 설명한다.

검토 기준:

- `association.js` SHA-256 `ec66a28a8bb92888228a45a6a626007f288c440b3054e2e203730bbe9e8e4c71`.
- 현재 `patches.json` SHA-256 `29145e9bf8f159134e08244e73b095230a56d0e8ec54c82aa7653c68ce9e50e2`.
- 최초 검토 patch SHA는 `5b4c46f744272a9fb152556c25be30cab1e3ec5414d22820770c80460c08cb90`였으며, 아래 surface 모델 경계 발견 후 guard가 추가됐다. 이 이력은 삭제하지 않는다.
- root 보고상 최초 SHADOW native의 canonical 순수성 검증은 통과했으나, **현재 surface guard를 포함한 새 frozen 산출물 재검증은 대기 중**이다. 새 ACTIVE 제품은 아직 생성하지 않았다. 이 agent의 정적 검토를 실제 시험 PASS로 세지 않는다.

## 1. 현재 실제 live 경로의 차단 결함 여부

검토한 **현재 네 가지 연결 경로**에서 native NIS winner·gate를 다른 해로 바꾸거나, canonical x/P·hit·분류/IFF/identity/authority·ROE를 직접 수정하거나, target truth/owner/faction을 읽어 증거를 강화하는 경로는 찾지 못했다.

다만 이 결론은 함수 호출부의 실제 모델·epoch 계약을 전제로 한다. 최초 검토의 일반화된 surface3D NIS/2D companion 위험은 현재 guard가 인증을 차단하도록 보완했다. metadata API의 임의 외부 호출, nativecache/성능/상태 순수성은 아래 경계와 실제 검증으로 따로 다룬다. 프로젝트 전체·모든 가능한 호출의 비누수를 증명했다는 뜻은 아니다.

## 2. 설계에서 달라진 데이터 취득 방식

설계 권고는 기존 NIS 평가가 이미 만든 S를 companion으로 수출하는 것이었다. 실제 구현은 물리/필터 함수 body를 보존하고 **네 caller의 pair 생성 지점**에서 증거 helper를 호출한다.

|지점|실제 구현|추가 작업과 한계|
|---|---|---|
|AIR, L123–130|기존 `trackRadarAssociationKernelPerfC(tr,meas)`를 다시 읽고 projected covariance에 native와 같은 R를 더함|같은 state/P/origin이면 기존 cache 재사용. 불일치하면 derived cache가 재구성될 수 있음. cache 절대 무변경/무비용 조회라고 설명하면 안 됨|
|surface position, L131–136|native prediction/Jacobian/PHt/R와 같은 산술로2D S를 다시 만듦|추가 순수 행렬 계산·할당이 존재. 추가 NIS/Update/Predict/RNG 호출은 아님|
|Cartesian, L137–140|native Cartesian measurement covariance를 복사·정리한 R와 기존 P position block 합산|원래 모델의 R 처리와 같은 산술. reportedSurface는 valid evidence로 승격하지 않음|
|log determinant, L107–115|S에 Cholesky를 수행해 logdet 계산|native NIS 값을 변경하지 않는 추가 계산. positive-definite가 아니면 unknown/invalid|

AIR cache kernel은 모든6 state/36 P와 receiver origin/velocity를 확인한다. helper는 먼저 finite x/P가 이미 존재하는지 검사한다(L120–121). native init은 존재하는 x/P에서 바로 반환하므로 이 경로가 미초기화 파일을 새로 만들도록 허용하지 않는다. surface의 native prediction도 내부 init helper를 통과할 수 있지만 같은 사전조건에서 새 필터를 만들지 않는다. 따라서 **추가 실제 필터 초기화/예측/correction은 없도록 설계**되어 있으나 cache 변화·행렬 비용 자체는 있다.

이는 root가 명시적으로 선택한 구현상 타협이다. `api.evidence`를 모든 cache까지 순수한 getter라고 부르지 않고, canonical 게임 상태 무변경·출력 동일성·새 비용은 실제 native 검증으로 확인해야 한다. 잘못된 prior를 가진 API 호출이 내부 init을 유발하지 않는 부정 시험도 필요하다.

R의 floor/default는 현재 native association과 동일하다. 누락된 noise에 새0분산을 넣지는 않는다. 다만 native가 사용한 fallback R는 **모델 가정**이지 sensor payload가 실제로 보고한 σ가 아니다. 이 추가 근거를 “공개 센서 제원”이나 “새로 관측한 정밀도”로 내보내면 안 된다.

## 3. 모델·시간 계약과 현재 적용 범위

`patches.json`은 다음만 변경한다.

- NPC `observerAcceptPlotsC`: native pair의 surface 여부에 따라 `SURFACE_POSITION`2D 또는 `AIR`4D companion. 기존 NIS 평가 뒤의 같은 synchronous batch에서 현재 `now`를 전달한다.
- own SPY global: 기존 native costs를 만든 뒤 `AIR`4D companion. native 생성/call 시점의 fixed epoch를 전달한다.
- own surface staged helper: 실제 callback이 position-only이거나 native surface-radar callback에 Doppler가 없을 때만 `SURFACE_POSITION`2D companion. 나머지는 unsupported/invalid로 추가 인증을 막는다. 기존 stage/used/held·실제 correction은 그대로다.
- Hawklink cohort: `CARTESIAN`3D companion에 현재 epoch와 원 report.measuredAtS를 별도로 전달한다. 둘이 다르면 helper가 먼저 invalid를 반환한다(L119). 지연된 과거 fix를 now의 정밀 증거로 승격하지 않는다. `_reportedSurface`도 L138에서 invalid다.

현재 local RF producer의 “해당 native call에서 생성한 현재 관측”이라는 계약을 명시적으로 신뢰한다. 이 helper가 payload에 있을 수 있는 모든 시각을 자동 추론·검증한 범용 timestamp validator는 아니다. 특히 `measurementEpochS` 생략 시 default=epochS이므로, 외부 지연 payload를 local 인자로 넣는 별도 caller는 실제 원 시각을 명시해야 한다. sensorAge로 filter epoch를 추론하거나 추가 predict하는 코드는 없다.

**surface 모델 guard의 재검토:** 공용 `surfaceAssignmentsPreferEstablishedWip13B14`는 `nisFn`을 받는다. 최초 patch는 항상2D companion을 붙여 직접/후속 caller가 native3D surface NIS를 계산할 때 잘못된2D S로 HOLD를 해제할 가능성이 있었다. 현재 네 번째 patch는 다음 조건을 정확히 적용한다.

```js
nisFn===trackSurfacePositionAssociationNisWip13B9 ||
(nisFn===trackSurfaceRadarAssociationNisV35 &&
 !Number.isFinite(plots[i].radialMps))
  ? 'SURFACE_POSITION' : 'UNSUPPORTED_SURFACE_ASSOCIATION'
```

position callback은 원 plot에 radial이 있어도 native가 이를 뺀2D NIS이므로2D companion이 맞다. native surface-radar callback도 radial이 관측되지 않으면 실제2D이므로 맞다. **실제 radial이 있는 native3D callback이나 알 수 없는 callback은 unsupported가 되어 helper L141의 invalid 경로로 가며, certificate L152에서 보류 해제 근거로 쓸 수 없다.**

이는 native3D correction/보고를 삭제·거부하거나 gate를 강화한 것이 아니라, 모델이 불일치하는 **추가 우도 인증만 사용하지 않는** 보수적 guard다. 현재 SPY/SPQ position-only와 Doppler를 제거한 BridgeMaster는 계속2D로 설명된다. 새 guard를 실제3D callback fixture에서 확인하는 fresh metadata 검증은 별도 시험이며, 이 정적 재검토만으로 PASS를 부여하지 않는다. 범용3D surface evidence 지원을 구현했다고 확대하지 않는다.

## 4. HOLD 해제의 실제 논리

`trackBEvidenceCertificateStableB` L147–162는 다음 보호를 적용한다.

1. base가 component의 모든 row를 실제 track에 매칭한 경우에만 수행한다(L148). 선택 row가 달라지는 unmatched-row 가설의 clutter/detection likelihood를 새로 만들지 않는다.
2. 모든 eligible edge의 finite·valid evidence가 필요하다. 한 row의 대안들 사이 dimension/epoch가 일치해야 한다(L152–154). missing/invalid은 certification 실패이며 강한 증거로 변환되지 않는다.
3. cost는 `nativeNis+logdetS`; row 상수만 빼므로 complete matching의 순위는 변하지 않는다(L158).
4. 이 cost의 최적해가 **기존 native NIS base와 모든 row에서 동일**해야 한다(L160). 증거가 다른 해를 선호하면 HOLD를 해제하지 않는다.
5. base edge를 하나씩 금지해 얻은 모든 complete 대안이 기존 Δ1보다 나빠야 한다(L161). 새 값으로 기준을 줄이지 않는다.
6. native 비용 exact tie는 evidence certificate 전에 차단한다(L197/200–201). 숫자 ID 순으로 골라진 exact tie를 강한 선택으로 포장하지 않는다.

이 구조는 기존 NIS winner 외의 해를 새로 강제하는 경로가 없다. finite S가 있다는 이유만으로 보류를 해제하지도 않는다. 실제 같은-S 완전 permutation에서는 logdet 합이 상쇄되므로 paired 첫 HOLD가 남을 수 있다는 설계 한계도 그대로다.419012의 실제 R/P에서 해제가 가능한지는 별도 native 측정 결과로 판단해야 한다.

행별 model dimension/epoch 검증과 **component의 모든 row가 같은 모델·epoch라는 검증**은 다르다. complete matching에서 각 row의 모델이 모든 대안에서 같다면 row 상수가 상쇄될 수 있지만, 서로 다른 epoch의 joint correlation까지 모델링한 것은 아니다. 실제 네 caller의 같은-batch local/지연-offboard invalid 계약 밖에서 `api.solve`를 쓸 때는 추가 시간·상관 계약이 필요하다.

## 5. 큰 component의 증명된 일부 선택

작은 component는 원래 exact alternative 검사를 유지한다.12행/열을 넘는 component는 native global optimum을 먼저 구한 뒤(L185–192), real+dummy 비용을 모두 포함한 row-minimum relaxation lower bound로 선택 edge를 인증한다. 특정 base edge를 제거한 모든 feasible 해의 비용 lower bound가 base.fullTotal+Δ1보다 클 때만 그 edge를 유지한다.

각 row가 column을 중복 사용해도 되는 relaxation은 feasible matching 집합보다 넓으므로 lower bound다. 따라서 이 조건은 해당 edge가 모든 near-optimal matching에 필수임을 증명하는 충분조건이다. local mutual-best/greedy peeling으로 바꾼 코드가 아니다. 인증하지 못한 row/col은 HOLD하며,128행/열 초과는 `COMPUTATION_BOUND_HOLD`다. 인증된 row/col을 held set에 동시에 넣지 않는 구조도 확인했다.

이는 계산 범위/association 정책의 명시적 변화다. RF/EKF/기동 계수나 uncertainty cap을 키운 것이 아니다. lower bound가 느슨해 명백한 일부 해를 인증하지 못할 수 있으며,128이 모든 dense raid 성능을 보장하지 않는다. 포화 unit과 실제 mean/p95/game battle 검증을 구분해야 한다.

## 6. 무단 유효강화·정보 역류 검토

정적 검토 범위에서 다음을 찾지 못했다.

- native NIS threshold,2500m/180m/s, R/P/gain·process Q를 더 유리하게 바꾸는 코드.
- truthRef/objectId/faction/target owner·실좌표·hidden seeker/INS를 읽는 비교.
- hit·confirmed·track 번호·source 이름·identity·authority를 새 비용 보너스로 쓰는 코드.
- 관측하지 않은 surface z8m·Doppler0을 evidence 차원에 추가하는 코드.
- evidence가 선호하는 다른 해로 native winner를 교체하거나, missing metadata를 valid confidence로 복구하는 코드.
- 새 companion을 native EKF·분류·IFF·ROE/FCS·무장 입력으로 되먹이는 코드.

`observerShip`, tactical track ID와 epoch는 기존 batch 소유/상관 문맥이며 target truth를 판독하는 입력이 아니다. R의 native floor/default, local epoch의 caller 신뢰, derived cache 재사용은 명시적 모델/실행 가정으로 공개해야 한다. 이 가정들을 추가 센서 성능이나 측정으로 표현하지 않는 한, **현재 네 경로에서 무단의 물리적 유효강화를 찾지 못했다**는 것이 이번 검토 결론이다.

## 7. 남은 검증과 판정

필수 실제 증거는 root/시험 agent의 책임이다: frozen B↔새 SHADOW의 기존 상태/RNG/결과 동일성, metadata query의 canonical 무변경, R/S 산술·dimension/epoch 음성·양성, exact tie 유지, original native kernel 호출 수, 포화 component 및 one-to-one/held/no-create, 네 caller와 focused/fallback 보존, strict5의 전후 원인, 완료된 실제 전투, 성능/원래 회귀다.

이 검토는 그 시험을 실행하거나 PASS를 선언하지 않았다. 기존419025·paired/D1 미승인 FAIL·완료되지 않은120초 전투·C55/SPQ live SHADOW-only 제한도 해소한 것으로 세지 않는다. 제품 수정·기대값 갱신·main/기준 브랜치 병합·전체 release 승인은 하지 않았다.
