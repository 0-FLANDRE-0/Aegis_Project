# AEGIS v48 WIP16A — Plan / Status

갱신: 2026-10-03 (KST)

**WIP16A 명시 범위 package·재빌드·Chromium 검사 통과 / 전체 PR 통합은 기존 3D 검사 실패로 HOLD / main 병합·v48.1 승격 보류.**

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
- PR [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41), tested head `4edae6dd627f57e9b67e7485ca386a70b67a368a`.
- WIP16 전용 Actions [37090059200](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37090059200): Python 3.11/3.12/3.13 exact package + Chromium, **4/4 job PASS**; runtime **13/13 PASS**, core failures `0`, page errors `0`.
- 일반 smoke [37090059060](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37090059060): **29/30 job PASS**, `aegis-3d-render` FAIL. 후보의 피격 구멍 연결과 구형 BridgeMaster 형상 audit 실패를 숨기지 않는다.
- 원격 artifact summary 및 렌더러 보존 증거는 [마감 기록](docs/wip16/A/CLOSEOUT.md)을 따른다.

일반 smoke에는 WIP12D 등 역사 payload 검사와 최신 파일 자동 선택 검사가 섞여 있다. 이번 3D job은 WIP16A를 열었으며 렌더러 ready/SwiftShader는 확인했지만 기존 형상/피격 구멍 계약을 통과하지 못했다. 해당 렌더러 이후 source는 정식 v48과 byte-identical다. 이는 source 보존 증거이며 새 v48 WebGL 재현 실행을 주장하지 않는다. WIP16 명시 기능의 acceptance는 전용 workflow가 맡는다.

## 승인·다음 진입점

현재 안정 기준은 v48이다. main 병합, v48.1 승격과 release/tag는 별도 승인 전까지 실행하지 않는다. 전체 통합 전에는 C5 모델의 피격 구멍 연결/renderer audit를 별도 범위로 정리해야 한다. 이후 다음 기능 범위는 출항 전 함선 선택·생성·초기화 공통화 → 기존 DDG-119 동작 보존 → 벙커힐 모델/프로필 연결이다. 하푼·토마호크는 후속 범위로 두며 새 번호는 아직 배정하지 않는다.
