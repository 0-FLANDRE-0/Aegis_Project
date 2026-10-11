# H4 — 함대 전술·합동 기동

H3 final `af1eade2d418b215720a68a5b902aae0d9387203` 위에 owner별 팀 설정과 지연 메시지를 추가한다. 한 자함·한 아군함·한 적함이라는 현재 배치 한도를 유지한다. 아래의 주기·간격·상관·자위 조건은 게임 SIM-TUNE이며 실제 해군 전술이나 Link 16 규격이 아니다. 최종 완료 판정과 직접 검사 수치는 루트 상태와 `evidence/verification-summary.json`을 따른다.

## 운용

1. FLEET에서 원래 자함과 아군함 각각 **함대 전술 ON**, 기존 **링크 ON**으로 설정한다. 기본은 OFF다. 원래 자함이 선도함이며 PLAYER/ALLY 역할·global runtime·프로필을 교환하지 않는다.
2. 아군함의 **전술 AI ON + 기동 AI 재개 + AUTO**를 설정한다. 선도함은 기존 항로·수동 항법으로 조종한다. 전형은 종렬/좌현 경계/우현 경계, 원하는 간격은 1/2/4 km다. FLEET의 선택 함정에 `임무 · 전형 적용`으로 저장하며 다른 owner의 설정을 복사하지 않는다.
3. 아군함은 받은 선도함 항법 보고의 위치·속도·heading·오차·시각으로 전형 위치를 계산하고 native H2 타/기관 명령으로 기동한다. 실제 선회·가감속·피해·침수 물리를 유지한다. 간격은 원하는 위치이며 순간 배치나 보장된 실제 간격이 아니다.
4. 양쪽 임무를 **수상전 · 공격 분담**으로 설정하면 관측된 같은 수상 접촉의 공격 담당을 정한다. 기존 트랙 공유 ON과 H3 공격 AI·현지 적성 식별·각 함정의 별도 1/2발 동의가 필요하다. 설정 ON이나 받은 HOSTILE 보고만으로 동의를 만들지 않는다. DDG-119는 현재 Harpoon을 장착하지 않는다.
5. FLEET의 **수상 자위 판단 ON**은 별도의 관측 기반 식별 정책이다. 자함/아군 기본은 OFF(IDENTIFIED_ONLY), 새 시나리오의 적함은 SELF_DEFENSE다. 이 선택도 아군의 공격 동의를 대신하지 않는다.

대공 방어 기동·수동 NAV/FLEET/지도 명령·MANUAL/HOLD·master OFF·기동 OFF가 전형보다 우선한다. 기동 AI ON/OFF로 수동 hold를 지우지 않고 명시 재개로 인계한다. 팀 OFF는 전형 명령을 즉시 반환하며, 보고가 2초를 넘기면 개별 항법으로 돌아간다. 팀 OFF와 공격 AI OFF는 별도 설정이다. 팀 OFF 뒤에도 기존에 동의한 H3 개별 공격은 유지될 수 있다. NAV/ARM/CIC와 기존 3D 상단 버튼은 원래 자함이며 아군 조작은 FLEET에서 한다.

## 팀 메시지와 판단

`ShipRuntime.combatSystem.teamH4`가 설정·대기열·수신 peer·전형·한시적 배정·발사 접수·자위 근거를 소유한다. G packet/보고 계약을 변경하지 않고 H4 전용 메시지를 기존 아군 radio/LOS/장비 가용성 경계로 보낸다. 센서/G phase 다음의 fixed tick에서 처리하며 2 Hz 송신, 18틱(0.3초) 지연, 2초 fresh다. 같은 sequence 재전송, 미래/오래된 시각, 잘못된 필드·covariance·용량을 상태 변경 전에 거부한다. 적함은 아군 transport에 가입하지 못한다.

보고는 sender 자신의 항법, 현지 fresh SURFACE KF·공분산, **자기** H3 동의와 native 발사 준비 가능 여부, 자기 native 실제 발사의 관측 cue 접수만 담는다. 비행 탄체의 위치·시커·생존·명중·BDA나 표적 physical ID, peer private FCS를 사용하지 않는다. G 트랙 공유 OFF면 H4도 항법만 주고받으며 수상 bid/접수/배정은 송수신하지 않는다.

선도함은 자기 현지 파일과 **받은** bid를 보수적인 6D 운동학 게이트로 연관한다. 서로 다른 현지 번호를 사용할 수 있으며 모호한 후보는 결합하지 않는다. bid는 기존 native readiness·손상·범위·예측 basket·발사축/해안/아군 경로를 실제 preview한다. preview는 동기 함수이며 기존 exact capability를 `finally`에서 복원하고 요청/발사 포트를 호출하지 않는다. 수동 준비를 빌리지 않는다. 실제 release 때 H3와 팀 gate를 재검사한다.

두 owner의 설정·개별 동의가 유효할 때 primary를 한 척으로 배정한다. 기존 primary의 짧은 native 문 개방/발사 간격을 유지하고, 교체 시 이전 1.8초 lease가 끝날 여유를 둔다. 최초 링크/배정 대기는 2.4초로 제한한다. 링크 소실·배정 만료 뒤 개별 native 권한으로 돌아가며 기존 G VLS 분담·RAM/Phalanx 자위는 H4 공격 배정으로 차단하지 않는다.

같은 접촉에 공동 2발 접수가 있으면 90초 동안 추가 AI 살보를 보류한다. 접수는 sender/serial로 중복 제거하고 배정·동의 소진·heartbeat 소실 뒤에도 만료까지 기억한다. 표적이 파괴되었다는 판정이 아니며 DL 없는 하푼의 실제 결과를 추측하지 않는다. 링크가 처음부터 없거나 접수를 받지 못한 상황의 모든 중복 공격을 보장해서 막는 분산 합의 체계는 아니다. 새 관측이 이전 cue와 연관되지 않으면 같은 표적으로 단정하지 않는다.

## 전형과 자위 식별

전형은 수신 SELF 항법에 대해 정한 상대 위치다. STATION/좌우 우회/HOLD 4개 후보를 H2의 피해가 반영된 예측과 native 교통·해안 검사로 비교한다. 받은 선도함 항법도 교통으로 넣으며 chart segment를 추가 검사한다. 공통 H2 baseline과 명령 소유권을 사용해 전형과 방어가 중복 조종하지 않는다. 실제 heading/speed/position을 직접 쓰지 않는다. 움직임과 해상효과·3D는 기존 물리/표시가 담당한다.

SELF_DEFENSE 정책은 fresh confirmed 현지 수상 접촉과 실제 관측된 incoming ASM 파일을 요구한다. 승인된 위협·분류/속도·고도·CPA와 짧은 역방향 운동학으로 발사원이 **하나**이고 위치 오차가 작아야 한다. 반복된 별도 관측을 받은 뒤 30초짜리 owner-local 자위 근거를 만든다. `_operatorIdentity`를 덮어쓰지 않고 H3의 별도 적성 근거로 사용한다. operator FRIEND/NEUTRAL·IFF·G 보호가 우선이며 늦게 아군으로 판명된 무장도 근거를 해제한다. 번호/객체 교체에 근거를 승계하지 않고 저장으로 복원하지 않는다.

IFF 무응답·ESM-only·다른 함정의 HOSTILE 보고·world faction·멀리서 처음 본 접근 무장만으로 수상 발사원을 적성 지정하지 않는다. 따라서 **발사원을 직접 관측해 연관하지 못한 미식별 적함의 첫 공격은 계속 보류**된다. 이 구현은 자유 교전 ROE나 모든 launch-origin 식별을 완료했다는 뜻이 아니다. 원래 native 대공 자위와 explicit operator/scenario designation은 유지한다.

실제 공동 시험에서 peer가 관측한 자함 반사가 FRIEND 보호 보고로 돌아와 자함 발사를 막는 경우를 수정했다. 자기 항법과 속도가 일치하고 작은 2σ 오차 타원이 자함 중심부의 등록 함체 안에 들어가는 fresh FRIEND TRACK relay만 자기 위치로 처리한다. 다른 현지 파일에 붙은 보고, 다른 함정 SELF, NEUTRAL, 주변 선박·큰 오차·stale 보고는 보호한다. 완벽한 식별/오격 방지나 모든 곡선 경로의 충돌 회피를 보장하지 않는다.

## 저장·검증·이후

fleet `AEGIS_NAVAL_PHYSICAL_FLEET_H4_1`, team `AEGIS_TEAM_TACTICS_H4_1`은 schema/enabled/mission/formation/spacingM/surfaceRoe만 저장한다. 현재 필수 설정 누락·타입·extra는 모든 owner detached preflight 후 zero-writes 거부다. H3/H2/H1/G/F/B/no-fleet은 팀 OFF·IDENTIFIED_ONLY로 명시 migration하고 pending 적함도 새 자위 권한을 얻지 않는다. 메시지·목표·배정·접수·근거는 transient이며 import/reset/deployment/retire에서 비운다. 저장 항법은 H2의 원래 operator 요청을 사용한다.

최종 HTML에 대해서만 정적·내장 selftest·측정 fixture·자연 RF·1/8/16/64배속·마우스/터치·H3와의 동일 물리/RNG·기존 방어/EW·native RAF/WebGL 피격·복원을 검사한다. 역사/폐기 draft 검사를 합산하지 않는다. [조건](PERFORMANCE.md), [남은 두 단계](DEPENDENCIES.md), [업로드](GITHUB_HANDOFF.md)를 따른다. GitHub Actions는 사용하지 않고 최종 원본 직접 검증을 gate로 사용한다.
