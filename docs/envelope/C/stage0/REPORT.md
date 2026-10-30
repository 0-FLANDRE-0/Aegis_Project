# 변경 전 현재 엔진500km 측정

SM-2ER/SM-6, 고도1/10/20km, 정지 표적. 실제 게임 native 비행/유도/신관 경로와 기존 이상 지원 경계를 사용했다. 1km 이분 탐색 뒤 더 먼 모든 정수km를 확인했다. 실제 장비 성능과 비교하지 않는다.

독립2회 각각 1,106사격, 19,690bytes 동일. SHA-256 `5137099780e8ab46a774690b2edf43d8eb5aa4be6ae95bb5dfc15c14bcf00e01`.
벽시계 492.545s / 491.711s. 다른 진단/브라우저 검사와 병행하여 단독 CPU 성능이 아니다.

| 기종 | 표적고도 | 최대 최초거리 | 실제 요격점거리 | 다음1km 실패 | 종말속도 | 최근접 |
|---|---:|---:|---:|---|---:|---:|
| SM2ER | 1km | 267km | 266.997930km | 268km: LOW_SPEED | 168.155m/s | 15.752m |
| SM2ER | 10km | 323km | 323.004233km | 324km: LOW_SPEED | 150.056m/s | 921.759m |
| SM2ER | 20km | 280km | 279.987734km | 281km: SEA_IMPACT | 535.487m/s | 158.950m |
| SM6 | 1km | 298km | 297.999655km | 299km: LOW_SPEED | 168.139m/s | 23.075m |
| SM6 | 10km | 368km | 368.003590km | 369km: LOW_SPEED | 149.831m/s | 70.790m |
| SM6 | 20km | 441km | 441.002128km | 442km: PROX_DETONATION_AIRCRAFT | 320.062m/s | 53.905m |

이 결과를 확정·보고한 뒤8개 설계 사거리 값을 변경했다. [baseline.json](baseline.json)에 원본 HTML SHA와 source/inputs/private byte 동일성을 남겼다.
