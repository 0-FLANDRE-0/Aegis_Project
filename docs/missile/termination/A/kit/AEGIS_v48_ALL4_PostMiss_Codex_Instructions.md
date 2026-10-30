# AEGIS SIM v48 — 누적 Dynamic B4 ALL4 + Game Flight Termination / Battery 패치

**상태:** 실험용 소스 수정 + 독립 로직 스모크 테스트 PASS. **전체 게임에서 실제 발사/교전 회귀시험까지 통과한 안정판은 아님.**  
**목적:** 미사일 유도·물리 밸런스 변경이 아니라, 게임 내부 센서 관측 정보에 근거한 비행 종료와 배터리 수명 명칭 및 시험값의 분리. Kappa TGO 90초 로직은 변경하지 않음.

## 누적 범위 — 반드시 한 세트로 적용

1. **Dynamic B4 (ALL4)**: SM-2MR, ESSM Block 2, SM-2ER, SM-6의 로프팅 목표고도 재평가 및 단계별 점진 변경. MR·ESSM의 기존 시험용 상한 완화 포함. 기존 ALL4 패치의 코드와 수치는 유지.
2. **Flight Termination**: ARH의 온보드 RF 추정 트랙 또는 SARH 수신기의 RF 추정 트랙에서 얻은 마지막 유효 교차 예상 시간을 별도 보존. 예상 교차를 2.5초 이상 지났고, 유효 신호가 2.5초 이상 소실됐으며, 신관 폭발 결과가 없으면 게임 자폭/비행 종료 처리. ARH는 활성화 후 12초 동안 한 번도 트랙을 잡지 못한 경우 별도 종료 판정.
3. **Battery**: 기존 `maxLife`를 비행 전원 지속시간으로 해석해 `BATTERY_EXHAUSTED` 사유로 종료. `_gameBatteryRemainingS` 진단 필드 제공. SM-6만 프로필 `maxFlightTimeS` **450→480초**(시험용)로 변경. MR 380초, ER 430초, ESSM 185초 유지.
4. `window.AEGIS_GAME_TERMINATION_ENABLED=false`로 **새 종말 비명중 종료만** 임시 비활성화 가능. 배터리 수명은 계속 적용됨. 이 스위치는 A/B 진단용.

## 비치트 원칙

종료 판단이 사용하는 값:
- `m._arhRfSeeker` / `m._sarhRfSeeker`의 추적 상태, 유효성, 마지막 신호 갱신 나이, 신뢰도
- 해당 필터의 추정 `posM`, `velMps`와 미사일 자신의 INS 항법 상태
- 신관이 실제로 작동했는지 나타내는 `m.proxDetonated` (결과 이벤트만)

**종료 판단에 절대 사용 금지:** `truthObjectForTrackV27`, `navalFuzeTargetD`, `killTarget`, `targetPool`, `missedTarget`, `afterClosestTimer`, `proxMissDistKm`, 실제 표적 좌표/속도. 해당 값은 기존 물리·신관 판정 또는 디버그에 남아 있어도 새 종료 판단의 입력으로 넘기면 안 됨.

**TGO 주의:** 별도 교차 시점은 마지막 유효 시커/수신기 추적과 상대 운동으로 계산하며, Kappa의 유도용 상한 90초를 사용하지 않음. Kappa 자체를 이번 패치에서 수정하지 않음.

## 적용 파일

| 파일 | 용도 |
|---|---|
| `AEGIS_B4_ALL4_Termination_apply.mjs` | 누적 패치 적용 CLI. v48 원본·MR/ESSM만 적용본·ALL4 적용본·패치 완료본을 구분. 실패 시 원본 변경 없이 중단 |
| `AEGIS_B4_Dynamic_Loft_v48_port.js` | MR/ESSM 동적 로프팅 변환 모듈 |
| `AEGIS_B4_ALL4_source_patch.js` | ER/SM-6 로프팅 확대 모듈 |
| `AEGIS_PostMiss_Battery_source_patch.js` | 이번 종료/배터리 변환 모듈 |
| `AEGIS_B4_ALL4_to_Termination_v48.patch` | 직전 ALL4 대비 JS 변경점 |
| `AEGIS_v48_B4_ALL4_Termination_Test_Results.json` | 종료 로직 테스트 결과 |

`.mjs`는 Node.js로 실행하는 **이식 프로그램**, `.js`는 이식 프로그램이 읽어 쓰는 **변경 코드**임. 실행 파일은 총 4개를 같은 폴더에 둔다.

```bash
# Node.js 18 이상
node AEGIS_B4_ALL4_Termination_apply.mjs --input Aegis_SIM_v48_WIP_UI_A1.html --output AEGIS_v48_ALL4_TERM.html

# 기존 ALL4 작업본이라면: 로프팅은 건드리지 않고 종료/배터리 부분만 추가
node AEGIS_B4_ALL4_Termination_apply.mjs --input AEGIS_SIM_v48_B4_Dynamic_ALL4_GAME_TEST.html --output AEGIS_v48_ALL4_TERM.html

# 적용 가능성 사전 확인
node AEGIS_B4_ALL4_Termination_apply.mjs --input Aegis_SIM_v48_WIP_UI_A1.html --dry-run
```

- 입력 파일을 **절대 덮어쓰지 않음**. 출력 파일이 이미 있으면 실패함.
- 현재 소스가 다른 버전이면 무리한 자동 매칭을 하지 말고 `.patch`와 소스 변환 코드를 참고해 *수동 이식*하고 별도 QA.
- **구식 `AEGIS_SIM_v48_B4_ALL4_PostMiss_GAME_TEST.html` 자폭 실험본은 실제 표적 위치 의존 문제 때문에 폐기 대상**. 이번 누적 패치에 추가하지 말 것.
- 기존 사거리 시험/궤적 결과는 변경 전 버전으로 보존하고, **이 누적 변경 이후 측정을 다시 수행**할 것.

## 실제 확인한 사항

- Node.js `--check` (변환 모듈, 누적 CLI, 최종 unpacked JS): PASS.
- **4개 시작점**에서 round-trip 확인: 원본 v48 / MR·ESSM만 패치된 HTML / ALL4 HTML / 이미 종료 패치가 적용된 HTML → 결과의 `c55-game-main` SHA-256이 모두 일치 (마지막은 중복 적용 없음): PASS.
- 종료 함수 실험: 추적하다 소실, 예상 교차 뒤 비명중, 재획득 중단 방지, 시커 미획득, SARH 경로, 신관 폭발 이벤트, A/B 토글, 비치트 정적 검사: **9/9 PASS** (내부 세부 픽스처 6/6).
- 이 테스트는 **합성된 시커 관측 상태를 게임에 사용된 실제 종료 함수로 주입한 함수·연결부 스모크 테스트**임. **전체 18MB 게임 브라우저 부팅, 실제 3D 비행, 물리 신관/요격 비행 결과를 회귀 검증한 것은 아님**. 여기서 브라우저 직접 로드가 제한돼 end-to-end 확인 불가.

## Codex 작업 지시 / 필수 회귀 테스트

1. Codex가 작업 중인 소스의 현재 변경 상태를 먼저 저장하고, 기존 B4 ALL4 적용 여부 및 중복 함수 정의(2개)를 확인한다.
2. 이번 패치가 MR·ER·SM-6·ESSM 네 종류에 누적 적용되었는지 확인한다. 기존 물리, 시커, 신관 처리, Kappa TGO를 변경하지 않는다.
3. **게임 전체 브라우저 실행** 후 정상 표적에 대한 실제 발사·요격을 비교한다. SM-2MR·SM-2ER·SM-6·ESSM별로 저/중/고고도, 중거리와 장거리 각 5발 이상, 같은 시드 및 같은 장면으로 실행한다.
4. **강제 비명중 A:** ARH가 실제 추적을 형성한 후 테스트 표적을 사라지게 하거나 유효 시커 에코를 차단한다. `predictedCrossS`, `lastGoodS`, RF 모드와 `TERMINAL_MISS_POST_CROSS` 종료 기록이 합치하는지 본다.
5. **강제 비명중 B:** 시커가 활성화됐으나 한 번도 표적을 획득하지 못하도록 테스트하고 `TERMINAL_SEARCH_NO_ACQUISITION`가 조건대로 발생하는지 본다.
6. **재획득 / 정상 신관:** 일시적 트랙 소실 후 재획득한 경우 조기 종료 금지. 근접신관이 정상 작동하거나 명중한 경우 새 종료기가 그 결과를 가로채지 않는지 확인한다.
7. **배터리:** SM-6이 450초를 지나도 정상 비행을 유지할 수 있지만 480초를 넘으면 `BATTERY_EXHAUSTED`로 종료되는지 확인한다. 다른 3종은 기존 수명 유지.
8. 종료기가 탐지되지 않은 실제 표적 좌표를 읽지 않는지 코드 검사. 물리적 신관의 실제 충돌거리 계산과 종료 판단을 혼동하지 않을 것.
9. **정상 교전 조기 종료 건수가 0**인지 확인 후 정식 반영. 실패 시 어떤 유도·추적/신관 이벤트가 판단에 영향을 주었는지 로그 첨부. 테스트 실패를 숨기지 않는다.

## 기술적 한계 / 유의

- '자폭'은 우선 게임 엔티티를 `m.dead=true`로 종료하는 의미. **새로운 물리 폭발 이펙트나 파편 피해를 생성하지 않음**. 원래 신관의 폭발과 별개임.
- SARH는 RF 지원이 사라져도 계속 비행할 수 있으므로, ARH의 '12초 미획득' 규칙을 SARH에 복사하지 않음.
- `gameFlightTerminationEvaluateV48`는 완전한 최적화 함수가 아니라 추적 기반 게임 종말 종료 로직. 2.5초 / 12초는 **게임 조정값**이므로 정식 적용 전 교전 사례로 검증.
- 배터리 480초는 공개된 실물 미사일 전원 수명이 아니라 **게임 실험값**.
- 페이지 실행/성능/시커-근접신관 간 이벤트 타이밍은 실제 브라우저 회귀가 필요. **통과하지 않았다면 안정 빌드로 선언하지 말 것.**
