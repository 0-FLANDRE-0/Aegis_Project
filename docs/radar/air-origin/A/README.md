# AIR_ORIGIN_A

main `9719f1e`를 기준으로 자체 SPY/SPQ AIR receiver 메타데이터만 복구한다.
게임: `Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html`.
[REPORT.md](REPORT.md), [STATUS.json](STATUS.json), [diff](AIR_ORIGIN_A.diff),
[검증 자료](evidence/summary.json)를 함께 확인한다. HTML ZIP과 보고서 ZIP은 분리한다.

RF 식·계수, KF 이득, clamp, 무장, 저장 스키마와 기존 reference 파일은 그대로다.
NPC 어댑터의 기존 6개 sensor 필드 계약을 자체 AIR에도 적용한다.
receiver 값은 해당 RF 측정에 실제 사용한 값이며 현재 함 위치나 표적 truth로
사후 보정하지 않는다. CG SPQ-9 수상 전용 기능도 그대로다.

## 재현

저장소 전체와 Python Playwright/시스템 Chromium, Node/Acorn이 필요하다.
보고서 ZIP만으로 공통 하네스가 모두 제공되지는 않는다.

```sh
python docs/radar/air-origin/A/build.py
python docs/radar/air-origin/A/verify_roundtrip.py
python docs/radar/air-origin/A/verify_live_receivers.py
node docs/radar/air-origin/A/static.cjs
python docs/radar/air-origin/A/run_regressions.py
```

`NODE_PATH`는 Acorn 설치 경로를 지정한다. 실행 환경에서는 TMPDIR=/dev/shm,
PYTHONDONTWRITEBYTECODE=1을 썼다. 원래 증거를 보존하고 별도 checkout에서 재현한다.

- 무잡음 검사: 실제 RF 함수·AIR 변환·SPQ 화이트리스트·EKF를 실행한다.
  private reflector/zero-noise 공급자는 진단에만 사용하고 복원한다.
- live receiver: 자연 탐지에서 실제 RF receiver와 EKF 입력을 비교한다.
  한 번에 레이더 하나만 활성화하는 격리는 진단 페이지에만 적용한다.
- run_regressions: main/후보 38작업, 기존 도메인 전체 + 42쌍대 + 시커28 +
  실제 자연 탐지/정식 VLS/WebGL8 + world120 + EW/H3/자연 CIWS.
- 시커28은 기존 이상 사통 트랙 공급 조건이다. 자체 레이더 자연 탐지라고 부르지 않는다.
- test_support: 기존 retired UI 명령 어댑터와 5in Auto OFF 설정을 재사용한다.
  world120에서 이미 반환한 상태와 쌍대 전투 종료 후 AFTER_ACTION_TRUTH를
  추가 기록한다. 검사 조건·기대값·게임 로직은 바꾸지 않는다.
- 기존 H3 fixture의 H4 현행 스키마 해석은 기존 verify_ew_h3.py와 동일한
  역사적 test migration이며 이번 작업에서 새 기대값을 채택한 것이 아니다.

원본 CIWS 진단은 퇴역된 미사일이 live 배열에서 제거된다. 사후 표적 결과를
보존하기 위해 같은 main CIWS 두 조건을 참조 로깅만 추가해 재실행했다.
원래 결과를 보존하고 표적 결과 필드를 제외한 샘플·물리 결과·RNG 동일을 검사한다.

추가 원인 분석은 `verify_causes.py raid`와 `verify_causes.py world`로 실행한다.
기존과 같은 테스트 설정을 적용하려면 저장소 루트에서 다음 환경을 사용한다.

```sh
export AIR_ORIGIN_REGRESSION=1
export AIR_ORIGIN_HTML=Aegis_SIM_v48_WIP_GUN_B1.html
export AIR_ORIGIN_OUT="$PWD/docs/radar/air-origin/A/evidence/cause-config"
export PYTHONPATH="$PWD/docs/radar/air-origin/A/test_support"
python docs/radar/air-origin/A/verify_causes.py raid
python docs/radar/air-origin/A/verify_causes.py world
python docs/radar/air-origin/A/analyze_causes.py
python docs/radar/air-origin/A/verify_combat.py Aegis_SIM_v48_WIP_GUN_B1.html docs/radar/air-origin/A/evidence/ciws-main-extra --only-ciws
```

원인 로거는 실제 fixed tick이 끝난 뒤 숫자만 읽는다. `analyze_causes.py`는
로거가 원래 함 상태·동역학·RNG/world120 hash를 바꾸지 않았는지 먼저 검사한다.
틱 로그는 무손실 gzip으로 보존하며 코드/수치 변경의 근거로 되먹이지 않는다.
구체적인 최초 차이 시점과 원시 데이터 해시는 `evidence/cause-analysis.json`에 있다.

모든 작업이 끝난 뒤 `collect.py` → `report.py` → `package.py` 순서로 수집한다.
실패한 기존 단언은 통과로 바꾸지 않으며 결과·hash 차이는 그대로 보고한다.
원격 다운로드 영수증은 ZIP 생성 후 별도 후속 커밋으로 기록한다.

## 중단 지점

PR을 열고 멈춘다. main 병합·release/tag 생성은 하지 않는다.
병합 후 gun-b2에 main을 반영하고 DDG/CG의 표적 1기, 0°/90° ×각15회
재진단을 한 뒤 Phase 1 착수 보고를 한다. 이 단계는 아직 실행하지 않았다.
