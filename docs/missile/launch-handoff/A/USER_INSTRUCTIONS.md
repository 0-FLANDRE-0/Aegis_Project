# AEGIS Codex 지시서 고각 발사 전환과 제어권 인계 수정

## 1. 작업 목표

고각 공중 사격에서 Standard 계열 미사일이 발사 전환 상태에 계속 남는 원인을 정식으로 수정하고 검증한다. PN 증폭으로 명중률을 맞추지 않는다.

작업은 다음 두 범위로 구분한다.

1. 고각 발사 전환 조건과 제어권 인계를 수정하고 회귀 검증한다.
2. 수정 후 남는 SM-6의 근접기폭 무효 사례를 계측해 원인을 분류한다. 별개의 신관·파편·피해 모델 수정은 이번 변경에 섞지 않는다.

설계 제안만 하지 말고 코드 수정, 필요한 검사, 새 HTML과 상태 문서, 비교 증거까지 완성한다. main 병합과 release/tag 생성은 하지 않는다.

## 2. 기준과 작업본 보존

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 사용자가 지정한 최신 작업 기준: `fuze-zem-a`의 DZT 후보
- 조사 당시 HEAD: `7d863699c596c30b0df5e34734f17fe11cadc21e`
- 기준 HTML: `Aegis_SIM_v48_WIP_FUZE_ZEM_A.html`
- 기준 HTML 크기: `18,452,900 bytes`
- 기준 HTML SHA-256: `edc159fa347d721d61d80228e2512665f22da0adb4f02fdf4e2dbe82789e0c9c`
- 당시 main HEAD: `cb70a637105ce00e7c0619270237cc35a83d39c2`

시작 시 현재 HEAD, 작업 트리, 적용되는 AGENTS.md, 프로젝트 지침, README, 최신 상태 문서와 체크섬을 확인한다. 위 SHA는 조사 시점의 기준이며 이후의 정당한 작업을 되돌리는 명령이 아니다.

사용자가 원래 작업하던 Codex에서 이어서 수정하므로 기존 미커밋 변경과 브랜치를 보존한다. main은 비교 기준으로 확인하고, 실제 수정 기준을 옛 main HTML로 바꾸지 않는다. 현재 브랜치가 기준보다 진행됐다면 차이를 확인하고 이어서 작업한다. reset/clean/강제 checkout으로 작업을 없애지 않는다.

새 산출물은 저장소의 현재 버전 규칙을 따른다. 이름이 미확정이면 `Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html`과 같은 버전 토큰의 상태 문서를 사용한다. 기준 FUZE_ZEM_A와 증거는 보존하고 같은 이름으로 다른 내용을 덮어쓰지 않는다.

## 3. 이미 확인된 원인과 근거

### 3.1 발사 전환 종료 조건

다음 경로를 실제 게임 소스에서 확인한다.

- `updateMissileBodyB3`의 PHASE 1b / FORWARD-COMMIT
- `_samVlsControlConfig`
- `_samLeadPointForLaunch`
- `_samSetLaunchCorridorCommand`
- `applyGuidanceKernelV1ToLegacyRates`
- `applyAccelCommandToAutopilotV1`
- `updateSamSixDofLiteDynamics`

현재 핵심 조건은 다음과 같다.

```js
const pitchEnvelopeReady =
  isESSM ? vectorAligned : Math.abs(m.velPitch ?? 0) <= cfg.maxVelExit;
```

5km/20km 시험에서 Standard의 `maxVelExit`는 약 40.32도인데 실제 비행경로각은 70~80도다. 이 절대각 조건이 false로 남아, 다른 이격·자세·속도 조건을 만족해도 발사 전환이 완료되지 않았다.

`deadlineExceeded`는 경고만 기록하며 제어권을 넘기지 않는다. 따라서 시간 제한이 있다는 이유로 교착이 해소된다고 판단하면 안 된다.

### 3.2 하류 영향

- `pitchoverPhase=true`가 최초 표적 통과까지 유지된다.
- 표시되는 `_v1GuidancePhase`는 TERMINAL/ENDGAME이어도 발사 제어권은 남아 있다.
- `launchOverlap` 경로에서 발사 자세 제어와 PN/APN/ZEM의 각속도 명령이 계속 혼합된다.
- 발사 전환 중에는 가속도 피드백 루프가 비활성화된다.
- Kappa 경로 등 `!pitchoverPhase`를 요구하는 경로도 정상 인계를 받지 못할 수 있으므로 실제 활성 경로를 확인한다.

독립 진단의 SM-2ER 12초 시점에서 bridge 피치 명령은 약 0.062828rad/s, 최종 기체 입력은 약 0.008129rad/s였다. 단순 물리 가용 G 부족으로만 분류하지 않는다.

`m._v1GAchieved`는 제한 후 명령 크기다. 실제 기체가 달성한 가속도로 해석하지 않는다. 실제 크기는 `sam6dofActualNormalG`, 명령 방향 성분은 `sam6dofDeliveredG`와 관련 벡터를 사용한다.

### 3.3 근거 위치

- [현재 발사 전환 조건을 포함한 native capsule](https://github.com/0-FLANDRE-0/Aegis_Project/blob/fuze-zem-a/docs/envelope/D/diagnostic/native-engine.js#L1009)
- [FUZE_ZEM_A 보고서](https://github.com/0-FLANDRE-0/Aegis_Project/blob/fuze-zem-a/docs/missile/fuze-zem/A/REPORT.md)
- [DZT 변경](https://github.com/0-FLANDRE-0/Aegis_Project/blob/fuze-zem-a/docs/missile/fuze-zem/A/changes/DZT.diff)
- [A 시험 엔진](https://github.com/0-FLANDRE-0/Aegis_Project/blob/fuze-zem-a/docs/missile/fuze-zem/A/engine.cjs)

native capsule의 링크는 조사 진입점이다. 최종 수정 대상은 실제 게임 HTML의 실행 소스이며 capsule만 고쳐 완료 처리하지 않는다.

## 4. 독립 진단 결과와 재현 계약

아래 수치는 이 대화에서 수행한 추가 진단 결과다. 기존 원격 REPORT에 기록된 새 정식 결과라고 취급하지 말고 Codex에서 다시 재현한다.

조건: 수평거리 5km, 고도 20,000m, 정지 Kh-35U 구조/피해 표적. 기존 private 진단의 이상적 RF/지원 경계와 60Hz 고정 틱을 사용했다. 자연 RF/EKF와 전체 게임 월드 시험과는 구분한다.

| seed | rngSeed | navigationSeed |
|---|---:|---:|
| 1 | 1831565813 | 2047861954 |
| 2 | 305419896 | 2654435769 |
| 3 | 2271560481 | 1013904242 |
| 4 | 324508639 | 2779096485 |
| 5 | 610839776 | 1515870810 |

원인 분리용 복사본에서 Standard의 절대각 검사를 발사 경로에 대한 상대각 검사로만 바꿨다.

```js
const pitchEnvelopeReady =
  isESSM ? vectorAligned
         : Math.abs((m.velPitch ?? 0) - cor.desiredPitch) <= cfg.pitchTol;
```

이 코드는 원인 확인용 후보이며 그대로 최종 채택하라는 요구가 아니다. 저각 사격에서는 기존 인계 시점도 달라졌으므로 정상 조건 회귀와 최종 계약 검토가 필요하다.

PN 이득과 추진·항력·질량·기동 한계는 유지한 DZT 비교 결과:

| 5km/20km, 각 5발 | 기존 DZT | 진단용 전환 조건 수정 |
|---|---:|---:|
| SM-2ER 최근접 기록 | 259.48~274.23m | 28.79~29.13m |
| SM-2ER 효과 발생 | 0/5 | 5/5: KILL 4, DAMAGED 1 |
| SM-6 최근접 기록 | 220.83~228.84m | 41.57~41.78m |
| SM-6 효과 발생 | 0/5 | 1/5: KILL 1, PROX_DETONATION_MISS 4 |
| SM-2ER 인계 시점 | 최초 통과까지 미인계 | 4.6333초 |
| SM-6 인계 시점 | 최초 통과까지 미인계 | 4.8833초 |

최근접 기록은 엔진이 비행 종료/기폭까지 기록한 값이다. 기폭하지 않았다면 도달했을 가상의 최저 CPA로 해석하지 않는다.

별도 30km/5km/접근 250m/s 조건에서 두 기종×5시드의 기존 격추 10/10을 유지했다. 궤적과 CPA가 동일했다는 의미는 아니다.

seed1 기존 DZT의 우선 재현값:

- SM-2ER: CPA 270.975728315m, TRACKED_DIVERGENCE 종료 21.716666667초.
- SM-6: CPA 223.444558551m, TRACKED_DIVERGENCE 종료 22.033333333초.

기존 엔진 baseline 호출 예:

```js
const { create, seeds } =
  require('./docs/missile/fuze-zem/A/engine.cjs');
const result = create('DZT').runCase({
  weapon: 'SM2ER',
  rangeKm: 5,
  altM: 20000,
  targetSpeedMps: 0,
  ...seeds[0],
  samples: true
});
```

## 5. 정식 수정 요구

1. 인계 조건을 이격 안전, 기체 자세, 속도 벡터와 예정 발사 경로의 정렬에 맞게 설계한다. 정상 고각 비행을 절대 수평각만으로 차단하지 않는다.
2. 수평속도 `Math.hypot(vHx,vHy)` 기반 최소 속도 조건이 거의 수직인 사격에서도 교착을 만드는지 검사한다. 필요하면 예정 3D 경로 방향의 속도 성분을 검토하되, 미검증 교체나 기준 완화를 하지 않는다.
3. 함체/발사대 안전 이격, 후방 비행 방지, 저속·과도한 받음각·불안정 자세 보호를 유지한다.
4. 정상 인계가 성립하면 발사 자세 제어의 혼합과 상태가 끝나고 선택된 유도 커널이 제어권을 받게 한다. 필요한 연속성 처리는 명시적으로 설계한다.
5. 단순 `pitMaxS` 초과나 거리/고도 특례만으로 `pitchoverPhase=false`를 강제하지 않는다. 미정렬 상태와 실제 비행 불능을 정상 인계와 구분한다.
6. 공중 사격과 대수상 발사의 계약을 구분하고 기존 `surfaceLaunchVectorAlignedWip13C6` 및 ESSM 보호를 보존한다. 관련성이 없는 ESSM 제어법을 변경하지 않는다.
7. 진단값은 전이 전후의 상태를 분리한다. 같은 tick에서 종료 직전/직후 상태가 다른 것은 오류가 아니지만, 이후에도 유효 제어권과 표시 상태가 지속적으로 모순되면 수정한다.

전환 기준과 히스테리시스가 필요하면 단위와 의미를 설명하고 SIM_TUNED임을 밝힌다. 특정 명중 사례에 맞춰 임계값을 반복 조정하지 않는다.

## 6. 고정할 항목

다음 항목을 성공률 보정 수단으로 변경하지 않는다.

- PN/APN/ZEM 이득과 전역 2.5배/3배 배율.
- DZT의 결정론적 신관 D, 수정된 ZEM 부호 Z, 종료기 T.
- 추진력, 추진제, 연소시간, 항력, 질량, 기준 면적, 구조/운용 G 한계.
- 배터리, 시커 탐지 거리/품질, 신관 반경/처리 지연, 파편/Pk/피해 계수.
- Truth 경계, 권한, 자동 교전 안전 조건, 고정 틱과 난수 스트림.
- 함선/무장 모델과 무관한 UI·자산.

새 게임 로직은 온보드 항법·수신 관측만 소비한다. truth 위치는 센서 합성·충돌·피해 및 격리된 사후 진단에만 사용한다.

## 7. 계측과 시험 도구의 실제 소스 확인

최소 다음 값을 같은 고정 tick에서 기록한다.

- life, 발사 단계, pitchoverTimer, 선택 유도 단계, 실제 명령 소유자.
- 인계 조건별 PASS/FAIL과 차단 사유, deadline 상태, 인계 시점.
- 예정 경로각, 기체 자세, 속도 벡터각, 방향별 정렬 오차, 3D/수평 속도, 안전 이격.
- 발사 자세 제어 명령, PN/APN/ZEM 명령, 혼합 계수, bridge 출력, 기체에 전달된 최종 명령.
- raw 요구 G, 제한 후 명령 G, availableG, 실제 normal G, 명령 방향 delivered G.
- 가속도 피드백 활성 여부, 구동기 포화, 유효 관측 종류와 나이.

현재 A/engine.cjs는 source.cjs의 baseline()으로 ENV_D 기준을 읽고 A의 D/Z/T 패치를 적용한다. 새 HTML만 수정하고 이 엔진을 그대로 돌리면 수정 전 후보를 시험할 수 있다.

신규 시험은 반드시 수정된 실제 HTML에서 해당 함수를 추출해 실행하거나 동일 소스임을 해시로 확인한다. 게임 함수와 private capsule의 동등성도 다시 확인한다. 시험 도구만 수정한 결과나 과거 evidence를 새 제품 검증으로 합산하지 않는다.

JSON 로그에는 객체 참조를 그대로 보관하지 말고 tick별로 복사한다. 나중에 변한 live 객체가 이전 샘플을 덮어쓰면 해당 계측을 폐기하고 다시 실행한다.

## 8. 검증 순서와 완료 조건

프로젝트 필수 검증 순서를 따른다. 앞 단계가 실패하면 원인을 해결한 뒤 진행한다.

1. 변경 전 baseline 재현: 두 기종×5시드의 비명중, 계속 남는 pitchover, 실제 차단 조건을 재현한다.
2. 정적 검사: 전체 JS 문법, 수정 호출 경로, 단위, truth 접근, 선언/상태 초기화와 리셋을 검사한다.
3. 경계 fixture: 저각/고각/거의 수직, 충분한 이격/미이격, 정렬/미정렬, 저속, 관측 단절/재획득, deadline 초과, 정상 인계를 검사한다. 단순 타임아웃 강제 해제로 통과시키지 않는다.
4. 소규모 비행 A/B: 위 5km/20km 10발, 30km/5km/접근250m/s 10발, 기존 정상 SM-2MR/ESSM·저고도·횡단·이탈·장거리·대수상 대표 조건을 같은 입력/seed로 비교한다.
5. 기존 공통 180발 비교와 해당 원래 회귀를 수정 후보에 다시 실행한다. 기존 성공→신규 실패를 전수 공개하고 원인을 분류한다. 검사 기준을 낮추지 않는다.
6. 실제 게임 브라우저: 자연 탐지→LOCK→정식 VLS 발사→물리 비행→기폭/피해/종료를 확인한다. 실제 함수/private 동등성과 자연 RF 시험을 구분한다.
7. 속도/표시 회귀: 대표 조건 1×/8×/16×, 2D/3D 전환 및 정상/손상 센서 상태를 검사한다. 64×는 성능·과부하 범위로 별도 기록한다.
8. 페이지 오류, 콘솔 오류, core self-test와 원래 관련 도메인/UI 검사를 같은 최종 산출물에서 확인한다.

명중 횟수를 인계 조건의 유일한 합격 기준으로 삼지 않는다. 인계 자체가 안전하고 정상적으로 완료되는지 검증하고, 신관 작동과 최종 피해는 별도 결과로 기록한다.

전체 ENV_D 175,955발 재측정은 이 수정의 원인 확인 전에 시작하지 않는다. 기존 ENV_D 표를 신규 결과처럼 표시하지 않으며 후보와 테이블의 불일치/재계산 필요 표시는 유지한다.

## 9. SM-6 잔여 실패 조사

전환 수정 후에도 PROX_DETONATION_MISS가 남을 수 있다. 이것만으로 신관 버그나 물리 한계로 단정하지 않는다.

최초 접근의 관측 기반 예상 CPA와 실제 궤적, 신호 획득 시각, 기폭 위치·시각, 기록된 miss, 파편 도달 시각의 분리거리, native 피해/Pk/난수 결과를 추적한다.

기존 검증된 모델에서 자연스럽게 발생한 무효 기폭인지, 여전히 남은 유도/제어 인계 문제인지, 별도 코드 결함인지 분류한다. 약 42m까지 접근한 사실을 격추 성공으로 표시하지 않는다. 이 단계에서 신관 반경·파편/Pk·처리 지연을 튜닝하지 않는다.

최초 비명중과 통과 후 phase 역전/종료 문제도 분리한다. 통과 이후에 발생한 단계 역전을 최초 접근 실패의 원인이라고 보고하지 않는다.

## 10. 최종 산출물과 보고

다음을 남긴다.

- 새 버전 HTML, 동일 버전 토큰 상태 문서, 체크섬.
- 실제 게임 소스 diff와 수정한 함수/상태 소유자.
- 원인, 최종 인계 계약, 저각/고각/수상/ESSM에 미치는 영향.
- 조건별/seed별 raw 결과와 전이·제어 전달 로그.
- baseline/수정본의 성공·손상·격추·실패를 구분한 비교표.
- 기존 성공→신규 실패 전수 목록 또는 해당 시험에서 0건이라는 결과.
- 실제 함수/private 동등성, 자연 RF, 전체 월드, 실제 브라우저의 구분된 결과.
- 실행하지 못한 검사와 이유, SM-6 잔여 실패 분류 및 다음 진입점.
- 기준 branch/HEAD, 최종 HTML 크기/SHA-256, GitHub Actions/PR 상태가 있으면 실제 기록.

인계 교착이 해결된 범위만 완료로 판정한다. 전 조건 명중 보장이나 모든 유도 문제가 해결됐다고 쓰지 않는다.

사용자가 원래 Codex에서 직접 작업하므로 실제 업로드는 그 환경의 기존 권한과 업로드 방식을 따른다. main 병합은 별도 명시 승인 전까지 하지 않는다. 새 release/tag를 만들지 않는다.

