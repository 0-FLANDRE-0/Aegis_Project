# AEGIS v48_WIP_MULTI_SHIP_G 상태

판정: **완료 — 최종 원본 897/897 로컬 검사 PASS**, page/core/runtime/presentation 오류0. GitHub Actions는 사용 불가라는 사용자 조건으로 실행하지 않는다. 별도 실제 휴대폰/GPU FPS 인증은 하지 않았다.

## 기준과 파일

- HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_G.html`, 15,664,301 bytes.
- HTML SHA-256 `7ffded6480e74e0f9ab6259c2c8a9e4dfd81ad70bb2434d8dcfd711db2e7bda7`.
- decoded main SHA-256 `a6f5a22de6ca0a4daac033dd05c3a2c03f8b5aeaeb5f97c0b6e8c4c7f2c1911f`.
- 기준 F head `e4a1ceb6700f1d891e1c11aee0f9519b8ccde9c5`, F HTML SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`.
- branch `multiship-network-g`, PR base `multiship-ew-f`. main/선행 branch 병합은 이번 범위에 없다.
- 지원: [G README](docs/multiship/G/README.md), [검증 집계](docs/multiship/G/evidence/verification-summary.json), [성능 조건](docs/multiship/G/PERFORMANCE.md), [인계](docs/multiship/G/GITHUB_HANDOFF.md), [다음 H](docs/multiship/G/DEPENDENCIES.md).

## 완료된 동작

1. **FLEET 탭**을 NAV/ARM/DEBUG와 함께 넣었다. 함정 변경으로 자함/아군함을 선택하고 FLEET의 속력·타각, 수동/자율 방어, EMCON·링크/공유/방어 분담, 현지 표적 선택/식별, SAM·함포·Harpoon 발사를 조작한다. 기관 명령은 원래 C17 전령 값으로 환산한다. 선수/후미 함포와 실제 설치된 무장/잔탄만 선택한다. 각 native owner 포트가 실행하며 다른 함정의 재고·센서/FCS·피해를 옮기지 않는다.
2. 3D 아군함 보기 버튼이 pointer-events:none 툴바의 직접 자식이어서 실제 input을 받지 못하던 문제를 수정했다. native press·pointer/touch로 focus를 바꾸고 reset/retire 레이블을 동기화한다. FLEET의 선택 함정 3D 보기도 연결했다. 실제 RAF 이후 camera position/함정 중심/복귀와 simulation state 무변경을 확인했다.
3. friendly 인증 항법/오차 및 현지 KF 추적/공분산/관측 시각을 2Hz/.3s 지연으로 공유한다. receiver-owned 파일·bounded queue와 보수적 covariance intersection으로 CIC 표시를 정정한다. canonical KF/FCS에는 원격 공유 파일을 쓰지 않는다. 공유만 있는 접촉은 UNKNOWN과 NET/age/coast로 표시한다.
4. 공동 탐색 레이더 개별/모두 탐색/모두 침묵/자함만/아군함만 정책을 지연 lease로 적용한다. radar silence 중에도 link 송신은 별도이며 연결 손실 시 각 함정의 개별 EMCON 값으로 복귀한다. FLEET의 개별 EMCON 조작은 그룹 정책을 끝내고 해당 owner의 native command로 전달한다.
5. 실제 현지 FCS/ROE 승인과 공유된 bid/한시적 lease에 한정해 SAM 담당을 분담한다. native 실제 VLS 발사에서 다시 검사한다. 긴급 자기방어와 단절/lease 만료는 독립 방어로 복귀한다. RAM/Phalanx를 lease로 막지 않으며 보호 식별은 유지한다.
6. 자함 하푼의 beam/notch·선회·짧은 재관측/새 alias 때 발사 승인 기록과 이전 레이더 측정 위치/속도 오차·시각·기동 여유로 연관을 유지한다. 모호하면 UNKNOWN/자동교전 보류다. 최초 연관은 기존 발사 회랑·발사 전 기존 파일 제외를 유지한다. actual flight/INS/seeker/alive를 읽어 위치나 FRIEND를 생성하지 않는다. **DL0/미관측 위치 없음**, 기존4초 표시 coast와 독립 INS→ARH를 유지한다.
7. network bool/enum 설정을 strict detached preflight 후 복원한다. F/B/no-fleet 저장은 명시 migration만 한다. 잘못된 저장은 authoritative 상태를 바꾸지 않는다. report/peer/lease/group 실행·선택/현지 command target/비행/관측 transient는 import/reset/deployment/retire에서 초기화한다. F의 누락된 외함 EW retirement도 처리했다.

## 운용 범위와 한계

- **NAV·ARM·CIC·3D 상단 기존 교전 버튼은 원래 자함 기준**이다. 아군함 조종·교전은 FLEET에서 한다. PLAYER/ALLY role이나 global profile/runtime을 교환하지 않는다. FLEET의 표적 목록은 선택 함정의 신선한 현지 관측이다. 공유 트랙만으로 발사하지 않는다.
- speed/rudder·identity/weapon/owner-local track 주소를 검사하고 enemy owner·잘못된 필드·한계 밖 명령은 거부한다. 수동 발사는 confirmed/fresh local HOSTILE/TRAINING_TARGET이며 FRIEND/NEUTRAL/UNKNOWN/stale 또는 AUTO 수동 포트는 보류한다. 실제 사각·탄약·손상·관측 품질·사통 조건은 원래 native 게이트를 유지한다.
- 외함 방어 관제의 import/reset 초기화는 기존 E 수명주기를 따른다. FLEET 선택/현지 target와 임시 발사 동의는 저장하지 않는다. 전환 자체가 자율 방어를 끄지는 않는다.
- desktop 세 열/mobile 한 열의 세로 스크롤이다. 아군함이 없으면 변경 버튼이 비활성이다. UI/mobile 검증은 에뮬레이션이며 실제 단말 성능 인증은 아니다.
- link/association·lease/Harpoon8초 재관측 gate는 게임 SIM-TUNE이다. 실제 Link16/CEC·전술 attack/maneuver AI·헬기·링크 파형/재밍/암호를 재현하지 않았다. 기존 SLQ I/J/X 재밍을 링크나 SPY S-band에 임의 적용하지 않는다. DDG EW antenna 등록/IFF 재인증 한계는 F 그대로다.

## 최종 직접 검증

| 검사 | 결과 |
|---|---|
| static | 48/48 PASS |
| guidance | 45/45 PASS |
| fleet-ui | 94/94 PASS |
| fleet-camera | 16/16 PASS |
| network-ui | 102/102 PASS |
| cooperation | 32/32 PASS |
| harpoon-protection | 26/26 PASS |
| clock | 104/104 PASS |
| native | 38/38 PASS |
| deployment-ew | 96/96 PASS |
| natural-ew | 22/22 PASS |
| defense | 76/76 PASS |
| aircraft | 48/48 PASS |
| weapons | 72/72 PASS |
| routes | 26/26 PASS |
| knowledge | 22/22 PASS |
| paired-ownship | 30/30 PASS |

모든 집계는 최종 HTML SHA를 실제로 실행한 결과다. source override·전임 G 파일 등가성 주장·F 역사 수를 합산하지 않았다. seed1831565813, 두 함종/three-owner1·8·16·64×1536 ticks, native WebGL 피격 ENTRY/EXIT/복원·카메라, 현지 수동 SAM/함포/Harpoon과 보호/오래된 관측 차단, natural Kh-35U EW와 경로 하푼을 포함한다. F/G idle·피격·Kh-32 8발 AUTO의 물리와 combat RNG는 exact다.

## 보존과 후속

F의 HTML/status/SHA/workflow 네 파일을 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_F/`에 옮겼다. stable v48, assets0~12/원본 models, 미사일·항법/피해/유체 커널,60/120/20Hz, 고정 VLS 셀, CG 양현 Phalanx/RAM0과 기존 해상효과를 유지한다. 원본 업로드 후 독립 원격 readback 증거는 `docs/multiship/G/evidence/remote-publication.json`을 따른다.

다음 H는 **현지 관측 기반 전술 AI**다. 위협·탄약/손상 상태에 따른 방어 태세·회피/방위 유지·현지 수상 공격을 native owner 포트 위에 연결한다. 헬기의 지평선 밖 관측, CEC급 사통과 RGM-109E Block Va는 별도 후속 범위다.
