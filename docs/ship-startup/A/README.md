# 출항 전 함선 선택·초기화 공통화

기존 WIP16B를 기준으로, profile 선택을 모든 함선 runtime과 subsystem 생성보다 먼저 확정한다. 선택 뒤 기존 builder 실행 순서로 자함을 한 번 생성하고, 장비 편성을 마친 뒤 출항한다. 현재 등록된 운용 함선은 DDG-119 한 척이다.

`WIP_STARTUP_A`는 번호 미확정인 기능명 작업 토큰이다. 정식 v48이나 v48.1 승격이 아니다. 사용자 업로드용 branch는 `ship-startup-ddg-regression`, 기준은 `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`이다.

## 구현 계약

- `SELECTING → INITIALIZING → PREPARING → DEPARTED`. 선택 전 runtime/월드/센서/무장 생성과 물리 실행을 시작하지 않는다. C55 loader는 main의 비동기 초기화 promise가 완료된 뒤에만 ready를 선언한다.
- `SHIP_PROFILE_REGISTRY`에서 선택지를 만든다. 알 수 없는 ID, prototype 속성 이름, 초기화 이후 재선택을 거부한다. 공개 catalog와 startup snapshot은 detached 값이다.
- `createPlayerShipSession(profile)`은 불변 profile로 runtime, engagement, 독립 ships Map과 world를 만든다. entity ID는 hull identity에서 유도하며 DDG-119의 기존 `SHIP_DDG119_OWN`을 보존한다. 기존 canonical 소유자·compatibility 참조는 선택된 객체에 한 번 결속한다.
- 피해/침수·환경·구획·승조원·질량·동역학과 함포/VLS/close-in은 출항 전에 생성·결속을 확인한다. 기존에 첫 tick까지 지연되던 동역학도 여기서 확정한다.
- VLS 재고는 profile의 section별 rows/cols/cells/defaultLoadout으로 생성하며 capacity 오류를 거부한다. DDG-119의 32+64셀과 기존 기본 탄종 순서는 같다.
- 재시작은 기존 subsystem lifecycle을 사용하며 선택된 profile의 초기 heading과 Phalanx/SeaRAM 탄수를 읽는다. 출항 확정 loadout과 canonical 참조를 유지한다. 함선 전환·재선택은 페이지의 새 세션에서 수행한다.
- `shipStartupState()`와 `runShipStartupIsolationAudit()`를 기존 진단 API에 추가한다. 두 독립 foundation runtime/world와 별도 identity·heading·소형 VLS fixture를 검사한다. fixture는 운용 registry에 등록하지 않고 전투 RNG/profile/활성 ships Map을 바꾸지 않는다.

현재 common화는 선택과 최초 생성 경계에 해당한다. 벙커힐용 profile·geometry·builder와 두 번째 완전 운용 함선은 다음 단계다. detached foundation 생성 검사를 다함 전투 지원으로 해석하지 않는다.

## 재현 및 검사

```sh
base=archive/v48/WIP16B/Aegis_SIM_v48_WIP16B.html
mkdir -p artifacts/ship-startup
python docs/ship-startup/A/build_startup.py "$base" /tmp/Aegis_SIM_v48_WIP_STARTUP_A.html
cmp Aegis_SIM_v48_WIP_STARTUP_A.html /tmp/Aegis_SIM_v48_WIP_STARTUP_A.html
python docs/ship-startup/A/tests/package.py Aegis_SIM_v48_WIP_STARTUP_A.html "$base"
python docs/ship-startup/A/tests/startup.py Aegis_SIM_v48_WIP_STARTUP_A.html "$base" artifacts/ship-startup/lifecycle
python docs/wip16/A/tests/runtime16a.py "$base" > artifacts/ship-startup/baseline-runtime.json
python docs/ship-startup/A/tests/runtime.py Aegis_SIM_v48_WIP_STARTUP_A.html > artifacts/ship-startup/runtime.json
python docs/ship-startup/A/tests/compare_runtime.py artifacts/ship-startup/baseline-runtime.json artifacts/ship-startup/runtime.json artifacts/ship-startup/comparison.json
python docs/ship-startup/A/tests/render.py Aegis_SIM_v48_WIP_STARTUP_A.html artifacts/ship-startup/renderer
```

archive 이동 전 검사에는 `base=Aegis_SIM_v48_WIP16B.html`을 사용한다. Playwright Chromium이 설치되어 있어야 한다. 시스템 Chromium을 사용하는 환경에서는 `AEGIS_CHROMIUM_EXECUTABLE`을 지정할 수 있다. 패킹은 고정 gzip 헤더로 byte-identical 재구성한다.

기존 runtime 13조건과 same-seed 전체 결과 반복 조건은 그대로 유지한다. 추가 원본/후보 비교는 integer·구조·사건 값의 일치를 요구하고 float 진단값에 absolute `1e-9` / relative `1e-12` tolerance를 적용한다. 로컬 비교에서 aggregate·발사·명중·교전 결과가 정확히 같았고 상세 float 10개만 최대 `3.871347686867921e-13` 차이를 보였다.

## 로컬 판정과 후속 반영

2026-10-03 로컬 Chromium: package 34/34, startup 15/15, 기존 DDG runtime 14/14, 3D geometry/recovery 13/13 PASS. core/page errors 0. 3D는 실제 mesh cut·구멍 중심 ray clear·geometry 복원·138 구획/160 portal/70 장비·310 승조원·VLS 결속·부정 fixture·표시 read-only를 검사했다. 침수 fixed-step fixture는 1×/8×/16×/64×에서 동일하다. 이는 해당 fixture의 결정성 결과이며 모든 실제 방위 시나리오의 성능 검사가 아니다.

사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 parent·크기·Git blob을 확인했고 검증본과 exact 일치한다. 전용 신규 workflow와 일반 smoke의 3D 입력은 실제 업로드를 재구성본과 `cmp`한 뒤 검사한다. startup 선택은 검사 harness가 UI 버튼으로 진행한다. 원격 CI 결과는 지원 반영 후 기록한다. main 병합·기존 PR #41 변경·승격·release/tag는 수행하지 않는다.

프로젝트 지침 7.1대로 사용자 HTML 업로드·원격 exact 확인을 마쳤다. 이전 WIP16B의 HTML/상태/체크섬은 동일 Git blob으로 `archive/v48/WIP16B/`에 이동한다. 옛 체크섬은 당시 경로·문서의 역사 증거이므로 새 문서에 적용하지 않는다. 최신 검사에는 새 체크섬을 사용한다. 로컬 raw evidence를 압축 보존한 경우 `.json.gz`는 gzip 해제 후 원본 JSON bytes를 그대로 얻을 수 있다.
