# AIR_ORIGIN_A — 자체 AIR receiver 원점 계약 복구

상태: 구현·쌍대 회귀 완료, PR 검토 대상. **기대값 갱신 0 / main 병합 0 / GUN_B2 Phase 1 미착수**.

**전체 기존 단언 통과는 아니다. 도메인 416/420: DDG/CG 습격의 물리·관측 exact 비교 4건 불일치, 전투 world120 고정 hash 불일치를 그대로 남긴다.** 무잡음 원점 계약은 통과했고 자연 발사 8발의 성공→실패는 0건이다. 불일치 사유 확인과 기대값 승인은 구별한다.

## 변경과 보존

기준 main `9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c`, 원본 HTML `c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc`. 새 HTML SHA-256 `4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb`. 변경은 다음 세 함수뿐이며, 메타데이터 추가를 역변환하면 기존 main JS 전체와 byte 동일하다.

| 함수 | 변경 |
|---|---|
| `shipboardRadarEchoFieldWip13B13` | 이미 RF 거리·고각·Doppler 계산에 사용한 정규화 receiver 높이/수직 속도를 에코에 보존. 기존 X/Y/수평 속도와 합쳐 6개 값. |
| `shipboardRadarEchoToAirPlotWip13B13` | 에코의 6개 sensor 필드를 값 그대로 AIR plot에 복사. |
| `spq9bAnonymousPlotContractV34` | 6개 sensor 필드를 기존 화이트리스트에서 보존. 표적 id/truth 필드 허용 없음. |

계약: `sensorXWorld`, `sensorYWorld`는 world 단위, `sensorZM`는 m, `sensorVxMps/sensorVyMps/sensorVzMps`는 m/s다. NPC AIR 어댑터와 같은 키·단위를 사용한다. EKF에서 현재 함 위치를 다시 읽어 보정하는 대신 **측정 당시 RF에 사용한 값**을 전달한다. 고정 오프셋·표적 truth 보정은 없다.

RF Pd·잡음·RCS·빔 모델/계수, RF 난수 호출, KF 예측/갱신/연관 수식과 이득 계산식·튜닝값, 음수 고도 clamp, SM/ESSM/SM-6/CIWS/EW/H3 구현 및 ENVELOPE_TABLE_D는 바꾸지 않았다. 보호 비행 함수 281개도 byte 동일하다. 관측이 달라진 뒤 기존 스케줄러·교전 분기·난수 소비가 달라질 수 있으므로 실제 전투 결과까지 byte 동일하다고 주장하지 않는다.

CG-52의 비-B형 SPQ-9은 기존대로 수상 채널만 지원하며 AIR 모드를 새로 추가하지 않았다. CG의 SPY AIR와 DDG의 SPY/SPQ AIR를 검증했다. legacy SPY 전자적 false plot은 기존 함 중심/OWN_ALT_M에서 합성되고 기존 EKF fallback과 일치하므로 생성 규칙을 그대로 유지했다. NPC·offboard 어댑터와 저장 스키마도 그대로다.

[전체 소스 diff](AIR_ORIGIN_A.diff), [정적 검증](evidence/static.json).

## 원점 계약 검증

| 검사 | 결과 |
|---|---|
| 무잡음 SPY 왕복 | DDG/CG ×4면 ×0/90° =16조건 통과 |
| DDG SPQ AIR 화이트리스트/왕복 | 추가 8조건 통과 |
| receiver 보존 | RF가 실제 사용한 6개 값과 plot 값 일치 |
| EKF | 측정 잔차 및 무잡음 갱신 위치·속도 상태벡터 변화 <1e−8 |
| 기존 결함 대조군 | main에서 원점 누락에 따른 잔차 재현 |
| 음수 clamp | private KF 높이 −4m → 기존 legacy 0m 처리 유지 |
| 실제 자연 측정 경로 | SPY 83 / SPQ AIR 12회 EKF 입력에서 실제 receiver 메타데이터 일치; main도 같은 입력 회수. 표적 트랙 삽입 0 |
| 난수/틱 | private 왕복 검사에서 전역 RNG/틱 변화 0 |

무잡음 검사에만 private reflector와 zero-noise RNG 공급자를 사용하고 finally에서 복원했다. 제품 계수는 수정하지 않았으며 자연 관측 회귀에는 이 공급자를 사용하지 않았다. 실제 receiver 경로 검사는 다른 레이더 업데이트만 진단 페이지에서 격리하고, 남은 레이더의 RF Pd/잡음과 전체 fixed tick을 그대로 실행했다.

## 회귀 결과

모든 회귀는 main과 후보를 새로 실행했다. 도메인은 기존 14개 suite 378검사 + main 기준 동일 시드 쌍대 42검사다. 과거 승인 reference JSON, 허용 오차, 검사 조건은 갱신하지 않았다. 기존 retired UI 명령 어댑터, AutoAA OFF 설정, 기존 H3→H4 fixture 해석만 양쪽에 동일하게 적용했다.

| 도메인 suite | main | AIR_ORIGIN_A |
|---|---:|---:|
| aps153 | 20/20 | 20/20 |
| emcon-native | 27/27 | 27/27 |
| emcon-ui | 14/14 | 14/14 |
| harpoon-clock | 24/24 | 24/24 |
| harpoon-f1 | 46/46 | 46/46 |
| helicopter-flight | 85/85 | 85/85 |
| isar-classes | 8/8 | 8/8 |
| isar-clock | 12/12 | 12/12 |
| isar-native | 36/36 | 36/36 |
| isar-ui | 38/38 | 38/38 |
| sov-casualty | 13/13 | 13/13 |
| sov-deployment | 15/15 | 15/15 |
| sov-native | 30/30 | 30/30 |
| sov-visual | 10/10 | 10/10 |
| paired42 | 42/42 | 38/42 |
| 합계 | 420/420 | 416/420 |

### 자연 탐지 → LOCK → 정식 VLS → 실제 WebGL 8발

자연 탐지·정식 발사·종료기 ON/OFF·WebGL 검사 자체는 양쪽 29/29다. 8발 모두 명중했다는 뜻은 아니다. main의 기존 명중 4발/실패 4발 구성을 그대로 공개한다.

| 무장 | 종료기 | main 표적 생존 / 종료 사유 / 비행 s | 후보 표적 생존 / 종료 사유 / 비행 s | 종료 위치 차이 m |
|---|---|---|---|---:|
| SM2 | OFF | False / PROX_DETONATION_AIRCRAFT / 25.483 | False / PROX_DETONATION_AIRCRAFT / 25.483 | 7.078146 |
| SM2 | ON | False / PROX_DETONATION_AIRCRAFT / 25.483 | False / PROX_DETONATION_AIRCRAFT / 25.483 | 7.078146 |
| SM2ER | OFF | False / PROX_DETONATION_AIRCRAFT / 20.900 | False / PROX_DETONATION_AIRCRAFT / 20.900 | 1.231576 |
| SM2ER | ON | False / PROX_DETONATION_AIRCRAFT / 20.900 | False / PROX_DETONATION_AIRCRAFT / 20.900 | 1.231576 |
| SM6 | OFF | True / LOW_SPEED / 79.433 | True / LOW_SPEED / 79.150 | 89.161572 |
| SM6 | ON | True / TERMINAL_MISS_POST_CROSS / 40.333 | True / TERMINAL_MISS_POST_CROSS / 40.050 | 306.463309 |
| ESSM | OFF | True / LOW_SPEED / 27.100 | True / LOW_SPEED / 59.900 | 7271.250555 |
| ESSM | ON | True / LOW_SPEED / 27.100 | True / TERMINAL_MISS_POST_CROSS / 34.250 | 2564.586991 |

성공→실패 0건, 실패→성공 0건. 원래 8발의 전체 샘플·발사 관문·센서 출처·WebGL 캡처는 `evidence/regression/각태그/webgl8/`에 보존했다.

추가 시커 RF 28조건의 결과 차이는 0건이다. **이 28조건은 함 사통 트랙을 이상적으로 공급하는 기존 시커 회귀**이며 자체 레이더 자연 탐지로 표기하지 않는다. 자체 레이더 자연 경로는 위 WebGL 8발, 실제 receiver 경로, CIWS 및 world120 전투에서 별도로 실행했다.

### CIWS / EW / H3

| 항목 | 함정 | main | 후보 |
|---|---|---|---|
| EW | DDG_119_LATE_FLIGHT_IIA | 47/47 | 47/47 |
| EW | CG_52_LATE_TICONDEROGA | 47/47 | 47/47 |
| H3 | DDG_119_LATE_FLIGHT_IIA | 97/97 | 97/97 |
| H3 | CG_52_LATE_TICONDEROGA | 98/98 | 98/98 |
| 자연 CIWS | DDG_119_LATE_FLIGHT_IIA | 탄 소모 105, HP 3.265264675423225, 실제 피격 1, 표적 생존 [False, False] | 탄 소모 105, HP 3.265264675423225, 실제 피격 1, 표적 생존 [False, False] |
| 자연 CIWS | CG_52_LATE_TICONDEROGA | 탄 소모 170, HP 70.60128799698977, 실제 피격 1, 표적 생존 [False, False] | 탄 소모 170, HP 70.60128799698977, 실제 피격 1, 표적 생존 [False, False] |

CIWS는 표적/트랙 강제 연결 없이 실제 ASM 두 기와 전체 fixed tick을 사용했다. SAM은 MANUAL, 5in 자동은 OFF, 아군·적 NPC 함정은 없는 상태다. 탄 소모는 RAM/20mm를 합친 재고 감소이며 마운트별 수치는 JSON에 별도로 있다. EW/H3는 기존 권한·업무 fixture다. 사후 물리 결과는 AFTER_ACTION_TRUTH 진단용이며 전술·AI에 다시 입력하지 않는다.

### world120

| 시나리오 | main hash | 후보 hash | 동일 | 변경 경로 수 |
|---|---|---|---|---:|
| idle | `fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc` | `fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc` | True | 0 |
| combat | `b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1` | `f546c836e56feac2e8823e2bfd9e27e32bf392d71c6aeeb36640f549e7fff078` | False | 8 |

기존 고정 hash 기대값을 그대로 검사하고 실패 여부도 원본 로그에 보존했다. 이미 반환된 truth snapshot을 수집해 필드별 차이를 기록했으며 hash가 달라졌다고 새 기대값으로 교체하지 않았다.

## 달라진 항목과 원인

| 분류 | 항목 | 원인 / 근거 |
|---|---|---|
| DOMAIN_CHECKS | paired42 | DDG/CG 각 samePhysicalState와 sameExistingObserverState, 총 4건 불일치. 관측 보정→기존 AUTO 발사 틱 변경→708kg 탄약 질량 제거 시점 변경→미세한 함체 자세 차이. HP·손상·최종 탄약·RNG·32초 시점 표적 결과 동일. 기대값 갱신 없음. 틱별 동등성 검증: cause-analysis.json. |
| NATURAL_WEBGL | SM2:False | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | SM2:True | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | SM2ER:False | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | SM2ER:True | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | SM6:False | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | SM6:True | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | ESSM:False | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| NATURAL_WEBGL | ESSM:True | receiver 보존으로 EKF 관측·발사 품질·유도 입력과 궤적이 변경됨. 원래 명중 4발은 계속 명중, 원래 실패 4발은 계속 실패. 비행·종료기 코드는 동일. 종료 위치·시점과 전체 변경 경로: natural-flight-comparison.json. |
| CIWS | DDG_119_LATE_FLIGHT_IIA | 자체 레이더 큐의 관측 고도·트랙 수/출처만 변화. CIWS 탄 소모·자함 HP·피격 수·표적별 최종 결과·RNG 동일. 로컬 RF·탄도·피해 코드 동일. |
| CIWS | CG_52_LATE_TICONDEROGA | 자체 레이더 큐의 관측 고도·트랙 수/출처만 변화. CIWS 탄 소모·자함 HP·피격 수·표적별 최종 결과·RNG 동일. 로컬 RF·탄도·피해 코드 동일. |
| WORLD120 | combat | 56틱 관측 차이→4032틱 SM-6 ACTIVE/IOG·시커 방사 시점 차이→4034틱 표적 위협 감지·회피 분기/RNG 소비 차이. 최종 항공기 운동 7필드+RNG만 변경, 자함 물리·재고·피해 동일. passive trace의 최종 hash는 원래 실행과 각각 정확히 일치. |

수치·발별 전후 값은 [summary.json](evidence/summary.json), [차이 CSV](evidence/differences.csv), [world 경로](evidence/world120-comparison.json), [EW/H3/CIWS 전후](evidence/combat-comparison.json)에 있다. 변화의 제품 원인은 receiver 계약 3곳으로 한정되며 별도 계수 조정은 없다. 자연 교전 성공→실패는 단순히 정상 변화로 승인하지 않고 검토 대상으로 남긴다.

### 4개 습격 불일치의 틱별 원인 확인

기존 8 Kh-32 fixture는 초기 테스트 트랙을 넣는 AUTO 쌍대 검사다. 자체 레이더 자연 탐지 검사로 세지 않는다. 원래와 동일한 32초 종료점에서 읽기 전용 로거를 추가 재실행했고, 원래 실행의 함 상태·동역학·RNG와 각각 일치했다. `mass.peek()`/`dynamics.snapshot()`만 읽으며 물리 계산에 값을 되먹이지 않는다.

| 함정 | 관측 첫 차이 | SAM 관측 배열 첫 차이 | 질량·자세 첫 차이 | SAM 감지 틱 main → 후보 |
|---|---:|---:|---:|---|
| DDG_119_LATE_FLIGHT_IIA | 3 | 720 | 721 | 1,528,576,624,672,720 → 1,528,576,624,672,744 |
| CG_52_LATE_TICONDEROGA | 3 | 528 | 529 | 1,540,588,636,684,732,780 → 1,528,576,624,672,720,768 |

위 틱은 SAM이 배열에서 처음 관측된 시점이다(첫 미사일 1틱 포함). DDG의 마지막 SAM은 720→744틱, CG의 두 번째 이후 SAM은 각각 12틱 앞당겨진다. 다음 틱 질량 ledger에는 SM-2 한 발 708kg 차이가 생긴다. 동일한 최종 탄약이어도 과도 질량·무게중심 이력이 달라져 작은 롤/트림/흘수 차이가 남는다.

| 함정 | 최종 heel rad main → 후보 | 최종 draft m main → 후보 | 32초 결과 |
|---|---|---|---|
| DDG_119_LATE_FLIGHT_IIA | 0.000560977382493036 → 0.000560956935203329 | -0.764707882992949 → -0.764707882573028 | HP 100·침수/손상·탄약·RNG 동일; 표적 8기 생존, 요격 0 |
| CG_52_LATE_TICONDEROGA | -0.00541628573375259 → -0.00541493810861205 | 0.42075741741356 → 0.420757422649339 | HP 100·침수/손상·탄약·RNG 동일; 표적 8기 생존, 요격 0 |

습격 종료까지의 전투 결과 동일을 주장하지 않는다. 이 fixture의 관측 종료점은 32초다. 관측 exact 비교 차이는 보정된 KF 고도·연관·재방문 스케줄/카운터이며 모든 경로를 `cause-analysis.json`에 보존했다. **기준값 승인은 하지 않았으며 4건은 실패 상태로 남긴다.**

### 전투 world120의 첫 차이 순서

| 시점 | main | 후보 | 의미 |
|---|---|---|---|
| 56틱 (0.933초) | 첫 관측 고도 4921.478738m | 4928.828791m | 실제 receiver 계약을 반영한 KF 관측 차이 |
| 900틱 (15초) | SM-6 정식 발사 | 같은 틱 발사 | 발사 시점과 초기 위치 동일 |
| 4032틱 (67.200초) | ACTIVE / active seeker=true | IOG / false | 기존 유도·시커 분기가 다른 관측 입력을 받음 |
| 4034틱 (67.233초) | 표적 threatened=true | false | 기존 `updateTarget()`의 active RF·빔·LOS 위협 판정 및 회피 난수 소비 분기 |

최종 차이는 표적 x/y/z/vx/vy/heading/speedMps 7개 필드와 전역 RNG뿐이다. 자함 물리·재고·피해는 같다. 전역 RNG 알고리즘이나 RF Pd/잡음을 바꾼 결과가 아니며, 이번 작업에서 분리 난수 등 다른 개선을 추가하지 않았다. 읽기 전용 로거 재실행의 최종 hash도 원래 main/후보 hash와 각각 정확히 같았다.

[틱별 분석 및 전체 변경 경로](evidence/cause-analysis.json), [습격 원시 틱 로그 gzip](evidence/causes-raid.json.gz), [world120 원시 틱 로그 gzip](evidence/causes-world.json.gz), [자연 발사 8발의 발사 품질·궤적·종료 상태 전체 차이](evidence/natural-flight-comparison.json). 사후 truth는 진단에만 사용하고 시뮬레이션에 입력하지 않는다.

## 산출물과 다음 단계

기존 회귀의 모든 단언 통과 여부: **False**. 원점 계약 검증 통과: **True**. 이 둘을 구별한다. 쌍대 회귀 38작업 총 경과 2301.7초이며 CPU headless/SwiftShader 환경의 진단 시간이다. 폰 FPS나 성능 향상 수치가 아니다.

추가 원인 재현은 습격 4실행+전투 world120 2실행이며 두 프로세스 누적 실행시간 204.2초다. 모든 passive 로거의 최종 상태 동등성을 확인했다. 무잡음/실제 receiver 검증 시간은 각각 원시 JSON에 별도 기록한다.

새 게임 HTML과 HTML ZIP, 보고서 ZIP을 따로 제공한다. ZIP은 GitHub에서 실제로 다시 내려받아 SHA-256/CRC와 내부 파일을 확인한다. 영수증은 자기 해시 순환을 피하려고 별도 후속 커밋에 둔다.

**여기서 PR을 열고 멈춘다. main 병합·release/tag 생성은 하지 않는다.** 병합 후 gun-b2에서 새 main을 통합하고 DDG/CG 표적 1기, 0°/90° 각각 15시드(총 60회)를 재진단한다. 그 결과를 바탕으로 Phase 1 착수 보고를 하며, 이번 작업에서 산포·신관·포인팅 창·파편은 구현하지 않았다.
