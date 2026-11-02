# ASM seeker 원인표

| 기종/현상 | Observed | Inferred | Confirmed | Unresolved |
|---|---|---|---|---|
| Kh-35U 20 km 복수 함정 | 10/20°에서 자함 첫 TRACK | 높은 SNR이 cue 잔차를 압도 | no-EKF cue가 점수 감점일 뿐 gate가 아님 | 없음 |
| Kh-35U TRACK-C salvo | 이탈 표본 37/37이 이웃 ASM RF_OBJECT 첫 TRACK | 잘못 초기화한 EKF가 salvo 분리 때 끊김 | 첫 TRACK 전 피해 0, 같은 tick cue 함정 echo 존재 | 저장 run과 fresh replay의 최종 방어 결과 변동 |
| Kh-35U 45 km | 50/50 TRACK 없음 | target-evidence/클러터 감도 | coefficient/model 현상 | 계수 조정 금지로 유지 |
| ACQUIRE 후보 조향 | Kh-35U 후보 추종 rate command 0 | INS가 유지됨 | 정적 호출 그래프와 runtime 일치 | Kh-32의 DIVE/INS command는 후보 조향과 분리해 해석 필요 |
| Kh-32 | 공용 WIP22 core 사용 | 같은 초기 cue 결함 가능 | S2 공용 수정 보존 시험 대상 | 물리 감도 계수는 변경 안 함 |
| Harpoon | 독립 `harpoonSeekerA`, 기존 core audit 통과 | 공용 WIP22 결함과 무관 | 독립 basket hard gate 존재 | live 물리 표본은 S2 결과에 기록 |

## 수정 판정

Confirmed인 초기 연관 결함만 S2로 넘겼다. 수정은 실제 ID·소속을 읽지 않고 기존 cue residual scale만 초기 획득 basket으로 승격한다. 피해, 기만, SNR 부족, 가림, 기동 한계 실패는 그대로 남긴다.
