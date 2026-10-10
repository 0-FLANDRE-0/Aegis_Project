# F 이후 단계

현재: 배치 분리와 receiver별 전자전. 다음에는 전술 AI의 판단 입력을 만들기 위해 아군 네트워크의 최소 공통 기반을 먼저 구현한다.

1. 측정 시각·source·sequence·공분산·지연/packet loss·유효시간이 있는 아군 보고 전송. 수신자가 받은 추정치만 사용하며 truth ID/좌표를 넘기지 않는다. C의 외부 관측 포트를 확장한다.
2. local track와 network report 연관·중복 제거·불일치/정정·출처/age 표시. LINK-only 파일과 자기 센서 확인을 구분하고 식별/권한을 자동 복사하지 않는다.
3. 레이더 EMCON 명령/응답·지연·개별 함정 예외와 방사 관리. 레이더 침묵과 방어 ECM 정책을 분리한다.
4. 네트워크 기반 기본 방어 분담과 중복 살보 억제부터 검증한다. 타함 보고만으로 사통/발사를 허용하는 CEC급 합동교전은 별도 단계다.
5. 그 기반 위에서 관측·탄약·피해·기하 조건으로 기동/공격·살보/위협 우선순위 전술 AI를 구현한다. 먼저 own local defense, 이어 팀 전술을 검증한다.

DDG 실제 EW 안테나 등록 및 개별 손상·사각, IFF 재인증/운용자 override/track coast 수명주기도 후속 보완이다. 모든 단계에서 same-seed 고정 tick·strict snapshot·owner/RNG 분리와 FRIEND/NEUTRAL/UNKNOWN 보호를 유지한다.

헬기는 센서 보고 포트 이후 모델·비행·센서/운용을 연결한다. Harpoon은 기존 INS→ARH와 DL=0이며 네트워크로 미사일 truth telemetry를 만들지 않는다. 추후 토마호크는 사용자가 지정한 **RGM-109E Block Va Maritime Strike Tomahawk**를 대상으로 별도 profile/model/guidance/운용 계획을 세운다. 이번 F에 토마호크·헬기·공격 AI는 포함하지 않는다.
