# AEGIS RANGE_A — 원인·복구 대책 (1차, 제한 범위)

## 이번 단계에서 완료한 내용

- 기존 게임 네이티브 엔진의 25개 동일 조건을 변경 전/후 1회씩 비교한 **50발 궤적 데이터**를 재사용했다. 새롭게 96조합 전체 스윕을 돌리지 않았다.
- 25쌍 중 **기존 격추 성공 → 신규 실패 13쌍**, 성공 유지 6쌍, 양쪽 실패 6쌍. 이는 조건별 단일 실행이지 통계적 명중률이 아니다.
- GitHub `range-a-env-c`의 `docs/envelope/C/REPORT.md`, `results/LOW_ALT_INVESTIGATION.md`, `docs/missile/range/A/build.py`에 기록된 원인·변경 범위를 대조했다.

## A. 사거리 정렬 이후 대규모 퇴행 — 원인

- 설계 최대 사거리와 로프트 **포화/강도 보간의 분모**(`fullLoftKm`)를 같은 값으로 키웠다.
- SM-2ER은 `fullLoftKm 240→360`, SM-6은 `260→450`으로 증가했다. 동일 거리에서 `거리 / fullLoftKm` 비율은 감소하므로, 기존 로프트 강도 계산식 아래에서는 이전보다 약한 로프팅 명령이 생길 수 있다.
- 대표 원본 게임 로그: **SM-2ER / 정지 5km / 150km**에서 최초 목표 선반 고도 **17.737→13.382km**, 최고고도 **15.943→12.266km**, 종말 속력 **467.5→161.3m/s**, 결과 **격추→LOW_SPEED**. 엔진의 추진/항력/배터리 수치 변경 없이 발생했다.
- RMAX(`nominalRmaxKm`, `maxRmaxKm`)와 B4 강도(`fullLoftKm`)의 책임을 분리해야 한다. 단지 최대 사거리 목표가 450km라는 이유로 `fullLoftKm=450`을 강제하면 안 된다.
- **확정 범위**: 위 50발 A/B 기록과 GitHub 보고서에서 퇴행을 확인. 앞선 대화에서 보고된 24회 네 조합 원인 분리시험(6/6, 6/6, 0/6, 0/6)은 원시 로그 파일이 현재 전달된 산출물에서 확인되지 않으므로 *예비 근거*로만 취급한다.

## B. 권장 소규모 복구 후보 (게임 코드 수정은 아직 안 함)

**1차 후보는 `fullLoftKm`만 되돌리는 것.**

| 필드 | SM-2ER RANGE_A → 후보 | SM-6 RANGE_A → 후보 |
|---|---:|---:|
| `nominalRmaxKm` | 360 → 360 | 450 → 450 |
| `maxRmaxKm` | 360 → 360 | 450 → 450 |
| `rangeGoalKm` (설계 목표/표시) | 360 → 360 | 450 → 450 |
| **`fullLoftKm` (로프트 포화 기준)** | **360 → 240** | **450 → 260** |

이 네 필드의 뜻을 분리할 것: **설계거리 ≠ 로프트 포화거리**. 향후 `fullLoftKm`의 명칭을 `loftSaturationDistanceKm` 등으로 바꾸는 것은 별도 리팩터링으로 넘긴다. 위 값은 정답이 확정된 최적화 값이 아니라 가장 안전한 **원인분리 및 복구 시험 후보**다.

## C. 단 6조건부터 재검증 (96조합은 아직 금지)

| 무장 | 표적고도 | 발사거리 | 변경 전 | RANGE_A |
|---|---:|---:|---|---|
| SM-2ER | 5km | 150km | INTERCEPT_SUCCESS | LOW_SPEED |
| SM-2ER | 1km | 267km | INTERCEPT_SUCCESS | SEA_IMPACT |
| SM-2ER | 10km | 323km | INTERCEPT_SUCCESS | LOW_SPEED |
| SM-6 | 10km | 150km | INTERCEPT_SUCCESS | LOW_SPEED |
| SM-6 | 1km | 298km | INTERCEPT_SUCCESS | SEA_IMPACT |
| SM-6 | 20km | 441km | INTERCEPT_SUCCESS | BATTERY_EXHAUSTED |

각 조건에 대해 동일 RNG·60Hz·정지 표적·이상 관측을 유지한다. 네 조합을 비교할 때만 다음을 분리한다:

- **BASE:** 이전 `ALL4_TERM` 설정
- **RMAX:** `nominalRmaxKm/maxRmaxKm`만 새 값
- **B4:** `fullLoftKm/rangeGoalKm`만 RANGE_A 값
- **RANGE_A:** 전부 새 값
- **RECOVERY 후보:** 현재 RANGE_A에서 `fullLoftKm`만 이전 240/260으로 복귀

이번 단계 성공 조건은 **기존 성공 6조건의 회복 여부, 로프팅 고도·속력·수명 종료 이유, 코드 변경 범위**를 확인하는 것. 6조건이 모두 회복되더라도 전체 96조합의 안정성을 증명한 것은 아니다. 실패가 남으면 그 조건만 유도 단계 전환과 종말 로그를 확인하고, 물리 성능값은 건드리지 않는다.

## D. 해면 충돌은 별도 원인 — 이번 복구와 분리

ENV_C의 `LOW_ALT_INVESTIGATION.md`는 **저고도 횡단 18조건 중 11건 SEA_IMPACT**를 기록한다. 세 이탈 재현 조건은 B4가 `DIRECT` 상태이고, **KAPPA_MIDCOURSE의 하강 명령 이후 회복이 늦어 충돌**했다. 이는 위 `fullLoftKm` 퇴행과 다른 코드 경로다.

기존 해면 보호 로직 `_samSeaClearanceRateGuard`는 **ESSM에만 적용되는 분기**가 확인됐다. 다른 SAM들은 저고도 보호를 동등하게 받지 못한다. 다음 별도 작업에서는 표적 30m·200m, 횡단/이탈, 10/20/40km의 기존 재현 케이스를 유지하며, 음의 수직속도·유도 명령·고도 예측 보호를 관찰해야 한다. **이번 단계에서는 해면 충돌 수정 금지.**

## E. Codex에게 넘길 짧은 후속 요청

> RANGE_A를 바로 튜닝하거나 엔진을 강화하지 말고 `fullLoftKm` 역할 분리만 **별도 시험 브랜치**에서 검증해 주세요. `nominalRmaxKm/maxRmaxKm`와 `rangeGoalKm`는 설계 목표 360/450km를 유지하고, `fullLoftKm`만 ER 360→240 / SM-6 450→260으로 돌린 후보를 만드세요. 위 여섯 조건에서 기준/전체 정렬/복구 후보의 비행 궤적·첫 shelf·최고고도·종말속도·성공 여부를 동일 시드로 비교해 주세요. 기존 게임 물리·Kappa·신관·배터리·종료기·UI는 변경하지 마세요. 해면 충돌 수정은 별도 과제로 남겨 주세요. 여섯 조건 결과만 먼저 보고하고 전체 96조합 재측정은 하지 마세요.

## 출처 및 한계

- 저장소: `0-FLANDRE-0/Aegis_Project`, 브랜치 `range-a-env-c`
- `docs/envelope/C/REPORT.md`, `docs/envelope/C/results/LOW_ALT_INVESTIGATION.md`, `docs/missile/range/A/REPORT.md`
- 게임 엔진의 SIM_TUNED 규칙에 대한 분석이며, 실제 무장 성능 주장 아님.
- 50발 궤적 비교는 한 조건당 각 빌드 **한 발씩**이다. 추가 재시험의 결과라고 해석하면 안 된다.
