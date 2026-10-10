# v48 WIP MULTI SHIP A — 1~2단계 완료

## 파일과 기준

- 실행 파일: `Aegis_SIM_v48_WIP_MULTI_SHIP_A.html`
- 크기: **15,314,629 bytes**
- HTML SHA-256: `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`
- decoded main SHA-256: `8cb35bd169cb6de69270297bf33222bec337055da19f64519936917c267089c8`
- 기준: `main@cb70a637105ce00e7c0619270237cc35a83d39c2`, PR #44 병합 Harpoon E.
- E HTML SHA: `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`.
- PACK records 0~12와 원본 함선·무장 asset은 동일하다. record 13 및 build label을 변경했다. 함종 profile revision·무장 스펙은 유지한다.

## 구현 범위

**1단계 기준 기록과 2단계 독립 함정 상태·컨텍스트를 완료했다.** 출항 전 화면과 VLS 편성 화면에 시험 표적함 `있음/없음`, 적함 준비 `없음/DDG-119/CG-52`를 추가했다. 기본값은 기존 시험 표적함 있음·적함 없음이다. 출항 후 설정을 잠그며 저장·복원·reset에도 적용한다. 배치 설정이 없는 옛 저장은 명시적으로 기본값으로 migration한다. 잘못된 저장은 전체 preflight 단계에서 권위 상태 변경 없이 거부한다.

적함을 선택하면 공유 생성 함수를 통해 독립 `ShipRuntime`과 live getter context를 준비한다. 함종별 VLS 고정 셀·탄창·Harpoon/SRBOC/Nulka 재고·SPG 상태·센서/트랙 버퍼·EW 상태·실제 피해/침수/보수/내부/승조원/질량/동역학 모델을 별도로 소유한다. 같은 프로필의 자함 현재 상태를 복제하지 않으며, 가변 객체 중복 바인딩과 비자함의 PLAYER 역할을 거부한다. CG는 두 Phalanx와 61+61셀, DDG는 기존 Phalanx+SeaRAM과 32+64셀을 따른다.

선택 자함의 기존 UI·전역 alias·물리·전투 루프를 유지한다. 공통 세계를 함정 수만큼 반복 업데이트하지 않는다. 기본 60 Hz tick, 침수/force 120 Hz, hydro quadrature 20 Hz 및 전투 난수 소비를 유지했다.

**적함은 `STATE_BOUND_INACTIVE`다. 실제 바다 위 모델 배치·항해·피해 tick은 3단계, observer 센서·양방향 요격/공격·EW·AI는 4~7단계다.** 등록 함정이 2척이어도 실행 함정은 자함 1척이다. 새 FCS·트랙 상태는 실행 준비용이며 자함의 전역 truth index나 FCS에 연결하지 않는다. 비자함 함포 발사/해법/step은 거부한다. 적함 구명뗏목은 provision만 준비하고 controller/world 연결은 3단계로 남겼다. 실제 enemy 전투를 완료한 것으로 해석하지 않는다.

## 동일 최종 HTML의 직접 검증

| 검사 | PASS 조건 수 | 확인한 내용 |
|---|---:|---|
| static/package | 26 | 고정 E, 원본 asset, PACK hash, syntax, 변경 범위, exact 재빌드 |
| runtime/deployment | 106 | 양 함종, 모든 표적/적함 조합, 잠금, 저장/import/reset, 실패 입력 무변경, 역할/소유권 |
| Harpoon guidance | 45 | 기존 INS/ARH·부스터·유도 회귀 |
| Harpoon routes | 26 | 실제 경로 UI·발사/취소·독립 airborne program·DDG 미설치 |
| Harpoon knowledge | 22 | DL 없음·자함 표시 정보 경계·센서 관측 |
| Harpoon clock | 4 | 1/8/16/64배속 각각 3072 full ticks exact |
| 기존 DDG runtime | 14 | 기존 Phalanx 반복 비교·spotting·피해/기동·수상/침수 |
| native 3D | 16 | 양 함종 393×852 선택, 실제 RAF/WebGL, 제어된 관통 피해/외판 구멍, 후속 draw/tick 지속 |
| E ↔ A paired baseline | 12 | 양 함종 × 대기/8 Kh-32 AUTO/침수: physical state·RNG exact 및 오류 없음 |
| **합계** | **271/271** | 모두 같은 `704d0724…` 최종 파일에서 직접 실행 |

runtime의 isolation audit 내부 42조건은 상위 isolation PASS에 포함되며 위 합계에 다시 더하지 않았다. 과거 E 178건·K 284건은 이번 직접 실행 수에 합산하지 않는다. 상세 원본 보고서와 source provenance는 [evidence/verification-summary.json](docs/multiship/A/evidence/verification-summary.json)을 따른다.

기준 비교와 기존 DDG 회귀의 boot seed는 `0x6d2b79f5`(1831565813)다. 같은 seed로 대기 240ticks/1배속, raid 1920ticks/8배속, 침수 480ticks/16배속을 실행했다. raid 초기 트랙은 기존 회귀 fixture로 주입하므로 자연 탐지/적 AI 시험이 아니다. 두 버전의 자함 물리 상태와 RNG가 정확히 일치했고 core/runtime 오류가 없었다.

native에서는 제어된 기존 Kh-32 DUD structural probe로 실제 물리 관통구를 생성하고, native geometry commit 뒤 draw와 게임 tick이 계속되는 것을 확인했다. geometry queue를 시험 코드에서 강제로 진행하지 않았다. 페이지·console·runtime·표시 오류는 0이다. 이 시험은 자연 미사일 명중률을 인증하지 않는다. 초기 DDG Kh-35 fixture의 미접촉은 PASS로 세지 않았으며 [검사 제한](docs/multiship/A/DEPENDENCIES.md)에 남겼다.

CPU fixture의 subsystem avg/p95/max·개체 수·CDP heap와 native SwiftShader frame 시간은 [PERFORMANCE.md](docs/multiship/A/PERFORMANCE.md)에 기록했다. 한 번의 실행으로 속도 향상이나 메모리 누수 유무를 결론내리지 않으며, 모바일 하드웨어 FPS 인증도 아니다.

## 보존·인계와 다음 작업

stable `Aegis_SIM_v48.html`은 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`로 변경 없이 보존했다. 직전 E HTML/status/SHA와 workflow는 `archive/v48/WIP_HARPOON_E/`에 같은 bytes로 보존한다. 기존 historical fixture 예외는 유지했다.

원격 `multiship-runtime-a` 브랜치를 기준 main에서 준비했다. 현재 새 HTML/support 원격 업로드·PR·Actions·병합은 미실행이다. 저장소 지침 7.1에 따라 사용자가 새 HTML 하나를 브랜치 루트에 올리면 Codex가 bytes/SHA/parent를 확인한 뒤 작은 지원 파일·archive 이동·PR/Actions를 진행한다. 지원 ZIP은 검증/재생성 자료의 백업이며 HTML에 필요한 별도 실행 의존성은 아니다. [GitHub 인계](docs/multiship/A/GITHUB_HANDOFF.md).

다음은 3단계로 실제 적함 1척의 모델·pose·해수면·피해/침수/crew/질량·외판/내부 표시를 runtime에 연결한다. 그 뒤 관측 경계를 분리하고 양방향 무장/EW, 마지막으로 관측과 허용 command만 쓰는 AI를 구현한다. 구체적 실행 소유권과 완료 조건은 [DEPENDENCIES.md](docs/multiship/A/DEPENDENCIES.md)를 따른다.
