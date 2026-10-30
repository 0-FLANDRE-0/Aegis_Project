# 재현과 증거 읽는 법

작업 기준은 `fuze-zem-a@7d863699c596c30b0df5e34734f17fe11cadc21e`의 DZT다. 새 후보는 `launch-handoff-a`, HTML SHA `e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7`. 이전 HTML은 `archive/v48/WIP_FUZE_ZEM_A`에 byte 동일하게 보존했다. REPORT ZIP은 재현 소스/증거 묶음이며 대용량 기준 HTML들은 저장소 또는 각 실행 ZIP에서 별도로 받는다.

Node24, Python3.12, Acorn8.19, Playwright/Chromium, matplotlib를 사용했다. Acorn은 저장소 `docs/performance/F/package-lock.json`으로 설치한다. `NODE_PATH`는 그 `node_modules` 디렉터리다. Chromium은 연결된 환경의 소프트웨어 WebGL을 사용했다. 실제 폰 GPU/FPS 측정은 아니다.

저장소 루트에서 다음을 실행한다. 빌드는 원본을 덮어쓰지 않고 `/tmp/aegis-launch-handoff-a/builds/contract-2`에 새 HTML을 만든다. 각 재실행은 저장된 결과 파일을 다시 쓰므로, 원본 증거는 별도 checkout에 보존한 뒤 재현한다.

```sh
export NODE_PATH="$PWD/docs/performance/F/node_modules"
node docs/missile/launch-handoff/A/build.cjs
node docs/missile/launch-handoff/A/test_static.cjs
node docs/missile/launch-handoff/A/test_gate.cjs
python docs/missile/launch-handoff/A/verify_core.py
node docs/missile/launch-handoff/A/reproduce_baseline.cjs
node docs/missile/launch-handoff/A/run_small.cjs
node docs/missile/launch-handoff/A/run_common.cjs
node docs/missile/launch-handoff/A/test_boundary_flights.cjs
node docs/missile/launch-handoff/A/verify_log_immutability.cjs
node docs/missile/launch-handoff/A/probe_pipeline.cjs
node docs/missile/launch-handoff/A/reproduce_reference.cjs
node docs/missile/launch-handoff/A/probe_reference_pk.cjs
node docs/missile/launch-handoff/A/export_fixture.cjs
python docs/missile/launch-handoff/A/verify_equivalence.py
python docs/missile/launch-handoff/A/run_natural.py
python docs/missile/launch-handoff/A/run_release.py
python docs/missile/launch-handoff/A/probe_release_regression.py
python docs/missile/launch-handoff/A/verify_surface.py
python docs/missile/launch-handoff/A/verify_clock.py
python docs/missile/launch-handoff/A/raid_followup.py
python docs/missile/launch-handoff/A/sm6_residual_world.py
python docs/missile/launch-handoff/A/verify_world120.py
```

원래 도메인/UI/WebGL 검사 명령은 `final-evidence/executions.json`에 있다. 테스트 입력과 판정 코드는 원본이며 결과 수집기의6개 실패를 완화하지 않았다. 예:

```sh
python docs/missile/range/A/collect_domain.py docs/missile/launch-handoff/A/final-evidence/domain docs/missile/launch-handoff/A/final-evidence/domain-acceptance.json
```

현재 결과에서 위 수집 명령은 **exit1**이 맞다(414PASS/6FAIL). 검증 총괄도 `releaseApproved:false`를 보존한다. 기대한 실패를 무시하고 PASS로 바꾸는 명령은 없다. 전체 ENV_D 스윕은 실행하지 않는다.

## 자료별 의미

| 위치 | 내용 |
|---|---|
| `final-results/small.json.gz` | 40발 전체 반환값,10Hz 궤적, 전환 전후 detached raw(초기15초60Hz, 이후 선택 샘플) |
| `analysis/transition-detached-ticks.csv.gz` | 같은 고정 tick의 beforeGate/preDynamics/postDynamics. stale gate 제외 |
| `analysis/pipeline-compact.csv.gz` | 8개 집중 사격의 PN/APN/ZEM **현재 호출 여부**와 실제 소비 명령, G 벡터/크기 |
| `final-results/common.json.gz` | 후보별180발, 선결정 입력/시드. 결과의 success=effect, lethal 별도 |
| `final-results/natural.json.gz` | native onboard RF/EKF와 고정 운동 ASM. 함 cue는 fixture가 공급 |
| `final-evidence/release-HANDOFF` | 원래 AIR/nativeRF release300 새 실행. 성공은 원래 native AIR 판정 |
| `final-results/release-regression.json.gz` | 원래 release152/153을 재실행한4발. observer 전후 전체 결과 동일 |
| `final-evidence/observed-HANDOFF` | 자연 함 탐지→LOCK→정식VLS→전체 월드 fixed tick→WebGL, 최종8발 |
| `final-evidence/equivalence.json` | 실제 browser lexical 함수 vs selected private10조건; 함수 hash ledger |
| `final-results/equivalence` | 동등성 전체 반환값, 같은 결과는 한 번 저장하고 양쪽 canonical hash 기록 |
| `final-results/reference-*` | 사용자 pitch-only 원인 분리 실험, **제품 아님** |
| `history/contract-v1` | 내부 superseded 설계/소스. 최종 검수로 합산하지 않음 |
| `final-evidence/invalid-v1-equivalence.json` 및 `history/invalid-*` | 폐기한 계측/메모리 오류, 채택 증거 아님 |

`small` raw의 `pnCommand/apnCommand/zemCommand` 및 corridor는 **마지막 사용 가능 캐시**다. Kappa 틱에서 현재 호출 명령으로 간주하면 안 된다. 현재 호출은 집중 `pipeline`의 `calls.*.calledThisTick`과 timestamp를 사용한다. `beforeGate`도 현재 life와 timestamp가 같을 때만 현재 전이 전 상태다. derived CSV는 이 규칙을 적용했다. `owner`는 동역학 호출 전 초기 샘플에서 실제 활성 제어기 판정이 아니다.

`_v1GAchieved`는 제한 후 요구이고 `actualNormalG`와 다르다. `deliveredG`는 명령 방향 투영으로 부호를 가질 수 있다. 각속도 단위는rad/s, 위치/속도는m/m·s⁻¹, 각도는rad다. 사후 truth 위치는 로그 전용이며 이 진단 값으로 유도를 바꾸지 않는다.

## 실제 코드 출처

`source.cjs`는 명시된 HTML의 asset13 main과 AST scope를 읽는다. `engine.cjs`는 native capsule의 기존 함수 이름마다 선택 HTML의 실제 선언으로 대체하며 D/Z/T 및 인계 helper도 같은 소스에서 가져온다. `sourceFor().keptBoundaries`의 원래 transport/이상 RF/표시 부수효과 boundary는 `docs/envelope/D/diagnostic/boundaries.json`에 있다. 별도 `envNativeAsmDamagePrefixD`는 게임 선언인 척하는 대체 유도가 아니라 원래 진단용 native ASM 피해 prefix이며 게임 함수 해시 집계에서 제외한다.

모든 추출 함수의 live lexical `toString()` 해시를 계측 wrapper 설치 전에 비교했다. E3는 ideal boundary를 양쪽에 같은 방식으로 공급하므로 자연 센서 성능 검증과 혼동하지 않는다. 자연 RF와 전체 월드 검사를 별도로 실행했다.

JSON 저장은 매 tick deep copy다. mutable 참조를 보관하던 잘못된 Pk observer는 폐기하고 숫자인 첫 인자 `pk`와 분리된 primitive label만 수집했다. 난수를 추가 추첨하지 않았고 원래 결과/RNG 불변을 확인했다.

## 판정과 남은 범위

`analysis/SUMMARY.json`, `final-evidence/verification.json`의 `releaseApproved:false`는 의도된 최종 판정이다. 추가 고각1 + 원래240km OFF/ON2의 성공 손실, 원래 상태 비교6개가 남았다. no-full-envelope, no-main-merge, no-release/tag 정책을 유지한다. 새 사거리나 완전 안정판으로 해석하지 않는다.
