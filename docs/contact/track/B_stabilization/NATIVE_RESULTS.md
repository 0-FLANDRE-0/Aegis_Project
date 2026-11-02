# TRACK-B 안정화: 단위·native 계약 검증

최종 후보의 이번 범위 검증은 **PASS**다. 전체 RF·전투 회귀의 승인이나 기존 strict 차이의 승인을 의미하지 않는다. 브라우저 lane2는 반환했다.

| 대상 | 결과 | 근거 |
|---|---:|---|
| 신규 정책 단위시험 | 39/39 | 실제 후보 solver + 원래 native Hungarian |
| 기존 B47, 원본 기대값 그대로 | **46/47, strict FAIL1 보존** |13×13 포화 정책 교체 차이 |
| 기존 대표 native5그룹 | 19/19 | 원본 helper/입력/기대값 변경0 |
| 신규 native5그룹, ACTIVE | 23/23, OFF·ON 모두 | 실제 surface/observer assign·update 경로 |
| 추가 실제 S·차원·epoch·callback5그룹 | 18/18, OFF·ON 모두 | 실제 native inverse 입력 행렬 검증 |

최종 source/제품:

- `association.js`: `ec66a28a8bb92888228a45a6a626007f288c440b3054e2e203730bbe9e8e4c71`
- ACTIVE: `87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18`
- SHADOW: `75b845f5b353c576ea191a2508578edcb29b4110a69cbf97e532df6562747d4f`
- 원래 B ACTIVE: `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`

기존 B47의 남은 실패는 `bounded.connectedThirteenByThirteenHeld`다. 이전 기대값은 component12 초과면 모두 HOLD였고, 후보는 유일한13개 diagonal을 원래 전역 최적해와 대안 비용 하한으로 인증해 배정한다. 원래 실패·이전 기대값을 그대로 보존했고 이 lane은 값을 갱신하거나 자동 승인하지 않았다. 초기 a304… 후보의 별도 SHADOW API 실패는 root의 API 보존 수정 후 ec66…에서 회복됐다. 두 source epoch의 원시 결과가 모두 남아 있다.

SHADOW는 새 ACTIVE 양성 기대4건이 실제 적용되지 않아 **19/23, raw FAIL4**다. 이 결과를 PASS로 바꾸지 않았다. 별도 control에서는 원래 B ACTIVE와 기존·신규 각 fixture의 filter/physical/private-RNG 상태 및 전체 마지막 상태가 정확히 같았고, own surface와 NPC에서 `SAME_NIS_WINNER_INNOVATION_DENSITY_CERTIFIED` 제안 로그가 실제 생성됐다. ACTIVE는 같은 양성에서 원래 NIS winner만 갱신해23/23을 통과했다.

음성 시험에서는 동일 신호·동일 S, ID/입력 순서 변경, NIS와 우도 충돌, 누락·다른 차원/epoch는 HOLD를 유지했다. 관측되지 않은 surface8m 고도 prior는2D 위치 모델의 관측으로 늘리지 않았다. 실제 full surfaceRadarNis callback에 유효 Doppler가 있을 때2D 인증을 사용하지 않고 HOLD했다. 누락 receiver 수직속도를0으로 만들지 않았고 지연 보고는 receipt 시각으로 freshen하지 않았다. 원래 age² 공분산 팽창과 측정 R/owned P를 보존했다.

추가 검증은 실제 NIS 한 번의 `_matInv` 입력 S를 pass-through로 복사하고 원래 함수를 `finally`에서 복원했다. 별도의 센서/NIS/연관 모델은 만들지 않았다. 이 행렬에 대한 독립 행렬 소거 log determinant와 후보 값을 비교한 최대 차이는 AIR4 **1.78e-15**, surface-position2 **0**, reported-Cartesian3 **0**다. Cartesian3은 보고된 위치3차원이며 물리 RF가3차원을 관측했다는 뜻이 아니다.

진단 OFF/ON에서 실제 native 결과, fixture별 전체 passive filter/P·physical·private/global RNG hash, 마지막 상태가 동일했다. 반복 snapshot과 mode 변경 시도, actual ENV status, 입력/prior 불변 검사도 통과했다. 실제 제품 helper와 기존 native prediction/Jacobian/noise-floor 경로를 사용했다.

API 출력의 raw/truth alias 참조는0건이다. `trackBPairCopyB`는 pair·sanity·evidence 스칼라 whitelist만 새 객체로 복사하고, evidence helper는 valid/dimension/epoch/logDet 같은 스칼라만 반환한다. snapshot도 새 스칼라 레코드 사본이다. truth canary·unknown field·alias·frozen input·결정성 시험과 source whitelist 감사를 별도 보존했다. 테스트용 AFTER_ACTION 상태 문자열·캡처 행렬은 검사 자료이며 association이나 게임에 되먹이지 않는다.

`evidence/native-shadow/`의57f3… 결과는 guard 수정 전 historical 자료다. 최종 근거는 `evidence/native-shadow-guard/`와 `evidence/native-active-guard/`이며 source별 raw 결과를 교체하거나 덮어쓰지 않았다. 최종3페이지씩 실행 시간은 SHADOW 46.18s, ACTIVE 48.50s다.

이 lane은 기존 B90 전체나 자연 RF/무장/전투 시험을 실행한 것이 아니다. 원래 B47/native90/cohort14 파일·기대값을 변경하지 않았고, 자연전투·D1·paired 회귀는 다른 lane의 최종 결과를 기다린다. 합계에 기존 도메인420의 새 통과 수를 더하지 않는다.

기계 판독용 요약: `NATIVE_SUMMARY.json`. 원시 자료와 helper/runner SHA는 각 evidence 디렉터리의 `PROVENANCE.json`과 `*-raw-before-aux.json.gz`에 보존했다.
