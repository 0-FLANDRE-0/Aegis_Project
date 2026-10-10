# v48 WIP MULTI SHIP C — 4단계 완료

- HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_C.html`, **15,344,725 bytes**.
- HTML SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`, decoded main SHA `d68eca1dbe2b3b6c491ba4f9d2de9c5ccbcb34221ee7d3f02631fd897925094e`.
- 기준 B head `ae94326caea7cd0329233f381933cdc240bedb47`, B HTML SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`.
- 변경은 packed main record13과 build label이다. asset records0~12·원본 함정/무장 모델·profile/module revision·stable v48을 보존한다.

## 이번 동작

실제 배치 함정의 SPY·SPQ·NAV가 독립 observer state/난수/scan/rotor/track을 실행한다. 자함은 기존 canonical scheduler/TrackStore를 유지한다. 공통 RF echo·해면 clutter·익명 측정·EKF에 명시 receiver를 사용하며 함종 면 배치/profile budget·CG 원본 사각·지형/지평선·EMCON/손상·coast/reacquire를 적용한다. 자함 CIC는 자함 센서의 익명 접촉만 표시하며 truth를 바로 복사하지 않는다. 분류와 식별/발사권한을 구분한다.

미래 헬기의 source/sequence/측정시각/추정위치/SPD공분산/domain evidence를 받을 외부 관측 포트를 준비했다. 지연·측정 age·링크 loss·재전송/반복 fix·첫 covariance 중복을 검증한다. 포트는 합성 계약 검사만 있으며 **헬기 모델·비행·실제 센서는 미구현**이다. Harpoon 발사 후 DL=0·INS/ARH와 ship knowledge 경계를 유지한다.

공통 세계1회, 각 observer fixed tick1회, 60/120/20 Hz를 유지한다. renderer는 실제 owner rotor각만 읽고 화면 전환/카메라는 관측·물리를 진행하지 않는다. 정상 reset/import/retire는 combat/외부 링크 transient를 정리하고 잘못된 import는 zero mutation이다. 저장의 deferred에 offboardLinksAndReports를 명시했다.

## 동일 최종 파일 직접 검증

| 검사 | PASS 조건 수 |
|---|---:|
| static | 30/30 |
| observers | 136/136 |
| propagation | 6/6 |
| fleet clock | 40/40 |
| paired baseline | 12/12 |
| native observers | 18/18 |
| physical native | 20/20 |
| departure | 48/48 |
| guidance | 45/45 |
| routes | 26/26 |
| knowledge | 22/22 |
| DDG runtime | 14/14 |
| 합계 | **417/417** |

과거 결과·예비 SHA·timeout 실행은 합산0이다. observerUnit/offboardUnit의 내부 조건은 상위 조건에 포함하여 이중 합산하지 않는다. DDG 입력 SHA는 별도 provenance로 고정한다. core/runtime/presentation/page 오류0이다.

- 네 자함/배치 함종 조합 자연 탐지, truth/plot/tentative/confirmed 계측, independent RNG·EMCON·손상·coast/재획득·detached facade·reset/import를 검사했다.
- 외부 오차/지연/측정 age·링크 loss·truth/replay/future/covariance 거부·반복 fix 확인 방지·Harpoon DL0을 검사했다.
- 60km 수평선 차폐와600m 진단 receiver에서의 물리 반사, 섬 LOS 차이를 검사했다. 실제 헬기나 완벽 OTH cue를 생성한 것으로 세지 않는다.
- 혼합 함종 두 쌍 × 1/8/16/64 × 각1536 full tick에서 물리/관측/RNG exact, common world25.6초·owner tick1536을 확인했다.
- native393×852 실제 RAF/WebGL 자연 접촉·rotor mesh각·원래 버튼 CIC전환/read-only/reset, 원본 class mesh·입출구 actualHole/후속 draw·tick/root disposal을 검사했다. SwiftShader·controlled inert probe이며 실제 hardware FPS 인증은 없다.
- 기본 적함 없음 B↔C 대기/AUTO raid/침수의 물리·RNG exact, 기존 DDG와 Harpoon guidance/routes/knowledge를 재검사했다.

[원본 집계](docs/multiship/C/evidence/verification-summary.json), [측정 조건/역사 CG triangle audit 한계](docs/multiship/C/PERFORMANCE.md), [포트/구조](docs/multiship/C/README.md).

## 원격/다음 범위

B HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_B/`에 같은 bytes/blob으로 보존한다. stable v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`를 유지한다. 현재 workflow/manifest는 C다.

`multiship-sensors-c`는 미병합 B PR#46 위에 연결한다. 지침7.1에 따라 원본 HTML/support 직접 push/readback/CI를 수행하며 A/B/C는 이번 요청에서 병합하지 않는다. 실제 publication과 해당 head CI는 [GitHub 인계](docs/multiship/C/GITHUB_HANDOFF.md) 및 원격 기록을 따른다.

다음은 **5단계 owner 사통·실제 탄 source/target/contact/피해 routing·양방향 무장**이다. 이후 수신기별 EW와 관측 기반 AI를 연결한다. 일반 시커의 새 naval reflector는 실제 routing과 같이 검증하여 켠다. [의존성](docs/multiship/C/DEPENDENCIES.md).
