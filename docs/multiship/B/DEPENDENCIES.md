# 3단계 이후의 연결 지점

이번 B는 A의 독립 runtime을 실제 세계에 배치하고 항해·피해·침수·승조원·질량·동역학·rescue와 원본 3D 모델을 실행한다. shared world에는 실제 navalShips가 들어가며 merchant/hulk 대체 객체를 만들지 않는다. 기본 적함 없음의 자함 경로는 A와 비교한다. A의 당시 계획은 [A/DEPENDENCIES.md](../A/DEPENDENCIES.md)에 보존한다.

| 다음 단계 | 연결할 경로 | 완료 조건 |
|---|---|---|
| 4. 함정별 관측 | radar/aux measurements, TrackStore, observer별 RNG | 양 함종 면 배치·사각·지형/지평선·해면·scan budget으로 익명 plot 생성. 트랙에는 실제 ship ID/위치 주입 금지. player CIC는 player 관측만 읽음 |
| 5. 양방향 무장 | sourceShipId, owner FCS/SPG/탄창·셀, 실제 피해 대상 routing | owner command 권한·사각·채널·질량 확인, 기존 contact/impact를 대상 runtime에 한 번 전달. CG SeaRAM/DDG Harpoon 생성 금지 |
| 6. EW와 CIC | emitter/receiver별 RF, world Nulka/SRBOC와 관측 | ESM 방위/오차·관측 품질·기만 관측·coast만 표시. 상대 jammer ON/정확한 효과/잔탄 truth 노출 금지 |
| 7. 적 AI | 관측 facade와 허용 command API | tracks·공분산·age·재고·사각·채널·피해·권한으로 방공/회피/EW/공격 결정. physicalWorld와 진단 truth를 AI에 제공하지 않음 |
| 8. 통합·성능 | 두 함정/다수 탄/EW/동시 피해/reset | 모든 DDG/CG 조합, 동시 침몰/수명주기, 실제 hardware FPS/heap/GPU 측정 |

현재 공개 UI는 배치/카메라와 기존 자함 운용이다. 적함을 자함으로 선택해 교대 조종하는 UI, 적함 원격 무장 발사, 편대 통신/AI는 이번 범위에 포함하지 않는다. fixed cadence를 낮추거나 renderer에서 물리를 진행하는 최적화는 사용하지 않는다. 현재 충돌은 bounded footprint 근사이며 파도에 따른 정밀 수중 접촉, swept 3D shell 충돌과 좌초 외판 파괴는 추가 작업이다.

native 검사는 실제 원본 모델, 확인된 입구·출구 관통구의 mesh commit, 후속 RAF/draw/tick와 reset disposal을 검사한다. 전투 flight/contact routing은 5단계이므로 diagnostic physical probe를 사용한다. SwiftShader 결과는 모바일 hardware FPS와 구분한다.
