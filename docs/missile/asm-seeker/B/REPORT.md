# ASM_SEEKER_B — 원거리 표적 검증과 cue 바구니 감사

IMPLEMENTED: **아니오** — 지시서식 SHADOW 후보가 기존 정지 수상표적을 탈락시키고 40–50 km 획득도 복구하지 못해 제품 승격을 거부했다.

TESTED: **예** — 실제 브라우저 게임 엔진에서 1,140조건을 두 번 실행했고 최종 실행은 182.38초, 오류 0건이다.

APPROVED: **아니오** — ESSM/SM-6 오획득 비증가 조건은 통과했지만 수상표적 주 판정이 실패했다.

UNRESOLVED: **분해되지 않은 함정+해면 합성 셀에서 함정성을 설명할 기존 관측량이 부족하다.**

RELEASE: **아니오** — B 제품 HTML, PR, 병합, release/tag를 만들지 않았다.

## 결론

45 km 실패는 단순 SNR 소실이 아니었다. 함정의 물리 반사는 존재하지만 같은 range-angle-Doppler 셀의 해면 반사와 합성되며, 거리와 함께 커지는 해면 셀 횡폭이 다시 `broadPenalty`와 평탄 배경 증거로 사용된다. `asmSeekerEchoMeasurement`가 임의의 폭을 새로 더한 것은 아니고, `asmSeekerCompositeReturns`가 물리 member와 해면 셀의 폭 및 centroid 분산을 전력 가중 RMS로 합성한 결과다.

지시서대로 분해되지 않은 축을 가점·감점 모두에서 빼고 기존 가중치만 재정규화한 SHADOW 후보를 만들었다. 이 후보는 해면·무표적 오획득 0을 유지하고 채프 통과를 제거했으며 ESSM Block 2와 SM-6 Block IA 대공·대함의 항공기/ASM 통과를 보존했다. 그러나 다음 이유로 ACTIVE가 될 수 없다.

- 기존 판정이 통과하던 정지 DDG/CG/SOV/시험 헐크의 고정 표본 80/80이 SHADOW에서는 0/80이 됐다.
- 40/45/50 km 수상 표본 240건에서 SHADOW 통과는 0건이라 원래 문제도 복구하지 못했다.
- 분해 불가 축을 모두 제외하면 정지 표적에는 사실상 kinematic/doppler 항만 남아 `.55`를 넘을 설명력이 없다.
- 이를 통과시키려면 threshold/가중치를 결과에 맞추거나 새 관측 특징을 도입해야 한다. 전자는 금지됐고 후자는 이번 단계에서 제안만 허용됐다.

따라서 제품 코드는 기준 ASM_SEEKER_A와 byte-for-byte 동일하게 보존했다. 기준 HTML SHA-256은 `9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f`다.

## 진단 행렬

| 구분 | 조건 수 | 결과 |
|---|---:|---|
| 수상 표적 | 480 | 거리 의존 결함 확인; SHADOW 160→80 snapshot pass, 원거리 복구 0 |
| 해면·채프·무표적 대조군 | 180 | 해면/무표적 0 유지, 채프 20→0 snapshot pass |
| ESSM B2 ARH | 120 | 항공기 30/30, ASM 30/30 유지; 해면 0 유지; 채프 30→0 |
| SM-6 IA 대공 | 120 | 항공기 30/30, ASM 30/30 유지; 해면 0 유지; 채프 30→0 |
| SM-6 IA 대함 | 120 | 항공기 30/30, ASM 30/30 유지; 해면 0 유지; 채프 30→0 |
| Kh-32/Kh-35U cue | 120 | 탐색 안·바구니 밖 0; 바구니 부작용 미확인 |

SM-6의 두 운용 경로는 같은 RF evidence 프런트엔드를 사용하므로 결과가 같았지만, 추론으로 대체하지 않고 각각 120조건을 별도로 실행했다. 사용자 추가 기준인 “공중 표적·해면·채프 오획득률 하나라도 증가 시 FAIL”에서 증가는 0건이다.

## 45 km 대표 표본

200 m 고도, 정지 시험 헐크, 45 km에서 물리 표적 반사는 5/5 존재했다. 대표 합성값은 SNR 약 0.389, 횡폭 약 961.5 m, 거리폭 약 101.2 m, 수직폭 약 9.6 m였다. 현재 점수 평균은 0.398, SHADOW는 0.357로 둘 다 `.55` 미만이었다. 같은 조건의 DDG도 현재 0.399, SHADOW 0.360이었다.

지시서가 “A에서 쓴 소형 수상표적”으로 부른 등록 객체 `EMPTY_CONTAINER_TEST_HULK_V1`은 코드상 전장 210 m, 폭 32.2 m의 대형 시험 헐크다. 보고서와 raw 데이터에서 이를 `HULK`로 명시했으며 소형정으로 오해하지 않았다.

## cue 바구니

Kh-32와 Kh-35U를 60/100/130 km에서 15 kn 직진, 30 kn 직진, 30°/90° 변침으로 시험했다. 120/120이 탐색 구역과 기존 바구니 안에 있었다. `탐색 안 + 바구니 밖`은 0건이므로 경과시간 기반 바구니 확대 조건은 성립하지 않았고 제품 변경도 하지 않았다. 일부 획득 실패는 evidence/LOS 경로였으며 바구니 원인으로 분류하지 않았다.

## 후속 개선 후보

동일한 분해능 셀 안에서 함정과 해면을 구별하려면 기존 폭의 재해석만으로 부족하다. 다음 중 하나를 별도 설계·물리 검증하는 것이 타당하다.

- 주변 해면 셀 대비 국소 signal-to-clutter contrast
- 여러 dwell 사이 centroid/전력의 지속성
- waveform 기반 range/Doppler morphology

이는 새 특징이므로 이번 B에는 구현하지 않았다. 공용 함수는 Kh-32, Kh-35U, ESSM B2, SM-6 IA에 영향을 주므로 후속 단계에서도 네 계열을 같은 행렬로 검증해야 한다.

## 산출물 안내

- 거리별 수치와 SAM 비교: `EVIDENCE_RANGE_AUDIT.md/.json`, `RANGE_SCORE_TABLE.csv`, `range_score.svg`
- cue 수치: `CUE_BASKET_AUDIT.md/.json`
- 코드 경로 원인: `ROOT_CAUSE.md`
- 원시 1,140조건: `BASELINE_DIAGNOSTICS.json`
- 제품 비변경 증명: `DIAGNOSTIC_BUILD.json`, `SCOPE.json`
- 기계 판정: `VALIDATION.json`

제품 변경이 없으므로 `Aegis_SIM_v48_WIP_ASM_SEEKER_B.html`, 제품 `BUILD.json`, `changes.diff`는 만들지 않았다. 주 판정 실패로 광범위 제품 회귀와 PR/병합도 실행하지 않았다.
