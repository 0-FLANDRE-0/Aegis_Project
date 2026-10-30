# HELI_F1 — Hawklink 트랙 하푼 OTH 관문·식별 근거·교전 로그

HELI_E1 `69a5e38` 위 `helicopter-harpoon-f1`. [구현 전 대조와 사용자 결정](CONFLICTS.md)을 먼저 따른다. 현재 플레이에서 DDG는 헬기, CG는 하푼만 지원하므로 완전한 라이브 연결은 CG 항공 운용 다음 단계다. 이번 검증의 CG 수신기 재생은 진단이며 새 전단 링크 기능이 아니다.

## 운용

ARM 또는 FLEET에서 수상 트랙을 선택하고 기존 운용자 식별(HOSTILE/훈련 표적)을 지정한다. 자동 발사관 선택은 기존처럼 유지한다. 순수 offboard도 실제 확정 상태/측정 나이≤10초/2σ INS 예측 바스켓/사거리/장비·발사 자세 조건을 통과해야 한다. 자동 발사 권한을 새로 만들지 않는다. 실패한 요청과 준비 단계에서 취소된 요청은 발사 로그를 생성하지 않는다. 실제 발사 직전 다시 검사한다.

DEBUG → **교전 로그**에서 선택한 FLEET 함정의 기록을 열고 전체 선택·복사한다. 최대 64발의 발사 기록에 종료 결과가 붙는다. 시간은 시뮬레이션 초, `predictionSigmaM`은 기존 계산의 2σ 반경이다. `LOCAL/OFFBOARD/MIXED`는 해당 트랙에 보존된 관측 구성 이력이며 freshness는 별도 관문이 검사한다. 발사 시 식별 근거는 그때의 값을 복제한다. 이후 변경이나 새로운 관측이 과거 발사 근거를 바꾸지 않는다.

`LOCAL_SENSOR`는 현지 관측도 있는 트랙의 근거 유형이며 센서만으로 적성 확인했다는 뜻이 아니다. 순수 offboard에 운용자가 지정하면 `OPERATOR_ONLY`; `ISAR`는 enum 자리만 예약한다. 익명 보고는 실제 표적 ID나 truth 참조를 포함하지 않는다.

종료 결과는 `AFTER_ACTION_TRUTH`로 명시한다. 명중 범주는 실제 충돌 대상의 진영/민간 선체 프로파일에서만 구한다. 현존 무인 컨테이너 표적선은 중립 상선 선체 범주에 포함한다(승조원·화물 피해 구현을 뜻하지 않는다). 의도한 트랙이나 운용자의 HOSTILE 지정으로 실제 범주를 덮지 않는다. 해면/지형/연료·수명 종료와 외부 요격 소실도 기록하며 기존 종료 물리와 효과는 변경하지 않는다. 자체 자폭 사유가 발생하면 SELF_DESTRUCT로 기록하지만 새 자폭 장치·효과는 이번에 만들지 않는다.

로그는 함정별 combatSystem이 소유하는 전투 transient다. lifecycle/reset/import 시 비우고 작전 저장에는 포함하지 않는다. 마지막64발보다 오래된 행은 비행 중이어도 빠질 수 있으며 그 행을 종료 때 되살리지 않는다. 로그를 읽는 API는 DEBUG/진단 전용이고 전술·센서·AI·유도는 참조하지 않는다. 공개 진단 `window.__HARPOON_JOURNAL_F1__.snapshot(ownerId?)`는 detached JSON, `.text()`는 복사 가능한 텍스트다. 실시간 전술 명중 보고나 DL이 아니다.

## 변경 경로

- `harpoonGateA`의 active/foreign 두 실행본에서 local blanket denial 제거. 별도의 가짜 허용 함수는 남기지 않는다.
- Harpoon만 shared readiness의 offboard 나이를 사용한다. MIXED에서 오래된 현지 contributor가 신선한 원격 보고를 덮지 않도록 한다. 이미 나이 보정된 공분산에 원격 페널티나 재전파를 더하지 않는다.
- FLEET/foreign 수동 wrapper도 Harpoon의 실제 관문에 freshness 판정을 위임한다. 다른 무장 wrapper의2초 조건은 유지한다. AI capability·local 관측·보호 corridor 조건은 유지한다.
- 운용자 식별 setter(자함/타함), 실제 관측 입력에 근거 필드 추가. 식별 허용 목록과 기존 보호 정책은 유지한다.
- 실제 release 뒤 launch writer, 실제 contact/finish 및 외부 소실/owner retirement 뒤 outcome writer. 기록만 쓰고 교전 판단으로 값을 반환하지 않는다.
- `shortTargetRangeM`, `longSmallTarget*`, `longMediumTarget*` 7개 reference만 `USER_DESIGN_TARGET`으로 수정한다. 수치·튜닝 수식·앵커는 같다. APS_REFS_F는 사용자 감각 목표이며 물리 근거가 아님을 명시한다.

## 재현

Python/Playwright 요건은 `../F/requirements.txt`, Node AST 도구는 `../../performance/F/package-lock.json`을 사용한다. Chromium 실행에 필요한 sandbox/network 실행 권한은 호스트 정책을 따른다.

```sh
python docs/helicopter/H/build.py archive/v48/WIP_HELI_E1/Aegis_SIM_v48_WIP_HELI_E1.html /tmp/HELI_F1.html
python docs/helicopter/H/verify_static.py archive/v48/WIP_HELI_E1/Aegis_SIM_v48_WIP_HELI_E1.html Aegis_SIM_v48_WIP_HELI_F1.html artifacts/static
NODE_PATH=docs/performance/F/node_modules node docs/helicopter/H/verify_policy.cjs /tmp/HELI_F1.main.js artifacts/policy
python docs/helicopter/H/verify_native.py Aegis_SIM_v48_WIP_HELI_F1.html artifacts/native
python docs/helicopter/H/verify_helo.py Aegis_SIM_v48_WIP_HELI_F1.html artifacts/helo
python docs/helicopter/H/verify_mixed.py Aegis_SIM_v48_WIP_HELI_F1.html artifacts/mixed
python docs/helicopter/H/verify_ui_clock.py Aegis_SIM_v48_WIP_HELI_F1.html artifacts/ui-clock
python docs/helicopter/F/verify_regression.py archive/v48/WIP_HELI_E1/Aegis_SIM_v48_WIP_HELI_E1.html Aegis_SIM_v48_WIP_HELI_F1.html artifacts/regression --baseline-only
```

정적 검사가 선행한다. 증거의 최종 통과 수·원본 SHA·조건은 `evidence/verification-summary.json`과 root 상태를 따른다. 과거 E1/E 검사 수를 합산하지 않는다. source/evidence는 이 H에만 추가하며 A–G는 동결한다. stable v48은 그대로다. Actions dispatch/main·이전 브랜치 병합/새 PR 생성은 하지 않는다.
