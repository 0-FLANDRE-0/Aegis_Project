# AEGIS 현실형 함정 방위 시뮬레이터

## 현재 안정 기준 — v48

- 정식 파일: [`Aegis_SIM_v48.html`](Aegis_SIM_v48.html)
- 크기: `7,354,511 bytes`
- SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- **WIP15C를 코드 변경 없이 byte-identical로 승격한 안정판**이다.
- 상태: [`AEGIS_PLAN_STATUS_v48.md`](AEGIS_PLAN_STATUS_v48.md), [체크섬](SHA256SUMS_v48.txt)
- WIP15에서 SRBOC 6기/36튜브 실제 발사 원점, 예비탄·빈 발사기 단위 재장전, Nulka active decoy, ASM seeker acquisition 안정화, SM-2ER/SM-6 수동 대수상 교전, WIP13A 침수 self-test fixture 수리를 마쳤다.
- WIP15C 최종 검사에서 core self-test failure `0`, final runtime page error `0`.
- 상세 WIP15C 감사·검증 기록은 [`docs/wip15/C/`](docs/wip15/C/)에 보존한다.

## 현재 업로드 후보 — 출항 전 함선 선택·초기화

- 파일: [`Aegis_SIM_v48_WIP_STARTUP_A.html`](Aegis_SIM_v48_WIP_STARTUP_A.html), `7,361,673 bytes`, SHA-256 `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`.
- 준비 branch: [`ship-startup-ddg-regression`](../../tree/ship-startup-ddg-regression), parent `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`. WIP 번호 미확정이며 `WIP_STARTUP_A`는 기능명 토큰이다.
- 선택 전에 runtime 생성을 대기하고 불변 profile을 확정한 뒤 공통 세션 생성 → 기존 subsystem 결속 → 장비 편성 → 출항을 수행한다. 현재 등록된 운용 함선은 DDG-119다.
- [상태](AEGIS_PLAN_STATUS_v48_WIP_STARTUP_A.md), [체크섬](SHA256SUMS_v48_WIP_STARTUP_A.txt), [구현·검사·인계](docs/ship-startup/A/README.md).
- 로컬: package 34/34, startup 15/15, DDG runtime 14/14, 실제 3D 복구 13/13 PASS. 기존 B와 전투 aggregate·발사·명중·교전 결과가 같다. 상세 float의 최대 차이 약 `3.9e-13`을 기록했다.
- 사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 크기·Git blob·parent를 확인했으며 검증본과 exact 일치한다. 전용 CI와 일반 smoke의 실제 3D 입력은 이 업로드를 검사한다. 원격 CI/PR 결과는 후속 마감 기록에 추가한다. 기존 PR #41/main/안정 v48은 변경하지 않았다. 다음 구현은 벙커힐 profile·model·builder 연결이다.

## 직전 검토 후보 — v48 WIP16B

- 작업 branch: [`WIP16`](../../tree/WIP16), PR [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41).
- 이전 사용자 업로드 파일: [`Aegis_SIM_v48_WIP16B.html`](archive/v48/WIP16B/Aegis_SIM_v48_WIP16B.html), **7,357,036 bytes**. `7562bb0925e2b85521d37fefd2c81898ed6de18a`에서 원격 크기·Git blob이 로컬 검증본과 exact 일치한다. 새 후보 반영 시 B 세트는 내용 변경 없이 archive로 이동한다.
- SHA-256: `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`, Git blob `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf`.
- 상태: [WIP16B 계획/검증](archive/v48/WIP16B/AEGIS_PLAN_STATUS_v48_WIP16B.md), [당시 체크섬](archive/v48/WIP16B/SHA256SUMS_v48_WIP16B.txt), [수정 계약](docs/wip16/B/README.md).
- Codex에서 이어갈 문서: [WIP16B 개발 인계서](docs/wip16/B/AEGIS_CODEX_HANDOFF_WIP16B.md). 최신 판정·검증 명령·미병합 상태·벙커힐 참고 파일과 다음 작업 경계를 포함한다.
- 필수 피격 구멍 생성 중에는 직전 canvas를 유지하고 geometry commit 뒤 GPU 제출을 재개한다. C5의 실제 센서·함포·VLS 부품과 profile binding을 검사한다.
- C55 records 0–12와 3D 렌더러 앞의 전투·피해·nav/DL/loft source는 동일하다.
- WIP16A 사용자 업로드와 [당시 마감 기록](docs/wip16/A/CLOSEOUT.md)은 보존한다.
- 검증: 로컬 package **34/34**, B Chromium renderer/recovery **13/13**, 기존 13조건과 seed 반복 검사 **14/14**, 최종 일반 smoke **32/32 PASS**. 최종 support의 WIP16A 원본 보존 workflow도 **4/4 job PASS**. 기술적 통합 판정은 PASS이며 main 병합은 명시 승인 대기다.
- main/v48.1 승격·release/tag는 아직 실행하지 않았다.

WIP16B HTML 사용자 업로드·원격 exact 확인을 마쳤다. 당시 CI와 파일 대조 guard의 최종 결과는 [마감 증거](docs/wip16/B/evidence/upload_closeout.json)를 따른다. 이후 함선 선택·초기화 결과와 잔여 반영은 위 최신 항목을 따른다. 하푼·토마호크와 다함 동시 운용은 후속 범위로 둔다.

## 이전 통합 기준 — v48 WIP14B4

- **WIP14 FEATURE SCOPE CLOSED.** 최종 작업본은 [`Aegis_SIM_v48_WIP14B4.html`](archive/v48/WIP14B4/Aegis_SIM_v48_WIP14B4.html)이다.
- 크기 `7,319,028 bytes`, SHA-256 `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`. 사용자 업로드 원격 파일은 로컬 최종본과 Git blob exact 일치 확인.
- B1~B4에서 onboard navigation/truth boundary, ASM/RAM own-nav, VLS release scheduler, generic one/two-way weapon-link, SM-6 GPS/양방향 DL, 미사일별 stateful loft를 구현했다.
- B4 게임 검토 범위는 SM-2MR 160 km, SM-2ER/SM-6 260 km이며 실제 무장 최대사거리 인증이나 전 조건 명중 보장값이 아니다.
- 최종 상태: [`AEGIS_PLAN_STATUS_v48_WIP14B4.md`](archive/v48/WIP14B4/AEGIS_PLAN_STATUS_v48_WIP14B4.md), [branch closeout](AEGIS_WIP14_BRANCH_STATUS.md), [checksums](archive/v48/WIP14B4/SHA256SUMS_v48_WIP14B4.txt).
- 상세 B4 report/validation evidence는 [`docs/wip14/B4/`](docs/wip14/B4/)에 보존한다.
- Known deferred: 기존 침수 core self-test 1건, 환경상 WebGL 실렌더링 미검증, 장거리/저고도 포락선 추가 검증. WIP14 유도·DL·loft feature scope 종료를 막는 항목으로 두지 않는다.
- 다음 기능 단계 WIP15는 **3D에 이미 존재하는 양현 3기씩 SRBOC와 runtime 4기/24발을 6기/36발 canonical layout으로 정합하고 실제 launcher/tube 위치에서 발사되게 하는 작업**부터 시작한다. Nulka는 그 뒤 연결한다.

## 이전 개발 기준 — v48 WIP13C22

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

- WIP12D 정적 계약 `36/36 PASS`; WIP12A `32/32`, WIP11C `32/32`, WIP11B runtime safety `16/16` 하위 호환 정적 계약 통과
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

현재 안정판은 [`v48`](../../releases/tag/v48)이다. 이전 WIP 아카이브는 `archive/v48/`에 보존한다. 루트의 과거 작업본 일괄 정리는 WIP16 코드 검토와 별도 범위다.
