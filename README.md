# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP12C.html`](Aegis_SIM_v48_WIP12C.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP12C.md`](AEGIS_PLAN_STATUS_v48_WIP12C.md)
- WIP12C 설계 계약: [`docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md`](docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md)
- WIP12B live ordnance 계약: [`docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md`](docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md)
- 공통 커널 설계: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- HTML SHA-256: `55c4c71ee05053820743ae3ce6cdf80cd07b34a92643062309700ff61530567d`
- 상태: WIP12C 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP12C 핵심 범위

- 정상 기폭 시 최대 4개의 결정적 `MACRO_FRAGMENT` 잔존체를 생성하고 각각 WIP12A event-driven traversal로 다시 추적
- 큰 잔존체의 질량·무결성·탄체축·속도·진행방향을 독립 상태로 전파하며 상세 구획의 재질별 경계, 실제 장비·탱크 체적과 반대편 외판을 순서대로 해결; 내부에서 막히면 출구를 만들지 않음
- 방향 변화마다 tapered hull의 다음 접촉과 국부 법선을 다시 계산하고, 138개 공간·78개 물질 체적을 10 m index로 좁혀 피격 순간에만 조회
- 미세 파편은 기존 통계 채널로 유지하고, 큰 잔존체와의 질량·에너지 ledger closure를 진단
- root 탄체와 모든 잔존체의 관통 corridor, 파괴구, 구조충격과 피해 채널을 부모 `DamagePacket`에 합쳐 한 번만 적용
- `impactEventId` 중복 적용 방지, 다중 관통선 승조원 노출, 다중 파괴구 침수, 명시적 폭발·열/소이 화재 consumer 연결
- 일반 충격·구조 충격량·비폭발성 불활성 파편은 화재를 만들지 않으며, 실제 연료/전기/탄약 volume을 때린 기계적 충격만 class별 최대 `1.8%/0.8%/0.6%` 이내의 결정적 희박 확률로 발화
- Kh-32/Kh-35U는 기존 피해·RNG exact parity를 보존하기 위해 잔존체 cascade를 `LEGACY_PREACCOUNTED_OBSERVATION_ONLY`로 기록하고 피해를 재적용하지 않음
- DUD는 탄두 기폭 cascade를 만들지 않음
- 외부 파괴구로 보이는 내부는 기존 coarse 침수구획으로 복원하고, 상세 138-space topology·hazard·crew는 명시적 `내부 구조` 모드에서만 표시
- 관통선, 폭발범위, 큰 잔존체 경로와 반대편 출구도 `내부 구조` 모드에서만 표시
- 내부 모드에서는 외형 재질을 투명화하고 coarse 침수구획은 숨김; 렌더러는 표시 전용이며 물리·피해·난수에 피드백하지 않음

## 검증

- WIP12C 정적 계약 `40/40 PASS`
- 정적 계약 파일 `10/10 PASS`; WIP12A `30/30`, WIP11C `32/32` 포함
- WIP12C Playwright `2/2 PASS`; core selftest failure `0`, 콘솔/page error `0`
- WIP12C 127 mm SAP fixture: root corridor `1`, 큰 잔존체 `3`, 반대편 외판 출구 `3`, 질량 closure error `0 kg`
- 합산 packet 최초 적용 `APPLIED`, 같은 `impactEventId` 재적용 `DUPLICATE_IMPACT_EVENT`; 침수·승조원·화재 consumer 연동 확인
- live Kh-35U 정상 피격은 관찰 전용 큰 잔존체 `4`가 상세 내부 재질에서 모두 정지해 반대편 출구 `0`, DUD는 `0/0`; 두 경로 모두 combat RNG 불변
- 최종 512회 traversal benchmark `0.2691 ms/impact`, 후보 감소 `65.9975%`, render-frame query `0`; 저속탄 내부 정지와 장비 volume 감속 검증
- 포화 fuel/lube 진단 발화 `57/4096`(`1.3916%`, 상한 `1.8%`), inert·shock-only 발화 `0`; 실제 boiler volume 적용 경로와 combat RNG 불변 확인
- 외부/내부 표시 분리, terminal-effect 가시성, macro 경로·출구 수 일치, 상세 구획 `138/138`, 외형 이탈 정점 `0` 확인
- WIP12A exact legacy adapter와 WIP12B archive 브라우저 회귀 각각 `2/2 PASS`
- 전체 Playwright `34/34 PASS` (로컬 Three.js 경로; 최종 전체 재실행 기준)
- Workflow YAML은 WIP12C 전용 2개 job을 더한 총 `26`개 job으로 구성

## 다음 단계

- WIP13: WIP12C 계약을 소비하는 제한적 표면교전 표적 승인·발사/FCS 경로
- WIP14: 간단한 표적함과 복수 함선 프로파일
- Kh-32/Kh-35U의 신규 solver·잔존체 피해 권위 이전은 legacy parity와 별도로 승인·검증
- 실제 함포 발사·포탑·탄창·외탄도·해상사격 해법은 범위를 별도로 고정한 뒤 연결
- homogeneous/KC 장갑 solver, persistent damage patch와 operational snapshot migration은 별도 단계로 유지

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며 WIP10, WIP11, WIP11A, WIP11B, WIP11C, WIP12A와 WIP12B는 각각 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
