# HELI_A — DDG-119 2기 출격·고정 고도 이동

사용자가 확정한 이번 단계는 **제원 제한을 둔 질점 운동 + 상태기계**다. 자함 DDG-119의 H1(좌현 격납고), H2(우현 격납고)를 운용한다. CG-52와 아군함의 항공 운용은 후속 작업이며 기존 FLEET 조작을 바꾸지 않는다.

## 조작

1. DDG-119로 새로 출항한다.
2. AIR 탭에서 H1/H2를 선택한다. 지도에서 이동할 위치를 누른다. 출격 전에 지정해도 된다.
3. **이륙 요청**을 누른다. 두 기를 요청하면 단일 갑판 대기열을 사용한다. 기다리는 기체는 **대기열 취소**가 가능하다.
4. **헬기 보기**로 선택 기체를 3D에서 따라가거나 **모함 보기**로 돌아간다.
5. 비행 중 지도에서 새 위치를 누르면 현재 위치·속도·방향을 유지하며 재지향한다. 도착하면 50m MSL에서 호버한다.

AIR에는 단계, 대기열, 대기속도/대지속도(kt), 고도, 기수 침로, 목표까지 거리와 추정 ETA, 시간제 단계의 남은 시간이 표시된다. ETA는 현재 대지속도 또는 기본 순항을 이용한 근사값이며 갑판 준비 시간과 선회 시간을 예측하지 않는다. 지도 아이콘·목표 마커·연결선은 소유 항공기의 운용 표시이며 레이더 트랙이 아니다.

콘솔: `window.__HELO__.snapshot()`은 복제된 상태와 출처 태그 상수를 반환한다. UI와 같은 명시적 명령은 `window.__HELO__.command(id, 'LAUNCH')`, `'CANCEL_QUEUE'`, `'WAYPOINT', {x, y}`로 사용할 수 있다. x/y는 **SI 미터**다. altitude/recovery 명령은 지원하지 않는다.

## 단계와 좌표

| 상태 | 표시 동작 | 시간 |
|---|---|---:|
| HANGAR_OPEN | 접힌 기체 표시, 해당 문 개방 | 10s |
| TRAVERSE | 엔진을 끈 채 갑판으로 이동·정렬 | 20s |
| SPREAD | 꼬리 먼저, 이어 로터 블레이드 전개 | 30s |
| START | 엔진 순차 시동, 로터 회전수 상승 | 45s |
| PRE_LAUNCH_CHECK | 시동 안정화 | 10s |
| LIFT_HOVER | 갑판 위 +5m로 수직 부상 | 5s |
| DEPART | 좌현 측방 이탈, 가속·50m까지 상승 | 운동으로 결정 |
| TRANSIT | 선회·감속하며 목표로 이동 | 운동으로 결정 |
| ARRIVED_HOVER | 50m에서 위치 유지 | 고정 시간 없음 |

시간제 준비는 120초이며 상수는 `SIM_TUNED`다. 기체는 LIFT_HOVER 마지막 틱까지 함 로컬 좌표에 붙어 있다. DEPART 전환 때 월드 SI로 분리하고 함 속도벡터를 상속한다. 두 번째 기체는 첫 기체의 로터 원판과 여유 폭이 갑판 경계를 벗어난 뒤에 HANGAR_OPEN을 시작한다. 별도 SPOTTING 상태 대신 확정된 TRAVERSE가 갑판 이동·정렬을 맡는다. RECOVERY는 enum 자리만 있으며 전환·착함은 구현하지 않았다.

## 운동과 상태 소유권

`motion.js`는 순수 질점 운동, `runtime.js`는 항공 운용 상태·대기열·저장 계약, `ui.js`는 명시적 명령과 표시, `render.js`는 읽기 전용 Three 어댑터다. 기존 SIM_FIXED_DT(1/60) 안에서 한 번만 적분한다. 임의 렌더 프레임이나 배속에 따라 운동을 적분하지 않는다.

| 항목 | 값 | 태그·근거 |
|---|---:|---|
| 최대 순항 | 140kt | PUBLIC_SPEC — 사용자가 이번 명세에서 제공한 MH-60R 공개 제원 |
| 최대 상승률 | 8.4m/s | PUBLIC_SPEC — 같은 사용자 제원 |
| 기본 이동 | 120kt | SIM_TUNED |
| 운용 상승·하강 | 3.5m/s | SIM_TUNED |
| 전진 가속·감속 | 1.5 / 2.0m/s² | SIM_TUNED |
| 최대 뱅크 | 30° | SIM_TUNED |
| 저속 기수 선회 | 30kt 미만, 15°/s | SIM_TUNED |
| 비행 고도 | 50m MSL | SIM_TUNED |

전진 선회는 `g·tan(bank)/airspeed`로 제한한다. 저속에서 기수와 이동 방향은 독립이다. 정지거리 `v²/(2·decel)`를 사용해 감속하고 오버슈트하면 재접근한다. 바람은 `maritimeEnvironmentSnapshotWip13A3().wind`에서 읽으며 대지속도=대기속도+풍속벡터다. 대기속도에 최대 제한을 적용한다. 가감속 피치와 선회 뱅크는 1차 지연 표시값이며 물리 판정에 사용하지 않는다. 모든 조정값과 시간은 이름 붙인 상수 및 태그로 공개한다.

ShipRuntime.aviation은 재고·격납고·문·대기열을, ENGAGEMENT_RUNTIME.world.entities.helicopters는 기체 위치·운동을 소유한다. 기존 함정의 8.5t AIRCRAFT 고정 질량 노드는 준비 중 기체 위치를 따라가고 월드 분리 뒤 자함 질량에서 빠진다. 같은 질량을 추가하지 않는다. 미출격 상태에서는 기존 PERF_F 질량과 정상 전투 경로를 보존한다.

작전 저장의 `AEGIS_HELO_SAVE_A1`은 2기, 준비 단계/틱, 문/대기열/갑판 소유권, 비행 위치·속도·목표·자세를 복원한다. 전체 preflight 통과 전에는 live 상태를 쓰지 않는다. 기존 DDG 저장의 빈 항공 재고는 명시적으로 격납 2기로 migration한다. 숫자/Boolean 타입 혼용, 중복 기체 ID, 잘못된 갑판 소유권, 시간·속도·고도 한계를 거부한다. reset 시 기체 상태와 렌더 lease를 정리한다.

## 모델·문·용량

[기존 A 추출물](../A/README.md)의 223,419bytes gzip을 HTML에 한 번 내장한다. 두 기는 geometry/material을 공유하고 먼 거리에서는 단순 LOD를 쓴다. 출처 [CC BY 4.0 / SB-129](../A/ATTRIBUTION.md)는 유지한다. 원본은 SH-60 공통 외형이며 MH-60R 세부 외장 형식을 확정한 자료로 취급하지 않는다. **MH-60R는 이번 운동 프로파일의 이름**이다.

source 정적 격납·전개·비행 부품을 공유하며 source 변환/힌지를 기반으로 꼬리·블레이드를 움직인다. 로터 회전/블러는 시각용이다. source C5 DDG 격납고의 기존 내부를 사용하고 뒷벽의 문 두 곳만 모델 생성 시 분리한다. shutters는 롤업 애니메이션을 사용한다. 문 분리를 피격 job이 geometry를 소유한 뒤에 수행하지 않는다.

`HELO_FACILITY_A`의 실제 C5 위치(door 약 x=-48.224m, bay y=±5.03m, deck x=-61.3m, z=3.18m)는 source geometry를 오프라인으로 재어 등록한 **SIM_TUNED** 값이다. runtime이 live 렌더러에서 좌표를 얻지 않는다. 시각 축척 16.36m rotor/5.13m 높이도 SIM_TUNED다. 기존 coarse profile의 항공 지점을 실제 렌더 위치로 오인하지 않는다.

완성 HTML 16,035,793bytes: PERF_F 대비 +326,494bytes (+2.07835%). 전체 원본 GLB·텍스처를 게임에 넣지 않는다.

## 이번 단계 경계

항공기를 truth→sensor, targetPool, configureOffboardSourceC에 연결하지 않았다. 자함/타함의 레이더·IFF·자동교전·관측 공유와 독립이다. 센서, 무장, 연료 소모, 로터 공력·동역학, 지면효과, 고도 UI, 착함·회수는 다음 단계다. 헬기 손상/충돌 전투 모델 역시 이번 질점 운동 범위에 포함하지 않는다.

## 재현과 검증

기준은 [보존된 PERF_F](../../../archive/v48/WIP_PERF_F/Aegis_SIM_v48_WIP_PERF_F.html), SHA `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5`다. packed13만 변경하고 기존 packed0..12와 embedded 선박/무장 모델 bytes는 그대로다. builder는 pinned 기준과 A 자산/로더 및 B의 4개 JS/rig.json을 사용한다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
pip install -r docs/helicopter/B/requirements.txt
python -m playwright install chromium
python docs/helicopter/B/build.py archive/v48/WIP_PERF_F/Aegis_SIM_v48_WIP_PERF_F.html /tmp/Aegis_SIM_v48_WIP_HELI_A.html
python docs/helicopter/B/run_suite.py static Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-static
python docs/helicopter/B/run_suite.py motion Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-motion
python docs/helicopter/B/run_suite.py runtime Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-runtime
python docs/helicopter/B/run_suite.py ui Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-ui
python docs/helicopter/B/run_suite.py native Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-native
python docs/helicopter/B/run_suite.py clock Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-clock
python docs/helicopter/B/run_suite.py baseline Aegis_SIM_v48_WIP_HELI_A.html /tmp/heli-baseline
sha256sum -c SHA256SUMS_v48_WIP_HELI_A.txt
sha256sum -c docs/helicopter/B/REPOSITORY_SUPPORT.sha256
```

`AEGIS_CHROMIUM_EXECUTABLE`을 Playwright Chromium 경로로 지정할 수 있다. Node parser는 기존 F package-lock의 acorn 8.19.0 / eslint-scope 9.1.2를 사용한다. builder가 쓰는 `.main.js`와 manifest는 재현용 임시 출력이며 게임 파일이 아니다.

최종 집계는 [verification-summary.json](evidence/verification-summary.json)을 따른다. 정적 packing/syntax/scope, 순수 운동, 실제 원본 브라우저 출격/저장, desktop/mobile AIR, native WebGL 문/기체/렌더 정리, 1/8/16/64배속, PERF_F↔HELI_A 양함종 idle/Kh-32 AUTO/피격 6조건을 검증한다. clock fixture만 초기 RAF를 정지해 출항 전 틱 차이를 없애며 원본 HTML을 수정하지 않고 실제 fixed-step 전체 경로를 실행한다. 나머지 브라우저 UI/native 검사는 정상 RAF를 사용한다. native reset 정리는 같은 read-only epoch/fittings 동기화를 명시적으로 호출해 검증하며 GPU 부하에 따른 다음 RAF 대기 시간을 100ms 같은 합격 기준으로 사용하지 않는다.

native는 Chromium SwiftShader, mobile은 touch/viewport 에뮬레이션이다. 실제 휴대폰 GPU FPS·장시간 운용 시험으로 표현하지 않는다. PERF_F의 과거 1817검사는 당시 기록이고 HELI_A의 새 집계에 더하지 않는다. 수동 workflow는 준비했으며 Actions는 실행하지 않았다.
