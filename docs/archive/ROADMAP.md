# 로드맵 (현재 합의)

1. **U3 하푼** — 완료, PR #72 main 병합
   - 하푼 cue 계산을 공통 CUE_A 필터로 바꾼다 (2026-11-06 결정)
   - 하푼 HOJ 추가: ECCM. 기존 ASM HOJ 훅을 재사용하고 하푼 프로필을 둔다
   - 하푼 미사일 쪽 중기 수동 RF는 넣지 않는다. 공개 자료상 수동 RF는 발사 함정 ESM 쪽이다
   - 함께 넣을 것: 수동 RF 우도 선택 (`BACKLOG.md`)
2. **EMITTER_A** — 완료, PR #73 사용자 병합 (`main@3dbe3b84`)
   - ShipProfile이 장비별 방사원을 데이터로 선언한다: 범주(AIR_SEARCH/SURFACE_SEARCH/NAV/FIRE_CONTROL/ECM), 대역, 출력, 안테나 형식·회전, 장착점, 손상 모듈, 의존 시스템
   - `electronicPhysicalEmittersF`의 SPY/SPQ/NAV 하드코딩을 프로필 기반으로 바꾼다. 출력 계약은 유지한다(DDG·CG 분기 커버리지 동등성)
   - 소브레멘니 방사원은 별도 커밋으로 추가한다
   - 방사 상태는 ShipRuntime이 소유한다. 소비자(수동 RF·ESM·HOJ·함 레이더)는 공통 API로 조회한다. NPC AI EMCON도 같은 구조로 간다
3. **EMCON_B** — 구현·검증 완료, PR #74 사용자 검토/병합 결정 대기
   - 범주 정책·장비 override·실제 방출/own·NPC 센서/ECM gate·profile UI·network/save lifecycle 완료
   - FIRE_CONTROL은 활성 SPG-62 등록이 없어 계약/비활성 UI까지만 완료
   - 통신 EMCON은 별도 후속 정책으로 남김
4. **U4** SARH 쌍정 어댑터 → **U5** RAM 수동 RF/IR 어댑터 → **U6** 상태기계·연관 공통화
   - RAM 메모: 자함용·타함용 복사본이 두 개 있다. 방사 세기가 상대 시커 추적 품질에 따라 바뀌는 이상한 점이 있다.
5. **TRACK-D**(링크·소비자 통합) → **HP 지표** → **통합 기준선** → **교전·방어 OODA**

- 2~3번과 4번 사이 순서는 상황 보고 사용자와 다시 정한다.
- **적 항공기 재제작**은 시점 미정이다. 설계 메모는 `DESIGN_NOTES.md`에 있다.
