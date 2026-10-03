# AEGIS v48 WIP16A — Plan / Status

갱신: 2026-10-03 (KST)

**사용자 업로드 exact 확인 / 로컬 패키지·재빌드 통과 / 원격 Chromium 검증 진행 전 / main 병합·v48.1 승격 보류.**

## 기준

- branch: `WIP16`
- base: `main@d2b840bae95267ffc53bfda847442b2211c1ab03`
- user upload commit: `3be1ba489a0f8b934b8d2000aec408b56ea863af`
- stable baseline: `Aegis_SIM_v48.html`, SHA-256 `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- candidate: `Aegis_SIM_v48_WIP16A.html`, `7,354,882 bytes`
- SHA-256: `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`
- Git blob: `d0d8b3de795716cb21ba2f7ba9673b8024dc2ceb`
- decoded main SHA-256: `8e5fb5f435c6f164879d4246feb5f548ceabef087701ac760c0132cb1dac0669`
- target stable version after approval: `v48.1`

## 범위와 보존

WIP16A의 기존 Phalanx 변경 범위는 [설계 계약](docs/wip16/WIP16_PHALANX_FIRE_CONTROL.md)을 따른다. 이번 마감에서는 사용자 HTML을 변경하지 않았다. Mk244 분산, 기존 spotting 상수, SeaRAM, WIP15 soft-kill, WIP14 nav/DL/loft와 v48 수상교전 경로를 추가 튜닝하지 않는다.

## 마감 수정

- Python의 `gzip.compress(mtime=0)` OS-header 차이를 제거하는 `GzipFile` 빌더. 원본과 같은 payload 및 HTML exact 재현.
- runtime benchmark를 audit 이전에 실행하고 benchmark/spotting/regression을 새 browser context로 격리. 기존 acceptance 13개와 threshold 유지.
- 지원 자료, 원본 증거 출처, 대응 체크섬과 후보 HTML 전용 CI 추가.
- README의 안정판 표기와 WIP14B4 아카이브 링크 수정.

## 검증

- 직접 재검사: original package `64/64 PASS`.
- 직접 재검사: 추가 hash/complete record set/전체 executable script/재빌드 `21/21 PASS`.
- 15개 executable script 문법 PASS; records 0–12 compressed bytes 보존.
- 재빌드 HTML과 업로드 HTML byte-identical.
- 로컬 Chromium: 미실행(설치된 executable 없음).
- 원본 지원 ZIP에는 runtime `13/13`, core failures `0`, page errors `0`이 기록되어 있다. 현재 Actions 결과와 구분한다.
- 원격 Chromium, 전체 PR job 및 PR 번호는 [마감 기록](docs/wip16/A/CLOSEOUT.md)에 갱신한다.

기존 일반 smoke workflow는 WIP12D 파일을 검사한다. 그 결과를 WIP16A 후보 회귀로 계산하지 않는다. 후보 검증은 `WIP16A package and browser regression` workflow가 맡는다.

## 승인·다음 진입점

현재 안정 기준은 v48이다. main 병합, v48.1 승격과 release/tag는 별도 승인 전까지 실행하지 않는다. WIP16 통합 후 다음 기능 범위는 출항 전 함선 선택·생성·초기화 공통화 → 기존 DDG-119 동작 보존 → 벙커힐 모델/프로필 연결이다. 하푼·토마호크는 후속 범위로 두며 새 번호는 아직 배정하지 않는다.
