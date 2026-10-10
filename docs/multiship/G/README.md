# Multi Ship G — FLEET 조작·아군 관측 공유·방어 분담

**FLEET → 선택 함정 네트워크**에서 링크, 트랙 공유, 방어 분담을 각각 선택한다. 공동 탐색 레이더는 개별 운용/모두 탐색/모두 침묵/자함만 탐색/아군함만 탐색을 지원한다. 레이더 침묵 중에도 링크 무선은 송신한다. 기존 자함 EMCON 또는 FLEET의 선택 함정 EMCON을 직접 누르면 개별 운용으로 돌아간다.

## FLEET 조작

NAV/ARM/FLEET/DEBUG 네 탭이다. **함정 변경**으로 기존 자함과 배치한 아군함 사이를 전환한다. FLEET의 속력/타각, 수동 또는 자율 방어, EMCON, 현지 표적/운용자 식별, SAM·함포·Harpoon 발사는 선택 함정의 native 포트에 전달한다. LINK/트랙 공유/방어 분담도 선택 함정 설정이며 공동 탐색 레이더 정책은 함대 전체에 적용한다.

기관 명령은 기존 C17 기관전령 값으로 환산한다. 조종 적용은 자함의 기존 항로 자동 조타를 해제한다. 함포는 설치된 선수/후미 마운트를 선택할 수 있다. CG의 Harpoon 8발과 DDG의 Harpoon 0발, 다른 탄약고와 현지 track ID를 분리한다. 레이더 보호 식별·관측 신선도·수동 발사 정책·native 사각/손상·사통·발사 간격/재고 조건을 통과해야 탄약을 소비한다. 교전 관제가 AUTO이면 FLEET 수동 발사는 보류한다.

FLEET 표적 목록은 해당 함정의 현지 확정 추적만 표시하며 공유 전용 파일을 사통에 주입하지 않는다. 운용자 적성 지정을 네트워크의 fresh FRIEND/NEUTRAL 보호에 우선시키지 않는다. `fleetCommandG(id, command)`는 아군 owner만 허용하고 잘못된 필드/타각/속력/owner-local track 주소를 무변경 거부한다. `ShipRuntime.combatSystem.operatorG`가 현지 표적 선택과 명령 결과를 갖고 `ENGAGEMENT_RUNTIME.fleetOperatorG`는 UI 명령 목적지만 가진다.

**NAV·ARM·CIC 및 3D 상단 기존 교전 버튼은 원래 자함 기준이다.** 함정의 PLAYER/ALLY 역할이나 global profile/runtime을 교환하지 않는다. 아군 수동 조종·교전은 FLEET에서 한다. FLEET 페이지는 desktop 세 열/mobile 한 열의 세로 스크롤이며 변경 버튼은 아군함이 없으면 비활성이다. 탭 전환과 함정 선택 자체는 항법/탄약/교전 상태를 바꾸지 않는다. import/reset/deployment에서 선택과 현지 표적/명령 표시를 초기화한다.

3D `아군함 보기`는 pointer-events가 꺼진 툴바의 직접 자식 버튼이어서 실제 입력을 받지 못했다. 해당 버튼의 pointer 입력을 명시 허용하고 native press 경로에 연결했다. 레이블은 focus/reset/retire와 함께 갱신한다. FLEET의 **선택 함정 3D 보기**도 실제 선택한 아군 또는 자함 카메라를 연다. 마우스 클릭과 터치 탭으로 actual RAF 이후 카메라 위치/함정 중심/복귀와 상태 무변경을 각각 확인했다.

## 정보와 권한

`ShipRuntime.combatSystem.networkG`가 수신 파일, 통신 대기열, 연결 상태, 설정 및 한시적 방어 배정을 소유한다. 불변 함종 프로필과 다른 함정의 사통을 바꾸지 않는다. 2Hz 송신, 18 fixed ticks(0.3초) 지연, 2초 fresh/12초 coast이며 모두 **게임 SIM-TUNE**이다. 실제 Link 16 장비나 CEC 성능을 재현했다는 의미가 아니다.

전송은 자기 항법의 위치·속도·오차 또는 현지 레이더가 실제로 측정한 confirmed 파일의 6D 추정·공분산·측정시각·분류·식별·평가·방어 가능 여부만 받는다. 발신자/발신 파일 번호는 무선 주소이며 물리 표적 ID가 아니다. 적 실제 ID, 위치, 미사일 항법·시커·생존 상태는 포함하지 않는다. 적함은 아군 링크에 가입하지 못한다. 전송 경계에서 참가 함정 자신의 radio on/off, 장비/승조원 가용성·지평선·지형 LOS를 검사한다.

수신 측은 6D NIS와 최대 거리/속도 차이로 파일을 연관한다. 가까운 두 후보가 비슷하면 결합하지 않고 현지 트랙과 일대일 대응한다. 시각이 같은 재전송은 새 관측이나 hits로 세지 않는다. 알 수 없는 측정 간 상관은 고정 0.5 covariance intersection으로 보수적으로 정정한다. 동일 공분산을 반복 전달해도 불확실성이 절반으로 줄지 않는다. 예측과 오래된 정보에는 오차가 커진다.

공유 정정은 **CIC 표시용 detached 값**이다. 현지 canonical EKF, 무장 사통, SAM DL 및 표적 추정은 현지 관측을 사용한다. 공유만 있는 접촉은 점선·NET·관측 나이·오차로 나타나며 UNKNOWN이다. 인증된 아군의 자기 항법 보고는 ALLY/FRIEND로 표시한다. 공유 HOSTILE 보고는 자함의 UNKNOWN을 자동발사 가능한 적으로 승격하지 않는다. 신선한 공유 FRIEND/NEUTRAL과 운동학적으로 연관된 현지 파일에는 제한적 발사 보류를 적용한다.

## 방어 분담과 단절

기존 현지 AUTO가 승인한 표적에 한해 VLS SAM 준비/탄약/추천·own in-flight 상태를 방어 bid로 보고한다. 자함은 **전달된 관측 보고와 자기 관측만** 사용해 primary를 정하고 1.8초 배정을 보내며 아군의 private 사통을 직접 읽지 않는다. 배정은 수신 함정의 최근 현지 FCS와 다시 연관해야 한다. 실제 VLS 주기 및 탄약 소모 함수에서 ROE/식별/사통·SPG/사각·재고와 네트워크 동의를 재검사한다. 이미 비행 중인 요격탄도 배정에 고려한다.

수동 발사 권한은 네트워크가 재배정하지 않는다. 접근시간 8초 이내 긴급 자위와 RAM/Phalanx의 현지 근접방어는 분담 때문에 막지 않는다. 공유 보호 식별과 기존 ROE는 유지한다. 링크가 끊기거나 배정이 만료되면 개별 방어로 돌아가며 배정 없이 기다리는 시간은 1.2초로 제한한다. 이 구현은 중복 SAM 살보 억제이며 원격 관측만으로 발사하는 CEC나 분산 사통은 후속이다.

공동 레이더 정책도 지연된 명령과 2초 lease로 적용한다. 연결이 사라지면 각 함정의 개별 EMCON 상태를 복원한다. 그룹 정책은 저장하되 일시적으로 적용된 레이더 값 대신 개별 기준값을 저장한다. 수동 ESM, 방어 ECM, 링크 송신과 탐색 레이더 침묵을 구분한다.

## 하푼 오인 완화

F에서는 첫 연관 뒤에도 추정 속도 45m/s 미만, 관측 간격 4초 초과 또는 선회로 운동학 gate를 벗어나면 발사 연관을 즉시 버렸다. 빔 방향에서 부정확한 속도 추정이나 파일 교체가 발생하면 현지 hostile-intent가 다시 요격을 허가할 수 있었다.

G는 발사 승인 기록과 **이전 익명 레이더 관측**의 위치/속도 오차·시각·기동 여유로 연관을 이어간다. 이미 확인된 파일은 8초 이내 재관측과 새 파일 alias를 검사하며, 애매한 재연관은 UNKNOWN/자동교전 보류다. 미관측 새 표적의 최초 연관은 기존 12초 발사 회랑·방향·속도 제한 및 발사 전 존재 파일 제외를 유지한다. 명확한 반대 방향 접근과 다중 후보는 FRIEND로 단정하지 않는다.

8초는 오인 완화용 SIM-TUNE이며 영구 우군 표식이 아니다. 위치 표시는 기존 4초 관측 coast 뒤 사라진다. 실제 미사일 월드·INS 위치·ARH 상태·생존 상태를 읽어 아군이나 위치를 생성하지 않으며 **Harpoon DL=0**을 유지한다. 신선한 레이더로 확인한 own FRIEND 파일은 아군 링크로 공유할 수 있다. INS/ARH/부스터/웨이포인트 및 물리 커널은 그대로다.

## 저장과 수명주기

배치 schema는 F_1, fleet는 `AEGIS_NAVAL_PHYSICAL_FLEET_G_1`, 설정은 `AEGIS_FRIENDLY_NETWORK_G_1`이다. enabled/shareTracks/cooperativeDefense는 bool, groupEmcon은 명시 enum이며 외함은 INDIVIDUAL만 저장한다. 적함의 링크 설정은 모두 false다. 네트워크 설정은 기존 detached preflight를 통과한 뒤 복원한다. F/B 및 이전 no-fleet 저장은 명시 migration으로 기본 설정을 추가한다. 잘못된 설정은 authoritative 상태를 바꾸지 않는다.

보고/대기열/heartbeat·lease·공동 EMCON 실행 상태는 저장하지 않고 deferred transient로 명시한다. reset/deployment/import/retire가 이를 비운다. 외함 퇴역 시 기존 EW context/물리 decoy도 함께 폐기한다. F의 원래 해상효과·3D 모델·피해 구멍·고정 셀·CG RAM0 및 60/120/20Hz 주기는 보존한다.

## 재현과 검증

```bash
npm ci --prefix docs/multiship/G --ignore-scripts --no-audit --no-fund
python docs/multiship/G/build.py archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html artifacts/G.html
python docs/multiship/G/verify_static.py archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/static
python docs/multiship/G/verify_fleet.py Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/fleet-ui
python docs/multiship/G/verify_fleet.py Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/fleet-camera --suite camera
python docs/multiship/G/verify_network.py Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/network
python docs/multiship/G/verify_cooperation.py Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/cooperation
python docs/multiship/G/verify_harpoon.py archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html Aegis_SIM_v48_WIP_MULTI_SHIP_G.html artifacts/harpoon
```

최종 SHA별 결과는 [검증 집계](evidence/verification-summary.json), 실행 조건은 [PERFORMANCE](PERFORMANCE.md), 후속 범위는 [DEPENDENCIES](DEPENDENCIES.md)를 따른다. `patch-index.json`은 F 원본 함수의 Python 문자 경계·SHA이며 UTF-16 AST offset을 그대로 사용하지 않는다. builder는 원본 SHA·각 변경 1회 일치를 요구한다. 원본 assets0~12·모델과 비행/물리 커널을 보존하고 record13만 바꾼다. Python·Node와 기존 [Playwright 의존성](../../bunkerhill/K/requirements.txt)을 사용한다.

## 현재 한계

- 무선은 기존 항법 레이더 높이를 기준으로 한 LOS/장비 가용성 추상화다. 별도 통신 안테나·L/UHF 파형·패킷 손실/암호·링크 재밍을 모델링하지 않는다. 기존 SLQ I/J/X 재밍을 링크 대역에 임의 적용하지 않는다.
- 파일96, 보고32+SELF, 대기열16, 로그128, 현지 연관 후보128로 비용을 제한한다. 이는 실장비 용량이나 휴대폰 FPS 보장이 아니다.
- 신선한 현지 관측이 없으면 공유 화면만 제공하며 CEC 원격 사통·헬기/공격·기동 전술 AI는 아직 없다. 기존 DDG EW 안테나 등록·IFF 재인증 수명주기 한계는 F와 같다.
