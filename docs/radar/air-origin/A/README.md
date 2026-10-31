# AIR_ORIGIN_A

현재 상태는 [사용자 승인 반영 보고서](APPROVAL_REPORT.md)와 [STATUS.json](STATUS.json)을
확인한다. 2026-11-01(KST) 명시 승인으로 **기대값 5건만** 갱신했다.
[승인 기록](approved-expectations.json)에 이전·새 값 전체와 원인 경로/해시가 있다.

- DDG/CG raid의 samePhysicalState / sameExistingObserverState: 4건
- 전투 world120 truth hash: 1건
- 다른 기대값·허용 오차·게임 HTML: 변경 0

게임 Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html은 검토한 파일과 byte 동일하다.
RF 식·계수, KF 이득, clamp, 무장, 저장 스키마는 그대로다. NPC 어댑터와 같은
6개 sensor 필드 계약을 자체 SPY/SPQ AIR에도 적용한 기존 변경만 들어 있다.
측정에 실제 사용한 receiver 값을 전달하며 고정 오프셋이나 truth 보정은 없다.

[승인 전 보고서](REPORT.md), [원점 복구 diff](AIR_ORIGIN_A.diff),
[승인 전 전체 raw 결과](evidence/summary.json)는 그대로 보존한다.
기존 결과의 불일치 5건을 지우거나 통과로 덮어쓰지 않았다.

## 승인 후 재검증

저장소 전체, Python Playwright/시스템 Chromium, Node/Acorn이 필요하다.
보고서 ZIP만으로 공통 하네스가 모두 제공되지는 않는다. 원래 증거를 보존하려면
별도 checkout에서 재현한다. 실행 환경은 TMPDIR=/dev/shm,
PYTHONDONTWRITEBYTECODE=1을 사용했다.

```sh
python docs/radar/air-origin/A/verify_approval.py
python docs/radar/air-origin/A/run_approval_validation.py
python docs/radar/air-origin/A/collect_approval.py
python docs/radar/air-origin/A/report_approval.py
python docs/radar/air-origin/A/package.py
```

run_approval_validation.py는 승인 파일을 명시적으로 전달해 쌍대 42검사와
world120 idle/combat을 새로 실행한다. 새 물리·관측·RNG 값이 검토 당시와
같은지도 비교한다. 나머지 378건은 동일 HTML과 변경 없는 하네스의 기존 결과를
재사용하며, 재실행했다고 표기하지 않는다.

공유 verifier에는 --approved-air-origin-baselines 선택 인자만 추가했다.
인자가 없으면 기존 기대값 경로를 유지한다. 승인 파일은 HTML/main JS 해시가
다르면 거부한다. 정확 비교이며 허용 오차 확대나 검사 제외는 없다.
run_regressions.py로 전체를 다시 실행하면 승인 파일을 후보에만 전달하고
새 raw 결과는 evidence/approval/full-regression/에 별도로 보존한다.
승인 후 자료 수집·보고는 위 collect_approval.py/report_approval.py를 사용한다.
prepare_approval.py는 처음 승인 기록을 동결한 도구이며 기존 기록을 덮어쓰지 않는다.

## 원래 진단과 산출물

무잡음 verify_roundtrip.py, 자연 receiver verify_live_receivers.py,
static.cjs 검증은 승인 전과 같은 게임을 사용한다. 과거 자연 8발/시커28/
CIWS/EW/H3와 원인 로거 자료도 그대로 남아 있다. 두 레이더 원점의 EKF 전달만
복구했고 이번 승인은 게임 코드를 바꾸지 않았다.

HTML ZIP과 보고서 ZIP은 분리한다. GitHub 원격 다운로드 영수증은
자기 해시 순환을 피하려고 산출물 커밋 뒤 별도 커밋에 기록한다.

## 중단 지점

air-origin-a 커밋·push·원격 readback 뒤 멈춘다. 병합은 사용자가 한다.
main 병합·release/tag 생성·gun-b2 rebase는 하지 않는다.
병합 후 gun-b2를 새 main으로 rebase하고 DDG/CG 표적 1기,
0°/90° ×각15회(총60회) 재진단 → Phase 1 착수 보고를 한다.
