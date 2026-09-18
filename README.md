# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP11C.html`](Aegis_SIM_v48_WIP11C.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP11C.md`](AEGIS_PLAN_STATUS_v48_WIP11C.md)
- HTML SHA-256: `464e1fc4a7e3ef9565bc32ce42e7e5a112041a977ee96fb7bdb5920f7410c01f`
- 상태: WIP11C 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP11C 핵심 범위

- 요격된 대함미사일의 위협 객체는 즉시 퇴역시키되, 물리 잔해는 별도 월드 entity로 존속
- WIP11B의 미사일 부위 손상·구조 손상·탄두 상태를 잔해 분열, 질량, 무결성, 연소에 연결
- 잔해의 속도 상속, 항력·중력·텀블링, 함체·지형·수면 충돌을 `60 Hz` 고정 tick에서 계산
- 수면 진입과 저고도 폭발에 물기둥·방향성 비산·확산 링·잔류 포말 효과 추가
- 연소 잔해에 다층 화염·짙은 검은 연기·화염 조각을 표시해 불타는 본체와 파편의 비행을 가시화
- 격추·근접신관 보고 직후 `KILL_ASSESSMENT`로 AUTO 사격권을 즉시 보류하고, 직접 분해 보고에는 DL·SPY 무기지원·SPG-62 예약/조명을 같은 틱에 해제
- 익명 SPY 트랙도 truth 역조회 없이 SM-2/ESSM의 `assignedTargetId`, RAM의 `targetId`, Phalanx 탄의 사격 당시 track ID를 직접 분해/BDA 보고까지 전달
- 직접 분해 보고의 시각·위치·속도와 엄격한 관측 운동학 게이트로 같은 표적의 격추 전 중복/coast 트랙도 BDA에 묶어 남은 `MEM-?` 유령을 닫고, 격추 뒤 일관된 새 측정이 들어오면 즉시 정상 위협평가로 재개방
- 앞선 약한 `FUZE_DETONATION` 기록이 실제 `DIRECT_BREAKUP`으로 승격될 때 효과 시각·종말 보고·해결 상태를 실제 분해 틱으로 함께 갱신해, 같은 틱의 마지막 SPY 플롯이 격추 후 생존 반사로 오인되는 경쟁 조건 차단
- 원본이 LOST가 되는 첫 평가 프레임에 대체 alias가 생겨도 SAM·RAM·Phalanx·CIWS cue·SPG-62 live ownership/예약·선택 lock을 대체 track ID로 함께 인계
- 직접 분해 후 `0.35초` 무응답이면 `DESTROYED`; `1.25초` kill-mark 뒤 원래 미사일의 유령 MEM 표시는 숨기되 별도 물리 잔해는 계속 비행하며, 일관 관측이 재개될 때만 `THREAT`로 복귀
- 우군 요격 보고 없이 고속 강하 ASM이 소실된 경우에도 적 truth 생존값을 읽지 않고, EKF 추정 고도·강하율·수면도달 시간·무반사와 함체 밖 예상 수면교차점을 확인해 `OBSERVED_SEA_IMPACT / HARMLESS`로 종결하고 MEM 위협·AUTO 재교전·SPG-62 지원을 해제
- 거의 수직인 Mk41 deck-normal의 미세 수평 성분이 SM-2 발사 방위를 정반대로 덮어쓰던 오류를 수정해, 셀 내부 위치·속도는 실제 deck-normal을 따르면서 탄체 방위는 명령된 표적 방위를 보존
- 요격탄 연기를 `8배` 수명과 원래의 `3.5배` 간격으로 길고 성기게 남기며, 수명 `36%` 이후 3개 중 2개를 유지해 노후 구간 유효 간격을 `5.25배`로 제한
- 노후 연기 확산·가시 잔류를 강화하되 요격탄/전역 입자 상한은 `9,000/12,000`으로 유지
- Kh-32 연기는 `5 km` 이하에서 생성하지 않고 `5–8 km` 전이 후 `8 km` 이상에서 정상 표시하며, Kh-35U는 기존 무연 터보제트 표현 유지
- 잔해의 함체 재충돌은 기존 DUD 관통·파공·침수·충격량 경로에 운동 피해만 전달
- 잔해 난수와 3D 표현을 전투 난수·위협 판단에서 격리하고 WIP11B 안전 계약 보존

## 검증

- 기존 정적 계약 6종과 WIP11C 전용 `32/32` 항목 계약, HTML JavaScript 문법 검사 통과
- Playwright 전체 `28/28 PASS` (로컬 Three.js 경로 사용)
- 실제 WebGL에서 물리 잔해 mesh 3개와 물기둥·수면 링·포말 생성 확인
- SM-2/ESSM/RAM의 `8배` 수명·저밀도 노후 확산/잔류·`9,000/12,000` 입자 예산과 ASM 고도 게이트 실제 WebGL 검사 통과
- BDA 회귀에서 직접 분해 직후 SPG/DL/SARH 지원 해제, AUTO 추가발사 `0`, `KILL_ASSESSMENT → DESTROYED → 유령 MEM 숨김 → THREAT` 관측 복구 확인
- 격추 전부터 존재한 중복 `MEM-?` 파일의 BDA 상관·숨김과 격추 뒤 coherent return 재개방, 첫 LOST 프레임 대체 alias의 전 무장/SPG 소유권 인계 회귀 통과
- 실제 익명 SPY track 회귀(seed `991212`)에서 ESSM 실비행·요격 후 `DIRECT_BREAKUP`이 배정 track ID에 기록되고, SPG/DL/SARH 즉시 해제·표시 ASM `0`·cleanup 신관 보고의 증거 강등 없음 확인
- 실제 Kh-32/ESSM 회귀(seed `112000`)에서 실제 분해 5 tick 전의 신관 보고를 강제로 재현하고, `DIRECT_BREAKUP` 승격 시 효과 시각이 실제 격추 tick으로 재기준화되어 같은-tick SPY 플롯이 위협을 재개방하지 않으며 AUTO 추가발사 `0`·지원 즉시 해제·표시 ASM `0`·독립 잔해 존속을 확인
- 실제 Kh-32/AUTO 회귀(seed `932008`)에서 SM-2가 `LOW_SPEED`로 빗나간 뒤 물리 표적 소실 시 남던 `MEM-?`를 16 tick 안에 관측 수면충돌로 종결하고, 거짓 격추 판정 없이 표시 ASM `0`·SPG/AUTO 지원 해제를 확인
- SM-2 네 방위(`-135/-45/+45/+135°`) 발사에서 Mk41 셀 내부 방위 오차 `0°`, 초기 유도 정렬 오차 최대 `0.099°` 확인
- WIP11B 대비 유도·Pk 핵심 함수와 Pk 곡선 exact parity, 같은-seed 12건의 이산 요격 결과·난수 상태 exact parity 및 연속값 `1e-8` 상대 허용오차 내 수치 동등성 확인
- 실제 WebGL 최악조건 부하 계측 완료: 최종 헤드리스 실행에서 9,000→12,000 가시 연기 증가 시 동기 렌더 비용 약 `+18.42 ms`; 실행별 편차가 크므로 실기 절대 FPS가 아니라 정확한 `+3,000` draw-call 증가와 상한 준수만 계약으로 사용
- 동일 fixture의 잔해 궤적·수면 사건 exact 결정성, 고고도 폭발 비결합, 저고도 폭발 결합 확인
- 기존 CIWS·함체·침수·승조원·재질·운영 snapshot·3D 다중 시점 회귀 통과
- GitHub Actions는 WIP11C 전용 정적/브라우저 job을 포함해 총 `20`개 job으로 구성

## 다음 단계

- WIP12A: 공통 종말탄도 상태·결과 계약과 경계/빈 공간/물질 볼륨 traversal 기틀
- 확정 설계: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- WIP12A에서는 하나의 만능 관통식이 아니라 공통 파이프라인과 regime별 solver interface를 만든다.
- 실제 함포 발사·외탄도·FCS 및 persistent damage patch 활성화는 WIP12A 범위 밖이다.
- WIP13: 해상사격 FCS
- WIP14: 간단한 표적함과 복수 함선 프로파일

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며, WIP10·WIP11·WIP11A·WIP11B는 각각의 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
