# GLOBAL HOLD와 센서 실패·해면 충돌 추론의 연결 감사

읽기 전용 소스 분석이다. 브라우저, AI/planner/RF/NIS/KF 추가 호출, 제품 수정은0이다. **GLOBAL HOLD가 직접 dwell miss를 누적한다는 가설은 현재 자함 경로에서 기각한다.** 다만 연관이 보류되면 측정 갱신이 없으므로 기존 경과시간·코스팅 및 noPlot 휴리스틱에 간접 영향은 줄 수 있다. 그것이 자연13의17→21초 발사 지연 원인인지는 미확정이다.

## 기준

| 제품 | HTML SHA-256 | 해제된 script13 main SHA-256 |
|---|---|---|
| 기존 B ACTIVE | `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6` | `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be` |
| R2 STABLE_B | `c8a9266fe12d6543cf09a1e851af5a0c717e73117945291c5bb5babc9670d584` | `18cd0131dd6ce8d41d66fb7afe470334f27b6bdb5ff0137e8a9cad15328ff2d1` |

아래 행 번호는 고정 R2 main을 해제한 소스 기준이다. 실제 함수명은 `markSpyDwellMiss`다. `spyMarkDwellFailure`라는 함수를 새로 호출한 것이 아니다.

## 반환 계약과 실제 호출 순서

1. `spyGlobalAssignmentsV36`, R2 main L27375~27403: 실제 `trackBSelectB`는 pairs/heldPlots/heldTracks/components를 반환한다. caller에게 주는 Map에는 accepted pair와 `assigned.trackBHeldPlots`만 보존한다. **heldTracks는 노출하지 않는다.** 기존 B의 대응 L27230~27258도 같다.
2. `executeSpyTask`, R2 L27454~27467: focused task는 **먼저** scheduled track에 기존 `spyBestPlotForTrackV31`을 실행한다. match가 있으면 기존 EKF 측정을 수행하고, 실제 수락 후 `spyFinalizeAcceptedTrackV31`에 들어간다. scheduled track이 수락되지 않으면 `markSpyDwellMiss(..., plots.length?'NO_ASSOCIATED_PLOT':'NO_PLOT')`를 호출한다.
3. 같은 함수 L27472에서 그 다음 global batch를 실행한다. L27475에서 `trackBHeldPlots.has(i)`면 `anonymousStats.rejectedPlots++` 후 continue한다. **이 분기는 markSpyDwellMiss를 호출하지 않고 miss counter·reacquiring·mean/P·hit/freshness를 변경하지 않는다.** focused 실패 판정은 global HOLD를 받기 전에 끝나 있다.
4. `recordSpyBeam`/`ok:hits>0`, L27494~27509: 수락되지 않은 HOLD는 beam 기록에서 ok=false일 수 있다. main 전체의 beamHistory/latestTasks 소비는 표시·진단·snapshot 경로이며 이 값을 dwell miss나 kill assessment로 되먹이는 경로는 찾지 못했다.

따라서 “GLOBAL HOLD→caller가 물리 NO_RETURN으로 처리→연속 miss 증가”라는 직접 통합 분기는 없다. focused 경로에는 NO_ASSOCIATED_PLOT과 NO_PLOT이 구분되어 있다. 전자는 plot을 받았지만 기존 NIS/EKF 관문을 통과하지 못한 경우도 포함한다. 이는 이전 B부터 존재하고 보존된 경로다. global 모듈에도 HOLD가 있다는 이유로 둘을 같은 새 결함으로 묶어서는 안 된다.

## 남아 있는 간접 경로

- `markSpyDwellMiss`, L27257~27266: 실제 focused 실패가 `_spyDwellFailed=true`, 연속 miss+1을 설정하고 기존 횟수 기준 이후 reacquiring/REACQUIRE를 만든다.
- `spyFinalizeAcceptedTrackV31`, L27406~27430: 실제 연관 측정 수락이 해면 충돌 추론을 지우고 관련 계수를 복구한다. REACQUIRE task는 기존 규칙대로 실제 수락 두 번이 필요하다. **첫 측정이 수락되어 sensorAge가 작아도 reacquiring=true일 수 있다.** 따라서 “fresh·confirmed이면서 AUTO WITHHELD”는 모순이 아니다. 실제17~20초가 이 경우인지는 원 반환 계측으로 확인해야 한다.
- `updateRadar`, L40203~40250: tick마다 sensorAge를 증가시키고 기존 dwellFailed/sector/overdue를 처리한 뒤 원 EKF를 예측한다. global HOLD가 miss를 직접 증가시키지는 않지만, 측정 갱신이 계속 없으면 기존 overdue 규칙으로 COAST/STALE이 될 수 있다. freshness를 만들어내지 않을 때의 기존 동작이다.
- `wip11cUpdateObservedSeaImpactTrack`, L27663~27683: noPlot은 `!lastUpdateSeen && (memActive || reacquiring || 연속miss기준 || sensorAge기준)`이다. 이는 “사용 가능한 연관 측정 없음”이며 “RF 전단에 어떤 echo도 없음”을 독립적으로 증명하지 않는다. GLOBAL HOLD 뒤 간접적으로 이 조건을 만족할 수 있지만, 기존 추정 하강률·예상 해면 교차시간·함선과의 거리·낮은 추정 고도·확인 지속시간도 모두 필요하다. **HOLD 하나만으로 해면 충돌 추론이 켜지지는 않는다.**

현재 자연13 자료에는 이 구간의 실제 markSpyDwellMiss reason, 연속 miss, reacquire-hit 계수 및 sea-impact candidate가 없다. HOLD 수나 mean 예측·물리 truth만으로 잘못된 퇴역 판정 또는4초 발사 지연을 단정할 수 없다.

## 정적 동일성 증명

원래 `compact_source.cjs` AST 추출기로 기존 B와 고정 R2를 읽기 전용 비교했다. 실제 자함 선언7개가 모두 byte 동일하다: `executeSpyTask`, `spyBestPlotForTrackV31`, `markSpyDwellMiss`, `spyFinalizeAcceptedTrackV31`, `updateRadar`, `wip11cUpdateObservedSeaImpactTrack`, `recordSpyBeam`. 허용된 연관 입력 인증을 넣은 spyGlobalAssignmentsV36만 다르다.

| 함수 | 두 제품의 공통 선언 SHA-256 |
|---|---|
| `executeSpyTask` | `4f44ba84a5cb5b9cedaca315a9ed9c731237e8a7c492b55a3e2e12c3857137ec` |
| `markSpyDwellMiss` | `dfd58afa3b3aa990c20ca9934dc89ef002278e9e833d7195fea6c02ea630e08b` |
| `updateRadar` | `703eca5964a085b8fd2e6309090975d013e3fba80b4b16f9f65d2676f6048ba5` |
| `wip11cUpdateObservedSeaImpactTrack` | `d127db819afe1c2fc18dbca82b7ec351af359ab1d3c582b25229cef59aaa4b00` |

## 향후 계약 개선을 논의한다면

현재는 제품 수정을 승인할 만큼 증거가 충분하지 않아 어떤 함수도 고치지 않는다. 독립적으로 검토 가능한 최소 **메타데이터** 개선은 Map이 receiver-local heldTracks와 현재 dwell의 AMBIGUOUS_ASSOCIATION 결과를 함께 전달하여 NO_RF_PLOT / NO_ASSOCIATED_PLOT / ASSOCIATION_HOLD를 구분하는 것이다. 이미 계산된 결과만 전달하고 mean/P/hits/freshness/IFF/교전권한은 갱신하지 않는다. truth·추가 RF·새 계수도 필요 없다.

이 메타데이터가 생겨도 모호한 group을 scheduled track의 성공 echo로 취급하거나, 실제 focused miss를 지우거나, 실제 측정 소실 후의 정상 노화를 영구 억제해서는 안 된다. sea-impact/BDA가 연관 모호성 때문에 부정적 결론을 잠시 보류하도록 바꾸려면, 먼저 현재 잘못 소비되는 구체적 호출·필드를 입증하고 시간 경계와 진짜 NO_PLOT을 가리지 않는 규칙을 설계해야 한다. 이는 별도 행동 계약 변경과 새 검증이 필요한 사안이며 “메타데이터만 추가하여 동작 영향0”으로 처리할 수 없다.

우선 실행 중인 실제 A3/FCQ/evaluate 반환을 읽는다. 그 증거가 reacquiring/sea-impact를 가리킬 때 실제 markSpyDwellMiss의 원 호출과 기존 필드를 수동 관찰하는 것이 다음 조사다. 어떤 판정 함수도 추가 호출하지 않는다. 자연13 결과 악화는 여전히 미승인이며 RNG 분기나 다른 개선 지표로 상쇄하지 않는다.
