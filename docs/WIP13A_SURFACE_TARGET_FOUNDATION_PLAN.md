# AEGIS v48 WIP13A 수상표적 기반 상세 구현계획

## 1. 기준과 작업선

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 기준 main commit: `ade7a0e96ad34d2f26e3f17a7b83adc885a9a974`
- 기준 HTML: `Aegis_SIM_v48_WIP12F.html`
- 기준 HTML Git blob: `472ddca40dcc40b4548b405583265853b14d91bb`
- 기준 HTML SHA-256: `887ee34656fbc18be59dfda14c8fdd35ce6558cc5626ef2fb29e4ba2f5187def`
- 작업 브랜치: `feat/v48-wip13a-surface-target-foundation`
- WIP 이름: `WIP13A_SURFACE_TARGET_FOUNDATION`
- 권위 blast mode: `COMPARTMENT_BLAST_AUTHORITY`

WIP13A는 WIP12F를 바꾸어 우회하지 않는다. 표적 형상과 damage consumer를 추가하고, 탄체·신관·관통·구획 폭발은 기존 WIP12A~F 계약을 그대로 소비한다.

## 2. 목표

첫 상세 수상표적은 화물과 승조원이 없는 가스 프리(gas-free) 컨테이너선 시험선으로 만든다. 이 표적은 다음 단계의 함포 외부탄도와 탄종 시험에 재사용하며, WIP13A 안에서는 SM-2MR Block IIIA와 ESSM Block 2의 제한적 대함 교전까지 실제 종단 피해 경로로 연결한다.

완료 상태는 다음과 같다.

1. 표적이 실제 크기의 3D 형상과 충돌 geometry를 갖는다.
2. aspect·주파수 대역·손상 상태를 입력으로 하는 명시적 RCS profile을 갖는다.
3. BridgeMaster E가 기존과 같이 익명 plot을 만들고, combat track에는 truth ID나 표적 이름이 들어가지 않는다.
4. 표적의 구획·모듈·침수·화재·종강도·영구 파괴구가 자함 상태와 완전히 분리되어 유지된다.
5. SM-2와 ESSM은 별도의 수상교전 계약을 통과한 수동 사격만 허용된다.
6. 직격 또는 근접 폭발은 확률식 즉사 판정이 아니라 WIP12F projectile spec과 target-local geometry/damage packet으로 처리된다.
7. 이후 WIP13B 함포가 동일한 target geometry와 damage adapter를 바로 사용할 수 있다.

## 3. 현재 코드 감사 결과

| 경로 | 현재 상태 | WIP13A에서 필요한 변경 |
|---|---|---|
| 수상 truth | `surfaceContacts[]`, `makeSurfaceContact()`, 이동·섬 회피가 이미 있음 | 기존 pool을 유지하고 상세 표적에만 `entityId`, profile, local damage state를 부착 |
| RCS | `surfaceRcsM2()`가 SMALL/MEDIUM/LARGE의 bow/beam/stern 단일 SIM_TUNED envelope 사용 | profile·band·aspect 기반 component RCS로 교체하되 기존 traffic fallback 유지 |
| 탐지/트랙 | BridgeMaster E가 2D anonymous plot을 생성하고 surface track으로 연관 | 익명성 유지, 상세 표적 식별 정보가 track으로 새지 않도록 회귀 고정 |
| 락온 | `selectedLockId`는 surface track도 지정 가능 | 지정과 무기사격 허가를 분리한 채 유지 |
| 일반 FCS 품질 | `trackIsFireControlQuality()`는 SPY/DL/TEST/SPQ-9B만 허용하고 BridgeMaster surface는 거부 | 일반 함대공 gate를 넓히지 않고 `surfaceFireControlSolution()`을 별도로 추가 |
| SPY scheduler | surface track을 명시적으로 건너뜀 | WIP13A에서는 그대로 둔다. 수상 FCS는 BridgeMaster E + SPQ-9B surface precision + 높이 prior로 구성 |
| SM-2/ESSM 발사 | 두 함수 모두 일반 FCS와 A3 gate를 요구 | weapon/domain별 `surfaceEngagementGate()`를 추가하고 기존 air path는 그대로 유지 |
| 미사일 truth resolver | 익명 track의 일시적 물리 표적 탐색이 air/ASM만 순회 | 무기·충돌 physics 경계에서만 surface pool을 포함하는 domain-aware resolver 추가 |
| SM-2 SARH RF | reflector pool이 항공기·ASM·채프만 포함 | 모든 live detailed surface reflector를 SPG-62 조명 volume에 추가 |
| ESSM ARH RF | SM-2와 같은 pool을 재사용하므로 surface echo가 없음 | surface RCS/extent/sea clutter를 가진 echo 추가 |
| 근접신관/충돌 | 표적을 점으로 보고 ASM/aircraft Pk 소비자로 분기 | 선박 OBB/section geometry와 swept contact를 사용하고 surface terminal resolver로 분기 |
| WIP12F terminal | projectile tracer와 armor patch key는 `targetEntityId` 범용 | 그대로 재사용 |
| WIP12F damage consumer | `wip12aApplyDamagePacket()` 이후가 자함 hitbox·module·flood 전역 상태에 결합 | target-local topology/module/flood/fire/strength adapter 추가 |
| 3D render-state | 수상 contact/target export가 없음 | detailed surface target와 영구 damage visual export 추가 |
| 2D 표시 | anonymous surface track symbol만 존재 | 전술 화면은 관측 정보만 유지; 별도 시험장 계측 패널에만 truth damage 표시 |

이 감사에서 가장 중요한 금지점은 `trackIsFireControlQuality()`를 surface 때문에 느슨하게 만드는 것이다. 그렇게 하면 함대공 자동화, CIWS cue, 기존 A3 권한까지 함께 넓어질 수 있다.

## 4. 상세 표적 계약

### 4.1 첫 profile

`EMPTY_CONTAINER_TEST_HULK_V1`을 추가한다.

- 용도: 무인·무화물·gas-free 탄착 및 피해평가 시험선
- 기준 치수: 길이 약 210 m, 폭 약 31 m의 generic large merchant proxy
- 상태: 정지 또는 일정 침로/속력 시나리오 선택
- 화물 위험: `NONE`
- 승조원: `NONE`
- 추진: 기본 `DEAD_SHIP`, 이동시험에서만 prescribed motion
- 연료/윤활유: 최소 service load만 두어 기관실 국부 화재는 가능하되 화물 연쇄폭발은 금지
- 출처 등급: 치수·강재·구획·RCS 수치는 모두 `SIM_TUNED_GENERIC_MERCHANT_PROXY`; 실선 고유 성능으로 주장하지 않음

일반 배경 traffic은 계속 lightweight contact로 둔다. 고비용 구획/피해/mesh 상태는 기본 한 척의 detailed target에만 할당한다.

### 4.2 entity와 profile 분리

```text
surface contact entity
  entityId
  physicalProfileId
  detailLevel: LIGHTWEIGHT | DAMAGEABLE
  motion state
  radar signature state
  target-local damage runtime
  render revision
```

- `id`는 기존 surface pool 수명에 쓰고, 외부 damage ledger에는 충돌하지 않는 문자열 `entityId`를 쓴다.
- 전술 track은 `entityId`, `physicalProfileId`, truth object reference를 보관하지 않는다.
- reset은 background traffic, detailed target, target damage ledger를 명시적 순서로 초기화한다.

### 4.3 형상과 내부

초기 topology는 약 18~22개 bounded space로 제한한다.

- 선수창/체인 로커
- 6~8개 빈 화물창과 대응 이중저·ballast 구역
- 기관실
- 보조기계실
- 축계/타기실
- 거주구·함교 하부
- 함교/항해실
- 상갑판 및 외부 shell section

초기 물리 모듈은 `BRIDGE`, `NAV_RADAR`, `MAIN_ENGINE`, `SHAFT`, `STEERING_GEAR`, `GEN_A`, `GEN_B`, `FIRE_MAIN`, `BILGE_PUMP_A`, `BILGE_PUMP_B`로 제한한다. 빈 화물창 자체는 피해를 흡수하지만 존재하지 않는 화물이나 LNG를 생성하지 않는다.

외판은 merchant steel material profile로 두며 RHA와 동일 취급하지 않는다. 판 두께는 위치별 generic proxy로 명시하고, 관통 판정은 WIP12F의 obliquity·plate failure·fuze qualification을 그대로 사용한다.

## 5. RCS 계약

### 5.1 profile 구조

단일 `sizeClass` 숫자 대신 다음 합성 profile을 사용한다.

```text
rcsProfile
  sourceClass
  bands
    S_NAVIGATION
    X_SURFACE_FC
    IJ_SARH_ARH_SIM
  aspect control points
  hull/superstructure/mast contributors
  radarHeightM
  horizontal/vertical extent
  sea-clutter coefficients
```

- 기존 LARGE의 S-band bow/beam/stern `110/780/190 m²`는 회귀용 초기 anchor일 뿐 측정값이 아니다.
- 0~180도 aspect control points를 연속 보간하고 좌우 대칭을 기본으로 한다.
- band별 값은 따로 보관한다. BridgeMaster E의 S-band scalar를 ESSM/SM-2 seeker에 그대로 재사용하지 않는다.
- 피해가 RCS에 미치는 영향은 큰 구조물·mast contributor의 상실만 반영한다. 작은 파괴구나 그을음이 매 frame RCS를 흔들게 만들지 않는다.
- RCS 합성은 sensor/seeker truth physics에서만 사용하고 combat track metadata에는 기록하지 않는다.

### 5.2 센서별 소비

- BridgeMaster E: S-band profile + horizon + sea clutter + 기존 독립 RNG
- SPQ-9B surface precision: X-band profile + 기계주사 revisit + 수평선/해면 clutter
- SM-2 SARH: SPG-62→표적→missile bistatic geometry, `IJ_SARH_ARH_SIM`
- ESSM ARH: missile→표적 monostatic geometry, `IJ_SARH_ARH_SIM`

각 센서는 같은 물체 geometry를 보되 서로 다른 RF equation과 RNG state를 사용한다.

## 6. surface fire-control과 교전권한

### 6.1 surface FCS

새 `surfaceFireControlSolution(trackId, weaponType)`은 다음을 모두 확인한다.

1. `domain === SURFACE`
2. track confirmed, displayable, non-MEM, non-reacquire
3. 최근 BridgeMaster E 또는 SPQ-9B surface measurement
4. position/velocity covariance가 무기별 한계 이하
5. waterline 기반 높이 prior가 명시적으로 존재
6. 사격함과 표적 사이 terrain/radar line of sight
7. 무기별 최소·최대 사거리와 launch/sea-clearance 해가 존재

결과는 일반 `trackIsFireControlQuality()`에 합치지 않는다.

### 6.2 권한

operator identity에 `TRAINING_TARGET`을 추가한다. surface manual gate는 `HOSTILE` 또는 `TRAINING_TARGET`만 허용한다.

- `UNKNOWN`: 차단
- `FRIEND`: 차단
- `NEUTRAL`: 차단
- `HOSTILE`: 수동 발사만 허용
- `TRAINING_TARGET`: 수동 발사만 허용
- AUTO/SEMIAUTO doctrine: WIP13A에서 surface launch 금지

단순 cursor designation이나 BridgeMaster track 생성은 발사권한이 아니다.

## 7. 제한적 SM-2/ESSM 대함 교전

### 7.1 공개 근거와 모델 경계

- 현재 Raytheon SM-2 설명은 SM-2를 주로 함대공/함정 방어 무기로 설명하며 수상표적 임무나 그 성능 envelope를 공개하지 않는다. 따라서 SM-2 surface mode는 `SIM_WORKING_ASSUMPTION_LIMITED_SARH_SURFACE`로 표시한다.
- Raytheon의 2013 ESSM 보도자료는 ESSM이 surface target에도 대응한다고 명시한다. 그러나 정확한 표적 종류, seeker logic, 최소/최대 사거리와 종말 aimpoint는 공개되지 않았으므로 수치 계약은 `SIM_TUNED_PUBLIC_UNKNOWN`으로 둔다.

근거:

- Raytheon SM-2: https://www.rtx.com/raytheon/what-we-do/sea/sm-2-missile
- Raytheon ESSM release: https://www.prnewswire.com/news-releases/essm-intercept-of-high-diving-threat-proves-expanded-defensive-capability-207345421.html
- U.S. Navy Standard Missile fact file: https://www.navy.mil/Resources/Fact-Files/Display-FactFiles/Article/2169011/standard-missile/

### 7.2 SM-2MR Block IIIA

- mode: `LIMITED_SURFACE_SARH`
- 수동 표적 지정과 별도 surface gate 필수
- EMCON 해제 필수
- SPG-62 배정과 종말까지의 line of sight 필수
- 중간유도는 surface track estimate만 사용
- SARH RF core가 실제 surface echo를 획득해야 종말 authority 승격
- 수평선과 조명 geometry 때문에 AAW 공개 최대사거리를 surface range로 사용하지 않음
- 초기 envelope seed는 대략 2.5~35 km의 SIM_TUNED 범위로 두고, 실제 6DOF/조명/CPA 회귀 결과로 줄일 수만 있음

### 7.3 ESSM Block 2

- mode: `LIMITED_SURFACE_ARH`
- 수동 표적 지정과 별도 surface gate 필수
- 발사 전 surface FCS track 필수
- 중간유도는 track/DL estimate, 종말은 surface RCS를 보는 onboard ARH가 권위
- sea clutter와 low-elevation multipath를 기존 RF chain에서 적용
- seeker acquisition 실패 시 truth 추적으로 대체하지 않음
- 초기 envelope seed는 대략 1.5~25 km의 SIM_TUNED 범위로 두고 6DOF/ARH 회귀로 조정

두 무기 모두 장거리 대함미사일의 대체재로 취급하지 않는다.

### 7.4 종말 효과

- 실제 hull/superstructure swept contact가 먼저 발생하면 `CONTACT_DIRECT_ACTION`
- contact 전에 유효한 TDD event가 발생하면 `PROXIMITY`
- direct contact는 기존 `WIP12B_LIVE_ORDNANCE.SM2/ESSM.spec`을 target geometry에 투입
- proximity는 burst point와 fragment field를 target-local damage packet으로 변환
- 선박에는 `computeInterceptPk()` 기반 즉사 확률을 사용하지 않음
- 작은 blast-frag 탄두이므로 비장갑 상부구조·센서·함교에는 큰 국부 피해가 가능하지만, 넓은 상선 전체가 단발로 사라지는 식의 scalar kill은 금지
- 개구는 WIP12F 규칙대로 `PERFORATED` 또는 solved blast rupture에서만 생성

## 8. target-local damage adapter

새 adapter는 WIP12F packet을 바꾸지 않고 소비 대상만 분기한다.

```text
damage packet
  -> target registry lookup by targetEntityId
  -> target geometry/topology adapter
  -> target module damage
  -> target flooding/fire/strength
  -> target persistent armor/scar/opening ledger
  -> read-only render snapshot
```

필수 규칙:

- `OWN_SHIP` packet은 기존 경로와 bit-for-bit 동일하게 유지한다.
- 상세 수상표적 packet은 `surfaceTargetDamageRuntime(entityId)`로만 들어간다.
- target A 피해가 target B 또는 자함 module/flood state를 바꾸면 실패다.
- damage packet은 impact event ID당 정확히 한 번 적용한다.
- hole/scar/armor patch/opening은 target reset 또는 scenario reset 전까지 사라지지 않는다.
- 이동·회전 후에도 target-local 좌표에 붙어 있어야 한다.
- 구획 침수, 화재와 종강도는 고정 timestep에서만 갱신하고 renderer는 읽기 전용이다.

## 9. 표시와 시험 계측

### 9.1 3D

- 컨테이너가 없는 hull, empty cell guides/hold openings, 선미 기관부, 거주구·함교를 식별 가능한 저비용 mesh로 구성
- `surfaceTargets[]` render contract에 world pose, dimensions, damage revision을 export
- target-local scar, opening, smoke, fire, flooding attitude를 export
- 상세 표적 한 척을 기본 budget으로 하고 배경 traffic에는 단순 silhouette 또는 3D 미표시 정책 유지

### 9.2 2D와 계측

- 전술 PPI는 기존 anonymous track symbol과 관측 기반 BDA만 표시
- 별도 `TEST TARGET INSTRUMENTATION` 패널에서만 truth damage를 표시
- 최소 계측: HULL, STRUCTURE, FLOODING, FIRE, BRIDGE, PROPULSION, STEERING, GENERATION
- 패널은 시험표적 전용임을 명시하고 Aegis sensor truth처럼 위장하지 않는다.

## 10. 구현 순서

### Phase A — 계약·entity·deterministic fixture

- profile/registry/entity ID
- detailed target 단일 spawn/reset
- target-local 좌표계와 OBB/section query
- diagnostic API와 정적 계약 시험

### Phase B — RCS·센서·surface FCS

- band/aspect RCS 합성
- BridgeMaster E 회귀 보존
- SPQ-9B surface precision plot
- surface FCS 품질/LOS/range gate
- `TRAINING_TARGET` 수동 권한

### Phase C — 3D 형상·피해 runtime

- render-state와 mesh
- compartment/module/flood/fire/strength state
- WIP12F target-local damage adapter
- persistent scar/opening/armor patch
- 시험 계측 패널

### Phase D — SM-2/ESSM surface flight와 RF

- domain-aware launch mode
- surface reflector를 SARH/ARH pool에 추가
- low-altitude trajectory/sea-clearance/aimpoint logic
- SPG-62 surface illumination과 ESSM terminal acquire
- physical hull contact와 proximity event

### Phase E — 종말 피해·회귀·성능

- contact/proximity를 WIP12F packet으로 단일 적용
- 기존 air/ASM/CIWS/A3 회귀
- 장기 timestep·3D 성능·reset lifetime 검증
- 최종 HTML, paired status, handoff, SHA-256 생성

## 11. 결정적 회귀 기준

### 11.1 truth/track 경계

- surface track에 `truthRef`, `entityId`, `physicalProfileId`, truthKind가 없어야 한다.
- 동일 seed에서 BridgeMaster/SPQ-9B plot, RCS와 association 결과가 반복되어야 한다.
- 센서 RNG와 weapon seeker RNG가 서로 소비 순서를 오염시키지 않아야 한다.

### 11.2 RCS

- 같은 band에서 beam aspect가 bow/stern보다 커야 한다.
- 0/180도 경계와 좌우 대칭에서 불연속 jump가 없어야 한다.
- S/X/IJ profile이 독립적으로 조회되어야 한다.
- mast contributor 제거 전후의 변화는 bounded하고 음수/NaN이 없어야 한다.

### 11.3 권한과 발사

- UNKNOWN/FRIEND/NEUTRAL surface track은 SM-2/ESSM 발사가 차단되어야 한다.
- TRAINING_TARGET/HOSTILE라도 자동 발사는 차단되어야 한다.
- 일반 air track의 기존 `trackIsFireControlQuality()`와 A3 결과가 변하지 않아야 한다.
- surface launch는 range, LOS, EMCON, SPG-62/ARH 조건의 각 실패 사유를 구분해야 한다.

### 11.4 유도·RF·종말

- SM-2는 surface SARH echo 없이 terminal authority를 얻지 못해야 한다.
- ESSM은 surface ARH echo를 실제 획득해야 하며 seeker 실패 때 truth 추적으로 전환하지 않아야 한다.
- missile assignment는 끝까지 track ID이고, truth object ID는 physics resolver 밖으로 나오지 않아야 한다.
- bow/beam/stern/상부구조 직격이 각각 실제 mesh와 같은 위치에서 terminal trace를 시작해야 한다.
- ship contact와 proximity의 가장 이른 유효 event 하나만 신관을 작동시켜야 한다.

### 11.5 피해와 persistence

- 동일 impact event 중복 적용은 거부되어야 한다.
- target packet이 자함 HP/module/crew/flood를 바꾸지 않아야 한다.
- 빈 화물창은 crew casualty나 cargo/LNG 폭발을 생성하지 않아야 한다.
- 기관·발전·함교·타기실은 물리 위치에 따라 독립적으로 피해를 받아야 한다.
- perforation/solved rupture만 opening과 flooding을 만들고 PARTIAL은 표면 손상만 남겨야 한다.
- 파괴구·그을음·armor patch·침수 opening은 장시간 진행 후에도 유지되고 target reset에서만 제거되어야 한다.

### 11.6 검증 순서

1. static contract test
2. 기존 core selftest
3. WIP13A deterministic diagnostics
4. Playwright/browser 시나리오
5. 1×/4×/고정 timestep 장기 안정성
6. 3D draw-call/heap/프레임 budget 확인
7. 기준 HTML과 최종 HTML SHA-256 기록

## 12. WIP13A 비범위

- 표적의 자율 항해, 회피, 사격 또는 전투 AI
- 실제 LNG 적재·BLEVE·극저온 누출
- 민간 승조원 및 damage-control AI
- 공개 근거가 없는 실기 RCS/ECM/사거리 수치의 사실 주장
- SM-2/ESSM 자동 대함교전
- 함포 director, 탄도, 탄종 UI와 사격 절차 — 이것은 같은 표적 계약을 소비하는 WIP13B 진입점
- 다수 detailed ship의 동시 full-damage simulation

## 13. 완료 산출물

- `Aegis_SIM_v48_WIP13A.html`
- `docs/WIP13A_SURFACE_TARGET_FOUNDATION_IMPLEMENTATION.md`
- `docs/WIP13A_SURFACE_TARGET_FOUNDATION_HANDOFF.md`
- `tests/surface-target-wip13a-contract.cjs`
- `tests/surface-target-wip13a.spec.js`
- `AEGIS_PLAN_STATUS_v48_WIP13A.md`
- `WIP13A_SHA256SUMS.txt`

대형 HTML 업로드는 기존 협업 규칙대로 사용자가 맡는다. 브랜치에는 우선 이 계획과 이후 테스트/문서를 체크포인트로 올리고, 최종 HTML이 업로드된 뒤 회귀·PR·병합을 진행한다.
