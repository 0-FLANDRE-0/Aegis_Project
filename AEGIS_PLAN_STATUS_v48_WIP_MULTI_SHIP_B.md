# v48 WIP MULTI SHIP B — 3단계 완료

- HTML: `Aegis_SIM_v48_WIP_MULTI_SHIP_B.html`, **15,328,273 bytes**.
- HTML SHA-256: `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`.
- decoded main SHA-256: `2d20d1927a47443aaaadc084faae07e21b6009baae4d78e055f600ecd143319c`.
- 기준 A head `3fab03782abb313cd3ece1bbfe254cdb77981231`, A HTML SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`.
- packed records 0~12·원본 함선/무장 assets·profile/module revision과 stable v48을 보존한다. main record13과 build label만 변경했다.

## 구현

출항 전 적함 배치 NONE/DDG-119/CG-52가 실제 두 번째 원본 함정과 독립 물리 runtime을 세계에 배치한다. 기본은 적함 없음이다. 초기 침로/8kt, 전방450m·우현350m에서 지형을 피해 난수 없이 배치하고 `3D VIEW → 배치 함정 보기`로 카메라를 따라볼 수 있다. 출항 후 배치 설정은 잠긴다.

공유 owner API로 항법·피해/보수·침수·구획/승조원·질량/동역학·복원성/침몰·구명뗏목을 실행한다. DDG 310명/138구획/96셀/Phalanx+SeaRAM, CG 330명/277구획/122셀/두 Phalanx를 따른다. 함체 접촉은 footprint SAT·질량 기반 비탄성 impulse와 bounded SIM-TUNE 개구, 적함 좌초는 해당 owner만 정지한다. 기존 자함 alias/UI와 shared world update1회, 60Hz tick/120Hz 침수·힘/20Hz hydro를 유지한다.

각 표시 모델은 root·geometry/material·map/job·interior cache를 소유한다. 기존 class builder와 profile asset을 재사용하고, 자기 함종과 다른 함종 asset도 로드한다. 외판/내부/승조원은 owner snapshot만 읽는다. retire/reset에서 이전 root·job·LOD proxy를 정리한다. 렌더링과 카메라는 물리/RNG를 바꾸지 않는다.

fleet 운용 저장은 NONE/PENDING/ACTIVE와 실제 배치 함정의 자세/항법/clock, 개구 role/door/pump/물, module damage·유체 재고·crew/rafts를 detached preflight 뒤 복원한다. 출항 전 PENDING 저장은 정상이며 ACTIVE 함정 누락은 거부한다. 옛 A fleet 누락은 명시 migration으로 새 배치를 준비한다. fire/DC/structural timeline·재료 손실 history·rigid-body rates·sensor/weapon/EW transient는 초기화하며 capabilities와 상세 문서에 제외 범위를 기록한다.

**관측/양방향 무장/EW/적 AI는 4~7단계 미완료다.** 배치 함정은 실제 항해/물리 피해를 수행하며 radar/무장은 준비 상태다. CIC에 상대 truth를 주입하지 않고 기존 탄을 이 함정에 자동 명중시키지 않는다. 이번 physical probe는 자연 미사일 flight/contact routing 검사가 아니다.

## 동일 최종 파일의 직접 검증

| 검사 | PASS 조건 수 |
|---|---:|
| static | 29/29 |
| departure | 48/48 |
| runtime | 194/194 |
| contacts | 20/20 |
| fleet clock | 32/32 |
| native | 20/20 |
| paired baseline | 12/12 |
| guidance | 45/45 |
| routes | 26/26 |
| knowledge | 22/22 |
| harpoon clock | 4/4 |
| DDG runtime | 14/14 |
| 합계 | **466/466** |

과거 A/E/K 숫자를 합산하지 않는다. isolation 내부42조건은 상위 PASS 안에 포함한다. 모든 보고서는 같은 최종 SHA에서 직접 실행했고 DDG 기존 검사 provenance를 별도 기록했다. core/runtime/presentation/page 오류가 없었다.

- 자함 두 함종, HULK/NONE×적함 없음/DDG/CG의 출항·저장/import/reset, 독립 피해와 난수, 잘못된 입력10개 zero mutation을 검사했다.
- 초기 선택6조합의 pre-sail export/core, 실제 두 함정의 1/8/16/64×각1536 full ticks exact와 공통날씨1회, 네 함종 조합의 접촉/좌초를 검사했다.
- 80% 침수·pump OFF·퇴함의 실제 LOST 전이와 인원 보존, 정상 CG 330명 전원 퇴함/25인승14척/330명 manifest, raft 저장/복원/retire 정리를 검사했다.
- native393×852 두 혼합 함종의 원본 A model fingerprint 일치, actualHole 입구/출구·후속 draw/tick·read-only·reset disposal을 검사했다. SwiftShader/controlled inert probe이며 geometry queue 강제 진행·mobile FPS 인증·적 AI 인증은 없다.
- 기본 적함 없음 A↔B의 대기/8 Kh-32 AUTO/침수와 기존 DDG·Harpoon INS/ARH/route/knowledge/clock을 재검사했다. raid는 초기 트랙 주입 회귀다.

상세 raw evidence와 count 기준은 [검증 집계](docs/multiship/B/evidence/verification-summary.json), 측정/역사 source-count audit 한계는 [PERFORMANCE](docs/multiship/B/PERFORMANCE.md)를 따른다.

## 보존·인계

A HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_A/`에 동일 bytes/blob으로 보존한다. stable v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`를 유지한다. 최신 workflow/support manifest는 B다. A 당시 manifest는 역사 자료다.

`multiship-physics-b`는 미병합 A PR #45 위에 연결한다. 지침7.1과 사용자 승인에 따라 Codex가 원본 HTML과 지원을 직접 push/readback하고 동일 파일 CI를 진행한다. 실제 원격 SHA/PR/CI는 [GitHub 인계](docs/multiship/B/GITHUB_HANDOFF.md) 및 GitHub 기록을 따른다. B 병합 요청은 없어 A/B를 임의 병합하지 않는다.

다음은 **4단계 함정별 센서/익명 관측·observer 트랙 분리**다. 이후 실제 탄의 source/target routing·양방향 무장, receiver별 EW와 관측 기반 AI를 연결한다. [의존성/잔여](docs/multiship/B/DEPENDENCIES.md).

원격 최초 publication `6b060dd156405ef97d59c2f7b5eb4ad77a95032f`의 HTML/support/A archive/stable 56파일을 독립 readback해 byte-identical임을 확인했다. 원본 B Git blob `f534ffd1de49b5a7a1c81a6efc6753b710fa4aa8`. [원격 증거](docs/multiship/B/evidence/remote-publication.json), [PR #46](https://github.com/0-FLANDRE-0/Aegis_Project/pull/46). 기록 자체를 포함하는 후속 commit의 HTML bytes는 동일하며 CI 실제 상태는 해당 head checks를 따른다.
