# AEGIS 현실형 함정 방위 시뮬레이터

단일 HTML/JavaScript 기반의 함정 방공 시뮬레이터 프로젝트다. 센서 관측, 트랙 관리, 교전 권한, 함대공 미사일, CIWS, 전자전, 손상·침수와 표시 전용 3D 장면을 한 실행 파일에서 다룬다.

## 현재 기준

- 구현 기준: A3 V37
- 최신 작업본: `Aegis_SIM_v37.1_WIP01.html`
- 현재 변경: 3D 화면의 AN/SPQ-9B 및 AN/SPS-73 독립 스윕 시각화
- 다음 핵심 단계: CIWS Closure B1

WIP 파일은 구현 또는 검증 중인 작업본이다. 정식 기준으로 승격하려면 프로젝트 지침의 정적 검사, 내장 셀프테스트, 결정적 런타임 회귀와 실제 브라우저 검사를 통과해야 한다.

## 파일

- `Aegis_SIM_v37.1_WIP01.html`: 현재 시뮬레이터 작업본
- `AEGIS_PLAN_STATUS_v37.1_WIP01.md`: 구현·검증 상태와 잔여 작업
- `AEGIS_PROJECT_INSTRUCTIONS.md`: 버전, 구조, 검증 및 인계 규칙

## 실행

정적 웹 서버에서 HTML을 제공하는 방식을 권장한다.

```bash
python3 -m http.server 8000
```

그다음 `http://localhost:8000/Aegis_SIM_v37.1_WIP01.html`을 연다. 3D 장면은 WebGL과 Three.js 로딩이 가능한 브라우저가 필요하다.

## Git 작업 방식

1. `main`은 마지막으로 검증된 기준을 유지한다.
2. 기능별 작업 브랜치를 만든다. 예: `wip/ciws-b1`.
3. HTML과 상태 문서의 버전 토큰을 동일하게 유지한다.
4. 검사 결과와 실행하지 못한 검사를 상태 문서에 기록한다.
5. 검증 후 Pull Request로 `main`에 병합한다.

세부 규칙은 `AEGIS_PROJECT_INSTRUCTIONS.md`를 따른다.
