# Multi Ship B 측정 조건

모두 최종 HTML SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`에서 실행했다. CPU fixture는 headless Chromium·고정 seed·terrain bypass를 사용한다. 일부 검사는 독립 프로세스로 함께 실행했고 단일 실행 값이다. 아래 관측으로 성능 향상·누수 부재·모바일 hardware FPS를 주장하지 않는다. cadence는 60/120/20 Hz 그대로다.

## 두 함정 full fixed tick

1/8/16/64배속 각각 1,536틱, 혼합 함종 2쌍을 실행했다. 각 쌍의 물리 상태와 RNG가 exact이며 공통 world time은 25.6초다. 실제 외판 관통 피해와 타각 명령을 적용했다. tick profiler는 최근 최대512개 표본이다.

| 자함 | 적함 | 배속 | 전체 실행 ms | tick avg ms | p95 ms | max ms |
|---|---|---:|---:|---:|---:|---:|
| DDG | CG | 1 | 5764.4 | 2.9546874999796273 | 7.800000004470348 | 51 |
| DDG | CG | 8 | 5359.4 | 2.6091796875116415 | 5.799999997019768 | 48.80000000447035 |
| DDG | CG | 16 | 4455.3 | 2.8314453125203727 | 8.100000001490116 | 54.19999999552965 |
| DDG | CG | 64 | 4606.6 | 2.419921875014552 | 4.299999997019768 | 35.70000000298023 |
| CG | DDG | 1 | 5423.5 | 2.399804687491269 | 6.0999999940395355 | 30.19999999552965 |
| CG | DDG | 8 | 4784.1 | 2.633203124991269 | 6.5 | 27.900000005960464 |
| CG | DDG | 16 | 5031.5 | 2.658984374967986 | 7 | 29.399999998509884 |
| CG | DDG | 64 | 4500.6 | 2.4822265625261934 | 4.700000002980232 | 28.899999998509884 |

원본 profiler·개체 수·상태는 `evidence/fleet-clock.json.gz`를 따른다. 기본 적함 없음 A↔B 비교는 양 함종 × 대기240틱/1배속, 8 Kh-32 AUTO1920틱/8배속, 침수480틱/16배속이며 자함 물리·RNG가 exact다. raid의 초기 트랙은 기존 회귀 fixture가 주입하므로 자연 탐지/적 AI 검사가 아니다. CDP V8 heap 관측은 GC/전체 GPU 메모리와 구분한다.

## 실제 native RAF/WebGL

393×852, 원본 A의 함종별 자함 mesh fingerprint와 B의 상대 함종 model을 대조했다. vertex position hash/mesh 이름·vertex/index count가 일치하고 packed source asset SHA도 그대로다. 입구/출구 두 actualHole과 attachment, 후속 draw/tick, 표시 read-only 및 reset 2회 root/job disposal을 확인했다. test가 physics/geometry queue를 강제 진행하지 않는다.

| 자함 | 실제 배치 모델 | draw | 최종 tick | frame avg ms | p95 ms | max ms |
|---|---|---:|---:|---:|---:|---:|
| DDG | CG | 84 | 69 | 2284.6 | 3960.0 | 7435.7 |
| CG | DDG | 46 | 69 | 1976.4 | 4712.7 | 6721.8 |

backend는 Chromium SwiftShader다. frame 시간은 소프트웨어 렌더링/호스트 관측이며 사용자 기기 FPS가 아니다. CG의 기존 `contractAudit.sourcePreserved`는 retained750535/meta740819/declared767571의 서로 다른 count 기준으로 false를 반환한다. 이번에 해당 전체 audit를 PASS로 세지 않았다. 원본 A와 함종별 실제 mesh fingerprint 일치 및 asset bytes 보존을 별도로 검사했다. 이 역사 count 정의의 정리는 별도 작업이다.
