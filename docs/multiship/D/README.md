# Multi Ship D — owner 무장·실제 접촉·shadow 판단

5A/5B와 shadow 로그 단계다. 출항 전 배치한 DDG-119/CG-52는 C의 실제 항해·피해·독립 센서를 유지하면서 자기 함정의 사통, 탄약, SPG-62, 함포, 근접방어와 Harpoon 실행 상태를 갖는다. **적 AI 자동발사·전자전·공격은 아직 켜지지 않는다.** 실제 수동 command 포트는 검증과 다음 방어 AI 연결을 위한 것으로, 상대 원격 조종 UI를 추가하지 않는다.

## 상태와 원본 커널

`ShipRuntime.weapons.executionD`가 SAM/RAM·함포탄·기관포탄·난수·동의·shadow 로그를 소유한다. 실제 탄체 collection은 공통 `ENGAGEMENT_RUNTIME.world.entities.navalOrdnanceD`에 등록한다. Harpoon은 기존 world antiShip 배열을 그대로 사용한다. profile/module revision과 packed assets0~12는 변하지 않는다.

`factory.js`의 명시 owner lexical context에 원본 C의 238개 함수를 build 시 결속한다. `function-index.json`은 C decoded source의 Unicode code point 위치·함수명·참조·SHA를 고정한다. Python builder는 각 span을 검증하고 선언된 adapter만 변경한다. 실행 중 ACTIVE 함정/profile 교대, alias 교대, eval/new Function은 없다. 발사 간격·VLS 고정 슬롯/ESSM quad·원본 SAM 추진/항법/유도/DL·SPG servo/예약/사각, Mk45 사통/조준/단발 동의·탄도, RAM 측정 시커/6DOF/접촉·근접신관, 팰렁스 로컬 측정/탄도/피격 커널을 재사용한다.

자함은 기존 실행 경로를 유지한다. 적함 없음에서는 새 physical routing이 비활성이다. DDG의 SeaRAM 사거리가 자함 CG의 RAM 없음 값을 따라 0이 되던 cross-profile builder 참조를 해당 설치 profile로 바꿨다. CG는 양현 Phalanx, DDG는 기존 Phalanx+SeaRAM이며 CG RAM/DDG Harpoon을 새로 설치하지 않는다.

60Hz fixed tick마다 owner 무장을 한 번 처리한다. VLS 내부 사고는 기존 피해통제의 10Hz callback과 해당 함정 전원·구획 상태를 사용한다. 기존 120Hz 침수/힘·20Hz hydro와 공통 world/Harpoon flight 한 번 처리는 유지한다.

## 관측과 command

`weaponCommandD(shipId,{observerShipId,trackId,weapon,mode:'MANUAL',mountId?,ammoId?})`는 살아 있는 배치 함정의 observer 주소를 요구한다. 그 함정의 확인된 신선한 track과 운용자 HOSTILE/TRAINING_TARGET 식별만 사용하며 UNKNOWN, 잘못된 owner 주소, 추가 truth field, AUTO/SEMIAUTO/automatic를 거부한다. 원본 실제 release 함수에서 탄약·장비 손상·조명/채널·발사 간격·조준/사각을 다시 검사한다. 서로 같은 숫자의 track ID는 `[observerShipId,trackId]`로 구별한다.

근접방어는 CMS track 외에 **원본 C55 자체 레이더의 확인되고 신선한 로컬 file**과 운동학 위협·보호 identity·사각 검사를 요구한다. CMS fixture만으로 발사하지 않는다. 수동 동의는 동일 관측 track의 제한된 시간 내 release이며 새로운 자동 표적 선택을 수행하지 않는다. 이 단계의 팰렁스 동의는 한 fixed tick의 발사 분량이고, 지속 burst/새 표적 전환은 후속 defense AI 범위다.

shadow는 5Hz로 owner measured track만 읽어 기존 CPA/NEZ/resource/salvo 계산을 참고한다. 모든 action은 WITHHOLD/executed=false이고, 로그는 최근64개다. surface ROE·unknown 식별·coast/harmless를 구별한다. **완성된 기존 AUTO controller를 전부 이식한 상태는 아니다.** acceleration은 현재 0이고, full BDA/alias 이관·coherent return·재교전/지원 해제는 다음 단계에 결속해야 한다. 관측 file에 실제 ship ID·world 객체·생존 truth를 넘기지 않는다.

## 물리 접촉과 피해

공통 RF 반사장에 실제 함정·owner 탄체를 포함한다. 센서 이후의 판단에는 익명 측정만 전달한다. 실제 물리에는 공통 swept segment와 움직이는 target body frame을 사용하여 가장 이른 함정 외형 진입을 선택한다. launch clearance 동안 발사 함정 형상을 제외하고, sea contact보다 늦은 접촉·이미 소모한 탄·같은 impact event 재적용을 막는다.

Harpoon/Mk45/surface SAM·RAM과 기존 Kh 탄체의 적함 접촉은 해당 `ShipRuntime`의 원본 WIP12 관통·구획 폭압·파편·승조원 노출·침수 개구·종강도·충격 커널에 한 번 전달한다. 임의 HP 대체 피해는 없다. 관통 후 함포탄의 잔여 위치·속도·질량·신관 handoff를 보존한다. 장갑 patch surface ID와 terminal event가 target owner로 구별된다. 외형 접촉은 현재 hull/구조물 layout union이며 얇은 외부 장비별 정밀 collision 확장은 후속이다. 기존 Kh의 자함 호환 피해 경로는 유지하고, 신규 적함은 공통 WIP12 terminal adapter를 사용한다.

Harpoon INS→ARH SEARCH/TRACK, 3.2초 boost, 날개·부스터, 무데이터링크와 발사 시점 memory는 유지한다. 직접 battle 검사는 8km 두 방향이고, 이번 함정 간 신규 120~140km battle 인증을 주장하지 않는다. 원본 장거리 경로/예산·시커 경계는 별도 회귀로 검사한다.

## 표시와 수명주기

3D는 실제 world 탄체와 owner fitting 상태를 읽는다. 적 SAM/RAM/Harpoon은 별도 presentation 필드로 합성하며 자함 미사일 status/자함 follow 목록에 넣지 않는다. CIC에는 원래 자함 observer 접촉만 보인다. Harpoon seeker RF는 실제 활성화 후에만 물리 emitter로 취급하며 발사 후 DL=0을 유지한다. 적함의 함포·SPG·팰렁스·VLS/Harpoon 덮개와 terminal path/실제 손상 구멍은 해당 모델에 적용한다. 발사 연기/후폭풍도 해당 owner hardpoint의 world 위치를 읽는다. 카메라나 renderer가 사통·물리를 적분하지 않는다.

저장은 `fleet.weaponInventorySchema=AEGIS_WEAPON_INVENTORY_D_1`과 함정별 실제 셀/탄창/근접방어/Harpoon inventory를 유지한다. 검증 전 authoritative 쓰기는 없으며 거부된 import는 무변경이다. schema가 없는 기존 B/C 저장만 명시 migration을 허용한다. 비행 탄체·센서 file·동의·예약·routes·shadow는 복원하지 않는다. reset/import/retire에서 owner collection과 pending launch를 정리한다.

## 빌드와 검사

```bash
python docs/multiship/D/build.py archive/v48/WIP_MULTI_SHIP_C/Aegis_SIM_v48_WIP_MULTI_SHIP_C.html artifacts/D.html
python docs/multiship/D/verify_static.py archive/v48/WIP_MULTI_SHIP_C/Aegis_SIM_v48_WIP_MULTI_SHIP_C.html Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/static
python docs/multiship/D/verify_weapons.py Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/weapons
python docs/multiship/D/verify_effectors.py Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/effectors
python docs/multiship/D/verify_battle.py Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/battle
python docs/multiship/D/verify_clock.py Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/clock
python docs/multiship/D/verify_native.py Aegis_SIM_v48_WIP_MULTI_SHIP_D.html artifacts/native
```

builder는 Python 표준 라이브러리만 필요하다. runtime browser 검사는 기존 [requirements](../../bunkerhill/K/requirements.txt)와 Chromium을 사용한다. guidance는 원본 E core에 명시 contact/world-flight/render-owner adapter만 적용해 실제 embedded text와 비교하고 기존45개 INS/SEARCH/TRACK/knowledge/route 수치 조건을 실행한다. 이전 C/E test 파일은 수정하지 않는다. workflow는 이 검사 후 C observers/propagation/native, A paired baseline, B departure, E routes/knowledge와 DDG runtime을 같은 원본 HTML에서 실행한다.

실행 근거와 현재 범위는 [상태](../../../AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_D.md), [측정 조건](PERFORMANCE.md), [다음 단계](DEPENDENCIES.md), [원격 인계](GITHUB_HANDOFF.md)를 따른다. 진단의 measured-state fixture·강제 관통 probe는 실전 탐지/실탄 launch-to-hit 증거와 구별한다.
