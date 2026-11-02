# TRACK-B 안정화 승인 범위

사용자 지시: track-b-association 최신 구현과 검증 위에서 별도 안정화 브랜치로 진행. 신규 연관 정책·5건 strict 차이·실제 종료 전투·12 초과 성분을 검증한다. 원인 설명과 최종 승인/안정화 완료를 구별한다.

보존: RF/EKF/IFF/ROE/무장·피해·함정물리/AI/저장 스키마와 계수, 기존 기대값·허용 오차. 419025, 이전 observer2 차이, legacy EMCON UI14는 상속 문제로 별도 관리한다. C55/SPQ AIR는 SHADOW-only 유지. TRACK-C/D/OODA/main·기준 브랜치 병합/PR/release/tag 없음.

새 후보는 기존 ΔNIS1을 낮춰 결과를 맞추지 않는다. 동일 epoch·실제 관측 차원의 innovation covariance S를 이용한 추가 근거를 SHADOW에서 먼저 검증한다. 수학적으로 증명되지 않은 로컬 greedy 강제 매칭을 쓰지 않는다. 실제 표적 위치/ID는 제품 연관·식별·교전 입력으로 쓰지 않는다. 사후 진단 자료만 별도 AFTER_ACTION 표기한다.

현재 B 산출물과 docs/contact/track/B는 읽기 전용으로 보존. 새 자료는 이 디렉터리에 작성.
