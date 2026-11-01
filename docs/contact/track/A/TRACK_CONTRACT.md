# TRACK-A 측정 계약과 진단 trace

## 1. 적용 범위

이 계약은 **DIAGNOSTIC_ONLY 호환 view**다. 기존 payload·TrackStore·필터·분류·IFF·수명·AI·발사 게이트·피해/무장 시스템을 교체하지 않는다. TRACK-A는 관측을 설명하고 실제 native 연관 결정을 추적하며, 이 레코드를 native 연관·FCS·자동 식별의 새 입력으로 사용하지 않는다.

규범 원천은 [INSTRUCTIONS.md](INSTRUCTIONS.md), baseline 경로 감사는 [TRACK_AUDIT.md](TRACK_AUDIT.md)다. 실제 구현 파일은 [measurement-contract.js](measurement-contract.js), fixture-only 검사는 [TEST_MATRIX_A.md](TEST_MATRIX_A.md)와 `test_contract.cjs`다. 최종 내장·연결 범위와 실제 실행 PASS 여부는 `REPORT.md`/`VALIDATION.json`에서 확인한다. **normalize 함수가 존재한다는 사실만으로 모든 sensor hook/실제 trace/동등성 검증이 끝났다고 선언하지 않는다.**

## 2. API와 공통 schema

```js
window.__TRACK_A__.normalize(kind, payload, context)
window.__TRACK_A__.configure({enabled: false, capacity: 1024})
window.__TRACK_A__.clear()
window.__TRACK_A__.snapshot()
```

`normalize`는 입력을 수정하지 않고 detached 호환 레코드를 만든다. 입력에 truth/불필요한 policy 필드가 있어도 whitelist 밖 값은 내보내지 않는다. 반복 조회로 게임 시계·난수·센서 producer·lazy filter helper를 호출하지 않는다.

| 필드 | 의미·결측 처리 |
|---|---|
| schema | `AEGIS_MEASUREMENT_CONTRACT_TRACK_A_1` |
| kind | 호출부가 알고 있는 기존 sensor/report 종류. target class/owner를 보고 선택하지 않음 |
| sourceSensor | receiver의 센서/보고 경로 식별. context 우선, payload source fallback, 없으면 UNSPECIFIED |
| observerShip | **자기 수신 함/receiver** 식별자. 목표 physical entity ID가 아님. 모르면 null |
| measuredAtS / receivedAtS | 원 측정 epoch와 실제 수신 epoch를 구분. payload/context에 없으면 null, 실제 0은 유효한 0. 현재 시각으로 과거 fix를 새 관측처럼 바꾸지 않음 |
| measuredFields | 실제 `observed`에 있는 독립 관측/특징의 mask. reported estimate의 x/v를 여기에 넣지 않음 |
| measurementModel | name, dimension, physicalObservationDimension, rows. 변환값·reported state 길이와 physical 센서 독립 차원을 구별 |
| observed | 실제 sensor/feature가 제공한 성분. 결측·NaN·Infinity를 0으로 바꾸지 않음 |
| assumed | surfaceReference, initializer·placeholder 등 model prior. 실제 측정으로 승격하지 않음 |
| derived | polar→Cartesian, 회귀/필터/기하 변환·분석 값. 별도 실제 hit가 아님 |
| reported | 외부 제공 위치/P, sender 추정 state/P, ISAR class 후보·position gate 자료. 직접 physical observation과 구분 |
| observerState | payload가 실제 제공한 receiver originM/velocityMps. world x/y를 m로 변환하며 누락 성분은 null. **receiver 자기 상태**이며 표적 위치·속도 관측이 아님 |
| uncertainty | 실제 제공된 sigma/P를 보존. 교차항이 없거나 해당 성분 noise가 없으면 **unknown**. 임의 0 noise/확정값/독립성을 만들어내지 않음 |
| quality / qualityOrigin / domainEvidence | 기존 제공 값·증거를 복사. 수신자가 만든 age quality는 qualityOrigin에서 reported/receiver-derived로 구분. confidence를 authority로 승격하지 않음 |
| provenance | 기존 sourceId/sequence/sender/전술 file 번호·시각·명시 retransmission 정보. 독립 여부가 없으면 null; packet sequence가 새롭다는 이유만으로 새 독립 fix로 간주하지 않음 |

`receivedAtS`를 넣기 위해 wall clock을 읽지 않는다. same-tick native local 측정은 실제 호출 문맥의 fixed time으로 기록할 수 있지만, offboard/ISAR/network에는 payload의 원 시각이 우선이다. 정보가 원 스키마에서 소실됐으면 “모름”을 보존한다.

## 3. 센서별 차원과 가정

| kind | 독립 관측 / model rows | assumed·derived·reported 구분 |
|---|---|---|
| AIR_RADAR | finite rangeM/azRad/elRad/radialMps, 정상4차원 | payload x/y/z는 polar 변환값이며 추가3관측 아님. receiver origin/velocity는 관측 모델의 알려진 자기 장비 상태 |
| SURFACE_RADAR | r/az 및 실제 제공된 radial, 정상2 또는3차원 | **el/z 미관측**. surfaceReferenceZM=8은 MODEL_PRIOR_NOT_ELEVATION. payload의 elevation 비슷한 필드가 있어도 surface waveform의 실제 채널로 간주하지 않음 |
| BridgeMaster(SURFACE_RADAR) | **r/az2차원** | 최종 native adapter가 Doppler를 제거함. ARPA 회귀 vx/vy는 derived이며 새 Doppler hit가 아님 |
| CIWS_LOCAL_RF | **r/az/el3차원** | rx/ry/rz는 이 관측의 상대 Cartesian 변환. filter rvx/rvy/rvz·CPA·TTI는 파생, 초기0속도/분산은 prior. 실제 C55 association은 거리 gate이며 가짜 NIS를 만들지 않음 |
| VISUAL_CARTESIAN | updater가 받는 xyz3차원·실제 Cartesian covariance | 원본 optical r/az/el 합성의 변환 결과. **radialMps=0은 OPTICAL_PLACEHOLDER_NOT_DOPPLER**, 관측 mask에 추가하지 않음 |
| HELO_RADAR | `measuredRangeM`/`measuredAzRad`2차원 | `positionM.x/y`는 기체 nav+slant 변환, `positionM.z`의 surfaceReference는 prior. z를 관측하거나 `positionM` m값을 world 단위로 두 번 변환하지 않음 |
| ESM_BEARING | bearing1차원+sigma | band/family/emitterClass/strength/quality는 방사체 증거. injected range/xyz를 무시하고 거리 없는 방위 접촉을 유지 |
| IFF_REPLY | 받은 r/az 및 AIR 응답의 el. 인증 bit는 evidence | 인증 bit는 별도 기하 차원이 아님. normalized record가 FRIEND/HOSTILE/authority를 새로 쓰지 않음. 기존 실제 수신 처리와 expiry는 별개 |
| ISAR_EVIDENCE | 길이·높이분포·마스트·분해능·quality 등 features. kinematic hit 차원0 | position/P는 판독을 트랙에 붙이는 gate 자료. class 후보는 reported classifier result. **위치 EKF/hit/age/identity/authority 갱신0**을 기존 경로대로 유지 |
| OFFBOARD_PLOT | received position/P는 reported Cartesian3D rows, upstream physical 차원은 null/unknown | H1/H2의 APS라면 원 센서는 range/az이고 z가 prior지만 **수신 스키마만으로 항상 단정하지 않음**. 미측정 속도를 보충하지 않음 |
| NETWORK_TRACK | sender filter state6D/P는 reported rows6, physical observation dimension null | x/y/z/vx/vy/vz 전부 송신자 추정. 6개의 독립 원시 센서 관측이나 새 local hit가 아님. measuredAtS와 stateAtS를 구분 |
| NETWORK_SELF | 자기 항법 보고이며 목표 physical measurement 아님 | 현재 native producer의 x/y/vx/vy는 sender nav, **z=8/vz=0은 가정**. received state 배열을 그대로 6D target observation으로 표시하지 않음 |

결측 payload를 넘겨도 해당 kind의 정상 차원을 강제로 채우지 않는다. 예를 들어 AIR에서 range만 finite면 rows1이며 absent az/el/rdot는 unknown이다. 실제 0 Doppler가 제공된 surface plot은 유효한 측정이고, visual의 정해진 placeholder0은 아니다. 이름이 아니라 producer 계약을 구분해야 한다.

## 4. provenance와 불확실성

- sourceId/sender/file 번호는 **관측·보고 체계 내부의 식별자**다. world targetId/rfId/objectId/hidden faction/owner로 바꾸지 않는다.
- trace의 `measurementId=M#`는 진단 WeakMap의 **payload-object 상관**이다. object가 clone되면 다른 M#일 수 있으며 같은 M# 재사용도 독립 관측·실제 target identity의 증명이 아니다.
- replay/independence 정보가 없다면 `independentObservation:null`. 새 sequence와 새로운 fix 시각, 같은 fix의 다른 source 전달은 서로 다르다. TRACK-A는 이를 보고할 뿐 실제 hit dedup 정책을 바꾸지 않는다.
- OFFBOARD의 age²×speed prior covariance 증가, age 기반 quality는 model-derived다. 송신자 P와 수신자가 확대한 P를 원 측정 noise 하나로 혼동하지 않는다.
- NETWORK의 P는 sender filter uncertainty이며 기존0.5 CI로 receiver picture에 반영된다. 원시 independent covariance 합산이나 새 KF update로 바꾸지 않는다.
- sigma만 있는 경로에서 완전한 관측 covariance/correlation이 알려졌다고 표기하지 않는다. ESM range variance도 없다. ISAR feature noise와 위치 gate P는 용도가 다르다.
- 3×3/6×6 covariance와6D state는 기대 길이가 정확하고 모든 성분이 finite일 때만 보존한다. 잘못된 길이를 잘라 정상 행렬처럼 보이게 하거나 missing off-diagonal을 임의0으로 채우지 않는다.

## 5. 기존 3D 증거와 수면 prior — **관찰만, 정책 변경 없음**

기준 제품의 `trackNoteAirObservationFC`는 성공한 local AIR radar update의 fixed-step을 `_radar3dAirStepFC`에 남긴다. `trackHasAirObservationFC`는 마지막 시각에서 **16.0초 이내**일 때만 true다. 2D 수상 기여는 이 시각을 갱신하지 않는다. true인 동안 기존 `trackApplySurfaceDomainConstraint`가8m prior 강제를 건너뛴다. 초기2D-only 표식은 수용된3D 이후 해제되고 surface motion prior flag도 해제된다.

만료는 해당 필드 삭제가 아니라 predicate false다. 그 뒤 기존 surface partition/prior 조건이 다시 적용될 수 있다. 이는 friendly-contact의 미승인 정책이며 이번 A에서 TTL을 늘리거나, 항상3D로 고정하거나, 필터 평균/분산을 보정하지 않는다. trace에는 **이미 저장된 시각·flag·실제 prior 적용 결과**만 기록한다. 진단 조회가 eligibility/quality helper를 다시 호출해서 counters/state를 바꾸면 실패다.

## 6. 연관 trace

기존 native 실행 중에 이미 계산된 후보·gate·결과를 bounded ring에 기록한다. native selector와 EKF를 재실행하지 않는다.

권장 레코드 내용은 source/observer, fixed tick/time, local diagnostic measurement ID, 전술 track/local file ID, 적용된 측정 모델과 차원, candidate NIS 또는 실제 거리와 gate, accept/reject/skip/new-file 이유, 최종 source, 전후 **whitelist 상태**다. 개별 경로는 다음을 분리해야 한다.

- eligibility 거부와 실제 NIS 거부.
- 위치-only 할당과 최종 Doppler 포함 update.
- 이미 다른 plot에 사용된 후보와 데이터 없음/마스킹/미시도.
- 수용된 update와 SPY-preferred source에서 실제 correction을 생략한 보조 기여.
- 새 파일·정상 coast 후 재획득·기존 파일 반복 갱신·drop.
- C55의 known-own partition·seen·거리 gate·capacity와 보호/동의 결과. physical source key를 공개 provenance로 사용하지 않음.
- 보고 schema/time/replay/link 거부와 canonical 연관 거부. ISAR evidence 첨부는 position update 수용과 다름.

`nis:null`은 계산하지 않았거나 해당 경로에 NIS가 없음을 뜻한다. gate가 존재하지 않는 경로에 임의 기준값을 붙이지 않는다. 후속 gate를 계산하지 않고 끝난 native 실행에는 **실제로 평가하지 않음**을 표시한다. 가능한 모든 후보가 trace에 보인다는 주장은 실제 hook coverage와 별도 검증 없이는 하지 않는다.

### 상태와 query 격리

- 기본 trace OFF. 수집을 켜도 기록만 추가하며 normalizer·record가 native decision/consumer의 반환값을 바꾸지 않는다.
- 현재 module의 기본 capacity1024, configure 범위16~4096. overflow는 오래된 진단만 덮어쓰고 dropped count를 남긴다. 이 값은 presentation/diagnostic memory bound이며 센서 하드웨어나 KF 튜닝 계수가 아니다.
- `configure`/`clear`는 진단 상태만 바꾼다. `snapshot`은 ring/stat의 deep copy를 반환한다. snapshot 연속 조회로 ring/head/serial·game RNG/tick/track·observer scheduler 상태가 변하면 실패다.
- before/after는 `trackAStateA`와 동등한 whitelist snapshot만 허용한다. native raw track, C55 proxy/WeakMap, target object를 그대로 JSON clone해서 내보내는 것은 안전한 비누수 처리가 아니다.
- record serial과 WeakMap은 게임 RNG·ID allocator·tick을 재사용하지 않는다. 오류는 diagnostic error count로 격리하되 이를 native update 성공으로 바꾸거나 실패를 숨기는 데 사용하지 않는다.

## 7. 구현과 검증의 구분

문서 작성 시 `measurement-contract.js`에 normalize와 bounded trace API가 있다. 다만 **그 API 존재, branch 정상 동작, 실제 production hook 연결, 원본과 native state 동등성은 서로 별도 증거**다. HELO의 `positionM`/surface prior, NETWORK_SELF의 고정 z/vz, 제공되지 않은 timestamp/noise, before/after whitelist, C55 두 문맥 및 각 ingress hook은 최종 module/fixture/native 검증에서 확인해야 한다. 이 목록을 문서만으로 완료 처리하지 않는다.

검증 등급:

| 검사 | 증거의 의미 |
|---|---|
| Node VM unit | 실제 내장할 adapter의 mask/결측/whitelist/detached/trace memory 규약. **fixture-only**, 자연 RF/교전 아님 |
| native normalize/hook | 실제 게임 함수에서 발생한 원 payload/계산 결과와 trace를 비교. 실제 실행하지 않은 후보를 evaluated로 만들지 않음 |
| baseline↔TRACK-A / trace OFF↔ON | 트랙 평균/P·분류·identity/authority·hit/age·lifecycle·물리·탄약·global/private RNG·scheduler 동등성. 진단 필드만 예외 |
| 세 자연 재현 | 헬기 hover/route·Harpoon 신규/최대/최종 파일, 실제 재획득 NIS·age·IFF가 baseline과 같음. 파일 수 하나만으로 false merge를 숨기지 않음 |
| CIWS30/419025 | 실제 fixed-tick 방어·source/file·RAM/Phalanx·동일 시점 RNG/피해 타임라인. 상속된419025 FAIL을 승인하지 않음 |
| 도메인/UI/무장/시간/성능 | 최초404/2/14 집계를 유지하고 fresh 결과를 별도 기록. UI213·WebGL8/29와 중복 합산하지 않음. owner당1회/tick,1·8·16·64배속 및 평균/p95 CPU·할당/candidate 비용 확인 |

TRACK-A의 동작 동등성 PASS는 `friendly-contact-a`의 release 승인과 다르다. seed419025, paired observer 미승인 차이, 구형 EMCON UI 및 TRACK_AUDIT에 기록한 legacy 정보 경계 debt가 남으면 그 상태대로 제출한다. 기대값/허용 오차/계수 수정, 기능 끄기, 자동 적성·OODA·새 전술 AI, main/기준 브랜치 수정·병합, PR/release/tag는 본 계약 범위가 아니다.
