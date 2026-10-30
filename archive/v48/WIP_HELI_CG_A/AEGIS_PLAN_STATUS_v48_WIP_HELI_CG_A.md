# AEGIS v48 WIP HELI_CG_A — 공용 헬기 운용·CG 단일 격납고 출입구

구현·정적·런타임·브라우저 회귀 완료. HELI_F1 `bd0e88a` 위 `helicopter-cg-a`, 소스 커밋 `0aafde4`. [사용자 단일 출구 교정](docs/helicopter/I/CONFLICTS.md), [운용·재현](docs/helicopter/I/README.md), [검증](docs/helicopter/I/evidence/verification-summary.json), [독립 원격 확인](docs/helicopter/I/remote-publication.json).

- 원본 **16,078,336bytes**, F1 대비 **2,614bytes 증가**. 새 모델/텍스처 자산을 넣지 않았다.
- HTML SHA-256 `c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3`.
- packed13 SHA-256 `2a4f032459ebd5e54e7221e5c9d68f8ff1037ebd76f183967fb9ea6650973ebc`. 그 외13 packed 자산은 원본과 같다.
- CG는 **하나의 공용 격납고·하나의 넓은 출입구·두 주기 위치**, DDG는 기존 좌우 독립 문을 사용한다.

## 구현

불변 `HELO_FACILITY_PROFILES_I` 등록으로 함종별 문/주기/이동/갑판 좌표를 분리하고, 동일한 상태기계·비행·AIR UI·센서·IFF·Hawklink·카메라·MH-60R 자산을 사용한다. CG 기존 질량 프로파일의 두 헬기 노드를 재사용하므로 중복 질량을 더하지 않는다. 고정60Hz/SI/소유 runtime/read-only 렌더 원칙을 유지한다.

CG 원본 모델의 후벽 x≈−30.413m와9.8m 갑판을 기준으로 겹친 외판·문 부속의 개구 부분을 잘라내고 공용 내부 바닥·천장·외측/전방 벽·작업 캐비닛·등·유도선을 만든다. 중앙 분리벽은 없다. 단일 문은2패널 상부 접힘 시각 표현이며, 정확한 치수/기구와 내부 배치는 **SIM_TUNED**다. [미 해군 2022년 사진](https://www.dvidshub.net/image/7548497/bunker-hill-helicopter-operations)은 공용 출입구와 접힌 MH-60R의 시각 근거이며 상세 구동 도면이 아니다. 기존 피해·침수 구획 전체를 새로 저작하지 않았다.

두 기 중 먼저 선택한 기체가10초 문 개방→20초 이동→30초 전개→45초 시동→10초 확인→5초 부상, 총120초 준비를 수행한다. 우현 주기 기체는 내부에서 통과 차선으로 정렬해 우현 관제 구조물을 피하고, 문을 완전히 지난 뒤 후방 공용 패드에서 멈춘다. 첫 기체가 실제 갑판을 비운 뒤에 다음 기체 준비가 시작된다. 문 index와 기체 slot을 분리하여 공중의 첫 기체가 두 번째 기체의 공용 문을 닫지 않게 했다.

문을 열 때 미요청 주기 기체도 내부에 보이지만 시뮬의 출격/센서 상태를 렌더가 바꾸지 않는다. 정적 개구/내부 생성은 clean source build 시 한 번, 문 애니메이션은 행렬만 갱신한다. DDG 기존16슬랫 독립 셔터/숫자 좌표/전체 출격 경로는 보존한다.

DDG는 기존 E1 저장 계약을 유지한다. CG는 단일 door 배열을 가진 `AEGIS_HELO_SAVE_I1` / `AEGIS_HELO_OPERATIONS_I1`을 사용한다. 이전 CG 빈 항공 재고는 두 기의 격납 상태로만 마이그레이션하고 비행 상태를 추측하지 않는다. 잘못된 문 수는 import 전 원자적으로 거부하며 snapshot은 detached다.

## 검증

동일 최종 HTML **206/206 PASS /8 suites**, 브라우저 오류0. static41 / native70 / 기하7 / 실제 OTH9 / 3D16 / UI14 / IFF7 / 기존 전투42. 과거 단계의 검사 수는 합산하지 않았다.

- CG H1 우선/H2 우선과 DDG를 각각260초 실행해120초 이탈·갑판 점유·두 기50m 비행·전개/시동·문 복구를 확인했다. DDG의 모든 샘플 기체/문/갑판/센서 상태는 F1과 정확히 같다. CG는1/8/16/64×의15360fixedticks에서 상태와 RNG가 정확히 같다.
- 원본 접힌 기체19,081삼각형과 구조물·fittings·새 내부·단일 문을 두 경로101지점씩, 총202포즈에서 검사했다. 정상 정적 형상의 삼각형 충돌0, 대기 기체와 AABB 겹침0. 모든 피격 변형 형상까지 검사한 것은 아니다.
- 실제 WebGL에서 하나의 개구와2패널 문/공용 내부/두 주기 기체/전개·시동·이탈을 확인했다. 후벽 개구3×3 ray가 모두 통과하며 문 움직임 중 static geometry UUID가 유지된다. DDG는 기존 두 문을 사용한다.
- 1100×800 및390×1000 AIR 포인터 조작, 출격/대기 취소·두 기 목록·고도300m·PERI·단일 문을 확인했다. 제거한 AIR 보기 버튼은 재등장하지 않는다.
- CG 기체의 IFF ON 측정 응답→FRIEND→기존 AUTO/CIWS 교전 보호, OFF 후 보존 시간 만료→UNKNOWN, 다시 ON→응답 기반 FRIEND를 확인했다. truth 기반 아군 예외는 추가하지 않는다.
- **실제로 CG에서 출격한 H1**이300m PERI로40km 표적을 탐지하고 원래 모함 Hawklink로 전달했다. 자함 EMCON으로 현지 레이더 관측이 없는 순수 OFFBOARD 트랙에 운용자가 HOSTILE/OPERATOR_ONLY를 부여해 기존 수동 관문으로 실제 하푼을 발사했다. F1의 수신기 진단 재생과 다르다. `updatesAfterRelease:false`, 공유 트랙 자동발사 금지, EMCON 독립 Hawklink 정책은 같다. REPORT_QUEUE_FULL0.
- DDG/CG 대기·8Kh32 AUTO·손상6조건에서 기존 물리/피해/배치/RNG/observer/offboard 상태가 F1과 같다. 소프트웨어 Chromium/SwiftShader 검증이며 실제 기기 FPS 개선 수치를 주장하지 않는다.

## 전달·후속 범위

F1 네 파일은 archive/v48/WIP_HELI_F1에 동일 bytes/blob으로 보존한다. stable v48 및 과거 A–H 소스·증거는 변경하지 않는다. 원본 전체를 작업 브랜치에 직접 업로드하고 GitHub tree/decoded full blob으로 독립 대조한다. 수동 workflow만 제공하며 Actions dispatch/main·이전 브랜치 병합/새 PR을 만들지 않는다.

이번 범위는 출항 시 플레이어가 선택한 DDG/CG의 항공 운용이다. 적/아군 타함 항공 AI, 착함/회수, 연료, 헬기 무장, 새 피해 구획, ISAR/Link16 확장은 후속이다.
