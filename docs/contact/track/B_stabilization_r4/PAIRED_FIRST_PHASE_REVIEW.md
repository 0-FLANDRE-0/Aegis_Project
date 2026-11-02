# R4 첫 회귀 phase — 원래 paired 42단언

고정 ACTIVE `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`, SHADOW `3c7d2490e7e0d6fe94452e43d8f22132fbdd8add83986208bf7173068c478444`, runner `ac73be71cea4924fc1eec577d0da82e84e88207423e1e1f622efd922a2a797fd`로 원본6case를 새 실행했다. 원래42단언은 **36 PASS /6 FAIL**이다. 오류0이며 실행182.43초 뒤 worker·브라우저·lease를 닫았다. 모든 원자료와 전체 leaf 차이를 보존했고 기대값·허용오차는 변경하지 않았다.

기존 DDG/CG raid의 samePhysicalState 및 sameExistingObserverState4건은 계속 실패한다. 추가로 두 함정의 raidInventoryDeltaBounded2건이 새로 실패한다. **6건 전부 미승인**이다.

## 재고 검사의 실제 의미

`docs/helicopter/F/verify_regression.py:66`은 H4의 과거 `abs(loadedVlsA-loadedVlsCandidate)<=1` 검사를 **정확한 수량 동등 비교 `==`로 바꾼다**. 이름 raidInventoryDeltaBounded는 현재 의미와 다르다. 물리적 사거리·발수 상한을 넘었다거나 무장 시스템이 새로 고장났다는 판정이 아니다.

명시적 approved-raid baseline이 선택되고 코드 hash가 맞으면 승인된 expected loaded count와도 정확히 `==`로 비교한다. 이번 실제 명령에는 approved-raid 또는 approved-air-origin 인자가 없으므로 그 승인 분기는 사용하지 않았다. 기존 exact 기준을 그대로 유지한 결과다.

## 실제 원자료 네 버전 비교

| 함정 | 값 | A | 전달 B | R1 | R4 |
|---|---|---:|---:|---:|---:|
| DDG | 남은 loaded VLS cell |90|90|90|89|
| DDG | 현재 자체 SAM entity |6|6|6|7|
| DDG | 남은 SM2 cell |66|66|66|65|
| CG | 남은 loaded VLS cell |115|115|115|114|
| CG | 현재 자체 SAM entity |7|7|7|8|
| CG | 남은 SM2 cell |91|91|91|90|

양쪽 모두 SM2 한 cell 추가 소비, 현재 SAM entity 한 개 추가, 기존 SM2 질량에 해당하는708kg 함 질량 차이가32초 말에 있다. ESSM4 cell은 모두24개로 같다. **원래 수집기는 누적 발사 시각/대상별 발사 로그를 저장하지 않으므로 특정 발사 시점이나 R4 finalizer 단독 원인으로 귀속하지 않는다.** R3 paired는 실행하지 않아 R3→R4 분리 비교도 없다.

모든 버전의 같은32초 말에 HP100, 물 질량/부피0, 모듈 피해 최대0, 초기 Kh-32 8개 모두 alive, native intercept event0, combat RNG2134102897이다. 직접적인 shipHitHistory 건수는 원래 fixture에 저장되지 않았으며 HP/손상0을 대신하여 피격 이력0으로 꾸미지 않는다. native 종료가 아니라 원래1920 fixed tick/32초 경계에서 끝났다.

이는 현재 시점의 자원·물리 상태·관측 strict 차이이며 **최종 방어 품질 판정은 미해결**이다. 8개 alive를8개 격추 또는 완료된 전투로 표현하지 않는다. 소스 인과 설명, 한 발 추가 소비, 최종 snapshot 일부 동등만으로 기준값 승인을 내리지 않는다. 원 코드·계수·검사·기대값 조정 없이 나머지 최신 회귀를 이어 측정한다.

기계 판독 자료는 [FIRST_PHASE_COMPARISON.json](evidence/regression/FIRST_PHASE_COMPARISON.json), 원래 결과는 [baseline-comparison.json](evidence/regression/paired-track-a/baseline-comparison.json), A/B/R1/R4 모든 leaf는 [paired-four-version.json.gz](evidence/regression/paired-four-version.json.gz)에 있다. 외부 main 이동은 이 고정 실행에 반영하지 않았다.
