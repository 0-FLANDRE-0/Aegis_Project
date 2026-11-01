# 원 실행기 보존 smoke 계획

상태: **실행 GO 대기**. 계획 생성은 브라우저를 시작하지 않는다.

| 작업 | 실제 원 실행 경로 | 새 페이지 | 과거 대조 범위 |
|---|---|---:|---|
| helo-hover 60초 / helo-route 120초 / harpoon-route 75초 | frozen B `verify_runtime.natural(trace=False)` → 원 friendly `repro.js` → 실제 fixed tick | 3 | A·B 원 result, 전체 observer/track/P/private RNG, 원 state 문자열 SHA와 압축 증거 bytes |
| autoIFF 90초 | frozen B `original_script('auto-iff')` → 원 `auto_iff.py` 전체 runpy | 1 | A·B 원 checks/result, 기존 result.rng; 과거 full observer/P/private RNG snapshot은 없음 |
| idle 120초 + DOM | frozen B `original_script('idle')` → 원 `idle_and_dom.py` 전체 runpy | 2 | fresh before/after truth·DOM·core, A·B 원 truth bytes/hash 및 원 rows/checks |

총 **6페이지**, 동시 브라우저1개다. 기존 B 실측 약60.7+25.4+52.3=138.4초를 실행시간 추정에만 사용하며 준비·비교 포함 약 **2.5~3분**을 예상한다. host 동시 부하가 있으면 실제 시간을 따로 보고한다. ON 추가 페이지, CIWS 추가 사격, clock24 중복 실행은 하지 않는다.

## 제품 매핑

- repro3은 원 B 함수의 명시적 `file` 인자로 새 `Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html`(SHA `48b023c5…e4ab`)을 받는다.
- autoIFF와 idle의 `current=True`는 원 B/A의 기존 `redirect_existing()`을 그대로 사용한다. 원 friendly 입력 경로를 새 ACTIVE로 읽기만 리다이렉트한다.
- idle의 `current=False`는 원 harness가 지정한 `Aegis_SIM_v48_WIP_CG_TURRET_A.html`을 **새로 실행**한다. 이를 A/B 실행으로 바꿔 부르지 않는다. 원래 before/after 두 페이지와 원 checks를 유지한다.
- 과거 TRACK-A `e2c1976a…d67a`, delivered B ACTIVE `0b3e5ad9…e4c6`의 실제 smoke 원시 결과를 각 published CHECKSUMS와 제품 SHA로 확인한 뒤 읽기 전용 대조 자료로 사용한다. 과거 결과를 새 실행으로 세지 않는다.

## 보존과 판정

원 B controller, friendly Python/JS, 원 world120 STATE와 assert는 편집하지 않는다. idle AST를 바꾸거나 before 페이지를 캐시로 대체하지 않는다. ENV는 수정 완료된 frozen B 코드의 `page.evaluate('__ENV_D__.status()')`로 실제 Promise 결과를 기다리는 경로를 그대로 사용한다.

원 실행기의 PASS/FAIL·exit code·전체 출력·로그를 먼저 남긴다. result 및 full state의 모든 필드·헤더를 비교하고 각 원시 bytes와 canonical hash를 함께 기록한다. gzip/header/schema/시각 필드 차이도 삭제하지 않는다. auto/idle 출력의 host wallS 차이는 원 checks와 별개로 전부 diff에 남기며 승인하지 않는다.

repro3에는 기존 A/B full snapshot이 있으므로 observer/P/private RNG 동일성을 실제로 확인할 수 있다. autoIFF는 기존 result/rng, idle은 원 STATE truth/rng·DOM이 역사적 비교의 한계다. 없는 full snapshot을 PASS로 만들거나 비용 benchmark 70초를 world120 보존으로 대신하지 않는다.

각 작업은 별도 Python worker에서 실행하여 기존 Path 리다이렉션이 다른 작업에 남지 않게 한다. worker 종료 시 Python Path 메서드도 복구한다. 원 게임 HTML, helper, 저장 정책, 기대값 및 허용 오차는 바꾸지 않는다. FAIL·차이는 보고만 하며 자동 수정·승인은 하지 않는다.

`smoke.py --plan`으로 해시·범위만 고정한다. root가 lane 실행 GO를 준 뒤 `smoke.py --run --go-reference ...`로 원 B의 공유 browser lease 하나를 잡아 세 작업을 순서대로 실행한다. 제품·입력 해시가 달라지거나 기존 실행 자료가 있으면 덮어쓰지 않고 중단한다.
