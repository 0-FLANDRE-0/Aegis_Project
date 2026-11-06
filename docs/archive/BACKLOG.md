# 백로그

## U3에서 완료

- **수동 RF 방사원 선택을 우도 기준으로 바꾸기 — 완료**
  - 지금은 게이트 거리(d²)가 가장 작은 방사원을 고른다. 이러면 σ가 큰(흐릿한) S대역 SPY가 오히려 유리해진다.
  - 근거: CUE_A-1에서 Kh-35U 방위 오차가 ALL_ON(SPY 선택) 1.19°, SPY_OFF(SPQ-9B 선택) 0.39°
  - 적용: 기존 gate 뒤 `d² + ln|S|` 최소, 관측값 동점 순서. truth/RNG 사용 0
- **ENV_D 무결성 메타데이터는 해당 단계 안에서 갱신한다.** 광역 회귀 뒤 제품을 고치는 일이 C와 CUE_A-1에서 두 번 반복됐다.

## U3 이후

- **EMITTER_A**: `electronicPhysicalEmittersF`의 함종별 하드코딩을 ShipProfile 선언형 장비 등록으로 이전. U3에서는 범위 밖으로 보존했다.
- **경로점 prior 불확실성**: U3는 기존 4 km `ROUTE_PLAN_PRIOR`를 유지했다. 관측으로 위장하지 않는 신규 계획 불확실성 모델은 별도 설계한다.
- **U3 paired raw 4건**: DDG/CG raid의 combat RNG/observer exact-state. D ACTIVE 정책 변화로 원인 분리됐으나 원본 expectation은 갱신하지 않았다.

## 별도 조사

- **Kh-32 60 km 명중 0**: C·CUE_A-1 모든 단계에서 0/20이다. 보정 전에도 함정을 17~25 km 지나쳤다. 시나리오나 최소 사거리 문제로 의심된다.

## 적 항공기 재제작 때 (`DESIGN_NOTES.md` 참고)

- 발사 cue에 공분산과 정보 시각 넘기기
- 바구니 하한 `max(1200 m, 0.12R)` 재검토
- 발사 전 트랙 나이 미반영, 발사 측 트랙 속도 배관

## 보류

- ASM 부엽 바닥 0.08 값 자체 검토 (C에서 값 유지, 제안만 허용)
- `CONFIRMED_ONLY` 성능 수치는 UNVERIFIED (MAX_THREAT만 시험하기로 결정)

## 기존 회귀 부채 (면제하지 않음)

- `#lockBtn` 14건 미실행 (INCOMPLETE)
- `CIWS_SEED_419025_FAIL`
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
