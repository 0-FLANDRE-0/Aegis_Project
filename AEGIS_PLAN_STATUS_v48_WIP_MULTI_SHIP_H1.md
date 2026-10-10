# v48 WIP MULTI SHIP H1 — 유틸리티 방어 AI

**판정: H1 방어 utility 구현·직접 검증 완료.** H2 기동/H3 대수상 공격은 후속이다. Actions는 사용 불가로 실행하지 않았으며 로컬 최종 원본을 gate로 사용한다. 원격 반영 결과는 [독립 readback](docs/multiship/H1/evidence/remote-publication.json)과 PR의 실제 상태를 따른다.

## 기준과 결과물

- 기준 G head: `d902d24486918c23d43e3067be16ab03fbaedde2`.
- 작업 branch: `multiship-tactical-h1`, PR base: `multiship-network-g`. main 및 선행 branch를 임의 병합하지 않는다.
- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H1.html): **15,669,638 bytes**, SHA-256 `e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058`.
- decoded main SHA-256: `302352d3dfe47e83fc38d057b002fe46a2e3b12656567dde214561cc28c17105`.
- G HTML/status/SHA/workflow 네 파일은 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_G/`에 이동했다. G HTML SHA `7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7`.
- stable v48: 7,354,511 bytes, SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`, blob `f540b68f138e3ed85614c41f6794be78602229d8`.
- [체크섬](SHA256SUMS_v48_WIP_MULTI_SHIP_H1.txt), [구조/운용](docs/multiship/H1/README.md), [측정 조건](docs/multiship/H1/PERFORMANCE.md), [후속 의존성](docs/multiship/H1/DEPENDENCIES.md), [업로드 계약](docs/multiship/H1/GITHUB_HANDOFF.md).

## 구현

`ShipRuntime.combatSystem.tacticalH1`이 자기 관측·자원·손상으로 WATCH/CONSERVE/DEFEND/SATURATED/DEGRADED를 비교한다. native5Hz에서 한 번씩 계산하고2초 최소 유지/.08 점수차·접근12초 긴급 대응으로 전환 떨림을 제한한다. priority96/log64 상한, RNG/wall clock 비접근이다. 비공개 수치와 doctrine은 SIM-TUNE이다.

승인된 fresh 현지 AIR 파일의 측정 KF·접근 시간/속도·품질·미대응 수와 자기 native 예비탄 이상 재고·SPG 가용/사용 채널·전투/레이더 상태를 사용한다. native 자원 배분 전과 실제 AUTO 추천에 우선순위를 적용한다. 현지 승인 위협3개 이상·선택 SAM 재고<2×위협이면, 접근25초 초과/속도600m/s 미만 표적의 native2발을1발로 배분한다. 고속·급박 위협은 native2발을 유지한다. 진행 중 pending 살보와 사각·NEZ·재고·reserve·FCS·BDA/재교전·근접방어·G 보호/lease·actual release 재검사는 기존 경로다.

현지 위협·anonymous ACTIVE_SEEKER ESM·실제 전파된 shared THREAT는 readiness만 올린다. 수동/그룹 우선권이 없으면 개별 탐색 레이더 및 기존 soft-kill AUTO/EA 허용을 임시 적용한다. 신선한 위협 이후 조용한2초 뒤 요청 baseline으로 복귀한다. 공유/ESM만으로 거리·적성 식별·현지 FCS나 살상 발사를 생성하지 않는다. 적 actual 위치·생존·시커·peer private FCS·자기 비행 탄 truth는 AI 입력이 아니다.

FLEET에 전술 AI ON/OFF와 AI 운용 재개를 추가했다. 자함 기본 OFF로 기존 AUTO를 보존하고 아군/적함 기본 ON이다. 해당 owner AUTO에서만 실행하며 교전 관제는 별도다. 수동 radar/EW와 공동 EMCON이 우선하며 단순 ON/OFF는 수동 hold를 지우지 않는다. AI 운용 재개가 이를 명시적으로 해제한다. group baseline capture 전에 AI 임시 radar를 반환한다. H1은 NAV/FLEET 속력·타각·route를 쓰지 않는다. 적함 운용자 명령은 거부한다. G의 owner 선택 범위도 그대로다: NAV/ARM/CIC/기존3D 버튼은 원래 자함, 선택 owner 운용은 FLEET이다.

fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H1_1`/AI `AEGIS_UTILITY_TACTICAL_H1_1`에는 enabled/manualRadar/manualEw만 저장한다. wrong/missing/extra current fields는 전 owner detached preflight에서 zero writes로 거부한다. G/F/B/no-fleet은 명시 migration한다. utility 판단·priority·log·임시 ownership은 deferred이며 reset/import/deployment/retire에서 비운다. EW/radar 저장은 AI 임시 값 대신 요청 기준값이다. foreign defense AUTO/HOLD의 기존 E 초기화도 유지한다.

모델 assets0~12·원본 프로필/모듈 revision·native 물리/유도/충돌/피해/RF/BDA/사통 커널,60/120/20Hz·공통 world1회·함정별 해상효과·고정 셀·CG RAM0·Harpoon INS/ARH/DL0를 보존한다. pinned G로 build.py를 재실행한 HTML도 최종 bytes와 일치한다.

## 최종 원본 직접 검사

각 보고서의 tested SHA는 위 H1 SHA와 동일하다. superseded fixture/draft와 역사 G897건은 합산하지 않는다. [직접 집계](docs/multiship/H1/evidence/verification-summary.json)에 원본 보고서·SHA·조건·captures를 pin했다.

| 직접 검사 | PASS |
|---|---:|
| 패킹/전체 JS syntax/scope/소유권·정보 경계/native 보존 | 45 |
| utility 정상/금지 실제 발사·salvo·설정/수명주기 | 128 |
| FLEET mouse/touch ON/OFF·재개·owner 조작 | 30 |
| manual/group 우선권·지연/단절·remote-only·손상 | 40 |
| 초기 CMS 파일 없는 물리 Kh-35U 센서→utility→AUTO | 22 |
| 세 함정1/8/16/64×1536full ticks·utility/물리/RNG exact | 120 |
| G/H1 자함 AI OFF idle/피격/Kh-32 8발 exact 회귀 | 30 |
| G 현지 FCS 방어 분담/lease·보호 | 32 |
| Harpoon beam/turn/reacquire·natural route/무DL 보호 | 26 |
| F natural Kh-35U EW·시커 RF | 22 |
| E 실제 defense·금지 발사/BDA/alias·재고 | 76 |
| 실제 pointer/touch/RAF 아군 카메라 | 16 |
| 실제 WebGL3모델/해상효과·피격 hole·import/reset | 38 |
| **합계** | **625/625** |

page/core/runtime/presentation 오류0이다. browser는 local Chromium/Python Playwright, seed1831565813, CPU fixture와 실제 SwiftShader WebGL/RAF다. natural fixture는 terrain bypass/40m Kh-35U 한 발/함종 조합과 초기 파일0 조건이다. native3D는 실제 RAF·geometry job 완료를 기다려 ENTRY/EXIT hole과 복원/owner 폐기를 확인했다. 수동 geometry drain이나 render 물리 적분은 하지 않는다.

단일 seed/대표 시나리오 결과이며 일반 격추율·대규모 함대/mobile hardware FPS나 성능 향상을 주장하지 않는다. DDG 실제 EW 안테나 등록/IFF 재인증 한계는 F/G 그대로다. Actions dispatch나 main/선행 PR 병합은 실행하지 않는다.

## 다음

**H2 기동 utility**에서 관측된 방위/접근·자기 조종 가능 상태/무장 사각으로 침로 유지·선회·속력 후보를 비교한다. 수동 항법 우선권과 명시 AI 재개를 먼저 만든다. 이후 **H3 대수상 공격**은 현지 수상 관측·ROE/보호·별도 승인으로 Harpoon 발사 계획을 연결한다. 현재 대수상 MANUAL-only를 H1에서 해제하지 않는다. 팀 기동·헬기/CEC·RGM-109E Block Va는 후속이다.
