# AEGIS v48 WIP13C — Surface Missile Engagement Plan

작성일: 2026-09-23

## 실제 WIP 번호 배정 — 2026-09-24 갱신

계획 작성 뒤 `WIP13C`부터 `WIP13C3`까지는 먼저 요청된 control-deck UI 정리에 사용되었다. 아래 구현 단계의 논리적 C1~C4는 실제 산출물에서 다음 번호로 이어간다.

| 논리 단계 | 실제 산출물 | 상태 |
| --- | --- | --- |
| C1 공통 계약·release foundation | `WIP13C4` | 완료 |
| C2 SM-2 제한적 SARH 대수상 교전 | `WIP13C5` | 완료 |
| C3 ESSM Block 2 ARH 대수상 교전 | `WIP13C6` | 구현 완료 · 브라우저 실플레이 확인 대기 |
| C4 운용 UI·회귀·마무리 | `WIP13C7` | 다음 단계 |

`WIP13C4`는 live surface launch를 열지 않고 `MANUAL + HOSTILE/TRAINING_TARGET`, 익명 composite-track FCQ, SM-2 SPG-62 사전검사, ESSM ARH handoff basket, 무장 중립 WIP12F surface-target adapter를 결정적으로 닫았다.

`WIP13C5`는 SM-2의 실제 대수상 발사 경로를 열었다. 발사 전 SPG-62 시간창을 commit하고, SPG-62 송신 빔과 미사일 수신 빔에 동시에 들어온 공통 물리 RF 반사원·해면 clutter를 SARH monopulse 측정과 미사일 로컬 EKF로 처리한다. 종말에는 실제 비행 segment와 3D 표적 선체의 swept contact만 WIP12F 및 표적 damage runtime으로 전달한다. release와 유도에는 surface truth ID나 좌표를 주입하지 않는다.

`WIP13C6`는 사용자 실비행에서 드러난 발사·유도 불안정을 우선 수정하면서 ESSM `SURFACE_ARH` live 경로를 열었다. 수상 SM-2는 BODY 정렬만으로 pitch-over를 종료하지 않고 실제 속도벡터까지 표적 corridor에 들어와야 launch controller가 권한을 넘긴다. 수상 SM-2에도 predictive sea-clearance guard를 적용하고, 수상 SM-2/ESSM은 선택된 onboard/DL estimator state에 짧은 source-local low-pass를 적용해 RF/EKF 측정 요동이 직접 PN 헌팅으로 증폭되는 것을 억제한다. ESSM은 공중용 `trackIsFireControlQuality()` 대신 C4의 익명 surface FCQ/handoff basket을 사용하고, `_surfaceArh` runtime, 실제 swept hull contact, WIP12F damage consumer까지 연결했다. 공중 SM-2/ESSM 경로는 기존 gate를 유지한다.

## 목표

WIP13C는 기존 SM-2MR Block IIIA 및 ESSM Block 2 비행체를 새 대함미사일처럼 복제하지 않고, 현재 무기 profile·VLS·유도·RF seeker·WIP12F 종말탄도 체계에 `MANUAL_SURFACE_ENGAGEMENT` 운용 모드를 추가한다.

- SM-2: SPG-62 연속파 조사와 SARH 수신을 요구하는 제한적 대수상 교전
- ESSM Block 2: 익명 수상트랙을 midcourse cue로 사용하고 ARH로 종말 획득하는 대수상 교전. SPG-62 지원은 선택적 품질 향상 수단
- 두 무기 모두 자동 수상교전 금지
- 수상트랙의 운용자 식별이 `HOSTILE` 또는 `TRAINING_TARGET`일 때만 수동 발사 가능
- 최종 명중은 Pk 즉사식이 아니라 실제 미사일 궤적과 표적 3D hull 충돌로 판정
- 명중 후 WIP12F 관통·신관·폭발 결과를 표적함 damage packet으로 변환
- 표적 truth ID는 센서 반사 합성·물리 충돌·피해 적용에서만 사용하고, 발사 판단·유도 cue·UI에는 누설하지 않음

## 선행 완료 — WIP13B12 ARH 해면 오획 방지

13C 착수 전에 Kh-32, Kh-35U, ESSM Block 2가 공유하는 ARH 측정 경로에 `AEGIS_ARH_RF_TARGET_VALIDATION_V48_WIP13B12`를 적용했다.

- 해면·지형 RF echo는 삭제하지 않고 SNR, clutter, composite measurement와 탐지거리 저하에 계속 기여한다.
- 다만 측정된 range/elevation 높이, 수직·수평 extent, 표면 대비 Doppler, Doppler spread로 계산한 discrete-target evidence가 임계값보다 낮으면 EKF guidance track을 갱신하지 못한다.
- 디버그용 reflector 종류, entity ID, 지정 표적 truth는 판별 권한에 사용하지 않는다.
- 고다이브 Kh-32 3개 결정적 seed에서 실제 함정 echo 추적은 유지했고, accepted sea-only guidance update는 0회였다.
- 이 계약은 13C3 ESSM 대수상 종말 획득의 선행조건으로 유지한다.

## WIP13C4 착수 당시 코드 감사 기록

### 이미 존재하여 재사용할 기반

1. `physicalRfReflectorRegistryWip13A3()`가 수상표적, 항공기, ASM, 채프, 지형과 해면 클러터를 공통 banded RF reflector로 제공한다.
2. SM-2 SARH의 `_sarhTruthReflectorPool()`과 ESSM ARH의 `_arhPhysicalEchoes()`는 이 공통 반사원 풀을 사용한다.
3. `runWip13a3AllRfSeekerFixture()`는 SARH와 ARH가 수상표적 반사원을 선택·추적할 수 있음을 이미 검사한다.
4. SPG-62 물리 mount, sector/mask, terrain LOS, 손상, 동시 채널 및 시간축 reservation scheduler가 존재한다.
5. SPY-1D(V)·SPQ-9B·BridgeMaster E의 수상트랙은 하나의 익명 EKF track으로 융합되고 contributor age·covariance·관측 extent를 제공한다.
6. `WIP12B_LIVE_ORDNANCE.SM2/ESSM`은 질량, 탄체, 폭약, 파편, proximity/contact fuze용 공통 terminal spec을 이미 가진다.
7. 표적함은 3D hull collision, armor patch, 파괴구, 9개 coarse 침수구획, 화재, 종강도·용골 피해 consumer를 이미 가진다.

### 아직 연결되지 않은 부분

1. `spawnMissile()`과 `spawnESSM()`은 공통 A3 gate만 사용한다. 수상표적에 요구할 `MANUAL + HOSTILE/TRAINING_TARGET` 전용 release gate가 없다.
2. 기존 A3 수동 gate는 `FRIEND/NEUTRAL`만 거부하므로 `UNKNOWN` 수상트랙도 통과할 수 있다.
3. `trackIsFireControlQuality()`는 공중 SAM 기준이다. 수상 미사일 교전용 covariance·track age·handoff basket·SPG geometry 판정이 별도로 없다.
4. SM-2 SPG reservation은 공중요격 terminal schedule을 전제로 한다. 수평선 부근 수상표적에 대한 조사 시작·유지·sector 상실 처리 계약이 없다.
5. 기존 SAM loft/direct-impact 제어는 저고도 공중표적 대응용이다. 실제 해면 위 함체를 향한 terminal aim height와 sea-clearance release 조건이 없다.
6. 현재 interceptor proximity-fuze 소비자는 `truthObjectForTrackV27()`가 반환한 비-ASM 표적을 항공기 분기로 처리할 수 있다. 수상표적에 이 경로를 그대로 열면 `alive=false` 즉사 처리될 수 있다.
7. friendly SM-2/ESSM 비행 segment와 수상표적 3D hull의 swept collision 경로가 없다.
8. `wip12bResolveSurfaceTerminal()`은 공통 ordnance terminal spec은 제공하지만 표적함 geometry/damage runtime에 연결된 live adapter가 아니다.

## 모델링 경계

### SM-2MR Block IIIA

현재 공개 임무 설명은 주로 함대공 임무를 명시하므로, 대수상 사용은 프로젝트의 명시적 시뮬레이션 가정으로 유지한다.

- 모드명: `LIMITED_SURFACE_SARH`
- 발사 전 유효한 SPG-62 sector·LOS·hardware availability 필요
- midcourse는 익명 composite surface track과 SPY datalink 사용 가능
- terminal은 실제 SPG-62 조사와 onboard SARH echo track이 없으면 정밀 유도 불가
- 지형 masking, 수평선, sea clutter, target RCS와 illuminator 손상이 실제 품질에 반영
- 조사 상실은 즉시 truth homing으로 대체하지 않고 SARH coast/reacquire 후 miss 가능
- 사거리와 scan/illumination 수치는 `SIM_TUNED_PUBLIC_UNKNOWN`으로 명시

### ESSM Block 2

공개적으로 알려진 확장 capability는 반영하되 Block 2의 정확한 대수상 종말 로직과 수치는 공개값으로 주장하지 않는다.

- 모드명: `SURFACE_ARH`
- midcourse는 익명 composite surface track을 사용
- terminal은 기존 X-band ARH 물리 echo·monopulse·EKF·ECCM 경로 사용
- SPG-62 SARH 지원은 optional contributor이며 발사의 필수 토큰이 아님
- seeker는 표적함뿐 아니라 지형·해면·채프 반사원을 계속 본다. 분산 배경반사는 clutter·측정 bias·coast/reacquire·miss를 유발할 수 있지만, WIP13B12의 discrete-target evidence가 없는 해면 셀 하나가 guidance track으로 승격되지는 않음
- seeker가 truth entity ID를 lock ID로 보유하거나 유도에 사용하지 않음
- 대수상 handoff range, terminal descent, clutter threshold는 `SIM_TUNED_PUBLIC_UNKNOWN`

## 공통 대수상 사격통제 계약

새 계약은 함포 module과 수치를 공유하지 않되, B8~B10의 익명 수상트랙 측정값을 재사용한다.

입력:

- track domain/classification = `SURFACE`
- confirmed/lifecycle/measurement age
- 전체 6-state covariance
- SPY-1D(V), SPQ-9B, BridgeMaster E contributor age
- 익명 관측 surface extent와 confidence
- 기동 innovation 및 coast uncertainty
- 예상 midcourse/handoff 시간
- 무기별 seeker acquisition basket
- SM-2에 한해 SPG-62 sector, terrain LOS, horizon, hardware health, reservation availability

출력:

- `SURFACE_MISSILE_FCS_READY`
- `SURFACE_MISSILE_FCS_DEGRADED`
- `SURFACE_MISSILE_FCS_INSUFFICIENT`
- 예상 handoff position/velocity sigma
- weapon-specific acquisition basket margin
- SM-2 illumination feasibility와 가능한 illuminator ID
- truthUsed = false

release 필수조건:

1. mode가 `MANUAL`
2. 선택된 익명 track이 confirmed surface track
3. 운용자 식별이 `HOSTILE` 또는 `TRAINING_TARGET`
4. `FRIEND`, `NEUTRAL`, `UNKNOWN`은 발사 차단
5. surface missile FCS가 허용 상태
6. VLS·전투체계·무기 inventory 정상
7. SM-2는 SPG-62 조사 feasibility와 예약 성공
8. ESSM은 ARH handoff basket 유효

`SEMIAUTO` 및 `AUTO`는 수상표적에 대해 항상 `AUTOMATIC_SURFACE_ENGAGEMENT_PROHIBITED`를 반환한다. 기존 공중위협 자동교전은 변경하지 않는다.

## 표적 조준점과 유도

전투체계는 표적 profile 길이·폭·entity ID를 읽어 조준하지 않는다.

- midcourse aim state는 익명 EKF position/velocity에서 생성
- 수직 기준은 관측된 surface reference와 평균 해면을 사용한 보수적 aim-height policy로 생성
- 표적 truth geometry는 최종 물리 충돌에서만 사용
- SM-2는 제한적 loft 후 SPG-62/SARH 측정으로 terminal descent
- ESSM은 짧은/중거리 surface corridor 후 ARH acquisition basket 진입
- 두 무기 모두 terminal sea guard를 유지하되, 유효한 ship-intercept corridor 안에서만 함체 높이까지 하강 허용
- track 오차가 크면 임의 Pk로 보정하지 않고 실제 miss 또는 sea impact가 발생

정확한 aim height와 corridor 수치는 C2/C3 결정적 sweep에서 선정하며 공개 실장값으로 주장하지 않는다.

## 표적함 종말 피해 경로

대수상 missile terminal은 다음 순서를 따른다.

1. 매 fixed tick에서 미사일 이전 위치와 현재 위치를 보존
2. terrain, sea surface, target 3D hull과의 첫 swept contact를 비교
3. proximity fuze가 물리 contact보다 먼저 유효하면 실제 burst point에서 fragment/blast packet 생성
4. hull contact가 먼저면 `CONTACT_DIRECT_ACTION`으로 WIP12F boundary traversal 실행
5. SM-2/ESSM 공통 ordnance spec으로 탄체 kinetic penetration, fragment, blast, fuze 결과 생성
6. 표적 local coordinate로 변환한 damage packet을 surface-target adapter에 단 한 번 적용
7. 파괴구, 침수, 화재, 장갑 약화, 종강도/용골 피해 갱신
8. damage model 결과만 mission kill/structural kill을 판정하고 `alive=false` 즉사식을 사용하지 않음

필요한 공통화:

- B3의 `surfaceTargetTerminalGeometryWip13B3()`를 함포 전용 이름/입력에서 ordnance-neutral geometry adapter로 승격
- WIP12F packet → surface target runtime 변환기를 `MK45`, `SM2`, `ESSM` 공통 consumer로 구성
- 동일 impact event ID의 중복 적용 금지
- proximity burst와 contact burst가 동시에 이중 적용되지 않도록 earliest-valid-event arbitration 유지

## 구현 단계

### WIP13C1 — 공통 계약·release foundation

- `SURFACE_MISSILE_ENGAGEMENT_PROFILE`과 SM-2/ESSM mode별 policy 추가
- 수상전용 manual identity gate 추가
- anonymous surface missile FCS quality 계산기 추가
- SM-2 SPG feasibility/예약 사전검사 추가
- ESSM ARH handoff basket 검사 추가
- 공중/ASM 자동교전과 수상 수동교전 경로를 명시적으로 분리
- ordnance-neutral surface terminal geometry/damage adapter와 진단 fixture 작성
- 이 단계에서는 live UI surface launch를 아직 활성화하지 않음

완료 기준:

- `UNKNOWN/FRIEND/NEUTRAL`, `AUTO/SEMIAUTO`, 저품질 track 발사 0회
- `HOSTILE/TRAINING_TARGET + MANUAL + 유효 FCQ`만 release candidate
- gate와 adapter가 truth ID 없이 결정적 검사 통과

### WIP13C2 — SM-2 제한적 SARH 대수상 교전

실제 `WIP13C5`에서 완료했다.

- `spawnMissile()`에 `LIMITED_SURFACE_SARH` branch 연결
- launch 전 SPG-62 예약 commit 및 EMCON 차단/해제 정책 명확화
- surface-specific midcourse/terminal corridor 연결
- 실제 SPG illumination → SARH physical echo → missile local track 유도 확인
- 조사 상실/coast/reacquire 및 sector/hardware failure 처리
- swept hull collision과 SM-2 WIP12F target damage 연결
- contextual `SM-2 SURF` UI 및 hold reason 표시

완료 기준:

- 정상 조사에서 실제 선체 hit 및 damage packet
- SPG sector/LOS/손상/EMCON 실패 시 발사 차단 또는 유도 실패
- 지형·해면 클러터가 SARH 품질에 실제 영향
- surface truth ID가 release/guidance/UI에 없음

### WIP13C3 — ESSM Block 2 ARH 대수상 교전

실제 `WIP13C6`에서 구현했다. 브라우저 실플레이 확인 후 C7 마무리로 넘긴다.

- `spawnESSM()`에 `SURFACE_ARH` branch 연결
- composite track midcourse와 surface acquisition basket 연결
- 기존 physical RF echo, sea/terrain clutter, monopulse, EKF, ECCM 경로 그대로 사용
- SPG 지원 유/무에 따른 연속적 품질 차이만 허용하고 필수 하드게이트로 만들지 않음
- ARH 획득, 오획, coast, reacquire, terminal descent 검증
- swept hull collision과 ESSM WIP12F target damage 연결
- 수상 SM-2 pitch-over 권한 이양에 실제 속도벡터 heading/pitch 정렬 조건 추가
- 수상 SM-2에 predictive sea-clearance guard 적용
- 수상 SARH/ARH/DL estimator state의 짧은 source-local low-pass로 좌우 hunting 억제
- ESSM 수상 midcourse 80 m / terminal 2 m floor와 13.5 km handoff를 `SIM_TUNED_PUBLIC_UNKNOWN`으로 명시
- contextual `ESSM SURF` UI 및 ARH state 표시는 C7 운용 UI 마무리에서 정리

완료 기준:

- SPG 없이도 조건을 만족하면 ARH 대수상 hit 가능
- 나쁜 clutter/track basket에서는 실제 miss·sea impact 가능
- seeker truth lock ID 없음
- 실제 hull hit만 contact damage를 발생시킴

### WIP13C4 — 운용 UI·회귀·마무리

- 선택 surface track 카드에 SM-2/ESSM surface FCS 상태 표시
- 버튼 라벨, inhibit reason, SPG assignment, ARH handoff 상태 표시
- 발사 후에도 identity/track/support 상실 정책 재검사
- 동일 표적 다중 발사와 SPG 채널 공유/경합 검사
- 1×/8×/16× 결정성, 64× 성능 검사
- 2D/3D 전환 무영향 검사
- 실제 WebGL 브라우저에서 발사, 비행, 충돌, 파괴구/화재/침수 확인

## 필수 회귀 행렬

| 조건 | SM-2 | ESSM |
| --- | --- | --- |
| `UNKNOWN` surface | 발사 금지 | 발사 금지 |
| `FRIEND/NEUTRAL` surface | 발사 금지 | 발사 금지 |
| `HOSTILE/TRAINING_TARGET`, MANUAL | 조건부 허용 | 조건부 허용 |
| AUTO/SEMIAUTO surface | 발사 금지 | 발사 금지 |
| SPY 단독 대형함 FCQ 충분 | SPG 가능 시 허용 | ARH basket 가능 시 허용 |
| SPQ 최신 갱신 | 품질 개선 | 품질 개선 |
| 모든 센서 coast | covariance 임계 초과 시 금지 | covariance 임계 초과 시 금지 |
| SPG-62 불가 | 발사 금지/공중탄 지원정책 보존 | 발사 가능, optional SARH만 상실 |
| EMCON | SM-2 정책에 따라 차단 또는 명시적 수동 해제 | 현재 doctrine상 차단 유지 |
| 지형 차폐 | 조사/DL/echo 실패 | DL/ARH echo 실패 가능 |
| 심한 sea clutter | SARH 품질·획득 저하 | ARH 품질·획득 저하 |
| hull contact | WIP12F contact packet | WIP12F contact packet |
| proximity before hull | fragment/blast packet 1회 | fragment/blast packet 1회 |
| miss/sea impact | 표적 damage 0 | 표적 damage 0 |

## 하지 않을 것

- SM-2/ESSM을 전용 대함미사일 수준의 장거리 sea-skimming weapon으로 만들지 않음
- 분류 confidence만으로 `HOSTILE` 또는 자동 수상교전권한 부여하지 않음
- surface target truth object를 release·weapon selection·midcourse guidance에서 직접 조회하지 않음
- 낮은 track 품질을 임의 Pk 보너스로 보정하지 않음
- 선박 명중을 항공기/ASM용 `alive=false` 또는 단일 Pk kill로 처리하지 않음
- 13C에서 WIP14A 좌표계·VFX 전면 리팩터를 섞지 않음

## 권장 시작점

공통 foundation은 실제 `WIP13C4`, SM-2 제한적 대수상 SARH 실발사는 `WIP13C5`, ESSM `SURFACE_ARH` live 연결과 수상 미사일 유도 안정화는 `WIP13C6`에서 구현됐다. 다음 실제 코드 단계는 `WIP13C7`이며 운용 UI/상태 표시, 다중 발사와 SPG 경합, 시간배속 결정성, 2D/3D 전환 무영향, 실제 브라우저 발사·비행·충돌·피해 확인을 마무리한다. SPG-62는 ESSM에서 계속 필수 토큰이 아니라 선택적 품질 기여로 유지한다.
