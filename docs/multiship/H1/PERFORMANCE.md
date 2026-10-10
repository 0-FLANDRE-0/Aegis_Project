# H1 검증 조건과 성능 해석

최종 HTML 원본을 Chromium에서 직접 읽는다. seed1831565813, desktop1100×820 pointer와 mobile430×900 emulated touch, 실제 SwiftShader WebGL/RAF를 사용한다. 수동 queue drain/render 물리 적분은 하지 않는다.

기존60Hz fixed tick,120Hz 침수/힘,20Hz hydro를 유지한다. H1은 native5Hz 추천 scheduler에서 owner별 같은 simStep 중복 평가를 방지한다. 최대96개 우선 파일/64개 태세 log를 보관하며 RNG·wall clock을 판단에 사용하지 않는다. 기존 native NEZ·사통·유도 계산을 재사용하고 별도의 world/physics 루프를 만들지 않는다.

세 척, 두 함종 조합을1/8/16/64× 각각1536ticks 진행하여 utility 결정/물리·관측·무장·EW·네트워크·난수·world clock을 비교한다. G/H1의 자함 AI 기본OFF idle·피격·Kh-32 8발 AUTO는 기존 물리/재고/RNG를 exact 비교한다. 새로운 AI 설정 및 기존 profiler/네트워크 설정 metadata만 이 비교에서 제외한다.

H1-on actual release는 isolated measured KF/terminal fixture로 검사하고, 별도의 physical 40m Kh-35U 시험에서는 초기 CMS 파일을 모두 지운 뒤 native 센서→utility→AUTO를 실행한다. terrain bypass/한 seed/대표 접근 조건이며 일반 격추율·대규모 함대 FPS를 인증하지 않는다.

테스트별 elapsed/heap/profiler/draw는 해당 host의 관측값이다. 여러 독립 시험의 CPU contention과 SwiftShader가 있으므로 실행 시간을 모바일/하드웨어 FPS 또는 성능 개선치로 환산하지 않는다. 최종 증거는 `evidence/`를 따른다. GitHub Actions는 사용자 조건으로 미실행이며 workflow_dispatch만 준비한다.
