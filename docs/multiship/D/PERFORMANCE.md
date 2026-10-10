# D 성능·측정 조건

최종 결과의 provenance는 evidence/verification-summary.json을 따른다. 구현 예비본에서 mixed DDG/CG 두 쌍 × 1/8/16/64 ×1,536 full fixed tick을 실행했고 모든 물리/관측/무장/난수·공통 시간 상태가 exact였다. 이 예비본 SHA의 결과를 최종 HTML 직접 PASS 수에 더하지 않는다. 최종 CI clock은 실제 원본 HTML에서 동일 fixture를 다시 실행한다.

60Hz fixed tick·120Hz 침수/힘·20Hz hydro와 native damage-control VLS 사고 주기는 유지한다. owner shadow5Hz/64로그, observer256tracks, C55 mount48files, active SAM/RAM256개 제한을 둔다. 여러 fixture를 동시에 실행한 호스트 CPU/terrain bypass 관측이며 FPS 향상·모바일 GPU·누수 부재를 인증하지 않는다.

| 자함 | 배치 함정 | 배속 | 실행 ms |
|---|---|---:|---:|
| DDG | CG | 1 | 16165.3 |
| DDG | CG | 8 | 14059.1 |
| DDG | CG | 16 | 17555.1 |
| DDG | CG | 64 | 17452.4 |
| CG | DDG | 1 | 14943.9 |
| CG | DDG | 8 | 16840.0 |
| CG | DDG | 16 | 16711.6 |
| CG | DDG | 64 | 19248.3 |

예비 clock SHA `d2863b39b3903e4d9c073978726a93afa246de335b6a0952b8b28427fdbb1500`. profiler 최근512틱·draw/native 증거는 결과물마다 SHA로 구별한다. 393×852 Chromium SwiftShader native RAF/WebGL로 SAM/SPG·적함 Harpoon mesh/덮개·실제 terminal path/손상 흔적·read-only camera를 검사한다. SwiftShader wall time은 사용자 하드웨어 FPS가 아니다. 피해 fixture는 진단 swept 관통이며, 8km 두 방향 Harpoon battle은 실제 launch/INS/ARH/contact다.

CG source 삼각형의 역사 metadata 불일치는 이전 C/K 문서의 한계를 유지한다. 모델 asset bytes 자체는 보존하며, 이번 단계에서 과거 audit를 새 PASS로 승격하지 않는다. 공격 AI·EW·헬기·다수 함정 FPS 인증은 후속 범위다.
