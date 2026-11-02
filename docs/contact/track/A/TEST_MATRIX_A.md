# TRACK-A 시험 구분과 단위시험 행렬

`test_contract.cjs`는 **실제 제품에 내장할 `measurement-contract.js` 호환 어댑터**를 Node VM에서 실행한다. 센서 물리, native 연관 결정, 요격·피해 결과를 대신하는 별도 모델은 만들지 않는다. 아래 시험은 fixture-only이며 자연 RF/무장 검수로 집계하지 않는다.

```sh
node docs/contact/track/A/test_contract.cjs docs/contact/track/A/measurement-contract.js --out docs/contact/track/A/evidence/contract-unit.json
```

기본 생산자가 아직 없으면 `BLOCKED`/exit 2, 단언 실패는 `FAIL`/exit 1, 모든 단언 통과일 때만 `PASS`/exit 0이다. 원본 `friendly-contact-a`의 기존 기대값·허용 오차를 수정하지 않는다.

| 구분 | fixture | 검증할 계약 |
|---|---|---|
| AIR | range/az/el/radial | 독립 관측 4차원, 값 보존, receiver 원점과 target truth 분리 |
| SURFACE + Doppler | range/az/radial + z=8 | 독립 3차원, 고도/고각 관측 없음, 8m는 prior |
| BridgeMaster | range/az only | Doppler를 발명하지 않는 2차원 |
| SURFACE prior 없음 | z/prior 없음 | 암묵적으로 8m를 넣지 않음 |
| CIWS | range/az/el + rx/ry/rz | polar 3차원. Cartesian 변환을 추가 3개 독립 관측으로 세지 않음 |
| VISUAL | x/y/z + radialMps=0 placeholder | Cartesian 3차원. placeholder 0을 Doppler 측정으로 승격하지 않음 |
| MH-60R radar | measuredRangeM/measuredAzRad | polar 2차원. XY는 변환 결과, z는 해면 prior |
| ESM | bearing, sigma | 거리/위치 생성 0, injected range/x/y/z 무시 |
| IFF | noisy geometry + reply bit | reply가 관측 근거일 뿐 HOSTILE/발사 권한 생성 없음 |
| ISAR | length/heights/mast/class candidates | 특징 측정 유지, 위치 hit와 독립 확인 증가 0 |
| Hawklink | reported XYZ/covariance/time/sequence | 보고 관측 모델 3차원과 실제 센서 독립 차원 불명 분리 |
| Link 16 TRACK | sender 6-state/P | filter estimate를 독립 6개 원시 관측으로 잘못 표시하지 않음 |
| Link 16 SELF | 자기 항법 보고 | 원격 표적의 직접 관측으로 간주하지 않음 |
| metadata | source/receiver/measuredAt/receivedAt | source 우선순위, 시각 미상 null과 실제 0 구분. packet measuredAt가 receipt-context 시각보다 우선 |
| receiver geometry | sensorXWorld/YWorld/ZM, sensorVx/y/zMps | 실제 측정에 담긴 원점·속도만 SI로 보존, 모함 truth/기본 22m fallback 생성 0 |
| uncertainty | σ, covariance9/36, local variance3 | 제공 σ 보존·미제공 잡음 미상 유지, 크기가 틀린 배열을 절단해 유효 공분산으로 위장하지 않음 |
| provenance | sourceId/sequence | 보고 출처·재전송 식별 자료 보존. actual hit dedup 동작은 A에서 하지 않음 |
| 정보 비누수 | truth/owner/faction/INS canary | 허용 필드만 복사. target truth 및 발사 권한 복사 0 |
| 순수성 | deep-frozen input / repeated call | 입력 mutate 0, returned alias 0, 동일 입력 출력 동일 |
| 결측/비정상 | null/NaN/Infinity/partial | 비유한 값을 실제 0으로 바꾸지 않음, 관측 mask가 결측을 드러냄 |
| trace | OFF/overflow/query | 기본 OFF, ring 상한·overflow 순서, native NIS/gate 결과만 복사, 원본 입력/시계/RNG 쓰기 0, 조회 무변경 |
| trace state privacy | before/after 상태 canary | 상태 스냅샷도 다시 허용 필드만 복사, truthRef·faction 등 유출 0 |

현재 실행한 52개 단언은 `evidence/contract-unit.json`에 결과와 모듈 SHA-256을 기록한다. 단언 개수는 기존 도메인420/UI213/natural WebGL29와 별도이며 합쳐서 기존 회귀 통과 수를 늘리지 않는다. 합성된 네트워크 추정치의 state epoch가 미상의 측정/수신 시각으로 잘못 승격되지 않는 API 검사도 포함한다. 실제 reconcile 호출부의 timestamp 계약은 별도 native ingress fixture로 확인해야 한다.

## 자연 시험과의 분리

다음 항목은 위 단위시험으로 대체할 수 없다. root의 별도 실제 HTML 실행 증거로 검증해야 한다.

- `HELO_HOVER_60S`, `HELO_ROUTE_120S`, `HARPOON_ROUTE_75S`의 native fixed tick 및 신규/동시/최종 파일 수.
- native 후보별 NIS/gate/거부 이유 추적. 단위시험은 NIS를 재계산하거나 native 연관 helper를 호출하지 않는다.
- CIWS 30시드와 419025 source handover·Phalanx/RAM·동일 틱 RNG 타임라인. 기존 결과는 미승인 상태 유지.
- 실제 IFF ON/OFF/만료와 AUTO의 VLS/ESSM/CIWS 재고, own-fire 보호 2문맥.
- Hawklink/Link 16의 실제 재전송 처리·지연·CI0.5·교전 권한과 함정별 독립성.
- trace OFF/ON 동일 게임 상태/RNG, 1·8·16·64배속, observer 1회/tick, 평균/p95 CPU·할당 비용.
- 기존 420건의 세부 집계와 현재 UI213·실제 WebGL8발/29단언. 환경 문제·구형 UI·관측 상태 차이를 PASS로 합산하지 않음.

이번 A 단계에서 B~D의 false merge/ambiguity/lifecycle/identity/network 정책을 수정하지 않는다. 위 단위시험에서 어떤 추가 기능이 필요해 보여도 계수 조정이나 새 권한 정책을 묵시적으로 승인하지 않는다.
