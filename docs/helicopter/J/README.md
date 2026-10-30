# HELI_CG_B — CG 좌현 원본 슬라이딩 문·후방 형상 복원

HELI_CG_A `3ce88eb` 위 `helicopter-cg-b`. [교정 근거·구현 전 충돌 보고](CONFLICTS.md).

A의 넓은 개구/상부 접힘 문은 실제 형상을 잘못 판단한 구현이었다. 이 버전은 원본 자산에서 좌현 문과 붙은 해치·창을 그대로 분리해 측방 이동한다. 우현 벽/세로 패널·상부 창/플랫폼·갑판 관제 구조물을 보존하고 원래 좁은 좌현 출입구만 뚫는다. 새 가로 판이나 상부 접힘 패널을 만들지 않는다. 정적 사진의 시각 근거와 사용자 요구에 따른 문 구동 표현을 구분하며, 원본 모델 치수/이동량/내부는 SIM_TUNED다.

두 기는 같은 선수·선미 위치에 평행하게 격납한다. AIR에서 H1을 출격시키고 H2를 대기시키면, 원래120초 준비와 갑판 이탈 뒤 H2가 빈 좌현 통로로 정렬해 같은 문으로 나온다. H2만 먼저 누르면 `좌현 H1이 출입 통로를 비울 때까지 대기`가 표시된다. H1을 무단 출격시키거나 H2가 H1/벽을 통과하게 하지 않는다. 대기는 같은 버튼으로 취소할 수 있다. DDG는 이 제한을 받지 않는다. H2의20초 이동은 횡이동6.4초/문 밖 이동8.6초/패드 선회5초로 배분하며, 함 기준 경로 최대 속도는 약2.55m/s다(SIM_TUNED).

같은 비행/경로/고도/추종/로터/센서/IFF/APS 모드/Hawklink/OTH 시스템을 사용한다. 새 모델·텍스처 자산, 타함 항공 AI, 착함·연료·무장은 추가하지 않는다. Hawklink의 EMCON 독립과 모함 전용, 하푼의 수동 발사 및 발사 후 무DL은 그대로다.

CG 저장은 J1이다. 이전 I1을 먼저 기존 계약대로 검증하고, 공중 기체는 그대로 보존한다. 진행 중인 지상 준비와 기존 대기 명령만 새 주기 위치의 대기로 되돌리며 문을 닫고 갑판 점유를 해제한다. DDG 저장은 기존 E1이다. 이전 F1의 빈 CG 재고도 두 격납 기체로 migration한다.

검증은 [최종 요약](evidence/verification-summary.json)을 따른다. 새로 추가한 핵심은 원본 F1과 닫힌 후방75개 ray 비교, 문 열림 중 우현/외곽 보존, 원본 문1456삼각형 유지·측방 이동만 수행, 실제 출구 ray,202포즈 삼각형 간섭, H2 통로 대기/취소·두 기 출격·DDG 전체 상태 동일성·저장 migration이다. A의 잘못된 가정을 재사용해 실제 형상 검증을 대체하지 않는다.

```sh
python docs/helicopter/J/build.py archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html /tmp/HELI_CG_B.html
python docs/helicopter/J/verify_static.py archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/static
python docs/helicopter/J/verify_native.py archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/native
python docs/helicopter/J/verify_clearance.py Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/clearance
python docs/helicopter/J/verify_visual.py Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/visual
python docs/helicopter/J/verify_ui.py Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/ui
python docs/helicopter/I/verify_live_oth.py Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/live-oth
python docs/helicopter/I/verify_iff.py Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/iff
python docs/helicopter/F/verify_regression.py archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html Aegis_SIM_v48_WIP_HELI_CG_B.html artifacts/regression --baseline-only
```

Python/Playwright/numpy는 F/requirements.txt, Node AST는 docs/performance/F/package-lock.json. Chromium/SwiftShader는 소프트웨어 검증이며 실제 기기 FPS 수치가 아니다. 정상 정적 형상만 간섭 검사하며 기존 피해·침수 구획 전체는 재작성하지 않는다.

원본 전체를 새 브랜치에 직접 올리고 독립 GitHub full blob 대조를 기록한다. 과거 A–I 소스·증거/HTML은 보존한다. main·기존 브랜치 병합, Actions dispatch, 새 PR은 하지 않는다.
