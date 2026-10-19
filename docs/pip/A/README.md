# PIP_A — 조작 가능한 공통 2D 전술 지도

기준은 MAP_A `c1297b6b0c6d7ceb600517aea3d5a4d0aa62594f`, 원본 SHA-256 `68c13d352c3e80ab8bae1e08138ee42284c426f7fb7cce24e9d64941b34362b5`이다. 상세 요구와 두 차례 사용자 보정(최소 반경 0.1km, 후보 전부 보임 우선)을 적용했다. 언급된 구상서 Markdown은 제공된 파일에서 발견되지 않아 지시서를 기준으로 작업했다.

- [결과·수치·스크린샷](REPORT.md)
- [그리기 부작용·데이터 출처 감사](RENDER_AUDIT.md)
- [최종 검증 집계](evidence/verification-summary.json)
- [원격 전체 원본 검증](remote-publication.json)

## 사용

3D를 열면 기존 CIC 창이 실제 전술 지도가 된다. 제목줄로 창을 옮기고 지도 안에서 팬한다. `− / + / 중심 / ⇄`는 지도 옆의 전용 공간에 있다. 중심은 자함 추적을 복원한다. 지도 탭·길게 누르기·우클릭·펜 버튼은 MAP_A와 같은 정보/통제/항로점/하푼 계획 함수를 사용한다. SYS에서 갱신을 2/4/10회로 바꾼다.

겹친 객체는 후보 목록에서 선택한다. [확대]는 심볼 여백 8px을 두고 후보 전부가 보이는 가장 작은 반경을 구한다. 그래도 40px 미만이면 [주화면에서 보기]로 같은 후보를 2D 주화면에 맞춘다. 목록과 통제·계획은 유지한다.

## 소스와 재현

`build.py`는 핀 고정 원본의 main block 13과 DOM 표시 CSS만 바꾼다. 앞 13개 패킹 블록과 함정 자산은 동일하다. `legacy-drawing/`는 원본 함수 경계를 보존한 재현용 입력이다. `adapt_map.py`는 역사 MAP_A를 수정하지 않고 새 입력 어댑터를 생성한다. `render.js`의 공통 준비와 픽셀 그리기를 분리하고, `pip.js`는 표시 전용 창 상태·스케줄을 소유한다.

```bash
python docs/pip/A/adapt_map.py
python docs/pip/A/build.py archive/v48/WIP_MAP_A/Aegis_SIM_v48_WIP_MAP_A.html /tmp/PIP_A.html
cmp /tmp/PIP_A.html Aegis_SIM_v48_WIP_PIP_A.html
python docs/pip/A/run_suite.py archive/v48/WIP_MAP_A/Aegis_SIM_v48_WIP_MAP_A.html Aegis_SIM_v48_WIP_PIP_A.html artifacts/pip-a
```

Chromium/Playwright와 기존 `docs/performance/F` Node 의존성이 필요하다. 헤드리스 Chromium의 소켓 생성이 가능한 실행 환경에서 실행한다. 역사 테스트 파일은 그대로 사용하며 `run_map.py`는 화면 캡처 대기만 CDP 캡처로 대체한다. 회귀 조건이나 게임 함수를 대체하지 않는다. MAP_A의 정적 48건은 핀/승인 패치가 달라져 PIP_A용 동일 48개 항목으로 재검사한다. 나머지 994개 런타임 회귀는 역사 검사 그대로 실행한다.

PiP 설정은 `aegis.pip.a.view.1` schema 1에만 저장한다. 손상·차단 시 40km/추적 ON/4Hz를 사용한다. 게임 저장 스키마에 포함하지 않는다. 실제 단말 FPS·펜 하드웨어는 이 헤드리스 결과로 주장하지 않는다.
