# R3 bounded exact native 검증

새 R3 정책의 제한된 순수함수·native 통합 계약은 **PASS**다. 원문 strict 시험 두 건은 정책 차이로 **FAIL을 그대로 보존**했다. 이 문서는 자연 교전, 성능 또는 배포 승인을 대신하지 않는다.

| 범위 | 결과 |
|---|---|
| 변경하지 않은 R1 정책 단위시험 | 39/39 |
| 신규 R3 bounded exact·보존·음성·순수성 | 28/28 |
| 원 B47 strict | **46/47; component>12 전체 HOLD 기대값 차이 1건** |
| 원 R2 residual15 strict | **14/15; C=0/full13 HOLD 기대값 차이 1건** |
| 추가 ACTIVE native | 원 대표19/19 + 새 native23/23 + 실제 S/epoch/callback18/18, OFF/ON 각각 |
| 원 native 전체23그룹 | SHADOW/ACTIVE 각각 OFF84/84·ON90/90 |
| 원 cohort14 | fresh4 contexts 모두14/14; 원 helper가 진단 ON 강제 |
| 실제 native 포화 | oldB42/42·SHADOW42/42·ACTIVE44/44 |

R3의 경로 변경은 R2 lower-bound 검사를 먼저 수행한 뒤 **C=0, full parent, 양쪽 크기≤16**인 경우에만 기존 exact forbidden-edge 검사를 사용하는 것이다. C>0의 R2 residual/S certificate 결과는 신규 시험에서 그대로 보존했다. partial parent, 17개 이상, 참 동률, 신뢰도 라벨만 있는 경우, epoch·차원 불일치는 보수적인 HOLD를 유지한다. δNIS1, 기존 winner, native Hungarian, 센서/RF·필터·물리 계수를 바꾸지 않았다.

- ACTIVE: `a1e09f0ba815a84152b140ffeafcf139b0cbbf82911713d6c5802ed797fb0561`
- SHADOW: `1faf9ec597c051fb672201db37c1e19f44344313ccb26e677154354e31dc6c5f`
- module: `1abcb0863af7908931aa8a3f7c28cda37c10077f086eb903f387cefa7f1f86d7`

실제 HTML의 packed main을 원 packer로 읽어 mode와 module occurrence1을 확인했다. 이 lane의 증거는 `evidence/RUNTIME_PRODUCT_RECEIPT.json`이다. pack 역변환·보호 scope는 별도 build 증거이며 이 native receipt에서 실행하지 않은 작업으로 표시하지 않았다.

## 보존한 실패와 수정 전 시도

원 B47의 `bounded.connectedThirteenByThirteenHeld`는 원래 전체 component>12 HOLD와 의도한 bounded/certified 정책이 달라 FAIL이다. 원 R2의 `negative.noCertifiedCDoesNotInvokeResidualEvenWithClearGlobalWinner`는 C=0/full13을 R3가 exact로 판정하므로 FAIL이다. 원 시험은 수정하지 않았고 기대값 갱신이나 허용 오차 변경도 하지 않았다. 새로운28시험은 이 정책 변화와 원 native minimum을 별도로 검증한다.

처음의 general≤16 routing은 C>0인 R2 결과를 훼손했다. 당시 source `c17cb6e7…6e7ed`와 원 R2 strict7/15 결과를 `evidence/attempts/general-route/`에 남겼다. 그 rejected 설계의 PASS 자료를 최종 제품 검증으로 사용하지 않는다.

또한 recursive header spread가 알 수 없는 getter를 읽는 결함을 발견했다. 이전 source `e43b58df…c91a71`에서는 canary getter1회와 예외를 재현했고, 최종 explicit4-field whitelist에서는 getter0회·예외0·선택13을 확인했다. 이전 raw/source와 최종 재검증은 `evidence/attempts/unknown-header-spread/` 및 `evidence/header-getter-final.json`에 있다. 이것은 가상 getter의 입력 경계시험이다. 실제 producer에 truth 필드가 있었다고 주장하지 않는다.

## SHADOW와 실제 native 통합

SHADOW는 ACTIVE 정책을 적용하지 않으므로 새 ACTIVE 기대4건의 raw19/23 FAIL4를 유지했다. 원 B와의 별도 통제는 fixture별 filter/P·physical·private/global RNG 및 마지막 상태가 모두 정확히 같았다. native 원본 helper·assertion·초기 입력·허용 오차를 바꾸지 않았다. 제안 로그는 own/NPC covariance 양성에서 해제를 제안하지만 실제 SHADOW 상태에는 반영되지 않는다.

ACTIVE에서는 새 native23/23과 metadata18/18을 통과했다. 여기에는 실제 native AIR4, surface position2, CARTESIAN3 innovation S와 logdet 일치, 현재 epoch만 인증, 지연 offboard 무효, receiver 원점/속도 보존, 가짜 surface elevation 제외, finite Doppler가 있는3D callback의2D 인증 금지, 진단 OFF/ON·query 순수성이 포함된다. covariance 양성 fixture는 실제419012 전투 재현이라고 부르지 않는다.

원 native23그룹·cohort를 최종 제품에서 fresh8 contexts로 모두 다시 실행했다. 전체 `nativeResult`(schema/header/A 진단 포함)와 fixture별 full private-state hash는 oldB 및 R2 대비 delta0이었다. post-world state, 함수복원, ENV status, query 순수성과 진단 OFF/ON 통제도 통과했다. cohort의 진단은 원 helper 내부에서 ON으로 강제하므로 OFF 검증으로 세지 않는다.

실제 포화 fixture는 익명 receiver 측정과 명시된 owned prior를 사용하여 기존 caller→실제 NIS→실제 solver→native filter update를 실행한다. RF echo 발생이나 자연 전투 증거는 아니다. clear13/16에서 ACTIVE 선택13/16·각 파일 correction1회·birth0, oldB/SHADOW는 원 HOLD를 소비했다. 같은 위치 equal13에서는 세 제품 모두 HOLD13·correction0·birth0·age0.5·full private-state 동일을 유지했다. 다른 private owner와 canonical store도 변하지 않았다.

## 모든 raw·진단 차이

전체 artifact가 byte동일하다고 표시하지 않는다. 원 native8 contexts의 outer 진단은 R2 대비 delta0이지만 oldB 대비3/23/2347개 leaf 차이가 있다. 이전 단계에서 상속된 초기 header와 진단 내용을 포함하며, 모두 전수 diff로 보존했다.

포화 자료의 R2 대비 차이는 equal13 exact 분기 진단이다. SHADOW nativeResult5개·ACTIVE10개, outer trace 각5개 leaf가 다르다. `LARGE_COMPONENT_UNCERTIFIED_HOLD`가 `NEAR_EQUAL_MATCHING_HOLD`로 바뀌고, 기존0값 네 진단 필드(`lowerBoundCertifiedCount`, `exactResidualCertifiedCount`, `residualComponentsSolved`, `residualRefinementRejected`)가 exact-path 기록에 없다. filter/private-state hash 차이는0이다. 달라진 필드를 삭제하거나 동일하다고 간주하지 않았고 자동 승인도 하지 않았다. 전체 diff는 `evidence/native-diagnostic-deltas/`에 있다.

## 시간과 범위

SHADOW native3페이지47.20s, ACTIVE native3페이지47.48s, 원 native/cohort8 contexts134.89s, 실제 포화3 contexts45.84s였다. 이 수치는 검증 wall time이며 성능 벤치마크가 아니다.

원 R1/R2 자연 교전 결과와 실패는 그대로 남아 있다. R3 자연 교전·넓은 회귀는 다른 lane의 별도 증거와 검토 대상이다. captured logger에서 pairs 배열이 없는 항목을 empty graph 또는 PASS로 세지 않는다. 이 lane은 자연 RF·센서 전체 경로·전투 승인 또는 기대값 갱신을 하지 않았다.

집계는 `NATIVE_SUMMARY.json`, 권위 raw는 각 `evidence/native-shadow`, `native-active`, `original-native-full`, `native-saturation`의 SUMMARY/PROVENANCE와 raw-before-aux다. 최종 제품/source 해시는 실행 뒤에도 일치했다. 브라우저/controller를 닫고 공유 lease를 반환한 뒤 추가 브라우저를 실행하지 않았다.
