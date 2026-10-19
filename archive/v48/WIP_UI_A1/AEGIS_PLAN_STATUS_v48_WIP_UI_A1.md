# AEGIS v48 WIP UI_A1 상태

기준 UI_A `30428d679ab0ecf724b3e6e007a94ebc3587f386` / 브랜치 `ui-a1`.

**구현·검수 완료: 456/456 assertions /4 suites PASS, 페이지 오류0.**

- `Aegis_SIM_v48_WIP_UI_A1.html`: **18,029,844 bytes**, UI_A 대비 **+6,522 bytes**.
- SHA-256 `fd7079e9154e8778f7f5a340e6102c8843930b9865d4dc1135714c4847cdc3b8`.
- [보고·스크린샷](docs/ui/A1/REPORT.md), [검증 색인](docs/ui/A1/evidence/verification-summary.json), [재현·조작](docs/ui/A1/README.md).

## 변경

모바일 상태 바를 세로42.84px·가로24px(기본100%)로 압축했다. 재고를 생략하지 않고 함 정보/재고·명령 묶음을 줄 단위로 배치한다. 창 목록/추가는 작은 아이콘이다. 창10px 글자·작은 기본 크기·28px 제목줄을 사용하며 누른 창 전면화·제목줄 이동·겹침·resize와 겹침 순서 저장을 지원한다. 모바일 자동 스냅은 해제하고 명시 고정과 PC 도크를 유지한다. FIRE/LOCK 등의 40px 보호 크기와 기존 핸들러를 유지한다.

EMCON 칩은 기존 native 버튼을 직접 호출하며 창을 열지 않는다. 교전 칩은 위쪽에 수동/반자동/자동을 표시하고 기존 canonical 함수로 한 번 선택한다. 팝업만 열면 모드는 바뀌지 않는다. 바깥 탭/Escape로 닫는다. 배치schema2는 예전 배치를 새 프리셋으로 시작하며 UI 크기 설정과 게임 저장은 유지한다.

## 검증

DDG/CG ×6 화면×3배율36조합에서 재고 잘림·가로 스크롤·id 중복0,2D 중심 오차0px다. 실제 겹침·탭 전면화·drag·resize·최대화 복원·저장 복원,30회 크기 변경 뒤 제목줄 포함,모드/EMCON native 동작·입력 격리와 모바일3D 중심을 확인했다. 원래 DOM 노드는 연결되어 있다.

정적46건으로14 records SHA/문법/스코프와 main의 UI shell 밖 byte-exact를 확인했다. 기존 탭별 native 조작의 상태와2D/3D 위젯 실제 발사를 비교했다.120초/7200틱 및 pause/resume의1,764,132-byte 상태 SHA `085812f497d54b66feb69e8bd15a53f0fe93e4199c95fdb4cc405b75518b6587` 일치. 이전UI_A1144건 전체 재실행으로 합산하지 않는다.

## 보존·게시·한계

UI_A HTML·상태·SHA·workflow 네 파일을 `archive/v48/WIP_UI_A/`로 같은 bytes/blob 이동했다. 원본 전체를 `ui-a1`에 직접 게시하고 원격 전체를 다시 읽어 확인한다. `docs/ui/A1/remote-publication.json`을 따른다. 수동 workflow만 준비하고 Actions dispatch/main·기존 브랜치 병합/새 PR은 하지 않는다.

UI 확대 설정에서는 바 높이가 늘어난다. 작은 일반 글자와21px 바 버튼은 사용자 압축 요청에 따른 변경이다. 실기기 GPU/FPS·OS 회전 드라이버는 미측정이며 헤드리스DPR2.8125/소프트웨어WebGL 범위다. HUD/SPY·손상/침수 창 편입,ARM 분리,실제 지도PIP는UI_B에 남긴다.
