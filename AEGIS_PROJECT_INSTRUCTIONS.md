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

### 7.1 GitHub 직접 업로드 및 확인

- 2026-10-10 사용자 승인에 따라 Codex는 **대용량 원본 HTML을 포함한 프로젝트 파일을 직접 GitHub에 업로드하고 원격 확인까지 수행한다.** HTML 직접 업로드를 위해 사용자에게 다시 승인이나 수동 업로드를 요청하지 않는다.
- 기준 `main`, 저장소 권한과 작업 브랜치의 현재 head를 확인한 뒤 검증이 끝난 파일을 작업 브랜치에 반영한다. 사용자의 새 commit을 보존하며 fast-forward 또는 expected-head 검사로 반영한다.
- 원본 HTML bytes를 그대로 업로드한다. Git push 또는 사용 가능한 GitHub API/blob 방식을 사용할 수 있다. 전송 크기·도구 제한은 적합한 방법으로 처리하며 HTML을 잘라 보내거나 전송용 대체 파일로 바꾸지 않는다.
- 같은 버전의 HTML·상태·SHA·README·본 지침·지원 파일·검사·workflow를 일관되게 반영한다. 이전 버전은 동일 bytes/blob으로 archive에 보존한다. 이미 사용자가 올린 HTML이 검증본과 일치하면 그 blob을 재사용한다.
- 업로드 후 원격 파일을 다시 읽어 크기·SHA-256·Git blob 및 commit 기준을 대조한다. 로컬 업로드 성공만으로 원격 검증 완료라고 보고하지 않는다. 완성 HTML의 파일명·크기·SHA와 다운로드 또는 원격 파일 링크를 남긴다.
- PR과 같은 파일의 CI를 진행하고 실제 결과와 남은 범위를 보고한다. 병합은 해당 작업에 대한 사용자 요청을 따른다. 사용자가 직접 올리는 방식도 선택할 수 있지만 필수 작업 분담으로 요구하지 않는다.

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

### 모델 검사 기준 — 헬기 v01

- 별도 `helicopter-model-a` 브랜치에서 사용자 DDG-118 GLB의 SH-60 정적 격납/전개/비행 부품을 추출했다. [미리보기](docs/helicopter/A/AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html), [상태](docs/helicopter/A/AEGIS_HELICOPTER_MODEL_STATUS_v01.md), [계약·재현·한계](docs/helicopter/A/README.md), [SHA](docs/helicopter/A/SHA256SUMS.txt).
- 공통 geometry/material 공유·텍스처0, lossless GLB 591,920bytes, Q16/SNORM16 압축223,419bytes, 게임 HTML 내 모델/로더 추가301,239bytes (+1.9176%). 구조14/native13/최종scene·UI24 검사와 정적 문법PASS. 디코더는 표시 전용이며 렌더러가 물리·센서·교전 상태를 소유하지 않는다.
- 게임 HTML/상태/체크섬, PERF_F/이전 검사·workflow는 보존한다. 모델 검사기는 §1의 별도 버전 규칙을 따르므로 새 시뮬레이터 WIP 또는 archive 이동은 없다. 이전 PERF_F 지원 checksum은 당시 PERF_F commit의 기록이고, 새 asset branch 문서 변경은 모델 SHA manifest에 포함한다. Actions/새 PR/병합을 실행하지 않는다.
- source 이름만으로 MH-60R 등 형식을 확정하지 않으며 source unit→meter 축척과 로터/꼬리 동적 animation은 미검증이다. 다음은 축척·회전축·갑판/격납고 배치·LOD, 이후 별도 항공 profile/runtime·비행·센서·초수평선 탐지·정보공유다.

### 최신 개발 기준 PERF_F — 최종 최적화 검증

- 현재 [HTML](Aegis_SIM_v48_WIP_PERF_F.html), 15,709,299bytes, SHA `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5`, main `e9eb7d600d01e6d271b4dcf99e98b5e65dd09bbfe58f0ef29955affc343b398c`. PERF_E final `bd8962011a16cfeb4158670d3e562a92e0a52ff4` 위 performance-f. 현재 support/workflow/checksum은 F, 이전 문장은 당시 기록이다.
- complete anchor 공개 이후에만 remaining quick work를 최신 피격으로 선점한다. unpublished opening은 보호하고 live/original buffers를 유지한다. 안정된 입력의 최종 형상·현재6ms budget·physics/피해/sensors/AI/RNG/fixed60/120/20Hz/actual release와 이전 캐시/모델/연기 결과는 보존한다. packed13 표시용 scheduler와 texture disposal만 수정한다.
- 최종 원본 1817/1817PASS/38suites, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_F.md), [SHA](SHA256SUMS_v48_WIP_PERF_F.txt), [계약](docs/performance/F/README.md), [성능/한계](docs/performance/F/PERFORMANCE.md), [검증](docs/performance/F/evidence/verification-summary.json).
- 기존 전체 회귀와 연속3회 cut/queue, 양함종 각각120simulated seconds/7200ticks의 세 함정 overload exact state/RNG,8회nativeGPU smoke/Kh32 epoch와pending-cut 외부 함정owner replacement/disposal 검증. 전체 회귀/카메라 종료 후 native second-hit submit4쌍 직렬 AB/BA. 제어된 detached scar/diagnostic tracks이며 자연 다발 피격·실제 수시간 soak·hardware/phone FPS는 미실행이다. 누적CPU는 E 당시기록을 참조하며 새 F측정으로 표현하지 않는다.
- E 네 파일 samebytes/blob archive, stable와 이전 증거 유지. §7.1 full original 직접 upload/독립 remote readback. Actions dispatch/main·선행 branch merge/새 PR 없음.
- 계획한 최종 최적화 검증 범위 완료. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.

### 직전 개발 기준 PERF_E — 최적화5단계 (당시 기록)

- 현재 v48_WIP_PERF_E, HTML 15,709,083bytes SHA `0b59340c2db16d33a6fefe810d8bbf27f96ff189ad8a8166139578b50f2051b5`, main `0f57e35ae2efe55a9ac9c1e5af54650d8eb574e1faf1672e2fef1b84931f617d`. PERF_D final `b4b58dcf61cff18674ec58f5798a2a15ca178ae9` 위 performance-e. 현재 support/workflow/checksum은 E이고 이전 단계 문장은 당시 기록이다.
- 등록 CG/DDG quick job은 각 mesh의 ordered holes를 유지하며 모든 actual scar anchor를 먼저 완성해 함께 공개한다. 주변 작업은 계속한다. unprocessed 이전 live geometry/originals를 조기 복원·dispose하지 않으며 incremental 입력을 보존한다. final publish는 attached anchor buffers를 재사용한다. finally는 미공개 버퍼만, reset/import/retirement는 기존 lifecycle로 live cuts를 회수한다. legacy 비등록 모델은 기존 공개 경로다. LOD proxy는 같은 draw 전에 opening revision을 확인한다.
- 동일 split plane distance를 인접 edge에서 재사용하고 triangle bound의3배열을 제거한다. plane 순서/epsilon/정점/법선/색상·산술과 최종 attrs/index/groups/bounds/bindings를 보존한다.
- smoke shader/sort/pool/time/RNG를 유지하고 exact Float32 dirty range만 전송한다. pending ranges는 native onUpload 또는 r140 consumed-range 확인 이후에만 해제한다. 여러 flush/숨김/재등장/축소된 tail/camera/origin/ULP/signed0/reset과 WebGL2 GPU bytes exact를 검증한다.
- packed13만 변경, 나머지 packed/model/envelope bytes와 physical damage/flight/sensors/AI/actual release/fixed60/120/20Hz/PERF_A/B/C caches 보존. 최종 원본 1735/1735PASS/35suites, 오류0. 누적 host CPU16쌍·native cut8쌍·RAF8쌍 직렬, 조건/한계/증거는 E docs를 따른다. generator shape fixture를 native latency로, host/SwiftShader submission을 hardware/phone FPS로 표현하지 않는다. 최초 H4A→D static-overlap timing은 제외/보존한다.
- 이전 D 네 파일 samebytes/blob archive, stablev48/이전 증거 유지. §7.1 승인 full original upload/독립 readback. Actions dispatch/main·선행 branch 병합/새 PR 없음. 다음은 다수 피격/장시간/자원 회수 최종 점검 이후 헬기 → RGM-109E Block Va다.

### 직전 개발 기준 PERF_D — 최적화4단계 (당시 기록)

- 현재 v48_WIP_PERF_D, HTML 15,707,799bytes SHA `bd3bc97089cd0085c1990b5460fd4b8d6f5c9bcf794e1f520a42bc9c2aa95c2e`, main `7212a596022d0aa7f7294633eff41015e03cb6f217d7150bcdd025c04e7d3b31`. PERF_C final `5ddd05ce9358e9a23c11d26030bff05c6f18fa1d` 위 performance-d. 현행 support/workflow/checksum은 PERF_D, 아래 이전 단계는 당시 기록이다.
- source sectional envelope의 기존 rounded-key/last-value/order/sort/convex 결과를 유지하면서 임시 배열을 줄인다. 변형 radial edge는 동일 scalar 산술이다. packed2/13만 변경하고 등록 모델·삼각형·envelope source bytes를 유지한다.
- 완성된 quick opening/fold snapshot을 atomic publish한 후 동일 generator로 scorch/outline을 완성한다. detail은 기존 동작. live geometry ownership을 publish 시 이전하며 cancellation finally는 미공개 작업만 dispose한다. reset/import/owner retirement가 기존 수명주기로 live geometry를 회수한다. presenter-only _damageOpeningRevisionPerfD는 snapshot/authority에 저장하지 않는다.
- 자함 quick은 다른 owner 이후 기존6ms allowance의 unused share를 빌린다. total allowance/다른 owner shares/detail slice/fixed60/120/20Hz 및 physics/damage/RNG/release/PERF_A/B/C caches를 보존한다. 기존 cooperative step overshoot 가능성은 남아 있다.
- 최종 원본 1660/1660PASS/33suites, 오류0. 두 함종 geometry quick/detail/sealed bytes/index/groups/bounds/bindings와 cancel/reset, layout3,072/convex384 사례 exact. 전체 기존 회귀·six strict ownship 조건·density16쌍·native latency4쌍 state/RNG exact. 증거의 fixture와 실제 native RAF latency를 구별하고 host CPU/SwiftShader submission을 phone/hardwareGPU FPS로 표현하지 않는다.
- 이전 PERF_C 네 파일 samebytes/blob archive, stablev48 보존. §7.1 승인으로 full original 직접 upload/readback. Actions dispatch/CI PASS/main·선행 branch 병합/새PR 생성 없음. 다음은 실제3D/효과 최적화·최종 재측정, 그 뒤 헬기/초수평선 → RGM-109E Block Va다.

### 직전 개발 기준 PERF_C — 최적화3단계 (당시 기록)

- 현재 세트 v48_WIP_PERF_C, HTML 15,707,171bytes SHA `5f8fb9ed69a960c4eef4c15ab22271c82c9b59a095a9ec8a959689ecba9acffd`, main `015c4cf9f83c9f6bd595ce61583e214bbd12c8248fad15bacdc87fa10f0c7358`. PERF_B final `d26e94194d52f0040f4d3d388b9bbce49460b440` 위 performance-c. 현행 support/workflow/checksum은 PERF_C, 아래 PERF_B 이하는 당시 기록이다.
- SPY 공통 대공 NIS의 prediction/Jacobian/공분산 투영·동일 오차 역행렬만 캐시한다. 트랙 객체별 WeakMap last1, 상태6·공분산36·센서 위치/속도6·오차4 exact 비교로 in-place/same-tick 변경도 즉시 반영한다. 측정 innovation은 매번 현재값, native 산술·행렬/NIS 합산 순서를 유지한다.
- 캐시는 파생값·snapshot 비저장이며 truth/권한/시간 기반 cache가 아니다. native EKF 예측/갱신·수상 연관·plot 생성/난수·focused/global 배정/게이트·actual release source와 fixed60/120/20Hz·물리/피해/EW/AI/Harpoon DL0·PERF_A/B 최적화를 유지한다.
- 최종 원본 직접 1603/1603PASS/31suites/15captures, 오류0. NIS231차등/전체 입력 제자리 변화·오차·signed zero/invalid·갱신/거부·게이트 경계, 두 함종 core, strict CG/DDG6조건/직렬16쌍 상태/RNG/entity exact와 기존 native/browser/세 owner1/8/16/64를 확인했다. 집계/SHA/조건/한계는 PERF_C evidence를 따른다.
- PERF_B 네 원본 samebytes/blob·stablev48/assets0~12 보존. §7.1 승인에 따라 full original 직접 upload/readback, Actions dispatch/CI PASS/main·선행PR 병합/새PR 생성 없음. 다음은 피격 envelope → 실제 render·최종 재측정이며 이후 헬기/초수평선 → RGM-109E Block Va다. host CPU를 휴대폰/실제GPU FPS로 표현하지 않는다.

### 직전 개발 기준 PERF_B — 최적화2단계 (당시 기록)

- 현재 세트 v48_WIP_PERF_B, HTML 15,706,015bytes SHA `292622e556192d3c954917437709a0f1e4489e1636cd6263a4b7737832013faf`, main `6577a3e216f0bec2ae7aeefb7e79524c33ee52c564de94dfb3763ad3cb24a977`. PERF_A final `4b42aacd4271ce790b47b981b9a58dc960e5d5c5` 위 performance-b. 현행 support/workflow/checksum은 PERF_B, 아래 PERF_A 이하는 당시 기록이다.
- 두 native lexical planner의 build-local ctx에서 같은 threat/delay forecast와 SPG 기하 점수를 재사용하고 unused track metadata 복사를 생략한다. 다음 판단의 현재 sensor/pose/damage/firecontrol과 매회 current reservation 충돌 검사는 유지한다. 실제 발사에 이 cache를 넘기지 않으며 권한/FRIEND/NEUTRAL/HOLD/EMCON/damage/capability/FCS/예비탄 재검사를 유지한다.
- owner별 body frame은 heading/heel/trim/draft/origin xyz 전부 Object.is exact일 때만 재사용한다. current snapshot/항법 읽기·canonical constructor/invalid 예외를 유지하고 same-tick 변화도 즉시 반영한다. 캐시는 파생값·snapshot 비저장, fixed60/120/20Hz·RNG·무장·피해·EW·AI·Harpoon DL0와 PERF_A 최적화를 유지한다.
- 새 원본 직접 1534/1534PASS/30suites/15captures, 오류0. planner96제어사례, exact frame transitions/두 함종 core, CG/DDG6조건·직렬16쌍 상태/RNG·entity exact와 기존26 H4A browser suites/native 방어/피해/UI·세 owner1/8/16/64를 확인했다. counts/SHA/조건/한계는 PERF_B evidence를 따른다.
- PERF_A 네 원본 samebytes/blob과 stablev48/assets0~12 보존. §7.1 직접 원본 upload/readback 승인 유지, Actions dispatch/CI PASS/main·선행PR 병합/새PR 생성 없음. 다음은 SPY 관측 연관 → 피격 envelope → 실제 render·최종 재측정이며 이후 헬기/초수평선 → RGM-109E Block Va다. host CPU를 휴대폰/실제GPU FPS로 표현하지 않는다.

### 직전 개발 기준 PERF_A — 최적화1단계 (당시 기록)

- 현재 세트 `v48_WIP_PERF_A`, HTML 15,704,207bytes SHA `13a9de64d918efd053ead648cb312a691688691ccbfa72fe50fefd72054ae6ad`, main `c43d9287e066bd56132d57d3a2cb2b4b37bee05e008f59432a61f82ae41d64e1`. H4A final `b97925cb5fb27d4dad26d62db78520641ee70857` 위 `performance-a`. 현행 support/workflow/checksum은 PERF_A, 아래 H4A 이하 내용은 당시 기록이다.
- 불변 등록 hitbox system→고유 module name만 WeakMap으로 색인하고 현재 owner damage를 매번 읽는다. 자함 기존 함수/가변 geometry scan을 유지한다. EW IJ band 검사를 pod geometry 이전으로 이동하며 지원 band 계산·정책은 유지한다.
- Kh32 기존 도색 texture/canvas를 view/THREE/실제 paint 입력별로 공유한다. geometry/material/plume은 개별이고 body geometry lease는 idempotent, 마지막 참조에서만 texture.dispose 및 entry 제거다. live/MAIN wreck/도감·import/reset/native render를 검사했다. 닫힌 도감은 기존 current model1개를 보관한다. 두 캐시는 파생 데이터이며 snapshot/전투 상태를 소유하지 않는다.
- 새 원본 직접 1483/1483PASS/29suites/15captures, 오류0. H4A26 browser suites, 두 함종 selftests/72 EW조건,64모델 source texture1개·pixel/geometry parity,6ownship strict state/RNG와3owner1/8/16/64배속exact,별도직렬16쌍을 확인했다. counts/SHA/조건/범위는 PERF_A evidence를 따른다.
- H4A 네 원본 samebytes/blob과 stablev48/assets0~12를 보존한다. §7.1 full original upload/readback 승인 유지; Actions 미실행/CI PASS 주장 없음; main/선행PR 병합·새PR 생성 없음. 다음은 planner/SPG·SPY·피격 envelope·실제 render 최적화이며 이후 헬기/초수평선 → RGM-109E Block Va를 유지한다. CPU 관측을 휴대폰/실제GPU FPS로 표현하지 않는다.

### 직전 개발 기준 MULTI SHIP H4A — 독립 근접 자위·측정 기반 채프 (당시 기록)

- 현재 세트 `v48_WIP_MULTI_SHIP_H4A`, HTML 15,702,263bytes SHA `3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a`, main `b9f2ae3e1f53d88df36dab03e52dcde4cdb2ddd9fc8043b6456f732e63948d77`. H4 final `b74a2c733352230a0799446cfdb6730b2bb87421` 위 `multiship-defense-h4a`, PR base H4. 현행 support/workflow/checksum은 H4A다. 아래 H4 이하 기록은 당시 기준이다.
- 기존 CMS+local RF 경로를 유지하고 confirmed fresh local RF·접근 지속·미사일 운동학·자함 CPA/품질/사각/구동/전원/탄약 조건을 통과한 독립 `LOCAL_SELF_DEFENCE_H4A`만 추가한다. 실제 발사에 동일 owner/mount/pending/file 객체와 freshness/FRIEND·NEUTRAL/own-fire/효과 보호/HOLD/EMCON/손상 재검사가 있다. generic AUTO 포트 개방·CMS 적성 파일 생성·SAM 권한 확대가 아니다.
- EW는 detached own local RF 거리/접근/오차와 passive ACTIVE_SEEKER 방위의 unique association만 기존 채프 정책에 전달한다. same-mount multiple/many-to-one/multiple-emitter 모호성은 보류, ESM bearing-only range/TTC 추측 금지. reserve/interval/살보/발사 geometry·EA/눌카를 유지한다.
- 자함 nativeCIWS/CG Phalanx-only·DDG장비·radar RF/search/CMS분류·Harpoon 무DL/INS/ARH·비행/피해·H4팀/H3공격/H2기동/H1유틸리티/G공유/60·120·20Hz를 보존한다. H4 저장 schema 그대로, 새 local pending는 기존 transient 수명주기를 따른다.
- 최종 원본 직접 1484/1484PASS,27suites와 검사/보고/capture SHA·조건은 H4A evidence를 따른다. freshCG8km actualHarpoon에서 CMS ASM0·채프4/Phalanx95발·실제 DIRECT_BREAKUP/잔해, HOLD0, DDG기존방어, baseline-admitted 뒤8개 late actual-release 차단,1/8/16/64배속exact 및 H4전체회귀를 확인했다. DIAGNOSTIC_ONLY probe의 phase 조정은 실제 권한·센서·명중을 변경하는 운용 기능이 아니다.
- H4 네 원본 samebytes/blob archive와 stable v48/assets0~12를 보존한다. §7.1 직접 upload/readback 승인 유지, Actions dispatch/main·선행 PR 병합 미실행이며 계정 제한 자동 smoke를 CI PASS로 쓰지 않는다. 후속2큰단계 헬기/초수평선 탐지 → RGM-109E Block Va다. 대표 조건 밖 요격률·오격 방지/remoteFCS/실제 doctrine/FPS 인증을 주장하지 않는다.

### 직전 개발 기준 MULTI SHIP H4 — 함대 전술·합동 기동 (당시 기록)

- 현재 개발 세트 `v48_WIP_MULTI_SHIP_H4`, HTML 15,697,218 bytes, SHA `602371dfd5be5147c2e04dd4078e3216ca4f47e8ce4e7b0092bd861c3d9a5132`, main `451a717f0dbc97c289990eda7bf4864703c5a8832b81b0d4af4f53d3f6c56416`. H3 final `af1eade2d418b215720a68a5b902aae0d9387203` 위 branch `multiship-tactical-h4`, PR base `multiship-tactical-h3`, 현행 support/workflow/checksum은 H4다. 아래 이전 기준은 당시 기록이다.
- canonical `ShipRuntime.combatSystem.teamH4`가 owner-local team 설정·지연 메시지·수신 항법·전형·배정·접수·자위 근거를 소유한다. 자함/아군 teamOFF, 적함은 friendly transport에 가입하지 않는다. 원래 PLAYER 선도함/ALLY 역할 유지, FLEET selected owner 설정이며 NAV/ARM/CIC/기존3D 교전은 원래 자함이다.
- H4 전용2Hz/18틱 지연/2초 fresh packet은 기존 G 가용성/LOS/radio 경계를 지킨다. G contract를 바꾸지 않고 shareTracksOFF는 항법만 허용한다. field/time/sequence/replay/SPD covariance/caps 전체를 write 전에 검사한다. sender 자기 항법·측정 bid·native 실제 발사 접수만 전송하고 world targetID/peer FCS/탄체 위치·시커·생존/BDA는 금지한다.
- formation은 받은 SELF 항법에 대한 종렬/좌우·1/2/4km desired slot, H2 공통 baseline과 타/기관 명령만 쓴다. 현지 대공 방어/수동NAV·지도/MANUAL/HOLD/masterOFF/기동OFF 우선, 단절/OFF는 반환한다. heading/speed/position 직접 write·순간 배치·간격 보장이 없다.4후보×6자세와 기존교통16+수신선도함1·chart guard로 bounded다.
- 수상전 담당 분담은 fresh 현지 적성 SURFACE·owner AUTO/H1/H3와 각 owner의 별도 동의가 필요하다. 받은 bid를6D측정으로 보수적으로 연관하고 모호하면 보류한다. native bid preview는 요청/발사 없이 exact capability를 finally 복원하며 수동 pending를 빌리지 않는다. primary lease/native release 재검사·임무 전환2.4초 대기·측정 접수2발 뒤90초 보류를 지킨다. 접수는 sender/serial dedup, 동의 소진/lease/heartbeat 만료 뒤 유지하고 BDA가 아니다. 연결이 없거나 못 받은 정보의 보편적 중복 방지는 아니다. teamOFF와 attackOFF는 별도다.
- 별도 SELF_DEFENSE는 반복된 현지 승인 incoming ASM·fresh confirmed SURFACE의 유일한 near-origin 운동학 근거30초만 적성으로 사용하고 operator identity를 바꾸지 않는다. 아군/중립/IFF/G 보호·late weapon FRIEND 우선, alias/expiry/reset/import 승계 없음. friendly 기본IDENTIFIED_ONLY/새enemy SELF_DEFENSE, 아군 별도 발사 동의 유지. IFF 무응답·ESM-only·received HOSTILE·faction·발사원 미관측 첫 공격은 계속 보류한다.
- tight own-hull FRIEND TRACK relay만 자기 항법으로 처리하는 H3 보호 오류 수정을 허용했다. 다른 local file/SELF/NEUTRAL·주변/큰 오차·stale 보고는 보호한다. Harpoon ARH에 IFF를 추가한 것이 아니며 DL0/nativeINS→ARH·RF/physics/damage/effects·CG RAM0/DDG Harpoon0/고정 셀·60/120/20Hz/owner 해상효과·3D는 보존한다.
- fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H4_1`, team `AEGIS_TEAM_TACTICS_H4_1` schema/enabled/mission/formation/spacingM/surfaceRoe만 strict all-owner detached preflight. 현재 missing/type/extra는 zero writes 거부하며 H3/H2/H1/G/F/B/no-fleet은 teamOFF·IDENTIFIED_ONLY migration, pending legacyenemy도 동일하다. 메시지/배정/접수/근거는 deferred이며 import/reset/deploy/retire에서 비우고 H2 operator baseline을 저장한다.
- 최종 원본 직접 1403/1403 PASS,24suites 및 검사/보고/capture SHA와 조건은 H4 evidence/verification-summary.json을 따른다. 역사/draft 수치 합산 금지. H3 네 원본을 same bytes/blob archive로 보존하고 stablev48/assets0~12를 유지한다. §7.1에 따라 원본/support 직접 upload·독립 readback, Actions dispatch/main·선행 PR 병합은 하지 않으며 자동 작업 미실행을 CI PASS로 표시하지 않는다.
- 이후2큰 단계는 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va다. 임의 다수 함대/자유 ROE/모든 발사원 획득·오격/충돌 방지/실제 doctrine/휴대폰 FPS 인증을 완료로 주장하지 않는다.

### 직전 개발 기준 MULTI SHIP H3 — owner 관측 기반 대수상 공격 AI (당시 기록)

- 현재 개발 세트 `v48_WIP_MULTI_SHIP_H3`, HTML 15,683,482 bytes, SHA `0a9626535c209d8ad4e5a9b5262bd826d8ede8df928562534ba6c44b5673d178`, main SHA `904116a4d73455b5a12d4c800afea30fac9e05415d81c0f1c16ce3f37cba38f4`. H2 final `59fad37cc170c760c1659b916febc168021a31b4` 위 `multiship-tactical-h3`, PR base `multiship-tactical-h2`, 현행 support/workflow/checksum은 H3다. 아래 이전 기준은 당시 기록이다.
- canonical root `ShipRuntime.combatSystem.attackH3`, 설정/제한 동의/계획/capability/접수 이력 owner-local. 자함/아군OFF, enemyON. H1 전술 ON + owner AUTO, fresh 현지 SURFACE/명시 HOSTILE + 별도1/2발120초 동의를 요구한다. 적함은 mission 권한이어도 현지 HOSTILE만 허용한다. UNKNOWN/IFF 무응답·shared/ESM-only를 적성/FCS/발사 권한으로 만들지 않는다.
- 5Hz bounded command phase, 파일96/후보16/protected64/log64, 예비2발·enemy90초 살보 재평가·선회120도 상한은 SIM-TUNE이다. 등록 CG departure geometry·native gate·CV route/chart·관측/수신 protected 경로/search basket 검사. actual release 재검사가 최종이다. 정확한 capability 객체만 새 H3 권한이며 generic AUTO/SEMIAUTO, coordinate search와 다른 surface weapons의 MANUAL-only를 완화하지 않는다.
- FLEET 공격 ON/OFF/1~2발 동의/철회는 selected friendly owner에만 작용한다. ON만으로 발사하지 않고 새 동의/ON/OFF는 이전 동의를 지운다. 철회/OFF/MANUAL/HOLD/masterOFF는 준비를 취소한다. 수동 Harpoon/waypoint가 우선하고 actual release만 동의량을 차감한다. 번호/alias는 동의를 승계하지 않는다.
- H3 AI는 비행 Harpoon world state/시커/생존/명중/BDA truth나 peer private FCS를 읽지 않는다. DL0, launch frozen INS cue→독립 ARH 및 native RF/physical/damage/effects는 유지한다. 실제 물리는 기존60/120/20Hz, heading/speed/position 직접 writes나 render physics/RNG가 없다.
- fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H3_1`, attack `AEGIS_SURFACE_ATTACK_H3_1` schema/enabled만 strict detached preflight로 저장한다. 현재 attack missing/type/extra는 zero writes 거부, H2 기존 필수 tactical/maneuver/network도 유지한다. H2/H1/G/F/B/no-fleet의 새 공격 권한은 명시 OFF migration하며 pending deployment에도 적용한다. 동의/계획/capability/log는 deferred, import/reset/deploy/retire에서 비운다.
- 최종 원본 직접 1198/1198 PASS와 조건은 H3 evidence/verification-summary.json을 따른다. 역사/폐기 draft 수치를 합산하지 않는다. 원본 직접 GitHub 업로드는 §7.1 standing authorization을 사용하고 Actions dispatch·main/선행 PR 병합은 실행하지 않는다. automatic smoke blocked를 CI PASS로 표기하지 않는다.
- 후속3큰 단계: H4 팀 전술/합동 기동, 헬기/초수평선 탐지, RGM-109E Block Va. ARH 자체 IFF/보편적 오격 방지·미식별 적성 추론/장거리 offboard firing 완료를 주장하지 않는다.

### 직전 개발 기준 MULTI SHIP H2 — owner 관측 기반 기동 AI

- 현재 개발 세트는 `v48_WIP_MULTI_SHIP_H2`, HTML 15,675,514 bytes, SHA `522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1`, main SHA `80ecfe1be494132521b6f6e1327647f50608c92da98fef235f541ed657926865`다. H1 head `43021f9693dc0500b5f2def531ec5d0d9e17bf0b` 위 `multiship-tactical-h2`, PR base `multiship-tactical-h1`, 최신 support/workflow/checksum은 H2다.
- `ShipRuntime.combatSystem.maneuverH2`가 설정·유틸리티 후보·임시 항법 소유권을 소유한다. 자함 기본OFF·외함 기본ON이며 H1 전술 AI ON + owner AUTO에서 실행한다. 현지 승인 fresh AIR 측정과 자기 장비/조종 상태·native SPG/CIWS 사각만 사용한다. shared/ESM-only는 H1 readiness이며 기동 목표/현지 FCS/살상 권한이 아니다.
- 5Hz fixed command phase,8후보/위협8/교통16/예측 자세6/log64 상한, 첫 판단 즉시·3초 유지/.04 margin·긴급12초는 SIM-TUNE이다. 고정 mission heading으로 목표 누적을 막고 native 기관 단계·타각 명령만 내린다. heading/speed/position을 직접 쓰지 않는다. 실제 chart/신선한 SURFACE 측정·수신 SELF 항법으로 위험 후보를 제외하되 전 해역 충돌 회피를 주장하지 않는다.
- NAV 타각/기관·지도 route와 FLEET 항법은 owner별 지속 manualNav hold다. ON/OFF로 이를 지우지 않고 기동 AI 재개만 명시 인계한다. 기동 재개는 레이더/EW hold를 보존하며 H1 운용 재개는 항법 hold를 해제하지 않는다. MANUAL/SEMIAUTO/HOLD/masterOFF/기동OFF/offline은 임시 orders를 반환한다. 조용한4초 뒤 native RECOVER하고 요청 항법으로 복귀한다. freshness와 실제 선회 시간이 더해진다.
- fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H2_1`/설정 `AEGIS_MANEUVER_UTILITY_H2_1` enabled/manualNav bool·native 기관 metadata를 전 owner detached preflight한다. current wrong/missing/extra fields는 zero writes로 거부한다. H1/G/F/B/no-fleet만 명시 migration하고 기존 manual flags를 항법 hold로 승계한다. `maneuverGoalsScoresAndCommandOwnership`은 deferred이며 reset/import/deployment/retire에서 비운다. save는 임시 AI orders 대신 요청 baseline과 실제 물리 상태를 내보낸다.
- 최종 원본 직접 **883/883 PASS**, 모든 tested SHA/조건/한계는 H2 evidence다. superseded draft/실패한 fixture/역사 수는 합산하지 않는다. H1 HTML/status/SHA/workflow4파일 same bytes/blob을 archive에 보존하고 stable v48·원본 models/profiles·native 물리/유도/damage/RF·60/120/20Hz·방어 gate·Harpoon INS/ARH/DL0·CG RAM0를 유지한다.
- §7.1 승인에 따라 원본 HTML/support를 직접 업로드·독립 readback한다. main/선행 branch는 새 병합 지시 없이 병합하지 않는다. Actions는 dispatch하지 않고 수동 workflow만 준비한다. 다음은 H3 별도 ROE/승인 대수상 공격, 이후 팀 기동/헬기/CEC·RGM-109E Block Va다.

### 직전 개발 기준 MULTI SHIP H1 — owner 유틸리티 방어 AI

- 현재 개발 세트는 `v48_WIP_MULTI_SHIP_H1`, HTML 15,669,638 bytes, SHA `e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058`, main SHA `302352d3dfe47e83fc38d057b002fe46a2e3b12656567dde214561cc28c17105`다. G head `d902d24486918c23d43e3067be16ab03fbaedde2` 위 `multiship-tactical-h1`, support/검사는 `docs/multiship/H1/`, 현재 workflow/support manifest는 H1이다.
- `ShipRuntime.combatSystem.tacticalH1`이 settings/utility/우선 파일/임시 radar·EW 기준값을 소유한다. 자함 기본 OFF·외함 기본 ON이며 해당 owner native AUTO에서만 실행한다. 기존 MANUAL/SEMIAUTO/HOLD 권한을 바꾸지 않는다. FLEET 전술 AI ON/OFF는 수동 권한을 보존하며 AI 운용 재개만 manualRadar/manualEw를 명시 해제한다. 적함에 운용자 FLEET 명령은 금지한다. NAV·ARM·CIC·기존3D는 원래 자함, 선택 owner 조작은 FLEET이라는 G 계약을 유지한다.
- 승인된 fresh 현지 AIR 위협의 측정 KF·접근 시간/속도/품질·미대응, 자기 native 예비탄 이상 재고·SPG 채널·전투/레이더 손상만 점수 입력이다. WATCH/CONSERVE/DEFEND/SATURATED/DEGRADED 비교·2초 유지/.08 margin·긴급12초, 최대96 priority/64 log는 SIM-TUNE이다. native5Hz에서 동일 simStep 평가를 한 번으로 제한하고 RNG/wall clock/상대 truth·생존/시커/peer private FCS는 읽지 않는다.
- utility 순서는 native 자원 배분과 실제 AUTO 추천에 모두 적용한다. 승인 현지 위협3개 이상·선택 SAM pool<2×위협·접근25초 초과·속도600m/s 미만만 native2→1발 살보로 배분한다. 급박/고속·진행 중 pending·NEZ/사각·재고·BDA/reengagement·근접방어·G 보호/lease·실제 release gate는 native를 유지한다.
- 신선한 현지 위협/anonymous ACTIVE_SEEKER ESM/실제 전달 shared THREAT는 readiness만 올린다. 현지 FCS 없이 lethal authority·거리·적성 식별을 만들지 않는다. manual/group 우선권이 없을 때만 개별 radar/EW baseline을 저장해 탐색 방사와 기존 soft-kill AUTO/EA 허용을 임시 적용하며 조용해지면 복귀한다. 그룹 명령 baseline capture 전에 AI 임시 레이더를 반환한다. group lease expiry/link loss 뒤도 요청된 개별 기준값을 보존한다. H1은 항법/route 명령을 쓰지 않는다.
- `AEGIS_NAVAL_PHYSICAL_FLEET_H1_1`과 `AEGIS_UTILITY_TACTICAL_H1_1` settings bool3개를 전 owner detached preflight한다. invalid/missing/extra H1 fields는 zero authoritative writes로 거부하고 G/F/B/no-fleet만 명시 migration한다. `utilityDecisionsPrioritiesAndEffectOwnership`은 deferred다. reset/import/deployment/retire에서 transient를 비우며 임시 AI radar/EW 대신 요청 baseline을 export한다. foreign defense AUTO/HOLD의 E 초기화 계약도 보존한다.
- final SHA 검증/상태/evidence만 완료 판정에 쓴다. superseded draft/test fixture 결과는 합산하지 않는다. G HTML/status/SHA/workflow 네 파일을 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_G/`에 이동한다. stable v48·assets0~12·native 물리/비행/damage/RF·60/120/20Hz·Harpoon INS/ARH/DL0·CG RAM0는 보존한다.
- §7.1 승인에 따라 원본 HTML/support를 직접 업로드하고 독립 remote tree/raw-byte readback한다. main/선행 branch/PR을 새 요청 없이 병합하지 않는다. GitHub Actions는 사용자 조건으로 미실행, workflow_dispatch만 준비한다. 다음 H2는 관측 기반 기동과 수동 항법 우선권, H3는 별도 ROE/승인 대수상 공격이다. 헬기/CEC/팀 기동·RGM-109E Block Va는 후속이다.

### 직전 개발 기준 MULTI SHIP G — FLEET 조작·관측 공유·공동 방어

- 현재 개발 세트는 `v48_WIP_MULTI_SHIP_G`, HTML 15,664,301 bytes, SHA `7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7`, main `a6f5a22de6ca0a4daac033dd05c3a2c03f8b5aeaeb5f97c0b6e8c4c7f2c1911f`다. F head `e4a1ceb6700f1d891e1c11aee0f9519b8ccde9c5` 위 `multiship-network-g`, support는 `docs/multiship/G/`를 따른다.
- FLEET은 새로운 정식 운용 탭이다. `ENGAGEMENT_RUNTIME.fleetOperatorG`는 UI 명령 목적지만, `ShipRuntime.combatSystem.operatorG`는 해당 owner의 현지 표적 선택/명령 결과만 소유한다. 자함·아군 함정의 native 항법/관제/식별/발사 포트로 전달하며 적함 조종·global profile/runtime/PLAYER role 교환은 하지 않는다. NAV·ARM·CIC·기존3D 교전 버튼은 원래 자함 기준이다. 선택 자체는 simulation authority가 없고 reset/import/deployment에서 UI 선택과 target transient를 비운다.
- 수동 발사는 fresh confirmed 현지 파일과 HOSTILE/TRAINING_TARGET 식별만 허용한다. 공유 FRIEND/NEUTRAL·stale/UNKNOWN·AUTO 수동 포트는 보류한다. native 발사 간격·사통/사각·재고/손상 재검증을 유지한다. 함포 마운트와 Harpoon 설치 유무도 owner profile에서 따르며 CG RAM0/Harpoon8·DDG Harpoon0을 보존한다.
- 네트워크는 friendly 인증 self 항법/오차와 실제 local KF 관측/공분산/시각/분류·식별만 전송한다. 2Hz/.3s delay/2s fresh/12s coast, bounded receiver 파일과 보수적 covariance intersection은 SIM-TUNE이다. 공유 정정은 detached CIC 표시용이며 canonical EKF/FCS에 원격 파일을 쓰지 않는다. 현지 승인과 전달된 bid/lease에 한정한 SAM 담당 분담, 긴급 방어/단절 복귀가 있고 CEC 사통·Harpoon DL은 없다.
- 그룹 EMCON은 각 함정의 개별 기준값을 보존하는 지연 lease다. 링크 무선은 레이더 침묵과 구분하며 단절 시 개별 운용으로 복귀한다. bool/enum 설정을 fleet G_1 strict preflight 후 복원하고 F/B 저장은 명시 migration만 한다. peer/report/lease/group runtime은 저장하지 않는다.
- Harpoon 오인 완화는 발사 승인과 이전 레이더 추적의 위치/속도 오차·기동 여유/시각만 읽는다. 최초 연관은 기존 발사 회랑을 유지하고 이후 notch/turn/alias 재획득은8초 이내, 모호하면 UNKNOWN/자동교전 보류다. 표시 coast4초와 DL0, 미사일 actual INS/seeker/truth 비접근을 유지한다.
- 3D 아군함 보기 버튼의 pointer-events와 실제 native 입력을 고치고 focus/reset/retire에 레이블을 동기화했다. 실제 pointer/touch와 RAF 이후 camera world position/함정 중심/복귀를 확인한다. render는 physics/RNG를 진행하지 않는다.
- final SHA 검사와 원격 검증은 G evidence/상태/SHA를 따른다. superseded 테스트 SHA를 final로 바꾸지 않는다. 원본 F 네 파일은 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_F/`에 보존한다. stable v48과 원본 모델 assets0~12, 60/120/20Hz/물리·비행 커널을 유지한다. §7.1에 따라 원본을 직접 upload/readback하고 Actions는 사용 불가로 dispatch하지 않는다. main/선행 PR을 임의 병합하지 않는다.
- 다음 H는 현지 관측 기반 방어 태세·기동/공격 전술 AI다. 헬기/CEC·RGM-109E Block Va는 후속이다. DDG 실제 EW antenna 등록과 IFF 재인증 한계는 F 그대로이며 별도 문서로 추적한다.

### 직전 개발 기준 MULTI SHIP F — 배치 분리·receiver 전자전·함정 해상효과

- 현재 개발 HTML/status/SHA 토큰은 `v48_WIP_MULTI_SHIP_F`, HTML 15,638,513 bytes, SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`, main `cbed31af60addb8a757225251783df462336c449730975d1a5d836fc7c487b16`. E head `bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6` 위 `multiship-ew-f`이며 지원·검증은 `docs/multiship/F/`를 따른다. stable v48과 original profiles/models/physics kernels는 보존한다.
- 출항 전 near ALLY/far ENEMY(10~30km)·각 radar EMCON·hulk·항공기 선택. role/faction을 sensor truth identity로 바꾸지 않는다. 일반3D focus는 아군만이며 진단 적 focus는 DIAGNOSTIC_ONLY다.
- `ShipRuntime.ew.executionF`와 47개 원본 owner soft-kill closure로 ESM/SLQ-32·Nulka/SRBOC 실행을 분리했다. anonymous receiver plot은 방위/sigma/세기/품질/대역/계열/시각만 받고 truth ID/좌표를 거부한다. noise/replay는 실제 수신 전력/빔·대역·장비/지형/기상에서 합성하고 기존 seeker/echo frontend로 적용한다. 기존 대역 I/J/X이며 SPY S-band에 임의 적용하지 않는다. 기본 외함 AUTO는 자기 측정 cue만 사용하고 자원/탄약/질량은 owner-local이다.
- 초기 EMCON은 탐색 레이더 침묵이다. 방어 ECM·수동ESM과 구분한다. IFF 측정은 기존 fresh SURFACE 트랙의 FRIEND/WITHHELD 보호용이다. network/CEC/전술 공격·기동 AI는 아직 없다. Harpoon DL0·INS→ARH와 CG 양현 Phalanx/RAM0을 유지한다.
- 자함의 원본 ocean shader/kernel을 그대로 보존하고 외함 함수파2+항적/선미 포말3개를 owner geometry/world history로 표시한다. 효과는 60초/255점 bounded, physics/RNG feedback0이며 import/reset/retire 때 owner layer/material/geometry를 폐기한다.
- F strict snapshot은 두 fleet owner/role/faction/profile·EW bools·seed·soft-kill 재고를 preflight하고 실패 시 무변경 거부한다. legacy A/E/B는 명시 migration만 한다. 설정/재고는 복원하되 contacts/기법 timeline·flight/track/예약은 transient다.
- 최종 직접 593/593 PASS: 세 척1/8/16/64×1536 ticks exact·두 함종 natural Kh-35U EW/시커·실제3D 피격/복원·기존 defense/무장/Harpoon 검증. ESM 난수를 격리했으므로 E의 shared combat RNG epoch와 raid 순서는 같다고 주장하지 않는다. paired fixture의 CG VLS1셀 delta를 기록했다.
- CG는 등록된 SLQ-32 양현 위치/손상, DDG는 원본 EW antenna registry 부재로 legacy RF 기준점과 CDC/발전기/offline 가용성을 사용한다. DDG 실제 antenna 등록과 IFF 재인증·운용자 해제는 후속 보완이다. RF/IFF/ECCM 값은 SIM-TUNE, SwiftShader는 하드웨어 FPS 인증이 아니다.
- E HTML/status/SHA/workflow는 same bytes로 `archive/v48/WIP_MULTI_SHIP_E/`에 보존한다. §7.1 직접 upload/readback을 수행한다. 사용자가 Actions 불가를 명시했으므로 이번 마감은 로컬 직접 검사이며 workflow는 수동 준비·미실행이다. main/선행 PR을 새 요청 없이 병합하지 않는다. 다음은 measured friendly network/정정/EMCON 기반이며 Tomahawk 미래 대상은 RGM-109E Block Va다.

### 직전 개발 기준 MULTI SHIP E — 방어 AUTO/BDA·출항 전 항공기 설정

- HTML/status/SHA 토큰은 `v48_WIP_MULTI_SHIP_E`, HTML 15,609,329 bytes, SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`, decoded main SHA `446f96c11279970cda4d9e5542137dad96ba86ee155f3f503cbf83fa51f2c105`. 지원/검사는 `docs/multiship/E/`, 현재 workflow/manifest는 E다.
- D head `c6da52b960b447d8b4eadb6cac904b9c0ebff730` 위에서 원본 AUTO/BDA/alias 67개 함수를 기존 owner closure에 결속했다. immutable profile/원본 모델·stable v48·공통 world1회·60/120/20Hz를 유지한다. 실제 발사 직전에도 관측/식별·권한·사각·장비·재고를 재검사한다.
- 적함은 기본 방어 AUTO이며 기존 measured hostile-intent와 보호 identity/ROE를 사용한다. effect/후속 coherent observation/alias 지원 이관은 owner-local이다. 실제 alive/truth로 격추를 확정하지 않는다. 독립 C55 확인 관측으로 RAM/Phalanx를 연속 실행한다. CG에 SeaRAM을 추가하지 않는다.
- 출항 전 적 항공기 ON/OFF는 두 UI에서 동기화되고 `AEGIS_DEPLOYMENT_MULTI_SHIP_E_1`로 저장한다. legacy A_1은 ON으로 명시 migration한다. OFF는 정상 초기/주기/reset/새 해역 스폰을 막고 시계·스폰 난수를 소비하지 않는다. 전투 transient/BDA/진행 살보는 저장 복원하지 않는다.
- 실탄 Harpoon 시험에서 DDG는 자동 ESSM을 발사했으나 해당 seed에서 접촉도 발생했다. CG의 저고도 접근은 확인된 ASM 관측이 없어 발사0이며, 별도의 자연 20m Kh-35U에서는 실제 Phalanx 방어를 확인한다. 센서 검출과 격추율 보장은 없다. EW/공격·기동/헬기는 후속이며 Harpoon DL=0을 유지한다.
- D HTML/status/SHA/workflow는 같은 bytes로 `archive/v48/WIP_MULTI_SHIP_D/`에 보존한다. §7.1에 따라 `multiship-defense-e` 원본 HTML 업로드/readback·D 위 PR/최신 head CI를 수행한다. main/A/B/C/D 병합은 새 요청 없이 실행하지 않는다. 최종 결과는 E 상태/evidence와 PR checks를 따른다.

### 직전 개발 기준 MULTI SHIP D — owner 무장·실물 접촉/shadow

- D 원본 HTML SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`, 15,575,097 bytes. PR #48은 C 위 미병합이며 D original status/evidence를 archive/지원에 보존한다. D의 active enemyAI 미구현 설명은 당시 기록이다.

### 직전 개발 기준 MULTI SHIP C — 함정별 관측·외부 관측 포트

- 이번 범위는 4단계다. HTML/status/SHA는 `v48_WIP_MULTI_SHIP_C`, 지원은 `docs/multiship/C/`, HTML 15,344,725 bytes, SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`, main SHA `d68eca1dbe2b3b6c491ba4f9d2de9c5ccbcb34221ee7d3f02631fd897925094e`.
- 기준 B head `ae94326caea7cd0329233f381933cdc240bedb47`·B HTML SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`. B 세트/workflow를 동일 bytes로 archive에 보존한다. 현재 workflow/manifest는 C, 역사 B 자료는 그대로다. stable v48과 원본 assets/profile/module revision은 유지한다.
- 자함은 기존 canonical scheduler/TrackStore, 비자함은 runtime-owned observer와 독립 RNG/scan/rotor/track을 사용한다. 공유 RF/측정/EKF에 명시 receiver를 전달한다. ACTIVE/global profile 교환 없이 fixed tick마다 각 owner 한 번, 공통 세계 한 번 진행한다.
- 함종 face normal·sensor suite·budget·지평선/지형/원본 CG 사각·해면 clutter·손상/EMCON을 반영한 익명 plot만 연관한다. 식별/자동권한은 별개이며 자함 CIC는 자함 관측만 읽는다. 진단 truth/가상 높은 receiver를 실제 센서나 AI 입력으로 연결하지 않는다.
- 외부 관측 포트는 source/sequence/measuredAt/추정 위치/SPD 공분산/domain evidence와 지연·링크 상태만 받는다. truth field·재전송/반복 fix·오래된/미래 시각을 검증하고 measured age를 유지한다. 헬기 모델/비행/센서는 아직 없다. Harpoon은 DL=0이며 발사 후 탄 정보를 이 포트로 받지 않는다.
- 저장에는 offboardLinksAndReports를 deferred로 명시한다. 정상 reset/import/retire는 combat transient를 비우며 잘못된 import는 zero mutation이다. 실제 owner radar 회전각을 renderer가 읽으며 화면은 시뮬레이션을 진행하지 않는다.
- 5단계 실제 탄 source/target routing·양방향 무장, 6단계 receiver별 EW, 7단계 관측 기반 AI는 후속 범위다. 일반 seeker에 naval reflector를 켤 때 실제 contact routing도 함께 검증한다. 60/120/20 Hz는 유지한다. SwiftShader native 관측은 실제 mobile FPS가 아니다.
- 7.1에 따라 `multiship-sensors-c`에 원본 HTML/support를 직접 업로드/readback하고 B branch 위에 PR/CI를 만든다. 새 병합 지시가 없으므로 A/B/C는 임의 병합하지 않는다. 최종 판정/원격 증거는 최신 상태와 C evidence/GitHub checks를 따른다.

### 직전 개발 기준 MULTI SHIP B — 실제 함정 물리·피해·표시

- 이번 범위는 다함정 3단계다. HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_B.html`, 상태/SHA 같은 토큰, 지원 `docs/multiship/B/`를 따른다. HTML 15,328,273 bytes, SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`, main SHA `2d20d1927a47443aaaadc084faae07e21b6009baae4d78e055f600ecd143319c`.
- 기준 A head `3fab03782abb313cd3ece1bbfe254cdb77981231`, A HTML SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`. A 세트/workflow를 `archive/v48/WIP_MULTI_SHIP_A/`에 같은 bytes로 보존한다. A 당시 support manifest는 역사 자료다. current workflow/manifest는 B다. stable v48과 packed asset records 0~12, 함종/무장 revision을 유지한다.
- 선택한 적함은 출항 때 PHYSICAL_ACTIVE가 되어 world navalShips에 연결한다. 함정별 navigation/flood/survival/control/interior/crew/mass/dynamics/wave/rescue를 shared owner API로 진행한다. 원본 DDG/CG builder를 함정별 root/material/job과 사용하며 global profile swap·render 물리 적분·상대 truth CIC 주입은 없다.
- deploymentState NONE/PENDING/ACTIVE를 구분하며 초기 선택 단계에도 정상 export/preflight가 된다. fleet state는 독립 detached 준비 후 복원하고 잘못된 입력은 zero mutation으로 거부한다. 저장의 fire/DC/structural timeline·body rates·combat transient 제외와 legacy/PENDING 새 배치를 명시한다.
- 함체 접촉은 profile footprint/질량 기반 비탄성 충격과 bounded SIM-TUNE 개구다. 좌초 정지는 대상 owner만 적용한다. 60 Hz tick/120 Hz 침수·힘/20 Hz hydro, world weather 한 번, 독립 전투 RNG를 보존한다.
- 4단계 센서/트랙 observer 분리, 5단계 실제 탄 source/target routing·양방향 무장, 6단계 receiver별 EW/CIC, 7단계 관측 기반 AI는 미완료다. B의 physical probe/native 구멍 검사는 자연 미사일 명중·적 AI·mobile FPS 인증이 아니다. 공개 UI는 배치/카메라와 기존 자함 운용이다.
- 7.1에 따라 Codex가 원본 HTML과 지원을 직접 push/readback한다. B branch는 `multiship-physics-b`이며 미병합 A PR #45 위에 연결한다. 이번 B 병합 요청은 없으므로 A/B를 임의 병합하지 않는다. 실제 최종 검증/PR/CI 상태는 B 상태·evidence와 GitHub 기록을 따른다.

### 직전 개발 기준 MULTI SHIP A — 독립 상태·출항 전 배치 설정

- 이번 승인 범위는 다함정 작업의 1~2단계다. HTML은 `Aegis_SIM_v48_WIP_MULTI_SHIP_A.html`, 상태/SHA는 같은 토큰이며 지원은 `docs/multiship/A/`다. HTML 15,314,629 bytes, SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`, main SHA `8cb35bd169cb6de69270297bf33222bec337055da19f64519936917c267089c8`.
- 기준은 PR #44 병합 main `cb70a637105ce00e7c0619270237cc35a83d39c2`의 Harpoon E다. E HTML/status/SHA와 당시 workflow는 `archive/v48/WIP_HARPOON_E/`에 same bytes로 이동하며 E의 profile/module revision과 전투 모델은 바꾸지 않는다. stable v48도 같은 bytes다.
- 표적함 HULK/NONE, 적함 준비 null/DDG/CG를 초기 함선 선택과 VLS 편성에서 지정·출항 확정한다. 기본은 HULK/적함 없음이다. NONE은 실제 기본 표적 생성·reset에 반영한다. 출항 후 변경 금지다.
- `createPreparedShipRuntimeA`는 불변 프로필·공통 생성 함수로 독립 core 모델·재고·센서/FCS/EW 준비 버퍼를 만든다. 가변 상태 복사나 함종 전역 swap을 사용하지 않는다. 명시적 runtime getter·살아 있는 context binding·가변 객체 소유권 guard를 사용하며 기존 자함 alias/UI를 유지한다.
- 적함은 STATE_BOUND_INACTIVE다. registered 2와 simulated 1을 구분하고 world/weather/ordnance·기존 ownship loop를 함정 수만큼 실행하지 않는다. 적함의 실제 model/world 배치·physics tick·observer measurement·무장 routing·EW·AI는 3~8단계다. 미연결 적함 함포 command/solve/fire/step은 명시적으로 거부한다. rescue는 provision만 준비하고 world/controller 연결을 3단계로 미룬다.
- 불변 피해 등록은 pinned E에서 함종별로 캡처한 기존 hitbox/material/ID다. geometry/revision 변경 시 재등록과 baseline 비교가 필요하다. 자함의 기존 hitbox 생성 경로를 유지한다.
- 운용 저장은 deployment codec을 포함한다. 옛 배치 누락은 HULK/적함 없음으로 명시 migration한다. 모든 codec 검사 후 detached 준비/적용하며 거부는 world·상태·난수 zero-mutation이다. 적함 transient/비행/EW timeline 복원으로 취급하지 않는다. 상세 의존성과 검사 범위는 `docs/multiship/A/DEPENDENCIES.md`와 최신 상태를 따른다.
- 원격 브랜치 `multiship-runtime-a`의 사용자 HTML 업로드 commit `28dfc4fcefb22e8c0989617b2212e37d096c05d6`은 기준 main을 parent로 가지며 로컬 검증본과 byte-identical이다. 이 revision은 지원 파일·기존 E blob archive 이동·직접 업로드 규칙을 포함한다. 7.1은 사용자 승인으로 원본 HTML 직접 업로드/원격 확인을 허용하도록 바꿨다. PR과 같은 bytes CI의 실제 결과는 GitHub 기록을 따른다. 최신 workflow/manifest는 Multi Ship A이며 archived E는 역사 기록이다.
- 후속 착수는 3단계의 실제 두 함정 물리·피해·표시다. 4단계 observer truth boundary와 5~7단계 양방향 요격·공격/EW/AI 완료 전에는 적함 교전이 구현되었다고 표시하지 않는다. 실제 mobile FPS/heap/GPU 측정은 소프트웨어 WebGL 결과와 구분한다.

### 직전 병합 기준 HARPOON E — 경유점/최종 통과 ARH

- 최신 E HTML 15,285,590 bytes, SHA `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`, main SHA `11cf8d757821b8601da5a3a50153666e48524ea31a33de1a88d7a11a72794067`. status/SHA/README/지원 E가 같은 인계다.
- HARPOON FIRE 아래 지정/해제 native click, 최대8 CIC 점·NAV/락온 분리·drag/pinch 점 추가0. 해제는 초안 clear/cursor 복귀. 마지막 점은 탐색 시작이며 final leg 전방8km/반경4km fixed search area다. route shot은 MANUAL 좌표 계획, 보호 수상 file/자동교전 금지. 경유점 없는 관측 track memory shot을 보존한다.
- pending에 자동 관/전체 immutable program pin. 실제 release safety/reinventory/권한/손상/경로 예산 재검사; 실패는 draft 보존·ammo/mass0, 성공은 clear/edit off. 탄 간 route 독립, flight index/passes는 world missile-owned INS only. 최종은 500m corridor 평면 통과, 중간200m flyby. 마지막 전 seeker OFF, 통과 후 SEARCH/ACQUIRE/TRACK/COAST.
- SIM-TUNE 총 경로+8km search+2km turn reserve ≤140km/fuel110kg·0.225kg/s/최소leg2km. public124/secondary약140 분리. measured vertical extent≥3.5m/Doppler spread≤2.5m/s로 anonymous echo filtering; 작은 선박/거친 해면 감도 제한 명시. physical RF/LOS/gimbals/alpha-beta/fuze/contact/피해·3.2초부스터/model/nozzle/smoke·asset/renderer와 stable v48 byte 보존이다.
- DL0·초안만 CIC draw/release즉시삭제·world flight 진행/시커/생존/명중 ship UI 접근0. launch-time 알려진 route first point는 초기 익명 radar 상관에만 쓰고 이후측정continuity로 FRIEND/관측만료 위치없음 유지.
- CG E_1/module RGM84D_BLOCK1C_E1(weapon revision HARPOON_E1), inventory A1/C·B·A·G·D legacy명시. routes/flight transient는 save capability deferred, 정상reset/import clear/preflightfail mutation0.
- 동일 최종 SHA 직접 178/178, 역사합산0. 120/124/130km×0/15kt6/6 physicalcontact/empty-sea noforcedTRACK/hit, 단일seed·hulk210m·terrainbypass·focused60Hz actualenv/target/ordnance. 일반hitprobability/140km전체조건인증0. track-onlypredictionbasket제한은 그대로다. 필터 전2contact4miss는 예비 evidence 별도.
- full accumulator1/8/16/64×각3072ticks exact, realmap/button/touch/reset/import/DDG·8관재고/손상/권한·realRF radar/CIC 무DL, native640×4802routes2fires/fullRAF/clock/caps/booster/draw/reset/UIfit faults0; manualphysics/geometryqueue0·SwiftShader/FPSclaim0.
- D HTML/status/SHA·workflow는 당시 bytes로 로컬 archive/역사 지원에 보존한다. 큰 A/B/C/D HTML은 원격 신규 업로드하지 않으며 K+작은 A/B/C/D/E 모듈로 E까지 exact 재구성한다. 현재 workflow/manifest는 E다. 7.1에 따른 사용자 E 업로드 `a96053ba1dc56389822c17c92a632f21fcc446b2`의 parent/bytes/SHA/Git blob을 대조했고 원격 무결성 검사도 통과했다. 이 revision은 작은 지원·상태/SHA·E workflow와 K 기존 blob의 archive 이동을 포함한다. PR #44의 해당 head 전체 Actions 성공을 확인한 뒤 요청된 merge commit 병합을 진행한다. 실제 CI/병합 결과는 PR 기록을 따른다. 과거 인계·evidence·전달 ZIP은 당시 기록으로 보존한다.
- 자세한 scope는 docs/harpoon/E/README.md와 evidence/status를 따른다. 다음 기능은 이 인계 뒤 진행한다.

### 직전 로컬 비교 HARPOON D — 발사관 자동 선택

- 최신 파일 `Aegis_SIM_v48_WIP_HARPOON_D.html`, 15,283,086 bytes, SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`, main SHA `aeaf6981dc163f3ae3ed67884830bfffb4df50eab83adb381edceda73039e683`. root status/SHA/README/지침/D지원이 같은 인계다.
- 장전된 관 중 기존 권한·관측·INS basket·함정·손상·발사 geometry gates를 통과한 후보를 관측 표적 예상 방향의 최소 초기 선회각으로 고른다. 동률은 profile 순서이고 truth/RNG는 쓰지 않는다. UI는 AUTO label, 발사는 수동 버튼이다. 요청 후 관을 pin하고 실제 release gate를 재확인하며 실패 시 취소한다.
- 선호 bank 소진/손상 fallback·고정 관 ID/재고·cooldown/권한/무DL을 유지한다. selectedTubeId는 저장 호환 field이며 옛 빈 관 선택을 다음 요청에 강제하지 않는다. C profile revision/module/inventory schema 그대로, 비행/INS/ARH/RF/피해/renderer/모델/boost·assets와 stable v48 byte 보존이다.
- 직접 67/67 PASS: static31/selection24/clock3/native9. 같은 최종 SHA, 실제8회 버튼/손상·취소·pending pin·저장/reset·DDG, 1·8·16·64× 각128틱 full accumulator exact, 모바일 native RAF 실제 두 관 덮개·오류0. 수동physics/geometryqueue0, SwiftShader. C 전체155·B133·A155·K284를 D에서 재실행/합산한 것으로 쓰지 않는다.
- C HTML/status/SHA를 archive/v48/WIP_HARPOON_C/로 same bytes 이동하고 C workflow/manifest를 역사 보존한다. 현재 workflow/manifest는 D다. 원자료 candidate.html과 전달 HTML은 same bytes다.
- 준비 harpoon-block1c-a/main K f51247496725aa8aadad69d5c8d3449c5bbc3a81와 권한 재확인. 7.1에 따라 최신 **D HTML 하나만** 사용자 업로드 → exact확인 → small support·K blob archive·Dworkflow → PR/CI. 새 remote upload/PR/CI/병합 미실행. A/B/C archive 큰 HTML은 remote 신규 업로드하지 않고 K+작은 모듈로 exact 기준을 재구성한다.
- 자세한 scope/한계는 docs/harpoon/D/README.md·최신 status·evidence다. 후속 docs/harpoon/long-range/D/REPORT.md에 같은 HTML의60~124km 별도 시험을 기록했다. 정상100·120·124km가4km prediction gate로 차단되며 독립 비행124km/15kn은 최근접190.775m·연료 소진·508초 SEA_IMPACT, exact 위치/시간 재현이다. 자동 선택67/67에 장거리 전체 PASS를 합산하지 않는다. 합성 외부 cue/한 seed/hulk/개방수역/focused60Hz 범위이며 실제 offboard/UI/함상 장거리 radar/native 임무 성공은 검증하지 않았다. HTML·튜닝은 unchanged, 알려진 장거리 제한은 미수정이다. 다음은 forecast uncertainty/search basket/발사 조건과 moving TRACK/COAST 종말 안정성 수정이 적 수상함 기능 확대보다 우선이다.

### 직전 로컬 비교 HARPOON C — INS·ARH 상태·무DL CIC

- 최신 파일 `Aegis_SIM_v48_WIP_HARPOON_C.html`, 15,281,856 bytes, SHA `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`, main SHA `6bf7962f50dba000c58f8abc937f302b357511bdb5258113c98472e399ce72a2`. 최신 status/SHA/README/C지원은 같은 인계다.
- ship 표시/연관은 발사 기록·익명 관측 file만 사용한다. 물리 Harpoon owner-ID/현재 위치·INS·시커·생존·명중을 CIC/발사 패널에 전달하지 않는다. RF reflector는 보존한다. 12초 초기 corridor·3개 측정·0.15초 연속성·one-to-one/모호 UNKNOWN은 SIM-TUNE이며 IFF가 아니다. FRIEND/청록·보류; 관측 상실은 EST/공분산, ship knowledge 위치는 4초 뒤 만료한다. DL을 새로 만들지 않는다.
- INS IMU delta-v/gyro·bias 적분/명시 release epoch·measurement age 중복 방지·측정 radar AGL, ARH OFF/SEARCH/ACQUIRE/TRACK/COAST와 좌우 sweep·양 축 gimbal/beam/range/SNR/Doppler/extent/basket gate를 사용한다. 시커 gimbal±45°/±30°·beam16°/20°·scan30°/s·slew90°/s·3hit/0.35초gap/4초coast는 공개 확인되지 않은 SIM-TUNE이다. 3D는 observer이고 Harpoon AUX CIC는 자함 중심/관측만 표시한다.
- B의 3.2초48kN·질량·분리·모델/후미/nozzle·heavy smoke·관 cut/법선 및 원본 asset은 exact 보존한다. CG revision C_1/module HARPOON_C1, inventory schema A1·명시 A/B/G/D 저장 호환. launch knowledge/비행은 transient로 저장하지 않는다.
- 직접 155/155 PASS, static32, guidance33, knowledge20, runtime29, stage11, salvo9, native16, salvo_identity5. 같은 최종 SHA/1·8·16·64× exact/오류0. B133/A155/K284와 합산하지 않는다. native 전체clock/RAF·실제UI·수동physics/geometryqueue0, SwiftShader 한계를 명시한다. B의 전체native36·CG30/DDG14를 전부 C에서 재실행한 것으로 쓰지 않는다.
- 준비 harpoon-block1c-a/main K f51247496725aa8aadad69d5c8d3449c5bbc3a81·권한 재확인. 7.1에 따라 **최신 C HTML 하나만** 사용자 업로드 → exact확인 → small support·K blob archive·Cworkflow → PR/CI. 새 remote upload/PR/CI/병합은 미실행이다. A/B archive HTML은 remote에 없으므로 새 큰 업로드하지 않고 K+작은 모듈로 exact 비교본을 만든다.
- B HTML/status/SHA를 로컬 archive/v48/WIP_HARPOON_B/에 same bytes 이동하고 Bworkflow/Bmanifest는 역사 보존한다. 현재 검사는 C manifest다. 자세한 범위·한계는 docs/harpoon/C/README.md·최신 status·evidence를 따른다.

### 직전 로컬 비교 HARPOON B — nozzle·빈 관·짙은 후연·3.2초 부스터

- 최신 개발 파일 `Aegis_SIM_v48_WIP_HARPOON_B.html`, 15,274,780 bytes, SHA `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`, main SHA `3e5db4f820844d3301617f5c3e21e69f03619e05dba056532483954a6c88ecbf`. 상태·SHA·README와 B 지원을 같은 인계로 갱신한다.
- 사용자 요청을 따라 부스터 burn 3.2초·평균 48kN을 SIM-TUNE으로 분리한다. public 참고 53kN/2.9초와 nominal impulse를 보존하며 질량 감소 시간도 3.2초를 따른다. CG revision `BUNKERHILL_HARPOON_B_1`, 모듈 `HARPOON_B1`, 관 schema `MK141_INVENTORY_A1` 및 명시적 A 저장 호환이다.
- 부스터 분리 뒤 본체 aft fairing/open nozzle·부스터 nozzle, stage/thrust 연동 core/outer plume를 사용한다. 후연이 많은 고체 추진제는 사용자 가정의 VISUAL-TUNE이며 공개 propulsion chemistry로 주장하지 않는다. 새 heavy trail은 boost에서만 만들고 분리 후 기존 구름만 남긴다. 표시 RNG/pool과 fixed-step 권위를 분리한다.
- 원본 8관의 front116/rear58 covers, 실제 bore와 rack 지지판의 국부 원형 절단을 적용한다. 정수 normalized 법선은 Float32로 복호화·보간하며 geometry source collision/장비 피해는 원본 자료를 유지한다. unrelated combat/ship/renderer source와 기존 asset은 허용 diff 외에 A와 byte 동일이다.
- 직접 B 133/133 PASS: static48/runtime29/stage11/native36/salvo9. core/page/native console 및 simulation/presentation fault 0. native 두 번째 firing은 전체 frame clock이고 수동 physics/geometry queue 진행이 없다. 빈 관 사진만 읽기 전용 geometry 검사 카메라로 촬영했다. SwiftShader 검사와 120초 native stage wait 한계를 명시하고 사용자 FPS를 주장하지 않는다.
- main/기존 `harpoon-block1c-a`는 재확인 시 K commit `f51247496725aa8aadad69d5c8d3449c5bbc3a81`이며 권한 확인. **7.1에 따라 최신 B HTML 하나만** 사용자 업로드한 뒤 exact 대조 → 작은 support/문서/체크섬/기존 K blob archive/B workflow → PR/동일 bytes CI를 진행한다. 새 remote HTML/support/PR/CI/병합은 미실행이다.
- A HTML/status/SHA는 로컬 archive에 same bytes 보존한다. **A HTML은 remote에 없으므로 archive의 A HTML을 API/Git로 새 업로드하지 않는다.** A 비교는 기존 remote K blob+작은 A 모듈에서 exact 재생성한다. A workflow와 옛 manifest는 역사 근거이고 현재 검사는 B manifest다. K blob은 동일 object 이동이며 선행 역사 root fixture 예외를 유지한다.
- 최신 지원 `docs/harpoon/B/`, 상태 `AEGIS_PLAN_STATUS_v48_WIP_HARPOON_B.md`, SHA `SHA256SUMS_v48_WIP_HARPOON_B.txt`. 다음은 업로드 인계 완료 뒤 적 수상함 runtime/시나리오 확대다. 헬리콥터·offboard targeting·경유점/pop-up·다함전·최대 사거리 인증은 이번 범위에 넣지 않는다.

### 직전 로컬 비교 HARPOON A — CG-52 수동 RGM-84D

이하 A 항목은 당시 기록이다. 파일 세트는 로컬 archive에 보존했고 업로드 대상/현재 작업 계약은 위 B가 우선한다.


- 최신 개발 파일 `Aegis_SIM_v48_WIP_HARPOON_A.html`, 14,962,500 bytes, SHA-256 `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`; main SHA `73891bfbf0030d92323a640eee39a236610ed8d7d7f2f1586463dc3cf1a29bac`.
- K PR #43은 `main@f51247496725aa8aadad69d5c8d3449c5bbc3a81`으로 병합 완료했다. 그 기준에서 `harpoon-block1c-a` remote branch를 생성했다. 7.1 사용자 HTML 업로드 분담을 유지하며 새 HTML/support/PR/CI/병합은 아직 원격 미완료다.
- 원본 CG Mk 141 8관의 입구·후방·축·전방 덮개를 등록했다. ARM → VLS 전용 수동 발사, 고정 관별 재고, 실제 release 권한 재확인, 발사 질량 690kg 제거, CG revision `BUNKERHILL_HARPOON_A_1`과 explicit legacy inventory migration을 연결한다. DDG에는 설치하지 않는다.
- 발사 시점 관측 KF 위치·속도·공분산을 동결한 INS → 공통 물리 RF 풀에서 얻은 익명 관측의 독립 ARH. data link/illuminator/자동발사는 없다. 유도에 표적 truth ID를 전달하지 않으며 실제 hull swept contact 이후에만 공통 관통·지연신관·피해·침수를 적용한다.
- 기존 Kh-35U/Kh-32 프로필·핵심 비행 함수의 bytes를 유지한다. 공유 대기·해면·RF·종말 기반을 재사용하지만 Harpoon 비행은 함상 booster/관 구속을 포함한 별도 점질량 프로필이다. 60/120/20 Hz와 격리된 결정적 RNG를 유지한다.
- 실제 native RAF에서 덮개·날개 전개·분리 booster·피격 후 draw/camera·RESET/cache를 검사했다. 모델 24,133 triangles와 Civorsky/CC BY 4.0 attribution을 보존하고 균일색 텍스처를 재질 색으로 변환했다. renderer는 물리 권위가 없다.
- A 직접 155/155 PASS(정적 58/runtime 29/native 15/64× 8발 workload 9/CG 기존 30/DDG 기존 14), core/page/native console errors 0. 실제 1/8/16/64× scheduler 결과 exact. native backend SwiftShader이며 사용자 하드웨어 FPS로 해석하지 않는다. K의 과거 284건과 합산하거나 모두 A에서 재실행했다고 쓰지 않는다.
- RGM-84D 공개 치수·중량·명목 속도·architecture를 적용하고 124/140km 자료 차이를 기록한다. CG 퇴역 직전 적재 block은 미확정이다. 시커 숫자·공력·연료·오차·고도·신관·전개 관절은 SIM-TUNE이다. source/범위는 `docs/harpoon/A/SOURCES.md`를 따른다.
- 피해 대상은 기존 물리 표적함 경로다. 다음은 사용자 업로드 exact 확인 → small support/새 workflow/PR/CI, 그 뒤 적 수상함 runtime·시나리오 확대다. 다함전·헬리콥터·경유점/pop-up·offboard targeting·최대 사거리 인증은 미구현/미검증 범위로 명시한다.
- K HTML·상태·SHA 세트를 `archive/v48/WIP_BUNKERHILL_K/`로 bytes 동일 이동했다. 역사 checksum의 당시 경로는 유지하고 새 root checksum/support manifest를 현재 검사에 사용한다. K workflow는 root K가 있을 때만 실행하며 archive를 자동 실행 후보로 고르지 않는다. 선행 legacy root baseline의 역사 검사 호환 예외는 유지한다.
- 상태 `AEGIS_PLAN_STATUS_v48_WIP_HARPOON_A.md`, SHA `SHA256SUMS_v48_WIP_HARPOON_A.txt`, 지원 `docs/harpoon/A/`. 원자료 `experimental.html`과 최종 명명본의 bytes가 같으므로 입력명을 바꿔 과거 evidence를 재작성하지 않는다.

### 직전 병합 후보 K — 함선별 SPY CIC·퇴함 구명뗏목

- 최신 파일 `Aegis_SIM_v48_WIP_BUNKERHILL_K.html`, 14,458,866 bytes, SHA-256 `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`. main SHA-256 `dbf339daa731b3b86408a1c5bb3c52e718975f5ad82b78d0ae76484b6db69897`.
- CG CIC는 등록된 전·후·양현 SPY 중심각으로 경계·부하 호·F1–F4를 그린다. DDG의 기존 대각선 도식은 pixel exact로 유지한다. 작동 상태 검사도 선택 함선 배열의 장비명을 사용하므로 CG의 손상 OFF가 실제 센서와 CIC에 함께 반영된다.
- USN Mark 7 공개 정원 25명을 공유 모듈로 적용했다. 실제 경로를 따라 도착한 생존자부터 순차 탑승하며 사망자·중복·막힌 탈출은 자동 탑승하지 않는다. 정상 전원 퇴함 fixture에서 CG 330명/14척/마지막 5명, DDG 310명/13척/마지막 10명을 확인했다.
- 함선별 정원으로 충분한 뗏목을 제공하는 상한, 양현 후방 진수 지점, 형상·크기·4초 간격·바람 표류·접촉은 SIM-TUNE이다. 정확한 CG-52 비치 수량·진수 위치는 미확정이다. 출처와 범위는 `docs/bunkerhill/K/RESCUE_SOURCES.md`를 따른다.
- 탑승 중에는 진수점에 붙어 있고 충원·퇴함 완료·상실 시 떠난다. 이미 떠난 뗏목은 canonical world 엔티티로 남는다. 기존 60 Hz tick에서 움직이며 renderer는 기존 해면 투영을 읽기 전용으로 사용한다. 뗏목 인원 instance buffer를 한 번만 해제하고 작은 공유 자원 한 벌을 재사용한다.
- 작전 envelope v2·CG revision `BUNKERHILL_LATE_G_1`을 유지하며 rescue codec과 capability를 추가했다. 전체 preflight 이후에만 저장 명단·위치·속도를 복원한다. 옛 J 저장의 퇴함자는 당시 뗏목 위치가 없으므로 detached migration으로 함선 바깥에 근사 재구성한다. 잘못된 저장은 mutation 0으로 거부한다.
- K 직접 검사 284/284. 입력 `preview-05.html`과 배포 K는 byte-identical이며 raw evidence의 파일명을 바꾸지 않았다. CIC·UI·저장·1/8/16/64×·native 뗏목·DDG·CG·클러터·실제 6발 Kh-32 AUTO를 직접 검사했다. native raid는 피격 scar 40개 이후 draw 36회와 tick 지속, fault/context loss/page error/crash 0, queue 수동 진행 0이다. 사용자 장치 FPS로 표시하지 않는다.
- J의 VLS·SPG·close-in·SPQ·3D 오류 복구와 고정 셀·277구획을 보존했다. 해당 전용 suite의 일부는 J/H/I 선행 근거이며 전부 K에서 재실행한 것으로 쓰지 않는다. K source 감사와 직접 회귀 범위는 `docs/bunkerhill/K/evidence/verification-summary.json`을 따른다.
- 상태 `AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_K.md`, SHA `SHA256SUMS_v48_WIP_BUNKERHILL_K.txt`, 지원 `docs/bunkerhill/K/`. 로컬 전체 ZIP의 J HTML/상태/SHA와 `MANIFEST.sha256`은 그대로 보존한다. GitHub는 업로드 K와 작은 지원 자료를 반영하며 대형 역사 Bunker Hill HTML을 추가 업로드하지 않는다. D/F/H/I/J는 작은 모듈·내장 asset에서 원래 hash로 재빌드한다. GitHub 지원 manifest와 원격 검사 범위는 `docs/bunkerhill/K/GITHUB_VALIDATION.md`를 따른다. legacy root baseline은 역사 검사 호환을 위해 유지하고 최신 K를 명시적으로 선택한다.
- 사용자 업로드 `5c883a5aeb80e0878f0f256f2a7a64d90224920e`의 K 크기·SHA·Git blob이 검증본과 exact 일치했다. 사용자가 main 병합을 명시적으로 요청했으며, PR의 현재 head와 성공한 Actions를 확인한 뒤 merge commit으로 반영한다. 원격 진행·결과는 PR 기록을 따른다. 기존 7.1 HTML 업로드 분담을 유지한다. K 단계는 PR #43으로 main 병합을 마쳤다. 이후 하푼 첫 구현과 인계는 위 HARPOON A 항목을 따른다.

### 직전 검증 로컬 후보 J — VLS 정지·SPG-62·양현 팰렁스·SPQ 두 면

- 당시 파일 `Aegis_SIM_v48_WIP_BUNKERHILL_J.html`, 14,446,182 bytes, SHA-256 `05306084448d4b68e25f696276346d3b9b2d4899d01a6b6d5b7ae2be9e2323b6`.
- 실제 Kh-32 6발 AUTO native 3D에서 C17 배기의 미장착 VLS 칸 참조 예외를 재현하고 실장 셀만 사용하도록 수정했다. 전방 4–7행을 DDG 4행으로 잘라 옮기는 발사 원점도 고쳤다. 122개 원점/488 ESSM/122 연출/12개 실제 발사를 원본 registration과 대조했다.
- 같은 native raid가 피격 scar 40개 이후까지 draw 36회와 fixed tick을 계속했다. RAM/physics fault/presentation fault/context loss/page error/crash 0. geometry pending 중에도 그리며 queue를 물리 tick에서 강제로 진행하지 않는다. 60/120/20 Hz와 frame 예산을 유지한다.
- 표시 예외는 오류 기록/CIC 복귀로 RAF 정지를 막고 RESET/3D 재개를 지원한다. 물리 오류 처리는 그대로다. 퇴장 SAM/ASM/wreck의 owned GPU 자원은 한 번만 해제한다.
- SPG-62 원본 연결 성분 전체를 pitch/yaw에 배정해 접시를 분리하지 않는다. 4대×12자세와 원본 indexed source 740,819 triangles를 확인했다. 벙커힐 양현 GUN은 20mm만 발사하며 탄체/보정/탄약/FX가 독립이다. DDG 실제 RAM은 유지한다.
- SPQ-9는 non-B/2D 수상 처리 유지. 공개 양면 배열 근거는 **SPQ-9B**이며 구형 A형 양면은 미확정이다. 요청한 두 면은 **SIM-TUNE**으로 명시해 180° 차이/30 RPM/명목 1초 재방문과 각 사각/3D 빔을 일치시킨다. B형 ASMD/공중 처리/측정 고도를 CG에 추가하지 않는다.
- J 직접 검사 249/249. suite/조건/hash는 `docs/bunkerhill/J/evidence/verification-summary.json`, 원인은 `ROOT_CAUSE.md`, 공개 근거는 `RADAR_SOURCES.md`다. DDG 집계 exact, 상세 float 기존 한도 안. I/H 선행 검사를 J 직접 실행으로 표기하지 않는다.
- CG 저장 revision `BUNKERHILL_LATE_G_1`, 고정61+61 VLS/277구획/상부71공간/330명과 D/E/F detached migration을 유지한다. 설치 ID·저장 schema를 바꾸지 않는다.
- J HTML·상태 `AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_J.md`·SHA `SHA256SUMS_v48_WIP_BUNKERHILL_J.txt`는 `archive/v48/WIP_BUNKERHILL_J/`, 당시 지원은 `docs/bunkerhill/J/`에 보존한다. H 및 조사용 I도 각 archive를 유지한다. I는 최신 실행 대상이 아니다.
- branch `bunkerhill-late-profile` 및 7.1 사용자 HTML 업로드 분담 유지. J 원격 업로드/CI/PR은 이번 작업에서 미실행. H/I 비교본도 동일 내장 asset과 작은 모듈로 exact 재빌드했다.

### 직전 검증 로컬 후보 H — 피격 후 3D 지속·고정 VLS·상부 내부 구획

- 당시 파일 `Aegis_SIM_v48_WIP_BUNKERHILL_H.html`, 14,444,174 bytes, SHA-256 `5aaffab97043a08b43459a374247f559c05e2c104fd8af581d094934078a5dd6`.
- F의 필수 관통구 대기 중 draw 보류를 실제 native RAF로 재현하고 마지막 완성 geometry를 계속 표시하도록 수정했다. 큰 CG static mesh는 원본 속성 그대로 compact chunk로 보존하며 물리 tick에서 queue를 강제 진행하지 않는다. 기존 60/120/20 Hz와 frame 시간 예산을 유지한다.
- 전후 각 61 VLS 설치 좌표를 고정하고 8×8의 미장착 3칸씩을 설치된 EMPTY와 구분한다. 모든 122셀×5종 편성·6프리셋·실제 클릭/드래그·출항 잠금·복원을 검사했다.
- CG 내부는 12 갑판·277 공간·392 연결·179 장비, 상부 71 공간. 함교 창문 높이에 맞춘 B1과 전후 갑판실 내부를 공유 피해/화재/문/crew 경로에 연결한다. 실함 도면이 아닌 source-contained SIM-TUNE 구획이며 물리 침수 24 column과 두 격납고 5.2 m 높이는 유지한다.
- CG revision `BUNKERHILL_LATE_G_1`; D/E/F `BUNKERHILL_LATE_D_1` 저장은 모든 codec 통과 후 detached clone으로 명시 migration한다. 잘못된 revision/구획/셀은 권위 상태 변경 없이 거부한다. H는 G의 renderer 분류와 표시 검사만 보완하므로 revision을 다시 바꾸지 않았다.
- H 직접 package 45/45, startup 17/17, 고정 셀/구획/저장 21/21, 레이더 통합 26/26, 클러터·2D 45/45, CG native 피격 18/18, DDG native 피격 16/16, 상부 구획/문/crew 10/10, G→H source 동일 범위 5/5. native 검사는 geometry generator 강제 진행 0회다.
- G CG runtime 30/30·DDG runtime 14/14·fixed-tick 1/8/16/64× 20/20을 H 직접 실행으로 표기하지 않는다. H의 CG renderer 외 main bytes/13 records/6 asset이 G와 같음을 검증해 물리 회귀가 변경 없음을 보증한다. 범위와 hash는 H evidence summary를 따른다.
- 상세 상태 `AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_H.md`, 체크섬 `SHA256SUMS_v48_WIP_BUNKERHILL_H.txt`, 전체 `MANIFEST.sha256`, 소형 코드·근거·검사 `docs/bunkerhill/H/`. 당시 H 인계는 루트 H 하나와 F/G archive 세트였다. 현재 H 세트도 archive에 bytes 동일 보존한다.
- 준비 branch `bunkerhill-late-profile` 및 7.1 사용자 HTML 업로드 분담을 유지한다. H 원격 업로드·CI·후속 PR은 미실행이다. D/F 비교 HTML은 H의 동일 내장 asset과 소형 기준 모듈로 exact 재생성할 수 있다.

### 직전 로컬 후보 — 벙커힐 후기 구성·마스트 레이더

- 최신 파일 `Aegis_SIM_v48_WIP_BUNKERHILL_D.html`, 14,351,727 bytes, SHA-256 `c71c0ec6117c1d80d593bc741a1515536ec04e34e79ca81c15ad28d1afd29e2c`.
- STARTUP_A 정확한 bytes에서 빌드했다. DDG-119 기본 선택과 CG-52의 독립 canonical runtime·프로필을 제공한다. 빨간 원 SPQ-9 non-B / 파란 원 SPS-73 실제 안테나만 회전하며 마스트 가로대·발판·난간·지지대는 고정한다.
- package 42/42, startup 17/17, CG 통합 26/26, CG runtime 30/30, DDG runtime 14/14, DDG 3D 13/13, CG 3D 14/14, 원본 등록 재생성 5/5 PASS. DDG 집계는 exact 일치하고 상세 float 최대 차이 3.87e-13은 기존 허용 오차 안이다. CG 3D는 native RAF 15초 후 동일 표시 작업 큐의 추가 진행을 포함하며 native FPS 검사로 취급하지 않는다.
- 대응 상태 `AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_D.md`, 루트 체크섬 `SHA256SUMS_v48_WIP_BUNKERHILL_D.txt`, 전체 로컬 인계 `MANIFEST.sha256`, 코드·근거·evidence `docs/bunkerhill/D/`.
- 준비 branch `bunkerhill-late-profile`는 출항 공통화 PR #42 head `d73e87f03c64d4a0429b0c6092215b44eb1688e0`에서 생성했다. PR #42는 확인 시 draft/open/unmerged다. 현재 D는 로컬 검증본으로 원격 D 업로드·CI·후속 PR을 완료했다고 간주하지 않는다.
- 7.1에 따라 사용자가 완성 HTML을 이 브랜치에 업로드한 뒤 원격 크기·SHA-256·기준을 확인하고 작은 문서·검사·workflow를 반영한다. STARTUP_A 이전 세트를 동일 bytes로 archive에 보존한다. 큰 모델 지원 자료는 새 HTML의 hash-pinned 내장 자료에서 추출하며 별도 GitHub binary 업로드를 요구하지 않는다.
- 실제 후기 레이더 세부형과 내부 도면 등 미확정 사항, SPQ-9 저고도 공중 트랙의 미구현 범위는 상태 문서와 RADAR_SOURCES를 따른다. main 병합·정식 승격·release/tag는 별도 명시 지시를 따른다.

### 직전 업로드 후보 — 출항 전 함선 선택·초기화

- 기준은 아래 WIP16B 사용자 파일이다. 새 파일은 `Aegis_SIM_v48_WIP_STARTUP_A.html`, `7,361,673 bytes`, SHA-256 `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`.
- WIP 번호 미확정 상태를 유지하며 기능명 작업 토큰 `WIP_STARTUP_A`를 사용한다. 준비 branch `ship-startup-ddg-regression`는 `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`에서 생성했다.
- 요청된 출항 전 선택·공통 최초 생성·기존 subsystem 결속과 DDG-119 회귀는 로컬 완료했다. package 34/34, startup 15/15, 기존 runtime 14/14, 3D geometry/recovery 13/13 PASS. 초기 선택에서 runtime이 없고, 선택 후 하나만 생성하며 출항 후 재선택을 거부한다.
- 상태 `AEGIS_PLAN_STATUS_v48_WIP_STARTUP_A.md`, 체크섬 `SHA256SUMS_v48_WIP_STARTUP_A.txt`, 빌더/검사/증거 `docs/ship-startup/A/`.
- 사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 크기·Git blob·parent를 확인했고 로컬 검증본과 exact 일치한다. 7.1 순서대로 작은 지원 파일 23개를 반영·원격 hash 대조했고 후속 draft PR #42를 `WIP16` 대상으로 만들었다.
- tested head `61a8931f0cc5e933fb901e270e0f5f28e046519b`에서 출항 준비 전용 [37102412380](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412380) 1/1, 기존 B 회귀 [37102412362](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412362) 1/1, 일반 smoke [37102412322](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412322) 32/32 job PASS. 일반 3D 입력은 이번 사용자 HTML이며 다른 job에는 역사 payload가 포함된다. 이후 마감 반영은 문서·증거·체크섬만 변경한다.
- 이전 B HTML/상태/체크섬 3개는 `archive/v48/WIP16B/`로 동일 Git blob을 이동·대조해 보존했다. 기존 원본과 증거를 덮어쓰지 않는다. archive의 옛 체크섬은 당시 경로/문서의 역사 증거이며 최신 검사에는 새 체크섬을 사용한다.
- STARTUP_A 당시 운용 registry는 DDG-119 한 척이다. 다음 구현은 벙커힐 profile/model/builder를 이 초기화 경계에 연결하는 것이다. 다함 동시 운용·하푼·토마호크는 후속 범위다. main 병합·승격·release/tag는 별도 명시 지시를 따른다.

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
