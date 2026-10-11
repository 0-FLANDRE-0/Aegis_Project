# v48 WIP MULTI SHIP H3 — 관측 기반 대수상 공격 AI

**판정: H3 구현·최종 원본 직접 검증 완료.** 전술 AI/owner AUTO와 별도 표적 공격 동의 아래 native 하푼 발사를 계획한다. 팀 전술·헬기/초수평선·RGM-109E Block Va는 후속이다. GitHub Actions는 dispatch하지 않고 로컬 최종 원본을 gate로 사용한다. 원격 결과는 [독립 readback](docs/multiship/H3/evidence/remote-publication.json)과 실제 PR 상태를 따른다.

## 기준과 원본

- H2 final 기준: `59fad37cc170c760c1659b916febc168021a31b4`.
- branch `multiship-tactical-h3`, PR base `multiship-tactical-h2`. main/선행 PR 병합은 실행하지 않는다.
- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H3.html): **15,683,482 bytes**, SHA-256 `0a9626535c209d8ad4e5a9b5262bd826d8ede8df928562534ba6c44b5673d178`.
- decoded main SHA-256 `904116a4d73455b5a12d4c800afea30fac9e05415d81c0f1c16ce3f37cba38f4`. packed record13만 변경하며 source models/assets0~12는 exact다.
- H2 HTML/status/SHA/workflow 네 파일은 original bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_H2/`에 보존한다. H2 HTML SHA `522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1`.
- stable v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`, blob `f540b68f138e3ed85614c41f6794be78602229d8` 유지.
- [운용/권한/정보 경계](docs/multiship/H3/README.md), [성능/검증 조건](docs/multiship/H3/PERFORMANCE.md), [남은 단계](docs/multiship/H3/DEPENDENCIES.md), [직접 업로드](docs/multiship/H3/GITHUB_HANDOFF.md), [SHA](SHA256SUMS_v48_WIP_MULTI_SHIP_H3.txt).

## 구현

`combatSystem.attackH3`가 owner별 설정·1/2발 동의·계획·pending capability·발사 접수 이력을 소유한다. 자함/아군함 기본OFF, 적함 기본ON이며 H1 전술 AI ON + owner AUTO에서 판단한다. 현지 fresh confirmed SURFACE KF와 명시 HOSTILE 식별, 별도120초 운용자 동의가 필요하다. UNKNOWN/ASSUMED_HOSTILE/TRAINING/FRIEND/NEUTRAL은 자동 공격하지 않는다. 동의는 파일 객체와 owner를 고정하고 번호 재사용/alias로 승계하지 않는다.

FLEET **공격 AI ON/OFF·하푼1/2발·선택 표적 공격 동의·공격 동의 취소**를 추가했다. 새 동의/ON/OFF 변경은 이전 동의를 지우고 actual release만 발수를 차감한다. OFF·철회·MANUAL/HOLD·masterOFF는 개방 중 AI 발사를 취소한다. 수동 발사와 수동 waypoint 초안/편집이 우선이며 다른 owner의 설정·동의는 복사하지 않는다. DDG의 하푼 미장착을 반영한다.

native5Hz, 파일96/계획16/protected64/log64,1~2발 살보·예비2발·적함90초 재평가·선회120도 상한은 SIM-TUNE이다. 기존 native 자동 튜브 선택, readiness·4~140km·예측 basket·손상·발사 자세 gate를 유지하며 CG 등록 geometry의 초기24m departure axis, measured CV direct route/거리 budget·실제 chart polygon crossing/100m coast 여유, observed/received protected SURFACE/SELF의 경로·4km종말 search basket을 검사한다. stale/invalid/capacity초과는 보류한다. 긴급 대공 방어는 우선한다.

정확한 canonical capability의 H3 typed release만 허용하고 일반 AUTO/SEMIAUTO·수동 좌표 search·Standard/ESSM의 대수상 MANUAL-only gate는 그대로다. native0.18초 문 개방과1.5초 release 간격, actual release 직전 식별/동의/freshness·재고/손상/자세/route/protection 재검사를 유지한다. 실제 heading/speed/position이나 physics를 직접 쓰지 않는다.

발사 시 관측을 고정한 INS cue→독립 ARH SEARCH/TRACK, 부스터3.2초·분리/날개/화염/후연·RF/ECM·피해 물리는 그대로다. DL0: AI는 자기/아군/적 하푼의 위치/시커/생존/명중 truth를 읽지 않는다. CIC는 실제 radar 및4초 이내 measured coast에서만 위치를 보이며 blind 후 위치가 사라진다. 발사 접수 이력은 명중 통보가 아니다.

적함은 자기 관측 파일이 HOSTILE로 명시 식별된 경우 mission 권한으로 최대2발을 계획한다. 현행 IFF는 아군 인증이며 무응답은 적성 증거가 아니다. 따라서 자연 UNKNOWN의 첫 공격은 보류된다. 자연 시험의 적성 designation은 실제 관측 후 명시 scenario 명령이다. 미식별 대상의 자동 공격/hostile intent 판정은 후속이며 이번 완료 범위로 주장하지 않는다.

current fleet schema `AEGIS_NAVAL_PHYSICAL_FLEET_H3_1`, attack `{schema,enabled}`만 저장한다. 전 owner detached preflight 후 writes하고 누락/타입/추가 필드는 atomic 거부한다. H2의 기존 tactical/maneuver/network 필수 설정도 지킨다. H2/H1/G/F/B/no-fleet은 명시 migration하며 새 공격 권한OFF; pending legacy deployment도 enemy 권한을 자동 획득하지 않는다. 동의·계획·capability·이력은 deferred이고 import/reset/deployment/retire에서 비운다.

기존 H1/H2 기동/방어·G 측정 공유/보호·고정 셀·CG RAM0·공통60/120/20Hz·RF/물리/유도/피해·해상효과/3D를 유지한다. 직접 CV 경로와 유한한 보호 관측으로 모든 곡선 비행/미관측 선박/급기동의 오격을 보장하지 않는다. 장거리 moving cue는 기존 acquisition basket에서 거부될 수 있고 헬기/초수평선 firing은 이번 범위에 없다.

## 최종 원본 직접 검증

[집계](docs/multiship/H3/evidence/verification-summary.json)는 각 suite의 최종 tested SHA, 실제 검사 소스 SHA, report/capture SHA를 pin한다. 실패/폐기 draft·역사 H2/G 시험은 합산하지 않는다.

| 직접 검사 | PASS |
|---|---:|
| static | 55 |
| attack | 195 |
| attack-guards | 20 |
| ui-h3 | 42 |
| surface | 18 |
| clock | 184 |
| maneuver | 132 |
| guards | 44 |
| ui-h2 | 40 |
| natural-h2 | 30 |
| baseline | 30 |
| tactical | 128 |
| policy | 40 |
| ui-h1 | 30 |
| cooperation | 32 |
| harpoon | 26 |
| camera | 16 |
| defense | 76 |
| natural-ew | 22 |
| native | 38 |
| **합계** | **1198/1198** |

page/core/runtime/presentation 오류0. 실제 empty CMS→surface RF→관측→명시 식별/동의→양측 native Harpoon, 관측 단절 위치 제거·INS freeze/ARH, 준비 중 철회·alias·freshness·손상·보호/예비탄·strict 저장, mouse/touch와 세 척1/8/16/64배속 결정성, H2 동일 물리·재고/RNG 및 기존 native 대공/기동/실제 RAF/WebGL ENTRY/EXIT hole·import/root disposal을 검사했다. queue를 수동 drain하거나 render에서 물리를 적분하지 않았다.

대표 seed와 제한된 측정/자연 시나리오·CPU/SwiftShader 조건이다. 일반 격추율·모든 sea geometry·mobile hardware FPS·실제 doctrine 인증은 아니다. Actions 자동 smoke가 계정 제한으로 시작되지 않아도 CI PASS로 표시하지 않는다.

## 다음 단계

H3 이후 큰 단계는 **3개**: H4 팀 전술·합동 기동 → 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va. 각 단계에 최적화와 최종 원본 회귀를 포함한다.
