# AEGIS 현실형 함정 방위 시뮬레이터 — 작업 지침

이 문서는 AEGIS 함정 방위 시뮬레이터를 이어서 개발할 때 사용하는 고정 작업 규칙이다. 대화 기억보다 현재 제공된 최신 HTML, 상태 계획표, 이 문서를 우선 기준으로 삼는다.

## 1. 기준 파일과 버전 규칙

- 시뮬레이터 파일명은 `Aegis_SIM_v버전.html` 형식을 사용한다.
- 큰 기능 단계나 개발 이정표가 완료되면 정수 버전을 올린다.
  - 예: `Aegis_SIM_v37.html` → `Aegis_SIM_v38.html`
- 정식 버전 이후의 작은 기능 추가, 튜닝, 버그 수정이 완료되면 소수점 버전을 올린다.
  - 예: `Aegis_SIM_v38.1.html` → `Aegis_SIM_v38.2.html`
- 아직 구현 또는 검증 중인 파일에는 `WIP`를 사용한다.
  - 예: `Aegis_SIM_v38_WIP01.html`, `Aegis_SIM_v38_WIP02.html`
- WIP 번호는 같은 목표 버전 안에서 작업본이 바뀔 때 증가시킨다. WIP 파일을 검증 없이 정식·소수점 버전으로 취급하지 않는다.
- 작은 작업의 권장 승격 흐름은 `Aegis_SIM_v38_WIP01.html` → `Aegis_SIM_v38_WIP02.html` → `Aegis_SIM_v38.1.html`이다.
- 큰 단계 작업의 권장 승격 흐름은 `Aegis_SIM_v38_WIP01.html` → `Aegis_SIM_v38.html`이다.
- 같은 버전 번호로 내용이 다른 파일을 여러 개 만들지 않는다. 내용이 바뀌면 소수점 또는 WIP 번호를 반드시 증가시킨다.
- 최신 기준 소스는 검증이 끝난 정식·소수점 버전이다. WIP는 사용자가 명시적으로 이어서 작업하라고 한 경우에만 기준 소스로 삼는다.
- `(1)`, `(2)`, `final`, `final_final`, 날짜·시간 문자열을 정식 결과물 파일명에 붙이지 않는다.
- 작업 시작 시 가장 높은 버전의 HTML 하나만 기준 소스로 선택한다. 이전 버전은 회귀 비교와 복구용으로 보존한다.
- 상태 문서는 HTML과 같은 버전 토큰을 사용한다.
  - `Aegis_SIM_v38.1.html` ↔ `AEGIS_PLAN_STATUS_v38.1.md`
  - `Aegis_SIM_v38_WIP02.html` ↔ `AEGIS_PLAN_STATUS_v38_WIP02.md`
- 모델·재질 검사기는 시뮬레이터와 별도 버전으로 관리한다. 필요할 경우 `AEGIS_MODEL_INSPECTOR_vNN.html`을 사용한다.

### 1.1 작업본 보존 규칙

- 루트에는 최신 시뮬레이터 HTML 하나와 그에 대응하는 상태 문서·체크섬 세트만 둔다.
- 새 WIP 또는 정식 버전이 생성되면 직전 버전을 `archive/버전/WIP번호/`로 이동한다.
- 시뮬레이터 HTML, 대응 상태 문서와 체크섬은 반드시 같은 폴더에 보존한다.
- 파일 내용을 변경하는 수정과 파일 내용을 유지한 단순 이동을 구분해 기록한다.
- `archive/` 내부 파일은 최신 소스 자동 선택 및 GitHub Actions 실행 대상에서 제외한다.

## 2. 작업 시작 절차

1. 최신 검증 버전의 `Aegis_SIM_v버전.html`, 대응 상태 문서, 이 지침을 읽는다.
2. 현재 완료 항목, 검증만 남은 항목, 미구현 항목을 구분한다.
3. 이번 작업 범위를 한 시스템 또는 한 문제로 제한한다.
4. 수정 전에 관련 함수, 호출자, 상태 소유자, 진단 API, 셀프테스트 위치를 먼저 찾는다.
5. 기존 정상 동작과 무관한 코드는 건드리지 않는다.
6. 작업 범위와 직접 관계없는 리팩터링은 별도 버전으로 미룬다.

## 3. 시뮬레이션 구조 원칙

### 3.1 Truth 경계

- 실제 적 객체, 실제 위치, 실제 생존 상태는 월드 물리와 센서 반사·관측 합성, 충돌·피해 판정에서만 사용한다.
- 센서 관측 이후의 트랙 연관, 위협 평가, 무기 선택, 자동 교전 판단은 실제 객체 ID나 실제 객체 배열을 직접 읽지 않는다.
- 센서 출력은 익명 plot이어야 한다. plot에 `objectId`, 실제 이름, 실제 도메인, `truthRef`를 실어 트랙 계층으로 넘기지 않는다.
- 진단 코드가 truth와 track을 비교할 수는 있지만 진단 결과가 실시간 교전 판단으로 역유입되면 안 된다.

### 3.2 트랙과 교전 상태

- `classification`, `identity`, `threatStatus`, `engagementAuthority`는 서로 다른 의미와 갱신 주체를 유지한다.
- 분류 신뢰도만으로 적성 식별 또는 자동 교전권한을 부여하지 않는다.
- `UNKNOWN`, `UNASSESSED`, `WITHHELD`, `FRIEND`, `NEUTRAL` 상태에는 자동발사를 허용하지 않는다.
- 아군 무장의 근접신관 작동이나 직접 분해 보고 뒤에는 물리 트랙을 즉시 삭제하지 않고 `KILL_ASSESSMENT`로 두되, 자동 교전권한은 즉시 `WITHHELD`로 바꾼다.
- `DESTROYED`는 truth 생존 플래그가 아니라 아군 무장효과 보고와 후속 센서 무응답으로 확인한다. 효과 보고 뒤 일관된 새 관측이 들어오면 `KILL_ASSESSMENT`나 `DESTROYED`를 해제하고 관측 기반 위협 평가로 복귀한다.
- `DIRECT_BREAKUP`이 확인된 트랙에는 기존 요격탄의 DL·SPY 무기지원·SPG-62 예약/조명을 즉시 해제한다. BDA 중인 트랙은 적색 live-threat 심벌로 표시하지 않으며, `DESTROYED` 확인 뒤 짧은 kill-mark 보존 시간이 끝나면 유령 MEM 심벌을 PPI에서 숨긴다.
- 앞선 `FUZE_DETONATION` 기록을 실제 `DIRECT_BREAKUP`으로 승격할 때는 증거 등급만 바꾸지 말고 effect step/time, 종말 위치·속도, 확인 지연과 return-resolution 상태를 실제 분해 사건으로 함께 갱신한다. 같은 틱의 마지막 센서 측정은 격추 후 귀환으로 취급하지 않으며 effect step보다 엄격히 늦은 coherent measurement만 BDA를 해제할 수 있다.
- 직접 분해 효과와 동일 표적의 중복/coast 파일을 묶을 때는 효과 시각·SI 위치·속도와 관측 track만 사용하는 엄격한 운동학 게이트를 적용한다. 효과보다 늦은 일관 측정은 즉시 BDA를 해제해야 하며, 상관 판단에 truth 생존 상태를 사용하지 않는다.
- 트랙 coast, 재획득, 새 alias 발생 시 운용자 식별과 교전권한을 무조건 복사하지 않는다.
- 다만 기존 파일이 LOST가 되는 첫 평가 프레임에 동일 접촉으로 검증된 대체 alias가 나타나면, 표적 ID를 보유한 SAM·RAM·Phalanx·CIWS cue·SPG-62 live ownership/예약·선택 lock을 원자적으로 대체 ID로 옮겨 유령 지원이나 이중 교전을 남기지 않는다.
- MANUAL, SEMIAUTO, AUTO의 권한 차이는 판단부뿐 아니라 실제 발사 함수에서도 다시 확인한다.

### 3.3 시간·물리·렌더링

- 물리 계산은 고정 시간 간격을 사용한다. 화면 프레임률이 물리 결과를 바꾸면 안 된다.
- 1×, 8×, 16×, 64×에서 같은 seed의 핵심 결과가 허용 오차 안에서 유지돼야 한다.
- 난수는 시뮬레이션 seed와 격리된 결정적 스트림을 사용한다. 진단·화면 효과가 전투 난수 순서를 바꾸면 안 된다.
- 3D 렌더러는 표시 전용이다. 유도, 센서, 충돌, 피해 상태를 3D 프레임에서 적분하지 않는다.
- 장비 손상은 가능하면 단순 ON/OFF 임계값보다 탐색 거리, 오차, 구동 한계, 발사율 등에 연속적으로 반영한다.

### 3.4 프로필·런타임·월드 소유권

- `ShipProfile`은 함종의 불변 설정이고 `ShipRuntime`은 한 함정 인스턴스의 가변 상태다. profile에 전투 중 상태를 역기록하지 않는다.
- 현재 자함의 canonical 가변 상태 소유자는 `ACTIVE_SHIP_RUNTIME`이다. 새 함선 종속 상태를 별도 전역 singleton으로 추가하지 않는다.
- 센서, track manager, 사통, VLS/CIWS, EW, 피해·침수, 질량·동역학, 내부구획, 승조원과 항공 운용 상태는 해당 `ShipRuntime` 아래에서 소유권을 확인할 수 있어야 한다.
- 적 항공기·미사일, 아군 탄체, 표면 접촉, 대응체계, 지형과 시나리오는 함선이 아니라 `ENGAGEMENT_RUNTIME`의 world가 소유한다.
- 기존 전역 이름이 필요하면 canonical 객체를 가리키는 `COMPAT_REQUIRED` 별칭으로만 유지한다. 새 코드는 별칭보다 canonical 이름을 우선 사용한다.
- 동일 개념의 옛/새 경로는 `LIVE_CANONICAL`, `COMPAT_REQUIRED`, `DIAGNOSTIC_ONLY`, `DEAD_LEGACY` 중 하나로 분류한다. 정상 실행에서 어떤 경로가 권위자인지 주석과 진단 계약으로 확인 가능해야 한다.
- `spawnShipRuntime()`은 미결속 runtime 기반만 만들며 다함전 활성화를 의미하지 않는다. 활성 자함은 `destroyShipRuntime()`으로 삭제할 수 없고 일반 호출자가 넘기는 override 옵션도 인정하지 않는다.

### 3.5 수명주기·작전 snapshot·계측

- reset은 수동 전역변수 나열을 UI 콜백에 다시 만들지 않고 subsystem lifecycle 함수로 구성한다.
- 작전모드와 교전모드 사이 상태는 버전이 붙은 `exportOperationalState()` / `importOperationalState()` 계약으로 이동한다.
- snapshot export는 live runtime이나 subsystem snapshot cache를 직접 노출하지 않는 detached JSON 값이어야 한다.
- snapshot import는 입력을 먼저 복제하고 schema/version, profile ID/revision, ship ID, 단위, 항법, 무장, 유체 재고, 피해·침수, 승조원과 항공 상태 전체를 preflight한다. 모든 codec을 통과하기 전에는 reset이나 authoritative 상태 쓰기를 시작하지 않는다.
- validation에 거부된 import는 자함, lifecycle, 월드 entity, track/EW/사통 예약을 포함한 authoritative 상태를 하나도 변경하지 않아야 한다.
- profile revision이 명시 호환 목록에 없으면 추측 복원하지 않고 migration이 필요하다는 오류로 거부한다.
- 센서 plot·track·비행 중 탄체·교전 예약 같은 전투 transient는 작전 snapshot으로 복원하지 않는다.
- 부분 복원 또는 의도적으로 제외한 상태는 snapshot의 `capabilities.deferred`에 명시한다.
- 성능 profiler는 기본 비활성이고 켰을 때만 subsystem별 tick 평균·p95·최댓값과 entity 수를 기록한다.
- profiler 결과 없이 60 Hz fixed tick, 120 Hz 침수/힘 적분, 20 Hz 정수압 quadrature 주기를 낮추지 않는다.

## 4. 구현 방식

1. 문제를 재현하거나 현재 코드에서 원인 경로를 확인한다.
2. 입력 → 상태 갱신 → 판단 → 출력 흐름을 정리한다.
3. 기존 데이터 계약을 유지하면서 가장 작은 변경으로 수정한다.
4. 새 동작에는 진단 스냅샷이나 결정적 fixture를 함께 추가한다.
5. 안전 조건은 추천·판단 함수와 실제 실행 함수 양쪽에 둔다.
6. 임시 진단 UI는 정식 결과물에 남기지 않는다. 재사용할 진단 API와 셀프테스트만 유지한다.
7. 실제로 검증하지 않은 상태를 `완료`라고 기록하지 않는다.

## 5. 필수 검증 순서

검증은 아래 단계를 순서대로 수행한다. 앞 단계가 실패하면 다음 단계로 넘어가지 않는다.

### 5.1 정적 검사

- HTML 내부 JavaScript 전체 문법 검사
- 중복 선언, 정의되지 않은 함수, TDZ, 잘못된 이벤트 ID 검사
- 수정 범위에서 금지된 truth 접근과 실제 객체 기반 트랙 결합 전수 검색
- 신규 UI 요소의 ID, 이벤트 바인딩, 초기 라벨 확인

### 5.2 내장 셀프테스트

- 페이지 시작 시 `window.__CORE_SELFTEST_FAILURES__`가 빈 배열이어야 한다.
- DEBUG 로그에 `CORE SELFTEST PASS`가 있어야 한다.
- 새 기능은 최소한 정상 전이, 차단 전이, 경계값, 상태 복구를 검사한다.

### 5.3 결정적 런타임 회귀

- 고정 seed와 fixture로 수정 전 증상과 수정 후 결과를 비교한다.
- 결과에는 입력 조건, 트랙 상태, 무기 발사 수, 실패 사유를 남긴다.
- 자동 교전 변경은 허가된 트랙의 실제 발사와 금지된 트랙의 발사 0회를 모두 확인한다.
- 센서 변경은 truth 수, plot 수, tentative 수, confirmed 수를 같은 시점에 계측한다.

### 5.4 실제 브라우저 검사

- 로컬 브라우저가 없으면 Vercel 팀 비공개 Preview를 사용한다.
- 페이지 로드, 출항, 핵심 버튼, HUD, DEBUG 로그, 콘솔 오류를 확인한다.
- Vercel에는 팀 인증이 적용된 비공개 Preview만 사용하며 공개 배포로 전환하지 않는다.
- 브라우저를 실제로 실행하지 못했으면 `브라우저 검증 완료`라고 쓰지 않는다. 대신 미실행 이유와 대체 검증 범위를 기록한다.
- WebGL이 없는 검사 환경에서 3D 검증 실패를 시뮬레이션 실패로 혼동하지 않는다. 3D는 WebGL 가능한 환경에서 별도로 확인한다.

### 5.5 속도·상태 회귀

- 대표 시나리오를 1×, 8×, 16×에서 확인한다.
- 64×는 탐지 정확도와 별도로 성능·과부하 회귀로 취급한다.
- 정상 장비와 주요 센서·사통 손상 상태를 비교한다.
- 2D/3D 전환이 시뮬레이션 상태나 전투 결과를 바꾸지 않는지 확인한다.

## 6. 판정 용어

- `구현 완료`: 코드와 정적 검사가 끝난 상태
- `런타임 검사 완료`: 내장 셀프테스트와 결정적 실행 검사가 통과한 상태
- `브라우저 검사 완료`: 실제 브라우저에서 UI·콘솔·시나리오를 확인한 상태
- `완료`: 해당 항목의 계획된 정적·런타임·브라우저 회귀가 모두 통과한 상태
- `검증 잔여`: 구현은 있으나 필수 검증 일부가 남은 상태
- `미완료`: 필요한 운용 경로가 아직 코드에 연결되지 않은 상태

## 7. 작업 종료 및 인계

작업 종료 시 다음을 반드시 남긴다.

1. 새 버전 파일 `Aegis_SIM_v버전.html`
2. 같은 버전 토큰의 상태 문서 `AEGIS_PLAN_STATUS_v버전.md`
3. 수정한 기능과 수정하지 않은 기능
4. 통과한 검사와 실행하지 못한 검사
5. 대표 회귀 결과와 seed
6. 남은 위험 요소와 정확한 다음 작업
7. HTML과 상태 문서의 SHA-256
8. README의 현재 기준·다음 단계, 이 문서의 현재 인계 기준, 최신 상태 문서와 체크섬을 같은 반영 작업에서 함께 갱신

### 7.1 GitHub 업로드 분담

- 대용량 시뮬레이터 HTML은 ChatGPT가 GitHub API의 Base64/blob 업로드로 직접 전송하지 않는다.
- ChatGPT는 기준 `main`과 권한을 확인하고 작업 브랜치를 먼저 만든 뒤, 완성된 HTML 파일명·크기·SHA-256과 다운로드 파일을 사용자에게 전달한다.
- 사용자가 그 HTML을 지정 브랜치에 직접 업로드하면 ChatGPT가 원격 파일의 SHA-256과 브랜치 기준을 확인한다.
- 확인 후 ChatGPT는 상태 문서, 체크섬, README, 본 지침, 테스트, workflow 등 작은 파일만 해당 브랜치에 반영하고 PR을 만든다.
- 사용자가 대용량 HTML의 직접 업로드를 명시적으로 다시 요청하지 않는 한 이 분담을 바꾸지 않는다.

## 8. 현재 인계 기준

- 현재 안정 기준은 `Aegis_SIM_v48.html`이다.
- 크기 `7,354,511 bytes`, SHA-256 `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`, Git blob SHA `f540b68f138e3ed85614c41f6794be78602229d8`.
- v48은 `Aegis_SIM_v48_WIP15C.html`의 **byte-identical promotion**이다. 승격 과정에서 HTML 코드·상수·패킹을 변경하지 않는다.
- WIP15 feature scope는 종료한다. SRBOC canonical 6×6, reserve/reload, Nulka active decoy, ASM seeker acquisition 안정화, SM-2ER/SM-6 수동 대수상 경로와 WIP13A submerged flood self-test fixture 수리가 포함된다.
- WIP15C 최종 검사에서 core self-test failures `0`, final runtime page errors `0`.
- 정식 상태와 한계는 `AEGIS_PLAN_STATUS_v48.md`, 체크섬은 `SHA256SUMS_v48.txt`, WIP15C 상세 evidence는 `docs/wip15/C/`를 따른다.
- WIP14B4와 WIP15C 최종 WIP 세트는 `archive/v48/WIP14B4/`, `archive/v48/WIP15C/`에 보존한다.
- 이후 새 기능은 v48 stable에서 새 WIP branch를 만들어 시작한다. 정식 v48 파일을 같은 이름으로 수정하지 않는다.
- surface SM-2ER/SM-6의 MANUAL-only 정책, FRIEND/NEUTRAL/UNKNOWN 보호, truth boundary, fixed-step 결정성 계약을 유지한다.
- Nulka/soft-kill의 비공개 성능 수치와 terminal glide/재장전 등 명시된 값은 `SIM_TUNED` 게임 추상화이며 실제 군용 장비 성능값으로 취급하지 않는다.

### 최신 업로드 후보 — 출항 전 함선 선택·초기화

- 기준은 아래 WIP16B 사용자 파일이다. 새 파일은 `Aegis_SIM_v48_WIP_STARTUP_A.html`, `7,361,673 bytes`, SHA-256 `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`.
- WIP 번호 미확정 상태를 유지하며 기능명 작업 토큰 `WIP_STARTUP_A`를 사용한다. 준비 branch `ship-startup-ddg-regression`는 `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`에서 생성했다.
- 요청된 출항 전 선택·공통 최초 생성·기존 subsystem 결속과 DDG-119 회귀는 로컬 완료했다. package 34/34, startup 15/15, 기존 runtime 14/14, 3D geometry/recovery 13/13 PASS. 초기 선택에서 runtime이 없고, 선택 후 하나만 생성하며 출항 후 재선택을 거부한다.
- 상태 `AEGIS_PLAN_STATUS_v48_WIP_STARTUP_A.md`, 체크섬 `SHA256SUMS_v48_WIP_STARTUP_A.txt`, 빌더/검사/증거 `docs/ship-startup/A/`.
- 사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 크기·Git blob·parent를 확인했고 로컬 검증본과 exact 일치한다. 7.1 순서대로 작은 지원 파일을 반영하고 신규 CI/PR을 진행한다. 원격 CI 성공은 실제 run 결과를 확인한 후 기록한다.
- 이전 B HTML/상태/체크섬은 지원 반영에서 `archive/v48/WIP16B/`로 동일 Git blob을 이동한다. 기존 원본과 증거를 덮어쓰지 않는다. archive의 옛 체크섬은 당시 경로/문서의 역사 증거이며 최신 검사에는 새 체크섬을 사용한다.
- 현재 운용 registry는 DDG-119 한 척이다. 다음 구현은 벙커힐 profile/model/builder를 이 초기화 경계에 연결하는 것이다. 다함 동시 운용·하푼·토마호크는 후속 범위다. main 병합·승격·release/tag는 별도 명시 지시를 따른다.

### 직전 개발 후보 — WIP16B

- branch `WIP16`, 기준 `main@d2b840bae95267ffc53bfda847442b2211c1ab03`, PR #41.
- WIP16A 사용자 업로드는 원본 그대로 보존한다. 현재 사용자 업로드 후보는 `Aegis_SIM_v48_WIP16B.html`: `7,357,036 bytes`, SHA-256 `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`, Git blob `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf`.
- 대응 상태 `AEGIS_PLAN_STATUS_v48_WIP16B.md`, 체크섬 `SHA256SUMS_v48_WIP16B.txt`, 소형 재현 빌더·검사·증거는 `docs/wip16/B/`를 따른다.
- 피격 구멍은 기존에도 올바른 선체 표면을 찾았으나 내부 GPU 렌더 제출 때문에 geometry commit이 지연됐다. B는 필수 구멍 commit 전 GPU 재제출만 미룬다. 기존 cut/fold·면적·물리/난수·고정 틱과 작업 예산은 유지한다.
- C5 센서 rotor의 중첩 ship-local 좌표, 등록점·parent·실제 scanner 2 meshes·mast 17 draws·single functional rotor를 검사한다. root 보호 스키마, 현재 source envelope·함포 joint·96 VLS 셀/hinge/panel binding을 검증한다. 옛 6개 구명뗏목 검사를 PASS로 간주하지 않으며 현재 C5에는 적용 불가로 표시한다.
- WIP16A의 package/Chromium 기준은 보존하고 B에서도 기존 13개 runtime acceptance를 같은 threshold로 재사용한다. 최종 결과와 tested head는 B 상태 문서 및 evidence를 따른다.
- 사용자 업로드 commit `7562bb0925e2b85521d37fefd2c81898ed6de18a`의 원격 크기·Git blob이 로컬/CI 검증본과 exact 일치한다. B 전용 CI와 일반 3D CI는 재구성본을 별도 임시 경로에 만들고 업로드 HTML과 `cmp`한 뒤 검사한다. 업로드 HTML이 있으면 덮어쓰지 않는다. 검증과 최종 통합 판정은 B 상태 문서 및 `evidence/upload_closeout.json`을 따른다.
- 새 브랜치·main 병합·v48.1 승격·release/tag는 실행하지 않았다.
- 다음 기능은 출항 전 함선 선택·초기화 공통화, 기존 DDG-119 회귀, 벙커힐 프로필/모델 연결 순서다. 하푼/토마호크·다함 동시 운용은 후속 범위며 번호는 미확정이다.

### WIP12D 이전 인계 기록

- 현재 이어서 작업할 기준은 `Aegis_SIM_v48_WIP12D.html`이다.
- 현재 기준 HTML SHA-256은 `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`이고 크기는 `3,058,349 bytes`다.
- 최종 로컬 검증은 WIP12D 정적 계약 `36/36`, WIP12A 정적 계약 `30/30`, WIP11C 정적 계약 `32/32`, WIP11B runtime-safety 정적 계약 `16/16`, 정적 계약 파일 `11/11`, WIP12D Playwright `2/2`, 전체 Playwright `36/36`을 통과했다. 실제 Kh-32 seed `481232`는 확장된 전방 연돌을 첫 surface로 맞아 primary damage budget `191`, 3-source power 합 `1.0`, damaged parts `17`을 만들며 잔존체 `4`, 내부 정지 `2`, 반대편 이탈·실제 외피 구멍 `2`, 제한된 기계적 보충 피해 `9.34313`을 기록한다. legacy ASM 공식과 전투 RNG 권위는 변하지 않았고 첫 접촉 형상만 의도적으로 달라졌다. 3D draw call은 전체 내부 `2,342`에서 피격 중심 `298`로 감소했다.
- WIP10, WIP11, WIP11A, WIP11B, WIP11C, WIP12A, WIP12B, WIP12C는 각각 `archive/v48/` 아래의 같은 이름 폴더에 보존한다. WIP12C HTML은 SHA-256 `55c4c71ee05053820743ae3ce6cdf80cd07b34a92643062309700ff61530567d`로 바이트 단위 보존한다.
- WIP11B의 활성 자함 삭제 금지, detached export, 7-codec preflight, `profileRevision` 호환성과 validation 거부 시 zero-mutation 계약은 그대로 유지한다.
- WIP11C는 살아 있는 적 대함미사일과 잔해를 분리한다. 요격된 위협은 즉시 truth association과 hostile collection에서 퇴역하며, 잔해는 `ENGAGEMENT_RUNTIME.world.entities.asmWreckage`에서만 고정 tick 물리를 계속한다. coast 중인 센서 track이 남더라도 truth를 다시 해석해서는 안 된다.
- WIP11C 교전통제는 요격탄 신관·직접 분해 보고를 받으면 코스팅 트랙을 유지한 채 `KILL_ASSESSMENT / WITHHELD`로 전환한다. 직접 분해는 `0.35초`, 신관 보고만 있는 경우는 `1.5초` 동안 일관 관측이 없을 때 `DESTROYED`로 확인한다. 보고 이후 새 측정이 들어오면 즉시 관측 기반 `THREAT` 또는 `HARMLESS` 판정으로 복귀한다.
- WIP11C에서 `DIRECT_BREAKUP`은 해당 표적의 DL·SPY 무기지원·SPG-62 live ownership과 시간 예약을 같은 틱에 해제한다. BDA 트랙은 적색 위협점 대신 `BDA/KILL` 십자표로 표시하고, `DESTROYED` 확인 뒤 `1.25초` kill-mark가 끝나면 원래 미사일의 유령 MEM 표시는 숨긴다. 내부 track record는 익명 search plot 재연관 가능성을 위해 남길 수 있지만 사격통제 품질이나 표시 자격을 갖지 않는다.
- 우군 종말효과 보고가 없는 고속 강하 ASM coast도 적 truth 생존 상태로 지우지 않는다. EKF 추정 강하율이 `-45 m/s` 이하이고 예상 수면도달이 `0.35초` 이내이며, 무반사가 `0.25초` 이상이고 예상 수면교차점이 함체 envelope보다 `25 m` 이상 바깥인 상태가 `0.30초` 지속된 뒤 추정 고도가 `8 m` 이하일 때만 `OBSERVED_SEA_IMPACT / HARMLESS`로 종결한다. 이때 표시·AUTO 재교전·SPG-62 지원을 막고, 이후 coherent return이 연관되면 즉시 추정을 취소한다. 이 경로도 `enemyMissiles`, `truthEnded`, 실제 생존 플래그를 읽지 않는다.
- 실전 SPY track은 `truthRef`가 없는 익명 파일이므로 파괴된 ASM의 truth object ID를 track ID로 역조회해 BDA를 만들지 않는다. SM-2/ESSM은 `assignedTargetId`, RAM은 `targetId`, Phalanx 탄은 발사 순간 mount track ID를 종말피해·직접분해 보고까지 운반하며, 지연 구조파괴에는 직전 우군 교전 provenance를 사용한다. 이후 5 Hz cleanup 신관 보고는 같은 사건에 병합하고 `DIRECT_BREAKUP` 증거를 fuze-only로 강등하지 않는다.
- Kh-32/ESSM 경쟁 조건 회귀는 seed `112000`에서 실제 분해 5 tick 전의 신관 보고(step `840`)를 실제 ESSM `4`의 `PROX_DETONATION_KILL`/분해(step `845`)로 승격한다. 병합 사건의 effect step은 `845`로 재기준화되고 같은-tick SPY 측정은 생존 귀환으로 오인되지 않아야 하며, AUTO 추가발사 `0`, SPG/DL/SARH 해제, 표시 ASM `0`, 독립 잔해 존속을 유지한다.
- `DIRECT_BREAKUP` 종말효과 보고는 효과 step과 SI 위치·속도를 함께 운반한다. 효과 발생 전부터 존재하며 엄격한 위치·속도 게이트를 통과하고 효과 뒤 새 측정이 없는 sibling/coast 파일만 같은 BDA로 상관해 `MEM-?` 유령을 닫는다. 상관된 파일도 효과 이후 coherent measurement가 들어오면 즉시 `THREAT`/`HARMLESS` 관측 평가로 복귀한다.
- 기존 track이 LOST로 바뀌는 같은 5 Hz 평가 프레임에 replacement alias가 생기는 경우를 별도 후처리한다. 검증된 alias에는 SM-2/ESSM `assignedTargetId`, RAM `targetId`, Phalanx `engagementTrackId`, CIWS mount tracking/cue, SPG-62 live map·예약행, 선택 lock을 모두 인계하고 이전 ID의 지원 소유권을 남기지 않는다.
- AUTO·CIWS·soft-kill·반자동 lock은 `KILL_ASSESSMENT`와 `DESTROYED`를 새 표적으로 취급하지 않는다. 이 판단 경로에서 `truthEnded`, `enemyMissiles`나 실제 생존 객체를 읽지 않는다.
- 잔해 생성은 요격 결과 직후가 아니라 기존 대함미사일 부위·구조·탄두 손상 observer가 끝난 뒤 수행한다. 연료 손상은 연소, 구조·조종 손상은 무결성과 분열, 탄두 기폭은 폭발 분열에 반영한다.
- 잔해는 전투 난수와 분리된 결정적 스트림을 사용한다. 3D는 잔해 위치·자세와 수면 사건을 표시만 하며 물리를 적분하지 않는다.
- 수면 진입과 저고도 폭발은 `WATER_ENTRY` / `WATER_SURFACE_BLAST` 사건을 남기지만, WIP11C에서는 수중 폭압이나 함체 수면 충격 피해를 새로 계산하지 않는다.
- WIP11C의 SM-2·ESSM·RAM 연기는 표시 전용 계약으로 명목 수명을 기존의 8배로 유지한다. 새 궤적 간격은 원래값의 3.5배, 수명 36% 이후 노후 궤적은 3개 중 2개를 남겨 유효 5.25배 간격으로 표시한다. 노후 연기는 최대 1.8배 추가 확산되고 86% 수명까지 약 42% 불투명도를 유지하며, 요격탄/전역 상한은 9,000/12,000이다. 상한 압력에서는 오래된 요격탄 연기를 균등하게 먼저 솎고 물리·센서·교전 결과에는 피드백하지 않는다.
- WIP11C의 대함미사일 연기는 고도 표시 전용 게이트를 사용한다. Kh-32는 5 km 이하에서 새 연기를 만들지 않고 5–8 km에서 점진적으로 나타나며 8 km 이상에서 정상 표시한다. Kh-35U는 기존 터보제트 무연 cloud 정책을 유지한다.
- Mk41 셀의 거의 수직인 deck-normal에서 생기는 미세 수평 투영은 유효한 발사 방위가 아니다. SM-2/ESSM 셀 내부의 위치와 속도는 실제 deck-normal 축을 따르되, 탄체 heading은 발사 순간 계산한 표적 방위를 별도 `launchAzimuthRad`로 보존해야 한다. deck-normal azimuth로 heading을 덮어쓰면 표적 정반대 선회가 재발한다.
- WIP11C는 WIP11B의 요격 운동학·파편 Pk·SM-2/ESSM/RAM 비행 유도·`updateMissile()`·CIWS 요격 해법을 바이트 단위로 보존한다. `applyInterceptResult()`의 난수 호출과 판정 임계값도 동일하다. 단, Mk41 초기 방위 덮어쓰기 결함은 발사/셀 구속 계층에서 의도적으로 수정했으므로 전체 audit JSON의 바이트 exact 일치는 요구하지 않는다. 같은-seed 이산 요격 결과와 난수 상태는 exact, 연속값은 `1e-8 × max(1, |a|, |b|)` 이내 수치 동등성, 독립 Pk 곡선은 exact를 기준으로 한다.
- 잔해의 함체 재충돌은 WIP11B의 DUD 관통 호환 경로를 운동 피해 전용으로 사용한다. 잔존 탄두의 일반화된 기폭·신관 처리는 WIP12A로 미룬다.
- 작전 snapshot에는 잔해와 수면 사건을 저장하지 않는다. 둘 다 교전 transient이며 전체/교전 reset과 moving-world 이동에는 포함한다.
- WIP11A의 `spawnShipRuntime()`은 identity/ownership 기반만 제공한다. 다른 함정을 실제 시뮬레이션 tick에 넣는 다함전 구현은 아니다.
- 이후 snapshot에 새로운 authoritative 상태를 추가할 때만 대응 codec과 정상/거부/zero-mutation fixture를 함께 갱신한다. snapshot 밖의 일반 전투 기능 추가는 WIP11B 계약 수정 사유가 아니다.
- WIP11 두께와 구조 계수는 모두 `SIM_TUNED`이며 실제 DDG-119 조선 도면값으로 취급하지 않는다. 아라미드는 대형 관통체 저항에 직접 합산하지 않고 파편·후면 스폴 채널에만 적용한다.
- WIP12A는 모든 탄체에 하나의 관통식을 강제하지 않는다. `TerminalProjectileSpec`, 가변 projectile state, ordered `ImpactTrace`, 독립 result 축과 채널별 `DamagePacket` 계약을 공유하고 충돌 regime에 따라 solver를 선택한다.
- `massKg`와 `penetratorMassKg`는 분리한다. state의 normalized `direction`과 `bodyAxis`가 권위값이며 운동에너지·운동량과 yaw는 파생값이다. 좌표는 `SHIP_LOCAL_METRES`, obliquity는 `0° = 정면`, `90° = grazing`이다.
- WIP12A traversal은 `BOUNDARY`, 저항이 없는 `EMPTY`, 실제 물질의 `DAMAGE_VOLUME`, 저항이 없는 `CREW_EXPOSURE`를 구분한다. EMPTY와 승조원 점유 자체는 속도·질량·coherent mass·무결성을 소모하지 않고 비행시간과 신관 시간만 진행한다.
- 최초 ray 후보 목록을 최종 경로로 사용하지 않는다. 모든 충돌·편향·도탄 뒤 현재 state와 direction으로 geometry를 다시 질의하며, 같은 거리 접촉의 우선순위·epsilon·최대 event/path 한계를 결정적으로 적용한다.
- 각 구간에서는 next contact, volume exit, projectile stop과 fuze expiry가 경쟁한다. 가장 빠른 사건을 처리하며 동시 사건은 contact/exit/stop 상태를 먼저 확정한 뒤 그 위치에서 기폭한다.
- `BoundaryImpactResult`의 `RICOCHET/STOPPED/PARTIAL/PERFORATED`와 `INTACT/DEFORMED/FRACTURED/SHATTERED`는 독립 축이다. plate failure mode와 `ImpactBudget`도 별도로 기록해 질량·에너지·운동량 closure를 진단한다.
- 활성 solver는 `THIN_DUCTILE_PLATE`, `LIGHT_STRUCTURE`, `VOLUME_CRUSH`다. `HOMOGENEOUS_ARMOR`와 `FACE_HARDENED_ARMOR`는 interface만 존재하며 검증되지 않은 상수로 작동하는 척하지 않고 명시적으로 거부한다.
- 종말탄도 계산은 authoritative damage state를 직접 바꾸지 않는다. `DamagePacket`은 direct, plug/spall, fragments, blast, thermal/incendiary, breach, impulse와 crew exposure를 나누고, `wip12aApplyDamagePacket()`만 기존 침수·구조·승조원·VLS/장비 consumer에 전달한다. `impactEventId` 중복 적용은 거부한다.
- 아라미드는 직접 관통 저항에 강철처럼 합산하지 않고 rear-spall과 fragment 채널을 감쇠한다. 승조원 점유 공간은 탄체 저항 volume이 아니다.
- 6종 fixture는 `TEST_12P7_AP`, `TEST_30_AP`, `TEST_30_HEI`, `TEST_76_SAP`, `TEST_127_HE`, `TEST_127_SAP`이며 모두 `DIAGNOSTIC_SIM_TUNED`다. 각 fixture는 정상 traversal뿐 아니라 도탄·정지·부분·완전 관통·shatter 경계를 검사한다.
- Kh-35U/Kh-32 live impact는 공통 API의 `LEGACY_ASM_PENETRATION_COMPAT`를 통과하지만 내부 권위 계산은 바이트 보존된 기존 경로다. 출력과 전투 RNG 상태의 exact parity를 유지하며 별도 승인 전 신규 solver로 이전하지 않는다.
- damage patch는 surface/local 좌표, 영향 반경, 잔존두께, hole, crack과 잔존강도 진단 계약만 존재한다. persistent patch ledger, 누적 피격 상태와 snapshot codec/revision migration은 활성화하지 않는다.
- WIP12A에서는 실제 함포 발사·포탑·탄창, 외탄도·공기저항·바람·분산, 해상사격 FCS, 실전 중장갑 solver와 새 표적함을 활성화하지 않는다.
- WIP12B는 Kh-32, Kh-35U, SM-2, ESSM, RAM을 공통 terminal-event 계약에 등록한다. Kh-32/Kh-35U 피해는 기존 compatibility path가 한 번만 적용하며, SM-2/ESSM/RAM의 live 요격 결과는 기존 파편/Pk 권위를 관찰해 event로 변환할 뿐 다시 판정하거나 피해를 중복 적용하지 않는다.
- SM-2, ESSM, RAM은 `PROXIMITY`, `CONTACT_DIRECT_ACTION`, `DUD` 경로를 가진다. earliest-valid-event가 우선하며 proximity는 접촉 전, contact는 실제 경계 해결 뒤 같은 위치, DUD는 탄두효과 없이 처리한다. ESSM direct-action backup의 정확한 공개 hardware identity는 확인하지 못했으므로 `SIM_WORKING_ASSUMPTION_PUBLIC_IDENTITY_UNRESOLVED`로 유지한다.
- WIP12B terminal-event ledger는 `impactEventId`로 중복을 막고 최근 32개만 보존하는 engagement transient다. operational snapshot과 persistent patch state에 넣지 않으며 reset lifecycle에 포함한다.
- 3D는 ship-local terminal event에서 경로, 경계·파괴구, 기폭, blast envelope와 fragment cone을 준비하되 명시적 `내부 구조` 보기에서만 표시한다. 2D 관통선·폭발범위도 같은 모드에만 표시하며, target-local 공중요격 event를 자함에 잘못 붙이지 않고 렌더러가 전투 물리나 난수를 계산하지 않는다.
- WIP12B 당시에는 피격 뒤의 `COMPARTMENT_INTERIOR_V8` coarse flood-cell proxy를 폐기하고 open damage에서 상세 WIP06 topology를 표시했다. WIP12C는 아래 인계 규칙에서 이 표시 정책만 의도적으로 되돌리며, 상세 구획과 침수·화재·연기 overlay가 실제 hull/upper-structure envelope 밖으로 돌출되지 않아야 한다는 containment 계약은 유지한다.
- 연돌 권위값은 `ACTIVE_SHIP_PROFILE.geometry.funnels`다. WIP12D 누적 보정 뒤 전방 연돌 범위는 `x=3.50…17.10 m`, 후방 연돌 범위는 `x=-18.15…-4.55 m`이며 3D, 외부 피격판정, RCS aim, 내부 배기 트렁크와 2D indicator가 이를 함께 소비한다. 후방 상단 SPG-62와 받침대는 `x=-20.0 m`로 이동해 보수적 평면 투영 `0.40 m`, 실제 높이의 테이퍼 외피 `1.499 m` 간격을 가진다. 연돌 접선각을 계산한 SPG-62 blind half-angle은 전방/후방상단/후방하단 순서로 `41°/49°/54°`다.
- WIP12B의 direct surface-impact resolver는 이후 제한적 대함전이 사용할 진입점일 뿐이다. 현재는 표면표적 선택, 발사 승인, 실제 SM-2/ESSM/RAM 대함 발사와 해상사격 FCS를 활성화하지 않는다.
- WIP12C는 정상 기폭의 pre-detonation state에서 최대 4개의 결정적 `MACRO_FRAGMENT`를 만든다. 각 잔존체는 질량·coherent mass·무결성·direction·bodyAxis를 가진 inert WIP12A 탄체이며 동일한 event-driven traversal로 장비 체적, 격벽과 반대편 외판을 다시 해결한다. 미세 파편은 통계 damage channel에 남긴다.
- WIP12C 잔존체 생성은 event ID hash만 사용하고 전투 RNG를 소비하지 않는다. parent non-explosive mass를 macro mass와 statistical fragment mass로 닫고, macro kinetic energy는 parent kinetic energy와 제한된 coupled chemical energy 합을 넘지 않도록 diagnostic ledger를 남긴다.
- 공통 경로에서는 root와 child의 `penetrationCorridors`, 관통·spall·파편·폭압·열·파괴구·충격·승조원 채널을 부모 `DamagePacket`에 평탄화한 뒤 한 번만 적용한다. 동일 `impactEventId` 재적용은 거부하며 다중 관통선과 반대편 파괴구는 침수·승조원 consumer에 한 사건으로 전달한다.
- Kh-32/Kh-35U는 기존 피해와 RNG exact parity를 유지한다. WIP12C cascade는 `LEGACY_PREACCOUNTED_OBSERVATION_ONLY`로 관찰·표시만 하고 child 피해를 다시 적용하지 않는다. DUD는 functioning detonation이 아니므로 macro body를 만들지 않는다. legacy ASM의 신규 solver 및 잔존체 피해 권위 이전은 별도 승인 대상이다.
- WIP12C는 외부 파괴구를 통해 보이는 내부를 `COMPARTMENT_INTERIOR_V8` coarse 침수구획으로 되돌린다. 명시적 `내부 구조` 모드에서는 coarse layer를 숨기고 상세 138-space topology·hazard·crew와 관통선·폭발범위·macro body 경로·반대편 출구를 표시하며 외형 재질을 투명화한다. 모든 3D 객체는 presentation-only다.
- WIP12C 실제 함체 traversal은 상세 138-space topology와 70개 장비·8개 tank material volume을 cache하고 10 m longitudinal bin으로 후보를 줄인다. 최초 직선 후보를 고정하지 않고 매 접촉·편향 뒤 현재 state로 다음 상세 경계, material volume과 tapered outer-shell exit를 재질의하며 국부 hull normal을 사용한다. open portal은 저항·spall·새 hole이 모두 0이고, low-energy body는 내부 경계나 volume에서 막혀 반대편 파괴구를 만들지 않아야 한다.
- WIP12C impact-time traversal은 body당 최대 80 m/128 events, cascade 최대 4 bodies로 제한하고 render frame에서는 geometry query를 하지 않는다. 최종 512회 로컬 benchmark는 `0.2691 ms/impact`, 후보 감소 `65.9975%`, render query `0`, combat RNG 불변을 기록했다.
- WIP12C 화재 정책에서 일반 impact damage와 structural impulse는 ignition source가 아니다. 비폭발성 inert 판재·plug·fragment는 자체 발화 확률 0이며, 실제 vulnerable `DAMAGE_VOLUME`을 맞힌 mechanical impact만 event-ID hash와 energy/speed로 희박 발화를 결정한다. hard cap은 fuel/lube `1.8%`, aviation fuel `1.4%`, electrical `0.8%`, ordnance `0.6%`, inert `0%`이고 각 volume은 더 낮은 cap을 선언할 수 있다. explosive blast는 detonation cell, thermal/incendiary는 명시적 direct candidate로만 처리하며 이 정책은 combat RNG를 소비하지 않는다.
- WIP12C에서도 실제 표면표적 선택·발사, 함포·포탑·탄창, 외탄도·해상사격 해법, persistent patch, heavy-armor solver, operational snapshot cascade 저장은 활성화하지 않는다.
- WIP12D는 Kh-32의 legacy 관통 상태에서 실제 기폭 거리의 잔존 유효에너지 비율을 읽고, raw entry 운동에너지에 그 비율을 곱해 폭발 직전의 물리 운동에너지와 속도를 복원한다. 이 값 자체는 기존 Kh-32 피해 공식을 바꾸지 않고 대형 잔존체의 병진운동 초기화에만 사용한다. 다만 사용자 지시로 변경된 연돌 hitbox를 실제 피격판정도 함께 소비하므로, 새 envelope와 교차하는 경로의 첫 접촉 surface와 그에 따른 공간 피해 결과는 의도적으로 달라질 수 있다.
- WIP12D의 macro translation은 부모 속도를 질량에 따라 계승하되 `0.92` retention과 TNT-equivalent의 `2.4%` chemical coupling 안에서 제한한다. 최대 4개 body, body당 최대 6회 shatter continuation과 128개 traversal event를 허용하며 mass/energy ledger와 combat-RNG 불변을 진단한다.
- `PERFORATED`와 `SHATTERED`는 동시에 성립할 수 있다. opt-in `MACRO_FRAGMENT`가 외판을 완전 관통하고 잔존 질량 `0.12 kg`, coherent mass `0.035 kg`, 속도 `35 m/s`, 에너지 `15 kJ` 이상이면 깨진 상태로도 후속 경계를 계속 처리한다. terminal outer-shell 관통은 shatter 정지보다 먼저 `TARGET_EXIT`로 확정한다. 일반 WIP12A 탄체는 opt-in하지 않으므로 기존 shatter 동작을 유지한다.
- 반대편 외판 이탈 뒤에는 중력만 적용하는 저항 0의 외부 비행을 진행하고, 현재 state로 실제 물리 선체와 상세 상부구조 공간을 다시 질의한다. body당 최대 재진입 `3`, 외피 교차 `8`, 외부 탐색 `220 m/2.5초/512 sample`로 제한하며 재진입 경계에서도 실제 재질 solver를 다시 실행해 도탄·정지·관통·파쇄를 허용한다. 실제 형상 fixture는 전방 S5 연돌 이탈, `12.35 m` 외부 비행, 후방 S5 연돌 재진입·재이탈의 `EXIT → REENTRY → EXIT`와 세 개의 `FUNNEL_SKIN` 파괴구를 검증한다.
- 모든 완전 관통 physical-hull 교차는 위치·법선·면적을 가진 `additionalShellOpening`으로 기존 침수 모델에 전달한다. 수중 또는 파랑에 젖은 구멍은 실제 유입과 기존 안정성·구조 후속 피해를 만든다. `${impactEventId}:RESIDUAL_SUPPLEMENT`는 중복을 거부하고 폭발·열·legacy blast를 재적용하지 않으며 직접 기계 피해만 `0.16 units/MJ`, row `8`, target `18`, total `42`로 제한한다.
- 수면 위 최종 이탈은 최대 `8초/1,800 m/18점`의 사전 계산 표시선을 만들고 수선 아래 이탈은 즉시 `SUBMERGED_WATER_ENTRY`로 기록한다. 해수 진입선은 표시 전용이며 수중 충격 피해나 render-frame 물리를 추가하지 않는다.
- high-speed projectile이 기폭 뒤 `0.75 m` 이상 coherent path를 가지면 authoritative WIP101 blast source는 최소 head/peak/tail로 분포한다. power fraction 합은 정확히 `1`이고 피해 consumer와 3D connected teardrop이 같은 source를 사용한다. 느리거나 path가 짧은 폭발은 기존처럼 구형에 가깝게 수렴한다.
- live Kh-32 cascade는 계속 `LEGACY_PREACCOUNTED_OBSERVATION_ONLY`, `mergeDamage:false`여서 primary legacy blast packet을 중복 적용하지 않는다. 다만 위의 제한된 residual supplement는 실제 기계 피해와 구멍을 한 번 적용한다. 새 연돌 hitbox를 소비하는 seed `481232` 회귀는 primary damage budget `191`, damaged parts `17`, macro body `4`, shatter continuation `10`, 내부 정지 `2`, 반대편 외판 이탈·실제 구멍·해수 진입 `2`, 추가 기계 피해 `9.34313`을 만든다. DUD는 body와 exit 모두 `0`이고 전투 RNG는 변하지 않는다.
- WIP12D의 관통선·잔존체·반대편 출구·재진입·해수 진입과 물방울형 blast envelope는 명시적 `내부 구조` 보기에서만 표시한다. 기본 `피격 중심`은 최신 impact 주위의 여섯 clipping plane과 object-AABB culling을 함께 사용하고 `전체 내부` 버튼으로 완전한 상세 구획을 복원한다. focus 선택은 event/damage revision 때만 다시 만들며 flood/fire/smoke overlay는 최대 3개 batch로 표시한다. 검증 장면의 draw call은 `2,342`에서 `298`로 감소했다.
- WIP12D에서도 inert fragment와 structural impulse 자체는 화재를 만들지 않는다. WIP12C의 실제 vulnerable material volume 희박 발화, explosive blast와 thermal/incendiary 직접 source만 유지한다.
- WIP12D는 primary legacy ASM solver의 공통 packet 완전 이전, legacy blast 재적용, 무제한 개별 파편, 수중 충격 피해, persistent patch, snapshot migration, 표면교전 발사/FCS, 함포와 외탄도를 활성화하지 않는다.
- 다음 코드 작업은 WIP12E다. `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`를 범위 계약으로 사용해 legacy scalar blast 재분배를 bounded compartment/portal pressure·impulse solver로 교체한다. incident/reflected pressure, positive-phase impulse, blast wind, hot gas, dynamic breach와 exterior vent를 분리하고, shadow 진단 뒤 신규 solver 하나만 피해 권위를 가져야 한다. 권위 전환 뒤 기존 Kh-32 `191` scalar budget과 부품별 피해 행은 calibration 비교값이지 exact 요구가 아니며, 관통·기폭 위치·잔존체·외피 구멍·침수·전투 RNG는 회귀 권위로 유지한다. WIP13은 그 다음의 제한적 표면교전 표적 승인·발사/FCS 경로이고, WIP14는 간단한 표적함과 복수 함선 프로파일이다. 실제 함포 발사·포탑·탄창·외탄도·해상사격 해법은 별도 승인된 범위로 고정한다.
- WIP 번호는 이 인계 순서를 사용하며 과거 대화의 다른 WIP 번호표를 재사용하지 않는다.
