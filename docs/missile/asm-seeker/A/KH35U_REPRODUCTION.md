# Kh-35U S1 재현

상태: **IMPLEMENTED / TESTED / APPROVED(지시서) / UNRESOLVED(45 km 감도) / RELEASE(no)**

고정 행렬은 거리 20/45 km, 표적함-자함 방위 분리 0/5/10/20/40°, 시드 519000~519009의 100조건이다. 계측 hook ON/OFF는 Kh-35U·Kh-32에서 final state와 전역 RNG가 일치했다. ACQUIRE 상태에서 후보 RF를 따라가는 횡방향 rate command는 Kh-35U 100조건 모두 0이었다.

## 수정 전 관측

| 거리 | 분리 | TRACK | 첫 후보 |
|---:|---:|---:|---|
| 20 km | 0° | 10/10 | 표적함/해면 합성 |
| 20 km | 5° | 10/10 | 표적함 |
| 20 km | 10° | 10/10 | **자함** |
| 20 km | 20° | 10/10 | **자함** |
| 20 km | 40° | 10/10 | 표적함 |
| 45 km | 전 분리 | 0/50 | 없음 |

리뷰 가설이던 “ACQUIRE 중 후보를 따라 좌우 조향”은 재현되지 않았다. 실제 결함은 EKF 초기화 전 연관 점수에서 강한 SNR이 launch cue 잔차 감점을 이기는 것이었다. 10/20°에서 자함이 cue 바스켓과 다른데도 먼저 선택됐다.

45 km 조건은 raw echo가 있어도 `DISTRIBUTED_BACKGROUND_EVIDENCE`로 거부됐다. 이는 RF 감도·evidence 계수 영역이며 이번 작업의 계수 변경 금지에 따라 수정하지 않는다.

원시 행렬과 요약은 `KH35U_REPRODUCTION.json`, `evidence/KH35U_*_RAW.json.gz`에 있다.
