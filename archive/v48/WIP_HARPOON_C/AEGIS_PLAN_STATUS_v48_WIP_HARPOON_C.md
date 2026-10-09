# v48 WIP HARPOON C — 로컬 검증 완료

- HTML `Aegis_SIM_v48_WIP_HARPOON_C.html`, **15,281,856 bytes**, SHA-256 `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`.
- main SHA `6bf7962f50dba000c58f8abc937f302b357511bdb5258113c98472e399ce72a2`, 기준 B `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`.
- main/준비 `harpoon-block1c-a`는 K commit `f51247496725aa8aadad69d5c8d3449c5bbc3a81`; 권한 재확인. 새 remote HTML/support/PR/CI/병합은 미실행이다.

INS·ARH 유도와 함정의 정보 경계를 수정했다. CIC의 실제 탄체 위치/시커 beam·발사 패널 phase/speed/survival·명중 notify를 제거했다. 하푼은 물리 RF 반사체로 유지하며 실제 익명 레이더 file을 발사 기록/관측 궤적/공분산으로 연관한다. 확인하면 FRIEND/청록/사격 보류, 모호하면 UNKNOWN/보류다. ASM 분류만으로 적색을 주지 않는다. 레이더 관측이 끊기면 EST/MEM·공분산을 사용하고 ship knowledge의 위치 제공은 4초 뒤 중단한다. 발사기록은 실제 탄체 생존·명중과 무관하게 남는다. DL·IFF나 원본 owner-ID shortcut을 만들지 않는다.

INS는 발사 당시 현재 KF estimate를 명시 release epoch로 동결하며 이미 예측된 상태에 measurement age를 두 번 더하지 않는다. 이후 자체 IMU delta-v·gyro 적분/센서 bias·측정 radar AGL로 비행한다. 실제 절대 위치/속도를 항법 상태로 덮어쓰지 않는다. 실제 함상 track 삭제·갱신·물리 위치 jump가 navigator를 임의 보정하지 않는다. 100초 결정적 IMU fixture 오차 약9.617m는 SIM-TUNE 값이다.

ARH의 SEARCH 좌우 선형 sweep/끝점 반전, ACQUIRE 반복 확인, TRACK, COAST/SEARCH 재획득을 분리했다. 3회 측정/0.35초 candidate gap/4초 coast, ±45° 방위·±30° 고각 gimbal, 16°/20° beam·30°/s scan·90°/s slew·14km 활성/18km 관측·0.1초 dwell은 공개 확인되지 않은 SIM-TUNE이다. 양 축 기계 범위·beam·거리·SNR·Doppler·표면 extent/basket gates가 실제 획득과 추적 판정에 적용된다. 표적 truth ID를 전달하거나 강제 명중시키지 않는다.

3D 외부 follow는 명시 `OBSERVER / NO DL`이고 Harpoon AUX CIC는 자함 중심·관측 file만 그린다. 관찰자 physics/beam 정보는 ship display/교전으로 돌아가지 않는다. B의 3.2초48kN boost·모델/nozzle·heavy smoke·빈 관/법선·기존 공통 피해와 DDG 미설치를 보존한다. CG revision C_1/module C1, 관 schema A1와 A/B/G/D 작전 저장 호환; launch knowledge/flight는 저장 복원하지 않는다.

## 직접 검증

동일 candidate bytes의 **155/155 PASS**, seed `0x6d2b79f5`. 과거 A155/B133/K284는 합산하지 않았다. 원자료 입력명 candidate-epoch.html은 전달본과 byte 동일이다.

| Suite | 통과 |
|---|---:|
| static | 32/32 |
| guidance | 33/33 |
| knowledge | 20/20 |
| runtime | 29/29 |
| stage | 11/11 |
| salvo | 9/9 |
| native | 16/16 |
| salvo_identity | 5/5 |

1·8·16·64× full accumulator 결과 exact, core/page/native console·simulation/presentation fault 0. 실제 레이더 plot→FRIEND file→CIC 청록 paint, EMCON에서 EST/위치 만료, radar OFF 중 독립 ARH·비관측 명중 telemetry 부재를 확인했다. native는 실제 ARM/VLS click·frame clock/RAF·모델·3.2초 분리·ARH·observer/CIC·RESET을 검사했고 수동 physics/geometry queue 진행 0이다. Chromium SwiftShader이므로 사용자 FPS 인증이 아니다. 내장16건과 개별 suite에서의 호출은 distinct suite 결과에 포함되며 추가 합산하지 않는다.

B36 전체 geometry/연기 native·CG30/DDG14 전체를 C에서 다시 실행했다고 주장하지 않는다. C renderer/asset exact parity와 runtime DDG core/ops 및 C 전용 native 범위를 근거로 구분한다. 표적함/다함전·헬리콥터·외부 표적 정보·경유점/최대사거리 인증은 미구현/미검증 후속 범위다.

[코드·원인·SIM-TUNE·재현](docs/harpoon/C/README.md), [직접 집계](docs/harpoon/C/evidence/verification-summary.json), [GitHub 인계](docs/harpoon/C/GITHUB_HANDOFF.md)를 따른다. B HTML/status/SHA는 `archive/v48/WIP_HARPOON_B/`에 같은 bytes 보존하고 workflow는 docs/harpoon/B/workflow-b.yml에 역사 보존했다. A/B 대형 HTML은 remote에 없으므로 새 API/Git upload하지 않으며 기존 K blob+작은 모듈로 exact 재생성한다.

지침7.1에 따라 **최신 C HTML 하나만** 사용자가 기존 branch 루트에 업로드한 뒤 SHA/bytes/parent 대조 → 작은 support/문서/checksum/C workflow·K blob archive → 새 PR/CI를 진행한다. 자동 main 병합/정식 승격은 이 단계에서 실행하지 않는다.
