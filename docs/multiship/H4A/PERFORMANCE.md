# H4A 최종 검증 조건과 비용 관측

- 최종 HTML SHA `3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a`, 원본 15,702,263bytes. seed1831565813/로컬 Chromium·Playwright, CPU fixed-step와 실제 RAF/WebGL SwiftShader, terrain bypass 대표 조건이다.
- 새 sensor/EW 판단은 기존 CIWS local bank·ESM contact 상한 안에서만 작동한다. 물리60Hz·침수/힘120Hz·정수압20Hz를 유지하고 화면/진단이 combat RNG를 소비하지 않는다. 새 local authority·측정 EW 타이밍은 실제1/8/16/64배속에서 exact state/RNG를 확인했다.
- H4 팀/H3 공격/H2 기동/H1 방어/G 공유/EW가 있는 세 owner의1536full-tick 테스트 비용 관측이다. 행간 수치는 다른 실행 순서/호스트 부하에 영향을 받으며 사용자 hardware FPS나 성능 개선율이 아니다.

| 자함 | 배속 | elapsed ms |
|---|---:|---:|
| DDG_119_LATE_FLIGHT_IIA | 1 | 65457.0 |
| DDG_119_LATE_FLIGHT_IIA | 8 | 65906.7 |
| DDG_119_LATE_FLIGHT_IIA | 16 | 72903.1 |
| DDG_119_LATE_FLIGHT_IIA | 64 | 68886.2 |
| CG_52_LATE_TICONDEROGA | 1 | 51007.8 |
| CG_52_LATE_TICONDEROGA | 8 | 59269.1 |
| CG_52_LATE_TICONDEROGA | 16 | 60572.1 |
| CG_52_LATE_TICONDEROGA | 64 | 61893.4 |

동일 seed의 H4/H4A no-peer 자함 idle/손상/8Kh32AUTO 비교는 physical state·combatRNG exact다. below elapsed는 측정 관측이며 한 번의 비교로 성능 개선/저하율을 주장하지 않는다.

| 함종 | 시나리오 | H4 ms | H4A ms |
|---|---|---:|---:|
| DDG_119_LATE_FLIGHT_IIA | idle | 654.1 | 629.8 |
| DDG_119_LATE_FLIGHT_IIA | raid | 13009.8 | 11167.7 |
| DDG_119_LATE_FLIGHT_IIA | damaged | 724.8 | 835.7 |
| CG_52_LATE_TICONDEROGA | idle | 793.0 | 638.8 |
| CG_52_LATE_TICONDEROGA | raid | 10724.1 | 11704.2 |
| CG_52_LATE_TICONDEROGA | damaged | 1266.0 | 1461.6 |

자연 Harpoon 검사에는 incoming file/defender identity·강제 명중을 주입하지 않았다.8km CG 사례의 채프4/Phalanx95발·직접 분해는 해당 seed/배치의 결과이며 보편적 요격률이 아니다. H4A clock의 최종 alive 상태와 분해 효과의 보존 시간을 혼동하지 않고, 중간 실제 효과는 별도 자연 표본으로 확인했다. pure association11조건과 baseline-admitted late release8조건을 검사했다.

기존 E close-in의 default simultaneous EW fixture는 unchangedH4에서도CG fire assertions을 실패한다. mechanics 회귀만 EW/기동OFF wrapper로 격리했고 원래 source/evidence를 변경하지 않았다. combined default EW/defense는 자연 Harpoon·natural-ew로 검사한다.

native 검사는 실제 RAF·geometry/damage jobs와 WebGL을 사용하고 큐를 수동 drain하지 않는다. mouse/touch는 viewport emulation이다. 일반 수평선 너머 탐지·원격 FCS·모든 오격/충돌 방지·실장비 doctrine/FPS 인증은 범위 밖이다. 상세 최종 원본별 count/source/report/capture SHA는 verification-summary.json을 따른다.
