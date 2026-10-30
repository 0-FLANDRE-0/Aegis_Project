# H3 — 관측 기반 대수상 공격 AI

H2 관측 기반 기동 위에 별도의 하푼 공격 권한을 추가한다. 최신 원본과 직접 검증 수치는 루트 상태 문서 및 `evidence/verification-summary.json`을 따른다. weights·시간·보호 여유는 게임 SIM-TUNE이며 실제 전술 doctrine이 아니다.

## 운용

1. FLEET에서 자함 또는 아군함을 선택한다. DDG-119는 현재 Mk141을 장착하지 않았으므로 공격 동의 버튼이 비활성화된다.
2. 전술 AI를 ON, 해당 함정의 교전 관제를 AUTO로 하고 **공격 AI ON**을 누른다. 공격 AI는 자함/아군함 기본 OFF이며 ON만으로 발사하지 않는다.
3. 해당 함정이 실제 탐지한 fresh 수상 표적을 선택하고 **적성 HOSTILE**로 식별한다. 미식별·추정 적성·훈련 표적·아군·중립은 자동 공격하지 않는다.
4. 하푼 1발/2발을 선택하고 **선택 표적 공격 동의**를 누른다. 동의는 해당 owner의 그 관측 파일 객체에만 120초 동안 유효하다. 표적 번호가 재사용되거나 파일이 바뀌면 승계하지 않는다.
5. 발사대/재고/사거리/관측 오차/해안/아군 보호 조건을 통과하면 기존 native 발사관 개방과 실제 발사를 수행한다. 예비 하푼 2발을 보존한다. 동의량은 실제 발사 시에만 차감된다.

**공격 동의 취소**, 공격 AI OFF, 전술 AI OFF, MANUAL/HOLD 전환은 준비 중인 AI 발사를 취소한다. 새 동의와 ON/OFF 변경은 이전 동의를 지운다. ON/OFF 후에는 표적 동의가 다시 필요하다. 이미 진행 중인 수동 하푼 발사와 웨이포인트 초안/편집이 우선하며, 수동 발사·수동 좌표 탐색의 기존 권한은 유지한다. AI 발사 준비 중 수동 발사로 인계하려면 동의를 취소하거나 MANUAL로 전환한다. FLEET 전환은 다른 함정의 설정이나 동의를 복사하지 않는다. NAV/ARM/CIC/기존3D는 계속 원래 자함이다.

## 판단과 발사 경계

`ShipRuntime.combatSystem.attackH3`가 enabled 설정, 제한된 동의, 후보, 준비 권한과 발사 접수 이력을 소유한다. 공통 native fixed command phase에서 12틱마다 한 번 판단한다. 자기 항법/발사대/손상과 fresh 현지 SURFACE KF 측정만 계획에 사용한다. 공유 정보나 ESM bearing만으로 현지 FCS·수상 적성 식별·공격 동의를 생성하지 않는다.

독립 opaque capability는 canonical 객체 및 같은 owner/관측 파일과 일치해야 한다. 기존 Harpoon gate의 일반 AUTO/SEMIAUTO 거부와 모든 Standard/ESSM 대수상 MANUAL-only 권한은 그대로다. H3의 typed 경로만 식별/동의/활성 조건을 별도로 검사한 뒤 기존 native readiness·4~140km 범위·예측 basket·발사대 손상·수면/자세 gate를 사용한다. 수동 coordinate-search gate를 AUTO로 우회하지 않는다.

native 자동 튜브 선택은 등록된 고정 슬롯에서 적합한 방향의 발사관을 고른다. 추가로 CG 실제 occluder BVH에서 발사축의 초기24m 차폐를 검사한다. 측정된 속도로 직접 INS 예상 경로와 종말 탐색 구역을 만들고 120도 선회 상한·선회 여유를 포함한 거리 budget·실제 chart polygon의 교차와100m 해안 여유를 검사한다. 수동 route나 지도 waypoint를 변경하지 않으며 우회 항로 생성은 후속이다.

현지 FRIEND/NEUTRAL 및 수신한 protected SURFACE/SELF 보고의 측정 위치·속도·공분산으로 비행 경로와4km 종말 탐색 구역을 보호한다. stale/invalid/과다 protected picture는 보류한다. 보호 보고는 발사 보류에만 사용하며 공유 HOSTILE은 발사 해법이 아니다. pending과1.5초 native 간격을 유지하고 개방 후 **실제 발사 순간**에 동의·식별·freshness·재고/손상/자세·route/보호를 다시 검사한다. 긴급 대공 방어 중에는 공격 준비를 보류한다.

현지 파일96·계획 후보16·protected64·로그64 상한, 동의1/2발, 예비2발, 적함 살보 후90초 재평가 주기는 SIM-TUNE이다. 계획은 actual 위치/속도/physics를 쓰거나 RNG를 소비하지 않는다. 기존60/120/20Hz, INS/ARH/IMU·부스터/분리·화염/연기·날개 전개·RF/ECM·대공 defense/FCS/NEZ/BDA/예비탄과 H2 기동을 유지한다.

## 적함 ROE와 정보 한계

적함의 공격 AI는 기본 ON이고, scenario mission 권한 아래 **자기 현지 파일이 HOSTILE로 식별된 경우**만 최대2발을 계획한다. IFF 응답 부재나 상대의 world faction/물리 ID를 읽어 적성으로 바꾸지 않는다. 현재 센서의 아군 IFF는 FRIEND를 인증하지만 적성을 자동 인증하지 않으므로 자연스럽게 생긴 UNKNOWN 수상 파일에 대한 첫 공격은 보류된다. 자동 대수상 적성 판정/추가 ROE는 후속이며 이번 단계에 구현한 것으로 주장하지 않는다. 적함 운용자 명령은 FLEET에서 허용되지 않는다. 자연 시험의 적성 판정은 이미 실제 탐지된 파일에 대한 명시 diagnostic scenario designation이다.

하푼은 발사 시점 관측 상태를 고정한 INS cue로 항법하고 종말에는 독립 ARH SEARCH/TRACK를 사용한다. **DL 없음**: AI는 비행 중 자기/아군 하푼의 실제 위치·시커·생존·명중·BDA를 조회하지 않는다. 발사 접수 이력만 안다. CIC 위치는 실제 레이더 관측과 그 측정의 짧은 coast estimate에서만 나오며 관측이 사라지면 위치도 사라진다. 파괴 여부를 몰래 알고 재발사하지 않는다.

발사 전 보호는 유한한 관측과 CV 예측에 의존한다. 하푼 시커 자체에 IFF를 추가하지 않았으므로 급기동·새 접촉·관측되지 않은 선박에 대한 오격을 완전히 보장하지 않는다. 직접 경로와 제한된 초기 발사축 검사이며 모든 실제 곡선 비행의 충돌 회피 보장이 아니다. 긴 거리의 움직이는 표적은 기존 acquisition basket 검사에서 거부될 수 있다. 헬기/초수평선 센서나 offboard firing은 이번 범위에 없다.

## 저장과 검증

fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H3_1`, attack 설정 `AEGIS_SURFACE_ATTACK_H3_1`은 `{schema,enabled}`만 저장한다. 현재 schema의 누락/타입/추가 필드는 모든 owner detached preflight에서 zero writes로 거부한다. 동의·계획·capability·발사 이력은 deferred이며 import/reset/deployment/retire에서 비운다. H2/H1/G/F/B/no-fleet은 명시 migration하고 새 공격 권한을 OFF로 시작한다. 새 시나리오의 기본 enemy mission과 legacy import를 구별한다.

직접 시험은 측정 fixture의 승인/취소/동의량/보호·실제 chart/8튜브·수신 report·자연 RF→관측→식별/동의→발사·**세 척**의 fixed clock·mouse/touch 및 기존 native 방어/기동/3D를 포함한다. GitHub Actions는 dispatch하지 않는다. 최종 SHA의 직접 검사만 집계하며 역사/중간 실패/폐기된 draft는 합산하지 않는다. 상세 조건은 [PERFORMANCE.md](PERFORMANCE.md), 후속은 [DEPENDENCIES.md](DEPENDENCIES.md), 업로드는 [GITHUB_HANDOFF.md](GITHUB_HANDOFF.md)를 따른다.
