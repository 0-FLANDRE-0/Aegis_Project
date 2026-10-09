# Harpoon E — 발사 전 경유점과 마지막 점 통과 후 탐색

최신 `Aegis_SIM_v48_WIP_HARPOON_E.html`, 15,285,590 bytes, SHA `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`, main SHA `11cf8d757821b8601da5a3a50153666e48524ea31a33de1a88d7a11a72794067`. D HTML/status/SHA와 workflow는 같은 bytes로 archive/역사 지원에 보존했다. stable v48과 원본 모델/발사관 asset, 3.2초 부스터·분리·후연·함정/피해 renderer는 유지했다.

## 조작

벙커힐 ARM → VLS의 HARPOON FIRE 아래 **웨이포인트 지정**을 누른다. CIC 탭/클릭으로 순서대로 최대 8점을 넣는다. 주황색 H-WP 점선은 발사 전 입력이고 함선 NAV 항로·락온 커서와 별도다. 드래그/휠/두 손가락 확대는 점을 추가하지 않는다. 지정 중 버튼은 **웨이포인트 해제**이며 누르면 초안을 지우고 AIM 락온 커서 조작으로 돌아온다. 클릭은 버튼의 native click 한 경로로 처리해 기존 bindPress의 220ms 중복 억제가 빠른 해제/재지정을 삼키지 않게 했다.

**마지막 점은 목표 함선 좌표가 아니라 탐색 시작점**이다. 마지막 진입 방향 전방 8km를 탐색 중심으로 잡고 반경 4km의 고정 검색 영역을 입력 표식으로 표시한다. 따라서 예상 표적보다 약 8km 앞에서 탐색을 시작하도록 마지막 점과 최종 진입 방향을 잡는다. 좌표 탐색 발사는 표적 트랙 없이도 수동으로 입력할 수 있다. 선택된 보호 수상 파일 FRIEND/NEUTRAL/UNKNOWN이 있으면 거부하며 AUTO/SEMIAUTO 교전으로 발사할 수 없다. 시커에는 피아 식별이 없고 검색 영역의 물리 반향으로 동작한다.

경유점을 넣지 않으면 기존의 신선한 HOSTILE/TRAINING_TARGET 관측 트랙 저장 → INS 예측 → 거리 기반 ARH 발사를 그대로 사용한다. 경유점이 있는 발사는 **고정 좌표 검색 계획**이며 선택 표적의 truth 위치/속도나 장거리 가짜 관측을 가져오지 않는다. 표시 READY는 수동 release gate 통과이며 ARH 명중 보장이 아니다.

발사 버튼을 누르면 자동 선택 관과 전체 경로/검색 중심을 freeze하고 0.18초 동안 덮개를 연다. 실제 release에서 요청 관·재고·손상·함정/축/해면 안전·입력 예산·요청한 보호 트랙 권한을 재검사한다. 도중 경로 편집은 막고 실패하면 탄약/질량 감소 없이 취소하며 초안을 보존한다. 성공할 때 초안과 지정 상태를 지운다. 다음 탄의 새 경로는 앞서 발사한 탄을 바꾸지 않는다. 관 ID/슬롯은 고정이며 자동 관 선택·1.5초 간격·690kg 재고 제거를 유지한다.

## 비행과 사거리

세계 탄체가 immutable program과 실행 index를 소유한다. 권위 60Hz tick에서 **INS 위치**로 경유점을 진행하고 현재 점을 향해 기존 4G/aero 제한 내에서 선회한다. 중간 점은 200m flyby capture 또는 500m 통과 corridor를 허용한다. 마지막 점은 근접만으로 완료하지 않고 마지막 leg의 수직 평면을 INS 궤적으로 통과해야 한다. 부스터 연소 중에는 점을 넘기지 않는다. 마지막 통과 전 ARH OFF, 통과 후 SEARCH → 3회 상관 ACQUIRE → TRACK/COAST를 적용한다. receiver LOS/beam/SNR·±45° az/±30° el gimbal·좌우 sweep·lock loss 재탐색과 실제 선체 swept contact/피해는 유지한다. 물리 position을 INS waypoint 조건으로 읽지 않는다.

공개 range 124km와 secondary 약140km는 profile evidence에 분리해 보존한다. 사용자 범위에 맞춰 **SIM-TUNE 계획 예산 140km**, fuel flow 0.225kg/s/110kg로 설정했다. 전체 점 간 거리 + 전방 검색 8km + 선회 예비 2km를 합쳐 초과 계획을 거부하고 점 간격은 2km 이상이다. 큰 우회·급격한 선회·표적 이동/재탐색은 추가 연료를 쓰므로 계획 예산은 모든 경로/해상 상태에서 실제 도달 보증이 아니다. 근접 점의 순간 방향 변경이나 정확 좌표 teleport는 없다.

해면과 비슷한 익명 반향의 거짓 상관을 줄이기 위해 **관측 vertical extent ≥3.5m / Doppler spread ≤2.5m/s**를 SIM-TUNE했다. 과거 1.4m/4m/s에서 같은 경로 시험 6건 중 접촉2·miss4였고 수정 후 같은 seed/scene/program의 6건은 접촉했다. source-kind/소속/target ID로 반향을 거르지 않는다. 이는 작은/낮은 선박과 거친 해면에서 탐지를 떨어뜨릴 수 있는 단순한 측정 필터이며 실제 하푼 처리 제원으로 주장하지 않는다. 알파베타 velocity filter, fuze와 피해 판정을 강제 명중으로 바꾸지 않았다.

DL은 계속 없다. CIC의 H-WP는 초안만 그리고 release 직후 사라진다. 실제 탄의 경유점 진행/INS/시커/생존/명중을 ship UI에 전달하지 않는다. 함정의 측정 RF 파일과 발사 직후 알려진 경로/관 정보로 초기 익명 상관을 수행하고 이후 관측 연속성으로만 FRIEND 표시한다. EMCON/관측 만료 뒤 위치가 없어져도 탄은 자체 항법/시커를 계속 사용한다. 3D는 기존 observer view다.

CG revision `BUNKERHILL_HARPOON_E_1`, module `RGM84D_BLOCK1C_E1` / weapon revision `HARPOON_E1`; inventory `MK141_INVENTORY_A1`은 유지하고 C/B/A/G/D legacy revision을 명시 허용한다. 초안·pending·비행·launch knowledge는 transient다. snapshot capability에 `harpoonPrelaunchRouteAndFlight`가 deferred임을 명시하고 정상 import/reset 때 지운다. 전체 preflight 실패 정책은 unchanged다. DDG-119에는 Mk141/경유점 UI를 설치하지 않는다.

## 직접 검사

동일 최종 SHA **178/178 PASS**. A/B/C/D/K 역사 건수는 합산하지 않는다.

| Suite | 통과 |
|---|---:|
| static | 32/32 |
| guidance | 45/45 |
| selection | 24/24 |
| routes | 26/26 |
| knowledge | 22/22 |
| clock | 4/4 |
| range | 14/14 |
| native | 11/11 |

static은 모든 14 records integrity/JS syntax·재현 build·선언 diff 역적용 D main/outer HTML exact·원본 asset exact·knowledge/route boundary를 검사한다. 기존 D selection24를 E bytes로 실행했다. guidance45는 실제 embedded functions의 INS·짐벌/beam·검색/획득/추적/손실·측정 필터·최종 통과와 physical jump 분리를 검사한다. routes26은 실제 버튼/지도 mouse/touch·cancel/기존 cursor·불변 pending/탄 간 독립·총거리/권한/손상·C 저장/reset/DDG다. knowledge22는 실제 RF radar 파일/CIC cyan·EMCON/블라인드/impact 무telemetry와 경로탄의 관측 상관이다. clock4는 1/8/16/64× 각3072 full fixed ticks에 경유점 진행/시커·비행/재고/RNG exact다.

native11은 640×480에서 실제 경로 버튼과 CIC 클릭으로 2탄을 지정·발사하고 전체 native RAF/clock·정확한 관 덮개·3.2초 부스터 분리·draw 지속·초안 정리/RESET·controls fit·NO DL를 검사했다. 수동 physics ticks/geometry queue 진행0, core/page/console/runtime/presentation faults0. Chromium SwiftShader이고 사용자 장치 FPS를 주장하지 않는다.

range14는 별도 offline fixture다. 원본 E main에 **scenario/probe 진단 bridge만** 추가하며 live gate/INS/비행/RF/시커/contact를 override하지 않는다. synthetic target track/발사 gate 우회/발사 뒤 함정 유도 업데이트0. 선체210m 실물 hulk, 단일 seed `0x6d2b79f5`, terrain diagnostic bypass/open sea, 실제 weather/물리 RF/표적 이동·침수/선체 contact를 사용했다. focused 60Hz environment+target+ordnance이며 전체 함정 subsystems/native RAF 장거리 인증은 아니다. global RNG 불변은 각 fixed stage 내 범위다.

| 표적 km | 속력 kt | 계획 km | SEARCH s | 접촉 s | 실제 비행 km | 잔여 fuel kg | 결과 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 120 | 0 | 122.888 | 396.050 | 423.450 | 120.960 | 15.440 | SURFACE_CONTACT |
| 120 | 15 | 122.888 | 396.050 | 425.733 | 121.616 | 14.926 | SURFACE_CONTACT |
| 124 | 0 | 126.857 | 409.783 | 437.183 | 124.929 | 12.350 | SURFACE_CONTACT |
| 124 | 15 | 126.857 | 409.783 | 439.633 | 125.633 | 11.799 | SURFACE_CONTACT |
| 130 | 0 | 132.815 | 430.417 | 457.800 | 130.888 | 7.711 | SURFACE_CONTACT |
| 130 | 15 | 132.815 | 430.417 | 460.483 | 131.658 | 7.108 | SURFACE_CONTACT |

**6/6은 이 6개 선언 장면의 물리 접촉 결과이고 일반 명중률/최대140km 인증이 아니다.** 추가 empty-water 장면은 경로/SEARCH가 진행되나 확정 TRACK/강제 명중 없이 연료 소진 후 SEA_IMPACT로 끝났다. [최종 range](evidence/range.json)와 [필터 전 예비 결과](evidence/preliminary-before-filter.json)를 구분한다. 후자는 전달 파일 검사 PASS 집계에 넣지 않는다.

기존 D 장거리 결과의 track-only INS prediction basket 실패를 제거한 것으로 주장하지 않는다. E track-only gate도 target velocity/motion prediction uncertainty를 유지한다. 경유점 모드는 추정 트랙을 장거리로 연장하는 대신 고정 검색 영역을 수동 입력하므로 120~130km 발사를 별도 검증했다. 실제 offboard targeting/DL/전 표적·해상조건·8점 급선회 최대거리 인증은 범위 밖이다.

## 인계

원격 native 검사는 소프트웨어 WebGL의 느린 실행을 허용하도록 전체 벽시계 한도 900초를 사용하고 15초 간격으로 프레임·물리 틱·발사 상태를 기록한다. 실제 입력·전체 RAF/고정 틱·4.2초/0.3초 비행·11개 판정 조건은 그대로이며 수동 물리/geometry queue 진행은 하지 않는다. 초기 180초 비행 대기 시간 초과 기록은 PR의 첫 Actions 실행에 보존한다. 같은 HTML의 진단 로컬 재실행은 11/11을 통과했다. 최종 원격 결과는 PR의 현재 head를 따른다.

사용자가 **E HTML 하나**를 업로드했고 원격 bytes/SHA/parent/Git blob 및 무결성 Actions를 확인했다. 이 revision은 작은 support/상태/manifest·K 기존 blob archive·E 전체 workflow를 포함한다. 큰 A/B/C/D 로컬 archive HTML은 재업로드하지 않고 K+작은 A/B/C/D/E 모듈로 E까지 byte exact 재생성한다. [GitHub 인계](GITHUB_HANDOFF.md), [업로드 검증](evidence/remote-publication.json), [PR #44](https://github.com/0-FLANDRE-0/Aegis_Project/pull/44)를 따른다. 전체 기능 CI는 E workflow의 해당 head 결과를 기준으로 하며 업로드 무결성 검사와 구분한다. 전달 전 evidence와 원본 ZIP은 다시 작성하지 않는다.
