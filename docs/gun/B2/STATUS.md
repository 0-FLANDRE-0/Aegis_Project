# GUN_B2 상태

**Phase 1 구현·측정 완료 · gun-b2 PR 검토용**

현재 관측 기반 발사 정합, 독립 산포, AIR 대칭 포인팅, 5인치 전용 신호 누적 신관·파편 띠를 승인 순서 1→5로 구현했다. OFF 기준은 AIR_ORIGIN_A(4c519…)다.

필수 자연 탐지 행렬 960회, 단발 거리 측정 1440시도/1400발, 16,459m 최종 앵커 400발을 완료했다. 상세 검수·원시 실패·재사용 범위는 [최종 보고](phase1/REPORT.md)에 있다. 기존 승인 5건 외 기대값·허용치 갱신은 없다.

**검토 사항:** 기존 같은 60회 대비 HP 악화 29회, 새 ON 동작 차이 24항목, 근거리 MFF 효과가 낮은 구간, 외측 .05 하강점을 찾지 못한 ≥9km 검열 링 제안이다. 전체 전투 결과 개선이나 모든 원시 검사의 통과를 주장하지 않는다. 피해 RNG/Pk 계수를 맞추지 않았다. main 병합/release/tag는 하지 않는다.

- [보고서](phase1/REPORT.md) · [변경 결과 분류](phase1/DIFFERENCES.md)
- [수치·계산 방식](phase1/PARAMETERS.md) · [시험 규약](phase1/PROTOCOL.md)
- [체크섬](phase1/CHECKSUMS.sha256) · [패키지 영수증](phase1/PACKAGE_RECEIPT.json)
- [기존 원점 복구 후 재진단/착수 보고](PHASE1_START.md) — 당시 상태를 그대로 보존
- [과거 Phase0](PHASE0.md) — 현재 제품 상태가 아님

원격 readback 영수증은 산출물 push 후 후속 커밋의 phase1/REMOTE_READBACK.json에 남긴다.
