# Baseline Audit + TRACK-A

먼저 [REPORT.md](REPORT.md), root 소유 `VALIDATION.json`, [TRACK_AUDIT.md](TRACK_AUDIT.md), [TRACK_CONTRACT.md](TRACK_CONTRACT.md)를 읽는다. `trackAStatus`가 `INCOMPLETE`이면 아직 최종 RC2 증거가 모이지 않은 상태다. 별도 `finalClosure=INCOMPLETE`는 상속 미해결 항목 때문에 유지된다. TRACK-A의 동작 보존 `PASS`도 `friendly-contact-a`에 남은419025 FAIL 및 CG history observer2건의 승인이나 release 승인이 아니다. `releaseApproved=false`를 유지한다.

기준은 `friendly-contact-a@4ba64ba0cace9124497a710d00df1b174984ffdc`, 작업은 `track-a-contract-trace`다. Baseline Audit 커밋은 `7e7ba089a689a0c876e5c99881d4631127a2a491`, RC1 구현은 `34c29992b2160428bf823136a6b765a546a1e34e`, RC2 metadata 보정은 `bae3cb3da79ba8de74220c9b53e99d7b884becea`다. 최종 독립 HTML은 `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA-256은 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`다.

HTML 전용 ZIP과 검증·보고서 ZIP을 별도로 제공한다. 보고서 ZIP은 Markdown/JSON/CSV 및 보존된 UI 증거를 읽는 용도다. 재실행에는 같은 저장소의 기존 fixture·과거 HTML·Python3/Playwright·Chromium·Node/acorn 의존성이 필요하다. SVG 타임라인을 재생성하려면 matplotlib도 필요하다. ZIP만으로 게임의 전체 시험 환경을 새로 만들지는 않는다. 원격 URL·최종 checksum·readback은 root 게시 기록을 따른다. PR 생성, main/기준 브랜치 병합, release/tag는 요청 범위가 아니다.

## 재현 명령

대형 브라우저 시험은 기본1개, 충분한 메모리가 확인된 경우 최대2개로 운영한다. `/dev/shm`은 이 실행 호스트의 임시 작업 위치이며 반드시 같은 절대경로를 써야 하는 제품 요구는 아니다. 기존 제출 증거를 먼저 별도 보존한다. 테스트 runner는 같은 출력 파일을 다시 쓸 수 있다.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/build.py
node docs/contact/track/A/test_contract.cjs docs/contact/track/A/measurement-contract.js --out docs/contact/track/A/evidence/contract-unit.json
NODE_PATH=/workspace/aegis-performance-c/docs/performance/C/node_modules node docs/contact/track/A/check_scope.cjs
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/baseline_runner.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/verify_runtime.py --sha e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a --only ingress
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/verify_runtime.py --sha e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/regression_runner.py
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/plot_trace.py
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/validate.py --require-complete
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/report.py --require-complete
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/A/package.py
```

`verify_runtime.py --only ingress`를 먼저 실행한 뒤 전체 기본 작업을 실행하면 final runtime 집계에 필요한 ingress 자료가 존재한다. 실행 여부와 합격 여부는 다르며 실제 final SHA·원시 결과를 확인한다. `regression_runner.py --resume`은 같은 최종 SHA의 이미 끝난 결과를 이어 실행하는 옵션이다. `report.py --require-complete`는 root의 최종 VALIDATION과 해당 SHA 증거가 모두 완성되지 않았으면 보고서를 INCOMPLETE로 쓰고 exit2로 끝난다. 보고서 생성기는 HTML·기대값·시험 결과·VALIDATION을 수정하지 않는다.

## API

```js
window.__TRACK_A__.normalize(kind, payload, context)
window.__TRACK_A__.configure({enabled:true,capacity:1024})
window.__TRACK_A__.snapshot()
window.__TRACK_A__.clear()
window.__TRACK_A__.configure({enabled:false})
```

기본은 trace OFF다. API는 detached diagnostic view/ring만 다루며 기존 센서·연관·EKF·분류·IFF·ROE·발사/피해·AI 입력으로 사용하지 않는다. ESM bearing에 거리 추가, 미관측 고도의 확정, source sequence를 독립 fix로 단정, remote-only를 FCS로 승격하는 동작은 하지 않는다. `NETWORK_RECONCILE`의 현재 시각은 추정 상태의 `stateAtS`이며 미상인 `measuredAtS/receivedAtS`로 복사하지 않는다.

## 증거 지도

- `INSTRUCTIONS.md`: 전체 지시서. 이번 구현은 Audit+A뿐이다.
- `TRACK_AUDIT.md`, `audit-local.*`, `audit-network.*`, `BASELINE_DELTAS.md`: 기준 packed/source·consumer·정보 경계 감사와 고정된 기존 차이.
- `TRACK_CONTRACT.md`, `TEST_MATRIX_A.md`, `measurement-contract.js`: 차원·가정·보고 추정치·시각·source·불확실성·진단 규약.
- `BUILD.json`, `SCOPE.json`, `hook-locations.json`, `changes.diff`: 실제 최종 소스 범위와 보호189심볼·해시.
- `evidence/baseline/`: fresh D1/세 재현/IFF/120s/배속/paired 및419025 RNG 계측. after-action truth는 이 시험 자료에서만 사용한다.
- `evidence/candidate/`, `REGRESSION_RESULTS.json`, `evidence/regression/`: 최종 RC2 동등성·trace/query·native component fixture·native13·현재 UI·WebGL·성능.
- `evidence/rc1-candidate/`, `evidence/regression/RC1/`: superseded RC1 historical. 최종 fresh 결과로 세지 않는다.
- `DEVELOPMENT.md`: 최초 환경 실패, RC1 metadata 오류 발견과 최종 재검증 경위.
- `FUTURE_STAGES.md`: TRACK-B/C/D 설계·위험·종료 기준만. 정책 구현 없음.

native ingress47과 unit52는 fixture-only다. 자연 RF/실제 무장 증거와 섞거나 기존420 통과 수에 더하지 않는다. IFF/APS/ISAR/ESM의 현재 trace는 producer-only 범위가 있고 전체 실패·만료·연관 계보 추적이 아니다. 성능의 live heap Δ는 할당량이 아니며 heap sampling도 통계적 추정이다.
