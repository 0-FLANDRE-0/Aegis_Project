# Bunker Hill K — GitHub 반영과 검사 범위

사용자 업로드 commit `5c883a5aeb80e0878f0f256f2a7a64d90224920e`, branch `bunkerhill-late-profile`의 HTML은 로컬 검증본과 byte-identical이다. 크기 14,458,866 bytes, SHA-256 `efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df`, Git blob `e41ae0f4207de57d1fa35807f008c2b5a5c51d3e`. 업로드한 HTML의 코드·패킹을 수정하지 않았다.

정식 `Aegis_SIM_v48.html`의 SHA-256 `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`도 유지한다. main에 통합해도 K의 정식 버전 승격·release/tag 생성을 의미하지 않는다.

## 로컬 근거와 원격 검사의 구분

- `evidence/verification-summary.json`은 같은 SHA의 K에서 직접 통과한 로컬 284개 검사를 정리한다. 각 raw evidence의 `preview-05.html`은 업로드 K와 같은 bytes이다.
- [원격 업로드 확인](evidence/remote-upload-check.json)은 사용자 업로드 commit·크기·Git blob·SHA를 기록한다.
- [Bunker Hill workflow](../../../.github/workflows/bunkerhill-late-profile.yml)는 현재 업로드를 다시 빌드하고 실제 브라우저·WebGL로 검사한다. 최종 원격 결과는 해당 PR의 Actions checks에서 확인한다. artifact에는 입력 hash, 시나리오 조건, page error/fault와 실제 검사 결과를 보관한다.
- 기존 일반 smoke에는 여러 역사 HTML 입력이 포함되어 있다. smoke 전체 통과 수를 K 직접 검사의 수로 합산하지 않는다.

DDG 동작 비교는 고정 SHA의 원본 WIP16B와 K를 같은 runner의 같은 Playwright Chromium 실행 파일로 다시 실행한다. 서로 다른 브라우저 엔진에서 저장한 과거 JSON은 출처 증거로 보존하며, 현재 회귀 판정은 같은 환경의 두 실행을 대조한다. 기존 comparator의 aggregate 완전 일치, case/event 비교, float 허용 오차를 그대로 유지하고 browser version·두 실행의 raw 결과를 artifact에 기록한다.

## GitHub에 보존한 지원 자료

K의 작은 모듈·빌더·검사·출처·로컬 evidence와 J의 선행 evidence를 반영했다. H의 작은 기준 모듈은 exact 비교본 재빌드에 사용한다. authored main, 거대한 diff, cache와 추출된 모델의 중복 사본은 commit하지 않는다.

선행 STARTUP_A의 원래 checksum이 root README·지침·workflow도 참조하므로, 이 파일들을 포함한 당시 32개 checksum 대상과 HTML·상태·SHA를 `archive/v48/WIP_STARTUP_A/`에 exact 보존했다. STARTUP_A workflow는 이 immutable snapshot의 모든 checksum을 검사하고 기존 baseline HTML을 그대로 실행한다. 최신 안내 문서 갱신이 선행 검사 당시의 hash를 바꾸지 않는다.

D/F/H/I/J의 대형 HTML은 이 브랜치에 추가 업로드하지 않는다. 로컬 전체 ZIP의 archive는 그대로 보존하며, 원격 workflow는 고정 STARTUP_A·K 내장 asset·작은 기준 모듈로 비교본을 exact 재빌드한다. 각 helper가 원래 SHA를 확인한 뒤에만 비교 검사를 진행한다. 로컬 상태 문서의 archive 설명과 `MANIFEST.sha256`은 전달한 전체 ZIP의 구성이고, repository에는 필요한 작은 지원 자료와 별도 [지원 파일 manifest](REPOSITORY_SUPPORT.sha256)를 둔다.

## 병합 판정

PR head가 검사한 commit과 같은지 확인하고, 적용된 Actions checks가 성공한 뒤 main에 merge commit으로 통합한다. 사용자가 이 병합을 요청했다. 강제 ref 갱신이나 보호 규칙 우회를 사용하지 않는다. 테스트 대상 head와 병합 결과는 PR 기록을 따른다.
