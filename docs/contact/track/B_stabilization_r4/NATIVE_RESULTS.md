# R4 fresh native 검증

최종 R4 두 제품에서 승인된 native 검증을 **새로 실행하여 PASS**했다. R3 실행 결과를 현재 제품의 실행 증거로 재사용하지 않았다. 원 strict 시험의 정책 차이 두 건은 **FAIL 그대로 보존**하며 자연 교전·성능·배포 승인은 별도다.

| 범위 | 결과 |
|---|---|
| 변경하지 않은 R1 정책 단위시험, R4 실제 module | 39/39 |
| 변경하지 않은 R3 bounded exact 시험, R4 실제 module | 28/28 |
| 원 B47 strict | **46/47; 상속된 component>12 전체 HOLD 기대값 차이** |
| 원 R2 residual15 strict | **14/15; 상속된 C=0/full13 HOLD 기대값 차이** |
| fresh ACTIVE basic | 원 대표19/19 + 새 native23/23 + 실제 S/epoch/callback18/18, OFF/ON 각각 |
| fresh 원 native 전체23그룹 | SHADOW/ACTIVE 각각 OFF84/84·ON90/90 |
| fresh 원 cohort14 | 4 contexts 모두14/14; 원 helper가 진단 ON 강제 |
| fresh 실제 native 포화 | oldB42/42·SHADOW42/42·ACTIVE44/44 |

- ACTIVE: `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`
- SHADOW: `3c7d2490e7e0d6fe94452e43d8f22132fbdd8add83986208bf7173068c478444`
- 실제 module: `1abcb0863af7908931aa8a3f7c28cda37c10077f086eb903f387cefa7f1f86d7` (R3와 byte동일)

이번 R4 제품 변경은 실제 `spyFinalizeAcceptedTrackV31`의 reacquire task ownership guard다. 다른 firm file에 연관된 관측을 scheduled file의 reacquire 상태로 잘못 취급하지 않도록 한 변경이다. native 시험 전 실제 packed main을 읽어 solver occurrence1·두 mode·실제 finalizer guard occurrence1을 확인했다. 실제 몸체·source 위치·해시는 `evidence/RUNTIME_PRODUCT_RECEIPT.json`에 있다. build scope/inverse 증거와 fresh native 실행 증거는 구별한다.

## fresh 실행 및 순수성

SHADOW basic3 contexts는 50.03s, ACTIVE basic3 contexts는45.95s, 원 native/cohort8 contexts는131.57s, 포화3 contexts는47.45s였다. 최대 동시 브라우저는 이 lane에서1개였다. 이 wall time은 성능 벤치마크가 아니다.

SHADOW의 새 ACTIVE 기대4건은 적용되지 않으므로 raw19/23 FAIL4를 그대로 남겼다. 별도 통제에서 모든 fixture의 filter/P·physical·private/global RNG 및 마지막 상태가 원 B와 정확히 같았다. own/NPC covariance 양성의 제안 로그도 확인했다. ACTIVE는 새 native23/23을 통과하고 진단 OFF/ON 결과·상태가 정확히 같다.

metadata18에는 실제 native AIR4·surface position2·CARTESIAN3 innovation S/logdet 일치, epoch 일치만 인증, 지연 offboard 무효, receiver 원점·속도 보존, surface 높이 prior를 물리 관측으로 세지 않기, finite Doppler3D callback의 position-only2D 인증 금지가 포함된다. covariance 양성 fixture는 실제419012 자연 전투 재현으로 표시하지 않았다.

원 native23그룹과 cohort14의 helper·assertion·초기 입력·허용 오차를 바꾸지 않고 최종 제품에서 fresh8 contexts로 실행했다. 전체 nativeResult(schema/header/A 진단 포함) 및 fixture별 full private-state hash가 oldB와 정확히 같았다. 실제 post-world state, ENV status, query·snapshot 순수성, 진단 OFF/ON 및 함수복원 통제를 모두 통과했다. cohort는 원 helper 내부에서 ON으로 강제하므로 OFF 검증으로 세지 않는다.

실제 포화 native fixture에서는 익명 receiver 측정과 명시된 owned prior를 기존 caller→실제 NIS→solver→원 native filter update에 넣었다. clear13/16 ACTIVE는 선택13/16·각 file correction1회·birth0이다. oldB/SHADOW는 원 HOLD를 소비한다. 동일 위치 equal13은 모든 제품에서 HOLD13·correction0·birth0·age0.5 및 full private-state 동일을 유지했다. 다른 private owner/canonical store 변화와 synthetic forbidden getter 읽기는0이다. 이 fixture는 RF 발생·자연 전투 증거가 아니다.

## 원값과 실패 보존

원 B47 `bounded.connectedThirteenByThirteenHeld`는 blanket component>12 HOLD와 bounded/certified 정책의 차이로 FAIL이다. 원 R2 residual15의 `negative.noCertifiedCDoesNotInvokeResidualEvenWithClearGlobalWinner`는 C=0/full13을 R3/R4가 exact로 판정하므로 FAIL이다. 두 원문 시험·기대값·허용 오차를 수정하지 않았다. R4에서 추가된 strict 실패는 없다. 새28시험은 C>0 R2 보존, full13/16 C0 exact, 참 동률·partial·17+ HOLD, 원 native winner 및 순수성을 별도로 검증한다.

R3의 rejected general routing과 이전 unknown-header getter failure raw/source는 이전 경로에 그대로 있다. 최종 R4 실제 module에 같은 getter 재현 시험을 실행해 읽기0·예외0을 확인했다. 가상 getter 경계시험이며 실제 producer에 truth 필드가 존재했다고 주장하지 않는다.

## raw·진단 차이 전수 기록

read-only 후처리에서 basic6 contexts의 원/신규/metadata native 결과, private-state hash, B 진단·초기 설정·ENV status를 R3와 전수 비교해 delta0을 확인했다. 원 native/cohort8 contexts와 포화3 contexts의 native 결과·outer 진단·상태 hash도 R3 대비 delta0이다. 파일명·제품 SHA·wall time은 별도 provenance로 유지하며 같은 실행의 byte동일이라고 부르지 않는다.

원 B 대비 outer 진단의3/23/2347개 leaf 차이는 이전 단계에서 상속된 초기 header와 진단 내용이다. 전체 nativeResult는 delta0이지만 전체 artifact가 byte동일하다고 표시하지 않았다. 모든 selected raw value의 전수 leaf diff는 `evidence/native-diagnostic-deltas/`에 보존하고 자동 승인이나 필드 제외를 하지 않았다.

## 바뀐 finalizer 증거의 범위

별도 lane의 `finalize-native-vm.json` 및 `finalize-native-vm-shadow.json`은 각 최종 제품에서 추출한 실제 finalizer 함수의 **dependency count stub을 사용한 격리 VM 시험**이다. 각3096 checks·600 actual function steps·12 mode/engagement 조합을 통과했다. 이를 실제 게임 월드 통합 시험이나 자연 RF/전투 건수에 더하지 않았다. 이 native fixture 묶음의 통과만으로 실제 foreign-firm 자연 교전의 해결을 선언하지 않는다.

최종 집계는 `NATIVE_SUMMARY.json`, 권위 raw는 각 `evidence/native-shadow`, `native-active`, `original-native-full`, `native-saturation`의 SUMMARY/PROVENANCE와 raw-before-aux다.26개 고정 시험 입력 hash도 readback PASS다. 기존 R1/R2/R3 자연 교전 결과·실패 및 별도 broad 검수는 그대로 남아 있으며 이 보고서가 승인하지 않는다.

브라우저/controller를 닫고 공유 lease를 반환하여 다른 lane에 알렸다. 이후 보고·diff 집계는 read-only이며 추가 브라우저를 실행하지 않았다. 기존 소스·원 raw·기대값·센서/RF·피해/RNG·물리 계수는 이 시험 과정에서 변경하지 않았다.
