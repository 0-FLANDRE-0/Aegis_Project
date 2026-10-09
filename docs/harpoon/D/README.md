# Harpoon D — 발사관 자동 선택

최신 `Aegis_SIM_v48_WIP_HARPOON_D.html`, 15,283,086 bytes, SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`, main SHA `aeaf6981dc163f3ae3ed67884830bfffb4df50eab83adb381edceda73039e683`. 기준 C는 HTML/status/SHA와 workflow를 같은 bytes로 역사 보존했다. 안정 v48은 변경하지 않았다.

개별 발사관 dropdown을 `AUTO · A1` 같은 자동 선택 표시로 바꿨다. 장전된 관 중 기존 식별·관측 신선도·INS basket·함정 상태·발사대 손상·해면/축 안전 gate를 통과한 후보를 비교한다. 관측 KF의 저장 위치·속도와 등록 자함 관 좌표/축으로 예상 표적 방향을 구하고, 초기 수평 선회각이 가장 작은 관을 고른다. 동률은 profile 순서로 결정하며 표적 truth·탄체 위치·RNG를 읽지 않는다. 이 선택 정책은 게임 운용 편의이며 실제 Mk 141 사통 알고리즘으로 주장하지 않는다.

선호 bank가 소진되거나 손상되면 다른 사용 가능 bank로 넘어간다. 관 ID·물리 위치·loaded 상태는 그대로 유지하고 빈 셀을 압축하지 않는다. cooldown 중에도 다음 적합 관을 표시하되 FIRE는 기존 1.5초 간격을 따른다. 모든 관이 비면 `AUTO · 소진`과 비활성 버튼을 표시한다. **자동 선택이고 발사는 계속 수동 버튼 입력**이다. AUTO/SEMIAUTO 교전권한 금지, UNKNOWN/FRIEND/NEUTRAL 보호를 유지한다.

버튼 입력 때 요청 관을 확정하고 덮개가 열리는 동안 pin한다. 선택 lock을 바꾸거나 관이 손상되어도 도중에 다른 관으로 갈아타지 않는다. 실제 release는 기존 요청 track/관으로 권한·관측·탄약·손상·자세를 다시 검사하고 실패하면 탄약/질량 감소 없이 취소한다. 취소·발사·reset·import 후의 다음 입력은 현재 상태에서 다시 자동 선택한다.

`selectedTubeId`는 기존 inventory 저장 형식 호환용 필드로 유지한다. 옛 저장에 빈 관이 선택되어 있어도 다음 실시간 발사는 자동 정책을 적용한다. CG revision `BUNKERHILL_HARPOON_C_1`/module `HARPOON_C1`, inventory `MK141_INVENTORY_A1` 및 profile 설정은 unchanged다. 명시 관 ID를 넘기는 진단 fire/gate는 기존 fixture 호환을 위해 남겼고 일반 UI에는 개별 선택 입력이 없다.

C의 INS/ARH/무DL CIC·물리 RF·피해·3.2초 booster·모델/nozzle/후연·8관 등록 asset/renderer와 DDG 미설치를 보존했다. 선언한 D 선택/UI/version diff를 역적용하면 C main과 outer HTML은 byte 동일이다. [C의 별도 검증 기록](../C/README.md) 155건을 D 직접 검사에 합산하지 않았다.

## 직접 검증

같은 최종 HTML SHA의 **67/67 PASS**, seed `0x6d2b79f5`.

| Suite | 통과 |
|---|---:|
| static | 31/31 |
| selection | 24/24 |
| clock | 3/3 |
| native | 9/9 |

정적 검사는 모든 embedded JS syntax·14 record integrity·exact 재빌드·원본 assets·C의 무관한 source/outer HTML 보존을 확인했다. selection은 실제 ARM 버튼 8회와 전체 fixed tick/radar 갱신으로 8개 관의 자동 사용·bank 소진 전환·5520kg 제거를 확인한다. 관측 방향 반전·손상 fallback/실제 release 취소·pending pin·저장/reset·권한·DDG는 별도 결정적 fixture다. 시간 진행/selector 갱신만으로 발사하지 않고 RNG도 소비하지 않는다.

clock은 각 128틱의 전체 accumulator를 1·8·16·64×로 실행해 auto-selected tube·비행/재고/RNG가 exact임을 확인했다. 전체 비행/명중을 반복 검사한 것은 아니다. native는 640×480 ARM/VLS 실제 버튼 두 번·전체 clock/RAF·두 관 덮개·draw 지속·UI fit/NO DL·RESET을 확인했다. 수동 physics tick/geometry queue 진행 0, core/page/console·simulation/presentation fault 0. SwiftShader이며 사용자 장치 FPS를 주장하지 않는다. 원자료 candidate.html은 전달 D와 bytes 동일하다.

이번 단계는 작은 선택/UI 변경이다. C의 전체 INS/ARH·명중·RF/CIC 회귀 155건과 B의 전체 모델/후연 검사를 D에서 모두 재실행하지 않았다. 원격 Actions/PR/병합은 미실행이며 [원격 인계](GITHUB_HANDOFF.md)를 따른다.

## 후속 장거리 별도 검사

[REPORT](../long-range/D/REPORT.md)에 동일 D 코드의 60~124km 시험/제한/실패를 추가했다. 정상 100·120·124km 발사 차단과 독립 비행124km/15kn의 빗나감을 재현했다. 자동 관 선택67/67와 별개이며 전체 장거리 PASS나 완성으로 쓰지 않는다. 다음 수정은 장거리 표적 예측 불확실성/탐색 basket/발사 조건과 moving TRACK/COAST 종말 안정성이 우선이다. HTML·비행 튜닝은 이번 검증에서 변경하지 않았다.
