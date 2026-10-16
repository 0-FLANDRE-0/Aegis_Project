# HELI_E — AN/APS-153(V) 수상 탐색

[실행 HTML](../../../Aegis_SIM_v48_WIP_HELI_E.html)은 HELI_D `e64f7af233897aa01e0bb7541c7cce88101b2638` 위 `helicopter-radar-e` 작업이다. [구현 전 대조·사용자 결정](CONFLICTS.md), [최종 검증](evidence/verification-summary.json)을 따른다. 소스 디렉터리 F는 기존 A–E를 보존하기 위한 다음 소스 묶음이며 제품 버전은 HELI_E다.

AIR에서 H1/H2를 선택한 뒤 **STBY/LONG/SHORT/PERI**를 조작한다. ISAR/ARPDD는 예약만 하며 표시·선택하지 않는다. 기본 STBY, IFF ON이다. 레이더 모드는 링크 단절이나 모함 레이더 EMCON과 무관하게 기체에서 바꿀 수 있다. 새 모드 한 회전 동안 전환 상태이며 데이터가 없다. 기존 출격·대기 취소/경로/UNDO/함선 추종/고도와 CAMERA 추적을 유지한다.

| 모드 | 회전 | 계기 사거리 | 거리분해능 | 이진 확정 |
|---|---:|---:|---:|---:|
| LONG | 12rpm / 5초 | 463m–296km | 45m | 2-of-3 |
| SHORT | 108rpm / 0.556초 | 91m–29.6km | 15m | 2-of-3 |
| PERI | 108rpm / 0.556초 | 3.7–59km | 3m | 4-of-9 |

위 수치와 아래 수치는 모두 **SIM_TUNED**다. APS-153의 실제 공개 성능 수치로 주장하지 않는다. 레이더 원리를 사용하는 시뮬레이션이며 파형·송신출력·CFAR training window·실제 해면 통계 전체를 복제하지 않는다. 출처 구분은 `model.js`의 `APS_REFS_F`, `APS_SPEC_F`, 모드별 references와 성능표에 있다. DTIC 원본 PDF를 이번 세션에서 내려받지 못했으며 서지와 2차 인용을 확인한 범위만 기록한다. [제조사 APS-153 브로슈어](https://www.ttm.com/sites/default/files/documents/TTM-00169%20AN%20APS-153(V)%20Brochure.pdf)는 모드 존재를 뒷받침하며 이 숫자 표의 출처가 아니다.

## 계산과 정보 경계

공통 `shipboardRadarEchoFieldWip13B13`에서 물리 반사·전파·해면 셀·기상을 합성한다. 수상 탐색은 X밴드 가정, R⁻⁴ 레이더 방정식, Gaussian 방위2.1°, 고각8°/아래 csc²와40° 직하 사각, ±30° 안정화 및 자동 틸트를 사용한다. 108rpm에서 빔을 놓치지 않도록 한 fixed tick의 빔 통과 구간을 적분한다. 기존 peak-gain 우회는 제거했다. 기체별 private RNG와 fixed60Hz가 소유하며 렌더는 시뮬에 쓰지 않는다.

PERI는 **단일 주사 검출 → 이진4-of-9 하나**다. 9회 에너지 적분은 없다. LONG의 긴 단일 주사 체류시간 이득과 조정된 processing efficiency는 같은 회전을 다시 적분하는 항목이 아니다. 오차는 SNR 기반 거리/방위 σ, 자체 항법 잡음3m와 SI3×3 공분산을 사용한다. 해면 셀 면적·그레이징각·해상상태는 clutter를 바꾸며 기존 별도 scalar 해면 감쇠는 제거했다. 이상적인 평균 배경 정규화 CFAR와 exponential-power/Swerling-I 근사를 사용한다.

RF 이후에는 익명 거리·방위·오차·측정 외형만 사용한다. 같은 거리분해능 셀과 방위 빔 안의 측정은 가중 중심/확대된 외형·공분산으로 병합한다. 접촉 연관은 기하학적 게이트뿐이며 표적truth ID를 사용하지 않는다. 각 완성된 주사 창에서 miss도 포함해 판정한다. 마지막 주사를 놓쳐도4회 이상이면 확정한다. 이동하는 헬기의 측정 게이트 좌표 기준은 매 회전 갱신한다. formal 접촉200, bounded 후보40,000, 회전별 만료와 공간 인덱스를 사용한다.

CFAR noise-tail은 RF 합성 안에서 익명 echo로 생성한다. 배경 반사와 동일하게 잡음 측정·기하 게이트·M-of-N을 통과해야 한다. downstream에 허위/진짜 표지를 주지 않는다. 넓은 연관 게이트에서 여러 독립 cell이 합쳐지는 효과를 역산에 포함한다. 성능표의 시간당 오경보는 신규 확정 birth의 희박사건 기대값이며 짧은 세션의 고정 개수가 아니다.

앵커는 고도152m / 높이1m·RCS1m² / 35km / Hs0.9m, PERI의 **임의의 완전한9주사 창 한 개**다. `BinomialTail(9,4,p)=.5`에서 단일 주사 목표 `p=0.3930848328`을 구한다. CFAR 임계값과 clutter 면적·고각·sub-tick 빔 위상 이득을 포함해 K를 역산한다. 현재 정규화 K≈4.5870×10¹⁹, `snrReferenceRangeKm≈82.29668`이며 실제 유효 사거리나 송신 전력이 아니다. 공통 RF와 실제 접촉 처리의 분리된5,000창 시험에서 확정률 약50%를 확인한다. 시뮬 상태·전투 RNG·트랙·포트는 이 진단으로 변하지 않는다.

Hawklink는 확인된 최신 측정만 기존 엄격한 스키마로 모함에 보낸다. 위치/공분산/도메인 증거/실제 측정 시각만 보내며 내부 contact ID·외형·truth를 싣지 않는다. H1/H2 각각32보고/초와 burst24, 총64보고/초, queue 예약8, batch 순환 선택으로64개 포트를 보호한다. 초과/단절 보고는 버리고 누적·재전송하지 않는다. 레이더EMCON과 링크 독립, LOS/최대거리/모함 장비 판정, 원격만으로 무장발사 금지, Link16 확대 금지는 기존 정책 그대로다.

실제 수평선은 해당 반사체/함정 프로파일 높이를 사용하고 없으면30m다. AIR·지도·3D의 수평선은 **표적 기준높이30m인 기하상한**이다. 확정 탐지나 무장 사거리가 아니며 SNR은 별도다. 계기 사거리는 slant이며 원은 수평거리로 투영한다. 헬기 자체 RCS는 관측 방위에 따라 정면3m²→측면8m²로 보간하며 RF·CIWS가 각 관측 위치에서 평가한다.

## 표시와 진단

AIR는 현재 모드/전환 남은 시간, 계기 거리, 기준 수평선과 기하상한 제한 요인을 표시한다. 지도는 선택 기체의 계기 원 실선·수평선 점선·PERI 최소거리 원이다. 3D CONTROLS → SENSORS → **AN/APS-153**은 같은 원들, 직하 사각,2.1° 쐐기, 모드별 잔상과 해면/고각 띠를 표시한다. STBY는 숨기고 전환 중에는 흐린 링만 보인다. H1/H2 색과 authoritative azimuth를 유지한다. geometry/material을 재사용하고 reset/disposal을 검증한다.

DEBUG → **HELO 레이더 성능표**에서 복사 가능한 표를 연다. 앵커·상수·reference 전체와 3표적×3모드×6고도×3해상상태를 출력한다. Pd50/제한 요인/직하 사각/확정 후 오경보 기대값을 표시한다. 순수 진단 계산이며 live RNG·수신 상태를 변경하지 않는다. 콘솔은 `window.__HELO__.snapshot()`, `window.__APS153__.snapshot()`, `performanceTable()`, `performance()`를 사용한다. detached `nativeProbe()`와 `anchorExperiment()`는 전투 트랙을 주입하지 않는다.

E1 저장은 radarMode와 기존 호환 radarOn을 일관되게 저장한다. D1의false→STBY, true→LONG이며 기존 비행 필드는 보존한다. 구형 A/B/C migration은 이어 유지한다. 잘못된 설정·추가 transient·불일치 bool/mode는 쓰기 전에 거부한다. scan/누적/접촉/RNG/링크 queue는 저장하지 않는다.

## 재현과 한계

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
pip install -r docs/helicopter/F/requirements.txt
python -m playwright install chromium
python docs/helicopter/F/build.py archive/v48/WIP_HELI_D/Aegis_SIM_v48_WIP_HELI_D.html /tmp/Aegis_SIM_v48_WIP_HELI_E.html
python docs/helicopter/F/run_suite.py static Aegis_SIM_v48_WIP_HELI_E.html /tmp/heli-e/static
# suite: model, transport, native, iff, policy, regression, ui, visual
python docs/helicopter/F/run_suite.py native Aegis_SIM_v48_WIP_HELI_E.html /tmp/heli-e/native
APS_TEST_HOURS=8 python docs/helicopter/F/run_suite.py model Aegis_SIM_v48_WIP_HELI_E.html /tmp/heli-e/model --false
```

[최종 증거](evidence/verification-summary.json)는 같은 최종 HTML에 대한 native/static/UI/3D/IFF/Hawklink/발사 권한/양함종 전투/1·8·16·64× 검사를 묶는다. model/transport는 이 소스의 detached 계산/포트 시험이며 static의 정확 재빌드로 제품과 결속한다. 오경보 endurance는 독립 receiver-noise 필드와 실제 측정·연관·확정 코드를 사용한 가속 수치 시험이다. 전체 월드를8시간 실시간 플레이한 시험, 실제 하드웨어/휴대폰 FPS 또는 실장비 검증으로 표현하지 않는다. 큰 회귀 JSON은 lossless gzip으로 보존한다.

[공유 SH-60 자산과 CC BY4.0](../A/ATTRIBUTION.md)을 그대로 사용한다. HTML 증가는 약13KB, 새 모델/텍스처는 없다. HELI_D 네 파일은 같은 bytes/blob으로 archive한다. full original을 `helicopter-radar-e`에 직접 올리고 독립 GitHub blob readback으로 확인한다. Actions 사용 불가 조건을 유지해 수동 workflow만 준비하며 dispatch/main·선행 branch 병합/새 PR 생성은 하지 않는다. 다음 단계는 헬기 센서 기반 OTH 표적지시/공유 정책을 별도 결정하는 것이다. 실제 피격·격추·무장·연료·회수·FLIR/ISAR/ARPDD/ESM/재밍/공중탐색은 이번 범위에 추가하지 않았다.
