# H4 검증 조건과 성능 범위

최종 원본 SHA와 실제 검사 수치는 `evidence/verification-summary.json`을 따른다. 이전 SHA/역사 H3 결과는 합산하지 않는다.

- local Chromium + Python Playwright, 고정 seed `1831565813`. fixture/자연 센서/동일 물리 비교는 CPU headless, native 3D는 SwiftShader RAF/WebGL이다. 1100×820 mouse, 430×900 emulated touch를 포함한다.
- 실제 익명 ship RF로 empty CMS에서 현지 SURFACE 파일을 만들고, 별도 operator 식별·각 owner 동의·배정·native Harpoon 실제 발사·접수 공유를 확인한다. 시험의 표적 적성 지정은 센서가 알아낸 world faction이 아니다.
- 자위 근거 fixture는 명시 측정 입력이며 가상의 관측 신선도·EKF를 설정한다. 자연 레이더 주기나 모든 발사원 획득 가능성을 이 fixture로 인증하지 않는다. 부정 조건·아군/중립·모호한 발사원·늦은 FRIEND·alias·만료를 검사한다.
- 전형 fixture는 받은 항법 보고와 실제 H2 명령/물리를 사용한다. 해안과 미관측 교통의 모든 상황, 전형 수렴 시간·간격 정확도를 보장하는 항해 계획기는 아니다.
- 두 함종 조합·세 척에 1/8/16/64배속을 실제 frame accumulator로 실행한다. 기존 native 방어·H3 실제 하푼과 H4 전형을 함께 비교한다. 표시 타이밍/측정 profiler 값을 물리 서명에 포함하지 않는다.
- H3/H4 팀 OFF·no-peer의 idle/손상/8 Kh-32 AUTO fixture에서 물리·고정 재고·전투 RNG를 비교한다. 대표 seed 회귀이며 일반 격추율·실제 doctrine·휴대폰 hardware FPS 인증이 아니다.
- owner-local 파일96/수상 bid16, queue16/송신2Hz/지연18틱, 수신2초 fresh, own 접수8/수신 접수16/로그64, 전형4후보와 각6예측 자세, 기존 교통16+받은 선도함1로 비용을 제한한다. H3 native bid preview는 읽기와 exact capability 임시 교체만 수행하고 `finally`에서 복원한다.
- 기존 60 Hz 공통 tick·120 Hz 침수/힘·20 Hz quadrature·render read-only와 RNG 격리를 유지한다. 세 함정의 센서·방어·무장·EW·G 네트워크를 tick마다 한 번 실행한다.

상관/배정이 없거나 연결이 끊기면 bounded 대기 뒤 개별 native 권한으로 돌아간다. 이미 받은 발사 접수는 만료까지 기억하지만 받지 못한 정보를 추측하지 않는다. packet loss/링크 재밍/다수 네트워크 topology는 별도 구현이다. GitHub Actions 자동 작업이 계정 제한으로 시작되지 않아도 CI PASS라고 표시하지 않는다.
