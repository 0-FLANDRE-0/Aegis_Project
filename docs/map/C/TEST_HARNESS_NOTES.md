# 검수 준비와 증거 구분

- 제품 HTML에 fixture를 넣지 않는다. `browser_tools.instrument`가 테스트 중에만 gzip main에 관측/네트워크 fixture를 주입하고 로더의 payload hash를 다시 계산한다. 제품 파일 SHA는 별도로 원문에서 기록한다.
- 기존 도메인 420, UI 88, MAP_B 91, 경고 23, 추가 13의 판정 수를 유지한다. MAP_B M9만 새 구조에 맞게 태그 캔버스 경계, 실제 40px hit box와 EMCON 12px 간격으로 이관했다. 네이티브 발사/비행 결과를 대체하는 구현은 만들지 않았다.
- 신규 UI 검사의 일부 준비 클릭은 실제 client 좌표에 pointer 이벤트를 보낸다. 소프트웨어 WebGL에서 Playwright의 두 동일 프레임 actionability 대기가 길어질 때만 이 방법을 사용하며, DOM `click()`로 발사를 강제하거나 비활성 관문을 우회하지 않는다. 기존 91/23/13 검사는 원래 클릭과 발사 경로를 유지했다.
- 트랙 소실 검사는 모델을 갱신한 뒤 소실 표시가 정착한 상태를 읽는다. 초기에는 소프트웨어 GPU가 지연된 전이 프레임을 읽어 false였으며, 신호/신관/소실 판정 임계값은 바꾸지 않았다.
- 하푼 계획 중 통제 금지 검사에는 원래 필요한 AIM 모드 전환 + route toggle을 포함한다. NAV 상태의 `routeDraft.editing`만 켜는 것은 원래 `harpoonRouteEditingE()` 정의상 편집 중이 아니다.
- 추종은 각 조건에서 10초 이상, 실제 모든 rAF 표본의 태그 기준점과 Canvas2D arc를 비교한다. 별도 최소 FPS를 합격 조건으로 만들지 않는다. 초기 임의의 20프레임 조건은 요청에 없는 성능 기준이어서 제거했으며, 최종 원시 데이터에 프레임 수/관찰 시간/실제 sim 진행을 모두 기록한다.
- initial 폴더는 납품 합격 판정에 사용하지 않는 개발/준비 증거다. 최종 acceptance는 각 결과의 HTML SHA가 납품 SHA와 같은지 엄격히 검사한다.
- 회귀 승인값 6건의 entries는 MAP_B/CLEAN_B와 동일하다. UI hash guard만 최종 코어에 연결했다.
