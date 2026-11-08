# 백로그

## U3에서 완료

- **일반 추적 covariance basket 보정 — 완료**
  - 제거 대상은 기존 4 km 상한뿐이며, pre-U3의 250 m 하한은 `LEGACY_HARPOON_NATIVE_250M_FLOOR`로 복구했다.
  - 실제 레이더 트랙 발사에서 250 m와 4,800 m가 cueHandoff·시커·보호 판정까지 전달되고, 실제 stale 코스팅 트랙이 상위 게이트에서 거부됨을 확인했다.
- **수동 RF 방사원 선택을 우도 기준으로 바꾸기 — 완료**
  - 지금은 게이트 거리(d²)가 가장 작은 방사원을 고른다. 이러면 σ가 큰(흐릿한) S대역 SPY가 오히려 유리해진다.
  - 근거: CUE_A-1에서 Kh-35U 방위 오차가 ALL_ON(SPY 선택) 1.19°, SPY_OFF(SPQ-9B 선택) 0.39°
  - 적용: 기존 gate 뒤 `d² + ln|S|` 최소, 관측값 동점 순서. truth/RNG 사용 0
- **ENV_D 무결성 메타데이터는 해당 단계 안에서 갱신한다.** 광역 회귀 뒤 제품을 고치는 일이 C와 CUE_A-1에서 두 번 반복됐다.

## U3 이후

- **EMITTER_A — 완료/병합**: `electronicPhysicalEmittersF`의 DDG/CG 함종별 하드코딩을 ShipProfile 선언형 장비 등록과 공통 ShipRuntime 어댑터로 이전했다. SOV는 기존 메타데이터만 비활성 등록했다. PR #73은 사용자 결정으로 `main@3dbe3b84`에 병합됐으며 release/tag는 없다.
- **EMCON_B — A–E + PR #74 2차 종료 보정 구현·제한 검증 완료**: V2 global hard-off, 범주·장비 통제, exact emitter/own·NPC sensor/ECM gate, profile UI, network/save lifecycle과 기존 lock 14건을 완료했다. 통신 EMCON은 별도 정책으로 유지한다.
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
- **통신 EMCON**: radar master/category silence와 별도다. Hawklink/Link 송신 통제를 새 정책으로 설계한다.
- **FIRE_CONTROL registry**: 현재 활성 SPG-62 장비가 없어 EMCON_B는 계약/비활성 UI만 제공한다. 물리 등록·RF·ESM 연계는 별도 단계가 필요하다.
- **광역 Chromium runner 메모리 부채**: APS-153/ISAR/legacy EMCON/Harpoon의 큰 기존 진단 modal·journal 경로가 제한 환경에서 assertion 전 `Target crashed`를 낸다. 제품 판정과 분리해 runner를 경량화한다.
- **SOV/UI 기존 fixture 부채**: EMITTER_A와 EMCON_B 양쪽에서 SOV deployment의 `selectedSOV/creditVisible`, UI의 `nativeHold/feedReject` 및 832.CG.PIP covered-point가 동일하게 재현된다.

## 기존 회귀 부채 (면제하지 않음)

- `#lockBtn` 14건은 EMCON_B에서 실제 Chromium 14/14로 해소했다. MAP_E가 visible node를 의도적으로 퇴역시킨 selector 부채였으며 제품 native listener는 유지됐다.
- `CIWS_SEED_419025_FAIL`
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
- Actions 고정 WIP12D `ciws-b1-closure` 배속 결정성: 같은 360 fixed step에서 1x 42발, 8x/16x 47발. U3 제품 경로는 아니며 기대값/허용오차를 바꾸지 않았다.
- Actions PR merge-ref checkout 시간 제한: `residual-overpenetration-wip12d-contract` 5분, `ciws-b3-damage` 12분에서 테스트 진입 전 취소. Playwright 1.55 설치 호환 문제와는 별개다.
