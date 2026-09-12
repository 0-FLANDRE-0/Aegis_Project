# AEGIS 이전 작업본

루트에는 현재 최신 작업본만 두며, 아래 파일은 내용 변경 없이 버전별 폴더에 보존한다. `archive/` 내부 파일은 최신 소스 자동 선택 및 GitHub Actions 실행 대상이 아니다.

| 버전 | 상태 | 주요 변경 | 검증 상태 | 후속 버전 |
| --- | --- | --- | --- | --- |
| v37.1 WIP01 | 보관 | SPQ-9B·SPS-73 독립 3D 스윕 시각화 | JavaScript 문법, 전체 스크립트 초기화, 내장 자기검사, 토글 독립성 및 WebGL 비의존 렌더 객체 생성 통과; 실제 3D 육안검사 잔여 | v37.1 WIP02 |
| v37.1 WIP02 | 보관 | CIWS Closure B1의 익명 관측 트랙 기반 위협 평가·cueing 및 로컬 RF 경계 분리 | JavaScript 문법 및 CIWS 판단부 truth 접근 정적 검사 통과; 자동 교전권한과 cue 시 로컬 탐지 조건 결함이 WIP03 검토에서 확인됨 | v37.1 WIP03 |
| v37.1 WIP03 | 보관 | CIWS 후보의 A3 AUTO 권한 및 cue 시 로컬 탐지 필수화 | 정적 검사 통과; Actions run 34681951551의 비공개 fixture 호출 실패와 획득 후 권한/소실 재검증 누락을 WIP04에서 수정 | v37.1 WIP04 |
| v37.1 WIP04 | 보관 | 명시적 B1 진단 API와 획득 후 권한 재검증 | Actions run 34682645360에서 자기검사 fixture 방향, SeaRAM 선수 사각, 지속되지 않는 보호/재획득 fixture 및 이미지 timeout 결함 확인 | v37.1 WIP05 |

## 보관 경로

- `v37.1/WIP01/Aegis_SIM_v37.1_WIP01.html`
- `v37.1/WIP01/AEGIS_PLAN_STATUS_v37.1_WIP01.md`
- `v37.1/WIP02/Aegis_SIM_v37.1_WIP02.html`
- `v37.1/WIP02/AEGIS_PLAN_STATUS_v37.1_WIP02.md`
- `v37.1/WIP03/Aegis_SIM_v37.1_WIP03.html`
- `v37.1/WIP03/AEGIS_PLAN_STATUS_v37.1_WIP03.md`

- `v37.1/WIP04/Aegis_SIM_v37.1_WIP04.html`
- `v37.1/WIP04/AEGIS_PLAN_STATUS_v37.1_WIP04.md`
