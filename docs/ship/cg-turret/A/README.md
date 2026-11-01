# CG_TURRET_A

게임은 루트 `Aegis_SIM_v48_WIP_CG_TURRET_A.html`, 사람이 읽는 결과는 `REPORT.md` 또는 `INDEX.html`이다. HTML ZIP과 보고서 ZIP은 `downloads/`에서 분리해 제공한다.

기준은 PR #61 병합 main `8fdd69533ff96fa652ceec752f6852eaf89fbebc`, B2B HTML SHA-256 `d2ae791e38221ec660283989728ea50e0eeb9075c2501cdbef9086e6c61cbc26`이다.

재현 순서: `build.py` → `audit_scope.cjs` → `run_measurements.py range` / `g7` → `verify_render.py` → `run_measurements.py baseline` / `control` → `run_checks.py` → `analyze.py` → `reconcile.py` → `report.py` → `package.py`. 측정과 회귀는 최대 두 브라우저 lane에서 실행한다. `NODE_PATH`는 기존 acorn 설치 경로를 사용하고 Python 임시는 `TMPDIR=/dev/shm`, `PYTHONDONTWRITEBYTECODE=1`을 쓴다.

`harness.py`는 B2B의 기존 실제 게임 계측 도구를 선택한 HTML bytes에 적용한다. origin-control은 CG 설치 원점 값만 B1 값으로 역복구한다. 진단 HTML은 메모리에서만 만들며 제품으로 배포하지 않는다.

회귀 원본은 수정하지 않는다. UI의 옛 생성 포탑 기대 두 건은 복구된 원형 메시로 이관하며, native 한 건은 원점 복구 후 새 가림을 검증하는 승인 기록을 별도로 남긴다. 기존 raw 실패도 보존한다. 원격 readback은 ZIP의 자기참조 체크섬을 피하기 위해 artifact 커밋 후 후속 커밋에 기록한다.
