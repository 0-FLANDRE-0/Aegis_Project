# H1 — 함정별 유틸리티 방어 AI

`ShipRuntime.combatSystem.tacticalH1`이 해당 함정의 관측·자원·손상으로 판단한다. 기존 native AUTO가 실행기이며 utility 판단이 현지 위협 순서와 SAM 살보를 조절한다. 실제 발사는 원래 ROE·FCS·NEZ·사통/사각·재고·예비탄·발사 간격 및 G의 보호 식별/담당 lease를 다시 검사한다. 프로필 교환이나 peer private FCS 접근은 없다.

## 운용

FLEET에서 **전술 AI ON/OFF**와 **AI 운용 재개**를 사용한다. 자함은 기본 OFF로 기존 AUTO를 보존하고 아군/적 함정은 기본 ON이다. AI 실행은 해당 함정의 AUTO에서만 허용한다. ON 버튼은 교전 관제를 AUTO로 바꾸지 않는다. 수동/반자동으로 바꾸면 AI가 임시 적용한 개별 레이더·전자전 설정을 복귀시킨다. 원래 EW AUTO는 별도 실행기다.

수동 EMCON·전자전은 해당 owner의 지속적인 우선권을 가진다. ON/OFF만으로 수동 우선권을 해제하지 않으며 **AI 운용 재개**가 이를 명시적으로 해제한다. 함대 공동 EMCON은 개별 AI보다 우선하고, 지연된 그룹 명령을 받기 전에 AI의 임시 레이더 값을 원래 기준값으로 돌려 group baseline을 보존한다. H1은 속력·타각·route를 쓰지 않으므로 FLEET/NAV 수동 항법은 그대로 실행한다.

FLEET의 owner 전환 범위는 G와 같다. NAV·ARM·CIC·기존3D 교전 버튼은 원래 자함이며 선택 함정의 조작은 FLEET에서 한다. 적함에 운용자 UI 명령을 보내지는 않는다.

## 점수와 실행

태세 후보는 WATCH(감시), CONSERVE(탄약 절약), DEFEND(방어), SATURATED(포화 대응), DEGRADED(손상 대응)다. 현지 승인 위협의 접근 시간/속도·품질·미대응 수, native 예비탄 이상 재고, 자기 SPG 가용/사용 채널과 레이더/전투 효율을 비교한다. 상대의 실제 위치/생존/시커나 자기 미사일 truth를 조회하지 않는다. 점수·태세·우선 파일·이유는 detached 진단과 선택 owner UI로 확인한다.

- native 5Hz scheduler에서 한 번 판단한다. 최소 태세 유지2초·교체 점수차.08, 접근12초 이하/장비 offline은 즉시 대응한다. 모두 게임 SIM-TUNE이다.
- 우선순위는 관측 기반 접근 긴급도·속도·품질·미대응으로 계산하고 **native 자원 배분 전 및 실제 자동발사 추천 순서**에 적용한다. 타깃 식별/자동 권한을 생성하지 않는다.
- 현지 승인 위협3개 이상이고 선택 SAM의 native 예비탄 이상 재고가 2발×위협 수에 부족하면, 접근 시간25초 초과·속도600m/s 미만 표적의 기존2발 살보를1발로 배분한다. 급박/고속 위협과 이미 진행 중인 pending 살보, 예비탄·reengagement/BDA·근접방어 조건은 native 경로를 유지한다. 무장 종류의 NEZ/채널 선택은 기존 AUTO다.
- 신선한 현지 위협·수동 ESM의 anonymous ACTIVE_SEEKER 방위·실제 전달된 shared THREAT는 방어 준비를 올린다. 수동/그룹 우선권이 없으면 개별 탐색 레이더를 켜고 기존 soft-kill AUTO/EA 허용을 적용한다. **공유·ESM만으로 FCS/표적 거리/적성 식별/살상 발사를 만들지 않는다.** 마지막 신선한 위협 이후2초 동안 조용하면 원래 개별 설정으로 복귀한다. 관측 freshness2초가 추가되므로 마지막 실제 fix부터 복귀까지는 최대 약4초다.

## 수명주기와 저장

fleet schema는 `AEGIS_NAVAL_PHYSICAL_FLEET_H1_1`, AI 설정은 `AEGIS_UTILITY_TACTICAL_H1_1`이다. `enabled/manualRadar/manualEw` bool만 저장한다. 설정·프로필·배치·무장 등 모든 detached preflight 이후 복원한다. H1 필드 누락/잘못된 타입/추가 필드는 zero authoritative writes로 거부한다. G/F/B 또는 기존 no-fleet 저장만 명시 migration한다.

점수·우선 파일·태세 log·radar/EW 임시 소유권은 combat transient로 복원하지 않는다. 정상 import/reset/deployment/retire에서 비우고, save는 AI 임시 값 대신 요청된 개별 radar/EW baseline을 내보낸다. foreign defense AUTO/HOLD의 기존 E reset/import 초기화는 유지한다. UI 선택도 G 그대로 초기화한다.

## 재현

지원은 G 원본 SHA를 pin한 `build.py`와 Python 문자 offset/SHA `patch-index.json`, `tactical.js`, `ui.js`다. assets0~12/원본 모델·native 유도/물리·damage/RF/NEZ/BDA 커널은 보존한다.

```sh
npm ci --prefix docs/multiship/H1 --ignore-scripts --no-audit --no-fund
python docs/multiship/H1/build.py archive/v48/WIP_MULTI_SHIP_G/Aegis_SIM_v48_WIP_MULTI_SHIP_G.html /tmp/h1.html
python docs/multiship/H1/verify_static.py archive/v48/WIP_MULTI_SHIP_G/Aegis_SIM_v48_WIP_MULTI_SHIP_G.html /tmp/h1.html /tmp/h1/static
```

Chromium은 `AEGIS_CHROMIUM_EXECUTABLE`로 지정하거나 K browser helper가 찾는 설치본을 사용한다. 자체 `verify_tactical.py`, `verify_policy.py`, `verify_ui.py`, `verify_natural.py`, `verify_clock.py`는 HTML과 output directory를 인자로 받는다. `verify_baseline.py`는 G/H1/output 세 인자다. G cooperation/Harpoon/camera, E defense, F natural-EW/native도 최종 H1 원본으로 검사한다. 각 직접 결과와 정확한 SHA/집계는 `evidence/verification-summary.json`이다. 이전 G897건은 역사 근거이며 H1 직접 수에 합산하지 않는다.

## 남은 범위

H2는 관측 방위·무장 사각·자기 조종 가능 상태로 기동 utility 후보를 비교하고 native 항법 포트에 연결한다. 수동 항법 명령의 지속 우선권과 명시 AI 재개를 먼저 마련한다. H3는 현지 수상 관측·ROE·Harpoon 수동 승인 정책과 별도로 자동 공격 동의를 설계한다. 함대 팀 기동, 헬기·CEC급 사통, RGM-109E Block Va는 후속이다. SLQ-32/센서/링크/utility 비공개 수치는 SIM-TUNE이며 실제 전술 doctrine 인증이 아니다.
