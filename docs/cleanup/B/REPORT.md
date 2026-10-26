# CLEAN_B — CG 기준 승인 및 유효 요격 구간 재정의

**도메인 420/420, UI88 및 검수 B1–B4 전체 PASS. 유효구간 120/120 확정, 값 변경 43칸.**

기준 `clean-a@60a83ccfbde89ec26d927b2993f0a4a9585c98af`, 입력 SHA `ceffbda64f3ffbefce4330b825e36408ea42bcc86abeddc27182843bd0b8ea45`. 산출물 `Aegis_SIM_v48_WIP_CLEAN_B.html` (22,000,252 bytes), SHA-256 `ab614891a44f05addc20aed8ac0822da1b997bc766478f2cc1ba3dc76d70fef8`. 별도 `clean-b` 브랜치. main/기준 브랜치 병합 및 release/tag 생성 없음. 게임용 SIM_TUNED 모델 산출값이며 실물 성능과 비교하지 않는다.

## 1. CG 회귀 3건 기준값 승인

사용자의 새 기준을 적용했다. 격추 수·표적별 최종 결과·자함 HP·침수·모듈 손상·생존이 같거나 좋으면 (a)이며, 자원 소모 차이는 수치만 보존한다. CG 3건을 (a)로 승인하고 DDG와 동일한 exact-state 기준 적용 경로에 추가했다.

| 180초 비교 항목 | KAPPA 기준 | 현재 | 판정 |
|---|---|---|---|
| SAM 발사 | 21 | 22 | 자원 차이 기록 |
| native SAM 격추 | 2 | 2 | 동일 |
| 자함 HP | 100 | 100 | 동일 |
| 침수 m³ | 0 | 0 | 동일 |
| 모듈 손상 | 0 | 0 | 동일 |
| 생존 | 생존 | 생존 | 동일 |
| VLS 잔여 셀 | 104 | 103 | 자원 차이 기록 |
| 20mm 잔탄 합계 | 3100 | 3039 | 61발 추가 소모 기록 |

원래 8발과 native 추가 스폰 47발의 개별 최종 상태도 동일하다. 비교는 앞선 CLEAN_A의 동일한 180초 고정 진단 지평이며, 추가 스폰 전부의 전투 종료를 의미하지 않는다. 이번에 180초 raid를 다시 쏘았다고 세지 않았다. 이 근거는 `evidence/cg-approval.json`, 원래 개별 결과는 CLEAN_A `RAID_OUTCOMES.csv`에 있다.

`approved-raid-baselines.json`에 CG의 이전/새 물리·관측·재고 전체 값, 각각 SHA-256 및 사유 **"사용자 승인: 결과 동일, 자원 소모 차이만 존재"**를 기록했다. DDG의 승인 항목3개는 그대로 보존했다. 승인된 게임 코어 해시에서만 적용하며 허용 오차를 늘리거나 비교 필드를 제외하지 않았다. 원래 판정값은 검수 로그 `originalChecks`에 유지한다.

| 함정 | 대상 검사 | 이전 상태 해시 | 새 상태 해시 | 사유 |
|---|---|---|---|---|
| DDG_119_LATE_FLIGHT_IIA | samePhysicalState, raidInventoryDeltaBounded, sameExistingObserverState | c2af74ca4c0f47ac3897824039e5912819fbef7d1460b4f501b42b0c1c4c2e6a | 2c7dfd5e810b8af7ebd7bd0036250516a22dc036d728431a18ae0a068648f579 | Native outcomes/damage/survival/weapon expenditure non-worse versus both Kappa and DZT; exact state changes are caused by the launch-handoff correction. |
| CG_52_LATE_TICONDEROGA | samePhysicalState, raidInventoryDeltaBounded, sameExistingObserverState | 169abb7dc6c0d7b3e514260e3a4df503b01cdf07354daf28404f6b346814c92e | aabf9b49ef5c56621f398280ba6628fcd187f7d5275270dbeac64408e9abe6c0 | 사용자 승인: 결과 동일, 자원 소모 차이만 존재 |

최종 CLEAN_B HTML을 대상으로 전체 15 suites **420/420**을 다시 실행했다. 미통과 검사: 없음. 소요 805.42초. `python docs/cleanup/B/run_domain.py`는 승인 manifest를 명시적으로 사용한다. 승인 옵션 없는 과거 비교기의 결과를 소급 변경하지 않는다.

## 2. 추가 사격 대상과 비용

실행 전에 `PLAN.md`/`PLAN.json`과 채팅에 대상/비용을 보고했다. 기본 격자 부족 **17,450발**, 경계 세분화 최대 **425발**, 합계 최대 **17,875발**, 예상 **35.68분**이었다. 3시간 제한 이내이므로 실행했다.

실제 기본 격자 17,450발 + 경계 세분화 140발 = **17,590발**, **24.35분**, 2 workers. 기존 격자 **25,455발**을 재사용했다. 서로 다른 시드의 비행을 하나로 재사용하지 않았다. 사전 추정은 같은 칸의 인접 기존 비행 tick 수×과거 비용,1.5 여유와 준비60초를 사용했다.

새 1km 격자 보강은120칸 모두 필요했다. 그중 CLEAN_A의 끊김 뒤 미측정이 남은 칸은21개다. 전체 부족 거리 목록은 PLAN.json에 있으며, 그21개는 아래와 같다.

| 기종 | 고도 m | 운동 | 이전 구간 km | 끊김 뒤 미측정 점 수 |
|---|---|---|---|---|
| SM2 | 30 | INBOUND_250 | 4~300 | 2 |
| SM2 | 30 | INBOUND_680 | 1~1 | 107 |
| SM2 | 5000 | INBOUND_680 | 1~1 | 107 |
| SM2 | 15000 | OUTBOUND_250 | 1~90 | 9 |
| SM2ER | 30 | STATIONARY | 3~245 | 1 |
| SM2ER | 30 | INBOUND_250 | 1~360 | 2 |
| SM2ER | 30 | INBOUND_680 | 1~1 | 107 |
| SM2ER | 5000 | INBOUND_680 | 1~1 | 107 |
| SM2ER | 10000 | INBOUND_680 | 1~5 | 102 |
| SM2ER | 15000 | INBOUND_680 | 1~5 | 102 |
| SM2ER | 15000 | OUTBOUND_250 | 1~105 | 21 |
| SM2ER | 20000 | CROSS_250 | 1~335 | 1 |
| SM6 | 30 | INBOUND_680 | 1~1 | 107 |
| SM6 | 5000 | INBOUND_680 | 1~1 | 107 |
| SM6 | 10000 | INBOUND_680 | 1~5 | 102 |
| SM6 | 15000 | INBOUND_680 | 1~5 | 102 |
| SM6 | 15000 | OUTBOUND_250 | 1~110 | 26 |
| ESSM | 30 | INBOUND_250 | 1~30 | 8 |
| ESSM | 30 | INBOUND_680 | 1~30 | 24 |
| ESSM | 10000 | INBOUND_250 | 1~1 | 25 |
| ESSM | 15000 | INBOUND_250 | 1~1 | 24 |

5개 고정 시드 세트(game RNG / navigation): (1831565813, 2047861954), (305419896, 2654435769), (2271560481, 1013904242), (324508639, 2779096485), (610839776, 1515870810). 같은 빌드·기종·고도·표적 운동·거리·시드의 기록만 재사용했다. D2 원시 데이터 logical SHA-256, CLEAN_A의 Git blob, 각5발 결과 SHA-256을 검증했다. 승인 전/다른 유도 버전의 기록은 섞지 않았다.

## 3. 바뀐 유효구간과 나머지 구간

격자는1~min(30, 바깥 최대거리)km의1km 간격, 이후35km부터 바깥 최대거리 이하5km 간격이다. 통과는5발 중3발 이상 native KILL/STRUCT_FAIL다. 격자의 연속 통과 묶음 중 **끝 거리가 가장 먼 묶음**을 선택했다. 폭이 가장 넓은 묶음 선택과 다르다. 그 시작이30km를 넘으면 앞 실패점과의 사이를1km 간격으로 모두 보강하고 연결성을 다시 계산했다. 숨은 중간 실패를 건너뛰어 첫 성공과 이어 붙이지 않는다.

다른 통과 묶음은 `otherRuns`, 묶음 사이 실패 지점들은 `deadZones`에 시작·끝과 대표 native 실패 사유를 남겼다. 첫 묶음 전/마지막 묶음 뒤 실패는 `boundaryFailures`로 별도 기록했다. 이 범위는 측정 격자의 결과이며, 사이의 모든 연속 실수 거리를 시험했다는 뜻이 아니다. 바깥 최대거리가5의 배수가 아니면 해당 끝값을 별도 격자점으로 추가하지 않았다. 바깥 링 값 자체는 변경하지 않았다.

| 기종 | 고도 m | 운동 | 이전→새 km | otherRuns | deadZones |
|---|---|---|---|---|---|
| SM2 | 30 | INBOUND_680 | 1~1 → 6~490 | 1~1 | 2~5(SEA_IMPACT) |
| SM2 | 5000 | INBOUND_680 | 1~1 → 7~500 | 1~3 | 4~6(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2 | 10000 | INBOUND_680 | 1~500 → 9~500 | 1~5 | 6~8(SEA_IMPACT) |
| SM2 | 15000 | INBOUND_680 | 1~500 → 15~500 | 1~11 | 12~14(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2 | 15000 | OUTBOUND_250 | 1~90 → 129~150 | 1~90 | 95~128(BATTERY_EXHAUSTED) |
| SM2ER | 30 | INBOUND_250 | 1~360 → 4~360 | 1~1 | 2~3(SEA_IMPACT) |
| SM2ER | 30 | INBOUND_680 | 1~1 → 7~500 | 1~3 | 4~6(SEA_IMPACT) |
| SM2ER | 1000 | INBOUND_680 | 1~500 → 4~500 | 1~1 | 2~3(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 1000 | OUTBOUND_250 | 1~35 → 42~45 | 1~35 | 40~41(LOW_SPEED) |
| SM2ER | 5000 | INBOUND_680 | 1~1 → 7~500 | 1~4 | 5~6(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 10000 | INBOUND_250 | 1~460 → 4~460 | 1~2 | 3~3(PROX_DETONATION_MISS) |
| SM2ER | 10000 | INBOUND_680 | 1~5 → 11~500 | 1~6 | 7~10(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 15000 | INBOUND_250 | 1~500 → 5~500 | 1~3 | 4~4(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 15000 | INBOUND_680 | 1~5 → 14~500 | 1~8 | 9~13(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 15000 | OUTBOUND_250 | 1~105 → 189~230 | 1~105 | 110~188(LOW_SPEED) |
| SM2ER | 20000 | INBOUND_680 | 1~500 → 15~500 | 1~10; 12~13 | 11~11(PROX_DETONATION_MISS); 14~14(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM2ER | 20000 | CROSS_250 | 1~335 → 342~345 | 1~335 | 340~341(PROX_DETONATION_MISS) |
| SM6 | 30 | INBOUND_250 | 1~380 → 4~380 | 1~1 | 2~3(SEA_IMPACT) |
| SM6 | 30 | INBOUND_680 | 1~1 → 7~500 | 1~3 | 4~6(SEA_IMPACT) |
| SM6 | 1000 | INBOUND_680 | 1~500 → 4~500 | 1~1 | 2~3(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM6 | 5000 | INBOUND_680 | 1~1 → 7~500 | 1~4 | 5~6(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM6 | 10000 | INBOUND_680 | 1~5 → 11~500 | 1~5 | 6~10(SEA_IMPACT) |
| SM6 | 15000 | INBOUND_680 | 1~5 → 14~500 | 1~8 | 9~13(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| SM6 | 15000 | OUTBOUND_250 | 1~110 → 190~260 | 1~110 | 115~189(LOW_SPEED) |
| SM6 | 20000 | INBOUND_680 | 1~500 → 12~500 | 1~10 | 11~11(PROX_DETONATION_MISS) |
| ESSM | 30 | STATIONARY | 1~25 → 35~50 | 1~28 | 29~34(LOW_SPEED) |
| ESSM | 30 | INBOUND_250 | 1~30 → 72~95 | 1~30 | 35~71(PROX_DETONATION_MISS) |
| ESSM | 30 | INBOUND_680 | 1~30 → 53~175 | 1~30; 45~45 | 35~40(PROX_DETONATION_MISS); 50~52(PROX_DETONATION_MISS) |
| ESSM | 30 | OUTBOUND_250 | 1~10 → 1~11 | 없음 | 없음 |
| ESSM | 30 | CROSS_250 | 1~15 → 1~17 | 없음 | 없음 |
| ESSM | 1000 | STATIONARY | 1~25 → 40~45 | 1~26 | 27~39(LOW_SPEED) |
| ESSM | 1000 | OUTBOUND_250 | 1~10 → 1~12 | 없음 | 없음 |
| ESSM | 1000 | CROSS_250 | 1~15 → 1~18 | 없음 | 없음 |
| ESSM | 5000 | INBOUND_250 | 1~60 → 3~60 | 1~1 | 2~2(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| ESSM | 5000 | OUTBOUND_250 | 1~10 → 1~13 | 없음 | 없음 |
| ESSM | 10000 | STATIONARY | 2~25 → 2~28 | 없음 | 없음 |
| ESSM | 10000 | INBOUND_250 | 1~1 → 6~40 | 1~1; 3~3 | 2~2(TERMINAL_MISS_TRACKED_DIVERGENCE); 4~5(TERMINAL_MISS_TRACKED_DIVERGENCE) |
| ESSM | 10000 | CROSS_250 | 1~20 → 1~22 | 없음 | 없음 |
| ESSM | 15000 | STATIONARY | 2~25 → 2~29 | 없음 | 없음 |
| ESSM | 15000 | INBOUND_250 | 1~1 → 9~40 | 1~1 | 2~8(LOW_SPEED) |
| ESSM | 15000 | CROSS_250 | 1~20 → 1~23 | 없음 | 없음 |
| ESSM | 20000 | STATIONARY | 2~25 → 2~27 | 없음 | 없음 |
| ESSM | 20000 | CROSS_250 | 2~20 → 2~22 | 없음 | 없음 |

값 변경 43칸, 동일 77칸. 범위가 같은 칸의 otherRuns/deadZones도 전체 JSON 및 FINAL_TABLE.csv에 보존했다. 근거리의 짧은 성공 구간을 삭제하거나 통과 기준을 완화하지 않았다.

## 4. 기종별 최종 표

각 칸은 **바깥 / 최소~최대 유효 km**. SM2=SM-2MR, SM2ER=SM-2ER, SM6=SM-6, ESSM=ESSM Block 2. 운동 속도 단위m/s. 500km는 측정 상한이며 상한 바깥 최대치를 추정하지 않았다.

### SM2

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 203 / 2~195 | 320 / 4~300 | 500 / 6~490 | 31 / 1~30 | 89 / 2~85 |
| 1000 | 212 / 1~210 | 329 / 2~325 | 500 / 3~500 | 33 / 1~30 | 102 / 1~100 |
| 5000 | 228 / 1~225 | 342 / 1~340 | 500 / 7~500 | 46 / 1~45 | 172 / 1~170 |
| 10000 | 249 / 1~245 | 365 / 1~355 | 500 / 9~500 | 63 / 1~60 | 202 / 1~200 |
| 15000 | 265 / 1~260 | 377 / 1~370 | 500 / 15~500 | 153 / 129~150 | 223 / 1~220 |
| 20000 | 265 / 1~260 | 365 / 1~355 | 500 / 1~500 | 163 / 1~160 | 233 / 1~225 |

### SM2ER

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 257 / 3~245 | 384 / 4~360 | 500 / 7~500 | 42 / 1~35 | 75 / 2~75 |
| 1000 | 274 / 1~270 | 403 / 2~400 | 500 / 4~500 | 45 / 42~45 | 81 / 2~80 |
| 5000 | 299 / 1~295 | 427 / 1~425 | 500 / 7~500 | 55 / 1~55 | 242 / 1~240 |
| 10000 | 334 / 1~330 | 469 / 4~460 | 500 / 11~500 | 65 / 1~65 | 284 / 1~280 |
| 15000 | 369 / 1~365 | 500 / 5~500 | 500 / 14~500 | 233 / 189~230 | 320 / 1~315 |
| 20000 | 392 / 1~385 | 500 / 1~500 | 500 / 15~500 | 258 / 1~255 | 351 / 342~345 |

### SM6

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 265 / 3~265 | 384 / 4~380 | 500 / 7~500 | 38 / 1~35 | 79 / 2~75 |
| 1000 | 297 / 1~295 | 431 / 2~430 | 500 / 4~500 | 45 / 1~45 | 85 / 2~80 |
| 5000 | 325 / 1~325 | 461 / 1~460 | 500 / 7~500 | 57 / 1~55 | 268 / 1~265 |
| 10000 | 365 / 1~365 | 500 / 1~500 | 500 / 11~500 | 69 / 1~65 | 313 / 1~310 |
| 15000 | 410 / 1~405 | 500 / 1~500 | 500 / 14~500 | 262 / 190~260 | 356 / 1~355 |
| 20000 | 443 / 1~435 | 500 / 1~500 | 500 / 12~500 | 293 / 1~285 | 397 / 1~395 |

### ESSM

| 고도 m | STATIONARY | INBOUND_250 | INBOUND_680 | OUTBOUND_250 | CROSS_250 |
|---|---|---|---|---|---|
| 30 | 53 / 35~50 | 99 / 72~95 | 179 / 53~175 | 11 / 1~11 | 17 / 1~17 |
| 1000 | 49 / 40~45 | 99 / 2~95 | 179 / 4~175 | 12 / 1~12 | 18 / 1~18 |
| 5000 | 30 / 1~30 | 62 / 3~60 | 116 / 7~115 | 13 / 1~13 | 20 / 1~20 |
| 10000 | 28 / 2~28 | 41 / 6~40 | 66 / 14~65 | 15 / 1~15 | 22 / 1~22 |
| 15000 | 29 / 2~29 | 40 / 9~40 | 63 / 19~60 | 15 / 1~15 | 23 / 1~23 |
| 20000 | 27 / 2~27 | 37 / 10~35 | 55 / 24~50 | 15 / 1~15 | 22 / 2~22 |

## 5. 검수 B1–B4

| 검수 | 결과 | 증거 |
|---|---|---|
| B1 | PASS | 420/420; DDG3+CG3 승인 exact 기준, 사유/해시 기록 |
| B2 | PASS | ENV_D 블록 외 게임 코드·UI·자산 byte 동일, 실제 함수283개 일치,120초 무표적/전투 truth 동일 |
| B3 | PASS | 최종 HTML에서 UI88/88 새 실행 |
| B4 | PASS | 120칸 최소/최대 확정, 미측정0, otherRuns/deadZones 기록 및 독립 Python 재구성 |

| 120초 상태 | 양쪽 동일 SHA-256 |
|---|---|
| 무표적 | fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc |
| 전투 | b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1 |

내장 표 `AEGIS_ENVELOPE_TABLE_D_3`, profileHash `fa87852960ef276597cd43653d3d112da07cd844448d5ee6ad703c4791043121`. DDG/CG status().match=true와complete=true를 확인했다. 각 행 previous는 CLEAN_A 원문 값이며 그 안의 이전 D2 기록도 보존했다. 지도·발사 판정에 연결하지 않았다. 게임 코드·PN/Kappa·추진·항력·질량·G·배터리·시커·신관·Pk 계수 변경0.

byte 동일 검사는 압축 실행 main을 해제한 뒤 ENV_D 블록을 제외해 비교했다. 재포장에 필요한 C55 asset13의 gzip payload와 rawBytes/gzipBytes/SHA-256 메타데이터만 갱신했다. 나머지 HTML shell·UI 및 자산0–12는 동일하다.

감사 도구의 초기 오류1건도 보존했다. 즉시 기폭 결과 samResult=MISS라도 이미 표적 탄두 유폭으로 native 최종 outcome=KILL인6발이 있었다. 초기 감사는 samResult만 검사해 이를 불일치로 표시했다. 기존 D2의 최종 outcome 및 lethal 정의를 확인해 감사 도구의 참조 필드를 바로잡았다. 게임·사격 결과·lethal 값·구간·통과 기준은 바꾸지 않았다. 원본 오류 로그와6발 내역은 evidence/audit-diagnostic-correction.json 및 shot-audit-initial-samresult-error.log에 있다.

재현 도구: plan.cjs → measure.cjs → build.py → audit.cjs → verify_intervals.py → verify_native.cjs → run_domain.py / run_ui.py / verify_delivery.py → report.py. 브라우저는 기존 Playwright/Chromium, Node AST 도구는 기존 acorn 의존성을 쓴다. 원시 새 사격은 results/cells, 소스/재사용 해시는 evidence, 별도 CSV는 ADDITIONAL_SHOTS.csv 및 CHANGED_INTERVALS.csv에 있다.
