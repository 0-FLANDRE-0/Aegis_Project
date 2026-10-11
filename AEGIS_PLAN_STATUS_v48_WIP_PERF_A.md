# AEGIS PLAN STATUS v48_WIP_PERF_A

## 현재 기준

- 최적화1단계 완료. H4A final `b97925cb5fb27d4dad26d62db78520641ee70857` 위 `performance-a`.
- HTML `Aegis_SIM_v48_WIP_PERF_A.html`, 15,704,207bytes, SHA-256 `13a9de64d918efd053ead648cb312a691688691ccbfa72fe50fefd72054ae6ad`.
- decoded main SHA-256 `c43d9287e066bd56132d57d3a2cb2b4b37bee05e008f59432a61f82ae41d64e1`. records0~12/모델 assets 및 stablev48 유지, records13만 변경.
- 직전 H4A HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_H4A/`에 같은 bytes/blob으로 보존한다.

## 적용 내용

1. 불변 hitbox의 system→고유 module name 색인. owner별 현재 손상값·자함 기존 경로·가변 geometry fallback을 유지한다.
2. EW 지원 대역 검사 선행으로 불필요한 pod 위치/손상/사각 계산 제거. 지원 대역의 결과와 기존 정책을 유지한다.
3. Kh-32 동일 도색 texture/canvas 공유. idempotent lease·마지막 참조 disposal·새 생성·import/reset·도감 수명 확인.

캐시는 snapshot에 저장하지 않는다. fixed60/120/20Hz·RNG, 센서/RF/CMS·AI·발사 권한·CG Phalanx-only·DDG장비, Harpoon INS/ARH/DL0, 충돌/관통/피해·EW·조작을 유지한다. 지원 계약은 docs/performance/A/README.md를 따른다.

## 최종 원본 직접 검증

- 1483/1483PASS,29suites/15captures, 과거·실패한 draft 검사 합산0. page/core/runtime/presentation 오류0.
- static packing/rebuild/scope, 두 함종 새 selftest,72 EW 동등성 조건, native64모델 픽셀/geometry와 전체 texture lifecycle을 확인했다.
- CG/DDG6조건 strict 상태/RNG exact, 세 owner1/8/16/64 결정성, 기존26 H4A browser suites를 새 원본으로 직접 실행했다.
- 별도 직렬 CPU 비교16쌍의 관측/저장/무장/방어/EW·entity/RNG exact. 표와 반복·조건·한계는 docs/performance/A/PERFORMANCE.md 및 evidence/benchmark.json을 따른다.
- 최종 원본·script/report/capture SHA와 집계는 docs/performance/A/evidence/verification-summary.json이 권위다. 초기 baseline 경로 오류는 같은 bytes의 archive 경로로 재실행했고 성공한 최종 보고만 합산했다.

## 업로드와 남은 단계

사용자 직접 원본 upload/readback 승인에 따라 branch에 전체 원본과 support를 반영한다. 독립 readback은 docs/performance/A/evidence/remote-publication.json이 권위이며 자기 자신을 checksum에서 제외한다. Actions 사용 불가로 수동 workflow만 준비하며 CI PASS를 주장하지 않는다. main/H4A/선행PR 병합과 새PR 생성은 실행하지 않는다.

다음 최적화는 교전 planner/SPG-62 중복 계산, SPY 연관, 피격 envelope 지연, 실제 가시 탄체/효과의 render 비용 순으로 검토한다. 큰 기능 순서는 최적화 이후 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va를 유지한다. 보편적 요격률·모든 오격 방지·하드웨어 FPS 보장은 이 대표 조건 검증에 포함하지 않는다.
