# FRIENDLY_CONTACT_A

`REPORT.md`와 `VALIDATION.json`을 먼저 확인한다. 사용자가 지정한 미병합 `cg-turret-a` 위에서, `ciws-dmg-a`의 진단 자료를 보존하고 만든 **수정 후보**다. 기존 성공이 피격으로 바뀐 시드 419025를 승인된 회귀로 취급하지 않는다. main/기준 브랜치 병합 및 release/tag 생성은 하지 않는다.

제품은 저장소 루트 `Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html`이다. HTML 전용 ZIP과 보고서 ZIP을 별도로 제공한다. 보고서 ZIP의 테스트 도구는 같은 저장소의 기존 진단 의존성이 있어야 재실행할 수 있다.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/build.py
NODE_PATH=/workspace/aegis-performance-c/docs/performance/C/node_modules node docs/contact/friendly/A/check_scope.cjs
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/contracts.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/repro.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/repro.py --current
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/ciws.py d1
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/ciws.py protection
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/isolated.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/variants.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/auto_iff.py
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/friendly/A/analyze.py
MPLCONFIGDIR=/dev/shm/mpl-friendly-contact python docs/contact/friendly/A/plots.py
```

대형 브라우저 시험은 메모리 여유에 맞춰 순차 실행한다. `regressions.py`는 기존 테스트의 단언을 바꾸지 않고 실행하지만, 일부 오래된 UI 테스트는 MAP_E에서 제거한 DOM을 요구한다. 이 결과는 합격으로 세지 않는다. 기존 보고서·기대값·허용 오차는 수정하지 않는다.

`harness.py`는 실제 제품의 압축 JS를 풀어 기존 시험 도구를 메모리에만 삽입한다. 게임 함수를 별도 근사 모델로 바꾸지 않는다. `repro.js`의 truth는 `truthDiagnosticOnly`에 사후 기록할 뿐 연관·식별·발사 입력에 넣지 않는다. 헬기 초기 위치는 검증된 세이브를 가져오고, 하푼은 native 발사/INS 경로를 사용한다. 센서·IFF·EKF·fixed tick은 실제 제품 함수다.

`evidence/`의 초기 실패 로그와 재시도 경위는 `DEVELOPMENT.md`에 남긴다. JSONL의 gzip 포장은 무손실이다. 제출 후 재실행 시 제출 증거를 다른 디렉터리로 먼저 보존해야 한다.
