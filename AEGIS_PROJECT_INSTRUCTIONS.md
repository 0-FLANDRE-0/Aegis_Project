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

- 현재 이어서 작업할 기준은 `Aegis_SIM_v48_WIP11C.html`이다.
- 현재 기준 HTML SHA-256은 `464e1fc4a7e3ef9565bc32ce42e7e5a112041a977ee96fb7bdb5920f7410c01f`이고 크기는 `2,819,872 bytes`다.
- 최종 로컬 검증은 WIP11C 정적 계약 `32/32`, WIP11C Playwright `11/11`, 전체 Playwright `28/28`을 통과했다.
- WIP10, WIP11, WIP11A, WIP11B는 각각 `archive/v48/WIP10/`, `archive/v48/WIP11/`, `archive/v48/WIP11A/`, `archive/v48/WIP11B/`에 보존한다.
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
- 다음 코드 작업은 WIP12A 종말탄도 기틀이다. 모든 탄체에 하나의 관통식을 강제하지 않고 `TerminalProjectileSpec`·가변 projectile state·impact trace·damage packet 계약을 공유하며, 충돌 regime에 따라 solver를 선택한다.
- WIP12A의 확정 설계 범위와 완료 기준은 `docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`를 기준으로 한다.
- WIP12A traversal은 `BOUNDARY`, `EMPTY`, 실제 `DAMAGE_VOLUME`을 구분한다. 빈 공간은 에너지를 소모하지 않고 비행시간과 신관 시간만 진행하며, 경계와 실제 물질 볼륨만 탄체 상태를 바꾼다.
- WIP12A에서는 실제 함포 발사·외탄도·FCS, 중장갑 실전 적용, persistent damage patch ledger를 활성화하지 않는다. 기존 ASM 결과는 compatibility adapter로 보존하고 신규 discrete-boundary fixture를 별도로 검증한다.
- WIP13은 해상사격 FCS, WIP14는 간단한 표적함과 복수 함선 프로파일이다.
- WIP 번호는 이 인계 순서를 사용하며 과거 대화의 다른 WIP 번호표를 재사용하지 않는다.
