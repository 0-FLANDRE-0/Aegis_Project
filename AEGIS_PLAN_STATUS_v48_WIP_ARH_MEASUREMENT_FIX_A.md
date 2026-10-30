# AEGIS v48 WIP ARH MEASUREMENT FIX A

상태: **로컬 구현·검증 완료 / 작업 브랜치 게시 준비 완료 / main 미병합 / release·tag 없음**

- 제품: `Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html`
- 크기: `18,453,432 bytes`
- SHA-256: `900be4a2d146ecf33eff67f1719134b9a93eb58c3dc79fbc9b6a6cc813c3cfab`
- 기준: `arh-measurement-contract-a@ef38c738e2d2d3b262d36d3a2001d0e903c969bf`
- 변경: 공통 RF_V2 사분면 각도 응답의 정확한 역변환, 실제 생성 각도 잡음과 반환 σ/R의 계약 일치.
- 원래 SM-6 240 km/5 km/접근 250 m/s/seed 12001: `51.308397 m 실패` → `1.349768 m 성공`.
- 신규 성공→실패 0. 종료기 300발에서 실패→성공 12.
- 회귀: 공통 SAM 180발, 자연 RF 28조건, UI 88/88, 고정 틱·배속 PASS. 도메인은 기존 실패 그대로 414/420.
- 제품 변경 함수는 `_arhV2MonopulseMeasurement` 하나. PN/APN/ZEM/Kappa, 발사 인계, 추진·공력·기동한계, 신관·피해, 탐지/Pd, 종료기는 기준판과 동일.
- 전체 ENV_D 재측정은 이번 범위가 아니다. 기존 사거리표는 `재계산 필요` 상태를 유지한다.

세부 결과와 재현 명령은 `docs/missile/arh-measurement/FIX_A/REPORT.md`, `REPRODUCE.md`, `verification-summary.json`을 따른다.
