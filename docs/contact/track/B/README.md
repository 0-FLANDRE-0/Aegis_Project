# TRACK-B 실행·검증 자료

이 디렉터리는 `ee960db`의 최종 TRACK-A를 기준으로 연관 단계만 변경하는 별도 시험 작업이다. TRACK-C/D, OODA, 새 전술 AI는 범위가 아니다. 현재 문서는 실행 안내이며 완료·병합 승인 보고서가 아니다. 제품·검증 결과의 최종 SHA와 상태는 root가 작성하는 `VALIDATION.json`이 있을 때 그 파일을 우선한다.

최종 증거는 모두 수집됐으며, 선언한 live 구현 계약은 PASS다. 단계는 **INCOMPLETE**, releaseApproved=false다. 원래 paired4건과 ACTIVE D1 signature1건은 원인 경로를 확인했지만 사용자 승인 전 strict FAIL을 보존한다. 원래 domain402 PASS/4 FAIL/14 INCOMPLETE, runtime24건 중23 strict PASS/1 FAIL이며 기대값·허용 오차를 갱신하지 않았다.120초 연장에서도 최초8+추가13ASM가 모두 살아 있어 완료된 전투·요격 보존을 주장하지 않는다.

RC1 제품 source commit은 `da73163a808aa6e480f1c26f42bdc1ae13ddb985`다. ACTIVE SHA는 `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`, SHADOW SHA는 `e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d`다. A/B 진단은 기본 OFF이며 UI/진단 설정으로 build-time ACTIVE/SHADOW를 바꾸지 않는다. 선언한 SHADOW-only 경로를 live 완료로 세지 않는다.

기준 제품은 `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA-256 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`다. 기존 419025 피격 FAIL, CG→friendly observer 2건 미승인 차이, 구형 EMCON UI14 INCOMPLETE를 보존한다. 새 시험 통과는 이 세 항목의 해결 또는 승인이 아니다.

## 준비 확인 — 브라우저 실행 없음

```sh
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/regression_runner.py
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/verify_runtime.py
```

두 명령 모두 read-only dry-run이다. 첫 명령은 재사용할 TRACK-A 증거의 게시 checksum과 기존 test/helper23파일의 git blob 일치를 확인한다. 두 번째는 원본 runtime fixture/helper9파일도 확인한다. 제품 고정 SHA와 root의 실행 순서가 결정되기 전에는 `--run`을 쓰지 않는다.

## 광역 원래 회귀

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/regression_runner.py --run --sha ACTIVE_SHA256
```

기본 순서는 native13(364단언) → TRACK-A paired42 → UI213 → WebGL8발/29단언이다. `--only aps153 harpoon-f1`처럼 suite를 골라 실행하거나 `--resume`으로 **동일 candidate/reference SHA**의 결과만 이어갈 수 있다. 기본 한 lane이며 root가 다른 lane이 비었다고 확인한 경우에만 `--parallel 2`를 쓴다. `evidence/regression/STOP_AFTER_CURRENT` 파일이 생기면 진행 중인 worker가 끝난 다음 멈추고 미실행 suite를 기록한다. 새 후보를 실행할 때 이전 증거와 중단 marker를 먼저 별도 경로로 보존한다.

native364+paired42=406이다. 제거된 `#lockBtn`을 요구하는 원본 EMCON UI14는 기대값을 고치거나 PASS로 세지 않는다. UI213·WebGL29를 domain420에 중복 더하지 않는다. paired의 원래 strict 비교와 모든 JSON leaf 차이는 함께 보존하며 실제 observer 상태 차이를 metadata로 축소하지 않는다.

## A / SHADOW / ACTIVE runtime 비교

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/verify_runtime.py --run --sha ACTIVE_SHA256 --shadow-sha SHADOW_SHA256
```

기본은 `--products baseline shadow active`, task는 `d1 repro trace auto-iff idle clocks performance allocation`이다. 필요한 task만 `--only d1 repro trace`로 고를 수 있다. SHADOW의 full-state 비교에는 앞서 실행한 같은 도구의 baseline 캡처가 필요하므로 기본 순서를 유지한다. `--resume`은 동일 ACTIVE/SHADOW SHA만 허용하며 PASS만 재사용한다. 실패/미완료 재시도 전 해당 variant의 전체 출력 snapshot과 이전 execution을 `evidence/runtime/attempts/`에 보존한다. `--worker`는 controller 내부용이다. 직접 실행하면 caller가 전역 browser lease와 frozen SHA를 보장해야 한다.

- `d1`: 원본 friendly/A CIWS script로 419010~419039 30시드. 원래 native signature를 최종 A 증거와 비교하고 원시 사건/자원/피해 차이도 보존한다.
- `repro`: 기존 자연 헬기 hover60초·route120초·Harpoon route75초를 실행한다. 원본 결과, RNG, 전체 관련 track/observer 상태를 비교 전에 저장한다.
- `trace`: 같은 세 조건과 419025를 진단 OFF/ON으로 실행한다. A/B snapshot 반복 조회·privacy와 전체 상태/RNG 무변경을 검사한다. 진단 스위치는 build-time SHADOW/ACTIVE를 바꾸지 않는다.
- `auto-iff`, `idle`: 원본 script와 단언을 그대로 실행한다. AUTO 아군 헬기 무장 소모 및 120초 idle truth/DOM 상태를 확인한다.
- `clocks`: 원래 1/8/16/64배속 fixture24단언을 실행한다.
- `performance`, `allocation`: 원래 A의 warmup/bench와 실제 native 함수를 사용한다. 두 owner 각각 한 fixed tick당 1회, median/p95, live heap과 통계적 sampling을 기록한다. 외국/NPC 연관 변화는 모든 상태 diff로 보존하며 자동 승인하지 않는다.

각 controller는 같은 `heavy_browser_slot()`의 두 flock lease를 사용한다. 이것은 협력 실행자의 전역 상한2를 지키는 도구이며, 외부의 미조정 Chromium까지 자동으로 제한하는 기능은 아니다. root가 다른 작업과 lane을 조정해야 한다. 동시 작업의 성능값은 host 부하가 섞인 raw proxy다. outlier를 제거하거나 이를 신뢰할 수 있는 속도 향상으로 표현하지 않는다. nested kernel timing/counter를 합산하지 않고 heap sampling을 정확한 할당량으로 부르지 않는다.

## 결과 해석

원래 assert가 실패하면 FAIL을 보존하고, 독립 사례는 계속 캡처한다. 경로가 의도대로 달라졌다는 이유만으로 기대값·허용 오차를 바꾸지 않는다. 원인 검증 전 차이를 자동 KNOWN_DELTA/PASS로 바꾸지 않는다. 직접 anonymous ingress fixture 성공과 자연 RF·실제 전투 증거는 구별한다. RC0 broad는 시작되지 않았으며 `evidence/RC0_BROAD_NOT_EXECUTED.json`은 실행 결과가 아니다.

초기 runtime 도구는 async `__ENV_D__.status()`를 기다리기 전에 `.match`를 읽는 fixture 오류가 있었다. 이 때문에 변경하지 않은 TRACK-A의 자연 재현에서도 원본 결과·상태·query는 일치하면서 ENV check만 거짓 실패했다. root 승인으로 원래 A처럼 Promise 결과 전체를 기다린 뒤 같은 `match===true` 조건을 검사하도록 고쳤으며 전체 resolved status를 저장한다. 실패 시도는 폐기하지 않고 archive하며, 새 worker receipt의 실제 controller SHA로 수정 전·후 실행을 구별한다. 제품이나 ENV hash 기준을 바꾼 것이 아니다.

PRIVATE/AFTER_ACTION 상태 사본은 검증 출력으로만 사용한다. 게임 association/classification/AI/fire 소비자에 truth를 전달하지 않는다. 새 제품의 RF, EKF, IFF, 무장·피해 계수와 저장 스키마는 이 검증 도구가 수정하지 않는다. main/기준 브랜치 병합, release/tag 생성도 수행하지 않는다.

## 최종 증거 대조·보고서·전송 포장 재현

```sh
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/validate.py --require-complete
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/report.py
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B/package.py
```

첫 명령은 원래 시험을 재실행하거나 기대값을 바꾸지 않고 현재 SHA와 완료된 raw 증거를 대조해 VALIDATION metadata를 작성한다. exit0은 증거가 모두 있다는 뜻이며 단계 승인이나 모든 strict 검사 통과라는 뜻이 아니다. 최종 성능 주 자료는 독점 lease/순차9구성의 `evidence/cost-final/SUMMARY.json`·`ASSESSMENT.json`·`COST_FINAL.md`다. 이전 동시 호스트 비용/retained-only sample도 지우지 않고 context로 남겼다.

`package.py`는 최종 증거 작업사본에서 실행한다. 원래 `.jsonl`을 무손실 `.jsonl.gz`로 바꾸고 원문/gzip 해시를 `RAW_COMPRESSION.json`에 기록한다. `CHECKSUMS.sha256` 및 별도 ACTIVE HTML ZIP/SHADOW HTML ZIP/REPORT ZIP을 만들고 모든 ZIP member를 읽어 SHA와 CRC를 검증한다. 게임 HTML·시험 결과의 의미·기대값은 바꾸지 않는다. 재생성은 고정 repository와 기존 fixture/Python/Playwright/Chromium/Node/acorn에 의존하며 그래프에는 matplotlib가 필요하다. 원격 업로드/readback은 root가 수행하며 release/tag는 만들지 않는다.
