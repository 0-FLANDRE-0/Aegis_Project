# HELI_C — 출구·착륙장치 수정과 AIR 고도 조작

현재 원본은 [Aegis_SIM_v48_WIP_HELI_C.html](../../../Aegis_SIM_v48_WIP_HELI_C.html)이다. HELI_B head `b4052e7113c8808bf89be43a21cba2d078bdb22c`에서 항공 모듈만 수정했다. 두 기의 120초 준비, SI/fixed60Hz 질점 운동, 읽기 전용 3D와 기존 공통 압축 모델을 유지한다.

## 조작

- AIR 왼쪽 조작/오른쪽 기체 목록은 유지하고 패널 높이를 줄였다. 목록은 여백과 자체 스크롤을 갖는다.
- H1/H2를 선택한 뒤 **출격 요청**을 누르면 같은 버튼이 **출격 대기 취소**로 바뀐다. 취소는 준비가 시작되기 전 대기열에 있는 기체에만 적용한다. 이미 준비/비행 중이면 버튼이 비활성이다.
- AIR의 **헬기 보기/모함 보기만 삭제**했다. 기존 3D CONTROLS → CAMERA → H1/H2 헬기 추적은 유지한다.
- **고도 …m 설정**은 별도 입력창을 연다. 수면 기준 미터로 직접 입력하거나 대표 고도를 선택한 뒤 적용한다. 기체마다 독립적이며 초기값은50m다. 범위는25–3,962.4m다. 최대값은 미 해군이 공개한 MH-60R ceiling13,000ft이며, MSL 설정 상한으로 적용하는 것은 게임 추상화다. [제원 근거](altitude-spec.md)를 따른다.
- 격납/대기/준비 중에도 출격 고도를 미리 설정할 수 있다. 비행 중에는 현재 위치·속도에서 제한된 상승·하강률로 이동한다. 대표값 선택만으로 적용하지 않으며 닫기는 설정을 바꾸지 않는다.
- 지도 다중 경로점/UNDO/경로 지우기/함선 따라가기와 선회 감속은 유지한다. 경로와 함선 추종은 기체의 설정 고도를 사용한다.

## 수정·저장 경계

기수 간섭은 출구에 놓인 source HULL_1의 작은 계단·난간과 경사진 비행갑판을 반영하지 않은 지상 높이에서 재현됐다. 계단·난간48개 삼각형만 좌현 가장자리로3.5m 옮기고 다른 외판/내부를 보존했다. 출입구 하단과 셔터 하단은 실제 floor2.997m로 맞추고, 벽 기울기 기준점3.18m는 별도로 보존해 낮은 뒷바퀴도 문턱에 닿지 않게 했다. 지상 높이와 자세는 실제 갑판 경사에 맞춰 시뮬레이션에서 정한다. 격납 위치는 접힌 원본의 비대칭과 내부 구조물 때문에 좌현−5.68m/우현+5.2m다. 먼저5m 뒤로 이동한 뒤 문에 맞춰 정렬하고, 꼬리가 벽을 벗어난 뒤 곡선으로 헬리패드에 정지한다. 부상5초 동안 갑판 기울기에서 수평으로 부드럽게 전환한다. source 등록/이동값은 SIM_TUNED다.

꼬리 바퀴는 원본 pose에 완성형12704와 압축형12708/12715가 겹쳐 들어 있었다. 완성형 하나를 유지하고 중복 바퀴를 숨긴다. 지상/비행용 상부 연결부12712/12719는 서로 배타적으로 표시한다. 단순히 동등한 지상/비행 부품을 교환하는 것으로는 해결되지 않는 원인이었다.

정확한 재현과 삼각형/실제 native 검사 결과는 `evidence/clearance/`와 `evidence/model/model.json`을 따른다. 전체 헬기·함정 충돌 구현은 이번 범위가 아니다. 원본 자산을 다시 내장하거나 전체 함정 GLB를 추가하지 않았다. generic SH-60 외형과 [SB-129/CC BY4.0 attribution](../A/ATTRIBUTION.md)은 그대로다.

고도 명령은 `__HELO__.command(id,'SET_ALTITUDE',{altitudeM:...})`다. `__HELO__.snapshot()`의 기체별 `targetAltitudeM`과 현재 `altitudeM`을 확인할 수 있다. 숫자·범위 검사는 명령과 저장 codec에서 수행한다. 구형 A/B 저장은50m 목표로 명시 migration하며 위치·속도·기수를 유지한다. 갑판 준비 중인 구형 저장은 다음 fixed tick부터 수정된 지상 배치·경로를 적용한다. 잘못된 저장은 live 상태를 쓰기 전에 거부한다.

LIFT_HOVER는 갑판+5m/5초이고 DEPART 이후 월드 운동에서 설정 고도로 상승한다. 고도 변경은 렌더가 아니라 기존 fixed-step에서 적분한다. 상승·하강률3.5m/s는 SIM_TUNED 운용값이며 기존 최대상승률8.4m/s 한계를 넘지 않는다. 회전익 공력/연료/회수/센서/IFF/무장/오프보드 관측은 이번에 추가하지 않았다.

## 검증·재현

최종 원본 16,041,537bytes, B 대비3,916bytes 증가. **248/248 PASS /6 suites**다. 최종 원본의 SHA, 검사 수와 조건은 [verification-summary.json](evidence/verification-summary.json)을 따른다. 실제 Chromium/SwiftShader와 desktop/touch viewport를 사용하며 실제 휴대폰 또는 hardware FPS 검증을 뜻하지 않는다. HELI_B의 과거264검사를 새 검사 수에 더하지 않는다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
pip install -r docs/helicopter/D/requirements.txt
python -m playwright install chromium
python docs/helicopter/D/build.py archive/v48/WIP_HELI_B/Aegis_SIM_v48_WIP_HELI_B.html /tmp/Aegis_SIM_v48_WIP_HELI_C.html
python docs/helicopter/D/run_suite.py static Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-static
python docs/helicopter/D/run_suite.py ui Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-ui
python docs/helicopter/D/run_suite.py altitude Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-altitude
python docs/helicopter/D/run_suite.py model Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-model
python docs/helicopter/D/run_suite.py clearance Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-clearance
python docs/helicopter/D/run_suite.py regression Aegis_SIM_v48_WIP_HELI_C.html /tmp/heli-c-regression
```

수동 workflow는 `.github/workflows/helicopter-c.yml`이며 Actions를 dispatch하지 않는다. HELI_B HTML/상태/SHA/workflow 네 파일은 `archive/v48/WIP_HELI_B/`에 같은 bytes/blob으로 보존한다. 이전 source/evidence와 stable v48은 변경하지 않는다. §7.1에 따라 전체 HTML을 직접 업로드하고 독립 GitHub blob readback을 남긴다. main/선행 branch 병합이나 새 PR은 실행하지 않는다.
