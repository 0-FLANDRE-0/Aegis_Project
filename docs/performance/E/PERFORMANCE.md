# PERF_E 최종 누적·표시 성능

HTML 15,709,083bytes SHA256 `0b59340c2db16d33a6fefe810d8bbf27f96ff189ad8a8166139578b50f2051b5`, main `0f57e35ae2efe55a9ac9c1e5af54650d8eb574e1faf1672e2fef1b84931f617d`. 최종 원본 직접 1735/1735PASS/35suites, page/core/runtime/presentation 오류0. 과거/draft 검사 집계0. shape fixture·실제 GPU readback·native RAF 타이밍은 구별한다.

## 직접 누적 CPU 비교

H4A 최적화 시작 전 원본 → 최종 PERF_E를 같은 실행에서 직접 비교했다. 단계별 비율을 더하지 않는다. seed1831565813, warm120/measure240 fixed ticks, 각2회·AB/BA 반대·두 번째 조건 역순·총16쌍/32pages, 전체 회귀/카메라 종료 후 직렬 실행했다. 이전과 같은 CG 자함·optional allyCG/enemyDDG, 항공기/구표적OFF, native Kh32 helper16km/10000m/4방위의 diagnostic seeded measured tracks다. 자연 센서 획득이나 요격률 인증이 아니다. state/RNG/entity와240ticks complete가16쌍 모두 exact다. 기존 performance/profiler/lastBuildMs/lastAssessmentMs host-duration만 명시적으로 제외하며 raw states를 보존한다.

| 함정 | Kh32 | H4A ms/tick | PERF_E ms/tick | 관측 CPU 감소 |
|---:|---:|---:|---:|---:|
| 1 | 0 | 2.242 | 2.347 | -4.7% |
| 1 | 8 | 5.096 | 4.985 | +2.2% |
| 1 | 32 | 17.944 | 13.966 | +22.2% |
| 1 | 64 | 52.565 | 34.287 | +34.8% |
| 3 | 0 | 7.326 | 5.643 | +23.0% |
| 3 | 8 | 17.954 | 11.196 | +37.6% |
| 3 | 32 | 38.574 | 25.816 | +33.1% |
| 3 | 64 | 88.506 | 50.728 | +42.7% |

첫 보고의 기록상31%/43%(단함/3함64발)는 서로 다른 실행의 잠정 절대시간 비교였다. 위 표는 격리된 직접 누적 비교로 갱신한다. 최초 H4A→D 탐색 측정은 파일 작업과 static 검사가 겹쳐 최종 개선율/PASS에 넣지 않는다. 당시 script/report/rawstates/note를 not-counted-cumulative-d-*로 보존한다.

## 실제 첫 cut/fold 제출

D→E 원본, native RAF/THREE/WebGL SwiftShader LOW640×480·자함만·물리 일시정지·x12/측면z1.5 및 갑판 주변z4/STARBOARD diagnostic Kh32 dud1회. 각2회·AB/BA 반대·순서 역전·8쌍/16pages를 위 CPU 비교 이후 다른 작업 없이 직렬 실행했다. 첫 THREE submission의 entry/exit actual cut keys와 attached geometry, native GL0, 물리/저장/RNG exact를 확인한다. generator를 강제 완료하지 않는다. E는 완성된 anchor 메쉬를 함께 먼저 보여주고 동일 주변 메쉬·장식·detail을 이어서 완성한다.

| 자함 | zM | D 평균 s | E 평균 s | 관측 지연 감소 |
|---|---:|---:|---:|---:|
| CG-52 | 1.5 | 6.65 | 7.04 | -5.8% |
| CG-52 | 4 | 167.43 | 6.29 | +96.2% |
| DDG-119 | 1.5 | 26.72 | 4.97 | +81.4% |
| DDG-119 | 4 | 25.39 | 3.60 | +85.8% |

D 조사에서는 양측 anchor가 이미 matched였으며 주변 structure/fittings/sensors의42,676회 cooperative steps가 첫 공개를 막았다. D x12/z4가 약101.5초 후 실제 표시된 trace를 investigation에 보존한다. 이 D 재현으로 과거 C240초 timeout 원인을 소급 확정하지 않는다. 위 타이밍은 이번 원본끼리의 별도 완료 비교다.

## 실제 native 3D submit과 효과 전송

D→E native RAF/THREE/SwiftShader LOW480×360, warm4/measured8frames, 각2회·반대 AB/BA·조건 역순·8쌍/16pages. 물리는 paused, 자함 카메라235m·native distant64Kh32와 optional1200 제어 smoke(age2/fixedtime)를 사용한다. 멀리 있는 미사일은 frustum culling될 수 있으므로64개 근접 동시 표시 시험은 아니다. 아래 반복 연기는 시간이 고정된 GPU dirty-range 조건이며 모든 advancing-frame 효과 속도를 대표하지 않는다. source scene/drawcalls/triangles/particles 및 physical state/RNG와 native GL0를 대조한다.

| 자함 | Kh32 | 연기 입자 | D CPU ms/frame | E CPU ms/frame | 관측 CPU 감소 | driver subData bytes/frame |
|---|---:|---:|---:|---:|---:|---:|
| CG-52 | 0 | 0 | 12.54 | 11.15 | +11.1% | 124704 → 124704 |
| CG-52 | 64 | 0 | 18.56 | 18.09 | +2.5% | 124704 → 124704 |
| CG-52 | 64 | 1200 | 18.89 | 10.65 | +43.6% | 211104 → 124704 |
| DDG-119 | 0 | 1200 | 13.93 | 13.27 | +4.8% | 211104 → 124704 |

별도 light-scene native WebGL2 getBufferSubData fixture에서 전체 GPU attribute bytes가 기존과 exact였다. 연기24개 반복 frame의 전달1728→0bytes, 위치 한 개 변경1728→4bytes를 확인했다. camera/order/origin/Float32 ULP/signed0/pending multipleflush/축소·숨김/재등장/reset도 확인했다. 버퍼 절약을 전체 게임 개선율로 바꾸지 않는다.

위 CPU와 native 제출 시간은 이 호스트의 관측이다. 소프트웨어 WebGL 절대 시간을 실제 GPU/휴대폰에 적용하지 않으며 hardware GPU 완료·FPS·자연 폭발/연속 다수 피격 효과/장시간 성능을 인증하지 않는다. 작은 감소·증가와 실행 변동을 그대로 표에 포함한다. 물리/센서/피해/RNG/고정 주기를 낮추지 않았다. Actions dispatch/CI PASS 주장은 없다.
