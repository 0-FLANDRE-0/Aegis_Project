# Baseline Audit — 외함·헬기·외부 보고·네트워크

이 문서는 **읽기 전용 코드 감사**다. 시험을 실행했거나 TRACK-B/C/D를 구현했다는 뜻이 아니다. 기준은 friendly-contact-a `4ba64ba0cace9124497a710d00df1b174984ffdc`, 제품 `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html` SHA-256 `cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda`다. 아래 `JS:L`은 해당 HTML의 index 13 압축 JS를 해제한 `/dev/shm/track-a-baseline-source.js` 줄번호다. 원본 모듈과 실제 실행 제품의 대응·SHA는 `audit-network.json`에 기록한다.

## 소유권과 정보 경계

| 저장소/단계 | 소유자 | 허용 입력·측정 차원 | 갱신/소비 상태 | 연관·수명과 근거 코드 |
|---|---|---|---|---|
| 외함 canonical observer | 각 `ShipRuntime.combatSystem.observerC`; 자함만 기존 `tracks`와 alias, 외함은 그 함 `trackManager.tracks` | 자체 RF 익명 plot, 해당 receiver 원점·속도, 측정 오차 | EKF x/P, sensorHits/confirmed, source/age, domain/classification, withheld authority | `prepareObserverC` JS:4629, `observerAcceptPlotsC` JS:4671, `stepObserversC` JS:4754. owner별 SPY/SPQ/NAV RNG와 tick guard. 다른 함 private TrackStore를 공유하지 않음 |
| 외함 SPY/SPQ/NAV RF→plot | `observerExtractC`/`observerAuxStepC`, owner receiver | AIR는 range/az/el/radial; 수상 plot은 range/az와 존재할 때 Doppler. NAV는 radial 값까지 명시적으로 제거 | 익명 `plots`, RF history/stat; 소스/원점은 실제 송수신기의 것 | JS:4698–4753. `shipboardRadarEchoFieldWip13B13` 결과에서 background/마스킹을 거르고, 관측 domain evidence에 따라 air/surface 중 한 경로로 전달 |
| APS-153 단일 주사 측정 | 모함의 `aviation.heloSensorsE.get(h.id).radar`; 기체별 private RNG/cells/contacts | **관측:** `measuredRangeM`, `measuredAzRad`; **가정:** `z=APS_F.surfaceReferenceM`; **유도:** 자체 항법+slant→horizontal로 계산한 XY 및 3×3 위치 공분산 | `cells`, bit mask, 마지막 측정; 공중 탐지 경로 아님 | `apsMeasurementF` JS:4299, `apsMergeMeasurementsF` JS:4301, `apsContactStepF` JS:4308, `apsFinalizeTurnF` JS:4321 |
| APS 접촉 확인 | 같은 기체의 contact table; 함 트랙과 별개 | 기하/시간 게이트, 측정 공분산, 주사 ordinal | 모드별 binary M-of-N 한 번, 최대 candidate/contact 제한; 같은 lastAtS의 재출력 없음 | JS:4308–4321. 최근 주사 bit mask, `turn-c.lastTurn>=n`이면 만료. 현재 `apsContactStepF`는 row를 순서대로 가장 작은 metric에 연관하며, 한 turn 내 `usedContacts`는 없음. 같은 주사 근접 plot의 재사용은 TRACK-B 검증 대상이지 A 수정 대상 아님 |
| Hawklink 송신 | 기체→그 모함 `H1/H2` 포트 | 측정 시각, reported Cartesian position/P, domain evidence만; 표적 ID/시커/INS 없음 | 모함 포트 queue, source sequence, 기체 전송 counters | JS:4561–4571. 링크 끊김 plot 버림/재전송 없음. 토큰·회전 cursor로 H1/H2 공정성/64 queue 보호. 원래 polar 성분은 현 스키마에서 제거되므로 수신 XYZ를 3D 독립 관측으로 부르면 안 됨 |
| Hawklink 연결/자함 반사 blanking | 송수신 플랫폼 자체 nav/시설 상태 | 자체 항법 위치·안테나 높이·장비상태, RF LOS/거리; 자기 hull footprint | `connected/reason`, 포트 configuration | JS:4527–4560. 레이더 EMCON은 통신을 차단하지 않음. 자신의 footprint를 불확실성으로 확장해 blanking하며, 그 안의 미분해 타 접촉도 구별하지 못함. 표적 truth owner로 골라 버리지 않음 |
| 외부 PLOT 수신 | 각 함 observer의 `offboard.sources/queue` | strict PLOT_C_1 schema, sourceId/sequence/measuredAtS, positionM, SPD covarianceM2, domainEvidence | availableAtS queue, lastSequence/lastReportS, remote provenance | `ingestOffboardReportC` JS:4794. 링크·시간·replay·SPD 검사, externalMaxAgeS=15, queue≤64. sourceId는 송신 포트 식별자이며 표적 ID가 아님 |
| 외부 PLOT→canonical track | 수신 함 observer, 자함은 mature native update 경로, 외함은 native Cartesian EKF | covariance 포함 위치만; 속도 0은 새 관측 속도가 아니라 initializer/prior. `quality=exp(-age/8)*.7`은 수신자가 유도한 값이며 실제 수신 품질 관측이 아님 | `observationReportsC.{localAtS,remote[sourceId]}`, x/P, hit/confirmation/age/ttl | `offboardPlotC` JS:4809, `acceptOffboardC` JS:4816, `drainOffboardC` JS:4840. 관측 age²×기존 speed prior로 P 확대, Cartesian NIS≤25의 최저 후보 선택. **배치 one-to-one 없음**. 같은 source의 같은/오래된 측정시각은 새 hit 아님. 여러 source의 같은 원정보 중복은 현재 알 수 없음 |
| ISAR RF/판독 | 기체별 `isarF2`와 private RNG, 승무원 보유 결과 buffer | RF 물리 경계에서 측정한 길이/높이분포/마스트/각도 signature, SNR. classId는 측정 특징을 library와 비교한 후보 결과 | integration/sample mean/quality/result; search window는 pause | JS:4125–4150 물리 경계, JS:4160 선택은 기체 자체 contact와 기하 게이트만, JS:4174 적분. 실제 profile/entity ID는 RF 형상 합성에만 쓰이며 분류기는 측정 특징만 받음 |
| ISAR 보고/함 연관 | `observerC(r).isarF2.{queue,history,lastSequence}` | ISAR_C_1: reported 위치/P+판독 결과+원 측정시각 | **isarEvidence만 첨부**; hit/age/EKF/identity/authority 증가 없음 | JS:4196–4225. strict key/SPD/result validation, source별 replay 방지. 링크 복구 후 원래 시각으로 전송. history는 resultMaxAgeS 동안 기하 재연관 가능; 이전 track ID·operator identity 승계 없음 |
| ESM 실시간 물리→측정 | 함별 electronic receiver, private RNG | bearing/bearingSigma/strength/quality/band/type/emitterClass/time만; range 없음 | `e.contacts`, `rangeKm:null`, UNKNOWN, own-coast age | JS:2450 physical emitters, JS:2471 noisy receiver, JS:2485 anonymous validation+greedy association. band/emitter family와 angular 3σ gate, 배치 used set 유지. actual source owner는 물리 self-coupling 억제 경계에서만 사용 |
| Link16/G transport | 각 함 `combatSystem.networkG`, `files`는 canonical track과 별개 | SELF: 송신 함 자체 nav x/y/vx/vy, **z=8·vz=0은 고정 가정**. TRACK: **송신 함 EKF/filter estimate 6D state/P**, 측정시각과 state시각, classification/identity/assessment/bid | peer/sequence/queue, 독립 cooperative picture; local FCS를 쓰지 않음 | JS:4906–4918, JS:4989–5012, JS:5068. authenticated allied membership은 통신 참가자 확인이지 목표의 faction을 읽는 것이 아님. packet strict schema·replay·age 검사 |
| Link16 수신 파일 연관 | 수신자 `n.files`, source key=`[senderId,fileId]` | 시간 정렬된 estimate/P, domain, source provenance | file sources/hits, localTrackId/fused presentation | JS:5018. NIS≤36, 거리 cap 2500m/속도 cap180m/s sanity, 다른 후보와 NIS차>4일 때만 선택. 한 sender의 서로 다른 file을 같은 file에 무조건 합치지 않음 |
| Link16 공분산 융합 | receiver cooperative file | 상관관계 미지의 estimate/P | fixed **0.5 Covariance Intersection**, canonical EKF 불변 | `networkNisG` JS:4951, `networkIntersectionG` JS:4958, `networkFileEstimateG` JS:5013. 같은 estimate 반복으로 독립 KF처럼 P를 반감하지 않음 |
| Link16 local 대응·소비 | receiver `n.files` ↔ 자신의 confirmed/fresh native tracks | native local estimate와 remote estimate/P만 | localTrackId와 별도 fused display snapshot; 공유 전용 report는 FCS 동의 없음 | `networkReconcileG` JS:5033. 최저 NIS 순 greedy one-to-one + ambiguity gap4. fresh2s/coast12s; `networkPresentationTrackG` JS:5054는 복사본, `networkPictureG` JS:5060는 fcsSource LOCAL_ONLY/automaticRelease false |
| IFF·보호·무장동의 | 해당 함이 수신한 응답/네트워크 증거와 기존 operator decision | IFF noisy geometry+authenticated bit; 새 적성 추정 아님 | FRIEND·NEUTRAL 보호, authority WITHHELD 또는 native 게이트 | canonical `networkProtectionG` JS:5048, `networkVlsGateG` JS:5159. JS:64675/64681의 같은 이름 함수는 `mapBNativePreview` 내부의 별도 lexical 복사본이며 전역 함수를 덮어쓰지 않는다. network 보호는 기존 발사를 더 제한하며 remote-only를 local fire control로 승격하지 않음 |

## 틱 순서

실제 fixed-tick 순서는 JS:55020–55044, JS:55226–55249, JS:55372–55380에서 확인했다.

1. 해상/피해 진행 후 `updateESM(dt)`가 `stepElectronicReceiversF`를 한 번 호출한다. 함별 `EW_DOUBLE_TICK_F` guard가 있다.
2. 항해/기동·공격 AI 및 함 이동 뒤 자함 radar/SPQ/NAV가 실행된다.
3. `heloHawklinkBeforeObserversE`가 링크 상태/끊긴 queue를 먼저 정리한다.
4. `stepObserversC`: 자함 offboard drain 및 tick 기록, 외함은 predict/coast/drop → scheduler/aux RF → offboard drain. 외함 `OBSERVER_DOUBLE_TICK` guard.
5. `stepElectronicOwnersF`의 EW context 및 수상함 IFF → `networkFixedStepG` → H4 → 헬기 IFF → native weapons.
6. 기체 운동과 APS-153/ISAR는 틱 후반 실행되고 보고를 enqueue한다. 따라서 그 틱의 모함 observer drain을 이미 지나간 보고는 다음 fixed tick 이후/지연 완료 후 수신된다.
7. `simStepCounter++` 후 기존 engagement control/automation. 네트워크도 `NETWORK_DOUBLE_TICK` guard가 있다.

새 진단은 이 순서를 바꾸거나 관측·정규화 때문에 두 번째 EKF predict/association/RNG 호출을 하면 안 된다. trace는 이미 계산된 NIS/게이트 반환값을 복사해야 한다. `observerC`, `prepareNetworkG` 같은 lazy initializer도 “독립 read-only 조회” 경로에서는 호출하지 않고 기존 저장소의 detached snapshot만 읽어야 한다.

## 원본 모듈과 실행 제품의 차이

`docs/multiship/C/observer.js`는 구축 당시 원본이며 현재 제품의 완전한 재생성 소스가 아니다. live에는 다음 누적 변경이 있다.

- `observerClassifyC`: 헬기 IFF 보호, classificationConfidence, 3D AIR 근거가 살아 있는 동안 2D 관측에 의한 domain vote 억제.
- `observerAcceptPlotsC`: friendly-contact cross-domain eligibility 및 3D accepted/2D-only metadata, network/local provenance stamps.
- `observerExtractC`: AIR_ORIGIN_A receiver origin/velocity 메타데이터는 현 원본 모듈과 제품 **양쪽에 이미 존재하며 함수 byte도 같다**. 이를 누락한 과거 기준으로 되돌리지 않는다.
- reset은 EW/network도 연결되며 facade에는 ISAR 증거가 있다.

`offboard.js` live에는 ISAR schema 분기/별도 drain, 식별 근거, helicopterImplemented=true, network/ISAR label 등의 누적 변경이 있다. `network.js`의 핵심 NIS/CI/수신·연관 함수는 현 제품과 byte가 같으며 별도 `cooperation.js`에 무장동의 함수가 있다. MAP의 private preview 내부에도 같은 이름 복사본이 있으므로 함수명 문자열만으로 전역을 잘못 선택하면 안 된다. TRACK-A는 현재 제품의 lexical scope를 기준으로 최소 adapter/trace만 넣어야 한다.

## 기존 시험 대응 및 판정 범위

- 외함 독립성/RF/시간: `docs/multiship/C/verify_observers.py`, `verify_clock.py`, `verify_propagation.py`, `verify_physical_native.py`.
- Link16 strict schema·replay·CI·remote-only 권한·저장: `docs/multiship/G/verify_network.py`; 실제 공유/교전은 `verify_cooperation.py`, `verify_guidance.py`, `verify_harpoon.py`, `verify_clock.py`.
- 헬기 APS/ISAR native: `docs/helicopter/G/verify_native.py`, `docs/helicopter/L/verify_native.py`, `verify_classes.py`, `verify_clock.py`, `verify_ui.py`.
- Hawklink 과거 `docs/helicopter/E/verify_stage_c.py`에는 **현재 F1에서 이미 폐기된 LOCAL_SURFACE_OBSERVATION_REQUIRED 기대값**이 있다. 전체 파일을 그대로 실행해 현재 정책 검증으로 취급하면 안 된다. 현재 F1의 검증은 `docs/helicopter/H/verify_native.py` 및 friendly/A에 이미 보존한 결과를 기준으로 구분한다.
- ESM/IFF: `docs/helicopter/E/verify_stage_a.py`, 현재 `docs/helicopter/I/verify_iff.py`, 기존 다함정 EW 시험과 friendly/A의 AUTO IFF 증거. 오래된 UI DOM 의존 검사 실패를 source 검사 PASS로 바꾸지 않는다.

이 감사만으로 위 시험의 PASS를 선언하지 않는다. parent 실행 기록과 Baseline Audit 최초 원시 결과를 별도 결합해야 한다.

## 남겨야 할 위험 — 이번 단계에서 수정 금지

1. APS 위치/P payload에서 관측 polar와 assumed 해수면 높이의 출처가 소실된다. TRACK-A의 호환 표기에서 차원을 명확히 하되 현재 filter 입력은 변경하지 않는다.
2. Hawklink는 source/sequence/time provenance가 있으나 같은 정보가 다른 source로 재전송되는 상관 계보는 없다. 단일 report 처리에는 배치 one-to-one가 없어 서로 다른 근접 표적의 동일 파일 업데이트를 별도 측정해야 한다.
3. APS contact greedy metric에는 한 turn의 여러 row에 대한 `used`가 없다. resolution merge와 scan bit mask 덕분에 무조건 hit 중복이 되지는 않지만, crossing/분해 후 재연관 fixture가 필요하다.
4. 네트워크 CI는 상관 미지의 P 과신을 줄이지만 원정보 순환을 증명하지는 않는다. local fix 후의 state가 이전 원격 정보를 포함할 수 있으며 sender/file만으로 그 계보가 완전히 보존되지는 않는다. B~D에서 shadow 진단으로 확인할 것.
5. 수상함 IFF(`stepFriendlyIffF` JS:2517)는 `_operatorIdentity='FRIEND'`까지 쓰며 별도 expiry가 없다. 헬기 `AIR_IFF_E`는 expiresAtS와 source를 사용한다. 이 차이를 IFF 보호를 임의 해제하는 수정으로 “정리”하지 말고 TRACK-C 설계 검토 대상으로 둔다.
6. 구형 `_updateEsmBearingContact` JS:28693는 truth-index를 쓰지만 현재 live 물리 pipeline의 경로가 아니다. 확인된 호출은 명시적 DIAG API JS:54721/54726뿐이다. 새 trace/consumer가 이 legacy index를 이용해 live 연관을 보정하면 정보 누수다.
7. 네트워크 참가자 자신의 owner/faction/nav를 인증·통신·SELF report에서 읽는 것과 **목표**의 hidden owner/faction/좌표를 읽는 것은 구분해야 한다. 새 adapter는 현재 허용된 측정 payload를 whitelist copy하고 전체 r/h/ref 객체를 진단 포트에 노출하지 않는다.
