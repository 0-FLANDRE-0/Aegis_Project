# TRACK-B C55 연관 감사와 최소 변경 권고

이 문서는 **설계 감사와 shadow 준비 내역**이다. C55 live 연관 선택·제어, RNG, RF, 사격·피해 계수, 기대값은 바꾸지 않았다. 초기 감사 후 root 검토를 받아 `c55-shadow.js`와 `patches-c55.json`을 준비했다. 이 감사 담당자는 브라우저 사격/HTML 생성/커밋을 실행하지 않았다. 실제 최종 합성과 native 검증은 별도 결과를 확인한다. 적용 기준은 root가 고정한 `/dev/shm/track-b-baseline-source.js`의 현재 TRACK-A RC2다. 아래 줄번호는 그 소스 기준이며 초기 friendly-contact source 번호가 아니다.

## 1. 권고

**현재 live C55는 no-op 유지하고, 공통의 순수 geometry candidate/일대일·모호성 분석을 shadow로 먼저 연결하는 것이 최소 안전 범위다.** C55가 이미 안전하거나 개선 불필요하다는 뜻이 아니다. source 순서 때문에 잘못된 재생성/번호 교환이 생길 수 있지만, 기존 loop를 즉시 batch commit으로 교체하면 같은 sweep의 RF 추적 mode와 후속 무장 RNG까지 달라질 수 있다. 미승인 419025가 있는 상태에서 이를 조용히 승인해서는 안 된다.

TRACK-B에서 다른 관측 경로의 연관을 실제로 개선하더라도 C55 shadow-only 범위는 별도 표시한다. 이 범위를 실제 개선 완료나 B 전체 CLOSED로 계산하지 않는다. root 검토 및 아래 native evidence 후 검증된 C55 경로만 별도로 활성화할 수 있다.

## 2. 현재 두 lexical 문맥

| 항목 | 자함 | NPC |
|---|---|---|
| `c55SensorSweep` | 37336~37370 | 7736~7763 |
| source pool | physicalShips가 있으면 `navalCiwsSourcesD(ACTIVE_SHIP_RUNTIME)`, 없으면 기존 ASM/AIR/HELO/own SAM/RAM 순서 | `navalCiwsSourcesD(owner)` |
| state owner | 자함 `CIWS_C55`의 mount별 banks | `createWeaponContextD(owner)`의 별도 banks/serial/clock/WeakMap 및 owner seed |
| 물리 센서 합성 | source 실제 위치/RCS/LOS는 `ciwsLocalMeasurement` 내부 프런트엔드 | 동일 함수 구조, owner mount origin/geometry |
| 연관 | noisy 상대 xyz와 기존 예측 xyz의 거리, source 순서 greedy, sweep별 `seen` | 동일 |
| own partition | `!!r.ownFireEvidence !== !!src.own`이면 제외 | 동일 |
| 파일 생성/업데이트 | 신규 local ID 할당→WeakMap/source proxy 연결→own flag OR→native filter | 동일 |
| CMS 연관/보호 | `c55AssociateCms` 37299~37315, 전달된 해당 owner CMS rows만 읽음 | 공용 함수가 owner별 rows를 인자로 받음 |
| tick 순서 | `c55StepSensors` 37395~37418에서 predict/age/expiry→sweep→CMS보호→CPA/approach/audit→winner | NPC 7788 이후 같은 순서 |

함별·mount별 로컬 파일은 독립 목적의 store다. 두 함정의 같은 음수 local ID나 같은 좌표를 공통 TrackStore로 합쳐서는 안 된다. 같은 반사체를 두 mount가 독립적으로 측정하는 것도 중복 오류라고 삭제하지 않는다.

## 3. 실제 gate와 관측 차원

실제 C55 측정은 noisy **range/azimuth/elevation 3차원**이다. `rxM/ryM/rzM`는 그 관측의 Cartesian 변환이며, `rvxMps/rvyMps/rvzMps`, CPA/TTI/가속도는 local filter의 파생값이다. C55 source의 실제 속도, label/faction/owner, proxy physical ID를 별도의 측정 속도나 연관 identity로 사용할 수 없다.

현재 후보 gate는 각 `meas`/file에 대해 다음 그대로다.

```text
d = hypot(file.rxM-meas.rxM, file.ryM-meas.ryM, file.rzM-meas.rzM)
gateM = 55
      + meas.rangeM × radians(cfg.searchAzSigmaDeg) × 3
      + (file.localHits < 5 ? 2200 : 350) × min(0.35, file.localAgeS)
eligible = !seen && sameKnownOwnPartition && d < gateM
```

`55`, `3`, `2200/350`, `.35`와 GUN/RAM의 현재 sigma를 바꾸지 않는다. 이는 NIS가 아니므로 `nis`라고 재명명하지 않는다. 큰 covariance만으로 더 큰 거리 gate를 새로 만들지도 않는다. 양의 경계는 기존의 strict `<`다.

GUN searchAzSigma는0.16°, RAM은0.18°(37005~37028). 5 hit 이전의 broad coast term은 특히 후보 충돌을 만들 수 있다. 필터 warm-up이나 confirmation을 완화해 그 충돌을 감추지 않는다.

## 4. source 순서 의존성 — 기하 반례

**순수 기하 fixture 예시이며 실제 센서 사격 결과가 아니다.** GUN, 양 file localHits=8, localAgeS=.05, 같은 own partition, 같은 y/z. 예측 x는 T0=4000m, T1=4200m, noisy plot x는 P0=4099m, P1=4000m, z≈2m다. 현재 native gate를 그대로 쓰면 약106.84m/106.01m다.

| 후보 | 거리 m | gate 통과 |
|---|---:|---|
| P0→T0 | 99 | 통과 |
| P0→T1 | 101 | 통과 |
| P1→T0 | 0 | 통과 |
| P1→T1 | 200 | 거부 |

- P0 먼저: nearest T0를 쓰고 `seen`에 넣음 → P1은 T0를 못 쓰고 T1도 gate 밖 → 신규 파일 생성.
- P1 먼저: T0를 쓰고, P0는 T1에 들어감 → 기존 파일2개 모두 갱신.
- 같은 geometry의 bounded 최대-cardinality 일대일 assignment는 두 순서에서 P0→T1, P1→T0를 제안할 수 있다.

그러나 이것을 곧바로 **올바른 truth ID 승계**라고 선언하면 안 된다. 관측 자체가 모호한 교차에서는 최대-cardinality가 duplicate birth를 줄이는 대신 ID swap을 만들 수 있다. B는 `same source count`만 볼 것이 아니라 false merge/split/ID swap과 ambiguous component를 따로 측정해야 한다.

## 5. 즉시 batch 교체가 unsafe인 이유

1. RF 생성과 file update가 interleave되어 있다. 각 source의 `lock`은 선택된 파일의 `CIWS_C55_SENSOR_LINKS`와 source key 일치를 읽어 TRACK/SEARCH를 고른다(자함37352, NPC7745 부근). 앞 source가 선택 파일의 링크를 갱신하면 뒤 source의 같은-sweep mode가 달라질 수 있다. 모든 측정을 먼저 만들고 마지막에 commit하는 변경은 RF 계수를 안 바꿔도 dwell/노이즈 draw 수·측정 이력이 달라질 수 있다.
2. C55 source 순서는 physics emitter enumeration 순서다. 순서 자체를 재정렬하면 mount-private RNG에서 어느 물체에 어느 draw가 붙는지도 바뀐다. 이를 source physical ID로 정렬해 안정화하면 비누수 계약을 깨며 관측도 달라진다.
3. 새 파일의 local ID는 생성 순서에 따라 달라진다. 선택된 local ID는 Phalanx aim/shot private seed에 참여한다(37422 이후 `c55Select`). 출생 수/commit 순서의 변화가 명중 결과까지 영향을 줄 수 있다.
4. 동일 own partition 안의 own 아닌 Harpoon/헬기/적 ASM은 관측으로 구분해야 한다. known-own boolean을 이용해 Harpoon의 숨은 owner를 FRIEND로 바꾸거나, ambiguity를 이유로 적 ASM을 보호해서는 안 된다.
5. 이미 flying RAM에 관한 score×2.5는 기존 우선순위다. 후보 ambiguity를 해결한다며 이 값을 바꾸거나 Phalanx를 강제로 기다리게 해서는 안 된다.

## 6. 최소 shadow 알고리즘 계약

입력은 해당 mount의 **sweep 시작 시 기존 예측 파일 snapshot**과 원래 순서/원래 native 업데이트를 유지하면서 얻은 **실제 accepted noisy measurement copy**다. snapshot/copy는 whitelist로 제한한다.

- file: 전술 local ID, 상대 위치, filter-derived 속도·필요한 age/hits, known-own flag, 해당 owner/mount 문맥. physical source key/proxy ID/label/truth velocity 없음.
- measurement: 상대 xyz, range/az/el, 제공된 variance/quality, 수신 tick, frontend가 이미 제공한 known-launch safety boolean. 새로운 truth 분류/owner 판정 없음.
- 순수 candidate helper: 원래 finite 조건·거리 식·strict gate·own partition으로 후보 graph를 만든다. 기존 `seen` native 단계의 결정은 비교용으로만 별도 보존한다.
- one-to-one 제안: connected component별 최대-cardinality 후 총 normalized distance 최소 등 bounded 방법을 비교한다. geometry와 기존 gate만 사용하며 목표 physical ID나 faction으로 tie를 깨지 않는다.
- 모호성: 이번 최소안은 새 숫자 margin 대신 **candidate graph에서 한 plot 또는 file에 복수 edge가 있는 component**를 `AMBIGUOUS_COMPETITION`으로 표시한다. exact tie도 별도 기록한다. 이는 shadow 진단이며, 실제 발사 hold/보호/삭제/merge로 이어지지 않는다.
- 독립된1×1 component는 resolved로 보고 native mapping과 동일해야 한다. 자체가 새로운 유효 타깃/authority를 만들지 않는다.
- 제안이 미정이거나 규모 상한을 넘으면 diagnostic reason만 남기고 native 경로를 그대로 둔다. 파일 capacity48/expiry2.0s 정책을 바꾸지 않는다.
- 원 native source 순서·RF·file update·ID 할당·hit/age·identity·CMS보호·weapon consumer는 그대로 실행한다. **shadow가 후보/trace를 계산한 것과 실제 consumer가 개선된 것을 별도 coverage로 표시한다.**

실제 적용으로 전환할 때는 전역 batch commit이 반드시 필요한지 먼저 검토한다. 매우 제한된 독립·비모호 component에서 이미 native와 같은 mapping만 반환하는 기계적 추출은 가능하지만, 이를 source-order 문제의 해결이라고 과장하지 않는다.

### 준비된 shadow hook

`patches-c55.json`은 module 삽입1개와 두 lexical 문맥 각각5개 hook, 총11개 패치다. 현재 pinned baseline에서 in-memory 적용과 역치환 byte 동일을 확인했다. 이 검사는 native 사격 PASS를 대신하지 않는다.

- sweep 시작에서 기존 local file의 상대 위치/hits/age/known-own만 snapshot.
- 원래 실제 센서의 accepted measurement를 원래 순서에서1회 포착. source key/proxy/실속도는 copy하지 않음.
- native가 이미 계산한 각 후보의 `d/gate` 및 최종 anonymous local file ID만 별도 기록.
- sweep 뒤 shared `trackBSolveB`를 호출한다. internal numeric-cost ABI 필드명은 `nis`지만 값은 **거리m**이며 `costUnits:'m'`, `ambiguityDeltaCost:0`을 명시한다. 새 C55 trace에는 NIS 필드 대신 `distanceM/distanceGateM`만 내보낸다. NIS margin1을 거리/normalized cost에 적용하지 않는다.
- native seen 때문에 원래 평가하지 않은 frozen-state edge는 `SHADOW_COUNTERFACTUAL_NATIVE_SEEN`, 실제 계산된 edge와 값이 같은 경우는 `NATIVE_EVALUATED_DISTANCE`로 구별한다. 신규 native file은 기존 파일 assignment 제안과 혼동하지 않도록 `NATIVE_NEW_FILE`로 표시한다.
- 현재 C55 graph가12개를 넘는 연결 component이면 shared solver의 bounded hold는 **shadow 결과**다. native 제어에는 hold를 전달하지 않는다. accepted plot256개를 넘으면 partial 성공을 주장하지 않고 diagnostic LIMIT를 기록한다.
- `TRACK_B_DIAG.enabled=false`이면 snapshot/measurement 배열 및 helper 호출이 없다. 새 local 변수는 null뿐이다. query, 생산자, RF/NIS, lazy bank constructor를 추가로 호출하지 않는다.

모듈·후크의 의미는 SHADOW ONLY다. 실제 candidate가 바뀐 것처럼 기존 native 결과를 대체해 검수하거나, 이 파일만으로 C55 live 개선이 완료되었다고 보고하면 안 된다.

## 7. own-fire 및 CMS 보호 안전

- 현재 own/non-own partition은 두 lexical 문맥 모두 유지되어야 한다. 모호한 geometry, source-order permutation, capacity 포화에서도 known-own RAM 측정이 적 ASM 파일에 들어가지 않아야 한다.
- `src.own`은 기존 known-launch inventory 증거다. `ownFireEvidence`를 분류 truth나 팀 정보로 재계산하지 않는다. Harpoon 무DL 정책의 예외를 새로 만들지 않는다.
- `c55AssociateCms`는 nearest row 외에도 gate 안의 FRIEND/NEUTRAL을 보수적으로 veto한다. 연관 개선이 이 보호를 지우거나 FCS 권한으로 올려서는 안 된다.
- 기존 CMS `protectedIdentity`의 sticky 수명과 proxy physical ID 전파 debt는 A 감사에 남아 있다. 이는 별도 C/정보 경계 변경 검토 사항이며 B의 C55 assignment 개선에 몰래 섞지 않는다.
- trace는 known-launch boolean과 anonymous local file ID만 공개한다. source key/proxy physical ID가 필요한 비교는 test-only AFTER_ACTION 자료에만 둔다.

## 8. 419025와 승인 기준

현재 A 보고서는 419025의 Phalanx34.55s hit에서 global RNG가4262938539→3399989146→3066683312로2회 소비되고, 실제 seekerFailed=false/guidance NORMAL인 증거까지 확보했다. 그 후 RAM의 RF/IR 측정이 달라지는 경로가 있지만 단일 원인 closure는 아직 미승인이다. old CG 기준 kill을 되살리려고 association threshold/RNG/발사 타이밍을 조정하지 않는다.

C55 shadow는 419025를 포함한30시드에서 **트랙·전투·physical·global/private RNG·타이밍을 baseline과 동일**하게 유지해야 한다. 그렇지 않으면 shadow 구현부터 FAIL이다. live 적용 시에는 새 성공→실패뿐 아니라 파일 승계/모호성/센서 mode·private draw/탄 소모 변화도 원인별로 제출한다. seed419025와 paired observer 기존 차이는 여전히 미승인이다. 코드나 기대값을 이 문서에서 승인하지 않는다.

실행 fixture와 판정 표는 [C55_FIXTURE_PLAN.md](C55_FIXTURE_PLAN.md)에 정리했다.
