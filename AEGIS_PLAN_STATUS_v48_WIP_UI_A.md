# AEGIS v48 WIP UI_A 상태

기준 VP_A `3afd0fc04d0dc707205f5532f9016cd32b10eb56` / 브랜치 `ui-a`.

**구현·검수 완료: 1144/1144 assertions, 24 suites PASS, 페이지 오류0.**

- 실행 파일 `Aegis_SIM_v48_WIP_UI_A.html`: **18,023,322 bytes**, VP_A 대비 **+20,368 bytes**.
- SHA-256 `a4b6825df6c28eb8f0747f73ec9469c90f277f96eb23e55be67298a6a1cab8e4`.
- [A–L 검수·스크린샷](docs/ui/A/REPORT.md), [검증 색인](docs/ui/A/evidence/verification-summary.json), [재현](docs/ui/A/README.md), [이동 컨트롤](docs/ui/A/MOVED_CONTROLS.tsv).

## 변경

AEGIS_VIEWPORT 위 공용 하단 상태 바, NAV/ARM/FLEET/AIR/SYS/소형 CIC 창, 고정 교전 위젯, 3D 진방위 테이프를 구현했다. 기존 컨트롤은 같은 DOM 노드를 이동했으며 127개 노드 연결·중복 id 0을 확인했다. 제목줄 이동, 모서리 크기 조절, 고정·해제, 최대화·복원, 접기, 불투명도, 전면화, 화면 밖 방지와 별도 배치 저장을 제공한다. AIR의 좌측 조작·우측 목록을 유지했다.

설치 무장 재고는 공용 exporter에서 최대 4Hz로 읽는다. 기존 배속 버튼은 이동하고 pause만 추가했다. DOM 전용 UI 크기 85/100/115/130%와 가로 고정을 별도 localStorage에 저장한다. 전체화면은 첫 버튼 동작에만 자동 요청하고 수동 해제 뒤 재요청하지 않는다. 고정 창과 바만 보이는 영역을 줄인다.

## 검증

- DDG/CG × 9크기 × 3배율 = 54조합, UI 497건·85/130% 3D 보충 17건 PASS. 재고 잘림·가로 스크롤 0.
- 2D 중심 최대 0.000000px, 지도 탭 최대 0.00002786px, 스냅 시 3D 중심 최대 0.00000000px.
- 창·바·위젯 위 드래그/휠/핀치/탭으로 지도·표적·경로 변경 0. 30회 크기 변경·회전 후 제목줄 포함.
- native 컨트롤 전후 비교: {'NAV': 11, 'ARM': 29, 'FLEET': 21, 'AIR': 13, 'DEBUG': 10}. ARM/FLEET 전체 버튼 포함. 공용 위젯 2D·3D 각각 실제 1발로 VP_A와 동일.
- 같은 준비 뒤 120초/7,200 native ticks, 1,764,132-byte 상태 SHA `085812f497d54b66feb69e8bd15a53f0fe93e4199c95fdb4cc405b75518b6587`. VP_A/UI_A/pause-resume/resize 혼합 일치.
- 기존 420건 + VP_A 표시·정적 148건 + 신규 UI 576건. 기존 567에 포함된 420을 중복 합산하지 않았다.

ShipRuntime·센서·판정·발사 권한·게임 저장 codec·모델은 보존했다. 원래 3,198개 함수 중 표시 경로 6개 본문만 바뀌었고 packed records 0–12·소브레멘니 assets는 byte-identical이다.

## 한계 / UI_B

100% PC 가로 상태 바는 41px다. 재고 생략·가로 스크롤 없이 최소 조작 크기를 유지하므로 좁은 화면은 2줄을 넘는다(CG 390×844 133px, 384×832 155px). 실폰 GPU/FPS·OS 회전 드라이버는 미측정이다. DPR 2.8125 헤드리스 검증을 실기기 성능으로 취급하지 않는다.

SHIP/손상통제/침수 창 편입, HUD/SPY 창 편입, ARM 분리, 실제 지도 PIP와 좁은 화면 추가 배치는 UI_B에 남긴다. 기존 소형 CIC는 관찰용으로 유지했다. 시뮬·파랑·소브레멘니 기능·provider는 이번 범위에서 변경하지 않았다.

## 보존 / 게시

VP_A HTML·상태·SHA·workflow 네 파일을 `archive/v48/WIP_VP_A/`에 동일 bytes/Git blob으로 보존했다. 전체 HTML·소스·증거·보고서·체크섬을 직접 게시한다. 원격 전체 바이트 대조 기록은 `docs/ui/A/remote-publication.json`을 따른다. 수동 workflow만 제공하며 Actions dispatch/main·기존 브랜치 병합/새 PR은 하지 않는다.
