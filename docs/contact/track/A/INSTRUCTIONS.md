# AEGIS 센서 관측·트랙 연관·식별 신뢰성 보강 — Codex 작업 지시서

## 0. 작업 기준 및 목적

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 기준 브랜치: `friendly-contact-a`
- 확인한 기준 HEAD: `4ba64ba0cace9124497a710d00df1b174984ffdc` (착수 전에 최신 HEAD와 차이를 재확인하고 임의로 다른 브랜치에 재기반하지 말 것)
- 기준 실행 제품: `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`
- 우선 확인 문서: `docs/contact/friendly/A/README.md`, `REPORT.md`, `VALIDATION.json`, `DEVELOPMENT.md`, `SCOPE.json`, `changes.diff`, `BUILD.json`, `analysis/track-reproduction.json`.
- 기존 관련 코드/문서: 자함 `updateSensorTrackMeasurement`, `trackEkfUpdateSurfaceRadar2D`, `trackRadarAssociationNisV31`, `trackApplySurfaceDomainConstraint`, `trackMayAcceptSurfacePlotCrossDomainWip13B14`, `updateTrackClassification`; 외함 `observerAcceptPlotsC`, `observerClassifyC` (`docs/multiship/C/observer.js`의 출처와 현 제품 코드를 반드시 대조); CIWS `c55SensorSweep`; Hawklink `ingestOffboardReportC` / `acceptOffboardC`; 네트워크 `networkAcceptReportG`, `networkReconcileG`, `networkIntersectionG`; AI H1~H4의 트랙 소비자.

**최종 목표:** OODA나 새로운 AI 전술을 도입하기 전에, 함정별 센서 관측이 오염 없이 연관되고, 동일 표적의 중복 트랙과 서로 다른 표적의 잘못된 병합을 줄이며, 추정·분류·IFF·아군탄 보호·교전권한을 근거와 유효기간에 따라 일관되게 관리할 수 있는 기반을 만든다. 단순히 화면의 트랙 번호를 숨기거나 결과가 좋아 보이게 만드는 작업은 허용하지 않는다.

### 확인된 현재 상태와 미해결 사항

- 기존에 EKF/NIS/공분산, 2D·3D 레이더, 헬기 Hawklink, ESM 방위 접촉, Link 16의 보수적 CI 융합, 로컬 CIWS 파일, IFF, 트랙 수명, 함정별 AI가 있음. **기존 기능을 다시 만들어 중복 체계를 생성하지 말 것.**
- `friendly-contact-a`는 관측된 3D AIR 높이를 수상 2D 관측의 가정 높이로 덮어쓰는 문제와 CIWS 자함탄 보호 오염을 수정한 **미승인 후보**다. 헬기 60초 3→1개, 이동 헬기 120초 4→1개, Harpoon 75초 22→2개 신규 트랙 생성(마지막 잔존 1개)을 기록한다. 관측 단절 후의 정당한 재획득을 강제로 동일 번호로 만들지 않는다.
- CIWS 30시드에서 피격 12→8회로 감소했으나 `419025`는 기존 요격→함선 피격으로 악화했다. 또한 paired observer 정확 상태 2개 차이가 남아 있고, 구형 EMCON UI 14개는 현 UI에 없는 `#lockBtn`을 요구한다. `VALIDATION.json`의 `releaseApproved=false`를 임의 변경하지 말 것.
- 기존 결과가 변한 경우 원인과 그 변경이 정당한 이유를 증명해야 한다. 테스트 기대값 수정, 기준 완화, Pd/Pk·발사 타이밍·무장 성능·RNG 보정으로 감추지 말 것.

## 1. 필수 안전 계약

1. **정보 비누수:** 실제 월드 표적 ID, faction, owner, 실좌표, 생존 여부, 미사일 시커·INS·진실 트랙 등은 센서 물리 합성 또는 사후 검증에서만 이용한다. 관측 연관·트랙 분류·자동 식별·AI·발사 판단의 입력으로 역류 금지. `truthRef` 같은 진단용 참조의 소비자를 추적하되, 진실을 이용해 트랙을 병합·보호·적성 지정하지 말 것.
2. **측정과 가정 분리:** 측정하지 않은 고도·속도·위치는 유효한 센서 측정인 것처럼 다루지 않는다. 수상 레이더의 8m 수면 높이는 모델 prior이지 관측 고도가 아니다. ESM bearing-only는 거리 있는 위치 트랙으로 임의 전환 금지. ISAR 판독은 그 자체로 새로운 레이더 위치 hit가 아니다.
3. **함정별 독립성:** 자함/외함의 canonical 트랙, 외부 보고, 네트워크 수신 파일, C55 로컬 CIWS 파일, 헬기 자체 접촉을 목적에 맞게 분리 유지한다. 공통 알고리즘을 재사용하더라도 무조건 동일 `TrackStore`에 넣지 않는다. 다른 함정의 private FCS/항법 상태를 직접 훔쳐보지 않는다.
4. **교전권한 보호:** `classification`, `identity`, `threatStatus`, `engagementAuthority`는 서로 다른 개념. AIR/ASM/SURFACE 분류가 HOSTILE이나 발사동의를 자동 생성하지 않음. UNKNOWN·FRIEND·NEUTRAL, IFF, 기존 ROE/사격 게이트, player MANUAL/HOLD 우선권 유지.
5. **물리/무장 동작 보존:** 임의로 레이더 RF Pd/Pfa/SNR/RCS/클러터 계수, EKF 행렬·이득, 센서 하드웨어 프로필, 함체·파랑·피해, 유도/신관/Pk, Harpoon DL=0, 발사대·무장 재고/사각 등을 조정하지 않는다. 조정이 꼭 필요하다고 판단되면 근거·영향·별도 승인 필요 항목으로 보고하고 본 패치에 섞지 않는다.
6. **고정 틱·재현성:** 실제 1/60s fixed step, owner별 독립 RNG, 1·8·16·64배속의 결과 결정성, observer 중복 실행 금지, diagnostic 조회 무상태 변경을 유지한다.
7. **브랜치와 산출물:** `main`, `cg-turret-a`, 원본 `friendly-contact-a`를 직접 수정·병합하지 않는다. 기준 HEAD에서 별도 작업 브랜치를 만들고 단계별 커밋·실행 가능한 HTML·검증 증거를 제출한다. PR 생성·병합·release/tag는 별도 요청 전 금지. 기존 packed asset/빌드·체크섬 절차를 사용하고 생성 HTML만 임의 편집하지 않는다.

## 2. 구현 전 Baseline Audit (필수)

실제 최신 실행 HTML의 압축 해제된 JS와 빌드 소스를 함께 검토하고 아래 표를 `TRACK_AUDIT.md`에 작성한다.

- **생성:** 센서별 raw RF/ESM/IFF/ISAR/Hawklink/Link 16 보고 → measurement/plot 생성 함수.
- **연관:** 자함 `updateSensorTrackMeasurement` 주변, 외함 `observerAcceptPlotsC`, 헬기 접촉, CIWS `c55SensorSweep`, Hawklink, 네트워크의 연관 게이트·후보 선택·일대일 처리.
- **상태 갱신:** EKF 상태벡터/공분산, domain prior, 분류, hit/confirmed, sensorAge, memory/coast/reacquire/drop, alias·재시작.
- **보호/소비자:** IFF/own-fire evidence, 네트워크 FRIEND/NEUTRAL 보호, C55 무장동의, H1~H4·native FCS·CIC·MAP 트랙 소비 경로.
- 각 지점의 **소유자·입력 출처·측정 차원·쓰기 필드·읽기 필드·틱 순서·기존 테스트·중복 여부**를 기록한다.
- 특히 `419025`의 관측→C55 파일→Phalanx/RAM→RNG/피해 이벤트 타임라인과 paired observer 2개 차이를 기준 증거로 고정한다. 초기 원인 가설과 재현 방법을 남긴다.
- 먼저 기존 검증 명령을 그대로 실행하고 통과/실패/환경 문제를 구별해 남긴다. 최초 baseline을 임의 갱신하지 않는다.

## 3. 순차 구현 계획 (4개 독립 단계)

### TRACK-A — Measurement Contract & Trace (동작 보존형)

**목적:** 각 센서가 정확히 무엇을 측정했고 무엇을 모르는지 공통으로 표현할 수 있게 하고, 오인 원인을 추적할 로그를 만든다.

- 기존 센서 측정을 내부 공통 형식 또는 **호환 어댑터**로 정규화한다. 필수 개념: `sourceSensor`, `observerShip`, `measuredAt`, `receivedAt`, `measuredFields`/measurement mask, 측정 벡터, 관측 모델·차원, 오차/공분산, quality, domain evidence, 독립 관측/재전송을 식별할 수 있는 provenance. 이름은 코드의 실제 관례에 맞춰 정한다.
- `observed`, `assumed/modelPrior`, `derived/filterEstimated`를 분리한다. 높이 8m를 실제 고각 측정으로 표시하거나 미관측 성분을 공분산 없이 확정값으로 넣지 않는다.
- 기존 3D 실제 관측의 유효기간 및 2D 가정 적용/해제 조건을 감사해 근거와 소멸 조건을 문서화한다. 이번 단계에서는 EKF 수치·분류·발사 행동을 바꾸지 않는다.
- **진단 전용 연관 추적:** 어떤 plot이 어느 track의 후보였고, 각 후보의 gate 판정·NIS·거부 이유·적용된 측정 차원·이전/다음 상태·최종 source를 요약한다. bounded ring buffer 또는 test-only 분리; 물리/RNG/스케줄러 영향 0. 독립 진단 조회는 상태를 mutate하지 않는다.
- 모든 센서의 원시 payload를 한꺼번에 갈아엎지 않는다. 기존 호출부를 깨지 않는 최소 어댑터부터 작성하고 향후 전환 지점을 표시한다.

**A 종료 조건:** 트랙/물리/전투/RNG의 기존 baseline과 동작상 동일(진단 필드만 예외), 출처·차원·가정 검증, 범위 외 변경 0, 검사 보고/실행 HTML 제출. **우선 이번 요청에서는 TRACK-A부터 구현하고 보고할 것.** B~D의 변경을 한 커밋에 섞지 않는다.

### TRACK-B — Association Reliability & Cross-Domain

**목적:** 물리적으로 같은 표적의 연속성을 높이되 서로 다른 표적은 안전하게 분리한다.

- 자함·외함·C55·Hawklink·네트워크의 연관 함수를 일괄 교체하지 말고, 공통으로 재사용 가능한 **시간 정렬·측정 차원별 NIS/거리·속도 게이트·후보 평가·모호성 판정**을 만들고 기존 경로에 점진 적용한다.
- 여러 plot/track이 동시에 맞는 상황은 **일대일 할당**을 유지하고, 관측과 예측이 거의 비슷한 후보가 여럿이면 즉시 임의 병합하거나 번호 교환하지 말고 보류/새 tentative/별도 불확실성으로 처리한다. 필요 시 bounded 최적 할당을 비교하되 큰 MHT/JPDA 전면 도입은 이번 범위 밖이다.
- 공분산이 아주 커졌다는 이유로 멀리 떨어진 표적을 강제로 결합하지 않는다. 관측 차원에 맞는 NIS, 별도 물리적 거리·속력 sanity gate, 시간 차와 coast 상태를 함께 본다. 기존 threshold를 일괄 완화해 중복 수만 낮추는 방식 금지.
- 2D 수상 레이더는 측정한 성분만 갱신하고 3D 관측으로 얻은 고도/수직속도 분포를 덮어쓰지 않는다. 2D-only 트랙은 유효한 3D 관측과 연관할 수 있어야 한다. 반대로 수상 표적을 공중 표적으로 무조건 바꾸지 않는다.
- `c55SensorSweep`의 **자함 발사 사실에서 온 own-fire evidence**와 비자함탄 측정은 한 파일에 오염되도록 병합하지 않는다. 모호한 경우 적 탄을 FRIEND로 억지 지정하거나, 기존 유효한 아군 보호를 무조건 삭제하지 않는다. 기존 자함/NPC 두 경로의 동등성 검증.
- 과도기에는 **shadow comparison**으로 기존/개선 결과·거부 이유를 같은 fixture에서 비교한 후 검증된 경로만 실제 소비자에 연결한다. 기존 EKF 수치·사격 계수는 보존.

**B 종료 조건:** 헬기 정지/이동 및 Harpoon 재현의 부당한 반복 생성 재발 없음; 두 분리된 표적은 일대일 유지; 정상적 공백 후 재획득은 허용; 아군탄 오염 0; 모호성 테스트 PASS; 영향 받은 기존 전투 결과 차이의 이유를 증명.

### TRACK-C — Lifecycle, Provenance & Identity Evidence

**목적:** 추정 트랙의 수명·출처·피아식별 근거가 더 이상 암묵적으로 영구 전파되지 않게 한다.

- 기존 `TENTATIVE/FIRM/COAST/MEMORY/REACQUIRE/DROP` 상태·필드 사용자를 감사하고, 각 상태에서 관측/예측/재획득/소멸의 조건을 한 군데에서 설명 가능한 계약으로 정리한다. 기존 소비자의 표시/ROE를 깨지 않도록 단계적 adapter 사용.
- 각 트랙의 독립 관측 hit, 마지막 실제 fix, 출처별 measurement age, 3D 측정 유효기간, prior 적용 여부, alias/재획득 출처를 기록한다. 같은 데이터의 재전송이나 동일 센서의 중복 전달을 독립 확인으로 반복 집계하지 않는다.
- `classification`과 `identity`, `engagementAuthority`, `ownFireEvidence`의 **근거 출처·시점·유효기간·연관 계보**를 구분. 연관이 파손되거나 새 ID로 분리될 때 근거 승계가 안전한지 재검증하고 무조건 복사하지 않는다. IFF 보호를 임의 해제하거나 UNKNOWN을 HOSTILE로 승격하지 않는다.
- 실제 신호가 약해 생긴 유령 파일, 동일 물체의 duplicate 파일, 서로 다른 물체의 false merge, 재획득 후 별도 파일을 **서로 다른 진단 유형**으로 분류한다. 화면에 번호가 하나만 보이게 만드는 은폐식 수정 금지.

**C 종료 조건:** 허위·중복·오병합·번호 전환/재획득/이력 추적 fixture 통과. 아군/중립 보호·기존 발사 권한/수동 명령은 보존.

### TRACK-D — Multi-Sensor/Network Consumer Integration & Final Closure

**목적:** 신뢰성 보강 결과를 각 소비자가 일관되게 읽게 만들되 별개의 독립 추적계를 없애지는 않는다.

- Hawklink 측정 시각/수신 지연/공분산 증가, 같은 보고 재수신, 링크 단절을 유지·검증한다. ESM은 bearing·sigma·emitter 증거로 제공하되 임의 x/y/z 보충 금지. ISAR 클래스 근거가 위치 hit나 HOSTILE 권한이 되지 않게 유지.
- Link 16/G의 NIS와 **고정 0.5 Covariance Intersection** 기반 보수적 수신 융합을 유지하면서, 동일 정보의 순환 재수신·source lineage 중복·오래된 정보와의 상관을 검증한다. 원격 보고는 기존처럼 표시/보호 용도이며 승인되지 않은 CEC·원격 사격통제로 확장 금지.
- H1 방어 utility, H2 기동, H3 대수상 공격, H4 협동 전술, CIC/MAP에 **detached, 읽기 전용의 신뢰도·출처·freshness·불확실성 정보**를 전달하되, **OODA/새 전술 점수·AI 성향·자동 적성 정책을 구현하거나 변경하지 않는다.** 현행 AI 소비자가 가정값을 측정값으로 착각하는 경로만 보정한다.
- 결과가 모두 검증된 후 superseded adapter/legacy 필드는 사용처 감사와 회귀 후에만 정리한다. 사후 진실 정보는 실행 소비자에 노출하지 않는다.

**D 종료 조건:** 함정별 독립성, 네트워크/헬기/ESM/IFF, 모든 AI/무장 소비자와 UI·저장·시간결정성, 이전 A~C 회귀 통과. 모든 미해결 차이를 명시한 별도 closure 보고서를 제출한다.

## 4. 필수 시험·재현 매트릭스

각 단계에서 관련 범위를 실행하고, 최종에는 아래를 모두 검증한다. **fixture-only 성공을 자연 RF/실제 무장 검증으로 둔갑시키지 말 것.**

1. **기존 세 재현:** `HELO_HOVER_60S`, `HELO_ROUTE_120S`, `HARPOON_ROUTE_75S`. 신규 파일 수/최대 동시/종료 파일, 정당한 재획득의 NIS, 신선도, domain 분류, IFF 상태를 전후 기록한다.
2. **2D↔3D 차원:** 수상 2D→AIR 3D, AIR 3D→2D 기여, 저방사속도/빔 직각 이동, 실제 고도 유무, 오래된 3D 근거 만료, native NIS 거부.
3. **다표적 연관:** 근접한 두 함정/항공기/미사일이 교차, 시간차 재관측, 서로 다른 반사체·도플러, 가짜 plot과 겹침. one-to-one, false merge·false split·ID swap·duplicate birth/age 분리 측정.
4. **허위 접촉:** CFAR noise-tail/해면 clutter/전자전 replay 편향; 실제 신호와 독립 잡음의 연관이 과도하게 confirmed되지 않는지. 기존 RF 확률 계수를 임의 변경하지 않는다.
5. **IFF·아군탄:** IFF ON/OFF/응답 만료/재연관, FRIEND·NEUTRAL 보호, own RAM/Harpoon과 적 ASM 근접, C55 2문맥의 보호 오염 0, AUTO+IFF ON에서 자함 헬기에 VLS/ESSM/CIWS 소모 0.
6. **외부 보고·네트워크:** Hawklink 지연·replay·공분산/시각 유효성, Link 16 중복 보고와 unknown correlation, 네트워크 OFF/끊김, SHARE-only→FCS 권한 상승 0, ESM bearing-only 거리 생성 0, ISAR 결과의 hit/교전권한 증가 0.
7. **실제 CIWS 30시드:** 원래 `419010~419039`, DDG-119, bearing 90°, Kh-35U 1발/11km, MANUAL, 함포 AutoAA OFF, 실제 fixed tick 유지. 피격/HP0/RAM·20mm 총 소모 및 시드별 타임라인 기록. **419025 결과는 별도 상세 분석, 기대값 수정·결과 숨김 금지.**
8. **기존 도메인/화면:** native 13 suite, 기존 도메인 420 세부 집계(404 통과/observer exact 차이 2/구형 UI 14 미완료라는 최초 상태를 정확히 표시), 현재 UI 213, WebGL 자연 발사 8발/기존 단언 29, EMCON, Harpoon·헬기, paired observer, DAMAGE/SHIP/FLEET/네트워크 재검증. 실패와 환경 문제를 구분하고 숫자 합산을 중복하지 않는다.
9. **불변성·성능:** 무표적 물리 truth SHA, observer diagnostic ON/OFF의 RNG/트랙/물리 동등성, 1·8·16·64배속 결정성, 각 함정 1회/tick, 테스트 전후 평균/p95 CPU·할당·트랙 수·연관 후보 비용 측정. 변경 전 대비 뚜렷한 성능 악화는 근거 없이 승인하지 않는다.

## 5. 완료 판정 규칙

- `PASS`: 실제 구현 경로/시험 조건·기대 기준이 모두 확인된 경우만.
- `KNOWN_DELTA`: 의도적 또는 실제 원인을 확인한 기존 차이. 별도 증거와 사용자 검토 전 자동 승인하지 않는다.
- `FAIL`: 새 오인·동작 오류·무방비 전환·전투 손실 등 예기치 않은 퇴행.
- `BLOCKED/INCOMPLETE`: 환경 문제/구형 UI/실행 미완료. 절대로 PASS로 계산하지 않는다.
- 파일 수만 줄었다는 이유로 PASS 판정 금지. 실제로 두 표적이 하나로 병합되면 더 심각한 실패다.
- 기존 허위 표적 확률, 실제 하푼 운용·전자전·함정 피해의 물리 결과를 보정해서 기대값과 맞추지 않는다.
- 마지막까지 `419025`와 observer paired 차이가 남으면 미해결 상태 그대로 제출하고, `releaseApproved=true`, 'all regressions green', 'final CLOSED' 선언을 하지 않는다.

## 6. 단계별 제출물 및 이번 작업 요청

각 단계마다 다음을 제출한다.

- 독립 실행 가능한 **최종 HTML** 및 SHA-256, 빌드 재현 명령, 소스 커밋 SHA/작업 브랜치.
- `TRACK_AUDIT.md`(최초), `TRACK_CONTRACT.md`(측정·연관·식별·수명 규칙), 해당 단계 `REPORT.md`(변경 함수·원인·수정 전/후·위험·미완료), `VALIDATION.json`(원시 집계와 승인 상태), `changes.diff` 또는 비교 링크.
- 필수 재현 JSON/CSV/간단한 타임라인 및 스크린샷이 의미 있을 때의 UI 증거, 테스트 명령·exit code·실행 환경. 실제 제품 함수 시험, fixture 시험, 진단 참조를 분리 기록.
- 코드 변경 목록/변경하지 않은 보호 범위, 기존 값/테스트 기대값 변경 여부, 성능 변화, `truth` 및 교전권한 입력 감사 결과.

**Codex에 내리는 현재 실행 지시:** 위 전체 계획을 기준으로 먼저 **Baseline Audit + TRACK-A**만 구현하고, 독립적으로 검증 가능한 결과물과 보고서를 제출하라. TRACK-B/C/D는 설계·리스크를 적어두되, A의 검증 결과를 확인하기 전 구현·병합하지 말라. 막히는 문제가 있으면 기존 기능을 꺼서 가짜 PASS를 만들지 말고 원인과 증거를 제시하라.

## 참고 문서 (해당 브랜치)

- https://github.com/0-FLANDRE-0/Aegis_Project/tree/friendly-contact-a
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/contact/friendly/A/REPORT.md
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/contact/friendly/A/changes.diff
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/C/observer.js
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/C/offboard.js
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/G/network.js
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/H1/tactical.js
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/H2/maneuver.js
- https://github.com/0-FLANDRE-0/Aegis_Project/blob/friendly-contact-a/docs/multiship/H4/team.js
