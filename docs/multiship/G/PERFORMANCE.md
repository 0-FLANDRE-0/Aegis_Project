# G 검증 환경과 성능 해석

최종 HTML 원본을 그대로 Chromium에서 읽는다. UI는 1100×800 pointer와 393×852 touch, 카메라는 실제 SwiftShader WebGL/RAF를 사용한다. 초기 배치·출항·FLEET 버튼은 실제 input 이벤트로 확인한다. 소스 override, queue 강제 배출 또는 render에서의 fixed tick 진행을 사용하지 않는다. seed는 1831565813이다.

고정 시간 검사는 DDG/CG 자함·반대 함종 아군·적함 세 척을 1/8/16/64×에서 각각 1536 ticks 진행한다. 물리, world weather, owner 관측/무장/EW/방어/네트워크 tick 수와 RNG가 동일한지 비교한다. 별도 F/G 비교는 아군/Harpoon 없는 idle·피격·Kh-32 8발 AUTO에서 기존 자함의 물리와 combat RNG를 대조한다. 네트워크 settings와 profiler는 이 비교에서 제외한다.

네트워크 picture96/report32+SELF/queue16/log128/local candidates128, 2Hz 송신과 5Hz 연관을 상한으로 둔다. FLEET 현지 목록은96개까지, UI 갱신은250ms 간격이며 시뮬레이션 시간이나 전투 난수를 소비하지 않는다. 기존 물리 60Hz·침수/힘120Hz·hydro20Hz와 모델 assets0~12는 유지한다.

브라우저 fixture가 측정한 elapsed/heap/draw 수는 해당 테스트 환경의 관측값이다. 독립 검사들이 동시에 실행될 수 있으므로 단일 실행의 시간을 FPS 또는 성능 향상 근거로 사용하지 않는다. SwiftShader는 소프트웨어 렌더링이며 휴대폰/실제 GPU의 FPS 인증이 아니다. 최종 실제 측정값과 오류 여부는 `evidence/clock.json.gz`, `paired-ownship.json.gz`, `native.json.gz`, `fleet-camera.json`, `verification-summary.json`을 따른다.
