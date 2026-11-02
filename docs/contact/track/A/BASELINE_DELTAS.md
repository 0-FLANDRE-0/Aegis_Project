# Baseline Audit — CIWS 419025와 paired observer 차이

이 문서는 **ARCHIVED 증거 분석**이다. 이 감사 작업 자체는 브라우저 재사격을 실행하지 않았다. 이번 TRACK-A의 fresh baseline/candidate 재실행 결과와 혼동하지 않는다. 숫자는 원본 `docs/ciws/dmg/A/` 및 `docs/contact/friendly/A/`의 고정 증거에서 추출했다. 입력 파일 SHA-256, 원시 서명, 추출 요약은 `baseline-deltas.json`, 78개 주요 사건은 `timeline419025.csv`에 있다.

기준은 `friendly-contact-a` HEAD `4ba64ba0cace9124497a710d00df1b174984ffdc`, 제품은 `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`이다. 기준 상태는 **미승인**이다. `releaseApproved=false`, 기대값 갱신 없음. `419025`는 기존 성공이 나빠진 **FAIL(이전 단계에서 상속)**이며, observer 2건은 **KNOWN_DELTA(미승인)**다. TRACK-A가 이를 동작 그대로 재현하더라도, 원래 결함이 해결되거나 승인되었다는 뜻은 아니다.

## 1. 동일 조건과 결과

원래 D1 fixture: DDG-119, bearing 90°, Kh-35U 1발, 11km, seed 419025, MANUAL, 함포 AutoAA OFF, native `simulateFixedTick(1/60)`. 위협이 소실된 틱에 종료한다. 자동 SAM 방어를 켜거나 다른 ROE를 적용한 비교가 아니다.

| 자료/성분 | 피격 | 종료 HP | 20mm | RAM | 종료 시각 |
|---|---:|---:|---:|---:|---:|
| CG_TURRET_A 원본 | 0 | 100 | 0 | 5 | 36.9500s |
| FRIENDLY_CONTACT_A | 1 | 6.846598842629405 | 68 | 5 | 38.1333s |
| CIWS 분리 수정만 적용 | 1 | 6.846598842629405 | 68 | 5 | 38.1333s |
| 레이더 차원 계약만 적용 | 0 | 100 | 0 | 5 | 36.9500s |

성분 시험은 `friendly/A/isolated.py`가 메모리에 원본/후보 패치를 분리해 실제 게임 함수를 실행한 과거 자료다. 새 계수나 별도 비행 모델을 넣은 자료가 아니다. 이 증거로 **419025 결과 변경은 CIWS own-fire 분리 쪽만으로 재현되며, 레이더 차원 계약만으로는 재현되지 않는다**고 말할 수 있다. 이것만으로 피해·RNG·시커 중 단일 후속 원인이 완전히 분리되었다고 말할 수는 없다.

## 2. 관측 → 파일 → 사격 → 피해 타임라인

아래 파일 번호는 전투 체계 번호와 별개인 C55 local ID다. 물리 표적 ID, source key와 진실 상태는 이 사후 감사 자료 밖의 TRACK-A 전술 입력에 사용하지 않는다.

| 시각 | 원본 | friendly-contact-a |
|---:|---|---|
| 4.7500s | GUN local `-5500001`이 `LOCAL_SELF_DEFENCE` 수용 | 동일 |
| 12.3667s | RAM 1 발사 | 동일 |
| 21.0000s | RAM 1 `PASSED_CPA`, 최근접 4.5057353m | 동일 |
| 21.0167s | RAM 2 발사 | 동일 |
| 27.2333s | RAM 2 `PASSED_CPA`, 최근접 3.5118078m | 동일 |
| 27.2500s | RAM 3 발사 | 동일 |
| 31.5000s | 기존 GUN local `-5500001`에 `PROTECTED_FRIEND` veto | 그 파일의 보호 veto 없음; 로컬 방어 수용 지속 |
| 31.8333s | RAM 3 `PASSED_CPA`, 최근접 4.9489784m | 동일 |
| 31.8500s | RAM 4 발사 | 동일 |
| 32.3667s | Phalanx 사격 없음 | Phalanx 최초 실제 20mm 소모 |
| 34.5500s | Phalanx hit 없음 | BODY hit → `DAMAGED`, seeker 57.8, 나머지 시스템 0, warhead `NORMAL` |
| 35.1500s | RAM 4 `PASSED_CPA`, 최근접 6.0672707m | 같은 종료 시각, 최근접 6.0656198m |
| 35.1667s | RAM 5 발사 | 같은 발사 시각 |
| 36.9333s | SeaRAM `KILL` | 요격 성공 사건 없음 |
| 36.9500s | RAM 5 `PROX_DETONATION_KILL`, fixture 종료 | 계속 진행 |
| 37.0500s | 이미 종료 | RAM 5 `SEA_IMPACT`, 최근접 3.8628267m |
| 38.1333s | 이미 종료 | 함 피격, HP 100 → 6.8465988 |

기존 파일 보호가 해제되면 무조건 더 나은 교전 결과가 된다고 단정할 수 없다. 이 시드에서는 실제 추가 사격과 피해 경로가 생긴 후, 기존 RAM의 후속 비행 결과가 달라졌다. 반대로 이 단일 시드를 살리기 위해 Phalanx 발사를 다시 차단하거나 Pk·조준·신관·발사 간격을 조정해서는 안 된다.

### 어디까지 증명되었는가

**확인됨:** 같은 RAM 1~4의 발사/종료 시각, 원본 GUN 파일의 보호 veto, 후보의 추가 20mm 사격, 실제 hit/시스템 손상, RAM 5 결과 차이, CIWS-only 성분 재현. 원시 로그와 서명은 JSON/CSV에서 고정했다.

**아직 미확인:** 과거 419025 D1에는 `PROTECTION_ASSOCIATION`의 source-key 전이와 사건별 global RNG 전후 값이 없다. 따라서 그 시드의 정확한 물리 source→local file 전환 및 최초 RNG 분기 시점은 새 계측으로 확인해야 한다. 다른 4개 HP0 시드에서 확인한 오염 타임라인을 이 시드의 관측 기록인 것처럼 대체하지 않는다.

**잘못 단정하면 안 되는 부분:** `WIP113_ASM_DAMAGE_BEHAVIOR.seekerFailDamage=100`(현재 main JS 22500행)이고 기록된 seeker 손상은 57.8이다. 이 값 하나로 hard seeker failure 또는 frozen-command drift가 시작되었다고 말할 수 없다. `wip113RefreshBehavior`(22514행)는 해당 100 임계에서만 `seekerFailed`를 켠다. legacy `_guidanceDegraded`의 무작위 drift 역시 `!wip113HasAnySystemDamage(em)` 조건(31481행) 아래다.

`applyPhalanxProjectileHit`(37346행)는 실제 hit에서 global `simRandom()` critical 판정 및 `rand(10,22)` 구조 손상 경로를 사용한다. 추가 hit가 후속 global RNG 소비를 바꿀 수 있는 **코드상 경로**는 확인된다. 하지만 아카이브의 종료 global RNG `4152832030` 대 `635811877`은 서로 다른 끝 틱 2217 대 2288에서 찍혔다. 이 마지막 값 차이만을 동일 시점의 원인 증명으로 사용하지 않는다.

Fresh 재현에서는 34.55s hit 직전/직후의 같은 틱 RNG, 실제 `seekerFailed/guidanceMode`·비행 명령, RAM 5 RF/IR 측정·유도 상태, local file 연관 근거를 함께 비교해야 한다. 사후 truth는 이 시험 증거에만 둘 것. 단순 성공률 상승이나 최종 HP만으로 closure하지 않는다.

## 3. paired observer 2건

고정 자료: `friendly/A/evidence/regression/paired-current/baseline-comparison.json` 및 `analysis/paired-observer-delta.json`.

| paired 경우 | 달라진 단언 | observer 변경 경로 수 | HP | VLS 잔여 | 물리/RNG/표적 사건 |
|---|---|---:|---|---|---|
| DDG 습격 | `sameExistingObserverState` | 874 | 100 → 100 | 90 → 90 | fixture 끝 시점 동일 |
| CG 습격 | `sameExistingObserverState` | 43 | 100 → 100 | 115 → 115 | fixture 끝 시점 동일 |

6조건 × 7단언에서 40/42가 동일하고 위 2개가 다르다. idle/damaged는 양 함정 모두 일치한다. 기존 도메인 전체 최초 상태는 **404 PASS / 2 observer 차이 / 14 구형 EMCON UI 미완료 = 420**이다. 현재 UI 213과 WebGL 8발/29단언을 이 420에 중복 더하지 않는다.

이 차이는 단순히 로그 키가 추가된 정도가 아니다. DDG에는 anonymous plot 연관/거부 횟수, 스케줄러 task/cursor/load, 여러 트랙의 평균·속도·공분산·source가 달라졌다. CG의 43개 경로는 트랙 8의 `SURFACE → UNKNOWN`, 고도 평균 `8 → 42.47837726538155m`, 수직속도 및 공분산 등의 변화다. friendly patch가 3D 관측 뒤 수면 prior를 억제하고 cross-domain 연관을 달리하여 생긴 실제 추정 경로 변화로 해석된다.

fixture 끝의 물리·RNG·HP·표적 상태가 같은 것은 확인된 제한적 증거다. 모든 미래 전투 결과가 같다는 증명은 아니다. **기대값은 승인되지 않았고 갱신하지 않았다.** TRACK-A에서는 이 기존 observer 변화가 후보와 baseline 사이에서 추가로 달라지지 않아야 한다. 진단 필드만 제외하되 평균·공분산·분류·sensor age·기존 RF counters를 비교에서 제외하면 안 된다.

## 4. C55 입력·소유자·수명·소비자 감사

아래 행 번호는 `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`의 packed index 13을 푼 **현재 기준 JS**다. 과거 docs의 파일 줄번호나 새 TRACK-A 제품 줄번호가 아니다. 기준 소스 SHA는 JSON에 있다.

| 지점/행 | 소유자 및 입력 | 관측/파생/쓰기 | 다음 소비자·주의점 |
|---|---|---|---|
| `navalCiwsSourcesD` 6354~6359 | 함별 runtime, 물리 반사체, 자함 무장 발사 재고 | 물리 프런트엔드에서 source pool, RCS, 알려진 own-fire boolean 생성 | owner/faction을 적성 판정으로 넘기면 안 됨. 무DL Harpoon은 own 예외에서 명시적으로 제외 |
| `createWeaponContextD` 6406~6439 | NPC lexical owner의 tracks/closeIn/SAM/RAM | 별도 C55 banks/serial/clock/WeakMap와 함별 seed | 플레이어 TrackStore와 합치지 않음. NPC `truthObjectForTrackV27`는 6477행에서 null stub |
| `ciwsLocalMeasurement` 36964~36988, NPC 7575 이후 | mount 위치·자세/차폐, 실제 반사체는 이 센서 경계 안에서만 | noisy **range/az/el 3차원** 관측. rx/ry/rz는 그 3개의 좌표 변환. positionVarianceM2는 대각 Cartesian 근사 | 도플러/속도 직접 측정 없음. rx/ry/rz와 range/az/el을 6개 독립 관측으로 세면 안 됨. null/거부를 plot으로 바꾸면 안 됨 |
| `c55SensorSweep` 37216~37246, NPC 7629~7652 | noisy local position, 기존 파일 예측, known-own flag | 거리 gate, own/non-own partition, sweep 내 seen 집합. source 순서 greedy | NIS gate가 아님. 같은 파일을 한 sweep에서 2회 쓰지 않지만 전역 최적 할당/모호성 해결은 없음 |
| `c55UpdateFile` 37197~37212 | noisy xyz, 대각 position variance | per-axis filter가 속도·오차 추정. 초기 속도 0은 prior, 속도 분산 prior 250000. hits/quality/confirmed/age 갱신 | rvx/rvy/rvz·가속·CPA·TTI는 파생량. 계수 보존 |
| `c55CmsRows` 37168~37177 | 해당 함의 최신 confirmed CMS 관측 파일 | 익명 trackId, 관측 기반 상대 상태/identity/sigma, cueEligible | cue는 탐색 힌트이며 local RF 확인을 대체하지 않음 |
| `c55AssociateCms` 37179~37195 | local 상태 + CMS 위치·속도·identity | 근접 CMS로 cue/보호 연결, ownFireEvidence이면 FRIEND 보호 | 가장 가까운 파일 외에도 gate 안의 보호 파일이 있으면 veto. matched/protected 조건이 사라져도 보호가 남을 수 있어 근거 TTL 감사 필요 |
| `c55StepSensors` 37271~37295 | 함별 C55 clock, mount bank, CMS rows | predict/age/expiry → sweep → CMS 보호 → CPA/approach → audit/winner | 독립 store 유지. control tick에서 호출 횟수 검증 필요 |
| `c55ContactAudit` 37249~37269 | 확인된 local position/velocity/quality, 보호 근거, 함체 사각 | 운동 기반 missile-like/approach/CPA/회전 가능성으로 자체방어 동의 | 실제 label/faction/owner로 적성 지정하지 않음. 이미 날아가는 RAM은 score×2.5이지 무조건 사격 중지 조건이 아님 |
| `updateCIWS` 37828 이후 | C55 audit winner와 local 추정 상태 | 기존 Phalanx/SeaRAM 상태·사격·무장 재고 실행 | 기본 MANUAL에서도 기존 local self-defence가 실행되는 시험이며 AUTO SAM과 혼동 금지 |

### 기존 정보 경계 위험 — TRACK-A에서 조용히 수정하지 말 것

1. **proxy physical ID 전파:** 센서 프런트엔드는 `CIWS_C55_SENSOR_LINKS` WeakMap로 물리 source를 보유하지만, `c55SensorSweep`는 `best.proxy.id=e.id`도 쓴다(37243~37246 / NPC 7649~7652). 이 proxy ID는 `c55Select`, spotting reset, `ciwsSpotAdjustedSolution`, 탄의 `intendedTargetId`로 전달된다(37299~37303, 37869/37886/37898). 분류/적성 정책이 이 ID를 직접 읽는 것은 찾지 못했지만, 물리 식별자가 제어 bookkeeping으로 전파되는 **기존 경계 위험**이다. 새 TRACK-A 정규화 payload에 복사하지 말 것. 실제 표적 ID 사용은 물리 충돌·프런트엔드 측정 또는 사후 감사로 한정해야 한다.
2. **front-end 추적 mode:** WeakMap의 source key는 `lock` 일치로 TRACK/SEARCH dwell을 고르는 데 사용된다(37232 / NPC 7638). 실제 센서 프런트엔드의 상태 유지 용도이고 CMS 적성 판단 입력은 아니지만, 이를 독립 관측 provenance나 공용 target identity로 노출해서는 안 된다.
3. **보호 근거 수명:** `ownFireEvidence`는 OR로 파일 수명 동안 유지된다. friendly patch의 own/non-own partition은 교차 오염을 막지만, CMS에서 온 protectedIdentity 자체의 일반적인 만료 계약을 해결하지 않는다. `c55AssociateCms`는 현재 근접 보호 파일이 없을 때도 특정 matched/protectedCmsId 조건에서만 지운다. TRACK-C 후속 감사 대상이다.
4. **조회 시 lazy 쓰기:** 기존 `c55Snapshot`(37305행)은 `c55Bank`를 호출하므로 bank가 없을 때 조회가 bank를 만들 수 있다. 새 독립 진단 조회는 이를 재사용하지 말고 existing Map의 get/values만 읽어야 한다.
5. **레거시 정의와 live 경로 구별:** `ciwsRelativeKinematicsTruth`(36958), `ciwsResolveLocalContactB1`(37003)는 코드에 남지만 현재 C55 live selector의 호출 근거를 찾지 못했다. 존재 자체를 현재 C55 ranking의 truth 입력으로 둔갑시키지 않는다. 반대로 전역 `truthObjectForTrackV27`의 물리 해석·진단 consumer는 존재하므로 프로젝트 전체가 이미 정보 비누수라는 보증도 하지 않는다.

## 5. TRACK-A에 요구되는 추적 항목과 다음 검증

- C55 측정 벡터는 range/az/el, Cartesian 좌표는 `derivedFromMeasurement`, 속도·CPA·TTI는 `filterEstimated/derived`, initial velocity/variance는 `modelPrior`로 표시한다.
- trace는 이미 계산된 거리 gate, known launch partition 판정, seen 제외, 수용/새 파일/최대 수 제한/expiry, 이전/다음 local 상태를 기록한다. NIS가 없는 C55 경로에 가짜 NIS를 넣지 않는다.
- observerShip/mount는 자기 장비 ID이며 허용된다. 전술 track/local file ID도 허용된다. 실제 물리 source key/proxy ID/label/owner/faction/진실 좌표는 정규화·소비자 레코드에서 금지한다.
- baseline 재사격은 기존 `__CIWS_DMG_A__.run({ship:'DDG_119_LATE_FLIGHT_IIA',bearing:90,seed:419025},true)`와 동일한 native fixture로 한다. 게임 월드에 새 전술 정책이나 AUTO SAM을 넣지 않는다. 기존 evidence 파일을 덮어쓰지 말고 TRACK-A 전용 경로에 저장한다.
- 진단 OFF/ON 결과는 트랙·물리·탄약·global 및 각 sensor/gun RNG를 같은 틱에서 비교한다. 타임스탬프/host wall time만 명시적으로 제외한다. 진단 조회가 쓰기·RNG·시뮬 tick·스케줄러를 바꾸면 FAIL이다.
- 새 TRACK-A가 419025 결과를 바꾸면 수동으로 구 기준을 맞추거나 성공으로 승인하지 않는다. A의 목적은 **동작 보존 trace**다. 원래 419025 원인 분리 및 paired correctness closure는 여전히 별도 증거가 필요하다.
