# E 이후 단계

5C 방어 AUTO와 5D BDA/alias를 owner 무장에 결속했다. 항공기 스폰 선택도 완료한다. 다음 큰 범위는 receiver별 EW다.

| 순서 | 구현 | 완료 기준 |
|---|---|---|
| 6 EW | 독립 emitter/receiver RF·ESM, Nulka/SRBOC와 inventory | 자함 CIC에 관측된 방위·오차·quality·coast를 표시. 상대 EW 토글/잔탄/효과 truth 복사 금지 |
| 7 공격/기동 | 관측 surface threat·회피·자원/ROE·Harpoon mission | 자기 측정/발사 전 추정으로만 계획. Harpoon 무DL 유지 |
| 헬기 | 원본 모델 분리, 항공 물리·센서·지연/단절 보고 | C offboard 포트에 noisy measured fix. 고도/지평선/지형·scan 실제 반영 |
| 센서 검토 | CG 저고도 Harpoon 접근의 수신/plot/확인 경계 분석 | 별도 공개 스펙/SIM-TUNE 근거와 측정 증거 후 조정. AUTO 편의를 위한 truth 보강 금지 |
| 통합/성능 | 다수 탄·피격·reset, CPU/GPU/heap·장비별 geometry | profiler 근거로 병목 수정. 60/120/20Hz 유지 |

현재 선체/구조물 layout union 외형 접촉, 얇은 외부 장비별 정밀 contact, 다수 함정 FPS는 잔여다. 기본 방어 AUTO의 실제 발사와 전체 조건에서의 요격 성공은 별개다. CG 자연 Kh-35U/Harpoon과 DDG 실탄 결과의 한계를 E README에 기록한다.
