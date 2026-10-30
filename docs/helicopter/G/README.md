# HELI_E1 — 빔 체류 펄스·주파수 민첩성 보정

기준은 HELI_E `ff3ecebbcb9b4660f0e627fb80175fc5737d1f1b`다. 기존 F 소스·HTML은 동일 bytes로 보존하고 G에서 보정한다. [수정 전 전체 표](evidence/final/comparison/performance-before.txt), [수정 후 전체 표](evidence/final/comparison/performance-after.txt), [288조건 비교](evidence/final/comparison/performance-comparison.md), [CSV](evidence/final/comparison/performance-comparison.csv), [검증](evidence/verification-summary.json)을 따른다.

## 기존 확정과 적용 범위

PERI의 주사 간 누적은 기존 **단일 주사 검출→이진4-of-9 하나**다. LONG/SHORT도2-of-3 하나다. 이번 펄스 적분은 그보다 앞선 **한 빔 체류 내부** 처리다. 신호·열잡음에 추가 N 배율을 붙이지 않고 클러터 항만 억제한다. PERI 앵커가 우선이며 K는 억제된 클러터를 포함해 다시 역산한다. 기존 모드별 열잡음 processing efficiency는 바꾸지 않는다.

고정 이득 하나로는 LONG 소형 표적을 약하게 유지하면서 고고도·거친 바다의 중형함을 살리는 목표가 충돌했다. 이 때문에 모드/해면 상태에 따른 잔류 coherent clutter와 공통 원시 클러터 배율을 역산했다. 표적 RCS·종류에 따라 실제 처리 경로를 분기하지 않는다. 기존 비행·IFF·Hawklink·EMCON·무장 권한·상태 소유권·렌더 읽기 전용 정책은 변경하지 않는다. 저장 스키마도 그대로다.

## 모형과 역산

모든 수치는 **SIM_TUNED**다. PRF 범위750–2491Hz는 사용자가 지정한 APS-143 계열 유추이며 모드 배정은 실제 APS-153 제원이라는 뜻이 아니다. `APS143_FAMILY_ANALOG`를 사용한다. 주파수 민첩성의 존재·개념은 `APS147_DTIC`, 상관도 모형과 아래 숫자는 `GENERIC_RADAR_PRINCIPLE`/SIM_TUNED다. 앞선 DTIC 원본 PDF 접근 한계는 F의 출처 기록을 그대로 따른다.

- FWHM 빔 체류시간 `T=2.1°/(rpm×6°/s)`.
- 예상 펄스 수 `N=PRF×T`. 정수가 아닌 값은 평균 pulse count이며 프레임별 반올림 계단을 만들지 않는다.
- 유효 쌍별 상관도 `rho=1/[1+beta(mode)×(Hs+H0)]`, `H0=0.32m`.
- 클러터 억제 이득 `G=N/[1+(N−1)rho]`, 범위1…N. 부분 상관의 coherent 잔류 성분을 가정한 모형이며 실제 파형·주파수 hopping schedule·정밀 해면 스펙트럼 복제가 아니다.
- 해면 원시 반사는 그대로 합성한다. 수신기의 해석적 클러터 항과 실제 샘플 local clutter 항을 각각 **G로 한 번** 나눈다. 열잡음의 `1`은 그대로며 신호에도 N/G를 곱하지 않는다. CFAR 이후 단일 주사 검출/M-of-N 경로도 유지한다.

PRF는 LONG750 / SHORT1200 / PERI2491Hz다. N은21.875 /3.888889 /8.072685다. PERI beta10/m와 H0는 명시된 자유 SIM_TUNED 값이다. H0는 해면이 거칠어질수록 유효 클러터가 역으로 감소하지 않도록 점검했다. PERI152m·1m²·높이1m·Hs0.9m·35km의4-of-9 확정50%에서 K≈3.16329679×10¹⁹, 정규화 참조거리≈74.995462km를 구한다. 이는 실제 유효 사거리/송신출력이 아니다.

같은 방정식에서 SHORT152m·SS3의12.5km를 맞추는 beta≈2.164348315/m를 구한다. LONG은 최저 운용 고도25m·Hs0.1m·1m²의3km와 고도3000m·Hs3m·180m²/표적 높이15m의50km를 동시에 풀어 beta≈2.540935601/m와 원시 클러터 배율≈4.601381920을 구한다. LONG의 기존1.7은 이 역산값으로 대체한다. PERI가 같은 대표 조건의 소형 표적에서 더 멀리 탐지하도록 유지했다. 요청한 운용 목표 중 포기한 항목은 없다.

## Limiter와 전후 표

계기거리 경계의 부동소수점 오차 때문에 cap과 같은 값이 SNR로 표시되던 경우를 수정했다. 사거리 비교 허용오차는0.001m이고 cap과 일치하면 INSTRUMENT/HORIZON을 명시한다. 실제 SNR 한계가 cap보다 작을 때는 SNR을 유지한다. 성능표는 직하 사각 바로 바깥의 한 점만으로 전체 구간을0 처리하지 않고 바깥부터 검출 구간을 찾은 뒤 이분법으로 마지막 Pd50 경계를 구한다.

전후 표는 **동일한288조건**(3표적×3모드×고도25/50/150/152/300/600/1000/3000m×Hs0.1/0.9/3/4m)이다. 수정 전은 공개한 F의 계산 결과를 그대로 보존한다. 수정 후는 G의 계산이다. 텍스트 두 파일에는 기존 DEBUG 표와 추가 조건을 모두 출력한다. `미형성`/0km는 유효 구간에서 Pd50을 이루지 못했다는 뜻이며 검출 확률0 또는 절대 탐지 불가라는 뜻이 아니다. 개별 표적의 센서 트랙/무장 사거리를 보장하지 않는다.

## 검증·재현·한계

`verify_static.py`는 pinned HTML의 정확 재빌드,14 packed 검증·문법, 추가 미정의 식별자 없음, 기존 함수 중 명시된6개만 변경됨을 검사한다. `verify_receiver.cjs`는 원시/샘플 클러터가 한 번만 억제되고 신호·열잡음·raw Pfa에 추가 펄스 이득이 없음을 검사한다. `compare.cjs`는 전후 전체 표와 목표·cap·단조성을 검사한다.

`verify_native.py`는 공통 RF에 분리된 물리 반사체를 넣어 원래 합성→측정→게이트→확정을 거친다. 전투 track/port를 주입하지 않으며 private receiver만 사용한다. PERI2만 창, 나머지 각5천 창의 목표 거리 확정률과 상태/RNG 읽기 전용을 검사한다. 두 기의 실제 SHORT/PERI 방사·Hawklink를1/8/16/64×1152 fixed ticks에서 비교하고 실제 DEBUG 모달도 누른다. 기존 F의 전체120초 준비/모델/3D/IFF/권한 검사를 새 결과 수에 다시 합산하지 않는다. 이 코드는 해당 경로를 바꾸지 않는다.

오경보는 실제 noise-tail/측정/기하 연관/M-of-N 코드의 모드별8시간 수치 가속으로 센다. 전체 월드8시간 실시간 플레이나 실장비 인증이 아니다. DDG-119/CG-52의 대기·8Kh-32 AUTO·피격6조건은 E와 비교한다. 실제 휴대폰/하드웨어 FPS는 측정하지 않았다.

```sh
python docs/helicopter/G/build.py archive/v48/WIP_HELI_E/Aegis_SIM_v48_WIP_HELI_E.html /tmp/Aegis_SIM_v48_WIP_HELI_E1.html
python docs/helicopter/G/verify_static.py archive/v48/WIP_HELI_E/Aegis_SIM_v48_WIP_HELI_E.html Aegis_SIM_v48_WIP_HELI_E1.html /tmp/e1/static
node docs/helicopter/G/compare.cjs /tmp/e1/comparison
node docs/helicopter/G/verify_receiver.cjs /tmp/e1/receiver
APS_TEST_HOURS=8 node docs/helicopter/G/verify_model.cjs /tmp/e1/model --false
python docs/helicopter/G/verify_native.py Aegis_SIM_v48_WIP_HELI_E1.html /tmp/e1/native
python docs/helicopter/F/verify_regression.py archive/v48/WIP_HELI_E/Aegis_SIM_v48_WIP_HELI_E.html Aegis_SIM_v48_WIP_HELI_E1.html /tmp/e1/regression --baseline-only
```

기존 자산·모델과 A–F 소스를 보존한다. E 네 파일은 동일 bytes/blob으로 archive한다. 전체 원본을 `helicopter-radar-e1`에 올리고 독립 GitHub blob readback으로 확인한다. Actions 사용 불가 조건을 유지해 수동 workflow만 준비하며 dispatch/main·이전 브랜치 병합/새 PR 생성은 하지 않는다.
