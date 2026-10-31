# GUN_B1 인계

게임 파일은 저장소 루트 `Aegis_SIM_v48_WIP_GUN_B1.html`. HTML ZIP과 보고서 ZIP은 `downloads/`에 별도로 둔다. `REPORT.md`, `STATUS.md`, `evidence/acceptance.json`, `remote-readback.json` 순으로 확인한다. 최종 원격 영수증은 ZIP 자기 해시 순환을 피하기 위해 별도 후속 커밋이다.

## 빌드

기준 `map-e` 커밋 `5542aa005479713a5a8959143157fdf4ba07447e`의 정확한 MAP_E HTML이 필요하다. Python 3.12에서:

```sh
python docs/gun/B1/build.py
```

`spec.js / air.js / auto.js / fuze.js / handoff.js`와 최소 문맥 치환을 실제 압축 게임 JS에 적용하고 gzip·manifest를 재생성한다. `base-functions.json`의 Node UTF-16 위치에서 추출한 동일 본문 순번을 사용하므로 NPC의 동명 private 함수는 수정하지 않는다. 본문 추출을 다시 할 때는 Acorn 설치 환경에서 `node docs/gun/B1/extract-base.cjs`를 사용한다. 런타임에 소스 파서를 탑재하지 않는다.

## 검증 재현

시스템 Chromium, Python Playwright, Node+Acorn이 필요하다. 기존 하네스는 저장소 `docs/`의 공통 코드를 불러오므로 보고서 ZIP만으로 전체 게임 회귀를 실행할 수는 없다. 저장소 전체를 checkout해야 한다. `TMPDIR=/dev/shm`, `PYTHONDONTWRITEBYTECODE=1`은 시험 환경의 디스크 제약을 위한 값이며 게임 로직에는 영향이 없다.

- `verify_static.cjs`: 비행 지문 281개, ENV_D byte, 변경된 기존 symbol 목록.
- `verify_native.py`, `verify_auto.py`, `verify_geometry.py`: 새 기능의 실제 게임 함수 검수.
- `verify_ui.py`, `verify_label.py`, `verify_mod4.py`, `verify_ui_handoff.py`: WebGL/지도/인계/포구·화면 경계 검수.
- `verify_physical_adapter.py`: 하푼 SI 물리 근접과 기존 종료·사후 로그 연결.
- `verify_mass_split.py`: 복사한 질량 노드만 병합해 CG 부동소수 차이의 원인을 확인. 제품·기대값 수정 없음.
- `run_regression.py`: 기존 MAP_E 검사, `test_support/sitecustomize.py`로 자동 대공 OFF를 명시. 결과 경로만 격리한다.
- `await_test_migrations.py`: 원래 MAP_D 결과를 먼저 보존한 후, 요청된 새 기능과 충돌하는 정확한 두 단언만 이관해 재검사한다. 원래 시험 파일은 바꾸지 않는다.

### G7 재현

최종 후보의 조건부 수정 전 측정 HTML은 다음 도구로 byte 정확히 재구성할 수 있다.

```sh
python docs/gun/B1/verify_engine_equivalence.py --write-measured /tmp/gun-b1-replay/measured.html
```

원래 960회는 그 측정 HTML에서 실행했다. 이후 변경은 라벨 위치, 하푼 물리 어댑터, 수동 인계 경로이며, 시험 조건에는 하푼·NPC·수동 명령이 없다. `evidence/engine-equivalence.json`에 역변환 전체와 적용 조건을 보존하고, `verify_effect_equivalence.py`에서 최종 후보와 16쌍의 full-world 결과/RNG 동등성을 확인했다. 실제 실행 SHA를 최종 SHA로 덮어쓰지 않는다.

새 결과 디렉터리에서 원래 측정을 재현하려면 아래를 worker 0/1/2로 실행한다. 환경 변수를 생략하면 최종 제품 HTML을 사용한다. 기존 증거는 덮어쓰지 않는 별도 경로를 권장한다.

```sh
GUN_B1_EFFECT_HTML=/tmp/gun-b1-replay/measured.html GUN_B1_EFFECT_OUT=/tmp/gun-b1-replay/results python docs/gun/B1/effect_trials.py 0 3
GUN_B1_EFFECT_HTML=/tmp/gun-b1-replay/measured.html GUN_B1_EFFECT_OUT=/tmp/gun-b1-replay/results python docs/gun/B1/effect_trials.py 1 3
GUN_B1_EFFECT_HTML=/tmp/gun-b1-replay/measured.html GUN_B1_EFFECT_OUT=/tmp/gun-b1-replay/results python docs/gun/B1/effect_trials.py 2 3
GUN_B1_EFFECT_OUT=/tmp/gun-b1-replay/results python docs/gun/B1/aggregate_effects.py
```

각 worker는 JSONL caseId를 보고 이미 완료한 건만 건너뛴다. 최초 측정의 source SHA, 30개 시드, 개별 결과, 조건별 평균 및 효과 그래프는 `evidence/effects/`에 있다. 부분 실행·개발 캡처는 최종 검수/패키지에서 제외한다.

## 후속 범위

GUN_B2 대공 유효 구간 측정, NPC 대공 함포 AI, 헬기 실제 피격, HOB/다른 5인치 탄종, 새 EMCON 비방사 지정 GUI는 이번에 구현하지 않았다. main 병합·release·tag·CI 변경 없이 PR 검토를 기다린다.
