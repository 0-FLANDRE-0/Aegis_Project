# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 개발 기준

- 시뮬레이터: [`Aegis_SIM_v48_WIP12B.html`](Aegis_SIM_v48_WIP12B.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP12B.md`](AEGIS_PLAN_STATUS_v48_WIP12B.md)
- WIP12B 설계 계약: [`docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md`](docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md)
- 공통 커널 설계: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- HTML SHA-256: `61dfcff533f7708df65e1939e3f5cd10448a6492ed0903b4dc2f17af50663f91`
- 상태: WIP12B 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP12B 핵심 범위

- Kh-32, Kh-35U, SM-2, ESSM, RAM을 WIP12A `TerminalProjectileSpec`/trace/packet 계약에 등록
- Kh-32/Kh-35U는 `LEGACY_ASM_PENETRATION_COMPAT` exact parity 유지
- SM-2/ESSM/RAM은 기존 파편/Pk 권위를 유지하고 공통 terminal event로 결과를 변환
- 요격탄의 `PROXIMITY`, `CONTACT_DIRECT_ACTION`, `DUD` 경로와 earliest-valid-event 정책 명시
- 향후 제한적 대함전용 direct surface-impact resolver 제공; 실제 표적 선택·발사·FCS는 비활성
- `impactEventId` 중복 방지와 최대 32개 transient terminal-event ledger
- 관통 경로, 경계·파괴구, 기폭, 폭압·파편 방향은 명시적 `내부 구조` 모드에서만 2D/3D로 표시
- 불투명 coarse flooding-cell proxy 제거
- 피격 개구부에서는 상세 WIP06 구획을 표시하고, 내부 모드에서는 외부 함체를 투명화
- 상세 구획과 침수·화재·연기 형상을 실제 선체·상부구조 envelope로 잘라 외형 밖 돌출 제거
- 전방 연돌은 기존 끝단 기준 후방 `1.75 m`·전방 `0.5 m`, 후방 연돌은 후방 `1.25 m`·전방 `1.0 m` 연장
- 연돌 권위값을 3D 형상, 외부 피격판정, RCS aim, 내부 배기 트렁크, 2D indicator와 SPG-62 차폐각에 공통 적용
- 렌더러는 표시 전용이며 전투 물리·피해·난수에 피드백하지 않음

## 검증

- WIP12B 정적 계약 `29/29 PASS`
- WIP12A 정적 계약 `30/30`, WIP11C 정적 계약 `32/32`, 기존 정적 계약 회귀 통과
- WIP12B Playwright `2/2 PASS`
- Playwright 전체 `32/32 PASS` (로컬 Three.js 경로)
- 정상/DUD ASM 피해 1회 적용, 요격탄 proximity/contact 기록, event ID 중복 방지 확인
- 외부 모드 terminal effect 숨김, 내부 모드 표시, 상세 구획 `138/138` 수용과 외형 이탈 정점 `0`, 공간별 hazard clipping 확인
- 두 연돌의 권위 끝단·실제 3D bounds, 피격판정·RCS·내부 트렁크·SPG-62 마스크 연동과 2D 연장부 실제 픽셀 표시 확인
- 기존 ASM same-seed/RNG, Kh-32/ESSM BDA, CIWS, 침수·구조·승조원·VLS, snapshot zero-mutation 회귀 통과
- Workflow YAML은 WIP12B 전용 2개 job을 더한 총 `24`개 job으로 구성

## 다음 단계

- WIP13: WIP12B 계약을 소비하는 제한적 표면교전 표적 승인·발사/FCS 경로
- WIP14: 간단한 표적함과 복수 함선 프로파일
- 실제 함포 발사·포탑·탄창·외탄도·해상사격 해법은 범위를 별도로 고정한 뒤 연결
- homogeneous/KC 장갑 solver, persistent damage patch와 ASM 신규 solver 이전은 별도 검증·승인 단계로 유지

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며 WIP10, WIP11, WIP11A, WIP11B, WIP11C와 WIP12A는 각각 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
