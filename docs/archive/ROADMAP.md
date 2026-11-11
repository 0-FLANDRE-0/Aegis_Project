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
3. **EMCON_B** — 완료, PR #74 사용자 병합 (`main@babb4d7f`)
   - V2 `ALL_RADIATION_SILENT`, 함종 중립 consumer→equipment 바인딩, 범주 정책·장비 override·exact 방출/own·NPC 센서/ECM gate·profile UI·network/save lifecycle 완료
   - FIRE_CONTROL은 활성 SPG-62 등록이 없어 계약/비활성 UI까지만 완료
   - 통신 EMCON은 별도 후속 정책으로 남김
4. **U4** — 완료, PR #76 사용자 병합 (`main@82617839`)
   - 커밋 A: SARH 쌍정 어댑터
   - 커밋 B: 기존 U5 RAM 수동 RF/IR 어댑터와 신호 소유권 수정
   - 커밋 C: 기존 U6 공통 연관·상태기계 ACTIVE
   - 별도 U5/U6 브랜치·PR은 만들지 않고 U4에 흡수
5. **TRACK-D / ESM_A** — 완료, PR #75 사용자 병합 (`main@f17d3777`)
   - DDG/CG 공통 익명 raw ESM receiver 계약, 단함 AOA, 협동 AOA/TDOA/FDOA, UI와 제한적 수동 cue를 하나의 PR로 구현
   - SOV Mineral 실제 어댑터·Moskit 표적지시는 후속 소브레멘니 센서·무장 단계
6. **HP_A 지표·권위 분리** — 완료, PR #77 사용자 병합 (`main@78b01165`)
7. **SEEKER_CLOSE_A** — 제품 비변경 진단·마감 완료, PR #78 병합 (`main@d5f43c5a`)
   - 현재 HP_A에서 보정된 종말 원인 19발과 채프/Nulka 배치→관측→gate→선택→최종 회복/유인을 분리 기록
   - 계약 결함 미재현으로 제품 수정·보상 튜닝·광역 재실행 없음
8. **INTEGRATION_BASELINE_A 통합 기준선 고정** — 구현·검증 완료, PR #79 제출 후보
   - 기존 AUTO/H1/H2/H3/H4/Network/CIWS 소유권·호출 그래프 동결
   - owner-addressed 불변 입력 DTO + advisory 명령 DTO + exact `LEGACY_H1` provider
9. **DEFENSE_OODA_A 교전·방어 OODA** — PR #79 병합 후 단일 다음 단계

- SEEKER_CLOSE_A 문서 PR은 병합됐다. INTEGRATION_BASELINE_A도 별도 정리 단계를 만들지 않고 PR #79 병합 뒤 `DEFENSE_OODA_A`로 간다.
- **적 항공기 재제작**은 시점 미정이다. 설계 메모는 `DESIGN_NOTES.md`에 있다.
