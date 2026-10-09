# v48 WIP HARPOON B — 로컬 검증 완료

- HTML: `Aegis_SIM_v48_WIP_HARPOON_B.html`, **15,274,780 bytes**
- HTML SHA-256: `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`
- main SHA-256: `3e5db4f820844d3301617f5c3e21e69f03619e05dba056532483954a6c88ecbf`
- 기준 A SHA: `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`; K PR #43 병합 main `f51247496725aa8aadad69d5c8d3449c5bbc3a81`.
- 준비 branch: [harpoon-block1c-a](https://github.com/0-FLANDRE-0/Aegis_Project/tree/harpoon-block1c-a). 확인한 main/branch는 같은 K commit이며 새 원격 HTML/support/PR/CI/병합은 아직 미실행이다.
- 범위: A의 하푼 운용을 유지하며 후미·빈 관·화염·짙은 연기와 사용자 요청 3.2초 부스터를 개선했다. 정식 v48은 변경하지 않았다.

## 완료한 변경

부스터 분리 뒤 본체 후미를 연속 테이퍼·금속 립·열린 nozzle bell·후퇴한 throat로 표시한다. 원본 연결 부품은 부스터 부착 중에만 남기고 본체 외피는 전후 단계에서 항상 유지한다. 부스터 외피와 노즐도 다듬으며 원본 본체/전체 길이 3.84/4.63m는 유지한다. Kh-35U의 후미와 rocket/jet 구분, 기존 SAM core/outer plume를 참고했다. Civorsky/CC BY 4.0 credit과 원본 62개 공유 mesh 자료를 보존한다.

선택한 Mk 141 관의 front 116 faces를 하나의 힌지 문으로 열고 rear 58 faces를 발사 상태에서 숨긴다. 기존 34 faces 뒤의 두 번째 막뿐 아니라 1.00/1.08m 깊이의 rack 지지판도 실제 관을 막았다. 관을 가로지르는 지지판의 원형 부분만 잘라 490개 source faces를 11,598개 표시 삼각형으로 재조립한다. 원본 surface attribute와 관 밖 지지판은 보존하고 정수 법선을 Float32로 복호화·보간해 검은 면이 생기지 않도록 했다. 실제 native raycast에서 발사 관의 중심/양측 내부 광선 3개가 약 5m 관을 통과하고 미발사 관은 원래 덮개에서 막혔다. RESET은 8관의 앞·뒤 덮개를 복원한다. 원본 CG collision 자료나 실제 피격 breach는 바꾸지 않는다.

부스터의 nozzle 끝에서 강한 2.6m outer/1.86m core 화염, 분리 후 본체 nozzle에서 약한 0.48m outer/0.24m core 제트 배기를 표시한다. 실제 motor/thrust/stage를 소비하며 분리된 booster에는 재점화 불꽃을 붙이지 않는다. 발사 rear backblast와 관을 떠나는 순간의 front pressure puff를 추가하고 공유 C13/HOT pool에 넣는다.

후연이 많은 고체 추진제라는 **사용자 가정**을 VISUAL-TUNE으로 적용했다. 0.60m 거리 간격, alpha .96, base 1.8m, 12초 수명과 완만한 팽창/감쇠로 짙은 회백색 trail을 유지한다. native live trail의 optical weight/metre는 약 23.308였다. 기존 같은 pool/emitter로 측정한 RAM/ESSM/SM-2 reference는 약 0.463/4.914/14.182로, 게임의 표시 광학량 비교이며 실제 공대공/대함 미사일의 후연 인증값이 아니다. 분리 뒤 새 부스터 연기는 멈추고 이미 생성된 구름은 바람에 표류·확산·감쇠한다. 제트 순항에 두꺼운 새 trail을 붙이지 않는다. pool 12,000, 발사 emitter 8, sample 48/탄체/프레임의 표시 상한을 유지한다.

공개 참고 53kN·2.9초는 public에 보존하고 **SIM-TUNE 3.2초·평균 48kN**을 분리한다. nominal impulse 153.6kN·s는 기존 153.7kN·s와 약 0.065% 차다. 90kg propellant의 질량 감소를 3.2초로 계산하고 실제 60Hz 틱에서 한 번 분리한다. 대표 분리 age 3.200000000초, 속도 225.121m/s였으며 분리 때 임의의 속도 재설정이 없다. 실제 제조사의 thrust curve·Isp·추진제 조성을 재현했다는 주장이 아니다.

CG 작전 revision은 `BUNKERHILL_HARPOON_B_1`, 모듈은 `HARPOON_B1`이며 `MK141_INVENTORY_A1` schema는 유지한다. A 저장 revision을 명시 호환으로 추가했고 inventory 누락/ID 오류는 기존 경계로 거부한다. 비행 중 탄체와 예약은 저장 복원하지 않는다. INS/독립 ARH·발사 권한·관별 탄약·690kg 발사 질량·공통 접촉/지연신관/피해/침수와 DDG의 Harpoon 미설치는 유지한다. 다른 미사일·센서·함포·구조·승조원·퇴함 source 및 기존 asset은 허용 diff를 제외하면 A와 byte 동일이다.

## 직접 검증

모든 아래 검사는 같은 최종 SHA에서 실행했다. 원자료 입력명 `experimental.html`과 최종 명명본은 byte 동일이다. 이전 A 155건과 K 284건을 이 파일에서 다시 실행한 것으로 합산하지 않는다. seed는 `0x6d2b79f5`다.

| Suite | 통과 | 범위 |
|---|---:|---|
| 정적 | 48/48 | 압축 record/JS 문법/exact 재빌드/허용 booster diff/나머지 source parity/원본 asset/관·지지판 barycentric 자료 |
| 하푼 runtime | 29/29 | 권한 재검사/고정 관·질량/INS 독립·ARH/이동 표적 접촉·피해 1회/저장 안전/1·8·16·64× exact/DDG core·작전 상태 |
| 3.2초 stage | 11/11 | 직전 틱까지 48kN/정확한 단일 분리/질량 감소/jet 전환/속도 연속/A 저장 호환 |
| native WebGL | 36/36 | 실제 모바일 ARM/VLS·RAF/caps·내부 광선/법선·날개·분리/nozzle/plume·짙은 trail/피격 후 camera·RESET·native full-clock 두 번째 발사·오류 0 |
| 64× 8발 workload | 9/9 | 8탄체·고정 관·8×690kg·유한 상태/공통 접촉/관측 저장 상한·profiler |
| 합계 | **133/133** | core/page/native console 오류 0, simulation/presentation fault 0 |

대표 A4 이동 표적 접촉은 32.75초, 상대속도 286.665m/s, 폭약 97.5kg의 공통 packet을 기록했다. native 두 번째 발사는 진단으로 physics를 수동 진행하지 않고 전체 시뮬레이션 clock/RAF에서 연소·분리·jet 전환을 확인했다. 첫 번째 focused flight fixture와 실제 frame clock을 구분해 원자료에 남긴다. 빈 관만 확대하는 캡처는 읽기 전용 geometry 검사 카메라를 사용하고, 일반 follow/wheel/pointer는 실제 UI 입력으로 검사했다. geometry queue를 수동 진행하지 않았다.

Chromium 151.0.7922.173/SwiftShader 검사이며 사용자 장치 FPS나 모든 전투 조건의 성능 보증값이 아니다. 예비 native 실행에서 60초 물리 진행 대기가 한 번 끝나지 않았고 원인은 게임 fault로 확정하지 못했다. 최종 harness는 소프트웨어 렌더링의 stage 대기를 최대 120초 허용하며 같은 최종 source에서 연속 진행과 오류 0을 확인했다. 기존 전체 CG30/DDG14를 B에서 반복 실행하지 않았으며 unrelated source parity와 B runtime의 DDG core/작전 검사를 근거로 구분한다.

## 근거·보존·다음 작업

[A 공개 자료](docs/harpoon/A/SOURCES.md), [B 코드·SIM-TUNE·재현](docs/harpoon/B/README.md), [직접 집계](docs/harpoon/B/evidence/verification-summary.json), [GitHub 인계](docs/harpoon/B/GITHUB_HANDOFF.md)를 따른다. 비공개 시커·공력·연료·고도·신관 수치는 계속 SIM-TUNE이다. 적 수상함 AI/다함전, 헬리콥터, 외부 표적 정보, 경유점/pop-up과 최대 사거리 실비행 인증은 이번 범위가 아니다.

A HTML/상태/SHA 세트를 `archive/v48/WIP_HARPOON_A/`에 같은 bytes로 이동했다. A HTML은 remote에 없으므로 API/Git로 새 업로드하지 않고 작은 A 모듈+기존 remote K blob에서 exact 재생성한다. 이전 A workflow는 `docs/harpoon/A/workflow-a.yml`에 역사 보존하고 현재 workflow는 B다. K는 동일 blob archive 이동을 준비했으며 root K workflow는 후보가 있을 때만 실행한다. 역사 root fixture 예외와 정식 v48 bytes는 보존한다.

다음은 프로젝트 지침 7.1에 따라 사용자 **최신 B HTML만** 기존 branch 루트 업로드 → 원격 SHA/parent 대조 → 작은 support/문서/체크섬/workflow·K archive 반영 → 새 PR/동일 bytes CI다. 그 뒤 적 수상함 runtime·정식 시나리오/UI를 확대하고 헬리콥터의 표적 정보 공급을 검토한다. 원격 main 병합/정식 승격은 새 지시 전 실행하지 않는다.
