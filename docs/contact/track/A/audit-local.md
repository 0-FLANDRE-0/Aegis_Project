# Baseline Audit — 자함 관측·트랙·소비자

이 문서는 **정적 감사**다. 새로운 시험의 PASS를 주장하지 않으며 코드·계수·기대값을 변경하지 않는다. TRACK-A에서 아래 동작을 유지하고 관측 설명과 진단만 추가해야 한다.

## 기준과 줄번호

- 기준 HEAD: `friendly-contact-a@4ba64ba0cace9124497a710d00df1b174984ffdc`.
- 실제 실행 입력: `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`.
- HTML SHA-256: `cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda`.
- 아래 `JS:Lnnn`은 **이 HTML의 압축 slot 13을 해제한 JS** 줄번호다. HTML의 줄번호가 아니다.
- 해제 JS: 40,611,957 bytes, SHA-256 `79c73e36809bfcf38141da6698ab43bf4c19048595652db736c970842a85afe3`.
- 본 감사에서 임시 읽기 파일 `/dev/shm/friendly-contact-baseline-audit.js`를 사용했다. 제품은 수정하지 않았다.

같은 이름이 NPC weapon context, 자함 main scope, UI preview 내부 scope에 중복 선언된다. 예를 들어 `trackIsDisplayable`은 JS:L2555/L7006/L27211, `updateTrackOperationalStateA3`는 JS:L13243/L26197/L64699 등에 존재한다. **자함 canonical A3는 L26197**이다. L64699는 `mapBNativePreview`(L64634) 내부의 detached preview 함수이며 실제 canonical 트랙을 갱신하는 main-scope 선언이 아니다. 단순 첫 번째/마지막 텍스트 검색 결과를 실동작으로 간주하지 않고 Acorn lexical scope로 확인했다. `audit-local.json`의 symbol 비교는 이미 이 main-scope AST를 사용하며 아래 정정과 모순되지 않는다.

## A. 생산·연관·갱신 표

| 경로 / 소유자 / 실제 함수 위치 | 입력과 측정 차원 | 연관과 일대일 처리 | 쓰는 필드 / 읽는 필드 / 시점 | 기존 검증·중복 여부 |
|---|---|---|---|---|
| 공통 ship RF 물리 경계, `shipboardRadarPhysicalSceneWip13B13` L30726, `shipboardRadarEchoFieldWip13B13` L30733 | 물리 반사체를 receiver 위치/속도·빔·환경으로 합성. 이 구간만 truth 좌표/반사체 형태를 사용한다. 출력 echo는 잡음이 적용된 거리·방위·고각·방사속도·불확실성·특징량. | 물리 해상도 셀/CFAR 경로. 전술 트랙 번호를 알지 않는다. | receiver별 전파/잡음 계산, radar별 private RNG. 동일 tick·band의 물리 장면 열거 cache는 공유하지만 트랙 store·관측은 공유하지 않는다. | 기존 APS/native RF 및 자연 출항 재현. 다른 observer가 같은 장면을 쓰는 것과 같은 측정을 재사용하는 것은 다르다. |
| RF echo → plot, `shipboardRadarEchoToAirPlotWip13B13` L30777 / `...ToSurfacePlot...` L30778 | AIR: `rangeM,azRad,elRad,radialMps` 4차원. Surface: `rangeM,azRad,radialMps` 3차원. 후자의 `z=referenceZM`은 prior, `losUz=0`은 모델 가정이다. x/y/z는 polar의 변환값이며 독립 추가 hit가 아니다. | `shipboardRadarDomainEvidenceWip13B13` L30766와 `...SurfaceDiscreteEvidence...` L30774가 측정 특징량으로 분기. | 출력은 측정·origin·sigma·quality·domainEvidence allowlist. 표적 ID/owner/faction으로 연관하지 않는다. | unified RF fixture 및 기존 출처 poison 검증. |
| 자함 SPY, `spyCollectUnifiedEchoPlotsWip13B13` L26858, `executeSpyTask` L26965 | 실제 장착 receiver 위치/속도 + 잡음 echo. 물리 echo마다 AIR 또는 SURFACE로 한 번 추출. Surface와 AIR 두 개의 독립 관측으로 중복 생성하지 않는다. | AIR remainder: `spyGlobalAssignmentsV36` L26895의 Hungarian 최소 총 NIS. Focused scheduled file은 `spyBestPlotForTrackV31` L26886가 먼저 제안. Surface는 별도 stage. `usedTracks`를 두 extractor 사이에 공유해 같은 **physical dwell**에서는 파일당 한 번만 수용. 다른 dwell은 같은 scheduler cycle에 다시 관측 가능. | `_kfX/_kfP`, hit/confirmed/last source/age를 canonical updater가 갱신. task focus는 추정 track 위치를 사용한다. 실제 위치로 빔을 조준하지 않는다. | 자연 `HELO_HOVER_60S`, `HELO_ROUTE_120S`, `HARPOON_ROUTE_75S`; 기존 formation/native RF 검사. |
| SPY surface 배치, `spyExecuteSurfacePlotsWip13B9` L26951 | 거리/방위, 유효한 경우 방사속도. | Position-only NIS로 후보를 배정한 뒤 canonical 2D updater가 실제 제공된 도플러까지 재검사. `surfaceAssignmentsPreferEstablishedWip13B14` L27464: established surface 먼저, 남은 AIR/UNKNOWN cross stage. Cross gate는 기존 25 상한. | source별 freshness, expected revisit, `_spySurface*`, extent를 갱신한다. | 기존 surface/class/native 테스트. 위치 stage와 최종 Doppler gate의 결과는 별도로 trace해야 한다. |
| 자함 SPQ AIR, `spq9bCollectUnifiedEchoPlotsWip13B13` L34289 / `spq9bAcceptAnonymousPlotsV34` L34184 | AIR 4D. SPQ라는 내부 명칭은 함별 실제 장비 프로파일과 구분한다(CG에는 SPQ-9 모델 경로가 있음). | `spq9bBestTrackForPlotV34` L34175는 plot 순서의 greedy 최소 NIS + usedTracks. **Hungarian은 아니다.** Cross-domain gate와 4D NIS 보존. | fresh SPY source가 <0.65s이면 기존 SPY state를 다시 EKF 갱신하지 않고 SPQ freshness·class evidence만 갱신한다. 그렇지 않으면 canonical updater. | 이 경로의 수용 수를 독립 실제 hit 수로 그대로 세면 안 된다. SPY-preferred consume은 trace에서 suppressed update로 구분. |
| 자함 SPQ surface, `spq9bAcceptSurfacePlotsWip13B1` L34256 | r/az/radial 3D, elevation 미측정. `surfaceReferenceZM=8`은 가정이다. | surface Hungarian stage에서 position-only NIS, 실제 update는 r/az/radial. NIS 64 및 cross 상한은 기존값. | `_spq9bSurfaceFreshS`, panel/lobe, extent, source contributor, canonical x/P. | 기존 SPQ vertical fixture·own/friendly 재현. |
| BridgeMaster E / CG auxiliary nav, `bridgeMasterECollectUnifiedEchoPlotsWip13B13` L34538, `bridgeMasterEAnonymousPlotContractV35` L34425, `updateBridgeMasterERadar` L34549 | **최종 adapter는 range+bearing만** 제공한다. RF echo의 radialMps는 allowlist에서 제거한다. z=8을 추가하지만 실제 높이 관측이 아니다. | `bridgeMasterEGlobalAssignmentsV35` L34450 → surface one-to-one Hungarian → native 2D NIS. 파일 capacity는 유지 파일 수 제한이며 RF 반사체 자체를 숨기는 제한이 아니다. | 2D state update + `_bridgeMasterE*` freshness, history, extent. CG mask/profile을 적용한다. | 기존 surface/native 및 재현에서 영향 받는 경로. |
| BridgeMaster ARPA, `bridgeMasterEUpdateArpaPlotHistory` L34473 | 여러 차례 **절대 측정 위치**를 회귀한 vx/vy, sigma. 직접 Doppler가 아니라 derived regression이다. | 공통 파일의 동일 history에 추가한다. 독립 센서가 새 velocity를 측정한 것이 아니다. | 3개/4.5s부터 회귀, mature sigma<=4.5 조건에서 기존 gain으로 x[3:4]·P를 갱신. A에서 이 수치나 쓰기 동작을 바꾸면 안 된다. | ARPA/native 결과와 기존 회귀. Source별 dimension과 derived velocity를 구분해야 한다. |
| Visual, `_opticalMeasurementFromTruth` L27345 → `acceptVisualAnonymousPlotV33` L27380 | 잡음 r/az/el에서 xyz와 3×3 covariance를 계산. payload의 `radialMps:0`은 placeholder로 **Doppler 측정이 아니다**. 실제 updater는 Cartesian xyz 3D. | `visualTrackAssociationV33` L27369의 greedy Cartesian NIS. `updateVisualDetection` L29249의 개체별 호출 사이에 공통 usedTracks가 없어 같은 tick의 두 optical plot이 같은 파일을 갱신할 수 있다. | canonical update, local source/freshness/hit, isASM legacy hint. | native visual/source poison 등. TRACK-B에서 볼 다표적/중복 hit 위험이지 A에서 고칠 항목이 아니다. |
| AIR IFF, `heloMeasureIffRepliesE` L4383 / `heloIffStepE` L4405 | noisy range/bearing/elevation + authenticatedFriendly bit와 sigma/time. 물리 경계에서 응답 가능 송신자를 선택하지만 수신 payload에는 target ID·truth pose가 없다. | receiver별 canonical files에 range/az/el 기하 gate·best score, reply별 한 파일/한 tick 내 used. | `iffF`, identity FRIEND, authority WITHHELD만 기록. 위치 EKF나 sensorHits를 직접 갱신하지 않는다. L4397이 expiry 시 evidence를 제거. | AUTO+IFF ON 탄약 0, IFF OFF UNKNOWN, expiry/reassociation 관련 검증. |
| Surface IFF, `friendlyIffPlotsF` L2507 / `stepFriendlyIffF` L2517 | noisy range/bearing + 인증 bit. | surface track geometry gate, used로 일대일. | `iffF={authenticatedFriendly:true,measuredAtS}`와 `_operatorIdentity='FRIEND'`를 기록한다. **현재 explicit expiry가 없다.** | AIR IFF와 동일 TTL이라고 표기하면 오기다. 지속 식별 근거 정책은 TRACK-C 위험으로 남긴다. |
| ESM, `electronicReceiverPlotsF` L2471 / `electronicAcceptPlotsF` L2485, `stepElectronicReceiversF` L2497 | bearing 1D + bearing sigma/band/type/emitterClass/quality/time. rangeKm=null. | band/emitter family + 각도 gate의 greedy used set. 별도 owner ew.contacts, canonical 위치 TrackStore와 별개. | age/hits/bearing 갱신; `truthRef` 삭제. 현재 `updateESM` L28711은 이 경로를 호출한다. 오래된 `_updateEsmBearingContact`를 새 ESM 원천으로 착각하면 안 된다. | ESM-only 거리 없음 및 EW regression. 각 receiver lastTick 중복 실행 guard가 있다. |

Hawklink/ISAR/Link 16/NPC/C55 세부 감사는 독립 감사 표와 합쳐야 한다. 이 표가 그 store들을 하나의 canonical store로 합칠 권한을 뜻하지 않는다.

## B. 공통 상태·수명·분류·권한

| 항목 | 실제 함수 / 읽기·쓰기 | 현재 계약과 TRACK-A 주의점 |
|---|---|---|
| EKF state | `trackEkfInit` L25826, `trackEkfPredict` L25859, `trackEkfUpdateRadar` L25901 | x=[xM,yM,zM,vxMps,vyMps,vzMps], P=6×6. AIR correction uses r/az/el/rdot 4D. Native NIS를 통과한 뒤 Joseph covariance update. A에서 식·행렬·gain·노이즈 상수 변경 금지. |
| Surface correction | `trackEkfUpdateSurfaceRadar2D` L26028 | finite radialMps이면 3D, 없으면 r/az 2D. elevation 관측 행은 없다. initial surface-only z/vz covariance와 surrogate el=0은 기존 prior. 최종 `trackApplySurfaceDomainConstraint`를 통해 수면 prior가 적용될 수 있다. |
| 3D evidence / prior | `trackHasAirObservationFC` L27410, `trackNoteAirObservationFC` L27413, `trackApplySurfaceDomainConstraint` L26013 | **성공한 local AIR radar 4D update** 시각만 `_radar3dAirStepFC`에 기록. current step과의 간격이 TRACK_HARD_TTL=16.0s (L25573) 이내면 8m prior의 강제 적용을 막는다. 2D hit가 sensorAge를 0으로 만들어도 이 3D 시각을 새로 쓰지 않는다. 만료는 삭제된 evidence가 아니라 predicate false로 처리되며 기존 surface classification/prior eligibility가 다시 적용될 수 있다. 이 정책 자체는 FC의 미승인 후보이고 A는 그대로 보존한다. |
| Source association | `trackMayAccept*CrossDomain*` L27441/L27450 | 측정 차원·기존 상태로 후보 eligibility를 정한다. 최근 실제 3D가 있으면 surface 기여 허용, initial 2D-only는 finite el의 3D 관측을 비교 가능. 실제 NIS gate는 별도로 유지. 거부 counter를 증가시키므로 진단에서 재호출하면 무상태 조회가 아니다. |
| Canonical update | `updateSensorTrackMeasurement` L27491 | 성공하면 x/P, sensorHits/confirmed/source/sensorAge/ttl/lastStep, source contributor, derived quality와 operational state를 갱신한다. 실패한 신규 file은 삭제. OFFBOARD initial covariance를 두 번 fuse하지 않는 별도 branch도 존재. |
| Classification | `accumulateTrackDomainEvidenceWip13B13` L27246, `updateTrackClassification` L27255 | RF 높이/크기/도플러/quality와 운동 특징으로 AIR/ASM/SURFACE/UNKNOWN을 추정. 최근 3D AIR에 2D 기여가 올 때 FC 후보는 class vote를 생략한다. Classification은 직접 operator HOSTILE 지정이나 발사 동의가 아니다. |
| Quality | `trackRefreshDerivedQuality` L26117, `trackSyncLegacyFromEkf` L26127 | P와 sourceAge/revisit에서 trackQuality/fireControlQuality·sigma/ellipse를 계산해 **필드에 쓴다**. legacy z 표현에는 기존 음수/상한 clamp가 있다. 단순 diagnostics에 이 함수를 호출하면 read-only가 아니다. |
| Lifecycle | `updateRadar` L39619, `trackLifecycleState` L27143, SPY finalize L26916/L26943 | 기존 tr.age/ttl/sensorAge/lastUpdateSeen/memActive/reacquiring와 dwell misses를 유지. age/TTL/P drop; COAST→REACQUIRE/MEMORY; 수용 관측은 freshness를 회복한다. `trackLifecycleState`는 여러 저장 필드에서 파생된 우선순위 판정이며 단일 enum을 새로 저장하는 체계가 아니다. |
| Display / FCS | `trackIsDisplayable` L27211 / `trackIsFireControlQuality` L27220 | display는 BDA hide·track quality·P; FCS는 confirmed/freshness/memory/reacquire/source 및 sigma 한계. FCS 함수는 quality를 다시 계산하므로 무상태 진단 getter가 아니다. |
| Identity / authority | **canonical main-scope** `updateTrackOperationalStateA3` L26197, `trackEngagementGateA3` L26239 | operator/known own launch/IFF와 기존 hostile-intent·network protection을 소비하고 identity/threatStatus/engagementAuthority를 별도로 결정한다. MANUAL/SEMIAUTO/AUTO 및 FRIEND/NEUTRAL 보호는 유지. L64699/L64733의 이름이 같은 함수들은 detached MAP preview 내부이며 canonical 갱신 경로와 구분한다. trace 출력은 새 발사동의 입력이 아니다. |

## C. 실제 fixed-tick 순서와 소비자

`simulateFixedTick` L55019의 현재 순서:

1. maritime 환경, 자함/NPC 손상·침수, observer side-channel 설치.
2. `updateESM`(모든 receiver의 1회/tick guard), chaff, NAV, H2/H3, visual detections (L55037~55044).
3. 함선 이동·world 좌표 적분과 충돌 (L55214~55228).
4. surface contact·Harpoon physical step 후 `updateRadar`→SPY scheduler, datalink allocation, SPQ, BridgeMaster (L55229~55238).
5. `heloHawklinkBeforeObserversE`→`stepObserversC`→EW owner contexts→Link 16 network→H4, 그 뒤 AIR IFF (L55239~55240).
6. NPC weapon context, 자함 gun, soft-kill threat/EA, SPG reservation/servo/SARH allocation (L55241 이후).
7. 물리 target/weapon/ASM/RAM/CIWS와 cleanup, helicopter physical step와 heloradar (L55269 이후~L55375).
8. `simStepCounter++` 후 WIP118/119 control·automatic engagement (L55376~55378).

따라서 같은 global tick에서도 측정이 취해진 **처리 구간**이 다르다. metadata의 measuredAt/receivedAt은 실제 payload 시각과 호출 문맥을 구분해야 한다. trace를 위해 producer를 다시 호출하면 RF/RNG·schedule이 바뀐다. helicopter radar의 새 plot 전달은 그 다음 observer pass라는 기존 순서를 보존해야 한다.

| 소비자 | 실제 위치 / 입력 | 보존 조건 |
|---|---|---|
| H1 utility | `tacticalEvaluateH1` L5530 | 자기 observer tracks + local estimate, assessments, freshness, protection, 권한을 필터. passive/shared alert는 readiness 영향만, 원격 파일을 FCS로 승격하지 않는다. lastStep guard가 있다. |
| H2 기동 | `maneuverObservedH2` L5647 / `maneuverTrafficH2` L5656, `maneuverEvaluateH2` L5706 | local tracks·수신 항해 정보·자함 own nav/피해/사각. 다른 함의 private FCS를 입력으로 쓰는 새 경로를 추가하지 않는다. |
| H3 공격 | `attackObservationGateH3` L5769, `attackEvaluateH3` L5859 | 자기 confirmed local surface, 명시 HOSTILE/현행 team intent, freshness와 protection, 자체 weapon authority. diagnostics로 새 자동 적성·동의를 만들지 않는다. |
| H4 협동 | `teamSurfaceEstimateH4` L5932, `teamFixedStepH4` L6039 | local surface estimate와 기존 intent/network 정책. 새 score/OODA/intent를 구현하지 않는다. |
| WIP118/119 | `wip118ThreatRows` L49577, `wip119EvaluateRow` L49753, `updateWip119EngagementAutomation` 인접 | track state/quality/assessment와 기존 gate/자원·consent. 동작 불변 대상이다. |
| Gun | `gunB1AirReady` L35605, `gunB1AirReleaseGate` L35625 | 3D state/P·측정 나이·position/velocity sigma와 existing identity/hardware gate. UI가 숫자만 보여 주는 것과 fire permitted는 별개다. |
| MAP/CIC/FLEET | `trackDisplayLabel*` L27200 근처, `trackIsDisplayable` L27211, `observerFacadeC` L4765 | 추정/수신 정보로 표시한다. trace ring의 사후 truth 또는 raw world는 render/selection/발사 UI에 공급하지 않는다. 오래된 source 파일보다 실행 HTML의 마지막 override를 우선한다. |

## D. 정보 비누수 감사 — 현재 baseline에 남아 있는 경로

아래는 **새 TRACK-A 코드가 만든 누수**가 아니다. 기존 코드 전체가 비누수라고 선언할 수 없다는 감사 결과다. 기능 보존형 A에서 바로 고치지 말고 별도 경계/사용자 검토 대상으로 남긴다.

| 경로 | 관찰한 현재 동작 | 분류 / 후속 위험 |
|---|---|---|
| `TrackStoreV27` / truth indices L26139~26170 | legacy/test track의 optional truthRef와 역 index가 존재. 일반 RF AIR/surface allowlist는 이를 전달하지 않는다. | legacy/diagnostic 보존용. normalized measurement와 trace export는 truthRef/objectId/owner/faction을 allowlist 밖으로 제외해야 한다. |
| `updateSensorTrackMeasurement` L27493~27494 | meta.truthRef가 주어지면 실제 trackIdForTruthV27로 ID를 예약한다. 자연 RF caller는 anonymous지만 공용 함수 자체는 legacy/test 입력을 수용한다. | 기존 fixture 모드와 자연 RF를 구분해서 보고해야 한다. A가 이 branch를 삭제하면 동작 보존 위반. |
| `truthObjectForTrackV27` L26272 | reference가 없더라도 실제 targetPool/enemyMissiles를 위치·속도 gate로 찾는다. | seeker/신관/피해·사후 진단에서만 허용할 경계다. 새 계약·연관·AI·UI가 호출하면 안 된다. |
| `updateRadar`의 target RWR 반응 L39702~39712 | precision track에 legacy truthDomain AIR가 있을 때 물리 aircraft를 찾아 threatened·radar threat vector를 기록. | target-side sensor/AI 경계의 기존 결합. 비누수 여부를 별도 검토할 debt이며 새 normalized observer payload에 넣지 않는다. |
| `updateThreatsFromMissiles` L39730/L39750 | assigned/seekerLock track를 truthObjectForTrack로 resolve한 뒤 실제 missile pose를 target의 threatX/Y/Kind로 쓴다. | legacy aircraft countermeasure AI 입력 경로. 실제 aircraft own seeker/RWR 측정 경계가 명시되지 않았으므로 baseline 감사 위험으로 남긴다. A에서 끄거나 무장 물리를 바꾸지 않는다. |
| `hardKillExistingEngagementCounts` L48958 | PHALANX 항목이 `ciws[0].trackingTarget.id === tracks.get(id)?.truthRef?.objectId`를 참조해 engagement resource count를 만든다. | 자연 anonymous track은 보통 null이지만, truth reference가 resource/전술 결정에 관여하는 기존 debt. 새 계약에 truth ID를 넣어 이 경로를 ‘보완’하면 안 된다. |
| `getIrccmAnchor` L48800 등 seeker helpers | physics target를 resolve해 actual angle/pose를 물리 시커에 공급. | 시커 물리 내부에 머무르는지 호출별 검토. AI/ship track의 관측값으로 전송 금지. |
| surface IFF L2517 vs AIR IFF L4397 | surface 인증은 expiry 없이 operator FRIEND 필드까지 쓴다. AIR 인증만 source/time/expiry를 분리. | 서로 같은 TTL·근거로 표시하면 잘못된 계약. TRACK-C에서 수명·operator provenance를 분리할 설계 위험. |
| visual association L27369/L29249 | 물리 경계에서 들어온 `meta.isASM`가 type exclusion과 tr.isASM에 쓰임. | optics가 분류한 관측 근거인지 legacy physics hint인지 명확하지 않다. A trace는 제공된 provenance를 기술하고 사실상 ‘완전한 ID’로 강화하지 않는다. |

## E. 진단 trace를 무상태로 만들 때 피할 호출

- `trackRadarAssociationNisV31` L25971은 단순 pure read처럼 보이지만 `trackEkfInit`과 derived WeakMap cache를 건드릴 수 있다. **실제 실행에서 계산된 NIS 결과를 기록**해야 하며 export 시 재계산하지 않는다.
- cross-domain eligibility 함수 L27441/L27450는 reject counter를 증가시킨다. trace 용도로 한 번 더 호출하지 않는다.
- `trackIsFireControlQuality` L27220와 `trackRefreshDerivedQuality` L26117는 track 파생 필드를 쓴다. trace export는 이미 존재하는 필드·typed array를 복사한다.
- `observerC`, `prepare*`, `c55Bank`, 일부 snapshot 함수는 없는 state를 생성할 수 있다. diagnostic 독립 조회에서 호출하지 말고 기록된 detached 자료만 반환한다.
- `harpoonTrackIdentityC` L5428는 history·correlation 필드를 갱신할 수 있는 operational function이다. 단순 설명 getter로 호출하지 않는다. trace에는 이미 확정된 결과만 기록한다.
- 통계/trace sequence는 simulation RNG·tick·scheduler counter를 재사용하지 않는다. normalized data가 기존 payload를 mutate하거나 필드를 추가해 JSON equality/validation/hashes를 바꾸지 않게 별도 sidecar/clone을 쓴다.

## F. source docs 대 실제 packed 실행 제품

`audit-local.json`은 Acorn으로 source 파일의 top-level function을 추출하고 packed baseline의 **마지막 main-scope symbol**과 코드 byte를 비교한 결과다. 파일 전체 exact=false는 문서 module를 현재 실행본으로 그대로 간주할 수 없다는 뜻이며, 아래 count가 동작 검증 PASS를 뜻하지는 않는다.

| 출처 파일 | top-level 함수 | packed current와 exact | 변경/추가 override 확인 |
|---|---:|---:|---|
| docs/multiship/H1/tactical.js | 22 | 17 | defaults/active/restore/command/reset |
| docs/multiship/H2/maneuver.js | 27 | 24 | yield/command/evaluate |
| docs/multiship/H3/attack.js | 23 | 17 | defaults/observation gate/command/authority/protection/commit |
| docs/multiship/H4/team.js | 32 | 31 | command |
| docs/multiship/C/observer.js | 21 | 13 | prepare/reset/classify/accept/step/view/snapshot/command |

실제 동작 판단은 packed current를 우선한다. 특히 FC의 NPC observer 차원 처리와 최신 Harpoon/H3 gate가 문서 초기 module와 다르다. 문서 파일을 통째로 다시 삽입해 최신 기능을 되돌리면 안 된다.

## G. 기존 증거 연결 및 판정

- `docs/contact/friendly/A/analysis/track-reproduction.json`: baseline의 세 자연 RF 재현 수(헬기 1/1/1, 이동 1/1/1, Harpoon 신규 2/최대2/마지막1). A에서 값이 달라지면 동작 보존 실패다.
- `docs/contact/friendly/A/evidence/contracts.json`: 측정 차원·prior/NIS·resolved one-to-one 및 ENV_D status의 9개 기존 검사. 이것만으로 자연 RF나 실 무장 회귀가 통과한 것은 아니다.
- `docs/contact/friendly/A/analysis/ciws30.csv`, `isolated.json`, `analysis/protection.json`: 419025와 오염 방지 증거. 이 audit-local 문서에서는 전투 원인을 새로 확정하지 않는다.
- `docs/contact/friendly/A/analysis/paired-observer-delta.json`: DDG/CG observer exact-state 2개 차이. 기대값을 승인/갱신하지 않는다.
- `docs/contact/friendly/A/VALIDATION.json`: releaseApproved=false, 도메인 404 PASS / observer exact 차이 2 / 구형 EMCON UI 14 미완료. 최초 기준으로 보존하고 새 실행 결과와 나란히 둔다.

본 감사는 TRACK-B/C/D에 대한 구현 승인이 아니다. 측정 계약에 불명확성이 발견돼도 TRACK-A에서 분류·prior·IFF 만료·AI·사격 결과를 바꾸지 말고, 메타데이터에 unknown/assumed/derived와 source를 명시해 기록해야 한다.
