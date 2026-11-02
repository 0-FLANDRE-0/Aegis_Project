# TRACK-C 이탈 표본 최초 원인

상태: **IMPLEMENTED / TESTED / APPROVED(자동 S2 조건) / UNRESOLVED(원본 저장 run 간 결과 변동) / RELEASE(no)**

지시서에는 39발로 적혀 있으나, 고정된 최신 TRACK-C `LINEAGE_RESULTS.json`의 C 제품 raw에서 qualified egress는 **37발**이었다. 16개 전투·37발을 같은 시드와 제품 SHA로 다시 실행했다.

## 확인 결과

- 첫 accepted association: RF_OBJECT 37/37
- 첫 confirmed TRACK: RF_OBJECT 37/37
- 첫 TRACK 이전 피해: 0/37
- 최초 연관이 DECOY인 경우: 0/37
- 최초 연관 예: 목표 함정은 약 10.7 km인데 같은 salvo의 ASM 합성 반사는 92.8 m, SNR 17,786이었다. 기존 점수는 후자를 선택했다.
- replay에서 원 저장본과 동일하게 egress한 것은 12/37이다. 그러나 계측 ON/OFF fresh pair는 comparable final JSON과 global RNG SHA가 완전히 같았다. 저장본과 fresh replay의 최종 방어 결과 차이는 기존 전투 경로의 run 간 분기이며 observer 효과가 아니다.

원인은 `STATE_MACHINE_DEFECT / INITIAL_CUE_ASSOCIATION_ACCEPTED_OUT_OF_BASKET_RF_OBJECT`로 확정했다. 실제 물체 종류를 전술 입력으로 사용해서 내린 결론이 아니다. 사후 ID는 원인 검증에만 썼다. 제품 시커가 본 정보만으로도 선택한 후보는 launch cue 거리에서 약 10 km 벗어나며, 같은 tick에 cue 근처 함정 측정이 존재했다.

기존 no-EKF 분기는 cue 거리·방위·고각을 **soft score penalty**로만 썼다. 가까운 이웃 ASM의 압도적인 SNR이 이 감점을 이겨 잘못된 RF EKF를 초기화했다. 이후 시커는 이웃 ASM이 편대에서 벌어질 때 COAST/REACQUIRE/SEARCH를 반복하고, 뒤늦게 함정을 재획득해도 이미 비행 경로가 틀어졌다.

상세 행별 근거는 `EGRESS_CAUSAL_ANALYSIS.json`, 원시 계측은 `evidence/egress/*.json.gz`, observer 동등성은 `REPLAY_DETERMINISM.json`에 있다.
