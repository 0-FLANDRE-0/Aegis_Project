# 사용자 승인 §5의 24개 단언 처리

기존 B1/MAP_D 시험 파일과 승인 기대값은 그대로다. private 실행본과 정확한 diff는 adapted/에 있다. source hash는 ASSERTION_MIGRATIONS.json을 따른다.

| 기존 단언 | 수 | 새 실행 / 현재 결과 |
|---|---:|---|
| DDG/CG G2 탄도 오차<.35m |12| 같은 .35m 한계, 탄도 진단 동안만 dispersion=false, finally 원래 플래그 복구. 모두 통과. ON 산포는400발 앵커 검사. |
| relativeSweptCPA 정확t=.5 |2| 최초 신호 탐지+정확2ms, CPA이전 기폭. 모두 통과. |
| G3.prox / friendlySAM 축상 양성 기대 |2| y=12.5m 횡방향 양의 통과거리로 실제 환형을 지나게 배치. SAM의 RF메타데이터는 기존NPC-SAM .06m²를 사용. 모두 통과. |
| Harpoon 축상 탐지/종료/사후기록 |3| 같은 시드·속도·처리지연·native피해 함수에서 y=12.5m, 실제 own-Harpoon .06m² 메타데이터. 탐지는 통과, nativeFinish/사후기록2개는 실제MISS로 미통과. |
| G4 r=0 강제격추 |1| b=1m 양의 통과거리, r_x=v·b/vf로 몸체90°의 native파편 도달을 구성. 통과. r=0은 별도 비어있지 않은 효과목록의Pk0 확인. |
| CG G5.singleNative |4| 원래 단언 그대로. AIR고정6.25m 창 적용 뒤4/4통과. |

추가 대조: AIR/SAM/Harpoon의 축상은 미탐, r=0은Pk0, 누락RCS(.001fallback)는 미탐, 탄도 진단 뒤 산포 플래그는 복구된다. 이는 변경 대상 밖의 기존 기대나 허용치를 완화한 것이 아니다.

초기 양성 mock에는 RCS가 없어 실제 missile reflector 대신 .001fallback이었다. 처음의 실패/소스를 evidence/fixture-rf-before/에 보존했다. .06m²는 결과를 맞추기 위해 고른 새 game계수가 아니라, 기존 NPC SAM과 자함Harpoon 생성코드에 이미 있는 RF메타데이터다. 제품RF/RCS/Pd/신호·누적 임계값·처리/피해 계수는 바꾸지 않았다.

RCS보완 뒤 Harpoon은 파편 몸체각74.3367°로 띠 안이고 Pk=.343512790077이지만 실제 피해 draw가 이를 넘어서MISS다. 남은2개 단언을 통과시키려고 시드·통과거리·계수를 바꾸거나 검사를 조건부로 완화하지 않았다. 최종 HTML의 읽기 전용 재생이 기존 실패 및 RNG와 일치하는지 별도 기록한다.
