# AEGIS 현실형 함정 방위 시뮬레이터

## WIP14 작업 브랜치 — 유도·데이터링크·로프팅

- branch: [`WIP14`](../../tree/WIP14), 기준 `main` commit `a8d14e3484200098be2143e0547c8e922642c042`
- 현재 commit은 **계획·인계·참고자료 준비**이며 새 시뮬레이터 기준판이나 정식 release가 아니다. runtime 기준은 아래 WIP13C22를 유지한다.
- B1 로컬 후보는 missile onboard INS/GPS와 DL truth boundary를 구현했다. 대형 `Aegis_SIM_v48_WIP14B1.html`은 원격에 올리지 않았고 [상태·보고·증거](docs/wip14/B1/)만 첨부했다.
- 기존 B2와 B3는 [하나의 B2 transport 단계](docs/wip14/WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md)로 통합한다. 내부 gate는 B2a one-way transport, B2b SM-6 limited return, B2c bounded assistance/회귀로 분리한다.
- B3 번호는 B2에 흡수된 것으로 보존하며 재사용하지 않는다. B4는 SM-2MR/SM-2ER/SM-6/ESSM별 stateful loft로 별도 유지한다.
- 사용자가 제공한 공대공 [참고 HTML](references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html)은 INS/GPS, packet DL, limited two-way link, stateful loft 구조 비교용이다. AIM-174B는 참고용이며 함정 VLS에 추가하지 않는다.
- branch 상태: [AEGIS_WIP14_BRANCH_STATUS.md](AEGIS_WIP14_BRANCH_STATUS.md), 첨부물 checksum: [WIP14_REFERENCE_SHA256SUMS.txt](WIP14_REFERENCE_SHA256SUMS.txt)


## 현재 개발 기준 — v48 WIP13C22

- 작업본: [`Aegis_SIM_v48_WIP13C22.html`](Aegis_SIM_v48_WIP13C22.html)
- 상태와 남은 검증: [`AEGIS_PLAN_STATUS_v48_WIP13C22.md`](AEGIS_PLAN_STATUS_v48_WIP13C22.md)
- SHA-256: `9b697fcb2edfef69b01d39add5600d1f61638fa42bf6b2d07222d25d491e75fa` (전체 파일: [체크섬](SHA256SUMS_v48_WIP13C22.txt))
- C22는 C19 외형·SPG 서보와 C18 해면/선체 판정을 보존하며, 기존 SM-2/ESSM 신관 프로파일로 대수상 충격·근접기폭을 판정한다. 충돌 예정이면 충격신관을 우선하고, 예상 선체 미스에 한해 신관 조건을 통과한 근접기폭을 허용한다.
- 판정: **C22 코드·결정적 런타임 검사 완료 / 13C 전체 종료 HOLD**. 정식 v48 릴리스가 아니다. 실제 브라우저/WebGL 및 전체 방위 실비행 검증은 남아 있다.
- 검사: [C22 전용 회귀](.github/workflows/wip13c22-regression.yml)에서 패키지·체크섬·고정 틱 신관 fixture·SPG 회귀와 3가지 실비행 시나리오를 실행한다.
- 이전 기준: [C19 상태](AEGIS_PLAN_STATUS_v48_WIP13C19.md), [C19 외형](AEGIS_WIP13C19_STATUS.md), [13C 수상교전 계획](WIP13C_SURFACE_MISSILE_ENGAGEMENT_PLAN.md). C20/C21은 철회된 중간 산출물이므로 병합하지 않는다. 실수로 생성된 C6/C17 브랜치에서도 병합하지 않는다.


## 과거 통합 기록 — WIP12D

- 시뮬레이터: [`Aegis_SIM_v48_WIP12D.html`](Aegis_SIM_v48_WIP12D.html)
- 상태·검증 기록: [`AEGIS_PLAN_STATUS_v48_WIP12D.md`](AEGIS_PLAN_STATUS_v48_WIP12D.md)
- WIP12D Kh-32 잔존체 계약: [`docs/WIP12D_KH32_RESIDUAL_OVERPENETRATION.md`](docs/WIP12D_KH32_RESIDUAL_OVERPENETRATION.md)
- WIP12E 구획 폭압 착수 인계서: [`docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`](docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md)
- WIP12C 내부 종말효과 계약: [`docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md`](docs/WIP12C_INTERNAL_TERMINAL_EFFECTS.md)
- WIP12B live ordnance 계약: [`docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md`](docs/WIP12B_LIVE_ORDNANCE_TERMINAL_EFFECTS.md)
- 공통 커널 설계: [`docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md`](docs/WIP12A_TERMINAL_BALLISTICS_DESIGN.md)
- HTML SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- 상태: WIP12D 구현·로컬 회귀 완료 — 정식 release/tag가 아님

## WIP12D 핵심 범위

- Kh-32의 실제 기폭 위치에서 legacy 잔존 유효에너지 비율을 읽어 폭발 직전 물리 속도와 운동에너지를 복원
- 최대 4개의 결정적 대형 잔존체에 부모의 병진운동과 제한된 화학에너지를 배분하고 질량·에너지 ledger를 닫음
- `PERFORATED`와 `SHATTERED`를 독립 결과로 유지해, 깨진 잔존체도 임계 질량·coherent mass·속도·에너지가 남으면 후속 내부 구조와 반대편 외판을 계속 관통
- 방향 변화마다 상세 구획·장비 volume·국부 외판을 다시 질의하고, 막힌 잔존체와 실제 함외 과관통을 모두 기록
- 함외 비행 뒤 다른 선체·상부구조와 다시 만나는지 제한적으로 재질의하고, 재진입 시 실제 재질·내부 구조·반대편 외피를 다시 계산하여 막힘·도탄·재이탈을 허용
- 모든 완전 관통 외피 접촉은 독립된 파괴구를 남기며, 물리 선체 구멍은 기존 침수 모델에 연결되어 위치·수심·파랑에 따라 실제 유입과 후속 피해를 발생
- 반대편 이탈 위치·파괴구·잔존 질량·속도·에너지를 보존하고, 최종 해수면 위 이탈은 제한된 탄도 표시선, 수선 아래 이탈은 즉시 수중 진입으로 표시
- 기존 폭발원은 속도와 기폭 후 진행거리에 따라 보존적인 head/peak/tail 연쇄원으로 분포하며, 3D도 같은 source를 연결한 물방울형 envelope를 표시
- 관통선·큰 잔존체·출구·바다 진입은 명시적 `내부 구조` 보기에서만 표시하며 렌더링은 물리·피해·난수에 피드백하지 않음
- `피격 중심` 모드는 국부 clipping과 object-AABB culling을 사용하고, `전체 내부`로 모든 세부 구획을 복원; hazard는 최대 3개 batch로 표시
- Kh-32/Kh-35U의 primary legacy 피해 권위와 전투 RNG는 유지하고, blast를 다시 적용하지 않는 별도 event-ID 보충 경로가 잔존체의 제한된 기계적 피해와 실제 외피 구멍만 한 번 적용
- 비폭발성 불활성 파편과 구조 충격은 자체 발화하지 않으며, 기존 WIP12C의 실제 취약 장비 volume 희박 발화 정책만 유지
- DUD는 대형 잔존체 cascade를 만들지 않음
- 누적 형상 보정으로 전방 연돌은 `x=3.50…17.10 m`, 후방 연돌은 `x=-18.15…-4.55 m`; 3D 메시·피격 AABB·RCS·내부 배기 트렁크·2D 상/측면 인디케이터가 같은 값을 소비
- 후방 상단 SPG-62와 받침대를 `x=-20.0 m`로 0.30 m 후퇴시켜 보수적 평면 투영 간격 `0.40 m`, 실제 높이 테이퍼 간격 `1.499 m`를 확보; 계산된 접선각 `48.18°`를 올림한 차단 반각 `49°` 적용

## 검증

- WIP12D 정적 계약 `36/36 PASS`; WIP12A `30/30`, WIP11C `32/32`, WIP11B runtime safety `16/16` 하위 호환 정적 계약 통과
- 정적 계약 파일 `11/11 PASS`, 전체 Playwright `36/36 PASS` (최신 WIP12D `32/32` + 보존 WIP12B·WIP12C `4/4`)
- WIP12D Playwright `2/2 PASS`; core selftest failure `0`, 콘솔/page error `0`
- 실제 Kh-32 seed `481232`: 확장된 전방 연돌을 먼저 맞아 primary damage budget `191`, 물방울형 3-source power 합 `1.0`, damaged parts `17`, 상위 피해 `제1보일러실 47 / 제1발전실 43`
- legacy ASM 공식과 전투 RNG 권위는 그대로이며, 위 seed 차이는 요청에 따라 넓어진 실제 연돌 피격 envelope가 첫 접촉 surface를 바꾼 의도된 형상 결과
- 폭발 직전 복원 속도 `900.1217 m/s`, 대형 잔존체 `4`, shatter continuation `10`, 내부 정지 `2`, 반대편 외판 이탈 `2`
- 실제 잔존체 외피 구멍 `2`, 제한된 기계적 보충 피해 `9.34313`; `0.045 m²` 수중 구멍 진단은 `0.5 s`에 `0.06548 m³` 유입
- 실제 함정 재진입 fixture는 전방 연돌 이탈 후 `12.35 m` 외부 비행과 후방 연돌 재진입·재이탈을 `EXIT → REENTRY → EXIT`로 검증
- 함외 잔존체는 각각 `10.723 kg @ 1178.123 m/s`, `13.137 kg @ 1135.289 m/s`; 해수면 진입 `1`, 즉시 수중 진입 `1`
- 같은 seed 결과 exact, DUD 잔존체/출구 `0/0`, combat RNG 불변, 질량 closure error `0 kg`
- traversal 256회 `0.2684 ms/impact`, render-frame geometry query `0`
- 3D draw call `2342 → 298`(`87.28%` 감소), 피격 중심/전체 내부 복원과 내부 전용 표시 확인
- Workflow YAML은 WIP12D 전용 2개 job을 더한 총 `28`개 job으로 구성

## WIP12D 당시 다음 단계

- WIP12E: legacy scalar blast 재분배를 bounded compartment/portal pressure·impulse solver로 교체하고, 반사압·폭풍·동적 breach·외부 vent를 구조/장비/승조원 consumer와 내부 전용 시각화에 연결
- WIP12E 권위 전환 뒤 기존 Kh-32 `191` scalar budget과 부품별 피해 exact parity는 강제하지 않고 calibration 비교값으로 유지하되, 관통·기폭 위치·잔존체·구멍·침수·전투 RNG 회귀는 보존
- WIP13: WIP12E 완료 뒤 공통 종말효과 계약을 소비하는 제한적 표면교전 표적 승인·발사/FCS 경로
- WIP14: 간단한 표적함과 복수 함선 프로파일
- Kh-32/Kh-35U primary 피해 권위의 공통 packet 완전 이전은 현재의 제한된 breach/mechanical 보충과 별도로 승인·검증
- 실제 함포 발사·포탑·탄창·외탄도·해상사격 해법은 범위를 별도로 고정한 뒤 연결
- homogeneous/KC 장갑 solver, 수중 충격 피해, persistent damage patch와 operational snapshot migration은 별도 단계로 유지

## 안정판과 아카이브

현재 공개 안정판은 [`v37.1`](../../releases/tag/v37.1)이다. 루트에는 최신 작업본만 두며 WIP10, WIP11, WIP11A, WIP11B, WIP11C, WIP12A, WIP12B와 WIP12C는 각각 `archive/v48/` 하위 폴더에 바이트 단위로 보존한다.
