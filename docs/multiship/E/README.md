# Multi Ship E — 방어 AUTO/BDA와 항공기 스폰 선택

D의 원본 owner 무장과 양방향 실물 피해 위에 5C/5D를 연결한다. 배치 적함은 기본 방어 AUTO이며 출항 전에 적 항공기 스폰 ON/OFF를 고른다. 원본 DDG/CG profile·모델·장착 위치와 stable v48은 보존한다. receiver별 EW, 공격/기동 AI와 헬기는 다음 단계다.

## 실행과 소유권

기존 `createWeaponContextD(owner)` 안에서 WIP118/119/121/122/123/124의 원본 67개 함수와 native control/response/BDA/alias 상태를 결속한다. 함수별 원본 D codepoint span·SHA는 [function-index](function-index.json), 수정 대상 경계는 [patch-index](patch-index.json)다. runtime eval, ACTIVE profile/global 교대, 별도 전투 singleton을 추가하지 않는다. owner 상태는 `ShipRuntime.weapons.executionD.defenseE`와 `combatSystem.engagementControl.defenseE`에서 확인한다.

60Hz owner step 안에서 기존 5Hz 판단 cadence를 사용한다. 관측 acceleration, CPA/NEZ, hostile intent, 식별/ROE, 사각, 사통/조명·예약, 실제 radar budget·장비 손상·탄약·salvo를 원본 커널로 평가한다. 신선하고 확인된 자기 관측을 요구하고 실제 pending salvo release에서도 다시 승인한다. UNKNOWN/분류만 높은 접촉, FRIEND/NEUTRAL, stale/coast, EMCON/HOLD, offline/빈 재고/지원 불능은 발사를 막는다. 측정 기반 hostile intent가 별도의 적성/권한 평가를 통과한 경우만 기존 AUTO 정책에 따라 방어한다.

근접방어는 독립 C55 레이더의 확인되고 신선한 local file·운동학/보호 identity와 CMS consent를 함께 사용한다. Map으로 각 mount를 독립 운용하고 원본 solver·slew·분산·탄도·사각·탄약을 유지한다. Phalanx 동의를 계속 갱신하여 연속 burst를 실행하고 RAM은 live shot/예비탄을 재검사한다. CG는 양현 20mm Phalanx이며 RAM을 만들지 않는다.

## BDA·alias·물리

자기 무장효과와 후속 관측으로 KILL_ASSESSMENT/DESTROYED/THREAT를 결정한다. FUZE→DIRECT 승격은 효과 시각/증거를 갱신하고 조명·DL/SPG 지원을 해제한다. 센서 손실만으로 격추를 확정하지 않는다. 같은 프레임의 검증된 alias로 SAM/RAM/탄/CIWS/SPG/선택 lock/response/owner key를 원자 이관하되 식별은 무조건 복사하지 않는다.

외국 함정 local track ID가 자함 BDA에 들어가지 않도록 물리 retirement에는 owner 표식만 남긴다. 실제 탄체 분해·잔해 수명은 공통 물리 collector가 진행한다. controller에는 실제 객체 ID·alive·world 배열을 넘기지 않는다. 3D는 실제 owner 탄체/장착물과 효과를 읽으며 foreign 미사일을 자함 telemetry/follow 목록에 넣지 않는다. Harpoon DL=0과 INS→ARH, 원본 물리·신관·피해는 유지한다.

D의 SPG reservation metadata는 const였지만 native offline reset이 재대입한다. E는 원본 reset 계약에 맞는 owner-local mutable binding과 metadata shape로 교정한다. 원래 C observer의 anonymous 분류 evidence에서 classification confidence를 산출하되 적성 identity와는 분리한다.

## 출항 전 항공기

함선 선택과 적재 화면의 `적 항공기 스폰` 선택은 같은 draft를 사용한다. ON 기본값은 원래 sandbox/작전모드 스폰 조건을 유지한다. OFF는 초기 patrol, periodic spawn, reset/delayed spawn, 새 해역의 정상 항공기 생성 경로를 막고 스폰 시계/난수를 소비하지 않는다. diagnostic 시험 항공기/미사일 생성은 자동 스폰 설정과 독립이다.

`AEGIS_DEPLOYMENT_MULTI_SHIP_E_1`의 boolean `enemyAircraftEnabled`로 저장한다. E schema의 누락/잘못된 타입은 preflight에서 무변경 거부한다. 예전 A_1 schema는 명시적으로 ON으로 migration한다. 출항 후 선택기는 잠긴다. 기존 owner 고정 셀/탄창 inventory는 그대로이며 비행/센서/BDA/pending 살보는 combat transient로 초기화한다.

## 직접 검증과 한계

최종 원본 SHA와 suite별 조건은 [verification-summary](evidence/verification-summary.json), 측정 환경은 [PERFORMANCE](PERFORMANCE.md)다. measured-state/effect fixture, 실제 anonymous radar 관측, native RAF/WebGL 시험을 구별한다.

- `verify_defense`: 권한 승인/거부, 실제 AUTO release, pending 재검사, BDA upgrade/후속 관측/alias, reset·truth 입력 거부.
- `verify_departure`: desktop/mobile의 두 선택기, ON/OFF 초기/주기/reset/새 해역·저장/legacy·atomic 거부.
- `verify_closein`: 실제 20m Kh-35U의 자연 관측, DDG RAM과 CG Phalanx 실발사/연속 burst. CMS fixture만으로 발사0.
- `verify_natural`: 실제 8km Harpoon 발사/INS/ARH/물리 접촉. DDG AUTO ESSM 2발이 나가지만 해당 seed에서 Harpoon 접촉도 발생한다. CG 저고도 접근은 확인된 ASM 관측이 없고 AUTO 발사0이다. 사각/검출 문턱을 바꾸거나 truth로 접촉을 만들지 않는다.
- `verify_clock`: mixed profiles ×1/8/16/64 ×1,536 full ticks, 물리/관측/무장/방어/난수 exact, owner/world 중복 진행0.
- `verify_native`: 원본 RAF/WebGL에서 measured HOSTILE에 AUTO 실발사·owner SAM mesh/SPG·카메라 read-only. 자연 탐지 증거는 위 별도 시험이다.
- `verify_regression`: D 원본 파일을 수정하지 않고 시험 측 mode를 HOLD로 설정해 manual port/효과/실탄 battle/native 피해 회귀를 유지한다. AUTO 시험은 HOLD를 사용하지 않는다.

기존 D guidance, C sensor/propagation/native, A paired ownship baseline, B departure, Harpoon routes/knowledge와 DDG runtime도 같은 E 원본에 실행한다. CI는 static +18 browser suite와 기존 smoke다. 검출률/격추율·120~140km 신규 함정간 battle·모바일 하드웨어 FPS를 인증하지 않는다.

```bash
python docs/multiship/E/build.py archive/v48/WIP_MULTI_SHIP_D/Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/E.html
python docs/multiship/E/verify_static.py archive/v48/WIP_MULTI_SHIP_D/Aegis_SIM_v48_WIP_MULTI_SHIP_D.html Aegis_SIM_v48_WIP_MULTI_SHIP_E.html artifacts/static
python docs/multiship/E/verify_defense.py Aegis_SIM_v48_WIP_MULTI_SHIP_E.html artifacts/defense
python docs/multiship/E/verify_departure.py Aegis_SIM_v48_WIP_MULTI_SHIP_E.html artifacts/aircraft
```

builder는 Python 표준 라이브러리, browser는 기존 [requirements](../../bunkerhill/K/requirements.txt)와 Chromium을 사용한다. [상태](../../../AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md), [다음 단계](DEPENDENCIES.md), [직접 원격 업로드](GITHUB_HANDOFF.md)를 따른다.
