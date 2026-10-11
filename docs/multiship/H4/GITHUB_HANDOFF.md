# H4 직접 업로드 인계

- 기준: H3 final `af1eade2d418b215720a68a5b902aae0d9387203`.
- branch `multiship-tactical-h4`, PR base `multiship-tactical-h3`.
- 2026-10-10 §7.1 사용자 승인으로 원본 HTML과 support를 Codex가 직접 업로드하고 독립 GitHub tree/raw-byte readback한다. 추가 수동 업로드나 승인을 요구하지 않는다.
- 새 병합 요청이 없으므로 main/선행 branch·PR을 병합하지 않는다. Actions는 dispatch하지 않고 로컬 최종 HTML 검증으로 gate를 충족한다. PR의 자동 smoke 상태는 실제 metadata/annotation으로 확인하며 계정 제한 실패를 코드 검사 통과로 바꾸지 않는다.
- H3 HTML/status/SHA/workflow 네 파일을 변경 없이 `archive/v48/WIP_MULTI_SHIP_H3/`로 보존한다. source models/assets0~12, stable v48, H3 이하 support를 유지한다. record13만 바꾸고 full HTML exact rebuild한다.
- `evidence/remote-publication.json`은 code commit의 독립 읽기 기록이다. 뒤의 proof-only commit은 원본/support blob을 바꾸지 않는다. 최종 commit의 전체 읽기 기록은 외부 작업 폴더에 남겨 자체 해시 재귀를 피한다.
- 최종 수치와 한계는 루트 상태·`evidence/verification-summary.json` 및 실제 PR을 따른다.
