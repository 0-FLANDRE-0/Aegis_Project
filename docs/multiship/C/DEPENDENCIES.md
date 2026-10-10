# C 이후 단계

4단계의 실제 함정별 관측·독립 file과 미래 외부 관측 수신 포트를 연결했다. 헬기는 이후에 이 포트를 이용해 넣을 수 있다. 먼저 같은 월드 함정 간 무장·피해를 연결하고, 그 위에 전자전과 관측 기반 판단을 올린다.

| 단계 | 연결할 부분 | 완료 기준 |
|---|---|---|
| 5. 양방향 무장 | sourceShipId/owner FCS·SPG·셀·탄창·사각과 실제 naval target routing | 양 함종의 허용 무장만 발사, release 권한 재검사, 실제 flight/contact/피해를 대상 runtime에 한 번 전달. CG SeaRAM/DDG Harpoon 금지 |
| 6. 수신기별 EW·CIC | emitter/receiver RF·ESM·Nulka/SRBOC | 측정 방위/오차·track quality·기만/상실만 표시. 상대 jammer ON/실제 효과/잔탄 truth를 화면에 복사하지 않음 |
| 7. 적 AI | observerFacade 추정치와 검증된 owner command API | 탐지·식별·권한/재고·채널·사각·피해를 바탕으로 요격/회피/EW/공격. world truth/진단을 AI에 제공하지 않음 |
| 헬기 | 원본 모델 분리, 항공 runtime, 실제 센서/통신 | 높이/지형/지평선·scan·오차·지연·끊긴 링크가 있는 측정 보고. 포트 자체는 센서가 아니며 탐지 데이터 생성도 아님 |
| 8. 통합·성능 | 다수 탄·동시 교전/피해·EW·reset | 함종 조합/생명주기와 실제 기기 FPS·heap/GPU 측정 |

현재 배치 함정은 실제 항해·물리 피해·센서 탐지를 수행한다. 요격/대함 공격·상대 EW·자동 판단은 미연결이다. CIC에는 상대 ship model 이름이나 truth 정체를 자동 표시하지 않는다. 기존 MANUAL 자함 무장과 HULK·merchant 표적의 동작은 유지한다.

5단계에서 seeker의 새 naval reflector를 켤 때 실제 contact routing도 같이 검증해야 한다. 발사한 Harpoon에 DL을 추가하거나 외부 관측 포트에서 탄의 위치를 받는 방식으로 연결하지 않는다. 장거리 표적 cue는 헬기 자체의 noisy measured fix를 통해 들어오며 직접 truth 지정은 금지한다.
