# HELI_B — 로터·격납고·갑판 이동·다중 경로

현재 원본은 [Aegis_SIM_v48_WIP_HELI_B.html](../../../Aegis_SIM_v48_WIP_HELI_B.html)이다. 자함 DDG-119의 두 기와 기존 120초 준비/50m MSL 질점 운동을 유지하면서 사용자 피드백을 반영했다.

## 조작

AIR **왼쪽은 조작 버튼**, **오른쪽은 항공기 목록**이다. 목록은 행 높이를 늘려 채우지 않고 여백을 남기며 자체 스크롤을 갖는다. 모바일에서도 두 열을 유지한다.

- H1/H2 선택 → 지도를 여러 번 누르면 순서대로 경로점이 추가된다. 최대32개다. 비행 중에도 남은 경로 뒤에 추가할 수 있다.
- **UNDO**는 아직 지나지 않은 마지막 경로점을 제거한다. 이미 지난 점은 되돌리지 않는다.
- **경로 지우기**는 기존 경로를 해제하고 감속·호버한다. 새 위치로 즉시 재지향하려면 지운 뒤 새 점을 찍는다.
- 중간 점은 20m 통과 반경을 사용하며 다음 코너에 맞춰 감속한다. 마지막 점에서는 정지·호버한다.
- **함선 따라가기**는 기존 경로를 해제하고 모함 뒤100m·측방400m, 약410m 거리의 이동하는 위치를 따라간다. H1은 좌현, H2는 우현이다. 함선 속도와 선회에 따른 위치 변화도 사용한다. 순간 이동하지 않는다.
- **출격 요청/출격 대기 취소**는 기존 단일 갑판 대기열을 사용한다.
- AIR **헬기 보기/모함 보기**, 3D **CONTROLS → CAMERA → H1/H2 헬기 추적**으로 시점을 바꾼다. 미출격 기체의 추적 버튼은 비활성이다.

속도/고도/침로/다음 목표 거리·근사 ETA/현재 단계 남은 시간과 경로 진행 수를 표시한다. ETA는 다음 목표의 근사이며 전체 경로·출격 준비 시간을 예측하지 않는다. 콘솔 `window.__HELO__.snapshot()`은 복제 상태를 반환한다. 기존 `WAYPOINT` 명령은 한 점으로 대체하는 API로 유지하고 지도는 `ROUTE_APPEND`를 사용한다. `UNDO_ROUTE`, `CLEAR_ROUTE`, `FOLLOW_SHIP`도 제공한다. x/y는 SI 미터, z는50m로 고정한다.

## 로터 수정

HELI_A는 기울어진 원본 축 대신 전역 Y/Z축으로 회전했고, 비균일 source 축척 아래에서 로터를 돌렸다. 꼬리의 고정 기어박스12821도 함께 회전했다.

- source hub12754/12823의 기하를 측정하여 중심과 평면 법선을 얻는다. 법선은 inverse transpose로 기체 미터 좌표에 옮긴다.
- 회전 그룹을 비균일 normalizer 밖의 **metric body space**에 둔다. 메인 hub/블레이드, 꼬리 hub12823/블레이드12825·12828·12831·12834만 실제 축으로 회전한다. gearbox12821과 지지부는 정지한다.
- 회전각에 따라 축 방향 높이·회전 반경이 달라지지 않는다. 기존 꼬리/블레이드 전개는 source hinge 변환을 유지한다.
- authored blur 면 여러 개를 겹쳐 돌리는 대신 같은 축에 맞춘 두 개의 공유 ring을 사용한다. 고 RPM에서 블레이드를 부드럽게 감춘다.
- 두 기의77개 source geometry와12개 source material 공유 및 LOD를 유지한다. 별도 texture/전체 GLB를 추가하지 않았다.

측정값은 `rig.json`의 `rotors`이며 source 등록/시각 조정이므로 **SIM_TUNED**다. [measure_rotors.py](measure_rotors.py)로 압축 source에서 재현한다. 일반 SH-60 외형을 MH-60R 상세 외장 검증으로 표현하지 않는다. 원본 [SB-129 / CC BY4.0](../A/ATTRIBUTION.md) attribution과 자산은 보존한다.

## 문과 갑판 경로

문을 열어도 남았던 HULL_1 등의 외판 면이 원인이었다. 모델 생성 시 두 출입구 범위에서만 HULL0..7/HANGAR/기존 door panel의 겹치는 후면을 분리한다. 기존 내부와 나머지 외판을 유지하며 피격 job이 참조 중인 geometry를 출격 때 교체하지 않는다.

`HELO_FACILITY_A`는 실제 source C5의 별도 항공 hardpoint 등록값이다. legacy coarse ShipProfile 지점을 live renderer에서 역으로 읽지 않는다. 아래 위치/경로는 **SIM_TUNED**다.

- 초기 로터 기준점 x=-40.75m, y=±5.43m: 두 기 모두 기존보다 바깥쪽0.4m, 앞쪽 벽에 여유를 두어 x도 조정했다.
- 첫2.4초는 문 폭에 맞춰 정렬한다. 접힌 기체가 좌우 비대칭이므로 문 중심에서0.367m를 보정한다.
- 이어 곧게 끌려 나오며, 로터 기준점이 x=-56.5m까지 이동해 꼬리도 벽을 벗어난 뒤 cubic 경로로 턴한다. 기수는 경로 접선에 맞추며 끝에서는 정렬한다.
- 정지 로터 기준점 x=-65m, y=0: 기존 -61.3m보다3.7m 뒤다. 꼬리/로터 전개 뒤 벽과 여유가 있다.

실제 source folded triangle와 양쪽401개 경로 pose를 검사했다. 문 측면 최소 여유 약0.37m, 상부 약0.29m이며 바퀴 접지 높이를 포함해 문/바닥 침범은 없다. 낮은 기체·바퀴는 갑판 폭8.5m 이내다. 실제 fixed-step에서 저장한 양쪽21개 pose도 동일한 경로와 일치한다. 이 검사는 전투용 헬기 충돌/피격 구현을 의미하지 않는다.

## 운동·저장 계약

기존140kt/8.4m/s PUBLIC_SPEC 사용자 제원, 기본120kt/운용 상하3.5m/s/가속1.5·감속2m/s²/최대 bank30°/저속 yaw15°/s를 유지한다. 새 조정값은 named SIM_TUNED 상수다.

목표가 크게 바뀌면 선회를 즉시 시작하면서 속도를 제한된 감속률로 줄인다. 30° bank 한계 안에서 속도가 내려가며 선회 반경도 줄어든다. 경로 코너의 접근 속도에도 같은 규칙을 적용한다. 새 목표/UNDO/함선 따라가기 명령은 현재 위치·속도·기수를 덮지 않는다. 예시 fixture의 첫30초 최소 속도는 A61.73→B34.10m/s였으며 같은30° 한계의 최소 반경 추정은673→205m였다. 전반적인 성능 배율이나 실제 항공 공력값으로 표현하지 않는다.

`AEGIS_HELO_SAVE_B1`/`AEGIS_HELO_OPERATIONS_B1`은 route/index/navigationMode/localYaw/hold/follow 목표를 저장한다. 실제 HELI_A 비행 저장을 명시적으로 확장하며 위치·속도·기수를 보존한다. A의 이미 도착한 목표는 hold로 옮기고, 갑판 단계에는 다음 fixed tick부터 B 위치를 적용한다. 잘못된 legacy 숫자/Boolean이나 route/null/index를 preflight 전에 live 상태에 쓰지 않는다.

ShipRuntime.aviation은 재고·문·대기열을, world.helicopters는 위치·운동을 소유한다. 모든 운동은 기존60Hz fixed tick이며 3D/카메라는 read-only다. 기존8.5t 질량 proxy를 재사용한다. 센서/IFF/truth→sensor/targetPool/offboard, 무장, 연료, 로터 공력, 회수, 고도 UI는 이번에 연결하지 않았다.

## 검증·재현

최종 [verification-summary.json](evidence/verification-summary.json)의 **264/264 PASS / 11 suites**를 따른다. packing/syntax/scope56, 운동35, 기본 runtime44, 확장27, UI30, native17, 실제 A 저장10, 배속5, 삼각형 간섭8, source 축 재측정2, A/B 양함종 idle/8Kh32 AUTO/피격 비교30이다. 기존 A198이나 PERF_F1817을 새 결과에 더하지 않았다.

native는 실제 Three/SwiftShader이고 mobile은390×844 touch/viewport 에뮬레이션이다. 실제 휴대폰 FPS를 측정한 결과가 아니다. clock fixture는 시작 RAF만 제어하며 원본 bytes를 바꾸지 않고 전체 fixed-step 경로에서 두 기/경로/함선 추종/선회를1/8/16/64배속으로 비교한다. native reset은 동일한 read-only epoch/fittings 동기화를 명시적으로 실행한다. Source 계측과 간섭 보고서는 게임 bytes의 정확한 rebuild 및 actual runtime pose로 연결한다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
pip install -r docs/helicopter/C/requirements.txt
python -m playwright install chromium
python docs/helicopter/C/build.py archive/v48/WIP_HELI_A/Aegis_SIM_v48_WIP_HELI_A.html /tmp/Aegis_SIM_v48_WIP_HELI_B.html
python docs/helicopter/C/run_suite.py static Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-static
python docs/helicopter/C/run_suite.py motion Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-motion
python docs/helicopter/C/run_suite.py runtime Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-runtime
python docs/helicopter/C/run_suite.py extensions Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-extensions
python docs/helicopter/C/run_suite.py ui Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-ui
python docs/helicopter/C/run_suite.py native Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-native
python docs/helicopter/C/run_suite.py legacy Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-legacy
python docs/helicopter/C/run_suite.py clock Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-clock
python docs/helicopter/C/run_suite.py baseline Aegis_SIM_v48_WIP_HELI_B.html /tmp/heli-baseline
python docs/helicopter/C/verify_clearance.py /tmp/heli-extensions/extensions.json /tmp/heli-clearance
python docs/helicopter/C/measure_rotors.py /tmp/heli-rig
sha256sum -c SHA256SUMS_v48_WIP_HELI_B.txt
sha256sum -c docs/helicopter/C/REPOSITORY_SUPPORT.sha256
```

필요하면 `AEGIS_CHROMIUM_EXECUTABLE`을 지정한다. Node parser는 기존 F lock을 사용한다. `.main.js`/manifest는 builder의 임시 재현 출력이며 배포 HTML을 대신하지 않는다. 새 수동 workflow를 준비했으며 Actions는 dispatch하지 않았다. A 네 파일은 같은 bytes/blob으로 archive했고 stable/이전 증거·source 자산을 유지한다. HTML은16,037,621bytes, A 대비 **1,828bytes 증가(+0.0114%)**다.
