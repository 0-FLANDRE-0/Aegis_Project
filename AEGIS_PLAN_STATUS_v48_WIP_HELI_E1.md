# AEGIS v48 WIP HELI_E1 — 클러터 펄스·민첩성 보정

구현·런타임·브라우저 회귀 완료. 기준은 HELI_E `ff3eceb`, 작업 브랜치는 `helicopter-radar-e1`, 구현 소스는 `8a919ae`다. [조작·계산·재현](docs/helicopter/G/README.md), [전후 비교](docs/helicopter/G/evidence/final/comparison/performance-comparison.md), [수정 전 전체 표](docs/helicopter/G/evidence/final/comparison/performance-before.txt), [수정 후 전체 표](docs/helicopter/G/evidence/final/comparison/performance-after.txt), [검증](docs/helicopter/G/evidence/verification-summary.json), [원격 확인](docs/helicopter/G/remote-publication.json)을 따른다.

- 원본 **16,074,222bytes**, E 대비 **2,277bytes** 증가.
- HTML SHA-256 `4515668a06d7efcbae351b8e7b1d433c8c534e2b479c0ea3f1e9a7d826e2a352`.
- packed13 SHA-256 `d0590a00b398e7155510069290fa5d23970bab198e32bf045b36bfb83953f9c8`.
- 나머지13 packed 자산과 비행·조작·3D·IFF·링크·무장 권한 경로를 보존한다. 저장 schema는 바꾸지 않는다.

## 보정

PRF는 LONG750 / SHORT1200 / PERI2491Hz, 모두 APS143_FAMILY_ANALOG를 참고한 SIM_TUNED다. N=PRF×(2.1°/각속도)로 예상 펄스 수21.875 /3.888889 /8.072685를 구한다. 주파수 민첩성의 부분 상관 모형 G=N/[1+(N−1)rho], rho=1/[1+beta×(Hs+0.32m)]로 클러터만 억제한다. 실제 해면 샘플과 해석적 항에 한 번씩 적용하며 신호·열잡음에는 N을 다시 곱하지 않는다. PERI의 주사 간4-of-9와 LONG/SHORT2-of-3은 유지한다.

PERI 앵커35km/152m/1m²/높이1m/Hs0.9m/창 확정50%를 우선해 K≈3.16329679×10¹⁹로 재역산했다. 모드 열잡음 processing efficiency는 보존한다. SHORT beta≈2.164348315/m, LONG beta≈2.540935601/m와 원시 클러터 배율≈4.601381920은 요청 목표를 동시에 푼 값이다. 실제 장비의 파형/상관 계수라는 뜻이 아니며 모든 신규 값에 SIM_TUNED/reference를 기록한다.

| 조건 — Pd50거리 | E | E1 |
|---|---:|---:|
| PERI 소형1m²,152m,SS3 |35.000km|35.000km|
| SHORT 소형1m²,152m,SS3 |미형성|12.500km|
| LONG 소형1m²,25m,Hs0.1m |9.393km|3.000km|
| LONG 소형1m²,50m,Hs0.1m |0.548km|미형성|
| LONG 중형180m²/높이15m,3000m,Hs3m |미형성|50.000km|
| PERI 소형1m²,152m,Hs3m |24.283km|34.162km|

요청한 목표 중 포기한 항목은 없다. 실제 처리는 표적 RCS/종류별 예외 없이 모드·해면 상관도·공통 클러터 배율로 계산한다. `미형성`은 유효 구간에서 Pd50에 미달한다는 뜻이며 절대 탐지 불가가 아니다. 수정 전·후 전체288조건 표를 따로 남겼다.

계기거리 끝값이 부동소수점 오차 때문에 SNR로 표시되던 사례를 INSTRUMENT로 바로잡았다. 허용오차0.001m로 실제 SNR 경계와 기하 cap을 구분한다. 성능표는 직하 사각 근처 한 점만으로 전체 구간을0 처리하지 않으며 바깥부터 검출 구간을 찾는다.

## 검증

최종 원본 **152/152 PASS /6 suites**, page errors0. static38 / comparison15 / receiver12 / model25 / native20 / regression42. 과거 E355와 중간 후보는 합산하지 않는다. 공통 RF의 PERI2만 창에서49.1%, SHORT12.5km에서49.36%, LONG3km에서49.9%, LONG중형50km에서49.64%의 확정률을 기록했다. 후자3개는 각5천 창이며 모두 단일 완전 창 기준이다. 진단 수식과 실제 RF의 샘플링 차이를 숨기지 않는다.

앵커의 신규 허위 접촉 기대값은1/h다. 모드별8시간 수치 가속에서는 LONG9 /SHORT11 /PERI6회(1.125/1.375/0.750회/h)로 E와 같은 결과를 보였다. 전체 월드8시간 실시간 플레이는 아니다. 수신기 단위 시험은 클러터 이득의 한 번 적용, 신호·열잡음 무중복, raw Pfa 보존을 확인했다. 실제 두 기의 SHORT/PERI·Hawklink를1/8/16/64×동일1152 fixed ticks에서 비교했다.

DDG-119/CG-52의 대기·8Kh-32 AUTO·피격6조건에서 기존 물리·피해·배치·RNG·관측·포트 결과가 E와 일치한다. native DEBUG 모달·읽기 전용도 확인했다. 120초 준비·기체 모델·렌더·IFF·무장 권한은 기존 함수 동일성으로 보존하며 과거 검사 수를 다시 세지 않는다. 실제 휴대폰/하드웨어 FPS는 측정하지 않았다.

## 전달

이전 E 네 파일을 `archive/v48/WIP_HELI_E/`에 동일 bytes/blob으로 보존한다. stable v48와 과거 A–F 소스·자산·증거도 그대로다. 원본 전체를 작업 브랜치에 올리고 독립 GitHub blob readback으로 확인한다. Actions는 실행하지 않으며 수동 workflow만 준비한다. main/이전 브랜치 병합·새 PR 생성은 하지 않는다.
