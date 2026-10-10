# Multi Ship C — 함정별 관측과 외부 관측 포트

4단계 구현이다. 출항 전 적함을 DDG-119 또는 CG-52로 선택하면, B의 실제 항해·피해 runtime에 해당 함종의 SPY/해면탐색/항법 레이더 관측을 실행한다. 자함 CIC에는 **자함 센서가 측정한 익명 접촉**만 나타난다. 배치 함정의 실제 위치를 트랙으로 바로 복사하지 않는다. 기본 적함 없음과 출항 시 자함 EMCON ON은 기존 설정대로다. 센서 송신을 켜야 자함 레이더 접촉을 얻는다.

## 실행과 경계

자함은 기존 canonical SPY scheduler·aux·TrackStore를 유지한다. 배치 함정은 `ShipRuntime.combatSystem.observerC` 아래 독립 scan cursor, 회전각, RNG/normal spare, 제한된 plot/history와 track Map을 가진다. 공통 RF 반사장·해면 clutter·SNR/측정 추출기·EKF를 명시 receiver 위치/속도/난수와 사용한다. 공통 세계·날씨는 한 번 진행하며 함정마다 fixed tick에 한 번만 observer를 실행한다. ACTIVE 함정/profile이나 전역 alias를 교대하지 않는다.

배치 함정의 실제 geometry/aspect가 물리 RF 반사를 만든다. 자기 함정 반사는 수신 단계에서 제외하고, echo 뒤 plot에는 target ID/실제 이름/정체를 전달하지 않는다. 반사 강도는 **SIM-TUNE**이며 실제 함정 RCS 자료로 주장하지 않는다. 일반 미사일 시커의 reflector registry에는 새 navalShips를 아직 넣지 않는다. 실제 탄의 해당 함정 contact/피해 routing과 owner 사통이 5단계이기 때문이다.

배치 함정 SPY는 원본 class face normal에서 360° 구역을 만들고 horizon/volume raster·확인/재방문/재획득을 profile budget 안에서 처리한다. CG는 기존 modernized AN/SPY-1A profile와 전후·양현 면, DDG는 AN/SPY-1D(V)와 대각 면을 따른다. CG SPQ-9 두 면·SPS-73, DDG SPQ-9B 두 면과 narrow horizon/down lobes·BridgeMaster E의 기존 profile을 적용한다. NAV의 2D/60-track·상대 속도 제한과 CG 원본 source geometry의 사각·지형/지평선 차폐를 사용한다. 새 장비 revision이나 공개되지 않은 성능을 확정하지 않는다. 역사 자료 범위는 [K 레이더 자료](../../bunkerhill/K/RADAR_SOURCES.md)를 따른다.

플롯 연관은 측정·공분산·domain evidence만 사용하고 배치 함정은 동일 tick 반복 hit를 확인으로 세지 않는다. 분류는 식별·교전권한과 분리하여 UNKNOWN/WITHHELD를 유지한다. 자함의 기존 MANUAL_ONLY 규칙은 유지하며 자동 적성/발사 권한을 새로 부여하지 않는다. EMCON/개별 센서 정지·해당 장비/전원 손상·함정 상실에서 관측을 멈추고 기존 file은 예측/coast/memory/drop한다. 미래 AI는 `observerFacadeC(runtime)`의 detached 추정치·공분산·age만 읽어야 한다.

3D는 observer의 실제 회전각을 읽는다. 카메라/2D↔3D 전환이 scan/RNG/물리를 진행하지 않는다. B의 원본 함정 모델과 피격 표시를 재사용하며 SPG/무장은 다음 단계까지 parked 상태다. reset/import/retire에서 observer·외부 링크와 대기 보고를 정리한다. 잘못된 import는 이전 상태를 바꾸지 않는다.

## 이후 헬기를 위한 포트

**헬기 모델·비행·실제 센서는 아직 없다.** 이번에는 측정 보고를 받을 공통 포트만 준비했다. `configureOffboardSourceC(runtime, {sourceId, connected, latencyS})`로 수신원을 설정하고 `ingestOffboardReportC(runtime, report)`에 아래 보고를 전달한다. 지연 0~10초, 최대8수신원/64대기 보고, 15초를 넘은 측정은 거부한다.

```json
{
  "schema": "AEGIS_OFFBOARD_PLOT_C_1",
  "sourceId": "HELI_TEST",
  "sequence": 1,
  "measuredAtS": 12.5,
  "positionM": {"x": 90000, "y": 65000, "z": 8},
  "covarianceM2": [40000,0,0,0,40000,0,0,0,400],
  "domainEvidence": {"surface":0.9,"air":0.1,"missile":0.1,"background":0.1}
}
```

sourceId는 보고원이지 표적 ID가 아니다. 보고에는 정확한 truth 위치/속도/실제 표적 ID가 아닌 **외부 센서의 추정 위치·측정시각·오차**를 넣어야 한다. 표적 truth field·비대칭/비양정 covariance·미래/오래된 시각·재전송·끊긴 링크를 거부한다. 수신 지연 동안 불확실성을 늘리고 측정 age를 보존한다. 첫 보고 공분산을 중복 갱신하지 않는다. 같은 file에서 같은 수신원의 반복/이전 fix는 새 sequence여도 확인 hit를 늘리지 않는다. 링크 단절은 대기 보고를 제거하며 이미 받은 file은 기존 예측으로 오래된다. CIC 선택 정보에는 EXT/source/측정 age/LINK LOST를 표시한다.

이 포트는 함정의 관측을 위한 것이다. Harpoon은 발사 전 알려진 접촉 추정이나 기존 좌표 경로를 사용하며 **발사 후 DL=0**을 유지한다. 헬기 보고 수신 여부로 발사한 탄의 현재 위치/INS/시커/명중을 함정 화면에 노출하지 않는다.

## 저장·진단·검사

운용 저장은 B의 함정 물리 state를 유지하지만 센서 file·flight·offboard 연결/대기 보고는 combat transient로 복원하지 않는다. `capabilities.deferred`에 외부 링크/보고 제외를 기록한다. 플레이어 교대 조종·상대 원격발사 UI와 적 AI는 없다. diagnostic observer command/가상 높은 receiver는 시험용이며 실제 헬기나 사통 입력으로 연결하지 않는다.

```bash
python docs/multiship/C/build.py archive/v48/WIP_MULTI_SHIP_B/Aegis_SIM_v48_WIP_MULTI_SHIP_B.html artifacts/C.html
python docs/multiship/C/verify_static.py archive/v48/WIP_MULTI_SHIP_B/Aegis_SIM_v48_WIP_MULTI_SHIP_B.html Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/static
python docs/multiship/C/verify_observers.py Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/observers
python docs/multiship/C/verify_propagation.py Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/propagation
python docs/multiship/C/verify_clock.py Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/clock
python docs/multiship/C/verify_native.py Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/native
python docs/multiship/C/verify_physical_native.py archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/physical-native
```

최종 직접 판정은 [집계](evidence/verification-summary.json), 실행 조건은 [PERFORMANCE](PERFORMANCE.md), 후속 범위는 [DEPENDENCIES](DEPENDENCIES.md), 원격 반영은 [GITHUB_HANDOFF](GITHUB_HANDOFF.md)를 따른다. 과거 A/B/E/K 및 예비 파일의 검사 숫자를 이번 직접 실행에 합산하지 않는다.
