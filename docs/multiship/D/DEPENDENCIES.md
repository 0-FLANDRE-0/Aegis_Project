# D 이후 단계

이번 단계는 owner 무장 실행과 실제 양방향 접촉을 만들고 shadow 판단만 실행한다. 다음에는 기존 AUTO controller의 결정을 이 포트에 연결한다.

| 순서 | 구현 | 완료 기준 |
|---|---|---|
| 5C 방어 AI | measured-track 위협, acceleration/CPA, 식별·ROE, NEZ/살보·채널·사각·탄약 | fresh authorized만 실제 발사. unknown/friend/neutral/stale/offline은0회. 전부 owner context |
| 5D 재교전·BDA | 효과 보고, 후속 coherent 측정, alias 이관, 지원 해제 | 실제 alive truth로 격추 확정하지 않음. 중복 살보·유령 조명·예약 방지 |
| 6 EW | owner emitter/receiver RF·ESM, Nulka/SRBOC, 수신기별 기만/quality | 자함 CIC에는 관측 방위/오차·track 상실만 표시. 상대 EW 토글/효과/잔탄 truth 복사 금지 |
| 7 기동·공격 AI | 관측 surface threat·회피·자원/ROE·Harpoon mission | 자기 관측/발사 전 추정으로 계획. Harpoon 무DL 유지 |
| 헬기 | 모델 분리, 항공 물리·탐지·지연/단절 보고 | C offboard 포트로 noisy measured fix 전달. 고도/수평선/지형·scan 실제 적용 |
| 통합/성능 | 다수 탄·피격·reset, CPU/GPU/heap | 먼저 profiler 근거. 기존 fixed/침수/hydro 주기 유지 |

active AI를 켜기 전에 원본 WIP118/WIP119의 BDA·alias·fire-authority/lifecycle을 owner 상태에 결속하고, 함정별 자동 release 승인과 거부를 함께 시험해야 한다. shadow의 acceleration=0·advisory 평가를 완성된 교전 AI로 취급하지 않는다. 현재 외형 접촉은 structural layout union이고 얇은 외부 장비 정밀 contact는 후속 범위다.
