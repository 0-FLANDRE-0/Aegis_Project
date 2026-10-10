# Multi Ship F — 아군·적군 배치 분리와 함정별 전자전

출항 전 아군함과 적함을 각각 없음/DDG-119/CG-52로 선택한다. 아군은 자함 근처, 적군은 독립 placement seed로 10~30km의 임의 방위·침로에 배치한다. 함체 지형 충돌·함정 중첩을 피하며 적군을 배치했다는 사실로 CIC 트랙이나 적성 identity를 생성하지 않는다. 시험 표적함과 적 항공기 스폰 선택도 유지한다.

## 실행과 RF 경계

`ShipRuntime.ew.executionF`가 각 함정의 ESM 파일·난수·전자전 설정·receiver 상태를 소유한다. 비자함의 `createElectronicContextF(owner)`는 기존 soft-kill/SLQ-32 47개 함수를 owner-local lexical binding으로 재사용한다. 원본 경계와 SHA는 `function-index.json`, 변경 경계는 `patch-index.json`에 기록한다. profile/global 교환이나 runtime eval은 없다. 60Hz마다 각 owner를 한 번 실행하고 세계의 탄체·채프·눌카 물리는 한 번만 진행한다. 원본 120Hz 침수/힘·20Hz 정수압 cadence는 유지한다.

RF 합성 경계에서 실제 건강한 탐색 레이더·실제 활성 시커·재밍·눌카의 방사 위치와 방위, 대역, 수신 안테나, 지평선/지형·기상·손상을 읽는다. receiver 이후에는 익명 bearing/sigma/strength/quality/band/family/measuredAt만 전달한다. 접촉에는 truthRef·객체/owner ID·좌표가 없고 거리 미확정 및 UNKNOWN이다. 근접 방위·대역·신호 계열로 연관하고 파일 수96·5Hz 수신·12초 coast/expire를 적용한다. 실제 alive를 보고 접촉을 즉시 지우지 않는다. 정상 CIC의 물리 대응체계 표시는 자함 소유 항목만 읽는다.

noise와 coherent replay는 각 수신기에서 실제 도달 전력·수신 빔·대역·ECCM에 따라 적용한다. 미사일의 기존 capture/hold/pull/coast/HOJ 커널과 radar echo frontend를 연결한다. 기존 전자전 모듈의 I/J/X 대역을 사용하며 S-band SPY에 같은 재밍을 강제로 적용하지 않는다. replay는 측정 바이어스이며 실제 적 좌표나 가짜 object ID 트랙을 주입하지 않는다. 양 기법의 기존 SLQ-32 자원 배분 합계는1 이하이다.

비자함은 기본 방어 AUTO/EW AUTO이며 관측 위협이 없으면 STANDBY다. EW AUTO는 자기 레이더와 익명 ESM의 위협 cue만 사용한다. Nulka/SRBOC는 기존 장착 좌표·사각·발사 속도·재고/예비탄/재장전·질량 변화로 실제 발사하며 owner별 난수·serial·cooldown을 분리한다. CG의 눌카4기×2튜브·SRBOC24 및 양현 Phalanx를 유지하고 RAM을 추가하지 않는다.

초기 EMCON은 **탐색 레이더 침묵** 설정이다. 수동 ESM 수신과 관측된 위협에 대한 방어 ECM은 가능하다. 아군 IFF의 기초는 인증 응답을 방위·거리 오차와 함께 수신하고 기존 fresh SURFACE 트랙과 측정 게이트로 연관한다. FRIEND/WITHHELD 보호를 적용하며 새 트랙·네트워크 좌표·합동교전 기능은 만들지 않는다. IFF FRIEND는 현재 파일의 보호 표식이며 정교한 IFF 재인증/운용자 해제 수명주기는 후속이다.

## 함종 등록과 SIM-TUNE 한계

CG는 원본 profile에 등록된 양현 AN/SLQ-32 pod 위치·건강도·사각을 사용한다. DDG 원본 모델/피해 registry에는 별도 EW 안테나가 없으므로 기존 body RF 기준점을 유지하고 CDC·발전기·함정/승조원 offline 상태로 가용성을 제한한다. DDG의 실제 안테나 위치나 개별 안테나 손상을 구현했다고 주장하지 않는다. 다음 geometry 등록 단계에서 보완한다.

대역별 전력·수신 감도·재밍 억압/ECCM·방위 오차·12초 보존·IFF 오차·replay 바이어스는 SIM-TUNE이며 실장비 비공개 성능 인증값이 아니다. 함종/장착 근거는 기존 [레이더 자료](../../bunkerhill/K/RADAR_SOURCES.md)와 [벙커힐 원본 구성](../../bunkerhill/K/README.md), soft-kill 공개 자료와 SIM-TUNE 구분은 기존 profile/source 주석을 따른다. 새 기밀 성능 자료를 사용하지 않았다.

## 모든 함정의 해상효과

자함의 기존 ocean foam shader와 speed/world-history 커널은 그대로 유지한다. 아군·적군에는 같은 커널을 해당 owner의 함종 수선면 함수/선미·반폭으로 결속한다. 양현 함수파2개와 양현 항적/선미 포말3개를 실제 항법 위치·침로·속도로 갱신하며 턴 뒤의 항적은 world history에 남는다. 같은 sea wave uniforms·floating origin으로 바다 표면을 따른다. 별도 폭발 splash나 새로운 추진기 물리 모델을 추가하지 않는다.

함정마다 mesh/geometry/material과 60초·최대255점 history를 소유한다. 원본 커널의 정지/속도별 fade, reset/teleport/긴3D 공백 단절을 재사용한다. renderer import/reset/retire에서 geometry/material/job과 해상효과 layer를 함께 폐기한다. 물리/전투 난수·world clock을 소비하지 않는 표시 전용이며 pooled mesh5개/owner로 제한한다. `ocean-index.json`은 원본 커널 SHA, `shipOceanEffectsAuditF`는 DIAGNOSTIC_ONLY detached 표시 감사다.

## 저장과 수명주기

배치는 `AEGIS_DEPLOYMENT_MULTI_SHIP_F_1`, fleet는 `AEGIS_NAVAL_PHYSICAL_FLEET_F_1`이다. ID/role/faction/profile/count/seed/EMCON 및 자함·외함 EW 설정과 soft-kill 재고를 detached preflight한다. 잘못된 import는 lifecycle·세계·예약·재고를 포함해 무변경 거부한다. A_1/E_1 배치는 명시적으로 아군 없음·기본 placement seed로 변환하며 A_1의 항공기 기본 ON을 유지한다. legacy B fleet/무장 미저장은 원래 명시 migration만 허용한다.

항법·피해·침수·승조원·유체·고정 VLS/무장·대응체계 재고/재장전과 EW 설정을 복원한다. ESM/track·비행 탄체·실제 재밍 technique timeline·예약/BDA는 combat transient로 비우며 `capabilities.deferred`에 명시한다. renderer는 같은 ID의 runtime 교체도 감지하여 원래 root/job을 폐기한다. 일반 `아군함 보기` 버튼으로 적 truth 위치를 노출하지 않는다. 기존 diagnostic focus는 검사 전용이다.

## 검증

최종 원본 SHA와 직접 실행 집계는 [verification-summary](evidence/verification-summary.json), 실측 환경은 [PERFORMANCE](PERFORMANCE.md)다. 진단 fixture와 실제 자연 관측 및 native RAF/WebGL 증거를 구별한다.

- `verify.py`: desktop/mobile의 실제 선택기, 3 owner/거리/재고, strict atomic 거부·legacy·저장 복원, passive RF·침묵/coast, 대역/거리/수신빔/손상, 측정 IFF, 실제 SRBOC/Nulka 발사와 재고 보존·독립성.
- `verify_natural.py`: 실제 20m Kh-35U 시커와 외함의 자연 레이더/ESM 관측으로 AUTO 재밍·눌카·SRBOC 수행 및 실제 시커의 J/N·coherent capture를 확인. hard-kill만 HOLD로 분리하며 EW는 AUTO다.
- `verify_clock.py`: 두 혼합 함종 편성의 세 척을 실제 accumulator로1/8/16/64×1536 full ticks 실행하고 물리·관측·무장·방어·EW/난수 및 shared world exact 비교.
- `verify_native.py`: 원본 RAF/WebGL의 세 모델, 모든 외함의 함수파/항적·독립 history·shared wave shader·reset 해상효과 폐기, 설치 부품, 일반 아군 카메라 read-only, 실제 피격 구멍 작업·지속 렌더, import/reset root 교체와 EW 설정 복원.
- `verify_departure.py`: 기존 항공기 ON/OFF 실제 UI/reset/new sea/import 및 명시 legacy schema migration.
- `verify_regression.py`: D 파일은 보존하고 시험 측 enemy HOLD/EW off로 manual 무장·효과 조건을 분리한다. 새 soft-kill 재고 비교는 transient `startedStep`을 제외하고 legacy fixture의 schema를 실제 옛 형식으로 지정한다.
- `verify_baseline.py`: 아군/적함 없음에서 원본 E와 F를 같은 seed/idle·raid·damaged로 비교한다. 새 EW 설정·profiler를 제외한 idle/damaged 물리는 exact다. E의 shared combat RNG 소비를 F의 독립 ESM RNG로 분리했으므로 이전 버전과 raid 발사 순서/RNG exact는 요구하지 않는다. 이번 fixture의 함체 HP/침수·손상·고정 셀/근접방어 재고는 같고 CG loaded VLS가1셀 차이이며, 이를 delta로 보존한다. 새 F 안의 배속/RNG 결정성은 별도 clock 검사가 확인한다.
- 원래 E의 방어 승인/차단/BDA/alias 검사와 D의 Harpoon INS/ARH/waypoint/DL0 격리 검사를 최종 F에도 실행한다.

정적 검사는 baseline SHA·packed14개 record 무결성·assets0~12/모델 exact·8개 원본 비행/탄도 커널·47개 source provenance·전체 JS 문법·재빌드 exact를 확인한다. 이전 E의660건을 이번 F 직접 실행 수에 합산하지 않는다. SwiftShader 결과는 실제 모바일 GPU/FPS 인증이 아니다. 검출/요격/전자전 성공률, 전 해역 배치 성공률, 현실 장비 성능을 보장하지 않는다.

```bash
python docs/multiship/F/build.py archive/v48/WIP_MULTI_SHIP_E/Aegis_SIM_v48_WIP_MULTI_SHIP_E.html artifacts/F.html
python docs/multiship/F/verify_static.py archive/v48/WIP_MULTI_SHIP_E/Aegis_SIM_v48_WIP_MULTI_SHIP_E.html Aegis_SIM_v48_WIP_MULTI_SHIP_F.html artifacts/static
python docs/multiship/F/verify.py Aegis_SIM_v48_WIP_MULTI_SHIP_F.html artifacts/verification
python docs/multiship/F/verify_natural.py Aegis_SIM_v48_WIP_MULTI_SHIP_F.html artifacts/natural
```

builder/검사는 Python 표준 라이브러리·Node 및 기존 [브라우저 의존성](../../bunkerhill/K/requirements.txt)을 사용한다. Actions 사용 불가라는 사용자 조건에 따라 로컬 검증·직접 업로드/readback으로 마감한다. workflow는 추후 사용 가능한 때 수동 실행하도록 준비하며 이번 마감의 필수 조건이 아니다.
