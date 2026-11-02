# R4의 범위와 승인 경계

작업 브랜치는 `track-b-stabilization-a`, 기준은 동결된 `track-b-association`이다. 기존 브랜치·main·기대값·허용 오차는 바꾸지 않는다. 이 문서는 완료 선언이 아니며 최종 판정은 `VALIDATION.json`과 보고서에 따로 기록한다.

## 연관 검사와 상태 전달을 구분한다

R3 모듈을 바이트 그대로 사용한다. δ=1, 원 NIS gate/dummy/native winner, 동일 관측 시각·차원에서 읽는 기존 S 증거, R2 하한/잔여 성분, C=0·완전 매칭·양축≤16의 정확 검사만 포함한다. >16의 계산 제한 및 비완전 큰 성분 보수성은 남아 있다. C55·SPQ AIR 소비 경로는 SHADOW-only다. 미완성 경로를 ACTIVE 구현으로 세지 않는다.

R3의 격리·native·실제 그래프 검사가 통과해도 자연 13기 전투 결과는 승인하지 않았다. 그 자료에서 별개의 상태 전달 오류를 발견했다. 실제 SHADOW는 기존 B의 native/passive/RNG/선택 결과와 같았고, 다른 파일의 재획득 작업에서 수용한 정상 관측이 수신 파일을 새 재획득 상태로 바꾸는 현상을 계측했다. 첫 사례의 관측은 신선하고 miss/hit counter가 0인데, 다른 task owner 때문에 flag와 miss가 생겼다. 이것은 단순 `GLOBAL HOLD → dwell miss` 경로라는 이전 가설과 다르다.

## 최소 수정의 근거

R4는 `spyFinalizeAcceptedTrackV31` 안에서 새 ACTIVE가 처리하는 **다른 task owner의 정상 accepted return**이 재획득 중이 아닌 수신 파일에 새 재획득 상태를 만드는 것만 막는다. 해당 수신 파일에는 기존 정상 수용 분기를 적용한다. 이미 재획득 중인 파일, task 자기 대상의 1·2회 복구, 실제 dwell miss 누적, source/face/revisit 기록은 기존 경로를 유지한다. owner가 없으면 기존 경로를 유지한다. SHADOW와 legacy implementation mode도 기존 경로 그대로다.

이는 연관 결과를 전달할 때의 파일별 상태 소유권 수정이다. FCS/A3/ROE/IFF/AI 관문을 완화하거나 재획득 2회 요건을 제거하지 않는다. RF task·파형·노이즈·RCS·빔, 현재 accepted measurement와 KF correction, EKF 방정식·계수, 무장·피해·함정 물리·RNG 함수·저장 스키마는 수정하지 않는다. source proof는 R3 대비 finalizer 한 함수만 달라졌는지 검사한다.

올바른 상태 전달 이후 scheduler·Q 선택·후속 RF/피해 난수의 실행 분기는 달라질 수 있다. 따라서 전체 EKF/RF 상태나 RNG 시퀀스가 모든 ACTIVE 전투에서 같다고 주장하지 않는다. 계수나 수식을 바꾼 것과, 수정된 관측/상태가 기존 소비 경로에 들어가 결과가 달라지는 것을 구분한다. 새 차이는 결과와 인과 자료를 보존해 검토하며 자동 승인하지 않는다.

## 시험과 완료 판정

실제 packed HTML의 함수 추출 격리 검사, 실제 native 통합, 원래 회귀, SHADOW 동일성, 자연 전투, 독점 비용 측정을 각각 구분한다. 이전 후보의 통과를 R4 통과로 대체하지 않는다. 원래 실패·미실행·기존 UI14 미완료를 통과로 바꾸지 않는다. 전투의 실제 초기 탄체 종말과 callback 수, legacy HP와 모듈/침수 상태도 구별한다.

논리적 일대일 연관 위반과 물리 표적 ID 교환은 다른 지표다. 기존 사후 표본은 최근접 물리 참조 변화와 잔차를 기술할 수 있지만, 실제 RF 반사체→측정 원점 및 모든 KF 시각을 보존하지 않았다. 이 자료만으로 물리 오병합/중복/ID 교환이 0이라고 주장하지 않는다. 사후 truth는 게임·UI·AI로 되먹이지 않는다.

paired 4건·419012 strict 차이와 이전 419025·observer2·EMCON UI14는 별도 장부를 유지한다. 의도된 정책 차이라는 설명만으로 기대값을 바꾸지 않는다. 새 후보에서 부당한 방어 실패가 남으면 미승인/미완료로 보고하며, 결과를 맞추는 계수 조정이나 TRACK-C/OODA 구현으로 범위를 넓히지 않는다.
