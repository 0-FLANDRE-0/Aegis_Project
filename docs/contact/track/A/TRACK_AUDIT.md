# TRACK Baseline Audit

## 기준·범위·증거 등급

- 기준: `friendly-contact-a@4ba64ba0cace9124497a710d00df1b174984ffdc`.
- 실행 제품: `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`, SHA-256 `cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda`.
- 압축 index 13을 해제한 JS: 40,611,957 bytes, SHA-256 `79c73e36809bfcf38141da6698ab43bf4c19048595652db736c970842a85afe3`.
- 아래 `JS:L`은 이 **기준 제품의 해제 JS 줄번호**이며 새 TRACK-A 산출물/원본 module 줄번호가 아니다.
- 이 문서는 정적 감사와 **ARCHIVED** 증거의 교차 확인이다. fresh baseline, 새 HTML 동등성, 실제 RF/무장, fixture-only 판정은 실행 로그·`REPORT.md`·`VALIDATION.json`에서 따로 집계한다. 정적 설명만으로 PASS를 선언하지 않는다.
- 이번 구현 범위는 Baseline Audit와 TRACK-A의 진단용 호환 view/trace다. 연관·수명·식별 정책의 개선은 [FUTURE_STAGES.md](FUTURE_STAGES.md)의 설계 상태로 남는다.

세부 원천: [audit-local.md](audit-local.md), [audit-network.md](audit-network.md), [BASELINE_DELTAS.md](BASELINE_DELTAS.md), 함수 대응 JSON 두 개. 아래는 이 자료를 합친 실행 경로별 감사다.

### Lexical scope 판정

문자열 검색에서 마지막으로 발견한 동명 함수가 항상 canonical 함수인 것은 아니다. 실제 main scope를 AST로 확인한다. 예를 들어 main `updateTrackOperationalStateA3`는 JS:L26197, `trackEngagementGateA3`는 L26239, `networkProtectionG`는 L5048, `networkVlsGateG`는 L5159다. L64633부터의 `mapBNativePreview` **내부**에는 동일 이름의 private 복사본들이 존재한다(L64675/L64681/L64699 등). 이것들은 전역을 덮어쓰는 선언이 아니라 UI의 detached 발사 사전 판정 문맥이다. NPC `createWeaponContextD` 내부의 같은 이름도 그 owner 문맥에 속한다. source/packed 대조와 trace 삽입은 이름만이 아니라 범위·offset으로 고정해야 한다.

## 1. 생성·연관·갱신 경로

`관측 차원`은 실제 수치 update가 보는 독립 채널을 뜻한다. polar를 xyz로 변환한 좌표나 필터 속도를 추가 관측으로 세지 않는다.

| 경로·현재 위치 | 소유자 / 입력 출처 / 관측 차원 | 후보·게이트·일대일 | 읽기·쓰기 / 다음 소비자 / 기존 시험 |
|---|---|---|---|
| 공통 RF scene/echo, L30726/30733 | 물리 프런트엔드. 반사체 truth·receiver·빔·해면·기상은 **여기에서만** 신호 합성에 사용. 출력은 잡음 r/az/el/rdot·sigma·RF 특징 | 해상도 셀·CFAR. 목표 Track ID는 입력이 아님 | radar별 private RNG, 같은 tick/band의 물리 장면 cache. scene cache와 owner별 트랙/측정 공유를 혼동하지 않음. native RF/APS 시험 |
| RF→AIR/SURFACE plot, L30777/30778 | AIR r/az/el/rdot 4D; surface r/az 및 제공된 rdot 2/3D. surface z=8/losUz=0은 prior | L30766/30774의 측정 domain evidence에 따라 echo당 한 경로 선택 | measured plot·receiver origin/velocity·noise·quality. 물리 object/owner/faction을 익명 payload로 복사하지 않음 |
| 자함 SPY, L26858/26895/26965 | 자함 canonical `tracks`, 실제 장착 receiver가 합성한 AIR4D 또는 surface2/3D | focused proposal 뒤 AIR Hungarian 최소총 NIS; surface는 별도 우선 stage. 물리 dwell 내부 `usedTracks` 공유 | native updater가 x/P·hit·source·age를 갱신. focus는 추정 위치로 조준. 세 자연 재현 및 SPY/native RF 시험 |
| 자함 surface 배치, L26951/L27464 | 같은 자함 store, surface polar와 P/이력 | established surface 먼저, 남은 AIR/UNKNOWN cross stage. position-only NIS 할당 후 실제 Doppler update gate. cross gate 기존25 | source별 freshness/revisit/extent. 할당 NIS와 최종 update NIS를 분리 기록해야 함 |
| 자함 SPQ AIR, L34175/34184/34289 | 자함 store; 실제 함별 SPQ 프로파일. AIR4D | plot 순서 greedy + usedTracks. Hungarian 아님. 최근 SPY<0.65s이면 SPQ freshness/class만 기여하는 branch | canonical x/P 또는 보조 freshness. suppression을 독립 새 EKF hit로 세지 않음. SPQ/native·자연 재현 |
| 자함 SPQ surface, L34256 | r/az/rdot 3D; el/z는 미관측 | surface position Hungarian + 실제 3D surface update, 기존64/cross25 gate | `_spq9bSurfaceFreshS`, extent·contributor·canonical filter |
| BridgeMaster E, L34425/34450/34538/34549 | r/az **2D**. 최종 adapter가 RF radial을 제거. z=8은 prior | surface Hungarian one-to-one + native2D gate, capacity 유지 | P·freshness·extent·history. CG mask/장비 프로파일 유지. native surface/viewport 재현 |
| ARPA velocity, L34473 | 같은 BridgeMaster file의 여러 절대 측정 위치 회귀. 직접 Doppler 아님 | 기존 history/성숙도 조건 | vx/vy/P를 기존 gain으로 갱신하는 derived 경로. A에서 재회귀/재갱신 금지 |
| Visual, L27345/27369/27380/29249 | 광학 물리 프런트엔드의 noisy polar→xyz, 실제 filter는 Cartesian3D. radialMps=0은 placeholder | Cartesian NIS greedy. 개별 optical 호출 사이 공통 used set 없음 | x/P·hits·age·isASM legacy hint. B의 false-merge/duplicate-hit 감사 대상. A에서는 바꾸지 않음 |
| 외함 observer, L4629/4671/4698/4754 | 함별 `observerC.tracks`; 자함만 mature `tracks` alias. 외함 SPY/SPQ/NAV private RNG·원점 | cross-domain eligibility 뒤 NIS≤64 pair sort, usedTracks/usedPlots one-to-one. 확인 spacing0.15s | x/P·sensorHits/confirmed·source·age·domain/classification·WITHHELD. owner당 tick guard. multiship C observer/clock/propagation 시험 |
| APS-153, L4299/4301/4308/4321/4322/4326 | 모함 소유의 기체별 radar cells/contacts/RNG. **관측 r/az 2D**, XY는 nav+기하 변환, z는 해면 prior | 같은 range cell/beam 안 측정 병합 후 시간·range/angle metric; binary M-of-N. 동일 turn row 전체 used set은 없음 | 별도 기체 contact table, mask·lastAtS·confirmed. 동일 fix 재출력 억제. 현재 함 canonical tracker와 통합 금지. APS native/clock·anchor 시험 |
| Hawklink 송신, L4527/4542/4552/4561 | 기체→자기 모함 H1/H2. source/sequence/time·reported XYZ/P·domain evidence만 | own footprint blanking, quota/token/queue reserve. 링크 미연결 plot은 버림 | source queue≤64, 전송 counters. actual polar 성분은 received schema에서 소실되므로 reported XYZ≠3D 센서 관측. EMCON은 레이더 통제이며 통신 유지 |
| Hawklink/PLOT 수신, L4794/4809/4816/4840 | 수신 함 offboard.sources/queue → 해당 함 canonical store | strict schema/SPD/sequence/time, maxAge15s. Cartesian NIS≤25 최저 후보. **수신 batch one-to-one 없음** | original measuredAt, availableAt/receivedAt, local/remote stamps, x/P·hits·age. 같은 source의 같은/과거 fix는 새 확인 아님. P age² inflation 및 quality는 receiver derived |
| ISAR, L4125/4135/4145/4160/4174/4196/4208/4210 | RF 물리에서 형상·운동 합성 → 측정 특징량으로 library 후보. 기체별 RNG/result buffer, 함별 queue/history | 자기 contact 기하 선택, 함에서는 위치/P gate로 evidence 연관 | **isarEvidence만** 부착. native EKF/hit/age/identity/authority 갱신 없음. 링크 끊김 결과만 제한 buffer, 원 시각 유지. H/L native/classes/clock 시험 |
| ESM, L2450/2471/2485/2497 | 함별 ew.contacts/private RNG. bearing1D + sigma/band/type/quality/time, rangeKm=null | band/emitter-family·angular gate greedy + used set | bearing/hits/age·별도 contact ID. 거리/xyz 생성 없음. owner는 물리 self-coupling 억제에서만 사용. EW/ESM-only 시험 |
| AIR IFF, L4383/4397/4405 | 수신 함별 noisy r/az/el+authenticated bit, 표적 ID 없음 | geometry/sigma best score + used | iffF·FRIEND·WITHHELD, 위치 filter/hits 아님. AIR_IFF_E source/time/expiry. ON/OFF·만료·AUTO 재고 시험 |
| 수상함 IFF, L2507/2517 | noisy r/az+authenticated bit | surface geometry + used | iffF와 `_operatorIdentity=FRIEND`까지 기록, **explicit expiry 없음**. A가 삭제·통일하지 않음 |
| C55 local RF, 자함 L36964/37216, NPC L7575/7629 | 함/마운트별 bank·RNG. noisy r/az/el3D, rx/ry/rz는 변환. 관측 속도 없음 | 거리 gate + known own/non-own partition + sweep seen. source-order greedy, NIS 아님 | local relative filter·속도·CPA·TTI·hits/age/quality. 자함/NPC 두 문맥 독립. CIWS30/419025/protection 시험 |
| C55 CMS 대응/무장동의, L37168/37179/37249/37271/37828 | 해당 함의 observed CMS cue + local RF 상태/보호 | geometry/velocity 대응, 보호 veto, 기존 CPA/회전/사각 gate | local audit winner→native Phalanx/SeaRAM. 이미 비행 중 RAM은 기존 score 영향이며 새 무조건 대기 규칙이 아님 |
| Link16/G 수신·연관, L4906/4999/5018/5033 | 수신 함별 `networkG.files`는 canonical FCS와 **별도**. TRACK은 sender filter6D estimate/P, SELF는 자체 nav(단 z8/vz0 가정) | strict packet/replay/time; NIS36+거리2500m/속도180m/s cap, ambiguity gap4. reconcile local one-to-one | source별 file/timestamp/hit·localTrackId·별도 fused view. local EKF/새 hostile/발사 권한 생성 없음. multiship G network/clock/cooperation/guidance 시험 |
| Link16 CI·소비, L4958/5054/5060/5068/5159 | unknown correlation의 estimate/P, receiver own local track | **고정0.5 CI**, fresh2s/coast12s, local-only FCS | detached presentation·FRIEND/NEUTRAL 보호·기존 cooperative lease. remote-only를 CEC로 승격하지 않음. 보고서 재송신을 독립 KF fix로 간주 금지 |

## 2. 상태·분류·수명과 소비자

### 실제 상태와 prior

공통 EKF state는 `[xM,yM,zM,vxMps,vyMps,vzMps]`, P는6×6이다. AIR update L25901은 r/az/el/rdot4D, surface update L26028은 radial 제공 여부에 따라 r/az2D 또는 r/az/rdot3D다. optical/외부 위치는 covariance를 가진 Cartesian update다. 기존 행렬·gain·Joseph update·노이즈·음수 고도 clamp는 A 보존 대상이다.

friendly-contact의 `_radar3dAirStepFC`는 **수용된 local AIR radar update**에서만 쓰인다(L27410/27413/L27491). `TRACK_HARD_TTL=16.0s`(L25573) 동안 predicate가 true이면 L26013의 수면8m prior 강제를 건너뛴다. 2D hit는 이 시각을 freshen하지 않는다. 만료는 field 삭제가 아니라 predicate false이며 그 뒤 기존 prior/class eligibility가 다시 적용될 수 있다. `_surface2DOnlyFC`, `_surfaceMotionPriorWip13B13`의 실제 적용·해제 동작은 미승인 friendly 후보의 일부로 그대로 보존한다. A metadata가 더 좋은 정책처럼 이를 바꾸거나 covariance를 복구해서는 안 된다.

`trackLifecycleState`(L27143)는 기존 age/TTL/memory/reacquiring/quality 필드에서 상태를 파생한다. 자함 `updateRadar`(L39619)와 외함 step(4754)의 갱신 간격/필드는 완전히 같은 체계가 아니므로 하나의 새 mutable lifecycle enum으로 대체하지 않는다. 저장 시 전투 트랙·consent/AI memory가 초기화되는 기존 정책도 유지한다.

### 식별·권한을 구분하는 소비자

| 소비자 | 읽는 관측·근거 / 유지할 조건 |
|---|---|
| canonical `updateTrackOperationalStateA3` L26197 / gate L26239 | classification과 identity·threatStatus·authority는 별개. operator, 기존 own-launch radar correlation, IFF, observed hostile-intent, network protection과 native FCS/ROE/모드를 사용. 새 trace는 입력 아님 |
| H1 `tacticalEvaluateH1` L5530 | 자기 observer·freshness·assessment·권한. passive/shared alert가 local FCS를 대체하지 않음 |
| H2 L5647/5656/5706 | 자기 observed threat/traffic, 수신 network SELF 항해 정보와 자기 nav·손상. 다른 함 private 추정/유도/행동 상태를 새 입력으로 추가하지 않음 |
| H3 L5769/5859 | 자기 confirmed/fresh SURFACE estimate, 명시적 HOSTILE 또는 현행 team intent, 보호/consent/설비 gate. OODA/새 공격 점수 없음 |
| H4 L5932/6039 | local surface estimate와 현재 team/network intent·보호. 새 적성 정책·의도 모델 없음 |
| native FCS·WIP118/119 | 기존 measured state/P/quality·지원 장비·자원·동의. `trackIsFireControlQuality` L27220은 quality 쓰기가 있으므로 독립 진단 getter로 호출 금지 |
| CIC/MAP/FLEET | 기존 관측/수신 detached view·번호·quality/age. after-action truth나 trace ring을 표적 위치/발사 입력으로 사용 금지. preview의 local function은 canonical 함수와 lexical scope를 구분 |

## 3. fixed-tick 처리 순서

`simulateFixedTick` L55019 이하의 기준 순서다. A는 순서·실행 횟수를 바꾸지 않는다.

1. 해상·피해/침수 → 물리 side-channel 설치.
2. ESM receiver → chaff/NAV → H2/H3 → optical detection(L55037–55044).
3. 자함/외함 이동과 world 접촉(L55214–55228).
4. surface/Harpoon physical → 자함 SPY → datalink allocation → SPQ → NAV radar(L55229–55238).
5. Hawklink 상태/queue 차단 → observer predict/RF/offboard drain → EW context/수상 IFF → network → H4 → AIR IFF(L55239–55240).
6. 함별 weapon context·자함 gun·soft-kill·SPG/SARH·실제 탄/미사일/충돌/피해.
7. 헬기 운동과 APS/ISAR, 그 보고 enqueue(L55374–55375).
8. tick 증가 후 engagement control/automation(L55376–55378).

헬기 radar의 신규 보고는 이미 지나간 같은 tick의 observer drain에서 받을 수 없다. 원 measuredAt, enqueue/availableAt, receivedAt을 구분해야 한다. 외함 `OBSERVER_DOUBLE_TICK`, EW `EW_DOUBLE_TICK_F`, network `NETWORK_DOUBLE_TICK` guard를 보존한다. 진단이 원 producer/association/predict를 한 번 더 호출하면 read-only가 아니다.

## 4. 원본 module 대 packed 실행 제품

전체 module를 현재 JS에 재삽입하는 빌드 방식은 누적 수정을 되돌릴 수 있다. [audit-local.json](audit-local.json)과 [audit-network.json](audit-network.json)의 AST·offset·SHA 비교가 출처 지도다. 정적 exact는 실행 PASS가 아니다.

- C/observer에는 IFF/class confidence, friendly-contact 차원 metadata/eligibility, network/local provenance, reset 후속 연결 등 누적 차이가 있다. AIR_ORIGIN receiver origin/velocity를 가진 `observerExtractC`는 현재 source와 packed 양쪽에 있고 exact-match다.
- C/offboard의 packed에는 ISAR schema 분기/별도 drain, 식별 근거, helicopterImplemented 및 label 확장이 있다.
- G/network의 핵심 NIS/CI/receive/accept/reconcile 함수, G/cooperation의 canonical network gate는 해당 current source와 byte가 같다. preview 내부 복사본은 별도 scope다.
- H1 source22함수 중17, H2 27중24, H3 23중17, H4 32중31, C/observer21중13이 audit-local 비교에서 packed와 exact다. 나머지는 defaults/명령·gate·reset 등의 누적 수정이므로 옛 모듈을 통째로 재사용하지 않는다.

## 5. 정보 비누수 감사와 기존 debt

**프로젝트 전체가 이미 정보 비누수라고 선언하지 않는다.** 아래는 baseline에 존재하는 경계/위험이며 TRACK-A에서 몰래 삭제하거나 성공을 위해 바꾸지 않는다. 새로운 정규화·trace에는 복사하지 않고 후속 검토를 명시한다.

| 경로 | 기존 동작 / 금지할 확대 |
|---|---|
| TrackStore truth index L26139–26170, canonical meta.truthRef L27493–27494 | legacy/diagnostic 입력은 truth ID 기반 예약을 지원한다. 자연 RF는 anonymous다. 새 contract가 truthRef/objectId를 provenance로 사용하거나 이 branch로 익명 관측을 “고정”하면 안 됨 |
| `truthObjectForTrackV27` L26272 | reference가 없어도 물리 target pool을 위치/속도로 찾는 legacy resolver. 시커·신관·피해 물리/사후 감사와 실행 관측 연관·분류·AI·지도 소비를 엄격히 구분. 새 설명 getter에서 호출 금지 |
| RWR/target AI, updateRadar L39702–39712 및 updateThreatsFromMissiles L39730 이후 | actual missile/target를 resolve해 target-side threat vector에 쓰는 기존 결합. 실제 RWR sensor boundary가 명확한지 별도 감사할 debt이며 새로운 observation payload로 전파 금지 |
| `hardKillExistingEngagementCounts` L48950 | PHALANX resource count가 `tracks.get(id)?.truthRef?.objectId`를 참조. 자연 anonymous 파일에서 보통 null인 것과 모든 consumer가 truth-free라는 주장은 다름. 새 contract로 ID를 보충하지 않음 |
| Visual meta.isASM L27369/L29249 | physical caller의 hint가 association exclusion/legacy tr.isASM에 영향. 관측 분류와 physics hint 출처를 구별해야 하며 새 자동 식별 근거로 강화 금지 |
| C55 `proxy.id=e.id` L37243–37246 및 NPC L7649–7652 | 물리 ID가 selector/spotting/projectile bookkeeping까지 이동하는 기존 경계 위험. 신관/충돌 용도와 제어 bookkeeping을 구분해 후속 감사. adapter/trace에 proxy id, source key, 실제 label/faction/pose를 복사하지 않음 |
| C55 WeakMap/source lock | source key는 센서 프런트엔드 SEARCH/TRACK dwell 유지에 쓰임. 공개 target provenance·CMS identity로 승격 금지. ownFireEvidence는 기존 자함 발사 사실의 safety 근거로만 기록 |
| C55 보호 수명 | known-own flag는 file 수명 중 OR, CMS 보호는 일부 조건에서만 해제. friendly partition이 해결한 오염과 모든 보호 expiry의 해결은 다름. A에서 유효 보호 삭제/적성 강제 금지 |
| 수상 IFF vs AIR IFF | 수상 응답은 operator FRIEND까지 기록하고 expiry가 없으며 AIR_IFF_E만 expiry가 있음. 서로 같은 의미로 normalize하지 않음. C에서 별도 검토 |
| legacy ESM L28693 | truth-index bearing helper는 현재 확인된 DIAG 호출 L54721/54726에 남음. live updateESM은 anonymous EW pipeline. 새 live 연관이 이 index를 참조하지 않음 |
| ISAR 물리 형상 | actual shape/운동은 RF feature synthesis에서만 사용. 후보 classId는 측정 특징→library 결과이며 identity/HOSTILE/새 hit가 아님 |
| own nav/authentication | receiver/mother/통신 참가자 자기 owner/faction/nav 확인은 표적 hidden owner/faction/실좌표를 사용하는 것과 다름. SELF z8/vz0는 그 경우에도 assumption이다 |
| private 추정/네트워크 lineage | remote filter estimate에 포함된 이전 정보와 다른 sender를 통한 순환 계보가 현 schema에 완전히 남지 않음. CI0.5만으로 모든 순환이 안전하다고 선언하지 않음 |

## 6. 419025·paired 차이의 고정 기준

[BASELINE_DELTAS.md](BASELINE_DELTAS.md), [baseline-deltas.json](baseline-deltas.json), [timeline419025.csv](timeline419025.csv)가 고정 원시 증거 지도다. 여기서 CG_TURRET_A와 friendly-contact의 **이전 변경 차이**를 새 TRACK-A와 friendly-contact의 **동등성**과 혼동하지 않는다.

| 항목 | 상속된 기준 / 현재 판정 |
|---|---|
| seed419025 | CG 원본 무피격/HP100 → friendly 피격/HP6.846598842629405. CIWS-only 변경으로 재현, radar-only는 원본과 같음. **FAIL(상속·미해결)**. 기대값/계수·타이밍 보정 금지 |
| 실제 타임라인 | 31.5s 구 GUN file 보호 veto → 후보 32.3667s Phalanx 사격 →34.55s BODY DAMAGED/seeker57.8 → 원본 RAM5 KILL36.9333s, 후보 RAM5 SEA_IMPACT37.05s → 함 피격38.1333s |
| 인과 한계 | seeker failure 임계100보다57.8이 작아 hard failure라고 단정 불가. 추가 hit에 global RNG 소비 경로는 있으나 서로 다른 종료 tick RNG 차이를 동일 tick 원인 증명으로 쓰지 않음. 최초 RNG/file/source/후속 RAM 분기는 fresh 진단 증거가 필요 |
| paired observer2건 | DDG raid874 observer 경로, CG raid43경로 차이. 물리/전역 RNG/HP/VLS/표적 사건은 fixture 끝에서 같지만 DDG scheduler/track state와 CG 고도·분류·P의 실제 차이. **KNOWN_DELTA(미승인)**, 단순 진단 키 추가 아님 |
| 최초 도메인420 | **404 PASS / observer exact 차이2 / 구형 EMCON UI 미완료14**. UI213과 WebGL8/29는 별도 집계. 기대값 갱신 없음 |

A가 동일 결과를 재현하면 동작 보존 증거일 뿐 상속된 결함을 해결·승인한 것이 아니다. `releaseApproved=false`를 유지하고 final CLOSED/all-green을 선언하지 않는다.

## 7. 진단 무상태성과 시험 연결

- `trackRadarAssociationNisV31`, cross eligibility, `trackIsFireControlQuality`, `trackRefreshDerivedQuality`, `harpoonTrackIdentityC`는 lazy init/cache/counter/track 쓰기를 할 수 있다. trace export에서 다시 호출하지 않고 **실제로 계산된 결과**만 기록한다.
- `observerC`, `prepareNetworkG`, `c55Bank`, 일부 기존 snapshot은 없는 owner state를 만들 수 있다. 독립 조회는 새 trace ring의 복사본 또는 이미 존재하는 Map을 읽어야 한다.
- 측정·trace serial은 별도 진단 상태다. 게임 RNG/tick/scheduler와 공유하지 않는다. normalized object를 원 payload/track에 붙이거나 native consumer에 되돌려 쓰지 않는다.
- 기존 계약 fixture·새 adapter unit은 자연 RF/교전 증거가 아니다. 세 자연 재현·native owner별 후보·C5530/419025·IFF/AUTO 재고·Hawklink/network·배속·진단 ON/OFF·성능을 실제 HTML에서 별도 확인한다.
- `docs/helicopter/E/verify_stage_c.py`에는 F1 이전 `LOCAL_SURFACE_OBSERVATION_REQUIRED` 기대값이 있다. 현 OTH 정책과 혼동하지 않고 현재 H/verify_native.py 및 고정 검증 경로를 사용한다. 기존 UI #lockBtn 부재14건은 BLOCKED/INCOMPLETE이며 PASS로 바꾸지 않는다.

TRACK-A는 이 감사에서 발견한 legacy debt를 꺼서 가짜 PASS를 만들지 않는다. 후속 B/C/D 구현·계수 변경·기대값 승인·PR/병합/release/tag는 별도 요청과 검증이 필요하다.
