# H2 검증 조건과 성능 해석

최종 HTML을 Chromium에서 직접 읽는다. seed1831565813, desktop1100×820 mouse와 mobile430×900 emulated touch, 실제 SwiftShader WebGL/RAF를 사용한다. CPU fixture의 wall time/heap/profiler는 해당 host의 관측값이며 hardware/mobile FPS 또는 성능 개선치로 환산하지 않는다.

기존60Hz fixed tick,120Hz 침수/힘,20Hz hydro를 유지한다. H2는 공통 command phase에서 12틱마다 owner별 한 번 판단한다. 위협8·수상 교통16·기동 후보8·각 예측 자세6·로그64개 상한을 둔다. 원래 geometry constraint cache를 재사용한다. 목표 truth 조회·추가 물리 루프·render 물리 적분·전투 RNG 소비는 없다.

세 척, 두 함종 조합을1/8/16/64× 각각1536full ticks 진행해 실제 초기 기동 명령과 최종 utility/물리·관측·무장·EW·링크·RNG/world clock을 비교한다. 초기64와 후속1472틱은 모든 배속의 프레임 적분 단위에 맞춘다. 초기 관측이 오래되어 소유권을 반환해도 실제 명령 이력을 별도로 확인한다.

H1/H2의 자함 기동 AI 기본OFF idle·피격·Kh-32 8발 AUTO는 동일 물리·재고·RNG를 비교한다. 기존 비교와 같은 EW/network/tactical metadata·새 maneuver 설정·profiler만 제외하며 항법/실제 재고/피해는 비교에 포함한다. H2 실제 기동은 별도 approved measured fixture와 초기 CMS 파일0인 실제40m Kh-35U에서 검사한다.

terrain guard는 실제 chart polygon으로 검사하고 수상 교통은 observed fixture로 검사한다. motion fixture는 terrain bypass/제한된 접근 조건이다. 6개 예측 자세·선회/기관 근사는 SIM-TUNE이며 전 해역 충돌 회피·전술 최적성·일반 격추율 인증이 아니다.

native3D는 실제 RAF와 geometry job 완료를 기다려 세 모델·함정별 해상효과·ENTRY/EXIT 피격 구멍·import/reset 폐기를 확인한다. geometry queue를 수동 배출하지 않는다. GitHub Actions는 사용자 조건으로 dispatch하지 않으며 수동 workflow만 준비한다. 로컬 최종 원본이 검증 gate다.
