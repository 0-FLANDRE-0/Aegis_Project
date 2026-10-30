# CLEAN_A 검증 보고서

**유효구간 120/120 확정. 전체 회귀 합격은 보류: 도메인 417/420, CG 실제 자원 퇴행 3건 유지.**

게임 비행·센서·교전 코드는 변경하지 않았다. DDG의 검증된 (a) 기준값 3건만 선택적으로 갱신했다. 결과를 맞추는 계수 조정·검사 완화·실패 제외는 없다. 원본 브랜치/main 병합 및 tag/release 생성 없음.

기준 `env-d-remeasure-a@837539645b663e8653caa7aac037e6857efe5a2d`. 입력 SHA-256 `b846bd92a01f405fda82bafa08a5758925106d9827615d9dd06553134648c8db`. 출력 `Aegis_SIM_v48_WIP_CLEAN_A.html`, 20,450,832 bytes, SHA-256 `ceffbda64f3ffbefce4330b825e36408ea42bcc86abeddc27182843bd0b8ea45`. 모든 값은 게임 SIM_TUNED 모델 산출값이며 실물과 비교하지 않는다.

## 1. 도메인 회귀 6건

| 함정 / 검사 | KAPPA | DZT | HANDOFF | ARH | NEAR_VERTICAL | 최신 | 분류 / 조치 |
|---|---|---|---|---|---|---|---|
| DDG / samePhysicalState | PASS | PASS | FAIL | FAIL | FAIL | FAIL | a / BASELINE_UPDATE |
| DDG / raidInventoryDeltaBounded | PASS | PASS | FAIL | FAIL | FAIL | FAIL | a / BASELINE_UPDATE |
| DDG / sameExistingObserverState | PASS | PASS | FAIL | FAIL | FAIL | FAIL | a / BASELINE_UPDATE |
| CG / samePhysicalState | PASS | PASS | FAIL | FAIL | FAIL | FAIL | b / PRESERVE_FAILURE_NO_COEFFICIENT_CHANGE |
| CG / raidInventoryDeltaBounded | PASS | PASS | FAIL | FAIL | FAIL | FAIL | b / PRESERVE_FAILURE_NO_COEFFICIENT_CHANGE |
| CG / sameExistingObserverState | PASS | PASS | FAIL | FAIL | FAIL | FAIL | b / PRESERVE_FAILURE_NO_COEFFICIENT_CHANGE |

6건 모두 처음 실패한 빌드는 LAUNCH_HANDOFF_A다. DZT→HANDOFF에서 변경된 기존 함수는 `updateMissileBodyB3` 하나이고, 새 보조 함수는 `samLaunchHandoffGateA`다. HANDOFF의 해당 함수만 DZT로 되돌린 **진단 전용 대조군**은 6건 모두 통과했다. 대조군의 복원은 제품에 적용하지 않았다. 자세·속도·3D 경로 정렬 기반 발사 제어권 인계 시점이 바뀌어 궤적, 추적기 관측, 재교전 스케줄과 재고가 달라진 인과관계를 확인했다.

32초 원래 fixture 비교를 보존하고 같은 원래 8발 Kh-32/AUTO 조건을 180초까지 연장했다. 팀·기동 유틸리티는 원래대로 OFF, 아군함은 없다. 고유 native 추가 스폰을 끄지 않았다. 총 55개 ASM 중 원래 8발만 모두 종료됐고 추가 47발은 아직 비행 중이다. 따라서 종료 시각/사유는 **32초 원래 검수 종료 및 180초 고정 진단 지평**이며, 전 세계 적 미사일 전멸·전투 종료를 의미하지 않는다. 원래 8발과 추가 47발의 개별 결과는 `RAID_OUTCOMES.csv`에 전부 수록했다.

| 함정 | 빌드 | SAM 발사 | native SAM KILL | 자함 HP | VLS 잔여 셀 | CIWS 잔탄 | 침수 m³ | 생존 |
|---|---|---|---|---|---|---|---|---|
| DDG | KAPPA | 23 | 0 | 17.048516 | 80 | 1379 / 11 | 0.942713 | 생존 |
| DDG | DZT | 23 | 0 | 100.000000 | 80 | 1388 / 11 | 0.000000 | 생존 |
| DDG | HANDOFF | 21 | 3 | 100.000000 | 81 | 1550 / 11 | 0.000000 | 생존 |
| DDG | LATEST | 21 | 3 | 100.000000 | 81 | 1550 / 11 | 0.000000 | 생존 |
| CG | KAPPA | 21 | 2 | 100.000000 | 104 | 1550 / 1550 | 0.000000 | 생존 |
| CG | DZT | 21 | 2 | 100.000000 | 104 | 1550 / 1550 | 0.000000 | 생존 |
| CG | HANDOFF | 22 | 2 | 100.000000 | 103 | 1550 / 1474 | 0.000000 | 생존 |
| CG | LATEST | 22 | 2 | 100.000000 | 103 | 1550 / 1489 | 0.000000 | 생존 |

DDG는 KAPPA와 DZT 모두 대비 SAM 발사 23→21, SAM KILL 0→3, HP/침수/모듈 손상/생존/탄약이 나빠지지 않았다. 원래 8발 결과도 사후 관측에서 개선됐다. (a)로 분류한 3건만 exact-state 새 값으로 갱신했다. `approved-raid-baselines.json`에 예전/새 물리·관측 상태와 재고, 양쪽 해시 및 갱신 사유를 보존하고, 검증된 게임 코어 해시에서만 사용할 수 있게 했다. 일반 회귀 실행의 기본 동작은 그대로다. 32초 VLS 비교는 DDG 91→90이며, 이 조기 한 시점의 소모 차이를 180초 결과로 검토한 것이다.

CG는 SAM 발사 21→22, VLS 잔여 104→103, 20mm 탄약 최신 61발 추가 소모, SAM KILL 2→2, HP100/침수0/생존 유지다. 이 경우 (a)로 처리하지 않았다. 같은 비행 함수 복원 대조군이 원래 상태로 돌아오므로 최초 원인은 인계 수정으로 특정되지만, 검증된 인계를 되돌리거나 발사 정책을 바꾸지 않고 고칠 수 있는 단일 최소 결함은 확정하지 못했다. CG 3건은 실제 자원 퇴행 (b)으로 남기며 기준값을 갱신하지 않는다. 이전 보고서의 “기존 실패” 표기를 바로잡는다. HANDOFF 시점에는 CIWS 추가 76발, 최신은 추가 61발이다.

대조 계측은 고유 fixed tick 뒤 읽기만 수행했다. 독립 비계측 원래 fixture 대비 32초의 state/dynamics/RNG/observer/offboard 40개 일치 검사를 통과했다. 모듈 손상은 모든 키 합집합으로 비교했다. native `NORMAL_HIT`은 대상 자체의 종료 원인 라벨이며 자함 명중 수와 동의어로 해석하지 않는다. 원래 표적별 내역은 다음과 같다.

| 함정 | 원래 표적 | KAPPA | DZT | HANDOFF | 최신 |
|---|---|---|---|---|---|
| DDG | 1 | NORMAL_HIT | NORMAL_HIT | INTERCEPT_KILL | INTERCEPT_KILL |
| DDG | 2 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| DDG | 3 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| DDG | 4 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| DDG | 5 | NORMAL_HIT | NORMAL_HIT | INTERCEPT_KILL | INTERCEPT_KILL |
| DDG | 6 | NORMAL_HIT | GUIDANCE_CONTROL_LOSS_MISS | INTERCEPT_KILL | INTERCEPT_KILL |
| DDG | 7 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| DDG | 8 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 1 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 2 | INTERCEPT_KILL | INTERCEPT_KILL | INTERCEPT_KILL | INTERCEPT_KILL |
| CG | 3 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 4 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 5 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 6 | INTERCEPT_KILL | INTERCEPT_KILL | INTERCEPT_KILL | INTERCEPT_KILL |
| CG | 7 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |
| CG | 8 | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT | NORMAL_HIT |

## 2. HANDOFF 신규 실패 3발 재확인

| 원래 조건 | KAPPA | HANDOFF | 최신 | 회복 단계 |
|---|---|---|---|---|
| SM6_240KM_AIR_TERMINATION_OFF | 성공 / CPA 10.334287m | 실패 / CPA 51.308397m | 성공 / CPA 1.349768m | ARH |
| SM6_240KM_AIR_TERMINATION_ON | 성공 / CPA 10.334287m | 실패 / CPA 51.308397m | 성공 / CPA 1.349768m | ARH |
| SM6_0P1KM_20KM_STATIONARY_ASM_SEED1 | 성공 / CPA 36.352123m | 실패 / CPA 227.985890m | 성공 / CPA 9.949687m | NEAR_VERTICAL |

240km 2발: 원래 normal.json 인덱스 152/153, SM-6, 고도5km, 접근250m/s, seed12001, 종료기 OFF/ON. 두 발 모두 HANDOFF에서 native 기폭 뒤 AIR miss였고 최신에서는 native AIR 명중이다. ARH_MEASUREMENT_FIX_A부터 회복했다.

극단 고각 1발: 수평0.1km / 고도20km / 정지 Kh-35U / `(rngSeed,navigationSeed)=(1831565813,2047861954)`. HANDOFF/ARH에서 TRACKED_DIVERGENCE, NEAR_VERTICAL부터 native KILL이다. 원래 AIR 시험과 ASM 피해 판정 경로를 섞지 않았다. 별도 신관·유도·종료기 조정은 없다. 세 발 전체 중간 단계 및 기폭 miss/시간은 `PART2_SHOTS.csv`, 원시 궤적은 `results/part2-*.json.gz`에 있다.

## 3. 게임 코드 변경 여부

변경 없음. 압축 실행 main의 ENV_D 진단 데이터/accessor 블록 외에는 byte 동일하고, 외부 HTML shell과 자산0–12도 동일하다. 새 함수/물리 계수/발사 정책을 적용하지 않았다. 수정한 별도 파일은 선택적 DDG 회귀 기준값 적용 도구와 CLEAN_A 측정·보고 도구다.

내장 표는 `AEGIS_ENVELOPE_TABLE_D_2`, prior 각 행은 `previous`에 그대로 보존. frozen 진단 엔진과 실제 새 HTML에서 추출한 **283개 native 함수 해시 및 native 엔진 전체 bytes 일치**. `status().match=true`, `effectiveIntervalsComplete=true`, `pendingEffectiveCells=0`, `additionalMeasurementsRequired=false`를 DDG/CG에서 확인했다. 지도·발사 판정 연결은 없다.

## 4. 유효 요격 구간

각 칸 표기: **바깥 / 최소~최대 유효 km**. 운동은 정지 / 접근250 / 접근680 / 이탈250 / 횡단250m/s. 최소는 1~30km 정수 지점 최초 3/5 KILL 또는 STRUCT_FAIL, 그 다음은 최소보다 엄격히 큰 5의 배수부터 연속 5km 간격이다. 최소가 정확히 5의 배수일 때 그 점을 중복 검사하지 않는다.

추가 사격은 총 1,230발: 앞선 최소거리 탐색 1,040발 + 이번 승인된 부족 grid 190발이다. 기존 같은 빌드·조건·5개 시드 사격은 논리 SHA-256을 확인해 재사용했다. 사용자가 “ㅇㅇ 추가 시험 해봐.”로 ESSM 5칸의 후속 grid 시험을 승인해 실행했다. 기존 최소거리 사격 전부와 완료된 다른 115칸은 그대로 보존했다.

### SM2

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 203 / 2~195 | 320 / 4~300 | 500 / 1~1 | 31 / 1~30 | 89 / 2~85 |
| 1000 | 212 / 1~210 | 329 / 2~325 | 500 / 3~500 | 33 / 1~30 | 102 / 1~100 |
| 5000 | 228 / 1~225 | 342 / 1~340 | 500 / 1~1 | 46 / 1~45 | 172 / 1~170 |
| 10000 | 249 / 1~245 | 365 / 1~355 | 500 / 1~500 | 63 / 1~60 | 202 / 1~200 |
| 15000 | 265 / 1~260 | 377 / 1~370 | 500 / 1~500 | 153 / 1~90 | 223 / 1~220 |
| 20000 | 265 / 1~260 | 365 / 1~355 | 500 / 1~500 | 163 / 1~160 | 233 / 1~225 |

### SM2ER

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 257 / 3~245 | 384 / 1~360 | 500 / 1~1 | 42 / 1~35 | 75 / 2~75 |
| 1000 | 274 / 1~270 | 403 / 2~400 | 500 / 1~500 | 45 / 1~35 | 81 / 2~80 |
| 5000 | 299 / 1~295 | 427 / 1~425 | 500 / 1~1 | 55 / 1~55 | 242 / 1~240 |
| 10000 | 334 / 1~330 | 469 / 1~460 | 500 / 1~5 | 65 / 1~65 | 284 / 1~280 |
| 15000 | 369 / 1~365 | 500 / 1~500 | 500 / 1~5 | 233 / 1~105 | 320 / 1~315 |
| 20000 | 392 / 1~385 | 500 / 1~500 | 500 / 1~500 | 258 / 1~255 | 351 / 1~335 |

### SM6

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 265 / 3~265 | 384 / 1~380 | 500 / 1~1 | 38 / 1~35 | 79 / 2~75 |
| 1000 | 297 / 1~295 | 431 / 2~430 | 500 / 1~500 | 45 / 1~45 | 85 / 2~80 |
| 5000 | 325 / 1~325 | 461 / 1~460 | 500 / 1~1 | 57 / 1~55 | 268 / 1~265 |
| 10000 | 365 / 1~365 | 500 / 1~500 | 500 / 1~5 | 69 / 1~65 | 313 / 1~310 |
| 15000 | 410 / 1~405 | 500 / 1~500 | 500 / 1~5 | 262 / 1~110 | 356 / 1~355 |
| 20000 | 443 / 1~435 | 500 / 1~500 | 500 / 1~500 | 293 / 1~285 | 397 / 1~395 |

### ESSM

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 53 / 1~25 | 99 / 1~30 | 179 / 1~30 | 11 / 1~10 | 17 / 1~15 |
| 1000 | 49 / 1~25 | 99 / 2~95 | 179 / 4~175 | 12 / 1~10 | 18 / 1~15 |
| 5000 | 30 / 1~30 | 62 / 1~60 | 116 / 7~115 | 13 / 1~10 | 20 / 1~20 |
| 10000 | 28 / 2~25 | 41 / 1~1 | 66 / 14~65 | 15 / 1~15 | 22 / 1~20 |
| 15000 | 29 / 2~25 | 40 / 1~1 | 63 / 19~60 | 15 / 1~15 | 23 / 1~20 |
| 20000 | 27 / 2~25 | 37 / 10~35 | 55 / 24~50 | 15 / 1~15 | 22 / 2~20 |

### 이전 0km 13칸

| 기종 | 고도 m | 운동 | 새 최소 km | 새 최대 km | 끊김/대기 지점 km |
|---|---|---|---|---|---|
| SM2 | 30 | INBOUND_680 | 1 | 1 | 5 |
| SM2 | 5000 | INBOUND_680 | 1 | 1 | 5 |
| SM2ER | 30 | INBOUND_680 | 1 | 1 | 5 |
| SM2ER | 5000 | INBOUND_680 | 1 | 1 | 5 |
| SM6 | 30 | INBOUND_680 | 1 | 1 | 5 |
| SM6 | 5000 | INBOUND_680 | 1 | 1 | 5 |
| ESSM | 5000 | INBOUND_680 | 7 | 115 | 120 |
| ESSM | 10000 | INBOUND_250 | 1 | 1 | 5 |
| ESSM | 10000 | INBOUND_680 | 14 | 65 | 70 |
| ESSM | 15000 | INBOUND_250 | 1 | 1 | 5 |
| ESSM | 15000 | INBOUND_680 | 19 | 60 | 65 |
| ESSM | 20000 | INBOUND_250 | 10 | 35 | 40 |
| ESSM | 20000 | INBOUND_680 | 24 | 50 | 55 |

13칸을 전부 “5km보다 먼 최소 사거리 문제”로 해석할 수 없다. 8칸은 1km에서 3/5 이상이지만 5km에서 실패한다. 지정한 첫 구간 정의로는 **1~1km**다. 15km 이후의 다른 성공 구간을 임의로 골라 최대 유효거리를 늘리지 않았다. 이 결과는 거리별 성공이 단조가 아니라는 게임 모델의 관측이며, 사용자 판단 없이 정의/임계값을 바꾸지 않았다.

### 이번에 확정한 ESSM 5칸

| 고도 m | 운동 | 유효 구간 km | 새 시험 지점 / 발수 | 최초 실패 km / 격추 수 |
|---|---|---|---|---|
| 5000 | INBOUND_680 | 7~115 | 17 / 85 | 120 / 0/5 |
| 10000 | INBOUND_680 | 14~65 | 7 / 35 | 70 / 0/5 |
| 15000 | INBOUND_680 | 19~60 | 7 / 35 | 65 / 0/5 |
| 20000 | INBOUND_250 | 10~35 | 3 / 15 | 40 / 0/5 |
| 20000 | INBOUND_680 | 24~50 | 4 / 20 | 55 / 2/5 |

미측정 38점×5발=190발을 추가했다. 새 지점은 모두 5/5 KILL(190/190)이었고, 이후 첫 실패는 기존 사격 결과에서 확인했다. 첫 실패 뒤 새 사격은 하지 않았다. `evidence/grid-followup.json`에 승인 범위, 기존 사격 해시 보존, 5칸 외 변경 없음, 끊김점 5발 내역을 기록했다. `GRID_FOLLOWUP_SHOTS.csv`에 새 190발의 시드·결과·최근접 거리·기폭 miss·요격 위치를 정리했다.

전체 120칸의 요격 지점 평균/최소/최대, 5발 내역, 끊김점, 이전값은 `EFFECTIVE_INTERVALS.csv` 및 `ENVELOPE_TABLE_D.json`에 있다. 최소·최대 값 미측정 칸은 0개다. 500km 상한까지 통과한 칸은 끊김점이 없으며 이를 실패 누락으로 세지 않았다. C4는 완료·통과다.

## 5. 검수 C1–C4와 실행 시간

| 검수 | 결과 | 수치 / 제한 |
|---|---|---|
| C1 | 미통과 | 417/420; 원래 기준 414/420. DDG (a) 3개 exact 기준만 갱신, CG (b) 3개 유지 |
| C2 | PASS (코드 동등성으로 기존 비행 결과 유지) | UI88 새 실행, 기존 종료기300·공통180·자연RF28·WebGL8 결과 재사용; 신규 실패0 |
| C3 | PASS (새 실행) | 무표적/전투 각각120초 truth 해시 동일, 게임 코어 byte 동일 |
| C4 | PASS | 120개 전체 구간 확정 / 0개 미측정; 이전0km 13개 최소·최대 모두 기록 |

| 시험 | 최신 성공 | CLEAN 성공 | 완전 반환값 차이 | 실행 초 (최신 / CLEAN) |
|---|---|---|---|---|
| release | 222/300 | 222/300 | 0 | 461.07 / 576.38 |
| common | 170/180 | 170/180 | 0 | 156.04 / 152.05 |
| natural | 24/28 | 24/28 | 0 | 28.96 / 29.37 |

실제 WebGL8발은 양쪽 모두 원래29/29 검사를 통과하고 발사/관측 샘플/최종 물리 반환값이 모두 동일하다. 기존 MR/ER 명중4발 유지, SM-6/ESSM 기존 비명중4발도 그대로다. “8발 검증”을 “8발 명중”으로 세지 않았다. 종료기300은240normal+36dual+12fault+8battery+4정식VLS이고 중복 합산하지 않았다. 자연RF28은 별도 제어된 ASM 경로다.

이 비행 회귀는 이번 190발에 중복 합산하지 않는다. 기존 회귀를 실행한 HTML SHA는 `e58924e83c90acd4473a8003e64d80b1771ea28ff39cf2be91f1873738212084`이며 새 산출물 SHA와 다르다. `evidence/regression-carryforward.json`으로 ENV_D 진단 표/accessor 블록 외 게임 실행 코드와 전체 UI/자산 bytes 동일함을 증명했다. 도메인/300/180/28/8 비행은 재실행하지 않고 그 결과를 보존했다. 이번에는 190발, 283개 함수 비교, UI88, DDG/CG 표 상태·API 독립성, 120초 무표적·전투를 새로 실행했다.

| 상태 | 양쪽 동일 SHA-256 |
|---|---|
| 무표적120초 | fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc |
| 전투120초 | b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1 |

전투 hash 시나리오(SM-6 100km/5km/접근250m/s/seed12002)의 기존 비명중/POST_CROSS 종료도 양쪽 그대로다. 이를 회복 명중으로 올려 세지 않는다.

최소거리 1,040발 벽시계 63.67초, 이번 후속 grid 190발 18.77초(각2 workers). 역사 raid 7개 변형, 장기 raid 8쌍, part2 18발, 전체 도메인 15 suites의 앞선 증거는 보존했다. 각 작업 실제 소요는 원시 결과의 `elapsedS`에 있다. 동시 실행 시간이 겹치므로 이를 직렬 총시간/실기 FPS로 해석하지 않는다.

### 재현

```sh
export NODE_PATH=/workspace/aegis-performance-f/docs/performance/F/node_modules
node docs/cleanup/A/intervals.cjs --allow-missing-grid
python docs/cleanup/A/verify_grid_followup.py
python docs/cleanup/A/build.py
node docs/cleanup/A/verify_native.cjs
python docs/cleanup/A/verify_regression_carryforward.py
python docs/cleanup/A/verify_delivery.py
python docs/cleanup/A/report.py
```

브라우저 도구는 Chromium/Playwright 및 기존 저장소 테스트 의존성을 사용한다. 최소거리 cache는 기존 D2 engine/functions/seed와 동일한 것만 재사용한다. 추가 grid는 명시적 scope 승인 파일 없이는 실행할 수 없다. 상세 원시 증거와 스크립트는 REPORT ZIP에 포함한다.
