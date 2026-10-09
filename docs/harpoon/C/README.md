# Harpoon C — INS·독립 ARH·무DL CIC

최신 파일 `Aegis_SIM_v48_WIP_HARPOON_C.html`, 15,281,856 bytes, SHA `b3b4f637fdfe0973e3aec566f1577401055c44235d8ccef22084aeb6e04175e7`, main SHA `6bf7962f50dba000c58f8abc937f302b357511bdb5258113c98472e399ce72a2`. B는 같은 bytes로 archive에 보존했고 현재 업로드 대상은 C 하나다. 원격 HTML/support/PR/CI/병합은 아직 실행하지 않았다.

## 원인과 수정

B의 `harpoonDrawCicA`는 물리 위치·heading·시커 lock/beam을 CIC에 직접 표시했고 발사 패널은 실제 phase·speed·생존 여부, impact notify는 명중을 전달했다. RGM-84D에 DL이 없으므로 이 정보는 함정에 전달할 수 없다. 또한 기존 CIC는 identity와 무관하게 ASM을 적색으로 그렸다.

이 직접 경로를 제거했다. 실제 하푼은 기존 RF registry에 그대로 남아 RCS·LOS·beam·거리·잡음 조건에 따라 탐지된다. 함정은 발사 acknowledgement/등록 관 좌표·축·자함 운동·입력 임무와 익명 레이더 관측의 EKF 위치·속도·시각·공분산만 사용한다. 물리 owner ID, 원본 source ID, 미사일 현재 INS·시커·생존·명중 결과를 연관에 사용하지 않는다.

발사 전 이미 존재한 파일과 inbound/corridor 밖/오래된 새 파일을 배제하고, release 뒤 12초 내 최초 출항 corridor 및 반복 관측 연속성으로 연관한다. 3개 측정과 0.15초 span이 필요하며 유사 후보 여러 개는 UNKNOWN/보류로 둔다. 확인한 파일은 FRIEND/사격 보류, 심벌은 청록색이다. 미확정 ASM은 황색이며 HOSTILE/ASSUMED_HOSTILE만 적색이다. 기존 다른 아군도 identity 색을 따른다. 이 숫자와 corridor는 SIM-TUNE이며 겹치는 궤적을 신분 보장 없이 구분하는 IFF가 아니다. 새 alias에 옛 아군 식별을 무조건 복사하지 않는다.

발사 패널은 `Hn · NO DL · 미관측/RADAR T…/ESTIMATE T…`만 표시한다. 위치가 없으면 launch 기록만 남긴다. 관측이 끊기면 마지막 관측의 extrapolation/증가하는 covariance를 EST/MEM으로 표시하며 ship knowledge 위치 제공은 4초 뒤 중단한다. 기존 canonical track의 MEM은 측정 불확실성과 lifecycle에 따라 잠깐 남을 수 있으며 실제 탄체 위치를 갱신하지 않는다. 명중·시커 상태·모터 phase·실제 속도는 발사 패널에 알려주지 않는다.

3D 외부 카메라는 시뮬레이터 관찰자 시점이다. Harpoon follow status에 `OBSERVER / NO DL`을 표시한다. 실제 외형·beam을 볼 수 있지만 그 정보가 CIC/교전으로 돌아가지 않는다. Harpoon follow의 AUX CIC는 자함 중심의 관측 파일만 표시하고 `OWN SHIP · NO DL`로 구분한다. 기존 RAM/SAM 링크 정책을 이 단계에서 바꾸지 않았다.

## INS와 시커

발사 시 관측 target 위치·속도·공분산을 깊은 복사/동결하며 이후 함상 track 삭제·갱신이 유도 입력을 바꾸지 않는다. 현재 시각까지 예측된 함상 KF의 release epoch와 마지막 measurement age를 구분한다. 현재 KF에는 measurement age를 다시 더하지 않으며, 시각이 따로 지정된 관측 fixture만 그 state age를 전파한다. INS는 발사 위치/초기 운동으로 정렬한 뒤, 물리 센서 boundary가 합성한 gravity-compensated delta-v/gyro increment에 센서 bias를 적용해 자체 속도·자세·위치를 적분한다. 실제 현재 속도/절대 위치를 매 틱 navigator에 덮어쓰지 않는다. radar altimeter의 측정 AGL로 고도를 제어하며 GPS·표적 truth·DL 보정을 넣지 않는다. 완전한 strapdown/하드웨어 오차 모델은 아니고 기존 점질량 모델의 SIM-TUNE 관성 센서 추상화다. 결정적 100초 직진 fixture의 위치오차는 약 9.617m였으며 실장비 항법 성능 인증값이 아니다.

ARH는 OFF → SEARCH → ACQUIRE → TRACK, 무응답 때 COAST → SEARCH다. SEARCH는 예상 표적 basket의 cue를 중심으로 좌우 선형 스캔·끝점 반전한다. ACQUIRE는 좁은 후보로 반복 관측을 확인하며 아직 종말 guidance lock을 주지 않는다. 3개 상관 return으로 TRACK, 일시 상실은 최대 4초 COAST, 후보 단발은 0.35초 gap 뒤 폐기한다. 이후 다시 탐색·획득한다. 실제 beam 밖/양 축 gimbal 밖/거리 밖/SNR 부족/Doppler·surface extent·basket 불일치 관측은 획득/추적 모두 거부한다. 익명 range/bearing/elevation/Doppler/extent만 tracker로 넘기며 실제 표적 ID로 강제 명중시키지 않는다.

방위 gimbal ±45°, 고각 ±30°, 방위/고각 beam 16°/20°, scan 30°/s, slew 상한 90°/s, 최소 search sector ±12°·불확실성에 따른 확대, 활성 cue 14km/최대 관측 18km·0.1초 dwell은 모두 **SIM-TUNE**이다. 공개 자료는 INS/능동 RF architecture를 뒷받침하지만 이 시커 수치와 하드웨어 mode 명칭을 확정하지 못했다. [기존 공개 근거](../A/SOURCES.md)를 유지한다.

B의 3.2초/평균48kN 부스터·mass schedule·분리·공통 피해·모델·nozzle·화염·heavy smoke·관 cut/법선은 그대로다. renderer/원본 ship·Harpoon assets는 exact 보존했고 허용 source delta를 되돌리면 B main과 byte 동일이다. CG revision `BUNKERHILL_HARPOON_C_1`, module `HARPOON_C1`; inventory schema A1와 A/B/G/D 저장 호환을 유지한다. launch knowledge·flight는 combat transient로 snapshot 복원하지 않는다.

## 직접 검증

같은 candidate bytes의 직접 155/155 PASS. B133/A155/K284를 합산하지 않는다. raw evidence의 입력명 `candidate-epoch.html`은 최종 명명본과 bytes 동일하므로 역사명을 바꾸지 않았다.

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

core/page/console 및 native simulation/presentation fault 0. runtime는 실제 1·8·16·64× accumulator 결과 exact와 A/B bank 이동 표적 접촉·ARH/INS 독립·save rejection/복원을 검사한다. knowledge는 실제 ship-radar front end/트랙과 실제 CIC canvas paint·EMCON/no-radar·명중 telemetry 부재를 검사한다. guidance는 최종 embedded 함수를 분리 실행해 gimbal/beam/range·스캔·상실/재획득·INS 오차·진실 위치 jump 비보정을 검사한다. native는 실제 모바일 입력/전체 frame clock/RAF·3.2초 분리/ARH·친군 관측/CIC·3D observer 구분·RESET을 검사하고 physics/geometry queue를 수동 진행하지 않는다. SwiftShader이며 사용자 GPU FPS를 주장하지 않는다.

B의 전체 36 native geometry/연기 검사와 CG30/DDG14는 C에서 전부 재실행하지 않았다. 이번 C native 범위·원본 렌더러/asset parity와 runtime DDG core/작전 회귀를 분리해서 해석한다. 제한 corridor/연관과 seeker 숫자는 SIM-TUNE이고 최대사거리 비행·offboard·다함전·헬리콥터는 이 단계의 검증 범위가 아니다.

## 재현과 GitHub 인계

```sh
python docs/harpoon/A/build.py --out artifacts/baseline-A.html
python docs/harpoon/B/build.py --baseline artifacts/baseline-A.html --out artifacts/baseline-B.html
python docs/harpoon/C/verify_static.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/static --baseline artifacts/baseline-B.html
python docs/harpoon/C/verify_guidance.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/guidance
python docs/harpoon/A/verify_runtime.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/runtime
python docs/harpoon/B/verify_stage.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/stage
python docs/harpoon/A/verify_salvo.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/salvo
python docs/harpoon/C/verify_knowledge.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/knowledge
python docs/harpoon/C/verify_native.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/native
python docs/harpoon/C/verify_salvo_identity.py Aegis_SIM_v48_WIP_HARPOON_C.html artifacts/salvo_identity
```

`core.js/profile.js`가 builder의 canonical module다. `navigation.js/seeker.js/knowledge.js`는 그 embedded authoring fragment이며 static으로 동일함을 검사한다. 요구 환경 Python3.12·Node22·numpy2.3.5·Playwright1.62.0/Chromium. `AEGIS_CHROMIUM_EXECUTABLE`로 browser 경로를 지정할 수 있다. native stage wait 최대240초는 소프트웨어 renderer의 벽시계 한계다.

최신 C HTML 하나만 준비 branch `harpoon-block1c-a` 루트에 사용자가 업로드 → exact SHA/bytes/parent 확인 → 작은 지원·문서·현재 checksum/C workflow·기존 K blob archive 반영 → PR/CI 순서다. 기존 A/B archive HTML은 remote에 없고 새 대형 upload 대상이 아니다. CI는 K+작은 A/B 모듈에서 exact 비교본을 재생성한다. 이전 B workflow/manifest는 역사 보존하고 현재 C 지원 manifest를 검사한다.
