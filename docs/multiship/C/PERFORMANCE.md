# Multi Ship C 측정 조건

최종 HTML SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`에서 실행했다. 단일 seed의 CPU fixture는 headless Chromium이며 terrain bypass와 공통 실제 RF/EKF를 사용한다. 여러 독립 검사를 함께 실행한 호스트 관측값이다. 성능 향상·누수 부재·모바일 hardware FPS를 주장하지 않는다. fixed tick/침수·힘/hydro는 60/120/20 Hz 그대로다.

## Full fixed tick와 관측

혼합 함종 두 쌍 × 1/8/16/64 × 각1,536틱이다. 실제 관통 probe와 타각 명령, 양 함정의 센서를 함께 실행했다. 같은 쌍의 물리·관측 file·sensor RNG·전체 전투 RNG·world time이 exact이며 공통 시간은25.6초다. profiler는 최근512틱 표본이다.

| 자함 | 적함 | 배속 | 실행 ms | tick avg ms | p95 ms | max ms |
|---|---|---:|---:|---:|---:|---:|
| DDG | CG | 1 | 15445.1 | 5.848 | 24.100 | 44.000 |
| DDG | CG | 8 | 12927.9 | 6.367 | 23.400 | 49.300 |
| DDG | CG | 16 | 18049.0 | 7.705 | 26.100 | 80.900 |
| DDG | CG | 64 | 19754.4 | 7.891 | 26.300 | 53.900 |
| CG | DDG | 1 | 13813.7 | 8.246 | 26.800 | 94.200 |
| CG | DDG | 8 | 9646.2 | 6.374 | 21.200 | 40.300 |
| CG | DDG | 16 | 11776.9 | 6.614 | 20.200 | 30.000 |
| CG | DDG | 64 | 11108.0 | 6.794 | 22.300 | 48.800 |

`evidence/fleet-clock.json.gz`는 원본 profiler/개체 수·관측/물리 상태를 포함한다. 기본 적함 없음 B↔C는 양 함종의 대기240틱/1배속, 8Kh-32 AUTO1920틱/8배속, 침수480틱/16배속에서 물리와 RNG exact다. AUTO raid는 초기 track 주입 회귀이므로 자연 탐지나 새 적 AI 검사로 세지 않는다. CDP heap은 전체 GPU 메모리/누수 측정이 아니다.

## 자연 탐지·외부 보고

네 함종 조합에서 공통 물리 RF로 접촉을 얻었다. truth/plot/tentative/confirmed 수를 같은 시점에 기록하고 독립 난수·EMCON/손상·coast/재획득·snapshot/reset/import를 확인했다. 외부 보고 fixture는 합성 noisy 측정/지연/링크 단절 계약 시험이며 실제 헬기 탐지 시험이 아니다.

60km에 실제 배치 함정을 놓았을 때 낮은 함상 receiver에는 반사가 없고, 진단 receiver를600m로 높이면 반사가 생겼다. 낮은 고도에서 섬 차폐·높은 고도에서 지형 LOS 차이를 확인했다. 해당 echo를 게임 track이나 외부 포트에 직접 주입하지 않았고 헬기 객체를 만들지 않았다.

## Native RAF/WebGL

393×852 Chromium SwiftShader에서 양 혼합 함종의 자연 접촉, rotor 실제 회전·mesh각 일치, 원래 버튼으로 CIC전환/read-only와 reset을 확인했다. physical-native는 원본 A의 class mesh fingerprint와 C의 배치 모델을 대조하고 실제 입구/출구 actualHole·후속 draw/tick·reset2회 root/job disposal을 확인했다. physics/geometry queue를 수동 진행하지 않는다. 원래1배속120초 wait 예비 실행은 호스트 벽시계 timeout이 발생했고, native8배속 fixture로 두 함종을 재검사했다. 예비 실행은 최종 PASS 수에 포함하지 않는다.

| 자함 | 배치 모델 | draw | 최종 tick | frame avg ms | p95 ms | max ms |
|---|---|---:|---:|---:|---:|---:|
| DDG | CG | 70 | 69 | 1199.3 | 1540.6 | 3483.6 |
| CG | DDG | 40 | 69 | 1078.0 | 2778.0 | 3256.1 |

SwiftShader의 frame 시간은 사용자 GPU/FPS가 아니다. CG의 기존 sourcePreserved triangle audit는 retained750535/meta740819/declared767571 기준 차이로 false를 유지한다. 그 전체 audit를 PASS로 세지 않고, 원본 asset bytes와 실제 함종별 vertex/index/name/hash fingerprint를 별도로 확인했다.
