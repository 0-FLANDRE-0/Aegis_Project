# AEGIS PLAN STATUS v48_WIP_PERF_B

## 현재 기준

- 최적화2단계 완료. PERF_A final `4b42aacd4271ce790b47b981b9a58dc960e5d5c5` 위 `performance-b`.
- HTML `Aegis_SIM_v48_WIP_PERF_B.html`, 15,706,015bytes, SHA-256 `292622e556192d3c954917437709a0f1e4489e1636cd6263a4b7737832013faf`. decoded main `6577a3e216f0bec2ae7aeefb7e79524c33ee52c564de94dfb3763ad3cb24a977`.
- records0~12/모델 assets·stablev48 보존, records13만 변경. 직전 PERF_A4원본은 archive/v48/WIP_PERF_A/에 samebytes/blob 보존.

## 적용 내용

1. 동일 synchronous planner ctx 안에서 관측 threat/delay 예측과 SPG 기하 점수를 공유한다. NEZ에 필요 없는 track metadata 복사를 생략한다. 다음 build에는 새 ctx로 현재 관측/자세/피해/사통을 읽고, 예약 충돌은 매번 검사한다.
2. owner별 body frame을 모든 heading/heel/trim/draft/origin x/y/z가 Object.is exact일 때만 공유한다. 같은 tick의 자세 변경을 즉시 반영하며 canonical constructor/invalid 예외를 유지한다.

캐시는 derived only·snapshot 비저장이다. 실제 발사의 보호/권한/HOLD/EMCON/손상/capability·예비탄·FCS 재검사는 유지한다. fixed60/120/20Hz·sensor/CMS·AI/RNG·native flight/collision/damage·EW·CG Phalanx-only·DDG장비·Harpoon INS/ARH/DL0·조작과 PERF_A 최적화를 유지한다. 상세 계약은 docs/performance/B/README.md다.

## 검증

- 최종 원본 직접 1534/1534PASS,30suites/15captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0.
- full packing/rebuild/scope, 두 native planner96제어사례·ctx 수명/예약/현재 관측/자세/피해·기본 반환 계약·frame exact inputs/core selftest.
- strict CG/DDG6조건 상태/RNG exact, 기존26 H4A browser suites와 PERF_A texture lifecycle 새 원본 직접 재검사, 세 owner1/8/16/64배속exact·native 방어/피해/저장/UI 회귀.
- 별도 직렬 CPU16쌍 상태·RNG·entity exact. 표/반복/조건/한계는 docs/performance/B/PERFORMANCE.md 및 evidence/benchmark.json, script/report/capture SHA/집계는 evidence/verification-summary.json이 권위다.

## 업로드·후속

사용자 full original 직접 업로드/readback 승인으로 새 branch에 원본/support를 반영한다. 독립 remote tree/blob/raw bytes 확인은 docs/performance/B/evidence/remote-publication.json이 code commit을 pin하고 자기 자신을 checksum에서 제외한다. 이후 final-head도 별도 확인한다. Actions 계정 제한으로 manual workflow만 준비하며 dispatch/CI PASS 주장은 없다. main/이전PR 병합·새PR 생성은 실행하지 않는다.

다음은 SPY 관측 연관 최적화, 피격 envelope 지연, 실제 가시3D/효과와 최종 재측정이다. 그 뒤 헬기/초수평선 탐지 → RGM-109E Block Va를 유지한다. 대표 조건 밖 보편적 요격률·모든 오격 방지·하드웨어 FPS 보장은 포함하지 않는다.
