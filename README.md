# AEGIS 현실형 함정 방위 시뮬레이터

## 최신 개발 기준 — Multi Ship WIP H4A

- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html), **15,702,263 bytes**, SHA `3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a`.
- CMS 미획득에도 **CIWS 자체 RF의 확인된 접근 위협**으로 독립 자위 대응한다. 실제 발사에서 owner-local capability·freshness·아군/중립/효과 보호·HOLD/EMCON/손상을 재검사한다. CMS 적성/원거리 SAM 권한을 만들지 않는다.
- 유일하게 연관된 **local RF 거리·접근 + passive 시커 방위**를 기존 채프 timing에 전달한다. ESM 방위만으로 거리를 추측하지 않는다. 기본 fresh CG 하푼 공격에서 채프4/Phalanx95발·실제 분해를 확인했다.
- 최종 원본 **1484/1484 PASS /27 suites**, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4A.md), [SHA](SHA256SUMS_v48_WIP_MULTI_SHIP_H4A.txt), [운용](docs/multiship/H4A/README.md), [직접 검증](docs/multiship/H4A/evidence/verification-summary.json), [조건](docs/multiship/H4A/PERFORMANCE.md).
- H4 final 위 `multiship-defense-h4a`, PR base H4. 원본/support 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. 새 main/선행 PR 병합은 실행하지 않는다. 다음은 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va다.

## 직전 개발 기준 — Multi Ship WIP H4 (당시 기록)

- [HTML](archive/v48/WIP_MULTI_SHIP_H4/Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html), **15,697,218 bytes**, SHA `602371dfd5be5147c2e04dd4078e3216ca4f47e8ce4e7b0092bd861c3d9a5132`.
- FLEET의 **함대 전술·호위/수상전 임무·종렬/좌우 전형·1/2/4km 간격**을 owner별로 설정한다. 기본OFF이며 아군은 받은 선도함 항법과 기존 H2 타/기관 명령으로 기동한다. 수동/대공 방어가 우선하고 단절/OFF에 항법을 반환한다.
- fresh 현지 적성 수상 관측과 **각 함정의 별도 H3 동의** 아래 한 primary에 native Harpoon2발을 분담한다. 받은 접수는 동의/lease 만료 뒤에도 기억해 추가 AI 살보를 보류한다. 공유OFF는 항법만, 링크 없는 상황의 보편적 중복 방지는 아니다.
- **수상 자위 판단**은 반복된 현지 incoming ASM와 유일한 near-origin 수상 관측의 근거를 사용한다. operator 식별을 덮어쓰지 않고 아군/중립 보호가 우선한다. 발사원 근거 없는 미식별 첫 공격은 보류한다. Harpoon DL0/INS→ARH, 기존 물리·무장·EW·해상효과/3D를 유지한다.
- strict 설정 저장·H3 이하 팀OFF migration·transient reset, 최종 원본 **1403/1403 PASS /24 suites**, 오류0. [상태](archive/v48/WIP_MULTI_SHIP_H4/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4.md), [SHA](archive/v48/WIP_MULTI_SHIP_H4/SHA256SUMS_v48_WIP_MULTI_SHIP_H4.txt), [운용](docs/multiship/H4/README.md), [직접 검증](docs/multiship/H4/evidence/verification-summary.json), [조건](docs/multiship/H4/PERFORMANCE.md), [남은2단계](docs/multiship/H4/DEPENDENCIES.md).
- H3 `af1eade2d418b215720a68a5b902aae0d9387203` 위 `multiship-tactical-h4`, PR base H3. 원본/support 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. main/선행 PR 병합은 실행하지 않는다. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.

## 직전 개발 기준 — Multi Ship WIP H3 (당시 기록)

- [HTML](archive/v48/WIP_MULTI_SHIP_H3/Aegis_SIM_v48_WIP_MULTI_SHIP_H3.html), **15,683,482 bytes**, SHA `0a9626535c209d8ad4e5a9b5262bd826d8ede8df928562534ba6c44b5673d178`.
- owner별 **대수상 공격 AI**: fresh 현지 HOSTILE 수상 관측·별도1/2발 공격 동의(120초)·발사대/사거리/예측 오차·chart/아군 보호를 거쳐 기존 native 하푼을 발사한다. 자함/아군함 기본OFF이며 전술 AI ON + AUTO와 동의가 필요하다. FLEET에서 공격량/동의/철회를 조작한다.
- 개방 중 OFF/철회/관제 인계·식별/alias/관측 소실/손상/보호 변경은 actual release를 막는다. 수동 하푼/waypoint 우선, 예비2발, native 자동 고정 튜브 선택/INS→ARH/DL0와 기존 H1/H2/G 물리·방어·기동·3D/해상효과를 유지한다.
- 적함도 자기 현지 HOSTILE 파일에만 mission 살보를 실행한다. IFF 무응답을 적성으로 간주하지 않아 UNKNOWN 첫 공격은 보류한다. 공유/ESM-only는 공격 권한이나 현지 FCS가 아니다. AI는 비행 위치/명중 truth를 알지 못한다.
- strict settings-only 저장, H2/H1/G/F/B/no-fleet 명시 OFF migration, 동의/계획/capability reset. 최종 원본 직접 **1198/1198 PASS**, page/core/runtime/presentation 오류0. [상태](archive/v48/WIP_MULTI_SHIP_H3/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H3.md), [SHA](archive/v48/WIP_MULTI_SHIP_H3/SHA256SUMS_v48_WIP_MULTI_SHIP_H3.txt), [운용](docs/multiship/H3/README.md), [직접 검증](docs/multiship/H3/evidence/verification-summary.json), [조건](docs/multiship/H3/PERFORMANCE.md), [남은3단계](docs/multiship/H3/DEPENDENCIES.md).
- H2 `59fad37cc170c760c1659b916febc168021a31b4` 위 `multiship-tactical-h3`, PR base H2. 원본 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. main/선행 PR 병합은 실행하지 않는다.

## 직전 개발 기준 — Multi Ship WIP H2

- [HTML](archive/v48/WIP_MULTI_SHIP_H2/Aegis_SIM_v48_WIP_MULTI_SHIP_H2.html), **15,675,514 bytes**, SHA `522f48fe0707c2e6393068b66b76ec99a4d8dfa68bfab025fe9399b2bbc557b1`.
- 관측 기반 **기동 utility AI**가 승인된 현지 위협·조종/장비 상태·기존 SPG-62/CIWS 사각으로 유지/선회/속력 후보를 비교한다. native 타/기관 명령만 쓰며 실제 선회·가감속·피해/침수 물리를 유지한다. chart 해안과 관측된 수상 교통으로 위험 후보를 제외한다.
- FLEET **기동 AI ON/OFF / 기동 AI 재개**, 자함 기본OFF·아군/적함 기본ON. 전술 AI ON + AUTO에서 실행하며 NAV/FLEET 수동 항법·지도 항로 조작이 우선한다. ON/OFF는 수동 우선권을 지우지 않는다. 기동 재개는 레이더/EW 수동 hold를 유지한다.
- 요청 항법 baseline과 strict 설정만 저장하며 판단/목표/명령 소유권은 reset/import 때 비운다. H1/G/F/B/no-fleet 저장을 명시 migration한다. 공유/ESM만으로 기동·현지 FCS·적성 식별을 생성하지 않는다. 기존 방어 gate·물리/비행·CG RAM0·고정 셀·Harpoon DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_H2/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H2.md), [SHA](archive/v48/WIP_MULTI_SHIP_H2/SHA256SUMS_v48_WIP_MULTI_SHIP_H2.txt), [운용/계약](docs/multiship/H2/README.md), [직접 검증](docs/multiship/H2/evidence/verification-summary.json), [측정 조건](docs/multiship/H2/PERFORMANCE.md), [후속 H3](docs/multiship/H2/DEPENDENCIES.md), [직접 업로드](docs/multiship/H2/GITHUB_HANDOFF.md).
- 최종 원본 직접 **883/883 PASS**, page/core/runtime/presentation 오류0. 실제 기동·수동 항법/저장·사각/해안/수상 접촉, 자연 센서→AI→요격, 세 척1/8/16/64 결정성, H1 물리/RNG, 실제 WebGL/RAF 피격·복원을 확인했다. 조건과 한계는 위 집계를 따른다.
- `multiship-tactical-h2`는 H1 head `43021f9693dc0500b5f2def531ec5d0d9e17bf0b` 위다. 원본 직접 업로드·독립 readback을 수행한다. Actions 사용 불가 조건에 따라 수동 workflow만 준비하고 로컬 검증으로 마감한다. 다음은 **H3 대수상 공격 AI**다.

## 직전 개발 기준 — Multi Ship WIP H1

- [HTML](archive/v48/WIP_MULTI_SHIP_H1/Aegis_SIM_v48_WIP_MULTI_SHIP_H1.html), **15,669,638 bytes**, SHA `e683e23f3bb832bac29bde05def2c46ce3acdbfe114cea37ce2156ec90db5058`.
- 함정별 **유틸리티 방어 AI**가 현지 관측의 접근 긴급도·미대응 수·가용탄·사통 채널·장비 손상을 비교한다. 기존 AUTO 실행기에 표적 우선순위와 부족한 탄약의 살보 배분을 연결하고 레이더·전자전 준비를 조절한다. 발사 권한·사각·NEZ·예비탄·BDA·G 아군 보호/담당 분담은 기존 gate를 유지한다.
- FLEET의 **전술 AI ON/OFF / AI 운용 재개**로 조작한다. 자함 기본 OFF, 아군/적함 기본 ON이며 해당 owner AUTO에서 실행한다. 수동 레이더·전자전과 공동 EMCON이 우선한다. 공유·ESM 경보는 준비에만 쓰며 현지 FCS 없이 발사하지 않는다.
- 설정만 strict detached preflight로 저장하고 판단·우선 파일·임시 radar/EW 소유권은 reset/import 때 비운다. G/F/B 저장은 명시 migration한다. 기존 owner 항법·3D·물리/비행·CG RAM0·고정 셀·Harpoon DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_H1/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H1.md), [SHA](archive/v48/WIP_MULTI_SHIP_H1/SHA256SUMS_v48_WIP_MULTI_SHIP_H1.txt), [운용/계약](docs/multiship/H1/README.md), [직접 검증](docs/multiship/H1/evidence/verification-summary.json), [측정 조건](docs/multiship/H1/PERFORMANCE.md), [후속 H2/H3](docs/multiship/H1/DEPENDENCIES.md), [직접 업로드](docs/multiship/H1/GITHUB_HANDOFF.md).
- 최종 원본 직접 **625/625 PASS**, page/core/runtime/presentation 오류0. H1-on 실제 발사, 초기 트랙 없는 자연 센서→AUTO, 수동/그룹 우선권과 손상, 세 척1/8/16/64 결정성, 기존 G 물리/RNG, 실제 WebGL/RAF 피격·복원을 확인했다. 조건과 한계는 위 집계를 따른다.
- `multiship-tactical-h1`은 G head `d902d24486918c23d43e3067be16ab03fbaedde2` 위다. 원본 직접 업로드·독립 readback을 수행한다. Actions 사용 불가 조건에 따라 수동 workflow를 준비하고 로컬 검증으로 마감한다. 다음은 **H2 기동 utility**, 이어 H3 대수상 공격이다.

## 직전 개발 기준 — Multi Ship WIP G

- [HTML](archive/v48/WIP_MULTI_SHIP_G/Aegis_SIM_v48_WIP_MULTI_SHIP_G.html), **15,664,301 bytes**, SHA `7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7`.
- 새 **FLEET** 탭에서 함정 변경으로 자함/아군함을 선택하고 속력·타각, 수동/자율 방어, 현지 표적 식별과 SAM·함포·Harpoon 발사, EMCON·링크/공유/방어 분담을 조작한다. 공동 탐색 레이더 정책은 함대에 적용한다. 각 함정의 항법·현지 track ID·탄약·센서/무장·피해 runtime은 유지한다. NAV·ARM·CIC·기존3D 교전 버튼은 원래 자함 기준이다.
- 3D 아군함 보기의 실제 pointer/touch 입력을 고쳤다. 카메라 focus/reset/retire 레이블과 FLEET의 선택 함정 3D 보기도 연결했다.
- 아군의 측정 위치·속도·공분산·관측 시각을 2Hz/.3s 지연으로 공유한다. 보수적 covariance intersection의 CIC 정정, 연결 손실 시 개별 EMCON 복귀, 현지 FCS 승인에 한정한 SAM 분담을 적용한다. 공유만으로 사통을 생성하거나 원격 발사하지 않는다.
- 하푼의 빔각·선회·짧은 재획득 때 이전 레이더 관측과 발사 기록으로 연관을 이어가고 애매하면 자동 요격을 보류한다. 위치 미관측 때 지도에 없고 **Harpoon DL=0**이다. 비행/물리 커널·CG RAM0·고정 셀·함정별 해상효과를 보존한다.
- [상태](archive/v48/WIP_MULTI_SHIP_G/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_G.md), [SHA](archive/v48/WIP_MULTI_SHIP_G/SHA256SUMS_v48_WIP_MULTI_SHIP_G.txt), [구조/운용/한계](docs/multiship/G/README.md), [검증 집계](docs/multiship/G/evidence/verification-summary.json), [측정 조건](docs/multiship/G/PERFORMANCE.md), [후속 H 전술 AI](docs/multiship/G/DEPENDENCIES.md), [직접 업로드](docs/multiship/G/GITHUB_HANDOFF.md).
- 최종 원본 직접 **897/897 PASS**, page/core/runtime/presentation 오류0. mouse/touch와 실제 RAF camera, owner별 실제 발사/보호, 세 척1/8/16/64 결정성, native3D 피격/복원과 F 물리/RNG 회귀를 확인했다. 각 tested SHA와 조건은 위 집계를 따른다.
- `multiship-network-g`는 F head `e4a1ceb6700f1d891e1c11aee0f9519b8ccde9c5` 위다. 원본 직접 업로드와 원격 readback을 수행하며 Actions 사용 불가 조건에 따라 로컬 검증으로 마감한다. 수동 workflow는 dispatch하지 않는다. main/선행 branch를 임의 병합하지 않는다.

## 직전 개발 기준 — Multi Ship WIP F

- [HTML](archive/v48/WIP_MULTI_SHIP_F/Aegis_SIM_v48_WIP_MULTI_SHIP_F.html), **15,638,513 bytes**, SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`.
- 출항 전 아군/적군을 각각 없음/DDG-119/CG-52로 선택한다. 아군은 자함 근처, 적군은10~30km 임의 해상에 배치한다. 초기 레이더 EMCON·시험 표적함·항공기 ON/OFF도 선택한다. normal3D `아군함 보기`로 적 truth 위치를 드러내지 않는다.
- 함정별 ESM·noise/replay·눌카/SRBOC를 기존 owner 무장/방어 AUTO에 연결했다. 실제 방사·대역·기하·손상·수신빔과 자기 측정으로 대응한다. CIC는 자함의 방위/오차·신호세기 및 거리 미확정만 표시한다. 초기 EMCON은 레이더 침묵이며 방어 ECM 정책과 분리한다.
- 아군·적군에도 자함과 같은 함수파·선미 포말·항적을 표시한다. 실제 속도/위치·침로와 함종 수선면을 따르며 표시용 history/mesh는 owner별로 분리·폐기한다.
- 인증 IFF 측정을 기존 수상 트랙에 연관해 FRIEND 보호한다. 아군 네트워크/정정/공동 EMCON·합동교전·기동/공격 AI는 다음 단계다. CG RAM0, 원본 물리·고정 셀·Harpoon INS→ARH/DL0를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_F/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_F.md), [SHA](archive/v48/WIP_MULTI_SHIP_F/SHA256SUMS_v48_WIP_MULTI_SHIP_F.txt), [구조/검사/한계](docs/multiship/F/README.md), [다음 단계](docs/multiship/F/DEPENDENCIES.md), [최종 검증](docs/multiship/F/evidence/verification-summary.json), [측정 조건](docs/multiship/F/PERFORMANCE.md), [직접 원격 반영](docs/multiship/F/GITHUB_HANDOFF.md).
- 최종 원본 직접 **593/593 PASS**. 실제 Kh-35U RF/자연 관측 AUTO·시커 재밍, 세 척1/8/16/64 결정성, 실제3D 피격/복원을 확인했다. ESM RNG 분리로 E 대비 일부 raid 발사 순서/잔탄은 바뀐다. DDG EW 안테나는 별도 등록이 없어 legacy RF 기준점으로 유지한다. SIM-TUNE/SwiftShader와 상세 한계는 위 문서를 따른다.
- `multiship-ew-f`는 E head `bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6` 위다. 원본 HTML을 직접 업로드·readback한다. Actions 사용 불가라는 사용자 조건에 따라 로컬 검증으로 마감하며 새 workflow는 수동 실행용이다. main/선행 branch를 임의 병합하지 않는다.

## 직전 개발 기준 — Multi Ship WIP E

- [E HTML](archive/v48/WIP_MULTI_SHIP_E/Aegis_SIM_v48_WIP_MULTI_SHIP_E.html), 15,609,329 bytes, SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`. [E 상태](archive/v48/WIP_MULTI_SHIP_E/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_E.md), [PR #49](https://github.com/0-FLANDRE-0/Aegis_Project/pull/49).
- 원래 AUTO/BDA·alias/지원 이관과 항공기 ON/OFF를 owner-local로 실행했다. 당시 E660건은 역사 기록이며 F 직접 수에 합산하지 않는다. E 원본 세트/workflow는 same bytes/blob으로 archive에 보존한다.

## 직전 개발 기준 — Multi Ship WIP D

- [D HTML](archive/v48/WIP_MULTI_SHIP_D/Aegis_SIM_v48_WIP_MULTI_SHIP_D.html), SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`, 15,575,097 bytes. [D 상태](archive/v48/WIP_MULTI_SHIP_D/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_D.md), [PR #48](https://github.com/0-FLANDRE-0/Aegis_Project/pull/48).
- 5A/5B의 owner 무장·양방향 실물 접촉/구획 피해·3D와 advisory shadow를 구현했다. E에서 방어 AUTO/BDA를 추가했으며 D 기록과 증거는 역사 기준으로 보존한다.

## 직전 개발 기준 — Multi Ship WIP C

- [HTML](archive/v48/WIP_MULTI_SHIP_C/Aegis_SIM_v48_WIP_MULTI_SHIP_C.html), **15,344,725 bytes**, SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`.
- 4단계: 실제 배치 함정의 SPY/해면탐색/항법 레이더와 익명 관측·추정 트랙을 함정별로 실행한다. 자함 CIC는 자함 관측만 읽으며 상대 위치·정체를 바로 주입하지 않는다. CG/DDG의 면 배치·센서 profile, 지평선·지형 차폐와 EMCON/손상·coast를 적용한다.
- 이후 헬기를 받을 오차·시각·지연·링크 단절이 있는 외부 관측 포트를 준비했다. **헬기 자체와 양방향 무장/EW/AI는 후속 단계**다. Harpoon 발사 후 DL=0, 기본 적함 없음/자함 EMCON ON, 60/120/20 Hz를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_C/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_C.md), [SHA](archive/v48/WIP_MULTI_SHIP_C/SHA256SUMS_v48_WIP_MULTI_SHIP_C.txt), [구조/포트](docs/multiship/C/README.md), [다음 단계](docs/multiship/C/DEPENDENCIES.md), [검증 집계](docs/multiship/C/evidence/verification-summary.json), [측정 조건](docs/multiship/C/PERFORMANCE.md), [GitHub 인계](docs/multiship/C/GITHUB_HANDOFF.md).
- `multiship-sensors-c`는 B head `ae94326caea7cd0329233f381933cdc240bedb47` 위에서 이어간다. B 원본 세트/workflow는 동일 bytes로 archive에 보존한다. stable v48은 그대로다. 새 PR은 B branch를 base로 하며 A/B/C는 미병합 상태로 유지한다.

- 최종 파일 직접 검증 **417/417 PASS**. [PR #47](https://github.com/0-FLANDRE-0/Aegis_Project/pull/47), [독립 원격104파일 readback](docs/multiship/C/evidence/remote-publication.json). CI 실제 상태는 해당 최신 head checks를 따른다.

## 직전 개발 기준 — Multi Ship WIP B

- [HTML](archive/v48/WIP_MULTI_SHIP_B/Aegis_SIM_v48_WIP_MULTI_SHIP_B.html), **15,328,273 bytes**, SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`.
- 3단계: 출항 전 선택한 DDG-119/CG-52를 실제 세계에 배치한다. 각 함정의 항해·피해·침수·구획/승조원·질량/동역학·침몰/구명뗏목과 원본 3D 모델을 독립 실행한다. `3D VIEW → 배치 함정 보기`로 카메라를 바꾼다.
- 함정별 센서와 양방향 요격/공격·EW·AI는 4~7단계 잔여다. 상대 truth 위치를 CIC/교전 판단에 주입하지 않는다. 기본 적함 없음과 기존 자함 운용, shared world 1회 및 60/120/20 Hz 주기를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_B/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_B.md), [SHA](archive/v48/WIP_MULTI_SHIP_B/SHA256SUMS_v48_WIP_MULTI_SHIP_B.txt), [범위/저장/진단](docs/multiship/B/README.md), [다음 단계](docs/multiship/B/DEPENDENCIES.md), [검증 집계](docs/multiship/B/evidence/verification-summary.json), [측정 조건](docs/multiship/B/PERFORMANCE.md).
- `multiship-physics-b`는 A head `3fab03782abb313cd3ece1bbfe254cdb77981231`을 기준으로 한다. A PR #45가 미병합이므로 B PR은 A 위에 연결한다. A HTML/status/SHA/workflow는 같은 bytes/blob으로 archive에 보존하고 stable v48은 변경하지 않는다. 원본 HTML 직접 업로드·원격 readback과 CI는 [GitHub 인계](docs/multiship/B/GITHUB_HANDOFF.md)를 따른다.

- 최종 직접 검증 **466/466 PASS**. [PR #46](https://github.com/0-FLANDRE-0/Aegis_Project/pull/46), [원격 56파일 readback](docs/multiship/B/evidence/remote-publication.json). CI 실제 상태는 해당 PR의 head checks를 따른다.

## 직전 개발 기준 — Multi Ship WIP A

- [HTML](archive/v48/WIP_MULTI_SHIP_A/Aegis_SIM_v48_WIP_MULTI_SHIP_A.html), **15,314,629 bytes**, SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`.
- 1~2단계: 기존 동작·성능 기준 기록과 독립 함정 상태/컨텍스트. 출항 전 표적함 `있음/없음`, 적함 준비 `없음/DDG-119/CG-52`를 선택하고 저장·reset에도 적용한다.
- 적함은 **STATE_BOUND_INACTIVE** 준비 상태다. 실제 해상 모델 배치·항해·탐지·요격·공격·EW/AI는 3단계 이후다. 자함의 기존 UI·물리·전투 루프와 세계 업데이트 1회를 유지한다.
- [상태](archive/v48/WIP_MULTI_SHIP_A/AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_A.md), [SHA](archive/v48/WIP_MULTI_SHIP_A/SHA256SUMS_v48_WIP_MULTI_SHIP_A.txt), [상세/한계](docs/multiship/A/README.md), [다음 단계](docs/multiship/A/DEPENDENCIES.md), [검증 집계](docs/multiship/A/evidence/verification-summary.json), [업로드 인계](docs/multiship/A/GITHUB_HANDOFF.md).
- 브랜치 `multiship-runtime-a`, 기준 main `cb70a637105ce00e7c0619270237cc35a83d39c2`. 사용자 업로드 `28dfc4fcefb22e8c0989617b2212e37d096c05d6`의 HTML을 검증본과 byte 단위로 대조했다. [업로드 검증 기록](docs/multiship/A/evidence/remote-upload-check.json). 이 revision은 지원 파일·E archive 이동·직접 업로드 규칙을 포함한다. PR/Actions 결과는 GitHub 기록을 따른다. stable v48은 같은 bytes로 보존한다.
- [GitHub 규칙 7.1](AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인): 사용자 승인에 따라 앞으로 Codex가 원본 HTML과 지원 파일을 직접 업로드하고 원격 bytes를 확인한다. 사용자 수동 HTML 업로드는 필수가 아니다.

## 직전 병합 기준 — Harpoon WIP E

- [HTML](archive/v48/WIP_HARPOON_E/Aegis_SIM_v48_WIP_HARPOON_E.html), **15,285,590 bytes**, SHA `ad68f7a5e37ac066d8f3a70db0fc2aaa7e2611047112d4053c4380b94db8d842`.
- ARM → VLS 하푼 아래 웨이포인트 지정/해제. 최대8점 CIC 탭·초안 점선, 해제 시 AIM 커서 복귀. 발사 시 관/경로 pin, 성공 뒤 초안 삭제/다음 탄의 독립 경로. 마지막 점 전 ARH OFF, INS 평면 통과 뒤 전방 SEARCH. 마지막 점은 탐색 시작점이다.
- 고정 좌표 검색 계획 +8km search/+2km turn reserve ≤140km SIM-TUNE, fuel0.225kg/s. 익명 height/Doppler filter 조정·DL0·보호 수상 track/수동 발사·자동 관/고정재고·DDG 미설치를 유지한다. CG E_1/C·B·A·G·D 명시 legacy; route/flight는 transient다.
- 동일 bytes **178/178 PASS**, 120/124/130km×정지/15kt6건 물리 접촉·empty-sea 강제명중0, 1/8/16/64×3072 full ticks exact, native640×480 실제 경로2/발사2·덮개/부스터/RAF/reset·오류0. 단일 seed·terrain bypass/focused60Hz range와 SwiftShader 범위를 명시하고 실제140km 전조건 인증/일반 명중률을 주장하지 않는다.
- [상태](archive/v48/WIP_HARPOON_E/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_E.md), [SHA](archive/v48/WIP_HARPOON_E/SHA256SUMS_v48_WIP_HARPOON_E.txt), [E 상세](docs/harpoon/E/README.md), [집계](docs/harpoon/E/evidence/verification-summary.json), [인계](docs/harpoon/E/GITHUB_HANDOFF.md).
- 사용자 업로드 `a96053ba1dc56389822c17c92a632f21fcc446b2`의 E HTML을 전달본과 byte 단위로 대조했고 원격 무결성 검사도 통과했다. 이 revision은 작은 지원 파일·상태/SHA·E 전체 workflow와 K 기존 blob의 archive 이동을 포함한다. 전체 Actions와 병합 결과는 [PR #44](https://github.com/0-FLANDRE-0/Aegis_Project/pull/44)를 따른다. [업로드 검증 기록](docs/harpoon/E/evidence/remote-publication.json).

## 직전 로컬 비교 — Harpoon WIP D

D HTML/status/SHA는 `archive/v48/WIP_HARPOON_D/`에 같은 bytes 보존했다. 당시 SHA `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`, 15,283,086 bytes. 자동 관 선택 직접67/67과 이후 별도 장거리 보고(60km gate 통과/100·120·124km prediction basket 거부, gate-only 우회124km15kt miss)는 [D 당시 상태](archive/v48/WIP_HARPOON_D/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_D.md)와 [D 장거리 보고](docs/harpoon/long-range/D/REPORT.md)를 따른다. E는 좌표 route mode로 장거리를 별도 검사하며 track-only prediction basket은 유지한다. K+작은 A/B/C/D 모듈로 D exact 재생성 가능하고 큰 D archive는 신규 remote 업로드 대상이 아니다.

## 직전 로컬 비교 — Harpoon WIP C

C HTML/status/SHA는 `archive/v48/WIP_HARPOON_C/`에 같은 bytes 보존했다. 당시 HTML SHA `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`, 15,281,856 bytes, 직접155/155 기록은 [당시 상태](archive/v48/WIP_HARPOON_C/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_C.md)와 [C 근거](docs/harpoon/C/README.md)를 따른다. A/B/C 큰 archive HTML은 remote 업로드 대상이 아니며 K+작은 모듈로 exact 재생성한다. C workflow/manifest는 역사 보존하고 현재 검사는 E manifest/workflow다.

## 직전 로컬 비교 — Harpoon WIP B

B HTML/status/SHA는 `archive/v48/WIP_HARPOON_B/`에 같은 bytes 보존했다. 당시 HTML SHA `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`, 15,274,780 bytes, 직접133/133 기록은 [당시 상태](archive/v48/WIP_HARPOON_B/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_B.md)와 [B 근거](docs/harpoon/B/README.md)를 따른다. A/B 대형 archive HTML은 remote에 없고 upload 대상이 아니다. K+작은 A/B 모듈로 비교본을 exact 재생성하며 역사 manifest/workflow는 현재 검사로 사용하지 않는다.

## 직전 로컬 비교 — Harpoon WIP A

- A HTML/상태/SHA는 로컬 `archive/v48/WIP_HARPOON_A/`에 같은 bytes로 보존했다. HTML은 14,962,500 bytes, SHA `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`이다. [당시 상태](archive/v48/WIP_HARPOON_A/AEGIS_PLAN_STATUS_v48_WIP_HARPOON_A.md), [A 소형 모듈·검사](docs/harpoon/A/README.md), [공개 자료](docs/harpoon/A/SOURCES.md), [당시 155/155 집계](docs/harpoon/A/evidence/verification-summary.json).
- A는 remote에 업로드되지 않았다. 원격 비교는 이미 존재하는 K blob과 작은 A 모듈에서 exact 재생성한다. 로컬 A archive HTML을 새 remote binary로 전송하지 않는다. A 당시 업로드 인계/workflow/support manifest는 역사 근거이며 현재 E의 분담과 manifest가 우선한다.
- A의 K 284건·기존 CG30/DDG14 이력은 B 검사에 재실행 수로 합산하지 않는다. 정식 v48은 별도 안정 기준이다.

## 직전 병합 기준 — 벙커힐 WIP K

- 파일: [Aegis_SIM_v48_WIP_BUNKERHILL_K.html](archive/v48/WIP_BUNKERHILL_K/Aegis_SIM_v48_WIP_BUNKERHILL_K.html), **14,458,866 bytes**, SHA-256 `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`.
- 사용자 업로드 commit `5c883a5aeb80e0878f0f256f2a7a64d90224920e`의 HTML을 검증본과 byte 단위로 대조했다. [원격 업로드 근거](docs/bunkerhill/K/evidence/remote-upload-check.json).
- 출항 전에 DDG-119 또는 퇴역 전 구성의 CG-52 USS Bunker Hill을 선택한다. 벙커힐은 원본 모델, 고정 61+61 VLS, 전후 함포, 양현 20mm Phalanx, 독립 장착 좌표·사각·탄약을 사용한다. SPG-62 접시 전체 회전, 레이더 회전 부품, 거친 해면 클러터와 피격 후 3D 지속을 검사했다.
- CIC에는 벙커힐의 전·후·양현 SPY 배열 방향을 표시하고 DDG의 기존 대각선 도식은 유지한다. 선택 함선의 피격 인디케이터와 선수 좌측 측면도를 사용한다. CG 내부는 SIM-TUNE 12갑판·277구획·330명 배치다.
- **SHIP → 보수반 → 승조원·함 포기**에서 실제 경로로 도착한 생존자부터 25인승 구명뗏목에 순차 탑승한다. CIC·3D 바다에서 표류하며 저장·복원된다. 정상 전원 퇴함에서 CG 330명/14척/마지막 5명과 DDG 310명/13척/마지막 10명을 확인했다.
- 구명뗏목 정원은 USN Mark 7 공개 자료를 따른다. 실제 CG 비치 수량·진수 위치는 미확정이며 충분한 provision·진수점·형상·표류·접촉은 SIM-TUNE이다. 레이더의 공개 확인 범위와 SPQ-9 두 면의 SIM-TUNE도 명시했다. [구명뗏목 근거](docs/bunkerhill/K/RESCUE_SOURCES.md), [레이더 근거](docs/bunkerhill/K/RADAR_SOURCES.md).
- 로컬 K **284/284** 검사 통과. [상태](archive/v48/WIP_BUNKERHILL_K/AEGIS_PLAN_STATUS_v48_WIP_BUNKERHILL_K.md), [체크섬](archive/v48/WIP_BUNKERHILL_K/SHA256SUMS_v48_WIP_BUNKERHILL_K.txt), [suite와 한계](docs/bunkerhill/K/evidence/verification-summary.json), [GitHub 반영·검증 안내](docs/bunkerhill/K/GITHUB_VALIDATION.md).
- [Bunker Hill workflow](.github/workflows/bunkerhill-late-profile.yml)가 업로드된 동일 HTML로 exact 재빌드, CIC, 퇴함·저장·배속·native 3D, CG/DDG, 셀·구획·클러터·SPG·실제 다수 Kh-32 AUTO를 검사한다. 원격 결과는 PR의 Actions checks와 artifact를 따른다. 일반 smoke에는 역사 payload 검사도 포함된다.
- 대형 비교 HTML을 추가 업로드하지 않고, 최신 K 내장 asset과 작은 기준 모듈로 D/F/H/I/J를 고정 SHA에 맞춰 재구성한다. 이전 Bunker Hill HTML archive는 전달한 로컬 ZIP에 보존되어 있다. GitHub의 선행 STARTUP_A는 당시 HTML·상태·전체 체크섬 대상 32개 파일을 `archive/v48/WIP_STARTUP_A/`에 exact 보존했고, 기존 root baseline은 역사 검사 호환을 위해 유지한다.
- K는 [PR #43](https://github.com/0-FLANDRE-0/Aegis_Project/pull/43)으로 main에 병합했다. K 뒤의 최신 하푼 구현·검사는 위 E를 따른다. 정식 v48은 별도 안정 기준으로 유지한다.

## 현재 안정 기준 — v48

- 정식 파일: [`Aegis_SIM_v48.html`](Aegis_SIM_v48.html)
- 크기: `7,354,511 bytes`
- SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- **WIP15C를 코드 변경 없이 byte-identical로 승격한 안정판**이다.
- 상태: [`AEGIS_PLAN_STATUS_v48.md`](AEGIS_PLAN_STATUS_v48.md), [체크섬](SHA256SUMS_v48.txt)
- WIP15에서 SRBOC 6기/36튜브 실제 발사 원점, 예비탄·빈 발사기 단위 재장전, Nulka active decoy, ASM seeker acquisition 안정화, SM-2ER/SM-6 수동 대수상 교전, WIP13A 침수 self-test fixture 수리를 마쳤다.
- WIP15C 최종 검사에서 core self-test failure `0`, final runtime page error `0`.
- 상세 WIP15C 감사·검증 기록은 [`docs/wip15/C/`](docs/wip15/C/)에 보존한다.

## 선행 검증 — 출항 전 함선 선택·초기화

- 파일: [`Aegis_SIM_v48_WIP_STARTUP_A.html`](Aegis_SIM_v48_WIP_STARTUP_A.html), `7,361,673 bytes`, SHA-256 `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`.
- 준비 branch: [`ship-startup-ddg-regression`](../../tree/ship-startup-ddg-regression), parent `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`. WIP 번호 미확정이며 `WIP_STARTUP_A`는 기능명 토큰이다.
- 선택 전에 runtime 생성을 대기하고 불변 profile을 확정한 뒤 공통 세션 생성 → 기존 subsystem 결속 → 장비 편성 → 출항을 수행한다. 이 단계에 등록된 운용 함선은 DDG-119였다.
- [상태](AEGIS_PLAN_STATUS_v48_WIP_STARTUP_A.md), [체크섬](SHA256SUMS_v48_WIP_STARTUP_A.txt), [구현·검사·인계](docs/ship-startup/A/README.md).
- 로컬: package 34/34, startup 15/15, DDG runtime 14/14, 실제 3D 복구 13/13 PASS. 기존 B와 전투 aggregate·발사·명중·교전 결과가 같다. 상세 float의 최대 차이 약 `3.9e-13`을 기록했다.
- 사용자 업로드 commit `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`의 크기·Git blob·parent를 확인했으며 검증본과 exact 일치한다. tested head `61a8931f0cc5e933fb901e270e0f5f28e046519b`에서 [출항 준비 CI](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412380) **1/1**, [원본 B 회귀](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412362) **1/1**, [일반 smoke](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37102412322) **32/32 job PASS**. 일반 3D의 실제 입력은 이번 HTML이며 다른 일반 job에는 역사 payload가 포함된다.
- [PR #42](https://github.com/0-FLANDRE-0/Aegis_Project/pull/42)는 `WIP16` 위의 후속 draft PR이다. 단계 구현·업로드·원격 회귀는 완료했다. 마감 문서·증거·체크섬 반영은 tested source를 변경하지 않는다. 기존 PR #41/main/안정 v48은 변경하지 않았다. 다음 구현은 벙커힐 profile·model·builder 연결이다.

## 직전 검토 후보 — v48 WIP16B

- 작업 branch: [`WIP16`](../../tree/WIP16), PR [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41).
- 이전 사용자 업로드 파일: [`Aegis_SIM_v48_WIP16B.html`](archive/v48/WIP16B/Aegis_SIM_v48_WIP16B.html), **7,357,036 bytes**. `7562bb0925e2b85521d37fefd2c81898ed6de18a`에서 원격 크기·Git blob이 로컬 검증본과 exact 일치한다. B HTML/상태/체크섬은 동일 Git blob으로 archive에 보존했다.
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
