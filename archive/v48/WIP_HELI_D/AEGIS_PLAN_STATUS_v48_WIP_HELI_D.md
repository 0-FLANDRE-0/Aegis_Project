# AEGIS v48 WIP HELI_D — 헬기 센서·IFF·Hawklink

- 원본 `Aegis_SIM_v48_WIP_HELI_D.html`, **16,058,953bytes**, SHA `843c86ac5de6f99ee3b9c24dcf425a79e5c0a55a11f0bc1cdec7c7c1546b25ac`, packed13 SHA `cfb6fa9a79d95cee17c68e99682d8476e851b848cb97208b48840f982100bb07`. [조작·계약](docs/helicopter/E/README.md), [검증](docs/helicopter/E/evidence/verification-summary.json).
- HELI_C `370d924a7bba5fa739498b9cd9e220e07abde823` 위 `helicopter-sensors`. A `856475f`, B `13c9b15`, C `de0e611`에서 각 단계 게이트를 고정했다. 최종 배포 코드는 같은 C 후보 bytes다.
- A: 비행 헬기의 물리 RF/CIWS 입력과 측정 기반 IFF를 연결했다. 기본 ON, 응답 유지/만료와 운용자 식별을 분리한다. 실제 SM-2/ESSM·CIWS 교전 판단의 아군 보호를 확인했다. OFF/무응답은 기존 ROE를 따르며 자동 적성이 아니다. 실제 헬기 피격·격추는 후속이다.
- B: 기본 OFF인 수상 전용 APS-153급 레이더. 공통 RF/SNR/해면/기상, 360° 회전당 1회 시도, 거리·방위 잡음과 SI 3×3 공분산을 사용한다. 밴드/출력/거리/오차는 모두 SIM_TUNED다. 같은70km 표적의50m/300m 수평선 차이, 실제 AIR/ASM 대표 사례 배제, 크기/기상/SNR과 고정 스텝을 확인했다.
- C: 원래 모함의 H1/H2 offboard source에 익명 plot을0.4초 지연 전송한다. **EMCON은 레이더 통제이므로 Hawklink를 끊지 않는다.** LOS/160km 상한/모함 장비 불능은 queue drain 전에 단절시키며 pending·신규 보고를 버리고 재전송하지 않는다. 통신 EMCON은 Link16·Hawklink 공통 후속 정책이다.
- 모함 자체 반사는 물리 장면에 남기고, C 전송에서 모함 자체 항법·선체와 측정 공분산으로 좁은 자기 접촉 영역을 제외한다. 같은 영역에서 분리되지 않는 근접 접촉도 제외되는 한계가 있다. truth ID/팀 정보로 표적을 제거하지 않는다.
- 순수 외부 관측만으로 실제 하푼 발사 경로가 열리던 누락 조건을 보완했다. 실제 현지 관측이 신선한 혼합 파일/타함 재관측/좌표 검색 발사를 보존한다. 외부 보고가 현지 관측 시각을 갱신하지 않는다. 기존 SAM/FLEET 제한과 Hawklink 전용 트랙의 Link16 비공유를 유지한다.
- generic 표적의 누락된 profileId가 기본 표적함 RCS로 바뀌던 기존 조건 누락을 수정했다. 기존 크기 envelope를 복원하고 명시된 함정/표적 프로파일의 S/X/IJ 특성은 보존했다.
- AIR 기체별 IFF/레이더·링크·최근 전송 수, 지도 선택 헬기 수상 수평선, 3D SENSORS HELO RADAR를 추가했다. 기존 출격·경로·추종·고도·CAMERA와 read-only 렌더/공유 자산을 유지한다. D1 저장은 새 설정만 보존하고 센서/링크 이력을 비운다.

## 최종 검증

**414/414 PASS / 9 suites**, 모두 위 최종 HTML SHA에 연결된다. 각 단계의 과거 검사 수를 다시 합산하지 않는다.

| 검사 | 통과 |
|---|---:|
| static | 54/54 |
| stage_a | 39/39 |
| stage_b | 54/54 |
| stage_c | 42/42 |
| transport | 32/32 |
| codec | 29/29 |
| ui | 92/92 |
| visual | 16/16 |
| regression | 56/56 |

- 기존 DDG/CG ×대기·8Kh32 AUTO·피격6쌍: 기존 물리/전투/global RNG 및 observer/private SPY·SPQ·NAV RNG/트랙·이력·기존 port queue/counter 일치. 새 항공 설정·H1/H2 무선 설정·완료 기능 metadata와 profiler만 명시적으로 정규화한다.
- 실제 헬기2기의 센서·IFF·Hawklink가 동작하는16,000tick을1/8/16/64배속으로 비교한다. 비행 상태와 private radar/IFF RNG, 익명 batch, observer/offboard/global RNG까지 비교하며 센서/전송이 실제 실행됐는지도 확인한다.
- 실제 브라우저/native Three·SwiftShader, desktop1000×760와 touch390×844 viewport 검사다. 실제 휴대폰/hardware FPS 검증은 아니다. 운송 단위 검사는 실제 포트 추출+제어된 모함 fixture이며 native C의 실제 비행/전송 검증과 별도로 집계한다.
- 센서 피탐 등록은 실제 헬기 피해/격추 구현을 뜻하지 않는다. 공중 탐색/FLIR/ISAR/ESM/소나/Link16 확장/무장/연료/회수/로터 공력은 후속이다.

HTML 증가는 HELI_C 대비 **17,416bytes (+0.10857%)**다. 원본 헬기 payload223,419bytes/geometry77/material12 공유와 embedded assets0–12를 유지한다.

이전 C HTML/상태/SHA/workflow는 `archive/v48/WIP_HELI_C/`에 같은 bytes/blob으로 보존한다. stable와 과거 자산/source/evidence는 유지한다. §7.1 전체 원본 직접 업로드·독립 GitHub blob readback을 수행한다. [원격 확인](docs/helicopter/E/remote-publication.json)은 업로드 뒤 기록한다. main/선행 branch 병합·새 PR·Actions dispatch는 실행하지 않으며 `.github/workflows/helicopter-d.yml`은 수동 준비다.
