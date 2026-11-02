# CIWS_DMG_A 진단 도구

최종 보고서는 `REPORT.md`를 먼저 읽는다. 이번 브랜치는 게임 HTML·게임 계수·기대값을 변경하지 않는다. `cg-turret-a` 커밋 `6d306849f290f987cd39c31c901adb4478b07edd`에서 분기했다. 사용자가 작업 도중 기준을 변경했으므로 원래 지시서의 main/B2B 대신 **CG_TURRET_A 원본**을 사용한다. 경위와 제외된 초기 결과는 `BASE_CHANGE.json` 및 `evidence-main-before-user-base-change/`에 보존한다.

진단 입력은 `Aegis_SIM_v48_WIP_CG_TURRET_A.html`, SHA-256 `af105075c65bf9c8774c8b1d347273476e53a3a5869c12387b2cd8d46824d933`다. 산출물 ZIP에는 새 게임 HTML을 넣지 않는다.

## 실행

전체 저장소의 같은 기준 커밋, Python 3, Playwright/Chromium 및 기존 저장소 진단 의존성이 필요하다. 보고서 ZIP만으로 게임을 재실행하지 않는다. 이미 저장된 JSON/CSV/SVG는 ZIP만으로 열 수 있다.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py equivalence
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py static
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py c1
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py d1
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py controls
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py protection
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py protection-hp0
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/ciws/dmg/A/run.py geometry
python docs/ciws/dmg/A/analyze.py
MPLCONFIGDIR=/dev/shm/mpl-ciws python docs/ciws/dmg/A/plots.py
```

실행 중에는 원래 시작 시점에서 3시간인 `TASK_CLOCK.json`의 마감 시각을 넘지 않는다. 이 제출본은 과거 실행 증거이므로 그 시각이 지나면 재실행은 명시적으로 중단한다. 새로운 실행은 사용자 지시의 새 시간 예산을 별도 기록해야 한다.

`run.py`는 같은 모드의 결과 파일을 다시 쓴다. 제출 증거를 먼저 별도 디렉터리에 보존해야 한다. 최종 저장소의 큰 원시 JSONL은 손실 없는 gzip이며, `analyze.py`와 `plots.py`는 원본 JSONL/gzip 모두 읽는다.

## 실제 게임 경로

`harness.py` → 기존 `docs/gun/B2/phase1b/harness.py`의 `build(file=..., record=False)` → 기존 GUN_B1 `__GB_TEST__.scenario` → 실제 `simulateFixedTick(SIM_FIXED_DT)`다. 기존 기록용 GUN_B2 삽입 패치는 `record=False`로 사용하지 않는다. 압축 JS index 13의 스타트업 뒤에 테스트 도구를 메모리에서 삽입하며, 새 게임 HTML을 디스크에 쓰지 않는다.

출항은 기존 DOM `input/change/click` 경로로 자함을 선택하고 아군·적함·훈련함·항공기 자동 생성을 끈다. 출항 후 RAF 진행을 일시정지하고 기존 시나리오 함수를 이용해 native fixed tick만 진행한다. 시드별 새 브라우저 페이지를 사용한다. 센서 탐지는 실제 센서 경로이며 트랙을 강제로 만들지 않는다. 이 시험의 원래 교전 모드는 MANUAL, 함포 AutoAA는 OFF다. SM/ESSM 자동 발사를 켜지 않는다. CIWS 독립 자위 경로는 그대로 실행한다.

`diagnostic.js`는 native 함수 결과를 그대로 반환하는 관찰 래퍼다. HP·모듈·침수·신관/폭발 기록·로컬 상태를 읽고 별도 로그에만 쓴다. 추가 `protection-trace.js`는 C55 측정 연관이 끝난 직후 기록을 읽는다. 이 파일에서 읽는 source key/엔티티는 **AFTER_ACTION_TRUTH_TEST_ONLY** 인과 분석용이며 센서/AI/교전 상태에 되돌려 쓰지 않는다.

계측 동등성 서명에는 전투 결과, HP/모듈/수밀 구획/강도/생존 상태, 잔탄, 선박 항법, 게임 RNG와 로컬 센서/조준/사격 RNG가 포함된다. 실행 호스트의 `performance.now`/경과시간 필드만 제외한다. 시뮬레이션 시간 `timeS`, fixed tick은 보존한다. 원래 시나리오는 위협이 사라진 틱에 종료되므로 피격 뒤 장시간 화재·침수 예측 시험으로 해석하지 않는다.

## 자료 지도

- `INSTRUCTIONS.md`: 원 지시서. 기준 변경은 `BASE_CHANGE.json`이 우선한다.
- `evidence/equivalence.json`: 4조건 ON/OFF 동등성, RNG/함수 SHA.
- `evidence/{c1,d1,controls}.jsonl.gz`: 전체 native 사건 로그.
- `evidence/protection*.jsonl.gz`: HP 0 네 시드의 추가 인과 계측.
- `analysis/`: 사각 경계 CSV, 방위 민감도, 회차별 타임라인, 피해 경로, 과거 결과 비교.
- `evidence/native-sources.json`, `source-excerpts.txt`: 실제 실행 함수와 원본 JS 줄번호를 단 진단 발췌.
- `PUBLIC_REVIEW.md`, `public/`: 공개 자료 대조 및 원본·출처 메타데이터.
- `analysis/pr-arc-opening-audit.json`, `pr-sources.json`, `pr55-team-source.json`: 미병합 PR 52–55의 고정 SHA 코드 조사.
- `figures/`: 검증 자료에서 만든 정적 그래프. 게임 표현 계층과 무관하다.
- `DEVELOPMENT.json`: fixture 오류, 기준 변경, 재시도 기록. 게임 오류나 합격 측정으로 숨기지 않는다.
