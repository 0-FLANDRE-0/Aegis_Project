# HELI_E → HELI_E1 성능 비교

비교 기준: 같은 RCS·표적 높이·헬기 고도·Hs. 모두 SIM_TUNED. 값은 M-of-N 후 Pd50 거리. 0은 유효 구간에서 Pd50을 형성하지 못했다는 뜻이며 탐지 확률0이라는 뜻이 아니다.

| 조건 | 수정 전 | 전 limiter | 수정 후 | 후 limiter |
|---|---:|---|---:|---|
| PERI 앵커 (h=152m, RCS=1m², 표적=1m, Hs=0.9m) | 35.000km | SNR | 35.000km | SNR |
| SHORT 소형 (h=152m, RCS=1m², 표적=1m, Hs=0.9m) | 미형성 | SNR/BLIND | 12.500km | SNR |
| LONG 소형 저고도25m (h=25m, RCS=1m², 표적=1m, Hs=0.1m) | 9.393km | SNR | 3.000km | SNR |
| LONG 소형 저고도50m (h=50m, RCS=1m², 표적=1m, Hs=0.1m) | 0.548km | SNR | 미형성 | SNR/BLIND |
| LONG 중형 고고도·거침 (h=3000m, RCS=180m², 표적=15m, Hs=3m) | 미형성 | SNR/BLIND | 50.000km | SNR |
| PERI 소형·거침 (h=152m, RCS=1m², 표적=1m, Hs=3m) | 24.283km | SNR | 34.162km | SNR |

모든 요청 운용 목표를 함께 충족했다. LONG 저고도 기준은 기존 최저 운용 고도25m까지 포함한다. 목표별 표적 분기 없이 모드/해면 상관도/공통 클러터 배율로 역산했다.

| 모드 | PRF Hz | 체류 ms | 예상 펄스 | SS3 상관도 | SS3 클러터 이득 | Hs3 이득 |
|---|---:|---:|---:|---:|---:|---:|
| LONG | 750 | 29.1667 | 21.8750 | 0.243906 | 3.5910 | 6.8098 |
| SHORT | 1200 | 3.2407 | 3.8889 | 0.274687 | 2.1683 | 2.8744 |
| PERI | 2491 | 3.2407 | 8.0727 | 0.075758 | 5.2563 | 6.6893 |

이득은 클러터에만 적용한다. 신호나 열잡음에 별도 펄스 수 배율을 추가하지 않는다. PERI 앵커 재역산으로 K는 45870055038317190000 → 31632967910890450000로 조정한다. 기존 모드 열잡음 처리 efficiency는 보존한다.

주사 간 PERI4-of-9 / LONG·SHORT2-of-3은 그대로다. 실제 빔 내부의 단일 주사 처리와 구별한다. 신규 허위 접촉 기대값은 앵커에서1/h, 기존 raw Pfa와 확인 경로는 유지한다.

전체 288개 동일 조건 행은 performance-comparison.csv/json, 수정 전/후 전체 텍스트는 performance-before.txt / performance-after.txt를 따른다.

## Limiter 변경 사례

- SHORT / MEDIUM_180 / 50m / Hs0.1: 29.599958km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 50m / Hs0.9: 29.599958km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 50m / Hs3: 29.599958km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 50m / Hs4: 29.599958km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 300m / Hs0.1: 29.598480km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 300m / Hs0.9: 29.598480km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 300m / Hs3: 29.598480km, SNR → INSTRUMENT
- SHORT / MEDIUM_180 / 300m / Hs4: 29.598480km, SNR → INSTRUMENT
- PERI / MEDIUM_180 / 152m / Hs0.1: 58.999804km, SNR → INSTRUMENT
- PERI / MEDIUM_180 / 152m / Hs0.9: 58.999804km, SNR → INSTRUMENT
- PERI / MEDIUM_180 / 152m / Hs3: 58.999804km, SNR → INSTRUMENT
- PERI / MEDIUM_180 / 152m / Hs4: 58.999804km, SNR → INSTRUMENT
