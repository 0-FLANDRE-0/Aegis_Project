# AEGIS v48 — Kappa 종말 수평방향 역전 수정 / Codex 이식 지시서

## 0. 작업 기준과 원칙

- **기준:** GitHub `0-FLANDRE-0/Aegis_Project`, `range-loft-recovery-a` 브랜치의 최신 커밋을 읽고 별도의 시험 브랜치를 만든다. 기존 브랜치 및 `main`은 직접 수정하거나 병합하지 않는다.
- 현재 후보가 유지하는 설정: `SM-2ER fullLoftKm=240`, `SM-6 fullLoftKm=260`; 게임 설계 목표 `rangeGoalKm=360/450`, `nominalRmaxKm/maxRmaxKm=360/360 및 450/450` 유지.
- **이번 변경 범위는 `_wip79KappaPipState(m, targetState)`의 종말 속도 목표 수평 방향 계산 하나뿐.** 추진, 항력, 질량, 연소, B4 상태/고도, 최대 배터리 수명, Kappa TGO 90초, 시커, 신관, 피해 판정, 해면 충돌 판정, UI 등은 고치지 않는다.
- 실제 표적 오브젝트/월드의 숨겨진 좌표·속도를 유도에 새로 주입하지 않는다. 함수에 이미 전달된 **관측 기반** `targetState`와 이 함수가 만든 `pip`만 사용한다.
- 본 작업은 SIM_TUNED **게임 로직 디버깅**이다. 실제 무기 성능 수치/실물 운용 파라미터와 대조하거나 보정하지 않는다.

## 1. 확인된 버그와 최소 변경

현재 `_wip79KappaPipState`는 관측 기반 예상 요격점 `pip`을 만들고 `dx=pip.x-mPos.x`, `dy=pip.y-mPos.y`를 계산한 뒤, 최종 수평 방향 `(hx, hy)`를 `-targetState.velMps.x/y`로 선정한다.

이탈 표적에서는 *표적 진행 방향의 반대*가 최종 수평 속도 방향이 되며, B4의 `CLIMB/CRUISE → DIVE` 종말 경유점 해제 시 `vFinal.x`가 갑자기 부호를 바꾸는 사례가 확인됐다. 과도한 하강 → 목표 고도 아래 진입 → 늦은 상승 및 `SEA_IMPACT`와 관련된 현상이다.

**진단에서 시험한 최소 수정:** 해당 수평 방향 벡터를 관측 기반 PIP까지의 수평 LOS `(dx,dy)`로 변경하고 기존 정규화, `gammaF`, `vFinal`, B4 로직, TGO, 나머지 Kappa 제어 계산은 보존한다.

```diff
-    // First experimental terminal-vector policy: level, head-on horizontal direction.
-    // This matches the ADD sea-skimmer geometry (gamma_f≈0) and keeps the high-diver adaptation minimal.
-    let hx=-targetState.velMps.x,hy=-targetState.velMps.y;
-    let hm=Math.hypot(hx,hy);
-    if(hm<1){hx=dx;hy=dy;hm=Math.max(1,Math.hypot(hx,hy));}
+    // Game terminal-vector heading follows the observed/estimated PIP LOS.
+    // Do not automatically reverse a retreating/crossing target's heading.
+    let hx=dx,hy=dy;
+    let hm=Math.max(1,Math.hypot(hx,hy));
     hx/=hm;hy/=hm;
```

동봉 `AEGIS_KAPPA_PIP_LOS_Source_Patch.mjs`는 이 블록만 exact-match로 교체한다. 원본 HTML의 **압축된 실행 JS를 추출하는 기능은 있지만**, 결과를 임의로 다시 HTML에 꽂지는 않는다. 빌드/진단 캡슐 생성 및 인덱스 해시는 저장소 빌드 절차로 다시 생성한다. **내장 진단 코드가 예전 함수인 상태에서 최신 결과라고 주장하지 말 것.**

## 2. 우선 소규모 회귀시험만 실시

공통: 게임 native 비행/유도·신관, RNG `1831565813`, fixed dt `1/60s`, 동일 표적 운동·진단 조건. `CURRENT`와 `PATCHED`를 쌍으로 2회 실행한다. 가능하면 실게임 월드·진단 입력의 동등성도 확인한다. 전부 500km 상한 탐색 **금지**.

**해면 충돌 재현 4건** (기존 `SEA_IMPACT`; 이전 분리 진단에서는 패치 후 `INTERCEPT_SUCCESS`로 변함):

| 무장 | 최초거리 | 고도 | 표적 운동 |
|---|---:|---:|---|
| SM-2MR | 16km | 30m | 이탈 250m/s |
| SM-2ER | 25km | 30m | 이탈 250m/s |
| SM-6 | 25km | 30m | 이탈 250m/s |
| SM-2ER | 60km | 1000m | 이탈 150m/s |

**성공 유지 대조군 최소 6건**:

- SM-2ER 60km/1km **정지**, **접근 300m/s**
- SM-6 60km/1km **이탈 150m/s** (이전 진단에서 성공)
- SM-2ER 150km/5km **정지**
- SM-6 150km/10km **정지**
- SM-6 441km/20km **정지** (배터리 480초 경계 확인)

**횡단 확인 최소 4건**: SM-2MR 20km/30m, SM-2ER 20km/30m, SM-6 20km/30m, SM-2ER 40km/200m (횡단 250m/s). 기존 실패가 패치에서 더 나빠지거나 성공이 실패로 바뀌는지 기록한다. 사용자 승인 없이 다른 제어·해면 보호 수치까지 조정하지 않는다.

즉 먼저 **14개 조건 × 변경 전/후 × 2회**만 검사한다. 훨씬 큰 전수검사나 96조합 사거리 재측정은 이후 별도 승인에서 한다.

## 3. 합격/불합격 게이트

1. 네 가지 지정 해면 충돌 조건에서 실제 명중으로 개선되는지 보고. **이 4건의 정상화만으로 모든 해면 충돌이 해결됐다고 주장하지 않는다.**
2. 기존 성공 대조군에서 성공→실패 **0건**. 특히 높은 표적, 접근 표적, `DIRECT` 및 `B4 DIVE` 전환. `TARGET_GAMMA_OPPOSE_H` 같은 비기본 정책이 사용된다면 별도 영향 테스트 또는 적용 범위 제한 후 테스트.
3. 시각별 로그: B4 `phase`, Kappa `policy`, `targetState.source`, 관측 `pip`, `vFinal.x/y/z`, 목표 고도 대비 미사일 고도, 수직속도, `cmdOmegaPit`, 최종 이유(`SEA_IMPACT/INTERCEPT_SUCCESS/LOW_SPEED/BATTERY_EXHAUSTED`), 최근접거리.
4. 새 참조에 전장 실제 표적의 숨겨진 위치·속도가 들어가지 않음. 신관 물리 판정 코드는 변경 없음.
5. 실행 함수 중 의도한 `_wip79KappaPipState`의 해당 블록과 정확히 필요한 진단 복사본·메타데이터 외 변경 **0**. 이전 ENV_C/RECOVERY_A 진단 해시 및 성능표는 **오래된 판정으로 표시**하고, 새 코드에 맞는 재생성·검증을 수행한다. 새 대규모 사거리 숫자를 추정해 기입하지 않는다.

## 4. 산출물

- 새 시험 브랜치 이름, 기준 SHA, 새 SHA
- 수정 전/후 diff (로프팅/유도/신관/배터리 외 다른 변화가 없어야 함)
- 실제 실행 가능한 게임 HTML 시험본 및 재생성한 진단 캡슐의 유효성 검사 결과
- 14조건 A/B 결과 CSV와 각 중요한 고도–수평거리/시간, 속력, `vFinal` 비교 그래프
- 통과/퇴행 사례와 재현 명령

실패가 있으면 다른 설정을 자동 변경하지 말고 그 한 조건의 시계열과 원인을 보고한다. **PIP-LOS가 선택된 몇 가지 사례를 개선한 것은 강한 근거지만, 모든 기동·접근 표적에 대한 안정성 보증은 아니다.**
