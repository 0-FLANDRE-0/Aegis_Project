# 실제 구현 결정과 한계

이 문서는 설계 검토와 실제 후보를 구별한다. 기존 B 파일·HTML·기대값·계수는 변경하지 않는다.

- `ambiguityDeltaNis=1`은 그대로다. native NIS gate와 Hungarian winner도 그대로다. 그 winner를 바꾸는 secondary assignment는 실행하지 않는다.
- `NIS + log(det(S))`는 같은 실제 row/dimension/epoch의 Gaussian innovation density 비교다. 기존 기준1을 비교 비용에도 재사용하는 association-only 휴리스틱이며 보정된 posterior 확률이나 새 RF 성능으로 주장하지 않는다.
- 모든 row가 real edge로 매칭될 때만 covariance 증명으로 HOLD를 해제한다. native exact tie, 누락/차원·epoch 충돌, full evidence winner 충돌, 부분 matching은 보수적으로 HOLD한다. hit/ID/age/IFF 보너스 없음.
- `S`는 full native `H P Hᵀ + R` 산술을 그대로 읽어 구성한다. native NIS/update/predict를 추가 실행하지 않는다. AIR의 derived kernel cache getter 검증을 한 번 더 호출하고 surface는 동일 prediction/Jacobian/행렬곱을 읽기 전용으로 재계산한다. **파생 cache는 변할 수 있으므로 모든 cache의 절대 무변경을 주장하지 않는다.** canonical state/P/private RNG 불변과 비용은 별도 검증한다. protected filter/RF 함수 본문은 byte 동일이다.
- own/NPC의 실시간 producer가 현재 native association 평가 시각을 명시한다. EKF 자체에 별도 절대 epoch 필드가 없다는 한계는 남는다. 새 과거 시각 정렬이나 추가 CV 예측을 하지 않는다. Hawklink의 지연 보고는 `measuredAtS != now`이면 추가 우도 근거를 쓰지 않는다.
- 수상 position-only 비용은 원 plot에 Doppler가 있어도 정확히2차원 S를 사용한다. 공용 callback이 native surface3D 또는 알 수 없는 함수라면2차원으로 인증하지 않고 추가 근거 없음으로 처리한다. 수상 Cartesian z prior도 새 관측으로 인증하지 않는다. 이 제한은 기존 offboard/gate/필터 처리를 삭제하는 것이 아니다.
- 기존 최대12 성분의 정확 대안 검사를 보존한다. 13~128 성분은 native Hungarian을 **한 번** 실행하고, dummy를 포함한 전역 objective와 row-minimum 하한을 비교해 모든 근접 대안에 필수인 edge만 갱신한다. 로컬 greedy/mutual-best peeling 아님. 미증명 row와 미확정 column은 HOLD하며 확정 column을 덮지 않는다.
- 128 초과 성분의 계산 한도 HOLD는 남는다. 128 밀집 Node 관측에서16.7ms를 넘는 비용도 남는다. CPU soundness와60Hz 예산 통과는 별개다. 제품 계수/cap를 성과에 맞춰 자동 축소하지 않았다.
- C55와 SPQ AIR의 실제 live 연관은 원래대로다. 새 solver의 비교 제안이 보여도 **SHADOW-only**이며 ACTIVE 완성으로 세지 않는다. focused SPY 우선 경로도 원래대로다.
- 새 SHADOW는 **기존 B ACTIVE를 소비하면서 새 후보를 평가**한다. 과거 B SHADOW(원 A 소비)와 구별한다. ACTIVE 이전에 원 B 대비 상태/private RNG 동일성과 실제 positive/negative native 증거를 검증한다.
- 원래 strict4+D1419012 및 상속419025/observer2/legacy14는 별도 상태로 남긴다. 원인 설명·새 fixture 통과·실전투 한정 결과가 자동 기준값 승인 또는 전체 안정화 완료를 의미하지 않는다.
