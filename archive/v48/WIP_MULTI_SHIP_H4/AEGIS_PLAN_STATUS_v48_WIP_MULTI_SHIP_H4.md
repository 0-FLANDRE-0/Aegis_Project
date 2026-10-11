# v48 WIP MULTI SHIP H4 — 함대 전술·합동 기동

**판정: H4 구현·최종 원본 직접 검증 완료.** 받은 아군 항법에 대한 전형 기동, 별도 동의 아래 관측 수상 접촉의 공격 담당 분담, 현지 발사원 근거의 수상 자위 판단을 추가했다. 현재 배치는 자함·아군·적함 각1척이다. 이후 큰 단계는 **2개: 헬기/초수평선 탐지 → RGM-109E Block Va**.

## 원본과 업로드

- H3 final `af1eade2d418b215720a68a5b902aae0d9387203` 위 branch `multiship-tactical-h4`, PR base `multiship-tactical-h3`. main/선행 PR 병합은 실행하지 않는다.
- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html): **15,697,218 bytes**, SHA-256 `602371dfd5be5147c2e04dd4078e3216ca4f47e8ce4e7b0092bd861c3d9a5132`.
- decoded main SHA-256 `451a717f0dbc97c289990eda7bf4864703c5a8832b81b0d4af4f53d3f6c56416`. packed record13만 바뀌며 models/assets0~12는 exact다. pinned patch로 full HTML을 byte-identical 재생성한다.
- H3 HTML/status/SHA/workflow 네 파일은 변경 없이 `archive/v48/WIP_MULTI_SHIP_H3/`에 보존한다. H3 HTML SHA `0a9626535c209d8ad4e5a9b5262bd826d8ede8df928562534ba6c44b5673d178`.
- stable v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`, blob `f540b68f138e3ed85614c41f6794be78602229d8` 유지.
- [운용/권한](docs/multiship/H4/README.md), [검증 조건/성능](docs/multiship/H4/PERFORMANCE.md), [남은 단계](docs/multiship/H4/DEPENDENCIES.md), [업로드 인계](docs/multiship/H4/GITHUB_HANDOFF.md), [SHA](SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt).
- §7.1 standing authorization으로 원본/support를 직접 업로드하고 [독립 원격 읽기](docs/multiship/H4/evidence/remote-publication.json)를 남긴다. Actions는 dispatch하지 않으며 아래 최종 원본 직접 검증을 gate로 사용한다. 자동 PR smoke의 실제 상태는 PR/annotation을 따르고 미실행을 CI PASS로 표시하지 않는다.

## 동작과 정보 경계

FLEET에 **함대 전술 ON/OFF**, **호위/수상전 임무**, **종렬·좌현·우현 전형**, **1/2/4km 간격**, **임무·전형 적용**, **수상 자위 판단 ON/OFF**를 추가했다. 자함/아군 team 기본OFF이며 설정은 선택 owner에만 적용한다. 원래 자함이 선도함, 아군은 링크와 H1 전술 ON·H2 기동 재개·AUTO에서 받은 항법을 따라 움직인다. NAV/ARM/CIC/기존3D 버튼은 원래 자함이다.

canonical `ShipRuntime.combatSystem.teamH4`가 설정·메시지·수신 항법·전형·배정·발사 접수·자위 근거를 소유한다. G contract와 별도의 H4 packet을 기존 friendly radio/LOS/장비 가용성 경계에서 센서/G 다음 fixed phase에 전송한다. 2Hz/18틱 지연/2초 fresh, 시각·sequence/replay·필드·SPD covariance·용량을 변경 전에 검사하며 malformed null records도 안전하게 거부한다. 적함은 friendly transport에 가입하지 못한다. G 트랙 공유OFF면 H4 항법만 허용한다.

전형은 받은 선도함 SELF 위치·속도·heading·오차를 사용한다. 4개 STATION/좌우 우회/HOLD 후보와 H2 피해 예측·native 교통/해안·chart segment 검사로 기존 타/기관 명령을 선택한다. 공통 H2 baseline을 반환하며 실제 heading/speed/position을 직접 쓰지 않는다. 현지 대공 방어 기동·수동 항법·MANUAL/HOLD·masterOFF·기동OFF가 우선한다. 링크 소실/팀OFF는 전형 명령을 반환한다. 간격은 원하는 전형 위치이며 순간 배치나 모든 항로에서의 수렴 보장이 아니다.

수상전 임무는 **fresh 현지 SURFACE 관측·적성 근거·각 owner의 별도 H3 1/2발 동의**를 요구한다. 공유만으로 FCS/적성/발사 동의를 만들지 않는다. 서로 다른 track 번호의 받은 bid를 6D 측정 게이트로 연관하며 모호하면 배정하지 않는다. bid는 실제 native 준비/손상/사거리/basket/발사축·해안·아군 경로를 읽기 preview하고 exact capability를 `finally`에서 복원한다. 수동 pending를 빌리거나 preview에서 요청/발사 포트를 호출하지 않는다.

한 primary에 짧은 lease를 부여하고 실제 release에서 native H3/팀 gate를 재검사한다. 임무 전환 시 링크 대기를 다시 시작한다. 같은 측정 접촉에 공동2발 접수 후90초 추가 AI 살보를 보류한다. 접수는 sender/serial로 중복 제거하고 동의 소진·배정/heartbeat 만료 뒤에도 기억한다. 링크가 없거나 접수를 못 받은 상황의 모든 중복 공격을 막는 분산 합의는 아니다. teamOFF와 attackOFF는 별도이며 기존 H3 개별 동의는 teamOFF 뒤에도 유지될 수 있다.

수상 자위 정책은 자함/아군 기본 IDENTIFIED_ONLY, 새 적함 SELF_DEFENSE다. 승인된 현지 incoming ASM의 fresh 운동학·분류/CPA와 작은 오차의 유일한 near-origin 수상 파일을 반복 관측한 경우30초 owner-local 근거를 만든다. `_operatorIdentity`는 바꾸지 않으며 FRIEND/NEUTRAL·IFF·G 보호와 늦은 무장 FRIEND 판정이 우선한다. alias/번호 재사용·expiry·import/reset에 근거를 승계하지 않는다. 아군의 별도 공격 동의를 대체하지 않는다.

**발사원을 직접 관측해 연관하지 못한 미식별 적함의 첫 공격은 보류**한다. IFF 무응답·ESM-only·받은 HOSTILE·world faction은 적성 근거가 아니다. 자연 RF 시험의 적성 designation은 실제 익명 관측 뒤 명시 operator/scenario 명령이다. 자유 ROE·모든 발사원 획득/식별을 완료한 것으로 주장하지 않는다.

peer가 관측한 자함 반사가 보호 보고로 돌아와 자기 발사를 막는 문제도 수정했다. fresh FRIEND TRACK relay의 위치/속도가 자기 항법과 일치하고 작은2σ 타원이 자함 중심부 안에 들어가는 경우만 자기 위치로 처리한다. 다른 파일·다른 함정 SELF·NEUTRAL·주변 선박·stale/큰 오차 보고는 계속 보호한다.

Harpoon DL0, launch-frozen INS→독립 ARH SEARCH/TRACK·3.2초 booster와 RF/ECM·물리·피해·효과를 유지한다. AI는 탄체 위치·시커·생존·명중/BDA truth나 peer private FCS를 읽지 않는다. 발사 접수는 명중 보고가 아니다. DDG Harpoon0·CG RAM0·고정 셀·60/120/20Hz·H1/H2 방어/기동·G 공유·owner별 해상효과/3D를 보존한다.

파일96/bid16/queue16/own접수8/수신접수16/log64, 판단5Hz/전형4후보×6자세/기존교통16+수신선도함1로 비용을 제한한다. 이 주기·게이트·lease·살보/간격은 SIM-TUNE이다.

## 저장과 직접 검증

fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H4_1`, team `AEGIS_TEAM_TACTICS_H4_1`의 schema/enabled/mission/formation/spacingM/surfaceRoe만 저장한다. 현재 필수 필드 누락/타입/추가는 모든 owner detached preflight 뒤 zero-writes 거부한다. H3/H2/H1/G/F/B/no-fleet은 팀OFF·IDENTIFIED_ONLY로 migration하며 pending legacy enemy도 새 권한을 획득하지 않는다. 메시지·배정·접수·근거는 transient이며 import/reset/deploy/retire에서 비운다. 저장 항법은 H2 operator baseline이다.

[검증 집계](docs/multiship/H4/evidence/verification-summary.json)는 최종 tested HTML SHA, 검사 소스·report·capture SHA를 pin한다. 실패/폐기 draft 및 역사 검사 수치를 합산하지 않는다.

| 최종 원본 직접 suite | PASS |
|---|---:|
| static | 59 |
| team | 88 |
| intent-h4 | 30 |
| ui-h4 | 42 |
| natural-h4 | 17 |
| attack | 195 |
| attack-guards | 20 |
| ui-h3 | 42 |
| surface | 18 |
| clock | 208 |
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
| **합계** | **1403/1403** |

24 suites, capture 14개. page/core/runtime/presentation 오류0. 지연 메시지·atomic save/migration·전형 실제 기동/인계·손상 primary 교체·동의 소진 뒤 추가 발사 방지·자위 근거와 부정 조건·mouse/touch·자연 radar→실제 공동2발을 검사했다. 세 owner/두 함종 조합1/8/16/64배속의 실제 H4/H3/방어·물리/RNG 결정성, H3 teamOFF/no-peer 동일 물리, 기존 native 방어/EW·actual RAF/WebGL 피격/복원·root disposal을 통과했다. queue를 수동 drain하거나 render에서 물리/RNG를 진행하지 않았다.

대표 seed·제한된 fixture/자연 시나리오·CPU/SwiftShader 조건이다. 보편적 충돌/오격 방지·모든 launch-origin 획득·격추율·다수 네트워크 topology·휴대폰 hardware FPS·실제 doctrine 인증은 아니다. 다음은 헬기/초수평선 탐지이며 이후 사용자 지정 RGM-109E Block Va다.
