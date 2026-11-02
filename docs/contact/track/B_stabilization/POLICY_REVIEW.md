# TRACK-B 안정화: ambiguity HOLD 정책 검토

상태: **READ_ONLY_DESIGN / 제품 구현·브라우저 검증 전**. 이 문서의 소유자는 분석 agent이며 제품 변경은 root가 담당한다. 제안은 결과를 맞추기 위한 Δ1 축소, hit/ID 보너스, RF/EKF/운동/식별/ROE 계수 조정이 아니다.

기준은 `track-b-stabilization-a@1d92554026d15f417d987aec519007ea9657a6b6`의 `docs/contact/track/B/association.js`와 해당 커밋에 고정된 실제 native 증거다. sparse checkout으로 과거 Markdown/JSON이 작업 트리에 없더라도 `git show HEAD:<path>`로 읽었다. 과거 파일·기대값은 변경하지 않았다.

## 1. 먼저 확정할 사항

1. **작은 NIS 차이 하나는 실제 동일 우도의 증명이 아니다.** 서로 다른 예측 P를 가진 파일은 같은 잔차도 서로 다른 S로 정규화한다. 더 넓은 P는 NIS를 낮출 수 있다.
2. 반대로 **NIS가 근접했다는 이유만으로 반드시 잘못 보류한 것도 아니다.** 같은 모델·epoch·S에서 현재 측정이 두 해를 구분하지 못하면 HOLD는 정당하다. 기존 사격 시각을 복원하려고 그 경우까지 해제하면 안 된다.
3. 보수적 첫 개선은 기존 native NIS/gate/Hungarian winner를 유지한 채, **그 winner를 지지하는 독립적인 비교 근거가 충분할 때만 추가 HOLD를 해제**하는 것이다. 정보가 없거나 근거가 충돌하면 보류한다.
4. 본 문서의 권고만으로 paired4/419012의 회복을 약속하지 않는다. 특히 두 plot×두 track의 완전 permutation에서는 covariance volume 항이 상쇄될 수 있다.

## 2. 현재 정책과 실제 원인 증거

`trackBSolveB`는 native gate·geometry sanity를 통과한 graph의 component를 Hungarian으로 푼다. 선택 edge 하나를 금지한 대안을 다시 풀어 cardinality가 같고 `alternative.total - base.total ≤1`이면 바뀌는 행/열을 HOLD한다. component가12행 또는12열을 넘는 경우도 HOLD다. total은 매칭된 real edge의 NIS 합이며 filter P·measurement R·관측 차원·epoch는 비교 입력에 없다. fixed2500m/180m/s sanity는 별도이며 유지해야 한다.

실제 사격 결과를 보고 기준을 조절하지 않은 native 증거:

|사례|최초 실제 HOLD|대안 NIS 합|차이|관측한 후속 경로|
|---|---|---|---:|---|
|DDG paired raid|tick194 /3.233333s|13.57587226717646 vs13.527191648311145|0.04868061886531372|갱신·scheduler 변경 → SAM2 발사8.8→9.0s →708kg 적재 이력·선체 응답 변화|
|CG paired raid|tick197 /3.283333s|8.864592769863421 vs9.379944785850297|0.5153520159868759|동일한 종류의 관측·발사·적재 이력 변화|
|D1 seed419012|tick1796 /29.933333s|1.4913444179610076 vs1.1536789827861333|0.33766543517487424|갱신 보류 → canonical/P·native 캐시 TTI 변화 → 최종 두 mount cue002→001|

paired의 첫 네 edge는 기존 gate64와2500m/180m/s sanity를 모두 통과했다. 첫 원인은 gate/sanity 실패나 component 크기 제한이 아니다. 실제 precomputed input/return 기록은 `B/evidence/paired-cause-120/CRITICAL_NATIVE_EDGES.json`이다. 네 paired strict FAIL은 미승인이다.32/120초 모두 완료된 습격 결과를 입증하지 않았다는 제한도 유지한다.

419012는 두 후보가 **같은 실제 AIR4D 관측**을 받았다. rangeσ40.51012879845772m, azσ0.0765191321748646°, elσ0.1500375140683619°, rdotσ8.102025759691543m/s다. 두 파일 모두 직전1795에 SPY_HIGH_THREAT로 이미 재획득됐다.29.0초의002가 VISUAL1hit/age4.5s·큰 P였다는 사실을 최초 HOLD 시점의 상태로 대체하면 안 된다. 최초 HOLD 무렵 P의 위치 대각은 대략001 `[.2,1.8,.4]`,002 `[.5,41,.96]`이며 실제 측정 R가 상당 부분 지배한다. **단순 stale/broad vs precise 예외가419012의 실제 수정을 증명하지 않는다.**

원래419012 after 종료 자료의 차이는 cue 두 개지만 canonical/P/source·재방문 경로 변화는 실제다. 양쪽 RAM3발·피격0·HP100·종료30.633333s 동일은 이 사격의 결과 관측이며 strict FAIL 승인이나 모든 미래 전투 불변을 뜻하지 않는다. 두 파일은29초 이전부터 존재했고 capture 창에 CREATE가 없으므로 duplicate 제거를 입증한 사례도 아니다.

## 3. 정당한 HOLD의 조건

다음을 모두 만족하는 **경쟁 대안**이 있을 때, 관측으로 해를 구별할 수 없다면 HOLD가 정당하다.

- 같은 observer의 실제 한 batch/physical dwell에 속한 독립 관측이다. native used/excluded·stage·scheduled priority를 보존한다.
- 두 해 모두 같은 실제 관측 모델·차원·원점·receiver 속도 계약을 사용한다. 수상8m prior나 미관측 Doppler0을 새 측정으로 사용하지 않는다.
- 양 해의 모든 edge는 기존 eligibility/native NIS gate·fixed geometry sanity를 통과한다. 금지 edge, 과거 보고 replay, invalid covariance를 대안으로 되살리지 않는다.
- filter estimate의 epoch와 관측 epoch가 호환된다. 현재 fixed tick에 이미 predict된 상태를 sensorAge만큼 또 predict하지 않는다.
- 같은 cardinality뿐 아니라 비교에 사용한 관측·track 집합과 미사용 row의 의미를 설명할 수 있다. 서로 다른 차원/보고 종류의 row를 골라 쓴 두 해는 raw NIS 합만으로 같은 정보량이라 할 수 없다.
- 전체 matching 관점에서 경쟁이 남는다. 한 row의2위 값이 근접하더라도 다른 row가 상대 track을 강하게 제한하면 유일한 해일 수 있다.
- 관측·P/R·실제 시간·운동 연속성에서 얻은 근거가 한 해를 충분히 구별하지 못한다. 단순 track 번호·먼저 태어난 순서·identity·faction·owner·truth는 구별 근거가 아니다.

S/시각/모델이 빠졌다면 **실제 ambiguity를 입증한 것**과 **판정 근거 부족**을 구별해 reason을 남긴다. 근거가 부족하다고 임의 match를 주지 않으며 보수적으로 HOLD할 수 있지만, 이를 완전한 확률 판정이라고 설명하지 않는다.

## 4. 권고 후보 A — native winner에 대한 covariance-aware HOLD 해제

관측 innovation covariance `S = H P Hᵀ + R`와 native NIS를 같은 실제 평가에서 얻을 수 있다면, 같은 측정 모델의 조건부 Gaussian 비교 비용은 다음과 같다.

```text
edge evidence cost = native NIS + log(det(S))
matching evidence cost = 비교 가능한 real edge cost의 합
```

같은 관측 row·dimension을 쓰는 비교에서는 `m·log(2π)`와 단위 상수는 상쇄된다. 이것은 S가 커질수록 작은 NIS를 주는 효과와 넓은 innovation volume의 낮은 밀도를 함께 표현한다. NIS를 확률이라고 이름만 바꾸거나, P를 줄이거나, KF를 다시 돌리는 방식이 아니다.

**가장 보수적인 적용안:**

1. 기존 NIS/gate/dummy/Hungarian으로 base와 near alternative를 구한다. 기존 winner를 다른 해로 교체하지 않는다.
2. full evidence가 비교 가능한 상태인지 확인한다. 같은 epoch·관측 모델·실제 R/P, finite positive-definite S와 동일 row/track 정보 계약이 필요하다.
3. 기존 near alternatives가 모두 full evidence에서도 base보다 분명히 나쁘면 추가 HOLD만 해제한다. 기존 Δ1을 별도 결과맞춤 값으로 낮추지 않는다. 동일 기준1을 새 비용의 비교 휴리스틱으로 유지한다면 그 의미는 별도로 명시해야 하며 보정된 posterior 확률이라고 주장하지 않는다.
4. NIS winner와 full evidence winner가 충돌하거나, near alternative가 남거나, 필요한 정보가 없으면 HOLD 유지/근거 부족으로 기록한다.
5. 보류 해제 후에도 native correction의 원래 gate를 그대로 실행한다. correction 거부를 억지 수용하지 않는다.

양성 예: 동일 관측에서 native NIS winner가 실제로 좁고 일관된 S를 갖고, 상대 후보는 큰 P 때문에 비슷한 NIS만 얻은 경우. full evidence도 같은 base를 충분히 지지하면 불필요한 HOLD를 해제할 수 있다. 상대가 단지 오래됐다는 이유로 제외하는 것이 아니다.

음성 예: native NIS는 broad 후보를 조금 선호하지만 full evidence는 precise 후보를 선호한다. 이때 secondary score를 핑계로 precise 파일을 강제 선택하지 않고 HOLD한다. 두 모델이 상충한 것이다. genuine coast/reacquisition file도 단지 나이가 많다는 이유로 일괄 금지하지 않는다.

### 이 후보가 해결하지 못하는 것

- **두 plot×두 track 완전 permutation에서 receiver/model/R가 같으면**, 각 해가 각 track을 한 번씩 사용하므로 `logdet S(trackA)+logdet S(trackB)`가 양 해에서 정확히 상쇄된다. 따라서 paired의 작은 총 NIS 차이는 그대로 남을 수 있다. 이를5건 복구 장치라고 설명하면 안 된다.
- plot별 R나 origin/model이 다르면 상쇄가 완전하지 않을 수 있지만, 정확한 native S를 봐야 한다. 실제 첫 paired edge 기록에는 S/P/R 전체가 없으므로 역사적 JSON만으로 full score가 강한 구별을 준다고 확정할 수 없다.
- 1track에 여러 plot이 경쟁해 선택 row 자체가 달라지면, 미사용 plot의 clutter/detection likelihood까지 필요한 경우가 있다. 이번 범위에는 새 Pfa/Pd/clutter prior를 만들지 않는다. 단순 Gaussian 밀도만으로 서로 다른 정보량의 unmatched-row 해를 동등한 posterior라고 취급하지 않는다.
- joint measurement correlation이 있는 센서/재전송이면 독립 edge Gaussian 곱은 완전한 모델이 아니다. 기존 Hawklink/Link16 lineage 한계를 감추거나 CI를 대체하지 않는다.

## 5. 후보 B — 실제 운동 연속성은 중복 증거로 가산하지 않기

운동 연속성은 우선 **native predict된 x/P와 실제 수신 모델**로 읽는다. 기존 CV/Q 및4D Doppler innovation에 이미 반영된 이력을 age/hit/track 수명 가중치로 다시 더하면 같은 근거를 이중 계산할 수 있다.

허용 가능한 구별:

- 실제 receiver origin/velocity, 측정 range/az/el/rdot, native filter epoch의 일치 확인.
- 같은 source의 독립적인 마지막 fix와 replay/재전송 여부를 구별. 같은 fix를 fresh 새 hit로 세지 않음.
- 현재 모델에 실제 포함된 measured Doppler와 관측 차원의 residual. prior8m·미관측 수직속도는 판별 채널이 아님.
- 추정 상태가 실제 측정 시각으로 정렬돼 있는지와 native prediction이 이미 수행됐는지 확인.

이번에 권고하지 않는 지름길:

- confirmed/hits가 많거나 ID가 작으면 항상 승리시키기.
- source가 VISUAL/remote라는 이유로 모든 경쟁에서 배제하기.
- age를 낮은 비용 보너스로 변환하거나 coast를 blanket 거부하기.
- 수평 tangential velocity를 단일 Doppler가 직접 측정한 값처럼 비교하기.
- 해가 근접했다는 이유로 KF 평균/P·Q·기동 한계 또는 gate를 조정하기.
- 같은 예측 state/P에 sensorAge만큼 추가 predict하거나 숨겨진 truth 속도로 과거 fix를 현재로 이동시키기.

같은 위치·같은 radial을 순간적으로 만드는 교차는 그 한 관측에서 ID가 관측 불가능할 수 있다. 과거 이력은 native filter에 존재하더라도 그 순간의 미측정 성분을 새 센서 증거로 꾸미면 안 된다. strong continuity 증거가 없으면 HOLD가 정당할 수 있고, 결과가 이전 사격 일정과 달라진다는 이유만으로 해제하면 안 된다.

## 6. native 데이터 취득과 구현 경계

현재 `trackBSelectB`는 `{i,id,nis,sanity}`만 받는다. `sanity.measurementPositionSigmaM`는 전체 S가 아니고 filter P까지 포함한 혁신 타원체도 아니다. 이 scalar나 P trace·대각합만으로 `logdet S`를 대체하면 안 된다. 교차 공분산을 버리면 다른 모델이다.

root가 후보 A를 택한다면 **이미 실행한 native association 평가 지점**에서 dimension·observed fields·실제 측정 epoch·state epoch·native S(또는 검증한 logdetS)를 companion 값으로 전달해야 한다. 실제 측정/필터 연산·native NIS 반환 순서는 보존하고, exporter/solver가 association helper를 다시 호출하지 않는다. AIR는 기존 cached projected covariance와 R, surface는 기존 계산한2D/3D S가 출처다. cache getter를 다시 불러 관측을 재구성하지 않는다.

필요한 계약:

- payload-object/track tactical ID는 해당 batch 안에서만 상관시킨다. target object/ref를 전달하지 않는다.
- unknown/missing timestamp·noise·origin은 null/unknown으로 남긴다. filter P로 누락된 센서 noise를 대신 채우지 않는다.
- logdet는 full S의 positive-definiteness를 확인해 안정적으로 계산한다. singular/invalid이면 evidence unknown이며 native gate를 억지 통과시키지 않는다.
- SI/rad 단위와 실제 적용된 측정 차원을 명시한다. 같은 정보량이 아닌 모델의 비용은 직접 비교하지 않는다.
- NIS·gate·RF·EKF update 수치·identity/authority·MANUAL/HOLD·예상 발사권한은 그대로다. LIVE 새 정책과 diagnostic ON/OFF는 분리한다.
- existing focused priority·surface-established-first·per-physical-dwell used·failed-correction fallback·held→no-create를 보존한다. 단계 통합으로 우선권을 지우지 않는다.
- component bound12·fixed2500m/180m/s·기존 invalid/replay 처리 유지. 변경이 필요하면 별도 원인/승인 항목으로 공개한다.

후보 A가 native metadata 범위를 과도하게 넓힌다면 이번 안정화에서 **shadow 설계/계측만** 먼저 적용하는 편이 정당하다. S 없는 상황에서 새 scale factor를 만들어 결과에 맞추는 것은 대안이 아니다.

## 7. 구현 전 양성·부정 검증

기존 B47/native90/cohort14와 과거 기대값은 수정하지 않는다. 새 계약의 검증은 별도 점수이며 fixture-only와 자연 RF/전투를 구분한다.

|분류|조건|필수 결과|
|---|---|---|
|양성1|1plot/2track, native base와 full evidence 모두 명확한 같은 해; 상대의 큰 P만 NIS를 비슷하게 만듦|기존 실제 gate 안의 base만 선택, identity/권한 승격0|
|양성2|두 row가 전역 제약으로 유일한 matching을 만듦; 한 row만 보면 근접|row-local margin로 오보류하지 않음, one-to-one 유지|
|양성3|2plot/2track, plot별 실제 R/모델 계약이 비교 가능하고 full evidence가 base를 분명히 지지|추가 HOLD만 해제; 순열/ID 재부여와 무관|
|음성1|equal S와 실제 관측·예측의 exact/near tie|HOLD 유지, 임의 ID winner·새 tentative 생성0|
|음성2|2plot/2track 완전 matching, 동일 receiver/R라 logdet 합 상쇄|단지 covariance 항을 넣었다고 해제하지 않음|
|음성3|NIS winner와 full evidence winner 충돌|HOLD/근거 상충, 다른 해 강제 선택0|
|음성4|missing/Singular/NaN S·noise·epoch·model mask 불일치|unknown/보수적 처리, 0 noise·now 채움0|
|음성5|큰 filter P와 큰 measurement R|fixed geometry cap 유지, 넓은 uncertainty만으로 먼 match 허용0|
|음성6|2D surface prior8m·누락 Doppler·receiver vz 미상|없는 채널로 강한 구별 근거 생성0, AIR3D 근거/기존 EKF 보존|
|음성7|실제 공백 후 coast/reacquisition|age/hits/id blanket 배제0; 유일한 유효 관측은 기존 방식으로 재획득 가능|
|음성8|같은 원 fix의 replay·서로 다른 센서/epoch·unknown correlation|독립 확정으로 중복 집계0, freshen0, 기존 wire/CI·권한 계약 유지|
|음성9|1track/2plot에서 선택 row 집합·관측 차원이 달라지는 대안|새 detection/clutter 모델 없이 calibrated posterior라고 해제0|
|음성10|focused·surface stage·실제 correction 실패 후 fallback|우선권/held/no-create/used 및 원래 실패 후처리 보존|
|보존|same observations에 truth/ID/faction/owner/hit 장식만 변경|구별 근거·선택이 바뀌지 않음, 입력 mutation0|
|보존|진단 OFF/ON·반복 query·배속·owner|RNG/트랙/물리 불변, 실제 helper 평가1회,1owner1tick|

특히 새 broad-vs-precise fixture를419012의 실제 수정 재현이라고 이름 붙이지 않는다.419012·paired 최초 edge는 원래 조건·시드·제품에 고정해 S/epoch 계약을 실제 native 경로에서 추가 계측하고, 결정 전후 관측·선택·HOLD 이유를 남긴다. 첫 차이와 최종 결과는 분리한다. paired4의 launch/mass/physics 경로와419012의 cue 경로가 유지되거나 달라진 이유를 보고하며 기대값은 승인 전 갱신하지 않는다.

## 8. 판정과 남은 위험

이 검토의 우선 권고는 **native 계산의 full innovation evidence를 확보한 뒤, 기존 winner를 더 강하게 지지하는 경우에만 HOLD를 줄이는 제한된 shadow→live 전환**이다. 새 물리 모델, RF 튜닝, KF 보정, 자동 식별/ROE 변경은 필요하지 않다. 다만 실제 과거 near ties가 진짜 약한 관측이라면 HOLD가 남는 것이 맞을 수 있다.

실제 검증이 모든5건을 회복하지 못해도 결과에 맞춰 Δ1·cap·PN·발사·피해 RNG를 바꾸지 않는다. 새로운 성공→실패, old-file 강제 매칭·ID swap·아군 보호 오염은 FAIL로 보고한다. 모든 native·자연 RF·전투·성능·저장/배속 검증 전에 안정화 완료·기대값 승인·main 병합·전체 release 승인으로 확대하지 않는다.
