# HELI_CG_A — DDG/CG 공용 항공 운용과 CG 단일 격납고 출입구

HELI_F1 `bd0e88a` 위 `helicopter-cg-a`. [구현 전 대조·사용자 단일 출구 교정](CONFLICTS.md)을 따른다.

출항 때 **CG-52** 또는 **DDG-119**를 선택한 뒤 AIR에서 기존처럼 기체를 선택해 출격한다. CG는 두 주기 위치가 있는 공용 격납고와 **하나의 넓은 문**, DDG는 기존 좌우 독립 문을 사용한다. CG 문은2패널 상부 접힘식 시각 표현, DDG 문은 기존16슬랫 롤셔터 표현이다. 문 치수와 정확한 메커니즘은 SIM_TUNED이며 공식 구동 도면의 복제라고 주장하지 않는다.

공용 상태기계가 문 개방10초 → 이동20초 → 꼬리/블레이드 전개30초 → 시동45초 → 확인10초 → 부상5초를 수행한다. 두 기 중 어느 것을 먼저 요청해도 다른 기체와 겹치지 않는다. CG의 우현 주기 기체는 안쪽에서 중앙 쪽 통과 차선으로 정렬해 갑판 우측 관제 구조물을 피한다. 기체가 문을 완전히 통과한 뒤 패드로 부드럽게 정렬하며 앞선 기체가 갑판을 비우기 전에는 다음 준비를 시작하지 않는다.

고도/경로/UNDO/함선 추종/IFF/APS 모드/Hawklink/CAMERA/기체·로터·랜딩기어는 기존 공용 구현이다. CG 문을 열면 요청하지 않은 주기 기체도 격납고 안에 표시하지만, 그 기체의 `visible`/출격·센서 시뮬 상태를 렌더에서 변경하지 않는다. 격납·갑판 기체를 별도 RF 표적으로 추가하지 않는다. 같은 MH-60R 원본 자산과 geometry lease를 두 기가 공유한다.

## 프로파일·소유권

`HELO_FACILITY_PROFILES_I`는 함정 profile ID별 불변 항공 시설 등록이다. 런타임의 `aviation.facilities.flightOperations`에서 등록을 확인할 수 있다. DDG 좌표값과 경로는 보존한다. CG는 원본 메쉬의 약9.8m 갑판과−30.413m 후벽을 기준으로 한다. `window.__HELO__.snapshot()`의 detached `facility`, `doors`에 선택 함종의 등록과 실제 문 수가 나온다.

기체 slot과 door index를 분리한다. CG의 `doors` 길이는1, DDG는2다. 문이 다시 열릴 때 앞선 공중 기체의 닫기 명령이 덮지 않도록 현재 지상 운용 기체가 문을 점유한다. 물리·이동은 SIM_FIXED_DT에서만 처리하며 렌더는 detached 표시 상태만 읽는다.

CG 저장은 `AEGIS_HELO_SAVE_I1` / `AEGIS_HELO_OPERATIONS_I1`, DDG는 기존 E1이다. 과거 CG 빈 재고 저장을 import하면 두 기가 격납 상태로 생기며 비행·센서 이력을 추측 복원하지 않는다. 문 수가 틀린 import는 원자적으로 거부한다. 기존 CG 질량 프로파일에는 두 기의8500kg 노드가 이미 있으므로 기체 질량을 중복 추가하지 않는다.

## 모델 처리와 한계

기존 CG 후벽의 겹친 외판과 문 앞 손잡이/보강재를 등록 개구 범위에서만 잘라낸다. 구조물·fittings의 위치/정점 속성을 보존하고 바깥 부분과 갑판 관제 구조물은 유지한다. 바닥·천장·외측/전방 벽·작업 캐비닛·유도선·등을 절차적으로 추가한다. 중앙 분리벽이나 두 번째 출입구는 만들지 않는다.

절단과 내부 생성은 clean source build 시 한 번 수행하고 프레임에서는 문 행렬만 갱신한다. 기존 damage 작업이 보유한 geometry를 개방 때마다 교체하지 않는다. 고정 geometry UUID가 문 개방/기체 전개 동안 유지됨을 확인했다. 원래 CG의 피해·침수용 구획/메타데이터 전체는 재저작하지 않았고, 새 내부를 실제 선내 피해 구획으로 검증했다고 주장하지 않는다. 원본 MH-60R·CG/DDG 자산은 그대로다.

CG에서 실제로 출격한 헬기의 APS→Hawklink→CG OTH 수동 하푼 발사를 확인했다. 이 검사는 F1 때의 수신기 재생이 아니다. 공유 트랙 자동발사나 하푼 비행 DL은 추가하지 않는다. 비행 연료·착함/회수·적/아군 타함 항공 AI·헬기 무장은 다음 범위다.

## 검증·재현

최종 수·원본 SHA는 `evidence/verification-summary.json`을 따른다. 기하 검사는 원본 source 및 새 내부/문 메쉬와 접힌 헬기19,081개 삼각형을 대조한다. 양쪽 주기 위치의101지점씩과 반대 기체 AABB를 검사한다. 이는 정상 정적 기하 검사이며 피격 변형 이후의 모든 모양이나 회전익 공력 검사라고 표현하지 않는다.

Python/Playwright/numpy는 `../F/requirements.txt`, Node AST는 `../../performance/F/package-lock.json`을 사용한다. Chromium/SwiftShader는 소프트웨어 검증이고 실제 휴대폰/하드웨어 FPS 수치는 아니다.

```sh
python docs/helicopter/I/build.py archive/v48/WIP_HELI_F1/Aegis_SIM_v48_WIP_HELI_F1.html /tmp/HELI_CG_A.html
python docs/helicopter/I/verify_static.py archive/v48/WIP_HELI_F1/Aegis_SIM_v48_WIP_HELI_F1.html Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/static
python docs/helicopter/I/verify_native.py archive/v48/WIP_HELI_F1/Aegis_SIM_v48_WIP_HELI_F1.html Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/native
python docs/helicopter/I/verify_clearance.py Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/clearance
python docs/helicopter/I/verify_visual.py Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/visual
python docs/helicopter/I/verify_ui.py Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/ui
python docs/helicopter/I/verify_live_oth.py Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/live-oth
python docs/helicopter/I/verify_iff.py Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/iff
python docs/helicopter/F/verify_regression.py archive/v48/WIP_HELI_F1/Aegis_SIM_v48_WIP_HELI_F1.html Aegis_SIM_v48_WIP_HELI_CG_A.html artifacts/regression --baseline-only
```

과거 A–H 소스·증거와 stable v48은 보존한다. 원본 전체 직접 업로드와 독립 GitHub blob readback을 수행하며 Actions dispatch/main·이전 브랜치 병합/새 PR은 하지 않는다.
