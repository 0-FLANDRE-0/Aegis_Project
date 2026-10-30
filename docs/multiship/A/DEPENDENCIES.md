# 실행 소유권과 다음 단계

기준 main은 PR #44 병합 `cb70a637105ce00e7c0619270237cc35a83d39c2`, Harpoon E HTML SHA `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`다. 이번 A는 1~2단계이며 실제 다함정 교전은 아래 순서로 진행한다.

| 영역 | 이번 상태·컨텍스트 | 다음 실행 분리 지점 |
|---|---|---|
| 항법·질량·침수·동역학 | 프로필/geometry/nav/ledger/clock을 받는 독립 모델 | `updateShipMovement`, `damageFloodTickV1`, survival/contact의 단일 자함 경로를 3단계에서 ship 인수로 분리 |
| 내부·보수·승조원 | 함종별 geometry와 부서·duty post, 독립 model/cache | 각 함정의 flood/control/crew 입력을 3단계에서 연결 |
| 센서·트랙 | 프로필 모델, 독립 radar/scheduler/Map/dwell | `updateRadar`, 보조 레이더, TrackStoreV27의 전역 index를 4단계에서 observer별 분리 |
| SPG/FCS | 독립 서보·할당·예약·상태 | `allocateSARH`, datalink, SPG 예약/서보와 선택 lock 의존을 5단계에서 owner별 분리 |
| 무장 | 설치·고정 셀·탄창·준비 상태, 비자함 함포 실행 거부 | 공통 발사 API에 shooter context·관측 트랙·권한을 전달. 탄의 sourceShipId와 실제 충돌 대상의 피해 runtime routing은 5단계 |
| EW | 독립 관측 Map·allocator·doctrine·soft-kill 재고 | noise/deception update의 전역 자함 의존을 6단계에서 emitter/receiver별 계산 |
| 구명뗏목·렌더링 | 자함의 기존 경로 유지, 적함 provision만 준비 | 3단계 활성화 때 controller/world 연결·함정별 root·owner damage state 연결 |
| UI | ACTIVE 자함 alias 유지 | CIC는 player observer에서만 읽음. 적함 진실 상태를 표시하지 않음 |
| 공통 세계 | 기존 weather/표적/탄/decoy/raft 배열 유지 | world step 1회 + 각 함정 step의 순서를 결정. world 이동과 scene origin 변경을 함정 수만큼 반복하지 않음 |

`simulateFixedTick`의 실행 순서와 난수 소비, `updateMissileBodyB3`와 `applyInterceptResult`의 전투 본문은 그대로다. 60 Hz 기본 tick, 120 Hz 침수·force 적분, 20 Hz hydro quadrature를 유지한다. 새 함정의 registry 등록 자체가 실행을 의미하지 않으며 적함 준비 과정에서 전투 RNG를 소비하지 않는다.

## 3~8단계 완료 조건

3. **실제 두 함정 물리·피해·표시**: fixed world 좌표로 하나의 적함을 먼저 배치한다. 함정별 pose/해수면/구획 피해·화재/침수/crew/질량/복원성/실제 외판·내부 표시를 연결하고, 자함 UI와 world origin 처리를 보존한다. 정상·편측 침수·기관/레이더 손실·침몰 및 1/8/16배속을 검사한다.
4. **관측**: 각 함정의 실제 레이더 면·사각·해면/지형/지평선·스캔 예산으로 관측을 만든다. 상대방 truth는 measurement synthesis에서만 읽으며 tracks는 관측값/공분산/age만 보유한다. 공개 스펙과 SIM-TUNE을 구분하고 observer별 난수 스트림을 먼저 정의한다.
5. **양방향 무장**: 기존 MANUAL/자동 방공 정책, 발사관·사각·SPG 채널·탄약/질량·source ID를 재사용한다. 실제 충돌 대상 runtime에 피해를 한 번 적용한다. CG의 SeaRAM 생성 금지와 DDG의 Harpoon 미설치를 유지한다.
6. **양방향 EW/CIC**: player는 ESM 방위·오차, 관측 신호 품질·트랙 공분산/끊김, 실제로 생성된 기만 관측만 본다. 상대의 `jammer ON`, 정확한 위치·효과·잔탄을 노출하지 않는다. 기존 I/J seeker 효과를 SPY의 수신 모델에 그대로 붙이지 않는다. Nulka/SRBOC는 실제 world decoy와 각 receiver의 관측에서 연결한다.
7. **적 AI**: observer facade와 허용된 command API만 제공한다. 위협 평가→방공 자원 배분→회피/EW→공격을 계층화한다. 공분산/age/채널·사각·재고·피해·권한을 지키며 상대 진실 위치로 탐지/명중을 보장하지 않는다.
8. **통합/성능**: DDG/CG 모든 조합·양방향 공격/요격·EW·상호 피해·동시 침몰·reset/save 실패를 검사한다. mobile hardware의 실제 FPS/heap/GPU 기록은 별도로 측정한다.

최적화는 1단계 측정을 비교 기준으로 한다. 우선 geometry·LOS/후보 공간 색인·동일 tick 재사용·관측/표시 cache·draw batching/particle 상한을 검토한다. 센서·무장 권위값이나 물리 cadence를 성능 조정용으로 낮추지 않는다. renderer는 물리·교전 난수를 계산하지 않는다.

## 알려진 검사 제한

이 단계의 native 검사는 미사일 비행 명중률이 아닌, 제어된 물리 관통 피해 후의 실제 GPU geometry commit과 draw/tick 지속을 목표로 한다. 초기 DDG `runWip107StraightKh35ImpactCase`(seed 107801, 4 km, 40초)는 접촉을 만들지 않아 그 장면을 피격 후 렌더링 PASS로 세지 않았다. CG에서 같은 fixture의 접촉은 관찰했지만 최종 판정에는 기존 양 함종 native 회귀의 Kh-32 structural probe를 사용한다. 이 작업에서 Kh-35 비행·피해 경로를 변경하지 않는다.
