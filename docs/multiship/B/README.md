# Multi Ship B — 실제 두 함정

출항 전 `적함 배치`에서 없음/DDG-119/CG-52를 고르면, 출항 시 원본 함정 모델과 독립 물리 runtime을 세계에 놓는다. 기본값은 적함 없음이며 시험 표적함 HULK/NONE 설정은 별개다. 적함은 자함의 최초 침로로 8 kt 항해를 시작한다. 기본 위치는 자함 기준 전방 450 m·우현 350 m이며, 지형과 겹치면 난수 없이 대체 위치를 탐색한다. 출항 후 배치 설정은 잠긴다. `3D VIEW → 배치 함정 보기`로 해당 함정을 따라보고, 같은 버튼으로 자함 카메라로 돌아온다.

이번 범위는 **3단계 물리·피해·표시**다. 각 함정의 항법, 함체 자세, 해수면 표본, 외판/구획 피해, 보수/승조원, 침수, 질량, 복원성, 침몰과 구명뗏목을 실제로 실행한다. DDG는 310명/138구획/96셀/Phalanx+SeaRAM, CG는 330명/277구획/122셀/두 Phalanx를 기존 프로필에서 읽는다. 원본 model asset·프로필 revision·무장 성능은 보존한다.

센서의 함정별 실행, 양방향 미사일/함포 충돌 routing, 상대 ECM과 교전 AI는 **4~7단계 잔여**다. 현재 배치 함정은 항해와 물리 피해를 수행하고 무장·레이더는 준비 상태다. 따라서 CIC에 상대 truth 위치를 곧바로 추가하거나 기존 미사일을 이 함정에 자동 명중시키지 않는다. 별도의 센서 접촉·AI·공격 완료로 해석하면 안 된다.

## 소유권과 시간

`preparePhysicalShipB`가 독립 모델을 준비하고 `activatePhysicalShipB`가 world navalShips 및 raft controller에 연결한다. 자함의 기존 alias/UI는 유지한다. 공유 `updateShipMovement(dt, runtime)`와 `damageFloodTickV1(dt, runtime)`에 명시적 소유자를 넘기며 ACTIVE profile/global context를 교체하지 않는다. 각 함정은 고정 tick마다 한 번 진행하고 공통 날씨·탄·지형 세계는 한 번만 진행한다. 60 Hz 기본 tick, 침수/힘 적분 120 Hz, 정수압 20 Hz를 유지한다.

함체 접촉은 함종별 hull station footprint의 SAT 분리·질량 가중 위치 보정·비탄성 충격으로 처리한다. 손상은 동일 flooding/control/crew impact API로 전달한다. 초기 충돌 튜닝은 0.5 MJ 이상, 최대 20 damage, 외판 개구 최대 0.06 m², 폭발/점화 없음이다. 이는 **SIM-TUNED 보수적 근사**이며 정밀 선체 충돌 FEM이나 실제 충돌 강도값이 아니다. 원래 geometry tolerance에서 선수/선미의 halfBeam=0인 확인된 축방향 crossing도 누락하지 않도록 10 cm 안팎의 inside/outside 전이를 확인한다. 적함 좌초는 해당 hull footprint로 판정하고 그 함정만 정지한다.

표시 객체는 함정별 mesh/material/map/job/root를 소유한다. 기존 DDG/CG builder와 source geometry를 재사용하고, 늦게 선택된 CG의 원본 packed asset도 읽는다. 외판 구멍과 내부/승조원은 해당 runtime snapshot만 사용한다. 카메라와 geometry job은 물리/RNG를 변경하지 않는다. 외판 job은 기존 공통 frame work allowance 안에서 남는 시간을 사용하며 자함 피해가 있으면 예산을 나눈다. 원본 render LOD/culling을 적용하며 retire/reset에서 이전 root·job·proxy를 정리한다.

## 저장과 진단

운용 저장의 `fleet` codec은 배치 함정의 profile/revision, 항법/clock, 체계 손상, 개구/door/pump/물, 유체 재고, survival 자세/상태, 승조원과 raft manifest를 detached JSON으로 저장한다. 전체 preflight 후 별도 runtime에 복원한 뒤 교체한다. 거부한 입력은 권위 상태와 RNG를 바꾸지 않는다. A 저장처럼 fleet 필드가 없으면 명시 migration으로 새 물리 배치를 시작한다.

`fleet.deploymentState`는 NONE/PENDING/ACTIVE를 구분한다. 출항 전 선택만 있는 PENDING은 빈 함정 목록이 정상이며 초기 셀프테스트와 저장 검사를 통과한다. ACTIVE는 정확히 한 함정의 물리 상태를 요구하므로 누락한 저장을 거부한다. PENDING/legacy 복원은 선택한 프로필로 새 배치를 준비한다.

운용 저장은 계속 진행되는 전투의 replay가 아니다. 적함의 fire/DC 작업 timeline, structural fatigue/material loss history, rigid-body rate, 센서/탄/EW/교전 transient는 초기화한다. 상대 무장 운용과 탄약 변화는 아직 실행하지 않는다. 제외 범위를 capabilities.deferred에 기록한다. 개구의 ENTRY/EXIT role·물·승조원·뗏목은 복원한다.

`__NAVAL_SIM_DIAG__.physicalFleetSnapshotB()`는 진단 truth다. `physicalShipCommandB(id,{targetSpeedKt,targetRudder,abandon})`와 `physicalShipProbeB(id)`는 비자함 시험 전용이며 AI/플레이어 사통에 연결하지 않는다. probe는 실제 geometry를 관통하는 비폭발성 trace와 충격을 적용한다. 자연 미사일 비행 명중을 검증한 것으로 세지 않는다.

## 재생성·검사

```bash
python docs/multiship/B/build.py archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html artifacts/B.html
python docs/multiship/B/verify_static.py archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/static
python docs/multiship/B/verify_runtime.py Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/runtime
python docs/multiship/B/verify_clock.py Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/clock
python docs/multiship/B/verify_contacts.py Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/contacts
python docs/multiship/B/verify_native.py archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/native
```

고정 A HTML SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`에서 record 13과 build label만 재생성한다. 최종 결과·직접 판정 수는 [검증 집계](evidence/verification-summary.json), 측정 조건은 [PERFORMANCE.md](PERFORMANCE.md), 단계별 잔여는 [DEPENDENCIES.md](DEPENDENCIES.md)를 따른다. 과거 A/E/K 검사를 이번 직접 실행 수에 합산하지 않는다.
