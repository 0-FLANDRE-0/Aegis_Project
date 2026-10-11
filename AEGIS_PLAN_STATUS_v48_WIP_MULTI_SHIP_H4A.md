# v48 WIP MULTI SHIP H4A — 센서 기반 근접 자위 연결

**판정: 구현·최종 원본 직접 검증 완료.** fresh H4 출항의 CG-52가 낮게 접근하는 하푼에 눌카만 쓰던 방어 연결을 수정했다. 기본 AUTO/레이더 ON 상태에서 독립 CIWS 자위와 측정 기반 채프를 사용한다.

## 원본과 기준

- [HTML](Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html), **15,702,263 bytes**, SHA-256 `3d7ad7dffb7fd060b903cbb150662cfda62a28be66f784fcbb41d4eb26bc985a`.
- decoded main SHA `b9f2ae3e1f53d88df36dab03e52dcde4cdb2ddd9fc8043b6456f732e63948d77`. H4 final `b74a2c733352230a0799446cfdb6730b2bb87421` 위 branch `multiship-defense-h4a`, PR base `multiship-tactical-h4`. 새 병합 요청이 없어 main/선행 PR 병합은 실행하지 않는다.
- H4 HTML/status/SHA/workflow4파일을 동일 bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_H4/`에 보존한다. stable v48/models/assets0~12 및 기존 지원·역사 evidence는 유지한다. pinned17patch/record13만 변경하고 full HTML exact rebuild한다.
- [운용/권한](docs/multiship/H4A/README.md), [조건](docs/multiship/H4A/PERFORMANCE.md), [후속2단계](docs/multiship/H4A/DEPENDENCIES.md), [검증](docs/multiship/H4A/evidence/verification-summary.json), [원격 읽기](docs/multiship/H4A/evidence/remote-publication.json), [체크섬](SHA256SUMS_v48_WIP_MULTI_SHIP_H4A.txt).
- §7.1 승인에 따라 full HTML/support 직접 업로드·독립 GitHub readback한다. Actions dispatch는 실행하지 않고 로컬 최종 원본 검사로 gate를 충족한다. 자동 PR smoke의 계정 제한 실패를 CI PASS로 표시하지 않는다.

## 수정 동작과 범위

기존 CMS 승인 + 자체 RF 확인 경로를 유지하면서 CMS 획득 실패에도 CIWS의 **confirmed fresh local RF·접근 지속·미사일 운동학·자함 통과 경로·품질/구동/사각/전원/탄약 조건**을 통과한 경우 `LOCAL_SELF_DEFENCE_H4A` 권한을 허용한다. 실제 발사에서 동일 owner/mount/pending 객체·sensor file 객체와 fresh/아군·중립/효과 보호/HOLD/EMCON/손상 조건을 다시 확인한다. 일반 명령 포트에 이 권한을 개방하지 않는다. CMS 파일·적성 식별을 만들어 넣거나 원거리 SAM 권한을 확대하지 않는다.

EW는 이 local RF의 거리·접근·오차와 passive ACTIVE_SEEKER 방위를 **유일한 측정 연관**으로 결합해 기존 채프 timing 정책에 전달한다. 같은 mount의 복수 접촉·다대일 연관·여러 emitter는 보류한다. ESM 방위만으로 range/TTC를 추측하지 않고, 기존 reserve/interval/살보 상한/발사 geometry 및 SLQ-32/눌카를 유지한다.

CG에는 양현 20mm Phalanx만 사용한다. DDG 장비·자함 CIWS·레이더 반사/탐색/확률·CMS 분류·하푼 INS/ARH/무DL·탄환/미사일 비행·피해 solver·H4 팀/H3 공격/H2 기동/H1 유틸리티·G network 및 60/120/20Hz를 보존한다. 저장 schema는 H4 그대로이며 pending/local 센서 파일은 기존 transient reset/import/deploy/retire 경계에서 비운다.

## 최종 원본 직접 검증

| suite | PASS |
|---|---:|
| static | 56 |
| team | 88 |
| intent-h4 | 30 |
| ui-h4 | 42 |
| natural-h4 | 17 |
| attack | 195 |
| attack-guards | 20 |
| ui-h3 | 42 |
| surface | 18 |
| clock | 208 |
| maneuver | 132 |
| guards | 44 |
| ui-h2 | 40 |
| natural-h2 | 30 |
| baseline | 30 |
| tactical | 128 |
| policy | 40 |
| ui-h1 | 30 |
| cooperation | 32 |
| harpoon | 26 |
| camera | 16 |
| defense | 76 |
| natural-ew | 22 |
| native | 38 |
| harpoon-defense | 36 |
| closein | 20 |
| clock-defense | 28 |
| **합계** | **1484/1484** |

**27 suites, capture 14개**, page/core/runtime/presentation 오류0. 검사 소스·report·capture 및 testedHTML SHA를 집계에 pin하며 폐기 후보/역사 검사 수치는 합산하지 않는다.

- 자연 하푼: fresh ownCG→defenderCG,8km 관측 뒤 실제 수동 발사. defender incoming file/identity 주입·강제 명중 없음. CMS confirmedASM0에서도 **눌카1·채프4·Phalanx95발**, 실제 포탑 이동·PHALANX DIRECT_BREAKUP·물리 잔해 확인. HOLD는 CIWS0이며 EW는 독립 운용한다. DDG의 기존 ESSM/RAM 경로도 자연 센서로 검사한다.
- 늦은 차단: 자연 획득 pending의 진단 발사 phase를 맞추고 **baseline admitted**를 먼저 확인한다. 아군·stale·unconfirmed·file replacement·cloned/expired capability·HOLD·EMCON 각각 해당 사유로 actual release 차단, 탄약·탄체·로그·RNG 변화0. 순수 측정 연관의 모호성·중복·측정 부재·freshness는 내장11조건을 검사한다.
- 배속: 새 실제 Harpoon/local CIWS/EW의640+2688 full ticks,1/8/16/64배속에서 물리·센서·EW·무장 상태/RNG exact. 중간 분해 효과는 자연 표본에서 별도 확인한다. H4 기존3owner 팀/기동/공격/방어 clock도 최종 원본으로 재실행했다.
- 회귀: H4/H4A no-peer 자함 idle/손상/8Kh32AUTO 물리·combatRNG exact. 기존 팀·기동·공격·공유·자함 Harpoon 아군 보호·defense/EW·mouse/touch·실제 RAF/WebGL 피격/복원/해상효과/root disposal 확인.
- 기존 E close-in fixture는 untouched H4에서도 CG actual-fire assertion이 실패한다. 새 regression wrapper는 EW/기동 OFF에서 native hard-kill mechanics를 격리한다. 기본 동시 대응은 자연 Harpoon 및 natural-ew suite로 별도 검사하며 원래 source/evidence를 바꾸지 않는다.

대표 seed·지형 bypass·CPU/SwiftShader 조건이다. CMS 저공 획득 자체나 보편적 요격률·오격 방지·초수평선 FCS·휴대폰 FPS·실제 doctrine을 완료로 주장하지 않는다. 후속 큰 단계는 **헬기/초수평선 탐지 → RGM-109E Block Va**다.
