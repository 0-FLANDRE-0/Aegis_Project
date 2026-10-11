# H2 — 관측 기반 함정 기동 AI

`ShipRuntime.combatSystem.maneuverH2`가 함정별 설정·판단·임시 항법 명령 소유권을 가진다. H1의 승인된 현지 위협을 다시 freshness/식별/권한/CPA로 검사하고 기존 SPG-62·CIWS 사각과 자기 조종 상태로 기동 후보를 비교한다. 출력은 native 속력·타각 명령이다. 실제 침로·속도·위치는 기존 힘·기관·타율·침수·손상 물리가 적분한다.

## 운용

FLEET에서 선택 함정의 **기동 AI ON/OFF**, **기동 AI 재개**를 사용한다. 자함 기본 OFF, 아군/적함 기본 ON이다. 해당 함정의 **전술 AI ON + AUTO**가 필요하며 기동 AI 버튼만으로 AUTO 교전 관제를 바꾸지 않는다. NAV·ARM·CIC·기존 3D 교전 버튼은 원래 자함이고 선택 아군함 운용은 FLEET이다. 적함 UI 명령은 거부한다.

NAV의 타각·기관 버튼, 지도 항로 추가/삭제/해제, FLEET 조종 명령은 AI의 임시 명령을 반환하고 해당 owner에 지속적인 `manualNav` 우선권을 설정한다. ON/OFF만으로 수동 우선권을 지우지 않는다. **기동 AI 재개**가 수동 항법 hold를 명시적으로 해제하고 전술 AI를 활성화한다. 수동 레이더/EW hold는 보존한다. H1의 **AI 운용 재개**는 레이더/EW hold만 해제하며 항법 우선권을 해제하지 않는다.

수동/반자동/HOLD, 전술 AI OFF, 기동 AI OFF, 장비 offline에서는 임시 항법 소유권을 반환한다. 반환되는 값은 원래 요청 속력·타각·수동 flags·기관 order이며 실제 운동 상태를 되돌리지 않는다.

## 판단과 정보 경계

- 공통 fixed tick의 12틱마다 5Hz로 owner별 한 번 평가한다. 첫 명령은 즉시 최선 후보를 선택하고 이후 최소 유지 3초·점수차 .04를 적용한다. 접근 12초 이하 또는 현재 후보의 경로 차단은 즉시 재선택한다. RNG와 wall clock을 읽지 않는다.
- 후보는 KEEP, PORT30/STARBOARD30, PORT60/STARBOARD60, FAST, SLOW, STOP의 8개다. 선회 목표는 처음 관측 당시 침로 또는 활성 자함 WP 기준으로 고정하여 매 평가마다 선회각이 누적되지 않는다. 속력은 손상 상한 안의 기존 C17 기관 단계(0/8/14/22/28/31kt)를 사용한다.
- 최대 8개의 승인된 fresh 현지 AIR 위협만 사용한다. 측정 KF의 상대 운동으로 미래 CPA/접근을 검사한다. stale/coast/reacquiring/protected/FRIEND/NEUTRAL/UNKNOWN/훈련 표적·수상 파일은 기동 위협이 아니다. 공유 THREAT·익명 ESM만으로 기동 목표를 만들지 않는다.
- 미래 운동은 최대 30초, 6개 자세의 **SIM-TUNE 근사 예측**이다. 실제 속도·타와 손상에 따른 선회/기관 지연을 반영하되 별도의 물리 권위가 되지 않는다. native `spg62Quality`와 `ciwsGameConstraintsV1.direction`을 후보 자세에서 재사용한다. CG의 실제 모델 차폐와 DDG의 접선 사각·train/elevation·장비 상태/탄약을 유지한다. 이것은 사각 기회 점수이며 탐지·FCS·LOS·발사 권한을 생성하지 않는다.
- 점수는 무장 기회 .55, CPA 여유 .2, 좁은 노출 방향 .1에서 선회 비용 .12·속력 변경 .08·현재 사용 SPG 지원 손실 .45를 감산하고 KEEP에 .02를 더한다. 계수와 전술 판단은 SIM-TUNE이다. 현재 조명 배정은 자기 사통 상태만 읽고 비행 탄·적 시커·peer private FCS를 조회하지 않는다.
- 해안선의 실제 chart polygon에 함체 길이와 15m 여유를 적용한다. 최대 16개의 신선한 현지 SURFACE 측정과 실제 수신된 아군 SELF 항법 보고로 접근 중인 근거리 교통을 확인한다. 상대 runtime의 실제 위치를 읽지 않는다. 모든 후보가 차단되면 SAFETY_HOLD로 native 정지 명령을 내린다. 제한된 예측과 유한한 제동 거리이므로 보편적 충돌 회피를 보장하지 않는다. 원래 terrain/contact 물리도 유지한다.
- 마지막 fresh 위협 뒤 4초간 조용하면 기존 임무 침로에 native 타로 RECOVER한 뒤 원래 요청 명령을 반환한다. freshness 2초와 실제 선회 시간이 더해진다. 침로·속도·위치를 순간 이동시키지 않는다. 자함 route 진행/도착 판정은 기존 경로이며 AI 임시 소유 중에는 route 명령이 타와 기관을 덮어쓰지 않는다.

## 저장과 수명주기

fleet schema `AEGIS_NAVAL_PHYSICAL_FLEET_H2_1`, 기동 설정 `AEGIS_MANEUVER_UTILITY_H2_1`의 `enabled/manualNav` bool만 저장한다. own/foreign 전체 설정과 native 기관 metadata를 detached preflight한 뒤 복원한다. current 필드 누락·타입/추가 필드 오류·잘못된 기관 order는 zero authoritative writes로 거부한다.

H1/G/F/B/no-fleet 저장은 명시 migration한다. 자함 기동 AI OFF·외함 ON이며 기존 `manualSpeedV15/manualRudderV15`가 켜져 있으면 수동 항법 hold를 승계한다. 현재 H2 저장의 누락 필드를 legacy로 추측 복구하지 않는다.

점수·후보·침로 목표·명령 소유권은 `maneuverGoalsScoresAndCommandOwnership` deferred 상태다. import/reset/deployment/retire에서 비운다. save의 항법 명령은 AI 임시 값 대신 요청 baseline이며 위치·실제 침로/속도는 현재 물리 상태다. H1/E/G의 기존 저장·교전/선택 초기화 계약을 유지한다.

## 재현과 검증

```sh
npm ci --prefix docs/multiship/H2 --ignore-scripts --no-audit --no-fund
python docs/multiship/H2/build.py archive/v48/WIP_MULTI_SHIP_H1/Aegis_SIM_v48_WIP_MULTI_SHIP_H1.html /tmp/h2.html
python docs/multiship/H2/verify_static.py archive/v48/WIP_MULTI_SHIP_H1/Aegis_SIM_v48_WIP_MULTI_SHIP_H1.html /tmp/h2.html /tmp/h2/static
```

H1 SHA를 pin한 `build.py`와 함수의 Python 문자 offset/SHA `patch-index.json`으로 packed record13만 수정한다. assets0~12·원본 모델·물리/유도/충돌/피해/RF·native 발사 gate는 보존한다. H1 manifest는 역사 기록이며 최신 실행 경로와 지원 pin은 H2 manifest를 따른다.

`verify_maneuver.py`, `verify_guards.py`, `verify_ui.py`, `verify_natural.py`, `verify_clock.py`는 최종 HTML/output을 받는다. `verify_baseline.py`는 H1/H2/output 세 인자다. H1 tactical/policy/UI, G cooperation/Harpoon/camera, E defense, F natural-EW/native도 최종 H2 원본으로 재검사한다. 원본 보고서의 SHA와 직접 집계는 `evidence/verification-summary.json`이다. 역사·실패한 시험·중간 초안 수는 합산하지 않는다.

후속 범위는 [H3 대수상 공격](DEPENDENCIES.md)이다. 현재 대수상 MANUAL-only와 Harpoon INS→ARH/DL0를 유지한다.
