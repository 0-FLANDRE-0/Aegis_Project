# MAP_E 시험 준비 이관

게임 DOM에 제거한 ARM 노드를 다시 붙이지 않는다. 새 E 검수는 legacy adapter 없이 실제 DOM/포인터로 실행한다.

| 시험 | 준비 이관 | 유지하는 검사 |
|---|---|---|
| 기존 ARM tab/LOCK/AUTO TGT/FIRE/하푼/EMCON 버튼 | test-only API가 분리된 **원래 노드의 원래 리스너**를 호출. `[data-tab=ARM]`은 같은 modeAimBtn 리스너. product에는 test API 없음 | 원래 식별·EMCON·발사·권한·RNG·상태 검사를 유지 |
| EMCON passiveLabel | 분리된 원래 버튼의 textContent. 시각 UI는 사용자 결정으로 유보 | 방사 없는 지정 분기/라벨 문자열을 유지. E1은 해당 DOM 부재를 별도 검사 |
| EMCON UI labelFits | 원래 내부 라벨 문자열 + 새 EMCON 칩의 실제 화면 경계 | 제거된 버튼의 가상 경계를 만들지 않음 |
| MAP_C UI 135의 직접 EMCON 토글 준비 | EMCON 칩 → 새 레이더 버튼 → 팝오버 닫기 | 기존 차단 판정·박스 불변 검사 그대로 |
| MAP_D native 84의 AUTO/SEMI 거부 사례 | preview test helper에 mode 인자를 명시해 원래 generic native gate와 비교 | generic automatic surface 발사 금지 검사는 유지. 새 지도 MANUAL 권한은 E5에서 별도 확인 |
| H3 currentStrictSchema | H3 시절 검사 상수만 현재 H4로 갱신 | 원본은 D/E 모두 이 항목만 실패(기존 게임의 현재 스키마 H4). 나머지 193개 검사와 모든 invalid-save/권한 검사 byte 동일. 원본 증거 ew-h3-original에 보존 |
| 기존 VP/MAP A~D 이관 | 기존 패널 탐색·viewport 변환·retired quick widget 준비 이관 그대로 | 기존 검사 개수/판정 유지 |

최초 ISAR/EMCON native 실행은 삭제된 `[data-tab=ARM]`을 기다려 준비에서 시간 초과했다. 선택자 어댑터와 내부 라벨 읽기를 보완한 뒤 같은 검사 전체를 재실행했다. 최초 로그는 `evidence/development/domain-first-*`, 재실행은 `domain-final/*-rerun.log` 및 `reruns.json`에 보존한다.

폰 폭 보정은 MAP_E_UI 블록만 변경했다. 표시 보정 전 완료한 native/도메인 결과의 실제 실행 HTML SHA는 바꾸지 않는다. `presentation-equivalence.json`은 해당 SHA와 최종 HTML 사이 **새 표시 블록 밖 전체 JS byte 동일**, 모든 named symbol 동일을 검증한다. 이 범위의 native 증거만 재사용하고, 입력·레이아웃 UI 검사는 최종 HTML에서 다시 실행한다.
