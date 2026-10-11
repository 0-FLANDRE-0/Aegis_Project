# v48 WIP MULTI SHIP H2 — 관측 기반 기동 AI

**판정: H2 기동 utility 구현·최종 원본 직접 검증 완료.** H3 대수상 공격은 후속이다. GitHub Actions는 사용자 조건으로 dispatch하지 않았고 로컬 최종 원본을 gate로 사용한다. 원격 결과는 [독립 readback](docs/multiship/H2/evidence/remote-publication.json)과 PR의 실제 상태를 따른다.

## 기준과 결과물

- 기준 H1 head: `43021f9693dc0500b5f2def531ec5d0d9e17bf0b`.
- 작업 branch: `multiship-tactical-h2`, PR base: `multiship-tactical-h1`. main/선행 branch는 병합하지 않는다.
- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H2.html): **15,675,514 bytes**, SHA-256 `522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1`.
- decoded main SHA-256: `80ecfe1be494132521b6f6e1327647f50608c92da98fef235f541ed657926865`.
- H1 HTML/status/SHA/workflow 네 파일은 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_H1/`에 이동했다. H1 HTML SHA `e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058`.
- stable v48: 7,354,511 bytes, SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`, blob `f540b68f138e3ed85614c41f6794be78602229d8`.
- [체크섬](SHA256SUMS_v48_WIP_MULTI_SHIP_H2.txt), [운용/정보 경계/튜닝](docs/multiship/H2/README.md), [측정 조건](docs/multiship/H2/PERFORMANCE.md), [후속 의존성](docs/multiship/H2/DEPENDENCIES.md), [업로드 계약](docs/multiship/H2/GITHUB_HANDOFF.md).

## 구현

함정별 `combatSystem.maneuverH2`가 H1의 승인된 fresh 현지 AIR 측정과 자기 조종/장비 상태를 사용해 침로 유지·좌/우30/60도·가속·감속·정지의8개 후보를 비교한다. native5Hz, 첫 판단 즉시·이후3초 유지/.04 margin·접근12초 긴급 대응, 위협8/수상 교통16/로그64 상한은 SIM-TUNE이다. 고정 mission heading으로 선회 목표 누적을 막는다.

최대30초/6자세의 조종 근사로 무장 사각 기회·CPA 여유·노출 방향과 선회/속력 비용·자기 SPG 지원 손실을 비교한다. 기존 SPG-62/CIWS의 health·train/elevation·CG model 차폐/DDG 접선 사각을 재사용한다. native 기관 단계와 타각 명령만 쓰며 실제 heading/speed/position은 기존120Hz 힘·타율·기관·손상 물리로 변화한다. 후보 예측은 물리 권위 또는 실제 전술 doctrine이 아니다.

실제 chart polygon과 신선한 현지 SURFACE KF/실제 수신된 SELF 항법 보고로 위험 후보를 제외한다. 모두 차단되면 SAFETY_HOLD로 native 감속을 명령한다. 제한된 표본 예측과 유한한 제동 거리이므로 보편적 충돌 회피를 보장하지 않는다. stale/coast/protected/UNKNOWN/FRIEND/NEUTRAL/훈련 표적·수상 위협은 기동 입력에서 제외하며 shared THREAT/ESM-only는 H1 readiness에만 사용한다. 적 truth 위치·생존/시커·peer private FCS·자기 비행 탄 truth를 읽지 않는다.

FLEET의 **기동 AI ON/OFF / 기동 AI 재개**로 선택 함정을 조작한다. 자함 기본OFF·아군/적함 기본ON이며 전술 AI ON + 해당 owner AUTO가 필요하다. NAV 타각/기관·지도 route 조작과 FLEET 항법은 owner별 지속 manualNav 우선권을 가진다. ON/OFF는 이를 지우지 않고 기동 AI 재개가 명시 인계한다. 레이더/EW 수동 hold는 보존한다. H1 AI 운용 재개는 항법 hold를 해제하지 않는다. MANUAL/SEMIAUTO/HOLD·masterOFF·기동OFF·offline은 임시 항법을 반환한다. NAV/ARM/CIC/기존3D는 원래 자함, FLEET은 선택 friendly owner라는 G 계약을 유지한다.

위협이 조용한4초 뒤 native 타로 RECOVER하고 임무 침로에 돌아오면 원래 요청 orders를 반환한다. freshness2초와 실제 선회 시간은 추가된다. 순간 침로/속도/위치 복원은 없다. 항로 진행/도착은 기존 경로를 유지하며 임시 소유 중 route가 기관/타를 덮어쓰지 않는다.

fleet schema `AEGIS_NAVAL_PHYSICAL_FLEET_H2_1`, 설정 `AEGIS_MANEUVER_UTILITY_H2_1`의 enabled/manualNav bool을 전 owner detached preflight한다. current 설정 누락/잘못된 타입/추가 필드·invalid native 기관 metadata는 zero writes로 거부한다. H1/G/F/B/no-fleet은 명시 migration하고 기존 manual flags를 항법 hold로 승계한다. 목표/후보/점수/명령 소유권은 deferred다. reset/import/deployment/retire에서 비운다. save는 임시 AI 명령 대신 원래 요청 orders를 내보내고 실제 물리 상태는 보존한다.

assets0~12·원본 모델/profile revision·native 유도/물리/충돌/피해/RF/ROE/FCS/NEZ/BDA/예비탄·G 보호/방어 분담,60/120/20Hz·함정별 해상효과·고정 셀·CG RAM0·Harpoon INS→ARH/DL0를 유지한다. H1에서 exact rebuild한 HTML도 최종 원본 bytes와 일치한다.

## 최종 원본 직접 검사

모든 tested SHA는 위 H2 SHA다. [직접 집계](docs/multiship/H2/evidence/verification-summary.json)가 보고서·현재 검사 소스 SHA·captures를 pin한다. superseded draft/실패한 시험/역사 H1·G 결과는 합산하지 않는다.

| 직접 검사 | PASS |
|---|---:|
| `static` | 47 |
| `maneuver` | 132 |
| `guards` | 44 |
| `ui-h2` | 40 |
| `natural-h2` | 30 |
| `clock` | 152 |
| `baseline` | 30 |
| `tactical` | 128 |
| `policy` | 40 |
| `ui-h1` | 30 |
| `cooperation` | 32 |
| `harpoon` | 26 |
| `camera` | 16 |
| `defense` | 76 |
| `natural-ew` | 22 |
| `native` | 38 |
| **합계** | **883/883** |

page/core/runtime/presentation 오류0. 초기 CMS 파일0인 실제40m Kh-35U에서 native 탐지→H1/H2→native 방어를 확인했다. 실제 타/선회/병진, 수동 항법과 복원/invalid import, chart/관측 교통·사각·손상, 세 척1/8/16/64×1536full ticks 결정성, H1/H2 기동OFF 물리·재고/RNG exact, 실제 pointer/touch/RAF camera와 WebGL 피격 ENTRY/EXIT hole·owner 폐기/복원을 검사했다. 수동 geometry drain/render 물리 적분은 하지 않았다.

단일 seed와 대표 시나리오·CPU/SwiftShader 조건이며 일반 격추율·대규모 함대/mobile hardware FPS·성능 개선 또는 실제 전술 doctrine 인증이 아니다. DDG EW 등록/IFF 재인증의 F/G 한계는 유지한다. 새로운 Actions dispatch·main/선행 PR 병합은 실행하지 않는다.

## 다음

**H3 대수상 공격**: 현지 SURFACE 관측·식별/ROE·아군 보호·별도 공격 동의와 사거리/발사대/route/uncertainty 검사로 하푼 발사 계획을 연결한다. 현재 대수상 MANUAL-only gate를 임의 해제하지 않는다. 팀 기동·헬기/CEC·RGM-109E Block Va는 후속이다.
