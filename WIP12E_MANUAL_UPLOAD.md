# WIP12E 수동 업로드 절차

대상 repository는 `0-FLANDRE-0/Aegis_Project`, 대상 branch는 `feat/v48-wip12e-compartment-blast`다.

## 업로드 파일

- 로컬 파일: `Aegis_SIM_v48_WIP12E.html`
- branch 경로: `/Aegis_SIM_v48_WIP12E.html`
- 크기: `3,148,363 bytes`
- SHA-256: `790a980ff6e4fa6ab045d3d15893ff5d22c23b064ccf4e93006de3ce59eb9bf9`

## 절차

1. GitHub UI 또는 정상 인증된 `git` 전송을 사용한다.
2. branch가 `feat/v48-wip12e-compartment-blast`인지 다시 확인한다.
3. 파일을 repository 루트에 추가한다.
4. 업로드한 파일을 다시 내려받아 SHA-256을 검증한다.
5. checksum이 맞은 뒤 `package.json`, workflow, README 및 `AEGIS_PROJECT_INSTRUCTIONS.md` 전환 commit을 만든다.
6. WIP12E contract와 Playwright 전체 회귀를 실행한다.

contents API, base64 또는 파일 분할 방식으로 큰 HTML을 우회 업로드하지 않는다.

